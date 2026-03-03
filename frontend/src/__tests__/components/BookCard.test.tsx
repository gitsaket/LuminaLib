import React from "react";
import { render, screen, fireEvent, act } from "@testing-library/react";
import { BookCard } from "@/components/books/BookCard";
import type { Book } from "@/types";

const mockBook: Book = {
  id: 1,
  title: "The Great Gatsby",
  author: "F. Scott Fitzgerald",
  isbn: null,
  description: "A classic novel",
  genre: "Fiction",
  published_year: 1925,
  file_url: null,
  ai_summary: null,
  ai_review_consensus: null,
  summary_status: "pending",
  average_rating: 4.2,
  review_count: 15,
  status: "available",
  created_at: "2024-01-01T00:00:00Z",
};

describe("BookCard", () => {
  it("renders title, author, and genre badge", () => {
    render(<BookCard book={mockBook} />);
    expect(screen.getByText("The Great Gatsby")).toBeInTheDocument();
    expect(screen.getByText("F. Scott Fitzgerald")).toBeInTheDocument();
    expect(screen.getByText("Fiction")).toBeInTheDocument();
  });

  it("renders 'Available' status badge when status is available", () => {
    render(<BookCard book={mockBook} />);
    expect(screen.getByText("Available")).toBeInTheDocument();
  });

  it("renders 'Borrow' button when available and not borrowed by user", () => {
    const onBorrow = jest.fn().mockResolvedValue(undefined);
    render(
      <BookCard book={mockBook} onBorrow={onBorrow} isBorrowedByUser={false} />,
    );
    expect(screen.getByRole("button", { name: /borrow/i })).toBeInTheDocument();
    expect(
      screen.queryByRole("button", { name: /return/i }),
    ).not.toBeInTheDocument();
  });

  it("renders 'Return' button when isBorrowedByUser is true", () => {
    const onReturn = jest.fn().mockResolvedValue(undefined);
    render(
      <BookCard
        book={{ ...mockBook, status: "borrowed" }}
        onReturn={onReturn}
        isBorrowedByUser={true}
      />,
    );
    expect(screen.getByRole("button", { name: /return/i })).toBeInTheDocument();
  });

  it("calls onBorrow with book id when Borrow is clicked", async () => {
    const onBorrow = jest.fn().mockResolvedValue(undefined);
    render(
      <BookCard book={mockBook} onBorrow={onBorrow} isBorrowedByUser={false} />,
    );
    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /borrow/i }));
    });
    expect(onBorrow).toHaveBeenCalledWith(mockBook.id);
  });

  it("calls onViewDetails when Details is clicked", () => {
    const onViewDetails = jest.fn();
    render(<BookCard book={mockBook} onViewDetails={onViewDetails} />);
    fireEvent.click(screen.getByRole("button", { name: /details/i }));
    expect(onViewDetails).toHaveBeenCalledWith(mockBook);
  });
});
