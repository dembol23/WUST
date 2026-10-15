"""Zadanie 2 - analiza wlasnosci algorytmow (entropia, histogramy, n-gramy, autokorelacja)."""
import math
from collections import Counter

import numpy as np

from ..analysis import autocorr, entropy, est_period, glabel, ioc, ngram_counter, ngram_entropy
from ..ciphers import rand_key, vigenere, xor_cipher
from ..config import LANGS
from ..reporting import plots


def _fmt(x):
    return "-" if x is None else x


def run(R, corp, src, plain_lang, pt, rng, ciphers):
    out = R.out_dir
    max_h = math.log2(26)

    # --- 2.1
    R.h("Zadanie 2.1 - entropia tekstow jawnych w roznych jezykach")
    R.p("Zrodla tekstow: " + "; ".join(f"{l}: {src[l]}" for l in LANGS))
    rows = []
    for l in LANGS:
        h = entropy(list(corp[l]))
        rows.append((f"{LANGS[l]} ({l})", len(corp[l]), h, ioc(list(corp[l])) * 26, max_h - h))
    R.table("2_1_entropia_jezyki",
            ["Jezyk", "Dlugosc", "H [bit/znak]", "IoC*26", "Nadmiarowosc (log2 26 - H)"], rows)
    plots.entropy_bar(out, list(LANGS), [r[2] for r in rows], max_h, "2_1_entropia_jezyki.png")
    R.fig("2_1_entropia_jezyki.png", "Entropia tekstow jawnych")

    plain_sym = list(pt)

    # --- 2.2
    R.h("Zadanie 2.2 - entropia tekstu jawnego i zaszyfrowanego")
    R.p(f"Tekst jawny: jezyk {LANGS[plain_lang]}, {len(pt)} znakow, poczatek: {pt[:60]}...")
    rows = [("TEKST JAWNY", "-", entropy(plain_sym), ioc(plain_sym), len(set(plain_sym)), pt[:40])]
    for name, sym, params, frag in ciphers:
        rows.append((name, params, entropy(sym), ioc(sym), len(set(sym)), frag[:40]))
    R.table("2_2_entropia_szyfry",
            ["Algorytm", "Parametry", "H [bit/symbol]", "IoC", "Rozmiar alfabetu",
             "Poczatek szyfrogramu"], rows)

    # --- 2.3 / 2.4
    R.h("Zadanie 2.3 - histogramy tekstow jawnych")
    lang_items = [(f"{LANGS[l]} ({l})", list(corp[l])) for l in LANGS]
    plots.hist_grid(out, lang_items, "2_3_histogramy_jezyki.png", "Histogramy tekstow jawnych")
    R.fig("2_3_histogramy_jezyki.png", "Histogramy liter - rozne jezyki")
    prof_rows = []
    for l in LANGS:
        c = Counter(corp[l])
        top = ", ".join(f"{ch}={v / len(corp[l]) * 100:.1f}%" for ch, v in c.most_common(6))
        prof_rows.append((LANGS[l], top))
    R.table("2_3_najczestsze_litery", ["Jezyk", "6 najczestszych liter"], prof_rows)

    R.h("Zadanie 2.4 - histogramy tekstu jawnego i szyfrogramow")
    items = [("TEKST JAWNY", plain_sym)] + [(c.name, c.symbols) for c in ciphers]
    plots.hist_grid(out, items, "2_4_histogramy_szyfry.png",
                    "Histogramy: tekst jawny vs szyfrogramy", cols=4)
    R.fig("2_4_histogramy_szyfry.png", "Histogramy szyfrogramow")

    # --- 2.5 / 2.6
    R.h("Zadanie 2.5 - n-gramy tekstow jawnych w roznych jezykach")
    for n, nm in ((2, "bigramy"), (3, "trigramy")):
        plots.ngram_grid(out, lang_items, n, f"2_5_{nm}_jezyki.png", f"Najczestsze {nm} - jezyki")
        R.fig(f"2_5_{nm}_jezyki.png", f"Najczestsze {nm} w roznych jezykach")
        counters = {l: ngram_counter(list(corp[l]), n) for l in LANGS}  # raz na jezyk
        tops = {l: counters[l].most_common(10) for l in LANGS}
        totals = {l: sum(counters[l].values()) for l in LANGS}
        rows = []
        for r in range(10):
            row = [r + 1]
            for l in LANGS:
                if r < len(tops[l]):
                    g, v = tops[l][r]
                    row.append(f"{glabel(g)} ({v / totals[l] * 100:.2f}%)")
                else:
                    row.append("-")
            rows.append(row)
        R.table(f"2_5_{nm}_top10", ["#"] + [LANGS[l] for l in LANGS], rows)

    R.h("Zadanie 2.6 - n-gramy tekstu jawnego i szyfrogramow")
    rows = []
    for name, sym in items:
        row = [name]
        for n in (2, 3):
            c = ngram_counter(sym, n)
            tot = sum(c.values())
            top = ", ".join(f"{glabel(g)}:{v / tot * 100:.2f}%" for g, v in c.most_common(3))
            row += [len(c), f"{ngram_entropy(sym, n):.3f}", top]
        rows.append(row)
    R.table("2_6_ngramy_szyfry",
            ["Algorytm", "Rozne bigramy", "H(bigram) [bit]", "Top-3 bigramy",
             "Rozne trigramy", "H(trigram) [bit]", "Top-3 trigramy"], rows)
    for n, nm in ((2, "bigramy"), (3, "trigramy")):
        plots.ngram_grid(out, items, n, f"2_6_{nm}_szyfry.png",
                         f"Najczestsze {nm}: tekst jawny vs szyfrogramy", cols=4)
        R.fig(f"2_6_{nm}_szyfry.png", f"Najczestsze {nm} szyfrogramow")

    # --- 2.7
    R.h("Zadanie 2.7 - autokorelacja: XOR i Vigenere dla roznych dlugosci hasel")
    lens, max_s = (3, 5, 8, 12), 60
    ac_p = autocorr(plain_sym, max_s)
    series, rows = {}, []
    for L in lens:
        k = rand_key(L, rng)
        for nm, sym in (("Vigenere", list(vigenere(pt, k))), ("XOR", xor_cipher(pt, k))):
            ac = autocorr(sym, max_s)
            series[(nm, L)] = ac
            rows.append((nm, L, k, _fmt(est_period(ac)),
                         f"{max(ac):.4f}" if ac else "-",
                         f"{float(np.median(ac)):.4f}" if ac else "-"))
    plots.autocorr_grid(out, ac_p, lens, series, "2_7_autokorelacja.png")
    R.fig("2_7_autokorelacja.png", "Autokorelacja szyfrogramow Vigenere i XOR")
    R.table("2_7_autokorelacja",
            ["Algorytm", "Prawdziwa dl. klucza", "Klucz", "Odczytany pierwszy pik (przesuniecie)",
             "Max", "Mediana"], rows)
    R.p("Piki autokorelacji wystepuja dla przesuniec rownych wielokrotnosciom dlugosci klucza - "
        "tak odczytuje sie dlugosc hasla.")
