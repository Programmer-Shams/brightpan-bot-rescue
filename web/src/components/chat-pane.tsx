"use client";

import { useEffect, useRef } from "react";
import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { CircleAlert, CircleCheck, TriangleAlert } from "lucide-react";
import { EvidenceRow } from "@/components/evidence-row";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { Build, Turn } from "@/lib/types";
import { cn } from "@/lib/utils";

export const BUILDS: Record<Build, { name: string; note: string }> = {
  broken: { name: "Broken build", note: "As handed over (tag broken). No memory between messages" },
  fixed: { name: "Fixed build", note: "After the audit (tag fixed-final)" },
};

export type Health = { up: boolean; port: string } | null;

export function ChatPane({ build, turns, health }: { build: Build; turns: Turn[]; health: Health }) {
  const end = useRef<HTMLDivElement>(null);
  useEffect(() => {
    const reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    end.current?.scrollIntoView({ behavior: reduce ? "auto" : "smooth", block: "end" });
  }, [turns]);
  const Icon = build === "broken" ? CircleAlert : CircleCheck;

  return (
    <section
      aria-label={BUILDS[build].name}
      className="flex min-h-0 flex-col overflow-hidden rounded-2xl border bg-card shadow-[0_1px_0_rgba(24,32,44,0.04)]"
    >
      <header
        className={cn(
          "flex items-center gap-3 border-b px-5 py-3.5",
          build === "broken" ? "bg-scorch-soft/60" : "bg-seasoned-soft/60",
        )}
      >
        <Icon className={cn("size-5", build === "broken" ? "text-scorch" : "text-seasoned")} aria-hidden />
        <div className="min-w-0">
          <h2 className="font-heading text-[0.95rem] font-semibold leading-tight tracking-tight">{BUILDS[build].name}</h2>
          <p className="text-xs text-muted-foreground">{BUILDS[build].note}</p>
        </div>
        <ServerStatus health={health} />
      </header>

      <div role="log" aria-live="polite" aria-label={`${BUILDS[build].name} conversation`} className="flex-1 space-y-6 overflow-y-auto px-5 py-5">
        {turns.length === 0 && (
          <p className="pt-6 text-center text-sm text-muted-foreground">Answers from the {build} build appear here.</p>
        )}
        {turns.map((t) => (
          <TurnView key={t.id} turn={t} build={build} />
        ))}
        <div ref={end} />
      </div>
    </section>
  );
}

function ServerStatus({ health }: { health: Health }) {
  if (!health) return null;
  return (
    <Tooltip>
      <TooltipTrigger asChild>
        <span className="ml-auto inline-flex items-center gap-1.5 rounded-full bg-card/80 px-2.5 py-1 text-xs text-muted-foreground">
          <span className={cn("size-1.5 rounded-full", health.up ? "bg-seasoned" : "bg-muted-foreground/50")} />
          {health.up ? "Running" : "Not running"}
        </span>
      </TooltipTrigger>
      <TooltipContent>
        {health.up ? `Answering on port ${health.port}` : `Start this build on port ${health.port} to use it`}
      </TooltipContent>
    </Tooltip>
  );
}

function TurnView({ turn, build }: { turn: Turn; build: Build }) {
  if (turn.role === "user") {
    return (
      <div className="flex flex-col items-end gap-1">
        {turn.testId && <span className="font-mono text-[0.7rem] text-muted-foreground">{turn.testId}</span>}
        <p className="max-w-[85%] rounded-2xl rounded-br-md bg-accent px-4 py-2.5 text-[0.925rem] leading-relaxed text-accent-foreground">
          {turn.text}
        </p>
      </div>
    );
  }
  if (turn.role === "pending") {
    return (
      <div className="space-y-2" aria-label="Waiting for the answer">
        <div className="h-3 w-3/4 animate-pulse rounded bg-muted" />
        <div className="h-3 w-1/2 animate-pulse rounded bg-muted" />
      </div>
    );
  }
  if (turn.role === "failed") {
    return (
      <p role="alert" className="flex items-start gap-2 rounded-xl bg-muted px-4 py-3 text-sm text-foreground/80">
        <TriangleAlert className="mt-0.5 size-4 shrink-0 text-scorch" aria-hidden />
        {turn.message}
      </p>
    );
  }
  return (
    <div className="text-[0.925rem] leading-relaxed">
      <ReactMarkdown
        remarkPlugins={[remarkGfm]}
        components={{
          p: (props) => <p className="mb-2 last:mb-0" {...props} />,
          ul: (props) => <ul className="mb-2 list-disc space-y-1 pl-5 last:mb-0" {...props} />,
          ol: (props) => <ol className="mb-2 list-decimal space-y-1 pl-5 last:mb-0" {...props} />,
          strong: (props) => <strong className="font-semibold" {...props} />,
          a: (props) => <a className="text-primary underline underline-offset-2" {...props} />,
        }}
      >
        {turn.reply.answer || "(empty answer)"}
      </ReactMarkdown>
      <EvidenceRow reply={turn.reply} build={build} />
    </div>
  );
}
