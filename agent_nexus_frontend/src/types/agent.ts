import { ExecutionStep } from '../visualization/timelines/ExecutionTimeline';

export enum AgentStatus {
  IDLE = 'idle',
  RUNNING = 'running',
  PAUSED = 'paused',
  ERROR = 'error',
  COMPLETE = 'complete',
}

export enum ToolType {
  API = 'api',
  INTERNAL = 'internal',
  DATABASE = 'database',
  FILE_SYSTEM = 'file_system',
}

export interface AgentTool {
  id: string;
  name: string;
  description: string;
  type: ToolType;
  schema: Record<string, unknown>;
  is_enabled: boolean;
}

export interface AgentMemory {
  id: string;
  type: 'short_term' | 'long_term' | 'episodic';
  content: string;
  timestamp: Date;
  metadata: Record<string, unknown>;
}

export interface AgentConfiguration {
  model_name: string;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  config: AgentConfiguration;
  tools: AgentTool[];
  created_at: Date;
  updated_at: Date;
}

export interface AgentTask {
  id: string;
  agent_id: string;
  name: string;
  prompt: string;
  status: AgentStatus;
  execution_log: ExecutionStep[];
  start_time: Date;
  end_time?: Date;
  result?: string;
}

export interface AgentTelemetry {
  timestamp: Date;
  cpu_usage_percent: number;
  memory_usage_mb: number;
  api_calls_count: number;
  token_cost_usd: number;
}