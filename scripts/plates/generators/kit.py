"""Hulpjes om conceptplaten te maken voor scripts/plates/ingest.mjs (ADR 0027)."""
import json, math, os, random

W = 200
A4 = 280  # hoogte van een staand A4-vel in de viewBox (breedte 200)

def f(v):
    return f"{v:.1f}".rstrip("0").rstrip(".") if isinstance(v, float) else str(v)

def pts(points):
    return " ".join(f"{f(float(x))} {f(float(y))}" for x, y in points)

class Sheet:
    def __init__(self, height=A4):
        self.h = height
        self.parts = []
        self.codes = []
    # vlak om in te kleuren
    def region(self, d, code="-"):
        self.parts.append(f'<path class="r" d="{d}"/>'); self.codes.append(code)
    def circle_r(self, cx, cy, r, code="-"):
        self.parts.append(f'<circle class="r" cx="{f(float(cx))}" cy="{f(float(cy))}" r="{f(float(r))}"/>'); self.codes.append(code)
    def ellipse_r(self, cx, cy, rx, ry, code="-"):
        self.parts.append(f'<ellipse class="r" cx="{f(float(cx))}" cy="{f(float(cy))}" rx="{f(float(rx))}" ry="{f(float(ry))}"/>'); self.codes.append(code)
    def poly_r(self, points, code="-"):
        self.region("M" + " L".join(f"{f(float(x))} {f(float(y))}" for x, y in points) + "Z", code)
    def rect_r(self, x, y, w, h, code="-", rx=0):
        if rx:
            self.parts.append(f'<rect class="r" x="{f(float(x))}" y="{f(float(y))}" width="{f(float(w))}" height="{f(float(h))}" rx="{f(float(rx))}"/>'); self.codes.append(code)
        else:
            self.poly_r([(x, y), (x + w, y), (x + w, y + h), (x, y + h)], code)
    # lijnen
    def line(self, d, cls="l", style=None):
        s = f' style="{style}"' if style else ""
        self.parts.append(f'<path class="{cls}" d="{d}"{s}/>')
    def seg(self, x1, y1, x2, y2, cls="l", style=None):
        self.line(f"M{f(float(x1))} {f(float(y1))}L{f(float(x2))} {f(float(y2))}", cls, style)
    def rect_line(self, x, y, w, h, cls="l", rx=0, style=None):
        s = f' style="{style}"' if style else ""
        r = f' rx="{f(float(rx))}"' if rx else ""
        self.parts.append(f'<rect class="{cls}" x="{f(float(x))}" y="{f(float(y))}" width="{f(float(w))}" height="{f(float(h))}"{r}{s} fill="none"/>')
    def circle_line(self, cx, cy, r, cls="l", style=None):
        s = f' style="{style}"' if style else ""
        self.parts.append(f'<circle class="{cls}" cx="{f(float(cx))}" cy="{f(float(cy))}" r="{f(float(r))}" fill="none"{s}/>')
    def dot(self, cx, cy, r=1.4):
        self.parts.append(f'<circle class="dot" cx="{f(float(cx))}" cy="{f(float(cy))}" r="{f(float(r))}"/>')
    def text(self, x, y, s, size=8, anchor="middle", cls="tx", rotate=None, weight=None):
        t = f' transform="rotate({rotate} {f(float(x))} {f(float(y))})"' if rotate is not None else ""
        w = f' font-weight="{weight}"' if weight else ""
        s = s.replace("&", "&amp;").replace("<", "&lt;")
        self.parts.append(f'<text class="{cls}" x="{f(float(x))}" y="{f(float(y))}" font-size="{f(float(size))}" text-anchor="{anchor}"{t}{w}>{s}</text>')
    def tip(self, x, y, s, anchor="start"):
        self.text(x, y, s, 6, anchor, "tip")
    def raw(self, s, code=None):
        self.parts.append(s)
        if code is not None: self.codes.append(code)
    def legend(self, items, y=None):
        """Uitleg van de lijnen onderaan (knippen, vouwen, lijmen)."""
        y = y if y is not None else self.h - 8
        x = 20
        for kind in items:
            if kind == "cut": self.seg(x, y - 2, x + 14, y - 2, "cut"); self.tip(x + 17, y, "knippen")
            if kind == "fold": self.seg(x, y - 2, x + 14, y - 2, "fold"); self.tip(x + 17, y, "vouwen")
            if kind == "glue": self.raw(f'<rect class="glue" x="{x}" y="{y-5}" width="10" height="6"/>'); self.tip(x + 13, y, "lijmen")
            x += 52
    def svg(self):
        return f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 {self.h}">' + "".join(self.parts) + "</svg>"

def write(outdir, slug, sheet, meta, pages=()):
    os.makedirs(outdir, exist_ok=True)
    meta = dict(meta)
    meta.setdefault("world", None); meta.setdefault("holiday", None)
    meta["height"] = sheet.h
    meta["codes"] = "".join(sheet.codes)
    nl = meta["i18n"]["nl"]; nl.setdefault("word", None); nl.setdefault("countQuestion", None)
    if pages:
        meta["pages"] = [{"role": role, "height": pg.h} for role, _, pg in pages]
        nl["pageTitles"] = [title for _, title, _ in pages]
        for i, (_, _, pg) in enumerate(pages):
            open(os.path.join(outdir, f"{slug}.p{i+2}.svg"), "w").write(pg.svg())
    open(os.path.join(outdir, f"{slug}.svg"), "w").write(sheet.svg())
    json.dump(meta, open(os.path.join(outdir, f"{slug}.json"), "w"), ensure_ascii=False, indent=1)

def title(sheet, s, y=16, size=11):
    sheet.text(100, y, s, size)

def arc_path(cx, cy, r1, r2, a1, a2):
    """Ringsegment van hoek a1 tot a2 (graden), tussen straal r1 en r2."""
    def p(r, a): return cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))
    x1, y1 = p(r2, a1); x2, y2 = p(r2, a2); x3, y3 = p(r1, a2); x4, y4 = p(r1, a1)
    large = 1 if (a2 - a1) > 180 else 0
    if r1 <= 0:
        return f"M{f(cx)} {f(cy)}L{f(x1)} {f(y1)}A{f(r2)} {f(r2)} 0 {large} 1 {f(x2)} {f(y2)}Z"
    return f"M{f(x1)} {f(y1)}A{f(r2)} {f(r2)} 0 {large} 1 {f(x2)} {f(y2)}L{f(x3)} {f(y3)}A{f(r1)} {f(r1)} 0 {large} 0 {f(x4)} {f(y4)}Z"
