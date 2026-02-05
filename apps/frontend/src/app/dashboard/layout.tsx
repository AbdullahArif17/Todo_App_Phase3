'use client';

import { ReactNode } from "react";
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/context/auth-context';

export default function DashboardLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();
  const { user, isAuthenticated, logout } = useAuth();

  const isActive = (path: string) => pathname === path;

  const handleLogout = () => {
    logout();
  };

  return (
    <div className="min-h-screen bg-background">
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-foreground">
                Todo App Dashboard
              </h1>
              <div className="ml-10 flex space-x-4">
                <Link
                  href="/dashboard/todos"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/dashboard/todos')
                      ? 'bg-primary text-primary-foreground'
                      : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  Todos
                </Link>
                <Link
                  href="/dashboard/chat"
                  className={`px-3 py-2 rounded-md text-sm font-medium ${
                    isActive('/dashboard/chat')
                      ? 'bg-primary text-primary-foreground'
                      : 'text-foreground hover:bg-accent hover:text-accent-foreground'
                  }`}
                >
                  AI Chat
                </Link>
              </div>
            </div>
            <div className="flex items-center">
              <button
                onClick={handleLogout}
                className="ml-4 px-4 py-2 text-sm font-medium text-destructive-foreground bg-destructive hover:bg-destructive/90 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-destructive transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main>
        <div className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">{children}</div>
      </main>
    </div>
  );
}
