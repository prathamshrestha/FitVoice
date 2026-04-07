import { Link, useLocation } from 'react-router-dom';
import { Activity, LayoutDashboard, MessageSquare, User, LogOut } from 'lucide-react';
import { useState, useEffect } from 'react';

export function Navbar() {
  const location = useLocation();
  const [userId, setUserId] = useState<string | null>(null);

  useEffect(() => {
    setUserId(localStorage.getItem('user_id'));
  }, [location]);

  const links = [
    { to: '/', label: 'Home', icon: Activity },
    { to: '/dashboard', label: 'Dashboard', icon: LayoutDashboard },
    { to: '/chat', label: 'Chat', icon: MessageSquare },
  ];

  const handleLogout = () => {
    localStorage.removeItem('user_id');
    setUserId(null);
  };

  return (
    <nav className="fixed top-0 left-0 right-0 z-50 border-b border-border bg-background/80 backdrop-blur-xl">
      <div className="max-w-6xl mx-auto px-6 flex items-center justify-between h-16">
        <Link to="/" className="flex items-center gap-2">
          <div className="w-8 h-8 rounded-lg bg-primary/15 border border-primary/30 flex items-center justify-center neon-glow">
            <Activity className="w-4 h-4 text-primary" />
          </div>
          <span className="text-lg font-bold tracking-tight">
            Fit<span className="text-primary text-glow">Voice</span>
          </span>
        </Link>

        <div className="flex items-center gap-1">
          {links.map(({ to, label, icon: Icon }) => {
            const active = location.pathname === to;
            return (
              <Link
                key={to}
                to={to}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  active
                    ? 'bg-primary/15 text-primary'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                }`}
              >
                <Icon className="w-4 h-4" />
                <span className="hidden sm:inline">{label}</span>
              </Link>
            );
          })}

          {userId && (
            <>
              <Link
                to="/profile"
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  location.pathname === '/profile'
                    ? 'bg-primary/15 text-primary'
                    : 'text-muted-foreground hover:text-foreground hover:bg-secondary'
                }`}
              >
                <User className="w-4 h-4" />
                <span className="hidden sm:inline">Profile</span>
              </Link>
              <button
                onClick={handleLogout}
                className="flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium text-muted-foreground hover:text-foreground hover:bg-secondary transition-all"
              >
                <LogOut className="w-4 h-4" />
                <span className="hidden sm:inline">Logout</span>
              </button>
            </>
          )}
        </div>
      </div>
    </nav>
  );
}
