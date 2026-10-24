"""Batch 7a: nieuwe kleurplaten (eigen tekeningen, 200x200): beroepen, sport, boerderij, sprookjes, ruimte, wereld, dino's en feestdagen."""
import math
from lib_gen import *
from batch5_kit import kp, grass, eye, smile
from shapes import heart_path, star_path, moon_path, cloud_path, leaf_path, fish_path


# ---------- hulpjes ----------
def limb(sh, x1, y1, x2, y2, code, w=9):
    """Arm of been als balk met afgeronde uiteinden van (x1,y1) naar (x2,y2)."""
    dx, dy = x2 - x1, y2 - y1; d = math.hypot(dx, dy) or 1
    nx, ny = -dy / d * w / 2, dx / d * w / 2
    r = w / 2
    sh.region(f"M{f(x1 + nx)} {f(y1 + ny)}L{f(x2 + nx)} {f(y2 + ny)}A{f(r)} {f(r)} 0 0 0 {f(x2 - nx)} {f(y2 - ny)}L{f(x1 - nx)} {f(y1 - ny)}A{f(r)} {f(r)} 0 0 0 {f(x1 + nx)} {f(y1 + ny)}Z", code)

def person(sh, cx, top, shirt="-", pants="-", hands=None, hair="w", legs=None, cap=None, shoes="x", face=True):
    """Staand kind/volwassene van voren. top = bovenkant hoofd. hands = ((x,y),(x,y)) absolute handposities.
    legs = ((x,y),(x,y)) voetposities; standaard recht naar beneden."""
    hy = top + 15
    sl, sr = (cx - 13, hy + 24), (cx + 13, hy + 24)
    hl, hr = hands or ((cx - 22, hy + 52), (cx + 22, hy + 52))
    hip_l, hip_r = (cx - 8, hy + 54), (cx + 8, hy + 54)
    fl, fr = legs or ((cx - 8, hy + 86), (cx + 8, hy + 86))
    limb(sh, *hip_l, *fl, pants, 12); limb(sh, *hip_r, *fr, pants, 12)
    sh.ellipse_r(fl[0] - 3, fl[1] + 3, 8, 4.5, shoes); sh.ellipse_r(fr[0] + 3, fr[1] + 3, 8, 4.5, shoes)
    limb(sh, *sl, *hl, shirt, 10); limb(sh, *sr, *hr, shirt, 10)
    sh.region(f"M{cx - 17} {hy + 58}V{hy + 30}Q{cx - 17} {hy + 17} {cx - 5} {hy + 16}H{cx + 5}Q{cx + 17} {hy + 17} {cx + 17} {hy + 30}V{hy + 58}Z", shirt)
    sh.circle_r(cx, hy, 15, "-")
    if hair and not cap:
        sh.region(f"M{cx - 15} {hy}A15 15 0 0 1 {cx + 15} {hy}Q{cx + 8} {hy - 9} {cx - 2} {hy - 7}Q{cx - 10} {hy - 6} {cx - 15} {hy}Z", hair)
    if face:
        eye(sh, cx - 5, hy + 3, 1.8); eye(sh, cx + 5, hy + 3, 1.8); smile(sh, cx, hy + 8, 4)
    sh.circle_r(hl[0], hl[1], 4.5, "-"); sh.circle_r(hr[0], hr[1], 4.5, "-")
    return hy

def sparkle(sh, x, y, r=5, code="y"):
    sh.region(f"M{f(x)} {f(y - r)}Q{f(x + r * .2)} {f(y - r * .2)} {f(x + r)} {f(y)}Q{f(x + r * .2)} {f(y + r * .2)} {f(x)} {f(y + r)}Q{f(x - r * .2)} {f(y + r * .2)} {f(x - r)} {f(y)}Q{f(x - r * .2)} {f(y - r * .2)} {f(x)} {f(y - r)}Z", code)

def flower(sh, x, y, r=5, petal="m", heart="y"):
    for k in range(5):
        a = math.radians(k * 72 - 90)
        sh.circle_r(x + r * math.cos(a), y + r * math.sin(a), r * .7, petal)
    sh.circle_r(x, y, r * .55, heart)


# ---------- beroepen ----------
def tuinman(sh):
    grass(sh, 182)
    # kruiwagen
    sh.region("M112 128H186L176 158H122Z", "g"); sh.line("M112 128L98 120M122 158L112 168")
    sh.circle_r(150, 168, 12, "x"); sh.circle_r(150, 168, 4, "z")
    sh.line("M128 158L132 182M170 158L166 182")
    for x, c in ((128, "m"), (148, "y"), (168, "r")):
        sh.line(f"M{x} 128V112"); flower(sh, x, 106, 5, c, "o")
    # tuinman met strohoed en schep
    hy = person(sh, 64, 84, "t", "n", hands=((42, 138), (88, 134)), cap=True)
    sh.region("M38 92Q64 86 90 92Q86 96 64 96Q42 96 38 92Z", "y")
    sh.region("M50 92Q50 70 64 70Q78 70 78 92Z", "y"); sh.rect_r(50, 86, 28, 5, "r")
    sh.rect_r(86, 96, 4, 72, "w", 1); sh.region("M80 166H96L94 182Q88 186 82 182Z", "z"); sh.rect_r(82, 92, 12, 6, "w", 2)
    sh.circle_r(30, 30, 13, "y")

def schilder(sh):
    sh.rect_r(0, 168, 200, 32, "w")
    # ezel met schilderij
    sh.line("M128 168L140 64M176 168L160 64M150 168L150 70")
    sh.rect_r(112, 62, 72, 62, "-", 2); sh.rect_r(112, 124, 72, 6, "w", 1)
    sh.circle_r(132, 80, 7, "y"); sh.region("M120 118L140 96L158 118Z", "g"); sh.region("M144 118L162 92L178 118Z", "l")
    # schilder met baret, palet en kwast
    person(sh, 60, 62, "b", "w", hands=((32, 118), (96, 96)), cap=True)
    sh.region("M44 72Q46 56 64 58Q80 58 78 70Q62 66 44 72Z", "r"); sh.circle_r(64, 56, 3, "r")
    sh.region("M22 108C10 116 14 132 30 134C44 136 52 128 48 122C44 118 40 124 36 122C30 118 40 108 30 106Z", "w")
    for x, y, c in ((22, 116, "r"), (24, 126, "n"), (34, 130, "y"), (42, 128, "g")): sh.circle_r(x, y, 3.2, c)
    sh.line("M96 96L112 78"); sh.region("M110 80L116 72L118 76L113 82Z", "p")

