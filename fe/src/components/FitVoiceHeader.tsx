import { Activity } from 'lucide-react';

export function FitVoiceHeader() {
  return (
    <header className="flex items-center gap-3 px-6 py-4 border-b border-border bg-card/50 backdrop-blur-md">
      <div className="w-10 h-10 rounded-xl bg-primary/15 border border-primary/30 flex items-center justify-center neon-glow">
        <Activity className="w-5 h-5 text-primary" />
      </div>
      <div>
        <h1 className="text-lg font-bold tracking-tight">
          Fit<span className="text-primary text-glow">Voice</span> AI
        </h1>
        <p className="text-xs text-muted-foreground">Your AI Fitness Coach</p>
      </div>
    </header>
  );
}
