"""Batch 6: nog meer kleurplaten (eigen tekeningen, 200x200)."""
import math
from lib_gen import *
from batch5_kit import kp, grass, eye, smile

def wasbeer(sh):
    grass(sh, 180)
    sh.region("M60 180C50 140 70 116 100 116C130 116 150 140 140 180Z", "z")
    for k in range(4): sh.region(f"M{140 + k * 0} {170 - k * 14}", "-") if False else None
    sh.region("M136 170C160 170 180 150 186 124L174 120C170 140 156 156 134 158Z", "z")
    for k, (x1, y1, x2, y2) in enumerate([(178, 122, 172, 136), (172, 140, 162, 150)]): sh.seg(x1 + 8, y1 + 2, x2 + 6, y2 + 2)
    sh.region("M60 86C60 56 140 56 140 86C140 110 120 124 100 124C80 124 60 110 60 86Z", "z")
    sh.poly_r([(64, 70), (62, 46), (82, 60)], "z"); sh.poly_r([(136, 70), (138, 46), (118, 60)], "z")
    sh.region("M64 84Q80 70 96 86Q100 92 104 86Q120 70 136 84Q130 100 116 98Q104 96 100 92Q96 96 84 98Q70 100 64 84Z", "x")
    sh.circle_r(82, 86, 5, "-"); sh.circle_r(118, 86, 5, "-"); eye(sh, 82, 86, 2.2); eye(sh, 118, 86, 2.2)
    sh.ellipse_r(100, 106, 6, 4, "x"); smile(sh, 100, 112, 5)
def hamster(sh):
    sh.region("M20 180H180V196H20Z", "y")
    sh.region("M40 176C30 120 70 92 100 92C130 92 170 120 160 176Z", "o")
    sh.region("M70 176C66 140 82 126 100 126C118 126 134 140 130 176Z", "-")
    sh.circle_r(66, 96, 12, "o"); sh.circle_r(134, 96, 12, "o"); sh.circle_r(66, 96, 6, "k"); sh.circle_r(134, 96, 6, "k")
    eye(sh, 84, 112); eye(sh, 116, 112); sh.ellipse_r(100, 122, 4, 3, "k")
    sh.circle_r(78, 124, 7, "k"); sh.circle_r(122, 124, 7, "k")
    sh.region("M88 146C88 136 112 136 112 146C112 156 88 156 88 146Z", "w")
    sh.ellipse_r(84, 146, 6, 5, "o"); sh.ellipse_r(116, 146, 6, 5, "o")
def zwaan(sh):
    sh.region("M0 140H200V200H0Z", "b")
    sh.region("M40 130C40 100 90 96 130 116C150 110 170 112 172 124C150 150 60 156 40 130Z", "-")
    sh.region("M60 122Q90 96 124 120Q96 132 60 122Z", "-")
    sh.region("M128 118C120 84 120 54 130 42C140 32 158 36 158 50C150 46 142 48 140 58C136 74 138 96 144 116Z", "-")
    sh.region("M156 46L176 54L156 56Z", "o"); sh.region("M150 44Q156 42 158 50L152 52Z", "x"); eye(sh, 148, 46, 2)
    for k in range(4): sh.line(f"M{20 + k * 50} 166Q{30 + k * 50} 160 {40 + k * 50} 166")
    sh.region("M20 60C10 40 40 30 46 46C56 40 66 56 54 62H24Z", "-")
def pelikaan(sh):
    sh.region("M0 160H200V200H0Z", "b"); sh.rect_r(20, 150, 70, 14, "w", 2); sh.rect_r(30, 160, 8, 40, "w"); sh.rect_r(70, 160, 8, 40, "w")
    sh.region("M40 150C30 110 60 86 90 92C110 96 116 120 104 150Z", "-")
    sh.region("M50 120Q70 104 92 120Q72 132 50 120Z", "z")
    sh.region("M96 100C96 70 100 52 112 46C124 42 132 52 128 62C122 58 116 60 114 68C112 80 112 92 110 104Z", "-")
    sh.region("M124 54L180 70Q170 100 132 84L122 66Z", "y"); sh.line("M124 62L178 72"); eye(sh, 118, 54, 2)
    sh.region("M160 150Q170 140 180 150Q170 160 160 150Z", "o")
