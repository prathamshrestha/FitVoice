import asyncio, io, base64
import sys
from pathlib import Path
import numpy as np
import soundfile as sf
import torch
import whisper
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from transformers import AutoTokenizer, AutoModelForCausalLM
from TTS.api import TTS
from typing import Tuple, Optional

# Add app directory to path to support both relative and direct imports
_app_dir = Path(__file__).parent
if str(_app_dir) not in sys.path:
    sys.path.insert(0, str(_app_dir))

try:
    # Try relative imports first (when run as module)
    from .user_profile import UserProfileManager, FitnessGoal, get_goal_specific_system_prompt
    from .fitness_llm_inference import FitnessLLMInference
    from .google_asr import GoogleASR
    from .conversation_memory import ConversationMemory
except ImportError:
    # Fallback to absolute imports (when running from app directory)
    from user_profile import UserProfileManager, FitnessGoal, get_goal_specific_system_prompt
    from fitness_llm_inference import FitnessLLMInference
    from google_asr import GoogleASR
    from conversation_memory import ConversationMemory


SAMPLE_RATE = 16000
MIN_UTTERANCE_SEC = 2.0          # process as soon as ~2s of audio is collected
SILENCE_GAP_SEC = 1.5            # consider utterance ended after 1.5s of silence
IDLE_CLOSE_SEC = 180.0
MAX_BUFFER_SEC = 15.0
RMS_THRESHOLD = 0.015  

app = FastAPI()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- ASR: Dual backend (Google Cloud STT + Whisper) ---
asr_mode = "google"  # Default: "google" or "whisper"

# Google ASR (initialized eagerly)
try:
    google_asr = GoogleASR(language_code="en-US", sample_rate=SAMPLE_RATE)
except Exception as e:
    print(f"⚠️ Google ASR failed to init: {e}")
    google_asr = None
    asr_mode = "whisper"  # Fallback to whisper if Google fails

# Whisper ASR (lazy loaded — only when first needed)
whisper_model = None

def get_whisper():
    """Lazy-load Whisper model only when needed."""
    global whisper_model
    if whisper_model is None:
        print("🔄 Loading Whisper model (tiny)...")
        whisper_model = whisper.load_model("tiny", device="cpu")
        print("✅ Whisper model loaded")
    return whisper_model


async def transcribe_audio(audio_buffer: bytes) -> str:
    """Transcribe audio using the currently active ASR backend."""
    if asr_mode == "google" and google_asr:
        return await google_asr.transcribe_async(audio_buffer)
    else:
        # Whisper expects float32 numpy array
        audio_f32 = np.frombuffer(audio_buffer, dtype=np.int16).astype(np.float32) / 32768.0
        model = get_whisper()
        result = await asyncio.to_thread(model.transcribe, audio_f32, fp16=torch.cuda.is_available())
        return (result.get("text") or "").strip()



tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
llm_model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)

# --- Fitness-specific components ---
profile_manager = UserProfileManager()
conversation_memory = ConversationMemory(max_turns=5)

# Initialize fitness LLM (with optional LoRA weights if available)
try:
    fitness_llm = FitnessLLMInference(
        lora_weights_path="fitness_llm_model"  # Will use base model if not found
    )
except:
    # Fallback to base model if fine-tuned version not available
    fitness_llm = FitnessLLMInference()

_tts = None
_tts_error = None

def get_tts():
    global _tts, _tts_error
    if _tts is None:
        try:
            _tts = TTS(model_name="tts_models/en/ljspeech/vits", gpu=torch.cuda.is_available())
        except Exception as e:
            _tts_error = str(e)
            print(f"⚠️ TTS initialization failed: {e}")
            print("📋 To fix this issue, install espeak-ng:")
            print("   Windows: choco install espeak-ng  (or download from https://github.com/espeak-ng/espeak-ng)")
            print("   Linux: sudo apt-get install espeak-ng")
            print("   Mac: brew install espeak-ng")
            return None
    return _tts

sample_rate = 16000

async def google_transcribe(audio_bytes: bytes) -> str:
    """Transcribe audio bytes using Google Cloud Speech-to-Text."""
    if google_asr:
        return await google_asr.transcribe_async(audio_bytes)
    return ""

