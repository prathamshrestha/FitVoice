/**
 * Voice API Client - WebSocket communication with backend
 * Handles audio streaming, transcription, emotion detection, and TTS responses
 */

export interface VoiceResponse {
  text: string;
  emotion: string;
  llm_response: string;
  audio: string; // base64-encoded audio
}

export interface VoiceApiClient {
  connect: () => Promise<void>;
  disconnect: () => void;
  sendAudio: (audioChunk: Uint8Array) => void;
  isConnected: () => boolean;
  onMessage: (callback: (data: VoiceResponse) => void) => void;
  onError: (callback: (error: string) => void) => void;
  ping: () => void;
}

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || "http://127.0.0.1:8000";
const WS_URL = BACKEND_URL.replace("http", "ws");
const SAMPLE_RATE = 16000;

class VoiceApiClientImpl implements VoiceApiClient {
  private ws: WebSocket | null = null;
  private messageCallbacks: ((data: VoiceResponse) => void)[] = [];
  private errorCallbacks: ((error: string) => void)[] = [];
  private audioContext: AudioContext | null = null;
  private mediaStream: MediaStream | null = null;
  private processor: ScriptProcessorNode | null = null;
  private isRecording = false;

  async connect(): Promise<void> {
    return new Promise((resolve, reject) => {
      try {
        this.ws = new WebSocket(`${WS_URL}/ws`);
        this.ws.binaryType = "arraybuffer";

        this.ws.onopen = () => {
          console.log("✅ Connected to voice API");
          resolve();
        };

        this.ws.onmessage = (event) => {
          try {
            // Check if message is text (like "server_ping") or JSON data
            if (typeof event.data === 'string' && (event.data === 'server_ping' || event.data === 'pong')) {
              console.log('📍 Received ping/pong:', event.data);
              // Ignore ping/pong messages
              return;
            }

            const data = JSON.parse(event.data);
            this.messageCallbacks.forEach((cb) => cb(data as VoiceResponse));
          } catch (e) {
            console.error("Failed to parse WebSocket message:", e);
          }
        };

        this.ws.onerror = (error) => {
          console.error("WebSocket error:", error);
          this.errorCallbacks.forEach((cb) => cb("Connection error"));
          reject(error);
        };

        this.ws.onclose = () => {
          console.log("Disconnected from voice API");
          this.cleanup();
        };
      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    this.cleanup();
    if (this.ws) {
      this.ws.close();
      this.ws = null;
    }
  }

  private cleanup(): void {
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
  }

  sendAudio(audioChunk: Uint8Array): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(audioChunk);
    }
  }

  isConnected(): boolean {
    return this.ws !== null && this.ws.readyState === WebSocket.OPEN;
  }

  onMessage(callback: (data: VoiceResponse) => void): void {
    this.messageCallbacks.push(callback);
  }

  onError(callback: (error: string) => void): void {
    this.errorCallbacks.push(callback);
  }

  ping(): void {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send("ping");
    }
  }

