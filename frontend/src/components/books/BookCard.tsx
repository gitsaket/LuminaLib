"use client";

import { useState } from "react";
import { BookOpen, Clock, Star } from "lucide-react";
import { Badge, Button, StarRating } from "@/components/ui";
import type { Book } from "@/types";

interface BookCardProps {
  book: Book;
  onBorrow?: (id: number) => Promise<void>;
  onReturn?: (id: number) => Promise<void>;
  onViewDetails?: (book: Book) => void;
  isBorrowedByUser?: boolean;
}

export function BookCard({
  book,
  onBorrow,
  onReturn,
  onViewDetails,
  isBorrowedByUser,
}: BookCardProps) {
  const [actionLoading, setActionLoading] = useState(false);

  console.log(isBorrowedByUser, book)

  const statusBadge: Record<string, "green" | "yellow"> = {
    available: "green",
    borrowed: "yellow",
  };

  const summaryBadge: Record<string, "blue" | "yellow" | "green" | "red"> = {
    pending: "yellow",
    processing: "blue",
    completed: "green",
    failed: "red",
  };

  const handleBorrow = async () => {
    if (!onBorrow) return;
    setActionLoading(true);
    try {
      await onBorrow(book.id);
    } finally {
      setActionLoading(false);
    }
  };

  const handleReturn = async () => {
    if (!onReturn) return;
    setActionLoading(true);
    try {
      await onReturn(book.id);
    } finally {
      setActionLoading(false);
    }
  };

  return (
    <div className="card flex flex-col gap-4 p-5 hover:shadow-md transition-shadow">
      {/* Header */}
      <div className="flex items-start justify-between gap-3">
        <div className="flex items-center gap-3 min-w-0">
          <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-lg bg-indigo-100 text-indigo-600">
            <BookOpen className="h-5 w-5" />
          </div>
          <div className="min-w-0">
            <h3 className="truncate font-semibold text-gray-900">
              {book.title}
            </h3>
            <p className="text-sm text-gray-500">{book.author}</p>
          </div>
        </div>
      </div>

      {/* Meta */}
      <div className="flex flex-wrap gap-2">
        {book.genre && <Badge variant="blue">{book.genre}</Badge>}
        <Badge variant={statusBadge[book.status] ?? "gray"}>
          {book.status === "available" ? "Available" : "Borrowed"}
        </Badge>
        {book.published_year && (
          <span className="flex items-center gap-1 text-xs text-gray-500">
            <Clock className="h-3 w-3" /> {book.published_year}
          </span>
        )}
      </div>

      {/* Rating */}
      <div className="flex items-center gap-2">
        <StarRating rating={book.average_rating} />
        <span className="text-xs text-gray-500">
          {book.average_rating.toFixed(1)} ({book.review_count} reviews)
        </span>
      </div>

      {/* AI Summary snippet */}
      {book.ai_summary && (
        <p className="line-clamp-5 text-xs text-gray-600 bg-gray-50 rounded-lg p-3">
          {book.ai_summary}
        </p>
      )}
      {book.summary_status !== "completed" && (
        <Badge
          variant={summaryBadge[book.summary_status] ?? "gray"}
          className="self-start"
        >
          AI summary: {book.summary_status}
        </Badge>
      )}

      {/* Actions */}
      <div className="mt-auto flex gap-2 pt-2">
        {onViewDetails && (
          <Button
            variant="secondary"
            size="sm"
            onClick={() => onViewDetails(book)}
          >
            Details
          </Button>
        )}
        {isBorrowedByUser && onReturn && (
          <Button
            variant="secondary"
            size="sm"
            onClick={handleReturn}
            isLoading={actionLoading}
          >
            Return
          </Button>
        )}
        {!isBorrowedByUser && book.status === "available" && onBorrow && (
          <Button size="sm" onClick={handleBorrow} isLoading={actionLoading}>
            Borrow
          </Button>
        )}
      </div>
    </div>
  );
}
