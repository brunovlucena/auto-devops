'use client';

import React from 'react';
import { Menu, Settings, Activity, AlertCircle, CheckCircle } from 'lucide-react';

interface HeaderProps {
  onMenuClick: () => void;
  jamieStatus?: any;
}

export function Header({ onMenuClick, jamieStatus }: HeaderProps) {
  const getStatusIcon = () => {
    if (!jamieStatus) return <AlertCircle className="text-jamie-warning" size={20} />;
    
    if (jamieStatus.ai_status?.brain_active) {
      return <CheckCircle className="text-jamie-success" size={20} />;
    } else {
      return <AlertCircle className="text-jamie-warning" size={20} />;
    }
  };

  const getStatusText = () => {
    if (!jamieStatus) return "Connecting...";
    
    if (jamieStatus.ai_status?.brain_active) {
      return "AI Brain Active";
    } else {
      return "Basic Mode";
    }
  };

  return (
    <header className="bg-white border-b border-jamie-border px-4 py-3 flex items-center justify-between">
      {/* Left side */}
      <div className="flex items-center gap-4">
        <button
          onClick={onMenuClick}
          className="lg:hidden p-2 hover:bg-jamie-background rounded-lg transition-colors"
        >
          <Menu size={20} />
        </button>
        
        <div className="flex items-center gap-3">
          <div className="w-8 h-8 bg-jamie-secondary rounded-full flex items-center justify-center">
            <span className="text-white font-bold text-sm">🤖</span>
          </div>
          <div>
            <h1 className="font-bold text-gray-900">Jamie</h1>
            <p className="text-xs text-jamie-muted">AI DevOps Copilot</p>
          </div>
        </div>
      </div>

      {/* Right side */}
      <div className="flex items-center gap-4">
        {/* Status indicator */}
        <div className="hidden sm:flex items-center gap-2 px-3 py-1 bg-jamie-background rounded-full">
          {getStatusIcon()}
          <span className="text-sm font-medium text-gray-700">
            {getStatusText()}
          </span>
        </div>

        {/* Settings button */}
        <button className="p-2 hover:bg-jamie-background rounded-lg transition-colors">
          <Settings size={20} className="text-jamie-muted" />
        </button>
      </div>
    </header>
  );
} 