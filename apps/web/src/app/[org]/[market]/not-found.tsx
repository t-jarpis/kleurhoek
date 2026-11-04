import Link from "next/link";

export default function NotFoundPage() {
  return (
    <div className="wrap">
      <main className="empty"><b role="heading" aria-level={1}>Deze plaat bestaat niet (meer)</b><span>Misschien is hij verhuisd of nog niet beschikbaar in jouw land.</span><Link className="btn" href="/">Naar alle platen</Link></main>
    </div>
  );
}
