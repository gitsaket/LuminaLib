"use client";

import { Sparkles } from "lucide-react";
import { useQuery } from "@tanstack/react-query";
import { Navbar } from "@/components/layout/Navbar";
import { BookCard } from "@/components/books/BookCard";
import { Spinner, Badge } from "@/components/ui";
import { booksService } from "@/services/books.service";

const STRATEGY_LABELS: Record<string, { label: string; variant: "green" | "blue" | "yellow" | "gray" }> = {
  content_based: { label: "Content-Based", variant: "green" },
  collaborative_filtering: { label: "Collaborative Filtering", variant: "blue" },
  cold_start_top_rated: { label: "Top Rated", variant: "yellow" },
  fallback_top_rated: { label: "Top Rated", variant: "yellow" },
  no_books_available: { label: "No Results", variant: "gray" },
};

export default function RecommendationsPage() {
  const { data, isLoading } = useQuery({
    queryKey: ["recommendations"],
    queryFn: () => booksService.getRecommendations(),
  });

  const strategyInfo = STRATEGY_LABELS[data?.strategy ?? ""] ?? { label: data?.strategy, variant: "gray" };

  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <div className="flex items-center gap-2">
              <Sparkles className="h-5 w-5 text-indigo-600" />
              <h1 className="text-2xl font-bold text-gray-900">Recommended For You</h1>
            </div>
            <p className="mt-1 text-sm text-gray-500">
              Personalized picks based on your reading history
            </p>
          </div>
          {data?.strategy && (
            <div className="flex items-center gap-2 text-sm text-gray-500">
              Strategy:
              <Badge variant={strategyInfo.variant as any}>{strategyInfo.label}</Badge>
            </div>
          )}
        </div>

        {isLoading ? (
          <div className="flex justify-center py-20">
            <Spinner className="h-10 w-10" />
          </div>
        ) : (data?.books?.length ?? 0) === 0 ? (
          <div className="flex flex-col items-center gap-3 py-20 text-gray-500">
            <Sparkles className="h-10 w-10 text-gray-300" />
            <p>No recommendations yet.</p>
            <p className="text-sm">Borrow a few books to get personalized suggestions!</p>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4">
            {data?.books.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </main>
    </>
  );
}
