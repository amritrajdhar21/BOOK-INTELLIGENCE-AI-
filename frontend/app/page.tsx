"use client";

import { useEffect, useMemo, useState } from "react";
import BookCard from "@/components/BookCard";
import LoadingSkeleton from "@/components/LoadingSkeleton";
import { Book, getBooks } from "@/lib/api";

export default function DashboardPage() {
  const [books, setBooks] = useState<Book[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState("");
  const [error, setError] = useState("");

  useEffect(() => {
    getBooks()
      .then(setBooks)
      .catch((err) => setError(err.message || "Failed to load books"))
      .finally(() => setLoading(false));
  }, []);

  const filteredBooks = useMemo(() => {
    return books.filter((book) => book.title.toLowerCase().includes(search.toLowerCase()));
  }, [books, search]);

  return (
    <main className="page-shell">
      <h1 className="text-4xl font-extrabold tracking-tight text-emerald-900 md:text-5xl">Book Intelligence Dashboard</h1>
      <p className="mx-auto mt-3 max-w-2xl text-emerald-700">
        Explore your library with AI-powered summaries, recommendations, and contextual Q&A.
      </p>
      <input
        type="text"
        placeholder="Search by title..."
        className="mx-auto mt-8 block w-full max-w-3xl rounded-xl border border-emerald-300 bg-white p-4 text-emerald-900 shadow-sm transition-all duration-300 outline-none focus:scale-[1.01] focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
        value={search}
        onChange={(e) => setSearch(e.target.value)}
      />
      {error && <p className="mt-4 text-red-600">{error}</p>}
      <section className="mt-8">
        {loading ? (
          <LoadingSkeleton />
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {filteredBooks.map((book) => (
              <BookCard key={book.id} book={book} />
            ))}
          </div>
        )}
      </section>
    </main>
  );
}
