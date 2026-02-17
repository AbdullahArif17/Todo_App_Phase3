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
  const [listError, setListError] = useState<string | null>(null);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);
  
  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const loadConversations = useCallback(async () => {
    if (!user) return;
    setIsListLoading(true);
    setListError(null);
    try {
      const convs = await chatService.getConversations(user.id);
      setConversations(convs);
    } catch (error) {
      console.error('Error fetching conversations:', error);
      setListError('Failed to load history');
    } finally {
      setIsListLoading(false);
    }
  }, [user]);

  const handleSelectConversation = useCallback(async (id: string) => {
    if (!user || isHistoryLoading) return;
    
    setIsHistoryLoading(true);
    setConversationId(id);
    setIsSidebarOpen(false); // Close sidebar on mobile after selection
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
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const startNewChat = () => {
    setConversationId(null);
    setMessages([]);
    setIsSidebarOpen(false);
    if (user) {
      localStorage.removeItem(`chat_conversation_${user.id}`);
    }
  };

  const handleDeleteConversation = async (e: React.MouseEvent, id: string) => {
    e.stopPropagation();
    if (!user || !window.confirm('Are you sure you want to delete this conversation?')) return;

    try {
      await chatService.deleteConversation(id);
      if (conversationId === id) {
        startNewChat();
      }
      await loadConversations();
    } catch (error) {
      console.error('Error deleting conversation:', error);
    }
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!message.trim() || isLoading || !user) return;

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

      if (!conversationId) {
        setConversationId(response.conversation_id);
        localStorage.setItem(`chat_conversation_${user.id}`, response.conversation_id);
        await loadConversations();
      }

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
        content: 'I encountered a communication disruption. Please verify your connection.',
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex flex-col lg:flex-row h-[calc(100dvh-64px)] lg:h-[calc(100vh-120px)] gap-0 lg:gap-6 max-w-7xl mx-auto overflow-hidden relative p-0 lg:p-4 animate-in fade-in duration-500">
      
      {/* Mobile Sidebar Overlay */}
      {isSidebarOpen && (
        <div 
          className="fixed inset-0 bg-background/60 backdrop-blur-md z-40 lg:hidden transition-all duration-300"
          onClick={() => setIsSidebarOpen(false)}
        />
      )}

      {/* Sidebar - Conversation History */}
      <div className={`
        fixed lg:relative inset-y-0 left-0 z-50 w-[85vw] max-w-xs lg:w-72 
        bg-card/98 lg:bg-card/40 backdrop-blur-3xl 
        border-r lg:border border-border/50 
        transition-all duration-500 cubic-bezier(0.4, 0, 0.2, 1) transform
        ${isSidebarOpen ? 'translate-x-0 shadow-[20px_0_50px_rgba(0,0,0,0.3)]' : '-translate-x-full lg:translate-x-0'}
        flex flex-col lg:rounded-[2.5rem] overflow-hidden lg:shadow-2xl
      `}>
        <div className="p-6 border-b border-border/30 flex items-center justify-between">
          <h2 className="text-[10px] font-black uppercase tracking-[0.3em] text-muted-foreground opacity-50">Operation Logs</h2>
          <button 
            onClick={() => setIsSidebarOpen(false)}
            className="lg:hidden p-2 text-muted-foreground hover:text-foreground transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M4.293 4.293a1 1 0 011.414 0L10 8.586l4.293-4.293a1 1 0 111.414 1.414L11.414 10l4.293 4.293a1 1 0 01-1.414 1.414L10 11.414l-4.293 4.293a1 1 0 01-1.414-1.414L8.586 10 4.293 5.707a1 1 0 010-1.414z" clipRule="evenodd" />
            </svg>
          </button>
        </div>

        <div className="p-4">
          <button 
            onClick={startNewChat}
            className="w-full h-14 flex items-center justify-center gap-3 bg-primary text-primary-foreground rounded-2xl hover:bg-primary/90 transition-all shadow-lg active:scale-95 font-black uppercase tracking-widest text-[10px] sm:text-[11px]"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={3} d="M12 4v16m8-8H4" />
            </svg>
            Initalize New Sync
          </button>
        </div>
        
        <div className="flex-1 overflow-y-auto p-3 space-y-2 custom-scrollbar">
          {isListLoading ? (
            <div className="space-y-3 p-2">
              {[1, 2, 3, 4].map(i => (
                <div key={i} className="h-16 bg-muted/40 rounded-2xl animate-pulse"></div>
              ))}
            </div>
          ) : listError ? (
            <div className="text-center py-10 px-4">
              <p className="text-[10px] font-black uppercase tracking-widest text-destructive mb-4">{listError}</p>
              <button 
                onClick={loadConversations}
                className="text-[10px] font-black uppercase tracking-widest bg-muted hover:bg-muted/80 px-6 py-3 rounded-xl transition-all"
              >
                Retry Link
              </button>
            </div>
          ) : conversations.length === 0 ? (
            <div className="text-center py-12 px-4">
              <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground opacity-30 italic">No historical data records</p>
            </div>
          ) : (
            conversations.map((conv) => (
              <div key={conv.id} className="group relative">
                <button
                  onClick={() => handleSelectConversation(conv.id)}
                  className={`w-full text-left p-4 rounded-2xl transition-all border ${
                    conversationId === conv.id 
                      ? 'bg-primary/10 border-primary/30 shadow-md' 
                      : 'hover:bg-muted/40 border-transparent'
                  }`}
                >
                  <div className={`text-[13px] font-bold truncate pr-6 leading-tight ${conversationId === conv.id ? 'text-primary' : 'text-foreground'}`}>
                    {conv.title || 'Untitled Operation'}
                  </div>
                  <div className="text-[9px] text-muted-foreground mt-2 flex items-center justify-between font-black uppercase tracking-widest opacity-60">
                    <span>{new Date(conv.last_activity || conv.updated_at).toLocaleDateString()}</span>
                    <span className="bg-muted px-2 py-0.5 rounded-md">{conv.message_count || 0} Logs</span>
                  </div>
                </button>
                <button
                  onClick={(e) => handleDeleteConversation(e, conv.id)}
                  className="absolute right-3 top-1/2 -translate-y-1/2 p-2 text-muted-foreground/30 hover:text-destructive opacity-0 group-hover:opacity-100 transition-all rounded-xl hover:bg-destructive/10"
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
      <div className="flex-1 flex flex-col bg-card/60 lg:bg-card border-l lg:border border-border/50 lg:rounded-[2.5rem] shadow-2xl relative overflow-hidden">
        
        {/* Chat Header */}
        <div className="p-4 lg:p-6 border-b border-border/30 bg-card/50 backdrop-blur-md flex items-center justify-between z-10 shrink-0">
          <div className="flex items-center gap-4">
            <button 
              onClick={() => setIsSidebarOpen(true)}
              className="lg:hidden p-2.5 bg-muted/50 text-foreground rounded-2xl hover:bg-muted active:scale-95 transition-all shadow-sm"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2.5} d="M4 6h16M4 12h16M4 18h16" />
              </svg>
            </button>
            <div className="w-10 h-10 lg:w-12 lg:h-12 rounded-2xl bg-primary/15 flex items-center justify-center text-primary shadow-inner shrink-0 leading-none">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 lg:h-6 lg:w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
              </svg>
            </div>
            <div className="min-w-0">
              <h1 className="font-black text-foreground tracking-tighter text-[13px] lg:text-base truncate">AI INTELLIGENCE</h1>
              <div className="flex items-center gap-2">
                <span className="flex h-1.5 w-1.5 rounded-full bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.6)] animate-pulse"></span>
                <p className="text-[9px] lg:text-[10px] font-black uppercase tracking-widest text-muted-foreground opacity-60">System Online</p>
              </div>
            </div>
          </div>
          
          <button 
            onClick={startNewChat}
            className="hidden sm:flex items-center gap-2 px-4 py-2 bg-muted/50 hover:bg-primary/10 hover:text-primary rounded-xl text-[10px] font-black uppercase tracking-widest transition-all border border-border/30"
          >
            New Sync
          </button>
        </div>

        {/* Messages Space */}
        <div className="flex-1 overflow-y-auto p-4 lg:p-8 space-y-8 custom-scrollbar relative">
          {isHistoryLoading ? (
            <div className="h-full flex flex-col items-center justify-center space-y-6">
              <div className="w-12 h-12 border-4 border-primary/20 border-t-primary rounded-full animate-spin"></div>
              <p className="text-[10px] font-black uppercase tracking-widest text-muted-foreground opacity-50">Syncing Neuronal Data...</p>
            </div>
          ) : messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center px-4 animate-in fade-in zoom-in-95 duration-500">
              <div className="w-16 h-16 lg:w-24 lg:h-24 bg-primary/10 rounded-[2.5rem] flex items-center justify-center mb-8 rotate-6 shadow-xl border border-primary/5">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 lg:h-12 lg:w-12 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-xl lg:text-3xl font-black text-foreground mb-4 tracking-tighter">MISSION <span className="text-primary italic">CONTROL</span></h3>
              <p className="text-xs lg:text-sm text-muted-foreground max-w-sm mb-12 leading-relaxed font-medium opacity-70">
                Execute complex todo operations via secure AI-link. What are our objectives today?
              </p>
              <div className="grid grid-cols-1 gap-3 w-full max-w-md px-2">
                {[
                  "Deploy a task: 'Finalize quarterly report'",
                  "Display all pending operations",
                  "Terminate completed tasks",
                ].map((hint, idx) => (
                  <button 
                    key={idx}
                    onClick={() => setMessage(hint.replace("Deploy a task: ", "").replace("Display all ", "").replace("Terminate ", "").replace(/'/g, ""))}
                    className="text-[11px] text-left p-4 rounded-2xl border border-border/50 bg-card/40 hover:border-primary/40 hover:bg-primary/5 transition-all flex items-center gap-4 group font-bold tracking-tight"
                  >
                    <span className="w-1 h-3 bg-primary/20 group-hover:bg-primary transition-all rounded-full"></span>
                    {hint}
                  </button>
                ))}
              </div>
            </div>
          ) : (
            <div className="space-y-6 lg:space-y-8 max-w-4xl mx-auto w-full">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'} animate-in slide-in-from-bottom-2 duration-400`}
                >
                  <div
                    className={`max-w-[92%] sm:max-w-[80%] px-4 sm:px-6 py-3 sm:py-4 rounded-3xl shadow-xl transition-all border break-words ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground border-primary/20 rounded-tr-none'
                        : 'bg-muted/40 text-foreground border-border/30 rounded-tl-none backdrop-blur-xl'
                    }`}
                  >
                    <div className="text-sm sm:text-[15px] leading-relaxed font-medium">{msg.content}</div>
                    <div className={`text-[9px] mt-2 sm:mt-3 font-black tracking-[0.2em] uppercase opacity-40 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} className="h-4" />
            </div>
          )}
        </div>

        {/* Input area */}
        <div className="p-4 lg:p-8 bg-card/80 backdrop-blur-3xl border-t border-border/30 shrink-0">
          <form onSubmit={handleSubmit} className="relative max-w-4xl mx-auto group">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Transmit Command..."
              disabled={isLoading || isHistoryLoading}
              className="w-full h-14 lg:h-16 bg-background/50 border border-input/40 rounded-3xl pl-6 pr-16 py-4 text-sm lg:text-base shadow-2xl focus:outline-none focus:ring-4 focus:ring-primary/10 focus:border-primary/60 transition-all disabled:opacity-50 font-bold tracking-tight placeholder:opacity-30"
            />
            <button
              type="submit"
              disabled={isLoading || !message.trim() || isHistoryLoading}
              className="absolute right-2.5 top-2.5 lg:right-3 lg:top-3 h-9 w-9 lg:h-10 lg:w-10 bg-primary text-primary-foreground rounded-2xl hover:bg-primary/90 focus:outline-none disabled:opacity-50 transition-all active:scale-95 shadow-lg flex items-center justify-center"
            >
              {isLoading ? (
                <div className="w-5 h-5 border-2 border-primary-foreground/30 border-t-primary-foreground rounded-full animate-spin"></div>
              ) : (
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" viewBox="0 0 20 20" fill="currentColor">
                  <path d="M10.894 2.553a1 1 0 00-1.788 0l-7 14a1 1 0 001.169 1.409l5-1.429A1 1 0 009 15.571V11a1 1 0 112 0v4.571a1 1 0 00.725.962l5 1.428a1 1 0 001.17-1.408l-7-14z" />
                </svg>
              )}
            </button>
          </form>
          <div className="mt-4 text-[9px] text-center text-muted-foreground font-black tracking-[0.3em] uppercase opacity-30 flex items-center justify-center gap-3">
             <span className="w-8 h-[1px] bg-border/40"></span>
             {isLoading ? 'Processing Signal' : 'Secure Connection Active'}
             <span className="w-8 h-[1px] bg-border/40"></span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChatPage;