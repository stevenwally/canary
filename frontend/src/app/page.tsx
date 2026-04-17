"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { createTopic, listTopics, analyzeTopic, deleteTopic } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import type { Topic } from "@/lib/types";

export default function Dashboard() {
  const [topics, setTopics] = useState<Topic[]>([]);
  const [keyword, setKeyword] = useState("");
  const [loading, setLoading] = useState(true);
  const [creating, setCreating] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const loadTopics = useCallback(async () => {
    try {
      const data = await listTopics();
      setTopics(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load topics");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    loadTopics();

    // Poll for status updates every 5 seconds
    const interval = setInterval(loadTopics, 5000);
    return () => clearInterval(interval);
  }, [loadTopics]);

  const handleCreate = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!keyword.trim()) return;

    setCreating(true);
    setError(null);
    try {
      const topic = await createTopic(keyword.trim());
      setKeyword("");
      // Immediately start analysis
      await analyzeTopic(topic.id);
      await loadTopics();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to create topic");
    } finally {
      setCreating(false);
    }
  };

  const handleDelete = async (id: string) => {
    try {
      await deleteTopic(id);
      await loadTopics();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to delete topic");
    }
  };

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      <div className="mb-8">
        <h1 className="text-2xl font-bold tracking-tight mb-1">Dashboard</h1>
        <p className="text-zinc-500 text-sm">
          Track sentiment across topics. Enter a keyword to start analysis.
        </p>
      </div>

      {/* Create topic form */}
      <form onSubmit={handleCreate} className="mb-8 flex gap-3">
        <input
          type="text"
          value={keyword}
          onChange={(e) => setKeyword(e.target.value)}
          placeholder="Enter a topic or keyword..."
          className="flex-1 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-900 px-4 py-2.5 text-sm placeholder:text-zinc-400 focus:outline-none focus:ring-2 focus:ring-accent/50 focus:border-accent"
          disabled={creating}
        />
        <button
          type="submit"
          disabled={creating || !keyword.trim()}
          className="rounded-lg bg-accent-dark hover:bg-accent px-5 py-2.5 text-sm font-medium text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {creating ? "Analyzing..." : "Analyze"}
        </button>
      </form>

      {error && (
        <div className="mb-6 rounded-lg bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 px-4 py-3 text-sm text-red-700 dark:text-red-400">
          {error}
        </div>
      )}

      {/* Topics list */}
      {loading ? (
        <div className="text-center text-zinc-400 py-12">Loading...</div>
      ) : topics.length === 0 ? (
        <div className="text-center text-zinc-400 py-12">
          <p className="text-lg mb-1">No topics yet</p>
          <p className="text-sm">
            Enter a keyword above to start your first analysis.
          </p>
        </div>
      ) : (
        <div className="space-y-3">
          {topics.map((topic) => (
            <div
              key={topic.id}
              className="flex items-center justify-between rounded-lg border border-zinc-200 dark:border-zinc-800 px-5 py-4 hover:bg-zinc-50 dark:hover:bg-zinc-900/50 transition-colors"
            >
              <Link
                href={`/topics/${topic.id}`}
                className="flex-1 min-w-0 flex items-center gap-4"
              >
                <span className="font-medium truncate">{topic.keyword}</span>
                <StatusBadge status={topic.status} />
              </Link>
              <div className="flex items-center gap-3 ml-4">
                <span className="text-xs text-zinc-400">
                  {new Date(topic.created_at).toLocaleDateString()}
                </span>
                <button
                  onClick={(e) => {
                    e.preventDefault();
                    handleDelete(topic.id);
                  }}
                  className="text-xs text-zinc-400 hover:text-red-500 transition-colors"
                  title="Delete topic"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
