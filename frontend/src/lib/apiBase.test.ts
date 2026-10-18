import { afterEach, describe, expect, test, vi } from "vitest"
import { apiBase } from "./apiBase.ts"

afterEach(() => {
  vi.unstubAllEnvs()
})

describe("apiBase", () => {
  test("uses same-origin /api when VITE_API_BASE_URL is unset", () => {
    vi.stubEnv("VITE_API_BASE_URL", "")
    expect(apiBase("localhost")).toBe("")
  })

  test("keeps an explicit host for local Uvicorn or Fly", () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000")
    expect(apiBase("localhost")).toBe("http://localhost:8000")
  })

  test("strips a trailing slash so /api paths do not double", () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://sniff-visa-dubhacks.fly.dev/")
    expect(apiBase("localhost")).toBe("https://sniff-visa-dubhacks.fly.dev")
  })

  test("ignores a baked localhost API when the page is on the public host", () => {
    vi.stubEnv("VITE_API_BASE_URL", "http://localhost:8000")
    expect(apiBase("sykes.select")).toBe("")
  })

  test("ignores a baked Fly URL when the page is on sykes.select", () => {
    vi.stubEnv("VITE_API_BASE_URL", "https://sniff-visa-dubhacks.fly.dev")
    expect(apiBase("sykes.select")).toBe("")
  })
})
