import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Book Intelligence",
  description: "Document intelligence platform for books",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="animated-gradient min-h-screen bg-white text-emerald-950">{children}</body>
    </html>
  );
}