def piloot(sh):
    sh.region("M0 0H200V200H0Z", "b")
    sh.region("M20 172C10 150 40 140 54 152C64 140 88 146 88 162C96 162 100 172 92 176H24Z", "-")
    sh.region("M136 40C130 26 152 20 158 32C170 26 182 38 174 46H138Z", "-")
    # vliegtuigje
    sh.region("M30 104C30 88 60 82 100 84L150 86C170 88 176 100 174 110C172 120 160 124 140 124H52C38 124 30 116 30 104Z", "r")
    sh.region("M146 88L168 54H182L176 92Z", "r")
    sh.region("M116 86C116 72 126 66 132 70L136 86Z", "b")
    sh.rect_r(22, 92, 10, 26, "z", 3); sh.region("M24 92L14 66L20 64L28 92Z", "z"); sh.region("M24 118L14 144L20 146L28 118Z", "z")
    sh.circle_r(27, 105, 5, "y")
    sh.line("M76 124L72 140M128 124L132 140"); sh.circle_r(72, 146, 7, "x"); sh.circle_r(132, 146, 7, "x")
    # piloot met muts en vliegbril, zwaaiend
    sh.circle_r(100, 66, 13, "-"); sh.region("M87 66A13 13 0 0 1 113 66Q100 58 87 66Z", "w")
    sh.circle_r(95, 60, 4, "t"); sh.circle_r(105, 60, 4, "t"); sh.seg(99, 60, 101, 60)
    eye(sh, 95, 68, 1.6); eye(sh, 105, 68, 1.6); smile(sh, 100, 72, 3.5)
    limb(sh, 112, 80, 124, 58, "w", 8); sh.circle_r(126, 54, 4.5, "-")
    sh.region("M56 112H150Q156 118 150 124H56Q50 118 56 112Z", "o")
    sh.line("M86 78Q74 82 66 76")

def postbode(sh):
    grass(sh, 184, "z")
    # huis met deur en brievenbus
    sh.rect_r(112, 40, 88, 144, "o"); sh.rect_r(134, 92, 42, 92, "g", 3); sh.circle_r(168, 140, 3, "y")
    sh.rect_r(144, 110, 22, 6, "z", 2); sh.rect_r(140, 56, 34, 24, "b", 2); sh.seg(157, 56, 157, 80); sh.seg(140, 68, 174, 68)
    sh.text(155, 104, "12", 7)
    # postbode met pet, tas en brief
    person(sh, 64, 76, "n", "n", hands=((44, 140), (98, 112)), cap=True)
    sh.region("M50 88Q50 72 64 72Q78 72 78 88Z", "n"); sh.region("M64 86H86Q86 90 78 90H64Z", "n"); sh.rect_r(58, 78, 12, 5, "y", 2)
    sh.line("M54 108L80 150"); sh.rect_r(68, 140, 30, 24, "r", 4); sh.line("M68 148H98")
    sh.rect_r(94, 100, 22, 15, "-", 1); sh.line("M94 100L105 109L116 100")
    sh.circle_r(30, 30, 12, "y")

def visser(sh):
    sh.rect_r(0, 132, 200, 68, "b")
    for k in range(4): sh.line(f"M{10 + k * 48} 150Q{20 + k * 48} 144 {30 + k * 48} 150")
    sh.circle_r(164, 36, 14, "y")
    # bootje
    person(sh, 72, 64, "y", "n", hands=((92, 104), (98, 100)), cap=True, legs=((64, 140), (80, 140)))
    sh.region("M56 74Q58 60 72 60Q86 60 88 74Z", "y"); sh.region("M50 76Q72 68 94 76Q72 80 50 76Z", "y")
    sh.region("M20 124H150L136 156H38Z", "w"); sh.line("M28 136H144")
    # hengel met lijn en vis
    sh.line("M90 106L170 60"); sh.line("M170 60L176 158", "l", "stroke-width:1.2")
    sh.region(fish_path(168, 168, 10), "o"); eye(sh, 162, 167, 1.4)


# ---------- sport ----------
def judo(sh):
    sh.rect_r(0, 170, 200, 30, "g"); sh.seg(0, 184, 200, 184); sh.seg(100, 170, 100, 200)
    hy = person(sh, 100, 40, "-", "-", hands=((70, 74), (130, 74)), legs=((88, 156), (112, 156)), shoes="-")
    sh.line("M89 72L100 92L111 72M100 92V100M100 106V112")
    sh.rect_r(83, 100, 34, 6, "x"); sh.region("M96 104L90 120L96 120L100 106L104 120L110 120L104 104Z", "x")
    sparkle(sh, 40, 50, 7); sparkle(sh, 160, 50, 7); sparkle(sh, 150, 22, 5); sparkle(sh, 50, 22, 5)

def hockey(sh):
    grass(sh, 170, "l")
    # doel
    sh.rect_line(126, 98, 66, 46, "l"); sh.seg(126, 98, 140, 84); sh.seg(192, 98, 192, 144)
    for k in range(1, 6): sh.seg(126 + k * 11, 98, 126 + k * 11, 144, "l", "stroke-width:.9")
    for k in range(1, 4): sh.seg(126, 98 + k * 11.5, 192, 98 + k * 11.5, "l", "stroke-width:.9")
    sh.rect_r(126, 96, 66, 4, "-")
    # speler met stick
    person(sh, 64, 66, "r", "n", hands=((80, 120), (88, 140)), legs=((52, 152), (76, 154)), hair="o")
    sh.region("M44 72Q64 58 84 72Q80 80 64 76Q48 80 44 72Z", "o")
    sh.line("M78 116L104 168"); sh.region("M100 164Q112 176 122 168Q120 162 114 166Q108 168 104 162Z", "w")
    sh.circle_r(132, 172, 5, "y")

def turnen(sh):
    sh.rect_r(0, 180, 200, 20, "b")
    # evenwichtsbalk
    sh.rect_r(20, 134, 160, 10, "w", 3); sh.region("M44 144L36 180H52L56 144Z", "z"); sh.region("M144 144L148 180H164L156 144Z", "z")
    # turnster op één been, armen omhoog
    hy = person(sh, 100, 34, "m", "m", hands=((72, 46), (128, 46)), legs=((100, 130), (128, 108)), hair="w")
    sh.region("M84 92H116L120 98H80Z", "m")
    sh.region("M86 42Q78 46 76 58Q84 54 88 48Z", "w"); sh.circle_r(100, 30, 6, "w")
    sparkle(sh, 40, 40, 7, "y"); sparkle(sh, 164, 80, 6, "y"); sparkle(sh, 34, 100, 5, "y")

