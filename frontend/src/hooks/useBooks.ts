import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { booksService, type CreateBookPayload } from "@/services/books.service";
import { toast } from "sonner";

export const BOOKS_KEY = "books";
export const RECOMMENDATIONS_KEY = "recommendations";

export function useBooks(page = 1, pageSize = 20) {
  return useQuery({
    queryKey: [BOOKS_KEY, page, pageSize],
    queryFn: () => booksService.list(page, pageSize),
  });
}

export function useBookAnalysis(bookId: number) {
  return useQuery({
    queryKey: [BOOKS_KEY, bookId, "analysis"],
    queryFn: () => booksService.getAnalysis(bookId),
    enabled: !!bookId,
  });
}

export function useRecommendations() {
  return useQuery({
    queryKey: [RECOMMENDATIONS_KEY],
    queryFn: booksService.getRecommendations,
  });
}

export function useCreateBook() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (payload: CreateBookPayload) => booksService.create(payload),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [BOOKS_KEY] });
      toast.success("Book uploaded successfully! AI summarization started.");
    },
    onError: () => toast.error("Failed to upload book."),
  });
}

export function useBorrowBook() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (bookId: number) => booksService.borrow(bookId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [BOOKS_KEY] });
      toast.success("Book borrowed!");
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Could not borrow book."),
  });
}

export function useReturnBook() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (bookId: number) => booksService.returnBook(bookId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [BOOKS_KEY] });
      toast.success("Book returned!");
    },
    onError: () => toast.error("Could not return book."),
  });
}

export function useSubmitReview() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: ({ bookId, rating, body }: { bookId: number; rating: number; body: string }) =>
      booksService.submitReview(bookId, rating, body),
    onSuccess: (_data, vars) => {
      qc.invalidateQueries({ queryKey: [BOOKS_KEY, vars.bookId, "analysis"] });
      toast.success("Review submitted! AI consensus update queued.");
    },
    onError: (err: any) =>
      toast.error(err?.response?.data?.detail ?? "Failed to submit review."),
  });
}

export function useDeleteBook() {
  const qc = useQueryClient();
  return useMutation({
    mutationFn: (bookId: number) => booksService.remove(bookId),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: [BOOKS_KEY] });
      toast.success("Book deleted.");
    },
    onError: () => toast.error("Failed to delete book."),
  });
}
