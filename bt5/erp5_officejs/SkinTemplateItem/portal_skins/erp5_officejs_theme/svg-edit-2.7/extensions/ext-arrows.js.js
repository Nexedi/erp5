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
            <value> <string>ts40515059.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-arrows.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgCanvas, $*/\n
/*jslint vars: true, eqeq: true*/\n
/*\n
 * ext-arrows.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
\n
svgEditor.addExtension(\'Arrows\', function(S) {\n
\tvar svgcontent = S.svgcontent,\n
\t\taddElem = S.addSvgElementFromJson,\n
\t\tnonce = S.nonce,\n
\t\trandomize_ids = S.randomize_ids,\n
\t\tselElems, pathdata,\n
\t\tlang_list = {\n
\t\t\t\'en\':[\n
\t\t\t\t{\'id\': \'arrow_none\', \'textContent\': \'No arrow\' }\n
\t\t\t],\n
\t\t\t\'fr\':[\n
\t\t\t\t{\'id\': \'arrow_none\', \'textContent\': \'Sans flèche\' }\n
\t\t\t]\n
\t\t},\n
\t\tarrowprefix,\n
\t\tprefix = \'se_arrow_\';\n
\n
\tfunction setArrowNonce(window, n) {\n
\t\trandomize_ids = true;\n
\t\tarrowprefix = prefix + n + \'_\';\n
\t\tpathdata.fw.id = arrowprefix + \'fw\';\n
\t\tpathdata.bk.id = arrowprefix + \'bk\';\n
\t}\n
\n
\tfunction unsetArrowNonce(window) {\n
\t\trandomize_ids = false;\n
\t\tarrowprefix = prefix;\n
\t\tpathdata.fw.id = arrowprefix + \'fw\';\n
\t\tpathdata.bk.id = arrowprefix + \'bk\';\n
\t}\n
\n
\n
\tsvgCanvas.bind(\'setnonce\', setArrowNonce);\n
\tsvgCanvas.bind(\'unsetnonce\', unsetArrowNonce);\n
\n
\tif (randomize_ids) {\n
\t\tarrowprefix = prefix + nonce + \'_\';\n
\t} else {\n
\t\tarrowprefix = prefix;\n
\t}\n
\n
\tpathdata = {\n
\t\tfw: {d: \'m0,0l10,5l-10,5l5,-5l-5,-5z\', refx: 8,  id: arrowprefix + \'fw\'},\n
\t\tbk: {d: \'m10,0l-10,5l10,5l-5,-5l5,-5z\', refx: 2, id: arrowprefix + \'bk\'}\n
\t};\n
\n
\tfunction getLinked(elem, attr) {\n
\t\tvar str = elem.getAttribute(attr);\n
\t\tif(!str) {return null;}\n
\t\tvar m = str.match(/\\(\\#(.*)\\)/);\n
\t\tif(!m || m.length !== 2) {\n
\t\t\treturn null;\n
\t\t}\n
\t\treturn S.getElem(m[1]);\n
\t}\n
\n
\tfunction showPanel(on) {\n
\t\t$(\'#arrow_panel\').toggle(on);\n
\t\tif(on) {\n
\t\t\tvar el = selElems[0];\n
\t\t\tvar end = el.getAttribute(\'marker-end\');\n
\t\t\tvar start = el.getAttribute(\'marker-start\');\n
\t\t\tvar mid = el.getAttribute(\'marker-mid\');\n
\t\t\tvar val;\n
\n
\t\t\tif (end && start) {\n
\t\t\t\tval = \'both\';\n
\t\t\t} else if (end) {\n
\t\t\t\tval = \'end\';\n
\t\t\t} else if (start) {\n
\t\t\t\tval = \'start\';\n
\t\t\t} else if (mid) {\n
\t\t\t\tval = \'mid\';\n
\t\t\t\tif (mid.indexOf(\'bk\') !== -1) {\n
\t\t\t\t\tval = \'mid_bk\';\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tif (!start && !mid && !end) {\n
\t\t\t\tval = \'none\';\n
\t\t\t}\n
\n
\t\t\t$(\'#arrow_list\').val(val);\n
\t\t}\n
\t}\n
\n
\tfunction resetMarker() {\n
\t\tvar el = selElems[0];\n
\t\tel.removeAttribute(\'marker-start\');\n
\t\tel.removeAttribute(\'marker-mid\');\n
\t\tel.removeAttribute(\'marker-end\');\n
\t}\n
\n
\tfunction addMarker(dir, type, id) {\n
\t\t// TODO: Make marker (or use?) per arrow type, since refX can be different\n
\t\tid = id || arrowprefix + dir;\n
\n
\t\tvar marker = S.getElem(id);\n
\t\tvar data = pathdata[dir];\n
\n
\t\tif (type == \'mid\') {\n
\t\t\tdata.refx = 5;\n
\t\t}\n
\n
\t\tif (!marker) {\n
\t\t\tmarker = addElem({\n
\t\t\t\t\'element\': \'marker\',\n
\t\t\t\t\'attr\': {\n
\t\t\t\t\t\'viewBox\': \'0 0 10 10\',\n
\t\t\t\t\t\'id\': id,\n
\t\t\t\t\t\'refY\': 5,\n
\t\t\t\t\t\'markerUnits\': \'strokeWidth\',\n
\t\t\t\t\t\'markerWidth\': 5,\n
\t\t\t\t\t\'markerHeight\': 5,\n
\t\t\t\t\t\'orient\': \'auto\',\n
\t\t\t\t\t\'style\': \'pointer-events:none\' // Currently needed for Opera\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\tvar arrow = addElem({\n
\t\t\t\t\'element\': \'path\',\n
\t\t\t\t\'attr\': {\n
\t\t\t\t\t\'d\': data.d,\n
\t\t\t\t\t\'fill\': \'#000000\'\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\tmarker.appendChild(arrow);\n
\t\t\tS.findDefs().appendChild(marker);\n
\t\t}\n
\n
\t\tmarker.setAttribute(\'refX\', data.refx);\n
\n
\t\treturn marker;\n
\t}\n
\n
\tfunction setArrow() {\n
\t\tvar type = this.value;\n
\t\tresetMarker();\n
\n
\t\tif (type == \'none\') {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t// Set marker on element\n
\t\tvar dir = \'fw\';\n
\t\tif (type == \'mid_bk\') {\n
\t\t\ttype = \'mid\';\n
\t\t\tdir = \'bk\';\n
\t\t} else if (type == \'both\') {\n
\t\t\taddMarker(\'bk\', type);\n
\t\t\tsvgCanvas.changeSelectedAttribute(\'marker-start\', \'url(#\' + pathdata.bk.id + \')\');\n
\t\t\ttype = \'end\';\n
\t\t\tdir = \'fw\';\n
\t\t} else if (type == \'start\') {\n
\t\t\tdir = \'bk\';\n
\t\t}\n
\n
\t\taddMarker(dir, type);\n
\t\tsvgCanvas.changeSelectedAttribute(\'marker-\' + type, \'url(#\' + pathdata[dir].id + \')\');\n
\t\tS.call(\'changed\', selElems);\n
\t}\n
\n
\tfunction colorChanged(elem) {\n
\t\tvar color = elem.getAttribute(\'stroke\');\n
\t\tvar mtypes = [\'start\', \'mid\', \'end\'];\n
\t\tvar defs = S.findDefs();\n
\n
\t\t$.each(mtypes, function(i, type) {\n
\t\t\tvar marker = getLinked(elem, \'marker-\'+type);\n
\t\t\tif(!marker) {return;}\n
\n
\t\t\tvar cur_color = $(marker).children().attr(\'fill\');\n
\t\t\tvar cur_d = $(marker).children().attr(\'d\');\n
\t\t\tvar new_marker = null;\n
\t\t\tif(cur_color === color) {return;}\n
\n
\t\t\tvar all_markers = $(defs).find(\'marker\');\n
\t\t\t// Different color, check if already made\n
\t\t\tall_markers.each(function() {\n
\t\t\t\tvar attrs = $(this).children().attr([\'fill\', \'d\']);\n
\t\t\t\tif(attrs.fill === color && attrs.d === cur_d) {\n
\t\t\t\t\t// Found another marker with this color and this path\n
\t\t\t\t\tnew_marker = this;\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\tif(!new_marker) {\n
\t\t\t\t// Create a new marker with this color\n
\t\t\t\tvar last_id = marker.id;\n
\t\t\t\tvar dir = last_id.indexOf(\'_fw\') !== -1?\'fw\':\'bk\';\n
\n
\t\t\t\tnew_marker = addMarker(dir, type, arrowprefix + dir + all_markers.length);\n
\n
\t\t\t\t$(new_marker).children().attr(\'fill\', color);\n
\t\t\t}\n
\n
\t\t\t$(elem).attr(\'marker-\'+type, \'url(#\' + new_marker.id + \')\');\n
\n
\t\t\t// Check if last marker can be removed\n
\t\t\tvar remove = true;\n
\t\t\t$(S.svgcontent).find(\'line, polyline, path, polygon\').each(function() {\n
\t\t\t\tvar elem = this;\n
\t\t\t\t$.each(mtypes, function(j, mtype) {\n
\t\t\t\t\tif($(elem).attr(\'marker-\' + mtype) === \'url(#\' + marker.id + \')\') {\n
\t\t\t\t\t\tremove = false;\n
\t\t\t\t\t\treturn remove;\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tif(!remove) {return false;}\n
\t\t\t});\n
\n
\t\t\t// Not found, so can safely remove\n
\t\t\tif(remove) {\n
\t\t\t\t$(marker).remove();\n
\t\t\t}\n
\t\t});\n
\t}\n
\n
\treturn {\n
\t\tname: \'Arrows\',\n
\t\tcontext_tools: [{\n
\t\t\ttype: \'select\',\n
\t\t\tpanel: \'arrow_panel\',\n
\t\t\ttitle: \'Select arrow type\',\n
\t\t\tid: \'arrow_list\',\n
\t\t\toptions: {\n
\t\t\t\tnone: \'No arrow\',\n
\t\t\t\tend: \'----&gt;\',\n
\t\t\t\tstart: \'&lt;----\',\n
\t\t\t\tboth: \'&lt;---&gt;\',\n
\t\t\t\tmid: \'--&gt;--\',\n
\t\t\t\tmid_bk: \'--&lt;--\'\n
\t\t\t},\n
\t\t\tdefval: \'none\',\n
\t\t\tevents: {\n
\t\t\t\tchange: setArrow\n
\t\t\t}\n
\t\t}],\n
\t\tcallback: function() {\n
\t\t\t$(\'#arrow_panel\').hide();\n
\t\t\t// Set ID so it can be translated in locale file\n
\t\t\t$(\'#arrow_list option\')[0].id = \'connector_no_arrow\';\n
\t\t},\n
\t\taddLangData: function(lang) {\n
\t\t\treturn {\n
\t\t\t\tdata: lang_list[lang]\n
\t\t\t};\n
\t\t},\n
\t\tselectedChanged: function(opts) {\n
\t\t\t// Use this to update the current selected elements\n
\t\t\tselElems = opts.elems;\n
\n
\t\t\tvar i = selElems.length;\n
\t\t\tvar marker_elems = [\'line\', \'path\', \'polyline\', \'polygon\'];\n
\t\t\twhile(i--) {\n
\t\t\t\tvar elem = selElems[i];\n
\t\t\t\tif(elem && $.inArray(elem.tagName, marker_elems) !== -1) {\n
\t\t\t\t\tif(opts.selectedElement && !opts.multiselected) {\n
\t\t\t\t\t\tshowPanel(true);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tshowPanel(false);\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tshowPanel(false);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\telementChanged: function(opts) {\n
\t\t\tvar elem = opts.elems[0];\n
\t\t\tif(elem && (\n
\t\t\t\telem.getAttribute(\'marker-start\') ||\n
\t\t\t\telem.getAttribute(\'marker-mid\') ||\n
\t\t\t\telem.getAttribute(\'marker-end\')\n
\t\t\t)) {\n
//\t\t\t\t\t\t\t\tvar start = elem.getAttribute(\'marker-start\');\n
//\t\t\t\t\t\t\t\tvar mid = elem.getAttribute(\'marker-mid\');\n
//\t\t\t\t\t\t\t\tvar end = elem.getAttribute(\'marker-end\');\n
\t\t\t\t// Has marker, so see if it should match color\n
\t\t\t\tcolorChanged(elem);\n
\t\t\t}\n
\t\t}\n
\t};\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6748</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
