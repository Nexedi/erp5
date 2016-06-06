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
            <value> <string>lang.ja.js</string> </value>
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
\tlang: "ja",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "OK",\n
\t\t"cancel": "キャンセル",\n
\t\t"key_backspace": "backspace", \n
\t\t"key_del": "削除", \n
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
\t\t"palette_info": "クリックで塗りの色を選択、Shift+クリックで線の色を選択",\n
\t\t"zoom_level": "ズーム倍率の変更",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identify the element",\n
\t\t"fill_color": "塗りの色を変更",\n
\t\t"stroke_color": "線の色を変更",\n
\t\t"stroke_style": "線種の変更",\n
\t\t"stroke_width": "線幅の変更",\n
\t\t"pos_x": "X座標を変更",\n
\t\t"pos_y": "Y座標を変更",\n
\t\t"linecap_butt": "Linecap: Butt",\n
\t\t"linecap_round": "Linecap: Round",\n
\t\t"linecap_square": "Linecap: Square",\n
\t\t"linejoin_bevel": "Linejoin: Bevel",\n
\t\t"linejoin_miter": "Linejoin: Miter",\n
\t\t"linejoin_round": "Linejoin: Round",\n
\t\t"angle": "回転角の変更",\n
\t\t"blur": "Change gaussian blur value",\n
\t\t"opacity": "不透明度",\n
\t\t"circle_cx": "円の中心を変更（X座標）",\n
\t\t"circle_cy": "円の中心を変更（Y座標）",\n
\t\t"circle_r": "変更円の半径",\n
\t\t"ellipse_cx": "楕円の中心を変更（X座標）",\n
\t\t"ellipse_cy": "楕円の中心を変更（Y座標）",\n
\t\t"ellipse_rx": "楕円の半径を変更（X座標）",\n
\t\t"ellipse_ry": "楕円の半径を変更（Y座標）",\n
\t\t"line_x1": "開始X座標",\n
\t\t"line_x2": "終了X座標",\n
\t\t"line_y1": "開始Y座標",\n
\t\t"line_y2": "終了Y座標",\n
\t\t"rect_height": "長方形の高さを変更",\n
\t\t"rect_width": "長方形の幅を変更",\n
\t\t"corner_radius": "長方形の角の半径を変更",\n
\t\t"image_width": "画像の幅を変更",\n
\t\t"image_height": "画像の高さを変更",\n
\t\t"image_url": "URLを変更",\n
\t\t"node_x": "ノードのX座標を変更",\n
\t\t"node_y": "ノードのY座標を変更",\n
\t\t"seg_type": "線分の種類を変更",\n
\t\t"straight_segments": "直線",\n
\t\t"curve_segments": "カーブ",\n
\t\t"text_contents": "テキストの内容の変更",\n
\t\t"font_family": "フォントファミリーの変更",\n
\t\t"font_size": "文字サイズの変更",\n
\t\t"bold": "太字",\n
\t\t"italic": "イタリック体"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Main Menu",\n
\t\t"bkgnd_color_opac": "背景色/不透明度の変更",\n
\t\t"connector_no_arrow": "No arrow",\n
\t\t"fitToContent": "コンテンツに合わせる",\n
\t\t"fit_to_all": "すべてのコンテンツに合わせる",\n
\t\t"fit_to_canvas": "キャンバスに合わせる",\n
\t\t"fit_to_layer_content": "レイヤー上のコンテンツに合わせる",\n
\t\t"fit_to_sel": "選択対象に合わせる",\n
\t\t"align_relative_to": "揃える",\n
\t\t"relativeTo": "相対:",\n
\t\t"ページ": "ページ",\n
\t\t"largest_object": "最大のオブジェクト",\n
\t\t"selected_objects": "選択オブジェクト",\n
\t\t"smallest_object": "最小のオブジェクト",\n
\t\t"new_doc": "新規イメージ",\n
\t\t"open_doc": "イメージを開く",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "画像を保存",\n
\t\t"import_doc": "Import SVG",\n
\t\t"align_to_page": "Align Element to Page",\n
\t\t"align_bottom": "下揃え",\n
\t\t"align_center": "中央揃え",\n
\t\t"align_left": "左揃え",\n
\t\t"align_middle": "中央揃え",\n
\t\t"align_right": "右揃え",\n
\t\t"align_top": "上揃え",\n
\t\t"mode_select": "選択ツール",\n
\t\t"mode_fhpath": "鉛筆ツール",\n
\t\t"mode_line": "直線ツール",\n
\t\t"mode_connect": "Connect two objects",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "フリーハンド長方形",\n
\t\t"mode_ellipse": "楕円",\n
\t\t"mode_circle": "円",\n
\t\t"mode_fhellipse": "フリーハンド楕円",\n
\t\t"mode_path": "パスツール",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "テキストツール",\n
\t\t"mode_image": "イメージツール",\n
\t\t"mode_zoom": "ズームツール",\n
\t\t"mode_eyedropper": "Eye Dropper Tool",\n
\t\t"no_embed": "NOTE: This image cannot be embedded. It will depend on this path to be displayed",\n
\t\t"undo": "元に戻す",\n
\t\t"redo": "やり直し",\n
\t\t"tool_source": "ソースの編集",\n
\t\t"wireframe_mode": "ワイヤーフレームで表示 [F]",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "グループ化",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "パスに変換",\n
\t\t"reorient_path": "現在の角度を０度とする",\n
\t\t"ungroup": "グループ化を解除",\n
\t\t"docprops": "文書のプロパティ",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "奥に移動",\n
\t\t"move_top": "手前に移動",\n
\t\t"node_clone": "ノードを複製",\n
\t\t"node_delete": "ノードを削除",\n
\t\t"node_link": "制御点の接続",\n
\t\t"add_subpath": "Add sub-path",\n
\t\t"openclose_path": "Open/close sub-path",\n
\t\t"source_save": "適用",\n
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
\t\t"layer":"レイヤ",\n
\t\t"layers": "Layers",\n
\t\t"del": "レイヤの削除",\n
\t\t"move_down": "レイヤを下へ移動",\n
\t\t"new": "新規レイヤ",\n
\t\t"rename": "レイヤの名前を変更",\n
\t\t"move_up": "レイヤを上へ移動",\n
\t\t"dupe": "Duplicate Layer",\n
\t\t"merge_down": "Merge Down",\n
\t\t"merge_all": "Merge All",\n
\t\t"move_elems_to": "移動先レイヤ:",\n
\t\t"move_selected": "選択対象を別のレイヤに移動"\n
\t},\n
\tconfig: {\n
\t\t"image_props": "イメージの設定",\n
\t\t"doc_title": "タイトル",\n
\t\t"doc_dims": "キャンバスの大きさ",\n
\t\t"included_images": "挿入された画像の扱い",\n
\t\t"image_opt_embed": "SVGファイルに埋め込む",\n
\t\t"image_opt_ref": "画像を参照する",\n
\t\t"editor_prefs": "エディタの設定",\n
\t\t"icon_size": "アイコンの大きさ",\n
\t\t"language": "言語",\n
\t\t"background": "エディタの背景色",\n
\t\t"editor_img_url": "Image URL",\n
\t\t"editor_bg_note": "※背景色はファイルに保存されません。",\n
\t\t"icon_large": "Large",\n
\t\t"icon_medium": "Medium",\n
\t\t"icon_small": "Small",\n
\t\t"icon_xlarge": "Extra Large",\n
\t\t"select_predefined": "デフォルト",\n
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
\t\t"invalidAttrValGiven":"無効な値が指定されています。",\n
\t\t"noContentToFitTo":"合わせる対象のコンテンツがありません。",\n
\t\t"dupeLayerName":"同名のレイヤーが既に存在します。",\n
\t\t"enterUniqueLayerName":"新規レイヤの一意な名前を入力してください。",\n
\t\t"enterNewLayerName":"レイヤの新しい名前を入力してください。",\n
\t\t"layerHasThatName":"既に同名が付いています。",\n
\t\t"QmoveElemsToLayer":"選択した要素をレイヤー \'%s\' に移動しますか？",\n
\t\t"QwantToClear":"キャンバスをクリアしますか？\\nアンドゥ履歴も消去されます。",\n
\t\t"QwantToOpen":"新しいファイルを開きますか?\\nアンドゥ履歴も消去されます。",\n
\t\t"QerrorsRevertToSource":"ソースにエラーがあります。\\n元のソースに戻しますか？",\n
\t\t"QignoreSourceChanges":"ソースの変更を無視しますか？",\n
\t\t"featNotSupported":"機能はサポートされていません。",\n
\t\t"enterNewImgURL":"画像のURLを入力してください。",\n
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
            <value> <int>9813</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
