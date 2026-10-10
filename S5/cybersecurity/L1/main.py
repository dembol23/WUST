import ciphers
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text

console = Console()

# 1. Wczytanie tekstu z pliku
with open("data/text1.txt", "r", encoding="utf-8") as file:
    text = file.read()

# 2. Oczyszczenie tekstu, ALE zachowanie spacji i nowych linii
# Zamieniamy polskie znaki na ich odpowiedniki, by nie tracić ich z tekstu
replacements = {
    'ą': 'a', 'ć': 'c', 'ę': 'e', 'ł': 'l', 'ń': 'n', 'ó': 'o', 'ś': 's', 'ź': 'z', 'ż': 'z',
    'Ą': 'A', 'Ć': 'C', 'Ę': 'E', 'Ł': 'L', 'Ń': 'N', 'Ó': 'O', 'Ś': 'S', 'Ź': 'Z', 'Ż': 'Z'
}
for old, new in replacements.items():
    text = text.replace(old, new)

# Dozwolone znaki to litery A-Z, spacje i nowe linie
allowed_chars = "ABCDEFGHIJKLMNOPQRSTUVWXYZ \n"
clean_text = "".join(char.upper() for char in text if char.upper() in allowed_chars)

key = "KEY"

# Wykonanie szyfrowań
caesar_text = ciphers.caesar(clean_text, 3, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
vigenere_text = ciphers.vigenere(clean_text, key, "ABCDEFGHIJKLMNOPQRSTUVWXYZ")
rot13_text = ciphers.rot13(clean_text)
playfair_text = ciphers.playfair(clean_text, key, "encrypt")

# 3. Wyświetlanie przy użyciu Rich i ikon z Nerd Font

# Panel z informacjami o kluczach
info_panel = Panel(
    f"[bold cyan]󰌆 Tekst oryginalny (oczyszczony):[/bold cyan]\n[italic]{clean_text.strip()}[/italic]\n\n"
    f"[bold magenta]󰟵 Klucz Vigenère/Playfair:[/bold magenta] {key}\n"
    f"[bold green]󰒓 Przesunięcie Cezara:[/bold green] 3",
    title="[bold yellow]󰢻 Kryptoanaliza - Dane wejściowe[/bold yellow]",
    expand=False
)
console.print(info_panel)
console.print()

# Tabela z wynikami
table = Table(show_header=True, header_style="bold yellow", border_style="dim")
table.add_column("󰢹 Algorytm", style="dim", width=15)
table.add_column("󰈈 Szyfrogram (fragment)", justify="left")

# Aby tabela w terminalu nie "rozjechała się" przez długi tekst, wyświetlamy pierwsze np. 80 znaków
def truncate(text, length=80):
    text_flat = text.replace('\n', ' 󱞣 ') # Zamiana nowych linii na specjalną ikonę w tabeli
    return text_flat if len(text_flat) <= length else text_flat[:length] + "..."

table.add_row("[bold cyan]Cezar[/bold cyan]", truncate(caesar_text))
table.add_row("[bold green]Vigenère[/bold green]", truncate(vigenere_text))
table.add_row("[bold red]ROT13[/bold red]", truncate(rot13_text))
table.add_row("[bold magenta]Playfair[/bold magenta]", truncate(playfair_text))

console.print(table)