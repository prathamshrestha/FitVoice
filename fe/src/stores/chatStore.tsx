import { useState, createContext, useContext, useCallback } from 'react';

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: Date;
  updatedAt: Date;
}

export interface ChatMessage {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatStoreContextType {
  sessions: ChatSession[];
  activeSessionId: string | null;
  createSession: () => string;
  addMessage: (sessionId: string, msg: Omit<ChatMessage, 'id' | 'timestamp'>) => void;
  getSession: (id: string) => ChatSession | undefined;
  deleteSession: (id: string) => void;
  setActiveSessionId: (id: string | null) => void;
}

const ChatStoreContext = createContext<ChatStoreContextType | null>(null);

export function ChatStoreProvider({ children }: { children: React.ReactNode }) {
  const [sessions, setSessions] = useState<ChatSession[]>([
    {
      id: 'demo-1',
      title: 'Breakfast nutrition check',
      messages: [
        { id: '1', role: 'user', content: 'I had two boiled eggs and a bowl of oatmeal for breakfast', timestamp: new Date(Date.now() - 3600000) },
        { id: '2', role: 'assistant', content: 'Great breakfast! **2 Boiled Eggs**: ~140 kcal, 12g protein. **Oatmeal**: ~150 kcal, 5g protein, 4g fiber. **Total: ~290 kcal, 17g protein.** 💪', timestamp: new Date(Date.now() - 3500000) },
      ],
      createdAt: new Date(Date.now() - 3600000),
      updatedAt: new Date(Date.now() - 3500000),
    },
    {
      id: 'demo-2',
      title: 'Workout routine advice',
      messages: [
        { id: '3', role: 'user', content: 'Recommend a full body workout for beginners', timestamp: new Date(Date.now() - 86400000) },
        { id: '4', role: 'assistant', content: 'Here\'s a beginner full body workout:\n\n1. **Squats** — 3×12\n2. **Push-ups** — 3×10\n3. **Lunges** — 3×10 each leg\n4. **Plank** — 3×30s\n\nRest 60s between sets. Do this 3x/week! 🔥', timestamp: new Date(Date.now() - 86300000) },
      ],
      createdAt: new Date(Date.now() - 86400000),
      updatedAt: new Date(Date.now() - 86300000),
    },
    {
      id: 'demo-3',
      title: 'High fiber meal ideas',
      messages: [
        { id: '5', role: 'user', content: 'How much fiber is in oatmeal and how can I get more?', timestamp: new Date(Date.now() - 172800000) },
        { id: '6', role: 'assistant', content: 'One cup of cooked oatmeal has ~**4g fiber** (14% daily). Boost it with:\n- Chia seeds (+5g/tbsp)\n- Blueberries (+1.8g)\n- Flaxseeds (+2g/tbsp)', timestamp: new Date(Date.now() - 172700000) },
      ],
      createdAt: new Date(Date.now() - 172800000),
      updatedAt: new Date(Date.now() - 172700000),
    },
  ]);
  const [activeSessionId, setActiveSessionId] = useState<string | null>(null);

  const createSession = useCallback(() => {
    const id = Date.now().toString();
    const session: ChatSession = {
      id,
      title: 'New conversation',
      messages: [],
      createdAt: new Date(),
      updatedAt: new Date(),
    };
    setSessions(prev => [session, ...prev]);
    setActiveSessionId(id);
    return id;
  }, []);

  const addMessage = useCallback((sessionId: string, msg: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    setSessions(prev => prev.map(s => {
      if (s.id !== sessionId) return s;
      const newMsg: ChatMessage = { ...msg, id: Date.now().toString(), timestamp: new Date() };
      const title = s.messages.length === 0 && msg.role === 'user'
        ? msg.content.slice(0, 50) + (msg.content.length > 50 ? '...' : '')
        : s.title;
      return { ...s, title, messages: [...s.messages, newMsg], updatedAt: new Date() };
    }));
  }, []);

  const getSession = useCallback((id: string) => sessions.find(s => s.id === id), [sessions]);

  const deleteSession = useCallback((id: string) => {
    setSessions(prev => prev.filter(s => s.id !== id));
    setActiveSessionId(prev => prev === id ? null : prev);
  }, []);

  return (
    <ChatStoreContext.Provider value={{ sessions, activeSessionId, createSession, addMessage, getSession, deleteSession, setActiveSessionId }}>
      {children}
    </ChatStoreContext.Provider>
  );
}

export function useChatStore() {
  const ctx = useContext(ChatStoreContext);
  if (!ctx) throw new Error('useChatStore must be used within ChatStoreProvider');
  return ctx;
}
