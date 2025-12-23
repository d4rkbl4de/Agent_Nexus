export interface AgentPulse {
  agentId: string;
  status: 'initializing' | 'running' | 'paused' | 'complete' | 'error';
  thoughtChunk: string;
  confidence: number;
  timestamp: number;
}