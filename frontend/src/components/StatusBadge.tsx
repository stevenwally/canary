import type { Topic } from "@/lib/types";

const statusStyles: Record<
  Topic["status"],
  { bg: string; text: string; label: string }
> = {
  pending: {
    bg: "bg-zinc-100 dark:bg-zinc-800",
    text: "text-zinc-600 dark:text-zinc-400",
    label: "Pending",
  },
  running: {
    bg: "bg-amber-100 dark:bg-amber-900/30",
    text: "text-amber-700 dark:text-amber-400",
    label: "Running",
  },
  completed: {
    bg: "bg-green-100 dark:bg-green-900/30",
    text: "text-green-700 dark:text-green-400",
    label: "Completed",
  },
  failed: {
    bg: "bg-red-100 dark:bg-red-900/30",
    text: "text-red-700 dark:text-red-400",
    label: "Failed",
  },
};

export function StatusBadge({ status }: { status: Topic["status"] }) {
  const style = statusStyles[status] ?? statusStyles.pending;
  return (
    <span
      className={`inline-flex items-center gap-1.5 rounded-full px-2.5 py-0.5 text-xs font-medium ${style.bg} ${style.text}`}
    >
      {status === "running" && (
        <span className="h-1.5 w-1.5 rounded-full bg-amber-500 animate-pulse" />
      )}
      {style.label}
    </span>
  );
}