def _is_silent(frame_bytes, threshold=0.6):
    audio = np.frombuffer(frame_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    rms = (np.mean(audio**2) ** 0.5)
    return rms < threshold

def generate_response(prompt: str, stop_flag: asyncio.Event, user_id: Optional[str] = None, session_id: Optional[str] = None) -> tuple:
    """Generate fitness-specific response using fine-tuned model.
    Returns (response_text, rag_debug_dict)"""
    if stop_flag.is_set():
        return "", {}
    
    try:
        # Get user profile if user_id provided
        user_profile = None
        if user_id:
            user_profile = profile_manager.get_profile(user_id)
        
        # Get conversation history for this session
        conv_history = ""
        if session_id:
            conv_history = conversation_memory.format_for_prompt(session_id)
            turn_count = conversation_memory.get_turn_count(session_id)
            if turn_count > 0:
                print(f"Context: {turn_count} previous turns for session {session_id[:8]}")
        
        # Generate using fitness LLM (now returns dict)
        result = fitness_llm.generate_fitness_advice(
            query=prompt,
            user_profile=user_profile,
            max_new_tokens=150,
            temperature=0.6,
            conversation_history=conv_history,
        )
        
        response = result["response"]
        rag_debug = result["rag_debug"]
        
        if stop_flag.is_set():
            return "", {}
        
        # Clean up response: keep all complete sentences
        last_period = -1
        for i, ch in enumerate(response):
            if ch in '.!?':
                last_period = i
        if last_period > 0:
            response = response[:last_period + 1]
        
        return response.strip(), rag_debug
    
    except Exception as e:
        print(f"LLM generation error: {e}")
        return "Thanks for your question. Please consult a fitness professional for personalized advice.", {}

async def synthesize_tts(text, stop_flag: asyncio.Event):
    try:
        tts = get_tts()
        if tts is None:
            print("TTS Error: TTS system not available. Install espeak-ng to enable text-to-speech.")
            return None
        audio_array = await asyncio.to_thread(tts.tts, text)
        if stop_flag.is_set():
            return None
        buf = io.BytesIO()
        sf.write(buf, np.array(audio_array), samplerate=22050, format='WAV')
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print("TTS Error:", e)
        return None

async def process_utterance(buffer: bytes, websocket: WebSocket, stop_flag: asyncio.Event, user_id: Optional[str] = None, session_id: Optional[str] = None):
    if stop_flag.is_set() or not buffer:
        return

    # Quick silence guard (check RMS on raw PCM)
    audio_f32 = np.frombuffer(buffer, dtype=np.int16).astype(np.float32) / 32768.0
    if float(np.sqrt(np.mean(audio_f32 ** 2))) < RMS_THRESHOLD:
        return

    # ASR — use active backend (Google or Whisper)
    try:
        transcription = await transcribe_audio(buffer)
        if not transcription or stop_flag.is_set():
            return
    except Exception as e:
        print("ASR error:", e)
        return

    # LLM - using fitness-aware generation with session context
    response, rag_debug = generate_response(transcription, stop_flag, user_id=user_id, session_id=session_id)
    if stop_flag.is_set() or not response:
        return

    # Save this turn to conversation memory
    if session_id:
        conversation_memory.add_turn(session_id, transcription, response)

    # TTS
    audio_base64 = await synthesize_tts(response, stop_flag)
    if stop_flag.is_set() or audio_base64 is None:
        return

    await websocket.send_json({
        "text": transcription,
        "llm_response": response,
        "audio": audio_base64,
        "rag_debug": rag_debug,
        "session_id": session_id,
    })

def rms(frame_i16: bytes) -> float:
    if not frame_i16:
        return 0.0
    x = np.frombuffer(frame_i16, dtype=np.int16).astype(np.float32) / 32768.0
    if x.size == 0:
        return 0.0
    return float(np.sqrt(np.mean(x * x)))

def is_silent(frame_i16: bytes, thr: float = RMS_THRESHOLD) -> bool:
    return rms(frame_i16) < thr

async def recv_any(ws: WebSocket, timeout: float = 25.0) -> Tuple[str, bytes | str | None]:
    """Return ('binary', bytes) | ('text', str) | ('disconnect', None) | ('noop', None)."""
    msg = await asyncio.wait_for(ws.receive(), timeout=timeout)
    t = msg.get("type")
    if t == "websocket.disconnect":
        return "disconnect", None
    if "bytes" in msg and msg["bytes"] is not None:
        return "binary", msg["bytes"]
    if "text" in msg and msg["text"] is not None:
        return "text", msg["text"]
    return "noop", None

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔌 WebSocket connection established")

    loop = asyncio.get_event_loop()
    last_activity = loop.time()
    last_voice_time = last_activity

    buf = bytearray()
    collected = 0
    min_samples = int(SAMPLE_RATE * 0.5)  # minimum 0.5s of voice content to process
    gap_samples = int(SAMPLE_RATE * SILENCE_GAP_SEC)  # 1.5s silence = end of utterance
    max_samples = int(SAMPLE_RATE * MAX_BUFFER_SEC)
    # running "silence gap" in samples
    silence_gap = 0
    voice_samples = 0  # track how many samples had actual voice
    
    # Debugging counters
    audio_chunks_received = 0
    silent_chunks = 0
    voice_chunks = 0
    
    # Lock to prevent concurrent utterance processing
    processing_lock = asyncio.Lock()

    stop_flag = asyncio.Event()
    user_id: Optional[str] = None  # Track user_id for personalized responses
    session_id: Optional[str] = None  # Track session for conversation memory

    try:
        while not stop_flag.is_set():
            # read any frame (binary or text), with timeout to keep connection alive
            try:
                kind, payload = await recv_any(websocket, timeout=25.0)
            except asyncio.TimeoutError:
                # keep-alive ping, do NOT close due to silence alone
                try: await websocket.send_text("server_ping")
                except: break
                continue

            now = loop.time()
            if kind == "disconnect":
                break

            if kind == "text":
                last_activity = now
                if payload == "ping":
                    try: await websocket.send_text("pong")
                    except: pass
                # Handle user_id setting (format: "user_id:actual_user_id")
                elif payload.startswith("user_id:"):
                    user_id = payload.split(":", 1)[1]
                    print(f"User connected: {user_id}")
                    try: 
                        await websocket.send_json({"info": f"user_id_set", "user_id": user_id})
                    except: pass
                # Handle session_id setting (format: "session_id:actual_session_id")
                elif payload.startswith("session_id:"):
                    session_id = payload.split(":", 1)[1]
                    turn_count = conversation_memory.get_turn_count(session_id)
                    print(f"Session set: {session_id[:12]}... ({turn_count} previous turns)")
                    try:
                        await websocket.send_json({"info": "session_id_set", "session_id": session_id, "turn_count": turn_count})
                    except: pass
                # idle close if absolutely nothing happening for a long time
                if (now - last_voice_time) > IDLE_CLOSE_SEC:
                    try: await websocket.send_json({"info": "idle_timeout"})
                    except: pass
                    break
                continue

            if kind != "binary" or payload is None:
                continue

            # binary audio (Int16 PCM)
            audio_chunks_received += 1
            last_activity = now
            buf.extend(payload)
            n_samples = len(payload) // 2
            collected += n_samples

            # Check if this chunk is silent
            chunk_is_silent = is_silent(payload)
            if chunk_is_silent:
                silent_chunks += 1
                silence_gap += n_samples
            else:
                voice_chunks += 1
                silence_gap = 0
                voice_samples += n_samples
                last_voice_time = now
            
            # Log audio statistics every 20 chunks
            if audio_chunks_received % 20 == 0:
                print(f"Audio stats - Chunks: {audio_chunks_received}, Voice: {voice_chunks}, Silent: {silent_chunks}, Collected: {collected}, Voice: {voice_samples}, Gap: {silence_gap}/{gap_samples}")

            # safety: cap buffer size to last MAX_BUFFER_SEC
            if collected > max_samples:
                buf = bytearray(buf[-max_samples * 2:])
                collected = len(buf) // 2

            # Process ONLY when silence gap detected after sufficient voice
            # This ensures the entire utterance is collected before processing
            if silence_gap >= gap_samples and voice_samples >= min_samples:
                chunk = bytes(buf)
                buf.clear()
                collected = 0
                silence_gap = 0
                voice_samples = 0
                
                # skip if whole chunk is silent
                if not is_silent(chunk):
                    print(f"Processing utterance ({len(chunk)} bytes, {len(chunk)//2} samples)")
                    try:
                        async with processing_lock:
                            await process_utterance(chunk, websocket, stop_flag, user_id=user_id, session_id=session_id)
                    except Exception as e:
                        print("process_utterance error:", e)
            
            # Reset buffer if only silence (no voice content) to avoid stale data
            elif silence_gap >= gap_samples and voice_samples < min_samples:
                buf.clear()
                collected = 0
                silence_gap = 0
                voice_samples = 0

            # hard idle close (nothing at all)
            if (now - last_activity) > IDLE_CLOSE_SEC:
                try: await websocket.send_json({"info": "idle_timeout"})
                except: pass
                break

    except WebSocketDisconnect:
        print("Client disconnected.")
    except Exception as e:
        print("❌ WS loop error:", e)
        try:
            if websocket.client_state.name == "CONNECTED":
                await websocket.send_json({"error": str(e)})
        except:
            pass
    finally:
        stop_flag.set()
        await asyncio.sleep(0.1)
        print("🧹 Cleanup.")


# --- REST API Endpoints for User Profile Management ---

@app.get("/api/health")
def health_check():
    """Health check endpoint with debugging info."""
    return {
        "status": "ok",
        "service": "FitVoice AI Coach",
        "device": str(device),
        "cuda_available": torch.cuda.is_available(),
        "websocket_endpoint": "/ws",
        "audio_config": {
            "sample_rate": SAMPLE_RATE,
            "min_utterance_sec": MIN_UTTERANCE_SEC,
            "silence_gap_sec": SILENCE_GAP_SEC,
            "max_buffer_sec": MAX_BUFFER_SEC,
            "rms_threshold": RMS_THRESHOLD,
        },
        "models": {
            "asr": f"{'Google Cloud STT' if asr_mode == 'google' else 'Whisper (tiny)'} [active: {asr_mode}]",
            "llm": "TinyLlama-1.1B",
            "tts": "VITS" if get_tts() is not None else "VITS (unavailable)"
        }
    }


@app.get("/api/asr/status")
def asr_status():
    """Get current ASR backend status."""
    return {
        "active_mode": asr_mode,
        "available_backends": {
            "google": google_asr is not None,
            "whisper": True,  # Always available (lazy loaded)
        },
        "description": {
            "google": "Google Cloud Speech-to-Text API (requires credentials)",
            "whisper": "OpenAI Whisper (tiny, runs locally on CPU)",
        }
    }


@app.post("/api/asr/toggle")
def toggle_asr(mode: str = None):
    """Toggle ASR backend between 'google' and 'whisper'.
    
    If mode is provided, switch to that mode.
    If no mode given, toggle between the two.
    """
    global asr_mode
    
    if mode:
        if mode not in ("google", "whisper"):
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid mode '{mode}'. Use 'google' or 'whisper'."}
            )
        if mode == "google" and google_asr is None:
            return JSONResponse(
                status_code=400,
                content={"error": "Google ASR not available (credentials missing or init failed)"}
            )
        asr_mode = mode
    else:
        # Toggle
        if asr_mode == "google":
            asr_mode = "whisper"
        else:
            if google_asr is None:
                return JSONResponse(
                    status_code=400,
                    content={"error": "Cannot switch to Google ASR (not available)"}
                )
            asr_mode = "google"
    
    # Pre-load whisper if switching to it
    if asr_mode == "whisper":
        get_whisper()
    
    print(f"🔄 ASR switched to: {asr_mode}")
    return {
        "success": True,
        "active_mode": asr_mode,
        "label": "Google Cloud STT" if asr_mode == "google" else "Whisper (tiny)",
    }


