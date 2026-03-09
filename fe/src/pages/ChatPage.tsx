import { useState, useRef, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Send, Search, Plus, MessageSquare, PanelLeftClose, PanelLeft, Clock } from 'lucide-react';
import { ChatMessage } from '@/components/ChatMessage';
import { VoiceButton } from '@/components/VoiceButton';
import { WaveformVisualizer } from '@/components/WaveformVisualizer';
import { useSpeechRecognition } from '@/hooks/useSpeechRecognition';
import { useTextToSpeech } from '@/hooks/useTextToSpeech';
import { useChatStore, type ChatSession } from '@/stores/chatStore';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';

async function getAIResponse(messages: { role: string; content: string }[]): Promise<string> {
  const lastMsg = messages[messages.length - 1]?.content.toLowerCase() || '';
  await new Promise(r => setTimeout(r, 800));

  if (lastMsg.includes('egg') || lastMsg.includes('oatmeal') || lastMsg.includes('breakfast')) {
    return `Great breakfast choice! Here's the nutritional breakdown:\n\n🥚 **2 Boiled Eggs**\n- Calories: ~140 kcal\n- Protein: 12g\n- Fat: 10g\n\n🥣 **1 Bowl of Oatmeal** (~1 cup cooked)\n- Calories: ~150 kcal\n- Protein: 5g\n- Carbs: 27g\n- Fiber: 4g\n\n**Total: ~290 kcal | 17g protein | 4g fiber**\n\nThis is a solid, balanced breakfast! 💪`;
  }
  if (lastMsg.includes('fiber')) {
    return `One cup of cooked oatmeal contains approximately **4g of fiber**, which is about **14% of your daily recommended intake** (28g/day).\n\nTo boost fiber, you can add:\n- 🫐 Blueberries (+1.8g)\n- 🥜 Chia seeds (+5g per tbsp)\n- 🍌 Banana (+3g)\n\nWant me to suggest a high-fiber meal plan?`;
  }
  if (lastMsg.includes('workout') || lastMsg.includes('gym') || lastMsg.includes('exercise') || lastMsg.includes('recommend')) {
    return `### 🏋️ Full Body Workout (45 min)\n\n**Warm-up** (5 min)\n- Jumping jacks, arm circles\n\n**Strength** (30 min)\n1. Squats — 3×12\n2. Push-ups — 3×15\n3. Dumbbell rows — 3×10\n4. Lunges — 3×10 each leg\n5. Plank — 3×45s\n\n**Cool-down** (10 min)\n- Stretching + deep breathing\n\nPairs well with a protein-rich meal! 🔥`;
  }
  return `I'm here to help with your fitness and nutrition goals! You can ask me about:\n\n- 🍽️ **Meal nutrition** — "What's in 2 eggs and oatmeal?"\n- 🏋️ **Workouts** — "Recommend a workout routine"\n- 💊 **Health tips** — "How can I get more fiber?"\n- 📊 **Calorie tracking** — "How many calories in my lunch?"\n\nJust speak or type your question!`;
}

export default function ChatPage() {
  const [searchParams] = useSearchParams();
  const { sessions, activeSessionId, createSession, addMessage, setActiveSessionId } = useChatStore();
  const [textInput, setTextInput] = useState('');
  const [isProcessing, setIsProcessing] = useState(false);
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [sidebarSearch, setSidebarSearch] = useState('');
  const scrollRef = useRef<HTMLDivElement>(null);

  const { isListening, transcript, startListening, stopListening } = useSpeechRecognition();
  const { isSpeaking, speak, stop: stopSpeaking } = useTextToSpeech();

  // Initialize session from URL or create new
  useEffect(() => {
    const urlSession = searchParams.get('session');
    if (urlSession && sessions.find(s => s.id === urlSession)) {
      setActiveSessionId(urlSession);
    } else if (!activeSessionId) {
      createSession();
    }
  }, [searchParams, sessions, activeSessionId, createSession, setActiveSessionId]);

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

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isProcessing || !activeSessionId) return;

    addMessage(activeSessionId, { role: 'user', content: content.trim() });
    setIsProcessing(true);

    try {
      const session = sessions.find(s => s.id === activeSessionId);
      const history = session ? session.messages.map(m => ({ role: m.role, content: m.content })) : [];
      history.push({ role: 'user', content: content.trim() });

      const response = await getAIResponse(history);
      addMessage(activeSessionId, { role: 'assistant', content: response });
      speak(response.replace(/[*#🥚🥣💪🫐🥜🍌🏋️🔥🍽️💊📊]/g, '').replace(/\n/g, '. '));
    } catch {
      addMessage(activeSessionId, { role: 'assistant', content: "Sorry, I couldn't process that. Please try again!" });
    } finally {
      setIsProcessing(false);
    }
  }, [activeSessionId, isProcessing, sessions, addMessage, speak]);

  const handleVoiceToggle = useCallback(() => {
    if (isListening) {
      stopListening();
      if (transcript.trim()) sendMessage(transcript);
    } else {
      stopSpeaking();
      startListening();
    }
  }, [isListening, transcript, stopListening, startListening, sendMessage, stopSpeaking]);

  const handleTextSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    sendMessage(textInput);
    setTextInput('');
  };

  const formatDate = (date: Date) => {
    const diff = Date.now() - date.getTime();
    const hours = Math.floor(diff / 3600000);
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    return `${Math.floor(hours / 24)}d ago`;
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
            {isProcessing && (
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

        {/* Transcript */}
        {isListening && transcript && (
          <div className="px-6 py-2 bg-card/80 border-t border-border">
            <p className="text-sm text-muted-foreground italic truncate max-w-2xl mx-auto">"{transcript}"</p>
          </div>
        )}

        {/* Input area */}
        <div className="border-t border-border bg-card/30 backdrop-blur-md px-6 py-4">
          <div className="max-w-2xl mx-auto">
            <WaveformVisualizer active={isListening || isSpeaking} />
            <div className="flex items-center gap-4 mt-2">
              <VoiceButton isListening={isListening} isSpeaking={isSpeaking} onToggle={handleVoiceToggle} />
              <form onSubmit={handleTextSubmit} className="flex-1 flex gap-2">
                <Input
                  value={textInput}
                  onChange={e => setTextInput(e.target.value)}
                  placeholder="Type your question..."
                  className="bg-secondary border-border text-foreground placeholder:text-muted-foreground"
                  disabled={isProcessing}
                />
                <Button type="submit" size="icon" disabled={!textInput.trim() || isProcessing} className="bg-primary text-primary-foreground hover:bg-primary/80 shrink-0">
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
