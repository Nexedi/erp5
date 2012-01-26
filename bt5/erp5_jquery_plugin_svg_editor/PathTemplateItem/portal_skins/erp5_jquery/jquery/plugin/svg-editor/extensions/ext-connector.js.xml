<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_Cacheable__manager_id</string> </key>
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts27579659.58</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-connector.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * ext-connector.js\n
 *\n
 * Licensed under the Apache License, Version 2\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
 \n
svgEditor.addExtension("Connector", function(S) {\n
\tvar svgcontent = S.svgcontent,\n
\t\tsvgroot = S.svgroot,\n
\t\tgetNextId = S.getNextId,\n
\t\tgetElem = S.getElem,\n
\t\taddElem = S.addSvgElementFromJson,\n
\t\tselManager = S.selectorManager,\n
\t\tcurConfig = svgEditor.curConfig,\n
\t\tstarted = false,\n
\t\tstart_x,\n
\t\tstart_y,\n
\t\tcur_line,\n
\t\tstart_elem,\n
\t\tend_elem,\n
\t\tconnections = [],\n
\t\tconn_sel = ".se_connector",\n
\t\tse_ns,\n
// \t\t\tconnect_str = "-SE_CONNECT-",\n
\t\tselElems = [];\n
\t\t\n
\tvar lang_list = {\n
\t\t"en":[\n
\t\t\t{"id": "mode_connect", "title": "Connect two objects" }\n
\t\t],\n
\t\t"fr":[\n
\t\t\t{"id": "mode_connect", "title": "Connecter deux objets"}\n
\t\t]\n
\t};\n
\t\n
\tfunction getOffset(side, line) {\n
\t\tvar give_offset = !!line.getAttribute(\'marker-\' + side);\n
// \t\tvar give_offset = $(line).data(side+\'_off\');\n
\n
\t\t// TODO: Make this number (5) be based on marker width/height\n
\t\tvar size = line.getAttribute(\'stroke-width\') * 5;\n
\t\treturn give_offset ? size : 0;\n
\t}\n
\t\n
\tfunction showPanel(on) {\n
\t\tvar conn_rules = $(\'#connector_rules\');\n
\t\tif(!conn_rules.length) {\n
\t\t\tconn_rules = $(\'<style id="connector_rules"><\\/style>\').appendTo(\'head\');\n
\t\t} \n
\t\tconn_rules.text(!on?"":"#tool_clone, #tool_topath, #tool_angle, #xy_panel { display: none !important; }");\n
\t\t$(\'#connector_panel\').toggle(on);\n
\t}\n
\t\n
\tfunction setPoint(elem, pos, x, y, setMid) {\n
\t\tvar pts = elem.points;\n
\t\tvar pt = svgroot.createSVGPoint();\n
\t\tpt.x = x;\n
\t\tpt.y = y;\n
\t\tif(pos === \'end\') pos = pts.numberOfItems-1;\n
\t\t// TODO: Test for this on init, then use alt only if needed\n
\t\ttry {\n
\t\t\tpts.replaceItem(pt, pos);\n
\t\t} catch(err) {\n
\t\t\t// Should only occur in FF which formats points attr as "n,n n,n", so just split\n
\t\t\tvar pt_arr = elem.getAttribute("points").split(" ");\n
\t\t\tfor(var i=0; i< pt_arr.length; i++) {\n
\t\t\t\tif(i == pos) {\n
\t\t\t\t\tpt_arr[i] = x + \',\' + y;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\telem.setAttribute("points",pt_arr.join(" ")); \n
\t\t}\n
\t\t\n
\t\tif(setMid) {\n
\t\t\t// Add center point\n
\t\t\tvar pt_start = pts.getItem(0);\n
\t\t\tvar pt_end = pts.getItem(pts.numberOfItems-1);\n
\t\t\tsetPoint(elem, 1, (pt_end.x + pt_start.x)/2, (pt_end.y + pt_start.y)/2);\n
\t\t}\n
\t}\n
\t\n
\tfunction updateLine(diff_x, diff_y) {\n
\t\t// Update line with element\n
\t\tvar i = connections.length;\n
\t\twhile(i--) {\n
\t\t\tvar conn = connections[i];\n
\t\t\tvar line = conn.connector;\n
\t\t\tvar elem = conn.elem;\n
\t\t\t\n
\t\t\tvar pre = conn.is_start?\'start\':\'end\';\n
// \t\t\t\t\t\tvar sw = line.getAttribute(\'stroke-width\') * 5;\n
\t\t\t\n
\t\t\t// Update bbox for this element\n
\t\t\tvar bb = $(line).data(pre+\'_bb\');\n
\t\t\tbb.x = conn.start_x + diff_x;\n
\t\t\tbb.y = conn.start_y + diff_y;\n
\t\t\t$(line).data(pre+\'_bb\', bb);\n
\t\t\t\n
\t\t\tvar alt_pre = conn.is_start?\'end\':\'start\';\n
\t\t\t\n
\t\t\t// Get center pt of connected element\n
\t\t\tvar bb2 = $(line).data(alt_pre+\'_bb\');\n
\t\t\tvar src_x = bb2.x + bb2.width/2;\n
\t\t\tvar src_y = bb2.y + bb2.height/2;\n
\t\t\t\n
\t\t\t// Set point of element being moved\n
\t\t\tvar pt = getBBintersect(src_x, src_y, bb, getOffset(pre, line)); // $(line).data(pre+\'_off\')?sw:0\n
\t\t\tsetPoint(line, conn.is_start?0:\'end\', pt.x, pt.y, true);\n
\t\t\t\n
\t\t\t// Set point of connected element\n
\t\t\tvar pt2 = getBBintersect(pt.x, pt.y, $(line).data(alt_pre + \'_bb\'), getOffset(alt_pre, line));\n
\t\t\tsetPoint(line, conn.is_start?\'end\':0, pt2.x, pt2.y, true);\n
\n
\t\t}\n
\t}\n
\t\n
\tfunction findConnectors(elems) {\n
\t\tif(!elems) elems = selElems;\n
\t\tvar connectors = $(svgcontent).find(conn_sel);\n
\t\tconnections = [];\n
\n
\t\t// Loop through connectors to see if one is connected to the element\n
\t\tconnectors.each(function() {\n
\t\t\tvar start = $(this).data("c_start");\n
\t\t\tvar end = $(this).data("c_end");\n
\t\t\t\n
\t\t\tvar parts = [getElem(start), getElem(end)];\n
\t\t\tfor(var i=0; i<2; i++) {\n
\t\t\t\tvar c_elem = parts[i];\n
\t\t\t\tvar add_this = false;\n
\t\t\t\t// The connected element might be part of a selected group\n
\t\t\t\t$(c_elem).parents().each(function() {\n
\t\t\t\t\tif($.inArray(this, elems) !== -1) {\n
\t\t\t\t\t\t// Pretend this element is selected\n
\t\t\t\t\t\tadd_this = true;\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tif(!c_elem || !c_elem.parentNode) {\n
\t\t\t\t\t$(this).remove();\n
\t\t\t\t\tcontinue;\n
\t\t\t\t}\n
\t\t\t\tif($.inArray(c_elem, elems) !== -1 || add_this) {\n
\t\t\t\t\tvar bb = svgCanvas.getStrokedBBox([c_elem]);\n
\t\t\t\t\tconnections.push({\n
\t\t\t\t\t\telem: c_elem,\n
\t\t\t\t\t\tconnector: this,\n
\t\t\t\t\t\tis_start: (i === 0),\n
\t\t\t\t\t\tstart_x: bb.x,\n
\t\t\t\t\t\tstart_y: bb.y\n
\t\t\t\t\t});\t\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\t}\n
\t\n
\tfunction updateConnectors(elems) {\n
\t\t// Updates connector lines based on selected elements\n
\t\t// Is not used on mousemove, as it runs getStrokedBBox every time,\n
\t\t// which isn\'t necessary there.\n
\t\tfindConnectors(elems);\n
\t\tif(connections.length) {\n
\t\t\t// Update line with element\n
\t\t\tvar i = connections.length;\n
\t\t\twhile(i--) {\n
\t\t\t\tvar conn = connections[i];\n
\t\t\t\tvar line = conn.connector;\n
\t\t\t\tvar elem = conn.elem;\n
\n
\t\t\t\tvar sw = line.getAttribute(\'stroke-width\') * 5;\n
\t\t\t\tvar pre = conn.is_start?\'start\':\'end\';\n
\t\t\t\t\n
\t\t\t\t// Update bbox for this element\n
\t\t\t\tvar bb = svgCanvas.getStrokedBBox([elem]);\n
\t\t\t\tbb.x = conn.start_x;\n
\t\t\t\tbb.y = conn.start_y;\n
\t\t\t\t$(line).data(pre+\'_bb\', bb);\n
\t\t\t\tvar add_offset = $(line).data(pre+\'_off\');\n
\t\t\t\n
\t\t\t\tvar alt_pre = conn.is_start?\'end\':\'start\';\n
\t\t\t\t\n
\t\t\t\t// Get center pt of connected element\n
\t\t\t\tvar bb2 = $(line).data(alt_pre+\'_bb\');\n
\t\t\t\tvar src_x = bb2.x + bb2.width/2;\n
\t\t\t\tvar src_y = bb2.y + bb2.height/2;\n
\t\t\t\t\n
\t\t\t\t// Set point of element being moved\n
\t\t\t\tvar pt = getBBintersect(src_x, src_y, bb, getOffset(pre, line));\n
\t\t\t\tsetPoint(line, conn.is_start?0:\'end\', pt.x, pt.y, true);\n
\t\t\t\t\n
\t\t\t\t// Set point of connected element\n
\t\t\t\tvar pt2 = getBBintersect(pt.x, pt.y, $(line).data(alt_pre + \'_bb\'), getOffset(alt_pre, line));\n
\t\t\t\tsetPoint(line, conn.is_start?\'end\':0, pt2.x, pt2.y, true);\n
\t\t\t\t\n
\t\t\t\t// Update points attribute manually for webkit\n
\t\t\t\tif(navigator.userAgent.indexOf(\'AppleWebKit\') != -1) {\n
\t\t\t\t\tvar pts = line.points;\n
\t\t\t\t\tvar len = pts.numberOfItems;\n
\t\t\t\t\tvar pt_arr = Array(len);\n
\t\t\t\t\tfor(var j=0; j< len; j++) {\n
\t\t\t\t\t\tvar pt = pts.getItem(j);\n
\t\t\t\t\t\tpt_arr[j] = pt.x + \',\' + pt.y;\n
\t\t\t\t\t}\t\n
\t\t\t\t\tline.setAttribute("points",pt_arr.join(" ")); \n
\t\t\t\t}\n
\n
\t\t\t}\n
\t\t}\n
\t}\n
\t\n
\tfunction getBBintersect(x, y, bb, offset) {\n
\t\tif(offset) {\n
\t\t\toffset -= 0;\n
\t\t\tbb = $.extend({}, bb);\n
\t\t\tbb.width += offset;\n
\t\t\tbb.height += offset;\n
\t\t\tbb.x -= offset/2;\n
\t\t\tbb.y -= offset/2;\n
\t\t}\n
\t\n
\t\tvar mid_x = bb.x + bb.width/2;\n
\t\tvar mid_y = bb.y + bb.height/2;\n
\t\tvar len_x = x - mid_x;\n
\t\tvar len_y = y - mid_y;\n
\t\t\n
\t\tvar slope = Math.abs(len_y/len_x);\n
\t\t\n
\t\tvar ratio;\n
\t\t\n
\t\tif(slope < bb.height/bb.width) {\n
\t\t\tratio = (bb.width/2) / Math.abs(len_x);\n
\t\t} else {\n
\t\t\tratio = (bb.height/2) / Math.abs(len_y);\n
\t\t}\n
\t\t\n
\t\t\n
\t\treturn {\n
\t\t\tx: mid_x + len_x * ratio,\n
\t\t\ty: mid_y + len_y * ratio\n
\t\t}\n
\t}\n
\t\n
\t// Do once\n
\t(function() {\n
\t\tvar gse = svgCanvas.groupSelectedElements;\n
\t\t\n
\t\tsvgCanvas.groupSelectedElements = function() {\n
\t\t\tsvgCanvas.removeFromSelection($(conn_sel).toArray());\n
\t\t\tgse();\n
\t\t}\n
\t\t\n
\t\tvar mse = svgCanvas.moveSelectedElements;\n
\t\t\n
\t\tsvgCanvas.moveSelectedElements = function() {\n
\t\t\tsvgCanvas.removeFromSelection($(conn_sel).toArray());\n
\t\t\tmse.apply(this, arguments);\n
\t\t\tupdateConnectors();\n
\t\t}\n
\t\t\n
\t\tse_ns = svgCanvas.getEditorNS();\n
\t}());\n
\t\n
\t// Do on reset\n
\tfunction init() {\n
\t\t// Make sure all connectors have data set\n
\t\t$(svgcontent).find(\'*\').each(function() { \n
\t\t\tvar conn = this.getAttributeNS(se_ns, "connector");\n
\t\t\tif(conn) {\n
\t\t\t\tthis.setAttribute(\'class\', conn_sel.substr(1));\n
\t\t\t\tvar conn_data = conn.split(\' \');\n
\t\t\t\tvar sbb = svgCanvas.getStrokedBBox([getElem(conn_data[0])]);\n
\t\t\t\tvar ebb = svgCanvas.getStrokedBBox([getElem(conn_data[1])]);\n
\t\t\t\t$(this).data(\'c_start\',conn_data[0])\n
\t\t\t\t\t.data(\'c_end\',conn_data[1])\n
\t\t\t\t\t.data(\'start_bb\', sbb)\n
\t\t\t\t\t.data(\'end_bb\', ebb);\n
\t\t\t\tsvgCanvas.getEditorNS(true);\n
\t\t\t}\n
\t\t});\n
// \t\t\tupdateConnectors();\n
\t}\n
\t\n
// \t\t$(svgroot).parent().mousemove(function(e) {\n
// // \t\t\tif(started \n
// // \t\t\t\t|| svgCanvas.getMode() != "connector"\n
// // \t\t\t\t|| e.target.parentNode.parentNode != svgcontent) return;\n
// \t\t\t\n
// \t\t\tconsole.log(\'y\')\n
// // \t\t\tif(e.target.parentNode.parentNode === svgcontent) {\n
// // \t\t\t\t\t\n
// // \t\t\t}\n
// \t\t});\n
\t\n
\treturn {\n
\t\tname: "Connector",\n
\t\tsvgicons: "jquery/plugin/svg-editor/images/conn.svg",\n
\t\tbuttons: [{\n
\t\t\tid: "mode_connect",\n
\t\t\ttype: "mode",\n
\t\t\ticon: "jquery_plugin/svg-editor/images/cut.png",\n
\t\t\ttitle: "Connect two objects",\n
\t\t\tkey: "Shift+3",\n
\t\t\tincludeWith: {\n
\t\t\t\tbutton: \'#tool_line\',\n
\t\t\t\tisDefault: false,\n
\t\t\t\tposition: 1\n
\t\t\t},\n
\t\t\tevents: {\n
\t\t\t\t\'click\': function() {\n
\t\t\t\t\tsvgCanvas.setMode("connector");\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}],\n
\t\taddLangData: function(lang) {\n
\t\t\treturn {\n
\t\t\t\tdata: lang_list[lang]\n
\t\t\t};\n
\t\t},\n
\t\tmouseDown: function(opts) {\n
\t\t\tvar e = opts.event;\n
\t\t\tstart_x = opts.start_x,\n
\t\t\tstart_y = opts.start_y;\n
\t\t\tvar mode = svgCanvas.getMode();\n
\t\t\t\n
\t\t\tif(mode == "connector") {\n
\t\t\t\t\n
\t\t\t\tif(started) return;\n
\t\t\t\t\n
\t\t\t\tvar mouse_target = e.target;\n
\t\t\t\t\n
\t\t\t\tvar parents = $(mouse_target).parents();\n
\t\t\t\t\n
\t\t\t\tif($.inArray(svgcontent, parents) != -1) {\n
\t\t\t\t\t// Connectable element\n
\t\t\t\t\t\n
\t\t\t\t\t// If child of foreignObject, use parent\n
\t\t\t\t\tvar fo = $(mouse_target).closest("foreignObject");\n
\t\t\t\t\tstart_elem = fo.length ? fo[0] : mouse_target;\n
\t\t\t\t\t\n
\t\t\t\t\t// Get center of source element\n
\t\t\t\t\tvar bb = svgCanvas.getStrokedBBox([start_elem]);\n
\t\t\t\t\tvar x = bb.x + bb.width/2;\n
\t\t\t\t\tvar y = bb.y + bb.height/2;\n
\t\t\t\t\t\n
\t\t\t\t\tstarted = true;\n
\t\t\t\t\tcur_line = addElem({\n
\t\t\t\t\t\t"element": "polyline",\n
\t\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t\t"points": (x+\',\'+y+\' \'+x+\',\'+y+\' \'+start_x+\',\'+start_y),\n
\t\t\t\t\t\t\t"stroke": \'#\' + curConfig.initStroke.color,\n
\t\t\t\t\t\t\t"stroke-width": (!start_elem.stroke_width || start_elem.stroke_width == 0) ? curConfig.initStroke.width : start_elem.stroke_width,\n
\t\t\t\t\t\t\t"fill": "none",\n
\t\t\t\t\t\t\t"opacity": curConfig.initStroke.opacity,\n
\t\t\t\t\t\t\t"style": "pointer-events:none"\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t\t$(cur_line).data(\'start_bb\', bb);\n
\t\t\t\t}\n
\t\t\t\treturn {\n
\t\t\t\t\tstarted: true\n
\t\t\t\t};\n
\t\t\t} else if(mode == "select") {\n
\t\t\t\tfindConnectors();\n
\t\t\t}\n
\t\t},\n
\t\tmouseMove: function(opts) {\n
\t\t\tvar zoom = svgCanvas.getZoom();\n
\t\t\tvar e = opts.event;\n
\t\t\tvar x = opts.mouse_x/zoom;\n
\t\t\tvar y = opts.mouse_y/zoom;\n
\t\t\t\n
\t\t\tvar\tdiff_x = x - start_x,\n
\t\t\t\tdiff_y = y - start_y;\n
\t\t\t\t\t\t\t\t\n
\t\t\tvar mode = svgCanvas.getMode();\n
\t\t\t\n
\t\t\tif(mode == "connector" && started) {\n
\t\t\t\t\n
\t\t\t\tvar sw = cur_line.getAttribute(\'stroke-width\') * 3;\n
\t\t\t\t// Set start point (adjusts based on bb)\n
\t\t\t\tvar pt = getBBintersect(x, y, $(cur_line).data(\'start_bb\'), getOffset(\'start\', cur_line));\n
\t\t\t\tstart_x = pt.x;\n
\t\t\t\tstart_y = pt.y;\n
\t\t\t\t\n
\t\t\t\tsetPoint(cur_line, 0, pt.x, pt.y, true);\n
\t\t\t\t\n
\t\t\t\t// Set end point\n
\t\t\t\tsetPoint(cur_line, \'end\', x, y, true);\n
\t\t\t} else if(mode == "select") {\n
\t\t\t\tvar slen = selElems.length;\n
\t\t\t\t\n
\t\t\t\twhile(slen--) {\n
\t\t\t\t\tvar elem = selElems[slen];\n
\t\t\t\t\t// Look for selected connector elements\n
\t\t\t\t\tif(elem && $(elem).data(\'c_start\')) {\n
\t\t\t\t\t\t// Remove the "translate" transform given to move\n
\t\t\t\t\t\tsvgCanvas.removeFromSelection([elem]);\n
\t\t\t\t\t\tsvgCanvas.getTransformList(elem).clear();\n
\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tif(connections.length) {\n
\t\t\t\t\tupdateLine(diff_x, diff_y);\n
\n
\t\t\t\t\t\n
\t\t\t\t}\n
\t\t\t} \n
\t\t},\n
\t\tmouseUp: function(opts) {\n
\t\t\tvar zoom = svgCanvas.getZoom();\n
\t\t\tvar e = opts.event,\n
\t\t\t\tx = opts.mouse_x/zoom,\n
\t\t\t\ty = opts.mouse_y/zoom,\n
\t\t\t\tmouse_target = e.target;\n
\t\t\t\n
\t\t\tif(svgCanvas.getMode() == "connector") {\n
\t\t\t\tvar fo = $(mouse_target).closest("foreignObject");\n
\t\t\t\tif(fo.length) mouse_target = fo[0];\n
\t\t\t\t\n
\t\t\t\tvar parents = $(mouse_target).parents();\n
\n
\t\t\t\tif(mouse_target == start_elem) {\n
\t\t\t\t\t// Start line through click\n
\t\t\t\t\tstarted = true;\n
\t\t\t\t\treturn {\n
\t\t\t\t\t\tkeep: true,\n
\t\t\t\t\t\telement: null,\n
\t\t\t\t\t\tstarted: started\n
\t\t\t\t\t}\t\t\t\t\t\t\n
\t\t\t\t} else if($.inArray(svgcontent, parents) === -1) {\n
\t\t\t\t\t// Not a valid target element, so remove line\n
\t\t\t\t\t$(cur_line).remove();\n
\t\t\t\t\tstarted = false;\n
\t\t\t\t\treturn {\n
\t\t\t\t\t\tkeep: false,\n
\t\t\t\t\t\telement: null,\n
\t\t\t\t\t\tstarted: started\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\t// Valid end element\n
\t\t\t\t\tend_elem = mouse_target;\n
\t\t\t\t\t\n
\t\t\t\t\tvar start_id = start_elem.id, end_id = end_elem.id;\n
\t\t\t\t\tvar conn_str = start_id + " " + end_id;\n
\t\t\t\t\tvar alt_str = end_id + " " + start_id;\n
\t\t\t\t\t// Don\'t create connector if one already exists\n
\t\t\t\t\tvar dupe = $(svgcontent).find(conn_sel).filter(function() {\n
\t\t\t\t\t\tvar conn = this.getAttributeNS(se_ns, "connector");\n
\t\t\t\t\t\tif(conn == conn_str || conn == alt_str) return true;\n
\t\t\t\t\t});\n
\t\t\t\t\tif(dupe.length) {\n
\t\t\t\t\t\t$(cur_line).remove();\n
\t\t\t\t\t\treturn {\n
\t\t\t\t\t\t\tkeep: false,\n
\t\t\t\t\t\t\telement: null,\n
\t\t\t\t\t\t\tstarted: false\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tvar bb = svgCanvas.getStrokedBBox([end_elem]);\n
\t\t\t\t\t\n
\t\t\t\t\tvar pt = getBBintersect(start_x, start_y, bb, getOffset(\'start\', cur_line));\n
\t\t\t\t\tsetPoint(cur_line, \'end\', pt.x, pt.y, true);\n
\t\t\t\t\t$(cur_line)\n
\t\t\t\t\t\t.data("c_start", start_id)\n
\t\t\t\t\t\t.data("c_end", end_id)\n
\t\t\t\t\t\t.data("end_bb", bb);\n
\t\t\t\t\tse_ns = svgCanvas.getEditorNS(true);\n
\t\t\t\t\tcur_line.setAttributeNS(se_ns, "se:connector", conn_str);\n
\t\t\t\t\tcur_line.setAttribute(\'class\', conn_sel.substr(1));\n
\t\t\t\t\tcur_line.setAttribute(\'opacity\', 1);\n
\t\t\t\t\tsvgCanvas.addToSelection([cur_line]);\n
\t\t\t\t\tsvgCanvas.moveToBottomSelectedElement();\n
\t\t\t\t\tselManager.requestSelector(cur_line).showGrips(false);\n
\t\t\t\t\tstarted = false;\n
\t\t\t\t\treturn {\n
\t\t\t\t\t\tkeep: true,\n
\t\t\t\t\t\telement: cur_line,\n
\t\t\t\t\t\tstarted: started\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\tselectedChanged: function(opts) {\n
\t\t\t\n
\t\t\t// Use this to update the current selected elements\n
\t\t\tselElems = opts.elems;\n
\t\t\t\n
\t\t\tvar i = selElems.length;\n
\t\t\t\n
\t\t\twhile(i--) {\n
\t\t\t\tvar elem = selElems[i];\n
\t\t\t\tif(elem && $(elem).data(\'c_start\')) {\n
\t\t\t\t\tselManager.requestSelector(elem).showGrips(false);\n
\t\t\t\t\tif(opts.selectedElement && !opts.multiselected) {\n
\t\t\t\t\t\t// TODO: Set up context tools and hide most regular line tools\n
\t\t\t\t\t\tshowPanel(true);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tshowPanel(false);\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tshowPanel(false);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\tupdateConnectors();\n
\t\t},\n
\t\telementChanged: function(opts) {\n
\t\t\tvar elem = opts.elems[0];\n
\t\t\tif (elem && elem.tagName == \'svg\' && elem.id == "svgcontent") {\n
\t\t\t\t// Update svgcontent (can change on import)\n
\t\t\t\tsvgcontent = elem;\n
\t\t\t\tinit();\n
\t\t\t}\n
\t\t\t\n
\t\t\t// Has marker, so change offset\n
\t\t\tif(elem && (\n
\t\t\t\telem.getAttribute("marker-start") ||\n
\t\t\t\telem.getAttribute("marker-mid") ||\n
\t\t\t\telem.getAttribute("marker-end")\n
\t\t\t)) {\n
\t\t\t\tvar start = elem.getAttribute("marker-start");\n
\t\t\t\tvar mid = elem.getAttribute("marker-mid");\n
\t\t\t\tvar end = elem.getAttribute("marker-end");\n
\t\t\t\tcur_line = elem;\n
\t\t\t\t$(elem)\n
\t\t\t\t\t.data("start_off", !!start)\n
\t\t\t\t\t.data("end_off", !!end);\n
\t\t\t\t\n
\t\t\t\tif(elem.tagName == "line" && mid) {\n
\t\t\t\t\t// Convert to polyline to accept mid-arrow\n
\t\t\t\t\t\n
\t\t\t\t\tvar x1 = elem.getAttribute(\'x1\')-0;\n
\t\t\t\t\tvar x2 = elem.getAttribute(\'x2\')-0;\n
\t\t\t\t\tvar y1 = elem.getAttribute(\'y1\')-0;\n
\t\t\t\t\tvar y2 = elem.getAttribute(\'y2\')-0;\n
\t\t\t\t\tvar id = elem.id;\n
\t\t\t\t\t\n
\t\t\t\t\tvar mid_pt = (\' \'+((x1+x2)/2)+\',\'+((y1+y2)/2) + \' \');\n
\t\t\t\t\tvar pline = addElem({\n
\t\t\t\t\t\t"element": "polyline",\n
\t\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t\t"points": (x1+\',\'+y1+ mid_pt +x2+\',\'+y2),\n
\t\t\t\t\t\t\t"stroke": elem.getAttribute(\'stroke\'),\n
\t\t\t\t\t\t\t"stroke-width": elem.getAttribute(\'stroke-width\'),\n
\t\t\t\t\t\t\t"marker-mid": mid,\n
\t\t\t\t\t\t\t"fill": "none",\n
\t\t\t\t\t\t\t"opacity": elem.getAttribute(\'opacity\') || 1\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t\t$(elem).after(pline).remove();\n
\t\t\t\t\tsvgCanvas.clearSelection();\n
\t\t\t\t\tpline.id = id;\n
\t\t\t\t\tsvgCanvas.addToSelection([pline]);\n
\t\t\t\t\telem = pline;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t// Update line if it\'s a connector\n
\t\t\tif(elem.getAttribute(\'class\') == conn_sel.substr(1)) {\n
\t\t\t\tvar start = getElem($(elem).data(\'c_start\'));\n
\t\t\t\tupdateConnectors([start]);\n
\t\t\t} else {\n
\t\t\t\tupdateConnectors();\n
\t\t\t}\n
\t\t},\n
\t\ttoolButtonStateUpdate: function(opts) {\n
\t\t\tif(opts.nostroke) {\n
\t\t\t\tif ($(\'#mode_connect\').hasClass(\'tool_button_current\')) {\n
\t\t\t\t\tclickSelect();\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t$(\'#mode_connect\')\n
\t\t\t\t.toggleClass(\'disabled\',opts.nostroke);\n
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
            <value> <int>15647</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