@app.post("/api/debug/test-audio")
def test_audio_chunk(audio_data: bytes):
    """Test audio processing without WebSocket."""
    try:
        # Test silence detection
        is_silent_result = is_silent(audio_data)
        rms_value = rms(audio_data)
        
        # Test with active ASR backend
        if asr_mode == "google" and google_asr:
            transcription = google_asr.transcribe(audio_data)
        else:
            audio_f32 = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            result = get_whisper().transcribe(audio_f32, fp16=torch.cuda.is_available())
            transcription = (result.get("text") or "").strip()
        
        return {
            "status": "ok",
            "asr_mode": asr_mode,
            "bytes_received": len(audio_data),
            "samples": len(audio_data) // 2,
            "rms": float(rms_value),
            "rms_threshold": RMS_THRESHOLD,
            "is_silent": is_silent_result,
            "transcription": transcription
        }
    except Exception as e:
        return {"status": "error", "error": str(e)}


@app.post("/api/users")
def create_user(
    user_id: str,
    name: str,
    primary_goal: str = "general_wellness",
    age: int = None,
    fitness_level: str = None,
    weight_kg: float = None,
    height_cm: float = None,
    medical_conditions: str = None,
):
    """Create a new user profile."""
    try:
        # Validate fitness goal
        if primary_goal not in [g.value for g in FitnessGoal]:
            return JSONResponse(
                status_code=400,
                content={"error": f"Invalid fitness goal. Choose from: {[g.value for g in FitnessGoal]}"}
            )
        
        profile = profile_manager.create_profile(
            user_id=user_id,
            name=name,
            primary_goal=FitnessGoal(primary_goal),
            age=age,
            fitness_level=fitness_level,
            weight_kg=weight_kg,
            height_cm=height_cm,
            medical_conditions=medical_conditions,
        )
        
        return {"success": True, "user_id": user_id, "profile": profile.to_dict()}
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/users/{user_id}")
def get_user(user_id: str):
    """Get user profile."""
    profile = profile_manager.get_profile(user_id)
    if not profile:
        return JSONResponse(
            status_code=404,
            content={"error": f"User {user_id} not found"}
        )
    return profile.to_dict()


