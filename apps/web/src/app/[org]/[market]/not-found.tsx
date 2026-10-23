import Link from "next/link";

export default function NotFoundPage() {
  return (
    <div className="wrap">
      <div className="empty"><b>Deze plaat bestaat niet (meer)</b><span>Misschien is hij verhuisd of nog niet beschikbaar in jouw land.</span><Link className="btn" href="/">Naar alle platen</Link></div>
    </div>
  );
}
