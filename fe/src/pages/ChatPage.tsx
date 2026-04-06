import { useState, useRef, useEffect, useCallback, useMemo } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Send, Search, Plus, MessageSquare, PanelLeftClose, PanelLeft, Clock, AlertCircle, X } from 'lucide-react';
import { ChatMessage } from '@/components/ChatMessage';
import { VoiceButton } from '@/components/VoiceButton';
import { WaveformVisualizer } from '@/components/WaveformVisualizer';
import { useVoiceChat } from '@/hooks/useVoiceChat';
import { useChatStore, type ChatSession } from '@/stores/chatStore';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

export default function ChatPage() {
  const [searchParams] = useSearchParams();
  const { sessions, activeSessionId, createSession, addMessage, setActiveSessionId } = useChatStore();
  const [textInput, setTextInput] = useState('');
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarSearch, setSidebarSearch] = useState('');
  const [transcript, setTranscript] = useState('');
  const [ragDebug, setRagDebug] = useState<any>(null);
  const scrollRef = useRef<HTMLDivElement>(null);
  const [dismissedError, setDismissedError] = useState(false);

  // Initialize session from URL or create new — only on mount / URL change
  useEffect(() => {
    const urlSession = searchParams.get('session');
    if (urlSession && sessions.find(s => s.id === urlSession)) {
      setActiveSessionId(urlSession);
    } else if (!activeSessionId) {
      createSession();
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [searchParams]);

  const currentSession = sessions.find(s => s.id === activeSessionId);

  const filteredSessions = sessions.filter(s =>
    s.title.toLowerCase().includes(sidebarSearch.toLowerCase()) ||
    s.messages.some(m => m.content.toLowerCase().includes(sidebarSearch.toLowerCase()))
  );

  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = scrollRef.current.scrollHeight;
    }
  }, [currentSession?.messages]);