def struisvogel(sh):
    sh.region("M0 186Q100 176 200 186V200H0Z", "y")
    sh.region("M50 110C40 70 120 64 150 96C140 124 70 134 50 110Z", "x")
    sh.region("M140 96Q150 90 160 100Q150 110 140 106Z", "-")
    sh.region("M110 84C116 60 112 40 114 26C116 16 130 14 134 24C128 24 124 28 124 34C124 50 126 70 122 90Z", "k")
    sh.region("M132 22L146 26L132 30Z", "o"); eye(sh, 124, 22, 2)
    sh.line("M86 122L80 160L90 186M80 160L70 186"); sh.line("M106 122L112 160L102 186M112 160L122 186")
    sh.region("M52 100Q30 90 26 106Q34 116 54 112Z", "-")
def wolf(sh):
    sh.rect_r(0, 0, 200, 200, "n"); sh.circle_r(150, 46, 28, "y")
    sh.region("M0 200V150L40 130L80 160L120 140L160 166L200 150V200Z", "p")
    sh.region("M50 170C40 130 50 100 70 90L82 50L90 74L100 70L110 40L114 84C126 100 130 140 120 170Z", "z")
    sh.region("M100 72L106 42L114 80Z", "-") if False else None
    sh.region("M78 108Q90 100 104 108Q90 126 78 108Z", "-")
    sh.poly_r([(82, 50), (78, 34), (92, 46)], "z"); eye(sh, 96, 86, 2.4)
    for x, y in ((30, 30), (60, 60), (110, 24)): sh.poly_r(star_pts(x, y, 6, 2.6), "y")
def otter(sh):
    sh.region("M0 120H200V200H0Z", "b")
    sh.region("M30 130C40 110 160 110 170 130C160 150 40 150 30 130Z", "w")
    sh.circle_r(52, 116, 22, "w"); sh.circle_r(36, 100, 5, "w"); sh.circle_r(66, 98, 5, "w")
    sh.ellipse_r(52, 124, 12, 8, "-"); sh.ellipse_r(52, 118, 4, 3, "x"); eye(sh, 44, 110, 2.4); eye(sh, 60, 110, 2.4)
    sh.region("M168 130Q190 124 196 136Q182 140 170 136Z", "w")
    sh.region("M76 118C80 102 108 102 110 118Z", "y") if False else None
    sh.region("M86 120C86 108 112 108 112 120C112 128 86 128 86 120Z", "z")
    sh.ellipse_r(84, 124, 6, 5, "w"); sh.ellipse_r(114, 124, 6, 5, "w")
    for k in range(4): sh.line(f"M{20 + k * 50} 170Q{30 + k * 50} 164 {40 + k * 50} 170")
def walrus(sh):
    sh.region("M0 160H200V200H0Z", "b"); sh.region("M20 160L60 120H180L200 160Z", "-")
    sh.region("M60 150C50 110 80 80 110 80C150 80 170 120 160 150Z", "w")
    sh.ellipse_r(96, 104, 14, 10, "w"); sh.ellipse_r(124, 104, 14, 10, "w")
    sh.region("M100 112L102 150L108 150L106 112Z", "-"); sh.region("M120 112L118 150L112 150L114 112Z", "-")
    eye(sh, 96, 88); eye(sh, 124, 88); sh.ellipse_r(110, 98, 5, 3.5, "x")
    sh.region("M60 150Q50 160 66 162Q74 156 70 150Z", "w"); sh.region("M160 150Q172 160 156 162Q148 156 152 150Z", "w")
def kreeft(sh):
    sh.region("M0 180H200V200H0Z", "y")
    sh.region("M86 70C86 56 114 56 114 70V140C114 150 86 150 86 140Z", "r")
    for k in range(4): sh.seg(86, 92 + k * 12, 114, 92 + k * 12)
    sh.region("M86 146L72 172H128L114 146Z", "r"); sh.line("M100 150V172M86 160L80 172M114 160L120 172")
    eye(sh, 94, 64, 2.4); eye(sh, 106, 64, 2.4); sh.line("M94 58Q80 30 60 24M106 58Q120 30 140 24")
    for s in (-1, 1):
        sh.line(f"M{100 + s * 14} 76Q{100 + s * 30} 70 {100 + s * 36} 58")
        sh.region(f"M{100 + s * 36} 58C{100 + s * 20} 46 {100 + s * 30} 26 {100 + s * 46} 30C{100 + s * 54} 32 {100 + s * 56} 46 {100 + s * 50} 56Z", "r")
        sh.line(f"M{100 + s * 40} 40L{100 + s * 46} 50")
        for k in range(3): sh.line(f"M{100 + s * 14} {100 + k * 12}L{100 + s * 34} {108 + k * 12}")
