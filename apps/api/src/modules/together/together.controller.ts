import { BadRequestException, Body, Controller, Get, HttpCode, NotFoundException, Param, Post, Query, Res } from "@nestjs/common";
import type { FastifyReply } from "fastify";
import { z } from "zod";
import { RateLimit } from "../operations/rate-limit.guard";
import { CODE, TogetherService } from "./together.service";

const Client = z.string().regex(/^[a-z0-9]{6,16}$/);
const Hex = z.string().regex(/^#[0-9a-f]{6}$/i);
const Fill = z.string().max(64).regex(/^(#[0-9a-f]{6}|g:#[0-9a-f]{6}:#[0-9a-f]{6}|p:[a-z]{3,12}:#[0-9a-f]{6}:#[0-9a-f]{6})$/i);
const Id = z.string().regex(/^[a-z0-9]{6,16}:\d{1,7}$/);
/** Wat er in een kamer mag: vullen, een streek, iets ongedaan maken, of opnieuw beginnen. Niets anders. */
const Op = z.discriminatedUnion("t", [
  z.object({ t: z.literal("f"), id: Id, r: z.number().int().min(0).max(5000), v: Fill.nullable(), p: Fill.nullable().optional() }).strict(),
  z.object({ t: z.literal("s"), id: Id, r: z.number().int().min(0).max(5000), b: z.enum(["potlood", "stift", "waterverf", "airbrush", "gum"]), c: Hex, w: z.number().min(0.25).max(4), pen: z.boolean().optional(), pts: z.array(z.number().min(-100).max(3000)).max(6000) }).strict(),
  z.object({ t: z.literal("x"), id: Id, ref: Id }).strict(),
  z.object({ t: z.literal("c"), id: Id }).strict(),
]);
const Create = z.object({ market: z.string().regex(/^[a-z]{2}-[a-z]{2}$/), slug: z.string().regex(/^[a-z0-9-]{1,64}$/), version: z.number().int().min(1).max(999999) }).strict();
const Send = z.object({ client: Client, ops: z.array(Op).min(1).max(40) }).strict();

const WAIT_MS = 20_000;
const STEP_MS = 400;
const sleep = (ms: number) => new Promise((r) => setTimeout(r, ms));

/** Samen kleuren (ADR 0060). Alleen via de website te bereiken; niets wordt langer bewaard dan nodig. */
@Controller("v1/together/rooms")
@RateLimit("together")
export class TogetherController {
  constructor(private readonly together: TogetherService) {}

  private async room(code: string) {
    const c = code.toUpperCase();
    const room = CODE.test(c) ? await this.together.find(c) : null;
    if (!room) throw new NotFoundException("Onbekende of verlopen code");
    return room;
  }

  @Post()
  @RateLimit("together-create")
  async create(@Body() body: unknown, @Res({ passthrough: true }) res: FastifyReply) {
    const r = Create.safeParse(body);
    if (!r.success) throw new BadRequestException("Ongeldige plaat");
    res.header("Cache-Control", "no-store");
    const room = await this.together.create(r.data.market, r.data.slug, r.data.version);
    return { code: room.code };
  }

  @Get(":code")
  async get(@Param("code") code: string, @Res({ passthrough: true }) res: FastifyReply) {
    const room = await this.room(code);
    res.header("Cache-Control", "no-store");
    return { code: room.code, market: room.market, slug: room.slug, version: room.version };
  }

  @Post(":code/ops")
  @HttpCode(200)
  async send(@Param("code") code: string, @Body() body: unknown, @Res({ passthrough: true }) res: FastifyReply) {
    const r = Send.safeParse(body);
    if (!r.success || JSON.stringify(r.data).length > 200_000) throw new BadRequestException("Ongeldige handelingen");
    const room = await this.room(code);
    res.header("Cache-Control", "no-store");
    if (!(await this.together.add(room, r.data.client, r.data.ops))) throw new BadRequestException("Deze plaat is vol");
    return { ok: true };
  }

  /** Wat er nieuw is. Wacht tot er iets is, of hooguit 20 seconden (long polling: werkt achter elke proxy). */
  @Get(":code/ops")
  async poll(@Param("code") code: string, @Query("client") client: string | undefined, @Query("after") after: string | undefined, @Query("wait") wait: string | undefined, @Res({ passthrough: true }) res: FastifyReply) {
    if (!Client.safeParse(client).success || !/^\d{1,15}$/.test(after ?? "0")) throw new BadRequestException("Ongeldig verzoek");
    const room = await this.room(code);
    res.header("Cache-Control", "no-store");
    const from = Number(after ?? 0);
    const until = Date.now() + (wait === "0" ? 0 : WAIT_MS);
    for (;;) {
      const r = await this.together.since(room, client!, from);
      if (r.ops.length || Date.now() >= until) return r;
      await sleep(STEP_MS);
    }
  }
}
