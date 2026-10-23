import type { Metadata } from "next";
import { Logo } from "@/components/Logo";
import { AccountPanel } from "@/components/AccountPanel";
import { Track } from "@/components/Track";
import { marketLanguage } from "@/lib/markets";
import { messages } from "@/i18n/nl";
import { notFound } from "next/navigation";
import { getOrg } from "@/lib/org";

export const metadata: Metadata = { title: "Mijn account", robots: { index: false } };

export default async function AccountPage({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org?.features.accounts) notFound();
  const t = messages(marketLanguage(market));
  return (
    <div className="wrap narrow" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "account" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={`/${market}`}>{t.back}</a></header>
      <h1 className="page-title">{t.account}</h1>
      <AccountPanel market={market} t={{
        login: t.login, logout: t.logout, loading: t.loading, accountError: t.accountError, name: t.name, email: t.email,
        memberSince: t.memberSince, accountPrivacy: t.accountPrivacy, deleteAccount: t.deleteAccount, deleteSure: t.deleteSure,
      }} />
    </div>
  );
}
