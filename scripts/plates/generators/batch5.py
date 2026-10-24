"""Batch 5: nieuwe kleurplaten (eigen tekeningen, 200x200)."""
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

def flamingo(sh):
    sh.region("M0 200V172Q100 160 200 172V200Z", "b")
    sh.rect_r(96, 118, 4, 62, "k"); sh.line("M98 140L112 152L104 162")
    sh.region("M66 104C66 78 112 70 132 92C140 102 132 122 108 124C86 126 66 120 66 104Z", "k")
    sh.region("M84 100Q100 86 120 98Q104 110 84 100Z", "m")
    sh.region("M70 96Q44 92 40 112Q58 108 70 106Z", "k")
    sh.region("M124 94C134 70 120 50 112 40Q108 30 118 26", "-") if False else None
    sh.region("M120 96C132 72 116 54 108 44C102 34 110 22 122 24C132 26 134 36 128 40C122 36 116 36 118 44C126 56 140 74 128 100Z", "k")
    sh.region("M124 26Q140 24 142 40Q136 34 126 34Z", "x"); eye(sh, 120, 31, 2)
    sh.region("M0 172Q30 166 60 170", "-") if False else None
def ijsbeer(sh):
    sh.region("M0 200V150L40 140L80 150L130 136L200 148V200Z", "b")
    sh.region("M20 150C20 108 70 92 120 98C160 102 176 124 170 150Z", "-")
    sh.circle_r(60, 98, 26, "-"); sh.circle_r(44, 76, 8, "-"); sh.circle_r(76, 74, 8, "-")
    sh.ellipse_r(54, 108, 12, 9, "-"); sh.ellipse_r(50, 104, 4, 3, "x"); eye(sh, 52, 92); eye(sh, 70, 92)
    sh.rect_r(44, 134, 20, 18, "-", 6); sh.rect_r(130, 134, 20, 18, "-", 6)
    sh.region("M120 20 L122 26 L128 28 L122 30 L120 36 L118 30 L112 28 L118 26Z", "y")
    sh.region("M160 40 L161 44 L165 45 L161 46 L160 50 L159 46 L155 45 L159 44Z", "y")
def zeehond(sh):
    sh.region("M0 200V160Q50 150 100 160T200 160V200Z", "n")
    sh.region("M120 140L176 120L200 128V160H110Z", "z")
    sh.region("M40 150C30 120 60 92 96 100C124 106 140 124 150 140C130 150 80 158 40 150Z", "z")
    sh.circle_r(60, 98, 22, "z"); eye(sh, 52, 92); eye(sh, 66, 92); sh.ellipse_r(58, 104, 5, 3.5, "x")
    sh.line("M50 106H34M50 109L36 114M66 106H82M66 109L80 114")
    sh.region("M146 138Q168 124 176 140Q164 140 156 150Z", "z"); sh.region("M80 140Q74 160 92 156Z", "z")
    sh.circle_r(64, 64, 14, "r"); sh.line("M52 58Q64 66 76 58M56 74Q64 68 72 74")
def koala(sh):
    sh.region("M140 0H164V200H140Z", "w")
    sh.region("M60 190C40 150 60 110 100 108C130 108 146 140 146 190Z", "z")
    sh.circle_r(96, 82, 34, "z"); sh.circle_r(62, 62, 18, "z"); sh.circle_r(130, 62, 18, "z")
    sh.circle_r(62, 62, 9, "k"); sh.circle_r(130, 62, 9, "k")
    sh.ellipse_r(96, 92, 9, 12, "x"); eye(sh, 82, 76); eye(sh, 110, 76); smile(sh, 96, 106, 5)
    sh.ellipse_r(140, 124, 14, 9, "z"); sh.ellipse_r(140, 150, 14, 9, "z")
    for y in (30, 100, 170): sh.region(f"M164 {y}Q186 {y - 16} 196 {y - 4}Q184 {y + 8} 164 {y}Z", "g")
def neushoorn(sh):
    grass(sh, 182)
    sh.region("M60 150C50 110 90 90 140 96C176 100 186 130 176 150Z", "z")
    sh.region("M66 92L62 76L74 90Z", "z")
    sh.region("M74 96C56 86 30 90 20 104C14 116 20 130 36 134C52 138 66 134 74 126Z", "z")
    sh.region("M24 100L12 70L38 96Z", "-"); sh.region("M44 94L42 80L54 92Z", "-")
    eye(sh, 56, 106, 2.6); sh.line("M22 120Q28 124 34 120")
    for x in (72, 96, 140, 160): sh.rect_r(x, 140, 16, 36, "z", 5)
    sh.line("M184 128Q194 132 192 144")
    sh.circle_r(168, 34, 16, "y")
