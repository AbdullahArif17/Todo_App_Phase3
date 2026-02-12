'use client';

import { useState, useEffect } from 'react';
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

  useEffect(() => {
    fetchTodos();
  }, []);

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

  const toggleTodoCompletion = async (id: string) => {
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

  if (loading) {
    return (
      <div className="flex justify-center items-center py-12">
        <p className="animate-pulse text-muted-foreground">Loading todos...</p>
      </div>
    );
  }

  return (
    <div className="border border-border rounded-lg p-6 bg-card shadow-sm">
      <h1 className="text-2xl font-bold text-foreground mb-6">Your Tasks</h1>
      
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
              placeholder="What needs to be done?"
            />
          </div>
          <div>
            <label htmlFor="description" className="block text-sm font-medium text-foreground mb-1">
              Description (optional)
            </label>
            <input
              type="text"
              id="description"
              value={newTodo.description}
              onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
              className="mt-1 block w-full rounded-md border border-input bg-background text-foreground placeholder-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent transition-colors sm:text-sm"
              placeholder="Any details?"
            />
          </div>
        </div>
        <div className="mt-4">
          <button
            type="submit"
            className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-primary-foreground bg-primary hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary transition-colors"
          >
            Add Task
          </button>
        </div>
      </form>

      <div className="mt-8">
        <h2 className="text-lg font-semibold text-foreground border-b border-border pb-2 mb-4">Todo List</h2>
        <ul className="space-y-3">
          {todos.length === 0 ? (
            <li className="text-muted-foreground italic py-12 text-center bg-muted/20 rounded-lg border border-dashed border-border">
              No todos yet. Add one above!
            </li>
          ) : (
            todos.map((todo) => (
              <li
                key={todo.id}
                className={`flex items-center justify-between p-4 bg-background border border-border rounded-lg transition-all ${
                  todo.is_completed ? 'opacity-60 grayscale-[0.5]' : 'hover:border-primary/50 hover:shadow-md'
                }`}
              >
                <div className="flex items-center flex-1 mr-4">
                  <input
                    type="checkbox"
                    checked={todo.is_completed}
                    onChange={() => toggleTodoCompletion(todo.id)}
                    className="h-5 w-5 text-primary border-input rounded cursor-pointer transition-colors"
                  />
                  <div className="ml-4 overflow-hidden">
                    <p className={`font-medium block truncate ${todo.is_completed ? 'line-through text-muted-foreground' : 'text-foreground'}`}>
                      {todo.title}
                    </p>
                    {todo.description && (
                      <p className="text-sm text-muted-foreground mt-1 truncate">{todo.description}</p>
                    )}
                  </div>
                </div>
                <div className="flex space-x-2 shrink-0">
                  <button
                    onClick={() => deleteTodo(todo.id)}
                    className="p-2 text-destructive hover:bg-destructive/10 rounded-md transition-colors"
                    title="Delete"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                    </svg>
                  </button>
                </div>
              </li>
            ))
          )}
        </ul>
      </div>
    </div>
  );
}