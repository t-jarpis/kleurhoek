"""Batch 8: kleurplaten (dieren, zee, eten, muziek, vervoer, natuur)."""
import math
from lib_gen import *
from batch5_kit import kp, grass, eye, smile

def gorilla(sh):
    grass(sh, 184, "g")
    sh.region("M40 184C30 130 60 96 100 96C140 96 170 130 160 184Z", "x")
    sh.region("M70 184C70 150 84 132 100 132C116 132 130 150 130 184Z", "z")
    sh.region("M40 140C24 150 20 176 30 184H54C50 170 52 156 58 146Z", "x"); sh.region("M160 140C176 150 180 176 170 184H146C150 170 148 156 142 146Z", "x")
    sh.circle_r(100, 78, 34, "x"); sh.region("M76 76C76 62 124 62 124 76C124 98 112 108 100 108C88 108 76 98 76 76Z", "z")
    sh.circle_r(88, 74, 4, "-"); sh.circle_r(112, 74, 4, "-"); eye(sh, 88, 74, 2); eye(sh, 112, 74, 2)
    sh.line("M94 88Q100 84 106 88"); sh.line("M90 98Q100 104 110 98")
    sh.circle_r(66, 72, 7, "x"); sh.circle_r(134, 72, 7, "x")
    for x in (20, 180): sh.region(f"M{x} 184C{x - 10} 150 {x + 10} 130 {x} 100C{x + 14} 130 {x + 6} 160 {x + 8} 184Z", "g")
def jachtluipaard(sh):
    sh.region("M0 186Q100 176 200 186V200H0Z", "y")
    sh.region("M50 120C50 100 80 92 120 96C150 98 160 110 160 124C150 136 70 138 50 120Z", "y")
    sh.region("M158 112C176 96 186 108 190 120C178 116 170 120 160 126Z", "y")
    sh.circle_r(44, 96, 20, "y"); sh.circle_r(32, 80, 5, "y"); sh.circle_r(56, 80, 5, "y")
    eye(sh, 38, 94, 2.2); eye(sh, 52, 94, 2.2); sh.ellipse_r(45, 104, 3.5, 2.6, "x")
    sh.line("M38 96Q34 106 38 112M52 96Q56 106 52 112")
    for x1, x2 in ((62, 50), (80, 84), (124, 116), (146, 152)): sh.line(f"M{x1} 124L{x2} 184")
    for x, y in ((80, 108), (96, 104), (112, 110), (130, 104), (100, 120), (140, 118), (68, 112), (120, 122), (172, 108)): sh.circle_r(x, y, 3, "x")
def axolotl(sh):
    sh.region("M0 160Q100 150 200 160V200H0Z", "w")
    sh.region("M60 130C60 100 140 100 160 120C176 130 190 130 196 120C194 140 176 146 160 140C140 150 70 150 60 130Z", "k")
    sh.ellipse_r(56, 110, 30, 24, "k")
    for s in (-1, 1):
        for k in range(3):
            yy = 110 + s * (14 + k * 6)
            sh.region(f"M{40 - k * 2} {f(110 + s * 12)}Q{30 - k * 8} {f(yy + s * 6)} {22 - k * 4} {f(yy)}Q{32 - k * 6} {f(yy - s * 2)} {42 - k * 2} {f(110 + s * 8)}Z", "m")
    eye(sh, 46, 104, 3); eye(sh, 68, 104, 3); smile(sh, 57, 116, 8)
    for x in (80, 140): sh.region(f"M{x} 140L{x - 6} 156H{x + 10}L{x + 8} 140Z", "k")
def kameleon(sh):
    sh.line("M0 150H140Q170 150 190 130"); sh.line("M0 156H140Q174 156 196 134")
    for x in (40, 100, 160): sh.region(f"M{x} 150C{x - 12} 130 {x + 6} 120 {x + 14} 132C{x + 10} 140 {x + 4} 146 {x + 6} 150Z", "g")
    sh.region("M40 130C40 100 70 84 110 88C130 90 150 100 150 120C150 134 130 142 110 142H70C54 142 40 140 40 130Z", "l")
    sh.region("M40 130Q20 120 22 100Q22 86 36 92Q30 104 46 118Z", "l")
    sh.region("M150 120C160 110 176 108 184 118C180 132 166 136 150 132Z", "l"); sh.circle_r(164, 116, 7, "y"); eye(sh, 165, 116, 2.4)
    sh.region("M112 142C112 128 104 118 102 110C110 110 120 128 124 142Z", "l") if False else None
    for k, x in enumerate((60, 80, 100, 120)): sh.region(f"M{x} 92Q{x + 10} 110 {x} 140Q{x + 18} 116 {x + 16} 90Z", "gtyo"[k % 4])
    sh.line("M70 142L64 150M120 142L126 150")
    sh.line("M184 122Q196 126 194 140Q190 150 200 152") if False else None
    sh.region("M180 124L198 108L196 116Z", "k")
