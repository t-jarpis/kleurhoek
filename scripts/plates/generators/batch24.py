"""Batch 24: Archimedische lichamen als bouwplaat (uitslag gezocht zonder overlap, zie polyhedra.search)."""
import itertools, math
from lib_gen import *
import polyhedra as ph

def perms_sign(base):
    out = set()
    for p in itertools.permutations(range(3)):
        for s in itertools.product((1, -1), repeat=3): out.add(tuple(base[p[i]] * s[i] for i in range(3)))
    return sorted(out)
r2 = math.sqrt(2)
MAT = [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "stevig-papier", "optional": True}]
def arch(slug, name, sub, verts, colors_by_sides, minutes):
    v, f = ph.hull_faces(verts)
    codes = [colors_by_sides[len(fc)] for fc in f]
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 27, sub, 6.5)
    ph.draw(sh, v, f, codes, (8, 34, 184, 228), find=True, depth=.16)
    sh.legend(["cut", "fold", "glue"], 274)
    write(OUT, slug, sh, {"category": "vormen", "age": "12+", "kind": "bouwplaat", "difficulty": 3, "minutes": minutes, "paperGsm": 160,
        "materials": MAT, "i18n": {"nl": {"name": name, "printNote": "Gebruik stevig papier (160 gram) en een liniaal om de vouwlijnen te krassen.", "steps": [
            "Kleur de vlakken: alle vlakken met hetzelfde aantal hoeken in dezelfde kleur geeft het mooiste patroon.",
            "Knip de bouwplaat uit langs de doorgetrokken lijnen; de grijze flapjes blijven eraan.",
            "Kras alle stippellijnen met een lege balpen langs een liniaal en vouw ze naar binnen, ook de flapjes.",
            "Plak de flapjes één voor één, steeds aan de rand die ernaast komt te liggen. Werk rondom en sluit als laatste het vlak dat nog open is."]}}})
arch("afgeknot-achtvlak", "Bouwplaat: afgeknot achtvlak", "Zes vierkanten en acht zeshoeken.", perms_sign((0, 1, 2)), {4: "o", 6: "b"}, 50)
arch("afgeknotte-kubus", "Bouwplaat: afgeknotte kubus", "Zes achthoeken en acht driehoeken.", perms_sign((r2 - 1, 1, 1)), {3: "y", 8: "g"}, 50)
arch("ruitkuboctaeder", "Bouwplaat: ruitkuboctaëder", "Achttien vierkanten en acht driehoeken: bijna een bal.", perms_sign((1, 1, 1 + r2)), {3: "r", 4: "k"}, 75)
