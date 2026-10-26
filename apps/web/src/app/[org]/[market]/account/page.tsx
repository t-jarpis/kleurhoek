import type { Metadata } from "next";
import { baseFor } from "@/lib/base";
import { link } from "@/lib/sites";
import { Logo } from "@/components/Logo";
import { AccountBenefits } from "@/components/AccountBenefits";
import { AccountPanel } from "@/components/AccountPanel";
import { Track } from "@/components/Track";
import { marketLanguage } from "@/lib/markets";
import { messages } from "@/i18n/nl";
import { notFound } from "next/navigation";
import { getOrg } from "@/lib/org";

export async function generateMetadata({ params }: { params: Promise<{ market: string }> }): Promise<Metadata> {
  const t = messages((await params).market);
  return { title: t.account, robots: { index: false } };
}

export default async function AccountPage({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org?.features.accounts) notFound();
  const base = baseFor(org, market);
  const t = messages(market);
  return (
    <div className="wrap narrow" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "account" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={link(base)}>{t.back}</a></header>
      <h1 className="page-title">{t.account}</h1>
      <AccountPanel market={market} t={{
        login: t.login, logout: t.logout, loading: t.loading, accountError: t.accountError, name: t.name, email: t.email,
        memberSince: t.memberSince, accountPrivacy: t.accountPrivacy, deleteAccount: t.deleteAccount, deleteSure: t.deleteSure,
        mlAccount: t.mlAccount, mlAccountHint: t.mlAccountHint, mlTopicNames: t.mlTopicNames, mlSave: t.mlSave, mlSaved: t.mlSaved, mlError: t.mlError,
      }} />
      <AccountBenefits market={market} language={marketLanguage(market)} />
    </div>
  );
}
