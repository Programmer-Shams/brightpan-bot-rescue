"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { ArrowUp, CookingPot, Info, PanelLeft, RotateCcw } from "lucide-react";
import { BUILDS, ChatPane, type Health } from "@/components/chat-pane";
import { QuestionRail } from "@/components/question-rail";
import { Button } from "@/components/ui/button";
import { Sheet, SheetContent, SheetDescription, SheetTitle, SheetTrigger } from "@/components/ui/sheet";
import { Textarea } from "@/components/ui/textarea";
import { ToggleGroup, ToggleGroupItem } from "@/components/ui/toggle-group";
import { Tooltip, TooltipContent, TooltipTrigger } from "@/components/ui/tooltip";
import type { BotReply, Build, Mode, TestQuestion, Turn } from "@/lib/types";
import { cn } from "@/lib/utils";

const ALL_BUILDS: Build[] = ["broken", "fixed"];
const STARTERS = ["Q02", "Q31", "Q41", "Q26"];
const newId = () => crypto.randomUUID();

async function ask(build: Build, sessionId: string, message: string): Promise<Turn> {
  try {
    const res = await fetch("/api/chat", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ build, session_id: sessionId, message }),
    });
    const data = await res.json().catch(() => null);
    if (!res.ok || !data) {
      return { role: "failed", id: newId(), message: data?.error ?? `This page's server returned HTTP ${res.status}. Check the npm run dev terminal.` };
    }
    const reply = data as BotReply;
    if (reply.error) return { role: "failed", id: newId(), message: `The ${build} build hit an error. Check its server log.` };
    return { role: "assistant", id: newId(), reply };
  } catch {
    return { role: "failed", id: newId(), message: "Can't reach this page's server. Check that npm run dev is running." };
  }
}

export function Workbench({ questions }: { questions: TestQuestion[] }) {
  const [mode, setMode] = useState<Mode>("compare");
  const [turns, setTurns] = useState<Record<Build, Turn[]>>({ broken: [], fixed: [] });
  // Created on first send (browser only), so the server render has no random values.
  const sessions = useRef<Record<Build, string> | null>(null);
  const [health, setHealth] = useState<Record<Build, Health>>({ broken: null, fixed: null });
  const [draft, setDraft] = useState("");
  const [busy, setBusy] = useState(false);
  const [active, setActive] = useState<TestQuestion | undefined>();
  const [railOpen, setRailOpen] = useState(false);

  const builds = useMemo<Build[]>(() => (mode === "compare" ? ALL_BUILDS : [mode]), [mode]);
  const empty = builds.every((b) => turns[b].length === 0);

  useEffect(() => {
    const check = () =>
      ALL_BUILDS.forEach((b) =>
        fetch(`/api/chat?build=${b}`)
          .then((r) => r.json())
          .then((h) => setHealth((prev) => ({ ...prev, [b]: typeof h?.up === "boolean" ? (h as Health) : null })))
          .catch(() => {}),
      );
    check();
    const timer = setInterval(check, 15_000);
    return () => clearInterval(timer);
  }, []);

  const send = useCallback(
    async (text: string, test?: TestQuestion) => {
      const message = text.trim();
      if (!message || busy) return;
      setBusy(true);
      setActive(test);
      setDraft("");
      setRailOpen(false);
      sessions.current ??= { broken: newId(), fixed: newId() };
      const ids = sessions.current;
      const pending = Object.fromEntries(builds.map((b) => [b, newId()])) as Record<Build, string>;
      setTurns((prev) => {
        const next = { ...prev };
        for (const b of builds) {
          next[b] = [
            ...prev[b],
            { role: "user", id: newId(), text: message, testId: test?.id },
            { role: "pending", id: pending[b] },
          ];
        }
        return next;
      });
      await Promise.all(
        builds.map(async (b) => {
          const turn = await ask(b, ids[b], message);
          setTurns((prev) => ({ ...prev, [b]: prev[b].map((t) => (t.id === pending[b] ? turn : t)) }));
        }),
      );
      setBusy(false);
    },
    [builds, busy],
  );

  const reset = () => {
    setTurns({ broken: [], fixed: [] });
    sessions.current = null;
    setActive(undefined);
  };

  const pick = (q: TestQuestion) => send(q.question, q);
  const rail = <QuestionRail questions={questions} activeId={active?.id} disabled={busy} onPick={pick} />;

  return (
    <div className="flex h-full flex-col">
      <header className="flex h-14 shrink-0 items-center gap-3 border-b bg-card px-3 sm:px-4">
        <Sheet open={railOpen} onOpenChange={setRailOpen}>
          <SheetTrigger asChild>
            <Button variant="ghost" size="icon" className="lg:hidden" aria-label="Show test questions">
              <PanelLeft />
            </Button>
          </SheetTrigger>
          <SheetContent side="left" className="flex w-[22rem] max-w-[90vw] flex-col gap-0 bg-sidebar p-0">
            <SheetTitle className="sr-only">Test questions</SheetTitle>
            <SheetDescription className="sr-only">Pick a question to ask the bot.</SheetDescription>
            {rail}
          </SheetContent>
        </Sheet>

        <div className="flex items-center gap-2.5">
          <span className="grid size-8 place-items-center rounded-lg bg-primary text-primary-foreground">
            <CookingPot className="size-[18px]" aria-hidden />
          </span>
          <div className="hidden leading-tight min-[420px]:block">
            <p className="font-heading text-[0.95rem] font-semibold tracking-tight">Brightpan</p>
            <p className="hidden text-xs text-muted-foreground sm:block">Support bot, before and after</p>
          </div>
        </div>

        <ToggleGroup
          type="single"
          value={mode}
          onValueChange={(v) => v && setMode(v as Mode)}
          variant="outline"
          spacing={0}
          aria-label="Which build to ask"
          className="mx-auto bg-background [&_[data-state=on]]:bg-primary [&_[data-state=on]]:text-primary-foreground"
        >
          <ToggleGroupItem value="broken" className="px-3">Broken</ToggleGroupItem>
          <ToggleGroupItem value="compare" className="px-3">
            <span className="hidden sm:inline">Side by side</span>
            <span className="sm:hidden">Both</span>
          </ToggleGroupItem>
          <ToggleGroupItem value="fixed" className="px-3">Fixed</ToggleGroupItem>
        </ToggleGroup>

        <Tooltip>
          <TooltipTrigger asChild>
            <button
              type="button"
              className="inline-flex shrink-0 items-center gap-1.5 rounded-full border bg-background px-2 py-1 text-xs font-medium focus-visible:outline-2 focus-visible:outline-ring md:px-3"
            >
              <Info className="size-3.5 text-primary" aria-hidden />
              <span className="sr-only md:not-sr-only">Faults planted on purpose</span>
            </button>
          </TooltipTrigger>
          <TooltipContent className="max-w-72">
            Portfolio project. The five faults in the broken build were planted on purpose.
          </TooltipContent>
        </Tooltip>
      </header>

      <div className="flex min-h-0 flex-1">
        <aside className="hidden w-80 shrink-0 flex-col border-r bg-sidebar lg:flex">{rail}</aside>

        <main className="flex min-w-0 flex-1 flex-col">
          {empty ? (
            <Intro questions={questions} onPick={pick} disabled={busy} />
          ) : (
            <div
              className={cn(
                "grid min-h-0 flex-1 gap-3 p-3 sm:p-4",
                builds.length === 2 ? "grid-rows-2 lg:grid-cols-2 lg:grid-rows-1" : "mx-auto w-full max-w-3xl",
              )}
            >
              {builds.map((b) => (
                <ChatPane key={b} build={b} turns={turns[b]} health={health[b]} />
              ))}
            </div>
          )}

          <form
            onSubmit={(e) => {
              e.preventDefault();
              send(draft);
            }}
            className="shrink-0 px-3 pb-3 sm:px-4 sm:pb-4"
          >
            <div className="mx-auto flex max-w-3xl items-end gap-2 rounded-2xl border bg-card p-2 shadow-[0_6px_24px_-12px_rgba(24,32,44,0.25)] focus-within:border-ring">
              <Textarea
                value={draft}
                onChange={(e) => setDraft(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault();
                    send(draft);
                  }
                }}
                rows={1}
                maxLength={2000}
                placeholder={mode === "compare" ? "Ask both builds a question" : `Ask the ${mode} build a question`}
                aria-label="Your question"
                className="max-h-40 min-h-10 resize-none border-0 bg-transparent shadow-none focus-visible:ring-0"
              />
              {!empty && (
                <Button type="button" variant="ghost" size="icon" onClick={reset} disabled={busy} aria-label="Clear the conversation">
                  <RotateCcw />
                </Button>
              )}
              <Button type="submit" size="icon" disabled={busy || !draft.trim()} aria-label={mode === "compare" ? "Ask both" : "Ask"}>
                <ArrowUp />
              </Button>
            </div>
          </form>
        </main>
      </div>
    </div>
  );
}

