/**
 * Het werk uit de kleurstudio als afbeelding of filmpje (ADR 0056). Alles gebeurt in de browser: de plaat wordt
 * een losse SVG met de stijl erin, die op een canvas wordt getekend. Niets gaat naar de server.
 */

const PROPS = ["fill", "stroke", "stroke-width", "stroke-linecap", "stroke-linejoin", "stroke-dasharray", "font-family", "font-weight", "font-size", "text-anchor", "dominant-baseline", "paint-order", "opacity", "display"] as const;

/** De stijl van de pagina als regels in de SVG zelf: een losse afbeelding kent de stylesheet niet. */
function styleFor(svg: SVGSVGElement): string {
  const seen = new Set<string>();
  const rules: string[] = [];
  const cs = getComputedStyle(svg);
  const ink = cs.getPropertyValue("--plate-ink").trim() || "black";
  const paper = cs.getPropertyValue("--color-paper").trim() || "white";
  const sw = cs.getPropertyValue("--sw").trim() || "2.4";
  for (const el of Array.from(svg.querySelectorAll<SVGElement>("[class]"))) {
    const cls = el.getAttribute("class")!.split(/\s+/).filter(Boolean).join(".");
    if (!cls || seen.has(cls)) continue;
    seen.add(cls);
    const c = getComputedStyle(el);
    const decl = PROPS.map((p) => {
      // Een vlak heeft vaak een eigen vulkleur; de regel zelf is het papier.
      // Lettergrootte alleen als het element hem niet zelf heeft (nummers hebben elk een eigen grootte).
      if (p === "font-size" && el.hasAttribute("font-size")) return "";
      const v = p === "fill" && /(^|\.)r(\.|$)/.test(cls) ? paper : c.getPropertyValue(p);
      return v ? `${p}:${v}` : "";
    }).filter(Boolean).join(";");
    rules.push(`.${cls}{${decl}}`);
  }
  const lines = svg.dataset.lines === "geen";
  rules.push(`.kh-ro{fill:none;stroke:${lines ? "none" : ink};stroke-width:${sw};stroke-linejoin:round}`, ".kh-sun{stroke:none}");
  if (lines) rules.push(".r{stroke:none}", ".l{display:none}");
  return rules.join("");
}

/** De plaat als losse SVG-tekst; met `inner` een andere binnenkant (een beeld uit de time-lapse). */
export function snapshotSvg(svg: SVGSVGElement, inner?: string): string {
  const clone = svg.cloneNode(true) as SVGSVGElement;
  if (inner !== undefined) clone.querySelector("[data-inner]")!.innerHTML = inner;
  clone.setAttribute("xmlns", "http://www.w3.org/2000/svg");
  const style = document.createElementNS("http://www.w3.org/2000/svg", "style");
  style.textContent = styleFor(svg);
  clone.insertBefore(style, clone.firstChild);
  return new XMLSerializer().serializeToString(clone);
}

function loadImage(svgText: string): Promise<HTMLImageElement> {
  return new Promise((resolve, reject) => {
    const img = new Image();
    const url = URL.createObjectURL(new Blob([svgText], { type: "image/svg+xml" }));
    img.onload = () => { URL.revokeObjectURL(url); resolve(img); };
    img.onerror = () => { URL.revokeObjectURL(url); reject(new Error("svg")); };
    img.src = url;
  });
}

/** Een SVG op een canvas, op papier, met wat witruimte. */
export async function drawSvg(canvas: HTMLCanvasElement, svgText: string, paper: string) {
  const img = await loadImage(svgText);
  const ctx = canvas.getContext("2d")!;
  ctx.fillStyle = paper;
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  const pad = canvas.width * 0.04;
  const w = canvas.width - pad * 2;
  const h = (w * img.height) / img.width;
  ctx.drawImage(img, pad, pad, w, h);
}

/** Canvasgrootte voor een SVG met deze viewBox. */
export function canvasSize(svg: SVGSVGElement, width: number): { width: number; height: number } {
  const vb = svg.viewBox.baseVal;
  const pad = width * 0.04;
  return { width, height: Math.round(((width - pad * 2) * vb.height) / vb.width + pad * 2) };
}

export function download(blob: Blob, name: string) {
  const url = URL.createObjectURL(blob);
  const a = document.createElement("a");
  a.href = url; a.download = name;
  document.body.appendChild(a); a.click(); a.remove();
  setTimeout(() => URL.revokeObjectURL(url), 10_000);
}

/** Welk filmformaat deze browser kan opnemen, of null. */
export function videoType(): string | null {
  if (typeof MediaRecorder === "undefined" || typeof HTMLCanvasElement.prototype.captureStream !== "function") return null;
  return ["video/mp4;codecs=avc1", "video/mp4", "video/webm;codecs=vp9", "video/webm"].find((t) => MediaRecorder.isTypeSupported(t)) ?? null;
}

/**
 * Time-lapse afspelen op een canvas en tegelijk opnemen. Elk beeld wordt pas getekend als het vorige klaar is,
 * zodat een trage telefoon een wat trager filmpje maakt in plaats van beelden over te slaan.
 */
export async function playFrames(canvas: HTMLCanvasElement, frames: string[], paper: string, opts: { fps?: number; record?: string | null; signal?: AbortSignal } = {}): Promise<Blob | null> {
  // Minstens vier seconden, ook als er maar een paar handelingen zijn.
  const fps = Math.min(opts.fps ?? 24, Math.max(3, frames.length / 4));
  const stream = opts.record ? canvas.captureStream(fps) : null;
  const rec = stream && opts.record ? new MediaRecorder(stream, { mimeType: opts.record, videoBitsPerSecond: 4_000_000 }) : null;
  const chunks: Blob[] = [];
  if (rec) { rec.ondataavailable = (e) => { if (e.data.size) chunks.push(e.data); }; rec.start(250); }
  const wait = (ms: number) => new Promise((r) => setTimeout(r, ms));
  for (const f of frames) {
    if (opts.signal?.aborted) break;
    const t0 = performance.now();
    await drawSvg(canvas, f, paper).catch(() => undefined);
    await wait(Math.max(0, 1000 / fps - (performance.now() - t0)));
  }
  if (!opts.signal?.aborted) await wait(1500); // het eindresultaat even laten staan
  if (!rec) return null;
  const done = new Promise<void>((r) => { rec.onstop = () => r(); });
  rec.stop();
  await done;
  stream!.getTracks().forEach((t) => t.stop());
  return opts.signal?.aborted || !chunks.length ? null : new Blob(chunks, { type: opts.record! });
}
