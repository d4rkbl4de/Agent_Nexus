import { LogLevel } from '../utils/logger';

export enum ThemeMode {
  LIGHT = 'light',
  DARK = 'dark',
  SYSTEM = 'system',
}

export interface FeatureFlags {
  is_agent_creation_enabled: boolean;
  is_graph_visualization_enabled: boolean;
  is_telemetry_dashboard_enabled: boolean;
}

export interface UserSession {
  id: string;
  username: string;
  email: string;
  roles: string[];
  last_login: Date;
}

export interface SystemConfiguration {
  app_version: string;
  api_base_url: string;
  environment: 'development' | 'staging' | 'production';
  log_level: LogLevel;
  max_concurrent_tasks: number;
}

export interface FrontendTelemetry {
  timestamp: Date;
  active_route: string;
  render_fps: number;
  memory_heap_used_mb: number;
  network_latency_ms: number;
}

export interface GlobalState {
  theme: ThemeMode;
  is_sidebar_collapsed: boolean;
  notifications_count: number;
  user: UserSession | null;
  flags: FeatureFlags;
  config: SystemConfiguration;
}