def rups(sh):
    sh.region("M10 180C40 140 140 140 190 180V200H10Z", "l")
    for k in range(6):
        x = 40 + k * 22; y = 132 + (-8 if k % 2 else 0)
        sh.circle_r(x, y, 14, "g" if k % 2 else "l")
        sh.line(f"M{x - 4} {y + 14}V{y + 20}M{x + 4} {y + 14}V{y + 20}")
    sh.circle_r(160, 110, 20, "g"); eye(sh, 154, 106); eye(sh, 168, 106); smile(sh, 162, 116, 5)
    sh.line("M152 92L146 76M168 92L172 76"); sh.circle_r(146, 74, 3, "y"); sh.circle_r(172, 74, 3, "y")
    sh.region("M20 60C40 30 80 40 70 70C60 90 30 80 20 60Z", "g"); sh.line("M24 62Q48 56 66 68")
def mier(sh):
    sh.region("M0 170H200V200H0Z", "w")
    sh.circle_r(60, 120, 18, "x"); sh.circle_r(96, 118, 12, "x"); sh.circle_r(126, 106, 16, "x")
    for x in (82, 96, 110):
        sh.line(f"M{x} 120L{x - 12} 150L{x - 18} 168M{x} 120L{x + 10} 150L{x + 16} 168")
    sh.line("M132 92L140 70M120 92L116 70"); sh.circle_r(140, 68, 3, "x"); sh.circle_r(116, 68, 3, "x")
    sh.circle_r(132, 102, 4, "-"); eye(sh, 133, 102, 1.8)
    sh.region("M110 70L170 50L176 72L116 90Z", "l")
    sh.region("M150 40C160 28 180 34 176 50", "-") if False else None
def landschildpad(sh):
    grass(sh, 182)
    sh.region("M40 150C40 90 150 90 150 150Z", "g")
    sh.poly_r([(80, 112), (110, 112), (120, 132), (95, 146), (70, 132)], "l")
    for x1, y1, x2, y2 in ((80, 112, 70, 100), (110, 112, 122, 100), (70, 132, 48, 130), (120, 132, 142, 130), (95, 146, 95, 150)): sh.seg(x1, y1, x2, y2)
    sh.region("M150 140C160 120 186 120 186 136C186 148 170 152 150 150Z", "l"); eye(sh, 172, 134); smile(sh, 176, 142, 4)
    for x in (54, 128): sh.rect_r(x, 146, 16, 16, "l", 6)
    sh.region("M40 140L28 146L40 148Z", "l")
    sh.circle_r(30, 40, 14, "y")
def motor(sh):
    grass(sh, 184, "z")
    sh.circle_r(50, 150, 26, "x"); sh.circle_r(50, 150, 12, "z"); sh.circle_r(150, 150, 26, "x"); sh.circle_r(150, 150, 12, "z")
    sh.region("M50 150L80 110H120L150 150", "-") if False else None
    sh.region("M70 120H130L140 110L120 96H86L70 108Z", "r")
    sh.region("M86 96C90 86 116 86 120 96Z", "x"); sh.region("M70 120L54 146L62 150L80 124Z", "z")
    sh.region("M124 108L148 148L156 144L136 106Z", "z"); sh.line("M136 106L132 80H120"); sh.circle_r(140, 82, 5, "y")
    sh.rect_r(82, 124, 36, 18, "z", 4)
def kano(sh):
    sh.region("M0 120H200V200H0Z", "b")
    sh.region("M20 120Q100 150 180 120Q100 132 20 120Z", "o")
    sh.region("M20 120Q100 112 180 120Q100 132 20 120Z", "y")
    sh.circle_r(100, 82, 12, "k"); sh.region("M88 120V102Q100 94 112 102V120Z", "r")
    eye(sh, 96, 80, 1.8); eye(sh, 104, 80, 1.8); smile(sh, 100, 86, 4); sh.region("M88 74Q100 62 112 74Z", "y")
    sh.line("M60 70L140 130"); sh.region("M50 62L66 66L62 80L46 76Z", "y"); sh.region("M134 126L150 130L146 144L130 140Z", "y")
    for k in range(4): sh.line(f"M{10 + k * 50} 160Q{20 + k * 50} 154 {30 + k * 50} 160")
