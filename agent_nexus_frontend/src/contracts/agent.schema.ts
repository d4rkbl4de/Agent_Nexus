export type MemoryType = 'short_term' | 'long_term' | 'episodic';

export type AgentStatus = 'idle' | 'running' | 'paused' | 'error' | 'complete';

export type ToolType = 'api' | 'internal' | 'database' | 'file_system' | 'custom';

export interface AgentMemoryMetadata {
  token_count?: number;
  source?: string;
  relevance_score?: number;
  [key: string]: any; 
}

export interface AgentMemory {
  id: string;
  timestamp: string;
  type: MemoryType;
  content: string;
  metadata: AgentMemoryMetadata;
}

export interface AgentConfiguration {
  model_name: string;
  temperature: number;
  max_tokens: number;
  system_prompt: string;
}

export interface AgentTool {
  id: string;
  name: string;
  description: string;
  type: ToolType;
  is_enabled: boolean;
  schema?: any;
}

export interface AgentTelemetry {
  timestamp: string;
  cpu_usage_percent: number;
  memory_usage_mb: number;
  api_calls_count: number;
  token_cost_usd: number;
}

export interface ExecutionStepDetails {
  tool_name?: string;
  tool_args?: Record<string, any>;
  result?: string;
  result_type?: string; 
  error_message?: string;
}

export type ExecutionStepStatus = 'PENDING' | 'RUNNING' | 'COMPLETE' | 'ERROR';

export type ExecutionStepType = 'THOUGHT' | 'TOOL_CALL' | 'OBSERVATION' | 'FINAL_ANSWER';

export interface ExecutionStep {
  id: string;
  timestamp: string;
  type: ExecutionStepType;
  status: ExecutionStepStatus;
  title: string;
  content: string;
  duration_ms?: number;
  details?: ExecutionStepDetails;
}

export interface AgentTask {
  id: string;
  agent_id: string;
  prompt: string;
  status: AgentStatus;
  start_time: string;
  end_time?: string;
  result?: string;
  execution_log: ExecutionStep[];
}

export interface Agent {
  id: string;
  name: string;
  description: string;
  status: AgentStatus;
  created_at: string;
  updated_at: string;
  config: AgentConfiguration;
  tools: AgentTool[];
}