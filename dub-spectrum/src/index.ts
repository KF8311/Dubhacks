import { readFileSync, writeFileSync } from "node:fs";
import { Spectrum } from "spectrum-ts";
import { imessage } from "@spectrum-ts/imessage";
import {
  createSession,
  formatResults,
  isSearchable,
  MENU,
  submitAnswers,
  toQuery,
  waitForResults,
} from "./agent";
import {
  ConsentStore,
  isStopReply,
  normalizePhone,
  parseConsentReply,
} from "./consent";

// Spectrum bridges a single agent loop to many messaging interfaces.
// Docs: https://photon.codes/docs/spectrum-ts
const app = await Spectrum({
  projectId: process.env.PROJECT_ID!,
  projectSecret: process.env.PROJECT_SECRET!,
  providers: [
    // imessage
    imessage.config(),
  ],
});

// The spectrum instance doubles as the platform namespace: `mail.space.create`
// opens (or resolves) a 1:1 chat from an E.164 number, and `space.get` returns
// the chat the user last texted. Both are how the website reaches the phone
// without the shopper copying a link between devices.
const mail = imessage(app);

type Chat = { query: string; awaitingDetail?: boolean };

// One conversation per space. A first text is a search; every later text
// refines the last search unless it starts with "new:".
const chats = new Map<string, Chat>();

// Where a website-initiated text goes. `MY_PHONE` is the explicit setting; a
// space remembered from an inbound text is the fallback, so the number never
// has to be typed into the site. The state file keeps that memory across a
// bridge restart.
const STATE_FILE = `${import.meta.dir}/../.last-space.json`;
const CONSENT_FILE = `${import.meta.dir}/../.phone-consent.json`;
const MY_PHONE = (process.env.MY_PHONE ?? "").trim();
const consents = new ConsentStore(CONSENT_FILE);
let lastSpaceId = "";

try {
  const state = JSON.parse(readFileSync(STATE_FILE, "utf8")) as { spaceId?: string };
  lastSpaceId = String(state.spaceId ?? "");
} catch {
  // No inbound text has been remembered yet.
}

function rememberSpace(spaceId: string): void {
  if (!spaceId || spaceId === lastSpaceId) return;
  lastSpaceId = spaceId;
  try {
    writeFileSync(STATE_FILE, JSON.stringify({ spaceId }));
  } catch {
    // A read-only checkout is still able to text while the process lives.
  }
}

async function phoneSpace() {
  if (MY_PHONE) return mail.space.create(MY_PHONE);
  if (lastSpaceId) return mail.space.get(lastSpaceId);
  throw new Error(
    "No phone is linked yet. Text the bridge once, or set MY_PHONE in dub-spectrum/.env.",
  );
}

/**
 * A number that replied Y to the opt-in text wins over the local setting.
 * `mail.space.get` needs only the chat id, so the bridge never stores a phone.
 */
async function notificationSpace() {
  const consent = consents.newestConfirmed();
  if (consent) {
    try {
      return await mail.space.get(consent.spaceId);
    } catch {
      // The chat may be gone after a platform reset; fall back rather than
      // trapping every send.
    }
  }
  return phoneSpace();
}

const OPT_IN_TEXT =
  "Sykes here. Want me to text you the best trusted deals as I find them? " +
  "Reply Y to opt in, or N to skip.";
const OPT_IN_CONFIRMED =
  "Deal alerts on. I'll text the best trusted picks. Reply STOP to opt out.";
const OPT_IN_DECLINED = "No problem. I won't send deal alerts.";
const OPT_IN_RETRY = "Reply Y to get deal alerts, or N to skip.";
const OPT_OUT_CONFIRMED = "Deal alerts off. Text a product any time to keep shopping.";

/** SDK errors can echo the recipient; keep numbers out of the log. */
function redact(value: unknown): string {
  const text = value instanceof Error ? `${value.name}: ${value.message}` : String(value);
  return text.replace(/\+?\d[\d\s().-]{6,}\d/g, "[number]").slice(0, 300);
}

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "GET, POST, OPTIONS",
  "access-control-allow-headers": "content-type",
};

function json(body: unknown, status = 200): Response {
  return Response.json(body, { status, headers: CORS });
}

