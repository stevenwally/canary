export interface Topic {
  id: string;
  keyword: string;
  status: "pending" | "running" | "completed" | "failed";
  created_at: string;
  updated_at: string;
}

export interface AspectSentiment {
  aspect: string;
  score: number;
  label: "positive" | "negative" | "neutral";
}

export interface SentimentScore {
  id: string;
  overall_score: number;
  confidence: number;
  label: "positive" | "negative" | "neutral";
  aspects: AspectSentiment[] | null;
  reasoning: string | null;
  created_at: string;
}

export interface SourceItem {
  id: string;
  source: string;
  title: string | null;
  text: string;
  author: string | null;
  url: string | null;
  published_at: string | null;
  verified: boolean;
  sentiment_score: SentimentScore | null;
  created_at: string;
}

export interface SentimentSummary {
  total_items: number;
  positive_count: number;
  negative_count: number;
  neutral_count: number;
  average_score: number | null;
  average_confidence: number | null;
  source_breakdown: Record<string, number>;
}

export interface TopicDetail extends Topic {
  summary: SentimentSummary | null;
  items: SourceItem[];
}
