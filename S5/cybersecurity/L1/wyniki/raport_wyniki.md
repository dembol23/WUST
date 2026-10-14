# Cyberbezpieczeństwo - Laboratorium nr 2
Wiktor Dembny, 284317

## Zadanie 1.1 i 1.2 - wlasciwosci wybranych algorytmow historycznych

| Algorytm | Klucz | Przestrzen kluczy | Klucze slabe / uwagi | Metody lamania |
|---|---|---|---|---|
| Cezar | przesunięcie $k \in \{0..25\}$ | 26 | $k=0$ (tożsamość); 25 nietrywialnych kluczy | przeszukanie wyczerpujace (brute-force); analiza czestosci |
| ROT13 | brak klucza (stałe $k=13$) | 1 | cały szyfr jest kluczem słabym (inwolucja: $\text{ROT13}(\text{ROT13}(x))=x$) | ponowne zastosowanie ROT13 |
| Vigenere | slowo dlugosci $L$ | $26^{L}$| klucz z jednej powtorzonej litery = Cezar; 'A..A' = tozsamosc; klucz okresowy ('ABAB'=='AB') | metoda Kasiskiego / indeks koincydencji (Friedman) + analiza czestosci kolumn |
| Playfair | kwadrat 5x5 (permutacja 25 liter, I=J) |  $25! \approx 1{,}551\cdot 10^{25} \ (2^{83{,}7})$ | klucze równowazne (cykliczne przesuniecia wierszy/kolumn kwadratu daja ten sam szyfrogram); brak podwojnych liter w digrafach | analiza czestosci digrafow, hill-climbing / symulowane wyzarzanie, atak ze znanym tekstem jawnym |
| Hill | macierz $n\times n$ odwracalna $\pmod{26}$ | $$\prod_{i=0}^{n-1} (2^n - 2^i)(13^n - 13^i)$$ | macierze nieodwracalne ($\gcd(\det, 26) \neq 1$); macierz jednostkowa $M=I$; macierze inwolutywne ($M^2 \equiv I \pmod{26}$) | atak ze znanym tekstem jawnym (algebra liniowa mod 26), analiza digrafow |
| Przestawieniowy | permutacja $L$ kolumn | $L!$ | permutacja tożsamościowa $[0,1,\dots,L-1]$; $L \ge \text{długość tekstu}$ | anagramowanie kolumn, dopasowywanie czestosci bigramow na stykach kolumn |
| Podstawieniowy monoalfabetyczny | permutacja 26 liter | $26! \approx 4{,}033\cdot 10^{26} \ (2^{88{,}4})$ | permutacja tozsamosciowa lub z duza liczba punktow stalych | analiza czestosci pojedynczych liter, bigramow i trigramow |
| ADFGVX | kwadrat $6\times 6$ + permutacja $L$ kolumn | $36! \cdot L!$ | permutacja tozsamosciowa w etapie transpozycji (redukcja do szyfru podstawieniowego) | odwrocenie transpozycji kolumnowej + analiza czestosci par |


## Zadanie 1.3 – Szyfrowanie wielokrotne

| Klasa / Algorytm | Parametry | Wynik złożenia | Obserwacje |
| :--- | :--- | :--- | :--- |
| **Cezar** | `k1=5`, `k2=9` | `Cezar(5) -> Cezar(9) == Cezar(14)` | `IoC = 0.0579` (`IoC` tekstu jawnego `0.0579`); brak wzrostu bezpieczeństwa |
| **ROT13** | `2x ROT13` | `ROT13(ROT13(x)) == x` | parzysta liczba szyfrowań zwraca tekst jawny |
| **Vigenère** | `k1=UDA` (`L=3`), `k2=XIHHE` (`L=5`) | Równoważny pojedynczemu szyfrowi Vigenère’a o kluczu `RLHBHXCKHYAIBKE` (`L = NWW(3,5) = 15`) | Wydłużenie efektywnego klucza z 3 i 5 do 15 znaków mocniej spłaszcza histogram i wymaga od atakującego znacznie dłuższego szyfrogramu |
| **Hill 2x2** | `M1=[[17, 2], [18, 13]]`, `M2=[[22, 17], [13, 7]]` | Równoważny pojedynczemu szyfrowi Hilla z macierzą `M2 * M1 mod 26` | Struktura grupy `GL_n(Z_26)` -> brak wzrostu przestrzeni kluczy |
| **Playfair**| `MONARCHY` + `KRYPTOGRAFIA` | Nie redukuje się do pojedynczego Playfaira; wymaga znajomości obu kluczy | `IoC = 0.0443` (spadek z `0.0483`); brak podwójnych liter (`AA`) w digrafach: TAK |
| **Przestawieniowy** | `perm1=[3, 0, 4, 1, 2]`, `perm2=[5, 2, 0, 6, 1, 3, 4]` | Podwójna transpozycja: histogram i `IoC` bez zmian, ale znacząco silniejsze rozproszenie digrafów | `IoC = 0.0580` (rozkład pojedynczych liter identyczny z tekstem jawnym) |

