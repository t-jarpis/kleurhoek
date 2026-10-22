import "@fontsource/nunito/400.css";
import "@fontsource/nunito/600.css";
import "@fontsource/nunito/800.css";
import "./globals.css";
import Link from "next/link";
import type { Metadata } from "next";

export const metadata: Metadata = { title: { default: "Kleurhoek beheer", template: "%s · Kleurhoek beheer" }, robots: { index: false, follow: false } };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nl">
      <body>
        <div className="shell">
          <nav className="side" aria-label="Beheer">
            <b>Kleurhoek beheer</b>
            <Link href="/">Dashboard</Link>
            <Link href="/rate-limits">Rate limits</Link>
          </nav>
          <main>{children}</main>
        </div>
      </body>
    </html>
  );
}
