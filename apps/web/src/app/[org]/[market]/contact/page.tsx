import type { Metadata } from "next";
import { baseFor } from "@/lib/base";
import { link } from "@/lib/sites";
import { notFound } from "next/navigation";
import { ContactForm } from "@/components/ContactForm";
import { Logo } from "@/components/Logo";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { pageMeta } from "@/lib/seo";
import { sendContact } from "./actions";

export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string }> }): Promise<Metadata> {
  const { org, market } = await params;
  const t = messages(marketLanguage(market));
  return { title: t.contact, description: t.metaContact, ...pageMeta(await getOrg(org), market, "/contact") };
}

/** Onderwerp vooraf kiezen via ?onderwerp=… (bijvoorbeeld vanuit de disclaimer). */
const TOPIC_PARAM: Record<string, string> = { vraag: "question", idee: "idea", fout: "bug", samenwerken: "partnership", partnership: "partnership", auteursrecht: "copyright", copyright: "copyright", privacy: "privacy" };

export default async function ContactPage({ params, searchParams }: { params: Promise<{ org: string; market: string }>; searchParams: Promise<{ onderwerp?: string }> }) {
  const [{ org: slug, market }, { onderwerp }] = await Promise.all([params, searchParams]);
  const org = await getOrg(slug);
  if (!org) notFound();
  const base = baseFor(org, market);
  const t = messages(marketLanguage(market));
  return (
    <div className="wrap narrow" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "contact" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={link(base)}>{t.back}</a></header>
      <h1 className="page-title">{t.contactTitle}</h1>
      <p className="lede">{t.contactLede}</p>
      {org.isDefault && <p className="lede">{t.ownHint} <a href={link(base, "/eigen-omgeving")}>{t.ownHintLink}</a>.</p>}
      <ContactForm action={sendContact.bind(null, market)} initialTopic={TOPIC_PARAM[onderwerp ?? ""] ?? "question"} t={{
        contactTopic: t.contactTopic, contactTopics: t.contactTopics, contactName: t.contactName, contactNameHint: t.contactNameHint,
        contactEmail: t.contactEmail, contactEmailHint: t.contactEmailHint, contactMessage: t.contactMessage, contactSend: t.contactSend,
        contactSending: t.contactSending, contactPrivacy: t.contactPrivacy, contactThanks: t.contactThanks, contactThanksText: t.contactThanksText,
        contactError: t.contactError, contactTooMany: t.contactTooMany, contactClosed: t.contactClosed,
      }} />
      <SiteFooter base={base} t={t} own={org.isDefault} />
    </div>
  );
}
