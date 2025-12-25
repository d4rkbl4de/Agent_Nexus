export interface ListRequest {
  page?: number;
  page_size?: number;
  sort_by?: string;
  sort_order?: 'asc' | 'desc';
  
  filters?: Record<string, string | string[] | number | number[]>;
}

export interface PaginatedListResponse<T> {
  items: T[];
  total_items: number;
  page: number;
  page_size: number;
  total_pages: number;
}