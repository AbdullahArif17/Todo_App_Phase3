'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '@/context/auth-context';
import chatService, { Conversation } from '@/services/chat-service';

const ChatPage = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<{id: string, role: string, content: string, timestamp: Date}[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  const [isListLoading, setIsListLoading] = useState(false);
  
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadConversations = useCallback(async () => {
    if (!user) return;
    setIsListLoading(true);
    try {
      const convs = await chatService.getConversations(user.id);
      setConversations(convs);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    } finally {
      setIsListLoading(false);
    }
  }, [user]);

  const handleSelectConversation = useCallback(async (id: string) => {
    if (!user || isHistoryLoading) return;
    
    setIsHistoryLoading(true);
    setConversationId(id);
    localStorage.setItem(`chat_conversation_${user.id}`, id);
    
    try {
      const history = await chatService.getMessages(user.id, id);
      setMessages(history.map(msg => ({
        id: msg.id,
        role: msg.role,
        content: msg.content,
        timestamp: new Date(msg.timestamp)
      })));
    } catch (error) {
      console.error('Error loading history:', error);
    } finally {
      setIsHistoryLoading(false);
    }
  }, [user, isHistoryLoading]);

  // Load conversation list and restore last session
  useEffect(() => {
    if (user) {
      loadConversations();
      const savedConversationId = localStorage.getItem(`chat_conversation_${user.id}`);
      if (savedConversationId) {
        handleSelectConversation(savedConversationId);
      }
    }
  }, [user, loadConversations, handleSelectConversation]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewChat = () => {
    setConversationId(null);
    setMessages([]);
    if (user) {
      localStorage.removeItem(`chat_conversation_${user.id}`);
    }
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation(); // Don't select the chat when deleting
    if (!user || !window.confirm('Are you sure you want to delete this conversation?')) return;

    try {
      await chatService.deleteConversation(id);
      if (conversationId === id) {
        startNewChat();
      }
      await loadConversations();
    } catch (error) {
      console.error('Error deleting conversation:', error);
      alert('Failed to delete conversation');
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim() || isLoading || !user) return;

    // Add user message to UI immediately
    const userMessage = {
      id: Date.now().toString(),
      role: 'user',
      content: message,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setMessage('');
    setIsLoading(true);

    try {
      const response = await chatService.sendMessage(user.id, message, conversationId || undefined);

      // Update conversation ID if this was the first message
      if (!conversationId) {
        setConversationId(response.conversation_id);
        localStorage.setItem(`chat_conversation_${user.id}`, response.conversation_id);
        await loadConversations(); // Refresh the list
      }

      // Add AI response to UI
      const aiMessage = {
        id: response.message_id || Date.now().toString(),
        role: 'assistant',
        content: response.response,
        timestamp: new Date()
      };

      setMessages(prev => [...prev, aiMessage]);
    } catch (error) {
      console.error('Error sending message:', error);

      const errorMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please check your connection and try again.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-[calc(100vh-140px)] gap-6 max-w-7xl mx-auto overflow-hidden">
      {/* Sidebar - Conversation History */}
      <div className="w-72 flex flex-col bg-card/60 backdrop-blur-xl border border-border/50 rounded-2xl overflow-hidden shadow-2xl">
        <div className="p-4 border-b border-border/30">
          <button 
            onClick={startNewChat}
            className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground py-3 rounded-xl hover:bg-primary/90 transition-all shadow-md active:scale-95 font-semibold text-sm"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-1.5 custom-scrollbar">
          {isListLoading ? (
            <div className="flex flex-col gap-2 p-2">
              {[1, 2, 3].map(i => (
                <div key={i} className="h-16 bg-muted/40 rounded-xl animate-pulse"></div>
              ))}
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-12 px-4 opacity-50">
              <p className="text-xs font-medium italic">No chat history found</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <div key={conv.id} className="group relative">
                <button
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`w-full text-left p-4 rounded-xl transition-all border ${
                    conversationId === conv.id 
                      ? 'bg-primary/10 border-primary/30 shadow-sm' 
                      : 'hover:bg-muted/40 border-transparent'
                  }`}
                >
                  <div className="text-[13px] font-semibold text-foreground truncate pr-6 leading-tight">
                    {conv.title || 'Untitled Session'}
                  </div>
                  <div className="text-[10px] text-muted-foreground mt-2 flex items-center justify-between font-medium">
                    <span>{new Date(conv.last_activity || conv.updated_at).toLocaleDateString()}</span>
                    <span>{conv.message_count || 0} msgs</span>
                  </div>
                </button>
                <button
                  onClick={(e) => handleDeleteConversation(e, conv.id)}
                  className="absolute right-2 top-1/2 -translate-y-1/2 p-2 text-muted-foreground hover:text-destructive opacity-0 group-hover:opacity-100 transition-all rounded-lg hover:bg-destructive/10"
                  title="Delete conversation"
                >
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-card border border-border rounded-2xl shadow-xl relative overflow-hidden">
        {/* Chat Header */}
        <div className="p-4 border-b border-border bg-card/50 backdrop-blur-md flex items-center justify-between z-10">
          <div className="flex items-center gap-4">
            <div className="w-11 h-11 rounded-2xl bg-primary/15 flex items-center justify-center text-primary shadow-inner">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h1 className="font-bold text-foreground tracking-tight">AI Todo Assistant</h1>
              <p className="text-[11px] text-muted-foreground mt-0.5 flex items-center gap-1.5">
                <span className="flex h-2 w-2 relative">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-green-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-2 w-2 bg-green-500"></span>
                </span>
                Active and ready
              </p>
            </div>
          </div>
          
          <div className="flex items-center gap-2">
            {conversationId && (
              <div className="text-[10px] bg-muted/60 px-2.5 py-1.5 rounded-lg text-muted-foreground font-mono tracking-tighter shadow-sm">
                ID: ...{conversationId.slice(-8)}
              </div>
            )}
          </div>
        </div>

        {/* Messages Space */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 custom-scrollbar bg-dots-pattern">
          {isHistoryLoading ? (
            <div className="h-full flex flex-col items-center justify-center space-y-6">
              <div className="relative w-16 h-16">
                <div className="absolute inset-0 border-4 border-primary/20 rounded-full"></div>
                <div className="absolute inset-0 border-4 border-primary rounded-full animate-spin border-t-transparent"></div>
              </div>
              <p className="text-sm font-medium text-muted-foreground animate-pulse">Syncing conversation data...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center px-8 animate-in fade-in zoom-in-95 duration-500">
              <div className="w-20 h-20 bg-primary/10 rounded-[2rem] flex items-center justify-center mb-8 rotate-6 shadow-sm border border-primary/5">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-10 w-10 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-2xl font-black text-foreground mb-4 tracking-tight">Your AI Productivity Hub</h3>
              <p className="text-sm text-muted-foreground max-w-sm mb-10 leading-relaxed font-medium">
                Manage your tasks through natural conversation. Capture ideas and organize your day effortlessly.
              </p>
              <div className="grid grid-cols-1 gap-3 w-full max-w-md px-4">
                {[
                  "Create a task: 'Meeting with the design team'",
                  "Show all my pending todos",
                  "Mark 'Grocery shopping' as completed",
                  "Search for tasks containing 'Work'"
                ].map((hint, idx) => (
                  <button 
                    key={idx}
                    onClick={() => setMessage(hint)}
                    className="text-[13px] text-left p-4 rounded-2xl border border-border bg-card/30 hover:border-primary/40 hover:bg-primary/5 transition-all shadow-sm flex items-center gap-3 group"
                  >
                    <span className="w-1.5 h-1.5 rounded-full bg-primary/40 group-hover:bg-primary transition-colors"></span>
                    &ldquo;{hint}&rdquo;
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-8 max-w-3xl mx-auto w-full">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-4 duration-500`}
                >
                  <div
                    className={`max-w-[88%] px-5 py-4 rounded-[1.5rem] shadow-md border ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground border-primary/20 rounded-tr-none'
                        : 'bg-muted/30 text-foreground border-border/40 rounded-tl-none backdrop-blur-md'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-[14px] leading-relaxed font-medium">{msg.content}</div>
                    <div className={`text-[10px] mt-3 font-bold tracking-widest uppercase opacity-40 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="p-5 bg-card/90 backdrop-blur-xl border-t border-border/50">
          <form onSubmit={handleSubmit} className="relative max-w-3xl mx-auto">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Message your assistant..."
              disabled={isLoading || isHistoryLoading}
              className="w-full bg-background/40 border border-input/60 rounded-2xl pl-5 pr-14 py-4.5 text-[15px] shadow-sm ring-offset-background placeholder:text-muted-foreground/60 focus:outline-none focus:ring-2 focus:ring-primary/40 transition-all disabled:opacity-50 font-medium"
            />
            <button
              type="submit"
              disabled={isLoading || !message.trim() || isHistoryLoading}
              className="absolute right-2.5 top-2.5 p-3 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 focus:outline-none disabled:opacity-50 transition-all active:scale-90 shadow-lg"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-3 border-primary-foreground border-t-transparent"></div>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              )}
            </button>
          </form>
          <div className="mt-3 text-[10px] text-center text-muted-foreground font-bold tracking-wider uppercase opacity-60">
            {isLoading ? 'Processing Request...' : 'Intelligent Todo Syncing Active'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;