def cementwagen(sh):
    grass(sh, 184, "z")
    sh.rect_r(16, 130, 168, 16, "z", 3)
    sh.raw('<g transform="rotate(-12 80 100)"><ellipse class="r" cx="80" cy="100" rx="56" ry="30"/></g>', "o")
    sh.raw('<g transform="rotate(-12 80 100)"><path class="l" d="M50 76Q60 100 50 124M80 70Q90 100 80 130M110 74Q120 100 110 126"/></g>')
    sh.rect_r(138, 92, 46, 40, "y", 6); sh.rect_r(150, 100, 26, 18, "b", 3)
    for x in (44, 80, 160): sh.circle_r(x, 150, 14, "x"); sh.circle_r(x, 150, 5, "z")
def sleepboot(sh):
    sh.region("M0 140H200V200H0Z", "n")
    sh.region("M20 120H180L160 154H40Z", "r"); sh.rect_r(60, 90, 60, 30, "-", 3)
    for x in (68, 88): sh.rect_r(x, 98, 12, 12, "b", 2)
    sh.rect_r(100, 60, 14, 30, "y"); sh.rect_r(100, 60, 14, 8, "x")
    for x, y, r in ((116, 46, 8), (128, 32, 10), (146, 22, 12)): sh.circle_r(x, y, r, "z")
    sh.circle_r(160, 134, 8, "o"); sh.circle_r(160, 134, 4, "-")
    for k in range(4): sh.line(f"M{10 + k * 50} 172Q{20 + k * 50} 166 {30 + k * 50} 172")
def step(sh):
    grass(sh, 184, "z")
    sh.rect_r(40, 150, 110, 10, "t", 5); sh.circle_r(48, 166, 12, "x"); sh.circle_r(148, 166, 12, "x")
    sh.region("M144 152L132 50L140 49L152 150Z", "t"); sh.rect_r(114, 42, 40, 9, "x", 4)
    sh.region("M100 150Q110 140 120 146", "-") if False else None
    sh.circle_r(30, 36, 14, "y")
def wekker(sh):
    sh.circle_r(100, 108, 62, "r"); sh.circle_r(100, 108, 50, "-")
    sh.circle_r(58, 50, 16, "y"); sh.circle_r(142, 50, 16, "y")
    sh.rect_r(94, 40, 12, 12, "z", 2)
    for k in range(12):
        a = math.radians(k * 30); sh.seg(100 + 42 * math.cos(a), 108 + 42 * math.sin(a), 100 + 47 * math.cos(a), 108 + 47 * math.sin(a))
    sh.line("M100 108V76M100 108L122 118"); sh.dot(100, 108, 3)
    sh.line("M64 160L52 178M136 160L148 178")
def gieter(sh):
    grass(sh, 180)
    sh.region("M50 90H130L136 170H44Z", "g"); sh.region("M60 90Q90 54 120 90", "-") if False else None
    sh.line("M64 90Q90 46 116 90")
    sh.region("M130 120L180 80L186 88L134 136Z", "g"); sh.region("M176 74L196 70L190 92L182 90Z", "g")
    for x, y in ((186, 104), (194, 116), (180, 122)): sh.circle_r(x, y, 3, "b")
    for x in (60, 90): sh.region(f"M{x} 180V160Q{x + 4} 148 {x + 10} 160V180Z", "-") if False else None
    sh.circle_r(40, 172, 8, "r"); sh.circle_r(28, 176, 6, "k")
def laarzen(sh):
    sh.region("M0 170Q100 160 200 170V200H0Z", "b")
    for x, c in ((40, "y"), (110, "r")):
        sh.region(f"M{x} 40H{x + 36}V140H{x + 60}Q{x + 70} 140 {x + 70} 156V166H{x}Z", c)
        sh.rect_r(x - 2, 34, 40, 14, c, 3); sh.rect_r(x, 150, 70, 16, "-", 4)
    for x, y in ((24, 20), (100, 14), (180, 30)):
        sh.region(f"M{x} {y - 8}C{x + 3} {y - 3} {x + 5} {y} {x + 5} {y + 2}A5 5 0 0 1 {x - 5} {y + 2}C{x - 5} {y} {x - 3} {y - 3} {x} {y - 8}Z", "b")
