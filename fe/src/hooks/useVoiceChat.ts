import { useState, useCallback, useEffect } from 'react';
import { voiceApi, playAudioResponse, type VoiceResponse } from '@/services/voiceApiClient';

export interface UseVoiceChatOptions {
  onTranscription?: (text: string) => void;
  onResponse?: (text: string) => void;
  onError?: (error: string) => void;
  onRagDebug?: (debug: any) => void;
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

        // Log RAG debug info to console
        if (data.rag_debug) {
          const rd = data.rag_debug;
          console.log(
            `📚 RAG: ${rd.rag_used ? '✅ USED' : '❌ NOT USED'} | ` +
            `${rd.num_docs} docs | ${rd.context_length} chars`,
            rd.sources
          );
          if (options.onRagDebug) {
            options.onRagDebug(data.rag_debug);
          }
        }

        // Notify LLM response
        if (options.onResponse) {
          options.onResponse(data.llm_response);
        }

        // Play audio response (mic stays active — barge-in enabled)
        if (data.audio) {
          voiceApi.setPlayingAudio(true);
          playAudioResponse(data.audio)
            .catch((err) => console.error('Audio playback error:', err))
            .finally(() => voiceApi.setPlayingAudio(false));
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
      console.log('🎤 startListening called');
      setError(null);
      
      // Only connect if not already connected
      if (!isConnected) {
        console.log('🔌 Connecting to voice API...');
        await voiceApi.connect();
        setIsConnected(true);
        console.log('✅ Voice API connected');
      } else {
        console.log('✅ Already connected to voice API');
      }

      // Start capturing and sending audio
      console.log('🎙️ Starting audio capture...');
      await voiceApi.startAudioCapture((audioChunk) => {
        voiceApi.sendAudio(audioChunk);
      });
      console.log('✅ Audio capture started');

      setIsListening(true);
    } catch (err) {
      const errorMsg = err instanceof Error ? err.message : String(err);
      console.error('❌ Voice error:', errorMsg);
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
