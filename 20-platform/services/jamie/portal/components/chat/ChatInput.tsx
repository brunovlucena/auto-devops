'use client';

import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2, Zap } from 'lucide-react';
import { JAMIE_SUGGESTIONS } from '@/lib/utils';

interface ChatInputProps {
  onSendMessage: (message: string) => void;
  isLoading?: boolean;
  disabled?: boolean;
}

export function ChatInput({ onSendMessage, isLoading = false, disabled = false }: ChatInputProps) {
  const [message, setMessage] = useState('');
  const [showSuggestions, setShowSuggestions] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !isLoading && !disabled) {
      onSendMessage(message.trim());
      setMessage('');
      setShowSuggestions(false);
      
      // Reset textarea height
      if (textareaRef.current) {
        textareaRef.current.style.height = 'auto';
      }
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessage(e.target.value);
    
    // Auto-resize textarea
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${textareaRef.current.scrollHeight}px`;
    }
    
    // Show suggestions for empty input
    setShowSuggestions(e.target.value.trim() === '');
  };

  const handleSuggestionClick = (suggestion: string) => {
    setMessage(suggestion);
    setShowSuggestions(false);
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  };

  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  return (
    <div className="relative">
      {/* Suggestions */}
      {showSuggestions && message.trim() === '' && (
        <div className="absolute bottom-full mb-2 w-full bg-white border border-jamie-border rounded-lg shadow-lg p-4">
          <div className="flex items-center gap-2 mb-3">
            <Zap size={16} className="text-jamie-primary" />
            <span className="text-sm font-medium text-jamie-muted">
              Try asking Jamie:
            </span>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-2">
            {JAMIE_SUGGESTIONS.map((suggestion, index) => (
              <button
                key={index}
                onClick={() => handleSuggestionClick(suggestion)}
                className="text-left p-2 text-sm bg-jamie-background hover:bg-jamie-border rounded-md transition-colors"
              >
                {suggestion}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Input Form */}
      <form onSubmit={handleSubmit} className="relative">
        <div className="flex items-end gap-2 p-4 bg-white border-t border-jamie-border">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              onFocus={() => setShowSuggestions(message.trim() === '')}
              onBlur={() => setTimeout(() => setShowSuggestions(false), 150)}
              placeholder="Ask Jamie about your infrastructure... (Shift+Enter for new line)"
              className="w-full min-h-[44px] max-h-32 px-4 py-3 pr-12 border border-jamie-border rounded-lg 
                        resize-none focus:outline-none focus:ring-2 focus:ring-jamie-primary focus:border-transparent
                        placeholder-jamie-muted"
              disabled={disabled || isLoading}
              rows={1}
            />
            
            {/* Character count */}
            {message.length > 100 && (
              <div className="absolute bottom-1 left-2 text-xs text-jamie-muted">
                {message.length}/1000
              </div>
            )}
          </div>

          {/* Send Button */}
          <button
            type="submit"
            disabled={!message.trim() || isLoading || disabled}
            className="flex-shrink-0 w-11 h-11 flex items-center justify-center bg-jamie-primary 
                      text-white rounded-lg hover:bg-blue-600 disabled:opacity-50 disabled:cursor-not-allowed
                      transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-jamie-primary focus:ring-offset-2"
          >
            {isLoading ? (
              <Loader2 size={20} className="animate-spin" />
            ) : (
              <Send size={20} />
            )}
          </button>
        </div>
      </form>

      {/* Loading indicator */}
      {isLoading && (
        <div className="absolute top-0 left-0 right-0 h-1 bg-jamie-background overflow-hidden">
          <div className="h-full bg-jamie-primary animate-pulse" />
        </div>
      )}
    </div>
  );
} 