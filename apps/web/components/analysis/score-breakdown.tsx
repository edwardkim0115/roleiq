import { Badge } from "@/components/ui/badge";
import { Card } from "@/components/ui/card";
import type { AnalysisDetail } from "@/lib/types";
import { scoreTone } from "@/lib/utils";

export function ScoreBreakdown({ analysis }: { analysis: AnalysisDetail }) {
  return (
    <div className="space-y-6">
      <section className="grid gap-5 lg:grid-cols-[0.95fr_1.05fr]">
        <Card className="animate-rise bg-ink text-white">
          <p className="text-sm font-semibold uppercase tracking-[0.25em] text-slate-300">Overall fit score</p>
          <div className="mt-5 flex items-end justify-between">
            <div>
              <p className="text-6xl font-semibold">{analysis.overall_score}</p>
              <p className="mt-3 max-w-sm text-sm leading-6 text-slate-300">
                Transparent weighted score across applicable requirement buckets. This is not an ATS simulator.
              </p>
            </div>
            <div className="rounded-[24px] bg-white/10 px-4 py-3 text-right">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-300">Evidence-backed</p>
              <p className="mt-2 text-2xl font-semibold">{analysis.requirements.length}</p>
              <p className="text-xs text-slate-300">requirements evaluated</p>
            </div>
          </div>
        </Card>
        <Card className="animate-rise animate-delay-1 space-y-4">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">Top takeaways</p>
              <h2 className="mt-1 text-2xl font-semibold text-ink">What helped and what hurt</h2>
            </div>
            <Badge tone="required">Fit logic visible</Badge>
          </div>
          <div className="grid gap-4 md:grid-cols-2">
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Strengths</p>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
                {(analysis.summary.top_strengths ?? []).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
            <div>
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Gaps</p>
              <ul className="mt-3 space-y-2 text-sm leading-6 text-slate-700">
                {(analysis.summary.top_gaps ?? []).map((item) => (
                  <li key={item}>{item}</li>
                ))}
              </ul>
            </div>
          </div>
          {analysis.summary.tailored_summary ? (
            <div className="rounded-[24px] bg-slate-50 p-4">
              <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Tailored summary</p>
              <p className="mt-2 text-sm leading-6 text-slate-700">{analysis.summary.tailored_summary}</p>
            </div>
          ) : null}
        </Card>
      </section>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {analysis.subscores.map((bucket, index) => (
          <Card
            key={bucket.key}
            className={`animate-rise ${index === 1 ? "animate-delay-1" : index > 1 ? "animate-delay-2" : ""}`}
          >
            <p className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">{bucket.label}</p>
            {bucket.applicable ? (
              <>
                <div className="mt-3 flex items-baseline gap-2">
                  <p className={`text-3xl font-semibold ${scoreTone(bucket.normalized_score ?? 0)}`}>
                    {bucket.normalized_score}
                  </p>
                  <span className="text-sm text-slate-500">/ 100</span>
                </div>
                <p className="mt-1 text-sm text-slate-600">
                  {bucket.earned_points} of {bucket.possible_points} weighted points
                </p>
                <p className="mt-4 text-xs uppercase tracking-[0.18em] text-slate-500">
                  {bucket.matched_requirements} matched of {bucket.total_requirements}
                </p>
              </>
            ) : (
              <>
                <p className="mt-3 text-3xl font-semibold text-slate-400">N/A</p>
                <p className="mt-2 text-sm text-slate-600">This bucket was not explicitly requested in the posting.</p>
              </>
            )}
          </Card>
        ))}
      </section>
    </div>
  );
}

