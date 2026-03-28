"""
Google Cloud Speech-to-Text ASR Module
Replaces Whisper for speech recognition in FitVoice

Requires:
    pip install google-cloud-speech
    
Authentication (one of):
    - Set GOOGLE_APPLICATION_CREDENTIALS env var to service account JSON path
    - Run: gcloud auth application-default login
"""

# Set environment variable for Google Cloud credentials
import os
_this_dir = os.path.dirname(os.path.abspath(__file__))
_key_path = os.path.join(_this_dir, "googleasr_key.json")
if os.path.exists(_key_path):
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = _key_path
else:
    print(f"⚠️ Google ASR key not found at {_key_path}")

import asyncio
import numpy as np
from typing import Optional

try:
    from google.cloud import speech
    GOOGLE_SPEECH_AVAILABLE = True
except ImportError:
    GOOGLE_SPEECH_AVAILABLE = False
    print("⚠️ google-cloud-speech not installed. Install with: pip install google-cloud-speech")


class GoogleASR:
    """Google Cloud Speech-to-Text wrapper for FitVoice"""
    
    def __init__(self, language_code: str = "en-US", sample_rate: int = 16000):
        """
        Initialize Google Cloud Speech-to-Text client.
        
        Args:
            language_code: BCP-47 language code (default: en-US)
            sample_rate: Audio sample rate in Hz (default: 16000)
        """
        if not GOOGLE_SPEECH_AVAILABLE:
            raise RuntimeError(
                "google-cloud-speech not installed. "
                "Install with: pip install google-cloud-speech"
            )
        
        self.client = speech.SpeechClient()
        self.sample_rate = sample_rate
        
        # Configure recognition for LINEAR16 (raw PCM Int16)
        self.config = speech.RecognitionConfig(
            encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
            sample_rate_hertz=sample_rate,
            language_code=language_code,
            # Enhanced settings for fitness/health vocabulary
            model="latest_long",  # Best accuracy for varied content
            enable_automatic_punctuation=True,
            audio_channel_count=1,
        )
        
        print(f"✅ Google ASR initialized (lang={language_code}, rate={sample_rate}Hz)")
    
    def transcribe(self, audio_bytes: bytes) -> str:
        """
        Transcribe raw PCM Int16 audio bytes.
        
        Args:
            audio_bytes: Raw PCM Int16 mono audio at configured sample rate
            
        Returns:
            Transcription text string (empty string if no speech detected)
        """
        if not audio_bytes:
            return ""
        
        audio = speech.RecognitionAudio(content=audio_bytes)
        
        try:
            response = self.client.recognize(config=self.config, audio=audio)
        except Exception as e:
            print(f"❌ Google ASR error: {e}")
            return ""
        
        # Concatenate all result transcripts
        transcript = ""
        for result in response.results:
            if result.alternatives:
                transcript += result.alternatives[0].transcript
        
        return transcript.strip()
    
    def transcribe_np(self, audio_np: np.ndarray) -> str:
        """
        Transcribe from numpy float32 array ([-1, 1] range).
        Converts to Int16 PCM bytes internally.
        
        Args:
            audio_np: Float32 numpy array in [-1, 1] range
            
        Returns:
            Transcription text string
        """
        # Convert float32 [-1,1] to Int16 PCM bytes
        audio_int16 = (audio_np * 32768.0).astype(np.int16)
        return self.transcribe(audio_int16.tobytes())
    
    async def transcribe_async(self, audio_bytes: bytes) -> str:
        """
        Async version — runs transcribe in a thread to avoid blocking.
        
        Args:
            audio_bytes: Raw PCM Int16 mono audio
            
        Returns:
            Transcription text string
        """
        return await asyncio.to_thread(self.transcribe, audio_bytes)
    
    async def transcribe_np_async(self, audio_np: np.ndarray) -> str:
        """
        Async version for numpy input.
        
        Args:
            audio_np: Float32 numpy array in [-1, 1] range
            
        Returns:
            Transcription text string
        """
        return await asyncio.to_thread(self.transcribe_np, audio_np)