**Wnioski:**
* **Szyfry tworzące grupę względem składania (Cezar, ROT13, podstawieniowy monoalfabetyczny, Hill tego samego wymiaru):** Wielokrotne szyfrowanie jest równoważne pojedynczemu szyfrowaniu jednym kluczem wypadkowym — przestrzeń kluczy oraz trudność kryptoanalizy nie wzrastają (a w przypadku inwolucji ROT13 dwukrotne szyfrowanie odszyfrowuje tekst).
* **Szyfry polialfabetyczne okresowe (Vigenère):** Złożenie dwóch kluczy o długościach `L1` i `L2` daje szyfr Vigenère’a o okresie równym `NWW(L1, L2)`, co utrudnia łamanie (dłuższy klucz efektywny mocniej spłaszcza rozkład częstości), ale nie zmienia samej klasy algorytmu.
* **Szyfry digraficzne (Playfair) i przestawieniowe:** Dwukrotne szyfrowanie Playfairem nie redukuje się do pojedynczego klucza i dodatkowo obniża indeks koincydencji (`IoC`). W szyfrach przestawieniowych podwójna transpozycja zachowuje częstości pojedynczych liter, lecz silnie niszczy sąsiedztwo znaków.

## Zadanie 1.4 – Który z przetestowanych algorytmów może być uznany za najsilniejszy i dlaczego?

Spośród wszystkich przetestowanych algorytmów historycznych za zdecydowanie najsilniejszy należy uznać hybrydowy (produktowy) szyfr **ADFGVX**.

1. **Największa przestrzeń kluczy:**
   Klucz składa się z dwóch niezależnych elementów: losowej permutacji 36 znaków (`A–Z` oraz `0–9`) w kwadracie podstawieniowym `6x6` oraz permutacji `L` kolumn w etapie transpozycji. Daje to łączną przestrzeń kluczy równą `36! * L!` (dla `L=7` wynosi ona `1.875e+45`, czyli ok. `2^150.4`), co całkowicie uniemożliwia atak metodą przeszukania wyczerpującego (*brute-force*).

2. **Połączenie dwóch klas transformacji (konfuzja i transpozycja)**

## Zadanie 2.1 – Entropia tekstów jawnych w różnych językach

W eksperymencie porównano właściwości statystyczne tekstów jawnych dla sześciu języków europejskich (po znormalizowaniu do 26 wielkich liter alfabetu łacińskiego `A–Z`, bez spacji i znaków interpunkcyjnych). Jako punkt odniesienia przyjęto maksymalną możliwą entropię dla alfabetu 26-znakowego przy rozkładzie jednostajnym, wynoszącą `H_max = log2(26) ≈ 4.7004 bit/znak`, oraz losowy indeks koincydencji `IoC_los = 1/26 ≈ 0.0385` (`IoC * 26 = 1.0`).

| Język | Długość próbki [znaki] | Entropia `H` [bit/znak] | Indeks koincydencji `IoC` | Znormalizowane `IoC * 26` | Nadmiarowość (`log2(26) - H`) [bit/znak] |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Angielski (en)** | 496 | 4.1059 | 0.0705 | 1.8339 | 0.5945 |
| **Polski (pl)** | 566 | 4.2392 | 0.0579 | 1.5046 | 0.4612 |
| **Niemiecki (de)** | 654 | 4.0333 | 0.0789 | 2.0502 | 0.6672 |
| **Francuski (fr)** | 634 | 3.9376 | 0.0848 | 2.2048 | 0.7629 |
| **Włoski (it)** | 587 | 3.9322 | 0.0762 | 1.9805 | 0.7682 |
| **Hiszpański (es)** | 605 | 3.9604 | 0.0782 | 2.0332 | 0.7400 |

![Entropia tekstów jawnych](2_1_entropia_jezyki.png)
*Wykres 2.1: Porównanie entropii tekstów jawnych w różnych językach względem wartości maksymalnej log2(26) = 4.70 bit/znak.*

**Wnioski i obserwacje:**
* **Entropia języków naturalnych a rozkład losowy:** Wszystkie badane języki wykazują entropię niższą od teoretycznego maksimum (`4.7004 bit/znak`), mieszczącą się w przedziale od `3.9322 bit/znak` (włoski) do `4.2392 bit/znak` (polski). Wynika to z faktu, że w językach naturalnych poszczególne litery nie występują z równym prawdopodobieństwem.
* **Specyfika języka polskiego:** Spośród badanych języków polski charakteryzuje się **najwyższą entropią (`4.2392 bit/znak`)** oraz **najniższym indeksem koincydencji (`IoC = 0.0579`)**. Oznacza to najbardziej równomierny (płaski) rozkład częstości liter — najpopularniejsza litera `A` stanowi w polskim tekście `11.0%` wszystkich znaków, a nadmiarowość jest najniższa (`0.4612 bit/znak`).
* **Języki o wysokiej nadmiarowości (francuski, włoski, niemiecki):** Języki romańskie (francuski `H = 3.9376`, włoski `H = 3.9322`, hiszpański `H = 3.9604`) oraz język niemiecki (`H = 4.0333`) posiadają niższą entropię i wyraźnie wyższy indeks koincydencji (`IoC` od `0.0762` do `0.0848`). Jest to spowodowane silną dominacją pojedynczych samogłosek i spółgłosek (szczególnie litery `E`, która we francuskim stanowi aż `19.6%`, a w niemieckim `18.3%` tekstu).
* **Znaczenie dla kryptoanalizy:** Odwrotna zależność między entropią (`H`) a indeksem koincydencji (`IoC`) pokazuje, że im większa jest nadmiarowość języka (i wyższe `IoC`), tym wyraźniejszy „odcisk palca” pozostawia on w szyfrogramie i tym łatwiej złamać szyfr metodą analizy częstości przy krótszej próbce tekstu.


