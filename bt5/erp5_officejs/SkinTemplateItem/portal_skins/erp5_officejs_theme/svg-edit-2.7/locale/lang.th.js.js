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
            <value> <string>lang.th.js</string> </value>
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
\tlang: "th",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "บันทึก",\n
\t\t"cancel": "ยกเลิก",\n
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
\t\t"palette_info": "คลิกเพื่อเปลี่ยนใส่สีกะคลิกเปลี่ยนสีจังหวะ",\n
\t\t"zoom_level": "เปลี่ยนระดับการซูม",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identify the element",\n
\t\t"fill_color": "เปลี่ยนใส่สี",\n
\t\t"stroke_color": "สีจังหวะเปลี่ยน",\n
\t\t"stroke_style": "รีบเปลี่ยนสไตล์จังหวะ",\n
\t\t"stroke_width": "ความกว้างจังหวะเปลี่ยน",\n
\t\t"pos_x": "Change X coordinate",\n
\t\t"pos_y": "Change Y coordinate",\n
\t\t"linecap_butt": "Linecap: Butt",\n
\t\t"linecap_round": "Linecap: Round",\n
\t\t"linecap_square": "Linecap: Square",\n
\t\t"linejoin_bevel": "Linejoin: Bevel",\n
\t\t"linejoin_miter": "Linejoin: Miter",\n
\t\t"linejoin_round": "Linejoin: Round",\n
\t\t"angle": "มุมหมุนเปลี่ยน",\n
\t\t"blur": "Change gaussian blur value",\n
\t\t"opacity": "เปลี่ยนความทึบเลือกรายการ",\n
\t\t"circle_cx": "Cx วงกลมเปลี่ยนของพิกัด",\n
\t\t"circle_cy": "วงกลมเปลี่ยนเป็น cy ประสานงาน",\n
\t\t"circle_r": "รัศมีวงกลมเปลี่ยนเป็น",\n
\t\t"ellipse_cx": "เปลี่ยน ellipse ของ cx ประสานงาน",\n
\t\t"ellipse_cy": "Ellipse เปลี่ยนของ cy ประสานงาน",\n
\t\t"ellipse_rx": "Ellipse เปลี่ยนของรัศมี x",\n
\t\t"ellipse_ry": "Ellipse เปลี่ยนของรัศมี y",\n
\t\t"line_x1": "สายเปลี่ยนเป็นเริ่มต้น x พิกัด",\n
\t\t"line_x2": "สายเปลี่ยนเป็นสิ้นสุด x พิกัด",\n
\t\t"line_y1": "สายเปลี่ยนเป็นเริ่มต้น y พิกัด",\n
\t\t"line_y2": "สายเปลี่ยนเป็นสิ้นสุด y พิกัด",\n
\t\t"rect_height": "ความสูงสี่เหลี่ยมผืนผ้าเปลี่ยน",\n
\t\t"rect_width": "ความกว้างสี่เหลี่ยมผืนผ้าเปลี่ยน",\n
\t\t"corner_radius": "รัศมีเปลี่ยนสี่เหลี่ยมผืนผ้า Corner",\n
\t\t"image_width": "ความกว้างเปลี่ยนรูปภาพ",\n
\t\t"image_height": "ความสูงเปลี่ยนรูปภาพ",\n
\t\t"image_url": "URL เปลี่ยน",\n
\t\t"node_x": "Change node\'s x coordinate",\n
\t\t"node_y": "Change node\'s y coordinate",\n
\t\t"seg_type": "Change Segment type",\n
\t\t"straight_segments": "Straight",\n
\t\t"curve_segments": "Curve",\n
\t\t"text_contents": "เปลี่ยนเนื้อหาข้อความ",\n
\t\t"font_family": "ครอบครัว Change Font",\n
\t\t"font_size": "เปลี่ยนขนาดตัวอักษร",\n
\t\t"bold": "ข้อความตัวหนา",\n
\t\t"italic": "ข้อความตัวเอียง"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Main Menu",\n
\t\t"bkgnd_color_opac": "สีพื้นหลังเปลี่ยน / ความทึบ",\n
\t\t"connector_no_arrow": "No arrow",\n
\t\t"fitToContent": "Fit to Content",\n
\t\t"fit_to_all": "พอดีกับเนื้อหาทั้งหมด",\n
\t\t"fit_to_canvas": "เหมาะสมในการผ้าใบ",\n
\t\t"fit_to_layer_content": "พอดีเนื้อหาชั้นที่",\n
\t\t"fit_to_sel": "เหมาะสมในการเลือก",\n
\t\t"align_relative_to": "จัดชิดเทียบกับ ...",\n
\t\t"relativeTo": "เทียบกับ:",\n
\t\t"หน้า": "หน้า",\n
\t\t"largest_object": "ที่ใหญ่ที่สุดในวัตถุ",\n
\t\t"selected_objects": "วัตถุเลือกตั้ง",\n
\t\t"smallest_object": "วัตถุที่เล็กที่สุด",\n
\t\t"new_doc": "รูปภาพใหม่",\n
\t\t"open_doc": "ภาพเปิด",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "บันทึกรูปภาพ",\n
\t\t"import_doc": "Import SVG",\n
\t\t"align_to_page": "Align Element to Page",\n
\t\t"align_bottom": "ด้านล่างชิด",\n
\t\t"align_center": "จัดแนวกึ่งกลาง",\n
\t\t"align_left": "จัดชิดซ้าย",\n
\t\t"align_middle": "กลางชิด",\n
\t\t"align_right": "จัดชิดขวา",\n
\t\t"align_top": "ด้านบนชิด",\n
\t\t"mode_select": "เครื่องมือเลือก",\n
\t\t"mode_fhpath": "เครื่องมือดินสอ",\n
\t\t"mode_line": "เครื่องมือ Line",\n
\t\t"mode_connect": "Connect two objects",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "สี่เหลี่ยมผืนผ้า Free-Hand",\n
\t\t"mode_ellipse": "Ellipse",\n
\t\t"mode_circle": "Circle",\n
\t\t"mode_fhellipse": "Ellipse Free-Hand",\n
\t\t"mode_path": "Path Tool",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "เครื่องมือ Text",\n
\t\t"mode_image": "เครื่องมือ Image",\n
\t\t"mode_zoom": "เครื่องมือซูม",\n
\t\t"mode_eyedropper": "Eye Dropper Tool",\n
\t\t"no_embed": "NOTE: This image cannot be embedded. It will depend on this path to be displayed",\n
\t\t"undo": "เลิก",\n
\t\t"redo": "ทำซ้ำ",\n
\t\t"tool_source": "แหล่งที่มาแก้ไข",\n
\t\t"wireframe_mode": "Wireframe Mode",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "องค์ประกอบของกลุ่ม",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "Convert to Path",\n
\t\t"reorient_path": "Reorient path",\n
\t\t"ungroup": "องค์ประกอบ Ungroup",\n
\t\t"docprops": "คุณสมบัติของเอกสาร",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "ย้ายไปด้านล่าง",\n
\t\t"move_top": "ย้ายไปด้านบน",\n
\t\t"node_clone": "Clone Node",\n
\t\t"node_delete": "Delete Node",\n
\t\t"node_link": "Link Control Points",\n
\t\t"add_subpath": "Add sub-path",\n
\t\t"openclose_path": "Open/close sub-path",\n
\t\t"source_save": "บันทึก",\n
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
\t\t"move_down": "ย้าย Layer ลง",\n
\t\t"new": "Layer ใหม่",\n
\t\t"rename": "Layer เปลี่ยนชื่อ",\n
\t\t"move_up": "ย้าย Layer Up",\n
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
\t\t"select_predefined": "เลือกที่กำหนดไว้ล่วงหน้า:",\n
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
            <value> <int>11459</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
