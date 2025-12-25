import { ExecutionStep } from './agent.schema';

export type ChatAuthor = 'user' | 'agent' | 'system';

export type MessageStatus = 'sending' | 'received' | 'error' | 'final';

export interface ChatMessage {
  id: string;
  session_id: string;
  author: ChatAuthor;
  timestamp: string;
  content: string;
  status: MessageStatus;
  
  task_id?: string; 
  
  metadata?: {
    tool_calls?: ToolCall[];
    [key: string]: any;
  };
}

export interface ToolCall {
  id: string;
  tool_name: string;
  arguments: Record<string, any>;
  result?: string;
}

export interface ChatInput {
  session_id: string;
  prompt: string;
  agent_id: string;
  config_overrides?: Record<string, any>;
}

export interface ChatResponse {
  message: ChatMessage;
  task_id: string;
}

export interface ChatSession {
  id: string;
  agent_id: string;
  user_id: string;
  created_at: string;
  updated_at: string;
  title: string;
  summary: string;
  
  recent_messages: ChatMessage[]; 
}

export interface StreamingUpdate {
    type: 'message_update' | 'step_update' | 'error' | 'end';
    timestamp: string;
    
    message_chunk?: {
        message_id: string;
        content_delta: string;
        status?: MessageStatus;
    };
    
    execution_step?: ExecutionStep;
    
    error?: {
        code: string;
        message: string;
        task_id?: string;
    };
    
    task_id?: string;
}