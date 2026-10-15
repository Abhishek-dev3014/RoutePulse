import { afterEach, describe, expect, it, vi } from "vitest";
import { api, clock, scenarioSchema } from "../lib/api";
afterEach(() => vi.unstubAllGlobals());
describe("API contract and presentation", () => {
  it("formats campus-local times across the hour", () => {
    expect(clock(0)).toBe("08:00");
    expect(clock(65)).toBe("09:05");
    expect(clock(120)).toBe("10:00");
  });
  it("surfaces API error messages", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: false,
        status: 422,
        json: async () => ({
          error: { message: "Invalid disruption interval" },
        }),
      }),
    );
    await expect(api("simulations", {})).rejects.toThrow(
      "Invalid disruption interval",
    );
  });
  it("returns real response values without substitutions", async () => {
    vi.stubGlobal(
      "fetch",
      vi
        .fn()
        .mockResolvedValue({ ok: true, json: async () => ({ served: 0 }) }),
    );
    expect(await api("dashboard")).toEqual({ served: 0 });
  });
  it("rejects a malformed scenario payload", () => {
    expect(scenarioSchema.safeParse({ id: "rush" }).success).toBe(false);
  });
});
