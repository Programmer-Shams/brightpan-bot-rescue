"use client";

import { useMemo, useState } from "react";
import { Search } from "lucide-react";
import { Input } from "@/components/ui/input";
import type { Category, TestQuestion } from "@/lib/types";
import { cn } from "@/lib/utils";

const GROUPS: { category: Category; title: string; hint: string }[] = [
  { category: "answerable", title: "Answer from the help center", hint: "Policy questions with one right answer" },
  { category: "order_lookup", title: "Look up an order", hint: "Order number and the matching email" },
  { category: "refuse", title: "Decline", hint: "Not in the help center, or details don't match" },
  { category: "escalate", title: "Hand off to a person", hint: "Refunds, damage, warranty, complaints" },
];

export function QuestionRail({
  questions,
  activeId,
  disabled,
  onPick,
}: {
  questions: TestQuestion[];
  activeId?: string;
  disabled: boolean;
  onPick: (q: TestQuestion) => void;
}) {
  const [query, setQuery] = useState("");
  const visible = useMemo(() => {
    const q = query.trim().toLowerCase();
    return q ? questions.filter((t) => `${t.id} ${t.question}`.toLowerCase().includes(q)) : questions;
  }, [questions, query]);

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="space-y-3 px-4 pb-3 pt-4">
        <div>
          <h2 className="font-heading text-[0.95rem] font-semibold tracking-tight">Test questions</h2>
          <p className="text-xs text-muted-foreground">The {questions.length} questions the before/after test runs</p>
        </div>
        <div className="relative">
          <Search className="pointer-events-none absolute left-2.5 top-1/2 size-4 -translate-y-1/2 text-muted-foreground" />
          <Input
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            placeholder="Find a question"
            aria-label="Find a test question"
            className="bg-card pl-8"
          />
        </div>
      </div>

      <nav aria-label="Test questions" className="flex-1 overflow-y-auto px-2 pb-4">
        {GROUPS.map((g) => {
          const items = visible.filter((q) => q.category === g.category);
          if (!items.length) return null;
          return (
            <section key={g.category} className="mt-3 first:mt-0">
              <div className="px-2 pb-1.5">
                <h3 className="text-[0.8rem] font-semibold">
                  {g.title} <span className="font-normal text-muted-foreground tabular-nums">{items.length}</span>
                </h3>
                <p className="text-[0.7rem] text-muted-foreground">{g.hint}</p>
              </div>
              <ul className="space-y-0.5">
                {items.map((q) => {
                  const active = q.id === activeId;
                  return (
                    <li key={q.id}>
                      <button
                        type="button"
                        disabled={disabled}
                        onClick={() => onPick(q)}
                        aria-current={active || undefined}
                        className={cn(
                          "group flex w-full gap-2.5 rounded-lg px-2 py-2 text-left text-[0.825rem] leading-snug transition-colors",
                          "hover:bg-sidebar-accent focus-visible:outline-2 focus-visible:outline-ring disabled:cursor-wait disabled:opacity-60",
                          active && "bg-sidebar-accent text-sidebar-accent-foreground",
                        )}
                      >
                        <span className="mt-px w-8 shrink-0 font-mono text-[0.7rem] text-muted-foreground">{q.id}</span>
                        <span className="min-w-0">
                          <span className="line-clamp-2">{q.question}</span>
                          {active && <span className="mt-1 block text-[0.75rem] text-muted-foreground">Expected: {q.expected}</span>}
                        </span>
                      </button>
                    </li>
                  );
                })}
              </ul>
            </section>
          );
        })}
        {!visible.length && <p className="px-2 pt-2 text-sm text-muted-foreground">No question matches “{query}”.</p>}
      </nav>
    </div>
  );
}
