"""Hulpjes voor kleurplaten (200x200)."""
import math
from lib_gen import *

MAT = [{"slug": "kleurpotloden"}, {"slug": "stiften", "optional": True}, {"slug": "waskrijtjes", "optional": True}]
def kp(slug, name, cat, age, diff, draw, holiday=None):
    sh = Sheet(200); draw(sh)
    meta = {"category": cat, "age": age, "kind": "kleurplaat", "difficulty": diff, "materials": MAT, "i18n": {"nl": {"name": name}}}
    if holiday: meta["holiday"] = holiday
    write(OUT, slug, sh, meta)
def grass(sh, y=184, code="l"):
    sh.region(f"M0 200V{y}Q50 {y - 8} 100 {y}T200 {y}V200Z", code)
def eye(sh, x, y, r=3): sh.dot(x, y, r)
def smile(sh, x, y, w=6): sh.line(f"M{x - w} {y}Q{x} {y + w * .8} {x + w} {y}")

