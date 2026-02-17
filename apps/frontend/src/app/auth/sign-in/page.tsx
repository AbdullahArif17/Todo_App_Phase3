'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { useAuth } from '@/context/auth-context';

export default function SignInPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const router = useRouter();
  const { login } = useAuth();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (loading) return;
    
    setError('');
    setLoading(true);

    try {
      await login(email, password);
      router.push('/dashboard/todos');
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred during login';
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-background px-4 py-12">
      {/* Background Decor */}
      <div className="fixed inset-0 overflow-hidden pointer-events-none opacity-20">
        <div className="absolute -top-[10%] -left-[10%] w-[40%] h-[40%] bg-primary/20 blur-[120px] rounded-full"></div>
        <div className="absolute -bottom-[10%] -right-[10%] w-[40%] h-[40%] bg-primary/10 blur-[120px] rounded-full"></div>
      </div>

      <div className="max-w-md w-full relative z-10 animate-in fade-in zoom-in-95 duration-700">
        <div className="bg-card/40 backdrop-blur-2xl border border-border/50 rounded-[2.5rem] p-8 sm:p-12 shadow-2xl">
          <div className="mb-10 text-center">
            <h1 className="text-4xl font-black text-foreground tracking-tighter mb-2">
              WELCOME <span className="text-primary italic">BACK</span>
            </h1>
            <p className="text-muted-foreground text-xs font-bold uppercase tracking-widest opacity-60">
              Identity Verification Required
            </p>
          </div>

          <form className="space-y-6" onSubmit={handleSubmit}>
            {error && (
              <div className="rounded-2xl bg-destructive/10 p-4 border border-destructive/20 flex items-center gap-3 animate-shake">
                <div className="text-xs text-destructive font-black uppercase tracking-tight">{error}</div>
              </div>
            )}

            <div className="space-y-5">
              <div className="space-y-2">
                <label htmlFor="email-address" className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 ml-1">
                  Access Portal / Email
                </label>
                <input
                  id="email-address"
                  type="email"
                  autoComplete="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="block w-full rounded-2xl border border-input/50 bg-background/50 px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all font-medium"
                  placeholder="name@example.com"
                />
              </div>

              <div className="space-y-2">
                <label htmlFor="password" className="text-[10px] font-black uppercase tracking-widest text-muted-foreground/60 ml-1">
                  Security Protocol / Password
                </label>
                <input
                  id="password"
                  type="password"
                  autoComplete="current-password"
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  className="block w-full rounded-2xl border border-input/50 bg-background/50 px-5 py-4 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all font-medium"
                  placeholder="••••••••"
                />
              </div>
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full inline-flex items-center justify-center h-16 bg-primary text-primary-foreground font-black uppercase tracking-widest text-xs rounded-2xl shadow-xl hover:bg-primary/90 focus:outline-none active:scale-[0.98] transition-all disabled:opacity-50 mt-4 overflow-hidden relative group"
            >
              <span className="relative z-10">
                {loading ? 'Verifying...' : 'Initiate Session'}
              </span>
              <div className="absolute inset-0 bg-white/10 translate-y-full group-hover:translate-y-0 transition-transform duration-300"></div>
            </button>
          </form>

          <div className="mt-10 text-center">
            <Link href="/auth/sign-up" className="text-[11px] font-black uppercase tracking-widest text-muted-foreground hover:text-primary transition-colors">
              New User? <span className="text-primary italic">Register Here</span>
            </Link>
          </div>
        </div>
        
        <p className="mt-8 text-center text-[10px] text-muted-foreground font-bold tracking-[0.2em] uppercase opacity-30">
          Secure Todo Infrastructure v3.0
        </p>
      </div>
    </div>
  );
}