"""Szyfr homofoniczny: 100 symboli (00-99) przydzielonych literom wg czestosci."""
from collections import Counter

from ..config import A


def make_homophones(pt, total=100, rng=None):
    """Metoda najwiekszych reszt: min. 1 symbol na litere, suma dokladnie `total`."""
    if rng is None:
        raise ValueError("rng jest wymagany")
    if total < 26 or total > 100:
        raise ValueError("total musi nalezec do przedzialu 26..100")
    if not pt:
        raise ValueError("pusty tekst jawny")
    cnt, n = Counter(pt), len(pt)
    spare = total - 26
    ideal = {c: cnt.get(c, 0) / n * spare for c in A}
    alloc = {c: 1 + int(ideal[c]) for c in A}
    rem = total - sum(alloc.values())
    for c in sorted(A, key=lambda c: ideal[c] - int(ideal[c]), reverse=True)[:rem]:
        alloc[c] += 1
    nums = list(range(total))
    rng.shuffle(nums)
    table, i = {}, 0
    for c in A:
        table[c] = nums[i:i + alloc[c]]
        i += alloc[c]
    return table


def homophonic(pt, table, rng):
    return [f"{rng.choice(table[c]):02d}" for c in pt]


def homophonic_decrypt(symbols, table):
    inv = {f"{n:02d}": c for c, nums in table.items() for n in nums}
    return "".join(inv[s] for s in symbols)
