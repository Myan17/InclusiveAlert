// __tests__/api.test.ts
import { buildHeaders, buildFormData } from "@/lib/api"

describe("buildHeaders", () => {
  it("returns JSON content-type and Authorization when token provided", () => {
    const h = buildHeaders("my-token")
    expect(h["Content-Type"]).toBe("application/json")
    expect(h["Authorization"]).toBe("Bearer my-token")
  })

  it("omits Authorization when no token", () => {
    const h = buildHeaders(null)
    expect(h["Authorization"]).toBeUndefined()
    expect(h["Content-Type"]).toBe("application/json")
  })
})

describe("buildFormData", () => {
  it("encodes key=value pairs as URL-encoded string", () => {
    const body = buildFormData({ username: "a@b.com", password: "pass" })
    expect(body).toBe("username=a%40b.com&password=pass")
  })
})
