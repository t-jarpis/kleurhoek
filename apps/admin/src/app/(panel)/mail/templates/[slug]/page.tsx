import Link from "next/link";
import { notFound } from "next/navigation";
import { adminApi, ApiError, describe, type MailTemplateInput } from "@/lib/api";
import { MailNav } from "../../nav";
import { TemplateEditor } from "./TemplateEditor";

export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) { return { title: `Template ${(await params).slug} · Mail` }; }

const EMPTY: MailTemplateInput = { name: "", kind: "campaign", subject: { nl: "" }, preheader: {}, blocks: [{ id: "h", type: "heading", text: { nl: "" } }, { id: "t", type: "text", text: { nl: "" } }] };

export default async function TemplatePage({ params, searchParams }: { params: Promise<{ slug: string }>; searchParams: Promise<{ melding?: string }> }) {
  const [{ slug }, { melding }] = await Promise.all([params, searchParams]);
  const isNew = slug === "nieuw";
  let data;
  try {
    const [t, list, me] = await Promise.all([isNew ? Promise.resolve(null) : adminApi.mailTemplate(slug), adminApi.mailTemplates(), adminApi.me()]);
    data = { template: t?.template ?? null, options: list.options, canManage: me.permissions.includes("mail.manage") };
  } catch (e) {
    if (e instanceof ApiError && e.status === 404) notFound();
    const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>;
  }
  const { template, options, canManage } = data;
  return (
    <>
      <div><p className="lead"><Link href="/mail/templates">Templates</Link></p><h1>{template?.name ?? "Nieuwe template"}</h1></div>
      <div className="toolbar"><MailNav active="templates" /></div>
      {melding && <p className="note" role="status">{melding}</p>}
      <TemplateEditor slug={isNew ? null : slug} initial={template ?? EMPTY} options={options} canManage={canManage} />
    </>
  );
}
