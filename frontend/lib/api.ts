export const API_BASE_URL = "http://localhost:8000";

export type Book = {
  id: number;
  title: string;
  author: string;
  rating: number;
  description?: string;
  genre: string;
  summary?: string;
  book_url?: string;
  cover_image_url: string;
};

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...(options?.headers ?? {}),
    },
    cache: "no-store",
  });

  if (!response.ok) {
    const errorBody = await response.text();
    throw new Error(errorBody || `HTTP ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export const getBooks = () => request<Book[]>("/api/books/");
export const getBook = (id: string | number) => request<Book>(`/api/books/${id}/`);
export const getRecommendations = (id: string | number) => request<Book[]>(`/api/books/${id}/recommendations/`);
export const askQuestion = (question: string, book_id?: string | number) =>
  request<{ answer: string; sources: string[] }>("/api/books/ask/", {
    method: "POST",
    body: JSON.stringify({ question, book_id }),
  });
