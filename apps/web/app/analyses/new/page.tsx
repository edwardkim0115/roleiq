import { AnalysisForm } from "@/components/analysis/analysis-form";

export default function NewAnalysisPage() {
  return (
    <div className="mx-auto w-full max-w-7xl px-6 pb-20 lg:px-10">
      <section className="mb-8 space-y-3">
        <p className="text-sm font-semibold uppercase tracking-[0.24em] text-slate-500">New analysis</p>
        <h1 className="text-4xl font-semibold tracking-tight text-ink sm:text-5xl">
          Upload the resume, paste the posting, and let the score explain itself.
        </h1>
        <p className="max-w-3xl text-base leading-7 text-slate-600">
          The product uses the model for structured extraction and optional summary help, but the score itself comes
          from explicit matching logic in the backend.
        </p>
      </section>
      <AnalysisForm />
    </div>
  );
}

