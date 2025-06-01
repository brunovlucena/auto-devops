import { ChatMessage, JamieResponse, JamieHealthStatus } from '@/types/chat';

const JAMIE_API_URL = process.env.NEXT_PUBLIC_JAMIE_API_URL || 'http://localhost:8000';

export class JamieApiClient {
  private baseUrl: string;

  constructor(baseUrl: string = JAMIE_API_URL) {
    this.baseUrl = baseUrl;
  }

  async healthCheck(): Promise<JamieHealthStatus> {
    const response = await fetch(`${this.baseUrl}/health`);
    if (!response.ok) {
      throw new Error(`Health check failed: ${response.statusText}`);
    }
    return response.json();
  }

  async sendMessage(
    message: string,
    userId: string = 'portal_user',
    sessionId: string = 'portal_session',
    context?: any
  ): Promise<JamieResponse> {
    const response = await fetch(`${this.baseUrl}/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        message,
        user_id: userId,
        session_id: sessionId,
        context,
      }),
    });

    if (!response.ok) {
      throw new Error(`Chat request failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getClusterStatus() {
    const response = await fetch(`${this.baseUrl}/devops/cluster/status`);
    if (!response.ok) {
      throw new Error(`Cluster status failed: ${response.statusText}`);
    }
    return response.json();
  }

  async getRecentErrors(duration: string = '1h') {
    const response = await fetch(`${this.baseUrl}/devops/errors/recent?duration=${duration}`);
    if (!response.ok) {
      throw new Error(`Recent errors failed: ${response.statusText}`);
    }
    return response.json();
  }

  async getServiceOverview(serviceName: string) {
    const response = await fetch(`${this.baseUrl}/devops/service/${serviceName}`);
    if (!response.ok) {
      throw new Error(`Service overview failed: ${response.statusText}`);
    }
    return response.json();
  }

  async searchDevOps(query: string, platforms?: string[]) {
    const response = await fetch(`${this.baseUrl}/devops/search`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        query,
        platforms,
      }),
    });

    if (!response.ok) {
      throw new Error(`DevOps search failed: ${response.statusText}`);
    }

    return response.json();
  }

  async getMcpStatus() {
    const response = await fetch(`${this.baseUrl}/mcp/status`);
    if (!response.ok) {
      throw new Error(`MCP status failed: ${response.statusText}`);
    }
    return response.json();
  }

  createWebSocket(userId: string): WebSocket {
    const wsUrl = this.baseUrl.replace('http://', 'ws://').replace('https://', 'wss://');
    return new WebSocket(`${wsUrl}/ws/${userId}`);
  }
}

export const jamieApi = new JamieApiClient(); 