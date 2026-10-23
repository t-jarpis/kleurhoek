"use client";
import { useRef, useState } from "react";
import { uploadLogo } from "./actions";

/** LogoUpload uit het design system: een echte knop om het bestandsveld; kiezen is meteen uploaden. */
export function LogoUpload({ slug }: { slug: string }) {
  const form = useRef<HTMLFormElement>(null);
  const [busy, setBusy] = useState(false);
  return (
    <form ref={form} action={uploadLogo}>
      <input type="hidden" name="slug" value={slug} />
      <label className="ui-btn" aria-busy={busy || undefined}>
        {busy ? "Bezig met uploaden…" : "Kies bestand"}
        <input type="file" name="logo" accept="image/png,image/webp,image/jpeg,image/svg+xml"
          onChange={(e) => { if (e.currentTarget.files?.length) { setBusy(true); form.current?.requestSubmit(); } }} />
      </label>
    </form>
  );
}
