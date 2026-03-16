import { ButtonHTMLAttributes } from "react";

import { cn } from "@/lib/utils";

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary" | "ghost";
}

export function Button({ className, variant = "primary", ...props }: ButtonProps) {
  return (
    <button
      className={cn(
        "inline-flex items-center justify-center rounded-full px-4 py-2 text-sm font-semibold transition duration-200",
        variant === "primary" &&
          "bg-ink text-white shadow-panel hover:bg-slate-800 disabled:bg-slate-400",
        variant === "secondary" &&
          "border border-line bg-white text-ink hover:border-signal hover:text-signal",
        variant === "ghost" && "text-slate-600 hover:bg-white/70 hover:text-ink",
        className,
      )}
      {...props}
    />
  );
}

