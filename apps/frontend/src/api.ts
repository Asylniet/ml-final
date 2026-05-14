import type {
  FeatureImportance,
  ModelStats,
  PredictionResponse,
} from "./types";

const API_URL = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function parseJsonResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const err = await response
      .json()
      .catch(() => ({ detail: response.statusText }));
    throw new Error(String(err.detail ?? "Request failed"));
  }
  return response.json() as Promise<T>;
}

export async function predict(sequence: string): Promise<PredictionResponse> {
  const res = await fetch(`${API_URL}/predict`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ sequence }),
  });

  return parseJsonResponse<PredictionResponse>(res);
}

export async function getFeatureImportances(): Promise<FeatureImportance[]> {
  const res = await fetch(`${API_URL}/features`);
  return parseJsonResponse<FeatureImportance[]>(res);
}

export async function getStats(): Promise<ModelStats> {
  const res = await fetch(`${API_URL}/stats`);
  return parseJsonResponse<ModelStats>(res);
}
