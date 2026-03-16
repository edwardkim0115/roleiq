import Link from "next/link";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { AnalysisListItem } from "@/lib/types";
import { formatDate, scoreTone } from "@/lib/utils";

export function AnalysisHistory({
  analyses,
  query,
}: {
  analyses: AnalysisListItem[];
  query?: string;
}) {
  return (
    <div className="space-y-6">
      <section className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
        <div className="animate-rise space-y-5 rounded-[36px] border border-line/70 bg-white/70 p-8 shadow-panel backdrop-blur">
          <span className="inline-flex rounded-full bg-mist px-3 py-1 text-xs font-semibold uppercase tracking-[0.25em] text-signal">
            Transparent scoring
          </span>
          <div className="space-y-3">
            <h1 className="max-w-3xl text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
              Match one resume against one job posting and inspect every scoring decision.
            </h1>
            <p className="max-w-2xl text-base leading-7 text-slate-600">
              RoleIQ keeps the logic visible. Every analysis stores parsed inputs, requirement-level matches,
              evidence snippets, and grounded suggestions so you can revisit the result later without guessing how it
              was produced.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link href="/analyses/new">
              <Button>Create analysis</Button>
            </Link>
            <a href="#history">
              <Button variant="secondary">Browse saved runs</Button>
            </a>
          </div>
        </div>
        <Card className="animate-rise animate-delay-1 grid-faint space-y-4 bg-ink text-white">
          <div>
            <p className="text-sm uppercase tracking-[0.22em] text-slate-300">What you can inspect</p>
            <h2 className="mt-2 text-2xl font-semibold">No black-box score</h2>
          </div>
          <ul className="space-y-3 text-sm leading-6 text-slate-200">
            <li>Overall fit score plus visible weighted subscores</li>
            <li>Requirement-by-requirement evidence mapping</li>
            <li>Missing items called out as real gaps, not hand-waved away</li>
            <li>Parsed resume and job JSON available for debugging</li>
          </ul>
        </Card>
      </section>

      <section id="history" className="space-y-4">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">Saved analyses</p>
            <h2 className="text-2xl font-semibold text-ink">History</h2>
          </div>
          <form className="flex gap-3" action="/analyses">
            <input
              type="search"
              name="q"
              defaultValue={query}
              placeholder="Search title, company, or file"
              className="w-full min-w-[240px] rounded-full border border-line bg-white/85 px-4 py-2 text-sm text-ink outline-none ring-0 transition focus:border-signal"
            />
            <Button variant="secondary" type="submit">
              Filter
            </Button>
          </form>
        </div>

        {analyses.length === 0 ? (
          <Card className="text-center">
            <p className="text-lg font-semibold text-ink">No analyses yet</p>
            <p className="mt-2 text-sm text-slate-600">
              Start with a resume upload and pasted job description. The first result will show up here.
            </p>
          </Card>
        ) : (
          <div className="grid gap-4">
            {analyses.map((analysis, index) => (
              <Link key={analysis.id} href={`/analyses/${analysis.id}`}>
                <Card
                  className={`animate-rise grid gap-4 transition hover:-translate-y-0.5 hover:border-signal/60 hover:shadow-xl md:grid-cols-[0.9fr_0.55fr_0.55fr] ${index % 2 === 1 ? "animate-delay-1" : ""}`}
                >
                  <div className="space-y-3">
                    <div className="flex flex-wrap items-center gap-3">
                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">
                        {analysis.company || "Company not extracted"}
                      </span>
                      <span className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-400">
                        {formatDate(analysis.created_at)}
                      </span>
                    </div>
                    <div>
                      <h3 className="text-2xl font-semibold text-ink">{analysis.title}</h3>
                      <p className="mt-1 text-sm text-slate-600">Resume: {analysis.filename}</p>
                    </div>
                  </div>
                  <div>
                    <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Top strengths</p>
                    <ul className="mt-3 space-y-2 text-sm text-slate-700">
                      {analysis.top_strengths.length > 0 ? (
                        analysis.top_strengths.map((strength) => <li key={strength}>{strength}</li>)
                      ) : (
                        <li>No strong signals captured.</li>
                      )}
                    </ul>
                  </div>
                  <div className="flex flex-col justify-between gap-4">
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Fit score</p>
                      <p className={`mt-2 text-4xl font-semibold ${scoreTone(analysis.overall_score)}`}>
                        {analysis.overall_score}
                      </p>
                    </div>
                    <div>
                      <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Top gaps</p>
                      <ul className="mt-3 space-y-2 text-sm text-slate-700">
                        {analysis.top_gaps.length > 0 ? (
                          analysis.top_gaps.map((gap) => <li key={gap}>{gap}</li>)
                        ) : (
                          <li>No major gaps highlighted.</li>
                        )}
                      </ul>
                    </div>
                  </div>
                </Card>
              </Link>
            ))}
          </div>
        )}
      </section>
    </div>
  );
}
