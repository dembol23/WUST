# crypto_lab - Laboratorium nr 2: kryptoanaliza klasycznych szyfrow

Zamiennik CrypTool 1.4 dla zadan 1 i 2 (Python 3.9+, numpy, matplotlib).

## Uruchomienie
    pip install -r requirements.txt
    python main.py                                   # teksty z ./texts, wyniki do ./wyniki
    python -m crypto_lab --plain-lang en --length 8000 --seed 7
    python -m unittest discover -v                   # testy (21)

Teksty: `texts/en.txt, pl.txt, de.txt, fr.txt, it.txt, es.txt` (zalecane >= 20 000 znakow;
brakujace pliki zastepuja krotkie probki wbudowane - tylko do testu dzialania).
Wynik: `wyniki/` z wykresami PNG, tabelami CSV i `raport_wyniki.md`.

## Struktura
    crypto_lab/
      config.py, corpus.py, samples.py   alfabet/jezyki, wczytywanie i normalizacja tekstow
      ciphers/                           Cezar/ROT13/Vigenere/XOR, Playfair, Hill, przestawieniowy,
                                         ADFGVX, homofoniczny, build_ciphers (zestaw do zad. 2)
      analysis/                          entropia, IoC, n-gramy, autokorelacja; chi2, lamanie, Friedman
      reporting/                         Report (MD + CSV) i wykresy
      tasks/                             selftest, task1, task2, breaking (2.9/2.10)
      cli.py                             argumenty wiersza polecen
    tests/test_crypto_lab.py

## Poprawki wzgledem pierwotnego main.py
1. `build_ciphers` wywolywany raz - tabele 2.2, 2.4, 2.6 i 2.9 (dawniej 6 i 13) opisuja te same szyfrogramy.
2. Wzor Friedmana: `kp` = IoC jezyka tekstu jawnego (dawniej stala angielska 0,0667).
3. Tabele n-gramow: zliczanie raz na jezyk + bezpieczne indeksowanie (brak IndexError).
4. `est_key_len` zawsze zwraca krotke.
5. Brak zmiennej globalnej `OUT` - katalog wyjsciowy w obiekcie `Report`.
6. Hill: dokladny wyznacznik calkowitoliczbowy (bez `np.linalg.det`), walidacja odwracalnosci.
7. Walidacja wejsc (A-Z, permutacje, klucze), autokorelacja i `est_period` odporne na krotkie teksty,
   dynamiczna oś Y wykresu entropii, selftest bez `assert` (dziala z `python -O`), test Playfaira
   z powtorzonymi literami (`playfair_unpad`).
