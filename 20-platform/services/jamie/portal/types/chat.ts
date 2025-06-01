export interface ChatMessage {
  id: string;
  content: string;
  role: 'user' | 'assistant';
  timestamp: Date;
  metadata?: {
    confidence?: number;
    topics?: string[];
    intent?: string;
    devops_data?: any;
  };
}

export interface ChatSession {
  id: string;
  title: string;
  messages: ChatMessage[];
  created_at: Date;
  updated_at: Date;
}

export interface JamieResponse {
  response: string;
  timestamp: string;
  session_id: string;
  confidence?: number;
  topics?: string[];
  intent?: string;
}

export interface JamieHealthStatus {
  status: string;
  message: string;
  timestamp: string;
  ai_status: {
    brain_active: boolean;
    vector_memory_active: boolean;
    llm_model: string;
    memory_collections: number;
    mcp_servers?: Record<string, any>;
  };
}

export interface DevOpsData {
  cluster_status?: any;
  recent_errors?: any;
  service_overview?: any;
  search_results?: any;
}

export interface WebSocketMessage {
  type: 'message' | 'typing' | 'error' | 'status';
  content?: string;
  data?: any;
  timestamp: string;
} 