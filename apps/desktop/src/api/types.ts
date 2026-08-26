/** Cross-domain shared API types (slice A of the frontend refactor plan). */

export interface ApiListResponse<T> {
  items: T[];
  total?: number;
}