def kameel(sh):
    sh.region("M0 200V170Q60 156 120 168T200 164V200Z", "y")
    sh.region("M50 120C56 84 76 84 86 104C96 70 120 70 128 104C134 110 140 118 140 128H50Z", "w")
    sh.region("M136 124C150 112 150 80 150 66C150 54 170 50 176 62C178 70 170 74 164 72C162 92 160 116 146 134Z", "w")
    eye(sh, 168, 60, 2.2); sh.region("M152 56L148 48L158 54Z", "w")
    for x in (58, 74, 112, 128): sh.rect_r(x, 128, 9, 42, "w", 3)
    sh.line("M52 124Q40 130 42 146")
    sh.circle_r(36, 36, 14, "o")
    sh.region("M20 200V188H40V200", "-") if False else None
def pauw(sh):
    for k in range(9):
        a = math.radians(-160 + k * 17.5)
        x, y = 100 + 82 * math.cos(a), 140 + 82 * math.sin(a)
        sh.region(f"M100 140L{f(100 + 50 * math.cos(a - .18))} {f(140 + 50 * math.sin(a - .18))}Q{f(x)} {f(y)} {f(100 + 50 * math.cos(a + .18))} {f(140 + 50 * math.sin(a + .18))}Z", "t" if k % 2 else "g")
        sh.ellipse_r(100 + 70 * math.cos(a), 140 + 70 * math.sin(a), 6, 6, "n")
    sh.region("M88 176C80 150 86 120 100 104C114 120 120 150 112 176Z", "n")
    sh.circle_r(100, 96, 12, "n"); eye(sh, 104, 94, 2); sh.poly_r([(110, 96), (120, 99), (110, 102)], "y")
    for dx in (-6, 0, 6): sh.line(f"M100 84L{100 + dx} 72"); sh.circle_r(100 + dx, 70, 2.5, "t")
    sh.line("M96 176V194M104 176V194")
def ooievaar(sh):
    sh.region("M0 200V180H200V200Z", "l")
    sh.region("M100 0 V20", "-") if False else None
    sh.region("M60 100C60 70 120 60 150 84C126 104 90 116 60 100Z", "-")
    sh.region("M120 84Q140 80 150 84Q140 104 110 100Z", "x")
    sh.region("M70 96Q40 102 26 118Q52 114 74 106Z", "x")
    sh.region("M60 92C56 72 54 52 60 40C66 30 80 32 82 42C76 40 70 44 70 52C70 66 72 80 76 96Z", "-")
    sh.region("M80 40L112 50L80 46Z", "r"); eye(sh, 70, 40, 2)
    sh.rect_r(94, 108, 3, 72, "r"); sh.line("M110 108L120 140L104 160")
    sh.region("M24 60Q60 50 90 62", "-") if False else None
    sh.circle_r(168, 40, 14, "y")
def vleermuis(sh):
    sh.rect_r(0, 0, 200, 200, "n"); sh.circle_r(150, 50, 28, "y")
    sh.region("M100 96C70 70 40 70 20 90C34 96 34 108 30 118C46 110 58 116 64 126C70 114 86 112 100 116C114 112 130 114 136 126C142 116 154 110 170 118C166 108 166 96 180 90C160 70 130 70 100 96Z", "x")
    sh.circle_r(100, 100, 16, "p"); sh.poly_r([(88, 92), (90, 78), (96, 88)], "p"); sh.poly_r([(112, 92), (110, 78), (104, 88)], "p")
    sh.circle_r(94, 98, 4, "-"); sh.circle_r(106, 98, 4, "-"); eye(sh, 94, 98, 1.6); eye(sh, 106, 98, 1.6)
    sh.poly_r([(96, 108), (98, 113), (100, 108)], "-"); sh.poly_r([(100, 108), (102, 113), (104, 108)], "-")
    for x, y in ((30, 30), (60, 160), (170, 160), (40, 180)): sh.poly_r(star_pts(x, y, 7, 3), "y")
