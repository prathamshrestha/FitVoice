import { Link } from 'react-router-dom';
import { Mic, Brain, Zap, Apple, Dumbbell, ArrowRight, Activity } from 'lucide-react';
import { Button } from '@/components/ui/button';
import heroImage from '@/assets/hero-fitness.jpg';

const features = [
  {
    icon: Mic,
    title: 'Voice-First Interaction',
    description: 'Speak naturally to your AI coach. No typing needed — perfect for hands-free use during workouts or cooking.',
  },
  {
    icon: Brain,
    title: 'Smart NLP Engine',
    description: 'Powered by advanced language models fine-tuned for fitness, nutrition, and wellness domains.',
  },
  {
    icon: Zap,
    title: 'Real-Time Responses',
    description: 'Sub-500ms pipeline from speech recognition to AI coaching to voice output. Instant advice when you need it.',
  },
  {
    icon: Apple,
    title: 'Nutrition Analysis',
    description: 'Get instant calorie counts, macro breakdowns, and meal suggestions. Just tell it what you ate.',
  },
  {
    icon: Dumbbell,
    title: 'Workout Planning',
    description: 'Personalized exercise routines based on your goals, fitness level, and available equipment.',
  },
  {
    icon: Activity,
    title: 'Wellness Tracking',
    description: 'Monitor your health journey with conversation history and insights tracked over time.',
  },
];

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background pt-16">
      {/* Hero */}
      <section className="relative overflow-hidden">
        <div className="absolute inset-0">
          <img src={heroImage} alt="FitVoice AI fitness technology" className="w-full h-full object-cover opacity-30" />
          <div className="absolute inset-0 bg-gradient-to-b from-background/60 via-background/80 to-background" />
        </div>

        <div className="relative max-w-6xl mx-auto px-6 py-24 md:py-36">
          <div className="max-w-2xl">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary/10 border border-primary/20 text-primary text-xs font-medium mb-6">
              <Mic className="w-3 h-3" />
              AI-Powered Voice Fitness Coach
            </div>
            <h1 className="text-4xl md:text-6xl font-bold leading-tight mb-6">
              Your Health.{' '}
              <span className="text-primary text-glow">Your Voice.</span>
              <br />
              Your Coach.
            </h1>
            <p className="text-lg text-muted-foreground leading-relaxed mb-8 max-w-lg">
              FitVoice AI is a real-time voice agent that acts as your personal fitness coach. 
              Get instant nutrition analysis, workout recommendations, and wellness tips — completely hands-free.
            </p>
            <div className="flex flex-wrap gap-4">
              <Link to="/chat">
                <Button className="bg-primary text-primary-foreground hover:bg-primary/80 neon-glow h-12 px-8 text-base font-semibold gap-2">
                  Start Talking <ArrowRight className="w-4 h-4" />
                </Button>
              </Link>
              <Link to="/dashboard">
                <Button variant="outline" className="border-border text-foreground hover:bg-secondary h-12 px-8 text-base">
                  View Dashboard
                </Button>
              </Link>
            </div>
          </div>
        </div>
      </section>

      {/* How it works */}
      <section className="max-w-6xl mx-auto px-6 py-20">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold mb-3">How It Works</h2>
          <p className="text-muted-foreground max-w-md mx-auto">Three NLP components working together for a seamless voice coaching experience.</p>
        </div>

        <div className="grid md:grid-cols-3 gap-6">
          {[
            { step: '01', title: 'ASR — You Speak', desc: 'Automatic Speech Recognition captures your voice in real-time with low latency and noise reduction.' },
            { step: '02', title: 'LLM — AI Thinks', desc: 'A language model fine-tuned for fitness processes your query and generates contextual coaching advice.' },
            { step: '03', title: 'TTS — Coach Responds', desc: 'Text-to-Speech delivers natural, prosody-aware responses back to you instantly.' },
          ].map(({ step, title, desc }) => (
            <div key={step} className="bg-card border border-border rounded-2xl p-6 hover:border-primary/30 transition-colors group">
              <span className="text-5xl font-bold text-primary/20 group-hover:text-primary/40 transition-colors">{step}</span>
              <h3 className="text-lg font-semibold mt-2 mb-2">{title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{desc}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Features */}
      <section className="max-w-6xl mx-auto px-6 py-20 border-t border-border">
        <div className="text-center mb-14">
          <h2 className="text-3xl font-bold mb-3">Features</h2>
          <p className="text-muted-foreground max-w-md mx-auto">Everything you need for a complete AI-powered fitness companion.</p>
        </div>

        <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
          {features.map(({ icon: Icon, title, description }) => (
            <div key={title} className="bg-card/50 border border-border rounded-xl p-5 hover:bg-card hover:border-primary/20 transition-all group">
              <div className="w-10 h-10 rounded-lg bg-primary/10 border border-primary/20 flex items-center justify-center mb-4 group-hover:neon-glow transition-all">
                <Icon className="w-5 h-5 text-primary" />
              </div>
              <h3 className="font-semibold mb-1">{title}</h3>
              <p className="text-sm text-muted-foreground leading-relaxed">{description}</p>
            </div>
          ))}
        </div>
      </section>

      {/* Demo scenario */}
      <section className="max-w-6xl mx-auto px-6 py-20 border-t border-border">
        <div className="max-w-2xl mx-auto text-center">
          <h2 className="text-3xl font-bold mb-6">See It In Action</h2>
          <div className="bg-card border border-border rounded-2xl p-8 text-left space-y-4">
            <div className="flex gap-3 items-start">
              <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0 mt-0.5">🧑</div>
              <p className="text-sm bg-secondary rounded-2xl rounded-tl-sm px-4 py-3">"I want two boiled eggs and a bowl of oatmeal for my breakfast."</p>
            </div>
            <div className="flex gap-3 items-start">
              <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0 mt-0.5">🤖</div>
              <p className="text-sm bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                "Great choice! That's approximately <strong>290 kcal</strong> with <strong>17g protein</strong> and <strong>4g fiber</strong>. A solid, balanced breakfast!"
              </p>
            </div>
            <div className="flex gap-3 items-start">
              <div className="w-8 h-8 rounded-full bg-secondary flex items-center justify-center shrink-0 mt-0.5">🧑</div>
              <p className="text-sm bg-secondary rounded-2xl rounded-tl-sm px-4 py-3">"How much fiber does the oatmeal have? Can you recommend a workout too?"</p>
            </div>
            <div className="flex gap-3 items-start">
              <div className="w-8 h-8 rounded-full bg-primary/20 border border-primary/30 flex items-center justify-center shrink-0 mt-0.5">🤖</div>
              <p className="text-sm bg-card border border-border rounded-2xl rounded-tl-sm px-4 py-3">
                "Oatmeal has ~<strong>4g fiber</strong> per cup. Add chia seeds for a boost! For your workout, I'd recommend squats, push-ups, and planks — 3 sets each. 💪"
              </p>
            </div>
          </div>
          <Link to="/chat">
            <Button className="mt-8 bg-primary text-primary-foreground hover:bg-primary/80 neon-glow h-12 px-8 text-base font-semibold gap-2">
              Try It Yourself <ArrowRight className="w-4 h-4" />
            </Button>
          </Link>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-border py-8">
        <div className="max-w-6xl mx-auto px-6 flex items-center justify-between text-sm text-muted-foreground">
          <span>© 2026 FitVoice AI</span>
          <span>Built with ❤️ for your wellness</span>
        </div>
      </footer>
    </div>
  );
}
