import type { Metadata } from "next";
import { baseFor } from "@/lib/base";
import { link } from "@/lib/sites";
import { notFound } from "next/navigation";
import { Logo } from "@/components/Logo";
import { OrgRequestForm } from "@/components/OrgRequestForm";
import { SiteFooter } from "@/components/SiteFooter";
import { Track } from "@/components/Track";
import { messages } from "@/i18n/nl";
import { marketLanguage } from "@/lib/markets";
import { getOrg } from "@/lib/org";
import { pageMeta } from "@/lib/seo";
import { sendOrgRequest } from "./actions";

export async function generateMetadata({ params }: { params: Promise<{ org: string; market: string }> }): Promise<Metadata> {
  const { org, market } = await params;
  const t = messages(market);
  return { title: t.metaOwnTitle, description: t.metaOwn, ...pageMeta(await getOrg(org), market, "/eigen-omgeving") };
}

/** Eigen omgeving (ADR 0028): wat een organisatie krijgt (ADR 0017) en een aanvraagformulier. Alleen op Kleurhoek zelf. */
export default async function OwnSpacePage({ params }: { params: Promise<{ org: string; market: string }> }) {
  const { org: slug, market } = await params;
  const org = await getOrg(slug);
  if (!org?.isDefault) notFound();
  const base = baseFor(org, market);
  const t = messages(market);
  return (
    <div className="wrap narrow" data-mode="ouder">
      <Track event={{ type: "page_view", market, page: "eigen-omgeving" }} />
      <header className="mast"><Logo market={market} org={org} /><a className="btn" href={link(base)}>{t.back}</a></header>
      <h1 className="page-title">{t.ownTitle}</h1>
      <p className="lede">{t.ownLede}</p>
      <p><a className="ui-btn" data-variant="primary" href="#aanvragen">{t.ownCta}</a></p>

      <section className="kh-pitch">
        <h2>{t.ownBenefitsTitle}</h2>
        <ul className="kh-benefits">
          {t.ownBenefits.map(([title, text]) => <li key={title}><b>{title}</b><span>{text}</span></li>)}
        </ul>
      </section>

      <section className="kh-pitch">
        <h2>{t.ownForWho}</h2>
        <p>{t.ownForWhoText}</p>
      </section>

      <section className="kh-pitch">
        <h2>{t.ownStepsTitle}</h2>
        <ol className="kh-steps">{t.ownSteps.map((s) => <li key={s}>{s}</li>)}</ol>
      </section>

      <section className="kh-pitch" id="aanvragen">
        <h2>{t.ownFormTitle}</h2>
        <OrgRequestForm action={sendOrgRequest.bind(null, market)} t={{
          orgName: t.orgName, orgKind: t.orgKind, orgKinds: t.orgKinds, orgCode: t.orgCode, orgCodeHint: t.orgCodeHint, orgCodeExample: t.orgCodeExample,
          orgChildren: t.orgChildren, orgChildrenHint: t.orgChildrenHint, orgSite: t.orgSite, contactName: t.contactName,
          contactEmail: t.contactEmail, contactEmailHint: t.contactEmailHint, orgMessage: t.orgMessage, orgMessagePlaceholder: t.orgMessagePlaceholder,
          orgSend: t.orgSend, contactSending: t.contactSending, contactPrivacy: t.contactPrivacy, orgThanks: t.orgThanks, orgThanksText: t.orgThanksText,
          contactError: t.contactError, contactTooMany: t.contactTooMany, contactClosed: t.contactClosed, optionalField: t.optionalField,
        }} />
      </section>
      <SiteFooter base={base} t={t} own />
    </div>
  );
}
