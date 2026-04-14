import Image from "next/image";
import Link from "next/link";
import { Book } from "@/lib/api";

type Props = { book: Book };

const stars = (rating: number) => "★".repeat(Math.round(rating)) + "☆".repeat(5 - Math.round(rating));

export default function BookCard({ book }: Props) {
  return (
    <Link
      href={`/books/${book.id}`}
      className="glass-card group p-5 text-left transition-all duration-300 hover:-translate-y-1 hover:scale-[1.02] hover:shadow-2xl hover:shadow-emerald-200"
    >
      <div className="relative h-64 w-full overflow-hidden rounded-xl bg-emerald-50">
        <Image
          src={book.cover_image_url || "/placeholder-book.svg"}
          alt={book.title}
          fill
          className="object-cover transition-transform duration-500 group-hover:scale-110"
        />
      </div>
      <h3 className="mt-4 line-clamp-1 text-lg font-bold text-emerald-900">{book.title}</h3>
      <p className="text-sm text-emerald-700">{book.author}</p>
      <p className="text-sm text-emerald-500">{stars(book.rating || 0)}</p>
      <span className="mt-2 inline-block rounded-full bg-emerald-100 px-3 py-1 text-xs font-medium text-emerald-700">
        {book.genre || "unknown"}
      </span>
      <p className="mt-2 text-sm text-emerald-800">
        {book.description
          ? `${book.description.slice(0, 100)}${book.description.length > 100 ? "..." : ""}`
          : "Description available on detail page"}
      </p>
    </Link>
  );
}
