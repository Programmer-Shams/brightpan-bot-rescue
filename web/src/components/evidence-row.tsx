import { FileText, FileX, PackageSearch, ShieldAlert, ShieldCheck, Timer, UserRound } from "lucide-react";
import type { BotReply, Build } from "@/lib/types";
import { cn } from "@/lib/utils";

const chip = "inline-flex items-center gap-1.5 rounded-md px-2 py-1 leading-none";

/**
 * What the answer rests on: sources, order check, hand-off, tools. Missing evidence is shown, not hidden:
 * the broken build can never return a source, so it gets the red flag; in the fixed build an answer without
 * an article (a refusal, an order lookup, a hand-off) is normal and gets a neutral note.
 */
export function EvidenceRow({ reply, build }: { reply: BotReply; build: Build }) {
  const sources = reply.sources ?? [];
  const tools = reply.tools_called ?? [];
  const lookedUp = tools.includes("lookup_order");

  return (
    <div className="mt-3 border-t border-dashed pt-3 text-xs">
      <div className="flex flex-wrap items-center gap-1.5">
        {sources.length > 0 ? (
          sources.map((s) => (
            <span key={s.id} className={cn(chip, "bg-seasoned-soft text-seasoned")}>
              <FileText className="size-3.5" aria-hidden />
              <span className="font-mono">{s.id}</span>
              <span className="text-foreground/80">{s.title}</span>
            </span>
          ))
        ) : build === "broken" ? (
          <span className={cn(chip, "border border-dashed border-scorch/60 text-scorch")}>
            <FileX className="size-3.5" aria-hidden />
            No source shown
          </span>
        ) : (
          <span className={cn(chip, "border border-dashed text-muted-foreground")}>
            <FileText className="size-3.5" aria-hidden />
            No article cited
          </span>
        )}

        {lookedUp && <OrderCheck reply={reply} />}

        {reply.escalated && (
          <span className={cn(chip, "bg-seasoned-soft text-seasoned")}>
            <UserRound className="size-3.5" aria-hidden />
            Handed to the support team
          </span>
        )}
      </div>

      <div className="mt-2 flex flex-wrap items-center gap-x-3 gap-y-1 text-muted-foreground">
        <span>
          {tools.length ? "Used " : "No tools used"}
          {[...new Set(tools)].map((t, i) => {
            const times = tools.filter((x) => x === t).length;
            return (
              <span key={t}>
                {i > 0 && ", "}
                <code className="font-mono text-foreground/75">{t}</code>
                {times > 1 && <span className="tabular-nums"> ×{times}</span>}
              </span>
            );
          })}
        </span>
        {reply.index_version && (
          <span>
            Help center <code className="font-mono text-foreground/75">{reply.index_version}</code>
          </span>
        )}
        {typeof reply.latency_ms === "number" && (
          <span className="ml-auto inline-flex items-center gap-1">
            <Timer className="size-3.5" aria-hidden />
            {(reply.latency_ms / 1000).toFixed(1)} s
          </span>
        )}
      </div>
    </div>
  );
}

function OrderCheck({ reply }: { reply: BotReply }) {
  const number = reply.order?.order_number;
  if (reply.lookup === "match" && reply.lookup_verified) {
    return (
      <span className={cn(chip, "bg-seasoned-soft text-seasoned")}>
        <ShieldCheck className="size-3.5" aria-hidden />
        Order {number}, email verified
      </span>
    );
  }
  if (reply.lookup === "match") {
    return (
      <span className={cn(chip, "bg-scorch text-white")}>
        <ShieldAlert className="size-3.5" aria-hidden />
        Order {number} shared without an email check
      </span>
    );
  }
  return (
    <span className={cn(chip, "bg-muted text-muted-foreground")}>
      <PackageSearch className="size-3.5" aria-hidden />
      {reply.lookup === "no_match" ? "No matching order, nothing shared" : "Order details not shared"}
    </span>
  );
}
