import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

const toneMap: Record<string, string> = {
  strong_match: "bg-teal-100 text-teal-700",
  moderate_match: "bg-amber-100 text-amber-700",
  weak_match: "bg-orange-100 text-orange-700",
  missing: "bg-rose-100 text-rose-700",
  required: "bg-slate-900 text-white",
  preferred: "bg-slate-200 text-slate-700",
};

interface BadgeProps extends HTMLAttributes<HTMLSpanElement> {
  tone?: string;
}

export function Badge({ className, tone, ...props }: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center rounded-full px-2.5 py-1 text-xs font-semibold uppercase tracking-[0.16em]",
        tone ? toneMap[tone] ?? "bg-slate-100 text-slate-700" : "bg-slate-100 text-slate-700",
        className,
      )}
      {...props}
    />
  );
}

