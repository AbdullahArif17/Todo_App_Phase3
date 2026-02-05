'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useRouter } from 'next/navigation';
import { useAuth } from '@/context/auth-context';
import chatService, { ChatRequest, ChatResponse, Message } from '@/services/chat-service';

const ChatPage = () => {
  const [message, setMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [messages, setMessages] = useState<{id: string, role: string, content: string, timestamp: Date}[]>([]);
  const [conversationId, setConversationId] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<Message[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [showSearchResults, setShowSearchResults] = useState(false);

  const router = useRouter();
  const { user, isAuthenticated } = useAuth();
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

  useEffect(() => {
    if (!isAuthenticated || !user) {
      router.push('/auth/sign-in');
    }
  }, [isAuthenticated, user, router]);

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
      const chatRequest: ChatRequest = {
        conversation_id: conversationId || undefined,
        message: message
      };

      const response = await chatService.sendMessage(user.id, chatRequest);

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
      // This would call the search API endpoint
      // For now, we'll simulate the search functionality
      console.log(`Searching for: ${searchQuery}`);

      // In a real implementation, we would call the search API
      // const results = await chatService.searchConversations(user.id, searchQuery);
      // setSearchResults(results);

      // For demo purposes, we'll just show a message
      setSearchResults([]);
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
    <div className="min-h-screen bg-gray-50">
      <div className="max-w-4xl mx-auto px-4 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-6">AI Todo Assistant</h1>

        {/* Search bar */}
        <div className="bg-white rounded-lg shadow-md p-4 mb-6">
          <form onSubmit={handleSearch} className="flex gap-2">
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Search conversations..."
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500"
            />
            <button
              type="submit"
              disabled={isSearching || !searchQuery.trim()}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300 disabled:cursor-not-allowed"
            >
              {isSearching ? 'Searching...' : 'Search'}
            </button>
            {showSearchResults && (
              <button
                type="button"
                onClick={clearSearch}
                className="bg-gray-300 text-gray-700 px-4 py-2 rounded-lg hover:bg-gray-400 focus:outline-none focus:ring-2 focus:ring-gray-500"
              >
                Clear
              </button>
            )}
          </form>

          {/* Search results */}
          {showSearchResults && (
            <div className="mt-4">
              <h3 className="font-medium text-gray-700 mb-2">Search Results:</h3>
              {searchResults.length > 0 ? (
                <div className="space-y-2 max-h-40 overflow-y-auto">
                  {searchResults.map((result) => (
                    <div key={result.id} className="p-2 bg-gray-100 rounded border">
                      <div className="text-sm font-medium text-gray-900">{result.role}: {result.content.substring(0, 60)}...</div>
                      <div className="text-xs text-gray-500">{new Date(result.timestamp).toLocaleString()}</div>
                    </div>
                  ))}
                </div>
              ) : (
                <div className="text-gray-500 text-sm">No results found for "{searchQuery}"</div>
              )}
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-xl font-semibold text-gray-800">
              {conversationId ? `Conversation: ${conversationId.substring(0, 8)}...` : 'New Conversation'}
            </h2>
          </div>

          {/* Messages container */}
          <div className="border border-gray-200 rounded-lg h-96 overflow-y-auto p-4 mb-4 bg-gray-50">
            {messages.length === 0 ? (
              <div className="h-full flex items-center justify-center text-gray-500">
                <p>Start a conversation with the AI assistant to manage your todos!</p>
              </div>
            ) : (
              <div className="space-y-4">
                {messages.map((msg) => (
                  <div
                    key={msg.id}
                    className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                  >
                    <div
                      className={`max-w-xs lg:max-w-md px-4 py-2 rounded-lg ${
                        msg.role === 'user'
                          ? 'bg-blue-500 text-white'
                          : 'bg-gray-200 text-gray-800'
                      }`}
                    >
                      <div className="whitespace-pre-wrap">{msg.content}</div>
                      <div className={`text-xs mt-1 ${msg.role === 'user' ? 'text-blue-100' : 'text-gray-500'}`}>
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
          <form onSubmit={handleSubmit} className="flex gap-2">
            <input
              type="text"
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              placeholder="Type your message here..."
              disabled={isLoading}
              className="flex-1 border border-gray-300 rounded-lg px-4 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-gray-100"
            />
            <button
              type="submit"
              disabled={isLoading || !message.trim()}
              className="bg-blue-500 text-white px-4 py-2 rounded-lg hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 disabled:bg-blue-300 disabled:cursor-not-allowed"
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </form>

          {isLoading && (
            <div className="mt-2 text-sm text-gray-500 flex items-center">
              <span className="mr-2">AI is thinking...</span>
              <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-blue-500"></div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ChatPage;