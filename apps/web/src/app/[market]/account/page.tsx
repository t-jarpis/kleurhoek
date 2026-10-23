import type { Metadata } from "next";
import { Logo } from "@/components/Logo";
import { AccountPanel } from "@/components/AccountPanel";
import { marketLanguage } from "@/lib/markets";
import { messages } from "@/i18n/nl";

export const metadata: Metadata = { title: "Mijn account", robots: { index: false } };

export default async function AccountPage({ params }: { params: Promise<{ market: string }> }) {
  const { market } = await params;
  const t = messages(marketLanguage(market));
  return (
    <div className="wrap narrow" data-mode="ouder">
      <header className="mast"><Logo market={market} /><a className="btn" href={`/${market}`}>{t.back}</a></header>
      <h1 className="page-title">{t.account}</h1>
      <AccountPanel market={market} t={{
        login: t.login, logout: t.logout, loading: t.loading, accountError: t.accountError, name: t.name, email: t.email,
        memberSince: t.memberSince, accountPrivacy: t.accountPrivacy, deleteAccount: t.deleteAccount, deleteSure: t.deleteSure,
      }} />
    </div>
  );
}
