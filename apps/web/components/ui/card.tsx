import { HTMLAttributes } from "react";

import { cn } from "@/lib/utils";

export function Card({ className, ...props }: HTMLAttributes<HTMLDivElement>) {
  return (
    <div
      className={cn(
        "rounded-[28px] border border-line/80 bg-white/90 p-6 shadow-panel backdrop-blur",
        className,
      )}
      {...props}
    />
  );
}

