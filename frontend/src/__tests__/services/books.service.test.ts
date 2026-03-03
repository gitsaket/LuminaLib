import { booksService } from "@/services/books.service";
import { apiClient } from "@/lib/api-client";

jest.mock("@/lib/api-client", () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
    put: jest.fn(),
    delete: jest.fn(),
  },
}));

const mockGet = apiClient.get as jest.Mock;
const mockPost = apiClient.post as jest.Mock;

const mockBorrow = {
  id: 1,
  user_id: 1,
  book_id: 42,
  status: "active",
  borrowed_date: "2024-01-01T00:00:00Z",
  return_date: null,
};

const mockPaginatedBooks = {
  items: [],
  total: 0,
  page: 1,
  page_size: 10,
};

const mockAnalysis = {
  book_id: 42,
  ai_summary: "A great book",
  ai_review_consensus: "Loved by all",
  average_rating: 4.5,
  review_count: 10,
};

beforeEach(() => {
  jest.clearAllMocks();
});

describe("booksService.list", () => {
  it("calls GET /books with pagination params and returns PaginatedBooks", async () => {
    mockGet.mockResolvedValueOnce({ data: mockPaginatedBooks });

    const result = await booksService.list(1, 10);

    expect(mockGet).toHaveBeenCalledWith("/books", {
      params: { page: 1, page_size: 10 },
    });
    expect(result).toEqual(mockPaginatedBooks);
  });
});

describe("booksService.borrow", () => {
  it("calls POST /books/42/borrow and returns Borrow", async () => {
    mockPost.mockResolvedValueOnce({ data: mockBorrow });

    const result = await booksService.borrow(42);

    expect(mockPost).toHaveBeenCalledWith("/books/42/borrow");
    expect(result).toEqual(mockBorrow);
  });
});

describe("booksService.returnBook", () => {
  it("calls POST /books/42/return and returns Borrow", async () => {
    const returned = { ...mockBorrow, status: "returned" };
    mockPost.mockResolvedValueOnce({ data: returned });

    const result = await booksService.returnBook(42);

    expect(mockPost).toHaveBeenCalledWith("/books/42/return");
    expect(result.status).toBe("returned");
  });
});

describe("booksService.submitReview", () => {
  it("calls POST /books/42/reviews with rating and body", async () => {
    const mockReview = {
      id: 1,
      book_id: 42,
      user_id: 1,
      rating: 4,
      body: "Great book!",
      sentiment_score: null,
      created_at: "2024-01-01T00:00:00Z",
    };
    mockPost.mockResolvedValueOnce({ data: mockReview });

    await booksService.submitReview(42, 4, "Great book!");

    expect(mockPost).toHaveBeenCalledWith("/books/42/reviews", {
      rating: 4,
      body: "Great book!",
    });
  });
});

describe("booksService.getAnalysis", () => {
  it("calls GET /books/42/analysis and returns BookAnalysis", async () => {
    mockGet.mockResolvedValueOnce({ data: mockAnalysis });

    const result = await booksService.getAnalysis(42);

    expect(mockGet).toHaveBeenCalledWith("/books/42/analysis");
    expect(result).toEqual(mockAnalysis);
  });
});
