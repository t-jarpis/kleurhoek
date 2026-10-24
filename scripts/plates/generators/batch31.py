"""Batch 31: tekenlessen in zes stappen (deel 3)."""
from lib_gen import *

lesson("tekenles-kikker", "Tekenles: een kikker", [
    [E(50, 64, 30, 22)], [C(36, 40, 9), C(64, 40, 9)], [C(36, 40, 4), C(64, 40, 4), "M34 70Q50 82 66 70"],
    ["M24 76Q10 82 14 92H30", "M76 76Q90 82 86 92H70"], ["M40 86V92M60 86V92M34 92H46M54 92H66"], ["M4 96H96", "M84 30L92 26M84 30L92 34"]], [
    "Teken een breed ovaal lijf.", "Twee ronde ogen bovenop.", "Pupillen en een brede glimlach.", "Twee gebogen achterpoten.", "Twee voorpootjes.", "De grond en een vliegje."], "4-6", 1, "dieren")
lesson("tekenles-giraf", "Tekenles: een giraf", [
    [E(56, 68, 22, 13)], ["M66 60L76 22L84 22L76 62"], [E(82, 18, 9, 6), "M78 12V6M84 12V6", C(84, 16, 1.5)], ["M40 78V96M48 80V96M64 80V96M72 78V96"],
    [C(50, 64, 3), C(62, 70, 3), C(56, 60, 2.5), C(79, 34, 2.5), C(76, 48, 2.5)], ["M34 66Q24 70 26 82"]], [
    "Teken een liggend ovaal lijf.", "Een lange schuine nek.", "Een klein hoofd met horentjes en een oog.", "Vier lange poten.", "Vlekken op het lijf en de nek.", "Een staartje."], "6-9", 2, "dieren")
lesson("tekenles-walvis", "Tekenles: een walvis", [
    ["M14 60Q14 30 50 30Q84 30 86 60Q70 74 40 74Q14 74 14 60Z"], ["M86 60Q94 50 98 40Q96 56 98 68Q92 62 86 64"], [C(28, 50, 2.5), "M14 62Q30 66 44 62"],
    ["M44 66Q40 78 50 74"], ["M44 30Q40 18 34 14M44 30Q48 18 54 14M44 30V16"], ["M4 86Q20 80 36 86T68 86T100 86"]], [
    "Teken een groot bol lijf.", "Een staart aan de achterkant.", "Een oog en de lange mond.", "Een kleine vin.", "Een waterfontein bovenop.", "Golfjes eronder."], "4-6", 1, "zee")
lesson("tekenles-octopus", "Tekenles: een octopus", [
    ["M26 50Q26 14 50 14Q74 14 74 50Z"], ["M26 50Q22 70 14 76", "M74 50Q78 70 86 76"], ["M31 50Q29 72 20 84", "M69 50Q71 72 80 84", "M38 50Q38 76 30 90", "M62 50Q62 76 70 90"],
    ["M46 50Q46 78 42 92", "M54 50Q54 78 58 92"], [C(42, 34, 3), C(58, 34, 3), "M44 44Q50 48 56 44"], ["M84 20Q88 14 92 20Q88 26 84 20", C(12, 30, 3), C(18, 22, 2)]], [
    "Teken een bolle kop met een platte onderkant.", "Twee buitenste armen.", "Vier armen daarbinnen.", "Twee armen in het midden: nu zijn het er acht!", "Ogen en een lieve mond.", "Belletjes en een visje."], "4-6", 1, "zee")
lesson("tekenles-kip", "Tekenles: een kip", [
    [E(48, 62, 26, 20)], [C(70, 40, 12)], ["M80 40L90 44L80 48", "M66 28Q68 20 72 26Q74 18 78 28", C(72, 38, 1.8)], ["M34 58Q48 50 58 62Q46 70 34 58"],
    ["M22 56Q10 44 14 36Q20 46 26 50"], ["M44 82V92M54 82V92M40 92H48M50 92H58"]], [
    "Teken een rond lijf.", "Een hoofd rechtsboven.", "Een snavel, een kammetje en een oog.", "Een vleugel.", "Een staart.", "Pootjes."], "4-6", 1, "boerderij")
lesson("tekenles-varken", "Tekenles: een varken", [
    [E(50, 60, 30, 20)], [C(78, 54, 14)], [E(88, 58, 6, 5), C(86, 58, 1.2), C(90, 58, 1.2), C(76, 48, 1.8)], ["M70 42L72 32L78 40", "M80 40L86 32L86 44"],
    ["M30 76V88M42 78V88M60 78V88M72 76V88"], ["M20 56Q10 52 14 46Q18 42 16 50"]], [
    "Teken een dik ovaal lijf.", "Een rond hoofd ertegenaan.", "Een snuit met twee gaatjes en een oog.", "Twee puntige oortjes.", "Vier korte pootjes.", "Een krulstaartje."], "4-6", 1, "boerderij")
lesson("tekenles-helikopter", "Tekenles: een helikopter", [
    ["M30 60Q30 40 52 40H62Q76 40 76 60Q76 74 56 74H44Q30 74 30 60Z"], ["M76 54H96V62H76", "M96 50V66"], ["M40 52Q42 46 50 46V58H40Z"],
    ["M53 40V32", "M18 30H88"], ["M40 74L36 84M64 74L68 84M28 84H76"], ["M8 20Q14 14 22 20Q28 14 36 20"]], [
    "Teken een ronde cabine.", "Een staart met een kleine rotor.", "Een raam.", "Een lange rotor bovenop.", "De landingsslede.", "Een wolkje."], "6-9", 2, "voertuigen")
lesson("tekenles-sneeuwpop", "Tekenles: een sneeuwpop", [
    [C(50, 72, 22)], [C(50, 38, 15)], ["M38 26H62M42 26V12H58V26"], [C(45, 36, 1.8), C(55, 36, 1.8), "M50 40L60 43L50 45", "M44 48Q50 51 56 48"],
    ["M28 64L12 52M72 64L88 52", C(50, 64, 2), C(50, 74, 2), C(50, 84, 2)], ["M36 52H64L62 58H38Z", "M6 94H94"]], [
    "Teken een grote bal onderaan.", "Een kleinere bal erop.", "Een hoge hoed.", "Ogen, een wortelneus en een mond.", "Takken als armen en knoopjes.", "Een sjaal en de sneeuw."], "4-6", 1, "feest")