def specht(sh):
    sh.rect_r(110, 0, 50, 200, "w")
    for y in (30, 80, 140): sh.line(f"M116 {y}Q130 {y + 6} 120 {y + 14}M150 {y + 20}Q142 {y + 28} 154 {y + 34}")
    sh.circle_r(134, 120, 9, "x")
    sh.region("M70 150C56 120 64 86 88 76C104 72 112 90 110 120L104 160Z", "x")
    sh.region("M86 96C80 112 82 132 90 146L102 140C98 120 98 104 96 94Z", "-")
    sh.circle_r(92, 66, 16, "-"); sh.region("M82 52C86 44 100 44 104 52Z", "r"); eye(sh, 96, 64, 2.4)
    sh.region("M106 66L130 64L106 72Z", "z"); sh.region("M70 150L60 184L76 170L80 154Z", "x")
    sh.line("M104 120L112 124M104 134L112 138")
def ijsvogel(sh):
    sh.region("M0 150H200V200H0Z", "b"); sh.line("M10 120H190")
    sh.region("M70 120C66 96 80 76 104 74C126 72 138 90 136 110C134 120 120 126 104 124C92 124 76 124 70 120Z", "n")
    sh.region("M86 108C90 98 112 96 124 104C120 116 104 122 90 118Z", "o")
    sh.circle_r(100, 70, 18, "n"); sh.region("M110 76C114 84 104 90 96 84Z", "-"); eye(sh, 104, 66, 2.6)
    sh.region("M116 68L150 70L116 74Z", "x"); sh.region("M70 112L46 130L66 126Z", "n")
    sh.line("M96 124V132M106 124V132")
    sh.region("M140 170Q150 160 164 170Q150 178 140 170Z", "z")
