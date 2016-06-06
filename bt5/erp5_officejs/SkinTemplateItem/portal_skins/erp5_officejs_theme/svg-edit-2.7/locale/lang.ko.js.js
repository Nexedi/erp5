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
            <value> <string>lang.ko.js</string> </value>
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
\tlang: "ko",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "저장",\n
\t\t"cancel": "취소",\n
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
\t\t"palette_info": "색상을 클릭, 근무 시간 채우기 스트로크 색상을 변경하려면 변경하려면",\n
\t\t"zoom_level": "변경 수준으로 확대",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identify the element",\n
\t\t"fill_color": "채우기 색상 변경",\n
\t\t"stroke_color": "뇌졸중으로 색상 변경",\n
\t\t"stroke_style": "뇌졸중 변경 대시 스타일",\n
\t\t"stroke_width": "뇌졸중 너비 변경",\n
\t\t"pos_x": "Change X coordinate",\n
\t\t"pos_y": "Change Y coordinate",\n
\t\t"linecap_butt": "Linecap: Butt",\n
\t\t"linecap_round": "Linecap: Round",\n
\t\t"linecap_square": "Linecap: Square",\n
\t\t"linejoin_bevel": "Linejoin: Bevel",\n
\t\t"linejoin_miter": "Linejoin: Miter",\n
\t\t"linejoin_round": "Linejoin: Round",\n
\t\t"angle": "회전 각도를 변경",\n
\t\t"blur": "Change gaussian blur value",\n
\t\t"opacity": "변경 항목을 선택 불투명도",\n
\t\t"circle_cx": "변경 동그라미 CX는 좌표",\n
\t\t"circle_cy": "동그라미 싸이 변경 조정할 수있어",\n
\t\t"circle_r": "변경 원의 반지름",\n
\t\t"ellipse_cx": "CX는 타원의 좌표 변경",\n
\t\t"ellipse_cy": "싸이 타원 변경 조정할 수있어",\n
\t\t"ellipse_rx": "변경 타원의 x 반지름",\n
\t\t"ellipse_ry": "변경 타원의 y를 반경",\n
\t\t"line_x1": "변경 라인의 X 좌표 시작",\n
\t\t"line_x2": "변경 라인의 X 좌표 결말",\n
\t\t"line_y1": "라인 변경 y를 시작 좌표",\n
\t\t"line_y2": "라인 변경 y를 결말의 좌표",\n
\t\t"rect_height": "사각형의 높이를 변경",\n
\t\t"rect_width": "사각형의 너비 변경",\n
\t\t"corner_radius": "변경 직사각형 코너 반경",\n
\t\t"image_width": "이미지 변경 폭",\n
\t\t"image_height": "이미지 높이 변경",\n
\t\t"image_url": "URL 변경",\n
\t\t"node_x": "Change node\'s x coordinate",\n
\t\t"node_y": "Change node\'s y coordinate",\n
\t\t"seg_type": "Change Segment type",\n
\t\t"straight_segments": "Straight",\n
\t\t"curve_segments": "Curve",\n
\t\t"text_contents": "텍스트 변경 내용",\n
\t\t"font_family": "글꼴 변경 패밀리",\n
\t\t"font_size": "글꼴 크기 변경",\n
\t\t"bold": "굵은 텍스트",\n
\t\t"italic": "기울임꼴 텍스트"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Main Menu",\n
\t\t"bkgnd_color_opac": "배경 색상 변경 / 투명도",\n
\t\t"connector_no_arrow": "No arrow",\n
\t\t"fitToContent": "맞춤 콘텐츠",\n
\t\t"fit_to_all": "맞춤 모든 콘텐츠에",\n
\t\t"fit_to_canvas": "맞춤 캔버스",\n
\t\t"fit_to_layer_content": "레이어에 맞게 콘텐츠",\n
\t\t"fit_to_sel": "맞춤 선택",\n
\t\t"align_relative_to": "정렬 상대적으로 ...",\n
\t\t"relativeTo": "상대:",\n
\t\t"페이지": "페이지",\n
\t\t"largest_object": "큰 개체",\n
\t\t"selected_objects": "당선 개체",\n
\t\t"smallest_object": "작은 개체",\n
\t\t"new_doc": "새 이미지",\n
\t\t"open_doc": "오픈 이미지",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "이미지 저장",\n
\t\t"import_doc": "Import SVG",\n
\t\t"align_to_page": "Align Element to Page",\n
\t\t"align_bottom": "히프 정렬",\n
\t\t"align_center": "정렬 센터",\n
\t\t"align_left": "왼쪽 정렬",\n
\t\t"align_middle": "중간 정렬",\n
\t\t"align_right": "오른쪽 맞춤",\n
\t\t"align_top": "정렬 탑",\n
\t\t"mode_select": "선택 도구",\n
\t\t"mode_fhpath": "연필 도구",\n
\t\t"mode_line": "선 도구",\n
\t\t"mode_connect": "Connect two objects",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "자유 핸드 직사각형",\n
\t\t"mode_ellipse": "타원",\n
\t\t"mode_circle": "동그라미",\n
\t\t"mode_fhellipse": "자유 핸드 타원",\n
\t\t"mode_path": "Path Tool",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "텍스트 도구",\n
\t\t"mode_image": "이미지 도구",\n
\t\t"mode_zoom": "줌 도구",\n
\t\t"mode_eyedropper": "Eye Dropper Tool",\n
\t\t"no_embed": "NOTE: This image cannot be embedded. It will depend on this path to be displayed",\n
\t\t"undo": "취소",\n
\t\t"redo": "재실행",\n
\t\t"tool_source": "수정 소스",\n
\t\t"wireframe_mode": "Wireframe Mode",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "그룹 요소",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "Convert to Path",\n
\t\t"reorient_path": "Reorient path",\n
\t\t"ungroup": "그룹 해제 요소",\n
\t\t"docprops": "문서 속성",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "아래로 이동",\n
\t\t"move_top": "상단으로 이동",\n
\t\t"node_clone": "Clone Node",\n
\t\t"node_delete": "Delete Node",\n
\t\t"node_link": "Link Control Points",\n
\t\t"add_subpath": "Add sub-path",\n
\t\t"openclose_path": "Open/close sub-path",\n
\t\t"source_save": "저장",\n
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
\t\t"del": "레이어 삭제",\n
\t\t"move_down": "레이어 아래로 이동",\n
\t\t"new": "새 레이어",\n
\t\t"rename": "레이어 이름 바꾸기",\n
\t\t"move_up": "레이어 위로 이동",\n
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
\t\t"select_predefined": "미리 정의된 선택:",\n
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
            <value> <int>9443</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