## Zadanie 2.2 – Entropia tekstu jawnego i zaszyfrowanego

Ten sam tekst jawny (język polski, 566 znaków, początek: `KRYPTOGRAFIATOSZTUKAUKRYWANIATRESCIWIADOMOSCI…`) zaszyfrowano wszystkimi algorytmami z zadania.

| Algorytm | Parametry | Entropia `H` [bit/symbol] | Indeks `IoC` | Rozmiar alfabetu | Początek szyfrogramu |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Tekst jawny** | – | 4.2392 | 0.0579 | 23 | `KRYPTOGRAFIATOSZTUKAUKR…` |
| **Cezar** | `k = 3` | 4.2392 | 0.0579 | 23 | `NUBSWRJUDILDWRVCWXNDXNUB…` |
| **ROT13** | `k = 13` | 4.2392 | 0.0579 | 23 | `XELCGBTENSVNGBFMGHXNHXEL…` |
| **Vigenère L=1** | `klucz = K` | 4.2392 | 0.0579 | 23 | `UBIZDYQBKPSKDYCJDEUKEUBI…` |
| **Przestawieniowy L=8** | `perm = [0,4,2,3,7,6,1,5]` | 4.2581 | 0.0575 | 24 | `KATWSMEILDIRLYOACTPOJJCO…` |
| **Playfair** | `klucz = MONARCHY` | 4.4652 | 0.0483 | 25 | `TDHQPRKNOISBPRTXLZIRZEND…` |
| **Vigenère L=3** | `klucz = OSI` | 4.5053 | 0.0470 | 26 | `YJGDLWUJITAIHGANLCYSCYJG…` |
| **Vigenère L=5** | `klucz = ZAYZF` | 4.5859 | 0.0432 | 26 | `JRWOYNGPZKHARNXYTSJFTKPX…` |
| **Vigenère L=8** | `klucz = WNKIEGYK` | 4.5993 | 0.0423 | 26 | `GEIXXUEBWSSIXUQJPHUIYQPI…` |
| **Vigenère L=12** | `klucz = DCMDLLTIZBXO` | 4.6566 | 0.0389 | 26 | `NTKSEZZZZGFOWQECEFDITLOM…` |
| **Hill 2×2** | `M = [[20,11],[5,11]]` | 4.6438 | 0.0400 | 26 | `XDVZOPVJDDEOOPLBCDSYQCGL…` |
| **Hill 3×3** | `M = [[8,4,7],[23,17,17],[8,23,18]]` | 4.6634 | 0.0388 | 26 | `ERTIWDMLXURQWTSAQJMYYERT…` |
| **Hill 4×4** | `M = [[24,5,16,3],[20,9,20,16],[19,6,4,11],[24,5,17,24]]` | 4.6626 | 0.0387 | 26 | `AHHBXOGWXXKFFSMCOGBYQSSR…` |
| **ADFGVX** | `kwadrat = B1HAUJKSGWOLMT8NQI5Z3V4E2RYC07X6F9DP`, `perm = [0,2,6,1,5,4,3]` | 2.5412 | 0.1767 | 6 | `DXVXDVDGAXDVDXXVFXDGXVAX…` |
| **Homofony (symbole 00–99)** | 100 homofonów wg częstości liter | 6.5003 | 0.0099 | 97 | `794308613134507449917672…` |
| **XOR L=8** | `klucz = YNTTZTHY` | 4.7741 | 0.0386 | 32 | `121c0d040e1b0f0b18081d15…` |

