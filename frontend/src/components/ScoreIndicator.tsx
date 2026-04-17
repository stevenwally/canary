/**
 * Visual indicator for a single sentiment score.
 * Shows a colored dot and the score value.
 */
export function ScoreIndicator({
  score,
  label,
  confidence,
}: {
  score: number;
  label: "positive" | "negative" | "neutral";
  confidence: number;
}) {
  const colors = {
    positive: "text-positive",
    negative: "text-negative",
    neutral: "text-neutral",
  };

  const bgColors = {
    positive: "bg-positive",
    negative: "bg-negative",
    neutral: "bg-neutral",
  };

  return (
    <div className="flex items-center gap-2">
      <span className={`h-2.5 w-2.5 rounded-full ${bgColors[label]}`} />
      <span className={`text-sm font-semibold ${colors[label]}`}>
        {score > 0 ? "+" : ""}
        {score.toFixed(2)}
      </span>
      <span className="text-xs text-zinc-400" title="Confidence">
        ({(confidence * 100).toFixed(0)}%)
      </span>
    </div>
  );
}
