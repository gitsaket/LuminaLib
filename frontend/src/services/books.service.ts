import type {
  Book,
  BookAnalysis,
  Borrow,
  PaginatedBooks,
  RecommendationResponse,
  Review,
} from "@/types";
import { apiClient } from "@/lib/api-client";

export interface CreateBookPayload {
  title: string;
  author: string;
  isbn?: string;
  description?: string;
  genre?: string;
  published_year?: number;
  file: File;
}

export const booksService = {
  async list(page = 1, pageSize = 20): Promise<PaginatedBooks> {
    const { data } = await apiClient.get<PaginatedBooks>("/books", {
      params: { page, page_size: pageSize },
    });
    return data;
  },

  async create(payload: CreateBookPayload): Promise<Book> {
    const form = new FormData();
    form.append("title", payload.title);
    form.append("author", payload.author);
    if (payload.isbn) form.append("isbn", payload.isbn);
    if (payload.description) form.append("description", payload.description);
    if (payload.genre) form.append("genre", payload.genre);
    if (payload.published_year)
      form.append("published_year", String(payload.published_year));
    form.append("file", payload.file);

    const { data } = await apiClient.post<Book>("/books", form, {
      headers: { "Content-Type": "multipart/form-data" },
    });
    return data;
  },

  async update(
    id: number,
    payload: Partial<Omit<Book, "id" | "created_at">>,
  ): Promise<Book> {
    const { data } = await apiClient.put<Book>(`/books/${id}`, payload);
    return data;
  },

  async remove(id: number): Promise<void> {
    await apiClient.delete(`/books/${id}`);
  },

  async getBorrowedBooks(userId: number): Promise<Borrow[]> {
    const { data } = await apiClient.get<Borrow[]>(`/books/${userId}/borrowed`);
    return data;
  },

  async borrow(id: number): Promise<Borrow> {
    const { data } = await apiClient.post<Borrow>(`/books/${id}/borrow`);
    return data;
  },

  async returnBook(id: number): Promise<Borrow> {
    const { data } = await apiClient.post<Borrow>(`/books/${id}/return`);
    return data;
  },

  async submitReview(
    id: number,
    rating: number,
    body: string,
  ): Promise<Review> {
    const { data } = await apiClient.post<Review>(`/books/${id}/reviews`, {
      rating,
      body,
    });
    return data;
  },

  async getAnalysis(id: number): Promise<BookAnalysis> {
    const { data } = await apiClient.get<BookAnalysis>(`/books/${id}/analysis`);
    return data;
  },

  async getRecommendations(): Promise<RecommendationResponse> {
    const { data } =
      await apiClient.get<RecommendationResponse>("/recommendations");
    return data;
  },
};