def paardrijden(sh):
    grass(sh, 182)
    sh.seg(0, 140, 200, 140); sh.seg(0, 150, 200, 150)
    for x in (10, 190): sh.rect_r(x - 4, 128, 8, 56, "w", 1)
    # paard (zijaanzicht, kijkt naar rechts)
    sh.region("M42 96C24 98 18 126 28 140Q30 128 38 122Z", "w")
    for x1, x2, y in ((56, 52, 180), (70, 74, 180), (124, 120, 180), (138, 144, 180)):
        limb(sh, x1, 120, x2, y - 6, "w", 11); sh.rect_r(x2 - 6, y - 8, 12, 6, "x", 1)
    sh.region("M44 100C44 84 64 78 96 80C124 82 142 82 148 96C152 112 140 126 116 128H66C50 128 44 116 44 100Z", "w")
    sh.region("M132 92C136 72 140 58 150 46L160 52C168 58 182 70 180 80C178 88 168 88 162 84C156 82 154 88 150 100Z", "w")
    sh.region("M142 54L144 40L152 48Z", "w"); eye(sh, 160, 62, 2); sh.dot(176, 80, 1.5)
    sh.region("M150 46C140 56 134 74 130 90L138 92C140 76 146 62 156 52Z", "x")
    sh.line("M176 76L148 70")
    # zadel en ruiter
    sh.region("M76 82Q94 74 114 82L112 92Q94 88 78 92Z", "r")
    sh.region("M86 84L82 114L92 116L100 86Z", "n"); sh.rect_r(78, 112, 16, 6, "x", 2)
    sh.region("M82 84V54Q82 44 94 44H98Q108 44 108 56V84Z", "t")
    limb(sh, 100, 56, 140, 70, "t", 9); sh.circle_r(142, 70, 4.5, "-")
    sh.circle_r(96, 30, 13, "-"); sh.region("M82 30A14 14 0 0 1 110 30Q110 34 106 32Q96 26 84 32Z", "x"); sh.region("M106 30H116Q114 34 106 34Z", "x")
    eye(sh, 101, 33, 1.7); smile(sh, 101, 37, 3)


# ---------- boerderij ----------
def stal(sh):
    grass(sh, 184, "y")
    sh.region("M20 184V80L100 30L180 80V184Z", "r")
    sh.region("M12 84L100 26L188 84L180 90L100 38L20 90Z", "z")
    sh.rect_r(64, 92, 72, 92, "-")
    sh.rect_r(64, 132, 72, 52, "r"); sh.line("M64 132L136 184M136 132L64 184"); sh.rect_line(64, 132, 72, 52)
    # paardenhoofd over de staldeur
    sh.region("M84 132C80 116 82 100 94 96L118 96C122 112 124 124 120 132Z", "w")
    sh.region("M96 98C90 90 92 84 96 84L102 96Z", "w"); sh.region("M114 98C118 90 116 84 112 84L106 96Z", "w")
    sh.region("M96 96Q104 90 112 96Q106 102 104 110Q102 102 96 96Z", "-")
    eye(sh, 94, 108, 2.2); eye(sh, 114, 108, 2.2)
    sh.ellipse_r(104, 126, 13, 8, "w"); sh.dot(99, 126, 1.8); sh.dot(109, 126, 1.8)
    sh.region("M96 96C90 104 86 114 86 126L82 122C82 110 86 100 94 94Z", "x")
    sh.rect_r(88, 54, 24, 22, "-", 2)
    sh.circle_r(100, 64, 9, "y"); sh.line("M100 57V64H106")
    sh.region("M144 184C144 168 176 168 178 184Z", "y"); sh.line("M150 176L156 170M162 178L166 170M170 180L172 174")

def hooiberg(sh):
    grass(sh, 178, "l")
    sh.circle_r(170, 30, 14, "y")
    for x in (40, 160): sh.rect_r(x - 4, 50, 8, 130, "w", 2)
    sh.region("M28 62L100 26L172 62Z", "r")
    sh.region("M44 180C40 140 52 104 100 98C148 104 160 140 156 180Z", "y")
    sh.line("M72 120Q86 128 92 140M120 116Q112 132 116 150M70 156Q82 160 90 172M128 160Q134 168 132 178")

def eend_met_kuikens(sh):
    sh.rect_r(0, 110, 200, 90, "b")
    for k in range(5): sh.line(f"M{8 + k * 42} 186Q{18 + k * 42} 180 {28 + k * 42} 186")
    for x, h in ((14, 58), (30, 72)):
        sh.line(f"M{x} 110V{h}"); sh.ellipse_r(x, h - 6, 4, 10, "w")
    # moeder eend (zwemt naar rechts)
    sh.raw('<g transform="translate(70 4)">')
    sh.region("M20 112C18 92 40 84 70 88C82 70 108 72 110 92C110 102 104 106 96 108C96 120 80 130 56 130C36 130 22 124 20 112Z", "-")
    sh.region("M108 88L124 92L108 98Z", "o"); eye(sh, 96, 86, 2.4)
    sh.region("M36 104Q56 92 74 106Q56 116 36 104Z", "-")
    sh.raw("</g>")
    # kuikens erachteraan
    for x, y in ((30, 142), (62, 156), (94, 168)):
        sh.ellipse_r(x, y, 14, 9, "y"); sh.circle_r(x + 9, y - 11, 8, "y")
        sh.poly_r([(x + 16, y - 13), (x + 23, y - 11), (x + 16, y - 8)], "o"); eye(sh, x + 11, y - 13, 1.6)
        sh.line(f"M{x - 7} {y - 1}Q{x - 1} {y - 5} {x + 4} {y}")
    sh.circle_r(170, 30, 14, "y")


