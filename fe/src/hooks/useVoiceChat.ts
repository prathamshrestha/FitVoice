import { useState, useCallback, useEffect } from 'react';
import { voiceApi, playAudioResponse, type VoiceResponse } from '@/services/voiceApiClient';

export interface UseVoiceChatOptions {
  onTranscription?: (text: string) => void;
  onEmotion?: (emotion: string) => void;
  onResponse?: (text: string) => void;
  onError?: (error: string) => void;
}

export const useVoiceChat = (options: UseVoiceChatOptions = {}) => {
  const [isConnected, setIsConnected] = useState(false);
  const [isListening, setIsListening] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Setup message and error handlers
  useEffect(() => {
    // Set up message handler
    voiceApi.onMessage(async (data: VoiceResponse) => {
      setIsProcessing(true);
      try {
        // Notify transcription
        if (options.onTranscription) {
          options.onTranscription(data.text);
        }

        // Notify emotion
        if (options.onEmotion) {
          options.onEmotion(data.emotion);
        }

        // Notify LLM response
        if (options.onResponse) {
          options.onResponse(data.llm_response);
        }

        // Play audio response
        if (data.audio) {
          await playAudioResponse(data.audio);
        }
      } catch (err) {
        const errorMsg = err instanceof Error ? err.message : String(err);
        setError(errorMsg);
        if (options.onError) {
          options.onError(errorMsg);
        }
      } finally {
        setIsProcessing(false);
      }
    });

    // Set up error handler
    voiceApi.onError((err) => {
      setError(err);
      if (options.onError) {
        options.onError(err);
      }
    });

    // Only disconnect on component unmount, not on re-runs
    return () => {
      // Don't disconnect the WebSocket here - let it persist
      // Only stop audio capture
      voiceApi.stopAudioCapture();
    };
  }, [options]);

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      voiceApi.stopAudioCapture();
      voiceApi.disconnect();
    };
  }, []);

  const startListening = useCallback(async () => {
    try {
      setError(null);
      
      // Only connect if not already connected
      if (!isConnected) {
        await voiceApi.connect();
        setIsConnected(true);
      }

      // Start capturing and sending audio
      await voiceApi.startAudioCapture((audioChunk) => {
        voiceApi.sendAudio(audioChunk);
      });

      setIsListening(true);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      setError(errorMsg);
      if (options.onError) {
        options.onError(errorMsg);
      }
    }
  }, [isConnected, options]);

  const stopListening = useCallback(() => {
    voiceApi.stopAudioCapture();
    setIsListening(false);
  }, []);

  const disconnect = useCallback(() => {
    stopListening();
    voiceApi.disconnect();
    setIsConnected(false);
  }, [stopListening]);

  return {
    isConnected,
    isListening,
    isProcessing,
    error,
    startListening,
    stopListening,
    disconnect,
  };
};
