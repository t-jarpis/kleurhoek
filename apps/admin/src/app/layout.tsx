import "@kleurhoek/theme/theme.css";
import "@kleurhoek/theme/ui.css";
import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = { title: { default: "Kleurhoek beheer", template: "%s · Kleurhoek beheer" }, robots: { index: false, follow: false } };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nl" data-mode="beheer">
      <body>{children}</body>
    </html>
  );
}
