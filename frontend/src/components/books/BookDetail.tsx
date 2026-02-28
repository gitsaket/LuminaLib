"use client";

import { useState } from "react";
import { X, Star } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button, Input, StarRating, Spinner, Textarea } from "@/components/ui";
import { booksService } from "@/services/books.service";
import { toast } from "sonner";
import type { Book } from "@/types";

interface BookDetailProps {
  book: Book;
  isBorrowedByUser: boolean;
  onClose: () => void;
}

export function BookDetail({ book, isBorrowedByUser, onClose }: BookDetailProps) {
  const qc = useQueryClient();
  const [rating, setRating] = useState(5);
  const [body, setBody] = useState("");
  const [hovered, setHovered] = useState(0);

  const { data: analysis, isLoading: analysisLoading } = useQuery({
    queryKey: ["analysis", book.id],
    queryFn: () => booksService.getAnalysis(book.id),
  });

  const reviewMutation = useMutation({
    mutationFn: () => booksService.submitReview(book.id, rating, body),
    onSuccess: () => {
      toast.success("Review submitted!");
      setBody("");
      qc.invalidateQueries({ queryKey: ["books"] });
      qc.invalidateQueries({ queryKey: ["analysis", book.id] });
    },
    onError: (err: any) => toast.error(err.response?.data?.detail ?? "Failed to submit review"),
  });

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/40 p-4 backdrop-blur-sm" onClick={onClose}>
      <div
        className="bg-white card relative flex max-h-[90vh] w-full max-w-2xl flex-col overflow-hidden"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Header */}
        <div className="flex items-start justify-between gap-4 border-b border-gray-200 p-6">
          <div>
            <h2 className="text-xl font-bold text-gray-900">{book.title}</h2>
            <p className="text-sm text-gray-500">{book.author}</p>
            {book.published_year && (
              <p className="text-xs text-gray-400">{book.published_year}</p>
            )}
          </div>
          <button onClick={onClose} className="rounded-lg p-1 text-gray-400 hover:bg-gray-100 hover:text-gray-600">
            <X className="h-5 w-5" />
          </button>
        </div>

        <div className="flex-1 overflow-y-auto p-6 space-y-6">
          {/* Description */}
          {book.description && (
            <div>
              <h3 className="mb-2 text-sm font-semibold text-gray-700">Description</h3>
              <p className="text-sm text-gray-600">{book.description}</p>
            </div>
          )}

          {/* AI Analysis */}
          <div>
            <h3 className="mb-2 text-sm font-semibold text-gray-700">AI Analysis</h3>
            {analysisLoading ? (
              <Spinner className="h-5 w-5" />
            ) : (
              <div className="space-y-3 rounded-lg bg-indigo-50 p-4">
                {analysis?.ai_summary && (
                  <div>
                    <p className="text-xs font-medium text-indigo-700 mb-1">Summary</p>
                    <p className="text-sm text-gray-700">{analysis.ai_summary}</p>
                  </div>
                )}
                {analysis?.ai_review_consensus && (
                  <div>
                    <p className="text-xs font-medium text-indigo-700 mb-1">Reader Consensus</p>
                    <p className="text-sm text-gray-700">{analysis.ai_review_consensus}</p>
                  </div>
                )}
                {!analysis?.ai_summary && !analysis?.ai_review_consensus && (
                  <p className="text-sm text-gray-500 italic">AI analysis is being generated…</p>
                )}
                <div className="flex items-center gap-2">
                  <StarRating rating={analysis?.average_rating ?? 0} />
                  <span className="text-xs text-gray-500">
                    {(analysis?.average_rating ?? 0).toFixed(1)} avg ({analysis?.review_count ?? 0} reviews)
                  </span>
                </div>
              </div>
            )}
          </div>

          {/* Review Form */}
          {isBorrowedByUser && (
            <div>
              <h3 className="mb-3 text-sm font-semibold text-gray-700">Leave a Review</h3>
              <div className="space-y-3">
                {/* Star selector */}
                <div className="flex gap-1">
                  {[1, 2, 3, 4, 5].map((s) => (
                    <button
                      key={s}
                      onMouseEnter={() => setHovered(s)}
                      onMouseLeave={() => setHovered(0)}
                      onClick={() => setRating(s)}
                      className="p-0.5"
                    >
                      <Star
                        className={`h-6 w-6 transition-colors ${
                          s <= (hovered || rating) ? "fill-yellow-400 text-yellow-400" : "text-gray-300"
                        }`}
                      />
                    </button>
                  ))}
                </div>
                <Textarea
                  label="Your review"
                  placeholder="Share your thoughts about this book…"
                  rows={3}
                  value={body}
                  onChange={(e) => setBody(e.target.value)}
                />
                <Button
                  onClick={() => reviewMutation.mutate()}
                  isLoading={reviewMutation.isPending}
                  disabled={body.length < 10}
                  size="sm"
                >
                  Submit Review
                </Button>
              </div>
            </div>
          )}

          {!isBorrowedByUser && (
            <p className="rounded-lg bg-yellow-50 px-4 py-3 text-sm text-yellow-800 border border-yellow-200">
              Borrow this book to leave a review.
            </p>
          )}
        </div>
      </div>
    </div>
  );
}