@app.put("/api/users/{user_id}")
def update_user(
    user_id: str,
    name: str = None,
    primary_goal: str = None,
    age: int = None,
    fitness_level: str = None,
    weight_kg: float = None,
    height_cm: float = None,
    medical_conditions: str = None,
):
    """Update user profile."""
    try:
        update_data = {}
        if name: update_data["name"] = name
        if primary_goal:
            if primary_goal not in [g.value for g in FitnessGoal]:
                return JSONResponse(status_code=400, content={"error": "Invalid fitness goal"})
            update_data["primary_goal"] = FitnessGoal(primary_goal)
        if age: update_data["age"] = age
        if fitness_level: update_data["fitness_level"] = fitness_level
        if weight_kg: update_data["weight_kg"] = weight_kg
        if height_cm: update_data["height_cm"] = height_cm
        if medical_conditions: update_data["medical_conditions"] = medical_conditions
        
        profile = profile_manager.update_profile(user_id, **update_data)
        if not profile:
            return JSONResponse(status_code=404, content={"error": f"User {user_id} not found"})
        
        return {"success": True, "profile": profile.to_dict()}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})


@app.delete("/api/users/{user_id}")
def delete_user(user_id: str):
    """Delete user profile."""
    success = profile_manager.delete_profile(user_id)
    if not success:
        return JSONResponse(status_code=404, content={"error": f"User {user_id} not found"})
    return {"success": True, "message": f"User {user_id} deleted"}


