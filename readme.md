
# FitVoice 🤖🎙️

A cutting-edge voice-powered fitness application that revolutionizes workout tracking through advanced AI speech recognition, and interactive voice feedback.

![FitVoice Demo](https://img.shields.io/badge/Status-In%20Development-orange)
![Python](https://img.shields.io/badge/Python-3.10-blue)
![React](https://img.shields.io/badge/React-18.3.1-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.116.1-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)

## 🌟 Key Features

### 🎯 Real-Time Voice Processing
- **Live Speech Recognition**: Instant transcription using OpenAI Whisper (tiny model for efficiency)
- **Voice Activity Detection**: Smart silence detection and utterance segmentation

### 💬 Interactive Voice Chat
- **AI-Powered Conversations**: TinyLlama LLM for contextual fitness coaching
- **Text-to-Speech**: High-quality voice synthesis using Coqui TTS
- **Real-time WebSocket Communication**: Seamless bidirectional audio streaming
- **Voice Commands**: Hands-free workout control and progress tracking

### 🎨 Modern Web Interface
- **Responsive Design**: Built with React 18, TypeScript, and Tailwind CSS
- **Component Library**: Shadcn/ui for consistent, accessible UI components
- **Real-time Visualizations**: Waveform display for audio input feedback
- **Multi-page Application**: Landing page, dashboard, and chat interface

### 🏗️ Robust Backend Architecture
- **FastAPI Server**: High-performance async API with WebSocket support
- **Docker Containerization**: Complete environment with micromamba for reproducible builds
- **Model Caching**: Pre-loaded models for instant startup
- **GPU Acceleration**: CUDA support for faster inference on compatible hardware

## 🛠️ Technology Stack

### Backend
- **Python 3.10** with async programming
- **FastAPI** for REST and WebSocket APIs
- **Whisper** (OpenAI) for speech-to-text
- **Wav2Vec2** (Hugging Face Transformers) 
- **TinyLlama** for conversational AI
- **Coqui TTS** for text-to-speech synthesis
- **PyAudio** for audio capture and processing
- **Docker** with micromamba for containerization

### Frontend
- **React 18** with TypeScript
- **Vite** for fast development and building
- **React Router** for client-side routing
- **TanStack Query** for server state management
- **Shadcn/ui + Radix UI** for accessible components
- **Tailwind CSS** for styling
- **Lucide React** for icons

### Audio Processing
- **Real-time audio streaming** via WebSocket
- **16kHz sample rate** for optimal model performance
- **Voice activity detection** with RMS thresholding
- **Automatic gain control** and noise filtering

## 🚀 Getting Started

### Prerequisites
- Docker and Docker Compose
- Node.js 18+ (for frontend development)
- Python 3.10+ (optional, for local development)

### Quick Start with Docker

1. **Clone the repository**
   ```bash
   git clone https://github.com/prathamshrestha/FitVoice.git
   cd FitVoice
   ```

2. **Start the backend**
   ```bash
   cd be
   docker build -t fitvoice-backend .
   docker run -p 8080:8080 fitvoice-backend
   ```

3. **Start the frontend**
   ```bash
   cd ../fe
   npm install
   npm run dev
   ```

4. **Open your browser** to `http://localhost:5173`

### Local Development

#### Backend Setup
```bash
cd be
# Create conda environment
conda env create -f environment.yml
conda activate voicebot

# Install additional dependencies
pip install -r requirements.txt

# Run the server
python -m app.server
```

#### Frontend Setup
```bash
cd fe
npm install
npm run dev
```

## 📁 Project Structure

```
FitVoice/
├── be/                          # Backend (Python/FastAPI)
│   ├── app/
│   │   ├── server.py           # Main FastAPI server
│   │   ├── asr_utils.py        # ASR utilities
│   │   └── models/             # Pre-trained models
│   ├── live_transcribe_emotion.py  # Real-time demo script
│   ├── wav2vec2_inference.py   # Wav2Vec2 inference class
│   ├── requirements.txt        # Python dependencies
│   ├── environment.yml         # Conda environment
│   ├── Dockerfile             # Container configuration
│   └── voicebot.yml           # Micromamba environment
├── fe/                         # Frontend (React/TypeScript)
│   ├── src/
│   │   ├── components/         # Reusable UI components
│   │   ├── pages/             # Application pages
│   │   ├── stores/            # State management
│   │   └── lib/               # Utilities
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Build configuration
└── README.md                  # This file
```

## 🎯 Core Components

### Real-Time Audio Pipeline
1. **Audio Capture**: Continuous microphone input at 48kHz
2. **Resampling**: Downsampled to 16kHz for model compatibility
3. **Voice Activity Detection**: RMS-based silence detection
4. **Speech Recognition**: Whisper transcription
6. **LLM Processing**: Contextual response generation
7. **Text-to-Speech**: Voice synthesis and playback

### WebSocket Communication
- **Binary audio streaming** for low-latency transmission
- **JSON metadata** for transcription
- **Connection management** with automatic reconnection
- **Error handling** and graceful degradation

## 🔬 Technical Achievements

### 🤖 AI/ML Integration
- **Transformer Model**: Custom Wav2Vec2 model training on health and wellness datasets
- **Efficient Inference**: Optimized for real-time performance on CPU/GPU
- **Model Quantization**: Reduced model size for deployment
- **Multi-modal Processing**: Speech 

### ⚡ Performance Optimizations
- **Async Processing**: Non-blocking audio processing pipeline
- **Model Caching**: Pre-loaded models to eliminate startup delays
- **Memory Management**: Efficient tensor operations and cleanup
- **Container Optimization**: Multi-stage Docker builds for smaller images

### 🎨 User Experience
- **Responsive Design**: Works on desktop and mobile devices
- **Accessibility**: WCAG compliant components and keyboard navigation
- **Real-time Feedback**: Visual indicators for voice activity and processing
- **Intuitive Interface**: Clean, modern design with clear visual hierarchy

## 🧪 Testing & Quality

### Automated Testing
- **Unit Tests**: Backend logic and API endpoints
- **Integration Tests**: Full audio pipeline testing
- **E2E Tests**: Playwright for frontend testing
- **Performance Tests**: Latency and throughput benchmarks

### Code Quality
- **TypeScript**: Full type safety in frontend
- **ESLint**: Code linting and formatting
- **Pre-commit Hooks**: Automated code quality checks
- **Docker Testing**: Container build and runtime validation

## 🚀 Deployment

### Production Setup
```bash
# Build optimized frontend
npm run build

# Build production Docker image
docker build -t fitvoice:latest .

# Run with GPU support (optional)
docker run --gpus all -p 8080:8080 fitvoice:latest
```

### Environment Variables
```env
PORT=8080
WHISPER_MODEL=tiny
COQUI_TTS_MODEL=tts_models/en/ljspeech/vits
HF_HOME=/app/models
```

## 📈 Future Roadmap

### Phase 2: Fine Tuning Model
- [ ] **Training transformer**: Next process is training the transformer model with fitness and health datasets


## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Claude AI** for Whisper speech recognition
- **Hugging Face** for Transformers library
- **Coqui TTS** for text-to-speech synthesis
- **FastAPI** for the excellent web framework
- **Shadcn/ui** for beautiful UI components


---

