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
            <value> <string>ts40515059.55</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>locale.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals jQuery*/\n
/*jslint vars: true, eqeq: true, forin: true*/\n
/*\n
 * Localizing script for SVG-edit UI\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Narendra Sisodya\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
\n
// Dependencies\n
// 1) jQuery\n
// 2) svgcanvas.js\n
// 3) svg-editor.js\n
\n
var svgEditor = (function($, editor) {\'use strict\';\n
\n
\tvar lang_param;\n
\t\n
\tfunction setStrings(type, obj, ids) {\n
\t\t// Root element to look for element from\n
\t\tvar i, sel, val, $elem, elem, node, parent = $(\'#svg_editor\').parent();\n
\t\tfor (sel in obj) {\n
\t\t\tval = obj[sel];\n
\t\t\tif (!val) {console.log(sel);}\n
\t\t\t\n
\t\t\tif (ids) {sel = \'#\' + sel;}\n
\t\t\t$elem = parent.find(sel);\n
\t\t\tif ($elem.length) {\n
\t\t\t\telem = parent.find(sel)[0];\n
\t\t\t\t\n
\t\t\t\tswitch ( type ) {\n
\t\t\t\t\tcase \'content\':\n
\t\t\t\t\t\tfor (i = 0; i < elem.childNodes.length; i++) {\n
\t\t\t\t\t\t\tnode = elem.childNodes[i];\n
\t\t\t\t\t\t\tif (node.nodeType === 3 && node.textContent.replace(/\\s/g,\'\')) {\n
\t\t\t\t\t\t\t\tnode.textContent = val;\n
\t\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\n
\t\t\t\t\tcase \'title\':\n
\t\t\t\t\t\telem.title = val;\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t\n
\t\t\t} else {\n
\t\t\t\tconsole.log(\'Missing: \' + sel);\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\teditor.readLang = function(langData) {\n
\t\tvar more = editor.canvas.runExtensions("addlangData", lang_param, true);\n
\t\t$.each(more, function(i, m) {\n
\t\t\tif (m.data) {\n
\t\t\t\tlangData = $.merge(langData, m.data);\n
\t\t\t}\n
\t\t});\n
\t\t\n
\t\t// Old locale file, do nothing for now.\n
\t\tif (!langData.tools) {return;}\n
\n
\t\tvar tools = langData.tools,\n
\t\t\tmisc = langData.misc,\n
\t\t\tproperties = langData.properties,\n
\t\t\tconfig = langData.config,\n
\t\t\tlayers = langData.layers,\n
\t\t\tcommon = langData.common,\n
\t\t\tui = langData.ui;\n
\t\t\n
\t\tsetStrings(\'content\', {\n
\t\t\t// copyrightLabel: misc.powered_by, // Currently commented out in svg-editor.html\n
\t\t\tcurve_segments: properties.curve_segments,\n
\t\t\tfitToContent: tools.fitToContent,\n
\t\t\tfit_to_all: tools.fit_to_all,\n
\t\t\tfit_to_canvas: tools.fit_to_canvas,\n
\t\t\tfit_to_layer_content: tools.fit_to_layer_content,\n
\t\t\tfit_to_sel: tools.fit_to_sel,\n
\t\t\t\n
\t\t\ticon_large: config.icon_large,\n
\t\t\ticon_medium: config.icon_medium,\n
\t\t\ticon_small: config.icon_small,\n
\t\t\ticon_xlarge: config.icon_xlarge,\n
\t\t\timage_opt_embed: config.image_opt_embed,\n
\t\t\timage_opt_ref: config.image_opt_ref,\n
\t\t\tincludedImages: config.included_images,\n
\t\t\t\n
\t\t\tlargest_object: tools.largest_object,\n
\t\t\t\n
\t\t\tlayersLabel: layers.layers,\n
\t\t\tpage: tools.page,\n
\t\t\trelativeToLabel: tools.relativeTo,\n
\t\t\tselLayerLabel: layers.move_elems_to,\n
\t\t\tselectedPredefined: config.select_predefined,\n
\t\t\t\n
\t\t\tselected_objects: tools.selected_objects,\n
\t\t\tsmallest_object: tools.smallest_object,\n
\t\t\tstraight_segments: properties.straight_segments,\n
\t\t\t\n
\t\t\tsvginfo_bg_url: config.editor_img_url + ":",\n
\t\t\tsvginfo_bg_note: config.editor_bg_note,\n
\t\t\tsvginfo_change_background: config.background,\n
\t\t\tsvginfo_dim: config.doc_dims,\n
\t\t\tsvginfo_editor_prefs: config.editor_prefs,\n
\t\t\tsvginfo_height: common.height,\n
\t\t\tsvginfo_icons: config.icon_size,\n
\t\t\tsvginfo_image_props: config.image_props,\n
\t\t\tsvginfo_lang: config.language,\n
\t\t\tsvginfo_title: config.doc_title,\n
\t\t\tsvginfo_width: common.width,\n
\t\t\t\n
\t\t\ttool_docprops_cancel: common.cancel,\n
\t\t\ttool_docprops_save: common.ok,\n
\n
\t\t\ttool_source_cancel: common.cancel,\n
\t\t\ttool_source_save: common.ok,\n
\t\t\t\n
\t\t\ttool_prefs_cancel: common.cancel,\n
\t\t\ttool_prefs_save: common.ok,\n
\n
\t\t\tsidepanel_handle: layers.layers.split(\'\').join(\' \'),\n
\n
\t\t\ttool_clear: tools.new_doc,\n
\t\t\ttool_docprops: tools.docprops,\n
\t\t\ttool_export: tools.export_img,\n
\t\t\ttool_import: tools.import_doc,\n
\t\t\ttool_imagelib: tools.imagelib,\n
\t\t\ttool_open: tools.open_doc,\n
\t\t\ttool_save: tools.save_doc,\n
\t\t\t\n
\t\t\tsvginfo_units_rulers: config.units_and_rulers,\n
\t\t\tsvginfo_rulers_onoff: config.show_rulers,\n
\t\t\tsvginfo_unit: config.base_unit,\n
\t\t\t\n
\t\t\tsvginfo_grid_settings: config.grid,\n
\t\t\tsvginfo_snap_onoff: config.snapping_onoff,\n
\t\t\tsvginfo_snap_step: config.snapping_stepsize,\n
\t\t\tsvginfo_grid_color: config.grid_color\n
\t\t}, true);\n
\t\t\n
\t\t// Shape categories\n
\t\tvar o, cats = {};\n
\t\tfor (o in langData.shape_cats) {\n
\t\t\tcats[\'#shape_cats [data-cat="\' + o + \'"]\'] = langData.shape_cats[o];\n
\t\t}\n
\t\t\n
\t\t// TODO: Find way to make this run after shapelib ext has loaded\n
\t\tsetTimeout(function() {\n
\t\t\tsetStrings(\'content\', cats);\n
\t\t}, 2000);\n
\t\t\n
\t\t// Context menus\n
\t\tvar opts = {};\n
\t\t$.each([\'cut\',\'copy\',\'paste\', \'paste_in_place\', \'delete\', \'group\', \'ungroup\', \'move_front\', \'move_up\', \'move_down\', \'move_back\'], function() {\n
\t\t\topts[\'#cmenu_canvas a[href="#\' + this + \'"]\'] = tools[this];\n
\t\t});\n
\n
\t\t$.each([\'dupe\',\'merge_down\', \'merge_all\'], function() {\n
\t\t\topts[\'#cmenu_layers a[href="#\' + this + \'"]\'] = layers[this];\n
\t\t});\n
\n
\t\topts[\'#cmenu_layers a[href="#delete"]\'] = layers.del;\n
\t\t\n
\t\tsetStrings(\'content\', opts);\n
\t\t\n
\t\tsetStrings(\'title\', {\n
\t\t\talign_relative_to: tools.align_relative_to,\n
\t\t\tcircle_cx: properties.circle_cx,\n
\t\t\tcircle_cy: properties.circle_cy,\n
\t\t\tcircle_r: properties.circle_r,\n
\t\t\tcornerRadiusLabel: properties.corner_radius,\n
\t\t\tellipse_cx: properties.ellipse_cx,\n
\t\t\tellipse_cy: properties.ellipse_cy,\n
\t\t\tellipse_rx: properties.ellipse_rx,\n
\t\t\tellipse_ry: properties.ellipse_ry,\n
\t\t\tfill_color: properties.fill_color,\n
\t\t\tfont_family: properties.font_family,\n
\t\t\tidLabel: properties.id,\n
\t\t\timage_height: properties.image_height,\n
\t\t\timage_url: properties.image_url,\n
\t\t\timage_width: properties.image_width,\n
\t\t\tlayer_delete: layers.del,\n
\t\t\tlayer_down: layers.move_down,\n
\t\t\tlayer_new: layers[\'new\'],\n
\t\t\tlayer_rename: layers.rename,\n
\t\t\tlayer_moreopts: common.more_opts,\n
\t\t\tlayer_up: layers.move_up,\n
\t\t\tline_x1: properties.line_x1,\n
\t\t\tline_x2: properties.line_x2,\n
\t\t\tline_y1: properties.line_y1,\n
\t\t\tline_y2: properties.line_y2,\n
\t\t\tlinecap_butt: properties.linecap_butt,\n
\t\t\tlinecap_round: properties.linecap_round,\n
\t\t\tlinecap_square: properties.linecap_square,\n
\t\t\tlinejoin_bevel: properties.linejoin_bevel,\n
\t\t\tlinejoin_miter: properties.linejoin_miter,\n
\t\t\tlinejoin_round: properties.linejoin_round,\n
\t\t\tmain_icon: tools.main_menu,\n
\t\t\tmode_connect: tools.mode_connect,\n
\t\t\ttools_shapelib_show: tools.mode_shapelib,\n
\t\t\tpalette: ui.palette_info,\n
\t\t\tzoom_panel: ui.zoom_level,\n
\t\t\tpath_node_x: properties.node_x,\n
\t\t\tpath_node_y: properties.node_y,\n
\t\t\trect_height_tool: properties.rect_height,\n
\t\t\trect_width_tool: properties.rect_width,\n
\t\t\tseg_type: properties.seg_type,\n
\t\t\tselLayerNames: layers.move_selected,\n
\t\t\tselected_x: properties.pos_x,\n
\t\t\tselected_y: properties.pos_y,\n
\t\t\tstroke_color: properties.stroke_color,\n
\t\t\tstroke_style: properties.stroke_style,\n
\t\t\tstroke_width: properties.stroke_width,\n
\t\t\tsvginfo_title: config.doc_title,\n
\t\t\ttext: properties.text_contents,\n
\t\t\ttoggle_stroke_tools: ui.toggle_stroke_tools,\n
\t\t\ttool_add_subpath: tools.add_subpath,\n
\t\t\ttool_alignbottom: tools.align_bottom,\n
\t\t\ttool_aligncenter: tools.align_center,\n
\t\t\ttool_alignleft: tools.align_left,\n
\t\t\ttool_alignmiddle: tools.align_middle,\n
\t\t\ttool_alignright: tools.align_right,\n
\t\t\ttool_aligntop: tools.align_top,\n
\t\t\ttool_angle: properties.angle,\n
\t\t\ttool_blur: properties.blur,\n
\t\t\ttool_bold: properties.bold,\n
\t\t\ttool_circle: tools.mode_circle,\n
\t\t\ttool_clone: tools.clone,\n
\t\t\ttool_clone_multi: tools.clone,\n
\t\t\ttool_delete: tools.del,\n
\t\t\ttool_delete_multi: tools.del,\n
\t\t\ttool_ellipse: tools.mode_ellipse,\n
\t\t\ttool_eyedropper: tools.mode_eyedropper,\n
\t\t\ttool_fhellipse: tools.mode_fhellipse,\n
\t\t\ttool_fhpath: tools.mode_fhpath,\n
\t\t\ttool_fhrect: tools.mode_fhrect,\n
\t\t\ttool_font_size: properties.font_size,\n
\t\t\ttool_group_elements: tools.group_elements,\n
\t\t\ttool_make_link: tools.make_link,\n
\t\t\ttool_link_url: tools.set_link_url,\n
\t\t\ttool_image: tools.mode_image,\n
\t\t\ttool_italic: properties.italic,\n
\t\t\ttool_line: tools.mode_line,\n
\t\t\ttool_move_bottom: tools.move_bottom,\n
\t\t\ttool_move_top: tools.move_top,\n
\t\t\ttool_node_clone: tools.node_clone,\n
\t\t\ttool_node_delete: tools.node_delete,\n
\t\t\ttool_node_link: tools.node_link,\n
\t\t\ttool_opacity: properties.opacity,\n
\t\t\ttool_openclose_path: tools.openclose_path,\n
\t\t\ttool_path: tools.mode_path,\n
\t\t\ttool_position: tools.align_to_page,\n
\t\t\ttool_rect: tools.mode_rect,\n
\t\t\ttool_redo: tools.redo,\n
\t\t\ttool_reorient: tools.reorient_path,\n
\t\t\ttool_select: tools.mode_select,\n
\t\t\ttool_source: tools.source_save,\n
\t\t\ttool_square: tools.mode_square,\n
\t\t\ttool_text: tools.mode_text,\n
\t\t\ttool_topath: tools.to_path,\n
\t\t\ttool_undo: tools.undo,\n
\t\t\ttool_ungroup: tools.ungroup,\n
\t\t\ttool_wireframe: tools.wireframe_mode,\n
\t\t\tview_grid: tools.toggle_grid,\n
\t\t\ttool_zoom: tools.mode_zoom,\n
\t\t\turl_notice: tools.no_embed\n
\n
\t\t}, true);\n
\t\t\n
\t\teditor.setLang(lang_param, langData);\n
\t};\n
\n
\teditor.putLocale = function (given_param, good_langs) {\n
\t\n
\t\tif (given_param) {\n
\t\t\tlang_param = given_param;\n
\t\t}\n
\t\telse {\n
\t\t\tlang_param = $.pref(\'lang\');\n
\t\t\tif (!lang_param) {\n
\t\t\t\tif (navigator.userLanguage) { // Explorer\n
\t\t\t\t\tlang_param = navigator.userLanguage;\n
\t\t\t\t}\n
\t\t\t\telse if (navigator.language) { // FF, Opera, ...\n
\t\t\t\t\tlang_param = navigator.language;\n
\t\t\t\t}\n
\t\t\t\tif (lang_param == null) { // Todo: Would cause problems if uiStrings removed; remove this?\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tconsole.log(\'Lang: \' + lang_param);\n
\t\t\t\n
\t\t\t// Set to English if language is not in list of good langs\n
\t\t\tif ($.inArray(lang_param, good_langs) === -1 && lang_param !== \'test\') {\n
\t\t\t\tlang_param = "en";\n
\t\t\t}\n
\t\n
\t\t\t// don\'t bother on first run if language is English\t\t\n
\t\t\t// The following line prevents setLang from running\n
\t\t\t//    extensions which depend on updated uiStrings,\n
\t\t\t//    so commenting it out.\n
\t\t\t// if (lang_param.indexOf("en") === 0) {return;}\n
\n
\t\t}\n
\t\t\n
\t\tvar conf = editor.curConfig;\n
\t\t\n
\t\tvar url = conf.langPath + "lang." + lang_param + ".js";\n
\t\t\n
\t\t$.getScript(url, function(d) {\n
\t\t\t// Fails locally in Chrome 5+\n
\t\t\tif (!d) {\n
\t\t\t\tvar s = document.createElement(\'script\');\n
\t\t\t\ts.src = url;\n
\t\t\t\tdocument.querySelector(\'head\').appendChild(s);\n
\t\t\t}\n
\t\t});\n
\t\t\n
\t};\n
\t\n
\treturn editor;\n
}(jQuery, svgEditor));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9719</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
