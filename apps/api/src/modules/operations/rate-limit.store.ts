/** Telt verzoeken per sleutel binnen een tijdvenster (fixed window). */
export interface RateLimitStore {
  hit(key: string, windowMs: number, now?: number): Promise<{ count: number; resetAt: number }>;
}
export const RATE_LIMIT_STORE = Symbol("RATE_LIMIT_STORE");

/**
 * Geheugenstore voor lokaal, tests en één replica. Met meerdere replica's in productie
 * komt hier een Redis-store (INCR + PEXPIRE) achter dezelfde interface.
 */
export class MemoryRateLimitStore implements RateLimitStore {
  private readonly buckets = new Map<string, { count: number; resetAt: number }>();
  private lastSweep = 0;

  async hit(key: string, windowMs: number, now = Date.now()) {
    if (now - this.lastSweep > 60_000) this.sweep(now);
    const b = this.buckets.get(key);
    if (!b || b.resetAt <= now) {
      const fresh = { count: 1, resetAt: now + windowMs };
      this.buckets.set(key, fresh);
      return fresh;
    }
    b.count += 1;
    return b;
  }

  private sweep(now: number) {
    this.lastSweep = now;
    for (const [k, b] of this.buckets) if (b.resetAt <= now) this.buckets.delete(k);
  }
}
