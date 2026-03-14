# FitVoice Voice Chat Integration - Testing Guide

## ✅ What's Been Set Up

### Backend (FastAPI WebSocket Server)
- ✅ Backend running on `http://127.0.0.1:8000`
- ✅ WebSocket endpoint at `ws://127.0.0.1:8000/ws`
- ✅ All ML models loaded (Whisper, Emotion detection, LLM, TTS)
- ✅ Server handles audio streaming and processes voice inputs

### Frontend (React + Vite)
- ✅ Created `src/services/voiceApiClient.ts` - WebSocket client for voice communication
- ✅ Created `src/hooks/useVoiceChat.ts` - React hook for voice chat integration
- ✅ Updated `src/pages/ChatPage.tsx` - Integrated voice API with chat UI
- ✅ Created `.env.local` - Backend URL configuration
- ✅ No TypeScript errors

## 🧪 Testing Steps

### Step 1: Ensure Backend is Running
```bash
# In FitVoice/be directory:
pip install -r requirements.txt
uvicorn app.server:app --reload
# Should see: INFO:     Uvicorn running on http://127.0.0.1:8000
```

### Step 2: Start Frontend Dev Server
```bash
# In FitVoice/fe directory:
npm install  # if not already done
npm run dev
# Should see the dev server URL printed (typically http://localhost:5173)
```

### Step 3: Open Frontend in Browser
Navigate to the frontend URL (e.g., http://localhost:5173)

### Step 4: Test Voice Chat
1. Click the **VoiceButton** (microphone icon) at the bottom of the chat
2. Speak your message (e.g., "What's good for breakfast?")
3. Wait for processing:
   - Your speech is transcribed
   - Emotion is detected
   - LLM generates a response
   - Audio response is synthesized and played
4. Messages appear in the chat:
   - Your transcribed text as "User" message
   - AI response as "Assistant" message
   - Emotion label shown in the transcription area

### Step 5: Test Text Input
1. Type a message in the text input field
2. Click "Send" button (or press Enter)
3. Note: Text messages are added to chat but don't trigger backend processing yet

## 🔍 What to Expect

### Successful Voice Interaction Flow:
```
User speaks → Audio captured → Sent to WebSocket
   ↓
Server processes:
  1. Whisper transcription
  2. Emotion detection
  3. LLM generates text response
  4. TTS creates audio response
   ↓
Server sends JSON response:
{
  "text": "what's good for breakfast",
  "emotion": "neutral",
  "llm_response": "Good breakfast options...",
  "audio": "base64-encoded-audio-data"
}
   ↓
Frontend displays:
- Transcription: "what's good for breakfast"
- Emotion: "neutral" (shown below transcript)
- Assistant message: "Good breakfast options..."
- Audio plays automatically
```

## 📊 Debugging

### Check Backend Logs
Look for messages like:
```
ASR result: transcribed text
Emotion detected: label
LLM response generated
TTS audio created
```

### Check Browser Console
Open Chrome DevTools (F12) → Console tab:
- Look for WebSocket connection logs
- Check for any audio playback errors
- Verify JSON messages being received

### Common Issues

**Issue: "Microphone access denied"**
- Solution: Check browser permission for microphone access
- Click the lock icon in address bar → Grant microphone access

**Issue: "WebSocket connection failed"**
- Solution: Ensure backend is running on http://127.0.0.1:8000
- Check .env.local has correct VITE_BACKEND_URL

**Issue: "No audio response"**
- Solution: Check backend logs for TTS errors
- Ensure speaker volume is on

**Issue: "Connection timeout"**
- Solution: Backend may be unresponsive
- Restart backend server with: `uvicorn app.server:app --reload`

## 🚀 Next Steps (Optional Enhancements)

1. **Text Message Processing**
   - Convert typed text to speech
   - Send audio to backend
   - Get and play response

2. **Emotion Display**
   - Show emotion emoji or color indicator
   - Display emotion confidence

3. **Session Management**
   - Save voice chat sessions
   - Replay audio responses

4. **Error Handling**
   - Better error messages
   - Automatic reconnection retry

## 📁 Key Files

| File | Purpose |
|------|---------|
| `src/services/voiceApiClient.ts` | WebSocket client, audio capture, audio playback |
| `src/hooks/useVoiceChat.ts` | React hook managing voice chat state and callbacks |
| `src/pages/ChatPage.tsx` | UI component integrating voice chat |
| `be/app/server.py` | Backend FastAPI server with WebSocket endpoint |
| `.env.local` | Environment variables (backend URL) |
