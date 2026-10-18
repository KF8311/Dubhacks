import { afterEach, describe, expect, test, vi } from "vitest"
import { apiBase } from "./apiBase.ts"

afterEach(() => {
  vi.unstubAllEnvs()
})

describe("apiBase", () => {
  test("uses same-origin /api when VITE_API_BASE_URL is unset in a production build", () => {
    expect(apiBase({ DEV: false })).toBe("")
  })

  test("falls back to Uvicorn on :8000 in dev when unset", () => {
    expect(apiBase({ DEV: true })).toBe("http://localhost:8000")
  })

  test("uses the page's hostname so a phone reaches the same machine", () => {
    expect(apiBase({ DEV: true }, "192.168.1.20")).toBe("http://192.168.1.20:8000")
  })

  test("keeps an explicit host for local Uvicorn or Fly", () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000")
    expect(apiBase()).toBe("http://localhost:8000")
  })

  test("strips a trailing slash so /api paths do not double", () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://sniff-visa-dubhacks.fly.dev/")
    expect(apiBase()).toBe("https://sniff-visa-dubhacks.fly.dev")
  })
})
