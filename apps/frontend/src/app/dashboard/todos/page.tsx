'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import apiService from '../../../services/api';

interface Todo {
  id: string;
  title: string;
  description?: string;
  is_completed: boolean;
  user_id: string;
  created_at: string;
  updated_at: string;
}

export default function TodoListPage() {
  const [todos, setTodos] = useState<Todo[]>([]);
  const [newTodo, setNewTodo] = useState({ title: '', description: '' });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const router = useRouter();

  // Check if user is authenticated
  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      router.push('/auth/sign-in');
    } else {
      fetchTodos();
    }
  }, [router]);

  const fetchTodos = async () => {
    try {
      const data = await apiService.get<Todo[]>('/api/v1/todos');
      setTodos(data);
      setLoading(false);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while fetching todos';
      setError(errorMessage);
      setLoading(false);
    }
  };

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    try {
      const createdTodo = await apiService.post<Todo>('/api/v1/todos', {
        title: newTodo.title,
        description: newTodo.description || null,
      });
      setTodos([...todos, createdTodo]);
      setNewTodo({ title: '', description: '' });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while adding todo';
      setError(errorMessage);
    }
  };

  const toggleTodoCompletion = async (id: string, currentStatus: boolean) => {
    try {
      const updatedTodo = await apiService.patch<Todo>(`/api/v1/todos/${id}/complete`);
      setTodos(todos.map(todo =>
        todo.id === id ? updatedTodo : todo
      ));
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while updating todo';
      setError(errorMessage);
    }
  };

  const deleteTodo = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this todo?')) {
      return;
    }

    try {
      await apiService.delete<object>(`/api/v1/todos/${id}`);
      setTodos(todos.filter(todo => todo.id !== id));
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while deleting todo';
      setError(errorMessage);
    }
  };

  const handleLogout = () => {
    localStorage.removeItem('access_token');
    router.push('/auth/sign-in');
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-screen">
        <p>Loading todos...</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-background">
      <nav className="bg-card border-b border-border">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex items-center">
              <h1 className="text-xl font-semibold text-foreground">Todo App</h1>
            </div>
            <div className="flex items-center">
              <button
                onClick={handleLogout}
                className="ml-4 px-4 py-2 text-sm font-medium text-destructive-foreground bg-destructive hover:bg-destructive/90 rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-destructive transition-colors"
              >
                Logout
              </button>
            </div>
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto py-6 sm:px-6 lg:px-8">
        <div className="px-4 py-6 sm:px-0">
          <div className="border border-border rounded-lg p-6 bg-card shadow-sm">
            {error && (
              <div className="mb-4 rounded-md bg-destructive/10 p-4 border border-destructive/30">
                <div className="text-sm text-destructive-foreground">{error}</div>
              </div>
            )}

            <form onSubmit={handleAddTodo} className="mb-8">
              <div className="grid grid-cols-1 gap-6 sm:grid-cols-2">
                <div>
                  <label htmlFor="title" className="block text-sm font-medium text-foreground mb-1">
                    Title *
                  </label>
                  <input
                    type="text"
                    id="title"
                    value={newTodo.title}
                    onChange={(e) => setNewTodo({...newTodo, title: e.target.value})}
                    required
                    className="mt-1 block w-full rounded-md border border-input bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors sm:text-sm"
                  />
                </div>
                <div>
                  <label htmlFor="description" className="block text-sm font-medium text-foreground mb-1">
                    Description
                  </label>
                  <input
                    type="text"
                    id="description"
                    value={newTodo.description}
                    onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
                    className="mt-1 block w-full rounded-md border border-input bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors sm:text-sm"
                  />
                </div>
              </div>
              <div className="mt-4">
                <button
                  type="submit"
                  className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-primary-foreground bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
                >
                  Add Todo
                </button>
              </div>
            </form>

            <div className="mt-6">
              <h2 className="text-lg font-semibold text-foreground">Your Todos</h2>
              <ul className="mt-4 space-y-3">
                {todos.length === 0 ? (
                  <li className="text-muted-foreground italic py-8 text-center">No todos yet. Add one above!</li>
                ) : (
                  todos.map((todo) => (
                    <li
                      key={todo.id}
                      className={`flex items-center justify-between p-4 bg-background border border-border rounded-lg transition-all ${
                        todo.is_completed ? 'opacity-70' : 'hover:bg-muted/50'
                      }`}
                    >
                      <div className="flex items-center">
                        <input
                          type="checkbox"
                          checked={todo.is_completed}
                          onChange={() => toggleTodoCompletion(todo.id, todo.is_completed)}
                          className="h-4 w-4 text-primary border-input rounded focus:ring-primary focus:ring-2"
                        />
                        <span className={`ml-3 ${todo.is_completed ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                          <span className="font-medium">{todo.title}</span>
                          {todo.description && (
                            <p className="text-sm text-muted-foreground mt-1">{todo.description}</p>
                          )}
                        </span>
                      </div>
                      <div className="flex space-x-3">
                        <button
                          onClick={() => toggleTodoCompletion(todo.id, todo.is_completed)}
                          className="text-sm font-medium text-primary hover:text-primary/80 transition-colors"
                        >
                          {todo.is_completed ? 'Undo' : 'Complete'}
                        </button>
                        <button
                          onClick={() => deleteTodo(todo.id)}
                          className="text-sm font-medium text-destructive hover:text-destructive/80 transition-colors"
                        >
                          Delete
                        </button>
                      </div>
                    </li>
                  ))
                )}
              </ul>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}