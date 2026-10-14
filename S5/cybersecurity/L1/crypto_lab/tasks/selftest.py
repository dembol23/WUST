"""Test odwracalnosci: deszyfrowanie(szyfrowanie(x)) == x dla kazdego szyfru."""
import random

from ..ciphers import (adfgvx, adfgvx_dec, adfgvx_square, caesar, hill, homophonic,
                       homophonic_decrypt, make_homophones, playfair, playfair_unpad, rand_hill,
                       rot13, transposition, vigenere, xor_cipher, xor_decrypt)

TEXT = "CRYPTOGRAPHYISFUNANDVERYUSEFULFORSECURITYSTUDENTS"
TEXT_DOUBLES = "BALLOONSTOOMANYHELLOWORLDAPPLEXXKEEP"  # powtorzone litery -> wypelniacze Playfaira


def _expect(cond, msg):
    if not cond:  # jawny raise zamiast assert (dziala tez z python -O)
        raise AssertionError(f"selftest: {msg}")


def run(verbose=True):
    rng = random.Random(1)
    t = TEXT
    _expect(caesar(caesar(t, 7), 7, True) == t, "Cezar")
    _expect(rot13(rot13(t)) == t, "ROT13")
    _expect(vigenere(vigenere(t, "LEMON"), "LEMON", True) == t, "Vigenere")
    for txt in (t, TEXT_DOUBLES, TEXT_DOUBLES + "A"):
        dec = playfair(playfair(txt, "MONARCHY"), "MONARCHY", True)
        _expect(playfair_unpad(dec) == txt.replace("J", "I"), f"Playfair ({txt[:8]}...)")
    for n in (2, 3, 4):
        M = rand_hill(n, rng)
        _expect(hill(hill(t, M), M, True).rstrip("X") == t.rstrip("X"), f"Hill {n}x{n}")
    perm = [2, 0, 3, 1, 4]
    _expect(transposition(transposition(t, perm), perm, True).rstrip("X") == t.rstrip("X"),
            "przestawieniowy")
    sq = adfgvx_square(rng)
    _expect(adfgvx_dec(adfgvx(t, sq, perm), sq, perm, len(t)) == t, "ADFGVX")
    table = make_homophones(t * 4, 100, rng)
    _expect(sum(len(v) for v in table.values()) == 100 and all(table.values()),
            "homofony: przydzial symboli")
    _expect(homophonic_decrypt(homophonic(t, table, rng), table) == t, "homofony")
    _expect(xor_decrypt(xor_cipher(t, "KEY"), "KEY") == t, "XOR")
    if verbose:
        print("[selftest] wszystkie szyfry: deszyfrowanie(szyfrowanie(x)) == x  OK")
