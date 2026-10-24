"""Batch 18: tekenlessen in zes stappen."""
from lib_gen import *

lesson("tekenles-konijn", "Tekenles: een konijn", [
    [E(50, 68, 24, 20)], [C(50, 38, 15)], ["M42 26C38 6 46 2 47 24", "M58 26C62 6 54 2 53 24"], [C(44, 36, 2), C(56, 36, 2), "M48 42L50 44L52 42M50 44V47M45 48Q50 51 55 48"],
    [E(36, 86, 9, 5), E(64, 86, 9, 5)], [C(76, 72, 6)]], [
    "Teken een ovaal lijf.", "Een rond hoofd erop.", "Twee lange oren.", "Ogen, een neusje en een mond.", "Twee voeten onderaan.", "Een pluizig staartje."], "4-6", 1, "dieren")
lesson("tekenles-slak", "Tekenles: een slak", [
    ["M10 84H86Q94 84 92 76L84 78"], [C(52, 60, 24)], ["M52 60m-6 0a6 6 0 1 0 12 0a12 12 0 1 0 -24 0a18 18 0 1 0 36 0"],
    ["M18 84Q10 70 22 64Q30 66 30 84"], ["M20 66L14 52M26 64L28 50", C(14, 50, 2), C(28, 48, 2)], ["M2 92H98"]], [
    "Teken een lange lijn: de buik van de slak.", "Een grote cirkel: het huisje.", "Een krul in het huisje.", "Een kopje aan de voorkant.", "Twee voelsprieten met bolletjes.", "De grond."], "2-4", 1, "natuur")
lesson("tekenles-muis", "Tekenles: een muis", [
    ["M20 80Q24 46 60 50Q84 54 86 80Z"], [C(26, 58, 9), C(40, 54, 9)], [C(24, 70, 2), "M10 76L18 75", "M12 80L18 78"], ["M14 72L6 74"],
    ["M86 78Q98 70 92 56Q88 48 96 42"], ["M40 80V86M66 80V86"]], [
    "Teken een halve cirkel: het lijfje.", "Twee ronde oren bovenop.", "Een oog en snorharen.", "Een puntig neusje.", "Een lange kronkelstaart.", "Twee pootjes."], "4-6", 1, "dieren")
lesson("tekenles-beer", "Tekenles: een beer", [
    [C(50, 34, 18)], [C(34, 18, 7), C(66, 18, 7)], [E(50, 40, 8, 6), C(43, 30, 2), C(57, 30, 2), "M50 40V44M46 46Q50 48 54 46"], [E(50, 74, 24, 22)],
    [E(26, 66, 7, 12), E(74, 66, 7, 12)], [E(38, 94, 9, 5), E(62, 94, 9, 5)]], [
    "Teken een rond hoofd.", "Twee ronde oren.", "Een snuit met neus, ogen en mond.", "Een dik lijf.", "Twee armen.", "Twee voeten."], "4-6", 1, "dieren")
lesson("tekenles-vos", "Tekenles: een vos", [
    ["M30 30L50 58L70 30Q50 22 30 30Z"], ["M30 30L30 12L42 26", "M70 30L70 12L58 26"], [C(42, 36, 2), C(58, 36, 2), C(50, 56, 3)],
    ["M40 58Q34 80 40 92H64Q70 80 62 58"], ["M64 88Q92 90 92 66Q90 56 82 60Q86 76 66 80"], ["M86 62L92 66L86 70"]], [
    "Teken een driehoek met de punt naar beneden: de kop.", "Twee puntige oren.", "Ogen en een neus.", "Een lijf onder de kop.", "Een dikke pluimstaart.", "Een wit puntje aan de staart."], "6-9", 2, "dieren")
lesson("tekenles-trein", "Tekenles: een trein", [
    ["M10 50H54V80H10Z"], ["M54 60H84V80H54Z", "M62 60V44H72V60"], [C(22, 84, 6), C(42, 84, 6), C(66, 84, 6)], ["M18 56H34V68H18Z", "M38 56H48V68H38Z"],
    ["M84 74L92 80H84"], ["M66 38Q70 30 76 34Q80 26 88 30", "M2 92H98"]], [
    "Teken een rechthoek: de cabine.", "Een lagere rechthoek ernaast en een schoorsteen.", "Drie wielen.", "Twee raampjes.", "Een puntje vooraan.", "Rookwolkjes en de rails."], "4-6", 1, "voertuigen")
lesson("tekenles-vliegtuig", "Tekenles: een vliegtuig", [
    ["M10 52Q10 42 20 42H82Q94 46 82 56H20Q10 56 10 52Z"], ["M44 48L30 76H40L60 48"], ["M44 48L34 26H42L58 44"], ["M18 44L12 30H20L28 42"],
    [C(66, 48, 2.5), C(58, 48, 2.5), C(50, 48, 2.5), "M82 46Q86 46 88 49"], ["M4 70Q10 64 18 70Q24 64 30 70", "M70 20Q76 14 84 20Q90 14 96 20"]], [
    "Teken een lange romp met een ronde neus.", "Een vleugel naar beneden.", "Een vleugel naar boven.", "Een staart achteraan.", "Raampjes en het cockpitraam.", "Wolkjes in de lucht."], "6-9", 2, "voertuigen")
lesson("tekenles-lieveheersbeestje", "Tekenles: een lieveheersbeestje", [
    [E(50, 58, 26, 30)], [C(50, 26, 10)], ["M50 34V88"], [C(38, 48, 5), C(62, 48, 5), C(40, 70, 4), C(60, 70, 4)],
    ["M44 20L38 8M56 20L62 8", C(38, 7, 2), C(62, 7, 2)], ["M26 50L14 46M24 64L12 66M28 78L18 86M74 50L86 46M76 64L88 66M72 78L82 86"]], [
    "Teken een groot ovaal.", "Een rond kopje erboven.", "Een lijn in het midden: daar gaan de vleugels open.", "Stippen op de vleugels.", "Twee voelsprietjes.", "Zes pootjes, drie aan elke kant."], "2-4", 1, "natuur")
