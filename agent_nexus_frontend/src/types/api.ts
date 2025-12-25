export enum HttpMethod {
  GET = 'GET',
  POST = 'POST',
  PUT = 'PUT',
  DELETE = 'DELETE',
  PATCH = 'PATCH',
}

export enum ApiResponseStatus {
  SUCCESS = 'success',
  ERROR = 'error',
  PENDING = 'pending',
}

export interface ApiRequest<T = unknown> {
  method: HttpMethod;
  url: string;
  data?: T;
  params?: Record<string, string | number | boolean>;
  headers?: Record<string, string>;
}

export interface ApiResponse<T = unknown> {
  status: ApiResponseStatus;
  data: T | null;
  message: string;
  timestamp: string;
  error?: {
    code: string;
    detail: string;
  } | null;
  metadata?: {
    page?: number;
    limit?: number;
    total?: number;
  } | null;
}

export interface PaginatedResponse<T> {
  items: T[];
  page: number;
  limit: number;
  total: number;
  total_pages: number;
}


export interface AgentListResponse extends PaginatedResponse<unknown> {} 

export interface TaskCreationRequest {
  agent_id: string;
  prompt: string;
  max_steps?: number;
}

export interface TaskStatusResponse {
  task_id: string;
  current_status: string;
  progress_percent: number;
}


export interface ApiErrorResponse {
  status: ApiResponseStatus.ERROR;
  data: null;
  message: string;
  timestamp: string;
  error: {
    code: string;
    detail: string;
    stack?: string;
  };
  metadata: null;
}