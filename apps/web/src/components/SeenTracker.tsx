"use client";
import { useEffect, useRef } from "react";
import { track, type TrackEvent } from "@/lib/track";

/** Telt één keer per paginabezoek dat dit stuk echt in beeld is geweest (de noemer van de klikratio). */
export function SeenTracker({ event }: { event: TrackEvent }) {
  const ref = useRef<HTMLSpanElement>(null);
  useEffect(() => {
    const el = ref.current?.parentElement;
    if (!el || typeof IntersectionObserver === "undefined") return;
    const io = new IntersectionObserver((entries) => {
      if (entries.some((e) => e.isIntersecting)) { track(event); io.disconnect(); }
    }, { threshold: 0.5 });
    io.observe(el);
    return () => io.disconnect();
  }, [event.type, event.market, event.plate]); // eslint-disable-line react-hooks/exhaustive-deps
  return <span ref={ref} hidden />;
}
