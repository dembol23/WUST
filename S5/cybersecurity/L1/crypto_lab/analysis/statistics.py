"""Narzedzia statystyczne: entropia, IoC, n-gramy, autokorelacja."""
import math
from collections import Counter

import numpy as np


def entropy(sym):
    c, n = Counter(sym), len(sym)
    return -sum(v / n * math.log2(v / n) for v in c.values())


def ioc(sym):
    """Indeks koincydencji: sum v(v-1) / (n(n-1))."""
    c, n = Counter(sym), len(sym)
    return sum(v * (v - 1) for v in c.values()) / (n * (n - 1)) if n > 1 else 0.0


def ngram_counter(sym, n):
    if n < 1:
        raise ValueError("n musi byc >= 1")
    sym = list(sym)
    return Counter(tuple(sym[i:i + n]) for i in range(len(sym) - n + 1))


def glabel(g):
    return "".join(g) if all(len(x) == 1 for x in g) else "-".join(g)


def ngram_entropy(sym, n):
    c = ngram_counter(sym, n)
    tot = sum(c.values())
    if tot == 0:
        return 0.0
    return -sum(v / tot * math.log2(v / tot) for v in c.values())


def autocorr(sym, max_shift=60):
    """Odsetek pozycji, na ktorych sym[i] == sym[i+d], d = 1..max_shift.

    max_shift jest przycinane do len(sym) - 1 (dla krotkich tekstow).
    """
    n = len(sym)
    max_shift = min(max_shift, n - 1)
    if max_shift < 1:
        return []
    idx = {s: i for i, s in enumerate(sorted(set(sym), key=str))}
    arr = np.array([idx[s] for s in sym])
    return [float((arr[:-d] == arr[d:]).mean()) for d in range(1, max_shift + 1)]


def est_period(ac):
    """Okres = najmniejsze d, dla ktorego srednia autokorelacji w punktach d, 2d, 3d...
    jest bliska najwyzszej (odporne na szum przy krotkich tekstach).
    Zwraca None, gdy autokorelacja jest zbyt krotka (< 3 punkty)."""
    maxd = len(ac) // 3  # co najmniej 3 wielokrotnosci do usrednienia
    if maxd < 1:
        return None
    score = {d: float(np.mean(ac[d - 1::d])) for d in range(1, maxd + 1)}
    m = max(score.values())
    base = float(np.median(ac))
    for d in range(1, maxd + 1):
        if score[d] - base >= 0.85 * (m - base):
            return d
    return None