function Intro({ questions, onPick, disabled }: { questions: TestQuestion[]; onPick: (q: TestQuestion) => void; disabled: boolean }) {
  const starters = STARTERS.map((id) => questions.find((q) => q.id === id)).filter((q): q is TestQuestion => !!q);
  return (
    <div className="flex flex-1 items-center overflow-y-auto px-5 py-10 sm:px-10">
      <div className="mx-auto w-full max-w-3xl">
        <h1 className="font-heading text-[2.6rem] font-semibold leading-[1.02] tracking-[-0.035em] text-balance sm:text-[3.4rem]">
          Ask the same question before and after the fix.
        </h1>
        <p className="mt-5 max-w-xl text-[1.02rem] leading-relaxed text-muted-foreground">
          The broken build is the store&apos;s support bot with five faults planted on purpose. The fixed build is
          the same bot after the audit. Every answer shows what it was based on.
        </p>

        <div className="mt-8 grid gap-3 sm:grid-cols-2">
          {ALL_BUILDS.map((b) => (
            <div
              key={b}
              className={cn(
                "rounded-xl border-l-4 bg-card px-4 py-3",
                b === "broken" ? "border-l-scorch" : "border-l-seasoned",
              )}
            >
              <p className="text-sm font-semibold">{BUILDS[b].name}</p>
              <p className="text-sm text-muted-foreground">{BUILDS[b].note}</p>
            </div>
          ))}
        </div>

        <p className="mt-8 text-sm font-medium">Try a question from the test</p>
        <div className="mt-3 flex flex-wrap gap-2">
          {starters.map((q) => (
            <button
              key={q.id}
              type="button"
              aria-disabled={disabled || undefined}
              onClick={() => !disabled && onPick(q)}
              className="group inline-flex max-w-full items-center gap-2 rounded-full border bg-card px-3.5 py-2 text-left text-sm transition-colors hover:border-primary hover:bg-accent focus-visible:outline-2 focus-visible:outline-ring aria-disabled:opacity-60"
            >
              <span className="font-mono text-[0.7rem] text-muted-foreground group-hover:text-accent-foreground">{q.id}</span>
              <span className="truncate">{q.question}</span>
            </button>
          ))}
        </div>
      </div>
    </div>
  );
}
