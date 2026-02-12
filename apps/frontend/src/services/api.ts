// API service using fetch instead of axios
class ApiService {
  private baseURL: string;
  private timeout: number;

  constructor() {
    let rawBaseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:7860';

    // Log the raw URL from environment variable for debugging
    if (typeof window !== 'undefined') {
      console.log('Raw NEXT_PUBLIC_API_BASE_URL from env:', rawBaseURL);
    }

    // Ensure HTTPS is used in production
    if (typeof window !== 'undefined' && window.location.hostname !== 'localhost' && !window.location.hostname.includes('127.0.0.1')) {
      // In production, ensure the URL starts with https://
      if (!rawBaseURL.startsWith('https://') && !rawBaseURL.startsWith('http://')) {
        rawBaseURL = 'https://' + rawBaseURL;
      } else if (rawBaseURL.startsWith('http://')) {
        rawBaseURL = rawBaseURL.replace('http://', 'https://');
      }

      // Additional check: if it contains the Hugging Face domain, enforce HTTPS
      if (rawBaseURL.includes('huggingface.co') || rawBaseURL.includes('.hf.space')) {
        rawBaseURL = rawBaseURL.replace('http://', 'https://');
      }
    }

    // Remove trailing slash if present
    let processedBaseURL = rawBaseURL.endsWith('/') ? rawBaseURL.slice(0, -1) : rawBaseURL;
    
    // If baseURL ends with /api, remove it because our endpoints already start with /api
    // This handles the case where NEXT_PUBLIC_API_BASE_URL=https://.../api
    if (processedBaseURL.endsWith('/api')) {
      processedBaseURL = processedBaseURL.slice(0, -4);
    }
    
    this.baseURL = processedBaseURL;

    // Log the final processed URL for debugging (will show in console in both dev and prod)
    if (typeof window !== 'undefined') {
      console.log('Final API Service BaseURL:', this.baseURL);
    }

    this.timeout = 10000;
  }

  private async request(endpoint: string, options: RequestInit = {}): Promise<Response> {
    // Remove leading slash from endpoint for proper concatenation
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint.substring(1) : endpoint;

    // Simple concatenation since baseURL is cleaned up in constructor
    let url = `${this.baseURL}/${normalizedEndpoint}`;

    // Ensure no double slashes (except after http:/https:)
    url = url.replace(/([^:]\/)\/+/g, "$1");

    // Log the constructed URL with a clear label to confirm code is updated
    if (typeof window !== 'undefined') {
      console.log('Final Request URL [v2]:', url);
    }

    const config: RequestInit = {
      headers: {
        'Content-Type': 'application/json',
        ...options.headers,
      },
      ...options,
    };

    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token && !config.headers?.['Authorization']) {
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

      // Handle token expiration
      if (response.status === 401) {
        localStorage.removeItem('access_token');
        window.location.href = '/auth/sign-in';
        throw new Error('Unauthorized: Please log in again');
      }

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return response;
    } catch (error: unknown) {
      clearTimeout(timeoutId);
      if (error instanceof Error && error.name === 'AbortError') {
        throw new Error('Request timeout');
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
    // For DELETE requests, we might get an empty response
    if (response.status === 204 || response.status === 200) {
      // No content or successful deletion, return an empty object
      return {} as T;
    }
    return response.json();
  }
}

const apiService = new ApiService();
export default apiService;