def spin(sh):
    for k in range(8):
        a = math.radians(k * 45); c, si = math.cos(a), math.sin(a)
        t = min([v for v in ((199 - 100) / c if c > 1e-9 else None, (1 - 100) / c if c < -1e-9 else None, (199 - 80) / si if si > 1e-9 else None, (1 - 80) / si if si < -1e-9 else None) if v is not None])
        sh.seg(100, 80, 100 + t * c, 80 + t * si)
    for r in (20, 38, 56, 74):
        sh.line("M" + " L".join(f"{f(100 + r * math.cos(math.radians(k * 45)))} {f(80 + r * math.sin(math.radians(k * 45)))}" for k in range(9)))
    sh.seg(100, 1, 100, 120)
    sh.circle_r(100, 130, 18, "x"); sh.circle_r(100, 108, 11, "x")
    for s in (-1, 1):
        for k in range(4):
            y = 118 + k * 9
            sh.line(f"M{100 + s * 14} {y}Q{100 + s * 32} {y - 14} {100 + s * 40} {y + 6}")
    sh.circle_r(95, 106, 3.5, "-"); sh.circle_r(105, 106, 3.5, "-"); eye(sh, 95, 106, 1.5); eye(sh, 105, 106, 1.5)
    smile(sh, 100, 112, 3)
def bever(sh):
    sh.region("M0 200V160Q100 150 200 160V200Z", "b")
    for k, y in enumerate((150, 134, 118)): sh.rect_r(132 + k * 6, y, 64 - k * 12, 14, "w", 7); sh.circle_r(132 + k * 6 + 6, y + 7, 4, "o")
    sh.region("M20 160C10 140 30 128 50 140Q40 150 44 164Z", "w")
    sh.region("M40 162C30 120 60 92 96 96C130 100 140 136 126 162Z", "w")
    sh.circle_r(88, 82, 26, "w"); sh.circle_r(68, 62, 7, "w"); sh.circle_r(108, 62, 7, "w")
    eye(sh, 80, 76); eye(sh, 96, 76); sh.ellipse_r(88, 88, 6, 4, "x")
    sh.rect_r(83, 96, 10, 9, "-", 1); sh.seg(88, 96, 88, 105)
    sh.ellipse_r(70, 130, 12, 8, "w"); sh.ellipse_r(108, 130, 12, 8, "w")
def mol(sh):
    sh.region("M0 120H200V200H0Z", "w")
    sh.region("M40 120Q100 60 160 120Z", "w")
    sh.region("M70 120C70 92 130 92 130 120Z", "z")
    sh.ellipse_r(100, 104, 8, 6, "k"); sh.line("M86 98Q90 100 94 98M106 98Q110 100 114 98")
    sh.region("M62 124Q56 112 66 108Q74 112 72 124Z", "k"); sh.region("M138 124Q144 112 134 108Q126 112 128 124Z", "k")
    for x, y in ((30, 150), (90, 170), (150, 160), (180, 140), (50, 186)): sh.ellipse_r(x, y, 6, 4, "z")
    sh.region("M140 130Q160 140 180 134Q166 160 150 150Z", "k") if False else None
    sh.line("M120 150Q140 156 150 148Q160 140 170 150")
    sh.circle_r(30, 40, 14, "y"); sh.region("M150 50C140 30 170 26 172 40C186 36 190 56 176 58H150Z", "-")
def kraan(sh):
    grass(sh, 186, "z")
    sh.rect_r(40, 140, 120, 30, "y", 4); sh.rect_r(120, 112, 36, 30, "y", 3); sh.rect_r(126, 118, 14, 14, "b", 2)
    for x in (60, 100, 140): sh.circle_r(x, 172, 13, "x"); sh.circle_r(x, 172, 5, "z")
    sh.region("M60 140L150 30L158 36L74 140Z", "o")
    for k in range(1, 6): sh.seg(60 + k * 15, 140 - k * 18.3, 72 + k * 14.5, 140 - k * 18)
    sh.seg(154, 34, 154, 92); sh.rect_r(146, 92, 16, 12, "r", 2); sh.line("M154 104V112Q154 118 160 116")