**Wnioski i obserwacje (2.2):**
* **Podstawienie monoalfabetyczne nie zmienia statystyki.** Cezar, ROT13 i Vigenère o kluczu jednoliterowym dają dokładnie te same `H = 4.2392` i `IoC = 0.0579` co tekst jawny, bo zmieniają tylko etykiety liter, a nie ich liczebności.
* **Szyfr przestawieniowy zachowuje rozkład liter** (`H = 4.2581`, `IoC = 0.0575`). Minimalna różnica wynika z dopełnienia znakami `X`, bo transpozycja zmienia wyłącznie kolejność znaków.
* **Playfair** podnosi entropię do `4.4652` i obniża `IoC` do `0.0483`, ponieważ szyfruje pary liter i zawsze używa 25 liter (bez `J`).
* **Vigenère:** wraz z długością klucza entropia rośnie (`4.5053` dla L=3; `4.5859` dla L=5; `4.5993` dla L=8; `4.6566` dla L=12), a `IoC` maleje z `0.0470` do `0.0389`, czyli do wartości losowej `1/26 ≈ 0.0385`.
* **Hill:** `H = 4.6438` (2×2), `4.6634` (3×3), `4.6626` (4×4); `IoC` spada z `0.0400` do `0.0387`, więc rozkład jest praktycznie jednostajny już dla macierzy 3×3.
* **ADFGVX:** szyfrogram ma tylko 6 symboli, dlatego `H = 2.5412` jest bliskie maksimum `log2(6) = 2.58`, a `IoC = 0.1767` jest wysokie (rozkład jednostajny na 6 symboli daje `1/6 ≈ 0.167`). Nie świadczy to o słabości, tylko o małym alfabecie.
* **Homofony:** `H = 6.5003` bita na symbol (maksimum dla 100 symboli to `6.64`), a `IoC = 0.0099 ≈ 1/100`, czyli rozkład jest praktycznie płaski.
* **XOR:** `H = 4.7741` przy 32 różnych wartościach bajtu (maksimum `5`).


## Zadanie 2.3 - histogramy tekstow jawnych

![Histogramy liter - rozne jezyki](2_3_histogramy_jezyki.png)
*Histogramy liter - rozne jezyki*

| Jezyk | 6 najczestszych liter |
|---|---|
| angielski | E=15.1%, T=9.9%, A=8.9%, S=8.3%, R=7.9%, I=6.5% |
| polski | A=11.0%, O=8.5%, I=7.8%, E=7.4%, T=6.2%, S=6.0% |
| niemiecki | E=18.3%, N=9.6%, R=8.3%, I=7.5%, T=7.0%, S=7.0% |
| francuski | E=19.6%, S=10.7%, A=8.4%, T=7.9%, L=6.5%, R=6.3% |
| wloski | E=14.1%, I=11.8%, A=9.0%, T=7.8%, O=7.8%, L=7.0% |
| hiszpanski | E=15.4%, A=11.9%, S=10.4%, N=7.3%, O=6.9%, I=6.6% |

**Wnioski i obserwacje:**
* **Unikalny profil każdego języka:** W języku angielskim, niemieckim, francuskim, włoskim i hiszpańskim silnie dominuje litera `E` (od `14.1%` we włoskim do aż `19.6%` we francuskim), natomiast w języku polskim rozkład jest bardziej wyrównany, a najczęściej występującymi literami są samogłoski `A` (`11.0%`), `O` (`8.5%`), `I` (`7.8%`) oraz `E` (`7.4%`).
* **Znaczenie kryptoanalityczne:** Wyraźna asymetria histogramów i obecność liter bardzo rzadkich (np. `Q, V, X`) stanowi charakterystyczny ślad statystyczny języka, który umożliwia bezpośrednie łamanie prostych szyfrów podstawieniowych.


## Zadanie 2.4 – Histogramy tekstu jawnego i szyfrogramów

![Histogramy szyfrogramów](2_4_histogramy_szyfry.png)
*Wykres 2.4: Histogramy tekstu jawnego i szyfrogramów dla wszystkich badanych algorytmów.*

**Wnioski i obserwacje:**
* **Zachowanie vs przesunięcie kształtu:** Szyfr przestawieniowy pozostawia histogram identyczny z tekstem jawnym, natomiast szyfry monoalfabetyczne (Cezar, ROT13, Vigenère `L=1`) zachowują wysokości słupków, przesuwając je jedynie cyklicznie wzdłuż osi alfabetu.
* **Spłaszczenie rozkładu:** Wraz ze wzrostem długości klucza w szyfrze Vigenère’a (`L=3..20`) oraz wymiaru macierzy w szyfrze Hilla (`2×2..4×4`) piki ulegają zatarciu, a histogram staje się coraz bardziej płaski (jednostajny).

## Zadanie 2.5 - n-gramy tekstów jawnych w różnych językach

![Najczestsze bigramy w roznych jezykach](2_5_bigramy_jezyki.png)
*Najczestsze bigramy w roznych jezykach*

| # | angielski | polski | niemiecki | francuski | wloski | hiszpanski |
|---|---|---|---|---|---|---|
| 1 | ER (2.63%) | ST (2.12%) | EN (4.29%) | ES (5.53%) | ER (2.39%) | EN (3.81%) |
| 2 | TH (2.42%) | IE (1.95%) | ER (4.13%) | DE (2.69%) | IS (2.22%) | ES (3.64%) |
| 3 | IN (2.42%) | PO (1.95%) | CH (3.37%) | RE (2.69%) | EL (2.05%) | DE (2.48%) |
| 4 | ET (2.02%) | LI (1.77%) | TE (2.76%) | LE (2.21%) | RA (1.88%) | AS (2.32%) |
| 5 | ES (2.02%) | OW (1.59%) | RE (2.30%) | SE (2.05%) | LE (1.88%) | LA (1.99%) |
| 6 | TE (2.02%) | YS (1.59%) | EI (1.99%) | ET (2.05%) | TE (1.71%) | RA (1.82%) |
| 7 | RE (1.82%) | TE (1.59%) | ND (1.99%) | LA (1.90%) | RE (1.71%) | SE (1.66%) |
| 8 | NT (1.82%) | ZY (1.59%) | DE (1.99%) | QU (1.90%) | ES (1.71%) | EL (1.66%) |
| 9 | HE (1.62%) | TO (1.42%) | IE (1.68%) | NT (1.74%) | TI (1.71%) | AR (1.66%) |
| 10 | SA (1.62%) | IA (1.42%) | SC (1.68%) | TE (1.74%) | IN (1.54%) | OS (1.66%) |

