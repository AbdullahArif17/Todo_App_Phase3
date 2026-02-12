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

  useEffect(() => {
    const checkSession = () => {
      try {
        const token = localStorage.getItem('access_token');
        const storedUser = localStorage.getItem('user');
        
        if (token && storedUser && storedUser !== "undefined" && storedUser !== "null") {
          const parsedUser = JSON.parse(storedUser);
          if (parsedUser && (parsedUser.id || parsedUser.email)) {
             setUser(parsedUser);
             setIsAuthenticated(true);
          } else {
             console.warn('Refreshing Auth: session data invalid');
             clearAuth();
          }
        } else if (token) {
          console.warn('Refreshing Auth: token found but user profile missing');
          clearAuth();
        }
      } catch (err) {
        console.error('CRITICAL: Failed to initialize auth session', err);
        clearAuth();
      } finally {
        setIsLoading(false);
      }
    };

    checkSession();
  }, []);

  const clearAuth = () => {
    localStorage.removeItem('access_token');
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
  };

  const login = async (email: string, password: string) => {
    try {
      // Clear any existing broken state before login
      clearAuth();
      
      const response = await apiService.post<{ access_token: string; user: User }>('/api/v1/auth/login', {
        email,
        password,
      });

      if (!response.access_token || !response.user) {
        throw new Error('Server response missing required authentication data');
      }

      // Important: set storage BEFORE state to ensure redirects pick it up
      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      setUser(response.user);
      setIsAuthenticated(true);
      console.log('User signed in successfully:', response.user.email);
    } catch (error: unknown) {
      console.error('Login action failed:', error);
      throw error;
    }
  };

  const signup = async (email: string, password: string) => {
    try {
      clearAuth();
      
      const response = await apiService.post<{ access_token: string; user: User }>('/api/v1/auth/register', {
        email,
        password,
      });

      if (!response.access_token || !response.user) {
        throw new Error('Server response missing required registration data');
      }

      localStorage.setItem('access_token', response.access_token);
      localStorage.setItem('user', JSON.stringify(response.user));

      setUser(response.user);
      setIsAuthenticated(true);
      console.log('User registered successfully:', response.user.email);
    } catch (error: unknown) {
      console.error('Signup action failed:', error);
      throw error;
    }
  };

  const logout = () => {
    clearAuth();
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