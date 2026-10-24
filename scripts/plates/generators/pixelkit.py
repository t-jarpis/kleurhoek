"""Pixelkunst op nummer (gedeeld)."""
import json, os
from lib_gen import *
# ---------- pixelkunst op nummer ----------
HEX = {c["code"]: c["hex"] for c in json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../../packages/catalog-data/colors.json")))}
NAMES = {"r": "rood", "o": "oranje", "y": "geel", "l": "lichtgroen", "g": "groen", "b": "lichtblauw", "n": "blauw", "p": "paars", "m": "roze", "k": "lichtroze", "w": "bruin", "z": "grijs", "x": "zwart"}
def pixel(slug, name, rows, age, diff, cat):
    n_r, n_c = len(rows), len(rows[0])
    assert all(len(r) == n_c for r in rows), (slug, [len(r) for r in rows])
    codes = sorted({c for row in rows for c in row if c != "."}, key=lambda c: "rolygbnpmkwzx".index(c))
    num = {c: i + 1 for i, c in enumerate(codes)}
    s = min(160 / n_c, 170 / n_r); x0 = (200 - n_c * s) / 2; y0 = 42
    def page(ans):
        sh = Sheet(); title(sh, "Zo wordt het" if ans else cap(name.split(": ", 1)[-1]), 16)
        if not ans: sh.text(100, 30, "Kleur elk vakje in de kleur van het cijfer. Lege vakjes blijven wit.", 6)
        for r_, row in enumerate(rows):
            for c_, ch in enumerate(row):
                x, y = x0 + c_ * s, y0 + r_ * s
                if ans and ch != ".": sh.raw(f'<rect x="{f(x)}" y="{f(y)}" width="{f(s)}" height="{f(s)}" style="fill:{HEX[ch]};stroke:#222;stroke-width:.4"/>')
                else: sh.rect_line(x, y, s, s, "l", 0, "stroke-width:.4")
                if ch != "." and not ans: sh.text(x + s / 2, y + s * .7, str(num[ch]), max(4.6, s * .55))
        ly = y0 + n_r * s + 12
        for i, c in enumerate(codes):
            x = 20 + (i % 3) * 60; y = ly + (i // 3) * 12
            sh.text(x, y, f"{num[c]} = {NAMES[c]}", 7, "start")
        return sh
    p1 = page(False)
    write(OUT, slug, p1, {"category": cat, "age": age, "kind": "werkblad", "difficulty": diff, "minutes": 15 + diff * 5,
        "materials": [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}],
        "i18n": {"nl": {"name": name, "steps": [
            "Kijk onder het rooster welke kleur bij welk cijfer hoort.",
            "Kleur elk vakje met een cijfer in die kleur. Werk rij voor rij, dan sla je niets over.",
            "Wat verschijnt er? Op de tweede bladzijde zie je hoe het wordt."]}}}, [("antwoorden", "Zo wordt het", page(True))])
