"""Szyfr Playfaira (J=I, wypelniacz X, a Q gdy powtorzona litera to X)."""
from ..config import A
from ._validate import require_letters


def pf_square(key):
    """Kwadrat 5x5 jako lista 25 liter (bez J)."""
    seen = []
    for c in key.upper().replace("J", "I") + A.replace("J", ""):
        if c in A and c not in seen:
            seen.append(c)
    return seen


def playfair(text, key, decrypt=False):
    require_letters(text)
    sq = pf_square(key)
    pos = {c: divmod(i, 5) for i, c in enumerate(sq)}
    t = text.replace("J", "I")
    if decrypt:
        if len(t) % 2:
            raise ValueError("szyfrogram Playfaira musi miec parzysta dlugosc")
        pairs = [(t[i], t[i + 1]) for i in range(0, len(t), 2)]
        if any(a == b for a, b in pairs):
            raise ValueError("w szyfrogramie Playfaira nie moze byc pary identycznych liter")
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


def playfair_unpad(text):
    """Usuwa wypelniacze wstawione przy szyfrowaniu (best effort).

    Wypelniacz jest zawsze drugim znakiem pary, czyli stoi na nieparzystym
    indeksie: albo miedzy dwiema identycznymi literami, albo na samym koncu.
    Naturalna litera X w tej samej pozycji byloby nieodroznialna - to cecha szyfru.
    """
    out, n = [], len(text)
    for i, c in enumerate(text):
        if i % 2 == 1:
            prev = text[i - 1]
            filler = "Q" if prev == "X" else "X"
            if c == filler and (i == n - 1 or text[i + 1] == prev):
                continue
        out.append(c)
    return "".join(out)