// A local-only endpoint the checkout sheet calls to text the pay link. It only
// ever sends to MY_PHONE or the space that texted this bridge — the request
// cannot choose a recipient.
const bridge = Bun.serve({
  hostname: "127.0.0.1",
  port: Number(process.env.BRIDGE_PORT ?? 8787),
  async fetch(request) {
    const url = new URL(request.url);
    if (request.method === "OPTIONS") {
      return new Response(null, { status: 204, headers: CORS });
    }
    if (url.pathname === "/health") {
      return json({
        ok: true,
        target: consents.newestConfirmed()
          ? "opted-in"
          : MY_PHONE
            ? "my-phone"
            : lastSpaceId
              ? "last-text"
              : "none",
      });
    }

    // Start a consent request: text the number and wait for a Y/N reply.
    if (url.pathname === "/opt-in" && request.method === "POST") {
      const body = (await request.json().catch(() => null)) as { phone?: string } | null;
      const phone = normalizePhone(body?.phone ?? "");
      if (!phone) {
        return json(
          { error: "Enter a phone number with its country code, e.g. +14155550123." },
          400,
        );
      }
      let consentId: string | undefined;
      try {
        const space = await mail.space.create(phone);

        // Already answered: do not text the number again on a page reload.
        const confirmed = consents.confirmedFor(space.id);
        if (confirmed) {
          return json({ request_id: confirmed.id, status: confirmed.status });
        }
        // A retry after a slow response reuses the request that is already
        // waiting for Y/N instead of expiring the text the shopper just got.
        const existing = consents.pendingFor(space.id);
        if (existing) {
          return json({ request_id: existing.id, status: existing.status });
        }

        const consent = consents.start(space.id);
        consentId = consent.id;
        await space.send(OPT_IN_TEXT);
        return json({ request_id: consent.id, status: consent.status });
      } catch (error) {
        // The opt-in text did not go out, so there is nothing to wait for.
        if (consentId) consents.abandon(consentId);
        console.error("[opt-in] could not open an iMessage chat:", redact(error));
        return json(
          {
            error:
              "Could not text that number. The bridge can only reach iMessage numbers — " +
              "check the number and try again.",
          },
          502,
        );
      }
    }

    const optIn = url.pathname.match(/^\/opt-in\/([\w-]+)$/);
    if (optIn && request.method === "GET") {
      const consent = consents.get(optIn[1] ?? "");
      if (!consent) return json({ error: "not found" }, 404);
      return json({ request_id: consent.id, status: consent.status });
    }

    // Only a consent that replied Y may be notified.
    const notify = url.pathname.match(/^\/notify\/([\w-]+)$/);
    if (notify && request.method === "POST") {
      const consent = consents.get(notify[1] ?? "");
      if (!consent) return json({ error: "not found" }, 404);
      if (consent.status !== "confirmed") {
        return json(
          { error: "Deal alerts are not confirmed. Reply Y to the opt-in text first." },
          409,
        );
      }
      const body = (await request.json().catch(() => null)) as { text?: string } | null;
      const text = (body?.text ?? "").trim();
      if (!text) return json({ error: "text is required" }, 400);
      try {
        const space = await mail.space.get(consent.spaceId);
        await space.send(text);
        return json({ ok: true });
      } catch {
        return json({ error: "Could not text the confirmed number." }, 502);
      }
    }

    if (url.pathname !== "/send" || request.method !== "POST") {
      return json({ error: "not found" }, 404);
    }
    const body = (await request.json().catch(() => null)) as { text?: string } | null;
    const text = (body?.text ?? "").trim();
    if (!text) {
      return json({ error: "text is required" }, 400);
    }
    try {
      const space = await notificationSpace();
      await space.send(text);
      return json({ ok: true });
    } catch (error) {
      return json(
        { error: error instanceof Error ? error.message : "send failed" },
        502,
      );
    }
  },
});

console.log(`[phone] bridge on http://127.0.0.1:${bridge.port}`);

// A pick goes out first, without asking questions: the agent's job is to
// answer, not to run a questionnaire. The refinements replace the old
// budget-first flow.
async function sendPick(space: { send: (text: string) => Promise<unknown> }, key: string, query: string) {
  await space.send(`Looking for “${query}”…`);
  const { session_id } = await createSession(query, key);
  await submitAnswers(session_id, [], true);
  const snapshot = await waitForResults(session_id);
  chats.set(key, { query });
  const body = snapshot
    ? formatResults(snapshot)
    : "That search ran out of time. Text a new search to try again.";
  await space.send(`${body}\n\n${MENU}`);
}

// `app.messages` is an async iterable. Each tick yields a `space` (the
// conversation) and an inbound `message`. Reply by awaiting `space.send(...)`.
for await (const [space, message] of app.messages) {
  if (message.content.type !== "text") continue;
  const text = message.content.text.trim();
  if (!text) continue;

  const key = String(space.id);
  // Any inbound text teaches the website where this shopper's phone is.
  rememberSpace(key);

  try {
    // A pending opt-in owns the next reply: Y confirms, N declines, anything
    // else gets the question again instead of being read as a product search.
    const pending = consents.pendingFor(key);
    if (pending) {
      const answer = parseConsentReply(text);
      if (answer === "yes") {
        consents.confirm(pending.id);
        await space.send(OPT_IN_CONFIRMED);
        continue;
      }
      if (answer === "no") {
        consents.decline(pending.id);
        await space.send(OPT_IN_DECLINED);
        continue;
      }
      await space.send(OPT_IN_RETRY);
      continue;
    }

    const confirmed = consents.confirmedFor(key);
    if (confirmed && isStopReply(text)) {
      consents.decline(confirmed.id);
      await space.send(OPT_OUT_CONFIRMED);
      continue;
    }

    const chat = chats.get(key);

    if (!chat) {
      const query = toQuery(text);
      if (!isSearchable(query)) {
        await space.send(
          'What are you shopping for? Text a product, e.g. "noise cancelling headphones under $300".',
        );
        continue;
      }
      await sendPick(space, key, query);
      continue;
    }

    if (chat.awaitingDetail) {
      await sendPick(space, key, `${chat.query} ${text}`);
      continue;
    }

    const lower = text.toLowerCase();
    if (lower.startsWith("new:")) {
      const query = toQuery(text.slice(4));
      if (!isSearchable(query)) {
        await space.send("What are you shopping for now?");
        continue;
      }
      await sendPick(space, key, query);
      continue;
    }
    if (lower === "3") {
      chat.awaitingDetail = true;
      await space.send("What should I change about the pick?");
      continue;
    }
    if (lower === "1") {
      await sendPick(space, key, `${chat.query} cheaper`);
      continue;
    }
    if (lower === "2") {
      await sendPick(space, key, `${chat.query} better quality`);
      continue;
    }
    await sendPick(space, key, `${chat.query} ${text}`);
  } catch (error) {
    console.error("sniff bridge failed", error);
    await space.send("The shopping agent is unreachable right now. Try again in a moment.");
  }
}
