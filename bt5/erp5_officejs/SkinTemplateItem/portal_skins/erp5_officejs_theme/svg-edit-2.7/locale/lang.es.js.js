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
            <value> <string>ts40515059.53</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>lang.es.js</string> </value>
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
\tlang: "es",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "OK",\n
\t\t"cancel": "Cancelar",\n
\t\t"key_backspace": "retroceso", \n
\t\t"key_del": "suprimir", \n
\t\t"key_down": "abajo", \n
\t\t"key_up": "arriba", \n
\t\t"more_opts": "More Options",\n
\t\t"url": "URL",\n
\t\t"width": "Width",\n
\t\t"height": "Height"\n
\t},\n
\tmisc: {\n
\t\t"powered_by": "Powered by"\n
\t}, \n
\tui: {\n
\t\t"toggle_stroke_tools": "Mostrar/ocultar herramientas de trazo adicionales",\n
\t\t"palette_info": "Haga clic para cambiar el color de relleno. Pulse Mayús y haga clic para cambiar el color del contorno.",\n
\t\t"zoom_level": "Cambiar el nivel de zoom",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identify the element",\n
\t\t"fill_color": "Cambiar el color de relleno",\n
\t\t"stroke_color": "Cambiar el color del contorno",\n
\t\t"stroke_style": "Cambiar el estilo del trazo del contorno",\n
\t\t"stroke_width": "Cambiar el grosor del contorno",\n
\t\t"pos_x": "Cambiar la posición horizontal X",\n
\t\t"pos_y": "Cambiar la posición vertical Y",\n
\t\t"linecap_butt": "Final de la línea: en el nodo",\n
\t\t"linecap_round": "Final de la línea: redondeada",\n
\t\t"linecap_square": "Final de la línea: cuadrada",\n
\t\t"linejoin_bevel": "Unión: biselada",\n
\t\t"linejoin_miter": "Unión: recta",\n
\t\t"linejoin_round": "Unión: redondeada",\n
\t\t"angle": "Cambiar ángulo de rotación",\n
\t\t"blur": "Ajustar desenfoque gausiano",\n
\t\t"opacity": "Cambiar la opacidad del objeto seleccionado",\n
\t\t"circle_cx": "Cambiar la posición horizonral CX del círculo",\n
\t\t"circle_cy": "Cambiar la posición vertical CY del círculo",\n
\t\t"circle_r": "Cambiar el radio del círculo",\n
\t\t"ellipse_cx": "Cambiar la posición horizontal CX de la elipse",\n
\t\t"ellipse_cy": "Cambiar la posición vertical CY de la elipse",\n
\t\t"ellipse_rx": "Cambiar el radio horizontal X de la elipse",\n
\t\t"ellipse_ry": "Cambiar el radio vertical Y de la elipse",\n
\t\t"line_x1": "Cambiar la posición horizontal X del comienzo de la línea",\n
\t\t"line_x2": "Cambiar la posición horizontal X del final de la línea",\n
\t\t"line_y1": "Cambiar la posición vertical Y del comienzo de la línea",\n
\t\t"line_y2": "Cambiar la posición vertical Y del final de la línea",\n
\t\t"rect_height": "Cambiar la altura del rectángulo",\n
\t\t"rect_width": "Cambiar el ancho rectángulo",\n
\t\t"corner_radius": "Cambiar el radio de las esquinas del rectángulo",\n
\t\t"image_width": "Cambiar el ancho de la imagen",\n
\t\t"image_height": "Cambiar la altura de la imagen",\n
\t\t"image_url": "Modificar URL",\n
\t\t"node_x": "Cambiar la posición horizontal X del nodo",\n
\t\t"node_y": "Cambiar la posición vertical Y del nodo",\n
\t\t"seg_type": "Cambiar el tipo de segmento",\n
\t\t"straight_segments": "Recta",\n
\t\t"curve_segments": "Curva",\n
\t\t"text_contents": "Modificar el texto",\n
\t\t"font_family": "Tipo de fuente",\n
\t\t"font_size": "Tamaño de la fuente",\n
\t\t"bold": "Texto en negrita",\n
\t\t"italic": "Texto en cursiva"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Menú principal",\n
\t\t"bkgnd_color_opac": "Cambiar color de fondo / opacidad",\n
\t\t"connector_no_arrow": "Sin flecha",\n
\t\t"fitToContent": "Ajustar al contenido",\n
\t\t"fit_to_all": "Ajustar a todo el contenido",\n
\t\t"fit_to_canvas": "Ajustar al lienzo",\n
\t\t"fit_to_layer_content": "Ajustar al contenido de la capa",\n
\t\t"fit_to_sel": "Ajustar a la selección",\n
\t\t"align_relative_to": "Alinear con respecto a ...",\n
\t\t"relativeTo": "en relación con:",\n
\t\t"Página": "Página",\n
\t\t"largest_object": "El objeto más grande",\n
\t\t"selected_objects": "Objetos seleccionados",\n
\t\t"smallest_object": "El objeto más pequeño",\n
\t\t"new_doc": "Nueva imagen",\n
\t\t"open_doc": "Abrir imagen",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "Guardar imagen",\n
\t\t"import_doc": "Importar un archivo SVG",\n
\t\t"align_to_page": "Align Element to Page",\n
\t\t"align_bottom": "Alinear parte inferior",\n
\t\t"align_center": "Centrar verticalmente",\n
\t\t"align_left": "Alinear lado izquierdo",\n
\t\t"align_middle": "Centrar horizontalmente",\n
\t\t"align_right": "Alinear lado derecho",\n
\t\t"align_top": "Alinear parte superior",\n
\t\t"mode_select": "Herramienta de selección",\n
\t\t"mode_fhpath": "Herramienta de lápiz",\n
\t\t"mode_line": "Trazado de líneas",\n
\t\t"mode_connect": "Conectar dos objetos",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "Rectángulo a mano alzada",\n
\t\t"mode_ellipse": "Elipse",\n
\t\t"mode_circle": "Círculo",\n
\t\t"mode_fhellipse": "Elipse a mano alzada",\n
\t\t"mode_path": "Herramienta de trazado",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "Insertar texto",\n
\t\t"mode_image": "Insertar imagen",\n
\t\t"mode_zoom": "Zoom",\n
\t\t"mode_eyedropper": "Herramienta de pipeta",\n
\t\t"no_embed": "NOTA: La imagen no puede ser integrada. El contenido mostrado dependerá de la imagen ubicada en esta ruta. ",\n
\t\t"undo": "Deshacer",\n
\t\t"redo": "Rehacer",\n
\t\t"tool_source": "Editar código fuente",\n
\t\t"wireframe_mode": "Modo marco de alambre",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "Agrupar objetos",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "Convertir a trazado",\n
\t\t"reorient_path": "Reorientar el trazado",\n
\t\t"ungroup": "Desagrupar objetos",\n
\t\t"docprops": "Propiedades del documento",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "Mover abajo",\n
\t\t"move_top": "Mover arriba",\n
\t\t"node_clone": "Clonar nodo",\n
\t\t"node_delete": "Suprimir nodo",\n
\t\t"node_link": "Enlazar puntos de control",\n
\t\t"add_subpath": "Añadir subtrazado",\n
\t\t"openclose_path": "Open/close sub-path",\n
\t\t"source_save": "Aplicar cambios",\n
\t\t"cut": "Cut",\n
\t\t"copy": "Copy",\n
\t\t"paste": "Paste",\n
\t\t"paste_in_place": "Paste in Place",\n
\t\t"suprimir": "Delete",\n
\t\t"group": "Group",\n
\t\t"move_front": "Bring to Front",\n
\t\t"move_up": "Bring Forward",\n
\t\t"move_down": "Send Backward",\n
\t\t"move_back": "Send to Back"\n
\t},\n
\tlayers: {\n
\t\t"layer":"Capa",\n
\t\t"layers": "Layers",\n
\t\t"del": "Suprimir capa",\n
\t\t"move_down": "Mover la capa hacia abajo",\n
\t\t"new": "Nueva capa",\n
\t\t"rename": "Renombrar capa",\n
\t\t"move_up": "Mover la capa hacia arriba",\n
\t\t"dupe": "Duplicate Layer",\n
\t\t"merge_down": "Merge Down",\n
\t\t"merge_all": "Merge All",\n
\t\t"move_elems_to": "Desplazar objetos a:",\n
\t\t"move_selected": "Mover los objetos seleccionados a otra capa"\n
\t},\n
\tconfig: {\n
\t\t"image_props": "Propiedades de la Imagen",\n
\t\t"doc_title": "Título",\n
\t\t"doc_dims": "Tamaño del lienzo",\n
\t\t"included_images": "Imágenes integradas",\n
\t\t"image_opt_embed": "Integrar imágenes en forma de datos (archivos locales)",\n
\t\t"image_opt_ref": "Usar la referencia del archivo",\n
\t\t"editor_prefs": "Preferencias del Editor",\n
\t\t"icon_size": "Tamaño de los iconos",\n
\t\t"language": "Idioma",\n
\t\t"background": "Fondo del editor",\n
\t\t"editor_img_url": "Image URL",\n
\t\t"editor_bg_note": "Nota: El fondo no se guardará junto con la imagen.",\n
\t\t"icon_large": "Grande",\n
\t\t"icon_medium": "Mediano",\n
\t\t"icon_small": "Pequeño",\n
\t\t"icon_xlarge": "Muy grande",\n
\t\t"select_predefined": "Seleccionar predefinido:",\n
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
\t\t"invalidAttrValGiven":"Valor no válido",\n
\t\t"noContentToFitTo":"No existe un contenido al que ajustarse.",\n
\t\t"dupeLayerName":"¡Ya existe una capa con este nombre!",\n
\t\t"enterUniqueLayerName":"Introduzca otro nombre distinto para la capa.",\n
\t\t"enterNewLayerName":"Introduzca el nuevo nombre de la capa.",\n
\t\t"layerHasThatName":"El nombre introducido es el nombre actual de la capa.",\n
\t\t"QmoveElemsToLayer":"¿Desplazar los elementos seleccionados a la capa \'%s\'?",\n
\t\t"QwantToClear":"¿Desea borrar el dibujo?\\n¡El historial de acciones también se borrará!",\n
\t\t"QwantToOpen":"Do you want to open a new file?\\nThis will also erase your undo history!",\n
\t\t"QerrorsRevertToSource":"Existen errores sintácticos en su código fuente SVG.\\n¿Desea volver al código fuente SVG original?",\n
\t\t"QignoreSourceChanges":"¿Desea ignorar los cambios realizados sobre el código fuente SVG?",\n
\t\t"featNotSupported":"Función no compatible.",\n
\t\t"enterNewImgURL":"Introduzca la nueva URL de la imagen.",\n
\t\t"defsFailOnSave": "NOTA: Debido a un fallo de su navegador, es posible que la imagen aparezca de forma incorrecta (ciertas gradaciones o elementos podría perderse). La imagen aparecerá en su forma correcta una vez guardada.",\n
\t\t"loadingImage":"Cargando imagen. Espere, por favor.",\n
\t\t"saveFromBrowser": "Seleccionar \\"Guardar como...\\" en su navegador para guardar la imagen en forma de archivo %s.",\n
\t\t"noteTheseIssues": "Existen además los problemas siguientes:",\n
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
            <value> <int>10351</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
