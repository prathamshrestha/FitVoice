import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Search, MessageSquare, Plus, Trash2, Clock } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import { ScrollArea } from '@/components/ui/scroll-area';
import { useChatStore } from '@/stores/chatStore';

export default function Dashboard() {
  const { sessions, createSession, deleteSession } = useChatStore();
  const [search, setSearch] = useState('');

  const filtered = sessions.filter(s =>
    s.title.toLowerCase().includes(search.toLowerCase()) ||
    s.messages.some(m => m.content.toLowerCase().includes(search.toLowerCase()))
  );

  const handleNewChat = () => {
    createSession();
  };

  const formatDate = (date: Date) => {
    const now = new Date();
    const diff = now.getTime() - date.getTime();
    const hours = Math.floor(diff / 3600000);
    if (hours < 1) return 'Just now';
    if (hours < 24) return `${hours}h ago`;
    const days = Math.floor(hours / 24);
    if (days === 1) return 'Yesterday';
    return `${days}d ago`;
  };

  return (
    <div className="min-h-screen bg-background pt-16">
      <div className="max-w-4xl mx-auto px-6 py-10">
        {/* Header */}
        <div className="flex items-center justify-between mb-8">
          <div>
            <h1 className="text-3xl font-bold">Dashboard</h1>
            <p className="text-muted-foreground mt-1">Your conversation history with FitVoice AI</p>
          </div>
          <Link to="/chat">
            <Button onClick={handleNewChat} className="bg-primary text-primary-foreground hover:bg-primary/80 neon-glow gap-2">
              <Plus className="w-4 h-4" /> New Chat
            </Button>
          </Link>
        </div>

        {/* Search */}
        <div className="relative mb-6">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <Input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search conversations..."
            className="pl-10 bg-card border-border text-foreground placeholder:text-muted-foreground"
          />
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-8">
          {[
            { label: 'Total Chats', value: sessions.length },
            { label: 'Messages', value: sessions.reduce((a, s) => a + s.messages.length, 0) },
            { label: 'This Week', value: sessions.filter(s => Date.now() - s.createdAt.getTime() < 604800000).length },
          ].map(({ label, value }) => (
            <div key={label} className="bg-card border border-border rounded-xl p-4 text-center">
              <div className="text-2xl font-bold text-primary">{value}</div>
              <div className="text-xs text-muted-foreground mt-1">{label}</div>
            </div>
          ))}
        </div>

        {/* Chat list */}
        <ScrollArea className="h-[calc(100vh-380px)]">
          <div className="space-y-3">
            {filtered.length === 0 ? (
              <div className="text-center py-16">
                <MessageSquare className="w-12 h-12 text-muted-foreground/30 mx-auto mb-3" />
                <p className="text-muted-foreground">{search ? 'No matching conversations' : 'No conversations yet'}</p>
                <Link to="/chat">
                  <Button variant="outline" className="mt-4 border-border text-foreground hover:bg-secondary gap-2">
                    <Plus className="w-4 h-4" /> Start your first chat
                  </Button>
                </Link>
              </div>
            ) : (
              filtered.map(session => (
                <Link
                  key={session.id}
                  to={`/chat?session=${session.id}`}
                  className="block bg-card border border-border rounded-xl p-4 hover:border-primary/30 transition-all group"
                >
                  <div className="flex items-start justify-between gap-3">
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <MessageSquare className="w-4 h-4 text-primary shrink-0" />
                        <h3 className="font-medium truncate">{session.title}</h3>
                      </div>
                      {session.messages.length > 0 && (
                        <p className="text-sm text-muted-foreground truncate pl-6">
                          {session.messages[session.messages.length - 1].content.replace(/[*#]/g, '').slice(0, 80)}
                        </p>
                      )}
                      <div className="flex items-center gap-3 mt-2 pl-6">
                        <span className="text-xs text-muted-foreground flex items-center gap-1">
                          <Clock className="w-3 h-3" /> {formatDate(session.updatedAt)}
                        </span>
                        <span className="text-xs text-muted-foreground">
                          {session.messages.length} messages
                        </span>
                      </div>
                    </div>
                    <button
                      onClick={(e) => { e.preventDefault(); e.stopPropagation(); deleteSession(session.id); }}
                      className="opacity-0 group-hover:opacity-100 p-2 rounded-lg hover:bg-destructive/10 text-muted-foreground hover:text-destructive transition-all"
                    >
                      <Trash2 className="w-4 h-4" />
                    </button>
                  </div>
                </Link>
              ))
            )}
          </div>
        </ScrollArea>
      </div>
    </div>
  );
}