# ---------- sprookjes ----------
def klein_draakje(sh):
    grass(sh, 182)
    # staart
    sh.region("M128 168C150 168 168 160 174 140L186 132L182 148C176 172 152 182 128 180Z", "g")
    sh.region("M174 140L186 132L182 148Z", "o")
    # vleugels
    sh.region("M70 112C46 96 34 74 38 56C48 66 58 66 62 74C66 70 76 74 76 84C84 84 88 94 86 104Z", "p")
    sh.region("M130 112C154 96 166 74 162 56C152 66 142 66 138 74C134 70 124 74 124 84C116 84 112 94 114 104Z", "p")
    # lijf
    sh.region("M66 180C56 150 70 112 100 112C130 112 144 150 134 180Z", "g")
    sh.region("M84 180C80 156 88 132 100 132C112 132 120 156 116 180Z", "y")
    for y in (144, 156, 168): sh.line(f"M{86 + (y - 132) * .1} {y}H{114 - (y - 132) * .1}")
    sh.ellipse_r(76, 180, 12, 6, "g"); sh.ellipse_r(124, 180, 12, 6, "g")
    # hoofd
    sh.region("M72 92C66 58 134 58 128 92C126 108 114 116 100 116C86 116 74 108 72 92Z", "g")
    sh.region("M80 64L76 46L90 60Z", "o"); sh.region("M120 64L124 46L110 60Z", "o")
    sh.poly_r([(96, 62), (100, 50), (104, 62)], "o")
    sh.circle_r(88, 84, 6, "-"); sh.circle_r(112, 84, 6, "-"); eye(sh, 89, 85, 2.8); eye(sh, 113, 85, 2.8)
    sh.dot(95, 100, 1.3); sh.dot(105, 100, 1.3); sh.line("M92 106Q100 111 108 106")
    # rookwolkje met hartjes
    sh.region(cloud_path(150, 46, 14), "-")
    sh.region(heart_path(146, 42, 5), "r"); sh.region(heart_path(160, 44, 3.5), "m")
    for x, y in ((128, 70), (136, 60)): sh.circle_r(x, y, 3, "-")

def elfje(sh):
    grass(sh, 184)
    # vleugels
    sh.region("M98 82C70 50 34 52 40 80C44 96 70 100 96 92Z", "t"); sh.region("M98 94C72 100 52 120 64 132C76 140 92 122 98 102Z", "t")
    sh.region("M102 82C130 50 166 52 160 80C156 96 130 100 104 92Z", "t"); sh.region("M102 94C128 100 148 120 136 132C124 140 108 122 102 102Z", "t")
    # jurkje en armen
    limb(sh, 112, 86, 136, 64, "k", 8); sh.circle_r(138, 62, 4.5, "-")
    limb(sh, 88, 86, 78, 112, "k", 8); sh.circle_r(76, 114, 4.5, "-")
    sh.line("M138 62L156 40"); sparkle(sh, 158, 36, 8, "y")
    sh.line("M94 140L92 172M106 140L108 172"); sh.ellipse_r(90, 174, 6, 3.5, "m"); sh.ellipse_r(110, 174, 6, 3.5, "m")
    sh.region("M90 82H110L130 140Q100 150 70 140Z", "k")
    for x in (82, 100, 118): sh.region(heart_path(x, 132, 3.5), "m")
    # hoofd met knotjes en bloemenkransje
    sh.circle_r(86, 50, 7, "w"); sh.circle_r(114, 50, 7, "w")
    sh.circle_r(100, 64, 15, "-"); sh.region("M85 64A15 15 0 0 1 115 64Q106 54 96 56Q90 56 85 64Z", "w")
    for k, c in enumerate("mym"): sh.circle_r(91 + k * 9, 51, 3.5, c)
    eye(sh, 95, 66, 1.8); eye(sh, 105, 66, 1.8); smile(sh, 100, 71, 3.5)
    flower(sh, 30, 168, 7, "m"); flower(sh, 172, 166, 7, "p"); flower(sh, 154, 176, 5, "o")
    for x, y in ((30, 30), (60, 18), (176, 104)): sparkle(sh, x, y, 5)

def toverhoed(sh):
    sh.rect_r(20, 178, 160, 8, "w", 2)
    # hoge hoed
    sh.region("M60 72H140L132 160H68Z", "x")
    sh.ellipse_r(100, 160, 52, 14, "x")
    sh.rect_r(64, 128, 72, 14, "r")
    sh.ellipse_r(100, 72, 40, 10, "z")
    # konijntje dat eruit kijkt
    sh.region("M86 70C80 40 82 18 90 18C98 18 96 44 94 66Z", "-"); sh.region("M114 70C120 40 118 18 110 18C102 18 104 44 106 66Z", "-")
    sh.region("M88 58C86 38 88 26 90 26C92 26 92 40 91 58Z", "k"); sh.region("M112 58C114 38 112 26 110 26C108 26 108 40 109 58Z", "k")
    sh.region("M76 76C76 54 124 54 124 76Z", "-")
    eye(sh, 92, 66, 2.2); eye(sh, 108, 66, 2.2); sh.ellipse_r(100, 72, 3, 2, "k")
    # toverstaf
    sh.region("M146 176L176 108L184 112L154 180Z", "x"); sh.region("M172 116L176 108L184 112L180 120Z", "-")
    for x, y, r in ((40, 60, 9), (164, 82, 7), (36, 130, 6), (168, 40, 8), (52, 26, 5)): sparkle(sh, x, y, r)

def schatkist(sh):
    sh.region("M0 200V172Q100 160 200 172V200Z", "y")
    # deksel (open)
    sh.region("M40 92V60Q40 34 100 34Q160 34 160 60V92Z", "w")
    sh.rect_r(40, 84, 120, 10, "o")
    for x in (64, 136): sh.rect_r(x - 5, 38, 10, 54, "o")
    # schat
    sh.region("M40 100Q60 76 100 80Q140 76 160 100Z", "y")
    for x, y in ((60, 92), (76, 86), (124, 86), (142, 92), (96, 82)): sh.ellipse_r(x, y, 7, 4, "y")
    sh.region("M100 62L106 70L104 82H96L94 70Z", "t")
    sh.region("M114 76L118 64L124 72L130 62L134 76Z", "y")
    sh.circle_r(78, 74, 5, "r")
    # kist
    sh.rect_r(36, 96, 128, 76, "w", 4)
    sh.rect_r(36, 96, 128, 10, "o"); sh.rect_r(36, 160, 128, 12, "o")
    for x in (64, 136): sh.rect_r(x - 5, 96, 10, 76, "o")
    sh.rect_r(90, 114, 20, 24, "o", 3); sh.circle_r(100, 123, 3.5, "x"); sh.seg(100, 125, 100, 132)
    sh.line("M44 120H58M70 134H86M114 120H130M142 146H158")
    sparkle(sh, 30, 40, 7); sparkle(sh, 174, 30, 6); sparkle(sh, 178, 120, 5)


