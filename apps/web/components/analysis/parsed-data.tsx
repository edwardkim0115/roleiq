import { Card } from "@/components/ui/card";
import type { AnalysisDetail } from "@/lib/types";

export function ParsedData({ analysis }: { analysis: AnalysisDetail }) {
  return (
    <div className="grid gap-4 xl:grid-cols-2">
      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Parsed resume JSON</p>
        <pre className="mt-4 max-h-[720px] overflow-auto rounded-[20px] bg-slate-950 p-4 text-xs text-slate-100">
          {JSON.stringify(analysis.parsed_resume, null, 2)}
        </pre>
      </Card>
      <Card>
        <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-500">Parsed job JSON</p>
        <pre className="mt-4 max-h-[720px] overflow-auto rounded-[20px] bg-slate-950 p-4 text-xs text-slate-100">
          {JSON.stringify(analysis.job_posting, null, 2)}
        </pre>
      </Card>
    </div>
  );
}

