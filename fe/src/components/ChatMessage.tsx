import ReactMarkdown from 'react-markdown';
import { Bot, User } from 'lucide-react';

export interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatMessageProps {
  message: Message;
}

export function ChatMessage({ message }: ChatMessageProps) {
  const isUser = message.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-full flex items-center justify-center shrink-0 ${
        isUser ? 'bg-secondary' : 'bg-primary/20 border border-primary/30'
      }`}>
        {isUser ? <User className="w-4 h-4 text-foreground" /> : <Bot className="w-4 h-4 text-primary" />}
      </div>
      <div className={`max-w-[80%] rounded-2xl px-4 py-3 ${
        isUser
          ? 'bg-secondary text-foreground rounded-tr-sm'
          : 'bg-card border border-border rounded-tl-sm'
      }`}>
        <div className="prose prose-sm prose-invert max-w-none text-sm leading-relaxed">
          <ReactMarkdown>{message.content}</ReactMarkdown>
        </div>
        <span className="text-[10px] text-muted-foreground mt-1 block">
          {message.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
        </span>
      </div>
    </div>
  );
}
