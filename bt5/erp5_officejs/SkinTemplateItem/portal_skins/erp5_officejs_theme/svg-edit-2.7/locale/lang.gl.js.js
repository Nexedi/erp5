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
            <value> <string>lang.gl.js</string> </value>
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
\tlang: "gl",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "Gardar",\n
\t\t"cancel": "Cancelar",\n
\t\t"key_backspace": "backspace", \n
\t\t"key_del": "delete", \n
\t\t"key_down": "down", \n
\t\t"key_up": "up", \n
\t\t"more_opts": "More Options",\n
\t\t"url": "URL",\n
\t\t"width": "Width",\n
\t\t"height": "Height"\n
\t},\n
\tmisc: {\n
\t\t"powered_by": "Powered by"\n
\t}, \n
\tui: {\n
\t\t"toggle_stroke_tools": "Show/hide more stroke tools",\n
\t\t"palette_info": "Preme aquí para cambiar a cor de recheo, Shift-clic para cambiar a cor do curso",\n
\t\t"zoom_level": "Cambiar o nivel de zoom",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identify the element",\n
\t\t"fill_color": "Cambia-la cor de recheo",\n
\t\t"stroke_color": "Cambiar a cor do curso",\n
\t\t"stroke_style": "Modifica o estilo do trazo do curso",\n
\t\t"stroke_width": "Cambiar o ancho do curso",\n
\t\t"pos_x": "Change X coordinate",\n
\t\t"pos_y": "Change Y coordinate",\n
\t\t"linecap_butt": "Linecap: Butt",\n
\t\t"linecap_round": "Linecap: Round",\n
\t\t"linecap_square": "Linecap: Square",\n
\t\t"linejoin_bevel": "Linejoin: Bevel",\n
\t\t"linejoin_miter": "Linejoin: Miter",\n
\t\t"linejoin_round": "Linejoin: Round",\n
\t\t"angle": "Cambiar o ángulo de xiro",\n
\t\t"blur": "Change gaussian blur value",\n
\t\t"opacity": "Cambia a opacidade elemento seleccionado",\n
\t\t"circle_cx": "Cx Cambiar círculo de coordenadas",\n
\t\t"circle_cy": "Círculo Cambio cy coordinar",\n
\t\t"circle_r": "Cambiar círculo de raio",\n
\t\t"ellipse_cx": "Cambiar elipse cx coordinar",\n
\t\t"ellipse_cy": "Elipse Cambio cy coordinar",\n
\t\t"ellipse_rx": "Raios X Change elipse",\n
\t\t"ellipse_ry": "Radio y Change elipse",\n
\t\t"line_x1": "Cambie a liña de partida coordenada x",\n
\t\t"line_x2": "Cambie a liña acaba coordenada x",\n
\t\t"line_y1": "Cambio na liña do recurso coordinada y",\n
\t\t"line_y2": "Salto de liña acaba coordinada y",\n
\t\t"rect_height": "Cambiar altura do rectángulo",\n
\t\t"rect_width": "Cambiar a largo rectángulo",\n
\t\t"corner_radius": "Cambiar Corner Rectangle Radius",\n
\t\t"image_width": "Cambiar o ancho da imaxe",\n
\t\t"image_height": "Cambiar altura da imaxe",\n
\t\t"image_url": "Cambiar URL",\n
\t\t"node_x": "Change node\'s x coordinate",\n
\t\t"node_y": "Change node\'s y coordinate",\n
\t\t"seg_type": "Change Segment type",\n
\t\t"straight_segments": "Straight",\n
\t\t"curve_segments": "Curve",\n
\t\t"text_contents": "Cambiar o contido de texto",\n
\t\t"font_family": "Cambiar fonte Familia",\n
\t\t"font_size": "Mudar tamaño de letra",\n
\t\t"bold": "Bold Text",\n
\t\t"italic": "Texto en cursiva"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Main Menu",\n
\t\t"bkgnd_color_opac": "Mudar a cor de fondo / Opacidade",\n
\t\t"connector_no_arrow": "No arrow",\n
\t\t"fitToContent": "Axustar ó contido",\n
\t\t"fit_to_all": "Axustar a todo o contido",\n
\t\t"fit_to_canvas": "Axustar a pantalla",\n
\t\t"fit_to_layer_content": "Axustar o contido da capa de",\n
\t\t"fit_to_sel": "Axustar a selección",\n
\t\t"align_relative_to": "Aliñar en relación a ...",\n
\t\t"relativeTo": "en relación ao:",\n
\t\t"Portada": "Portada",\n
\t\t"largest_object": "maior obxecto",\n
\t\t"selected_objects": "obxectos elixidos",\n
\t\t"smallest_object": "menor obxecto",\n
\t\t"new_doc": "Nova Imaxe",\n
\t\t"open_doc": "Abrir Imaxe",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "Gardar Imaxe",\n
\t\t"import_doc": "Import SVG",\n
\t\t"align_to_page": "Align Element to Page",\n
\t\t"align_bottom": "Align bottom",\n
\t\t"align_center": "Centrar",\n
\t\t"align_left": "Aliñar á Esquerda",\n
\t\t"align_middle": "Aliñar Medio",\n
\t\t"align_right": "Aliñar á Dereita",\n
\t\t"align_top": "Align Top",\n
\t\t"mode_select": "Seleccionar a ferramenta",\n
\t\t"mode_fhpath": "Ferramenta Lapis",\n
\t\t"mode_line": "Ferramenta Liña",\n
\t\t"mode_connect": "Connect two objects",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "Free-Hand Rectangle",\n
\t\t"mode_ellipse": "Elipse",\n
\t\t"mode_circle": "Circle",\n
\t\t"mode_fhellipse": "Free-Hand Ellipse",\n
\t\t"mode_path": "Path Tool",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "Ferramenta de Texto",\n
\t\t"mode_image": "Image Tool",\n
\t\t"mode_zoom": "Zoom Tool",\n
\t\t"mode_eyedropper": "Eye Dropper Tool",\n
\t\t"no_embed": "NOTE: This image cannot be embedded. It will depend on this path to be displayed",\n
\t\t"undo": "Desfacer",\n
\t\t"redo": "Volver",\n
\t\t"tool_source": "Fonte Editar",\n
\t\t"wireframe_mode": "Wireframe Mode",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "Elementos do grupo",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "Convert to Path",\n
\t\t"reorient_path": "Reorient path",\n
\t\t"ungroup": "Elementos Desagrupadas",\n
\t\t"docprops": "Propriedades do Documento",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "Move a Bottom",\n
\t\t"move_top": "Move to Top",\n
\t\t"node_clone": "Clone Node",\n
\t\t"node_delete": "Delete Node",\n
\t\t"node_link": "Link Control Points",\n
\t\t"add_subpath": "Add sub-path",\n
\t\t"openclose_path": "Open/close sub-path",\n
\t\t"source_save": "Gardar",\n
\t\t"cut": "Cut",\n
\t\t"copy": "Copy",\n
\t\t"paste": "Paste",\n
\t\t"paste_in_place": "Paste in Place",\n
\t\t"delete": "Delete",\n
\t\t"group": "Group",\n
\t\t"move_front": "Bring to Front",\n
\t\t"move_up": "Bring Forward",\n
\t\t"move_down": "Send Backward",\n
\t\t"move_back": "Send to Back"\n
\t},\n
\tlayers: {\n
\t\t"layer":"Layer",\n
\t\t"layers": "Layers",\n
\t\t"del": "Delete Layer",\n
\t\t"move_down": "Move capa inferior",\n
\t\t"new": "New Layer",\n
\t\t"rename": "Rename Layer",\n
\t\t"move_up": "Move Layer Up",\n
\t\t"dupe": "Duplicate Layer",\n
\t\t"merge_down": "Merge Down",\n
\t\t"merge_all": "Merge All",\n
\t\t"move_elems_to": "Move elements to:",\n
\t\t"move_selected": "Move selected elements to a different layer"\n
\t},\n
\tconfig: {\n
\t\t"image_props": "Image Properties",\n
\t\t"doc_title": "Title",\n
\t\t"doc_dims": "Canvas Dimensions",\n
\t\t"included_images": "Included Images",\n
\t\t"image_opt_embed": "Embed data (local files)",\n
\t\t"image_opt_ref": "Use file reference",\n
\t\t"editor_prefs": "Editor Preferences",\n
\t\t"icon_size": "Icon size",\n
\t\t"language": "Language",\n
\t\t"background": "Editor Background",\n
\t\t"editor_img_url": "Image URL",\n
\t\t"editor_bg_note": "Note: Background will not be saved with image.",\n
\t\t"icon_large": "Large",\n
\t\t"icon_medium": "Medium",\n
\t\t"icon_small": "Small",\n
\t\t"icon_xlarge": "Extra Large",\n
\t\t"select_predefined": "Seleccione por defecto:",\n
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
\t\t"invalidAttrValGiven":"Invalid value given",\n
\t\t"noContentToFitTo":"No content to fit to",\n
\t\t"dupeLayerName":"There is already a layer named that!",\n
\t\t"enterUniqueLayerName":"Please enter a unique layer name",\n
\t\t"enterNewLayerName":"Please enter the new layer name",\n
\t\t"layerHasThatName":"Layer already has that name",\n
\t\t"QmoveElemsToLayer":"Move selected elements to layer \'%s\'?",\n
\t\t"QwantToClear":"Do you want to clear the drawing?\\nThis will also erase your undo history!",\n
\t\t"QwantToOpen":"Do you want to open a new file?\\nThis will also erase your undo history!",\n
\t\t"QerrorsRevertToSource":"There were parsing errors in your SVG source.\\nRevert back to original SVG source?",\n
\t\t"QignoreSourceChanges":"Ignore changes made to SVG source?",\n
\t\t"featNotSupported":"Feature not supported",\n
\t\t"enterNewImgURL":"Enter the new image URL",\n
\t\t"defsFailOnSave": "NOTE: Due to a bug in your browser, this image may appear wrong (missing gradients or elements). It will however appear correct once actually saved.",\n
\t\t"loadingImage":"Loading image, please wait...",\n
\t\t"saveFromBrowser": "Select \\"Save As...\\" in your browser to save this image as a %s file.",\n
\t\t"noteTheseIssues": "Also note the following issues: ",\n
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
            <value> <int>9362</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
