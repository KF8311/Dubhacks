import { readFileSync, writeFileSync } from "node:fs";
import { randomUUID } from "node:crypto";

/**
 * Deal-alert consent.
 *
 * A shopper enters a number on the site; the bridge texts that number and asks
 * for a Y/N reply. Only a confirmed conversation may be notified. The phone
 * number itself is never written to disk or to the website's storage — the
 * bridge keeps the Spectrum space id, which is enough to send later.
 */

export type ConsentStatus = "pending" | "confirmed" | "declined" | "expired";

export type ConsentRequest = {
  id: string;
  spaceId: string;
  status: ConsentStatus;
  createdAt: number;
};

export const PENDING_TTL_MS = 15 * 60 * 1000;

const YES = new Set(["y", "yes", "yeah", "yep", "sure", "ok", "okay"]);
const NO = new Set(["n", "no", "nope", "nah", "stop"]);
const STOP = /^(stop|stop alerts|unsubscribe)$/i;

/** E.164 for the bridge. US 10/11-digit forms get +1; anything else needs +. */
export function normalizePhone(raw: string): string | null {
  const cleaned = raw.trim().replace(/[\s().-]/g, "");
  if (/^\+\d{8,15}$/.test(cleaned)) return cleaned;
  if (/^\d{10}$/.test(cleaned)) return `+1${cleaned}`;
  if (/^1\d{10}$/.test(cleaned)) return `+${cleaned}`;
  return null;
}

export function parseConsentReply(text: string): "yes" | "no" | null {
  const answer = text.trim().toLowerCase().replace(/[.!]+$/, "");
  if (YES.has(answer)) return "yes";
  if (NO.has(answer)) return "no";
  return null;
}

export function isStopReply(text: string): boolean {
  return STOP.test(text.trim());
}

type Persisted = { requests?: ConsentRequest[] };

export class ConsentStore {
  private readonly requests = new Map<string, ConsentRequest>();
  private readonly path: string;

  constructor(path: string) {
    this.path = path;
    try {
      const data = JSON.parse(readFileSync(path, "utf8")) as Persisted;
      for (const request of data.requests ?? []) {
        if (!request?.id || !request?.spaceId || !request?.status) continue;
        this.requests.set(request.id, {
          id: request.id,
          spaceId: request.spaceId,
          status: request.status,
          createdAt: Number(request.createdAt) || 0,
        });
      }
    } catch {
      // First run, or the file is unreadable: start empty.
    }
  }

  start(spaceId: string, now = Date.now()): ConsentRequest {
    for (const request of this.requests.values()) {
      if (request.spaceId === spaceId && request.status === "pending") {
        request.status = "expired";
      }
    }
    const request: ConsentRequest = {
      id: randomUUID(),
      spaceId,
      status: "pending",
      createdAt: now,
    };
    this.requests.set(request.id, request);
    this.persist();
    return request;
  }

  get(id: string, now = Date.now()): ConsentRequest | undefined {
    const request = this.requests.get(id);
    if (!request) return undefined;
    this.expire(request, now);
    return request;
  }

  pendingFor(spaceId: string, now = Date.now()): ConsentRequest | undefined {
    for (const request of this.requests.values()) {
      if (request.spaceId !== spaceId) continue;
      this.expire(request, now);
      if (request.status === "pending") return request;
    }
    return undefined;
  }

  confirmedFor(spaceId: string): ConsentRequest | undefined {
    return [...this.requests.values()].find(
      (request) => request.spaceId === spaceId && request.status === "confirmed",
    );
  }

  newestConfirmed(): ConsentRequest | undefined {
    return [...this.requests.values()]
      .filter((request) => request.status === "confirmed")
      .sort((a, b) => b.createdAt - a.createdAt)[0];
  }

  confirm(id: string, now = Date.now()): ConsentRequest | undefined {
    const request = this.get(id, now);
    if (!request || request.status !== "pending") return undefined;
    request.status = "confirmed";
    this.persist();
    return request;
  }

  decline(id: string, now = Date.now()): ConsentRequest | undefined {
    const request = this.get(id, now);
    if (!request) return undefined;
    request.status = "declined";
    this.persist();
    return request;
  }

  private expire(request: ConsentRequest, now: number): void {
    if (request.status === "pending" && now - request.createdAt > PENDING_TTL_MS) {
      request.status = "expired";
      this.persist();
    }
  }

  private persist(): void {
    try {
      writeFileSync(
        this.path,
        JSON.stringify({ requests: [...this.requests.values()] }, null, 2),
        { mode: 0o600 },
      );
    } catch {
      // A read-only checkout can still honor consent while the process lives.
    }
  }
}
