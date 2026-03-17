"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useState } from "react";

import { EvidencePanel } from "@/components/analysis/evidence-panel";
import { ParsedData } from "@/components/analysis/parsed-data";
import { RequirementList } from "@/components/analysis/requirement-list";
import { ScoreBreakdown } from "@/components/analysis/score-breakdown";
import { SuggestionsPanel } from "@/components/analysis/suggestions-panel";
import { Button } from "@/components/ui/button";
import { Tabs } from "@/components/ui/tabs";
import { deleteAnalysis } from "@/lib/api";
import type { AnalysisDetail as AnalysisDetailType } from "@/lib/types";
import { formatDate } from "@/lib/utils";

export function AnalysisDetail({ analysis }: { analysis: AnalysisDetailType }) {
  const router = useRouter();
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteError, setDeleteError] = useState<string | null>(null);

  async function handleDelete() {
    const confirmed = window.confirm(
      "Delete this saved analysis? This removes the stored resume/job pairing from local history.",
    );
    if (!confirmed) {
      return;
    }

    setIsDeleting(true);
    setDeleteError(null);
    try {
      await deleteAnalysis(analysis.id);
      router.push("/analyses");
      router.refresh();
    } catch (error) {
      setDeleteError(error instanceof Error ? error.message : "Failed to delete analysis.");
      setIsDeleting(false);
    }
  }

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
              {analysis.job_posting.company ? ` | ${analysis.job_posting.company}` : ""}
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
          <Button
            type="button"
            variant="secondary"
            className="border-rose-200 text-rose-700 hover:border-rose-400 hover:text-rose-800"
            disabled={isDeleting}
            onClick={handleDelete}
          >
            {isDeleting ? "Deleting..." : "Delete analysis"}
          </Button>
        </div>
      </section>

      {deleteError ? (
        <div className="rounded-[24px] border border-rose-200 bg-rose-50 px-5 py-4 text-sm text-rose-700">
          {deleteError}
        </div>
      ) : null}

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