def paraplu(sh):
    sh.region("M24 100A76 70 0 0 1 176 100Q157 88 138 100Q119 88 100 100Q81 88 62 100Q43 88 24 100Z", "p")
    sh.line("M62 100Q70 60 100 30M138 100Q130 60 100 30M100 30V100")
    sh.rect_r(97, 100, 6, 70, "x"); sh.region("M97 170Q97 186 112 186Q126 186 126 172H120Q120 180 112 180Q103 180 103 170Z", "x")
    for x, y in ((30, 140), (60, 170), (160, 140), (180, 180), (140, 190)):
        sh.region(f"M{x} {y - 8}C{x + 3} {y - 3} {x + 5} {y} {x + 5} {y + 2}A5 5 0 0 1 {x - 5} {y + 2}C{x - 5} {y} {x - 3} {y - 3} {x} {y - 8}Z", "b")
def wortel(sh):
    sh.region("M70 60C90 50 130 60 136 72L60 180C56 184 50 180 52 176Z", "o")
    for x1, y1, x2, y2 in ((90, 90, 104, 96), (76, 120, 88, 126), (66, 150, 76, 154)): sh.seg(x1, y1, x2, y2)
    for a in (-60, -30, 0):
        r = math.radians(a)
        sh.region(f"M114 62Q{f(130 + 30 * math.cos(r - .4))} {f(40 + 30 * math.sin(r - .4))} {f(130 + 50 * math.cos(r))} {f(46 + 50 * math.sin(r))}Q{f(126 + 20 * math.cos(r))} {f(46 + 20 * math.sin(r))} 120 66Z", "g")
def broccoli(sh):
    sh.region("M86 200V120L72 100H128L114 120V200Z", "l")
    for x, y, r in ((70, 90, 24), (100, 74, 28), (130, 90, 24), (84, 110, 20), (116, 110, 20), (100, 50, 20)): sh.circle_r(x, y, r, "g")
    eye(sh, 92, 150); eye(sh, 108, 150); smile(sh, 100, 160, 6)
def kersen(sh):
    sh.line("M70 130Q80 70 110 40M140 136Q130 80 110 40")
    sh.region("M110 40C120 20 160 18 170 34C150 46 128 46 110 40Z", "g"); sh.line("M114 40Q140 34 166 34")
    sh.circle_r(64, 150, 28, "r"); sh.circle_r(144, 156, 28, "r")
    sh.region("M52 140Q56 132 64 132Q58 136 56 144Z", "-"); sh.region("M132 146Q136 138 144 138Q138 142 136 150Z", "-")
def croissant(sh):
    sh.rect_r(10, 150, 180, 36, "b", 18)
    sh.region("M30 140C20 120 40 98 56 106C70 70 130 70 144 106C160 98 180 120 170 140C150 150 130 132 120 136C110 150 90 150 80 136C70 132 50 150 30 140Z", "o")
    for x in (70, 100, 130): sh.line(f"M{x} 92Q{x + 6} 116 {x - 4} 140")
    sh.region("M150 40H184V84H150Z", "-"); sh.region("M184 50Q196 56 184 70", "-") if False else None
    sh.line("M184 52Q196 60 184 72"); sh.line("M158 30Q154 22 160 16M170 30Q166 22 172 16")
def popcorn(sh):
    sh.region("M50 80H150L136 190H64Z", "-")
    for k in range(5): sh.region(f"M{50 + k * 20} 80H{60 + k * 20}L{f(66 + k * 15.6)} 190H{f(64 + k * 14.4)}Z", "r") if k % 2 == 0 else None
    for x, y in ((56, 70), (78, 60), (100, 56), (122, 60), (144, 70), (66, 48), (90, 38), (112, 40), (134, 50), (100, 22)):
        sh.region(f"M{x - 10} {y + 4}A8 8 0 0 1 {x - 4} {y - 8}A8 8 0 0 1 {x + 8} {y - 6}A8 8 0 0 1 {x + 10} {y + 6}A8 8 0 0 1 {x - 10} {y + 4}Z", "y")
