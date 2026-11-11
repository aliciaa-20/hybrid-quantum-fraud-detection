export const API_BASE: string = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

export type Source = "live" | "stored";
export type ModelScore = { label: 0 | 1; score: number; source: Source };
export type Sample = {
  id: number;
  test_index: number;
  features: Record<string, number>;
  actual: 0 | 1;
  rf: ModelScore;
  qsvm: ModelScore;
  vqc_paper: ModelScore;
};
export type LiveResult = { qsvm: ModelScore; vqc_live: ModelScore; notes: string[] };
export type ScoreRow = {
  row: number;
  features: Record<string, number>;
  rf: ModelScore;
  qsvm: ModelScore | null;
  vqc: ModelScore | null;
  warnings: string[];
};
export type ScoreResult = { rows: ScoreRow[]; notes: string[]; caps: Record<string, number> };
export type FindingsTable = {
  rows: Record<string, string | number>[];
  scope: string;
  caveat: string | null;
};
export type Findings = {
  classical_quantum: FindingsTable;
  cost_benefit: FindingsTable;
  qsvm_vs_vqc: FindingsTable;
  thresholds: FindingsTable;
  validated: FindingsTable;
};
export type Meta = {
  provenance: Record<string, Record<string, unknown>>;
  rf_threshold: number;
  caps: Record<string, number>;
  sample_scope: string;
};

export class ApiError extends Error {}

async function request<T>(path: string, init?: RequestInit, timeoutMs = 60_000): Promise<T> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), timeoutMs);
  try {
    const res = await fetch(`${API_BASE}${path}`, { ...init, signal: ctrl.signal });
    if (!res.ok) {
      let detail = `Request failed (${res.status})`;
      try {
        const body = await res.json();
        if (typeof body.detail === "string") detail = body.detail;
      } catch {
        /* keep default message */
      }
      throw new ApiError(detail);
    }
    return (await res.json()) as T;
  } catch (e) {
    if (e instanceof ApiError) throw e;
    throw new ApiError("Could not reach the server. It may still be waking up; try again in a moment.");
  } finally {
    clearTimeout(timer);
  }
}

export const getHealth = () => request<{ status: string }>("/api/health", undefined, 5_000);
export const getSamples = () => request<Sample[]>("/api/samples");
export const liveScore = (id: number) =>
  request<LiveResult>(`/api/samples/${id}/live`, { method: "POST" }, 40_000);
export const scoreCsv = (file: File) => {
  const body = new FormData();
  body.append("file", file);
  return request<ScoreResult>("/api/score", { method: "POST", body }, 60_000);
};
export const getFindings = () => request<Findings>("/api/findings");
export const getMeta = () => request<Meta>("/api/meta");
