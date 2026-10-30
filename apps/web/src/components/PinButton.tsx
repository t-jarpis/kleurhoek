"use client";
import { Icon } from "@kleurhoek/theme";

/**
 * "Bewaar op Pinterest" (ADR 0057). Op de computer opent de gewone Pinterest-link een venster om een bord te kiezen.
 * Op een telefoon negeert de Pinterest-app die link vaak en opent hij alleen de startpagina; daar gebruiken we het
 * deelmenu van het toestel met de pin-afbeelding en de link, zodat de app er zelf een pin van maakt.
 */
export function PinButton({ href, image, url, text, label, file }: { href: string; image: string; url: string; text: string; label: string; file: string }) {
  const onClick = async (e: React.MouseEvent<HTMLAnchorElement>) => {
    const touch = typeof window !== "undefined" && window.matchMedia("(pointer: coarse)").matches;
    if (!touch || typeof navigator.share !== "function") return;
    e.preventDefault();
    try {
      const blob = await fetch(image).then((r) => (r.ok ? r.blob() : Promise.reject(new Error(String(r.status)))));
      const shared = new File([blob], file, { type: blob.type || "image/png" });
      const data: ShareData = navigator.canShare?.({ files: [shared] }) ? { files: [shared], text: `${text}\n${url}`, url } : { text, url };
      await navigator.share(data);
    } catch (err) {
      if ((err as Error)?.name === "AbortError") return;
      try { await navigator.share({ text, url }); } catch { window.location.href = href; }
    }
  };
  return (
    <a className="ui-btn" target="_blank" rel="noopener noreferrer" href={href} onClick={(e) => void onClick(e)}>
      <Icon name="pin" size={16} /> {label}
    </a>
  );
}
