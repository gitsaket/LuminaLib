export interface User {
  id: number;
  email: string;
  username: string;
  full_name: string;
  bio: string | null;
  is_active: boolean;
}

export interface Book {
  id: number;
  title: string;
  author: string;
  isbn: string | null;
  description: string | null;
  genre: string | null;
  published_year: number | null;
  file_url: string | null;
  ai_summary: string | null;
  ai_review_consensus: string | null;
  summary_status: "pending" | "processing" | "completed" | "failed";
  average_rating: number;
  review_count: number;
  status: "available" | "borrowed";
  created_at: string;
}

export interface PaginatedBooks {
  items: Book[];
  total: number;
  page: number;
  page_size: number;
}

export interface Borrow {
  id: number;
  user_id: number;
  book_id: number;
  status: "active" | "returned";
  borrowed_date: string;
  return_date: string | null;
}

export interface Review {
  id: number;
  book_id: number;
  user_id: number;
  rating: number;
  body: string;
  sentiment_score: number | null;
  created_at: string;
}

export interface BookAnalysis {
  book_id: number;
  ai_summary: string | null;
  ai_review_consensus: string | null;
  average_rating: number;
  review_count: number;
}

export interface RecommendationResponse {
  books: Book[];
  strategy: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

export interface ApiError {
  detail: string;
}
