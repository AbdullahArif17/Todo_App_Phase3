import api from './api';

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
      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch todos');
    }
  }

  async createTodo(todoData: TodoTaskCreate): Promise<TodoTask> {
    try {
      const response = await api.post<TodoTask>('/api/v1/todos', todoData);
      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to create todo');
    }
  }

  async getTodoById(id: string): Promise<TodoTask> {
    try {
      const response = await api.get<TodoTask>(`/api/v1/todos/${id}`);
      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to fetch todo');
    }
  }

  async updateTodo(id: string, todoData: TodoTaskUpdate): Promise<TodoTask> {
    try {
      const response = await api.put<TodoTask>(`/api/v1/todos/${id}`, todoData);
      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to update todo');
    }
  }

  async deleteTodo(id: string): Promise<void> {
    try {
      await api.delete<void>(`/api/v1/todos/${id}`);
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to delete todo');
    }
  }

  async toggleTodoComplete(id: string, isCompleted: boolean): Promise<TodoTask> {
    try {
      const response = await api.patch<TodoTask>(`/api/v1/todos/${id}/complete`, { is_completed: isCompleted });
      return response;
    } catch (error: unknown) {
      const errorMessage = this.getErrorMessage(error);
      throw new Error(errorMessage || 'Failed to update todo completion status');
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

const todoService = new TodoService();
export default todoService;