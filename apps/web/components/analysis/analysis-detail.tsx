"use client";

import Link from "next/link";

import { EvidencePanel } from "@/components/analysis/evidence-panel";
import { ParsedData } from "@/components/analysis/parsed-data";
import { RequirementList } from "@/components/analysis/requirement-list";
import { ScoreBreakdown } from "@/components/analysis/score-breakdown";
import { SuggestionsPanel } from "@/components/analysis/suggestions-panel";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";
import type { AnalysisDetail as AnalysisDetailType } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export function AnalysisDetail({ analysis }: { analysis: AnalysisDetailType }) {
  return (
    <div className="space-y-8">
      <section className="animate-rise flex flex-col gap-5 rounded-[36px] border border-line/70 bg-white/75 p-8 shadow-panel backdrop-blur lg:flex-row lg:items-end lg:justify-between">
        <div className="space-y-3">
          <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">
            Analysis saved {formatDate(analysis.created_at)}
          </p>
          <div>
            <h1 className="text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
              {analysis.job_posting.title || "Untitled job analysis"}
            </h1>
            <p className="mt-2 text-base text-slate-600">
              Resume: {analysis.resume_document.filename}
              {analysis.job_posting.company ? ` • ${analysis.job_posting.company}` : ""}
            </p>
          </div>
        </div>
        <div className="flex flex-wrap gap-3">
          <Link href="/analyses">
            <Button variant="secondary">Back to history</Button>
          </Link>
          <Link href="/analyses/new">
            <Button>Run another analysis</Button>
          </Link>
        </div>
      </section>

      <Tabs
        items={[
          { key: "overview", label: "Overview", content: <ScoreBreakdown analysis={analysis} /> },
          { key: "requirements", label: "Requirement Mapping", content: <RequirementList analysis={analysis} /> },
          { key: "evidence", label: "Resume Evidence", content: <EvidencePanel analysis={analysis} /> },
          { key: "suggestions", label: "Suggestions", content: <SuggestionsPanel analysis={analysis} /> },
          { key: "parsed", label: "Parsed Data", content: <ParsedData analysis={analysis} /> },
        ]}
      />
    </div>
  );
}

