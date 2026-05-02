import { decodeToken } from "@/store/authStore"

describe("decodeToken", () => {
  it("returns null for null input", () => {
    expect(decodeToken(null)).toBeNull()
  })

  it("returns null for malformed token", () => {
    expect(decodeToken("not.a.token")).toBeNull()
  })

  it("decodes a valid JWT payload", () => {
    const payload = Buffer.from(JSON.stringify({ sub: "a@b.com", role: "victim" }))
      .toString("base64url")
    const token = `header.${payload}.sig`
    const result = decodeToken(token)
    expect(result?.sub).toBe("a@b.com")
    expect(result?.role).toBe("victim")
  })
})
