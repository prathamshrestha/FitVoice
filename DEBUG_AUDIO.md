# FitVoice Audio Debugging Guide

## Issue: Microphone is Capturing but Server Not Processing

The server logs now include detailed debugging information to help identify where audio gets stuck.

### Step 1: Verify Server is Running

Check the health endpoint:
```bash
curl http://localhost:8000/api/health
```

Expected output should show audio configuration:
```json
{
  "status": "ok",
  "websocket_endpoint": "/ws",
  "audio_config": {
    "sample_rate": 16000,
    "min_utterance_sec": 1.0,
    "silence_gap_sec": 0.4,
    "rms_threshold": 0.015
  }
}
```

### Step 2: Check Console Logs

When a client connects and sends audio, you should see:

1. **Connection established:**
   ```
   🔌 WebSocket connection established
   ```

2. **Audio chunks arriving (every 10 chunks):**
   ```
   📊 Audio stats - Chunks: 10, Voice: 8, Silent: 2, Collected: 5120/16000, Gap: 0/6400
   ```

3. **Processing triggered (when reaching 1 second or 0.4s silence):**
   ```
   🎤 Processing utterance (16384 bytes, 8192 samples)
   ```

### Step 3: Troubleshooting

#### No audio chunks arriving (statistics never print)
- **Problem:** Audio is not being sent to the server
- **Check:**
  - Browser console for errors during audio capture
  - Check that WebSocket connection is actually established (look for `🔌 WebSocket connection established`)
  - Verify microphone permissions are granted in browser
  - Check frontend logs in browser DevTools

#### Many silent chunks, no voice chunks
- **Problem:** Microphone capture is working but audio is being classified as silent
- **Solution:** Increase RMS_THRESHOLD in server.py or check microphone input level
  ```python
  RMS_THRESHOLD = 0.015  # Try increasing to 0.01 or 0.005
  ```

#### Statistics show Collected > min_samples but no processing
- **Problem:** Audio is arriving but silence gap detection might be wrong
- **Solution:** Reduce SILENCE_GAP_SEC or MIN_UTTERANCE_SEC:
  ```python
  MIN_UTTERANCE_SEC = 0.5    # Try 0.5 instead of 1.0 for faster processing
  SILENCE_GAP_SEC = 0.2      # Try 0.2 instead of 0.4 for quicker trigger
  ```

#### Processing starts but very slow response
- **Problem:** Model inference is taking time
- **Check:**
  - Is GPU available? Look for `torch.cuda.is_available()` in health response
  - Check server CPU/memory usage
  - This is expected on CPU (~15-30 seconds per response)

### Step 4: Temporary Configuration Changes for Testing

For faster testing, reduce the thresholds temporarily:

Edit `be/app/server.py`:
```python
MIN_UTTERANCE_SEC = 0.3          # Quick trigger (300ms)
SILENCE_GAP_SEC = 0.15           # Quick silence detection
```

This allows testing with shorter utterances.

### Step 5: Check Frontend Connection

Open browser DevTools (F12) → Console tab and look for:
```
✅ Connected to voice API
📍 Audio stats from server...
```

If you don't see these, the WebSocket connection isn't working.

### Detailed Log Output Reference

The console output format:
```
📊 Audio stats - Chunks: {N}, Voice: {V}, Silent: {S}, Collected: {C}/{MIN}, Gap: {G}/{GAP}
```

- **Chunks:** Total audio chunks received
- **Voice:** Chunks detected as voice (above RMS threshold)
- **Silent:** Chunks detected as silence
- **Collected:** Current buffer size / Minimum required (16000 samples = 1 second)
- **Gap:** Current silence gap / Silence threshold (6400 samples = 0.4 seconds)

### Example Good Flow

```
🔌 WebSocket connection established
📊 Audio stats - Chunks: 10, Voice: 8, Silent: 2, Collected: 5120/16000, Gap: 0/6400
📊 Audio stats - Chunks: 20, Voice: 16, Silent: 4, Collected: 10240/16000, Gap: 0/6400
📊 Audio stats - Chunks: 30, Voice: 24, Silent: 6, Collected: 16000/16000, Gap: 0/6400
🎤 Processing utterance (16384 bytes, 8192 samples)
📝 Text: How can I lose weight effectively?
📊 Emotion: neutral
💭 Response: For weight loss, focus on creating a calorie deficit...
```

### If Still Having Issues

1. **Test with curl directly:**
   ```bash
   # Check server is responding
   curl http://localhost:8000/api/health | jq
   ```

2. **Check browser WebSocket in DevTools:**
   - Open DevTools → Network tab
   - Filter by "WS" (WebSocket)
   - Should see connection to `ws://localhost:8000/ws`
   - Status should be "101 Switching Protocols"

3. **Test audio format:**
   - Audio must be Int16 PCM
   - Sample rate 16000 Hz
   - Mono (1 channel)
   - Sent as binary frames

4. **Enable more detailed logging:**
   Add to server startup to see model loading:
   ```python
   # At the beginning of server.py, after imports
   logging.basicConfig(level=logging.DEBUG)
   ```
