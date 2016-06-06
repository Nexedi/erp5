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
            <value> <string>lang.sv.js</string> </value>
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
\tlang: "sv",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "Spara",\n
\t\t"cancel": "Avbryt",\n
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
\t\t"palette_info": "Klicka för att ändra fyllningsfärg, shift-klicka för att ändra färgar",\n
\t\t"zoom_level": "Ändra zoomnivå",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identify the element",\n
\t\t"fill_color": "Ändra fyllningsfärg",\n
\t\t"stroke_color": "Ändra färgar",\n
\t\t"stroke_style": "Ändra stroke Dash stil",\n
\t\t"stroke_width": "Ändra stroke bredd",\n
\t\t"pos_x": "Change X coordinate",\n
\t\t"pos_y": "Change Y coordinate",\n
\t\t"linecap_butt": "Linecap: Butt",\n
\t\t"linecap_round": "Linecap: Round",\n
\t\t"linecap_square": "Linecap: Square",\n
\t\t"linejoin_bevel": "Linejoin: Bevel",\n
\t\t"linejoin_miter": "Linejoin: Miter",\n
\t\t"linejoin_round": "Linejoin: Round",\n
\t\t"angle": "Ändra rotationsvinkel",\n
\t\t"blur": "Change gaussian blur value",\n
\t\t"opacity": "Ändra markerat objekt opacitet",\n
\t\t"circle_cx": "Ändra cirkeln cx samordna",\n
\t\t"circle_cy": "Ändra cirkeln samordna cy",\n
\t\t"circle_r": "Ändra cirkelns radie",\n
\t\t"ellipse_cx": "Ändra ellips&#39;s cx samordna",\n
\t\t"ellipse_cy": "Ändra ellips&#39;s samordna cy",\n
\t\t"ellipse_rx": "Ändra ellips&#39;s x radie",\n
\t\t"ellipse_ry": "Ändra ellips&#39;s y radie",\n
\t\t"line_x1": "Ändra Lines startar x samordna",\n
\t\t"line_x2": "Ändra Lines slutar x samordna",\n
\t\t"line_y1": "Ändra Lines startar Y-koordinat",\n
\t\t"line_y2": "Ändra Lines slutar Y-koordinat",\n
\t\t"rect_height": "Ändra rektangel höjd",\n
\t\t"rect_width": "Ändra rektangel bredd",\n
\t\t"corner_radius": "Ändra rektangel hörnradie",\n
\t\t"image_width": "Ändra bild bredd",\n
\t\t"image_height": "Ändra bildhöjd",\n
\t\t"image_url": "Ändra URL",\n
\t\t"node_x": "Change node\'s x coordinate",\n
\t\t"node_y": "Change node\'s y coordinate",\n
\t\t"seg_type": "Change Segment type",\n
\t\t"straight_segments": "Straight",\n
\t\t"curve_segments": "Curve",\n
\t\t"text_contents": "Ändra textinnehållet",\n
\t\t"font_family": "Ändra Typsnitt",\n
\t\t"font_size": "Ändra textstorlek",\n
\t\t"bold": "Fet text",\n
\t\t"italic": "Kursiv text"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Main Menu",\n
\t\t"bkgnd_color_opac": "Ändra bakgrundsfärg / opacitet",\n
\t\t"connector_no_arrow": "No arrow",\n
\t\t"fitToContent": "Fit to Content",\n
\t\t"fit_to_all": "Passar till allt innehåll",\n
\t\t"fit_to_canvas": "Anpassa till duk",\n
\t\t"fit_to_layer_content": "Anpassa till lager innehåll",\n
\t\t"fit_to_sel": "Anpassa till val",\n
\t\t"align_relative_to": "Justera förhållande till ...",\n
\t\t"relativeTo": "jämfört:",\n
\t\t"sida": "sida",\n
\t\t"largest_object": "största objekt",\n
\t\t"selected_objects": "valda objekt",\n
\t\t"smallest_object": "minsta objektet",\n
\t\t"new_doc": "New Image",\n
\t\t"open_doc": "Öppna bild",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "Save Image",\n
\t\t"import_doc": "Import SVG",\n
\t\t"align_to_page": "Align Element to Page",\n
\t\t"align_bottom": "Align Bottom",\n
\t\t"align_center": "Centrera",\n
\t\t"align_left": "Vänsterjustera",\n
\t\t"align_middle": "Justera Middle",\n
\t\t"align_right": "Högerjustera",\n
\t\t"align_top": "Justera Top",\n
\t\t"mode_select": "Markeringsverktyget",\n
\t\t"mode_fhpath": "Pennverktyget",\n
\t\t"mode_line": "Linjeverktyg",\n
\t\t"mode_connect": "Connect two objects",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "Fri hand rektangel",\n
\t\t"mode_ellipse": "Ellips",\n
\t\t"mode_circle": "Circle",\n
\t\t"mode_fhellipse": "Fri hand Ellipse",\n
\t\t"mode_path": "Path Tool",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "Textverktyg",\n
\t\t"mode_image": "Bildverktyg",\n
\t\t"mode_zoom": "Zoomverktyget",\n
\t\t"mode_eyedropper": "Eye Dropper Tool",\n
\t\t"no_embed": "NOTE: This image cannot be embedded. It will depend on this path to be displayed",\n
\t\t"undo": "Ångra",\n
\t\t"redo": "Redo",\n
\t\t"tool_source": "Redigera källa",\n
\t\t"wireframe_mode": "Wireframe Mode",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "Group Elements",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "Convert to Path",\n
\t\t"reorient_path": "Reorient path",\n
\t\t"ungroup": "Dela Elements",\n
\t\t"docprops": "Dokumentegenskaper",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "Move to Bottom",\n
\t\t"move_top": "Flytta till början",\n
\t\t"node_clone": "Clone Node",\n
\t\t"node_delete": "Delete Node",\n
\t\t"node_link": "Link Control Points",\n
\t\t"add_subpath": "Add sub-path",\n
\t\t"openclose_path": "Open/close sub-path",\n
\t\t"source_save": "Spara",\n
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
\t\t"del": "Radera Layer",\n
\t\t"move_down": "Flytta Layer Down",\n
\t\t"new": "New Layer",\n
\t\t"rename": "Byt namn på Layer",\n
\t\t"move_up": "Flytta Layer Up",\n
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
\t\t"select_predefined": "Välj fördefinierad:",\n
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
            <value> <int>9196</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