def tram(sh):
    sh.seg(0, 20, 200, 20); sh.seg(100, 20, 100, 40); sh.seg(92, 40, 108, 40)
    sh.rect_r(20, 40, 160, 110, "r", 14); sh.rect_r(20, 120, 160, 22, "-", 0)
    for x in (32, 72, 112): sh.rect_r(x, 54, 32, 34, "b", 4)
    sh.rect_r(150, 54, 22, 60, "b", 3); sh.circle_r(160, 132, 5, "y"); sh.circle_r(40, 132, 5, "y")
    for x in (50, 150): sh.circle_r(x, 158, 10, "x")
    sh.rect_r(0, 168, 200, 6, "z"); sh.rect_r(0, 182, 200, 6, "z")
    sh.text(92, 100, "7", 14)
def vuilniswagen(sh):
    grass(sh, 186, "z")
    sh.rect_r(16, 84, 116, 76, "g", 6); sh.rect_r(132, 104, 50, 56, "y", 6); sh.rect_r(146, 112, 26, 20, "b", 3)
    for x in (24, 56, 88): sh.rect_r(x, 96, 26, 52, "l", 3)
    for x in (44, 92, 160): sh.circle_r(x, 164, 14, "x"); sh.circle_r(x, 164, 5, "z")
    sh.rect_r(150, 70, 18, 22, "z", 2); sh.region("M146 70H172L170 64H148Z", "z")
def camper(sh):
    grass(sh, 184)
    sh.region("M16 156V80Q16 64 32 64H140Q172 64 182 104L188 120V156Z", "-")
    sh.rect_r(16, 120, 172, 20, "t", 0)
    sh.rect_r(30, 78, 36, 28, "b", 4); sh.rect_r(76, 78, 24, 52, "o", 3); sh.region("M144 78H156Q170 80 174 104H144Z", "b")
    for x in (50, 150): sh.circle_r(x, 158, 14, "x"); sh.circle_r(x, 158, 5, "z")
    sh.rect_r(40, 52, 80, 12, "z", 3)
    sh.circle_r(30, 30, 12, "y")
def hamburger(sh):
    sh.region("M40 96C40 54 160 54 160 96Z", "o")
    for x, y in ((70, 74), (92, 66), (116, 70), (134, 82), (82, 86), (108, 84)): sh.ellipse_r(x, y, 3, 1.8, "y")
    sh.region("M34 100Q50 92 66 102Q82 92 98 102Q114 92 130 102Q146 92 166 100L162 110H38Z", "l")
    sh.rect_r(40, 108, 120, 16, "w", 6)
    sh.region("M36 122H164L156 134L142 126L126 136L110 126L94 136L78 126L62 136L46 126Z", "y")
    sh.rect_r(38, 128, 124, 10, "r", 4)
    sh.region("M40 140H160C160 160 40 160 40 140Z", "o")
    sh.region("M150 40L156 20L162 40Z", "-") if False else None
    sh.rect_r(98, 28, 4, 34, "w"); sh.poly_r([(102, 28), (122, 34), (102, 40)], "r")
def sushi(sh):
    sh.rect_r(16, 120, 168, 40, "w", 6)
    for x in (50, 100, 150):
        sh.circle_r(x, 100, 22, "x"); sh.circle_r(x, 100, 16, "-"); sh.circle_r(x, 100, 7, "o" if x != 100 else "l")
    sh.region("M60 60C60 48 140 48 140 60V74H60Z", "-"); sh.region("M56 46Q100 30 144 46L140 58Q100 44 60 58Z", "o")
    sh.line("M70 50L76 44M86 46L92 40M104 46L110 40M120 48L126 42")
    sh.line("M150 20L184 70M162 18L192 64")
def ananas(sh):
    for k in range(7):
        a = math.radians(-150 + k * 20); sh.region(f"M100 70Q{f(100 + 30 * math.cos(a - .2))} {f(70 + 30 * math.sin(a - .2))} {f(100 + 50 * math.cos(a))} {f(70 + 50 * math.sin(a))}Q{f(100 + 26 * math.cos(a + .2))} {f(70 + 26 * math.sin(a + .2))} 100 70Z", "g" if k % 2 else "l")
    sh.ellipse_r(100, 128, 44, 58, "y")
    for k in range(-3, 4):
        sh.line(f"M{70 + k * 14} {78}L{130 + k * 14} 186") if False else None
    for k in range(1, 6):
        sh.seg(58 + k * 14, 74, 58 + k * 14 - 40, 74 + 80) if False else None
    for y in (96, 116, 136, 156):
        for x in (80, 100, 120): sh.poly_r([(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)], "o")
