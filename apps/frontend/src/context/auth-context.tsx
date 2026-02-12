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
    // Check if user is logged in on initial load
    const token = localStorage.getItem('access_token');
    const storedUser = localStorage.getItem('user');
    
    if (token && storedUser && storedUser !== "undefined" && storedUser !== "null") {
      try {
        const parsedUser = JSON.parse(storedUser);
        if (parsedUser && parsedUser.id) {
          console.log('Restored user from storage:', parsedUser.email);
          setUser(parsedUser);
          setIsAuthenticated(true);
        } else {
          console.warn('Stored user was invalid, clearing session');
          localStorage.removeItem('access_token');
          localStorage.removeItem('user');
        }
      } catch (e) {
        console.error('Failed to parse stored user, clearing session', e);
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
      }
    } else if (token) {
        // We have a token but no user object - this happens after previous bugs
        // In a real app we'd fetch the profile here. For now, clear to be safe
        console.warn('Token found but no user object, clearing session');
        localStorage.removeItem('access_token');
    }
    setIsLoading(false);
  }, []);

  const login = async (email: string, password: string) => {
    try {
      const data = await apiService.post<{ access_token: string; user: User }>('/api/v1/auth/login', {
        email,
        password,
      });

      if (!data.user) {
        throw new Error('Server response missing user object');
      }

      // Store the token and user
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      setUser(data.user);
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
      const data = await apiService.post<{ access_token: string; user: User }>('/api/v1/auth/register', {
        email,
        password,
      });

      if (!data.user) {
         throw new Error('Server response missing user object');
      }

      // Store the token and user
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('user', JSON.stringify(data.user));

      setUser(data.user);
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
    localStorage.removeItem('user');
    setUser(null);
    setIsAuthenticated(false);
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