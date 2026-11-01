"""Drie lijndiktes voor gedetailleerde platen (ADR 0064, design system: PlateInk).

Een generator zet met `obj("naam")` neer bij welk onderwerp de volgende vlakken horen (uil, maan, tak) en met
`part()` waar een nieuw deel van dat onderwerp begint (vleugel, buik, oog). Na `finish` maakt `ink_layer` er
lijnen van:
  - dik (`l3`): de zichtbare omtrek van elk onderwerp;
  - middel (`l2`): de zichtbare omtrek van elk groot deel binnen een onderwerp.
De achtergrond (`obj("bg")`, ook de stand aan het begin) krijgt geen extra lijnen. De vlakken zelf veranderen
niet: kleur-op-nummer, het Atelier en de nummering blijven hetzelfde.

We nemen de vormen van vóór het samenvoegen van snippers, zodat de lijnen glad zijn (geen kartels langs
schubben of veren).
"""
from shapely.geometry import box
from shapely.ops import unary_union

PAGE = box(0, 0, 200, 200)
MIN_PART = 120  # kleinere delen (pupil, glimlichtje, stip) houden de fijne lijn

_state = {"obj": "bg", "gid": 0, "items": None}


def obj(name):
    """Vanaf hier horen de vlakken bij dit onderwerp; "bg" is achtergrond (geen extra lijnen)."""
    _state["obj"] = name
    _state["gid"] += 1


def part():
    """Vanaf hier begint een nieuw deel van het huidige onderwerp (krijgt een middellijn als het groot genoeg is)."""
    _state["gid"] += 1


def reset():
    _state.update(obj="bg", gid=0, items=None)


def install(Canvas):
    """Canvas onthoudt per vlak bij welk onderwerp en deel het hoort. Eén keer aanroepen per generator."""
    if getattr(Canvas, "_ink", False):
        return
    put, put_many, finish = Canvas.put, Canvas.put_many, Canvas.finish

    def tag(code):
        # Patronen bouwen soms zelf een Canvas en geven die vlakken door: dan telt het label van nu.
        return f"{code.split(chr(31))[0]}\x1f{_state['obj']}\x1f{_state['gid']}"

    def put_(self, g, code="-"):
        return put(self, g, tag(code))

    def put_many_(self, pieces):
        return put_many(self, [(g, tag(c)) for g, c in pieces])

    def finish_(self, sh, *a, **k):
        _state["items"] = [(g, c.split("\x1f")) for g, c in self.items]
        n = finish(self, sh, *a, **k)
        sh.codes = [c.split("\x1f")[0] for c in sh.codes]
        return n

    Canvas.put, Canvas.put_many, Canvas.finish, Canvas._ink = put_, put_many_, finish_, True


def _n(v):
    return f"{v:.1f}".rstrip("0").rstrip(".")


def _close(g):
    return g.buffer(.4, join_style=2).buffer(-.4, join_style=2)


def _paths(geom, clip):
    b = geom.boundary.intersection(clip)
    out = []
    for ls in getattr(b, "geoms", [b]):
        if hasattr(ls, "coords") and len(ls.coords) > 1:
            out.append("M" + " L".join(f"{_n(x)} {_n(y)}" for x, y in ls.coords))
    return out


def ink_layer(page=PAGE):
    """De <g class="ink"> met de middel- en dikke lijnen, of "" als de plaat geen onderwerpen heeft."""
    items = _state["items"] or []
    objects, parts = {}, {}
    for g, (_code, o, gid) in items:
        if o == "bg":
            continue
        objects.setdefault(o, []).append(g)
        parts.setdefault((o, gid), []).append(g)
    if not objects:
        return ""
    clip = page.buffer(-.6)
    whole = {o: _close(unary_union(v)).simplify(.12) for o, v in objects.items()}
    mid, bold = [], []
    for (o, _gid), v in parts.items():
        u = _close(unary_union(v)).simplify(.12)
        if u.area < MIN_PART or u.symmetric_difference(whole[o]).area < 1:
            continue
        mid += _paths(u, clip)
    for u in whole.values():
        bold += _paths(u, clip)
    reset()
    return ('<g class="ink">' + "".join(f'<path class="l l2" d="{d}"/>' for d in mid)
            + "".join(f'<path class="l l3" d="{d}"/>' for d in bold) + "</g>")
