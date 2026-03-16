import type { Metadata } from "next";
import Link from "next/link";

import "./globals.css";

export const metadata: Metadata = {
  title: "RoleIQ",
  description: "Transparent resume-to-job match analysis",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <div className="min-h-screen">
          <header className="mx-auto flex w-full max-w-7xl items-center justify-between px-6 py-6 lg:px-10">
            <Link href="/analyses" className="flex items-center gap-3">
              <span className="rounded-full border border-line bg-white/80 px-3 py-1 text-xs font-bold uppercase tracking-[0.28em] text-slate-600">
                RoleIQ
              </span>
              <span className="hidden text-sm text-slate-600 md:block">
                Evidence-backed resume match analyzer
              </span>
            </Link>
            <nav className="flex items-center gap-3 text-sm font-semibold text-slate-700">
              <Link href="/analyses" className="rounded-full px-3 py-2 hover:bg-white/70">
                History
              </Link>
              <Link href="/analyses/new" className="rounded-full bg-ink px-4 py-2 text-white">
                New analysis
              </Link>
            </nav>
          </header>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
