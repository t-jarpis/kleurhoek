"""Illustratiekit (ADR 0090): schattige, getekende platen in plaats van losse rechthoeken en cirkels.

- `smooth(punten)`: vloeiende vorm door punten (Catmull-Rom naar Bezier), met een licht trillende lijn zodat het
  niet wiskundig glad oogt (`wob`, vaste seed: dezelfde punten geven altijd dezelfde tekening).
- `blob`, `cloud`, `leaf`, `fern`, `tuft`, `eye`: vaste onderdelen in één stijl.
- `R(d, code)`: een vlak om in te kleuren, met de kleurcode voor kleur-op-nummer ("-" = geen nummer).
- `O(d, code)`: hoofdvorm van een figuur: een vlak plus een inktrand die aan de schaduwkant (rechtsonder) dikker
  wordt. De rand is een zwarte vorm (`dot`), geen vlak, dus hij telt niet mee als vlak en niet voor de nummers.
- `L2(d)`: detaillijn als penseelstreek (dun begin, dikker midden, dun einde), ook als zwarte vorm.
Alle vlakken blijven gesloten, zodat online kleuren, kleur-op-nummer en het voorbeeld werken.
"""
import math
import random
import re

_codes = []


def reset():
    _codes.clear()


def codes():
    return "".join(_codes)


class P(str):
    pts = None


def _bez(p0, c1, c2, p1, n=10):
    out = []
    for k in range(n):
        t = k / n
        u = 1 - t
        out.append((u**3 * p0[0] + 3 * u * u * t * c1[0] + 3 * u * t * t * c2[0] + t**3 * p1[0],
                    u**3 * p0[1] + 3 * u * u * t * c1[1] + 3 * u * t * t * c2[1] + t**3 * p1[1]))
    return out


def smooth(pts, closed=True, t=0.5, wob=0.35, seed=None):
    rnd = random.Random(seed if seed is not None else int(sum(x * 31 + y * 17 for x, y in pts)) & 0xFFFF)
    if wob:
        pts = [(x + rnd.uniform(-wob, wob), y + rnd.uniform(-wob, wob)) for x, y in pts]
    n = len(pts)
    d = f"M{pts[0][0]:.1f} {pts[0][1]:.1f}"
    dense = []
    for i in (range(n) if closed else range(n - 1)):
        p0 = pts[(i - 1) % n] if closed or i > 0 else pts[i]
        p1, p2 = pts[i], pts[(i + 1) % n]
        p3 = pts[(i + 2) % n] if closed or i + 2 < n else p2
        c1 = (p1[0] + (p2[0] - p0[0]) * t / 3, p1[1] + (p2[1] - p0[1]) * t / 3)
        c2 = (p2[0] - (p3[0] - p1[0]) * t / 3, p2[1] - (p3[1] - p1[1]) * t / 3)
        d += f" C{c1[0]:.1f} {c1[1]:.1f} {c2[0]:.1f} {c2[1]:.1f} {p2[0]:.1f} {p2[1]:.1f}"
        dense += _bez(p1, c1, c2, p2)
    out = P(d + (" Z" if closed else ""))
    out.pts = dense
    return out


def blob(cx, cy, rx, ry, n=10, wob=0.0, rot=0.0, seed=1):
    pts = []
    for i in range(n):
        a = 2 * math.pi * i / n + rot
        w = 1 + wob * math.sin(i * 2.3 + seed)
        pts.append((cx + rx * w * math.cos(a), cy + ry * w * math.sin(a)))
    return smooth(pts, seed=seed + int(cx * 7 + cy))


def R(d, code="-"):
    _codes.append(code)
    return f'<path class="r" d="{d}"/>'


def C(x, y, r, code="-"):
    _codes.append(code)
    return f'<circle class="r" cx="{x}" cy="{y}" r="{r}"/>'


def D(x, y, r):
    return f'<circle class="dot" cx="{x}" cy="{y}" r="{r}"/>'


def L(d):
    return f'<path class="l" d="{d}"/>'


def _normals(pts):
    n = len(pts)
    area = sum(pts[i][0] * pts[(i + 1) % n][1] - pts[(i + 1) % n][0] * pts[i][1] for i in range(n))
    sgn = 1 if area > 0 else -1
    out = []
    for i in range(n):
        a, b = pts[(i - 1) % n], pts[(i + 1) % n]
        dx, dy = b[0] - a[0], b[1] - a[1]
        ln = math.hypot(dx, dy) or 1
        out.append((sgn * dy / ln, -sgn * dx / ln))
    return out


def weight(d, w=2.4, light=(-0.55, -0.85)):
    pts = d.pts
    outer = []
    for (x, y), (nx, ny) in zip(pts, _normals(pts)):
        k = max(0.0, -(nx * light[0] + ny * light[1])) ** 1.4
        outer.append((x + nx * (1.0 + w * k), y + ny * (1.0 + w * k)))
    ring = ("M" + " L".join(f"{x:.1f} {y:.1f}" for x, y in outer) + " Z M"
            + " L".join(f"{x:.1f} {y:.1f}" for x, y in reversed(pts)) + " Z")
    return f'<path class="dot" fill-rule="evenodd" d="{ring}"/>'


def O(d, code="-"):
    return R(d, code) + weight(d)


