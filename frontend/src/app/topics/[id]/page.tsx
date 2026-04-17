"use client";

import { useCallback, useEffect, useState } from "react";
import Link from "next/link";
import { useParams } from "next/navigation";
import { getTopic, analyzeTopic } from "@/lib/api";
import { StatusBadge } from "@/components/StatusBadge";
import { SentimentBar } from "@/components/SentimentBar";
import { SourceItemCard } from "@/components/SourceItemCard";
import type { TopicDetail } from "@/lib/types";

export default function TopicDetailPage() {
  const params = useParams();
  const id = params.id as string;
  const [topic, setTopic] = useState<TopicDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadTopic = useCallback(async () => {
    try {
      const data = await getTopic(id);
      setTopic(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to load topic");
    } finally {
      setLoading(false);
    }
  }, [id]);

  useEffect(() => {
    loadTopic();

    // Poll while running
    const interval = setInterval(() => {
      loadTopic();
    }, 3000);

    return () => clearInterval(interval);
  }, [loadTopic]);

  // Stop polling once completed or failed
  useEffect(() => {
    if (topic && topic.status !== "running") {
      // One final load to ensure we have the latest data
    }
  }, [topic]);

  const handleReanalyze = async () => {
    try {
      await analyzeTopic(id);
      await loadTopic();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Failed to start analysis");
    }
  };

  if (loading) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-center text-zinc-400 py-12">Loading...</div>
      </div>
    );
  }

  if (error || !topic) {
    return (
      <div className="max-w-6xl mx-auto px-6 py-8">
        <div className="text-center text-red-500 py-12">
          {error || "Topic not found"}
        </div>
      </div>
    );
  }

  const summary = topic.summary;

  return (
    <div className="max-w-6xl mx-auto px-6 py-8">
      {/* Header */}
      <div className="mb-8">
        <Link
          href="/"
          className="text-xs text-zinc-400 hover:text-foreground transition-colors mb-3 inline-block"
        >
          &larr; Back to Dashboard
        </Link>
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <h1 className="text-2xl font-bold tracking-tight">
              {topic.keyword}
            </h1>
            <StatusBadge status={topic.status} />
          </div>
          <button
            onClick={handleReanalyze}
            disabled={topic.status === "running"}
            className="rounded-lg bg-accent-dark hover:bg-accent px-4 py-2 text-sm font-medium text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {topic.status === "running" ? "Analyzing..." : "Re-analyze"}
          </button>
        </div>
      </div>

      {/* Running state */}
      {topic.status === "running" && (
        <div className="mb-8 rounded-lg bg-amber-50 dark:bg-amber-900/20 border border-amber-200 dark:border-amber-800 px-5 py-4">
          <div className="flex items-center gap-3">
            <span className="h-2 w-2 rounded-full bg-amber-500 animate-pulse" />
            <span className="text-sm text-amber-700 dark:text-amber-400">
              Analysis in progress. Fetching sources and scoring sentiment...
            </span>
          </div>
        </div>
      )}

      {/* Summary section */}
      {summary && (
        <div className="mb-8 space-y-6">
          <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-6">
            <h2 className="text-sm font-medium text-zinc-500 mb-4 uppercase tracking-wider">
              Sentiment Overview
            </h2>

            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-6">
              <StatCard
                label="Total Items"
                value={summary.total_items.toString()}
              />
              <StatCard
                label="Avg. Score"
                value={
                  summary.average_score !== null
                    ? (summary.average_score > 0 ? "+" : "") +
                      summary.average_score.toFixed(3)
                    : "-"
                }
                color={
                  summary.average_score !== null
                    ? summary.average_score > 0.15
                      ? "text-positive"
                      : summary.average_score < -0.15
                        ? "text-negative"
                        : "text-neutral"
                    : undefined
                }
              />
              <StatCard
                label="Avg. Confidence"
                value={
                  summary.average_confidence !== null
                    ? `${(summary.average_confidence * 100).toFixed(0)}%`
                    : "-"
                }
              />
              <StatCard
                label="Sources"
                value={Object.keys(summary.source_breakdown).length.toString()}
              />
            </div>

            <SentimentBar summary={summary} />

            {/* Source breakdown */}
            {Object.keys(summary.source_breakdown).length > 0 && (
              <div className="mt-4 pt-4 border-t border-zinc-100 dark:border-zinc-800">
                <h3 className="text-xs font-medium text-zinc-400 mb-2">
                  Items by Source
                </h3>
                <div className="flex gap-4">
                  {Object.entries(summary.source_breakdown).map(
                    ([source, count]) => (
                      <span key={source} className="text-xs text-zinc-500">
                        <span className="font-medium capitalize">{source}</span>:{" "}
                        {count}
                      </span>
                    )
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Items list */}
      {topic.items.length > 0 && (
        <div>
          <h2 className="text-sm font-medium text-zinc-500 mb-4 uppercase tracking-wider">
            Source Items ({topic.items.length})
          </h2>
          <div className="space-y-3">
            {topic.items
              .sort((a, b) => {
                // Sort by sentiment score (most extreme first)
                const aScore = Math.abs(
                  a.sentiment_score?.overall_score ?? 0
                );
                const bScore = Math.abs(
                  b.sentiment_score?.overall_score ?? 0
                );
                return bScore - aScore;
              })
              .map((item) => (
                <SourceItemCard key={item.id} item={item} />
              ))}
          </div>
        </div>
      )}

      {/* Empty state */}
      {topic.status === "completed" && topic.items.length === 0 && (
        <div className="text-center text-zinc-400 py-12">
          <p className="text-lg mb-1">No results found</p>
          <p className="text-sm">
            No relevant content was found for this keyword. Try a different
            search term.
          </p>
        </div>
      )}
    </div>
  );
}

function StatCard({
  label,
  value,
  color,
}: {
  label: string;
  value: string;
  color?: string;
}) {
  return (
    <div className="rounded-lg bg-zinc-50 dark:bg-zinc-900 p-3">
      <div className="text-xs text-zinc-400 mb-1">{label}</div>
      <div className={`text-lg font-semibold ${color ?? ""}`}>{value}</div>
    </div>
  );
}
