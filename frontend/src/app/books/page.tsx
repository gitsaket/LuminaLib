"use client";

import { useState, useEffect } from "react";
import { Plus, Search } from "lucide-react";
import { useQuery, useMutation, useQueryClient } from "@tanstack/react-query";
import { Button, Spinner } from "@/components/ui";
import { BookCard } from "@/components/books/BookCard";
import { BookDetail } from "@/components/books/BookDetail";
import { UploadBookForm } from "@/components/books/UploadBookForm";
import { Navbar } from "@/components/layout/Navbar";
import { booksService } from "@/services/books.service";
import { useAuth } from "@/context/auth-context";
import { toast } from "sonner";
import type { Book } from "@/types";
import { handleError } from "@/utils/";

export default function BooksPage() {
  const qc = useQueryClient();
  const [page, setPage] = useState(1);
  const [search, setSearch] = useState("");
  const [selectedBook, setSelectedBook] = useState<Book | null>(null);
  const [showUpload, setShowUpload] = useState(false);
  const { user } = useAuth();

  const { data, isLoading } = useQuery({
    queryKey: ["books", page],
    queryFn: () => booksService.list(page, 12),
  });

  // Track which books the user has borrowed (optimistic)
  const [borrowedIds, setBorrowedIds] = useState<Set<number>>(new Set());

  const borrowMutation = useMutation({
    mutationFn: (id: number) => booksService.borrow(id),
    onSuccess: (_, id) => {
      setBorrowedIds((prev) => new Set([...prev, id]));
      toast.success("Book borrowed! Enjoy reading.");
      qc.invalidateQueries({ queryKey: ["books"] });
    },
    onError: (err: any) => toast.error(handleError(err, "Could not borrow")),
  });

  const returnMutation = useMutation({
    mutationFn: (id: number) => booksService.returnBook(id),
    onSuccess: (_, id) => {
      setBorrowedIds((prev) => {
        const s = new Set(prev);
        s.delete(id);
        return s;
      });
      toast.success("Book returned. Thanks!");
      qc.invalidateQueries({ queryKey: ["books"] });
    },
    onError: (err: any) => toast.error(handleError(err, "Could not return")),
  });

  const borrowedBookMutation = useMutation({
    mutationFn: () => booksService.getBorrowedBooks(user?.id ?? 0),
    onSuccess: (borrowedBooks) => {
      setBorrowedIds(new Set(borrowedBooks.map((b) => b.book_id)));
    },
    onError: (err: any) => toast.error(handleError(err, "Could not return")),
  });


  useEffect(() => {
    if (user) {
      borrowedBookMutation.mutate();
    }
  }, [user]);

  const filtered =
    data?.items.filter(
      (b) =>
        !search ||
        b.title.toLowerCase().includes(search.toLowerCase()) ||
        b.author.toLowerCase().includes(search.toLowerCase()),
    ) ?? [];

  return (
    <>
      <Navbar />
      <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6">
        {/* Header */}
        <div className="mb-8 flex flex-wrap items-center justify-between gap-4">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">Library</h1>
            <p className="text-sm text-gray-500">
              {data?.total ?? 0} books available
            </p>
          </div>
          <div className="flex gap-3">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-gray-400" />
              <input
                className="input pl-9 w-56"
                placeholder="Search books…"
                value={search}
                onChange={(e) => setSearch(e.target.value)}
              />
            </div>
            <Button onClick={() => setShowUpload(true)}>
              <Plus className="h-4 w-4" /> Add Book
            </Button>
          </div>
        </div>

        {/* Grid */}
        {isLoading ? (
          <div className="flex justify-center py-20">
            <Spinner className="h-10 w-10" />
          </div>
        ) : filtered.length === 0 ? (
          <div className="flex flex-col items-center gap-4 py-20 text-gray-500">
            <p>No books found.</p>
            <Button onClick={() => setShowUpload(true)}>
              <Plus className="h-4 w-4" /> Upload the first book
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-3">
            {filtered.map((book) => (
              <BookCard
                key={book.id}
                book={book}
                isBorrowedByUser={borrowedIds.has(book.id)}
                onBorrow={(id) => borrowMutation.mutateAsync(id)}
                onReturn={(id) => returnMutation.mutateAsync(id)}
                onViewDetails={setSelectedBook}
              />
            ))}
          </div>
        )}

        {/* Pagination */}
        {data && data.total > 12 && (
          <div className="mt-8 flex items-center justify-center gap-3">
            <Button
              variant="secondary"
              size="sm"
              disabled={page === 1}
              onClick={() => setPage((p) => p - 1)}
            >
              Previous
            </Button>
            <span className="text-sm text-gray-600">
              Page {page} of {Math.ceil(data.total / 12)}
            </span>
            <Button
              variant="secondary"
              size="sm"
              disabled={page * 12 >= data.total}
              onClick={() => setPage((p) => p + 1)}
            >
              Next
            </Button>
          </div>
        )}
      </main>

      {/* Modals */}
      {selectedBook && (
        <BookDetail
          book={selectedBook}
          isBorrowedByUser={borrowedIds.has(selectedBook.id)}
          onClose={() => setSelectedBook(null)}
        />
      )}
      {showUpload && <UploadBookForm onClose={() => setShowUpload(false)} />}
    </>
  );
}
