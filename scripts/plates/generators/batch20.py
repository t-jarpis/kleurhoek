"""Batch 20: woordzoekers in nieuwe thema's."""
from wordkit import woordzoeker, H, V, D
woordzoeker("woordzoeker-fruit", "Woordzoeker: fruit", ["APPEL", "PEER", "KERS", "DRUIF", "MELOEN", "KIWI", "MANGO", "PRUIM", "CITROEN", "BANAAN", "LIMOEN", "ANANAS"], 11, [H, V], "6-9", 2, 21, "eten")
woordzoeker("woordzoeker-beroepen", "Woordzoeker: beroepen", ["JUF", "BAKKER", "DOKTER", "SMID", "PILOOT", "BOER", "KAPPER", "AGENT", "VISSER", "SCHILDER", "TUINMAN", "POSTBODE"], 12, [H, V], "6-9", 2, 22, "beroepen")
woordzoeker("woordzoeker-kleding", "Woordzoeker: kleding", ["JAS", "MUTS", "SJAAL", "BROEK", "TRUI", "SOK", "ROK", "JURK", "LAARS", "PET", "SCHOEN", "WANT"], 12, [H, V], "6-9", 2, 23, "thuis")
woordzoeker("woordzoeker-zee", "Woordzoeker: aan zee", ["HAAI", "KRAB", "SCHELP", "GOLF", "STRAND", "EMMER", "MEEUW", "WALVIS", "BOOT", "DOLFIJN", "ZEESTER", "KWAL"], 12, [H, V, D], "9+", 3, 24, "zee")
woordzoeker("woordzoeker-ruimte", "Woordzoeker: de ruimte", ["MAAN", "ZON", "STER", "RAKET", "PLANEET", "KOMEET", "MARS", "AARDE", "SATELLIET", "HEELAL", "ASTRONAUT", "BAAN"], 12, [H, V, D], "9+", 3, 25, "ruimte")
woordzoeker("woordzoeker-feest", "Woordzoeker: feest", ["TAART", "BALLON", "CADEAU", "SLINGER", "KAARS", "MUZIEK", "DANSEN", "SPELLETJE", "VRIENDEN", "HOERA", "FEEST", "LIMONADE"], 12, [H, V, D], "9+", 3, 26, "feest")
