import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { AnalysisDetail } from "@/lib/types";

export function SuggestionsPanel({ analysis }: { analysis: AnalysisDetail }) {
  return (
    <div className="space-y-4">
      {analysis.summary.tailored_summary ? (
        <Card className="bg-ink text-white">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-300">Tailored summary</p>
          <p className="mt-3 text-base leading-7 text-slate-100">{analysis.summary.tailored_summary}</p>
        </Card>
      ) : null}

      {analysis.suggestions.length > 0 ? (
        analysis.suggestions.map((suggestion) => (
          <Card key={suggestion.id}>
            <div className="flex flex-wrap items-start justify-between gap-3">
              <div>
                <div className="flex flex-wrap gap-2">
                  <Badge tone={suggestion.grounded ? "strong_match" : "missing"}>
                    {suggestion.grounded ? "Supported by resume" : "Real gap"}
                  </Badge>
                  <Badge>{suggestion.suggestion_type}</Badge>
                </div>
                <h3 className="mt-3 text-xl font-semibold text-ink">{suggestion.title}</h3>
              </div>
            </div>
            <p className="mt-3 text-sm leading-7 text-slate-700">{suggestion.body}</p>
            {suggestion.supporting_fragment_ids.length > 0 ? (
              <p className="mt-4 text-xs uppercase tracking-[0.18em] text-slate-500">
                Supporting fragments: {suggestion.supporting_fragment_ids.join(", ")}
              </p>
            ) : (
              <p className="mt-4 text-xs uppercase tracking-[0.18em] text-slate-500">
                No supporting evidence is currently present in the resume.
              </p>
            )}
          </Card>
        ))
      ) : (
        <Card>
          <p className="text-sm text-slate-600">No suggestions were generated for this analysis.</p>
        </Card>
      )}
    </div>
  );
}

