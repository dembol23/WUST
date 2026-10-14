"""Zadania 2.9 / 2.10 - rozpoznawanie jezyka, klasy szyfru oraz lamanie hasla."""
from ..analysis import (break_caesar, break_vigenere, entropy, est_key_len, friedman,
                        identify_language, ioc, profile)
from ..ciphers import caesar, rand_key, vigenere
from ..config import LANGS


def run(R, corp, plain_lang, pt, rng, ciphers):
    R.h("Zadania 2.9 / 2.10 - rozpoznawanie jezyka, algorytmu i hasla narzedziami analizy")
    refs = {l: profile(t) for l, t in corp.items()}

    # identyfikacja jezyka (profil z pierwszej polowy, test na drugiej)
    half_refs = {l: profile(t[: len(t) // 2]) for l, t in corp.items()}
    rows = []
    for l, t in corp.items():
        test = t[len(t) // 2:][:500]
        guess = identify_language(test, half_refs)
        rows.append((LANGS[l], len(test), LANGS[guess], "TAK" if guess == l else "NIE"))
    R.table("2_9_rozpoznanie_jezyka",
            ["Jezyk tekstu", "Dlugosc probki", "Rozpoznany (chi2)", "Poprawnie?"], rows)

    # rozpoznanie klasy szyfru - TE SAME szyfrogramy co w zadaniu 2.2 (jedno build_ciphers)
    R.h("Wskazowki do rozpoznania klasy szyfru (IoC, entropia, alfabet)", 3)
    rows = [(name, len(set(sym)), f"{entropy(sym):.3f}", f"{ioc(sym) * 26:.3f}")
            for name, sym, _, _ in ciphers]
    R.table("2_9_wskazowki", ["Szyfr", "Symbole", "H", "IoC*26"], rows)
    R.p("IoC*26 ~ 1.5-1.8 (wartosc jak w jezyku) -> szyfr monoalfabetyczny/przestawieniowy "
        "(rozklad liter bez zmian); IoC*26 -> 1.0 -> polialfabetyczny z dlugim kluczem lub "
        "macierzowy; 6 symboli -> ADFGVX; alfabet 100 symboli -> homofony; brak dwoch jednakowych "
        "liter obok siebie w parach -> Playfair.")

    # lamanie Cezara
    R.h("Lamanie Cezara (2.10 - klucz z analizy czestosci)", 3)
    rows = []
    for k in (3, 11, 20):
        kk, lang = break_caesar(caesar(pt, k), refs)
        rows.append((k, kk, LANGS[lang], "TAK" if kk == k else "NIE"))
    R.table("2_10_lamanie_cezara",
            ["Prawdziwy klucz", "Odzyskany klucz", "Rozpoznany jezyk", "Sukces?"], rows)

    # lamanie Vigenere; kp we wzorze Friedmana = IoC jezyka tekstu jawnego
    kp = ioc(list(corp[plain_lang]))
    R.h("Lamanie Vigenere (2.10 - Kasiski/IoC + analiza kolumn)", 3)
    rows = []
    for L in (3, 5, 8, 12):
        k = rand_key(L, rng)
        ct = vigenere(pt, k)
        Lest, _ = est_key_len(ct)
        fr = friedman(ct, kp)
        _, _, key, _ = break_vigenere(ct, Lest, refs)
        rows.append((L, k, Lest, f"{fr:.1f}", key, "TAK" if key == k else "NIE"))
    R.table("2_10_lamanie_vigenere",
            ["Prawdziwa dl.", "Prawdziwy klucz", "Dl. z IoC kolumn",
             f"Dl. z wzoru Friedmana (kp={kp:.4f})", "Odzyskany klucz", "Sukces?"], rows)
    R.p("Uwaga: skutecznosc zalezy od dlugosci szyfrogramu (przy ~500 znakach i dlugim kluczu "
        "kolumny sa zbyt krotkie). Wzor Friedmana jest bardzo czuly na krotki tekst.")
