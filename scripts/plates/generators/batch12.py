"""Batch 12: doolhoven en verbind-de-punten in nieuwe thema's."""
import math
from lib_gen import *
from shapes import heart_path, star_path, leaf_path

# figuurtjes (klein, rond x,y)
def bij(sh, x, y):
    sh.ellipse_r(x, y, 8, 6, "y"); sh.line(f"M{x - 2} {y - 6}V{y + 6}M{x + 3} {y - 6}V{y + 6}")
    sh.ellipse_r(x - 2, y - 9, 4, 3, "-"); sh.ellipse_r(x + 3, y - 9, 4, 3, "-"); sh.dot(x + 6, y - 1, 1)
def bloem(sh, x, y):
    for k in range(5): a = math.radians(k * 72); sh.circle_r(x + 5 * math.cos(a), y + 5 * math.sin(a), 4, "m")
    sh.circle_r(x, y, 3, "y")
def hond(sh, x, y):
    sh.circle_r(x, y, 7, "w"); sh.ellipse_r(x - 7, y, 3, 6, "w"); sh.ellipse_r(x + 7, y, 3, 6, "w"); sh.dot(x - 2.5, y - 1, 1); sh.dot(x + 2.5, y - 1, 1); sh.dot(x, y + 3, 1.4)
def bot(sh, x, y):
    sh.region(f"M{x - 8} {y - 3}A3 3 0 1 1 {x - 6} {y - 6}H{x + 6}A3 3 0 1 1 {x + 8} {y - 3}V{y + 3}A3 3 0 1 1 {x + 6} {y + 6}H{x - 6}A3 3 0 1 1 {x - 8} {y + 3}Z", "-")
def auto(sh, x, y):
    sh.region(f"M{x - 10} {y + 3}V{y - 1}L{x - 5} {y - 1}L{x - 2} {y - 6}H{x + 4}L{x + 7} {y - 1}H{x + 10}V{y + 3}Z", "r"); sh.circle_r(x - 5, y + 4, 2.5, "x"); sh.circle_r(x + 5, y + 4, 2.5, "x")
def garage(sh, x, y):
    sh.poly_r([(x - 10, y - 2), (x, y - 10), (x + 10, y - 2)], "r"); sh.rect_r(x - 9, y - 2, 18, 12, "z"); sh.rect_r(x - 5, y + 2, 10, 8, "-")
def kabouter(sh, x, y):
    sh.poly_r([(x - 5, y - 2), (x, y - 14), (x + 5, y - 2)], "r"); sh.circle_r(x, y + 2, 4.5, "k"); sh.region(f"M{x - 5} {y + 3}Q{x} {y + 14} {x + 5} {y + 3}Z", "-")
def paddenstoel(sh, x, y):
    sh.region(f"M{x - 10} {y}A10 9 0 0 1 {x + 10} {y}Z", "r"); sh.rect_r(x - 3, y, 6, 8, "-"); sh.circle_r(x - 4, y - 4, 1.6, "-"); sh.circle_r(x + 3, y - 6, 1.6, "-")
def pinguin(sh, x, y):
    sh.ellipse_r(x, y, 6, 9, "x"); sh.ellipse_r(x, y + 1, 4, 7, "-"); sh.poly_r([(x - 1.5, y - 4), (x + 1.5, y - 4), (x, y - 2)], "o"); sh.dot(x - 2, y - 6, .9); sh.dot(x + 2, y - 6, .9)
def ijsschots(sh, x, y):
    sh.poly_r([(x - 12, y + 4), (x - 8, y - 4), (x + 6, y - 6), (x + 12, y + 2), (x + 4, y + 6)], "b")
def eekhoorn(sh, x, y):
    sh.region(f"M{x + 2} {y + 8}C{x + 14} {y + 8} {x + 14} {y - 10} {x + 4} {y - 10}C{x + 10} {y - 4} {x + 8} {y + 4} {x + 2} {y + 4}Z", "o")
    sh.ellipse_r(x - 2, y + 2, 5, 7, "o"); sh.circle_r(x - 3, y - 6, 4, "o"); sh.dot(x - 4, y - 7, .9)
