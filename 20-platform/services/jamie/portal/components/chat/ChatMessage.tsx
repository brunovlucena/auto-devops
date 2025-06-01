'use client';

import React from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import rehypeHighlight from 'rehype-highlight';
import { User, Bot, Clock, Brain, AlertTriangle } from 'lucide-react';
import { ChatMessage as ChatMessageType } from '@/types/chat';
import { formatTimestamp } from '@/lib/utils';

interface ChatMessageProps {
  message: ChatMessageType;
  isStreaming?: boolean;
}

export function ChatMessage({ message, isStreaming = false }: ChatMessageProps) {
  const isUser = message.role === 'user';
  const isJamie = message.role === 'assistant';

  return (
    <div className={`flex gap-4 p-4 ${isJamie ? 'bg-jamie-background' : 'bg-white'} 
                    animate-slide-up transition-all duration-300`}>
      {/* Avatar */}
      <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center
                      ${isUser ? 'bg-jamie-primary text-white' : 'bg-jamie-secondary text-white'}
                      ${isStreaming ? 'animate-pulse-glow' : ''}`}>
        {isUser ? (
          <User size={20} />
        ) : (
          <Bot size={20} />
        )}
      </div>

      {/* Message Content */}
      <div className="flex-1 min-w-0">
        {/* Header */}
        <div className="flex items-center gap-2 mb-2">
          <span className="font-semibold text-gray-900">
            {isUser ? 'You' : 'Jamie'}
          </span>
          {isJamie && (
            <span className="text-xs px-2 py-1 bg-jamie-secondary text-white rounded-full">
              🤖 AI DevOps Copilot
            </span>
          )}
          <div className="flex items-center gap-1 text-xs text-jamie-muted">
            <Clock size={12} />
            {formatTimestamp(message.timestamp)}
          </div>
        </div>

        {/* Message Body */}
        <div className={`prose max-w-none ${isJamie ? 'prose-blue' : 'prose-gray'}`}>
          {isUser ? (
            <p className="text-gray-800 m-0">{message.content}</p>
          ) : (
            <div className="jamie-response">
              <ReactMarkdown
                remarkPlugins={[remarkGfm]}
                rehypePlugins={[rehypeHighlight]}
                components={{
                  // Custom code block styling
                  code: ({ node, inline, className, children, ...props }) => {
                    const match = /language-(\w+)/.exec(className || '');
                    return !inline && match ? (
                      <pre className="bg-gray-900 text-gray-100 rounded-lg p-4 overflow-x-auto">
                        <code className={className} {...props}>
                          {children}
                        </code>
                      </pre>
                    ) : (
                      <code 
                        className="bg-jamie-background px-1 py-0.5 rounded text-sm font-mono" 
                        {...props}
                      >
                        {children}
                      </code>
                    );
                  },
                  // Custom table styling
                  table: ({ children }) => (
                    <div className="overflow-x-auto">
                      <table className="min-w-full border-collapse border border-jamie-border">
                        {children}
                      </table>
                    </div>
                  ),
                  th: ({ children }) => (
                    <th className="border border-jamie-border bg-jamie-background px-4 py-2 text-left">
                      {children}
                    </th>
                  ),
                  td: ({ children }) => (
                    <td className="border border-jamie-border px-4 py-2">
                      {children}
                    </td>
                  ),
                }}
              >
                {message.content}
              </ReactMarkdown>
              
              {isStreaming && (
                <span className="inline-block w-3 h-5 bg-jamie-primary animate-typing ml-1" />
              )}
            </div>
          )}
        </div>

        {/* Metadata */}
        {message.metadata && (
          <div className="mt-3 flex flex-wrap gap-2">
            {message.metadata.confidence && (
              <div className="flex items-center gap-1 text-xs bg-white px-2 py-1 rounded-full border">
                <Brain size={12} />
                <span>Confidence: {Math.round(message.metadata.confidence * 100)}%</span>
              </div>
            )}
            
            {message.metadata.intent && (
              <div className="text-xs bg-jamie-primary text-white px-2 py-1 rounded-full">
                Intent: {message.metadata.intent}
              </div>
            )}
            
            {message.metadata.topics && message.metadata.topics.length > 0 && (
              <div className="flex gap-1">
                {message.metadata.topics.map((topic, index) => (
                  <span 
                    key={index}
                    className="text-xs bg-jamie-secondary text-white px-2 py-1 rounded-full"
                  >
                    {topic}
                  </span>
                ))}
              </div>
            )}
            
            {message.metadata.devops_data && (
              <div className="flex items-center gap-1 text-xs bg-jamie-success text-white px-2 py-1 rounded-full">
                <AlertTriangle size={12} />
                DevOps Data Available
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
} 