def druiven(sh):
    sh.line("M100 40Q104 24 116 18"); sh.region("M104 34C120 20 150 24 156 40C140 46 120 44 104 34Z", "g")
    pts_ = [(84, 54), (106, 54), (128, 54), (74, 76), (96, 76), (118, 76), (140, 76), (84, 98), (106, 98), (128, 98), (94, 120), (116, 120), (104, 142)]
    for x, y in pts_: sh.circle_r(x, y, 12, "p")
    sh.region("M20 170Q100 150 180 170V186H20Z", "w")
def citroen(sh):
    sh.region("M30 100C30 60 100 44 140 64C160 74 170 90 172 100C170 110 160 126 140 136C100 156 30 140 30 100Z", "y")
    sh.ellipse_r(26, 100, 6, 5, "y"); sh.ellipse_r(176, 100, 6, 5, "y")
    sh.region("M110 54C110 34 130 24 150 30C144 44 128 54 110 54Z", "g")
    sh.circle_r(64, 164, 26, "y"); sh.circle_r(64, 164, 21, "-")
    for k in range(8):
        a1, a2 = k * 45 + 4, k * 45 + 41
        sh.region(arc_path(64, 164, 4, 18, a1, a2), "y")
def peer(sh):
    sh.region("M100 40C84 40 82 64 80 82C76 96 50 110 52 146C54 176 80 188 100 188C120 188 146 176 148 146C150 110 124 96 120 82C118 64 116 40 100 40Z", "l")
    sh.line("M100 40Q98 26 106 16"); sh.region("M104 26C116 14 136 18 140 28C126 34 114 32 104 26Z", "g")
    sh.ellipse_r(76, 140, 8, 14, "-")
def vulkaan(sh):
    sh.region("M0 200V184H200V200Z", "w")
    sh.region("M20 184L80 70H120L180 184Z", "w")
    sh.region("M80 70Q100 60 120 70L112 92Q106 80 100 96Q94 82 88 92Z", "r")
    sh.region("M88 92Q84 110 90 130Q96 112 100 96Z", "o"); sh.region("M112 92Q118 116 112 140Q104 116 100 96Z", "o")
    for x, y, r in ((90, 46, 12), (110, 30, 14), (128, 50, 10), (78, 24, 8)): sh.circle_r(x, y, r, "z")
    for x, y in ((60, 40), (148, 30)): sh.circle_r(x, y, 5, "o")
def waterval(sh):
    sh.region("M0 0H70V140H0Z", "z"); sh.region("M130 0H200V140H130Z", "z")
    sh.rect_r(70, 0, 60, 140, "b")
    for x in (80, 92, 104, 116): sh.line(f"M{x} 10V130")
    sh.region("M0 140H200V200H0Z", "n")
    for x in (60, 80, 100, 120, 140): sh.circle_r(x, 142, 9, "-")
    sh.region("M20 160Q40 150 60 160", "-") if False else None
    sh.region("M140 180C130 170 150 160 160 170L176 160V184L160 176C150 188 134 186 140 180Z", "o")
    for x, y in ((20, 120), (40, 100), (170, 110)): sh.region(f"M{x} {y}C{x - 10} {y - 18} {x + 10} {y - 28} {x + 14} {y - 12}C{x + 22} {y - 18} {x + 26} {y - 2} {x + 14} {y}Z", "g")
