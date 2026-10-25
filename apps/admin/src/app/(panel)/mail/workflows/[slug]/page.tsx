import Link from "next/link";
import { notFound } from "next/navigation";
import { adminApi, describe, type MailWorkflow } from "@/lib/api";
import { MailNav } from "../../nav";
import { WorkflowEditor } from "./WorkflowEditor";

export const dynamic = "force-dynamic";
export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) { return { title: `Workflow ${(await params).slug} · Mail` }; }

const EMPTY: Pick<MailWorkflow, "name" | "enabled" | "trigger" | "steps"> = {
  name: "", enabled: false, trigger: { type: "plates_published", min: 5 }, steps: [{ type: "filter", topics: ["nieuwe-platen"] }, { type: "send", template: "nieuwe-platen" }],
};

export default async function WorkflowPage({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const isNew = slug === "nieuw";
  let data;
  try {
    const [list, me] = await Promise.all([adminApi.mailWorkflows(), adminApi.me()]);
    data = { ...list, canManage: me.permissions.includes("mail.manage") };
  } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const current = data.workflows.find((w) => w.slug === slug);
  if (!isNew && !current) notFound();
  return (
    <>
      <div><p className="lead"><Link href="/mail/workflows">Workflows</Link></p><h1>{current?.name ?? "Nieuwe workflow"}</h1></div>
      <div className="toolbar"><MailNav active="workflows" /></div>
      <WorkflowEditor slug={isNew ? null : slug} initial={current ?? EMPTY} options={data.options} canManage={data.canManage} />
    </>
  );
}
