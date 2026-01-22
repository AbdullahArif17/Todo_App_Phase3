import api from './api';
import { User } from './auth-service';

export interface TodoTask {
  id: string;
  title: string;
  description?: string;
  is_completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export interface TodoTaskCreate {
  title: string;
  description?: string;
}

export interface TodoTaskUpdate {
  title?: string;
  description?: string;
  is_completed?: boolean;
}

class TodoService {
  async getAllTodos(): Promise<TodoTask[]> {
    try {
      const response = await api.get<TodoTask[]>('/api/v1/todos');
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch todos');
    }
  }

  async createTodo(todoData: TodoTaskCreate): Promise<TodoTask> {
    try {
      const response = await api.post<TodoTask>('/api/v1/todos', todoData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to create todo');
    }
  }

  async getTodoById(id: string): Promise<TodoTask> {
    try {
      const response = await api.get<TodoTask>(`/api/v1/todos/${id}`);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to fetch todo');
    }
  }

  async updateTodo(id: string, todoData: TodoTaskUpdate): Promise<TodoTask> {
    try {
      const response = await api.put<TodoTask>(`/api/v1/todos/${id}`, todoData);
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to update todo');
    }
  }

  async deleteTodo(id: string): Promise<void> {
    try {
      await api.delete(`/api/v1/todos/${id}`);
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to delete todo');
    }
  }

  async toggleTodoCompletion(id: string, isCompleted: boolean): Promise<TodoTask> {
    try {
      const response = await api.patch<TodoTask>(`/api/v1/todos/${id}/complete`, { is_completed: isCompleted });
      return response.data;
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || 'Failed to update todo completion status');
    }
  }
}

export default new TodoService();