"""
Deployment script
Creates gap structure under gap/pl/default.
The definition text is a raw text representation of a wiki page
with accountants-approved gap structure
"""

gap_text = \
"""* [0] Aktywa trwałe
   * [01] Środki trwałe
     * [011] Grunty (w tym prawo wieczystego użytkowania gruntu)
     * [012] Budynki, lokale i obiekty inżynierii lądowej i wodnej
     * [013] Urządzenia techniczne i maszyny
     * [014] Środki transportu
       * [0141] Samochody osobowe
       * [0142] Samochody ciężarowe
     * [015] Inne środki trwałe (w tym inwentarz żywy zaliczany do środków trwałych)
   * [02] Wartości niematerialne i prawne
     * [021] Koszty zakończonych prac rozwojowych
     * [022] Wartość firmy
     * [023] Inne wartości niematerialne i prawne
   * [03] Długoterminowe aktywa finansowe
     * [031] Udziały lub akcje
     * [032] Inne papiery wartościowe
     * [033] Udzielone pożyczki
     * [034] Inne długoterminowe aktywa finansowe
     * [035] Odpisy aktualizujące długoterminowe aktywa finansowe
   * [04] Inwestycje w nieruchomości i prawa
     * [041] Nieruchomości
     * [042] Wartości niematerialne i prawne
   * [07] Odpisy umorzeniowe środków trwałych, wartości niematerialnych i prawnych oraz inwestycji w nieruchomości i prawa
     * [071] Odpisy umorzeniowe środków trwałych (do kont 011000 do 015000)
     * [072] Odpisy umorzeniowe wartości niematerialnych i prawnych  (do kont 021000 do 023000)
     * [073] Odpisy umorzeniowe inwestycji w nieruchomości i prawa (do kont 041000 do 042000)
   * [08] Środki trwałe w budowie
   * [09] Ewidencja pozabilansowa
     * [091] Obce środki trwałe
     * [092] Środki trwałe w likwidacji
 * [1] Środki pieniężne, rachunki bankowe oraz inne krótkoterminowe aktywa finansowe
   * [10] Kasa
   * [13] Rachunki i kredyty bankowe
     * [131] Rachunek bieżący
     * [132] Rachunek walutowy
     * [133] Kredyty bankowe
     * [134] Inne rachunki bankowe
       * [1341] Rachunek bankowy wyodrębnionych środków pieniężnych ZFŚS
       * [1342] Rachunek bankowy lokat terminowych (według poszczególnych lokat)
       * [1343] Rachunek bankowy akredytywy (według poszczególnych kontrahentów}
     * [135] Środki pieniężne w drodze
   * [14] Krótkoterminowe aktywa finansowe
     * [141] Udziały lub akcje
     * [142] Inne papiery wartościowe
     * [143] Udzielone pożyczki
     * [144] Inne krótkoterminowe aktywa finansowe
     * [145] Odpisy aktualizujące krótkoterminowe aktywa finansowe
 * [2] Rozrachunki i roszczenia
   * [20] Rozrachunki z kontrahentami
     * [201] Rozrachunki z odbiorcami
     * [202] Rozrachunki z dostawcami
   * [22] Rozrachunki publicznoprawne
     * [221] Rozrachunki z urzędem skarbowym z tytułu VAT
     * [222] Rozrachunki z urzędem skarbowym z tytułu VAT należnego
       * [2221] rozliczenie należnego VAT
       * [2222] korekty należnego VAT
     * [223] Rozrachunki z urzędem skarbowym z tytułu VAT naliczonego
       * [2231] rozliczenie naliczonego VAT
       * [2232] korekty naliczonego VAT
     * [224] Pozostałe rozrachunki publicznoprawne
       * [2241] Rozrachunki publicznoprawne z urzędem skarbowym
         * [22411] podatek dochodowy
         * [22412] podatek od czynności cywilnoprawnych
       * [2242] Rozrachunki publicznoprawne z urzędem miasta/gminy
         * [22421] Podatek od nieruchomości
         * [22422] podatek od środków transportowych
       * [2243] Rozrachunki publicznoprawne z urzędem celnym
       * [2244] Rozrachunki publicznoprawne z ZUS
       * [2245]  Rozrachunki publicznoprawne z PFRON
   * [23] Rozrachunki z tytułu wynagrodzeń i innych świadczeń na rzecz pracowników
     * [231] Rozrachunki z tytułu wynagrodzeń
       * [2311] umowa o pracę
       * [2312] umowy cywilnoprawne
     * [232] Rozrachunki z pracownikami
       * [2321] zaliczki
   * [24] Rozrachunki z akcjonariuszami i udziałowcami
     * [241] Rozrachunki z akcjonariuszami
     * [242] Rozrachunki z udziałowcami
   * [25] Pozostałe rozrachunki
     * [251] Inne rozrachunki z kontrahentami
   * [26] Pożyczki
     * [261] Pożyczki otrzymane
     * [262]  Pożyczki udzielone
   * [27] Rozliczenie niedoborów i nadwyżek
     * [271] Rozliczenie niedoborów
     * [272] Rozliczenie nadwyżek
   * [28] Należności dochodzone na drodze sądowej
   * [29] Rozrachunki pozabilansowe
     * [291] Należności warunkowe
     * [292] Zobowiązania warunkowe
     * [293] Weksle obce dyskontowane lub indosowane
 * [3] Materiały i towary
   * [30] Rozliczenie zakupu
     * [301] Rozliczenie zakupu materiałów
     * [302] Rozliczenie zakupu towarów
     * [303] Rozliczenie zakupu usług obcych
     * [304] Rozliczenie zakupu składników aktywów trwałych
   * [31] Materiały i opakowania
     * [311] Materiały
     * [312] Opakowania
     * [313] Materiały w przerobie
   * [33] Towary
     * [331] Towary w hurcie
     * [332] Towary w detalu
     * [333] Towary w zakładach gastronomicznych
     * [334] Towary skupu
     * [335] Towary poza jednostką
     * [336] Nieruchomości i prawa majątkowe przeznaczone do obrotu
   * [34] Odchylenia od cen ewidencyjnych materiałów i towarów
     * [341] Odchylenia od cen ewidencyjnych materiałów
     * [342] Odchylenia od cen ewidencyjnych towarów
       * [3421] Odchylenia od cen ewidencyjnych towarów w hurcie
       * [3422] Odchylenia od cen ewidencyjnych towarów w detalu
       * [3423] Odchylenia od cen ewidencyjnych towarów w zakładach gastronomicznych
       * [3424] Odchylenia od cen ewidencyjnych towarów skupu
     * [346] Odchylenia od cen ewidencyjnych opakowań
     * [347] Odchylenia z tytułu aktualizacji wartości zapasów materiałów i towarów
   * [39] Zapasy obce
 * [4] Koszty według rodzajów i ich rozliczenie
   * [40] Koszty według rodzajów
     * [401] Amortyzacja
       * [4011] amortyzacja urządzeń technicznych
       * [4012] amortyzacja środków transportu
     * [402] Zużycie materiałów i energii
       * [4021] Zużycie surowców do wytwarzania produktów
       * [4022] Zużycie energii
       * [4023] Zużycie paliwa dla środków transportu
         * [40231] Zużycie Oleju napędowego
         * [40232] Zużycie  Etyliny 95
       * [4024] Zużycie innych materiałów
     * [403] Usługi obce
       * [4031] Usługi obcego transportu
       * [4032] Usługi remontowe obce
       * [4033] Pozostałe usługi obce
     * [404] Podatki i opłaty
       * [4041] Podatek od nieruchomości
       * [4042]  Podatek od środków transportowych
       * [4043] Podatek akcyzowy
       * [4045] VAT niepodlegający odliczeniu
       * [4046] Pozostałe podatki i opłaty
     * [405] Wynagrodzenia
       * [4051] Wynagrodzenia pracowników
       * [4052] Wynagrodzenia osób doraźnie zatrudnionych
     * [406] Ubezpieczenia społeczne i inne świadczenia
       * [4061]  Składki na ubezpieczenia społeczne, FP, FGŚP
       * [4062] Odpisy na zakładowy fundusz świadczeń socjalnych lub świadczenia urlopowe
       * [4063] Pozostałe świadczenia
     * [407] Pozostałe koszty rodzajowe
   * [49] Rozliczenie kosztów
 * [5] Koszty według typów działalności i ich rozliczenie
   * [50] Koszty działalności podstawowej - produkcyjnej
     * [501] Koszty produkcji przemysłowej
     * [502] Koszty produkcji budowlano-montażowej
     * [503] Koszty produkcji rolnej
     * [504] Koszty usług podstawowych
     * [509] Koszty braków
   * [52] Koszty działalności podstawowej - handlowej
     * [522] Koszty działalności podstawowej - handlowej
       * [5221] Koszty hurtu
       * [5222] Koszty detalu
       * [5223] Koszty zakładów gastronomicznych
       * [5224] Koszty skupu
     * [523] Koszty wydziałowe
     * [529] Koszty sprzedaży
   * [53] Koszty działalności pomocniczej
   * [55] Koszty zarządu
   * [58] Rozliczenie kosztów działalności
 * [6] Produkty i rozliczenia międzyokresowe
   * [60] Produkty gotowe i półprodukty
     * [601] Produkty gotowe
       * [6011]  Produkty gotowe w magazynie
       * [6012] Produkty gotowe poza jednostką
     * [602] Półprodukty
   * [62] Odchylenia od cen ewidencyjnych produktów
     * [621] Odchylenia od cen ewidencyjnych produktów
     * [622] Odchylenia z tytułu aktualizacji wartości zapasów produktów
   * [64] Rozliczenia międzyokresowe kosztów
     * [641] Czynne rozliczenia międzyokresowe kosztów
     * [642] Bierne rozliczenia międzyokresowe kosztów
   * [65] Pozostałe rozliczenia międzyokresowe
     * [651] Aktywa z tytułu odroczonego podatku dochodowego
     * [652] Inne rozliczenia międzyokresowe
   * [67] Inwentarz żywy
     * [671] Inwentarz żywy
     * [672] Odchylenia od cen ewidencyjnych inwentarza żywego
 * [7] Przychody i koszty związane z ich osiągnięciem
   * [70] Przychody i koszty związane ze sprzedażą produktów
     * [701] Sprzedaż produktów
     * [702] Koszt sprzedanych produktów
   * [73] Przychody i koszty związane ze sprzedażą towarów
     * [731] Sprzedaż towarów
     * [732] Wartość sprzedanych towarów w cenach zakupu (nabycia)
   * [74] Przychody i koszty związane ze sprzedażą materiałów i opakowań
     * [741] Sprzedaż materiałów i opakowań
     * [742] Wartość sprzedanych materiałów i opakowań
   * [75] Przychody i koszty finansowe
     * [751] Przychody finansowe
     * [752] Koszty finansowe
   * [76] Pozostałe przychody i koszty operacyjne
     * [761] Pozostałe przychody operacyjne
     * [762] Pozostałe koszty operacyjne
   * [77] Zyski i straty nadzwyczajne
     * [771] Zyski nadzwyczajne
     * [772] Straty nadzwyczajne
   * [79] Obroty wewnętrzne i koszty obrotów wewnętrznych
     * [791] Obroty wewnętrzne
     * [792] Koszty obrotów wewnętrznych
 * [8] Kapitały (fundusze) własne, fundusze specjalne i wynik finansowy
   * [80] Kapitały własne
     * [801] Kapitał (fundusz) podstawowy
     * [802] Kapitał (fundusz) zapasowy
     * [803] Kapitał (fundusz) rezerwowy
     * [804] Kapitał (fundusz) z aktualizacji wyceny
     * [805] Kapitały  (fundusze)  wydzielone w jednostce statutowej  i  zakładach  (oddziałach) samodzielnie sporządzających bilans
   * [81] Rozliczenie wyniku finansowego
   * [82] Rezerwy
     * [821] Rezerwa z tytułu odroczonego podatku dochodowego
     * [822] Pozostałe rezerwy
   * [83] Rozliczenia międzyokresowe przychodów
   * [84] Fundusze specjalne
     * [841] Zakładowy fundusz świadczeń socjalnych
     * [842] Inne fundusze specjalne
       * [8421] Zakładowy fundusz rehabilitacji osób niepełnosprawnych
       * [8422] Fundusz nagród
       * [8423]  Fundusz na remonty zasobów mieszkaniowych
   * [86] Wynik finansowy
   * [87] Podatek dochodowy i inne obowiązkowe obciążenia wyniku finansowego
     * [871] Podatek dochodowy od osób prawnych
     * [872] Inne obowiązkowe obciążenia wyniku finansowego"""

gap = context.getPortalObject().portal_categories.gap.pl.default

for line in gap_text.splitlines():
  sp_line = line.split(None, 2)
  num = sp_line[1].strip('[]')
  descr = sp_line[2]
  if len(num)==1:
    parent = gap
  else:
    cpath=''
    path=[]
    for n in num[0:-1]:
      cpath += n
      path.append(cpath)
    parent = gap.restrictedTraverse('/'.join(path))
    print('Added to ',parent)

  parent.newContent(id=num, title=descr)



return printed
