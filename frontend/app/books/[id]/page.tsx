"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import BookCard from "@/components/BookCard";
import { Book, getBook, getRecommendations } from "@/lib/api";

export default function BookDetailPage({ params }: { params: { id: string } }) {
  const [book, setBook] = useState<Book | null>(null);
  const [recommendations, setRecommendations] = useState<Book[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    getBook(params.id)
      .then(setBook)
      .catch((err) => setError(err.message || "Failed to load book"));

    getRecommendations(params.id)
      .then(setRecommendations)
      .catch(() => setRecommendations([]));
  }, [params.id]);

  if (error) return <main className="page-shell text-red-600">{error}</main>;
  if (!book) return <main className="page-shell">Loading...</main>;

  return (
    <main className="page-shell">
      <div className="mx-auto grid max-w-6xl grid-cols-1 gap-8 text-left md:grid-cols-[320px_1fr]">
        <div className="glass-card relative h-[460px] overflow-hidden">
          <Image
            src={book.cover_image_url || "/placeholder-book.svg"}
            alt={book.title}
            fill
            className="object-cover transition-transform duration-500 hover:scale-105"
          />
        </div>
        <div>
          <h1 className="text-4xl font-extrabold text-emerald-900">{book.title}</h1>
          <p className="mt-2 text-emerald-700">{book.author}</p>
          <p className="mt-2 font-medium text-emerald-500">Rating: {book.rating}</p>
          <span className="mt-3 inline-block rounded-full bg-emerald-100 px-3 py-1 text-sm font-medium text-emerald-700">
            {book.genre || "unknown"}
          </span>
          <p className="mt-4 leading-7 text-emerald-900">{book.description}</p>

          <section className="glass-card mt-8 p-5">
            <h2 className="text-xl font-semibold text-emerald-900">AI Summary</h2>
            <p className="mt-2 text-emerald-800">{book.summary || "No summary available yet."}</p>
          </section>

          <Link
            href={`/qa?book_id=${book.id}`}
            className="mt-6 inline-block rounded-xl bg-emerald-500 px-5 py-3 font-semibold text-white transition-all duration-300 hover:-translate-y-0.5 hover:bg-emerald-600 hover:shadow-lg hover:shadow-emerald-200"
          >
            Ask about this book
          </Link>
        </div>
      </div>

      <section className="mx-auto mt-12 max-w-6xl">
        <h2 className="mb-4 text-center text-2xl font-bold text-emerald-900">Recommendations</h2>
        <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {recommendations.map((rec) => (
            <BookCard key={rec.id} book={rec} />
          ))}
        </div>
      </section>
    </main>
  );
}