def eikel(sh, x, y):
    sh.ellipse_r(x, y + 2, 5, 7, "w"); sh.region(f"M{x - 7} {y - 1}A7 5 0 0 1 {x + 7} {y - 1}Z", "w"); sh.line(f"M{x} {y - 6}V{y - 9}")
def heks(sh, x, y):
    sh.poly_r([(x - 9, y - 3), (x, y - 16), (x + 9, y - 3)], "p"); sh.circle_r(x, y + 1, 5, "l"); sh.dot(x - 2, y, .9); sh.dot(x + 2, y, .9)
def ketel(sh, x, y):
    sh.region(f"M{x - 10} {y - 4}H{x + 10}Q{x + 10} {y + 9} {x} {y + 9}Q{x - 10} {y + 9} {x - 10} {y - 4}Z", "x"); sh.circle_r(x - 3, y - 7, 2.5, "l"); sh.circle_r(x + 3, y - 9, 2, "l")
def slak(sh, x, y):
    sh.circle_r(x + 2, y - 2, 7, "o"); sh.line(f"M{x + 2} {y - 2}m-3 0a3 3 0 1 0 6 0"); sh.region(f"M{x - 12} {y + 5}H{x + 10}Q{x + 12} {y + 5} {x + 10} {y + 3}H{x - 8}Q{x - 10} {y - 6} {x - 12} {y}Z", "k")
def blaadje(sh, x, y): sh.region(leaf_path(x, y, 7, 10), "g")
def drakie(sh, x, y):
    sh.ellipse_r(x, y + 2, 7, 6, "g"); sh.circle_r(x + 6, y - 5, 4, "g"); sh.poly_r([(x - 4, y - 3), (x - 2, y - 8), (x, y - 3)], "y"); sh.dot(x + 7, y - 6, .9)
def kasteeltje(sh, x, y):
    sh.rect_r(x - 10, y - 4, 20, 14, "z"); sh.rect_r(x - 10, y - 9, 5, 5, "z"); sh.rect_r(x + 5, y - 9, 5, 5, "z"); sh.region(f"M{x - 3} {y + 10}V{y + 3}A3 3 0 0 1 {x + 3} {y + 3}V{y + 10}Z", "w")
def zon(sh, x, y):
    sh.circle_r(x, y, 7, "y")
    for k in range(8): a = math.radians(k * 45); sh.seg(x + 9 * math.cos(a), y + 9 * math.sin(a), x + 12 * math.cos(a), y + 12 * math.sin(a))
def wolkje(sh, x, y): sh.region(f"M{x - 11} {y + 4}A5 5 0 0 1 {x - 6} {y - 3}A7 7 0 0 1 {x + 6} {y - 4}A5 5 0 0 1 {x + 11} {y + 4}Z", "-")

doolhof("doolhof-bij-bloem", "Doolhof: bij zoekt een bloem", "Vlieg naar de bloem", 7, 8, "4-6", 1, 1201, bij, bloem, "natuur", "de bij", "de bloem")
doolhof("doolhof-hond-bot", "Doolhof: hond zoekt zijn bot", "Waar is het bot?", 9, 10, "4-6", 1, 1202, hond, bot, "dieren", "de hond", "het bot")
doolhof("doolhof-auto-garage", "Doolhof: auto naar de garage", "Rij naar de garage", 10, 12, "6-9", 2, 1203, auto, garage, "voertuigen", "de auto", "de garage")
doolhof("doolhof-kabouter-paddenstoel", "Doolhof: kabouter naar huis", "Breng de kabouter thuis", 11, 13, "6-9", 2, 1204, kabouter, paddenstoel, "sprookjes", "de kabouter", "de paddenstoel")
doolhof("doolhof-pinguin-ijsschots", "Doolhof: pinguïn naar de ijsschots", "Glij naar de ijsschots", 12, 14, "6-9", 2, 1205, pinguin, ijsschots, "dieren", "de pinguïn", "de ijsschots")
doolhof("doolhof-eekhoorn-eikel", "Doolhof: eekhoorn zoekt een eikel", "Zoek de eikel", 14, 16, "9+", 3, 1206, eekhoorn, eikel, "natuur", "de eekhoorn", "de eikel")
doolhof("doolhof-heks-ketel", "Doolhof: heks zoekt haar ketel", "Waar is de toverketel?", 15, 17, "9+", 3, 1207, heks, ketel, "sprookjes", "de heks", "de ketel")
doolhof("doolhof-slak-blaadje", "Doolhof: slak zoekt een blaadje", "Kruip naar het blaadje", 6, 7, "2-4", 1, 1208, slak, blaadje, "natuur", "de slak", "het blaadje")
doolhof("doolhof-draakje-kasteel", "Doolhof: draakje naar het kasteel", "Vlieg naar het kasteel", 18, 20, "12+", 3, 1209, drakie, kasteeltje, "sprookjes", "het draakje", "het kasteel")
doolhof("doolhof-wolk-zon", "Doolhof: wolkje zoekt de zon", "Waar is de zon?", 8, 9, "4-6", 1, 1210, wolkje, zon, "natuur", "het wolkje", "de zon")