def _sample(dstr):
    toks = re.findall(r"[MLQ]|-?\d+\.?\d*", dstr)
    subs, i, cur, pos = [], 0, None, None
    while i < len(toks):
        c = toks[i]
        i += 1
        if c == "M":
            pos = (float(toks[i]), float(toks[i + 1]))
            i += 2
            cur = [pos]
            subs.append(cur)
        elif c == "L":
            p = (float(toks[i]), float(toks[i + 1]))
            i += 2
            cur += [(pos[0] + (p[0] - pos[0]) * k / 6, pos[1] + (p[1] - pos[1]) * k / 6) for k in range(1, 7)]
            pos = p
        elif c == "Q":
            c1 = (float(toks[i]), float(toks[i + 1]))
            p = (float(toks[i + 2]), float(toks[i + 3]))
            i += 4
            cur += [((1 - t) ** 2 * pos[0] + 2 * (1 - t) * t * c1[0] + t * t * p[0],
                     (1 - t) ** 2 * pos[1] + 2 * (1 - t) * t * c1[1] + t * t * p[1]) for t in [k / 10 for k in range(1, 11)]]
            pos = p
    return subs


def L2(dstr, w=1.5):
    out = []
    for pts in _sample(dstr):
        n = len(pts)
        if n < 2:
            continue
        left, right = [], []
        for i, (x, y) in enumerate(pts):
            a, b = pts[max(i - 1, 0)], pts[min(i + 1, n - 1)]
            dx, dy = b[0] - a[0], b[1] - a[1]
            ln = math.hypot(dx, dy) or 1
            ww = 0.25 + (w / 2) * math.sin(math.pi * i / (n - 1)) ** 0.6
            left.append((x - dy / ln * ww, y + dx / ln * ww))
            right.append((x + dy / ln * ww, y - dx / ln * ww))
        poly = left + list(reversed(right))
        out.append("M" + " L".join(f"{x:.2f} {y:.2f}" for x, y in poly) + " Z")
    return f'<path class="dot" d="{" ".join(out)}"/>'


def eye(x, y, look=(0, 0), s=1.0):
    lx, ly = look
    return [R(blob(x, y, 8.5 * s, 10.5 * s, 12)), D(x + lx * s, y + ly * s, 6.4 * s),
            C(round(x + lx * s + 2.4 * s, 1), round(y + ly * s - 2.6 * s, 1), round(2.3 * s, 1)),
            C(round(x + lx * s - 2.2 * s, 1), round(y + ly * s + 2.4 * s, 1), round(1.1 * s, 1))]


def leaf(x0, y0, x1, y1, w, code="g", vein=True):
    dx, dy = x1 - x0, y1 - y0
    ln = math.hypot(dx, dy)
    nx, ny = -dy / ln, dx / ln
    m = lambda f, s: (x0 + dx * f + nx * w * s, y0 + dy * f + ny * w * s)
    shape = smooth([(x0, y0), m(.3, .9), m(.65, .75), (x1, y1), m(.65, -.75), m(.3, -.9)])
    veinpath = f"M{x0:.1f} {y0:.1f} Q{x0 + dx * .5 + nx * w * .1:.1f} {y0 + dy * .5 + ny * w * .1:.1f} {x0 + dx * .85:.1f} {y0 + dy * .85:.1f}"
    return [R(shape, code)] + ([L2(veinpath)] if vein else [])


def fern(x, y, x1, y1, n=6, w=6, code="g"):
    out = [L2(f"M{x} {y} Q{(x + x1) / 2 + 4} {(y + y1) / 2} {x1} {y1}")]
    for i in range(1, n + 1):
        f = i / (n + 1)
        px, py = x + (x1 - x) * f, y + (y1 - y) * f
        ww = w * (1 - f * .6)
        for sgn in (-1, 1):
            out += leaf(px, py, px + sgn * ww * 1.5, py - ww * 1.0, ww * .6, code, vein=False)
    return out


def tuft(x, y, h=8):
    return L2(f"M{x - 4} {y} Q{x - 3} {y - h * .6} {x - 6} {y - h} M{x} {y} Q{x} {y - h * .7} {x + 1} {y - h * 1.15} "
              f"M{x + 4} {y} Q{x + 4} {y - h * .6} {x + 7} {y - h * .9}")


def cloud(x, y, s=1, code="-"):
    return R(smooth([(x, y), (x - 4 * s, y - 6 * s), (x + 2 * s, y - 12 * s), (x + 10 * s, y - 12 * s), (x + 15 * s, y - 18 * s),
                     (x + 26 * s, y - 16 * s), (x + 30 * s, y - 9 * s), (x + 37 * s, y - 7 * s), (x + 36 * s, y), (x + 18 * s, y + 2 * s)]), code)


def scales(pts, r=2.2):
    return L2(" ".join(f"M{x - r:.1f} {y:.1f} Q{x:.1f} {y + r * 1.2:.1f} {x + r:.1f} {y:.1f}" for x, y in pts))


def flower(x, y, petal="k", heart="y"):
    return [C(x - 4, y, 3.4, petal), C(x + 4, y, 3.4, petal), C(x, y - 4, 3.4, petal), C(x, y + 4, 3.4, petal), C(x, y, 2.4, heart)]
