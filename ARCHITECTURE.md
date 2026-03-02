# LuminaLib – Architecture

## 1. DB Schema Design – User Preferences

### Design Decisions
The `user_preferences` table deliberately separates **explicit** user signals from **ML-derived** signals:

| Column | Type | Purpose |
| `favourite_genres` | `JSONB` | User-declared genre preferences |
| `disliked_genres` | `JSONB` | User-declared dislikes (penalised in scoring) |
| `genre_weights` | `JSONB` | ML-computed `{genre: float}` map, updated after each borrow |


## 2. Async LLM Generation Strategy

All LLM calls run in **FastAPI Background**, never in the FastAPI request cycle.

### Flow

```
POST /books  (multipart upload)
    1.FastAPI saves file to local/S3
    2. Creates Book row (summary_status = "pending")
    3. Returns 201 immediately a fast response
    4. Fires: generate_book_summary(book_id)

Background Tasks:
    1. Reads file bytes from MinIO
    2. Extracts text (pdfplumber for PDFs, decode for .txt)
    3. Calls LLMService.complete(system_prompt, excerpt)
    4. Saves ai_summary, sets summary_status = "completed"
```

```
POST /books/{id}/reviews
    1. FastAPI saves Review row
    2. Returns 201 immediately
    3. Fires: update_review(book_id)

Background Tasks:
    1. Loads all reviews for book
    2. Calls LLMService.complete(review_consensus_prompt)
    3. Updates ai_review_consensus, average_rating, review_count
```

### Provider Swapping

To switch from Ollama to OpenAI, change **one config line**:
```env
LLM_BACKEND=openai
OPENAI_API_KEY=sk-...
```
The `get_llm_service()` factory reads this at runtime. No code changes needed.

---

## 3. ML Recommendation Strategy

The engine implementation

### 1. Cold Start (< 2 borrows)
Returns top-rated available books the user hasn't read. Always produces results.

### 2. – Content-Based Filtering (default)
1. Derive `genre_weights: {genre: score}` from the user's borrow history (frequency-normalised).
2. Boost genres in `favourite_genres`, penalise `disliked_genres`.
3. Blend genre score with `average_rating * 0.1` to surface quality books.
4. Persist updated weights to `user_preferences.genre_weights` for next call.

This is an O(n\_books) operation — fast and interpretable.

---

## 4. Frontend Design Choices

### Framework: Next.js 14 (App Router)
- **SSR** for the library listing page ensures book data is visible to crawlers and loads without a client-side waterfall.
- **React Server Components** allow server-side data fetching while interactive components remain `"use client"`.

### State Management
- **React Query (TanStack Query)**: All server state lives in Query's cache. This provides automatic background refetching, stale-while-revalidate, and mutation invalidation with zero boilerplate.
- **AuthContext**: Lightweight React Context for user identity. Avoids Redux overhead for a simple auth flag + user object.
- No global state library (Redux, Zustand) needed — server state → React Query; UI state → local `useState`.

### Network Layer Abstraction
Components **never call `fetch`/`axios` directly**. The hierarchy is:
Component → Hook → Service → API Client

This means swapping the HTTP client, adding auth headers, or mocking in tests requires changes in exactly one file.

### Styling: Tailwind CSS
- Consistent design token system (spacing, colour, radius).

### Error Handling
- Axios response interceptor auto-redirects to `/login` on 401.
- React Query's `retry: 1` handles transient network failures silently.

