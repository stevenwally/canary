import type { Topic, TopicDetail } from "./types";

const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${API_URL}/api${path}`, {
    headers: { "Content-Type": "application/json" },
    ...options,
  });
  if (!res.ok) {
    const body = await res.text();
    throw new Error(`API error ${res.status}: ${body}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json();
}

export async function listTopics(): Promise<Topic[]> {
  return request<Topic[]>("/topics");
}

export async function createTopic(keyword: string): Promise<Topic> {
  return request<Topic>("/topics", {
    method: "POST",
    body: JSON.stringify({ keyword }),
  });
}

export async function getTopic(id: string): Promise<TopicDetail> {
  return request<TopicDetail>(`/topics/${id}`);
}

export async function analyzeTopic(
  id: string
): Promise<{ status: string; topic_id: string }> {
  return request(`/topics/${id}/analyze`, { method: "POST" });
}

export async function deleteTopic(id: string): Promise<void> {
  return request(`/topics/${id}`, { method: "DELETE" });
}
