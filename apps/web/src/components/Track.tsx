"use client";
import { useEffect } from "react";
import { track, type TrackEvent } from "@/lib/track";

export function Track({ event }: { event: TrackEvent }) {
  const key = JSON.stringify(event);
  useEffect(() => { track(JSON.parse(key) as TrackEvent); }, [key]);
  return null;
}
