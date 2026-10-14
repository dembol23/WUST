"""Szyfr Hilla (mod 26) - arytmetyka calkowitoliczbowa, bez bledow zaokraglen."""
import math

import numpy as np

from ..config import A, IDX
from ._validate import require_letters


def int_det(M):
    """Dokladny wyznacznik macierzy (rozwiniecie Laplace'a na liczbach calkowitych)."""
    M = [[int(x) for x in row] for row in M]
    n = len(M)
    if n == 0 or any(len(r) != n for r in M):
        raise ValueError("macierz musi byc kwadratowa i niepusta")
    if n == 1:
        return M[0][0]
    if n == 2:
        return M[0][0] * M[1][1] - M[0][1] * M[1][0]
    return sum(((-1) ** j) * M[0][j] * int_det([r[:j] + r[j + 1:] for r in M[1:]])
               for j in range(n))


def is_invertible(M, m=26):
    return math.gcd(int_det(M) % m, m) == 1


def mat_inv_mod(M, m=26):
    M = [[int(x) for x in row] for row in M]
    n = len(M)
    det = int_det(M) % m
    if math.gcd(det, m) != 1:
        raise ValueError(f"macierz nieodwracalna mod {m} (det={det})")
    inv_det = pow(det, -1, m)
    adj = np.zeros((n, n), dtype=np.int64)
    for i in range(n):
        for j in range(n):
            minor = [r[:j] + r[j + 1:] for k, r in enumerate(M) if k != i]
            adj[j][i] = ((-1) ** (i + j)) * (int_det(minor) if n > 1 else 1)
    return (inv_det * adj) % m


def rand_hill(n, rng):
    while True:
        M = np.array([[rng.randint(0, 25) for _ in range(n)] for _ in range(n)], dtype=np.int64)
        if is_invertible(M):
            return M


def hill(text, M, decrypt=False):
    require_letters(text)
    M = np.array(M, dtype=np.int64) % 26
    if M.ndim != 2 or M.shape[0] != M.shape[1]:
        raise ValueError("macierz Hilla musi byc kwadratowa")
    n = M.shape[0]
    if not is_invertible(M):
        raise ValueError("macierz Hilla jest nieodwracalna mod 26")
    if decrypt:
        if len(text) % n:
            raise ValueError("dlugosc szyfrogramu musi byc wielokrotnoscia rozmiaru macierzy")
        M = mat_inv_mod(M)
        t = text
    else:
        t = text + "X" * (-len(text) % n)
    if not t:
        return ""
    v = np.array([IDX[c] for c in t], dtype=np.int64).reshape(-1, n).T
    r = (M @ v) % 26
    return "".join(A[i] for i in r.T.flatten())


def gl_mod26_order(n):
    """|GL_n(Z_26)| = |GL_n(Z_2)| * |GL_n(Z_13)| (chinskie twierdzenie o resztach)."""
    def gl(p):
        r = 1
        for i in range(n):
            r *= p ** n - p ** i
        return r
    return gl(2) * gl(13)
