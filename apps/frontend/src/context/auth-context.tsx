'use client';

import { createContext, useContext, useState, useEffect, ReactNode } from 'react';
import apiService from '../services/api';

interface User {
  id: string;
  email: string;
  created_at: string;
}

interface AuthContextType {
  user: User | null;
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  signup: (email: string, password: string) => Promise<void>;
  isAuthenticated: boolean;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUser] = useState<User | null>(null);
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    // Check if user is logged in on initial load
    const token = localStorage.getItem('access_token');
    if (token) {
      // In a real app, you would verify the token with the backend
      setIsAuthenticated(true);
    }
  }, []);

  const login = async (email: string, password: string) => {
    try {
      // Use apiService which handles the base URL configuration
      const data = await apiService.post<{ access_token: string; user?: User }>('/api/v1/auth/login', {
        email,
        password,
      });

      // Store the token
      localStorage.setItem('access_token', data.access_token);

      // Set user data if available in response
      if (data.user) {
        setUser(data.user);
      }

      setIsAuthenticated(true);
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw new Error(error.message || 'Login failed');
      }
      throw new Error('Login failed');
    }
  };

  const signup = async (email: string, password: string) => {
    try {
      // Use apiService which handles the base URL configuration
      const data = await apiService.post<{ access_token: string; user?: User }>('/api/v1/auth/register', {
        email,
        password,
      });

      // Store the token
      localStorage.setItem('access_token', data.access_token);

      // Set user data if available in response
      if (data.user) {
        setUser(data.user);
      }

      setIsAuthenticated(true);
    } catch (error: unknown) {
      if (error instanceof Error) {
        throw new Error(error.message || 'Registration failed');
      }
      throw new Error('Registration failed');
    }
  };

  const logout = () => {
    localStorage.removeItem('access_token');
    setUser(null);
    setIsAuthenticated(false);
  };

  return (
    <AuthContext.Provider value={{ user, login, logout, signup, isAuthenticated }}>
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