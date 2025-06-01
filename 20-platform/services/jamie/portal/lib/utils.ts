import { type ClassValue, clsx } from 'clsx';

export function cn(...inputs: ClassValue[]) {
  return clsx(inputs);
}

export function generateId(): string {
  return Math.random().toString(36).substring(2) + Date.now().toString(36);
}

export function formatTimestamp(date: Date): string {
  const now = new Date();
  const diff = now.getTime() - date.getTime();
  
  // Less than 1 minute
  if (diff < 60000) {
    return 'Just now';
  }
  
  // Less than 1 hour
  if (diff < 3600000) {
    const minutes = Math.floor(diff / 60000);
    return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
  }
  
  // Less than 1 day
  if (diff < 86400000) {
    const hours = Math.floor(diff / 3600000);
    return `${hours} hour${hours > 1 ? 's' : ''} ago`;
  }
  
  // More than 1 day
  return date.toLocaleString();
}

export function truncateText(text: string, maxLength: number): string {
  if (text.length <= maxLength) return text;
  return text.substring(0, maxLength) + '...';
}

export function extractDevOpsContext(message: string): Record<string, any> {
  const context: Record<string, any> = {};
  
  // Check for DevOps keywords
  const keywords = [
    'kubernetes', 'k8s', 'pod', 'deployment', 'service',
    'prometheus', 'grafana', 'metrics', 'alert',
    'loki', 'logs', 'error', 'debug',
    'cluster', 'node', 'namespace',
    'cpu', 'memory', 'disk', 'network'
  ];
  
  const foundKeywords = keywords.filter(keyword => 
    message.toLowerCase().includes(keyword)
  );
  
  if (foundKeywords.length > 0) {
    context.devops_intent = true;
    context.keywords = foundKeywords;
  }
  
  return context;
}

export function getBritishGreeting(): string {
  const hour = new Date().getHours();
  
  if (hour < 12) {
    return "Good morning";
  } else if (hour < 17) {
    return "Good afternoon"; 
  } else {
    return "Good evening";
  }
}

export const JAMIE_SUGGESTIONS = [
  "How's my cluster doing?",
  "Show me recent errors",
  "What's the CPU usage?",
  "Any alerts firing?",
  "Check pod status",
  "Search logs for 'timeout'",
  "Memory usage across nodes",
  "Service health overview"
]; 