# ---------- ruimte ----------
def satelliet(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.region("M0 200V176Q100 140 200 176V200Z", "t")
    sh.region("M40 190Q60 172 90 178Q80 192 60 196Z", "g"); sh.region("M130 180Q150 168 170 176Q160 190 140 188Z", "g")
    for x, y in ((20, 24), (176, 22), (30, 130), (172, 140), (100, 16)): sh.region(star_path(x, y, 5, 2.2), "y")
    # zonnepanelen
    for x0, s in ((18, -1), (130, 1)):
        y0 = 72 if s < 0 else 66
        sh.region(f"M{x0} {y0}L{x0 + 52} {y0 + s * 6}V{y0 + s * 6 + 34}L{x0} {y0 + 34}Z", "b")
        for k in (1, 2, 3):
            x = x0 + k * 13; yt = y0 + s * 6 * k * 13 / 52
            sh.seg(x, yt, x, yt + 34)
    sh.line("M18 89L70 83M130 83L182 89")
    sh.seg(70, 86, 80, 86); sh.seg(120, 86, 130, 86)
    # romp
    sh.rect_r(80, 66, 40, 42, "z", 4); sh.rect_r(86, 76, 28, 10, "y", 2); sh.circle_r(100, 96, 4, "r")
    # schotel
    sh.region("M82 58Q100 70 118 58Q112 42 100 40Q88 42 82 58Z", "-"); sh.seg(100, 58, 100, 66); sh.seg(100, 50, 100, 38); sh.circle_r(100, 36, 2.5, "r")
    sh.line("M100 108V120"); sh.circle_r(100, 122, 3, "r")

def komeet(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    # staart in drie banen
    sh.region("M128 70L20 168Q60 150 100 100Z", "o")
    sh.region("M134 82L60 190Q96 160 120 108Z", "y")
    sh.region("M122 64L30 96Q70 96 112 78Z", "r")
    sh.circle_r(140, 62, 24, "y")
    eye(sh, 134, 58, 2.6); eye(sh, 148, 58, 2.6); smile(sh, 141, 68, 5)
    sh.circle_r(40, 40, 14, "p")
    sh.ellipse_r(40, 40, 22, 5, "m"); sh.region("M26 38A14 14 0 0 1 54 38Z", "p")
    for x, y in ((176, 150), (100, 30), (176, 20), (150, 180)): sh.region(star_path(x, y, 6, 2.6), "y")

def maanlander(sh):
    sh.rect_r(0, 0, 200, 200, "x")
    sh.region("M0 200V160Q50 150 100 158T200 154V200Z", "z")
    for x, y, r in ((30, 178, 8), (150, 176, 10), (90, 188, 6)): sh.ellipse_r(x, y, r, r * .4, "-")
    sh.circle_r(166, 40, 18, "b"); sh.region("M156 30Q162 40 158 52Q150 44 156 30Z", "g"); sh.region("M170 26Q180 34 176 46Q168 40 170 26Z", "g")
    for x, y in ((20, 20), (60, 40), (120, 18), (30, 90), (186, 100)): sh.region(star_path(x, y, 4, 1.8), "y")
    # lander
    sh.line("M64 112L44 160M136 112L156 160M76 118L66 158M124 118L134 158")
    for x in (44, 156): sh.ellipse_r(x, 160, 10, 3.5, "z")
    sh.ellipse_r(66, 158, 6, 2.5, "z"); sh.ellipse_r(134, 158, 6, 2.5, "z")
    sh.region("M58 94H142L136 120H64Z", "y")
    for x in (76, 94, 112, 130): sh.seg(x, 94, x - 1, 120)
    sh.region("M70 94L66 64L82 46H118L134 64L130 94Z", "-")
    sh.circle_r(100, 70, 10, "b"); sh.rect_r(78, 80, 10, 8, "z", 1)
    sh.line("M118 46L124 30"); sh.circle_r(124, 28, 4, "-")
    sh.region("M92 120L86 134H114L108 120Z", "z")
    # vlag (zonder land)
    sh.line("M176 158V112"); sh.region("M176 112H196V126H176Z", "r")
    sh.ellipse_r(176, 158, 6, 2, "z")


# ---------- wereld ----------
def iglo(sh):
    sh.rect_r(0, 0, 200, 200, "b")
    sh.region("M0 200V160Q100 150 200 160V200Z", "-")
    sh.region("M24 164C24 104 60 72 100 72C140 72 176 104 176 164Z", "-")
    sh.line("M30 136H170M44 108H156M66 86H134")
    for x in (70, 120, 160): sh.seg(x, 136, x, 164)
    for x in (48, 94, 140): sh.seg(x, 108, x, 136)
    for x in (80, 120): sh.seg(x, 86, x, 108)
    sh.region("M76 164V138C76 118 124 118 124 138V164Z", "n")
    sh.region("M86 164V142C86 128 114 128 114 142V164Z", "x")
    sh.circle_r(170, 36, 14, "y")
    for x, y in ((30, 30), (60, 50), (130, 26), (100, 40)): sh.circle_r(x, y, 3, "-")
    sh.ellipse_r(36, 184, 16, 5, "n"); sh.region(fish_path(160, 184, 8), "o"); eye(sh, 155, 183, 1.3)

def pagode(sh):
    sh.rect_r(0, 186, 200, 14, "z")
    sh.rect_r(70, 162, 60, 24, "r"); sh.rect_r(92, 166, 16, 20, "x", 2)
    sh.region("M40 162Q60 154 64 144H136Q140 154 160 162Q100 170 40 162Z", "g")
    sh.rect_r(76, 126, 48, 18, "r"); sh.rect_r(94, 130, 12, 10, "y", 1)
    sh.region("M48 126Q66 118 70 108H130Q134 118 152 126Q100 134 48 126Z", "g")
    sh.rect_r(82, 90, 36, 18, "r"); sh.rect_r(95, 94, 10, 10, "y", 1)
    sh.region("M56 90Q72 82 76 72H124Q128 82 144 90Q100 98 56 90Z", "g")
    sh.rect_r(88, 56, 24, 16, "r")
    sh.region("M64 56Q80 46 88 36H112Q120 46 136 56Q100 62 64 56Z", "g")
    sh.line("M100 36V14"); sh.circle_r(100, 26, 4, "y"); sh.circle_r(100, 16, 3, "y")
    for x, y in ((40, 162), (160, 162), (48, 126), (152, 126), (56, 90), (144, 90), (64, 56), (136, 56)): sh.circle_r(x, y + 4, 2.5, "y")
    # bloesemtak
    sh.line("M0 40Q20 44 34 60M14 44Q20 30 30 26")
    for x, y in ((34, 60), (30, 26), (22, 50), (8, 38)): flower(sh, x, y, 4, "k", "m")
    sh.circle_r(170, 30, 13, "o")

def tipi(sh):
    grass(sh, 176)
    sh.region(moon_path(166, 34, 14), "y")
    for x, y in ((24, 24), (60, 40), (130, 18)): sh.region(star_path(x, y, 5, 2.2), "y")
    # tent
    sh.line("M100 40L84 18M100 40L110 14M100 40L120 20")
    sh.region("M100 40L156 176H44Z", "o")
    sh.region("M76 116H124L130 130H70Z", "r")
    for k in range(6): sh.poly_r([(72 + k * 10, 132), (77 + k * 10, 142), (82 + k * 10, 132)], "y")
    sh.region("M84 80L100 64L116 80L100 96Z", "t")
    sh.region("M100 146L88 176H112Z", "w")
    sh.line("M100 146V176")
    sh.region("M100 40L106 54H94Z", "o")
    # boompjes
    for x in (24, 178):
        sh.rect_r(x - 3, 150, 6, 28, "w"); sh.region(f"M{x} 96L{x + 16} 154H{x - 16}Z", "g")

def windmolenpark(sh):
    sh.region("M0 200V150Q60 140 110 150T200 146V200Z", "l")
    sh.region("M0 200V172Q100 160 200 176V200Z", "g")
    sh.region(cloud_path(150, 30, 16), "-"); sh.region(cloud_path(50, 24, 12), "-")
    for cx, cy, s, rot in ((54, 70, 1.0, 10), (118, 94, .75, 45), (176, 116, .5, 80)):
        H = 150 - cy + (10 if s < 1 else 6)
        sh.region(f"M{f(cx - 3 * s)} {f(cy)}L{f(cx - 5 * s)} {f(cy + H)}H{f(cx + 5 * s)}L{f(cx + 3 * s)} {f(cy)}Z", "-")
        for k in range(3):
            a = math.radians(rot + k * 120)
            ux, uy = math.cos(a), math.sin(a); px, py = -uy, ux
            L = 44 * s
            tip = (cx + ux * L, cy + uy * L)
            b1 = (cx + ux * 6 * s + px * 5 * s, cy + uy * 6 * s + py * 5 * s); b2 = (cx + ux * 6 * s - px * 2 * s, cy + uy * 6 * s - py * 2 * s)
            m = (cx + ux * L * .5 + px * 4 * s, cy + uy * L * .5 + py * 4 * s)
            sh.region(f"M{f(b1[0])} {f(b1[1])}Q{f(m[0])} {f(m[1])} {f(tip[0])} {f(tip[1])}L{f(b2[0])} {f(b2[1])}Z", "-")
        sh.circle_r(cx, cy, 5 * s, "z")


# ---------- dino's ----------
def ankylosaurus(sh):
    grass(sh, 184)
    sh.region("M150 120C170 124 178 134 180 144L186 140C194 140 198 150 192 158C186 166 176 162 176 154L178 150C170 144 160 140 146 138Z", "o")
    for x in (52, 78, 120, 144): sh.rect_r(x - 8, 136, 16, 40, "o", 5); sh.region(f"M{x - 9} 176H{x + 9}V182H{x - 9}Z", "o")
    sh.region("M40 140C34 104 70 86 100 86C134 86 160 104 156 140Z", "o")
    for k in range(7):
        a = math.radians(200 + k * 23)
        x, y = 98 + 54 * math.cos(a), 140 + 50 * math.sin(a)
        sh.poly_r([(x - 6, y + 2), (x + 6 * math.cos(a) * 1.8 - 0, y + 10 * math.sin(a)), (x + 6, y + 2)], "w")
    for x, y in ((70, 112), (98, 104), (126, 112), (84, 126), (112, 126)): sh.ellipse_r(x, y, 9, 6, "w")
    sh.region("M44 124C30 116 14 120 12 132C10 142 20 150 34 148C42 146 48 140 48 132Z", "o")
    sh.poly_r([(26, 120), (28, 110), (36, 120)], "w"); eye(sh, 24, 130, 2.4); sh.line("M14 140Q22 144 30 140")

def parasaurolophus(sh):
    grass(sh, 184)
    sh.region(cloud_path(160, 40, 14), "-")
    # staart
    sh.region("M136 112C160 112 182 122 196 140L190 146C174 132 156 130 136 134Z", "g")
    # achterpoten (achter) en voorpoten
    limb(sh, 136, 120, 140, 176, "g", 16); sh.rect_r(130, 174, 22, 8, "g", 3)
    limb(sh, 84, 124, 86, 176, "g", 11); sh.rect_r(78, 174, 16, 8, "g", 3)
    # lijf
    sh.region("M60 112C60 92 90 84 120 88C146 92 152 114 140 132C126 144 80 144 66 132C62 128 60 120 60 112Z", "g")
    sh.region("M70 128Q100 142 134 128Q120 144 100 144Q80 144 70 128Z", "y")
    sh.region("M106 104C132 98 144 118 132 140L128 174H110L112 142C102 136 98 116 106 104Z", "g")
    sh.rect_r(106, 174, 26, 8, "g", 3)
    limb(sh, 72, 120, 70, 176, "g", 11); sh.rect_r(62, 174, 18, 8, "g", 3)
    # nek en kop met lange kuif naar achter
    sh.region("M60 108C52 92 50 74 52 62L70 60C70 74 74 90 80 100Z", "g")
    sh.region("M70 46C84 36 104 26 124 22L126 30C108 36 90 48 78 58Z", "o")
    sh.region("M46 62C42 50 50 42 62 42C72 42 78 50 74 60C72 68 64 70 56 68L38 72C32 72 32 64 36 62Z", "g")
    eye(sh, 60, 52, 2.4); sh.line("M38 68L52 66")
    for k in range(6): sh.ellipse_r(76 + k * 11, 92 - (2 if k in (2, 3) else 0), 4, 2.6, "o")


# ---------- feestdagen ----------
def paasnest(sh):
    sh.rect_r(0, 168, 200, 32, "l")
    for x, c in ((20, "y"), (180, "m"), (34, "r"), (166, "p")):
        sh.line(f"M{x} 170V{120 + (x % 3) * 8}"); sh.region(leaf_path(x + 6, 150, 5, 10), "g")
        sh.region(f"M{x - 8} {112 + (x % 3) * 8}L{x - 4} {124 + (x % 3) * 8}H{x + 4}L{x + 8} {112 + (x % 3) * 8}L{x + 4} {116 + (x % 3) * 8}L{x} {110 + (x % 3) * 8}L{x - 4} {116 + (x % 3) * 8}Z", c)
    # eieren
    for cx, cy, rot, c1, c2 in ((74, 112, -12, "b", "y"), (100, 104, 0, "m", "t"), (126, 112, 12, "y", "p")):
        sh.raw(f'<g transform="rotate({rot} {cx} {cy})">')
        sh.ellipse_r(cx, cy, 16, 22, c1)
        sh.region(f"M{cx - 15.6} {cy - 4}Q{cx - 8} {cy - 10} {cx} {cy - 4}T{cx + 15.6} {cy - 4}L{cx + 15.9} {cy + 2}Q{cx + 8} {cy + 8} {cx} {cy + 2}T{cx - 15.9} {cy + 2}Z", c2)
        sh.circle_r(cx - 6, cy + 12, 2.5, c2); sh.circle_r(cx + 6, cy + 12, 2.5, c2); sh.circle_r(cx, cy - 13, 2.5, c2)
        sh.raw("</g>")
    # nest
    sh.region("M44 118C44 150 70 164 100 164C130 164 156 150 156 118C140 128 60 128 44 118Z", "w")
    sh.line("M54 132Q76 140 100 138T148 132M62 148Q84 154 100 152T140 148")
    # kuikentje
    sh.circle_r(160, 76, 12, "y")
    sh.region("M146 96C146 84 158 80 164 86C176 86 180 100 172 106C164 112 146 108 146 96Z", "y")
    sh.circle_r(156, 76, 10, "y"); sh.poly_r([(145, 76), (139, 78), (145, 80)], "o"); eye(sh, 152, 74, 1.6)
    sh.line("M156 66Q158 60 162 62")
    sh.circle_r(30, 30, 13, "y")

def pakjesboot(sh):
    sh.rect_r(0, 140, 200, 60, "n")
    for k in range(5): sh.line(f"M{4 + k * 42} 176Q{14 + k * 42} 170 {24 + k * 42} 176")
    # boot
    sh.region("M14 116H186L170 156H34Z", "r"); sh.rect_r(14, 116, 172, 8, "-")
    for x in (50, 76, 102, 128, 154): sh.circle_r(x, 140, 5, "-")
    sh.rect_r(50, 86, 96, 30, "-", 2)
    for x in (60, 84, 108, 130): sh.rect_r(x, 92, 12, 12, "b", 2)
    sh.rect_r(110, 50, 20, 36, "z"); sh.rect_r(110, 50, 20, 8, "x")
    sh.region("M114 46C108 34 120 24 128 30C134 18 152 22 150 34C160 34 160 46 150 46Z", "-")
    # pakjes op het dek
    sh.rect_r(22, 96, 20, 20, "y"); sh.line("M32 96V116M22 106H42"); sh.line("M32 96Q26 88 30 92M32 96Q38 88 34 92")
    sh.rect_r(156, 100, 22, 16, "m"); sh.line("M167 100V116"); sh.rect_r(160, 86, 14, 14, "g"); sh.line("M167 86V100")
    # vlaggenlijn
    sh.line("M14 116L40 60L70 86M146 86L176 52L186 116")
    for x, y, c in ((24, 94, "r"), (32, 78, "y"), (50, 70, "b"), (60, 78, "m"), (156, 74, "y"), (166, 62, "b"), (180, 70, "r"), (182, 90, "g")):
        sh.poly_r([(x - 3.5, y - 2), (x + 3.5, y - 2), (x, y + 6)], c)
    sh.region(moon_path(30, 26, 12), "y")

def kerstsokken(sh):
    sh.rect_r(0, 180, 200, 20, "w")
    # schoorsteenmantel
    sh.rect_r(22, 70, 156, 112, "r")
    for y in (88, 106, 124, 142, 160):
        sh.seg(22, y, 178, y)
    for row, y in enumerate((70, 88, 106, 124, 142, 160)):
        for x in range(22 + (20 if row % 2 else 0), 178, 40): sh.seg(x, y, x, y + 18) if x > 22 else None
    sh.rect_r(56, 112, 88, 70, "x", 0)
    sh.region("M70 182C66 168 80 156 84 146C90 160 92 150 100 138C106 154 112 150 116 144C122 160 134 168 130 182Z", "o")
    sh.region("M84 182C82 172 92 166 100 158C108 166 118 172 116 182Z", "y")
    sh.rect_r(76, 176, 48, 6, "w", 2)
    sh.rect_r(14, 60, 172, 12, "w", 2)
    # sokken
    for x, c, d in ((40, "g", "-"), (100, "n", "-"), (160, "r", "-")):
        sh.seg(x, 72, x, 76, "l")
        sh.region(f"M{x - 10} 76H{x + 10}V108Q{x + 10} 118 {x + 2} 120L{x - 14} 122Q{x - 24} 122 {x - 24} 114Q{x - 24} 106 {x - 10} 104Z", c)
        sh.rect_r(x - 12, 74, 24, 10, d, 3)
    sh.region(star_path(100, 96, 6, 2.6), "y"); sh.region(heart_path(40, 96, 4), "-"); sh.circle_r(160, 96, 4, "-")
    # kaarsjes en guirlande op de schoorsteen
    for x in (34, 166):
        sh.rect_r(x - 4, 38, 8, 22, "-"); sh.region(f"M{x} 26Q{x + 5} 32 {x} 36Q{x - 5} 32 {x} 26Z", "y")
    sh.line("M50 60Q75 50 100 60T150 60")
    for x, c in ((62, "r"), (88, "y"), (112, "b"), (138, "r")): sh.circle_r(x, 56 + (0 if x in (62, 138) else 0), 3.5, c)
    sh.region(star_path(100, 28, 14, 6), "y")

def vrijmarkt(sh):
    sh.region("M0 200V120H200V200Z", "z")
    for x in range(0, 200, 40): sh.seg(x, 120, x - 20, 200)
    # vlaggenlijn met oranje vlaggetjes
    sh.line("M0 20Q50 46 100 26T200 24")
    for k, x in enumerate(range(12, 200, 22)):
        y = 20 + 18 * math.sin(math.pi * (x / 100)) ** 2 * (1 if x < 100 else .2) + (0 if x < 100 else 4)
        y = 20 + (26 - abs(x - 50) * .5) if x < 100 else 26 + (6 - abs(x - 150) * .1) * 0
        sh.poly_r([(x - 6, y - 2), (x + 6, y - 2), (x, y + 12)], "o" if k % 2 == 0 else "-")
    # kleed
    sh.region("M24 190L44 124H156L176 190Z", "o")
    sh.line("M38 146H162M30 168H170M78 124L72 190M122 124L128 190")
    # spulletjes: beer, bal, boekjes, kroon
    sh.circle_r(64, 140, 12, "w"); sh.circle_r(54, 128, 5, "w"); sh.circle_r(74, 128, 5, "w")
    sh.ellipse_r(64, 162, 14, 12, "w"); eye(sh, 60, 138, 1.6); eye(sh, 68, 138, 1.6); sh.ellipse_r(64, 144, 3.5, 2.5, "x")
    sh.circle_r(140, 168, 13, "r"); sh.line("M127 168H153M140 155Q148 168 140 181")
    sh.rect_r(92, 160, 28, 8, "b", 1); sh.rect_r(94, 152, 24, 8, "g", 1); sh.rect_r(90, 168, 32, 8, "y", 1)
    sh.region("M128 140L132 124L140 134L148 122L154 134L160 124L162 140Z", "y")
    # bordje met prijs
    sh.rect_r(92, 120, 32, 18, "-", 2); sh.text(108, 133, "1 euro", 6.5)
    sh.region(cloud_path(156, 70, 14), "-"); sh.circle_r(40, 72, 14, "y")

def sint_maarten(sh):
    sh.rect_r(0, 0, 200, 200, "n")
    sh.rect_r(0, 180, 200, 20, "z")
    sh.region(moon_path(30, 32, 14), "y")
    for x, y in ((70, 20), (110, 40), (60, 60)): sh.region(star_path(x, y, 5, 2.2), "y")
    # huis met deur
    sh.rect_r(130, 60, 70, 120, "w"); sh.region("M120 66L170 24L200 50V66Z", "r")
    sh.rect_r(148, 112, 34, 68, "r", 2); sh.circle_r(176, 148, 2.5, "y"); sh.rect_r(150, 76, 30, 24, "y", 2); sh.seg(165, 76, 165, 100)
    # kind met lampion
    person(sh, 76, 72, "g", "n", hands=((54, 128), (102, 112)), cap=True)
    sh.region("M60 80C58 60 94 60 92 80Z", "r"); sh.circle_r(76, 60, 4.5, "-"); sh.rect_r(60, 77, 32, 6, "-", 2)
    sh.region("M60 98Q76 108 92 98L90 106Q76 112 62 106Z", "y")
    sh.line("M102 112L118 96"); sh.line("M118 96V108")
    sh.region("M106 110H130V136H106Z", "o"); sh.ellipse_r(118, 110, 12, 3, "r"); sh.ellipse_r(118, 136, 12, 3, "r")
    sh.region("M118 114Q124 122 118 130Q112 122 118 114Z", "y")


PLATES = [
    ("tuinman", "Tuinman met kruiwagen", "beroepen", "4-6", 2, tuinman, None),
    ("schilder", "Schilder bij de ezel", "beroepen", "4-6", 2, schilder, None),
    ("piloot", "Piloot in een vliegtuigje", "beroepen", "4-6", 2, piloot, None),
    ("postbode", "Postbode met een brief", "beroepen", "4-6", 2, postbode, None),
    ("visser", "Visser in een bootje", "beroepen", "4-6", 2, visser, None),
    ("judo", "Judoka met een zwarte band", "sport", "6-9", 2, judo, None),
    ("hockey", "Hockeyen", "sport", "6-9", 2, hockey, None),
    ("turnen", "Turnen op de balk", "sport", "4-6", 2, turnen, None),
    ("paardrijden", "Paardrijden", "sport", "6-9", 3, paardrijden, None),
    ("stal", "Paard in de stal", "boerderij", "4-6", 2, stal, None),
    ("hooiberg", "Hooiberg", "boerderij", "2-4", 1, hooiberg, None),
    ("eend-met-kuikens", "Eend met kuikens", "boerderij", "2-4", 1, eend_met_kuikens, None),
    ("klein-draakje", "Klein draakje", "sprookjes", "4-6", 2, klein_draakje, None),
    ("elfje", "Elfje met toverstaf", "sprookjes", "4-6", 2, elfje, None),
    ("toverhoed", "Toverhoed met konijn", "sprookjes", "2-4", 1, toverhoed, None),
    ("schatkist", "Schatkist", "sprookjes", "6-9", 2, schatkist, None),
    ("satelliet", "Satelliet", "ruimte", "4-6", 2, satelliet, None),
    ("komeet", "Komeet", "ruimte", "2-4", 1, komeet, None),
    ("maanlander", "Maanlander", "ruimte", "6-9", 3, maanlander, None),
    ("iglo", "Iglo", "wereld", "2-4", 1, iglo, None),
    ("pagode", "Pagode", "wereld", "6-9", 2, pagode, None),
    # ("tipi", "Tipi-tent", "wereld", "4-6", 2, tipi, None),
    ("windmolenpark", "Windmolenpark", "wereld", "4-6", 1, windmolenpark, None),
    ("ankylosaurus", "Ankylosaurus", "dinos", "4-6", 2, ankylosaurus, None),
    ("parasaurolophus", "Parasaurolophus", "dinos", "6-9", 2, parasaurolophus, None),
    ("paasnest", "Paasnest met eieren", "feest", "2-4", 1, paasnest, "pasen"),
    ("pakjesboot", "Pakjesboot", "feest", "4-6", 2, pakjesboot, "sinterklaas"),
    ("kerstsokken", "Kerstsokken bij de open haard", "feest", "6-9", 2, kerstsokken, "kerst"),
    ("vrijmarkt", "Vrijmarkt op Koningsdag", "feest", "6-9", 2, vrijmarkt, "koningsdag"),
    ("sint-maarten", "Sint-Maarten: lopen met je lampion", "feest", "4-6", 2, sint_maarten, "sintmaarten"),
]

for slug, name, cat, age, diff, draw, hol in PLATES:
    kp(slug, name, cat, age, diff, draw, hol)
