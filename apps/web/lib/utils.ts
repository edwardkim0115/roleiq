import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function formatDate(value: string) {
  return new Intl.DateTimeFormat("en-US", {
    year: "numeric",
    month: "short",
    day: "numeric",
  }).format(new Date(value));
}

export function scoreTone(value: number) {
  if (value >= 80) return "text-teal-700";
  if (value >= 60) return "text-amber-700";
  return "text-rose-700";
}

export function groupBy<T>(items: T[], getter: (item: T) => string) {
  return items.reduce<Record<string, T[]>>((acc, item) => {
    const key = getter(item);
    acc[key] = acc[key] || [];
    acc[key].push(item);
    return acc;
  }, {});
}

