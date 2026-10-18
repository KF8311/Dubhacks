import { describe, expect, test } from "vitest"
import { apiBase } from "./apiBase.ts"

describe("apiBase", () => {
  test("uses same-origin /api when VITE_API_BASE_URL is unset in a production build", () => {
    expect(apiBase("localhost", { DEV: false })).toBe("")
  })

  test("falls back to Uvicorn on :8000 in dev when unset", () => {
    expect(apiBase("localhost", { DEV: true })).toBe("http://localhost:8000")
  })

  test("keeps an explicit host for local Uvicorn or Fly", () => {
    expect(apiBase("localhost", { VITE_API_BASE_URL: "http://localhost:8000" })).toBe(
      "http://localhost:8000",
    )
  })

  test("strips a trailing slash so /api paths do not double", () => {
    expect(apiBase("localhost", { VITE_API_BASE_URL: "https://sniff-visa-dubhacks.fly.dev/" })).toBe(
      "https://sniff-visa-dubhacks.fly.dev",
    )
  })

  test("ignores a baked localhost API when the page is on the public host", () => {
    expect(apiBase("sykes.select", { VITE_API_BASE_URL: "http://localhost:8000" })).toBe("")
  })

  test("ignores a baked Fly URL when the page is on sykes.select", () => {
    expect(
      apiBase("sykes.select", { VITE_API_BASE_URL: "https://sniff-visa-dubhacks.fly.dev" }),
    ).toBe("")
  })
})
