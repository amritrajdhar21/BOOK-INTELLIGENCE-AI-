export default function LoadingSkeleton() {
  return (
    <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
      {Array.from({ length: 6 }).map((_, i) => (
        <div key={i} className="animate-pulse rounded-2xl border border-emerald-200 bg-white p-4 shadow-sm shadow-emerald-100">
          <div className="h-64 rounded-xl bg-emerald-100" />
          <div className="mt-3 h-4 rounded bg-emerald-100" />
          <div className="mt-2 h-3 w-2/3 rounded bg-emerald-100" />
        </div>
      ))}
    </div>
  );
}
