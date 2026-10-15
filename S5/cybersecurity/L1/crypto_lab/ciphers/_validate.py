"""Wspolna walidacja danych wejsciowych szyfrow."""
from ..config import IDX


def require_letters(text, what="tekst"):
    bad = sorted({c for c in text if c not in IDX})
    if bad:
        raise ValueError(f"{what} zawiera znaki spoza A-Z: {''.join(bad)!r}")


def require_key(key, what="klucz"):
    if not key:
        raise ValueError(f"{what} nie moze byc pusty")
    require_letters(key, what)
