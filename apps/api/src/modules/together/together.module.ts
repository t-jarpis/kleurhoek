import { Module } from "@nestjs/common";
import { TogetherController } from "./together.controller";
import { TogetherScheduler } from "./together.scheduler";
import { TogetherService } from "./together.service";

/** Domein Samen kleuren (ADR 0060): kamers met een code, en wat er in die kamer gekleurd wordt. */
@Module({ controllers: [TogetherController], providers: [TogetherService, TogetherScheduler], exports: [TogetherService] })
export class TogetherModule {}
