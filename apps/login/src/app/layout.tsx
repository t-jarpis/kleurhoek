import "@kleurhoek/theme/theme.css";
import "@kleurhoek/theme/ui.css";
import "./globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = { title: "Inloggen", robots: { index: false, follow: false } };

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="nl" data-mode="ouder">
      <body>{children}</body>
    </html>
  );
}
