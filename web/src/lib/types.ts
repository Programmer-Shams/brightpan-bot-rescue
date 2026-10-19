export type Build = "broken" | "fixed";
export type Mode = Build | "compare";

export type Category = "answerable" | "order_lookup" | "refuse" | "escalate";

export interface TestQuestion {
  id: string;
  category: Category;
  question: string;
  expected: string;
}

/** The bot's /chat response (same shape as the Demo 1 endpoint). */
export interface BotReply {
  answer: string;
  tools_called?: string[];
  article_ids_used?: string[];
  sources?: { id: string; title: string }[];
  lookup?: "match" | "no_match" | "incomplete" | null;
  /** True only when the bot checked the order's email before using it (fixed build). */
  lookup_verified?: boolean;
  order?: { order_number: string; fulfillment_status?: string } | null;
  escalated?: boolean;
  handoff_id?: string | null;
  latency_ms?: number;
  model?: string;
  /** Help-center version the answer came from (fixed build). */
  index_version?: string;
  error?: boolean;
}

export type Turn =
  | { role: "user"; id: string; text: string; testId?: string }
  | { role: "assistant"; id: string; reply: BotReply }
  | { role: "pending"; id: string }
  | { role: "failed"; id: string; message: string };
