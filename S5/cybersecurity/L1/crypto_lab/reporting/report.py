"""Raport w formacie Markdown + tabele CSV (katalog wyjsciowy jako atrybut, bez zmiennych globalnych)."""
import csv
from pathlib import Path


class Report:
    def __init__(self, out_dir):
        self.out_dir = Path(out_dir)
        self.out_dir.mkdir(parents=True, exist_ok=True)
        self.lines = []

    def h(self, title, lvl=2):
        self.lines += ["", "#" * lvl + " " + title, ""]
        print("\n" + "=" * 70 + f"\n{title}\n" + "=" * 70)

    def p(self, text):
        self.lines += [text, ""]
        print(text)

    def table(self, name, headers, rows):
        rows = [[(f"{c:.4f}" if isinstance(c, float) else str(c)) for c in r] for r in rows]
        with open(self.out_dir / f"{name}.csv", "w", newline="", encoding="utf-8") as f:
            w = csv.writer(f)
            w.writerow(headers)
            w.writerows(rows)

        def esc(s):
            return s.replace("|", "\\|")

        md = ["| " + " | ".join(esc(str(h)) for h in headers) + " |", "|" + "---|" * len(headers)]
        md += ["| " + " | ".join(esc(c) for c in r) + " |" for r in rows]
        self.lines += md + [""]
        print("\n".join(md))

    def fig(self, fname, caption):
        self.lines += [f"![{caption}]({fname})", f"*{caption}*", ""]
        print(f"[wykres] {fname}")

    def save(self):
        (self.out_dir / "raport_wyniki.md").write_text("\n".join(self.lines), encoding="utf-8")
