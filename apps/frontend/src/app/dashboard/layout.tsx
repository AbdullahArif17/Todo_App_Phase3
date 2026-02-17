'use client';

import { ReactNode, useEffect } from "react";
import Link from 'next/link';
import { usePathname, useRouter } from 'next/navigation';
import { useAuth } from '@/context/auth-context';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const router = useRouter();
  const { user, isAuthenticated, logout, isLoading } = useAuth();

  const isActive = (path: string) => pathname === path;

  const handleLogout = () => {
    logout();
  };

  useEffect(() => {
    if (!isLoading && (!isAuthenticated || !user)) {
      router.replace('/auth/sign-in');
    }
  }, [isLoading, isAuthenticated, user, router]);

  // Show loading state while checking authentication or redirecting
  if (isLoading || !isAuthenticated || !user) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center">
        <div className="text-center animate-pulse">
          <p className="text-lg text-muted-foreground">
            {isLoading ? 'Verifying session...' : 'Redirecting...'}
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="bg-card/80 backdrop-blur-md border-b border-border sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center gap-2 sm:gap-8 overflow-hidden">
              <h1 className="text-lg sm:text-xl font-black text-foreground tracking-tighter truncate shrink-0">
                TODO<span className="text-primary italic">APP</span>
              </h1>
              <div className="flex items-center space-x-1 sm:space-x-4 overflow-x-auto no-scrollbar py-1">
                <Link
                  href="/dashboard/todos"
                  className={`px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold transition-all whitespace-nowrap ${
                    isActive('/dashboard/todos')
                      ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  Objectives
                </Link>
                <Link
                  href="/dashboard/chat"
                  className={`px-3 py-1.5 rounded-xl text-xs sm:text-sm font-bold transition-all whitespace-nowrap ${
                    isActive('/dashboard/chat')
                      ? 'bg-primary text-primary-foreground shadow-lg shadow-primary/20'
                      : 'text-muted-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  AI Assistant
                </Link>
              </div>
            </div>
            <div className="flex items-center ml-2">
              <button
                onClick={handleLogout}
                className="px-3 sm:px-4 py-1.5 sm:py-2 text-[10px] sm:text-xs font-black uppercase tracking-widest text-destructive hover:bg-destructive/10 border border-destructive/20 rounded-xl transition-all active:scale-95 whitespace-nowrap"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="relative">
        <div className="max-w-7xl mx-auto py-4 sm:py-8">
          {children}
        </div>
      </main>
    </div>
  );
}
