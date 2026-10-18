// Bridges a text message to the Sniff backend: create a session, answer the
// clarifying questions, wait for the investigation, and format the reply.

export type QuestionOption = { id: string; label: string };

export type Question = {
  id: string;
  prompt: string;
  options: QuestionOption[];
  allow_free_text: boolean;
};

export type Listing = {
  id: string;
  title: string;
  price_cents: number;
  merchant_name: string;
  merchant_domain: string;
  product_url: string;
};

export type Recommendation = {
  recommended_listing_id?: string;
  median_trusted_cents?: number;
  savings_cents?: number;
  reason?: string;
  no_trusted_option?: boolean;
  narrative?: string;
};

export type Snapshot = {
  session_id: string;
  stage: string;
  listings: Listing[];
  recommendation: Recommendation;
  stats?: { listings?: number; trusted?: number; caution?: number; danger?: number };
};

export type Answer = { question_id: string; option_id?: string; text?: string };

// `localhost` rather than 127.0.0.1: the backend binds to whatever the dev
// script chose, and the browser uses the same host.
export function backendUrl(): string {
  return (process.env.BACKEND_URL ?? "http://localhost:8000").replace(/\/$/, "");
}

async function json<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${backendUrl()}${path}`, {
    ...init,
    headers: { "content-type": "application/json", ...(init?.headers ?? {}) },
  });
  if (!response.ok) {
    throw new Error(`${path} returned ${response.status}`);
  }
  return (await response.json()) as T;
}

export async function createSession(
  query: string,
  clientId: string,
): Promise<{ session_id: string; questions: Question[] }> {
  return json("/api/sessions", {
    method: "POST",
    body: JSON.stringify({ query, client_id: clientId }),
  });
}

export async function submitAnswers(
  sessionId: string,
  answers: Answer[],
  skipRemaining = true,
): Promise<void> {
  await json(`/api/sessions/${sessionId}/answers`, {
    method: "POST",
    body: JSON.stringify({ answers, skip_remaining: skipRemaining }),
  });
}

export async function getSession(sessionId: string): Promise<Snapshot> {
  return json(`/api/sessions/${sessionId}`);
}

const DONE = new Set(["ready", "no_trusted_option", "failed"]);

export async function waitForResults(
  sessionId: string,
  timeoutMs = 40_000,
): Promise<Snapshot | null> {
  const deadline = Date.now() + timeoutMs;
  while (Date.now() < deadline) {
    const snapshot = await getSession(sessionId);
    if (DONE.has(snapshot.stage)) return snapshot;
    await Bun.sleep(1000);
  }
  return null;
}

/** "2", "$300-$600", or "between 300 and 600" → the matching option. */
export function parseChoice(options: QuestionOption[], input: string): QuestionOption | null {
  const text = input.trim().toLowerCase();
  if (!text) return null;
  const index = Number.parseInt(text, 10);
  if (!Number.isNaN(index) && String(index) === text && index >= 1 && index <= options.length) {
    return options[index - 1]!;
  }
  return (
    options.find((option) => option.label.toLowerCase() === text) ??
    options.find((option) => text.includes(option.label.toLowerCase())) ??
    null
  );
}

// Polite framing turns a text into a bad Google query ("hey can you find me
// noise cancelling headphones" should search for the headphones, not the
// sentence). Strip the framing, keep the noun phrase.
const POLITE =
  /^(?:hey|hi|hello|yo|ok|okay|please|pls|can you|could you|would you|i need|i want|i'd like|i'm looking for|im looking for|looking for|find me|show me|help me find|search for|get me)\b[\s,:-]*/i;

const GREETINGS = new Set([
  "",
  "hi",
  "hey",
  "hello",
  "yo",
  "test",
  "testing",
  "ok",
  "okay",
  "thanks",
  "thank you",
]);

export function toQuery(text: string): string {
  let query = text.trim().replace(/\s+/g, " ");
  for (let pass = 0; pass < 6; pass += 1) {
    const next = query.replace(POLITE, "").trim();
    if (next === query) break;
    query = next;
  }
  return query.replace(/[.!?]+$/, "").trim();
}

export function isSearchable(query: string): boolean {
  return query.length >= 3 && !GREETINGS.has(query.toLowerCase());
}

export const MENU = [
  "Not the one? Reply:",
  "1. Cheaper",
  "2. Better quality",
  "3. Something else — tell me what to change",
  'or text "new: <product>" for a different search.',
].join("\n");

export function formatQuestion(question: Question): string {
  const lines = [question.prompt, ""];
  question.options.forEach((option, index) => lines.push(`${index + 1}. ${option.label}`));
  lines.push("", "Reply with a number.");
  return lines.join("\n");
}

export function formatMoney(cents: number): string {
  return `$${(cents / 100).toFixed(2).replace(/\.00$/, "")}`;
}

export function formatResults(snapshot: Snapshot): string {
  if (snapshot.stage === "failed") {
    return "Live search is taking too long. We did not substitute unrelated products — text a new search to try again.";
  }
  const recommendation = snapshot.recommendation ?? {};
  if (recommendation.no_trusted_option) {
    return "Nothing in that search passed the trust checks, so I will not recommend a purchase. Try a different search or budget.";
  }
  const pick = snapshot.listings?.find(
    (listing) => listing.id === recommendation.recommended_listing_id,
  );
  if (!pick) {
    return "The investigation finished but produced no trusted pick. Try a different search.";
  }
  const stats = snapshot.stats ?? {};
  const lines = [
    `Best trusted pick: ${pick.title}`,
    `${formatMoney(pick.price_cents)} at ${pick.merchant_domain || pick.merchant_name}`,
  ];
  const reason = recommendation.reason || recommendation.narrative;
  if (reason) lines.push("", reason);
  if (pick.product_url) lines.push("", pick.product_url);
  lines.push(
    "",
    `${stats.trusted ?? 0} trusted · ${stats.caution ?? 0} caution · ${stats.danger ?? 0} flagged`,
  );
  return lines.join("\n");
}
