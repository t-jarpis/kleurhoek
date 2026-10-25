import { BadRequestException } from "@nestjs/common";
import { z } from "zod";
import { PLATE_SOURCES, TEMPLATE_KINDS, TOPICS } from "./messaging.types";

/** Zod-schema's voor de API van Berichten (ADR 0037). */
const Lang = z.string().regex(/^[a-z]{2}$/);
export const I18n = (max: number) => z.record(Lang, z.string().max(max));
const Id = z.string().regex(/^[a-zA-Z0-9_-]{1,40}$/);
export const Topic = z.enum(TOPICS);
export const Market = z.string().regex(/^[a-z]{2}-[a-z]{2}$/i).transform((m) => m.toLowerCase());

export const Block = z.discriminatedUnion("type", [
  z.object({ id: Id, type: z.literal("heading"), text: I18n(160) }).strict(),
  z.object({ id: Id, type: z.literal("text"), text: I18n(4000) }).strict(),
  z.object({ id: Id, type: z.literal("button"), label: I18n(60), url: z.string().trim().max(500) }).strict(),
  z.object({
    id: Id, type: z.literal("plates"), source: z.enum(PLATE_SOURCES), collection: z.string().max(64).optional(), slugs: z.array(z.string().regex(/^[a-z0-9-]{1,64}$/)).max(30).optional(),
    max: z.number().int().min(1).max(12), columns: z.union([z.literal(2), z.literal(3)]),
  }).strict(),
  z.object({ id: Id, type: z.literal("divider") }).strict(),
]);

export const TemplateBody = z.object({
  name: z.string().trim().min(2).max(80), kind: z.enum(TEMPLATE_KINDS),
  subject: I18n(200), preheader: I18n(200), blocks: z.array(Block).max(40),
}).strict();

export const Trigger = z.discriminatedUnion("type", [
  z.object({ type: z.literal("subscribed") }).strict(),
  z.object({ type: z.literal("schedule"), weekday: z.number().int().min(0).max(6), hour: z.number().int().min(0).max(23) }).strict(),
  z.object({ type: z.literal("plates_published"), min: z.number().int().min(1).max(100) }).strict(),
  z.object({ type: z.literal("holiday_soon"), days: z.number().int().min(1).max(60) }).strict(),
]);
export const Step = z.discriminatedUnion("type", [
  z.object({ type: z.literal("filter"), topics: z.array(Topic).max(3).optional(), markets: z.array(Market).max(40).optional() }).strict(),
  z.object({ type: z.literal("require_plates"), min: z.number().int().min(1).max(100) }).strict(),
  z.object({ type: z.literal("wait"), hours: z.number().int().min(1).max(24 * 60) }).strict(),
  z.object({ type: z.literal("send"), template: z.string().regex(/^[a-z0-9-]{1,64}$/) }).strict(),
]);
export const WorkflowBody = z.object({ name: z.string().trim().min(2).max(80), enabled: z.boolean(), trigger: Trigger, steps: z.array(Step).min(1).max(20) }).strict();

export const Audience = z.object({ topics: z.array(Topic).min(1).max(3), markets: z.array(Market).max(40).nullable() }).strict();
export const CampaignBody = z.object({
  name: z.string().trim().min(2).max(120), template: z.string().regex(/^[a-z0-9-]{1,64}$/), audience: Audience,
  context: z.object({ holiday: z.string().max(64).optional(), plates: z.array(z.string().regex(/^[a-z0-9-]{1,64}$/)).max(30).optional() }).strict().optional(),
}).strict();

export const Subscribe = z.object({
  email: z.string().trim().email().max(254), market: Market, topics: z.array(Topic).min(1).max(3),
  adult: z.literal(true, { error: "Bevestig dat je 16 jaar of ouder bent" }),
  trap: z.string().max(200).optional(), elapsedMs: z.number().int().min(0).optional(),
}).strict();

export function parse<T>(schema: z.ZodType<T>, value: unknown): T {
  const r = schema.safeParse(value);
  if (!r.success) throw new BadRequestException(r.error.issues.map((i) => `${i.path.join(".") || "body"}: ${i.message}`).join("; "));
  return r.data;
}
