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
const MY_PHONE = (process.env.MY_PHONE ?? "").trim();
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

const CORS = {
  "access-control-allow-origin": "*",
  "access-control-allow-methods": "POST, OPTIONS",
  "access-control-allow-headers": "content-type",
};

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
      return Response.json(
        { ok: true, target: MY_PHONE ? "my-phone" : lastSpaceId ? "last-text" : "none" },
        { headers: CORS },
      );
    }
    if (url.pathname !== "/send" || request.method !== "POST") {
      return Response.json({ error: "not found" }, { status: 404, headers: CORS });
    }
    const body = (await request.json().catch(() => null)) as { text?: string } | null;
    const text = (body?.text ?? "").trim();
    if (!text) {
      return Response.json({ error: "text is required" }, { status: 400, headers: CORS });
    }
    try {
      const space = await phoneSpace();
      await space.send(text);
      return Response.json({ ok: true }, { headers: CORS });
    } catch (error) {
      return Response.json(
        { error: error instanceof Error ? error.message : "send failed" },
        { status: 502, headers: CORS },
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
