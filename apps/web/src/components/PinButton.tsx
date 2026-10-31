"use client";
import { Icon } from "@kleurhoek/theme";

/**
 * "Bewaar op Pinterest" (ADR 0057). Op de computer opent de gewone Pinterest-link een venster om een bord te kiezen.
 * Op een telefoon negeert de Pinterest-app die link en opent hij alleen de startpagina. Daar delen we via het deelmenu
 * alleen de link (zoals Safari doet): de app haalt de plaat zelf op via og:image. Een afbeelding plus tekst en link
 * delen gaf in de Pinterest-app een fout bij het maken van de pin.
 */
export function PinButton({ href, url, title, label }: { href: string; url: string; title: string; label: string }) {
  const onClick = async (e: React.MouseEvent<HTMLAnchorElement>) => {
    const touch = typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches;
    if (!touch || typeof navigator.share !== "function") return;
    e.preventDefault();
    try {
      await navigator.share({ title, url });
    } catch (err) {
      if ((err as Error)?.name !== "AbortError") window.location.href = href;
    }
  };
  return (
    <a className="ui-btn" target="_blank" rel="noopener noreferrer" href={href} onClick={(e) => void onClick(e)}>
      <Icon name="pin" size={16} /> {label}
    </a>
  );
}
