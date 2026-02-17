'use client';

import { useEffect, useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';

export default function Home() {
  const router = useRouter();
  const [checkingAuth, setCheckingAuth] = useState(true);

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (token) {
      router.push('/dashboard/todos');
    } else {
      setCheckingAuth(false);
    }
  }, [router]);

  if (checkingAuth) {
    return (
      <div className="min-h-screen bg-background flex flex-col items-center justify-center">
        <div className="w-16 h-16 border-4 border-primary/20 border-t-primary rounded-full animate-spin mb-4"></div>
        <p className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground animate-pulse">Syncing Protocols...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background text-foreground overflow-hidden relative">
      {/* Background Kinetic Decor */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-[-10%] left-[-10%] w-[50%] h-[50%] bg-primary/20 blur-[150px] rounded-full animate-pulse"></div>
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] bg-primary/10 blur-[150px] rounded-full animate-pulse [animation-delay:2s]"></div>
        <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150"></div>
      </div>

      <nav className="relative z-20 px-6 py-8 flex justify-between items-center max-w-7xl mx-auto">
        <div className="flex items-center gap-2">
          <div className="w-10 h-10 bg-primary rounded-xl flex items-center justify-center shadow-lg shadow-primary/20">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary-foreground" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M13 10V3L4 14h7v7l9-11h-7z" />
            </svg>
          </div>
          <span className="text-xl font-black tracking-tighter uppercase italic">TASK<span className="text-primary">ASSIST</span></span>
        </div>
        <div className="flex items-center gap-6">
          <Link href="/auth/sign-in" className="text-xs font-black uppercase tracking-widest hover:text-primary transition-colors">Login</Link>
          <Link href="/auth/sign-up" className="px-5 py-2.5 bg-foreground text-background rounded-full text-xs font-black uppercase tracking-widest hover:scale-105 active:scale-95 transition-all shadow-xl">Join Forces</Link>
        </div>
      </nav>

      <main className="relative z-10 max-w-7xl mx-auto px-6 pt-20 pb-32 flex flex-col items-center text-center">
        <div className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-primary/10 border border-primary/20 mb-8 animate-in slide-in-from-top-4 duration-700">
          <span className="flex h-2 w-2 rounded-full bg-primary animate-pulse"></span>
          <span className="text-[10px] font-black uppercase tracking-widest text-primary">Cybernetic Intelligence v3.0 Active</span>
        </div>

        <h1 className="text-6xl md:text-8xl font-black tracking-tighter leading-[0.9] mb-8 animate-in fade-in slide-in-from-bottom-8 duration-700">
          COMMAND YOUR <br />
          <span className="text-primary italic">EFFICIENCY</span>
        </h1>

        <p className="max-w-2xl text-lg md:text-xl text-muted-foreground font-medium leading-relaxed mb-12 animate-in fade-in slide-in-from-bottom-10 duration-700 [animation-delay:100ms]">
          Deploy next-generation task management powered by advanced AI. Organize missions, sync objectives, and conquer your schedule through our high-performance secure interface.
        </p>

        <div className="flex flex-col sm:flex-row gap-4 w-full max-w-md animate-in fade-in slide-in-from-bottom-12 duration-700 [animation-delay:200ms]">
          <Link 
            href="/auth/sign-up" 
            className="flex-1 h-16 flex items-center justify-center bg-primary text-primary-foreground rounded-2xl font-black uppercase tracking-widest text-xs shadow-2xl shadow-primary/30 hover:bg-primary/90 hover:scale-105 active:scale-95 transition-all group"
          >
            Launch System
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 ml-2 group-hover:translate-x-1 transition-transform" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M14 5l7 7m0 0l-7 7m7-7H3" />
            </svg>
          </Link>
          <Link 
            href="/auth/sign-in" 
            className="flex-1 h-16 flex items-center justify-center bg-card/40 backdrop-blur-xl border border-border/50 rounded-2xl font-black uppercase tracking-widest text-xs hover:bg-card/60 transition-all shadow-sm"
          >
            Access Portal
          </Link>
        </div>

        {/* Feature Grid Section */}
        <div className="mt-32 grid grid-cols-1 md:grid-cols-3 gap-6 w-full animate-in fade-in slide-in-from-bottom-16 duration-700 [animation-delay:400ms]">
          {[
            { 
              title: "NEURAL CHAT", 
              desc: "Talk to your assistant to generate, update, or find tasks instantly.",
              icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
            },
            { 
              title: "MISSION OPS", 
              desc: "Powerful todo dashboard designed for maximum visibility and control.",
              icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 002 2h2a2 2 0 002-2" />
            },
            { 
              title: "ENCRYPTED SYNC", 
              desc: "Your data is secured behind next-gen authentication protocols.",
              icon: <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 00-2 2zm10-10V7a4 4 0 00-8 0v4h8z" />
            }
          ].map((feature, i) => (
            <div key={i} className="bg-card/30 backdrop-blur-md border border-border/50 p-8 rounded-[2rem] text-left hover:border-primary/40 transition-all group">
              <div className="w-12 h-12 rounded-2xl bg-primary/10 flex items-center justify-center text-primary mb-6 shadow-inner group-hover:scale-110 transition-transform">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  {feature.icon}
                </svg>
              </div>
              <h3 className="text-xs font-black uppercase tracking-widest mb-3 opacity-60">{feature.title}</h3>
              <p className="text-sm font-medium leading-relaxed opacity-70 group-hover:opacity-100 transition-opacity">
                {feature.desc}
              </p>
            </div>
          ))}
        </div>
      </main>

      <footer className="relative z-10 py-12 border-t border-border/20 text-center">
        <p className="text-[10px] font-black uppercase tracking-[0.4em] opacity-20">
          Advanced Mission Infrastructure © 2026
        </p>
      </footer>
    </div>
  );
}