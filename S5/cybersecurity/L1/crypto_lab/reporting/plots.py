"""Wykresy (matplotlib, backend Agg - dziala bez serwera graficznego)."""
import math
from collections import Counter
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402

from ..analysis.statistics import glabel, ngram_counter  # noqa: E402
from ..config import A  # noqa: E402


def _save(fig, out_dir, fname):
    fig.tight_layout()
    fig.savefig(Path(out_dir) / fname, dpi=130)
    plt.close(fig)


def entropy_bar(out_dir, labels, values, max_h, fname):
    fig = plt.figure(figsize=(6, 3.5))
    plt.bar(labels, values)
    plt.axhline(max_h, color="r", ls="--", label=f"max = log2(26) = {max_h:.2f}")
    lo = min(values) if values else max_h
    plt.ylim(max(0.0, math.floor((lo - 0.1) * 10) / 10), max_h + 0.1)
    plt.ylabel("entropia [bit/znak]")
    plt.legend()
    _save(fig, out_dir, fname)


def hist_grid(out_dir, items, fname, title, cols=3):
    rows = math.ceil(len(items) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 2.8 * rows), squeeze=False)
    for ax, (name, sym) in zip(axes.flat, items):
        letters = all(isinstance(s, str) and len(s) == 1 and s in A for s in sym)
        alphabet = list(A) if letters else sorted(set(sym), key=str)
        c, n = Counter(sym), max(len(sym), 1)
        ax.bar(range(len(alphabet)), [c[a] / n * 100 for a in alphabet])
        if len(alphabet) <= 36:
            ax.set_xticks(range(len(alphabet)))
            ax.set_xticklabels([str(a) for a in alphabet], fontsize=6)
        else:
            ax.set_xticks([])
        ax.set_title(name, fontsize=9)
        ax.set_ylabel("% wystapien", fontsize=8)
    for ax in list(axes.flat)[len(items):]:
        ax.axis("off")
    fig.suptitle(title)
    _save(fig, out_dir, fname)


def ngram_grid(out_dir, items, n, fname, title, top=12, cols=3):
    rows = math.ceil(len(items) / cols)
    fig, axes = plt.subplots(rows, cols, figsize=(5 * cols, 3 * rows), squeeze=False)
    for ax, (name, sym) in zip(axes.flat, items):
        c = ngram_counter(sym, n)
        tot = sum(c.values())
        mc = c.most_common(top)
        ax.barh([glabel(g) for g, _ in mc][::-1], [v / tot * 100 for _, v in mc][::-1])
        ax.tick_params(labelsize=7)
        ax.set_title(name, fontsize=9)
        ax.set_xlabel("% wszystkich n-gramow", fontsize=8)
    for ax in list(axes.flat)[len(items):]:
        ax.axis("off")
    fig.suptitle(title)
    _save(fig, out_dir, fname)


def autocorr_grid(out_dir, plain_ac, lens, series, fname):
    """series: slownik {(nazwa, dlugosc_klucza): autokorelacja}; kolumny: Vigenere, XOR."""
    names = ("Vigenere", "XOR")
    fig, axes = plt.subplots(len(lens) + 1, 2, figsize=(11, 2.4 * (len(lens) + 1)), squeeze=False)
    for j in range(2):
        axes[0][j].plot(range(1, len(plain_ac) + 1), plain_ac, marker=".")
        axes[0][j].set_title("Tekst jawny", fontsize=9)
    for i, L in enumerate(lens, 1):
        for j, nm in enumerate(names):
            ac = series[(nm, L)]
            axes[i][j].plot(range(1, len(ac) + 1), ac, marker=".")
            axes[i][j].set_title(f"{nm}, |klucz|={L}", fontsize=9)
    for ax in axes.flat:
        ax.set_ylabel("czesc zgodnych", fontsize=7)
    axes[-1][0].set_xlabel("przesuniecie")
    axes[-1][1].set_xlabel("przesuniecie")
    _save(fig, out_dir, fname)
