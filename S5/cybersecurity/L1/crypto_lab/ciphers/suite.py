"""Zestaw szyfrogramow uzywany w zadaniu 2 (budowany DOKLADNIE RAZ na uruchomienie)."""
from typing import List, NamedTuple

from .hill import hill, rand_hill
from .homophonic import homophonic, make_homophones
from .playfair import playfair
from .substitution import caesar, rand_key, rot13, vigenere, xor_cipher
from .transposition import adfgvx, adfgvx_square, transposition


class CipherResult(NamedTuple):
    name: str
    symbols: List[str]
    params: str
    snippet: str


def build_ciphers(pt, rng):
    """Zwraca liste CipherResult (rozpakowuje sie jak krotka 4-elementowa)."""
    res = []

    def add(name, sym, params):
        sym = list(sym)
        res.append(CipherResult(name, sym, params, "".join(sym)[:60]))

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
    joined = "".join(hom)
    res.append(CipherResult("Homofony (symbole)", hom,
                            "100 homofonow wg czestosci liter, symbol = liczba 00-99", joined[:60]))
    res.append(CipherResult("Homofony (cyfry)", list(joined),
                            "ten sam szyfrogram liczony po cyfrach", joined[:60]))
    k = rand_key(8, rng)
    xr = xor_cipher(pt, k)
    res.append(CipherResult("XOR L=8", xr, f"haslo={k}; symbol = bajt hex", "".join(xr)[:60]))
    return res
