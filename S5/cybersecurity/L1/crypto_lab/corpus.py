"""Wczytywanie i normalizacja tekstow (alfabet lacinski A-Z)."""
import unicodedata
from pathlib import Path

from .config import A, LANGS
from .samples import SAMPLES

MIN_CORPUS_LEN = 50  # krotszy plik uznajemy za pusty i uzywamy probki wbudowanej


def normalize(text):
    """Sprowadza tekst do liter A-Z (usuwa diakrytyki, spacje i interpunkcje)."""
    text = text.replace("ł", "l").replace("Ł", "L").replace("ß", "ss")
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return "".join(c for c in text.upper() if c in A)


def load_corpora(tdir):
    """Zwraca (korpusy, opisy zrodel) dla wszystkich jezykow z LANGS."""
    corp, src = {}, {}
    for lang in LANGS:
        f = Path(tdir) / f"{lang}.txt"
        text = ""
        if f.is_file():
            text = normalize(f.read_text(encoding="utf-8", errors="ignore"))
        if len(text) >= MIN_CORPUS_LEN:
            corp[lang] = text
            src[lang] = f"plik {f} ({len(text)} znakow)"
        else:
            corp[lang] = normalize(SAMPLES[lang])
            src[lang] = f"PROBKA WBUDOWANA ({len(corp[lang])} znakow) - dodaj {f}"
    return corp, src
