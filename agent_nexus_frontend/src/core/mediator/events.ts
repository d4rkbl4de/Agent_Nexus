import { AgentPulse } from '../../contracts/shared.schema';

export type EventType = 
  | 'AGENT_STATUS_UPDATE'
  | 'USER_LOGGED_IN'
  | 'INSIGHT_PROCESS_START'
  | 'THEME_CHANGED'
  | 'GLOBAL_LOGOUT';

export type EventPayloads = {
  AGENT_STATUS_UPDATE: AgentPulse;
  USER_LOGGED_IN: { userId: string; username: string };
  INSIGHT_PROCESS_START: { queryId: string; payload: any };
  THEME_CHANGED: 'light' | 'dark';
  GLOBAL_LOGOUT: void;
};

export type EventHandler<T extends EventType> = (payload: EventPayloads[T]) => void;