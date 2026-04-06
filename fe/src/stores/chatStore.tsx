import { useState, createContext, useContext, useCallback, useEffect } from 'react';

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

// --- localStorage helpers ---
const STORAGE_KEY = 'fitvoice_chat_sessions';
const ACTIVE_SESSION_KEY = 'fitvoice_active_session';

interface StoredSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  createdAt: string;
  updatedAt: string;
}

function loadSessions(): ChatSession[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (!raw) return [];
    const parsed: StoredSession[] = JSON.parse(raw);
    return parsed.map(s => ({
      ...s,
      createdAt: new Date(s.createdAt),
      updatedAt: new Date(s.updatedAt),
      messages: s.messages.map(m => ({
        ...m,
        timestamp: new Date(m.timestamp),
      })),
    }));
  } catch {
    return [];
  }
}

function saveSessions(sessions: ChatSession[]): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(sessions));
  } catch {
    console.warn('Failed to save chat sessions to localStorage');
  }
}

function loadActiveSessionId(): string | null {
  return localStorage.getItem(ACTIVE_SESSION_KEY);
}

function saveActiveSessionId(id: string | null): void {
  if (id) {
    localStorage.setItem(ACTIVE_SESSION_KEY, id);
  } else {
    localStorage.removeItem(ACTIVE_SESSION_KEY);
  }
}

// --- Context ---
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
  const [sessions, setSessions] = useState<ChatSession[]>(() => loadSessions());
  const [activeSessionId, setActiveSessionIdState] = useState<string | null>(() => loadActiveSessionId());

  // Persist sessions to localStorage whenever they change
  useEffect(() => {
    saveSessions(sessions);
  }, [sessions]);

  // Persist active session ID
  const setActiveSessionId = useCallback((id: string | null) => {
    setActiveSessionIdState(id);
    saveActiveSessionId(id);
  }, []);

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
  }, [setActiveSessionId]);

  const addMessage = useCallback((sessionId: string, msg: Omit<ChatMessage, 'id' | 'timestamp'>) => {
    if (!msg.content) return; // Guard against undefined content
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
    setActiveSessionIdState(prev => {
      const newId = prev === id ? null : prev;
      saveActiveSessionId(newId);
      return newId;
    });
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
