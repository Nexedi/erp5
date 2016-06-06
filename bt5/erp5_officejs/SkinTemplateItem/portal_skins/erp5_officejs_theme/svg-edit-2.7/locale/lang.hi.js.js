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
            <value> <string>lang.hi.js</string> </value>
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
\tlang: "hi",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "बचाना",\n
\t\t"cancel": "रद्द करें",\n
\t\t"key_backspace": "बैकस्पेस", \n
\t\t"key_del": "हटायें", \n
\t\t"key_down": "नीचे", \n
\t\t"key_up": "ऊपर", \n
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
\t\t"palette_info": "रंग बदलने पर क्लिक करें, बदलाव भरने के क्लिक करने के लिए स्ट्रोक का रंग बदलने के लिए",\n
\t\t"zoom_level": "बदलें स्तर ज़ूम",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identify the element",\n
\t\t"fill_color": "बदलें का रंग भरना",\n
\t\t"stroke_color": "बदलें स्ट्रोक रंग",\n
\t\t"stroke_style": "बदलें स्ट्रोक डेश शैली",\n
\t\t"stroke_width": "बदलें स्ट्रोक चौड़ाई",\n
\t\t"pos_x": "X समकक्ष बदलें ",\n
\t\t"pos_y": "Y समकक्ष बदलें",\n
\t\t"linecap_butt": "Linecap: Butt",\n
\t\t"linecap_round": "Linecap: Round",\n
\t\t"linecap_square": "Linecap: Square",\n
\t\t"linejoin_bevel": "Linejoin: Bevel",\n
\t\t"linejoin_miter": "Linejoin: Miter",\n
\t\t"linejoin_round": "Linejoin: Round",\n
\t\t"angle": "बदलें रोटेशन कोण",\n
\t\t"blur": "Change gaussian blur value",\n
\t\t"opacity": "पारदर्शिता बदलें",\n
\t\t"circle_cx": "बदल रहा है चक्र cx समन्वय",\n
\t\t"circle_cy": "परिवर्तन चक्र cy समन्वय है",\n
\t\t"circle_r": "बदल रहा है चक्र त्रिज्या",\n
\t\t"ellipse_cx": "बदलें दीर्घवृत्त है cx समन्वय",\n
\t\t"ellipse_cy": "बदलें दीर्घवृत्त cy समन्वय है",\n
\t\t"ellipse_rx": "बदल रहा है दीर्घवृत्त x त्रिज्या",\n
\t\t"ellipse_ry": "बदल रहा है दीर्घवृत्त y त्रिज्या",\n
\t\t"line_x1": "बदल रहा है लाइन x समन्वय शुरू",\n
\t\t"line_x2": "बदल रहा है लाइन x समन्वय समाप्त",\n
\t\t"line_y1": "बदलें रेखा y शुरू हो रहा है समन्वय",\n
\t\t"line_y2": "बदलें रेखा y अंत है समन्वय",\n
\t\t"rect_height": "बदलें आयत ऊंचाई",\n
\t\t"rect_width": "बदलें आयत चौड़ाई",\n
\t\t"corner_radius": "बदलें आयत कॉर्नर त्रिज्या",\n
\t\t"image_width": "बदलें छवि चौड़ाई",\n
\t\t"image_height": "बदलें छवि ऊँचाई",\n
\t\t"image_url": "बदलें यूआरएल",\n
\t\t"node_x": "नोड का x समकक्ष बदलें",\n
\t\t"node_y": "नोड का y समकक्ष बदलें",\n
\t\t"seg_type": "वर्ग प्रकार बदलें",\n
\t\t"straight_segments": "सीधे वर्ग",\n
\t\t"curve_segments": "घुमाव",\n
\t\t"text_contents": "बदलें पाठ सामग्री",\n
\t\t"font_family": "बदलें फ़ॉन्ट परिवार",\n
\t\t"font_size": "फ़ॉन्ट का आकार बदलें",\n
\t\t"bold": "मोटा पाठ",\n
\t\t"italic": "इटैलिक पाठ"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Main Menu",\n
\t\t"bkgnd_color_opac": "पृष्ठभूमि का रंग बदल / अस्पष्टता",\n
\t\t"connector_no_arrow": "No arrow",\n
\t\t"fitToContent": "सामग्री के लिए फिट",\n
\t\t"fit_to_all": "सभी सामग्री के लिए फिट",\n
\t\t"fit_to_canvas": "फिट कैनवास को",\n
\t\t"fit_to_layer_content": "फिट परत सामग्री के लिए",\n
\t\t"fit_to_sel": "चयन के लिए फिट",\n
\t\t"align_relative_to": "संरेखित करें रिश्तेदार को ...",\n
\t\t"relativeTo": "रिश्तेदार को:",\n
\t\t"पृष्ठ": "पृष्ठ",\n
\t\t"largest_object": "सबसे बड़ी वस्तु",\n
\t\t"selected_objects": "निर्वाचित वस्तुओं",\n
\t\t"smallest_object": "छोटी से छोटी वस्तु",\n
\t\t"new_doc": "नई छवि",\n
\t\t"open_doc": "छवि खोलें",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "सहेजें छवि",\n
\t\t"import_doc": "Import SVG",\n
\t\t"align_to_page": "Align Element to Page",\n
\t\t"align_bottom": "तलमेंपंक्तिबद्धकरें",\n
\t\t"align_center": "मध्य में समंजित करें",\n
\t\t"align_left": " पंक्तिबद्ध करें",\n
\t\t"align_middle": "मध्य संरेखित करें",\n
\t\t"align_right": "दायाँपंक्तिबद्धकरें",\n
\t\t"align_top": "शीर्षमेंपंक्तिबद्धकरें",\n
\t\t"mode_select": "उपकरण चुनें",\n
\t\t"mode_fhpath": "पेंसिल उपकरण",\n
\t\t"mode_line": "लाइन उपकरण",\n
\t\t"mode_connect": "Connect two objects",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "नि: शुल्क हाथ आयत",\n
\t\t"mode_ellipse": "दीर्घवृत्त",\n
\t\t"mode_circle": "वृत्त",\n
\t\t"mode_fhellipse": "नि: शुल्क हाथ दीर्घवृत्त",\n
\t\t"mode_path": "Path Tool",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "पाठ उपकरण",\n
\t\t"mode_image": "छवि उपकरण",\n
\t\t"mode_zoom": "ज़ूम उपकरण",\n
\t\t"mode_eyedropper": "Eye Dropper Tool",\n
\t\t"no_embed": "NOTE: This image cannot be embedded. It will depend on this path to be displayed",\n
\t\t"undo": "पूर्ववत करें",\n
\t\t"redo": "फिर से करें",\n
\t\t"tool_source": "स्रोत में बदलाव करें",\n
\t\t"wireframe_mode": "रूपरेखा मोड",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "समूह तत्वों",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "पथ में बदलें",\n
\t\t"reorient_path": "पथ को नई दिशा दें",\n
\t\t"ungroup": "अंश को समूह से अलग करें",\n
\t\t"docprops": "दस्तावेज़ गुण",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "नीचे ले जाएँ",\n
\t\t"move_top": "ऊपर ले जाएँ",\n
\t\t"node_clone": "नोड क्लोन",\n
\t\t"node_delete": "नोड हटायें",\n
\t\t"node_link": "कड़ी नियंत्रण बिंदु",\n
\t\t"add_subpath": "Add sub-path",\n
\t\t"openclose_path": "Open/close sub-path",\n
\t\t"source_save": "बचाना",\n
\t\t"cut": "Cut",\n
\t\t"copy": "Copy",\n
\t\t"paste": "Paste",\n
\t\t"paste_in_place": "Paste in Place",\n
\t\t"हटायें": "Delete",\n
\t\t"group": "Group",\n
\t\t"move_front": "Bring to Front",\n
\t\t"move_up": "Bring Forward",\n
\t\t"move_down": "Send Backward",\n
\t\t"move_back": "Send to Back"\n
\t},\n
\tlayers: {\n
\t\t"layer":"परत",\n
\t\t"layers": "Layers",\n
\t\t"del": "परत हटाएँ",\n
\t\t"move_down": "परत नीचे ले जाएँ",\n
\t\t"new": "नई परत",\n
\t\t"rename": "परत का नाम बदलें",\n
\t\t"move_up": "परत ऊपर ले जाएँ",\n
\t\t"dupe": "Duplicate Layer",\n
\t\t"merge_down": "Merge Down",\n
\t\t"merge_all": "Merge All",\n
\t\t"move_elems_to": "अंश को ले जाएँ:",\n
\t\t"move_selected": "चयनित अंश को दूसरी परत पर  ले जाएँ"\n
\t},\n
\tconfig: {\n
\t\t"image_props": "छवि के गुण",\n
\t\t"doc_title": "शीर्षक",\n
\t\t"doc_dims": "कैनवास आयाम",\n
\t\t"included_images": "शामिल छवियाँ",\n
\t\t"image_opt_embed": "एम्बेड डेटा (स्थानीय फ़ाइलें)",\n
\t\t"image_opt_ref": "फाइल के संदर्भ का प्रयोग",\n
\t\t"editor_prefs": "संपादक वरीयताएँ",\n
\t\t"icon_size": "चिह्न का आकार",\n
\t\t"language": "भाषा",\n
\t\t"background": "संपादक पृष्ठभूमि",\n
\t\t"editor_img_url": "Image URL",\n
\t\t"editor_bg_note": "नोट: पृष्ठभूमि छवि के साथ नहीं बचायी जाएगी",\n
\t\t"icon_large": "बड़ा",\n
\t\t"icon_medium": "मध्यम",\n
\t\t"icon_small": "छोटा",\n
\t\t"icon_xlarge": "बहुत बड़ा",\n
\t\t"select_predefined": "चुनें पूर्वनिर्धारित:",\n
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
\t\t"invalidAttrValGiven":"अमान्य मूल्य",\n
\t\t"noContentToFitTo":"कोई सामग्री फिट करने के लिए उपलब्ध नहीं",\n
\t\t"dupeLayerName":"इस नाम कि परत पहले से मौजूद है !",\n
\t\t"enterUniqueLayerName":"कृपया परत का एक अद्वितीय नाम डालें",\n
\t\t"enterNewLayerName":"कृपया परत का एक नया नाम डालें",\n
\t\t"layerHasThatName":"परत का पहले से ही यही नाम है",\n
\t\t"QmoveElemsToLayer":"चयनित अंश को परत \'%s\' पर ले जाएँ ?",\n
\t\t"QwantToClear":"क्या आप छवि साफ़ करना चाहते हैं?\\nयह आपके उन्डू  इतिहास को भी मिटा देगा!",\n
\t\t"QwantToOpen":"Do you want to open a new file?\\nThis will also erase your undo history!",\n
\t\t"QerrorsRevertToSource":"आपके एस.वी.जी. स्रोत में त्रुटियों थी.\\nक्या आप मूल एस.वी.जी स्रोत पर वापिस जाना चाहते हैं?",\n
\t\t"QignoreSourceChanges":"एसवीजी स्रोत से लाये बदलावों को ध्यान न दें?",\n
\t\t"featNotSupported":"सुविधा असमर्थित है",\n
\t\t"enterNewImgURL":"नई छवि URL दर्ज करें",\n
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
            <value> <int>12992</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
