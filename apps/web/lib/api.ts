import { AnalysisDetail, AnalysisListItem } from "@/lib/types";

const serverBaseUrl =
  process.env.WEB_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const browserBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function fetchApi<T>(path: string): Promise<T> {
  const response = await fetch(`${serverBaseUrl}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(`API request failed: ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export async function getAnalyses(query?: string) {
  const suffix = query ? `?q=${encodeURIComponent(query)}` : "";
  return fetchApi<AnalysisListItem[]>(`/api/analyses${suffix}`);
}

export async function getAnalysis(id: string) {
  return fetchApi<AnalysisDetail>(`/api/analyses/${id}`);
}

export async function createAnalysis(formData: FormData) {
  const response = await fetch(`${browserBaseUrl}/api/analyses`, {
    method: "POST",
    body: formData,
  });

  if (!response.ok) {
    const detail = await response.text();
    throw new Error(detail || "Failed to create analysis");
  }

  return response.json() as Promise<AnalysisDetail>;
}

export async function deleteAnalysis(id: string) {
  const response = await fetch(`${browserBaseUrl}/api/analyses/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error("Failed to delete analysis");
  }
}