def kampvuur(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    for x, y in ((30, 30), (80, 20), (150, 40), (180, 16), (110, 50)): sh.poly_r(star_pts(x, y, 6, 2.6), "y")
    sh.circle_r(160, 70, 14, "-")
    sh.region("M0 160H200V200H0Z", "g")
    sh.region("M100 70C120 96 136 110 128 138C122 158 78 158 72 138C64 112 84 100 100 70Z", "o")
    sh.region("M100 100C110 116 116 126 112 140C108 150 92 150 88 140C84 126 94 116 100 100Z", "y")
    sh.raw('<g transform="rotate(-15 100 158)"><rect class="r" x="56" y="150" width="88" height="14" rx="7"/></g>', "w")
    sh.raw('<g transform="rotate(15 100 158)"><rect class="r" x="56" y="150" width="88" height="14" rx="7"/></g>', "w")
    for x in (40, 164): sh.circle_r(x, 168, 8, "z")
def regenwolk(sh):
    sh.region("M40 100A24 24 0 0 1 62 64A32 32 0 0 1 120 52A28 28 0 0 1 164 80A20 20 0 0 1 160 120H52A20 20 0 0 1 40 100Z", "z")
    eye(sh, 88, 92); eye(sh, 120, 92); smile(sh, 104, 104, 7)
    for x, y in ((60, 140), (90, 150), (120, 140), (150, 154), (76, 176), (136, 182), (106, 180)):
        sh.region(f"M{x} {y - 10}C{x + 4} {y - 4} {x + 6} {y} {x + 6} {y + 2}A6 6 0 0 1 {x - 6} {y + 2}C{x - 6} {y} {x - 4} {y - 4} {x} {y - 10}Z", "b")
    sh.region("M150 30L170 30L162 46L174 46L150 72L156 52L144 52Z", "y")
def badeend(sh):
    sh.region("M0 130H200V200H0Z", "b")
    for k in range(5): sh.line(f"M{k * 40} 130Q{k * 40 + 10} 124 {k * 40 + 20} 130T{k * 40 + 40} 130")
    sh.region("M40 120C40 96 80 92 110 104C120 96 136 98 150 108C160 128 140 150 100 150C64 150 40 140 40 120Z", "y")
    sh.circle_r(124, 74, 26, "y")
    sh.region("M146 70Q170 70 172 80Q162 88 146 84Z", "o"); eye(sh, 130, 66)
    sh.region("M60 116Q80 104 100 120Q80 132 60 116Z", "y")
    for x, y in ((40, 40), (64, 26), (170, 30)): sh.circle_r(x, y, 8, "-")
def lamp(sh):
    sh.rect_r(20, 170, 160, 14, "w", 3)
    sh.region("M70 40H130L150 100H50Z", "y")
    sh.rect_r(96, 100, 8, 50, "z"); sh.region("M70 170Q70 150 100 150Q130 150 130 170Z", "z")
    sh.region("M98 40V24", "-") if False else None
    sh.rect_r(140, 140, 30, 30, "r", 3); sh.region("M146 140V128H164V140", "-") if False else None
kp("flamingo", "Flamingo op één poot", "dieren", "4-6", 2, flamingo)
kp("ijsbeer", "IJsbeer op het ijs", "dieren", "4-6", 1, ijsbeer)
kp("zeehond", "Zeehond met een bal", "zee", "4-6", 2, zeehond)
kp("koala", "Koala in een boom", "dieren", "2-4", 1, koala)
kp("neushoorn", "Neushoorn", "dieren", "4-6", 2, neushoorn)
kp("kameel", "Kameel in de woestijn", "dieren", "4-6", 2, kameel)
kp("pauw", "Pauw met open staart", "dieren", "6-9", 2, pauw)
kp("ooievaar", "Ooievaar", "dieren", "4-6", 2, ooievaar)
kp("vleermuis", "Vleermuis bij volle maan", "dieren", "4-6", 2, vleermuis)
kp("spin", "Spin in haar web", "dieren", "4-6", 2, spin)
kp("bever", "Bever bij de dam", "dieren", "4-6", 2, bever)
kp("mol", "Mol uit de molshoop", "dieren", "2-4", 1, mol)
kp("kraanwagen", "Kraanwagen", "voertuigen", "4-6", 2, kraan)
kp("tram", "Tram", "voertuigen", "4-6", 1, tram)
kp("vuilniswagen", "Vuilniswagen", "voertuigen", "4-6", 1, vuilniswagen)
kp("camper", "Camper op vakantie", "voertuigen", "4-6", 1, camper)
kp("hamburger", "Hamburger met vlaggetje", "eten", "2-4", 1, hamburger)
kp("sushi", "Sushi met stokjes", "eten", "6-9", 2, sushi)
kp("ananas", "Ananas", "eten", "2-4", 1, ananas)
kp("druiven", "Tros druiven", "eten", "2-4", 1, druiven)
kp("citroen", "Citroen en schijfje", "eten", "2-4", 1, citroen)
kp("peer", "Peer", "eten", "2-4", 1, peer)
kp("vulkaan", "Vulkaan", "natuur", "4-6", 2, vulkaan)
kp("waterval", "Waterval", "natuur", "6-9", 2, waterval)
kp("kampvuur", "Kampvuur onder de sterren", "natuur", "4-6", 2, kampvuur)
kp("regenwolk", "Vrolijke regenwolk", "natuur", "2-4", 1, regenwolk)
kp("badeend", "Badeend", "thuis", "2-4", 1, badeend)
kp("lamp", "Leeslamp", "thuis", "2-4", 1, lamp)
