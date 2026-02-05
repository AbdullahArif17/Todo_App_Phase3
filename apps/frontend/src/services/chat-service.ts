import api from './api';

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
  async sendMessage(userId: string, chatRequest: ChatRequest): Promise<ChatResponse> {
    try {
      const response = await api.post<ChatResponse>(`/api/v1/chat/${userId}`, chatRequest);
      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to send chat message');
    }
  }

  async getMessages(conversationId: string): Promise<Message[]> {
    try {
      // This would need a backend endpoint for fetching messages
      // For now, we'll return an empty array or handle differently
      console.warn('getMessages not implemented on backend yet');
      return [];
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch messages');
    }
  }

  async getConversations(userId: string, skip: number = 0, limit: number = 20): Promise<Conversation[]> {
    try {
      const response = await api.get<Conversation[]>(`/api/v1/chat/${userId}/conversations?skip=${skip}&limit=${limit}`);
      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch conversations');
    }
  }

  async searchConversations(userId: string, query: string, limit: number = 20, offset: number = 0): Promise<any> {
    try {
      const response = await api.get(`/api/v1/chat/${userId}/search?query=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`);
      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to search conversations');
    }
  }

  async getConversationMessages(conversationId: string, userId: string, skip: number = 0, limit: number = 50): Promise<Message[]> {
    try {
      const response = await api.get<Message[]>(`/api/v1/chat/${userId}/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`);
      return response;
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