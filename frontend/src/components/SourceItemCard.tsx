import type { SourceItem } from "@/lib/types";
import { ScoreIndicator } from "./ScoreIndicator";

const sourceLabels: Record<string, string> = {
  reddit: "Reddit",
  newsapi: "News",
  bluesky: "Bluesky",
};

export function SourceItemCard({ item }: { item: SourceItem }) {
  const sentiment = item.sentiment_score;

  return (
    <div className="rounded-lg border border-zinc-200 dark:border-zinc-800 p-4 space-y-3">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs font-medium px-2 py-0.5 rounded bg-zinc-100 dark:bg-zinc-800 text-zinc-600 dark:text-zinc-400">
              {sourceLabels[item.source] ?? item.source}
            </span>
            {item.author && (
              <span className="text-xs text-zinc-400 truncate">
                {item.author}
              </span>
            )}
            {item.published_at && (
              <span className="text-xs text-zinc-400">
                {new Date(item.published_at).toLocaleDateString()}
              </span>
            )}
          </div>
          {item.title && (
            <h4 className="text-sm font-medium leading-snug mb-1">
              {item.url ? (
                <a
                  href={item.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="hover:underline"
                >
                  {item.title}
                </a>
              ) : (
                item.title
              )}
            </h4>
          )}
          <p className="text-sm text-zinc-600 dark:text-zinc-400 line-clamp-3">
            {item.text}
          </p>
        </div>
        {sentiment && (
          <div className="shrink-0">
            <ScoreIndicator
              score={sentiment.overall_score}
              label={sentiment.label}
              confidence={sentiment.confidence}
            />
          </div>
        )}
      </div>
      {sentiment?.reasoning && (
        <p className="text-xs text-zinc-400 italic border-t border-zinc-100 dark:border-zinc-800 pt-2">
          {sentiment.reasoning}
        </p>
      )}
    </div>
  );
}