![Najczestsze trigramy w roznych jezykach](2_5_trigramy_jezyki.png)
*Najczestsze trigramy w roznych jezykach*

| # | angielski | polski | niemiecki | francuski | wloski | hiszpanski |
|---|---|---|---|---|---|---|
| 1 | THE (1.62%) | SCI (1.06%) | SCH (1.53%) | DES (1.42%) | ELL (1.03%) | DES (1.16%) |
| 2 | TER (1.21%) | UJA (0.71%) | NDE (1.07%) | QUE (1.42%) | ERE (0.85%) | ENT (1.00%) |
| 3 | ERS (1.01%) | ALI (0.71%) | ERS (0.92%) | EDE (1.11%) | TTE (0.85%) | ENE (1.00%) |
| 4 | INT (1.01%) | TER (0.71%) | EIN (0.92%) | ESE (0.95%) | TER (0.85%) | SDE (1.00%) |
| 5 | NTH (1.01%) | SZY (0.71%) | DEN (0.92%) | ESS (0.79%) | CHE (0.68%) | ENC (0.83%) |
| 6 | ING (0.81%) | YST (0.71%) | ABE (0.92%) | NTE (0.79%) | STI (0.68%) | ELA (0.66%) |
| 7 | LET (0.81%) | IAT (0.53%) | CHE (0.92%) | TRE (0.79%) | CON (0.68%) | ESC (0.66%) |
| 8 | ETT (0.81%) | WAN (0.53%) | ERE (0.77%) | EST (0.63%) | LET (0.68%) | QUE (0.66%) |
| 9 | TTE (0.81%) | NIA (0.53%) | EIT (0.77%) | DEC (0.63%) | ETT (0.68%) | CUE (0.66%) |
| 10 | EVE (0.81%) | WIA (0.53%) | TER (0.77%) | IRE (0.63%) | NEL (0.68%) | UEN (0.66%) |

**Wnioski i obserwacje:**
* **Charakterystyczne zbitki językowe:** Każdy język posiada specyficzne, wysoko powtarzalne kombinacje liter wynikające z typowych rodzajników, przyimków i końcówek fleksyjnych — np. angielskie `ER, TH, IN` oraz `THE` (`1.62%`), niemieckie `EN, ER, CH` oraz `SCH` (`1.53%`), francuskie `ES, DE` oraz `DES, QUE` (`1.42%`), czy polskie `ST, IE, PO` oraz `SCI` (`1.06%`).
* **Zastosowanie:** Nawet w przypadku zaszyfrowania wiadomości szyfrem podstawieniowym lub przestawieniowym analiza najczęstszych par i trójek znaków pozwala zidentyfikować język oryginału oraz odtworzyć sąsiedztwo kolumn lub tablicę podstawień.


## Zadanie 2.6 - n-gramy tekstu jawnego i szyfrogramow

