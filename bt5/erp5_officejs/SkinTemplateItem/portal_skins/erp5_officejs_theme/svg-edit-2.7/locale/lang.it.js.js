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
            <value> <string>lang.it.js</string> </value>
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
\tlang: "it",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "Salva",\n
\t\t"cancel": "Annulla",\n
\t\t"key_backspace": "backspace", \n
\t\t"key_del": "Canc", \n
\t\t"key_down": "giù", \n
\t\t"key_up": "su", \n
\t\t"more_opts": "More Options",\n
\t\t"url": "URL",\n
\t\t"width": "Width",\n
\t\t"height": "Height"\n
\t},\n
\tmisc: {\n
\t\t"powered_by": "Powered by"\n
\t}, \n
\tui: {\n
\t\t"toggle_stroke_tools": "Mostra/nascondi strumenti per il tratto",\n
\t\t"palette_info": "Fare clic per cambiare il colore di riempimento, shift-click per cambiare colore del tratto",\n
\t\t"zoom_level": "Cambia il livello di zoom",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identifica l\'elemento",\n
\t\t"fill_color": "Cambia il colore di riempimento",\n
\t\t"stroke_color": "Cambia il colore del tratto",\n
\t\t"stroke_style": "Cambia lo stile del tratto",\n
\t\t"stroke_width": "Cambia la larghezza del tratto",\n
\t\t"pos_x": "Modifica la coordinata x",\n
\t\t"pos_y": "Modifica la coordinata y",\n
\t\t"linecap_butt": "Inizio linea: Punto",\n
\t\t"linecap_round": "Inizio linea: Tondo",\n
\t\t"linecap_square": "Inizio linea: Quadrato",\n
\t\t"linejoin_bevel": "Giunzione: smussata",\n
\t\t"linejoin_miter": "Giunzione: spezzata",\n
\t\t"linejoin_round": "Giunzione: arrotondata",\n
\t\t"angle": "Cambia l\'angolo di rotazione",\n
\t\t"blur": "Cambia l\'intensità della sfocatura",\n
\t\t"opacity": "Cambia l\'opacità dell\'oggetto selezionato",\n
\t\t"circle_cx": "Cambia la coordinata Cx del cerchio",\n
\t\t"circle_cy": "Cambia la coordinata Cy del cerchio",\n
\t\t"circle_r": "Cambia il raggio del cerchio",\n
\t\t"ellipse_cx": "Cambia la coordinata Cx dell\'ellisse",\n
\t\t"ellipse_cy": "Cambia la coordinata Cy dell\'ellisse",\n
\t\t"ellipse_rx": "Cambia l\'asse x dell\'ellisse",\n
\t\t"ellipse_ry": "Cambia l\'asse y dell\'ellisse",\n
\t\t"line_x1": "Modifica la coordinata iniziale x della linea",\n
\t\t"line_x2": "Modifica la coordinata finale x della linea",\n
\t\t"line_y1": "Modifica la coordinata iniziale y della linea",\n
\t\t"line_y2": "Modifica la coordinata finale y della linea",\n
\t\t"rect_height": "Cambia l\'altezza rettangolo",\n
\t\t"rect_width": "Cambia la larghezza rettangolo",\n
\t\t"corner_radius": "Cambia il raggio dell\'angolo",\n
\t\t"image_width": "Cambia la larghezza dell\'immagine",\n
\t\t"image_height": "Cambia l\'altezza dell\'immagine",\n
\t\t"image_url": "Cambia URL",\n
\t\t"node_x": "Modifica la coordinata x del nodo",\n
\t\t"node_y": "Modifica la coordinata y del nodo",\n
\t\t"seg_type": "Cambia il tipo di segmento",\n
\t\t"straight_segments": "Linea retta",\n
\t\t"curve_segments": "Curva",\n
\t\t"text_contents": "Cambia il contenuto del testo",\n
\t\t"font_family": "Cambia il tipo di Font",\n
\t\t"font_size": "Modifica dimensione carattere",\n
\t\t"bold": "Grassetto",\n
\t\t"italic": "Corsivo"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Menù principale",\n
\t\t"bkgnd_color_opac": "Cambia colore/opacità dello sfondo",\n
\t\t"connector_no_arrow": "No freccia",\n
\t\t"fitToContent": "Adatta al contenuto",\n
\t\t"fit_to_all": "Adatta a tutti i contenuti",\n
\t\t"fit_to_canvas": "Adatta all\'area di disegno",\n
\t\t"fit_to_layer_content": "Adatta al contenuto del livello",\n
\t\t"fit_to_sel": "Adatta alla selezione",\n
\t\t"align_relative_to": "Allineati a ...",\n
\t\t"relativeTo": "Rispetto a:",\n
\t\t"Pagina": "Pagina",\n
\t\t"largest_object": "Oggetto più grande",\n
\t\t"selected_objects": "Oggetti selezionati",\n
\t\t"smallest_object": "Oggetto più piccolo",\n
\t\t"new_doc": "Nuova immagine",\n
\t\t"open_doc": "Apri immagine",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "Salva",\n
\t\t"import_doc": "Importa SVG",\n
\t\t"align_to_page": "Allinea elementi alla pagina",\n
\t\t"align_bottom": "Allinea in basso",\n
\t\t"align_center": "Allinea al centro",\n
\t\t"align_left": "Allinea a sinistra",\n
\t\t"align_middle": "Allinea al centro",\n
\t\t"align_right": "Allinea a destra",\n
\t\t"align_top": "Allinea in alto",\n
\t\t"mode_select": "Seleziona",\n
\t\t"mode_fhpath": "Matita",\n
\t\t"mode_line": "Linea",\n
\t\t"mode_connect": "Collega due oggetti",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "Rettangolo a mano libera",\n
\t\t"mode_ellipse": "Ellisse",\n
\t\t"mode_circle": "Cerchio",\n
\t\t"mode_fhellipse": "Ellisse a mano libera",\n
\t\t"mode_path": "Spezzata",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "Testo",\n
\t\t"mode_image": "Immagine",\n
\t\t"mode_zoom": "Zoom",\n
\t\t"mode_eyedropper": "Seleziona colore",\n
\t\t"no_embed": "NOTA: L\'immagine non può essere incorporata: dipenderà dal percorso assoluto per essere vista",\n
\t\t"undo": "Annulla",\n
\t\t"redo": "Rifai",\n
\t\t"tool_source": "Modifica sorgente",\n
\t\t"wireframe_mode": "Contorno",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "Raggruppa elementi",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "Converti in tracciato",\n
\t\t"reorient_path": "Riallinea",\n
\t\t"ungroup": "Separa gli elementi",\n
\t\t"docprops": "Proprietà del documento",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "Sposta in fondo",\n
\t\t"move_top": "Sposta in cima",\n
\t\t"node_clone": "Clona nodo",\n
\t\t"node_delete": "Elimina nodo",\n
\t\t"node_link": "Collegamento tra punti di controllo",\n
\t\t"add_subpath": "Aggiungi sotto-percorso",\n
\t\t"openclose_path": "Apri/chiudi spezzata",\n
\t\t"source_save": "Salva",\n
\t\t"cut": "Cut",\n
\t\t"copy": "Copy",\n
\t\t"paste": "Paste",\n
\t\t"paste_in_place": "Paste in Place",\n
\t\t"Canc": "Delete",\n
\t\t"group": "Group",\n
\t\t"move_front": "Bring to Front",\n
\t\t"move_up": "Bring Forward",\n
\t\t"move_down": "Send Backward",\n
\t\t"move_back": "Send to Back"\n
\t},\n
\tlayers: {\n
\t\t"layer":"Livello",\n
\t\t"layers": "Layers",\n
\t\t"del": "Elimina il livello",\n
\t\t"move_down": "Sposta indietro il livello",\n
\t\t"new": "Nuovo livello",\n
\t\t"rename": "Rinomina il livello",\n
\t\t"move_up": "Sposta avanti il livello",\n
\t\t"dupe": "Duplicate Layer",\n
\t\t"merge_down": "Merge Down",\n
\t\t"merge_all": "Merge All",\n
\t\t"move_elems_to": "Sposta verso:",\n
\t\t"move_selected": "Sposta gli elementi in un diverso livello"\n
\t},\n
\tconfig: {\n
\t\t"image_props": "Proprietà Immagine",\n
\t\t"doc_title": "Titolo",\n
\t\t"doc_dims": "Dimensioni dell\'area di disegno",\n
\t\t"included_images": "Immagini incluse",\n
\t\t"image_opt_embed": "Incorpora dati (file locali)",\n
\t\t"image_opt_ref": "Usa l\'identificativo di riferimento",\n
\t\t"editor_prefs": "Preferenze",\n
\t\t"icon_size": "Dimensione Icona",\n
\t\t"language": "Lingua",\n
\t\t"background": "Sfondo dell\'editor",\n
\t\t"editor_img_url": "Image URL",\n
\t\t"editor_bg_note": "Nota: Lo sfondo non verrà salvato con l\'immagine.",\n
\t\t"icon_large": "Grande",\n
\t\t"icon_medium": "Medio",\n
\t\t"icon_small": "Piccolo",\n
\t\t"icon_xlarge": "Molto grande",\n
\t\t"select_predefined": "Selezioni predefinite:",\n
\t\t"units_and_rulers": "Units & Rulers",\n
\t\t"show_rulers": "Show rulers",\n
\t\t"base_unit": "Base Unit:",\n
\t\t"grid": "Grid",\n
\t\t"snapping_onoff": "Snapping on/off",\n
\t\t"snapping_stepsize": "Snapping Step-Size:",\n
\t\t"grid_color": "Grid color"\n
\t},\n
\tshape_cats: {\n
\t\t"basic": "Basic",\n
\t\t"object": "Objects",\n
\t\t"symbol": "Symbols",\n
\t\t"arrow": "Arrows",\n
\t\t"flowchart": "Flowchart",\n
\t\t"animal": "Animals",\n
\t\t"game": "Cards & Chess",\n
\t\t"dialog_balloon": "Dialog balloons",\n
\t\t"electronics": "Electronics",\n
\t\t"math": "Mathematical",\n
\t\t"music": "Music",\n
\t\t"misc": "Miscellaneous",\n
\t\t"raphael_1": "raphaeljs.com set 1",\n
\t\t"raphael_2": "raphaeljs.com set 2"\n
\t},\n
\timagelib: {\n
\t\t"select_lib": "Select an image library",\n
\t\t"show_list": "Show library list",\n
\t\t"import_single": "Import single",\n
\t\t"import_multi": "Import multiple",\n
\t\t"open": "Open as new document"\n
\t},\n
\tnotification: {\n
\t\t"invalidAttrValGiven":"Valore assegnato non valido",\n
\t\t"noContentToFitTo":"Non c\'è contenuto cui adeguarsi",\n
\t\t"dupeLayerName":"C\'è già un livello con questo nome!",\n
\t\t"enterUniqueLayerName":"Assegna un diverso nome a ciascun livello, grazie!",\n
\t\t"enterNewLayerName":"Assegna un nome al livello",\n
\t\t"layerHasThatName":"Un livello ha già questo nome",\n
\t\t"QmoveElemsToLayer":"Sposta gli elementi selezionali al livello \'%s\'?",\n
\t\t"QwantToClear":"Vuoi cancellare il disegno?\\nVerrà eliminato anche lo storico delle modifiche!",\n
\t\t"QwantToOpen":"Do you want to open a new file?\\nThis will also erase your undo history!",\n
\t\t"QerrorsRevertToSource":"Ci sono errori nel codice sorgente SVG.\\nRitorno al codice originale?",\n
\t\t"QignoreSourceChanges":"Ignoro i cambiamenti nel sorgente SVG?",\n
\t\t"featNotSupported":"Caratteristica non supportata",\n
\t\t"enterNewImgURL":"Scrivi un nuovo URL per l\'immagine",\n
\t\t"defsFailOnSave": "NOTA: A causa dlle caratteristiche del tuo browser, l\'immagine potrà apparire errata (senza elementi o gradazioni) finché non sarà salvata.",\n
\t\t"loadingImage":"Sto caricando l\'immagine. attendere prego...",\n
\t\t"saveFromBrowser": "Seleziona \\"Salva con nome...\\" nel browser per salvare l\'immagine con nome %s .",\n
\t\t"noteTheseIssues": "Nota le seguenti particolarità: ",\n
\t\t"unsavedChanges": "There are unsaved changes.",\n
\t\t"enterNewLinkURL": "Enter the new hyperlink URL",\n
\t\t"errorLoadingSVG": "Error: Unable to load SVG data",\n
\t\t"URLloadFail": "Unable to load from URL",\n
\t\t"retrieving": "Retrieving \\"%s\\"..."\n
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
            <value> <int>9773</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
