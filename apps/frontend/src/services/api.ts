// API service using fetch instead of axios
class ApiService {
  private baseURL: string;
  private timeout: number;

  constructor() {
    let rawBaseURL = process.env.NEXT_PUBLIC_API_BASE_URL || process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:7860';

    if (typeof window !== 'undefined') {
      console.log('[API] Environment variable URL:', rawBaseURL);
    }

    // Standardize URL
    let processed = rawBaseURL.trim();
    if (processed.endsWith('/')) {
      processed = processed.slice(0, -1);
    }

    // If baseURL ends with /api, we strip it because all our endpoint paths start with /api/v1
    // This prevents the common ERROR: https://domain.com/api/api/v1/...
    if (processed.endsWith('/api')) {
      processed = processed.slice(0, -4);
    }

    // For production environments (not localhost), ensure HTTPS
    if (typeof window !== 'undefined' &&
        window.location.hostname !== 'localhost' &&
        !window.location.hostname.includes('127.0.0.1')) {
      // If the processed URL starts with http://, convert to https://
      if (processed.startsWith('http://')) {
        processed = processed.replace('http://', 'https://');
      }
      // If it doesn't start with a protocol, assume HTTPS for production
      if (!processed.startsWith('http://') && !processed.startsWith('https://')) {
        processed = 'https://' + processed;
      }
    }

    this.baseURL = processed;

    if (typeof window !== 'undefined') {
      console.log('[API] BaseURL set to:', this.baseURL);
    }

    this.timeout = 15000;
  }

  private async request(endpoint: string, options: RequestInit = {}): Promise<Response> {
    // Ensure endpoint has a leading slash
    const path = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    
    // Construct final URL
    let url = `${this.baseURL}${path}`;
    
    // Clean double slashes (except in protocol)
    url = url.replace(/([^:]\/)\/+/g, "$1");

    if (typeof window !== 'undefined') {
      console.log(`[API Request] ${options.method || 'GET'} ${url}`);
    }

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    const token = localStorage.getItem('access_token');
    if (token) {
      (config.headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
    }

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.timeout);

    try {
      const response = await fetch(url, {
        ...config,
        signal: controller.signal,
      });

      clearTimeout(timeoutId);

      // Log response for debugging
      if (typeof window !== 'undefined') {
        console.log(`[API Response] ${response.status} from ${url}`);
      }

      // Handle common errors
      if (response.status === 401 && !path.includes('/auth/login')) {
        console.warn('Unauthorized detected, clearing session');
        localStorage.removeItem('access_token');
        localStorage.removeItem('user');
        if (typeof window !== 'undefined' && !window.location.pathname.startsWith('/auth/')) {
           window.location.href = '/auth/sign-in';
        }
      }

      if (!response.ok) {
        const errorBody = await response.text();
        console.error(`[API Error] Body:`, errorBody);
        
        let detail = `Error ${response.status}`;
        try {
          const parsed = JSON.parse(errorBody);
          detail = parsed.detail || detail;
        } catch {
          detail = errorBody || detail;
        }
        throw new Error(detail);
      }

      return response;
    } catch (error: unknown) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Connection timed out. The backend might be sleeping or unreachable.');
      }
      throw error;
    }
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await this.request(endpoint, { method: 'GET' });
    return response.json();
  }

  async post<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.request(endpoint, {
      method: 'POST',
      body: data ? JSON.stringify(data) : undefined,
    });
    return response.json();
  }

  async put<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.request(endpoint, {
      method: 'PUT',
      body: data ? JSON.stringify(data) : undefined,
    });
    return response.json();
  }

  async patch<T>(endpoint: string, data?: unknown): Promise<T> {
    const response = await this.request(endpoint, {
      method: 'PATCH',
      body: data ? JSON.stringify(data) : undefined,
    });
    return response.json();
  }

  async delete<T>(endpoint: string): Promise<T> {
    const response = await this.request(endpoint, { method: 'DELETE' });
    if (response.status === 204 || response.status === 200) {
      return {} as T;
    }
    return response.json();
  }
}

const apiService = new ApiService();
export default apiService;