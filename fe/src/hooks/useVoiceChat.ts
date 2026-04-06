import { useState, useCallback, useEffect, useRef } from 'react';
import { voiceApi, playAudioResponse, type VoiceResponse } from '@/services/voiceApiClient';

export interface UseVoiceChatOptions {
  sessionId?: string;
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

  // Use refs for callbacks to avoid re-running the effect when they change
  const optionsRef = useRef(options);
  optionsRef.current = options;

  // Setup message and error handlers — runs ONCE on mount
  useEffect(() => {
    // Set up message handler
    voiceApi.onMessage(async (data: VoiceResponse) => {
      // Skip info/control messages (like session_id_set, user_id_set)
      if (!data.text && !data.llm_response) {
        console.log('📍 Info message received:', data);
        return;
      }

      setIsProcessing(true);
      try {
        const opts = optionsRef.current;

        // Notify transcription
        if (opts.onTranscription && data.text) {
          opts.onTranscription(data.text);
        }

        // Log RAG debug info to console
        if (data.rag_debug) {
          const rd = data.rag_debug;
          console.log(
            `📚 RAG: ${rd.rag_used ? '✅ USED' : '❌ NOT USED'} | ` +
            `${rd.num_docs} docs | ${rd.context_length} chars`,
            rd.sources
          );
          if (opts.onRagDebug) {
            opts.onRagDebug(data.rag_debug);
          }
        }

        // Notify LLM response
        if (opts.onResponse) {
          opts.onResponse(data.llm_response);
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
        const opts = optionsRef.current;
        if (opts.onError) {
          opts.onError(errorMsg);
        }
      } finally {
        setIsProcessing(false);
      }
    });

    // Set up error handler
    voiceApi.onError((err) => {
      setError(err);
      const opts = optionsRef.current;
      if (opts.onError) {
        opts.onError(err);
      }
    });

    // Cleanup on unmount only
    return () => {
      voiceApi.stopAudioCapture();
      voiceApi.disconnect();
    };
  }, []); // Empty deps — runs once

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

      // Send session ID for conversation memory
      const sid = optionsRef.current.sessionId;
      if (sid) {
        voiceApi.sendSessionId(sid);
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
      const opts = optionsRef.current;
      if (opts.onError) {
        opts.onError(errorMsg);
      }
    }
  }, [isConnected]);

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
