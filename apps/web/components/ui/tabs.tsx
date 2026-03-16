"use client";

import { ReactNode, useState } from "react";

import { cn } from "@/lib/utils";

interface TabItem {
  key: string;
  label: string;
  content: ReactNode;
}

export function Tabs({ items }: { items: TabItem[] }) {
  const [activeKey, setActiveKey] = useState(items[0]?.key);

  return (
    <div className="space-y-5">
      <div className="flex flex-wrap gap-2">
        {items.map((item) => (
          <button
            key={item.key}
            type="button"
            onClick={() => setActiveKey(item.key)}
            className={cn(
              "rounded-full px-4 py-2 text-sm font-semibold transition",
              activeKey === item.key
                ? "bg-ink text-white"
                : "border border-line bg-white/80 text-slate-600 hover:text-ink",
            )}
          >
            {item.label}
          </button>
        ))}
      </div>
      <div>
        {items.map((item) => (
          <div key={item.key} className={activeKey === item.key ? "block" : "hidden"}>
            {item.content}
          </div>
        ))}
      </div>
    </div>
  );
}

