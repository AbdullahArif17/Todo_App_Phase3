'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/context/auth-context';
import chatService, { Conversation } from '@/services/chat-service';

const ChatPage = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<{id: string, role: string, content: string, timestamp: Date}[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [conversations, setConversations] = useState<Conversation[]>([]);
  const [isHistoryLoading, setIsHistoryLoading] = useState(false);
  
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation list and restore last session
  useEffect(() => {
    if (user) {
      loadConversations();
      const savedConversationId = localStorage.getItem(`chat_conversation_${user.id}`);
      if (savedConversationId) {
        handleSelectConversation(savedConversationId);
      }
    }
  }, [user]);

  const loadConversations = async () => {
    if (!user) return;
    try {
      const convs = await chatService.getConversations(user.id);
      setConversations(convs);
    } catch (error) {
      console.error('Error fetching conversations:', error);
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const handleSelectConversation = async (id: string) => {
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
  };

  const startNewChat = () => {
    setConversationId(null);
    setMessages([]);
    if (user) {
      localStorage.removeItem(`chat_conversation_${user.id}`);
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
      <div className="w-72 flex flex-col bg-card/50 backdrop-blur-md border border-border rounded-2xl overflow-hidden shadow-sm">
        <div className="p-4 border-b border-border">
          <button 
            onClick={startNewChat}
            className="w-full flex items-center justify-center gap-2 bg-primary text-primary-foreground py-2.5 rounded-xl hover:bg-primary/90 transition-all shadow-sm active:scale-95 font-medium"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
            </svg>
            New Chat
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-2 space-y-1 custom-scrollbar">
          {conversations.length === 0 ? (
            <div className="text-center py-10 px-4">
              <p className="text-xs text-muted-foreground italic">No chat history yet</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <button
                key={conv.id}
                onClick={() => handleSelectConversation(conv.id)}
                className={`w-full text-left p-3 rounded-xl transition-all group relative ${
                  conversationId === conv.id 
                    ? 'bg-primary/10 border-primary/20 border shadow-sm' 
                    : 'hover:bg-muted/50 border border-transparent'
                }`}
              >
                <div className="text-sm font-medium text-foreground truncate pr-4">
                  {conv.title || 'New Conversation'}
                </div>
                <div className="text-[10px] text-muted-foreground mt-1 flex items-center justify-between">
                  <span>{new Date(conv.created_at).toLocaleDateString()}</span>
                  {conversationId === conv.id && (
                    <span className="w-1.5 h-1.5 rounded-full bg-primary animate-pulse"></span>
                  )}
                </div>
              </button>
            ))
          )}
        </div>
      </div>

      {/* Main Chat Area */}
      <div className="flex-1 flex flex-col bg-card border border-border rounded-2xl shadow-lg relative overflow-hidden">
        {/* Chat Header */}
        <div className="p-4 border-b border-border bg-card/50 backdrop-blur-sm flex items-center justify-between z-10">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center text-primary">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div>
              <h1 className="font-semibold text-foreground leading-none">AI Todo Assistant</h1>
              <p className="text-[11px] text-muted-foreground mt-1 flex items-center gap-1">
                <span className="w-1.5 h-1.5 rounded-full bg-green-500"></span>
                Ready to manage your tasks
              </p>
            </div>
          </div>
          
          {conversationId && (
            <div className="text-[10px] bg-muted px-2 py-1 rounded-md text-muted-foreground font-mono">
              ID: ...{conversationId.slice(-8)}
            </div>
          )}
        </div>

        {/* Messages Space */}
        <div className="flex-1 overflow-y-auto p-4 space-y-6 custom-scrollbar bg-dots-pattern">
          {isHistoryLoading ? (
            <div className="h-full flex flex-col items-center justify-center space-y-4">
              <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
              <p className="text-sm text-muted-foreground animate-pulse">Loading conversation history...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center px-8 animate-in fade-in duration-700">
              <div className="w-16 h-16 bg-primary/10 rounded-3xl flex items-center justify-center mb-6 rotate-3">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-xl font-bold text-foreground mb-3">Hello! I'm your task companion.</h3>
              <p className="text-sm text-muted-foreground max-w-sm mb-8 leading-relaxed">
                I can help you capture ideas, organize your schedule, and track progress. Try asking: 
              </p>
              <div className="grid grid-cols-1 gap-2 w-full max-w-xs">
                {[
                  "Add 'Buy coffee beans' to my list",
                  "What are my tasks for today?",
                  "Mark 'Meeting with team' as done",
                  "Find tasks related to 'Work'"
                ].map((hint, idx) => (
                  <button 
                    key={idx}
                    onClick={() => setMessage(hint)}
                    className="text-xs text-left p-3 rounded-xl border border-border bg-card hover:border-primary/50 hover:bg-primary/5 transition-all"
                  >
                    "{hint}"
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 max-w-2xl mx-auto w-full">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2 duration-300`}
                >
                  <div
                    className={`max-w-[85%] px-4 py-3 rounded-2xl shadow-sm ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground rounded-tr-none'
                        : 'bg-muted/50 text-foreground border border-border rounded-tl-none backdrop-blur-sm'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-[13px] leading-6 font-normal">{msg.content}</div>
                    <div className={`text-[9px] mt-2 font-medium opacity-60 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
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
        <div className="p-4 bg-card/80 backdrop-blur-md border-t border-border">
          <form onSubmit={handleSubmit} className="relative max-w-2xl mx-auto">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message..."
              disabled={isLoading || isHistoryLoading}
              className="w-full bg-background/50 border border-input rounded-2xl pl-4 pr-14 py-3.5 text-sm ring-offset-background placeholder:text-muted-foreground focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !message.trim() || isHistoryLoading}
              className="absolute right-2 top-2 p-2 bg-primary text-primary-foreground rounded-xl hover:bg-primary/90 focus:outline-none disabled:opacity-50 transition-all active:scale-90 shadow-md"
            >
              {isLoading ? (
                <div className="animate-spin rounded-full h-5 w-5 border-2 border-primary-foreground border-t-transparent"></div>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              )}
            </button>
          </form>
          <div className="mt-2 text-[10px] text-center text-muted-foreground">
            {isLoading ? 'Agent is analyzing your request...' : 'Secure AI processing powered by Groq/OpenAI'}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;