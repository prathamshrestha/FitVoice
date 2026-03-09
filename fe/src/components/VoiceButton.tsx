import { Mic, MicOff } from 'lucide-react';

interface VoiceButtonProps {
  isListening: boolean;
  isSpeaking: boolean;
  onToggle: () => void;
}

export function VoiceButton({ isListening, isSpeaking, onToggle }: VoiceButtonProps) {
  return (
    <div className="flex flex-col items-center gap-3">
      <div className="relative">
        {isListening && (
          <>
            <div className="absolute inset-0 rounded-full bg-primary/20 animate-pulse-ring scale-150" />
            <div className="absolute inset-0 rounded-full bg-primary/10 animate-pulse-ring scale-[1.8]" style={{ animationDelay: '0.3s' }} />
          </>
        )}
        <button
          onClick={onToggle}
          className={`relative z-10 w-20 h-20 rounded-full flex items-center justify-center transition-all duration-300 ${
            isListening
              ? 'bg-primary neon-glow-strong'
              : 'bg-secondary hover:bg-secondary/80 border border-border'
          }`}
        >
          {isListening ? (
            <MicOff className="w-8 h-8 text-primary-foreground" />
          ) : (
            <Mic className="w-8 h-8 text-foreground" />
          )}
        </button>
      </div>
      <span className="text-xs text-muted-foreground uppercase tracking-widest">
        {isListening ? 'Listening...' : isSpeaking ? 'Speaking...' : 'Tap to speak'}
      </span>
    </div>
  );
}
