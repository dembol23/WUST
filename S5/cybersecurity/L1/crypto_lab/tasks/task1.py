"""Zadanie 1 - algorytmy historyczne: wlasciwosci, przestrzen kluczy, szyfrowanie wielokrotne."""
import math
from collections import Counter

from ..analysis import est_key_len, ioc
from ..ciphers import (caesar, gl_mod26_order, hill, pf_square, playfair, rand_hill, rand_key,
                       rot13, transposition, vigenere)
from ..config import A, IDX


def keyspace_fmt(x):
    if x > 10 ** 6:
        return f"{x:.3e} (2^{math.log2(x):.1f})"
    if x > 1:
        return f"{x} (2^{math.log2(x):.1f})"
    return str(x)


def run(R, pt, corp, rng):
    R.h("Zadanie 1.2 - wlasciwosci wybranych algorytmow")
    rows = [
        ("Cezar", "klucz k in 0..25", keyspace_fmt(26), "k=0 (tozsamosc); 25 sensownych kluczy",
         "przeszukanie wszystkich kluczy; analiza czestosci"),
        ("ROT13", "brak klucza (k=13)", "1", "caly szyfr jest 'slaby'; inwolucja: ROT13(ROT13(x))=x",
         "wystarczy zastosowac ROT13 ponownie"),
        ("Vigenere L=5", "slowo dlugosci L", keyspace_fmt(26 ** 5),
         "klucz z jednej litery = Cezar; klucz 'A..A' = tozsamosc; klucz okresowy ('ABAB'='AB')",
         "Kasiski / indeks koincydencji (Friedman) + analiza czestosci kolumn"),
        ("Vigenere L=12", "slowo dlugosci L", keyspace_fmt(26 ** 12), "j.w.",
         "j.w. (potrzeba dluzszego tekstu)"),
        ("Playfair", "kwadrat 5x5 (permutacja 25 liter)", keyspace_fmt(math.factorial(25)),
         "klucze rownowazne (przesuniecia cykliczne wierszy/kolumn kwadratu); "
         "brak digrafow typu AA w szyfrogramie",
         "analiza czestosci digrafow, hill-climbing / simulated annealing, atak ze znanym tekstem"),
        ("Hill 2x2", "macierz odwracalna mod 26", keyspace_fmt(gl_mod26_order(2)),
         "macierze o det niewzglednie pierwszym z 26 odpadaja; M=I tozsamosc",
         "atak ze znanym tekstem (algebra liniowa), analiza digrafow"),
        ("Hill 3x3", "macierz odwracalna mod 26", keyspace_fmt(gl_mod26_order(3)), "j.w.",
         "znany tekst: 3 bloki -> uklad rownan"),
        ("Przestawieniowy L=8", "permutacja kolumn", keyspace_fmt(math.factorial(8)),
         "permutacja tozsamosciowa; L>=dlugosc tekstu", "anagramowanie, analiza digramow"),
        ("Podst. monoalfabet.", "permutacja 26 liter", keyspace_fmt(math.factorial(26)),
         "litery odwzorowane na siebie", "analiza czestosci"),
        ("ADFGVX", "kwadrat 6x6 + slowo L=7", keyspace_fmt(math.factorial(36) * math.factorial(7)),
         "-", "odwrocenie transpozycji + analiza czestosci (atak Painvina)"),
    ]
    R.table("1_2_wlasciwosci",
            ["Algorytm", "Klucz", "Przestrzen kluczy", "Klucze slabe / uwagi", "Metody lamania"], rows)

    R.h("Zadanie 1.2 - weryfikacja wlasciwosci eksperymentem", 3)
    s = pt[:300]
    checks = [
        ("Cezar k=0 jest tozsamoscia", caesar(s, 0) == s),
        ("ROT13 jest inwolucja", rot13(rot13(s)) == s),
        ("Vigenere klucz 'AAAAA' jest tozsamoscia", vigenere(s, "AAAAA") == s),
        ("Vigenere klucz 'DDDD' == Cezar k=3", vigenere(s, "DDDD") == caesar(s, 3)),
        ("Vigenere 'ABAB' == 'AB'", vigenere(s, "ABAB") == vigenere(s, "AB")),
    ]
    key = "PLAYFAIREXAMPLE"
    sq = pf_square(key)
    ct = playfair(s, key)
    shifted_key = "".join(sq[r * 5 + (c + 1) % 5] for r in range(5) for c in range(5))
    checks.append(("Playfair: przesuniecie cykliczne kolumn kwadratu daje IDENTYCZNY szyfrogram "
                   "(klucze rownowazne)", playfair(s, shifted_key) == ct))
    checks.append(("Playfair: w szyfrogramie nigdy nie wystepuje digraf z dwiema identycznymi literami",
                   all(ct[i] != ct[i + 1] for i in range(0, len(ct) - 1, 2))))
    R.table("1_2_weryfikacja", ["Wlasciwosc", "Potwierdzona?"],
            [(a, "TAK" if b else "NIE") for a, b in checks])

    # --- 1.3 szyfrowanie wielokrotne
    R.h("Zadanie 1.3 - szyfrowanie wielokrotne")
    s = pt[:1500]
    rows = []
    c2 = caesar(caesar(s, 5), 9)
    rows.append(("Cezar", "k1=5, k2=9", "Cezar(5)->Cezar(9) == Cezar(14)", c2 == caesar(s, 14),
                 f"IoC={ioc(list(c2)):.4f} (IoC tekstu jawnego {ioc(list(s)):.4f})"))
    rows.append(("ROT13", "2x ROT13", "ROT13(ROT13(x)) == x", rot13(rot13(s)) == s,
                 "3x ROT13 = ROT13, nx: parzyste n -> tekst jawny"))
    k1, k2 = rand_key(3, rng), rand_key(5, rng)
    comb = "".join(A[(IDX[k1[i % 3]] + IDX[k2[i % 5]]) % 26] for i in range(15))
    v2 = vigenere(vigenere(s, k1), k2)
    L, _ = est_key_len(v2)
    rows.append(("Vigenere", f"k1={k1}, k2={k2}",
                 f"rownowazny jednemu Vigenere o kluczu {comb} (L=NWW=15)", v2 == vigenere(s, comb),
                 f"oszacowana dlugosc klucza: {L}"))
    M1, M2 = rand_hill(2, rng), rand_hill(2, rng)
    h2 = hill(hill(s, M1), M2)
    rows.append(("Hill 2x2", f"M1={M1.tolist()}, M2={M2.tolist()}",
                 "rownowazny jednemu Hillowi z macierza M2*M1 mod 26",
                 h2 == hill(s, (M2 @ M1) % 26),
                 "grupa -> brak wzrostu przestrzeni kluczy ponad |GL2(Z26)|"))
    pf1, pf2 = "MONARCHY", "KRYPTOGRAFIA"
    p2 = playfair(playfair(s, pf1), pf2)
    no_aa = all(p2[i] != p2[i + 1] for i in range(0, len(p2) - 1, 2))
    rows.append(("Playfair", f"{pf1} + {pf2}",
                 "wynik nie jest (w praktyce) zadnym pojedynczym Playfairem; wymaga obu kluczy",
                 "n/d", f"IoC={ioc(list(p2)):.4f}, brak AA w digrafach: {no_aa}"))
    t1, t2 = [3, 0, 4, 1, 2], [5, 2, 0, 6, 1, 3, 4]
    s = s[: len(s) // 35 * 35]  # wielokrotnosc 5 i 7 -> brak dopelnien 'X'
    tt = transposition(transposition(s, t1), t2)
    rows.append(("Przestawieniowy", f"perm1={t1}, perm2={t2}",
                 "dalej permutacja pozycji -> histogram i IoC bez zmian "
                 "(podwojna transpozycja jest silniejsza)",
                 sorted(Counter(tt).values()) == sorted(Counter(s).values()),
                 f"IoC={ioc(list(tt)):.4f}"))
    R.table("1_3_wielokrotne", ["Klasa/algorytm", "Parametry", "Wynik", "Zgodne?", "Obserwacje"], rows)
    R.p("Wniosek: w szyfrach monoalfabetycznych i macierzowych (Cezar, ROT13, Hill) skladanie "
        "szyfrowan daje znow ten sam szyfr (struktura grupy) - bezpieczenstwo nie rosnie. "
        "W polialfabetycznym (Vigenere) rosnie okres klucza (NWW), ale szyfr pozostaje okresowy. "
        "Przestawieniowe pozostaja przestawieniowymi (rozklad liter bez zmian), a silniejsze sa "
        "dopiero kombinacje roznych klas (podstawienie + przestawienie = szyfr produktowy, np. ADFGVX).")
