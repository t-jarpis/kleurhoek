"""Batch 11: bouwplaten van veelvlakken, uitgerekend vanuit een 3D-model (zie polyhedra.py)."""
from lib_gen import *
import polyhedra as ph

MAT = [{"slug": "kleurpotloden"}, {"slug": "kinderschaar"}, {"slug": "lijmstift"}, {"slug": "stevig-papier", "optional": True}]
def bp(slug, name, sub, model, age, diff, minutes, cat="vormen", codes=None, extra_step=None):
    verts, faces = model
    sh = Sheet(); title(sh, cap(name.split(": ", 1)[-1]), 16); sh.text(100, 27, sub, 6.5)
    pal = codes or "rybgotpmnk"
    cs = [pal[i % len(pal)] for i in range(len(faces))]
    ph.draw(sh, verts, faces, cs, (12, 36, 176, 222))
    sh.legend(["cut", "fold", "glue"], 274)
    steps = ["Kleur de vlakken in. Knip de bouwplaat uit langs de doorgetrokken lijnen; de grijze flapjes blijven eraan.",
             "Vouw alle stippellijnen en flapjes naar binnen (de tekening blijft buiten). Kras ze eerst met een lege balpen en een liniaal, dan vouwt het strakker.",
             "Plak de flapjes één voor één vast, aan de binnenkant van de rand ernaast. Begin bij de flapjes die het verst van het laatste vlak af zitten.",
             extra_step or "Het laatste vlak sluit je als deksel: druk de flapjes van buitenaf aan tot de lijm droog is."]
    write(OUT, slug, sh, {"category": cat, "age": age, "kind": "bouwplaat", "difficulty": diff, "minutes": minutes, "paperGsm": 160, "adultHelp": age in ("6-9",),
        "materials": MAT, "i18n": {"nl": {"name": name, "printNote": "Op stevig papier (160 gram) wordt hij het mooist.", "steps": steps}}})

bp("zeshoekig-prisma", "Bouwplaat: zeshoekig doosje", "Een doosje met zes kanten, zoals een honingraatcel.", ph.prism(6, 1, 1.4), "6-9", 2, 30, codes="yyoooooo")
bp("achthoekig-prisma", "Bouwplaat: achthoekige toren", "Acht wanden en een achthoekig dak en bodem.", ph.prism(8, 1, 2.2), "9+", 2, 35, codes="zznbnbnbnb")
bp("vijfhoekige-piramide", "Bouwplaat: vijfhoekige piramide", "Vijf driehoeken rond een vijfhoek.", ph.pyramid(5, 1, 1.4), "9+", 2, 25, codes="yrogbp")
bp("afgeknotte-piramide", "Bouwplaat: afgeknotte piramide", "Een piramide zonder punt, zoals een bloempotje.", ph.frustum(4, 1, .6, .9), "9+", 2, 30, codes="wwoooo")
bp("zesvlak-dubbele-piramide", "Bouwplaat: dubbele driehoekpiramide", "Zes driehoeken: twee piramides met de bodems tegen elkaar.", ph.bipyramid(3, 1, 1.2), "9+", 2, 25, codes="rbyrby")
bp("antiprisma", "Bouwplaat: vierkant antiprisma", "Twee vierkanten met een band van driehoeken.", ph.antiprism(4), "12+", 3, 40, codes="pptmtmtmtm")
bp("kuboctaeder", "Bouwplaat: kuboctaëder", "Acht driehoeken en zes vierkanten: half kubus, half achtvlak.", ph.cuboctahedron(), "12+", 3, 50)
bp("afgeknot-viervlak", "Bouwplaat: afgeknot viervlak", "Een viervlak met afgezaagde punten.", ph.truncated_tetrahedron(), "12+", 3, 45)