  /**
   * Initialize browser audio capture and streaming
   */
  async startAudioCapture(onAudioData: (data: Uint8Array) => void): Promise<void> {
    try {
      // Check if browser supports Web Audio API
      if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        throw new Error(
          'Your browser does not support Web Audio API or microphone access. ' +
          'Please use a modern browser (Chrome, Firefox, Safari, Edge).'
        );
      }

      // Step 1: Get microphone stream FIRST (before creating AudioContext)
      console.log('📍 Requesting microphone access...');
      this.mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          echoCancellation: true,
          noiseSuppression: true,
          autoGainControl: false,
        },
      });

      if (!this.mediaStream) {
        throw new Error('Failed to get media stream from microphone');
      }
      console.log('✅ Microphone stream acquired');

      // Step 2: Now create AudioContext
      console.log('📍 Creating AudioContext...');
      if (!this.audioContext) {
        const AudioContextClass = window.AudioContext || (window as any).webkitAudioContext;
        if (!AudioContextClass) {
          throw new Error('AudioContext is not available in this browser');
        }

        // Try with sampleRate first
        try {
          this.audioContext = new AudioContextClass({ sampleRate: SAMPLE_RATE });
          console.log('✅ AudioContext created with sampleRate:', SAMPLE_RATE);
        } catch (e) {
          console.warn('⚠️ Failed to create with sampleRate, trying without:', e);
          try {
            this.audioContext = new AudioContextClass();
            console.log('✅ AudioContext created without sampleRate');
          } catch (e2) {
            throw new Error(`Failed to create AudioContext: ${e2 instanceof Error ? e2.message : String(e2)}`);
          }
        }
      }

      // Validate audioContext exists and is valid
      if (!this.audioContext) {
        throw new Error('AudioContext instance is null or undefined');
      }

      console.log('📍 AudioContext state:', this.audioContext.state);

      // Step 3: Resume audio context if needed
      if (this.audioContext.state === 'suspended') {
        console.log('📍 Resuming suspended AudioContext...');
        try {
          await this.audioContext.resume();
          console.log('✅ AudioContext resumed');
        } catch (err) {
          console.warn('⚠️ Failed to resume AudioContext:', err);
          // Continue anyway - might still work
        }
      }

      // Step 4: Create media stream source
      console.log('📍 Creating media stream source...');
      let source;
      try {
        source = this.audioContext.createMediaStreamSource(this.mediaStream);
        console.log('✅ Media stream source created');
      } catch (err) {
        throw new Error(`Failed to create media stream source: ${err instanceof Error ? err.message : String(err)}`);
      }

      // Step 5: Create script processor
      console.log('📍 Creating ScriptProcessor...');
      const bufferSize = 4096;
      try {
        this.processor = this.audioContext.createScriptProcessor(bufferSize, 1, 1);
        console.log('✅ ScriptProcessor created');
      } catch (err) {
        throw new Error(`Failed to create ScriptProcessor: ${err instanceof Error ? err.message : String(err)}`);
      }

      if (!this.processor) {
        throw new Error('ScriptProcessor instance is null');
      }

      // Step 6: Set up audio processing
      console.log('📍 Setting up audio processing...');
      this.processor.onaudioprocess = (event) => {
        const inputData = event.inputBuffer.getChannelData(0);
        const int16Data = new Int16Array(inputData.length);

        for (let i = 0; i < inputData.length; i++) {
          int16Data[i] = Math.max(-1, Math.min(1, inputData[i])) * 0x7fff;
        }

        onAudioData(new Uint8Array(int16Data.buffer));
      };

      source.connect(this.processor);
      this.processor.connect(this.audioContext.destination);
      this.isRecording = true;
      console.log('✅ Audio capture started successfully');
    } catch (error) {
      let errorMsg = 'Failed to start audio capture';

      if (error instanceof DOMException) {
        if (error.name === 'NotAllowedError') {
          errorMsg = 'Microphone access was denied. Please check your browser permissions.';
        } else if (error.name === 'NotFoundError') {
          errorMsg = 'No microphone device found.';
        } else if (error.name === 'NotReadableError') {
          errorMsg = 'Microphone is in use by another application.';
        } else if (error.name === 'SecurityError') {
          errorMsg = 'Microphone access blocked by browser security policy.';
        } else {
          errorMsg = `DOMException: ${error.message}`;
        }
      } else if (error instanceof Error) {
        errorMsg = error.message;
      }

      console.error('❌ Audio capture failed:', error);
      this.errorCallbacks.forEach((cb) => cb(errorMsg));
      this.cleanup();
      throw new Error(errorMsg);
    }
  }

  stopAudioCapture(): void {
    this.isRecording = false;
    if (this.processor) {
      this.processor.disconnect();
      this.processor = null;
    }
    if (this.mediaStream) {
      this.mediaStream.getTracks().forEach((track) => track.stop());
      this.mediaStream = null;
    }
    if (this.audioContext) {
      this.audioContext.close();
      this.audioContext = null;
    }
  }

  isAudioCapturing(): boolean {
    return this.isRecording;
  }
}

export const voiceApi = new VoiceApiClientImpl();

/**
 * Helper function to decode base64 audio and play it
 */
export async function playAudioResponse(base64Audio: string): Promise<void> {
  try {
    const binaryString = atob(base64Audio);
    const bytes = new Uint8Array(binaryString.length);
    for (let i = 0; i < binaryString.length; i++) {
      bytes[i] = binaryString.charCodeAt(i);
    }

    const audioContext = new (window.AudioContext ||
      (window as any).webkitAudioContext)();
    const audioBuffer = await audioContext.decodeAudioData(bytes.buffer);

    const source = audioContext.createBufferSource();
    source.buffer = audioBuffer;
    source.connect(audioContext.destination);
    source.start(0);

    return new Promise((resolve) => {
      source.onended = () => resolve();
    });
  } catch (error) {
    console.error("Failed to play audio:", error);
    throw error;
  }
}