# ---------- verbind de punten ----------
def ground(sh): sh.seg(20, 236, 180, 236, "guide")
def nothing(sh): pass
kroon = [(40, 190), (40, 110), (70, 150), (100, 90), (130, 150), (160, 110), (160, 190)]
kroon = [(40, 190), (40, 150), (40, 110), (55, 130), (70, 150), (85, 120), (100, 90), (115, 120), (130, 150), (145, 130), (160, 110), (160, 150), (160, 190), (130, 190), (100, 190), (70, 190)]
dots_sheet("verbind-de-punten-kroon", "Verbind de punten: kroon", kroon, "4-6", 1, nothing, "kroon", "sprookjes")
boom = [(100, 50), (130, 95), (115, 95), (145, 140), (125, 140), (160, 190), (110, 190), (110, 225), (90, 225), (90, 190), (40, 190), (75, 140), (55, 140), (85, 95), (70, 95)]
dots_sheet("verbind-de-punten-kerstboom", "Verbind de punten: kerstboom", boom, "4-6", 1, nothing, "kerstboom", "feest")
kasteel = [(40, 220), (40, 120), (55, 120), (55, 135), (70, 135), (70, 120), (85, 120), (85, 100), (100, 80), (115, 100), (115, 120), (130, 120), (130, 135), (145, 135), (145, 120), (160, 120), (160, 220), (115, 220), (115, 190), (100, 175), (85, 190), (85, 220)]
dots_sheet("verbind-de-punten-kasteel", "Verbind de punten: kasteel", kasteel, "6-9", 2, ground, "kasteel", "sprookjes")
pad = [(100 + 60 * math.cos(math.radians(a)), 140 - 50 * math.sin(math.radians(a))) for a in range(0, 181, 20)] + [(60, 140), (80, 140), (78, 210), (122, 210), (120, 140), (140, 140)]
pad = [(160, 140)] + [(100 + 60 * math.cos(math.radians(a)), 140 - 50 * math.sin(math.radians(a))) for a in range(20, 161, 20)] + [(40, 140), (80, 140), (78, 210), (122, 210), (120, 140)]
dots_sheet("verbind-de-punten-paddenstoel", "Verbind de punten: paddenstoel", pad, "4-6", 1, ground, "paddenstoel", "natuur")
car = [(30, 170), (30, 145), (55, 140), (75, 110), (102, 110), (130, 110), (150, 140), (172, 145), (172, 170), (156, 170), (100, 170)]
def car_extra(sh): sh.seg(20, 192, 180, 192, "guide"); sh.circle_line(65, 175, 13); sh.circle_line(135, 175, 13)
dots_sheet("verbind-de-punten-auto", "Verbind de punten: auto", car, "4-6", 1, car_extra, "auto", "voertuigen")
eend = [(60, 150), (55, 120), (70, 95), (90, 90), (105, 100), (125, 98), (110, 108), (105, 125), (140, 120), (165, 105), (160, 140), (145, 165), (110, 175), (75, 172)]
def eend_extra(sh): sh.seg(30, 200, 170, 200, "guide"); sh.dot(88, 102, 2.2)
# dots_sheet("verbind-de-punten-eend", "Verbind de punten: eend", eend, "4-6", 1, eend_extra, "eend", "boerderij")
