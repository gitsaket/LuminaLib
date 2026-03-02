# LuminaLib Frontend

Next.js frontend for LuminaLib library management system.

## Tech Stack

- Next.js 16.1.6
- React 18.3.1
- TypeScript 5.5.3
- Tailwind CSS 4.2.1

## Setup

### Using Docker

Docker setup is in the main README. It will build and run the frontend along with the backend and other services.

### Local Development

1. #Install Dependencies:
   ```bash
   cd frontend
   npm install
   ```

2. #Configure Environment:
   ```bash
   # Set API URL (optional, both are set defaults to http://localhost:8000)
   INTERNAL_API_URL=http://localhost:8000 # for server-side API calls
   NEXT_PUBLIC_API_URL=http://localhost:8000 # for client-side API calls in browser
   ```

3. #Start Development Server:
   ```bash
   npm run dev
   ```
Application URL, after development server runs with above command `http://localhost:3000`

## Available Scripts

```bash
npm run dev # start development server with hot reload
npm run build # create production build
npm run start # start production server
npm run lint # check for linting errors
```

## Project Structure

## Project Structure

- `frontend/`
  - `Dockerfile`
  - `package.json`
  - `next.config.js`
  - `tailwind.config.js`
  - `src/`
    - `app/` — Next.js App Router pages
      - `layout.tsx` — Root layout with providers
      - `page.tsx` — Redirect home
      - `login/`
      - `signup/`
      - `books/` — Main library page
      - `recommendations/`
    - `components/`
      - `ui/` — Atomic primitives
      - `books/` — BookCard, BookDetail, UploadForm
      - `layout/` — Navbar
    - `context/` — AuthContext, QueryProvider
    - `hooks/` — useBooks, useBorrow
    - `services/` — authService, booksService
    - `lib/`
      - `api-client.ts` — Axios instance + interceptors
    - `types/` — Shared TypeScript interfaces

# API Calls
- `src/lib/api.client.ts` - API client with functions for authentication, book management, and library management. Uses axios with error handling.
Tokens are stored in localStorage and included in Authorization headers for authenticated requests from api.client.ts by interceptors setup in api.ts
## Code Quality

```bash
npm run lint     # Check for linting errors
```

