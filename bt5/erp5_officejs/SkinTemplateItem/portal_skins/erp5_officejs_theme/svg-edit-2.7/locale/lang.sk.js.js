<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts40515059.54</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>lang.sk.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor */\n
svgEditor.readLang({\n
\tlang: "sk",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "Uložiť",\n
\t\t"cancel": "Zrušiť",\n
\t\t"key_backspace": "Backspace", \n
\t\t"key_del": "Delete", \n
\t\t"key_down": "šípka dole", \n
\t\t"key_up": "šípka hore", \n
\t\t"more_opts": "Viac možností",\n
\t\t"url": "URL",\n
\t\t"width": "Šírka",\n
\t\t"height": "Výška"\n
\t},\n
\tmisc: {\n
\t\t"powered_by": "Beží na"\n
\t}, \n
\tui: {\n
\t\t"toggle_stroke_tools": "Skryť/ukázať viac nástrojov pre krivku",\n
\t\t"palette_info": "Kliknutím zmeníte farbu výplne, so Shiftom zmeníte farbu obrysu",\n
\t\t"zoom_level": "Zmena priblíženia",\n
\t\t"panel_drag": "Potiahnutie vľavo/vpravo na zmenu veľkosti bočného panela"\n
\t},\n
\tproperties: {\n
\t\t"id": "Zmeniť ID elementu",\n
\t\t"fill_color": "Zmeniť farbu výplne",\n
\t\t"stroke_color": "Zmeniť farbu obrysu",\n
\t\t"stroke_style": "Zmeniť štýl obrysu",\n
\t\t"stroke_width": "Zmeniť hrúbku obrysu",\n
\t\t"pos_x": "Zmeniť súradnicu X",\n
\t\t"pos_y": "Zmeniť súradnicu Y",\n
\t\t"linecap_butt": "Koniec čiary: presný",\n
\t\t"linecap_round": "Koniec čiary: zaoblený",\n
\t\t"linecap_square": "Koniec čiary: so štvorcovým presahom",\n
\t\t"linejoin_bevel": "Napojenie čiar: skosené",\n
\t\t"linejoin_miter": "Napojenie čiar: ostré",\n
\t\t"linejoin_round": "Napojenie čiar: oblé",\n
\t\t"angle": "Zmeniť uhol natočenia",\n
\t\t"blur": "Zmeniť intenzitu rozmazania",\n
\t\t"opacity": "Zmeniť prehľadnosť vybraných položiek",\n
\t\t"circle_cx": "Zmeniť súradnicu X stredu kružnice",\n
\t\t"circle_cy": "Zmeniť súradnicu Y stredu kružnice",\n
\t\t"circle_r": "Zmeniť polomer kružnice",\n
\t\t"ellipse_cx": "Zmeniť súradnicu X stredu elipsy",\n
\t\t"ellipse_cy": "Zmeniť súradnicu Y stredu elipsy",\n
\t\t"ellipse_rx": "Zmeniť polomer X elipsy",\n
\t\t"ellipse_ry": "Zmeniť polomer Y elipsy",\n
\t\t"line_x1": "Zmeniť počiatočnú súradnicu X čiary",\n
\t\t"line_x2": "Zmeniť koncovú súradnicu X čiary",\n
\t\t"line_y1": "Zmeniť počiatočnú súradnicu Y čiary",\n
\t\t"line_y2": "Zmeniť koncovú súradnicu Y čiary",\n
\t\t"rect_height": "Zmena výšku obdĺžnika",\n
\t\t"rect_width": "Zmeniť šírku obdĺžnika",\n
\t\t"corner_radius": "Zmeniť zaoblenie rohov obdĺžnika",\n
\t\t"image_width": "Zmeniť šírku obrázka",\n
\t\t"image_height": "Zmeniť výšku obrázka",\n
\t\t"image_url": "Zmeniť URL",\n
\t\t"node_x": "Zmeniť uzlu súradnicu X",\n
\t\t"node_y": "Zmeniť uzlu súradnicu Y",\n
\t\t"seg_type": "Zmeniť typ segmentu",\n
\t\t"straight_segments": "Rovný",\n
\t\t"curve_segments": "Krivka",\n
\t\t"text_contents": "Zmeniť text",\n
\t\t"font_family": "Zmeniť font",\n
\t\t"font_size": "Zmeniť veľkosť písma",\n
\t\t"bold": "Tučné",\n
\t\t"italic": "Kurzíva"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Hlavné menu",\n
\t\t"bkgnd_color_opac": "Zmeniť farbu a priehľadnosť pozadia",\n
\t\t"connector_no_arrow": "Spojnica bez šípok",\n
\t\t"fitToContent": "Prispôsobiť obsahu",\n
\t\t"fit_to_all": "Prisposobiť celému obsahu",\n
\t\t"fit_to_canvas": "Prispôsobiť stránke",\n
\t\t"fit_to_layer_content": "Prispôsobiť obsahu vrstvy",\n
\t\t"fit_to_sel": "Prispôsobiť výberu",\n
\t\t"align_relative_to": "Zarovnať relatívne k ...",\n
\t\t"relativeTo": "vzhľadom k:",\n
\t\t"page": "stránke",\n
\t\t"largest_object": "najväčšiemu objektu",\n
\t\t"selected_objects": "zvoleným objektom",\n
\t\t"smallest_object": "najmenšiemu objektu",\n
\t\t"new_doc": "Nový obrázok",\n
\t\t"open_doc": "Otvoriť obrázok",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "Uložiť obrázok",\n
\t\t"import_doc": "Import SVG",\n
\t\t"align_to_page": "Zarovnať element na stránku",\n
\t\t"align_bottom": "Zarovnať dole",\n
\t\t"align_center": "Zarovnať na stred",\n
\t\t"align_left": "Zarovnať doľava",\n
\t\t"align_middle": "Zarovnať na stred",\n
\t\t"align_right": "Zarovnať doprava",\n
\t\t"align_top": "Zarovnať hore",\n
\t\t"mode_select": "Výber",\n
\t\t"mode_fhpath": "Ceruzka",\n
\t\t"mode_line": "Čiara",\n
\t\t"mode_connect": "Spojiť dva objekty",\n
\t\t"mode_rect": "Obdĺžnik",\n
\t\t"mode_square": "Štvorec",\n
\t\t"mode_fhrect": "Obdĺžnik voľnou rukou",\n
\t\t"mode_ellipse": "Elipsa",\n
\t\t"mode_circle": "Kružnica",\n
\t\t"mode_fhellipse": "Elipsa voľnou rukou",\n
\t\t"mode_path": "Krivka",\n
\t\t"mode_shapelib": "Knižnica Tvarov",\n
\t\t"mode_text": "Text",\n
\t\t"mode_image": "Obrázok",\n
\t\t"mode_zoom": "Priblíženie",\n
\t\t"mode_eyedropper": "Pipeta",\n
\t\t"no_embed": "POZNÁMKA: Tento obrázok nemôže byť vložený. Jeho zobrazenie bude závisieť na jeho ceste",\n
\t\t"undo": "Späť",\n
\t\t"redo": "Opakovať",\n
\t\t"tool_source": "Upraviť SVG kód",\n
\t\t"wireframe_mode": "Drôtový model",\n
\t\t"toggle_grid": "Zobraz/Skry mriežku",\n
\t\t"clone": "Klonuj element(y)",\n
\t\t"del": "Zmaž element(y)",\n
\t\t"group_elements": "Zoskupiť elementy",\n
\t\t"make_link": "Naviaž odkaz (hyper)link",\n
\t\t"set_link_url": "Nastav odkaz URL (ak prázdny, odstráni sa)",\n
\t\t"to_path": "Previesť na krivku",\n
\t\t"reorient_path": "Zmeniť orientáciu krivky",\n
\t\t"ungroup": "Zrušiť skupinu",\n
\t\t"docprops": "Vlastnosti dokumentu",\n
\t\t"imagelib": "Knižnica obrázkov",\n
\t\t"move_bottom": "Presunúť spodok",\n
\t\t"move_top": "Presunúť na vrch",\n
\t\t"node_clone": "Klonovať uzol",\n
\t\t"node_delete": "Zmazať uzol",\n
\t\t"node_link": "Prepojiť kontrolné body",\n
\t\t"add_subpath": "Pridať ďalšiu súčasť krivky",\n
\t\t"openclose_path": "Otvoriť/uzatvoriť súčasť krivky",\n
\t\t"source_save": "Uložiť",\n
\t\t"cut": "Vystrihnutie",\n
\t\t"copy": "Kópia",\n
\t\t"paste": "Vloženie",\n
\t\t"paste_in_place": "Vloženie na pôvodnom mieste",\n
\t\t"delete": "Zmazanie",\n
\t\t"group": "Group",\n
\t\t"move_front": "Vysuň navrch",\n
\t\t"move_up": "Vysuň vpred",\n
\t\t"move_down": "Zasuň na spodok",\n
\t\t"move_back": "Zasuň dozadu"\n
\t},\n
\tlayers: {\n
\t\t"layer": "Vrstva",\n
\t\t"layers": "Vrstvy",\n
\t\t"del": "Odstrániť vrstvu",\n
\t\t"move_down": "Presunúť vrstvu dole",\n
\t\t"new": "Nová vrstva",\n
\t\t"rename": "Premenovať vrstvu",\n
\t\t"move_up": "Presunúť vrstvu hore",\n
\t\t"dupe": "Zduplikovať vrstvu",\n
\t\t"merge_down": "Zlúčiť s vrstvou dole",\n
\t\t"merge_all": "Zlúčiť všetko",\n
\t\t"move_elems_to": "Presunúť elementy do:",\n
\t\t"move_selected": "Presunúť vybrané elementy do inej vrstvy"\n
\t},\n
\tconfig: {\n
\t\t"image_props": "Vlastnosti obrázka",\n
\t\t"doc_title": "Titulok",\n
\t\t"doc_dims": "Rozmery plátna",\n
\t\t"included_images": "Vložené obrázky",\n
\t\t"image_opt_embed": "Vložiť data (lokálne súbory)",\n
\t\t"image_opt_ref": "Použiť referenciu na súbor",\n
\t\t"editor_prefs": "Vlastnosti editora",\n
\t\t"icon_size": "Veľkosť ikon",\n
\t\t"language": "Jazyk",\n
\t\t"background": "Zmeniť pozadie",\n
\t\t"editor_img_url": "Image URL",\n
\t\t"editor_bg_note": "Poznámka: Pozadie nebude uložené spolu s obrázkom.",\n
\t\t"icon_large": "Veľká",\n
\t\t"icon_medium": "Stredná",\n
\t\t"icon_small": "Malá",\n
\t\t"icon_xlarge": "Extra veľká",\n
\t\t"select_predefined": "Vybrať preddefinovaný:",\n
\t\t"units_and_rulers": "Jednotky & Pravítka",\n
\t\t"show_rulers": "Ukáž pravítka",\n
\t\t"base_unit": "Základné jednotky:",\n
\t\t"grid": "Mriežka",\n
\t\t"snapping_onoff": "Priväzovanie (do mriežky) zap/vyp",\n
\t\t"snapping_stepsize": "Priväzovanie (do mriežky) veľkosť kroku:",\n
\t\t"grid_color": "Grid color"\n
\t},\n
\tshape_cats: {\n
\t\t"basic": "Základné",\n
\t\t"object": "Objekty",\n
\t\t"symbol": "Symboly",\n
\t\t"arrow": "Šípky",\n
\t\t"flowchart": "Vývojové diagramy",\n
\t\t"animal": "Zvieratá",\n
\t\t"game": "Karty & Šach",\n
\t\t"dialog_balloon": "Dialogové balóny",\n
\t\t"electronics": "Elektronika",\n
\t\t"math": "Matematické",\n
\t\t"music": "Hudba",\n
\t\t"misc": "Rôzne",\n
\t\t"raphael_1": "raphaeljs.com sada 1",\n
\t\t"raphael_2": "raphaeljs.com sada 2"\n
\t},\n
\timagelib: {\n
\t\t"select_lib": "Výber knižnice obrázkov",\n
\t\t"show_list": "Prehľad knižnice",\n
\t\t"import_single": "Import jeden",\n
\t\t"import_multi": "Import viacero",\n
\t\t"open": "Otvoriť ako nový dokument"\n
\t},\n
\tnotification: {\n
\t\t"invalidAttrValGiven":"Neplatná hodnota",\n
\t\t"noContentToFitTo":"Vyberte oblasť na prispôsobenie",\n
\t\t"dupeLayerName":"Vrstva s daným názvom už existuje!",\n
\t\t"enterUniqueLayerName":"Zadajte jedinečný názov vrstvy",\n
\t\t"enterNewLayerName":"Zadajte názov vrstvy",\n
\t\t"layerHasThatName":"Vrstva už má zadaný tento názov",\n
\t\t"QmoveElemsToLayer":"Presunúť elementy do vrstvy \'%s\'?",\n
\t\t"QwantToClear":"Naozaj chcete vymazať kresbu?\\n(História bude taktiež vymazaná!)!",\n
\t\t"QwantToOpen":"Chcete otvoriť nový súbor?\\nTo však tiež vymaže Vašu UNDO knižnicu!",\n
\t\t"QerrorsRevertToSource":"Chyba pri načítaní SVG dokumentu.\\nVrátiť povodný SVG dokument?",\n
\t\t"QignoreSourceChanges":"Ignorovať zmeny v SVG dokumente?",\n
\t\t"featNotSupported":"Vlastnosť nie je podporovaná",\n
\t\t"enterNewImgURL":"Zadajte nové URL obrázka",\n
\t\t"defsFailOnSave": "POZNÁMKA: Kvôli chybe v prehliadači sa tento obrázok môže zobraziť nesprávne (napr. chýbajúce prechody či elementy). Po uložení sa zobrazí správne.",\n
\t\t"loadingImage":"Nahrávam obrázok, prosím čakajte ...",\n
\t\t"saveFromBrowser": "Vyberte \\"Uložiť ako ...\\" vo vašom prehliadači na uloženie tohoto obrázka do súboru %s.",\n
\t\t"noteTheseIssues": "Môžu sa vyskytnúť nasledujúce problémy: ",\n
\t\t"unsavedChanges": "Sú tu neuložené zmeny.",\n
\t\t"enterNewLinkURL": "Zadajte nové URL odkazu (hyperlink)",\n
\t\t"errorLoadingSVG": "Chyba: Nedajú sa načítať SVG data",\n
\t\t"URLloadFail": "Nemožno čítať z URL",\n
\t\t"retrieving": "Načítavanie \\"%s\\"..."\n
\t},\n
\tconfirmSetStorage: {\n
\t\tmessage: "By default and where supported, SVG-Edit can store your editor "+\n
\t\t"preferences and SVG content locally on your machine so you do not "+\n
\t\t"need to add these back each time you load SVG-Edit. If, for privacy "+\n
\t\t"reasons, you do not wish to store this information on your machine, "+\n
\t\t"you can change away from the default option below.",\n
\t\tstoragePrefsAndContent: "Store preferences and SVG content locally",\n
\t\tstoragePrefsOnly: "Only store preferences locally",\n
\t\tstoragePrefs: "Store preferences locally",\n
\t\tstorageNoPrefsOrContent: "Do not store my preferences or SVG content locally",\n
\t\tstorageNoPrefs: "Do not store my preferences locally",\n
\t\trememberLabel: "Remember this choice?",\n
\t\trememberTooltip: "If you choose to opt out of storage while remembering this choice, the URL will change so as to avoid asking again."\n
\t}\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9940</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
