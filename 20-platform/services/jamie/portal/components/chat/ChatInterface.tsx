'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import { ChatMessage } from './ChatMessage';
import { ChatInput } from './ChatInput';
import { Sidebar } from '../layout/Sidebar';
import { Header } from '../layout/Header';
import { ChatMessage as ChatMessageType } from '@/types/chat';
import { jamieApi } from '@/lib/jamie-api';
import { generateId, extractDevOpsContext } from '@/lib/utils';

interface ChatInterfaceProps {
  userId?: string;
}

export function ChatInterface({ userId = 'portal_user' }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<ChatMessageType[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [sessionId] = useState(() => generateId());
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [jamieStatus, setJamieStatus] = useState<any>(null);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const wsRef = useRef<WebSocket | null>(null);

  // Scroll to bottom when new messages arrive
  const scrollToBottom = useCallback(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, []);

  useEffect(() => {
    scrollToBottom();
  }, [messages, scrollToBottom]);

  // Initialize WebSocket connection
  useEffect(() => {
    const connectWebSocket = () => {
      try {
        const ws = jamieApi.createWebSocket(userId);
        wsRef.current = ws;

        ws.onopen = () => {
          console.log('Connected to Jamie via WebSocket');
        };

        ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            
            if (data.type === 'message' && data.response) {
              // Add Jamie's response
              const jamieMessage: ChatMessageType = {
                id: generateId(),
                content: data.response,
                role: 'assistant',
                timestamp: new Date(data.timestamp),
                metadata: {
                  confidence: data.confidence,
                  topics: data.topics,
                  intent: data.intent
                }
              };
              
              setMessages(prev => [...prev, jamieMessage]);
              setIsLoading(false);
            }
          } catch (error) {
            console.error('Error parsing WebSocket message:', error);
          }
        };

        ws.onclose = () => {
          console.log('WebSocket connection closed');
          // Attempt to reconnect after 3 seconds
          setTimeout(connectWebSocket, 3000);
        };

        ws.onerror = (error) => {
          console.error('WebSocket error:', error);
        };

      } catch (error) {
        console.error('Failed to connect WebSocket:', error);
        // Fallback to HTTP API
      }
    };

    connectWebSocket();

    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, [userId]);

  // Load Jamie's health status
  useEffect(() => {
    const loadJamieStatus = async () => {
      try {
        const status = await jamieApi.healthCheck();
        setJamieStatus(status);
      } catch (error) {
        console.error('Failed to load Jamie status:', error);
      }
    };

    loadJamieStatus();
    
    // Refresh status every 30 seconds
    const interval = setInterval(loadJamieStatus, 30000);
    return () => clearInterval(interval);
  }, []);

  // Add initial greeting
  useEffect(() => {
    const greeting: ChatMessageType = {
      id: generateId(),
      content: `Alright mate! I'm Jamie, your AI DevOps Copilot! 🤖

I've got my eyes on your infrastructure and I'm ready to help with:
- **Kubernetes clusters** - Pod status, deployments, services
- **Prometheus metrics** - CPU, memory, alerts, performance data  
- **Loki logs** - Error analysis, log searching, real-time tailing
- **DevOps troubleshooting** - Cross-platform investigation

Just ask me anything about your infrastructure - I'll give you the full rundown with a bit of British flair!

Try something like: *"How's my cluster doing?"* or *"Show me recent errors"*`,
      role: 'assistant',
      timestamp: new Date(),
      metadata: {
        intent: 'greeting',
        topics: ['introduction', 'capabilities']
      }
    };

    setMessages([greeting]);
  }, []);

  const handleSendMessage = useCallback(async (messageContent: string) => {
    // Add user message
    const userMessage: ChatMessageType = {
      id: generateId(),
      content: messageContent,
      role: 'user',
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // Extract DevOps context from message
      const context = extractDevOpsContext(messageContent);

      // Send via WebSocket if available
      if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
        wsRef.current.send(JSON.stringify({
          message: messageContent,
          session_id: sessionId,
          context
        }));
      } else {
        // Fallback to HTTP API
        const response = await jamieApi.sendMessage(
          messageContent,
          userId,
          sessionId,
          context
        );

        const jamieMessage: ChatMessageType = {
          id: generateId(),
          content: response.response,
          role: 'assistant',
          timestamp: new Date(response.timestamp),
          metadata: {
            confidence: response.confidence,
            topics: response.topics,
            intent: response.intent
          }
        };

        setMessages(prev => [...prev, jamieMessage]);
        setIsLoading(false);
      }
    } catch (error) {
      console.error('Error sending message:', error);
      
      // Add error message
      const errorMessage: ChatMessageType = {
        id: generateId(),
        content: "Blimey! I'm having a bit of trouble connecting right now. Could you give me a moment to sort myself out?",
        role: 'assistant',
        timestamp: new Date(),
        metadata: {
          intent: 'error'
        }
      };

      setMessages(prev => [...prev, errorMessage]);
      setIsLoading(false);
    }
  }, [sessionId, userId]);

  return (
    <div className="flex h-screen bg-jamie-background">
      {/* Sidebar */}
      <Sidebar 
        isOpen={sidebarOpen}
        onClose={() => setSidebarOpen(false)}
        jamieStatus={jamieStatus}
      />

      {/* Main Chat Area */}
      <div className="flex flex-col flex-1 min-w-0">
        {/* Header */}
        <Header 
          onMenuClick={() => setSidebarOpen(true)}
          jamieStatus={jamieStatus}
        />

        {/* Messages */}
        <div className="flex-1 overflow-y-auto">
          <div className="max-w-4xl mx-auto">
            {messages.map((message, index) => (
              <ChatMessage
                key={message.id}
                message={message}
                isStreaming={index === messages.length - 1 && isLoading && message.role === 'assistant'}
              />
            ))}
            
            {/* Loading message */}
            {isLoading && (
              <div className="flex gap-4 p-4 bg-jamie-background">
                <div className="flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center bg-jamie-secondary text-white animate-pulse-glow">
                  🤖
                </div>
                <div className="flex-1">
                  <div className="font-semibold text-gray-900 mb-2">Jamie</div>
                  <div className="flex items-center gap-2 text-jamie-muted">
                    <div className="w-2 h-2 bg-jamie-primary rounded-full animate-typing" />
                    <div className="w-2 h-2 bg-jamie-primary rounded-full animate-typing" style={{ animationDelay: '0.2s' }} />
                    <div className="w-2 h-2 bg-jamie-primary rounded-full animate-typing" style={{ animationDelay: '0.4s' }} />
                    <span className="ml-2">Jamie is thinking...</span>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>
        </div>

        {/* Chat Input */}
        <ChatInput
          onSendMessage={handleSendMessage}
          isLoading={isLoading}
        />
      </div>
    </div>
  );
} 