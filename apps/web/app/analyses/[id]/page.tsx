import { notFound } from "next/navigation";

import { AnalysisDetail } from "@/components/analysis/analysis-detail";
import { getAnalysis } from "@/lib/api";

export default async function AnalysisDetailPage({
  params,
}: {
  params: { id: string } | Promise<{ id: string }>;
}) {
  const { id } = await Promise.resolve(params);

  try {
    const analysis = await getAnalysis(id);
    return (
      <div className="mx-auto w-full max-w-7xl px-6 pb-20 lg:px-10">
        <AnalysisDetail analysis={analysis} />
      </div>
    );
  } catch {
    notFound();
  }
}
