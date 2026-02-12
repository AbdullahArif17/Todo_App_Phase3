'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiService from '../services/api';

interface User {
  id: string;
  email: string;
  created_at: string;
  full_name?: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  signup: (email: string, password: string) => Promise<void>;
  isAuthenticated: boolean;
  isLoading: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  // Initialize auth from localStorage on mount
  useEffect(() => {
    const initAuth = () => {
      try {
        const token = localStorage.getItem('access_token');
        const storedUser = localStorage.getItem('user');
        
        if (token && storedUser && storedUser !== "undefined" && storedUser !== "null") {
          const parsedUser = JSON.parse(storedUser);
          if (parsedUser && (parsedUser.id || parsedUser.email)) {
             setUser(parsedUser);
             setIsAuthenticated(true);
             console.log('[Auth] Restored session for:', parsedUser.email);
          } else {
             console.warn('[Auth] Token found but user data was invalid/empty');
             handleLogoutInternal();
          }
        } else if (token) {
          console.warn('[Auth] Token exists but no user profile found in storage');
          handleLogoutInternal();
        } else {
          console.log('[Auth] No existing session found');
        }
      } catch (err) {
        console.error('[Auth] Error during session initialization:', err);
        handleLogoutInternal();
      } finally {
        setIsLoading(false);
      }
    };

    initAuth();
  }, []);

  const handleLogoutInternal = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
  };

  const login = async (email: string, password: string) => {
    try {
      console.log('[Auth] Attempting login for:', email);
      
      const response = await apiService.post<{ access_token: string; user: User }>('/api/v1/auth/login', {
        email,
        password,
      });

      console.log('[Auth] Login response received');

      if (!response.access_token || !response.user) {
        console.error('[Auth] Login successful but response structure invalid:', response);
        throw new Error('Server response missing access_token or user profile');
      }

      // 1. Update Storage
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      // 2. Update React State
      setUser(response.user);
      setIsAuthenticated(true);
      
      console.log('[Auth] Session established for:', response.user.email);
    } catch (error: unknown) {
      console.error('[Auth] Login phase failed:', error);
      throw error;
    }
  };

  const signup = async (email: string, password: string) => {
    try {
      console.log('[Auth] Attempting registration for:', email);
      
      const response = await apiService.post<{ access_token: string; user: User }>('/api/v1/auth/register', {
        email,
        password,
      });

      console.log('[Auth] Registration response received');

      if (!response.access_token || !response.user) {
        console.error('[Auth] Signup successful but response structure invalid:', response);
        throw new Error('Server response missing access_token or user profile');
      }

      // 1. Update Storage
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      // 2. Update React State
      setUser(response.user);
      setIsAuthenticated(true);
      
      console.log('[Auth] Account created and session established for:', response.user.email);
    } catch (error: unknown) {
      console.error('[Auth] Registration phase failed:', error);
      throw error;
    }
  };

  const logout = () => {
    console.log('[Auth] Logging out user');
    handleLogoutInternal();
    if (typeof window !== 'undefined') {
      window.location.href = '/auth/sign-in';
    }
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, signup, isAuthenticated, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}