| Algorytm | Rozne bigramy | H(bigram) [bit] | Top-3 bigramy | Rozne trigramy | H(trigram) [bit] | Top-3 trigramy |
|---|---|---|---|---|---|---|
| TEKST JAWNY | 208 | 7.279 | ST:2.12%, IE:1.95%, PO:1.95% | 444 | 8.656 | SCI:1.06%, UJA:0.71%, ALI:0.71% |
| Cezar | 208 | 7.279 | VW:2.12%, LH:1.95%, SR:1.95% | 444 | 8.656 | VFL:1.06%, XMD:0.71%, DOL:0.71% |
| ROT13 | 208 | 7.279 | FG:2.12%, VR:1.95%, CB:1.95% | 444 | 8.656 | FPV:1.06%, HWN:0.71%, NYV:0.71% |
| Playfair | 295 | 7.916 | KF:1.59%, TL:1.59%, SB:1.23% | 526 | 8.997 | KFS:0.71%, XSB:0.53%, NVR:0.53% |
| Vigenere L=1 | 208 | 7.279 | CD:2.12%, SO:1.95%, ZY:1.95% | 444 | 8.656 | CMS:1.06%, ETK:0.71%, KVS:0.71% |
| Vigenere L=3 | 274 | 7.821 | IB:1.24%, HW:1.24%, QS:1.24% | 503 | 8.913 | GUQ:0.71%, SVW:0.53%, AHQ:0.53% |
| Vigenere L=5 | 329 | 8.140 | NW:1.06%, RD:1.06%, YN:0.88% | 533 | 9.027 | QBN:0.53%, NWY:0.53%, HAR:0.35% |
| Vigenere L=8 | 348 | 8.241 | GO:1.42%, OG:1.42%, IX:0.88% | 535 | 9.035 | GQO:0.53%, IXX:0.35%, XXU:0.35% |
| Vigenere L=12 | 358 | 8.305 | UH:0.88%, PK:0.88%, ZZ:0.71% | 535 | 9.037 | ZZZ:0.35%, RDF:0.35%, LKH:0.35% |
| Vigenere L=20 | 350 | 8.234 | GR:1.06%, JF:1.06%, TN:1.06% | 546 | 9.076 | UKR:0.35%, RKX:0.35%, GRD:0.35% |
| Hill 2x2 | 335 | 8.095 | MV:1.77%, XN:1.42%, CG:1.06% | 529 | 9.007 | NXN:0.53%, WNI:0.53%, NIJ:0.53% |
| Hill 3x3 | 356 | 8.288 | AM:0.88%, OP:0.88%, QS:0.71% | 537 | 9.038 | AMW:0.71%, OPD:0.53%, ERT:0.35% |
| Hill 4x4 | 371 | 8.375 | GW:0.71%, SM:0.71%, GB:0.71% | 550 | 9.088 | BNN:0.35%, WYG:0.35%, PYC:0.35% |
| Permutacyjny L=8 | 287 | 7.929 | EI:1.23%, OA:1.23%, AS:1.06% | 544 | 9.067 | IRL:0.35%, OUA:0.35%, ANO:0.35% |
| ADFGVX | 36 | 5.048 | GD:5.47%, DD:5.38%, DG:4.77% | 209 | 7.449 | DGD:1.50%, FDD:1.33%, DDD:1.33% |
| Homofony (symbole) | 525 | 8.998 | 54-97:0.53%, 15-17:0.53%, 59-32:0.35% | 563 | 9.136 | 12-37-74:0.35%, 79-43-08:0.18%, 43-08-61:0.18% |
| Homofony (cyfry) | 100 | 6.566 | 86:1.77%, 54:1.68%, 20:1.68% | 637 | 9.132 | 864:0.44%, 486:0.44%, 081:0.44% |
| XOR L=8 | 346 | 8.236 | 1b-1f:0.88%, 0e-11:0.88%, 1b-03:0.71% | 532 | 9.025 | 10-00-1d:0.53%, 1b-00-1a:0.35%, 0a-0d-1d:0.35% |

![Najczestsze bigramy szyfrogramow](2_6_bigramy_szyfry.png)
*Najczestsze bigramy szyfrogramow*

![Najczestsze trigramy szyfrogramow](2_6_trigramy_szyfry.png)
*Najczestsze trigramy szyfrogramow*

**Wnioski i obserwacje:**
* **Szyfry monoalfabetyczne (Cezar, ROT13, Vigenère L=1):** Zachowują dokładnie tę samą liczbę unikalnych bigramów (`208`) i trigramów (`444`) oraz ich entropię (`7.279 bit` i `8.656 bit`) co tekst jawny — zmieniają się wyłącznie etykiety liter tworzących zbitki (np. polskie `ST: 2.12%` przechodzi w `VW: 2.12%` dla Cezara).
* **Szyfry przestawieniowe, polialfabetyczne i macierzowe:** Szyfr permutacyjny, mimo nienaruszenia histogramu pojedynczych liter, rozrywa ich sąsiedztwo i zwiększa liczbę różnych bigramów do `287` (`H = 7.929 bit`). Szyfry Vigenère’a (dla większych `L`), Hilla oraz homofoniczny jeszcze silniej rozpraszają zbitki znakowe, podnosząc entropię n-gramów powyżej `8.2–9.0 bit` i redukując udział najczęstszych układów poniżej `1%`.


## Zadanie 2.7 – Autokorelacja: XOR i Vigenère dla różnych długości haseł

W eksperymencie zbadano funkcję autokorelacji (zliczającą ułamek pokrywających się symboli pomiędzy szyfrogramem a jego kopią przesuniętą o `d = 1..60` pozycji) dla dwóch szyfrów okresowych: klasycznego szyfru **Vigenère’a** oraz szyfru strumieniowego **XOR** z powtarzanym kluczem o długościach `L ∈ {3, 5, 8, 12}`.

![Autokorelacja szyfrogramów Vigenère i XOR](2_7_autokorelacja.png)
*Wykres 2.7: Autokorelacja tekstu jawnego oraz szyfrogramów Vigenère’a i XOR dla różnych długości kluczy.*

**Wnioski i obserwacje:**
* **Wykrywanie okresowości i długości klucza:** W przeciwieństwie do płaskiego wykresu dla tekstu jawnego, szyfrogramy uzyskane algorytmami Vigenère’a oraz XOR wykazują wyraźne, cykliczne szpilki (maksima lokalne) w punktach przesunięć będących wielokrotnościami długości klucza (`d = L, 2L, 3L...`).
* **Wpływ długości hasła:** Odczytanie odstępu pomiędzy kolejnymi regularnymi pikami na wykresie autokorelacji pozwala bezpośrednio wyznaczyć długość hasła `L` (zarówno dla `L = 3, 5, 8`, jak i `12`), przy czym wraz z wydłużaniem klucza piki pojawiają się rzadziej i są nieco mniej wyraźne na tle szumu losowego.

