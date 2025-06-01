'use client';

import React from 'react';
import { X, Activity, Server, Database, Eye, GitBranch, AlertTriangle } from 'lucide-react';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  jamieStatus?: any;
}

export function Sidebar({ isOpen, onClose, jamieStatus }: SidebarProps) {
  const mcpServers = jamieStatus?.ai_status?.mcp_servers || {};

  return (
    <>
      {/* Backdrop */}
      {isOpen && (
        <div 
          className="fixed inset-0 bg-black bg-opacity-50 lg:hidden z-40"
          onClick={onClose}
        />
      )}

      {/* Sidebar */}
      <div className={`
        fixed lg:relative inset-y-0 left-0 z-50 w-80 bg-white border-r border-jamie-border
        transform transition-transform duration-300 ease-in-out lg:translate-x-0
        ${isOpen ? 'translate-x-0' : '-translate-x-full lg:translate-x-0'}
      `}>
        <div className="flex flex-col h-full">
          {/* Header */}
          <div className="flex items-center justify-between p-4 border-b border-jamie-border">
            <h2 className="text-lg font-semibold text-gray-900">Jamie Status</h2>
            <button 
              onClick={onClose}
              className="lg:hidden p-2 hover:bg-jamie-background rounded-lg"
            >
              <X size={20} />
            </button>
          </div>

          {/* Content */}
          <div className="flex-1 overflow-y-auto p-4 space-y-6">
            {/* AI Status */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-900 flex items-center gap-2">
                <Activity size={16} />
                AI System Status
              </h3>
              
              <div className="space-y-2">
                <div className="flex items-center justify-between py-2 px-3 bg-jamie-background rounded-lg">
                  <span className="text-sm">AI Brain</span>
                  <div className={`w-2 h-2 rounded-full ${
                    jamieStatus?.ai_status?.brain_active ? 'bg-jamie-success' : 'bg-jamie-error'
                  }`} />
                </div>
                
                <div className="flex items-center justify-between py-2 px-3 bg-jamie-background rounded-lg">
                  <span className="text-sm">Vector Memory</span>
                  <div className={`w-2 h-2 rounded-full ${
                    jamieStatus?.ai_status?.vector_memory_active ? 'bg-jamie-success' : 'bg-jamie-error'
                  }`} />
                </div>

                {jamieStatus?.ai_status?.llm_model && (
                  <div className="py-2 px-3 bg-jamie-background rounded-lg">
                    <span className="text-sm text-jamie-muted">Model:</span>
                    <span className="text-sm ml-2">{jamieStatus.ai_status.llm_model}</span>
                  </div>
                )}
              </div>
            </div>

            {/* MCP Servers */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-900 flex items-center gap-2">
                <Server size={16} />
                DevOps Integrations
              </h3>
              
              <div className="space-y-2">
                {Object.entries(mcpServers).map(([serverName, serverStatus]: [string, any]) => (
                  <div key={serverName} className="py-2 px-3 bg-jamie-background rounded-lg">
                    <div className="flex items-center justify-between">
                      <div className="flex items-center gap-2">
                        <ServerIcon serverName={serverName} />
                        <span className="text-sm capitalize">{serverName}</span>
                      </div>
                      <div className={`w-2 h-2 rounded-full ${
                        serverStatus?.connected ? 'bg-jamie-success' : 'bg-jamie-error'
                      }`} />
                    </div>
                    
                    {serverStatus?.capabilities && (
                      <div className="mt-1 text-xs text-jamie-muted">
                        {serverStatus.capabilities.length} capabilities
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Quick Actions */}
            <div className="space-y-3">
              <h3 className="text-sm font-medium text-gray-900 flex items-center gap-2">
                <Eye size={16} />
                Quick Actions
              </h3>
              
              <div className="space-y-2">
                <button className="w-full text-left py-2 px-3 bg-jamie-background hover:bg-jamie-border rounded-lg transition-colors">
                  <div className="text-sm">Cluster Health</div>
                  <div className="text-xs text-jamie-muted">Check all systems</div>
                </button>
                
                <button className="w-full text-left py-2 px-3 bg-jamie-background hover:bg-jamie-border rounded-lg transition-colors">
                  <div className="text-sm">Recent Errors</div>
                  <div className="text-xs text-jamie-muted">Last hour analysis</div>
                </button>
                
                <button className="w-full text-left py-2 px-3 bg-jamie-background hover:bg-jamie-border rounded-lg transition-colors">
                  <div className="text-sm">Performance Metrics</div>
                  <div className="text-xs text-jamie-muted">CPU, Memory, Network</div>
                </button>
              </div>
            </div>

            {/* Footer Info */}
            <div className="pt-4 border-t border-jamie-border">
              <div className="text-xs text-jamie-muted space-y-1">
                <div>Jamie AI DevOps Copilot</div>
                <div>Sprint 4: Chat Portal</div>
                <div className="flex items-center gap-1">
                  <div className="w-1 h-1 bg-jamie-success rounded-full" />
                  Connected to infrastructure
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
}

function ServerIcon({ serverName }: { serverName: string }) {
  switch (serverName) {
    case 'kubernetes':
      return <Server size={14} className="text-blue-500" />;
    case 'prometheus':
      return <Activity size={14} className="text-red-500" />;
    case 'loki':
      return <Database size={14} className="text-green-500" />;
    case 'github':
      return <GitBranch size={14} className="text-gray-700" />;
    default:
      return <AlertTriangle size={14} className="text-jamie-muted" />;
  }
} 