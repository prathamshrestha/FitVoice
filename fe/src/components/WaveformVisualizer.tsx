interface WaveformVisualizerProps {
  active: boolean;
}

export function WaveformVisualizer({ active }: WaveformVisualizerProps) {
  if (!active) return null;
  
  return (
    <div className="flex items-center justify-center gap-1 h-10">
      {Array.from({ length: 12 }).map((_, i) => (
        <div
          key={i}
          className="w-1 rounded-full bg-primary animate-waveform"
          style={{
            animationDelay: `${i * 0.08}s`,
            animationDuration: `${0.5 + Math.random() * 0.5}s`,
          }}
        />
      ))}
    </div>
  );
}
