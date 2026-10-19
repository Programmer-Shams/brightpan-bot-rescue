import { createHmac, randomBytes } from "node:crypto";
import type { Build } from "@/lib/types";

// Proxies the page to the two bot builds (FastAPI /chat). The bot URLs stay on the server,
// and the page needs no CORS setup. Request checks follow the Demo 1 proxy.
const ENDPOINTS: Record<Build, string> = {
  broken: process.env.BOT_BROKEN_URL ?? "http://127.0.0.1:8003/chat",
  fixed: process.env.BOT_FIXED_URL ?? "http://127.0.0.1:8004/chat",
};
// The demo orders are dated October 2026; the eval harness freezes "today" to the same day.
const TODAY = process.env.DEMO_TODAY ?? "2026-10-18";
const MAX_MESSAGE = 2000;
// Hosts this page is served from; anything else (e.g. a DNS-rebinding name) is refused.
const ALLOWED_HOSTS = new Set((process.env.ALLOWED_HOSTS ?? "127.0.0.1:3300,localhost:3300").split(",").map((h) => h.trim()));
// The browser's random id is mapped to a keyed hash before it reaches the bot, so a session id seen in the
// bot's logs can't be replayed through this page to read that conversation's memory.
const SESSION_KEY = process.env.SESSION_SECRET || randomBytes(32).toString("hex");
const serverSessionId = (clientId: string) =>
  "web-" + createHmac("sha256", SESSION_KEY).update(clientId).digest("hex").slice(0, 32);

export const maxDuration = 120;

// In-memory rate limit for this single-process local demo; one shared bucket. Rejected requests don't count.
const RATE = { max: 60, windowMs: 5 * 60 * 1000 };
let hits: number[] = [];

function rateLimited(): boolean {
  const now = Date.now();
  hits = hits.filter((t) => now - t < RATE.windowMs);
  if (hits.length >= RATE.max) return true;
  hits.push(now);
  return false;
}

const fail = (status: number, error: string) => Response.json({ error }, { status });

/** Only same-origin requests to an allowed host: blocks other websites from posting through the proxy. */
function crossSite(request: Request): boolean {
  if (!ALLOWED_HOSTS.has(request.headers.get("host") ?? "")) return true;
  if (request.headers.get("sec-fetch-site") === "cross-site") return true;
  const origin = request.headers.get("origin");
  if (!origin) return false;
  try {
    return new URL(origin).host !== request.headers.get("host");
  } catch {
    return true;
  }
}

const parseBuild = (value: unknown): Build | null => (value === "broken" || value === "fixed" ? value : null);

/** GET /api/chat?build=fixed — is that build's server up? */
export async function GET(request: Request) {
  if (crossSite(request)) return fail(403, "Requests must come from this page.");
  const build = parseBuild(new URL(request.url).searchParams.get("build"));
  if (!build) return fail(400, "Pick a build: broken or fixed.");
  try {
    const res = await fetch(new URL("/openapi.json", ENDPOINTS[build]), {
      signal: AbortSignal.timeout(3000),
      cache: "no-store",
    });
    return Response.json({ up: res.ok, port: new URL(ENDPOINTS[build]).port });
  } catch {
    return Response.json({ up: false, port: new URL(ENDPOINTS[build]).port });
  }
}

export async function POST(request: Request) {
  if (crossSite(request)) return fail(403, "Requests must come from this page.");
  if (!request.headers.get("content-type")?.toLowerCase().startsWith("application/json")) {
    return fail(415, "Send the message as JSON.");
  }
  let body: { message?: unknown; session_id?: unknown; build?: unknown };
  try {
    body = await request.json();
  } catch {
    return fail(400, "Request body must be JSON.");
  }

  const message = typeof body.message === "string" ? body.message.trim() : "";
  const sessionId = typeof body.session_id === "string" ? body.session_id : "";
  const build = parseBuild(body.build);

  if (!build) return fail(400, "Pick a build: broken or fixed.");
  if (!message || message.length > MAX_MESSAGE) {
    return fail(400, `Write a message of 1 to ${MAX_MESSAGE.toLocaleString("en-US")} characters.`);
  }
  if (!/^[\w-]{8,100}$/.test(sessionId)) return fail(400, "Start a new conversation and send the message again.");
  if (rateLimited()) return fail(429, "Too many messages in a short time. Wait a few minutes, then try again.");

  let res: Response;
  try {
    res = await fetch(ENDPOINTS[build], {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ message, session_id: serverSessionId(sessionId), today: TODAY }),
      signal: AbortSignal.timeout(110_000),
      cache: "no-store",
    });
  } catch (err) {
    const timedOut = err instanceof Error && err.name === "TimeoutError";
    const port = new URL(ENDPOINTS[build]).port;
    return fail(
      502,
      timedOut
        ? "The bot took longer than 110 seconds. Send the message again."
        : `The ${build} build isn't running. Start it on port ${port}, then send the message again.`,
    );
  }

  if (!res.ok) return fail(502, `The ${build} build returned HTTP ${res.status}. Check its server log.`);
  try {
    return Response.json(await res.json());
  } catch {
    return fail(502, `The ${build} build sent a reply that isn't JSON. Check its server log.`);
  }
}
