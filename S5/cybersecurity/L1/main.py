#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Laboratorium nr 2 - Kryptoanaliza klasycznych algorytmow szyfrowania
Zamiennik CrypTool 1.4 dla zadan 1 i 2 (Python 3.9+, numpy, matplotlib).

Uruchomienie:
    pip install numpy matplotlib
    python crypto_lab.py                      # domyslnie: teksty z ./texts, wyniki do ./wyniki
    python crypto_lab.py --plain-lang en --length 8000 --seed 7

Teksty do analizy: pliki texts/en.txt, pl.txt, de.txt, fr.txt, it.txt, es.txt
(im dluzsze, tym lepsze statystyki; zalecane >= 20 000 znakow). Brakujace jezyki
sa zastepowane krotkimi probkami wbudowanymi w skrypt (tylko do testu dzialania!).

Wynik: folder 'wyniki' z wykresami PNG, tabelami CSV i plikiem raport_wyniki.md.
"""
import argparse
import csv
import math
import random
import unicodedata
from collections import Counter
from pathlib import Path

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

A = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LANGS = {"en": "angielski", "pl": "polski", "de": "niemiecki",
         "fr": "francuski", "it": "wloski", "es": "hiszpanski"}

SAMPLES = {
    "en": "Cryptography is the art of writing secret messages. Julius Caesar is said to have protected his military letters by replacing every letter with the one three places further in the alphabet. Such a simple shift is easy to break today, because every language leaves a characteristic fingerprint in the frequency of its letters. Arab scholars described frequency analysis already in the ninth century, and since then the contest between code makers and code breakers has never stopped. Later inventors built more complex systems with many alphabets, tables of letter pairs and even rotating machines.",
    "pl": "Kryptografia to sztuka ukrywania treści wiadomości przed osobami niepowołanymi. Podobno Juliusz Cezar chronił listy wysyłane do dowódców, zastępując każdą literę inną, położoną o trzy miejsca dalej w alfabecie. Tak prosty szyfr można dziś złamać w kilka sekund, ponieważ każdy język pozostawia w tekście charakterystyczny ślad w postaci częstości występowania liter. Już w dziewiątym wieku uczeni arabscy opisali analizę częstotliwości i od tamtej pory trwa wyścig pomiędzy twórcami szyfrów a tymi, którzy próbują je łamać. Później powstawały coraz bardziej skomplikowane systemy, wykorzystujące wiele alfabetów, tablice par liter, a nawet obrotowe maszyny szyfrujące.",
    "de": "Die Kryptografie ist die Kunst, Nachrichten so zu verschlüsseln, dass nur der berechtigte Empfänger sie lesen kann. Von Julius Caesar wird berichtet, dass er seine Briefe an die Feldherren schützte, indem er jeden Buchstaben durch den drei Stellen weiter hinten im Alphabet ersetzte. Eine so einfache Verschiebung lässt sich heute in wenigen Sekunden brechen, denn jede Sprache hinterlässt im Text einen typischen Fingerabdruck in der Häufigkeit ihrer Buchstaben. Schon im neunten Jahrhundert beschrieben arabische Gelehrte die Häufigkeitsanalyse, und seitdem hat der Wettstreit zwischen Verschlüsselern und Entzifferern nie aufgehört. Später entstanden immer kompliziertere Verfahren mit mehreren Alphabeten, Tabellen für Buchstabenpaare und sogar drehbare Maschinen.",
    "fr": "La cryptographie est l'art d'écrire des messages secrets que seul le destinataire légitime peut lire. On raconte que Jules César protégeait ses lettres aux généraux en remplaçant chaque lettre par celle qui se trouve trois places plus loin dans l'alphabet. Un décalage aussi simple se casse aujourd'hui en quelques secondes, car chaque langue laisse dans un texte une empreinte caractéristique sous la forme de la fréquence de ses lettres. Dès le neuvième siècle, les savants arabes ont décrit l'analyse des fréquences, et depuis lors la lutte entre ceux qui chiffrent et ceux qui déchiffrent ne s'est jamais arrêtée. Plus tard, on a inventé des systèmes bien plus complexes, utilisant plusieurs alphabets, des tableaux de paires de lettres et même des machines rotatives.",
    "it": "La crittografia è l'arte di scrivere messaggi segreti che solo il destinatario legittimo può leggere. Si racconta che Giulio Cesare proteggesse le lettere inviate ai suoi generali sostituendo ogni lettera con quella che si trova tre posti più avanti nell'alfabeto. Uno spostamento così semplice oggi si rompe in pochi secondi, perché ogni lingua lascia nel testo un'impronta caratteristica nella frequenza delle proprie lettere. Già nel nono secolo gli studiosi arabi descrissero l'analisi delle frequenze, e da allora la gara tra chi cifra e chi decifra non si è mai fermata. In seguito vennero inventati sistemi molto più complessi, con più alfabeti, tabelle di coppie di lettere e perfino macchine rotanti.",
    "es": "La criptografía es el arte de escribir mensajes secretos que solo el destinatario legítimo puede leer. Se cuenta que Julio César protegía las cartas enviadas a sus generales sustituyendo cada letra por la que se encuentra tres posiciones más adelante en el alfabeto. Un desplazamiento tan sencillo se rompe hoy en pocos segundos, porque cada idioma deja en el texto una huella característica en la frecuencia de sus letras. Ya en el siglo noveno los sabios árabes describieron el análisis de frecuencias, y desde entonces la competencia entre quienes cifran y quienes descifran no ha cesado nunca. Más tarde se inventaron sistemas mucho más complejos, con varios alfabetos, tablas de pares de letras e incluso máquinas giratorias.",
}

OUT = Path("wyniki")


# ======================================================================
# Normalizacja tekstu (zalecenie z instrukcji: tylko alfabet lacinski A-Z)
# ======================================================================
def normalize(text):
    text = text.replace("ł", "l").replace("Ł", "L").replace("ß", "ss")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return "".join(c for c in text.upper() if c in A)


# ======================================================================
# SZYFRY
# ======================================================================
def caesar(text, k, decrypt=False):
    k = -k if decrypt else k
    return "".join(A[(A.index(c) + k) % 26] for c in text)


def rot13(text):
    return caesar(text, 13)


def vigenere(text, key, decrypt=False):
    s = -1 if decrypt else 1
    return "".join(A[(A.index(c) + s * A.index(key[i % len(key)])) % 26]
                   for i, c in enumerate(text))


def xor_cipher(text, key):
    """XOR bajtow tekstu z powtarzanym haslem; wynik jako lista tokenow hex."""
    return [f"{ord(c) ^ ord(key[i % len(key)]):02x}" for i, c in enumerate(text)]


def pf_square(key):
    seen = []
    for c in key.upper().replace("J", "I") + A.replace("J", ""):
        if c in A and c not in seen:
            seen.append(c)
    return seen


def playfair(text, key, decrypt=False):
    sq = pf_square(key)
    pos = {c: divmod(i, 5) for i, c in enumerate(sq)}
    t = text.replace("J", "I")
    if decrypt:
        pairs = [(t[i], t[i + 1]) for i in range(0, len(t) - 1, 2)]
    else:
        pairs, i = [], 0
        while i < len(t):
            a = t[i]
            b = t[i + 1] if i + 1 < len(t) else None
            if b is None or a == b:
                b = "X" if a != "X" else "Q"
                i += 1
            else:
                i += 2
            pairs.append((a, b))
    d = -1 if decrypt else 1
    out = []
    for a, b in pairs:
        ra, ca = pos[a]
        rb, cb = pos[b]
        if ra == rb:
            out += [sq[ra * 5 + (ca + d) % 5], sq[rb * 5 + (cb + d) % 5]]
        elif ca == cb:
            out += [sq[((ra + d) % 5) * 5 + ca], sq[((rb + d) % 5) * 5 + cb]]
        else:
            out += [sq[ra * 5 + cb], sq[rb * 5 + ca]]
    return "".join(out)


def mat_inv_mod(M, m=26):
    M = np.array(M)
    n = len(M)
    det = int(round(np.linalg.det(M))) % m
    inv_det = pow(det, -1, m)
    adj = np.zeros((n, n), dtype=int)
    for i in range(n):
        for j in range(n):
            minor = np.delete(np.delete(M, i, 0), j, 1)
            adj[j][i] = ((-1) ** (i + j)) * int(round(np.linalg.det(minor)))
    return (inv_det * adj) % m


def rand_hill(n, rng):
    while True:
        M = np.array([[rng.randint(0, 25) for _ in range(n)] for _ in range(n)])
        if math.gcd(int(round(np.linalg.det(M))) % 26, 26) == 1:
            return M


def hill(text, M, decrypt=False):
    M = np.array(M)
    n = len(M)
    if decrypt:
        M = mat_inv_mod(M)
    t = text + "X" * (-len(text) % n)
    v = np.array([A.index(c) for c in t]).reshape(-1, n).T
    r = (M @ v) % 26
    return "".join(A[i] for i in r.T.flatten())


def transposition(text, perm, decrypt=False, pad="X"):
    """Przestawieniowy (kolumnowy): tekst wpisany wierszami w n kolumn,
    odczyt kolumnami w kolejnosci perm (lista indeksow 0..n-1)."""
    n = len(perm)
    if not decrypt:
        t = text + pad * (-len(text) % n)
        rows = [t[i:i + n] for i in range(0, len(t), n)]
        return "".join("".join(r[c] for r in rows) for c in perm)
    nrows = len(text) // n
    cols = {c: text[i * nrows:(i + 1) * nrows] for i, c in enumerate(perm)}
    return "".join(cols[c][r] for r in range(nrows) for c in range(n))


def adfgvx_square(rng):
    chars = list(A + "0123456789")
    rng.shuffle(chars)
    return chars


def adfgvx(text, sq, perm):
    L = "ADFGVX"
    fr = "".join(L[sq.index(c) // 6] + L[sq.index(c) % 6] for c in text)
    return transposition(fr, perm)


def adfgvx_dec(ct, sq, perm, n):
    L = "ADFGVX"
    fr = transposition(ct, perm, True)[:2 * n]
    return "".join(sq[L.index(fr[i]) * 6 + L.index(fr[i + 1])] for i in range(0, 2 * n, 2))


def make_homophones(pt, total=100, rng=None):
    cnt, n = Counter(pt), len(pt)
    spare = total - 26
    ideal = {c: cnt.get(c, 0) / n * spare for c in A}
    alloc = {c: 1 + int(ideal[c]) for c in A}
    rem = total - sum(alloc.values())
    for c in sorted(A, key=lambda c: ideal[c] - int(ideal[c]), reverse=True)[:rem]:
        alloc[c] += 1
    nums = list(range(total))
    rng.shuffle(nums)
    table, i = {}, 0
    for c in A:
        table[c] = nums[i:i + alloc[c]]
        i += alloc[c]
    return table


def homophonic(pt, table, rng):
    return [f"{rng.choice(table[c]):02d}" for c in pt]


def rand_key(L, rng):
    return "".join(rng.choice(A) for _ in range(L))


# ======================================================================
# NARZEDZIA ANALIZY
# ======================================================================
def entropy(sym):
    c, n = Counter(sym), len(sym)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def ioc(sym):
    c, n = Counter(sym), len(sym)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) if n > 1 else 0.0


def ngram_counter(sym, n):
    return Counter(zip(*[sym[i:] for i in range(n)]))


def glabel(g):
    return "".join(g) if all(len(x) == 1 for x in g) else "-".join(g)


def ngram_entropy(sym, n):
    c = ngram_counter(sym, n)
    tot = sum(c.values())
    return -sum(v / tot * math.log2(v / tot) for v in c.values())


def autocorr(sym, max_shift=60):
    idx = {s: i for i, s in enumerate(sorted(set(sym)))}
    arr = np.array([idx[s] for s in sym])
    return [float((arr[:-d] == arr[d:]).mean()) for d in range(1, max_shift + 1)]


def est_period(ac):
    base, mx = np.median(ac), max(ac)
    thr = base + 0.5 * (mx - base)
    for d, v in enumerate(ac, 1):
        if v >= thr:
            return d
    return None


def profile(text):
    c = Counter(text)
    n = len(text)
    return np.array([(c.get(ch, 0) + 0.5) / (n + 13) for ch in A])


def chi2_counts(counts, ref):
    n = counts.sum()
    exp = n * ref
    return float(((counts - exp) ** 2 / exp).sum())


def chi2_text(text, ref):
    c = Counter(text)
    return chi2_counts(np.array([c.get(ch, 0) for ch in A], dtype=float), ref)


def break_caesar_k(s, ref):
    c = Counter(s)
    counts = np.array([c.get(ch, 0) for ch in A], dtype=float)
    best = min(range(26), key=lambda k: chi2_counts(np.roll(counts, -k), ref))
    return best, chi2_counts(np.roll(counts, -best), ref)


def break_caesar(ct, refs):
    best = None
    for lang, ref in refs.items():
        k, sc = break_caesar_k(ct, ref)
        if best is None or sc < best[0]:
            best = (sc, lang, k)
    return best[2], best[1]


def est_key_len(ct, max_len=20):
    sc = {L: float(np.mean([ioc(list(ct[i::L])) for i in range(L)])) for L in range(1, max_len + 1)}
    m = max(sc.values())
    for L in range(1, max_len + 1):
        if sc[L] >= 0.9 * m:
            return L, sc


def friedman(ct):
    N, I = len(ct), ioc(list(ct))
    kp, kr = 0.0667, 1 / 26
    den = (N - 1) * I - kr * N + kp
    return (kp - kr) * N / den if den > 0 else float("nan")


def break_vigenere(ct, L, refs):
    best = None
    for lang, ref in refs.items():
        key = "".join(A[break_caesar_k(ct[i::L], ref)[0]] for i in range(L))
        pt = vigenere(ct, key, True)
        sc = chi2_text(pt, ref)
        if best is None or sc < best[0]:
            best = (sc, lang, key, pt)
    return best


def identify_language(text, refs):
    return min(refs, key=lambda l: chi2_text(text, refs[l]))


# ======================================================================
# RAPORT (markdown + CSV) i WYKRESY
# ======================================================================
class Report:
    def __init__(self):
        self.lines = []

    def h(self, title, lvl=2):
        self.lines += ["", "#" * lvl + " " + title, ""]
        print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)

    def p(self, text):
        self.lines += [text, ""]
        print(text)

    def table(self, name, headers, rows):
        rows = [[(f"{c:.4f}" if isinstance(c, float) else str(c)) for c in r] for r in rows]
        with open(OUT / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            w.writerows(rows)
        md = ["| " + " | ".join(headers) + " |", "|" + "---|" * len(headers)]
        md += ["| " + " | ".join(r) + " |" for r in rows]
        self.lines += md + [""]
        print("\n".join(md))

    def fig(self, fname, caption):
        self.lines += [f"![{caption}]({fname})", f"*{caption}*", ""]
        print(f"[wykres] {fname}")

    def save(self):
        (OUT / "raport_wyniki.md").write_text("\n".join(self.lines), encoding="utf-8")


def hist_grid(items, fname, title, cols=3):
    rows = math.ceil(len(items) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 2.8 * rows), squeeze=False)
    for ax, (name, sym) in zip(axes.flat, items):
        letters = all(isinstance(s, str) and len(s) == 1 and s in A for s in sym)
        alphabet = list(A) if letters else sorted(set(sym), key=str)
        c, n = Counter(sym), len(sym)
        ax.bar(range(len(alphabet)), [c[a] / n * 100 for a in alphabet])
        if len(alphabet) <= 36:
            ax.set_xticks(range(len(alphabet)))
            ax.set_xticklabels([str(a) for a in alphabet], fontsize=6)
        else:
            ax.set_xticks([])
        ax.set_title(name, fontsize=9)
        ax.set_ylabel("% wystapien", fontsize=8)
    for ax in list(axes.flat)[len(items):]:
        ax.axis("off")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=130)
    plt.close(fig)


def ngram_grid(items, n, fname, title, top=12, cols=3):
    rows = math.ceil(len(items) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 3 * rows), squeeze=False)
    for ax, (name, sym) in zip(axes.flat, items):
        c = ngram_counter(sym, n)
        tot = sum(c.values())
        mc = c.most_common(top)
        ax.barh([glabel(g) for g, _ in mc][::-1], [v / tot * 100 for _, v in mc][::-1])
        ax.tick_params(labelsize=7)
        ax.set_title(name, fontsize=9)
        ax.set_xlabel("% wszystkich n-gramow", fontsize=8)
    for ax in list(axes.flat)[len(items):]:
        ax.axis("off")
    fig.suptitle(title)
    fig.tight_layout()
    fig.savefig(OUT / fname, dpi=130)
    plt.close(fig)


# ======================================================================
# DANE
# ======================================================================
def load_corpora(tdir):
    corp, src = {}, {}
    for lang in LANGS:
        f = Path(tdir) / f"{lang}.txt"
        if f.exists():
            corp[lang] = normalize(f.read_text(encoding="utf-8", errors="ignore"))
            src[lang] = f"plik {f} ({len(corp[lang])} znakow)"
        else:
            corp[lang] = normalize(SAMPLES[lang])
            src[lang] = f"PROBKA WBUDOWANA ({len(corp[lang])} znakow) - dodaj {f}"
    return corp, src


def selftest():
    rng = random.Random(1)
    t = "CRYPTOGRAPHYISFUNANDVERYUSEFULFORSECURITYSTUDENTS"
    assert caesar(caesar(t, 7), 7, True) == t
    assert rot13(rot13(t)) == t
    assert vigenere(vigenere(t, "LEMON"), "LEMON", True) == t
    assert playfair(playfair(t, "MONARCHY"), "MONARCHY", True).rstrip("X") == t.rstrip("X")
    M = rand_hill(3, rng)
    assert hill(hill(t, M), M, True).rstrip("X") == t.rstrip("X")
    perm = [2, 0, 3, 1, 4]
    assert transposition(transposition(t, perm), perm, True).rstrip("X") == t.rstrip("X")
    sq = adfgvx_square(rng)
    assert adfgvx_dec(adfgvx(t, sq, perm), sq, perm, len(t)) == t
    print("[selftest] wszystkie szyfry: deszyfrowanie(szyfrowanie(x)) == x  OK")


# ======================================================================
# ZADANIE 1
# ======================================================================
def keyspace_fmt(x):
    return f"{x:.3e} (2^{math.log2(x):.1f})" if x > 10 ** 6 else f"{x} (2^{math.log2(x):.1f})" if x > 1 else str(x)


def gl_mod26(n):
    def gl(p):
        r = 1
        for i in range(n):
            r *= p ** n - p ** i
        return r
    return gl(2) * gl(13)  # |GL_n(Z_26)| = |GL_n(Z_2)| * |GL_n(Z_13)|


def task1(R, pt, corp, rng):
    R.h("Zadanie 1.2 - wlasciwosci wybranych algorytmow")
    rows = [
        ("Cezar", "klucz k in 0..25", keyspace_fmt(26), "k=0 (tozsamosc); 25 sensownych kluczy",
         "przeszukanie wszystkich kluczy; analiza czestosci"),
        ("ROT13", "brak klucza (k=13)", "1", "caly szyfr jest 'slaby'; inwolucja: ROT13(ROT13(x))=x",
         "wystarczy zastosowac ROT13 ponownie"),
        ("Vigenere L=5", "slowo dlugosci L", keyspace_fmt(26 ** 5),
         "klucz z jednej litery = Cezar; klucz 'A..A' = tozsamosc; klucz okresowy ('ABAB'='AB')",
         "Kasiski / indeks koincydencji (Friedman) + analiza czestosci kolumn"),
        ("Vigenere L=12", "slowo dlugosci L", keyspace_fmt(26 ** 12), "j.w.", "j.w. (potrzeba dluzszego tekstu)"),
        ("Playfair", "kwadrat 5x5 (permutacja 25 liter)", keyspace_fmt(math.factorial(25)),
         "klucze rownowazne (przesuniecia cykliczne wierszy/kolumn kwadratu); brak digrafow typu AA w szyfrogramie",
         "analiza czestosci digrafow, hill-climbing / simulated annealing, atak ze znanym tekstem"),
        ("Hill 2x2", "macierz odwracalna mod 26", keyspace_fmt(gl_mod26(2)), "macierze o det niewzglednie pierwszym z 26 odpadaja; M=I tozsamosc",
         "atak ze znanym tekstem (algebra liniowa), analiza digrafow"),
        ("Hill 3x3", "macierz odwracalna mod 26", keyspace_fmt(gl_mod26(3)), "j.w.", "znany tekst: 3 bloki -> uklad rownan"),
        ("Przestawieniowy L=8", "permutacja kolumn", keyspace_fmt(math.factorial(8)),
         "permutacja tozsamosciowa; L>=dlugosc tekstu", "anagramowanie, analiza digramow"),
        ("Podst. monoalfabet.", "permutacja 26 liter", keyspace_fmt(math.factorial(26)), "litery odwzorowane na siebie", "analiza czestosci"),
        ("ADFGVX", "kwadrat 6x6 + slowo L=7", keyspace_fmt(math.factorial(36) * math.factorial(7)), "-",
         "odwrocenie transpozycji + analiza czestosci (atak Painvina)"),
    ]
    R.table("1_2_wlasciwosci", ["Algorytm", "Klucz", "Przestrzen kluczy", "Klucze slabe / uwagi", "Metody lamania"], rows)

    R.h("Zadanie 1.2 - weryfikacja wlasciwosci eksperymentem", 3)
    s = pt[:300]
    checks = []
    checks.append(("Cezar k=0 jest tozsamoscia", caesar(s, 0) == s))
    checks.append(("ROT13 jest inwolucja", rot13(rot13(s)) == s))
    checks.append(("Vigenere klucz 'AAAAA' jest tozsamoscia", vigenere(s, "AAAAA") == s))
    checks.append(("Vigenere klucz 'DDDD' == Cezar k=3", vigenere(s, "DDDD") == caesar(s, 3)))
    checks.append(("Vigenere 'ABAB' == 'AB'", vigenere(s, "ABAB") == vigenere(s, "AB")))
    key = "PLAYFAIREXAMPLE"
    sq = pf_square(key)
    ct = playfair(s, key)
    shifted = [sq[r * 5 + (c + 1) % 5] for r in range(5) for c in range(5)]  # przesuniecie cykliczne kolumn
    shifted_key = "".join(shifted)
    checks.append(("Playfair: przesuniecie cykliczne kolumn kwadratu daje IDENTYCZNY szyfrogram (klucze rownowazne)",
                   playfair(s, shifted_key) == ct))
    checks.append(("Playfair: w szyfrogramie nigdy nie wystepuje digraf z dwiema identycznymi literami",
                   all(ct[i] != ct[i + 1] for i in range(0, len(ct) - 1, 2))))
    R.table("1_2_weryfikacja", ["Wlasciwosc", "Potwierdzona?"], [(a, "TAK" if b else "NIE") for a, b in checks])

    # --- 1.3 szyfrowanie wielokrotne
    R.h("Zadanie 1.3 - szyfrowanie wielokrotne")
    s = pt[:1500]
    rows = []
    c2 = caesar(caesar(s, 5), 9)
    rows.append(("Cezar", "k1=5, k2=9", "Cezar(5)->Cezar(9) == Cezar(14)", c2 == caesar(s, 14),
                 f"IoC={ioc(list(c2)):.4f} (IoC tekstu jawnego {ioc(list(s)):.4f})"))
    rows.append(("ROT13", "2x ROT13", "ROT13(ROT13(x)) == x", rot13(rot13(s)) == s, "3x ROT13 = ROT13, nx: parzyste n -> tekst jawny"))
    k1, k2 = rand_key(3, rng), rand_key(5, rng)
    comb = "".join(A[(A.index(k1[i % 3]) + A.index(k2[i % 5])) % 26] for i in range(15))
    v2 = vigenere(vigenere(s, k1), k2)
    L, _ = est_key_len(v2)
    rows.append(("Vigenere", f"k1={k1}, k2={k2}", f"rownowazny jednemu Vigenere o kluczu {comb} (L=NWW=15)", v2 == vigenere(s, comb),
                 f"oszacowana dlugosc klucza: {L}"))
    M1, M2 = rand_hill(2, rng), rand_hill(2, rng)
    h2 = hill(hill(s, M1), M2)
    rows.append(("Hill 2x2", f"M1={M1.tolist()}, M2={M2.tolist()}", "rownowazny jednemu Hillowi z macierza M2*M1 mod 26",
                 h2 == hill(s, (M2 @ M1) % 26), "grupa -> brak wzrostu przestrzeni kluczy ponad |GL2(Z26)|"))
    pf1, pf2 = "MONARCHY", "KRYPTOGRAFIA"
    p2 = playfair(playfair(s, pf1), pf2)
    rows.append(("Playfair", f"{pf1} + {pf2}", "wynik nie jest (w praktyce) zadnym pojedynczym Playfairem; wymaga obu kluczy",
                 "n/d", f"IoC={ioc(list(p2)):.4f}, brak AA w digrafach: {all(p2[i] != p2[i + 1] for i in range(0, len(p2) - 1, 2))}"))
    t1, t2 = [3, 0, 4, 1, 2], [5, 2, 0, 6, 1, 3, 4]
    tt = transposition(transposition(s, t1), t2)
    rows.append(("Przestawieniowy", f"perm1={t1}, perm2={t2}", "dalej permutacja pozycji -> histogram i IoC bez zmian (podwojna transpozycja jest silniejsza)",
                 sorted(Counter(tt).values()) == sorted(Counter(s).values()), f"IoC={ioc(list(tt)):.4f}"))
    R.table("1_3_wielokrotne", ["Klasa/algorytm", "Parametry", "Wynik", "Zgodne?", "Obserwacje"], rows)
    R.p("Wniosek: w szyfrach monoalfabetycznych i macierzowych (Cezar, ROT13, Hill) skladanie szyfrowan daje znow ten sam szyfr "
        "(struktura grupy) - bezpieczenstwo nie rosnie. W polialfabetycznym (Vigenere) rosnie okres klucza (NWW), ale szyfr "
        "pozostaje okresowy. Przestawieniowe pozostaja przestawieniowymi (rozklad liter bez zmian), a silniejsze sa dopiero "
        "kombinacje roznych klas (podstawienie + przestawienie = szyfr produktowy, np. ADFGVX).")


# ======================================================================
# ZADANIE 2
# ======================================================================
def build_ciphers(pt, rng):
    """Zwraca liste (nazwa, symbole, parametry, fragment szyfrogramu)."""
    res = []

    def add(name, sym, params):
        sym = list(sym)
        res.append((name, sym, params, "".join(sym)[:60]))

    add("Cezar", caesar(pt, 3), "k=3")
    add("ROT13", rot13(pt), "k=13")
    pk = "MONARCHY"
    add("Playfair", playfair(pt, pk), f"klucz={pk}")
    for L in (1, 3, 5, 8, 12, 20):
        k = rand_key(L, rng) if L > 1 else "K"
        add(f"Vigenere L={L}", vigenere(pt, k), f"klucz={k}")
    for n in (2, 3, 4):
        M = rand_hill(n, rng)
        add(f"Hill {n}x{n}", hill(pt, M), f"M={M.tolist()}")
    perm = rng.sample(range(8), 8)
    add("Permutacyjny L=8", transposition(pt, perm), f"perm={perm}")
    sq = adfgvx_square(rng)
    aperm = rng.sample(range(7), 7)
    add("ADFGVX", adfgvx(pt, sq, aperm), f"kwadrat={''.join(sq)}, perm={aperm}")
    table = make_homophones(pt, 100, rng)
    hom = homophonic(pt, table, rng)
    res.append(("Homofony (symbole)", hom, "100 homofonow wg czestosci liter, symbol = liczba 00-99", "".join(hom)[:60]))
    res.append(("Homofony (cyfry)", list("".join(hom)), "ten sam szyfrogram liczony po cyfrach", "".join(hom)[:60]))
    k = rand_key(8, rng)
    res.append(("XOR L=8", xor_cipher(pt, k), f"haslo={k}; symbol = bajt hex", "".join(xor_cipher(pt, k))[:60]))
    return res


def task2(R, corp, src, plain_lang, pt, rng):
    max_h = math.log2(26)
    # --- 2.1
    R.h("Zadanie 2.1 - entropia tekstow jawnych w roznych jezykach")
    R.p("Zrodla tekstow: " + "; ".join(f"{l}: {src[l]}" for l in LANGS))
    rows = [(f"{LANGS[l]} ({l})", len(corp[l]), entropy(list(corp[l])), ioc(list(corp[l])) * 26, max_h - entropy(list(corp[l])))
            for l in LANGS]
    R.table("2_1_entropia_jezyki", ["Jezyk", "Dlugosc", "H [bit/znak]", "IoC*26", "Nadmiarowosc (log2 26 - H)"], rows)
    plt.figure(figsize=(6, 3.5))
    plt.bar([l for l in LANGS], [r[2] for r in rows])
    plt.axhline(max_h, color="r", ls="--", label=f"max = log2(26) = {max_h:.2f}")
    plt.ylim(3.8, 4.8)
    plt.ylabel("entropia [bit/znak]")
    plt.legend()
    plt.tight_layout()
    plt.savefig(OUT / "2_1_entropia_jezyki.png", dpi=130)
    plt.close()
    R.fig("2_1_entropia_jezyki.png", "Entropia tekstow jawnych")

    ciphers = build_ciphers(pt, rng)
    plain_sym = list(pt)

    # --- 2.2
    R.h("Zadanie 2.2 - entropia tekstu jawnego i zaszyfrowanego")
    R.p(f"Tekst jawny: jezyk {LANGS[plain_lang]}, {len(pt)} znakow, poczatek: {pt[:60]}...")
    rows = [("TEKST JAWNY", "-", entropy(plain_sym), ioc(plain_sym), len(set(plain_sym)), pt[:40])]
    for name, sym, params, frag in ciphers:
        rows.append((name, params, entropy(sym), ioc(sym), len(set(sym)), frag[:40]))
    R.table("2_2_entropia_szyfry", ["Algorytm", "Parametry", "H [bit/symbol]", "IoC", "Rozmiar alfabetu", "Poczatek szyfrogramu"], rows)

    # --- 2.3 / 2.4
    R.h("Zadanie 2.3 - histogramy tekstow jawnych")
    hist_grid([(f"{LANGS[l]} ({l})", list(corp[l])) for l in LANGS], "2_3_histogramy_jezyki.png", "Histogramy tekstow jawnych")
    R.fig("2_3_histogramy_jezyki.png", "Histogramy liter - rozne jezyki")
    prof_rows = []
    for l in LANGS:
        c = Counter(corp[l])
        top = ", ".join(f"{ch}={v / len(corp[l]) * 100:.1f}%" for ch, v in c.most_common(6))
        prof_rows.append((LANGS[l], top))
    R.table("2_3_najczestsze_litery", ["Jezyk", "6 najczestszych liter"], prof_rows)

    R.h("Zadanie 2.4 - histogramy tekstu jawnego i szyfrogramow")
    items = [("TEKST JAWNY", plain_sym)] + [(n, s) for n, s, _, _ in ciphers]
    hist_grid(items, "2_4_histogramy_szyfry.png", "Histogramy: tekst jawny vs szyfrogramy", cols=4)
    R.fig("2_4_histogramy_szyfry.png", "Histogramy szyfrogramow")

    # --- 2.5 / 2.6
    R.h("Zadanie 2.5 - n-gramy tekstow jawnych w roznych jezykach")
    for n, nm in ((2, "bigramy"), (3, "trigramy")):
        ngram_grid([(f"{LANGS[l]} ({l})", list(corp[l])) for l in LANGS], n, f"2_5_{nm}_jezyki.png", f"Najczestsze {nm} - jezyki")
        R.fig(f"2_5_{nm}_jezyki.png", f"Najczestsze {nm} w roznych jezykach")
        rows = []
        for r in range(10):
            row = [r + 1]
            for l in LANGS:
                c = ngram_counter(list(corp[l]), n)
                tot = sum(c.values())
                g, v = c.most_common(10)[r]
                row.append(f"{glabel(g)} ({v / tot * 100:.2f}%)")
            rows.append(row)
        R.table(f"2_5_{nm}_top10", ["#"] + [LANGS[l] for l in LANGS], rows)

    R.h("Zadanie 2.6 - n-gramy tekstu jawnego i szyfrogramow")
    rows = []
    for name, sym in [("TEKST JAWNY", plain_sym)] + [(n, s) for n, s, _, _ in ciphers]:
        row = [name]
        for n in (2, 3):
            c = ngram_counter(sym, n)
            tot = sum(c.values())
            top = ", ".join(f"{glabel(g)}:{v / tot * 100:.2f}%" for g, v in c.most_common(3))
            row += [len(c), f"{ngram_entropy(sym, n):.3f}", top]
        rows.append(row)
    R.table("2_6_ngramy_szyfry", ["Algorytm", "Rozne bigramy", "H(bigram) [bit]", "Top-3 bigramy",
                                  "Rozne trigramy", "H(trigram) [bit]", "Top-3 trigramy"], rows)
    for n, nm in ((2, "bigramy"), (3, "trigramy")):
        ngram_grid(items, n, f"2_6_{nm}_szyfry.png", f"Najczestsze {nm}: tekst jawny vs szyfrogramy", cols=4)
        R.fig(f"2_6_{nm}_szyfry.png", f"Najczestsze {nm} szyfrogramow")

    # --- 2.7
    R.h("Zadanie 2.7 - autokorelacja: XOR i Vigenere dla roznych dlugosci hasel")
    lens = (3, 5, 8, 12)
    max_s = 60
    fig, axes = plt.subplots(len(lens) + 1, 2, figsize=(11, 2.4 * (len(lens) + 1)), sharex=True)
    ac_p = autocorr(plain_sym, max_s)
    for j in range(2):
        axes[0][j].plot(range(1, max_s + 1), ac_p, marker=".")
        axes[0][j].set_title("Tekst jawny", fontsize=9)
    rows = []
    for i, L in enumerate(lens, 1):
        k = rand_key(L, rng)
        for j, (nm, sym) in enumerate((("Vigenere", list(vigenere(pt, k))), ("XOR", xor_cipher(pt, k)))):
            ac = autocorr(sym, max_s)
            axes[i][j].plot(range(1, max_s + 1), ac, marker=".")
            axes[i][j].set_title(f"{nm}, |klucz|={L}", fontsize=9)
            rows.append((nm, L, k, est_period(ac), f"{max(ac):.4f}", f"{np.median(ac):.4f}"))
    for ax in axes.flat:
        ax.set_ylabel("czesc zgodnych", fontsize=7)
    axes[-1][0].set_xlabel("przesuniecie")
    axes[-1][1].set_xlabel("przesuniecie")
    fig.tight_layout()
    fig.savefig(OUT / "2_7_autokorelacja.png", dpi=130)
    plt.close(fig)
    R.fig("2_7_autokorelacja.png", "Autokorelacja szyfrogramow Vigenere i XOR")
    R.table("2_7_autokorelacja", ["Algorytm", "Prawdziwa dl. klucza", "Klucz", "Odczytany pierwszy pik (przesuniecie)", "Max", "Mediana"], rows)
    R.p("Piki autokorelacji wystepuja dla przesuniec rownych wielokrotnosciom dlugosci klucza - tak odczytuje sie dlugosc hasla.")


def task_break(R, corp, plain_lang, pt, rng):
    R.h("Zadania 2.9 / 2.10 - rozpoznawanie jezyka, algorytmu i hasla narzedziami analizy")
    refs = {l: profile(t) for l, t in corp.items()}

    # identyfikacja jezyka (profil z pierwszej polowy, test na drugiej)
    half_refs = {l: profile(t[: len(t) // 2]) for l, t in corp.items()}
    rows = []
    for l, t in corp.items():
        test = t[len(t) // 2:][:500]
        guess = identify_language(test, half_refs)
        rows.append((LANGS[l], len(test), LANGS[guess], "TAK" if guess == l else "NIE"))
    R.table("2_9_rozpoznanie_jezyka", ["Jezyk tekstu", "Dlugosc probki", "Rozpoznany (chi2)", "Poprawnie?"], rows)

    # rozpoznanie klasy szyfru po IoC / entropii / liczbie symboli
    R.h("Wskazowki do rozpoznania klasy szyfru (IoC, entropia, alfabet)", 3)
    ciph = build_ciphers(pt, rng)
    rows = []
    for name, sym, _, _ in ciph:
        rows.append((name, len(set(sym)), f"{entropy(sym):.3f}", f"{ioc(sym) * 26:.3f}"))
    R.table("2_9_wskazowki", ["Szyfr", "Symbole", "H", "IoC*26"], rows)
    R.p("IoC*26 ~ 1.6-1.8 (wartosc jak w jezyku) -> szyfr monoalfabetyczny/przestawieniowy (rozklad liter bez zmian); "
        "IoC*26 -> 1.0 -> polialfabetyczny z dlugim kluczem lub macierzowy; 6 symboli -> ADFGVX; alfabet 100 symboli -> homofony; "
        "brak dwoch jednakowych liter obok siebie w parach -> Playfair.")

    # lamanie Cezara
    R.h("Lamanie Cezara (2.10 - klucz z analizy czestosci)", 3)
    rows = []
    for k in (3, 11, 20):
        ct = caesar(pt, k)
        kk, lang = break_caesar(ct, refs)
        rows.append((k, kk, LANGS[lang], "TAK" if kk == k else "NIE"))
    R.table("2_10_lamanie_cezara", ["Prawdziwy klucz", "Odzyskany klucz", "Rozpoznany jezyk", "Sukces?"], rows)

    # lamanie Vigenere
    R.h("Lamanie Vigenere (2.10 - Kasiski/IoC + analiza kolumn)", 3)
    rows = []
    for L in (3, 5, 8, 12):
        k = rand_key(L, rng)
        ct = vigenere(pt, k)
        Lest, _ = est_key_len(ct)
        fr = friedman(ct)
        sc, lang, key, dec = break_vigenere(ct, Lest, refs)
        rows.append((L, k, Lest, f"{fr:.1f}", key, "TAK" if key == k else "NIE"))
    R.table("2_10_lamanie_vigenere", ["Prawdziwa dl.", "Prawdziwy klucz", "Dl. z IoC kolumn", "Dl. z wzoru Friedmana",
                                      "Odzyskany klucz", "Sukces?"], rows)
    R.p("Uwaga: skutecznosc zalezy od dlugosci szyfrogramu (przy ~500 znakach i dlugim kluczu kolumny sa zbyt krotkie).")


# ======================================================================
def main():
    global OUT
    ap = argparse.ArgumentParser(description="Lab 2: kryptoanaliza klasycznych szyfrow")
    ap.add_argument("--texts-dir", default="texts")
    ap.add_argument("--out", default="wyniki")
    ap.add_argument("--plain-lang", default="pl", choices=list(LANGS))
    ap.add_argument("--length", type=int, default=5000, help="dlugosc tekstu jawnego do szyfrowania")
    ap.add_argument("--seed", type=int, default=42)
    a = ap.parse_args()
    OUT = Path(a.out)
    OUT.mkdir(parents=True, exist_ok=True)
    rng = random.Random(a.seed)

    selftest()
    corp, src = load_corpora(a.texts_dir)
    pt = corp[a.plain_lang][: a.length]
    if len(pt) < 2000:
        print(f"[UWAGA] Tekst jawny ma tylko {len(pt)} znakow - wyniki beda zaszumione. "
              f"Wstaw dluzszy plik {a.texts_dir}/{a.plain_lang}.txt (>= 5000 znakow).")

    R = Report()
    R.lines += ["# Wyniki eksperymentow - Laboratorium nr 2", "",
                f"Ziarno generatora: {a.seed}. Tekst jawny: {LANGS[a.plain_lang]}, {len(pt)} znakow.", ""]
    task1(R, pt, corp, rng)
    task2(R, corp, src, a.plain_lang, pt, rng)
    task_break(R, corp, a.plain_lang, pt, rng)
    R.save()
    print(f"\nGotowe. Wyniki w folderze: {OUT.resolve()}  (raport_wyniki.md, *.png, *.csv)")


if __name__ == "__main__":
    main()