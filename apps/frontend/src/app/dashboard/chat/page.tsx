'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAuth } from '@/context/auth-context';
import chatService from '@/services/chat-service';

const ChatPage = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<{id: string, role: string, content: string, timestamp: Date}[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  
  interface SearchResult {
    id: string;
    role: string;
    content: string;
    timestamp: string;
  }

  const [searchResults, setSearchResults] = useState<SearchResult[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);

  const { user } = useAuth();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Load conversation from localStorage if available
  useEffect(() => {
    if (user) {
      const savedConversationId = localStorage.getItem(`chat_conversation_${user.id}`);
      if (savedConversationId) {
        setConversationId(savedConversationId);
      }
    }
  }, [user]);

  // Save conversation to localStorage when it changes
  useEffect(() => {
    if (user && conversationId) {
      localStorage.setItem(`chat_conversation_${user.id}`, conversationId);
    }
  }, [conversationId, user]);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

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

      // Add error message to UI
      const errorMessage = {
        id: Date.now().toString(),
        role: 'assistant',
        content: 'Sorry, I encountered an error processing your request. Please try again.',
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!searchQuery.trim() || !user) return;

    setIsSearching(true);
    setShowSearchResults(true);

    try {
      // Call the search API endpoint
      const results = await chatService.searchConversations(user.id, searchQuery, 20, 0);
      setSearchResults(results.messages || []);
    } catch (error) {
      console.error('Error searching conversations:', error);
      setSearchResults([]);
    } finally {
      setIsSearching(false);
    }
  };

  const clearSearch = () => {
    setSearchQuery('');
    setSearchResults([]);
    setShowSearchResults(false);
  };

  return (
    <div className="max-w-4xl mx-auto py-2">
      <h1 className="text-3xl font-bold text-foreground mb-6">AI Todo Assistant</h1>

      {/* Search bar */}
      <div className="bg-card border border-border rounded-lg shadow-sm p-4 mb-6 transition-all hover:shadow-md">
        <form onSubmit={handleSearch} className="flex gap-2">
          <input
            type="text"
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            placeholder="Search in past conversations..."
            className="flex-1 border border-input rounded-lg px-4 py-2 bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all"
          />
          <button
            type="submit"
            disabled={isSearching || !searchQuery.trim()}
            className="bg-primary text-primary-foreground px-6 py-2 rounded-lg hover:bg-primary/90 focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50 transition-colors"
          >
            {isSearching ? 'Search...' : 'Search'}
          </button>
          {showSearchResults && (
            <button
              type="button"
              onClick={clearSearch}
              className="bg-muted text-muted-foreground px-4 py-2 rounded-lg hover:bg-muted/80 focus:outline-none focus:ring-2 focus:ring-primary transition-colors"
            >
              Clear
            </button>
          )}
        </form>

        {/* Search results */}
        {showSearchResults && (
          <div className="mt-4 border-t border-border pt-4 animate-in fade-in slide-in-from-top-2">
            <h3 className="font-medium text-foreground mb-3">Found Messages:</h3>
            {searchResults.length > 0 ? (
              <div className="space-y-2 max-h-56 overflow-y-auto pr-2 custom-scrollbar">
                {searchResults.map((result) => (
                  <div key={result.id} className="p-3 bg-muted/30 rounded-lg border border-border hover:bg-muted/50 transition-colors cursor-pointer">
                    <div className="text-sm font-medium text-foreground capitalize mb-1">{result.role}</div>
                    <div className="text-sm text-muted-foreground line-clamp-2 italic">&ldquo;{result.content}&rdquo;</div>
                    <div className="text-[10px] text-muted-foreground mt-2 text-right">{new Date(result.timestamp).toLocaleString()}</div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="text-muted-foreground text-sm italic py-4 text-center">No results matched your query.</div>
            )}
          </div>
        )}
      </div>

      <div className="bg-card border border-border rounded-lg shadow-sm p-6 mb-6">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-lg font-semibold text-foreground flex items-center">
            <span className="inline-block w-2 h-2 rounded-full bg-green-500 mr-2 animate-pulse"></span>
            {conversationId ? `Chat Session: ...${conversationId.substring(conversationId.length - 8)}` : 'New Chat Session'}
          </h2>
        </div>

        {/* Messages container */}
        <div className="border border-border rounded-lg h-[500px] overflow-y-auto p-4 mb-6 bg-muted/10 custom-scrollbar flex flex-col">
          {messages.length === 0 ? (
            <div className="flex-1 flex flex-col items-center justify-center text-center px-8">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-foreground mb-2">How can I help you today?</h3>
              <p className="text-sm text-muted-foreground max-w-sm">
                You can ask me to create todos, list your tasks, or mark things as complete. 
                Try saying: &ldquo;Remind me to buy groceries tomorrow&rdquo;
              </p>
            </div>
          ) : (
            <div className="space-y-6">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[85%] px-4 py-3 rounded-2xl shadow-sm ${
                      msg.role === 'user'
                        ? 'bg-primary text-primary-foreground rounded-tr-none'
                        : 'bg-card text-foreground border border-border rounded-tl-none'
                    }`}
                  >
                    <div className="whitespace-pre-wrap text-sm leading-relaxed">{msg.content}</div>
                    <div className={`text-[10px] mt-2 opacity-70 ${msg.role === 'user' ? 'text-right' : 'text-left'}`}>
                      {msg.timestamp.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </div>
                  </div>
                </div>
              ))}
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* Input form */}
        <form onSubmit={handleSubmit} className="relative">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            placeholder="Talk to your tasks..."
            disabled={isLoading}
            className="w-full border border-input rounded-xl pl-4 pr-14 py-3 bg-background text-foreground focus:outline-none focus:ring-2 focus:ring-primary transition-all disabled:opacity-50"
          />
          <button
            type="submit"
            disabled={isLoading || !message.trim()}
            className="absolute right-2 top-1.5 p-2 bg-primary text-primary-foreground rounded-lg hover:bg-primary/90 focus:outline-none disabled:opacity-50 transition-colors"
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

        {isLoading && (
          <div className="mt-3 text-xs text-muted-foreground flex items-center justify-center animate-pulse">
            <span>Assistant is thinking...</span>
          </div>
        )}
      </div>
    </div>
  );
};

export default ChatPage;