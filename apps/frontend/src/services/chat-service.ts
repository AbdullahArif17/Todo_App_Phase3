
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
  last_activity?: string;
  message_count?: number;
  is_archived?: boolean;
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

import apiService from './api';

export interface SearchResultsResponse {
  query: string;
  conversations: Conversation[];
  messages: Message[];
  total_conversation_results: number;
  total_message_results: number;
  limit: number;
  offset: number;
}

class ChatService {
  async sendMessage(userId: string, message: string, conversationId?: string): Promise<ChatResponse> {
    try {
      // Use the main API service instead of direct fetch to ensure proper URL handling
      const response = await apiService.post<ChatResponse>(`/api/v1/chat/${userId}`, {
        message,
        conversation_id: conversationId
      });

      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to send chat message');
    }
  }

  async deleteConversation(conversationId: string): Promise<void> {
    try {
      await apiService.delete(`/api/v1/conversations/${conversationId}`);
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to delete conversation');
    }
  }

  async getMessages(userId: string, conversationId: string, skip: number = 0, limit: number = 50): Promise<Message[]> {
    try {
      // Use the cleaner message fetching route
      const response = await apiService.get<Message[]>(`/api/v1/chat/${userId}/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`);

      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch messages');
    }
  }

  async getConversations(userId: string, skip: number = 0, limit: number = 20): Promise<Conversation[]> {
    try {
      // Use the dedicated conversations router which is cleaner
      const response = await apiService.get<Conversation[]>(`/api/v1/conversations/?skip=${skip}&limit=${limit}`);

      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch conversations');
    }
  }

  async searchConversations(userId: string, query: string, limit: number = 20, offset: number = 0): Promise<SearchResultsResponse> {
    try {
      // Use the main API service instead of direct fetch to ensure proper URL handling
      const response = await apiService.get<SearchResultsResponse>(`/api/v1/chat/${userId}/search?query=${encodeURIComponent(query)}&limit=${limit}&offset=${offset}`);

      // Return properly structured result
      return {
        query: response.query || query,
        conversations: response.conversations || [],
        messages: response.messages || [],
        total_conversation_results: response.total_conversation_results || 0,
        total_message_results: response.total_message_results || 0,
        limit: response.limit || limit,
        offset: response.offset || offset
      };
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to search conversations');
    }
  }

  async getConversationMessages(conversationId: string, userId: string, skip: number = 0, limit: number = 50): Promise<Message[]> {
    try {
      // Consistent with getMessages
      const response = await apiService.get<Message[]>(`/api/v1/chat/${userId}/conversations/${conversationId}/messages?skip=${skip}&limit=${limit}`);

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