// Use voice chat hook for backend integration
  const handleTranscription = useCallback((text: string) => {
    setTranscript(text);
    // Automatically add user's transcribed message to chat
    if (activeSessionId) {
      addMessage(activeSessionId, { role: 'user', content: text });
    }
  }, [activeSessionId, addMessage]);



  const handleResponse = useCallback((response: string) => {
    // Add assistant's response to chat
    if (activeSessionId) {
      addMessage(activeSessionId, { role: 'assistant', content: response });
    }
  }, [activeSessionId, addMessage]);

  const handleError = useCallback((err: string) => {
    console.error('Voice error:', err);
    if (activeSessionId) {
      addMessage(activeSessionId, {
        role: 'assistant',
        content: `❌ Voice error: ${err}`,
      });
    }
  }, [activeSessionId, addMessage]);

  const handleRagDebug = useCallback((debug: any) => {
    setRagDebug(debug);
  }, []);

  // Memoize options to prevent hook re-runs
  const voiceChatOptions = useMemo(
    () => ({
      sessionId: activeSessionId ?? undefined,
      onTranscription: handleTranscription,
      onResponse: handleResponse,
      onError: handleError,
      onRagDebug: handleRagDebug,
    }),
    [activeSessionId, handleTranscription, handleResponse, handleError, handleRagDebug]
  );

  const {
    isListening,
    isProcessing: isVoiceProcessing,
    error: voiceError,
    startListening,
    stopListening,
    disconnect,
  } = useVoiceChat(voiceChatOptions);

  const handleVoiceToggle = useCallback(() => {
    console.log('🔽 Voice button clicked, isListening:', isListening);
    if (isListening) {
      console.log('⏹️ Ending call — disconnecting WebSocket + stopping audio');
      disconnect();
    } else {
      console.log('▶️ Starting voice listener');
      setDismissedError(false); // Reset error when trying again
      setTranscript('');
      setRagDebug(null);
      startListening();
    }
  }, [isListening, startListening, disconnect]);

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (textInput.trim() && activeSessionId) {
      // Add user message to chat
      addMessage(activeSessionId, { role: 'user', content: textInput.trim() });
      setTextInput('');
      // TODO: Send text message to backend if text-to-speech is needed
    }
  };

  const formatDate = (date: Date | string) => {
    try {
      const d = date instanceof Date ? date : new Date(date);
      if (isNaN(d.getTime())) return '';
      const diff = Date.now() - d.getTime();
      const hours = Math.floor(diff / 3600000);
      if (hours < 1) return 'Just now';
      if (hours < 24) return `${hours}h ago`;
      return `${Math.floor(hours / 24)}d ago`;
    } catch {
      return '';
    }
  };

  return (
    <div className="flex h-screen pt-16 bg-background">
      {/* Sidebar */}
      <div className={`border-r border-border bg-card/50 transition-all duration-300 flex flex-col ${sidebarOpen ? 'w-80' : 'w-0 overflow-hidden'}`}>
        <div className="p-4 border-b border-border">
          <Button onClick={() => createSession()} className="w-full bg-primary text-primary-foreground hover:bg-primary/80 gap-2 mb-3">
            <Plus className="w-4 h-4" /> New Chat
          </Button>
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-3.5 h-3.5 text-muted-foreground" />
            <Input
              value={sidebarSearch}
              onChange={e => setSidebarSearch(e.target.value)}
              placeholder="Search chats..."
              className="pl-9 h-9 text-sm bg-secondary border-border"
            />
          </div>
        </div>
        <ScrollArea className="flex-1">
          <div className="p-2 space-y-1">
            {filteredSessions.map(session => (
              <button
                key={session.id}
                onClick={() => setActiveSessionId(session.id)}
                className={`w-full text-left p-3 rounded-lg transition-all ${
                  session.id === activeSessionId
                    ? 'bg-primary/10 border border-primary/20'
                    : 'hover:bg-secondary border border-transparent'
                }`}
              >
                <div className="flex items-center gap-2 mb-1">
                  <MessageSquare className="w-3.5 h-3.5 text-primary shrink-0" />
                  <span className="text-sm font-medium truncate">{session.title}</span>
                </div>
                <div className="flex items-center gap-2 pl-5.5">
                  <Clock className="w-3 h-3 text-muted-foreground" />
                  <span className="text-xs text-muted-foreground">{formatDate(session.updatedAt)}</span>
                </div>
              </button>
            ))}
          </div>
        </ScrollArea>
      </div>

      {/* Main chat */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Chat header */}
        <div className="flex items-center gap-3 px-4 py-3 border-b border-border bg-card/30">
          <button onClick={() => setSidebarOpen(!sidebarOpen)} className="p-2 rounded-lg hover:bg-secondary text-muted-foreground">
            {sidebarOpen ? <PanelLeftClose className="w-4 h-4" /> : <PanelLeft className="w-4 h-4" />}
          </button>
          <div>
            <h2 className="text-sm font-semibold truncate">{currentSession?.title || 'New conversation'}</h2>
            <p className="text-xs text-muted-foreground">{currentSession?.messages.length || 0} messages</p>
          </div>
        </div>

        {/* Messages */}
        <ScrollArea className="flex-1 px-4 py-4" ref={scrollRef}>
          <div className="space-y-4 pb-4 max-w-2xl mx-auto">
            {(!currentSession || currentSession.messages.length === 0) && (
              <div className="text-center py-16">
                <div className="w-16 h-16 rounded-2xl bg-primary/10 border border-primary/20 flex items-center justify-center mx-auto mb-4 neon-glow">
                  <MessageSquare className="w-8 h-8 text-primary" />
                </div>
                <h3 className="text-lg font-semibold mb-2">Start a Conversation</h3>
                <p className="text-sm text-muted-foreground max-w-sm mx-auto">
                  Ask me about nutrition, workouts, or health tips. Try: "I had two boiled eggs and oatmeal for breakfast"
                </p>
              </div>
            )}
            {currentSession?.messages.map(msg => (
              <ChatMessage key={msg.id} message={{ ...msg, timestamp: new Date(msg.timestamp) }} />
            ))}
            {isVoiceProcessing && (
              <div className="flex gap-3">
                <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center">
                  <div className="w-2 h-2 rounded-full bg-primary animate-pulse" />
                </div>
                <div className="bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '150ms' }} />
                    <div className="w-2 h-2 rounded-full bg-muted-foreground animate-bounce" style={{ animationDelay: '300ms' }} />
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        {/* Transcript + RAG Debug */}
        {(transcript || ragDebug) && (
          <div className="px-6 py-2 bg-card/80 border-t border-border">
            <div className="max-w-2xl mx-auto">
              {transcript && (
                <p className="text-sm text-muted-foreground italic truncate">"{transcript}"</p>
              )}
              {ragDebug && (
                <div className="flex items-center gap-2 mt-1 flex-wrap">
                  <span className={`inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium ${
                    ragDebug.rag_used 
                      ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/20' 
                      : 'bg-amber-500/10 text-amber-400 border border-amber-500/20'
                  }`}>
                    {ragDebug.rag_used ? '✅' : '⚠️'} RAG {ragDebug.rag_used ? 'Active' : 'Inactive'}
                  </span>
                  {ragDebug.rag_used && (
                    <>
                      <span className="text-xs text-muted-foreground">
                        {ragDebug.num_docs} docs · {ragDebug.context_length} chars
                      </span>
                      {ragDebug.sources?.slice(0, 3).map((src: any, i: number) => (
                        <span key={i} className="inline-flex items-center px-2 py-0.5 rounded-full text-xs bg-primary/10 text-primary border border-primary/20">
                          {Math.round(src.relevance * 100)}% {src.title.substring(0, 25)}{src.title.length > 25 ? '...' : ''}
                        </span>
                      ))}
                    </>
                  )}
                </div>
              )}
            </div>
          </div>
        )}

        {/* Input area */}
        <div className="border-t border-border bg-card/30 backdrop-blur-md px-6 py-4">
          <div className="max-w-2xl mx-auto">
            {/* Error Banner */}
            {voiceError && !dismissedError && (
              <div className="bg-destructive/10 border border-destructive/30 rounded-lg px-4 py-3 mb-3 flex items-start gap-3">
                <AlertCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
                <div className="flex-1 min-w-0">
                  <p className="text-sm text-destructive font-medium">Microphone Error</p>
                  <p className="text-xs text-destructive/80 mt-1">{voiceError}</p>
                  <p className="text-xs text-muted-foreground mt-2">
                    💡 <strong>Tip:</strong> Make sure to grant microphone permission in your browser settings. Refresh the page and try again.
                  </p>
                </div>
                <button
                  onClick={() => setDismissedError(true)}
                  className="flex-shrink-0 text-destructive/60 hover:text-destructive transition-colors"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            )}

            <WaveformVisualizer active={isListening || isVoiceProcessing} />
            <div className="flex items-center gap-4 mt-2">
              <VoiceButton
                isListening={isListening}
                isSpeaking={isVoiceProcessing}
                onToggle={handleVoiceToggle}
              />
              <form onSubmit={handleTextSubmit} className="flex-1 flex gap-2">
                <Input
                  value={textInput}
                  onChange={e => setTextInput(e.target.value)}
                  placeholder="Type your question..."
                  className="bg-secondary border-border text-foreground placeholder:text-muted-foreground"
                  disabled={isListening}
                />
                <Button
                  type="submit"
                  size="icon"
                  disabled={!textInput.trim() || isListening}
                  className="bg-primary text-primary-foreground hover:bg-primary/80 shrink-0"
                >
                  <Send className="w-4 h-4" />
                </Button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
