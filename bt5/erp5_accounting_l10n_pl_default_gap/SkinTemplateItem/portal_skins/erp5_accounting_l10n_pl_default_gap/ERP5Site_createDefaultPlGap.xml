<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>"""\n
Deployment script\n
Creates gap structure under gap/pl/default.\n
The definition text is a raw text representation of a wiki page\n
with accountants-approved gap structure\n
"""\n
\n
gap_text = \\\n
"""* [0] Aktywa trwałe\n
   * [01] Środki trwałe\n
     * [011] Grunty (w tym prawo wieczystego użytkowania gruntu)\n
     * [012] Budynki, lokale i obiekty inżynierii lądowej i wodnej\n
     * [013] Urządzenia techniczne i maszyny\n
     * [014] Środki transportu\n
       * [0141] Samochody osobowe\n
       * [0142] Samochody ciężarowe\n
     * [015] Inne środki trwałe (w tym inwentarz żywy zaliczany do środków trwałych)\n
   * [02] Wartości niematerialne i prawne\n
     * [021] Koszty zakończonych prac rozwojowych\n
     * [022] Wartość firmy\n
     * [023] Inne wartości niematerialne i prawne\n
   * [03] Długoterminowe aktywa finansowe\n
     * [031] Udziały lub akcje\n
     * [032] Inne papiery wartościowe\n
     * [033] Udzielone pożyczki\n
     * [034] Inne długoterminowe aktywa finansowe\n
     * [035] Odpisy aktualizujące długoterminowe aktywa finansowe\n
   * [04] Inwestycje w nieruchomości i prawa\n
     * [041] Nieruchomości\n
     * [042] Wartości niematerialne i prawne\n
   * [07] Odpisy umorzeniowe środków trwałych, wartości niematerialnych i prawnych oraz inwestycji w nieruchomości i prawa\n
     * [071] Odpisy umorzeniowe środków trwałych (do kont 011000 do 015000)\n
     * [072] Odpisy umorzeniowe wartości niematerialnych i prawnych  (do kont 021000 do 023000)\n
     * [073] Odpisy umorzeniowe inwestycji w nieruchomości i prawa (do kont 041000 do 042000)\n
   * [08] Środki trwałe w budowie\n
   * [09] Ewidencja pozabilansowa\n
     * [091] Obce środki trwałe\n
     * [092] Środki trwałe w likwidacji\n
 * [1] Środki pieniężne, rachunki bankowe oraz inne krótkoterminowe aktywa finansowe\n
   * [10] Kasa\n
   * [13] Rachunki i kredyty bankowe\n
     * [131] Rachunek bieżący\n
     * [132] Rachunek walutowy\n
     * [133] Kredyty bankowe\n
     * [134] Inne rachunki bankowe \n
       * [1341] Rachunek bankowy wyodrębnionych środków pieniężnych ZFŚS\n
       * [1342] Rachunek bankowy lokat terminowych (według poszczególnych lokat)\n
       * [1343] Rachunek bankowy akredytywy (według poszczególnych kontrahentów}\n
     * [135] Środki pieniężne w drodze\n
   * [14] Krótkoterminowe aktywa finansowe\n
     * [141] Udziały lub akcje\n
     * [142] Inne papiery wartościowe\n
     * [143] Udzielone pożyczki\n
     * [144] Inne krótkoterminowe aktywa finansowe\n
     * [145] Odpisy aktualizujące krótkoterminowe aktywa finansowe\n
 * [2] Rozrachunki i roszczenia\n
   * [20] Rozrachunki z kontrahentami\n
     * [201] Rozrachunki z odbiorcami\n
     * [202] Rozrachunki z dostawcami\n
   * [22] Rozrachunki publicznoprawne\n
     * [221] Rozrachunki z urzędem skarbowym z tytułu VAT\n
     * [222] Rozrachunki z urzędem skarbowym z tytułu VAT należnego\n
       * [2221] rozliczenie należnego VAT\n
       * [2222] korekty należnego VAT\n
     * [223] Rozrachunki z urzędem skarbowym z tytułu VAT naliczonego\n
       * [2231] rozliczenie naliczonego VAT\n
       * [2232] korekty naliczonego VAT\n
     * [224] Pozostałe rozrachunki publicznoprawne \n
       * [2241] Rozrachunki publicznoprawne z urzędem skarbowym \n
         * [22411] podatek dochodowy\n
         * [22412] podatek od czynności cywilnoprawnych\n
       * [2242] Rozrachunki publicznoprawne z urzędem miasta/gminy\n
         * [22421] Podatek od nieruchomości\n
         * [22422] podatek od środków transportowych\n
       * [2243] Rozrachunki publicznoprawne z urzędem celnym\n
       * [2244] Rozrachunki publicznoprawne z ZUS \n
       * [2245]  Rozrachunki publicznoprawne z PFRON\n
   * [23] Rozrachunki z tytułu wynagrodzeń i innych świadczeń na rzecz pracowników\n
     * [231] Rozrachunki z tytułu wynagrodzeń\n
       * [2311] umowa o pracę \n
       * [2312] umowy cywilnoprawne\n
     * [232] Rozrachunki z pracownikami\n
       * [2321] zaliczki\n
   * [24] Rozrachunki z akcjonariuszami i udziałowcami\n
     * [241] Rozrachunki z akcjonariuszami\n
     * [242] Rozrachunki z udziałowcami\n
   * [25] Pozostałe rozrachunki\n
     * [251] Inne rozrachunki z kontrahentami\n
   * [26] Pożyczki \n
     * [261] Pożyczki otrzymane\n
     * [262]  Pożyczki udzielone\n
   * [27] Rozliczenie niedoborów i nadwyżek\n
     * [271] Rozliczenie niedoborów\n
     * [272] Rozliczenie nadwyżek\n
   * [28] Należności dochodzone na drodze sądowej\n
   * [29] Rozrachunki pozabilansowe\n
     * [291] Należności warunkowe\n
     * [292] Zobowiązania warunkowe\n
     * [293] Weksle obce dyskontowane lub indosowane\n
 * [3] Materiały i towary\n
   * [30] Rozliczenie zakupu\n
     * [301] Rozliczenie zakupu materiałów\n
     * [302] Rozliczenie zakupu towarów\n
     * [303] Rozliczenie zakupu usług obcych\n
     * [304] Rozliczenie zakupu składników aktywów trwałych\n
   * [31] Materiały i opakowania\n
     * [311] Materiały\n
     * [312] Opakowania\n
     * [313] Materiały w przerobie\n
   * [33] Towary\n
     * [331] Towary w hurcie\n
     * [332] Towary w detalu\n
     * [333] Towary w zakładach gastronomicznych\n
     * [334] Towary skupu\n
     * [335] Towary poza jednostką\n
     * [336] Nieruchomości i prawa majątkowe przeznaczone do obrotu\n
   * [34] Odchylenia od cen ewidencyjnych materiałów i towarów\n
     * [341] Odchylenia od cen ewidencyjnych materiałów\n
     * [342] Odchylenia od cen ewidencyjnych towarów \n
       * [3421] Odchylenia od cen ewidencyjnych towarów w hurcie\n
       * [3422] Odchylenia od cen ewidencyjnych towarów w detalu\n
       * [3423] Odchylenia od cen ewidencyjnych towarów w zakładach gastronomicznych\n
       * [3424] Odchylenia od cen ewidencyjnych towarów skupu\n
     * [346] Odchylenia od cen ewidencyjnych opakowań\n
     * [347] Odchylenia z tytułu aktualizacji wartości zapasów materiałów i towarów\n
   * [39] Zapasy obce\n
 * [4] Koszty według rodzajów i ich rozliczenie\n
   * [40] Koszty według rodzajów\n
     * [401] Amortyzacja\n
       * [4011] amortyzacja urządzeń technicznych\n
       * [4012] amortyzacja środków transportu\n
     * [402] Zużycie materiałów i energii \n
       * [4021] Zużycie surowców do wytwarzania produktów \n
       * [4022] Zużycie energii\n
       * [4023] Zużycie paliwa dla środków transportu\n
         * [40231] Zużycie Oleju napędowego\n
         * [40232] Zużycie  Etyliny 95\n
       * [4024] Zużycie innych materiałów\n
     * [403] Usługi obce\n
       * [4031] Usługi obcego transportu\n
       * [4032] Usługi remontowe obce\n
       * [4033] Pozostałe usługi obce\n
     * [404] Podatki i opłaty\n
       * [4041] Podatek od nieruchomości\n
       * [4042]  Podatek od środków transportowych \n
       * [4043] Podatek akcyzowy\n
       * [4045] VAT niepodlegający odliczeniu\n
       * [4046] Pozostałe podatki i opłaty\n
     * [405] Wynagrodzenia\n
       * [4051] Wynagrodzenia pracowników\n
       * [4052] Wynagrodzenia osób doraźnie zatrudnionych\n
     * [406] Ubezpieczenia społeczne i inne świadczenia\n
       * [4061]  Składki na ubezpieczenia społeczne, FP, FGŚP\n
       * [4062] Odpisy na zakładowy fundusz świadczeń socjalnych lub świadczenia urlopowe \n
       * [4063] Pozostałe świadczenia\n
     * [407] Pozostałe koszty rodzajowe\n
   * [49] Rozliczenie kosztów\n
 * [5] Koszty według typów działalności i ich rozliczenie\n
   * [50] Koszty działalności podstawowej - produkcyjnej\n
     * [501] Koszty produkcji przemysłowej\n
     * [502] Koszty produkcji budowlano-montażowej\n
     * [503] Koszty produkcji rolnej\n
     * [504] Koszty usług podstawowych\n
     * [509] Koszty braków\n
   * [52] Koszty działalności podstawowej - handlowej\n
     * [522] Koszty działalności podstawowej - handlowej \n
       * [5221] Koszty hurtu \n
       * [5222] Koszty detalu \n
       * [5223] Koszty zakładów gastronomicznych \n
       * [5224] Koszty skupu\n
     * [523] Koszty wydziałowe\n
     * [529] Koszty sprzedaży\n
   * [53] Koszty działalności pomocniczej\n
   * [55] Koszty zarządu\n
   * [58] Rozliczenie kosztów działalności\n
 * [6] Produkty i rozliczenia międzyokresowe\n
   * [60] Produkty gotowe i półprodukty\n
     * [601] Produkty gotowe\n
       * [6011]  Produkty gotowe w magazynie \n
       * [6012] Produkty gotowe poza jednostką\n
     * [602] Półprodukty\n
   * [62] Odchylenia od cen ewidencyjnych produktów\n
     * [621] Odchylenia od cen ewidencyjnych produktów\n
     * [622] Odchylenia z tytułu aktualizacji wartości zapasów produktów\n
   * [64] Rozliczenia międzyokresowe kosztów\n
     * [641] Czynne rozliczenia międzyokresowe kosztów\n
     * [642] Bierne rozliczenia międzyokresowe kosztów\n
   * [65] Pozostałe rozliczenia międzyokresowe\n
     * [651] Aktywa z tytułu odroczonego podatku dochodowego\n
     * [652] Inne rozliczenia międzyokresowe\n
   * [67] Inwentarz żywy\n
     * [671] Inwentarz żywy\n
     * [672] Odchylenia od cen ewidencyjnych inwentarza żywego\n
 * [7] Przychody i koszty związane z ich osiągnięciem\n
   * [70] Przychody i koszty związane ze sprzedażą produktów\n
     * [701] Sprzedaż produktów\n
     * [702] Koszt sprzedanych produktów\n
   * [73] Przychody i koszty związane ze sprzedażą towarów\n
     * [731] Sprzedaż towarów\n
     * [732] Wartość sprzedanych towarów w cenach zakupu (nabycia)\n
   * [74] Przychody i koszty związane ze sprzedażą materiałów i opakowań\n
     * [741] Sprzedaż materiałów i opakowań\n
     * [742] Wartość sprzedanych materiałów i opakowań\n
   * [75] Przychody i koszty finansowe\n
     * [751] Przychody finansowe\n
     * [752] Koszty finansowe\n
   * [76] Pozostałe przychody i koszty operacyjne\n
     * [761] Pozostałe przychody operacyjne\n
     * [762] Pozostałe koszty operacyjne\n
   * [77] Zyski i straty nadzwyczajne\n
     * [771] Zyski nadzwyczajne\n
     * [772] Straty nadzwyczajne\n
   * [79] Obroty wewnętrzne i koszty obrotów wewnętrznych\n
     * [791] Obroty wewnętrzne\n
     * [792] Koszty obrotów wewnętrznych\n
 * [8] Kapitały (fundusze) własne, fundusze specjalne i wynik finansowy\n
   * [80] Kapitały własne\n
     * [801] Kapitał (fundusz) podstawowy\n
     * [802] Kapitał (fundusz) zapasowy \n
     * [803] Kapitał (fundusz) rezerwowy\n
     * [804] Kapitał (fundusz) z aktualizacji wyceny\n
     * [805] Kapitały  (fundusze)  wydzielone w jednostce statutowej  i  zakładach  (oddziałach) samodzielnie sporządzających bilans\n
   * [81] Rozliczenie wyniku finansowego\n
   * [82] Rezerwy\n
     * [821] Rezerwa z tytułu odroczonego podatku dochodowego\n
     * [822] Pozostałe rezerwy\n
   * [83] Rozliczenia międzyokresowe przychodów\n
   * [84] Fundusze specjalne\n
     * [841] Zakładowy fundusz świadczeń socjalnych\n
     * [842] Inne fundusze specjalne\n
       * [8421] Zakładowy fundusz rehabilitacji osób niepełnosprawnych \n
       * [8422] Fundusz nagród \n
       * [8423]  Fundusz na remonty zasobów mieszkaniowych\n
   * [86] Wynik finansowy\n
   * [87] Podatek dochodowy i inne obowiązkowe obciążenia wyniku finansowego\n
     * [871] Podatek dochodowy od osób prawnych\n
     * [872] Inne obowiązkowe obciążenia wyniku finansowego"""\n
\n
gap = context.getPortalObject().portal_categories.gap.pl.default\n
\n
for line in gap_text.splitlines():\n
  sp_line = line.split(None, 2)\n
  num = sp_line[1].strip(\'[]\')\n
  descr = sp_line[2]\n
  if len(num)==1:\n
    parent = gap\n
  else:\n
    cpath=\'\'\n
    path=[]\n
    for n in num[0:-1]:\n
      cpath += n\n
      path.append(cpath)\n
    parent = gap.restrictedTraverse(\'/\'.join(path))\n
    print \'Added to \',parent\n
\n
  parent.newContent(id=num, title=descr)  \n
  \n
\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_createDefaultPlGap</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
