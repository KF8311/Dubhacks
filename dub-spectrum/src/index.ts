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

type Chat = { query: string; awaitingDetail?: boolean };

// One conversation per space. A first text is a search; every later text
// refines the last search unless it starts with "new:".
const chats = new Map<string, Chat>();

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
