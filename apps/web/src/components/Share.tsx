"use client";
import { Icon } from "@kleurhoek/theme";
import { useEffect, useRef, useState } from "react";
import type { Messages } from "@/i18n/nl";
import { download } from "@/lib/export";
import { shareUrl, whatsappUrl } from "@/lib/share";
import { track } from "@/lib/track";

type Link = { text: string; url: string };

/**
 * Delen vanuit de kleurstudio (ADR 0074). Het plaatje wordt op dit apparaat gemaakt en via het deelmenu van het
 * apparaat verstuurd; er gaat niets naar onze server. Zonder deelmenu (computer): WhatsApp-link en link kopiëren.
 */
export function ShareButton({ t, market, slug, title, colored, code, image }: {
  t: Messages["shareKit"]; market: string; slug: string; title: string; colored: boolean;
  /** De kleuren van de plaat als code voor de link, of null als er niets (effen) is ingekleurd. */
  code: () => string | null;
  /** Het ingekleurde werk als PNG, zonder eigen tekst. */
  image: () => Promise<Blob | null>;
}) {
  const dialog = useRef<HTMLDialogElement>(null);
  const [open, setOpen] = useState(false);
  const [fallback, setFallback] = useState<Link | null>(null);
  const [copied, setCopied] = useState(false);
  const [busy, setBusy] = useState(false);
  const [saved, setSaved] = useState(false);
  useEffect(() => { if (open) dialog.current?.showModal(); }, [open]);

  const page = () => window.location.href;
  const counted = () => track({ type: "share", market, plate: slug });

  /** Een link delen: via het deelmenu als dat kan, anders tonen we WhatsApp en kopiëren. */
  const shareLink = async (l: Link) => {
    setCopied(false); setSaved(false);
    if (typeof navigator.share === "function") {
      try { await navigator.share({ title, text: l.text, url: l.url }); counted(); return; }
      catch (e) { if ((e as Error)?.name === "AbortError") return; }
    }
    setFallback(l);
  };

  const shareMine = async () => {
    setBusy(true); setCopied(false); setSaved(false);
    const k = code();
    const l = { text: t.mineText, url: shareUrl(page(), k) };
    try {
      const blob = await image();
      const file = blob ? new File([blob], `kleurhoek-${slug}.png`, { type: "image/png" }) : null;
      if (file && typeof navigator.canShare === "function" && navigator.canShare({ files: [file] })) {
        try { await navigator.share({ files: [file], title, text: `${l.text} ${l.url}` }); counted(); return; }
        catch (e) { if ((e as Error)?.name === "AbortError") return; }
      }
      if (blob) { download(blob, `kleurhoek-${slug}.png`); setSaved(true); }
      setFallback(l);
    } finally { setBusy(false); }
  };

  const copy = (url: string) => {
    void navigator.clipboard?.writeText(url).then(() => { setCopied(true); counted(); setTimeout(() => setCopied(false), 2000); });
  };

  return (
    <>
      <button type="button" className="btn" onClick={() => { setFallback(null); setOpen(true); }}><Icon name="share" size={16} /> {t.button}</button>
      {open && (
        <dialog ref={dialog} className="ui-dialog kh-sharesheet" aria-labelledby="share-title" onClose={() => setOpen(false)}>
          <h2 id="share-title">{t.title}</h2>
          <p className="hint">{t.lede}</p>
          <div className="kh-sharesheet-options">
            {colored && (
              <>
                <button type="button" className="ui-btn" data-variant="primary" disabled={busy} onClick={() => void shareMine()}>
                  <Icon name="image" size={16} /> {t.mine}
                </button>
                <span className="hint">{t.mineHint}</span>
                <button type="button" className="ui-btn" onClick={() => void shareLink({ text: t.restText, url: shareUrl(page(), code()) })}>
                  <Icon name="together" size={16} /> {t.rest}
                </button>
              </>
            )}
            <button type="button" className="ui-btn" onClick={() => void shareLink({ text: t.challengeText, url: shareUrl(page()) })}>
              <Icon name="star" size={16} /> {t.challenge}
            </button>
            <button type="button" className="ui-btn" onClick={() => void shareLink({ text: t.blankText, url: shareUrl(page()) })}>
              <Icon name="share" size={16} /> {t.blank}
            </button>
          </div>
          {fallback && (
            <div className="kh-sharesheet-fallback" role="status">
              {saved && <p className="hint">{t.saved}</p>}
              <div className="kh-sharesheet-link">
                <a className="ui-btn" href={whatsappUrl(fallback.text, fallback.url)} target="_blank" rel="noopener noreferrer" onClick={counted}>{t.whatsapp}</a>
                <button type="button" className="ui-btn" onClick={() => copy(fallback.url)}>{copied ? t.copied : t.copy}</button>
              </div>
            </div>
          )}
          {colored && <p className="hint">{t.note}</p>}
          <div className="ui-dialog-actions">
            <button type="button" className="ui-btn" onClick={() => dialog.current?.close()}>{t.close}</button>
          </div>
        </dialog>
      )}
    </>
  );
}