@app.get("/api/users")
def list_users():
    """List all users."""
    profiles = profile_manager.list_all_profiles()
    return {
        "count": len(profiles),
        "users": [p.to_dict() for p in profiles]
    }


@app.get("/api/fitness-goals")
def get_fitness_goals():
    """Get available fitness goals."""
    return {
        "goals": [g.value for g in FitnessGoal],
        "descriptions": {
            g.value: f.description
            for g, f in zip(FitnessGoal, [
                type('obj', (object,), {'description': 'Weight loss and fat reduction'}),
                type('obj', (object,), {'description': 'Muscle gain and strength development'}),
                type('obj', (object,), {'description': 'Heart health and endurance'}),
                type('obj', (object,), {'description': 'Overall health, flexibility, and balance'}),
                type('obj', (object,), {'description': 'Sports performance and agility'}),
            ])
        }
    }


@app.post("/api/fitness-advice")
def get_fitness_advice(
    user_id: str,
    query: str,
):
    """Get fitness advice for a user."""
    try:
        profile = profile_manager.get_profile(user_id)
        if not profile:
            return JSONResponse(status_code=404, content={"error": f"User {user_id} not found"})
        
        response = fitness_llm.generate_fitness_advice(
            query=query,
            user_profile=profile,
            max_new_tokens=50,
        )
        
        return {
            "query": query,
            "user_id": user_id,
            "user_goal": profile.primary_goal.value,
            "advice": response,
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
        print("🧹 Cleanup.")