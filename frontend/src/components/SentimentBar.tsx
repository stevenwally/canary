import type { SentimentSummary } from "@/lib/types";

export function SentimentBar({ summary }: { summary: SentimentSummary }) {
  const { positive_count, negative_count, neutral_count, total_items } = summary;
  if (total_items === 0) return null;

  const posPercent = (positive_count / total_items) * 100;
  const negPercent = (negative_count / total_items) * 100;
  const neuPercent = (neutral_count / total_items) * 100;

  return (
    <div className="space-y-2">
      <div className="flex h-3 w-full overflow-hidden rounded-full bg-zinc-100 dark:bg-zinc-800">
        {posPercent > 0 && (
          <div
            className="bg-positive transition-all duration-500"
            style={{ width: `${posPercent}%` }}
            title={`Positive: ${positive_count} (${posPercent.toFixed(1)}%)`}
          />
        )}
        {neuPercent > 0 && (
          <div
            className="bg-neutral transition-all duration-500"
            style={{ width: `${neuPercent}%` }}
            title={`Neutral: ${neutral_count} (${neuPercent.toFixed(1)}%)`}
          />
        )}
        {negPercent > 0 && (
          <div
            className="bg-negative transition-all duration-500"
            style={{ width: `${negPercent}%` }}
            title={`Negative: ${negative_count} (${negPercent.toFixed(1)}%)`}
          />
        )}
      </div>
      <div className="flex justify-between text-xs text-zinc-500">
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-positive" />
          Positive {positive_count}
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-neutral" />
          Neutral {neutral_count}
        </span>
        <span className="flex items-center gap-1">
          <span className="h-2 w-2 rounded-full bg-negative" />
          Negative {negative_count}
        </span>
      </div>
    </div>
  );
}
