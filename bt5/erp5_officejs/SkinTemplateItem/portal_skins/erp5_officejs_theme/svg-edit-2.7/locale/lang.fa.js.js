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
            <value> <string>lang.fa.js</string> </value>
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
\tlang: "fa",\n
\tdir : "ltr",\n
\tcommon: {\n
\t\t"ok": "‫تأیید‬",\n
\t\t"cancel": "‫لغو‬",\n
\t\t"key_backspace": "‫پس بر ‬", \n
\t\t"key_del": "‫حذف ‬", \n
\t\t"key_down": "‫پایین ‬", \n
\t\t"key_up": "‫بالا ‬", \n
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
\t\t"palette_info": "‫برای تغییر رنگ، کلیک کنید. برای تغییر رنگ لبه، کلید تبدیل (shift) را فشرده و کلیک کنید‬",\n
\t\t"zoom_level": "‫تغییر بزرگ نمایی‬",\n
\t\t"panel_drag": "Drag left/right to resize side panel"\n
\t},\n
\tproperties: {\n
\t\t"id": "Identify the element",\n
\t\t"fill_color": "‫تغییر رنگ‬",\n
\t\t"stroke_color": "‫تغییر رنگ لبه‬",\n
\t\t"stroke_style": "‫تغییر نقطه چین لبه‬",\n
\t\t"stroke_width": "‫تغییر عرض لبه‬",\n
\t\t"pos_x": "‫تغییر مختصات X‬",\n
\t\t"pos_y": "‫تغییر مختصات Y‬",\n
\t\t"linecap_butt": "Linecap: Butt",\n
\t\t"linecap_round": "Linecap: Round",\n
\t\t"linecap_square": "Linecap: Square",\n
\t\t"linejoin_bevel": "Linejoin: Bevel",\n
\t\t"linejoin_miter": "Linejoin: Miter",\n
\t\t"linejoin_round": "Linejoin: Round",\n
\t\t"angle": "‫تغییر زاویه چرخش‬",\n
\t\t"blur": "Change gaussian blur value",\n
\t\t"opacity": "‫تغییر تاری عنصر انتخاب شده‬",\n
\t\t"circle_cx": "‫تغییر مختصات cx دایره‬",\n
\t\t"circle_cy": "‫تغییر مختصات cy دایره‬",\n
\t\t"circle_r": "‫تغییر شعاع دایره‬",\n
\t\t"ellipse_cx": "‫تغییر مختصات cx بیضی‬",\n
\t\t"ellipse_cy": "‫تغییر مختصات cy بیضی‬",\n
\t\t"ellipse_rx": "‫تغییر شعاع rx بیضی‬",\n
\t\t"ellipse_ry": "‫تغییر شعاع ry بیضی‬",\n
\t\t"line_x1": "‫تغییر مختصات x آغاز خط‬",\n
\t\t"line_x2": "‫تغییر مختصات x پایان خط‬",\n
\t\t"line_y1": "‫تغییر مختصات y آغاز خط‬",\n
\t\t"line_y2": "‫تغییر مختصات y پایان خط‬",\n
\t\t"rect_height": "‫تغییر ارتفاع مستطیل‬",\n
\t\t"rect_width": "‫تغییر عرض مستطیل‬",\n
\t\t"corner_radius": "‫شعاع گوشه:‬",\n
\t\t"image_width": "‫تغییر عرض تصویر‬",\n
\t\t"image_height": "‫تغییر ارتفاع تصویر‬",\n
\t\t"image_url": "‫تغییر نشانی وب (url)‬",\n
\t\t"node_x": "‫تغییر مختصات x نقطه‬",\n
\t\t"node_y": "‫تغییر مختصات y نقطه‬",\n
\t\t"seg_type": "‫تغییر نوع قطعه (segment)‬",\n
\t\t"straight_segments": "‫مستقیم‬",\n
\t\t"curve_segments": "‫منحنی‬",\n
\t\t"text_contents": "‫تغییر محتویات متن‬",\n
\t\t"font_family": "‫تغییر خانواده قلم‬",\n
\t\t"font_size": "‫تغییر اندازه قلم‬",\n
\t\t"bold": "‫متن توپر ‬",\n
\t\t"italic": "‫متن کج ‬"\n
\t},\n
\ttools: { \n
\t\t"main_menu": "Main Menu",\n
\t\t"bkgnd_color_opac": "‫تغییر رنگ پس زمینه / تاری‬",\n
\t\t"connector_no_arrow": "No arrow",\n
\t\t"fitToContent": "‫هم اندازه شدن با محتوا‬",\n
\t\t"fit_to_all": "‫هم اندازه شدن با همه محتویات‬",\n
\t\t"fit_to_canvas": "‫هم اندازه شدن با صفحه مجازی (بوم)‬",\n
\t\t"fit_to_layer_content": "‫هم اندازه شدن با محتوای لایه‬",\n
\t\t"fit_to_sel": "‫هم اندازه شدن با اشیاء انتخاب شده‬",\n
\t\t"align_relative_to": "‫تراز نسبت به ...‬",\n
\t\t"relativeTo": "‫نسبت به:‬",\n
\t\t"‫صفحه‬": "‫صفحه‬",\n
\t\t"largest_object": "‫بزرگترین شئ‬",\n
\t\t"selected_objects": "‫اشیاء انتخاب شده‬",\n
\t\t"smallest_object": "‫کوچکترین شئ‬",\n
\t\t"new_doc": "‫تصویر جدید ‬",\n
\t\t"open_doc": "‫باز کردن تصویر ‬",\n
\t\t"export_img": "Export",\n
\t\t"save_doc": "‫ذخیره تصویر ‬",\n
\t\t"import_doc": "Import SVG",\n
\t\t"align_to_page": "Align Element to Page",\n
\t\t"align_bottom": "‫تراز پایین‬",\n
\t\t"align_center": "‫وسط چین‬",\n
\t\t"align_left": "‫چپ چین‬",\n
\t\t"align_middle": "‫تراز میانه‬",\n
\t\t"align_right": "‫راست چین‬",\n
\t\t"align_top": "‫تراز بالا‬",\n
\t\t"mode_select": "‫ابزار انتخاب ‬",\n
\t\t"mode_fhpath": "‫ابزار مداد ‬",\n
\t\t"mode_line": "‫ابزار خط ‬",\n
\t\t"mode_connect": "Connect two objects",\n
\t\t"mode_rect": "Rectangle Tool",\n
\t\t"mode_square": "Square Tool",\n
\t\t"mode_fhrect": "‫مستطیل با قابلیت تغییر پویا‬",\n
\t\t"mode_ellipse": "‫بیضی‬",\n
\t\t"mode_circle": "‫دایره‬",\n
\t\t"mode_fhellipse": "‫بیضی با قابلیت تغییر پویا‬",\n
\t\t"mode_path": "‫ابزار مسیر ‬",\n
\t\t"mode_shapelib": "Shape library",\n
\t\t"mode_text": "‫ابزار متن ‬",\n
\t\t"mode_image": "‫ابزار تصویر ‬",\n
\t\t"mode_zoom": "‫ابزار بزرگ نمایی ‬",\n
\t\t"mode_eyedropper": "Eye Dropper Tool",\n
\t\t"no_embed": "NOTE: This image cannot be embedded. It will depend on this path to be displayed",\n
\t\t"undo": "‫واگرد ‬",\n
\t\t"redo": "‫ازنو ‬",\n
\t\t"tool_source": "‫ویرایش منبع ‬",\n
\t\t"wireframe_mode": "‫حالت نمایش لبه ها ‬",\n
\t\t"toggle_grid": "Show/Hide Grid",\n
\t\t"clone": "Clone Element(s)",\n
\t\t"del": "Delete Element(s)",\n
\t\t"group_elements": "‫قرار دادن عناصر در گروه ‬",\n
\t\t"make_link": "Make (hyper)link",\n
\t\t"set_link_url": "Set link URL (leave empty to remove)",\n
\t\t"to_path": "‫تبدیل به مسیر‬",\n
\t\t"reorient_path": "‫جهت دهی مجدد مسیر‬",\n
\t\t"ungroup": "‫خارج کردن عناصر از گروه ‬",\n
\t\t"docprops": "‫مشخصات سند ‬",\n
\t\t"imagelib": "Image Library",\n
\t\t"move_bottom": "‫انتقال به پایین ترین ‬",\n
\t\t"move_top": "‫انتقال به بالاترین ‬",\n
\t\t"node_clone": "‫ایجاد کپی از نقطه‬",\n
\t\t"node_delete": "‫حذف نقطه‬",\n
\t\t"node_link": "‫پیوند دادن نقاط کنترل‬",\n
\t\t"add_subpath": "Add sub-path",\n
\t\t"openclose_path": "Open/close sub-path",\n
\t\t"source_save": "‫اعمال تغییرات‬",\n
\t\t"cut": "Cut",\n
\t\t"copy": "Copy",\n
\t\t"paste": "Paste",\n
\t\t"paste_in_place": "Paste in Place",\n
\t\t"‫حذف ‬": "Delete",\n
\t\t"group": "Group",\n
\t\t"move_front": "Bring to Front",\n
\t\t"move_up": "Bring Forward",\n
\t\t"move_down": "Send Backward",\n
\t\t"move_back": "Send to Back"\n
\t},\n
\tlayers: {\n
\t\t"layer":"‫لایه‬",\n
\t\t"layers": "Layers",\n
\t\t"del": "‫حذف لایه‬",\n
\t\t"move_down": "‫انتقال لایه به پایین‬",\n
\t\t"new": "‫لایه جدید‬",\n
\t\t"rename": "‫تغییر نام لایه‬",\n
\t\t"move_up": "‫انتقال لایه به بالا‬",\n
\t\t"dupe": "Duplicate Layer",\n
\t\t"merge_down": "Merge Down",\n
\t\t"merge_all": "Merge All",\n
\t\t"move_elems_to": "‫انتقال عناصر به:‬",\n
\t\t"move_selected": "‫انتقال عناصر انتخاب شده به یک لایه متفاوت‬"\n
\t},\n
\tconfig: {\n
\t\t"image_props": "‫مشخصات تصویر‬",\n
\t\t"doc_title": "‫عنوان‬",\n
\t\t"doc_dims": "‫ابعاد صفحه مجازی (بوم)‬",\n
\t\t"included_images": "‫تصاویر گنجانده شده‬",\n
\t\t"image_opt_embed": "‫داده های جای داده شده (پرونده های محلی)‬",\n
\t\t"image_opt_ref": "‫استفاده از ارجاع به پرونده‬",\n
\t\t"editor_prefs": "‫تنظیمات ویراستار‬",\n
\t\t"icon_size": "‫اندازه شمایل‬",\n
\t\t"language": "‫زبان‬",\n
\t\t"background": "‫پس زمینه ویراستار‬",\n
\t\t"editor_img_url": "Image URL",\n
\t\t"editor_bg_note": "‫توجه: پس زمینه همراه تصویر ذخیره نخواهد شد.‬",\n
\t\t"icon_large": "‫بزرگ‬",\n
\t\t"icon_medium": "‫متوسط‬",\n
\t\t"icon_small": "‫کوچک‬",\n
\t\t"icon_xlarge": "‫خیلی بزرگ‬",\n
\t\t"select_predefined": "‫از پیش تعریف شده را انتخاب کنید:‬",\n
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
\t\t"invalidAttrValGiven":"‫مقدار داده شده نامعتبر است‬",\n
\t\t"noContentToFitTo":"‫محتوایی برای هم اندازه شدن وجود ندارد‬",\n
\t\t"dupeLayerName":"‫لایه ای با آن نام وجود دارد!‬",\n
\t\t"enterUniqueLayerName":"‫لطفا یک نام لایه یکتا انتخاب کنید‬",\n
\t\t"enterNewLayerName":"‫لطفا نام لایه جدید را وارد کنید‬",\n
\t\t"layerHasThatName":"‫لایه از قبل آن نام را دارد‬",\n
\t\t"QmoveElemsToLayer":"‫عناصر انتخاب شده به لایه \'%s\' منتقل شوند؟‬",\n
\t\t"QwantToClear":"‫آیا مطمئن هستید که می خواهید نقاشی را پاک کنید؟\\nاین عمل باعث حذف تاریخچه واگرد شما خواهد شد!‬",\n
\t\t"QwantToOpen":"Do you want to open a new file?\\nThis will also erase your undo history!",\n
\t\t"QerrorsRevertToSource":"‫در منبع SVG شما خطاهای تجزیه (parse) وجود داشت.\\nبه منبع SVG اصلی بازگردانده شود؟‬",\n
\t\t"QignoreSourceChanges":"‫تغییرات اعمال شده در منبع SVG نادیده گرفته شوند؟‬",\n
\t\t"featNotSupported":"‫این ویژگی پشتیبانی نشده است‬",\n
\t\t"enterNewImgURL":"‫نشانی وب (url) تصویر جدید را وارد کنید‬",\n
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
            <value> <int>11816</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
