"use client";
import Link from "next/link";
import { useEffect, useState, type CSSProperties } from "react";
import { messages } from "@/i18n/nl";
import type { Door } from "@/lib/advent";
import { link } from "@/lib/sites";

const COLORS = ["rood", "groen", "blauw", "paars", "oranje", "teal", "roze", "amber"];
/** Sinterklaaskalender (ADR 0065): rood, goud en paars, de kleuren van Sinterklaas. */
const SINT_COLORS = ["rood", "amber", "paars"];

/**
 * De deurtjes (ADR 0058). Welke al open zijn, onthoudt alleen dit apparaat. Een deurtje dat aan de beurt is
 * gaat open met een tik; daarna leidt het naar de plaat. Ook voor de Sinterklaaskalender (ADR 0065): dan met
 * `kind="sint"`, een ander aantal deurtjes en per deurtje het label voor als hij nog dicht is.
 */
export function AdventCalendar({ doors, order, open, today, year, base, market, kind = "advent", total = 24, lockedLabels }: {
  doors: Door[]; order: number[]; open: number; today: number | null; year: number; base: string; market: string;
  kind?: "advent" | "sint"; total?: number; lockedLabels?: string[];
}) {
  const key = (y: number) => `kh:${kind === "sint" ? "sinterklaaskalender" : "aftelkalender"}:${y}`;
  const colors = kind === "sint" ? SINT_COLORS : COLORS;
  const t = messages(market);
  const [opened, setOpened] = useState<number[]>([]);
  // Buiten december (archief) staan alle deurtjes open.
  const archive = open === total && today === null;
  useEffect(() => {
    try { const v = JSON.parse(localStorage.getItem(key(year)) ?? "[]"); if (Array.isArray(v)) setOpened(v.filter((n) => typeof n === "number")); } catch { /* geen opslag */ }
  }, [year]);
  const openDoor = (d: number) => {
    const next = [...new Set([...opened, d])];
    setOpened(next);
    try { localStorage.setItem(key(year), JSON.stringify(next)); } catch { /* geen opslag */ }
  };
  const byDay = new Map(doors.map((d) => [d.day, d]));
  return (
    <ol className="kh-advent">
      {order.map((day, i) => {
        const door = byDay.get(day);
        const allowed = day <= open;
        const isOpen = allowed && (archive || opened.includes(day));
        return (
          <li key={day} className="kh-door" data-open={isOpen ? "" : undefined} data-locked={allowed ? undefined : ""} data-today={today === day ? "" : undefined}>
            {allowed && door ? (
              <Link className="kh-door-inside" href={link(base, `/platen/${door.plate.slug}`)} tabIndex={isOpen ? 0 : -1} aria-hidden={isOpen ? undefined : true}>
                <b>{day}</b>
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img src={door.plate.svg} alt="" loading="lazy" />
                <span>{door.plate.name}</span>
              </Link>
            ) : <div className="kh-door-inside" aria-hidden="true" />}
            <button type="button" className="kh-door-front" style={{ "--door": `var(--krijt-${colors[i % colors.length]}-sterk)` } as CSSProperties}
              aria-disabled={allowed ? undefined : true} aria-label={allowed ? t.advent.openDoor(day) : lockedLabels?.[day - 1] ?? t.advent.locked(day)}
              tabIndex={isOpen ? -1 : 0} onClick={() => allowed && openDoor(day)}>{day}</button>
          </li>
        );
      })}
    </ol>
  );
}
