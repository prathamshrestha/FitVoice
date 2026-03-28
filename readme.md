
# FitVoice 🤖🎙️

A voice-powered fitness coaching application with real-time speech recognition, RAG-enhanced fitness advice, and interactive voice feedback.

![Python](https://img.shields.io/badge/Python-3.10-blue)
![React](https://img.shields.io/badge/React-18.3.1-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🌟 Key Features

### 🎯 Real-Time Voice Processing
- **Dual ASR Backend**: Toggle between Google Cloud Speech-to-Text and OpenAI Whisper at runtime
- **Smart Voice Activity Detection**: Silence-based utterance segmentation (1.5s gap)
- **Barge-In Support**: Interrupt the AI mid-sentence by speaking — TTS stops immediately

### 💬 AI Fitness Coaching
- **RAG-Enhanced Responses**: Retrieves relevant fitness knowledge from 19,000+ Q&A pairs and curated knowledge base using ChromaDB vector search
- **TinyLlama LLM**: Fine-tuned for fitness coaching with context-aware prompts
- **Confidence Tracking**: RAG debug info (relevance scores, retrieved sources) visible in the UI
- **User Profiles**: Personalized advice based on fitness goals, level, and health info

### 🗣️ Text-to-Speech
- **Coqui TTS (VITS)**: High-quality voice synthesis for natural-sounding responses
- **Non-blocking Playback**: Audio plays without blocking the mic — enables barge-in

### 🎨 Modern Web Interface
- **React 18 + TypeScript**: With Tailwind CSS and Shadcn/ui components
- **Real-time Visualizations**: Waveform display for audio input
- **RAG Confidence Badges**: Shows retrieved docs and relevance scores per response
- **Chat Sessions**: Persistent conversation history with sidebar navigation

## 🛠️ Technology Stack

### Backend
| Component | Technology |
|-----------|-----------|
| API Server | FastAPI (async WebSocket + REST) |
| ASR (Primary) | Google Cloud Speech-to-Text |
| ASR (Fallback) | OpenAI Whisper (tiny, CPU) |
| LLM | TinyLlama 1.1B Chat (with optional LoRA) |
| RAG | ChromaDB + SentenceTransformers (persistent) |
| TTS | Coqui TTS (VITS, LJSpeech) |
| Dataset | `hammamwahab/fitness-qa` (19,743 Q&A pairs) |

### Frontend
| Component | Technology |
|-----------|-----------|
| Framework | React 18 + TypeScript + Vite |
| Styling | Tailwind CSS |
| Components | Shadcn/ui + Radix UI |
| Audio | Web Audio API + ScriptProcessor |
| Routing | React Router |
| State | Zustand |

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Google Cloud credentials (`googleasr_key.json`) for Google STT
- espeak-ng (for TTS)

### Backend Setup
```bash
cd be

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # Linux/Mac
# or: venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Place Google ASR credentials
cp /path/to/googleasr_key.json be/app/googleasr_key.json

# Run the server
cd app
uvicorn server:app --reload --port 8000
```

### Frontend Setup
```bash
cd fe
npm install
npm run dev
```

Open `http://localhost:5173` in your browser.

## 📁 Project Structure

```
FitVoice/
├── be/                              # Backend (Python/FastAPI)
│   ├── app/
│   │   ├── server.py               # Main FastAPI server + WebSocket handler
│   │   ├── google_asr.py           # Google Cloud STT integration
│   │   ├── fitness_llm_inference.py # LLM inference with RAG support
│   │   ├── user_profile.py         # User profile system
│   │   └── googleasr_key.json      # Google credentials (gitignored)
│   ├── fitness_rag_system.py       # ChromaDB RAG system
│   ├── fitness_knowledge_base.py   # Knowledge base generator
│   ├── fitness_knowledge_base.jsonl # Curated fitness knowledge (44 docs)
│   ├── chroma_db/                  # Persistent vector database (gitignored)
│   ├── requirements.txt
│   └── Dockerfile
├── fe/                              # Frontend (React/TypeScript)
│   ├── src/
│   │   ├── components/             # UI components (VoiceButton, ChatMessage, etc.)
│   │   ├── pages/                  # ChatPage, LandingPage, Dashboard
│   │   ├── hooks/                  # useVoiceChat, useChat
│   │   ├── services/              # voiceApiClient (WebSocket + audio)
│   │   └── stores/                # Zustand state management
│   └── package.json
└── README.md
```

## 🎯 Architecture

### Real-Time Audio Pipeline
```
Mic → Web Audio API → Int16 PCM → WebSocket → Backend
  ↓                                              ↓
  ├─ VAD (barge-in detection)           Google STT / Whisper
  ↓                                              ↓
  Stop TTS if user speaks              Transcription
                                                 ↓
                                        RAG Retrieval (ChromaDB)
                                                 ↓
                                        TinyLlama LLM (w/ context)
                                                 ↓
                                        Coqui TTS → base64 WAV
                                                 ↓
                                        WebSocket JSON response
                                                 ↓
                                    Frontend plays audio + shows RAG debug
```

### Key Design Decisions
- **Silence-based utterance detection**: Audio buffers until 1.5s of silence, then processes entire utterance at once (no mid-speech chunking)
- **Persistent ChromaDB**: Vector embeddings stored on disk, skips re-embedding on restart (<1s init vs ~30s)
- **Barge-in via frontend VAD**: RMS threshold on mic input stops TTS playback instantly when user speaks
- **Lazy Whisper loading**: Whisper model only loaded when toggled to, saving memory

## 🔌 API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/ws` | WebSocket | Audio streaming + responses |
| `/api/health` | GET | System status + active ASR mode |
| `/api/asr/status` | GET | Current ASR backend info |
| `/api/asr/toggle` | POST | Switch between Google/Whisper |
| `/api/asr/toggle?mode=whisper` | POST | Switch to specific backend |
| `/api/profile/{user_id}` | GET/POST | User profile management |

## ⚙️ Environment Variables

```env
GOOGLE_APPLICATION_CREDENTIALS=app/googleasr_key.json
VITE_BACKEND_URL=http://127.0.0.1:8000   # Frontend .env
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for Whisper speech recognition
- **Google Cloud** for Speech-to-Text API
- **Hugging Face** for Transformers and SentenceTransformers
- **Coqui TTS** for text-to-speech synthesis
- **ChromaDB** for vector database
- **FastAPI** for the web framework
- **Shadcn/ui** for UI components
