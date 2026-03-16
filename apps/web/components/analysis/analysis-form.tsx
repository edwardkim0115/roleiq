"use client";

import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { createAnalysis } from "@/lib/api";

export function AnalysisForm() {
  const router = useRouter();
  const [jobLabel, setJobLabel] = useState("");
  const [jobText, setJobText] = useState("");
  const [resumeFile, setResumeFile] = useState<File | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    if (!resumeFile) {
      setError("Choose a resume file before running the analysis.");
      return;
    }
    if (!jobText.trim()) {
      setError("Paste a job description before running the analysis.");
      return;
    }

    setIsSubmitting(true);
    setError(null);

    try {
      const formData = new FormData();
      formData.append("file", resumeFile);
      formData.append("job_text", jobText);
      if (jobLabel.trim()) {
        formData.append("job_label", jobLabel.trim());
      }

      const analysis = await createAnalysis(formData);
      router.push(`/analyses/${analysis.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "The analysis request failed.");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <form onSubmit={handleSubmit} className="grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
      <Card className="animate-rise space-y-6">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">Resume</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Upload one source resume</h2>
          <p className="mt-2 text-sm leading-6 text-slate-600">
            Supported formats: PDF, DOCX, and TXT. The backend keeps fragments traceable so every evidence snippet can
            point back to source text.
          </p>
        </div>

        <label className="flex min-h-56 cursor-pointer flex-col items-center justify-center rounded-[28px] border border-dashed border-line bg-sand/70 px-6 text-center transition hover:border-signal hover:bg-white">
          <input
            type="file"
            accept=".pdf,.docx,.txt"
            className="hidden"
            onChange={(event) => setResumeFile(event.target.files?.[0] ?? null)}
          />
          <span className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">Resume file</span>
          <span className="mt-3 text-lg font-semibold text-ink">
            {resumeFile ? resumeFile.name : "Drop a file here or click to browse"}
          </span>
          <span className="mt-2 max-w-xs text-sm text-slate-600">
            Keep it to the source resume you actually use. The suggestions stay grounded in what is already there.
          </span>
        </label>

        <div className="rounded-[24px] bg-slate-50 p-4 text-sm text-slate-600">
          <p className="font-semibold text-ink">What happens next</p>
          <ul className="mt-2 space-y-2 leading-6">
            <li>1. The resume is parsed into ordered fragments.</li>
            <li>2. The job post is broken into explicit requirement items.</li>
            <li>3. Matching combines exact, lexical, rule-based, and semantic signals.</li>
            <li>4. The app stores the result so you can reopen it later.</li>
          </ul>
        </div>
      </Card>

      <Card className="animate-rise animate-delay-1 space-y-5">
        <div>
          <p className="text-sm font-semibold uppercase tracking-[0.22em] text-slate-500">Job posting</p>
          <h2 className="mt-2 text-2xl font-semibold text-ink">Paste the target role</h2>
        </div>

        <div className="space-y-2">
          <label htmlFor="jobLabel" className="text-sm font-semibold text-slate-700">
            Optional label
          </label>
          <input
            id="jobLabel"
            value={jobLabel}
            onChange={(event) => setJobLabel(event.target.value)}
            placeholder="Senior Backend Engineer - Example Co"
            className="w-full rounded-2xl border border-line bg-white px-4 py-3 text-sm outline-none transition focus:border-signal"
          />
        </div>

        <div className="space-y-2">
          <label htmlFor="jobText" className="text-sm font-semibold text-slate-700">
            Job description
          </label>
          <textarea
            id="jobText"
            value={jobText}
            onChange={(event) => setJobText(event.target.value)}
            placeholder="Paste the job posting here..."
            className="min-h-[380px] w-full rounded-[24px] border border-line bg-white px-4 py-4 text-sm leading-6 outline-none transition focus:border-signal"
          />
        </div>

        {error ? <p className="rounded-2xl bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</p> : null}

        <div className="flex flex-wrap gap-3">
          <Button type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Running analysis..." : "Run analysis"}
          </Button>
          <Button type="button" variant="secondary" onClick={() => router.push("/analyses")}>
            Back to history
          </Button>
        </div>
      </Card>
    </form>
  );
}

