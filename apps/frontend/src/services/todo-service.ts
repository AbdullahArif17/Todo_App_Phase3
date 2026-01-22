interface Todo {
  id: string;
  title: string;
  description?: string;
  is_completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

class TodoService {
  private baseUrl = '/api/v1/todos';

  async getAllTodos(): Promise<Todo[]> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(this.baseUrl, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to fetch todos');
    }

    return response.json();
  }

  async createTodo(todoData: { title: string; description?: string }): Promise<Todo> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(this.baseUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(todoData),
    });

    if (!response.ok) {
      throw new Error('Failed to create todo');
    }

    return response.json();
  }

  async updateTodo(id: string, todoData: Partial<Todo>): Promise<Todo> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(todoData),
    });

    if (!response.ok) {
      throw new Error('Failed to update todo');
    }

    return response.json();
  }

  async deleteTodo(id: string): Promise<void> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${this.baseUrl}/${id}`, {
      method: 'DELETE',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to delete todo');
    }
  }

  async toggleTodoCompletion(id: string, isCompleted: boolean): Promise<Todo> {
    const token = localStorage.getItem('access_token');
    const response = await fetch(`${this.baseUrl}/${id}/complete`, {
      method: 'PATCH',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify({ is_completed: isCompleted }),
    });

    if (!response.ok) {
      throw new Error('Failed to update todo completion status');
    }

    return response.json();
  }
}

export default new TodoService();