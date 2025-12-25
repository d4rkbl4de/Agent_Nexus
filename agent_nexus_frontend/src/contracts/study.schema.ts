import { AgentConfiguration, AgentStatus } from './agent.schema';

export type StudyStatus = 'draft' | 'scheduled' | 'running' | 'completed' | 'canceled';

export type StudyDesign = 'a_b' | 'multi_variant' | 'optimization_sweep';

export interface StudyVariant {
  id: string;
  name: string;
  description: string;
  
  config_overrides: Partial<AgentConfiguration>;
  
  traffic_split: number; 
}

export interface StudyTestPrompt {
  id: string;
  content: string;
  expected_outcome?: string;
  
  tags: string[]; 
}

export interface VariantResult {
  variant_id: string;
  prompt_id: string;
  
  metrics: {
    latency_ms_avg: number;
    token_usage_total: number;
    success_rate: number;
    cost_usd: number;
  };
  
  agent_response: string; 
  
  human_evaluation_score?: number; 
}

export interface AgentStudy {
  id: string;
  name: string;
  description: string;
  base_agent_id: string;
  
  status: StudyStatus;
  design: StudyDesign;
  
  created_at: string;
  start_time?: string;
  end_time?: string;

  variants: StudyVariant[];
  
  test_prompts: StudyTestPrompt[];
  
  summary_metrics?: {
    winning_variant_id?: string;
    metrics_comparison: Record<string, { a_value: number; b_value: number; p_value: number }>;
  };
}