def tennis(sh):
    sh.region("M0 170H200V200H0Z", "l"); sh.seg(0, 170, 200, 170)
    sh.raw('<g transform="rotate(-30 90 90)"><ellipse class="r" cx="90" cy="70" rx="36" ry="46"/></g>', "-")
    sh.raw('<g transform="rotate(-30 90 90)"><path class="l" d="M66 40V100M78 30V112M90 26V116M102 30V112M114 40V100M58 50H122M56 64H124M56 78H124M58 92H122M64 104H116"/><rect class="r" x="84" y="116" width="12" height="60" rx="5"/></g>', "r")
    sh.circle_r(156, 130, 18, "l"); sh.line("M140 122Q156 132 172 122M142 142Q156 132 170 142")
def herfst(sh):
    grass(sh, 176, "o")
    for x, y in ((70, 132), (130, 138)):
        sh.raw(f'<g transform="translate({x} {y}) scale(1.4) translate({-x} {-y})">')
        sh.ellipse_r(x, y, 15, 19, "w")
        sh.region(f"M{x - 19} {y - 10}C{x - 19} {y - 30} {x + 19} {y - 30} {x + 19} {y - 10}C{x + 8} {y - 4} {x - 8} {y - 4} {x - 19} {y - 10}Z", "w")
        for k in range(3): sh.line(f"M{x - 12 + k * 12} {y - 24}L{x - 6 + k * 12} {y - 8}")
        sh.line(f"M{x} {y - 25}V{y - 33}")
        sh.raw("</g>")
    for x, y, rot, c in ((40, 40, -20, "o"), (110, 30, 30, "r"), (170, 70, -40, "y"), (90, 70, 10, "o")):
        sh.raw(f'<g transform="rotate({rot} {x} {y})"><path class="r" d="M{x} {y - 16}L{x + 6} {y - 6}L{x + 16} {y - 8}L{x + 10} {y + 2}L{x + 14} {y + 12}L{x} {y + 8}L{x - 14} {y + 12}L{x - 10} {y + 2}L{x - 16} {y - 8}L{x - 6} {y - 6}Z"/><path class="l" d="M{x} {y - 10}V{y + 18}"/></g>', c)
kp("wasbeer", "Wasbeer met masker", "dieren", "4-6", 2, wasbeer)
kp("hamster", "Hamster met volle wangen", "dieren", "2-4", 1, hamster)
kp("zwaan", "Zwaan op het water", "dieren", "4-6", 1, zwaan)
kp("pelikaan", "Pelikaan op de steiger", "dieren", "4-6", 2, pelikaan)
kp("struisvogel", "Struisvogel", "dieren", "4-6", 2, struisvogel)
kp("walrus", "Walrus op het ijs", "zee", "4-6", 1, walrus)
kp("kreeft", "Kreeft", "zee", "4-6", 2, kreeft)
kp("rups", "Rups op een blaadje", "natuur", "2-4", 1, rups)
kp("landschildpad", "Schildpad in het gras", "dieren", "2-4", 1, landschildpad)
kp("motor", "Motor", "voertuigen", "4-6", 2, motor)
kp("kano", "Kano op het water", "sport", "4-6", 1, kano)
kp("cementwagen", "Betonmixer", "voertuigen", "4-6", 2, cementwagen)
kp("sleepboot", "Sleepboot", "voertuigen", "4-6", 1, sleepboot)
kp("step", "Step", "voertuigen", "2-4", 1, step)
kp("wekker", "Wekker", "thuis", "2-4", 1, wekker)
kp("gieter", "Gieter in de tuin", "thuis", "2-4", 1, gieter)
kp("regenlaarzen", "Regenlaarzen", "thuis", "2-4", 1, laarzen)
kp("paraplu", "Paraplu in de regen", "thuis", "2-4", 1, paraplu)
kp("wortel", "Wortel", "eten", "2-4", 1, wortel)
kp("broccoli", "Vrolijke broccoli", "eten", "2-4", 1, broccoli)
kp("kersen", "Kersen", "eten", "2-4", 1, kersen)
kp("croissant", "Croissant met koffie", "eten", "4-6", 1, croissant)
kp("popcorn", "Popcorn", "eten", "2-4", 1, popcorn)
kp("tennis", "Tennisracket en bal", "sport", "4-6", 1, tennis)
kp("herfst-eikels", "Eikels en herfstbladeren", "natuur", "4-6", 2, herfst)
