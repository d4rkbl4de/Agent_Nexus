export type InsightSeverity = 'info' | 'warning' | 'critical' | 'optimization';

export type TimePeriod = 'hour' | 'day' | 'week' | 'month';

export interface AgentInsight {
  id: string;
  agent_id: string;
  timestamp: string;
  severity: InsightSeverity;
  title: string;
  description: string;
  
  context_data: Record<string, any>; 
}

export interface TimeSeriesDataPoint {
  time_label: string;
  value: number; 
  secondary_value?: number;
}

export interface MetricData {
  metric_name: string;
  unit: string;
  current_value: number;
  trend_data: TimeSeriesDataPoint[]; 
  
  change_percent: number; 
}

export interface ResourceUsageSummary {
  period: TimePeriod;
  total_token_count: number;
  total_cost_usd: number;
  total_api_calls: number;
  
  token_usage_by_model: Record<string, number>; 
}

export interface PerformanceBenchmark {
  agent_id: string;
  task_type: string;
  average_latency_ms: number;
  p95_latency_ms: number;
  success_rate: number;
  
  tool_latency_breakdown: Record<string, number>; 
}