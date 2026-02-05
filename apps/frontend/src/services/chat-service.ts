
export interface ChatRequest {
  conversation_id?: string;
  message: string;
}

export interface ChatResponse {
  conversation_id: string;
  response: string;
  message_id?: string;
}

export interface Conversation {
  id: string;
  title: string;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface Message {
  id: string;
  conversation_id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  timestamp: string;
  created_at: string;
  updated_at: string;
}

class ChatService {
  async sendMessage(userId: string, message: string, conversationId?: string): Promise<ChatResponse> {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:7860'}/api/${userId}/chat`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'Authorization': `Bearer ${token}`,
        },
        body: JSON.stringify({
          message,
          conversation_id: conversationId
        })
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to send chat message');
    }
  }

  async getMessages(userId: string, conversationId: string, skip: number = 0, limit: number = 50): Promise<Message[]> {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:7860'}/api/${userId}/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.messages || data;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch messages');
    }
  }

  async getConversations(userId: string, skip: number = 0, limit: number = 20): Promise<Conversation[]> {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:7860'}/api/${userId}/conversations?skip=${skip}&limit=${limit}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      return response.json();
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch conversations');
    }
  }

export interface SearchResultsResponse {
    query: string;
    conversations: Conversation[];
    messages: Message[];
    total_conversation_results: number;
    total_message_results: number;
    limit: number;
    offset: number;
  }

  async searchConversations(userId: string, query: string, limit: number = 20, offset: number = 0): Promise<SearchResultsResponse> {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:7860'}/api/${userId}/search?query=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const result = await response.json();

      // Return properly structured result
      return {
        query: result.query || query,
        conversations: result.conversations || [],
        messages: result.messages || [],
        total_conversation_results: result.total_conversation_results || 0,
        total_message_results: result.total_message_results || 0,
        limit: result.limit || limit,
        offset: result.offset || offset
      };
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to search conversations');
    }
  }

  async getConversationMessages(conversationId: string, userId: string, skip: number = 0, limit: number = 50): Promise<Message[]> {
    try {
      const token = localStorage.getItem('access_token');
      const response = await fetch(`${process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:7860'}/api/${userId}/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`, {
        method: 'GET',
        headers: {
          'Authorization': `Bearer ${token}`,
        }
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}));
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`);
      }

      const data = await response.json();
      return data.messages || data;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch conversation messages');
    }
  }

  private getErrorMessage(error: unknown): string {
    if (error instanceof Error) {
      return error.message;
    }
    if (typeof error === 'object' && error !== null) {
      const errorObj = error as Record<string, unknown>;
      if ('response' in errorObj && errorObj.response) {
        const response = errorObj.response as Record<string, unknown>;
        if ('data' in response && response.data) {
          const data = response.data as Record<string, unknown>;
          if ('detail' in data && typeof data.detail === 'string') {
            return data.detail;
          }
        }
      }
    }
    return 'An error occurred';
  }
}

const chatService = new ChatService();
export default chatService;