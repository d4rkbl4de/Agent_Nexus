export interface PaginatedResponse<T> {
  items: T[];
  total_items: number;
  page: number;
  page_size: number;
  total_pages: number;
}

export interface PaginationRequest {
  page?: number;
  page_size?: number;
}

export interface FilterRequest {
  search_query?: string;
  status?: string | string[];
  type?: string | string[];
  start_date?: string;
  end_date?: string;
}

export interface SortRequest {
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
}

export interface SuccessResponse {
  success: boolean;
  message: string;
  data?: Record<string, any>;
}

export interface ApiError {
  error_code: string;
  message: string;
  details?: Record<string, any>;
  timestamp: string;
}

export interface EntityReference {
  id: string;
  type: string;
  name?: string;
}