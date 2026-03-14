import asyncio, io, base64
import numpy as np
import soundfile as sf
import torch, whisper
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from transformers import Wav2Vec2ForSequenceClassification, AutoTokenizer, AutoModelForCausalLM
from torch.nn.functional import softmax
from TTS.api import TTS
from typing import Tuple


SAMPLE_RATE = 16000
MIN_UTTERANCE_SEC = 1.0          # process as soon as ~1s of audio is collected
SILENCE_GAP_SEC = 0.4            # consider utterance ended after 0.4s of silence
IDLE_CLOSE_SEC = 180.0
MAX_BUFFER_SEC = 15.0
RMS_THRESHOLD = 0.015  

app = FastAPI()
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# --- Lazy init heavy models (avoid blocking import time) ---
asr_model = whisper.load_model("tiny", device="cpu")  # now cached by Docker build

emotion_model = Wav2Vec2ForSequenceClassification.from_pretrained(
    "superb/wav2vec2-base-superb-ks"
).to(device).eval()
id2label = emotion_model.config.id2label

tokenizer = AutoTokenizer.from_pretrained("TinyLlama/TinyLlama-1.1B-Chat-v1.0")
llm_model = AutoModelForCausalLM.from_pretrained(
    "TinyLlama/TinyLlama-1.1B-Chat-v1.0",
    device_map="auto",
    torch_dtype=torch.float16 if torch.cuda.is_available() else torch.float32,
)

_tts = None
def get_tts():
    global _tts
    if _tts is None:
        _tts = TTS(model_name="tts_models/en/ljspeech/vits", gpu=torch.cuda.is_available())
    return _tts

sample_rate = 16000

async def whisper_transcribe_np(audio_np: np.ndarray):
    # CPU-bound; run in a thread
    return await asyncio.to_thread(asr_model.transcribe, audio_np, fp16=False)

def _is_silent(frame_bytes, threshold=0.6):
    audio = np.frombuffer(frame_bytes, dtype=np.int16).astype(np.float32) / 32768.0
    rms = (np.mean(audio**2) ** 0.5)
    return rms < threshold

def generate_response(prompt: str, stop_flag: asyncio.Event) -> str:
    if stop_flag.is_set():
        return ""
    prompt = f"<|system|>\nYou are a helpful assistant. \n<|user|>\n{prompt}\n<|assistant|>\n"
    input_ids = tokenizer.encode(prompt, return_tensors="pt", add_special_tokens=False).to(llm_model.device)
    bos = torch.tensor([[tokenizer.bos_token_id]], device=llm_model.device)
    input_ids = torch.cat([bos, input_ids], dim=-1)
    output = llm_model.generate(input_ids, max_new_tokens=50)
    if stop_flag.is_set():
        return ""
    return tokenizer.decode(output[0][input_ids.shape[-1]:], skip_special_tokens=True).split(".")[0] + "."

async def synthesize_tts(text, stop_flag: asyncio.Event):
    try:
        tts = get_tts()
        audio_array = await asyncio.to_thread(tts.tts, text)
        if stop_flag.is_set():
            return None
        buf = io.BytesIO()
        sf.write(buf, np.array(audio_array), samplerate=22050, format='WAV')
        return base64.b64encode(buf.getvalue()).decode("utf-8")
    except Exception as e:
        print("❌ TTS Error:", e)
        return None

async def process_utterance(buffer: bytes, websocket: WebSocket, stop_flag: asyncio.Event):
    if stop_flag.is_set() or not buffer:
        return

    # Convert directly to float32 in [-1,1] and feed Whisper (no temp file)
    audio_f32 = np.frombuffer(buffer, dtype=np.int16).astype(np.float32) / 32768.0

    # Quick silence guard
    if float(np.sqrt(np.mean(audio_f32 ** 2))) < RMS_THRESHOLD:
        return

    # ASR (avoid fp16 on CPU)
    try:
        result = asr_model.transcribe(audio_f32, fp16=torch.cuda.is_available())
        transcription = (result.get("text") or "").strip()
        if not transcription or stop_flag.is_set():
            return
    except Exception as e:
        print("ASR error:", e)
        return

    # Emotion (keep your existing code, but ensure correct shape)
    try:
        emo_input = torch.tensor(audio_f32).unsqueeze(0).to(device)
        with torch.no_grad():
            emo_logits = emotion_model(emo_input).logits
            probs = torch.softmax(emo_logits, dim=1)
            emotion = id2label[int(torch.argmax(probs, dim=1))]
    except Exception as e:
        print("Emotion error:", e)
        emotion = "neutral"

    # LLM
    response = generate_response(transcription, stop_flag)
    if stop_flag.is_set() or not response:
        return

    # TTS
    audio_base64 = await synthesize_tts(response, stop_flag)
    if stop_flag.is_set() or audio_base64 is None:
        return

    await websocket.send_json({
        "text": transcription,
        "emotion": emotion,
        "llm_response": response,
        "audio": audio_base64,
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

    loop = asyncio.get_event_loop()
    last_activity = loop.time()
    last_voice_time = last_activity

    buf = bytearray()
    collected = 0
    min_samples = int(SAMPLE_RATE * MIN_UTTERANCE_SEC)
    gap_samples = int(SAMPLE_RATE * SILENCE_GAP_SEC)
    max_samples = int(SAMPLE_RATE * MAX_BUFFER_SEC)
    # running "silence gap" in samples
    silence_gap = 0

    stop_flag = asyncio.Event()

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
                # idle close if absolutely nothing happening for a long time
                if (now - last_voice_time) > IDLE_CLOSE_SEC:
                    try: await websocket.send_json({"info": "idle_timeout"})
                    except: pass
                    break
                continue

            if kind != "binary" or payload is None:
                continue

            # binary audio (Int16 PCM)
            last_activity = now
            buf.extend(payload)
            n_samples = len(payload) // 2
            collected += n_samples

            if is_silent(payload):
                silence_gap += n_samples
            else:
                silence_gap = 0
                last_voice_time = now

            # safety: cap buffer size to last MAX_BUFFER_SEC
            if collected > max_samples:
                buf = bytearray(buf[-max_samples * 2:])
                collected = len(buf) // 2

            # condition A: enough audio for low-latency processing
            # condition B: end-of-utterance detected by silence gap
            if collected >= min_samples or silence_gap >= gap_samples:
                chunk = bytes(buf)
                buf.clear()
                collected = 0
                silence_gap = 0

                # skip silent chunks
                if not is_silent(chunk):
                    try:
                        await process_utterance(chunk, websocket, stop_flag)
                    except Exception as e:
                        print("process_utterance error:", e)

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