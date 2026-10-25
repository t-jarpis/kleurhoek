"use client";
import { useEffect, useState } from "react";
import { messages } from "@/i18n/nl";

/** Bevestigt een aanmelding zodra de pagina in een browser opent (niet bij het ophalen door een linkscanner). */
export function ConfirmMail({ token, language, market }: { token: string; language: string; market: string }) {
  const t = messages(language);
  const [status, setStatus] = useState<"busy" | "confirmed" | "invalid">("busy");
  useEffect(() => {
    fetch("/mail/bevestigen", { method: "POST", headers: { "content-type": "application/json" }, body: JSON.stringify({ t: token }) })
      .then(async (r) => setStatus(r.ok && ((await r.json()) as { status: string }).status === "confirmed" ? "confirmed" : "invalid"))
      .catch(() => setStatus("invalid"));
  }, [token]);
  if (status === "busy") return <p className="muted" role="status">{t.mlConfirming}</p>;
  if (status === "invalid") return <div className="ui-callout" data-tone="warning" role="status"><div>{t.mlConfirmInvalid}</div></div>;
  return (
    <div className="stack">
      <div className="ui-callout" data-tone="success" role="status"><div><strong>{t.mlConfirmed}</strong>{t.mlConfirmedText}</div></div>
      <p><a className="btn primary" href={`/${market}`}>{t.back}</a></p>
    </div>
  );
}
