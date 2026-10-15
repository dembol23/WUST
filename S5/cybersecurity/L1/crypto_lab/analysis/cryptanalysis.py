"""Kryptoanaliza: test chi^2, lamanie Cezara/Vigenere'a, dlugosc klucza, Friedman."""
from collections import Counter

import numpy as np

from ..config import A
from ..ciphers.substitution import vigenere
from .statistics import ioc


def profile(text):
    """Profil czestosci liter z wygladzaniem Laplace'a (brak dzielenia przez 0 w chi^2)."""
    c = Counter(text)
    n = len(text)
    return np.array([(c.get(ch, 0) + 0.5) / (n + 13) for ch in A])


def _counts(text):
    c = Counter(text)
    return np.array([c.get(ch, 0) for ch in A], dtype=float)


def chi2_counts(counts, ref):
    n = counts.sum()
    exp = n * ref
    return float(((counts - exp) ** 2 / exp).sum())


def chi2_text(text, ref):
    return chi2_counts(_counts(text), ref)


def break_caesar_k(s, ref):
    counts = _counts(s)
    best = min(range(26), key=lambda k: chi2_counts(np.roll(counts, -k), ref))
    return best, chi2_counts(np.roll(counts, -best), ref)


def break_caesar(ct, refs):
    """Zwraca (klucz, jezyk) o najmniejszej statystyce chi^2."""
    if not refs:
        raise ValueError("brak profili jezykowych")
    best = None
    for lang, ref in refs.items():
        k, sc = break_caesar_k(ct, ref)
        if best is None or sc < best[0]:
            best = (sc, lang, k)
    return best[2], best[1]


def est_key_len(ct, max_len=20):
    """Najmniejsze L, dla ktorego srednie IoC kolumn >= 90% maksimum. Zwraca (L, wyniki)."""
    sc = {L: float(np.mean([ioc(list(ct[i::L])) for i in range(L)]))
          for L in range(1, max_len + 1)}
    m = max(sc.values())
    for L in range(1, max_len + 1):
        if sc[L] >= 0.9 * m:
            return L, sc
    return 1, sc  # nieosiagalne matematycznie, ale gwarantuje zwrot krotki


def friedman(ct, kp, kr=1 / 26):
    """Wzor Friedmana. kp = IoC jezyka tekstu jawnego (NIE stala angielska 0,0667!)."""
    N, I = len(ct), ioc(list(ct))
    den = (N - 1) * I - kr * N + kp
    return (kp - kr) * N / den if den > 0 and kp > kr else float("nan")


def break_vigenere(ct, L, refs):
    """Zwraca (chi2, jezyk, klucz, tekst jawny) dla najlepiej pasujacego profilu."""
    if not 1 <= L <= len(ct):
        raise ValueError("niepoprawna dlugosc klucza")
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
