"""Szyfry podstawieniowe: Cezar, ROT13, Vigenere oraz XOR z powtarzanym haslem."""
from ..config import A, IDX
from ._validate import require_key, require_letters


def caesar(text, k, decrypt=False):
    require_letters(text)
    k = -k if decrypt else k
    return "".join(A[(IDX[c] + k) % 26] for c in text)


def rot13(text):
    return caesar(text, 13)


def vigenere(text, key, decrypt=False):
    require_letters(text)
    require_key(key)
    s = -1 if decrypt else 1
    n = len(key)
    return "".join(A[(IDX[c] + s * IDX[key[i % n]]) % 26] for i, c in enumerate(text))


def xor_cipher(text, key):
    """XOR bajtow tekstu z powtarzanym haslem; wynik jako lista tokenow hex."""
    if not key:
        raise ValueError("haslo nie moze byc puste")
    if not (text.isascii() and key.isascii()):
        raise ValueError("XOR: dozwolone tylko znaki ASCII")
    n = len(key)
    return [f"{ord(c) ^ ord(key[i % n]):02x}" for i, c in enumerate(text)]


def xor_decrypt(tokens, key):
    if not key:
        raise ValueError("haslo nie moze byc puste")
    n = len(key)
    return "".join(chr(int(t, 16) ^ ord(key[i % n])) for i, t in enumerate(tokens))


def rand_key(length, rng):
    if length < 1:
        raise ValueError("dlugosc klucza musi byc >= 1")
    return "".join(rng.choice(A) for _ in range(length))
