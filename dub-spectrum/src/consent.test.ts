import { describe, expect, test } from "bun:test";
import { readFileSync } from "node:fs";
import { tmpdir } from "node:os";
import { join } from "node:path";
import { randomUUID } from "node:crypto";

import {
  ConsentStore,
  PENDING_TTL_MS,
  isStopReply,
  normalizePhone,
  parseConsentReply,
} from "./consent";

function tempPath(): string {
  return join(tmpdir(), `sykes-consent-${randomUUID()}.json`);
}

describe("normalizePhone", () => {
  test("accepts E.164", () => {
    expect(normalizePhone("+14155550123")).toBe("+14155550123");
    expect(normalizePhone(" +44 20 7946 0958 ")).toBe("+442079460958");
  });

  test("adds +1 to US 10 and 11 digit forms", () => {
    expect(normalizePhone("4155550123")).toBe("+14155550123");
    expect(normalizePhone("(415) 555-0123")).toBe("+14155550123");
    expect(normalizePhone("1 415 555 0123")).toBe("+14155550123");
  });

  test("rejects something that is not a callable number", () => {
    expect(normalizePhone("")).toBeNull();
    expect(normalizePhone("555-0123")).toBeNull();
    expect(normalizePhone("call me maybe")).toBeNull();
    expect(normalizePhone("+1234567")).toBeNull();
    expect(normalizePhone("+1415555012345678")).toBeNull();
  });
});

describe("parseConsentReply", () => {
  test("reads yes and no", () => {
    expect(parseConsentReply("Y")).toBe("yes");
    expect(parseConsentReply(" yes. ")).toBe("yes");
    expect(parseConsentReply("nope")).toBe("no");
    expect(parseConsentReply("N!")).toBe("no");
  });

  test("does not mistake a product for an answer", () => {
    expect(parseConsentReply("noise cancelling headphones")).toBeNull();
    expect(parseConsentReply("yes please find pens")).toBeNull();
  });

  test("stop is a no", () => {
    expect(parseConsentReply("stop")).toBe("no");
  });
});

describe("isStopReply", () => {
  test("matches the revocation words only", () => {
    expect(isStopReply("STOP")).toBe(true);
    expect(isStopReply("unsubscribe")).toBe(true);
    expect(isStopReply("stop alerts")).toBe(true);
    expect(isStopReply("stop sending me pens")).toBe(false);
  });
});

describe("ConsentStore", () => {
  test("a pending request can be confirmed", () => {
    const store = new ConsentStore(tempPath());
    const request = store.start("space-1", 1_000);

    expect(store.get(request.id, 1_001)?.status).toBe("pending");
    expect(store.pendingFor("space-1", 1_001)?.id).toBe(request.id);

    expect(store.confirm(request.id, 1_002)?.status).toBe("confirmed");
    expect(store.pendingFor("space-1", 1_002)).toBeUndefined();
    expect(store.confirmedFor("space-1")?.id).toBe(request.id);
    expect(store.newestConfirmed()?.id).toBe(request.id);
  });

  test("a declined request never becomes confirmed", () => {
    const store = new ConsentStore(tempPath());
    const request = store.start("space-1", 1_000);

    store.decline(request.id, 1_001);

    expect(store.get(request.id, 1_002)?.status).toBe("declined");
    expect(store.confirm(request.id, 1_003)).toBeUndefined();
    expect(store.newestConfirmed()).toBeUndefined();
  });

  test("a pending request expires", () => {
    const store = new ConsentStore(tempPath());
    const request = store.start("space-1", 1_000);

    expect(store.get(request.id, 1_000 + PENDING_TTL_MS + 1)?.status).toBe("expired");
    expect(store.confirm(request.id, 1_000 + PENDING_TTL_MS + 2)).toBeUndefined();
  });

  test("a retry for the same chat reuses the pending request", () => {
    const store = new ConsentStore(tempPath());
    const first = store.start("space-1", 1_000);
    const second = store.start("space-1", 1_001);

    expect(second.id).toBe(first.id);
    expect(store.get(first.id, 1_002)?.status).toBe("pending");
  });

  test("space ids that differ only in prefix still match the same chat", () => {
    const store = new ConsentStore(tempPath());
    const request = store.start("any;-;+14155550123", 1_000);

    expect(store.pendingFor("imessage;-;+14155550123", 1_001)?.id).toBe(request.id);
    store.confirm(request.id, 1_002);
    expect(store.confirmedFor("imessage;-;+14155550123")?.id).toBe(request.id);
  });

  test("an abandoned request is forgotten", () => {
    const store = new ConsentStore(tempPath());
    const request = store.start("space-1", 1_000);

    store.abandon(request.id);

    expect(store.get(request.id, 1_001)).toBeUndefined();
    expect(store.pendingFor("space-1", 1_001)).toBeUndefined();
  });

  test("confirmed consent survives a restart, and no phone number is written", () => {
    const path = tempPath();
    const first = new ConsentStore(path);
    const request = first.start("space-42", 1_000);
    first.confirm(request.id, 1_001);

    const second = new ConsentStore(path);
    expect(second.confirmedFor("space-42")?.id).toBe(request.id);

    const raw = readFileSync(path, "utf8");
    expect(raw).toContain("space-42");
    expect(raw).not.toMatch(/\+?\d{8,15}/);
  });
});
