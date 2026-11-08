import { Controller, Get, UseGuards } from "@nestjs/common";
import { AdminGuard, RequirePermission } from "../identity/admin.guard";
import { CapacityService } from "./capacity.service";
import { RateLimit } from "./rate-limit.guard";

/** Capaciteit van de servers (ADR 0092): alleen lezen. Schalen gebeurt in Terraform, niet hier. */
@Controller("v1/admin/capacity")
@UseGuards(AdminGuard)
@RateLimit("admin")
export class AdminCapacityController {
  constructor(private readonly capacity: CapacityService) {}

  @Get()
  @RequirePermission("operations.capacity.read")
  overview() {
    return this.capacity.overview();
  }
}
