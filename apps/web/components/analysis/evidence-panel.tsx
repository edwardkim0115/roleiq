import { Card } from "@/components/ui/card";
import type { AnalysisDetail } from "@/lib/types";

export function EvidencePanel({ analysis }: { analysis: AnalysisDetail }) {
  const usageCount = new Map<string, number>();
  analysis.requirements.forEach((match) => {
    match.evidence_fragment_ids.forEach((id) => usageCount.set(id, (usageCount.get(id) ?? 0) + 1));
  });
  analysis.suggestions.forEach((suggestion) => {
    suggestion.supporting_fragment_ids.forEach((id) => usageCount.set(id, (usageCount.get(id) ?? 0) + 1));
  });

  return (
    <div className="grid gap-4">
      {analysis.fragments.map((fragment) => {
        const count = usageCount.get(fragment.id) ?? 0;
        return (
          <Card
            key={fragment.id}
            className={count > 0 ? "border-signal/50 bg-mist/50" : "bg-white/90"}
          >
            <div className="flex flex-wrap items-center justify-between gap-3">
              <div>
                <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">
                  {fragment.section_name}
                  {fragment.page_number ? ` • page ${fragment.page_number}` : ""}
                </p>
                <p className="mt-2 text-sm leading-6 text-slate-700">{fragment.text}</p>
              </div>
              <div className="rounded-full bg-white px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                {count > 0 ? `${count} references` : "Unused"}
              </div>
            </div>
          </Card>
        );
      })}
    </div>
  );
}

