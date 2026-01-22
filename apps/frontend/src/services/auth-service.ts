import api from './api';

export interface User {
  id: string;
  email: string;
  full_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface UserRegister {
  email: string;
  password: string;
  full_name?: string;
}

export interface UserLogin {
  email: string;
  password: string;
}

interface AuthResponse {
  access_token: string;
  token_type: string;
  user_id: string;
  email: string;
}

class AuthService {
  async register(userData: UserRegister): Promise<{ user: User; accessToken: string }> {
    try {
      const response = await api.post<AuthResponse>('/api/v1/auth/register', userData);

      const { access_token, user_id, email } = response.data;

      // Store the token in localStorage
      localStorage.setItem('access_token', access_token);

      // Return user data and token
      const user: User = {
        id: user_id,
        email,
        is_active: true,
        created_at: new Date().toISOString()
      };

      return { user, accessToken: access_token };
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Registration failed');
    }
  }

  async login(credentials: UserLogin): Promise<{ user: User; accessToken: string }> {
    try {
      const response = await api.post<AuthResponse>('/api/v1/auth/login', credentials);

      const { access_token, user_id, email } = response.data;

      // Store the token in localStorage
      localStorage.setItem('access_token', access_token);

      // Return user data and token
      const user: User = {
        id: user_id,
        email,
        is_active: true,
        created_at: new Date().toISOString()
      };

      return { user, accessToken: access_token };
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Login failed');
    }
  }

  logout(): void {
    // Remove the token from localStorage
    localStorage.removeItem('access_token');
  }

  getCurrentUser(): User | null {
    const token = localStorage.getItem('access_token');
    if (!token) {
      return null;
    }

    // In a real implementation, you'd decode the JWT to get user ID/email
    // For now, we'll just return a placeholder - in a real implementation you'd have an endpoint to get user details
    try {
      // This would be an actual API call to get user details
      // const response = await api.get<User>('/api/v1/auth/me');
      // return response.data;

      // For now, return a dummy user based on the stored token
      // In a real implementation, you'd decode the JWT to get user ID/email
      return {
        id: 'dummy-user-id',
        email: 'dummy@example.com',
        is_active: true,
        created_at: new Date().toISOString()
      };
    } catch (error) {
      return null;
    }
  }

  isAuthenticated(): boolean {
    const token = localStorage.getItem('access_token');
    return !!token;
  }

  getAuthToken(): string | null {
    return localStorage.getItem('access_token');
  }
}

export default new AuthService();