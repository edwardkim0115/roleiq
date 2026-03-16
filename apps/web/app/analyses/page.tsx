import { AnalysisHistory } from "@/components/analysis/analysis-history";
import { getAnalyses } from "@/lib/api";

export default async function AnalysesPage({
  searchParams,
}: {
  searchParams?: { q?: string } | Promise<{ q?: string }>;
}) {
  const resolvedSearchParams = (await Promise.resolve(searchParams)) ?? {};
  const analyses = await getAnalyses(resolvedSearchParams.q);

  return (
    <div className="mx-auto w-full max-w-7xl px-6 pb-20 lg:px-10">
      <AnalysisHistory analyses={analyses} query={resolvedSearchParams.q} />
    </div>
  );
}
