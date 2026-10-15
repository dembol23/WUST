"""Szyfr przestawieniowy kolumnowy oraz ADFGVX."""
from ..config import A

ADFGVX_LETTERS = "ADFGVX"


def _check_perm(perm):
    n = len(perm)
    if n == 0 or sorted(perm) != list(range(n)):
        raise ValueError("perm musi byc permutacja 0..n-1")


def transposition(text, perm, decrypt=False, pad="X"):
    """Tekst wpisany wierszami w n kolumn, odczyt kolumnami w kolejnosci perm."""
    _check_perm(perm)
    n = len(perm)
    if not decrypt:
        t = text + pad * (-len(text) % n)
        rows = [t[i:i + n] for i in range(0, len(t), n)]
        return "".join("".join(r[c] for r in rows) for c in perm)
    if len(text) % n:
        raise ValueError("dlugosc szyfrogramu musi byc wielokrotnoscia dlugosci permutacji")
    nrows = len(text) // n
    cols = {c: text[i * nrows:(i + 1) * nrows] for i, c in enumerate(perm)}
    return "".join(cols[c][r] for r in range(nrows) for c in range(n))


def adfgvx_square(rng):
    chars = list(A + "0123456789")
    rng.shuffle(chars)
    return chars


def _check_square(sq):
    if len(sq) != 36 or len(set(sq)) != 36:
        raise ValueError("kwadrat ADFGVX musi miec 36 roznych znakow")


def adfgvx(text, sq, perm):
    _check_square(sq)
    pos = {c: divmod(i, 6) for i, c in enumerate(sq)}
    L = ADFGVX_LETTERS
    try:
        fr = "".join(L[pos[c][0]] + L[pos[c][1]] for c in text)
    except KeyError as e:
        raise ValueError(f"znak {e.args[0]!r} spoza kwadratu ADFGVX") from None
    return transposition(fr, perm)


def adfgvx_dec(ct, sq, perm, n):
    """Deszyfruje n znakow tekstu jawnego."""
    _check_square(sq)
    fr = transposition(ct, perm, True)[:2 * n]
    if len(fr) < 2 * n:
        raise ValueError("szyfrogram jest krotszy, niz wynika z n")
    L = ADFGVX_LETTERS
    return "".join(sq[L.index(fr[i]) * 6 + L.index(fr[i + 1])] for i in range(0, 2 * n, 2))
