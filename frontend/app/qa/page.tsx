"use client";

import { Suspense } from "react";
import { useSearchParams } from "next/navigation";
import { useEffect, useMemo, useState } from "react";
import { askQuestion } from "@/lib/api";

type ChatItem = { question: string; answer: string; sources: string[]; createdAt: string };

function QAPageContent() {
  const searchParams = useSearchParams();
  const bookId = useMemo(() => searchParams.get("book_id") || undefined, [searchParams]);
  const [question, setQuestion] = useState("");
  const [loading, setLoading] = useState(false);
  const [answer, setAnswer] = useState("");
  const [sources, setSources] = useState<string[]>([]);
  const [history, setHistory] = useState<ChatItem[]>([]);
  const [error, setError] = useState("");

  useEffect(() => {
    const raw = window.localStorage.getItem("book-chat-history");
    if (raw) setHistory(JSON.parse(raw));
  }, []);

  const saveHistory = (nextHistory: ChatItem[]) => {
    setHistory(nextHistory);
    window.localStorage.setItem("book-chat-history", JSON.stringify(nextHistory));
  };

  const onSubmit = async () => {
    if (!question.trim()) return;
    setLoading(true);
    setError("");
    try {
      const res = await askQuestion(question, bookId);
      setAnswer(res.answer);
      setSources(res.sources);
      saveHistory([{ question, answer: res.answer, sources: res.sources, createdAt: new Date().toISOString() }, ...history]);
      setQuestion("");
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to ask question");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="page-shell">
      <h1 className="text-4xl font-extrabold text-emerald-900">Book Q&A</h1>
      {bookId && <p className="mt-2 text-sm font-medium text-emerald-600">Context book ID: {bookId}</p>}

      <textarea
        className="mx-auto mt-6 block h-40 w-full max-w-4xl rounded-2xl border border-emerald-300 bg-white p-4 text-emerald-900 shadow-sm transition-all duration-300 outline-none focus:scale-[1.01] focus:border-emerald-500 focus:ring-4 focus:ring-emerald-100"
        placeholder="Ask anything about this book or your whole library..."
        value={question}
        onChange={(e) => setQuestion(e.target.value)}
      />
      <button
        onClick={onSubmit}
        disabled={loading}
        className="mt-4 rounded-xl bg-emerald-500 px-6 py-3 font-semibold text-white transition-all duration-300 hover:-translate-y-0.5 hover:bg-emerald-600 hover:shadow-lg hover:shadow-emerald-200 disabled:cursor-not-allowed disabled:opacity-50"
      >
        {loading ? "Thinking..." : "Ask"}
      </button>
      {error && <p className="mt-3 text-red-600">{error}</p>}

      {answer && (
        <section className="glass-card mx-auto mt-8 max-w-4xl p-5 text-left">
          <h2 className="text-xl font-semibold text-emerald-900">Answer</h2>
          <p className="mt-2 whitespace-pre-wrap text-emerald-800">{answer}</p>
          <h3 className="mt-4 font-medium text-emerald-900">Sources</h3>
          <ul className="mt-2 list-inside list-disc text-emerald-700">
            {sources.map((source) => (
              <li key={source}>{source}</li>
            ))}
          </ul>
        </section>
      )}

      <section className="mx-auto mt-10 max-w-4xl text-left">
        <h2 className="text-xl font-semibold text-emerald-900">Chat History</h2>
        <div className="mt-4 space-y-3">
          {history.map((item) => (
            <div
              key={`${item.createdAt}-${item.question}`}
              className="glass-card p-4 transition-all duration-300 hover:-translate-y-0.5 hover:shadow-md hover:shadow-emerald-200"
            >
              <p className="text-sm font-medium text-emerald-700">Q: {item.question}</p>
              <p className="mt-1 text-sm text-emerald-900">A: {item.answer}</p>
            </div>
          ))}
        </div>
      </section>
    </main>
  );
}

export default function QAPage() {
  return (
    <Suspense fallback={<main className="page-shell">Loading...</main>}>
      <QAPageContent />
    </Suspense>
  );
}
