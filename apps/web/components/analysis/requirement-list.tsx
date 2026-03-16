import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { AnalysisDetail } from "@/lib/types";
import { groupBy } from "@/lib/utils";

export function RequirementList({ analysis }: { analysis: AnalysisDetail }) {
  const grouped = groupBy(analysis.requirements, (item) => item.bucket);
  const fragmentLookup = new Map(analysis.fragments.map((fragment) => [fragment.id, fragment]));

  return (
    <div className="space-y-6">
      {Object.entries(grouped).map(([bucket, matches]) => (
        <Card key={bucket} className="space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Requirement bucket</p>
              <h3 className="mt-1 text-2xl font-semibold text-ink">{bucket.replaceAll("_", " ")}</h3>
            </div>
            <span className="text-sm text-slate-500">{matches.length} items</span>
          </div>

          <div className="space-y-4">
            {matches.map((match) => (
              <details
                key={match.id}
                className="rounded-[24px] border border-line/80 bg-slate-50/70 p-5 open:bg-white"
              >
                <summary className="cursor-pointer list-none">
                  <div className="flex flex-col gap-3 md:flex-row md:items-center md:justify-between">
                    <div className="space-y-2">
                      <div className="flex flex-wrap gap-2">
                        <Badge tone={match.match_strength}>{match.match_strength.replace("_", " ")}</Badge>
                        <Badge tone={match.importance}>{match.importance}</Badge>
                      </div>
                      <p className="text-base font-semibold text-ink">{match.requirement_text}</p>
                    </div>
                    <div className="text-right">
                      <p className="text-xs uppercase tracking-[0.2em] text-slate-500">Contribution</p>
                      <p className="text-2xl font-semibold text-ink">{match.score_contribution.toFixed(2)}</p>
                    </div>
                  </div>
                </summary>

                <div className="mt-5 grid gap-5 lg:grid-cols-[0.8fr_1.2fr]">
                  <div className="space-y-3">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Why it scored this way</p>
                      <p className="mt-2 text-sm leading-6 text-slate-700">{match.explanation}</p>
                    </div>
                    <div className="grid gap-3 md:grid-cols-2">
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Matched terms</p>
                        <p className="mt-2 text-sm text-slate-700">
                          {match.matched_terms.length > 0 ? match.matched_terms.join(", ") : "None"}
                        </p>
                      </div>
                      <div>
                        <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Missing terms</p>
                        <p className="mt-2 text-sm text-slate-700">
                          {match.missing_terms.length > 0 ? match.missing_terms.join(", ") : "None"}
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="space-y-3">
                    <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Evidence snippets</p>
                    {match.evidence_fragment_ids.length > 0 ? (
                      match.evidence_fragment_ids.map((fragmentId) => {
                        const fragment = fragmentLookup.get(fragmentId);
                        if (!fragment) return null;
                        return (
                          <div key={fragmentId} className="rounded-[20px] border border-line bg-white p-4">
                            <p className="text-xs uppercase tracking-[0.18em] text-slate-500">
                              {fragment.section_name}
                              {fragment.page_number ? ` • page ${fragment.page_number}` : ""}
                            </p>
                            <p className="mt-2 text-sm leading-6 text-slate-700">{fragment.text}</p>
                          </div>
                        );
                      })
                    ) : (
                      <div className="rounded-[20px] border border-dashed border-line bg-white p-4 text-sm text-slate-600">
                        No direct evidence was selected for this requirement.
                      </div>
                    )}
                  </div>
                </div>
              </details>
            ))}
          </div>
        </Card>
      ))}
    </div>
  );
}

