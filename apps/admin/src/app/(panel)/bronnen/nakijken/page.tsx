import { adminApi, describe } from "@/lib/api";
import { SourcesNav } from "../labels";
import { SourceRow } from "../SourceRow";

export const dynamic = "force-dynamic";
export const metadata = { title: "Bronnen nakijken" };

/** Alles wat aandacht vraagt: nieuwe links, links die niet meer werken en pagina's die veranderd zijn. */
export default async function Review({ searchParams }: { searchParams: Promise<{ melding?: string; fout?: string }> }) {
  const q = await searchParams;
  let list, me;
  try { [list, me] = await Promise.all([adminApi.sourceReview(), adminApi.me()]); } catch (e) { const d = describe(e); return <div className="err"><h1>{d.title}</h1><p>{d.text}</p></div>; }
  const canManage = me.permissions.includes("sources.manage");
  return (
    <>
      <div className="row-between">
        <div><h1>Nakijken</h1><p className="lead">Nieuwe links wachten op goedkeuring. Werkt een link niet meer, dan staat hij al offline; controleer opnieuw of verwijder hem. Een veranderde pagina blijft online tot je hem nakijkt.</p></div>
        <SourcesNav active="nakijken" attention={list.length} />
      </div>
      {q.melding && <p className="note" role="status">{q.melding}</p>}
      {q.fout && <div className="err" role="alert"><p>{q.fout}</p></div>}
      {list.length === 0 ? <section className="panel"><p className="lead">Niets na te kijken.</p></section> : list.map((s) => <SourceRow key={s.id} s={s} canManage={canManage} from="nakijken" />)}
    </>
  );
}
