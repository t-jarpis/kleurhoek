import "@kleurhoek/theme/theme.css";
import "@kleurhoek/theme/ui.css";
import "./globals.css";
import type { Metadata } from "next";
import { headers } from "next/headers";
import { pickLanguage, t } from "@/lib/i18n";
import { readFlow } from "@/lib/state";

/** Taal van de pagina: uit de flow, anders de browser (ADR 0029). */
async function language() {
  return (await readFlow())?.lang ?? pickLanguage(undefined, (await headers()).get("accept-language"));
}

export async function generateMetadata(): Promise<Metadata> {
  return { title: t(await language()).title, robots: { index: false, follow: false } };
}

export default async function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang={await language()} data-mode="ouder">
      <body>{children}</body>
    </html>
  );
}
