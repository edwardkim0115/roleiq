import { AnalysisDetail, AnalysisListItem } from "@/lib/types";

const serverBaseUrl =
  process.env.WEB_API_BASE_URL ?? process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

const browserBaseUrl =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

async function readErrorMessage(response: Response) {
  const contentType = response.headers.get("content-type") ?? "";
  if (contentType.includes("application/json")) {
    const payload = (await response.json()) as {
      detail?: string | { message?: string } | Array<{ msg?: string }>;
      message?: string;
    };
    if (typeof payload.detail === "string") {
      return payload.detail;
    }
    if (Array.isArray(payload.detail)) {
      return payload.detail.map((item) => item.msg).filter(Boolean).join("; ") || "Request failed";
    }
    if (payload.detail && typeof payload.detail === "object" && "message" in payload.detail) {
      return payload.detail.message ?? "Request failed";
    }
    if (typeof payload.message === "string") {
      return payload.message;
    }
  }

  const text = await response.text();
  return text || `API request failed: ${response.status}`;
}

async function fetchApi<T>(path: string): Promise<T> {
  const response = await fetch(`${serverBaseUrl}${path}`, {
    cache: "no-store",
  });

  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
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
    throw new Error(await readErrorMessage(response));
  }

  return response.json() as Promise<AnalysisDetail>;
}

export async function deleteAnalysis(id: string) {
  const response = await fetch(`${browserBaseUrl}/api/analyses/${id}`, {
    method: "DELETE",
  });
  if (!response.ok) {
    throw new Error(await readErrorMessage(response));
  }
}
