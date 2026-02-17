'use client';

import { useState, useEffect, useCallback } from 'react';
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
  const [isAdding, setIsAdding] = useState(false);

  const fetchTodos = useCallback(async () => {
    try {
      const data = await apiService.get<Todo[]>('/api/v1/todos');
      setTodos(data);
      setLoading(false);
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while fetching todos';
      setError(errorMessage);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchTodos();
  }, [fetchTodos]);

  const handleAddTodo = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!newTodo.title.trim() || isAdding) return;
    
    setError('');
    setIsAdding(true);

    try {
      const createdTodo = await apiService.post<Todo>('/api/v1/todos', {
        title: newTodo.title,
        description: newTodo.description || null,
      });
      setTodos(prev => [...prev, createdTodo]);
      setNewTodo({ title: '', description: '' });
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while adding todo';
      setError(errorMessage);
    } finally {
      setIsAdding(false);
    }
  };

  const toggleTodoCompletion = async (id: string) => {
    try {
      const updatedTodo = await apiService.patch<Todo>(`/api/v1/todos/${id}/complete`);
      setTodos(prev => prev.map(todo =>
        todo.id === id ? updatedTodo : todo
      ));
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while updating todo';
      setError(errorMessage);
    }
  };

  const deleteTodo = async (id: string) => {
    if (!window.confirm('Are you sure you want to delete this task?')) return;

    try {
      await apiService.delete<object>(`/api/v1/todos/${id}`);
      setTodos(prev => prev.filter(todo => todo.id !== id));
    } catch (err: unknown) {
      const errorMessage = err instanceof Error ? err.message : 'An error occurred while deleting todo';
      setError(errorMessage);
    }
  };

  if (loading) {
    return (
      <div className="min-h-[60vh] flex flex-col items-center justify-center space-y-4">
        <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
        <p className="text-sm text-muted-foreground animate-pulse font-medium">Synchronizing tasks...</p>
      </div>
    );
  }

  const completedCount = todos.filter(t => t.is_completed).length;
  const pendingCount = todos.length - completedCount;

  return (
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-4 sm:py-8 space-y-8 animate-in fade-in duration-500">
      {/* Header & Stats Card */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div className="md:col-span-2 flex flex-col justify-center">
          <h1 className="text-3xl sm:text-4xl font-black text-foreground tracking-tight mb-2">
            Task <span className="text-primary italic">Commander</span>
          </h1>
          <p className="text-muted-foreground text-sm sm:text-base font-medium">
            Manage your daily operations with precision.
          </p>
        </div>
        <div className="bg-card/50 backdrop-blur-md border border-border/50 rounded-2xl p-6 flex justify-around items-center shadow-xl">
          <div className="text-center">
            <div className="text-2xl font-black text-primary">{pendingCount}</div>
            <div className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground opacity-60">Pending</div>
          </div>
          <div className="h-10 w-[1px] bg-border/40"></div>
          <div className="text-center">
            <div className="text-2xl font-black text-green-500">{completedCount}</div>
            <div className="text-[10px] uppercase tracking-widest font-bold text-muted-foreground opacity-60">Completed</div>
          </div>
        </div>
      </div>
      
      {error && (
        <div className="rounded-xl bg-destructive/10 p-4 border border-destructive/20 flex items-center gap-3 animate-in slide-in-from-top-2 duration-300">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-destructive" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
          </svg>
          <div className="text-sm text-destructive font-semibold">{error}</div>
        </div>
      )}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-10 items-start">
        {/* Creation Form */}
        <div className="lg:col-span-4 space-y-6 lg:sticky lg:top-24">
          <div className="bg-card border border-border rounded-3xl p-6 sm:p-8 shadow-2xl relative overflow-hidden group">
            <div className="absolute top-0 right-0 p-4 opacity-5 group-hover:opacity-10 transition-opacity">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 9v3m0 0v3m0-3h3m-3 0H9m12 0a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h2 className="text-xl font-extrabold text-foreground mb-6 flex items-center gap-2">
              <span className="w-2 h-6 bg-primary rounded-full"></span>
              New Deployment
            </h2>
            <form onSubmit={handleAddTodo} className="space-y-5">
              <div className="space-y-2">
                <label htmlFor="title" className="text-[11px] font-black uppercase tracking-widest text-muted-foreground ml-1">
                  Task Identifier
                </label>
                <input
                  type="text"
                  id="title"
                  value={newTodo.title}
                  onChange={(e) => setNewTodo({...newTodo, title: e.target.value})}
                  required
                  disabled={isAdding}
                  className="block w-full rounded-2xl border border-input/50 bg-background/50 px-4 py-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all placeholder:text-muted-foreground/40 font-medium"
                  placeholder="What is the mission?"
                />
              </div>
              <div className="space-y-2">
                <label htmlFor="description" className="text-[11px] font-black uppercase tracking-widest text-muted-foreground ml-1">
                  Technical Brief
                </label>
                <textarea
                  id="description"
                  rows={3}
                  value={newTodo.description}
                  onChange={(e) => setNewTodo({...newTodo, description: e.target.value})}
                  disabled={isAdding}
                  className="block w-full rounded-2xl border border-input/50 bg-background/50 px-4 py-3.5 text-sm focus:outline-none focus:ring-2 focus:ring-primary/40 focus:border-primary transition-all placeholder:text-muted-foreground/40 font-medium resize-none"
                  placeholder="Additional parameters..."
                />
              </div>
              <button
                type="submit"
                disabled={isAdding || !newTodo.title.trim()}
                className="w-full inline-flex items-center justify-center h-14 bg-primary text-primary-foreground font-black uppercase tracking-widest text-xs rounded-2xl shadow-lg hover:bg-primary/90 focus:outline-none active:scale-[0.98] transition-all disabled:opacity-50 disabled:grayscale mt-2"
              >
                {isAdding ? (
                  <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></div>
                ) : (
                  'Deploy Task'
                )}
              </button>
            </form>
          </div>
        </div>

        {/* Task List */}
        <div className="lg:col-span-8 space-y-6">
          <div className="flex items-center justify-between mb-2 px-2">
            <h2 className="text-xl font-extrabold text-foreground tracking-tight">Active Duty</h2>
            <div className="text-[10px] font-black bg-muted px-3 py-1.5 rounded-full text-muted-foreground uppercase">
              Total: {todos.length}
            </div>
          </div>

          {todos.length === 0 ? (
            <div className="py-24 text-center bg-card/30 border-2 border-dashed border-border/60 rounded-[3rem] animate-in fade-in zoom-in-95 duration-700">
              <div className="w-20 h-20 bg-primary/5 rounded-full flex items-center justify-center mx-auto mb-6">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-primary/30" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <p className="text-muted-foreground font-bold tracking-tight text-lg mb-2">No active objectives detected</p>
              <p className="text-xs text-muted-foreground/60 font-medium">Add your first task to begin the operation.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 gap-4">
              {todos.sort((a, b) => (a.is_completed === b.is_completed ? 0 : a.is_completed ? 1 : -1)).map((todo) => (
                <div
                  key={todo.id}
                  className={`group flex items-center gap-4 p-5 bg-card/60 backdrop-blur-sm border rounded-3xl transition-all animate-in slide-in-from-right-4 duration-500 ${
                    todo.is_completed 
                      ? 'border-border/30 opacity-50 bg-muted/20' 
                      : 'border-border/60 hover:border-primary/40 hover:bg-card hover:shadow-2xl hover:-translate-y-0.5'
                  }`}
                >
                  <label className="relative flex items-center cursor-pointer">
                    <input
                      type="checkbox"
                      checked={todo.is_completed}
                      onChange={() => toggleTodoCompletion(todo.id)}
                      className="peer sr-only"
                    />
                    <div className="w-8 h-8 rounded-xl border-2 border-primary/20 bg-background transition-all peer-checked:bg-primary peer-checked:border-primary flex items-center justify-center">
                      <svg xmlns="http://www.w3.org/2000/svg" className={`h-5 w-5 text-primary-foreground ${todo.is_completed ? 'scale-100' : 'scale-0'} transition-transform`} viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    </div>
                  </label>

                  <div className="flex-1 min-w-0">
                    <p className={`font-bold text-base sm:text-lg truncate tracking-tight transition-all ${todo.is_completed ? 'line-through text-muted-foreground decoration-primary/30' : 'text-foreground hover:text-primary transition-colors'}`}>
                      {todo.title}
                    </p>
                    {todo.description && (
                      <p className="text-xs sm:text-sm text-muted-foreground mt-1 line-clamp-2 font-medium opacity-80 leading-relaxed">
                        {todo.description}
                      </p>
                    )}
                    <div className="flex items-center gap-3 mt-3">
                      <span className="text-[9px] font-black uppercase tracking-widest text-muted-foreground/40 flex items-center gap-1">
                        <svg xmlns="http://www.w3.org/2000/svg" className="h-3 w-3" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                        </svg>
                        {new Date(todo.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>

                  <div className="flex gap-2">
                    <button
                      onClick={() => deleteTodo(todo.id)}
                      className="p-3 text-muted-foreground/40 hover:text-destructive hover:bg-destructive/10 rounded-2xl transition-all opacity-0 group-hover:opacity-100 focus:opacity-100"
                      title="Decommission Task"
                    >
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                        <path fillRule="evenodd" d="M9 2a1 1 0 00-.894.553L7.382 4H4a1 1 0 000 2v10a2 2 0 002 2h8a2 2 0 002-2V6a1 1 0 100-2h-3.382l-.724-1.447A1 1 0 0011 2H9zM7 8a1 1 0 012 0v6a1 1 0 11-2 0V8zm5-1a1 1 0 00-1 1v6a1 1 0 102 0V8a1 1 0 00-1-1z" clipRule="evenodd" />
                      </svg>
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      </div>
    </div>
  );
}