// API service using fetch instead of axios
class ApiService {
  private baseURL: string;
  private timeout: number;

  constructor() {
    const rawBaseURL = process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:7860';
    // Remove trailing slash if present to avoid double slashes when concatenating
    this.baseURL = rawBaseURL.endsWith('/') ? rawBaseURL.slice(0, -1) : rawBaseURL;

    // Log the baseURL for debugging in development
    if (typeof window !== 'undefined' && process.env.NODE_ENV !== 'production') {
      console.log('API Service BaseURL:', this.baseURL);
    }

    this.timeout = 10000;
  }

  private async request(endpoint: string, options: RequestInit = {}): Promise<Response> {
    // Ensure proper URL construction with proper slash handling
    const normalizedBaseURL = this.baseURL.endsWith('/') ? this.baseURL.slice(0, -1) : this.baseURL;
    const normalizedEndpoint = endpoint.startsWith('/') ? endpoint : `/${endpoint}`;
    const url = `${normalizedBaseURL}${normalizedEndpoint}`;

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