---

## Zadanie 2.8 – Jak zmieniają się obserwowane parametry w zadaniach 2.1 – 2.7?

Wpływ poszczególnych klas algorytmów kryptograficznych na badane parametry statystyczne tekstu kształtuje się następująco:

1. **Entropia pojedynczych znaków (`H`) oraz Indeks Koincydencji (`IoC`):**
   * *Teksty jawne w językach naturalnych:* Charakteryzują się entropią niższą od maksymalnej możliwej dla danego alfabetu (występuje nadmiarowość języka) oraz podwyższonym indeksem koincydencji wynikającym z nierównomiernej częstości występowania liter.
   * *Szyfry podstawieniowe monoalfabetyczne (Cezar, ROT13, Vigenère dla klucza jednoznakowego):* **Nie zmieniają** wartości entropii ani indeksu koincydencji, ponieważ dokonują jedynie wzajemnie jednoznacznej podmiany etykiet poszczególnych znaków przy zachowaniu ich liczebności.
   * *Szyfry przestawieniowe (permutacyjne):* Również **zachowują** entropię pojedynczych znaków oraz indeks koincydencji tekstu jawnego, gdyż zmieniają wyłącznie pozycje liter w wiadomości, nie ingerując w ich zbiór.
   * *Szyfry polialfabetyczne (Vigenère) oraz poligraficzne/macierzowe (Playfair, Hill):* Powodują **wzrost entropii** (dąży ona do wartości maksymalnej dla alfabetu o danym rozmiarze) oraz **spadek indeksu koincydencji** (dąży on do wartości charakterystycznej dla ciągu losowego). Efekt ten jest tym silniejszy, im dłuższe jest hasło w szyfrze Vigenère’a lub im większy jest wymiar macierzy w szyfrze Hilla.
   * *Szyfry zmieniające rozmiar alfabetu (ADFGVX, homofoniczny, XOR):* Wartość entropii oraz indeksu koincydencji dostosowuje się do mocy nowego zbioru symboli wyjściowych (w szyfrze homofonicznym rozkład symboli ulega maksymalnemu wyrównaniu, przez co entropia rośnie, a `IoC` spada do minimum).

2. **Histogramy częstości znaków:**
   * Każdy język naturalny posiada charakterystyczny, asymetryczny kształt histogramu z wyraźną dominacją kilku najpopularniejszych liter (przede wszystkim samogłosek).
   * Szyfry przestawieniowe pozostawiają histogram **identyczny** z histogramem tekstu jawnego.
   * Szyfry monoalfabetyczne zachowują wysokości poszczególnych słupków histogramu, powodując jedynie ich **cykliczne przesunięcie** (Cezar, ROT13) lub **permutację** na osi znaków.
   * Szyfry polialfabetyczne, macierzowe oraz homofoniczne powodują **spłaszczenie histogramu** (wyrównanie częstości występowania znaków), upodabniając go do rozkładu jednostajnego.

3. **Rozkład i entropia n-gramów:**
   * Szyfry podstawieniowe monoalfabetyczne zachowują pierwotną strukturę n-gramów — liczba unikalnych par i trójek znaków, ich procentowe udziały oraz entropia pozostają bez zmian (zmieniają się wyłącznie litery tworzące poszczególne zbitki).
   * Szyfry przestawieniowe, mimo zachowania statystyk pojedynczych liter, rozrywają naturalne sąsiedztwo znaków, co skutkuje wyraźnym wzrostem liczby unikalnych bigramów i trigramów oraz podniesieniem ich entropii.
   * Szyfry polialfabetyczne, poligraficzne (Hill, Playfair) oraz produktowe (ADFGVX) silnie rozpraszają zbitki literowe, zwiększając różnorodność n-gramów i redukując częstość występowania najpopularniejszych układów.

4. **Funkcja autokorelacji (Zad. 2.7):**
   * Dla tekstu jawnego oraz szyfrów nieokresowych (np. Hilla, przestawieniowego) wykres autokorelacji pozostaje relatywnie płaski.
   * Dla szyfrów wykorzystujących cyklicznie powtarzane hasło (Vigenère, XOR) na wykresie autokorelacji pojawiają się regularne, wyraźne maksima lokalne (szpilki) dla przesunięć będących wielokrotnościami długości klucza (`L, 2L, 3L...`).

---

## Zadanie 2.9 – W jaki sposób można wykorzystać narzędzia analizy tekstu do określenia algorytmu szyfrowania?

Identyfikację nieznanego algorytmu szyfrowania na podstawie samego szyfrogramu przeprowadza się wieloetapowo, eliminując kolejne klasy szyfrów za pomocą narzędzi statystycznych:

