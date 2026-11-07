// Uitstekende hoekjes (ADR 0088): een vlak dat onder een later vlak hoort te verdwijnen (een been onder een buik,
// een arm onder een mouw), maar er net naast begint, laat een scherp hoekje zien vlak naast de rand van dat
// latere vlak. We lopen in de browser langs de omtrek van elk vlak, kijken welk stuk bedekt is door een vlak dat
// later getekend wordt, en melden een scherpe hoek op het zichtbare stuk vlak na zo'n overgang.

/** Draait in de browser (page.evaluate). Geeft per verdacht vlak { i, x, y } in viewBox-eenheden. */
export const STUBS_JS = `(opts) => {
  const { step = 0.5, minTurn = 35, maxCap = 20, minShow = 5 } = opts ?? {};
  const svg = document.querySelector("svg");
  const toRoot = svg.getScreenCTM().inverse();
  const shapes = [...svg.querySelectorAll(".r")].filter((el) => el instanceof SVGGeometryElement && !el.closest("defs,clipPath,mask,pattern"));
  const all = [...svg.querySelectorAll("*")];
  const order = new Map(all.map((el, i) => [el, i]));
  const box = (el) => {
    const b = el.getBBox(), m = toRoot.multiply(el.getScreenCTM());
    const pts = [[b.x, b.y], [b.x + b.width, b.y], [b.x, b.y + b.height], [b.x + b.width, b.y + b.height]].map(([x, y]) => new DOMPoint(x, y).matrixTransform(m));
    return { x0: Math.min(...pts.map((p) => p.x)), x1: Math.max(...pts.map((p) => p.x)), y0: Math.min(...pts.map((p) => p.y)), y1: Math.max(...pts.map((p) => p.y)) };
  };
  const boxes = new Map(shapes.map((el) => [el, box(el)]));
  const overlap = (a, b) => a.x0 <= b.x1 && b.x0 <= a.x1 && a.y0 <= b.y1 && b.y0 <= a.y1;
  const found = [];
  for (const a of shapes) {
    const ba = boxes.get(a);
    const later = shapes.filter((b) => order.get(b) > order.get(a) && overlap(ba, boxes.get(b)));
    if (!later.length) continue;
    const len = a.getTotalLength();
    if (!len || len < 6) continue;
    const n = Math.max(12, Math.round(len / step));
    const toA = toRoot.multiply(a.getScreenCTM());
    const inv = later.map((b) => [b, b.getScreenCTM().inverse().multiply(a.getScreenCTM())]);
    const pts = [], cover = [];
    for (let k = 0; k < n; k++) {
      const p = a.getPointAtLength((k / n) * len);
      pts.push(new DOMPoint(p.x, p.y).matrixTransform(toA));
      cover.push(inv.some(([b, m]) => b.isPointInFill(new DOMPoint(p.x, p.y).matrixTransform(m))));
    }
    if (cover.every(Boolean) || !cover.some(Boolean)) continue;
    const ds = len / n, w = Math.max(1, Math.round(1 / ds));
    const turn = (k) => {
      const p = pts[(k - w + n) % n], q = pts[k], r = pts[(k + w) % n];
      const ux = q.x - p.x, uy = q.y - p.y, vx = r.x - q.x, vy = r.y - q.y;
      const lu = Math.hypot(ux, uy), lv = Math.hypot(vx, vy);
      if (lu < 1e-6 || lv < 1e-6) return 0;
      return Math.acos(Math.max(-1, Math.min(1, (ux * vx + uy * vy) / (lu * lv)))) * 180 / Math.PI;
    };
    // Hoeken (scherpe bocht) verdelen de omtrek in stukken; we zoeken een kort recht stuk (de "dop" van een been of
    // arm) dat deels bedekt is, tussen twee veel langere stukken: de dop die net niet onder het latere vlak valt.
    const corners = [];
    for (let k = 0; k < n; k++) if (turn(k) >= minTurn && turn(k) >= turn((k - 1 + n) % n) && turn(k) > turn((k + 1) % n)) corners.push(k);
    if (corners.length < 3) continue;
    const segs = corners.map((c, i) => {
      const e = corners[(i + 1) % corners.length], idx = [];
      for (let k = c; k !== e; k = (k + 1) % n) idx.push(k);
      idx.push(e);
      const a0 = pts[idx[0]], a1 = pts[idx[idx.length - 1]];
      return { idx, length: (idx.length - 1) * ds, chord: Math.hypot(a1.x - a0.x, a1.y - a0.y) };
    });
    segs.forEach((g, i) => {
      if (g.length < 3 || g.length > maxCap || g.chord < 0.95 * g.length) return;
      const prev = segs[(i - 1 + segs.length) % segs.length], next = segs[(i + 1) % segs.length];
      if (prev.length < 1.5 * g.length || next.length < 1.5 * g.length) return;
      const inner = g.idx.slice(1, -1), c = inner.map((k) => cover[k]), vis = c.filter((x) => !x).length / c.length;
      // Een stukje korter dan een lijndikte valt weg in de lijn; pas daarboven zie je een hoekje.
      if (vis < 0.12 || vis > 0.9 || vis * g.length < minShow) return;
      const flips = c.slice(1).filter((x, j) => x !== c[j]).length;
      if (flips !== 1) return;
      const end = c[0] ? g.idx[g.idx.length - 1] : g.idx[0];
      found.push({ i: Number(a.dataset.i ?? -1), x: +pts[end].x.toFixed(1), y: +pts[end].y.toFixed(1) });
    });
  }
  return found;
}`;
