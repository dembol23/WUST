"""Interfejs wiersza polecen."""
import argparse
import random
from pathlib import Path

from .ciphers import build_ciphers
from .config import LANGS
from .corpus import load_corpora
from .reporting import Report
from .tasks import breaking, selftest, task1, task2

MIN_PLAIN_LEN = 50


def build_parser():
    ap = argparse.ArgumentParser(prog="crypto_lab",
                                 description="Lab 2: kryptoanaliza klasycznych szyfrow")
    ap.add_argument("--texts-dir", default="texts", help="folder z plikami en.txt, pl.txt, ...")
    ap.add_argument("--out", default="wyniki", help="folder wynikow")
    ap.add_argument("--plain-lang", default="pl", choices=list(LANGS))
    ap.add_argument("--length", type=int, default=5000,
                    help="dlugosc tekstu jawnego do szyfrowania")
    ap.add_argument("--seed", type=int, default=42)
    return ap


def main(argv=None):
    ap = build_parser()
    a = ap.parse_args(argv)
    if a.length < MIN_PLAIN_LEN:
        ap.error(f"--length musi byc >= {MIN_PLAIN_LEN}")

    rng = random.Random(a.seed)
    selftest.run()
    corp, src = load_corpora(a.texts_dir)
    pt = corp[a.plain_lang][: a.length]
    if len(pt) < MIN_PLAIN_LEN:
        ap.error(f"tekst jawny ({a.plain_lang}) ma tylko {len(pt)} znakow (wymagane >= {MIN_PLAIN_LEN})")
    if len(pt) < 2000:
        print(f"[UWAGA] Tekst jawny ma tylko {len(pt)} znakow - wyniki beda zaszumione. "
              f"Wstaw dluzszy plik {a.texts_dir}/{a.plain_lang}.txt (>= 5000 znakow).")

    R = Report(a.out)
    R.lines += ["# Wyniki eksperymentow - Laboratorium nr 2", "",
                f"Ziarno generatora: {a.seed}. Tekst jawny: {LANGS[a.plain_lang]}, {len(pt)} znakow.", ""]

    task1.run(R, pt, corp, rng)
    ciphers = build_ciphers(pt, rng)  # JEDEN zestaw szyfrogramow dla tabel 2.2, 2.4, 2.6 i 2.9
    task2.run(R, corp, src, a.plain_lang, pt, rng, ciphers)
    breaking.run(R, corp, a.plain_lang, pt, rng, ciphers)
    R.save()
    print(f"\nGotowe. Wyniki w folderze: {Path(a.out).resolve()}  (raport_wyniki.md, *.png, *.csv)")
    return 0