1. **Analiza rozmiaru i charakteru alfabetu szyfrogramu:**
   * **Szyfr ADFGVX:** Szyfrogram składa się wyłącznie z 6 specyficznych liter (`A, D, F, G, V, X`) i ma parzystą długość.
   * **Szyfr homofoniczny:** Rozbudowany alfabet wyjściowy (np. liczby dwucyfrowe lub zestaw symboli znacznie przekraczający rozmiar alfabetu języka jawnego) przy niemal idealnie płaskim histogramie i bardzo wysokiej entropii symboli.
   * **Szyfr Playfair:** Alfabet ograniczony do maksymalnie 25 liter (zwykle brak litery `J`), parzysta długość szyfrogramu oraz całkowity brak podwójnych, identycznych liter w obrębie poszczególnych par (digrafów).
   * **Szyfr XOR:** Szyfrogram przyjmuje postać strumienia bajtów (np. w zapisie szesnastkowym lub binarnym) wykraczającego poza standardowy zakres znaków drukowalnych.

2. **Analiza entropii (`H`) oraz Indeksu Koincydencji (`IoC`) (dla klasycznego alfabetu 26-literowego):**
   * **Gdy entropia i `IoC` są zbliżone do wartości typowych dla języka naturalnego:** Wskazuje to na szyfr zachowujący częstości pojedynczych liter (przestawieniowy lub podstawieniowy monoalfabetyczny). Rozróżnia się je za pomocą **histogramu** oraz **analizy n-gramów**:
     * Jeżeli histogram pokrywa się bezpośrednio z rozkładem liter danego języka (te same litery są najczęstsze), ale rozkład bigramów uległ zniszczeniu $\rightarrow$ **szyfr przestawieniowy (permutacyjny)**.
     * Jeżeli słupki histogramu mają wysokości typowe dla języka naturalnego, lecz są cyklicznie przesunięte lub przetasowane, a rozkład częstości n-gramów jest zachowany $\rightarrow$ **szyfr Cezara / ROT13 / podstawieniowy monoalfabetyczny**.
   * **Gdy entropia jest bliska wartości maksymalnej, histogram jest płaski, a `IoC` spadło w okolice wartości losowej:** Wskazuje to na szyfr polialfabetyczny lub poligraficzny (macierzowy). Rozróżnia się je za pomocą **autokorelacji**:
     * Jeżeli wykres autokorelacji wykazuje regularne, okresowe piki co stałą liczbę znaków $\rightarrow$ **szyfr polialfabetyczny (np. Vigenère)**.
     * Jeżeli wykres autokorelacji jest płaski i nie wykazuje okresowości $\rightarrow$ **szyfr macierzowy Hilla** (lub Vigenère z kluczem o długości porównywalnej z całym tekstem).

---

## Zadanie 2.10 – W jaki sposób można wykorzystać narzędzia analizy tekstu do ustalenia hasła używanego do szyfrowania?

Sposób odzyskiwania klucza zależy od rozpoznanej wcześniej klasy algorytmu szyfrowania:

1. **Szyfr Cezara i podstawieniowe szyfry monoalfabetyczne:**
   * Wykorzystuje się **histogram częstości znaków** oraz **analizę n-gramów**.
   * W szyfrze Cezara porównuje się histogram szyfrogramu ze wzorcowym histogramem języka jawnego — wielkość przesunięcia cyklicznego, która nakłada najczęstsze litery szyfrogramu na najczęstsze litery języka, bezpośrednio wyznacza klucz przesunięcia.
   * W ogólnym szyfrze monoalfabetycznym poszczególne litery klucza odtwarza się poprzez dopasowywanie najczęstszych pojedynczych znaków, a następnie weryfikację utworzonych przez nie najpopularniejszych bigramów i trigramów charakterystycznych dla danego języka.

2. **Szyfry polialfabetyczne okresowe (Vigenère, XOR):**
   Proces ustalania hasła przebiega dwuetapowo:
   * **Etap I – Wyznaczenie długości hasła (`L`):** Długość klucza można określić na podstawie np. wykresu autokorelacji: Odczytując odległość pomiędzy kolejnymi regularnymi pikami (lub wyznaczając największy wspólny dzielnik odstępów między najsilniejszymi szpilkami).
   * **Etap II – Wyznaczenie kolejnych znaków hasła:** Po poznaniu długości klucza `L`, szyfrogram dzieli się na `L` niezależnych podciągów (kolumn), grupując razem co `L`-ty znak wiadomości. Ponieważ wszystkie znaki w obrębie jednej kolumny zostały zaszyfrowane tym samym znakiem hasła, każdą z `L` kolumn poddaje się niezależnej analizie częstości (dokładnie tak jak pojedynczy szyfr Cezara). Złożenie odzyskanych przesunięć z wszystkich `L` kolumn daje pełne hasło szyfrujące.

3. **Szyfry przestawieniowe (kolumnowe):**
   * Wykorzystuje się **analizę bigramów i trigramów**. Szyfrogram dzieli się na segmenty odpowiadające przypuszczalnej liczbie kolumn `L`, a następnie zestawia kolumny w takiej kolejności, aby pary i trójki liter powstające na stykach sąsiednich kolumn w wierszach tworzyły poprawne i często występujące n-gramy danego języka.