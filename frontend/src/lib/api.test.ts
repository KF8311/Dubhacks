import { createCheckout, confirmCheckout, getReceipt } from "./api.ts"

type Call = { path: string; method: string; body: unknown }

const checkoutPayload = {
  checkout_id: "chk_1",
  stage: "awaiting_passkey",
  amount_cents: 17999,
  currency: "USD",
  merchant: { name: "Target", domain: "target.com" },
  mandate: {
    id: "mnd_1",
    max_amount_cents: 30000,
    merchant_domain: "target.com",
    expires_at: "2026-10-17T18:10:00Z",
    single_use: true,
  },
  trust_snapshot: { score: 92, verdict: "trusted", confidence: 1 },
  passkey_challenge: { challenge: "abc", rp_id: "sniff.vercel.app" },
  sandbox_label: "Sandbox — simulated Visa Intelligent Commerce flow.",
  expires_at: "2026-10-17T18:05:00Z",
}

const confirmPayload = {
  checkout_id: "chk_1",
  status: "captured",
  transaction: { id: "txn_1", status: "captured", token_last4: "4242" },
  receipt_id: "rcp_1",
  receipt_url: "/r/shr_1",
  sandbox_label: "Sandbox — simulated Visa Intelligent Commerce flow.",
}

const receiptPayload = {
  id: "rcp_1",
  share_id: "shr_1",
  checkout_id: "chk_1",
  transaction_id: "txn_1",
  token_last4: "4242",
  amount_cents: 17999,
}

function stubFetch(...responses: Array<{ status?: number; body: unknown }>) {
  const calls: Call[] = []
  let index = 0
  globalThis.fetch = (async (input: RequestInfo | URL, init?: RequestInit) => {
    calls.push({
      path: String(input),
      method: init?.method ?? "GET",
      body: init?.body ? JSON.parse(String(init.body)) : null,
    })
    const next = responses[index++]
    return {
      ok: (next.status ?? 200) < 400,
      status: next.status ?? 200,
      statusText: "",
      json: async () => next.body,
    } as Response
  }) as typeof fetch
  return calls
}

beforeEach(() => {
  window.history.replaceState({}, "", "/")
})

test("createCheckout posts the contracted mandate and maps checkout_id to id", async () => {
  const calls = stubFetch({ body: checkoutPayload })

  const created = await createCheckout({
    session_id: "ses_1",
    listing_id: "lst_1",
    max_amount_cents: 30000,
  })

  expect(calls).toHaveLength(1)
  expect(calls[0].path).toMatch(/\/api\/checkout$/)
  expect(calls[0].body).toEqual({
    session_id: "ses_1",
    listing_id: "lst_1",
    mandate: { max_amount_cents: 30000, currency: "USD", expires_in_seconds: 600 },
  })
  expect(created.id).toBe("chk_1")
  expect(created.mandate.merchant_name).toBe("Target")
  expect(created.mandate.merchant_domain).toBe("target.com")
})

test("confirmCheckout sends a full passkey assertion and an idempotency key", async () => {
  const calls = stubFetch({ body: confirmPayload }, { body: receiptPayload })

  await confirmCheckout("chk_1", { client_data: "mock" })

  expect(calls[0].path).toMatch(/\/api\/checkout\/chk_1\/confirm$/)
  expect(calls[0].body).toEqual({
    passkey_assertion: { credential_id: "mock", client_data: "mock" },
    idempotency_key: "chk_1:confirm",
  })
})

test("confirmCheckout follows receipt_url to the public receipt", async () => {
  const calls = stubFetch({ body: confirmPayload }, { body: receiptPayload })

  const receipt = await confirmCheckout("chk_1", { client_data: "mock" })

  expect(calls[1].path).toMatch(/\/api\/public\/receipts\/shr_1$/)
  expect(receipt.share_id).toBe("shr_1")
  expect(receipt.token_last4).toBe("4242")
})

test("getReceipt reads the public share route", async () => {
  const calls = stubFetch({ body: receiptPayload })

  await getReceipt("shr_1")

  expect(calls[0].path).toMatch(/\/api\/public\/receipts\/shr_1$/)
})

test("a server refusal surfaces its PayabilityCode", async () => {
  stubFetch({
    status: 409,
    body: {
      error: {
        code: "MERCHANT_NOT_TRUSTED",
        message: "This merchant is not trusted.",
        details: { verdict: "danger" },
      },
    },
  })

  await expect(
    createCheckout({ session_id: "ses_1", listing_id: "lst_vln", max_amount_cents: 30000 }),
  ).rejects.toMatchObject({
    code: "MERCHANT_NOT_TRUSTED",
    message: "This merchant is not trusted.",
  })
})

test("a refused payment is not silently retried", async () => {
  const calls = stubFetch({
    status: 402,
    body: { error: { code: "PAYMENT_DECLINED", message: "Payment was declined." } },
  })

  await expect(confirmCheckout("chk_1", { client_data: "fail" })).rejects.toMatchObject({
    code: "PAYMENT_DECLINED",
  })
  expect(calls).toHaveLength(1)
})
