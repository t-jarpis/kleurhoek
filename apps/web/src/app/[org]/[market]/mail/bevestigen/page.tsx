import type { Metadata } from "next";
import { Logo } from "@/components/Logo";
import { ConfirmMail } from "@/components/ConfirmMail";
import { messages } from "@/i18n/nl";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { notFound } from "next/navigation";

export async function generateMetadata({ params }: { params: Promise<{ market: string }> }): Promise<Metadata> {
  return { title: messages(marketLanguage((await params).market)).mlConfirmed, robots: { index: false, follow: false } };
}

export default async function ConfirmPage({ params, searchParams }: { params: Promise<{ org: string; market: string }>; searchParams: Promise<{ t?: string }> }) {
  const [{ org: slug, market }, { t: token }] = await Promise.all([params, searchParams]);
  const org = await getOrg(slug);
  if (!org?.isDefault) notFound();
  const language = marketLanguage(market);
  const t = messages(language);
  return (
    <div className="wrap narrow" data-mode="ouder">
      <header className="mast"><Logo market={market} org={org} /></header>
      <h1 className="page-title">{t.mlTitle}</h1>
      {token && /^[A-Za-z0-9_-]{20,64}$/.test(token) ? <ConfirmMail token={token} language={language} market={market} />
        : <div className="ui-callout" data-tone="warning" role="status"><div>{t.mlConfirmInvalid}</div></div>}
    </div>
  );
}