def rog(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region("M100 50C120 60 180 80 196 110C170 106 140 120 120 130C112 150 106 170 100 196C94 170 88 150 80 130C60 120 30 106 4 110C20 80 80 60 100 50Z", "z")
    sh.region("M88 58L82 44M112 58L118 44", "-") if False else None
    sh.line("M90 56Q86 46 80 44M110 56Q114 46 120 44")
    eye(sh, 90, 66, 2.6); eye(sh, 110, 66, 2.6); smile(sh, 100, 80, 7)
    for x, y, r in ((40, 40, 4), (160, 30, 5), (150, 160, 4), (40, 160, 6)): sh.circle_r(x, y, r, "-")
def narwal(sh):
    sh.region("M0 150Q50 140 100 150T200 150V200H0Z", "n")
    sh.region("M40 120C40 90 90 80 130 92C150 98 160 110 160 120C160 132 140 140 110 140C80 140 40 136 40 120Z", "z")
    sh.region("M40 120L12 100L20 120L10 140Z", "z")
    sh.region("M152 104L196 70L156 112Z", "y")
    for k in range(4): sh.seg(160 + k * 9, 102 - k * 7, 164 + k * 9, 106 - k * 7)
    eye(sh, 140, 112, 2.6); smile(sh, 148, 124, 5); sh.region("M96 136Q90 150 106 148Z", "z")
    for x, y in ((60, 104), (84, 100), (104, 112), (74, 120)): sh.circle_r(x, y, 3, "-")
def kogelvis(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.circle_r(100, 100, 52, "y")
    for k in range(16):
        a = math.radians(k * 22.5); x, y = 100 + 52 * math.cos(a), 100 + 52 * math.sin(a)
        sh.poly_r([(100 + 50 * math.cos(a - .1), 100 + 50 * math.sin(a - .1)), (100 + 64 * math.cos(a), 100 + 64 * math.sin(a)), (100 + 50 * math.cos(a + .1), 100 + 50 * math.sin(a + .1))], "y")
    sh.circle_r(82, 88, 10, "-"); sh.circle_r(118, 88, 10, "-"); eye(sh, 84, 90, 4); eye(sh, 116, 90, 4)
    sh.circle_r(100, 118, 7, "r")
    sh.region("M152 100L184 80V120Z", "o")
    for x, y in ((30, 30), (170, 160), (40, 170)): sh.circle_r(x, y, 6, "-")
def donut(sh):
    sh.circle_r(100, 100, 70, "o"); sh.region("M40 92C40 50 160 50 160 92C164 110 150 118 140 112C130 130 112 120 100 130C88 120 70 132 60 116C46 122 38 108 40 92Z", "m")
    sh.circle_r(100, 96, 20, "-")
    for x, y, rot, c in ((60, 80, 30, "y"), (80, 66, -20, "b"), (120, 64, 60, "g"), (140, 84, -40, "r"), (70, 104, 10, "b"), (132, 104, 70, "y"), (104, 70, 0, "r")):
        sh.raw(f'<rect class="r" x="{x - 5}" y="{y - 1.5}" width="10" height="3" rx="1.5" transform="rotate({rot} {x} {y})"/>', c)
def wafel(sh):
    sh.rect_r(30, 40, 140, 120, "y", 16)
    for k in range(1, 5): sh.seg(30 + k * 28, 40, 30 + k * 28, 160); sh.seg(30, 40 + k * 24, 170, 40 + k * 24)
    sh.region("M60 44C60 30 100 26 110 40C120 30 140 36 136 50C130 60 70 60 60 44Z", "-")
    for x, y in ((150, 140), (60, 140)): sh.region(f"M{x} {y - 12}C{x + 14} {y - 12} {x + 14} {y + 8} {x} {y + 12}C{x - 14} {y + 8} {x - 14} {y - 12} {x} {y - 12}Z", "r")
    sh.region("M140 18L150 30L160 18Z", "-") if False else None
def spaghetti(sh):
    sh.ellipse_r(100, 130, 86, 40, "-"); sh.ellipse_r(100, 126, 66, 28, "-")
    for k in range(7): sh.line(f"M{50 + k * 14} 116Q{60 + k * 14} 96 {44 + k * 16} 140")
    sh.region("M60 110C70 90 140 90 150 110C140 126 70 126 60 110Z", "r")
    for x, y in ((80, 104), (110, 100), (130, 110)): sh.circle_r(x, y, 7, "w")
    sh.region("M100 96L104 86L110 92Z", "g")
    sh.line("M160 30L130 110M170 34L140 114")
    sh.region("M150 20L164 22L172 40L160 38Z", "z") if False else None
def gebakken_ei(sh):
    sh.circle_r(100, 110, 74, "z"); sh.circle_r(100, 110, 64, "-")
    sh.rect_r(170, 98, 30, 24, "x", 4)
    sh.region("M60 110C50 80 90 70 110 80C140 76 150 100 140 120C140 140 110 150 90 142C66 146 54 130 60 110Z", "-")
    sh.circle_r(100, 108, 18, "y"); sh.region("M92 100Q96 96 100 96", "-") if False else None
    sh.line("M92 102Q94 98 100 97")
def gitaar(sh):
    sh.raw('<g transform="rotate(-30 100 110)">')
    sh.region("M100 120C70 120 64 150 70 166C76 186 124 186 130 166C136 150 130 120 100 120Z", "w")
    sh.region("M100 100C84 100 78 116 84 126C88 132 112 132 116 126C122 116 116 100 100 100Z", "w")
    sh.circle_r(100, 140, 9, "x")
    sh.rect_r(95, 30, 10, 84, "x"); sh.rect_r(92, 14, 16, 20, "w", 3)
    for x in (97, 100, 103): sh.seg(x, 32, x, 162, "l", "stroke-width:.5")
    sh.rect_r(90, 158, 20, 5, "x")
    sh.raw("</g>")
    for x, y in ((40, 40), (160, 160)): sh.line(f"M{x} {y}V{y - 20}L{x + 12} {y - 24}V{y - 4}"); sh.circle_r(x - 4, y, 4, "x"); sh.circle_r(x + 8, y - 4, 4, "x")
def trommel(sh):
    sh.region("M40 80V150C40 170 160 170 160 150V80Z", "r")
    sh.ellipse_r(100, 80, 60, 18, "-")
    for k in range(6):
        x = 46 + k * 22; sh.line(f"M{x} {84 + (8 if 0 < k < 5 else 0)}L{x + 11} {158}" if k < 5 else f"M{x} 84V150")
    sh.region("M40 140C40 160 160 160 160 140V150C160 170 40 170 40 150Z", "y")
    sh.region("M40 86C40 102 160 102 160 86V94C160 110 40 110 40 94Z", "y")
    sh.raw('<g transform="rotate(30 60 40)"><rect class="r" x="56" y="10" width="7" height="60" rx="3"/><circle class="r" cx="59.5" cy="10" r="6"/></g>', None); sh.codes += ["w", "w"]
    sh.raw('<g transform="rotate(-30 140 40)"><rect class="r" x="136" y="10" width="7" height="60" rx="3"/><circle class="r" cx="139.5" cy="10" r="6"/></g>', None); sh.codes += ["w", "w"]
def trompet(sh):
    sh.region("M20 96H120V112H20Z", "y"); sh.region("M120 92Q150 90 180 60V148Q150 118 120 116Z", "y")
    sh.ellipse_r(180, 104, 8, 44, "y")
    sh.region("M40 112V136H110V112", "-") if False else None
    sh.line("M40 112V132Q40 140 48 140H104Q112 140 112 132V112")
    for x in (60, 76, 92): sh.rect_r(x - 4, 76, 8, 20, "y", 2); sh.circle_r(x, 74, 5, "y")
    sh.rect_r(10, 98, 12, 12, "y", 3)
    for x, y in ((40, 40), (70, 30), (150, 170)): sh.line(f"M{x} {y}V{y - 20}"); sh.circle_r(x - 4, y, 4, "x")
def piano(sh):
    sh.rect_r(20, 60, 160, 50, "x", 6); sh.rect_r(20, 110, 160, 50, "-")
    for k in range(1, 10): sh.seg(20 + k * 16, 110, 20 + k * 16, 160)
    for k in (0, 1, 3, 4, 5, 7, 8):
        sh.rect_r(20 + (k + 1) * 16 - 4, 110, 8, 30, "x")
    sh.rect_r(24, 160, 8, 30, "x"); sh.rect_r(168, 160, 8, 30, "x")
    sh.rect_r(70, 70, 60, 30, "-", 3)
    for x in (80, 100, 120): sh.line(f"M{x} 92V78L{x + 8} 76V90"); sh.circle_r(x - 3, 92, 3, "x")
def bakfiets(sh):
    grass(sh, 186, "z")
    sh.circle_r(40, 164, 18, "-"); sh.circle_r(150, 164, 18, "-"); sh.circle_r(40, 164, 4, "z"); sh.circle_r(150, 164, 4, "z")
    sh.region("M16 110H92L86 146H22Z", "g")
    sh.line("M86 146L150 164L118 112L96 112M118 112L112 96H128M150 164L130 150L104 150L86 146")
    sh.region("M110 90C110 82 124 82 126 90Z", "x") if False else None
    sh.rect_r(104, 90, 22, 6, "x", 3)
    sh.circle_r(40, 90, 12, "k"); eye(sh, 36, 88, 1.8); eye(sh, 44, 88, 1.8); smile(sh, 40, 94, 4)
    sh.circle_r(68, 94, 9, "k"); eye(sh, 65, 92, 1.6); eye(sh, 71, 92, 1.6)
    sh.region("M30 80Q40 70 50 80Z", "y")
def tandem(sh):
    grass(sh, 186, "z")
    for x in (34, 166): sh.circle_r(x, 160, 24, "-"); sh.circle_r(x, 160, 4, "z")
    sh.line("M34 160L64 116H138L166 160M64 116L84 160H126L138 116M84 160L76 106M126 160L116 106M138 116L150 98H160")
    sh.rect_r(66, 100, 20, 6, "x", 3); sh.rect_r(106, 100, 20, 6, "x", 3)
    sh.circle_r(40, 40, 14, "y")
def zeppelin(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.ellipse_r(100, 80, 80, 34, "z")
    for x in (60, 100, 140): sh.line(f"M{x} 47Q{x + 8} 80 {x} 113")
    sh.poly_r([(170, 68), (196, 50), (192, 80)], "r"); sh.poly_r([(170, 92), (196, 110), (192, 80)], "r")
    sh.rect_r(80, 112, 40, 16, "r", 4)
    for x in (88, 100, 112): sh.rect_r(x - 4, 116, 8, 7, "-", 1)
    for x, y in ((30, 160), (160, 170), (90, 180)): sh.region(f"M{x - 20} {y + 6}A10 10 0 0 1 {x - 8} {y - 6}A12 12 0 0 1 {x + 12} {y - 4}A9 9 0 0 1 {x + 18} {y + 6}Z", "-")
def vorkheftruck(sh):
    grass(sh, 186, "z")
    sh.rect_r(60, 120, 90, 40, "y", 6); sh.region("M80 120V70H130L140 120Z", "-")
    sh.line("M80 70H134M84 70V120"); sh.rect_r(140, 120, 20, 30, "y", 3)
    for x in (80, 140): sh.circle_r(x, 164, 16, "x"); sh.circle_r(x, 164, 5, "z")
    sh.rect_r(46, 50, 8, 120, "z"); sh.rect_r(20, 150, 34, 6, "z")
    sh.rect_r(16, 120, 34, 30, "w", 2); sh.line("M16 135H50M33 120V150")
    sh.circle_r(108, 92, 9, "k"); sh.region("M98 86Q108 76 118 86Z", "o")
def bloemenveld(sh):
    sh.region("M0 120Q100 100 200 120V200H0Z", "l")
    sh.circle_r(160, 40, 18, "y")
    for i, (x, y, s, c) in enumerate(((30, 150, 1, "r"), (70, 130, .8, "y"), (110, 160, 1.2, "m"), (150, 140, .9, "p"), (180, 170, 1, "o"), (50, 180, .9, "b"), (130, 186, .8, "y"))):
        sh.line(f"M{x} {y}V{y + 30 * s}")
        for k in range(5): a = math.radians(k * 72 - 90); sh.circle_r(x + 8 * s * math.cos(a), y + 8 * s * math.sin(a), 6 * s, c)
        sh.circle_r(x, y, 4.5 * s, "y" if c != "y" else "o")
    for x, y in ((90, 70), (40, 60)): sh.line(f"M{x - 8} {y}Q{x - 4} {y - 6} {x} {y}Q{x + 4} {y - 6} {x + 8} {y}")
def onweer(sh):
    sh.rect_r(0, 0, 200, 200, "z")
    sh.region("M30 90A26 26 0 0 1 56 54A34 34 0 0 1 120 44A30 30 0 0 1 170 70A22 22 0 0 1 166 112H44A22 22 0 0 1 30 90Z", "n")
    sh.region("M96 112L80 150H96L86 196L124 140H106L118 112Z", "y")
    sh.region("M150 112L144 130H152L146 150L162 126H154L160 112Z", "y")
    for x, y in ((40, 140), (60, 170), (140, 170), (170, 140), (24, 180)): sh.line(f"M{x} {y}L{x - 6} {y + 14}")
    sh.region("M0 186H60V200H0Z", "g") if False else None

kp("gorilla", "Gorilla in het oerwoud", "dieren", "4-6", 2, gorilla)
# kp("jachtluipaard", "Jachtluipaard", "dieren", "6-9", 2, jachtluipaard)
# kp("axolotl", "Axolotl", "dieren", "4-6", 1, axolotl)
# kp("kameleon", "Kameleon op een tak", "dieren", "6-9", 2, kameleon)
kp("specht", "Specht aan een boom", "dieren", "4-6", 2, specht)
kp("ijsvogel", "IJsvogel bij het water", "dieren", "4-6", 2, ijsvogel)
kp("rog", "Rog in de zee", "zee", "4-6", 1, rog)
kp("narwal", "Narwal", "zee", "4-6", 1, narwal)
kp("kogelvis", "Opgeblazen kogelvis", "zee", "2-4", 1, kogelvis)
kp("donut", "Donut met spikkels", "eten", "2-4", 1, donut)
kp("wafel", "Wafel met aardbeien", "eten", "2-4", 1, wafel)
kp("spaghetti", "Bord spaghetti", "eten", "4-6", 1, spaghetti)
kp("gebakken-ei", "Gebakken ei in de pan", "eten", "2-4", 1, gebakken_ei)
kp("gitaar", "Gitaar", "thuis", "4-6", 2, gitaar)
kp("trommel", "Trommel met stokken", "thuis", "2-4", 1, trommel)
kp("trompet", "Trompet", "thuis", "4-6", 1, trompet)
kp("piano", "Piano", "thuis", "4-6", 2, piano)
kp("bakfiets", "Bakfiets", "voertuigen", "4-6", 2, bakfiets)
kp("tandem", "Tandem", "voertuigen", "4-6", 2, tandem)
kp("zeppelin", "Zeppelin", "voertuigen", "4-6", 1, zeppelin)
kp("vorkheftruck", "Vorkheftruck", "voertuigen", "4-6", 2, vorkheftruck)
kp("bloemenveld", "Bloemenveld", "natuur", "2-4", 1, bloemenveld)
kp("onweer", "Onweer", "natuur", "4-6", 1, onweer)
