import type { Metadata } from "next";
import { Logo } from "@/components/Logo";
import { MailPreferences } from "@/components/MailPreferences";
import { SubscribeForm } from "@/components/SubscribeForm";
import { messages } from "@/i18n/nl";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { notFound } from "next/navigation";
import { subscribe } from "./actions";

export async function generateMetadata({ params }: { params: Promise<{ market: string }> }): Promise<Metadata> {
  return { title: messages(marketLanguage((await params).market)).mlPrefsTitle, robots: { index: false, follow: false } };
}

/** Mail (ADR 0037): met een link uit een mail de voorkeuren of afmelden, anders aanmelden. */
export default async function MailPage({ params, searchParams }: { params: Promise<{ org: string; market: string }>; searchParams: Promise<{ t?: string; afmelden?: string }> }) {
  const [{ org: slug, market }, { t: token, afmelden }] = await Promise.all([params, searchParams]);
  const org = await getOrg(slug);
  if (!org?.isDefault) notFound();
  const language = marketLanguage(market);
  const t = messages(language);
  return (
    <div className="wrap narrow" data-mode="ouder">
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={`/${market}`}>{t.back}</a></header>
      <h1 className="page-title">{token ? t.mlPrefsTitle : t.mlTitle}</h1>
      {token && /^[A-Za-z0-9_.-]{20,80}$/.test(token)
        ? <MailPreferences token={token} language={language} unsubscribe={afmelden === "1"} />
        : <SubscribeForm action={subscribe.bind(null, market)} language={language} titled={false} />}
    </div>
  );
}
