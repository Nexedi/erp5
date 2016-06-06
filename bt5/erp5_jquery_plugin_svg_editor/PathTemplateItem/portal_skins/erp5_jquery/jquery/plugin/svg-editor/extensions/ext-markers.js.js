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
            <value> <string>ts27579594.61</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-markers.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * ext-markers.js\n
 *\n
 * Licensed under the Apache License, Version 2\n
 *\n
 * Copyright(c) 2010 Will Schleter \n
 *   based on ext-arrows.js by Copyright(c) 2010 Alexis Deveria\n
 *\n
 * This extension provides for the addition of markers to the either end\n
 * or the middle of a line, polyline, path, polygon. \n
 * \n
 * Markers may be either a graphic or arbitary text\n
 * \n
 * to simplify the coding and make the implementation as robust as possible,\n
 * markers are not shared - every object has its own set of markers.\n
 * this relationship is maintained by a naming convention between the\n
 * ids of the markers and the ids of the object\n
 * \n
 * The following restrictions exist for simplicty of use and programming\n
 *    objects and their markers to have the same color\n
 *    marker size is fixed\n
 *    text marker font, size, and attributes are fixed\n
 *    an application specific attribute - se_type - is added to each marker element\n
 *        to store the type of marker\n
 *        \n
 * TODO:\n
 *    remove some of the restrictions above\n
 *    add option for keeping text aligned to horizontal\n
 *    add support for dimension extension lines\n
 *\n
 */\n
\n
svgEditor.addExtension("Markers", function(S) {\n
\tvar svgcontent = S.svgcontent,\n
\taddElem = S.addSvgElementFromJson,\n
\tselElems;\n
\n
\tvar mtypes = [\'start\',\'mid\',\'end\'];\n
\n
\tvar marker_prefix = \'se_marker_\';\n
\tvar id_prefix = \'mkr_\';\n
\t\t\n
\t// note - to add additional marker types add them below with a unique id\n
\t// and add the associated icon(s) to marker-icons.svg\n
\t// the geometry is normallized to a 100x100 box with the origin at lower left\n
\t// Safari did not like negative values for low left of viewBox\n
\t// remember that the coordinate system has +y downward\n
\tvar marker_types = {\n
\t\tnomarker: {},  \n
\t\tleftarrow:  \n
\t\t\t{element:\'path\', attr:{d:\'M0,50 L100,90 L70,50 L100,10 Z\'}},\n
\t\trightarrow:\n
\t\t\t{element:\'path\', attr:{d:\'M100,50 L0,90 L30,50 L0,10 Z\'}},\n
\t\ttextmarker:\n
\t\t\t{element:\'text\', attr: {x:0, y:0,\'stroke-width\':0,\'stroke\':\'none\',\'font-size\':75,\'font-family\':\'serif\',\'text-anchor\':\'left\',\n
\t\t\t\t\'xml:space\': \'preserve\'}},\n
\t\tforwardslash:\n
\t\t\t{element:\'path\', attr:{d:\'M30,100 L70,0\'}},\n
\t\treverseslash:\n
\t\t\t{element:\'path\', attr:{d:\'M30,0 L70,100\'}},\n
\t\tverticalslash:\n
\t\t\t{element:\'path\', attr:{d:\'M50,0 L50,100\'}},\n
\t\tbox:\n
\t\t\t{element:\'path\', attr:{d:\'M20,20 L20,80 L80,80 L80,20 Z\'}},\n
\t\tstar:\n
\t\t\t{element:\'path\', attr:{d:\'M10,30 L90,30 L20,90 L50,10 L80,90 Z\'}},\n
\t\txmark:\n
\t\t\t{element:\'path\', attr:{d:\'M20,80 L80,20 M80,80 L20,20\'}},\n
\t\ttriangle:\n
\t\t\t{element:\'path\', attr:{d:\'M10,80 L50,20 L80,80 Z\'}},\n
\t\tmcircle:\n
\t\t\t{element:\'circle\', attr:{r:30, cx:50, cy:50}},\t\t\t\n
\t}\n
\t\n
\t\n
\tvar lang_list = {\n
\t\t"en":[\n
\t\t\t{id: "start_marker_list", title: "Select start marker type" },\n
\t\t\t{id: "mid_marker_list", title: "Select mid marker type" },\n
\t\t\t{id: "end_marker_list", title: "Select end marker type" },\n
\t\t\t{id: "nomarker", title: "No Marker" },\n
\t\t\t{id: "leftarrow", title: "Left Arrow" },\n
\t\t\t{id: "rightarrow", title: "Right Arrow" },\n
\t\t\t{id: "textmarker", title: "Text Marker" },\n
\t\t\t{id: "forwardslash", title: "Forward Slash" },\n
\t\t\t{id: "reverseslash", title: "Reverse Slash" },\n
\t\t\t{id: "verticalslash", title: "Vertical Slash" },\n
\t\t\t{id: "box", title: "Box" },\n
\t\t\t{id: "star", title: "Star" },\n
\t\t\t{id: "xmark", title: "X" },\n
\t\t\t{id: "triangle", title: "Triangle" },\n
\t\t\t{id: "mcircle", title: "Circle" },\n
\t\t\t{id: "leftarrow_o", title: "Open Left Arrow" },\n
\t\t\t{id: "rightarrow_o", title: "Open Right Arrow" },\n
\t\t\t{id: "box_o", title: "Open Box" },\n
\t\t\t{id: "star_o", title: "Open Star" },\n
\t\t\t{id: "triangle_o", title: "Open Triangle" },\n
\t\t\t{id: "mcircle_o", title: "Open Circle" },\n
\t\t]\n
\t};\n
\n
\n
\t// duplicate shapes to support unfilled (open) marker types with an _o suffix\n
\t$.each([\'leftarrow\',\'rightarrow\',\'box\',\'star\',\'mcircle\',\'triangle\'],function(i,v) {\n
\t\tmarker_types[v+\'_o\'] = marker_types[v];\n
\t});\n
\t\n
\t// elem = a graphic element will have an attribute like marker-start\n
\t// attr - marker-start, marker-mid, or marker-end\n
\t// returns the marker element that is linked to the graphic element\n
\tfunction getLinked(elem, attr) {\n
\t\tvar str = elem.getAttribute(attr);\n
\t\tif(!str) return null;\n
\t\tvar m = str.match(/\\(\\#(.*)\\)/);\n
\t\tif(!m || m.length !== 2) {\n
\t\t\treturn null;\n
\t\t}\n
\t\treturn S.getElem(m[1]);\n
\t}\n
\n
\t//toggles context tool panel off/on\n
\t//sets the controls with the selected element\'s settings\n
\tfunction showPanel(on) {\n
\t\t$(\'#marker_panel\').toggle(on);\n
\n
\t\tif(on) {\n
\t\t\tvar el = selElems[0];\n
\t\t\tvar val;\n
\t\t\tvar ci;\n
\n
\t\t\t$.each(mtypes, function(i, pos) {\n
\t\t\t\tvar m=getLinked(el,"marker-"+pos);\n
\t\t\t\tvar txtbox = $(\'#\'+pos+\'_marker\');\n
\t\t\t\tif (!m) {\n
\t\t\t\t\tval=\'\\\\nomarker\';\n
\t\t\t\t\tci=val;\n
\t\t\t\t\ttxtbox.hide() // hide text box\n
\t\t\t\t} else {\n
\t\t\t\t\tif (!m.attributes.se_type) return; // not created by this extension\n
\t\t\t\t\tval=\'\\\\\'+m.attributes.se_type.textContent;\n
\t\t\t\t\tci=val;\n
\t\t\t\t\tif (val==\'\\\\textmarker\') {\n
\t\t\t\t\t\tval=m.lastChild.textContent;\n
\t\t\t\t\t\t//txtbox.show(); // show text box\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\ttxtbox.hide() // hide text box\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\ttxtbox.val(val);\t\t\t\t\n
\t\t\t\tsetIcon(pos,ci);\n
\t\t\t})\n
\t\t}\n
\t}\t\n
\n
\tfunction addMarker(id, val) {\n
\t\tvar txt_box_bg = \'#ffffff\';\n
\t\tvar txt_box_border = \'none\';\n
\t\tvar txt_box_stroke_width = 0;\n
\t\t\n
\t\tvar marker = S.getElem(id);\n
\n
\t\tif (marker) return;\n
\n
\t\tif (val==\'\' || val==\'\\\\nomarker\') return;\n
\n
\t\tvar el = selElems[0];\t\t \n
\t\tvar color = el.getAttribute(\'stroke\');\n
\t\t//NOTE: Safari didn\'t like a negative value in viewBox\n
\t\t//so we use a standardized 0 0 100 100\n
\t\t//with 50 50 being mapped to the marker position\n
\t\tvar refX = 50;\n
\t\tvar refY = 50;\n
\t\tvar viewBox = "0 0 100 100";\n
\t\tvar markerWidth = 5;\n
\t\tvar markerHeight = 5;\n
\t\tvar strokeWidth = 10;\n
\t\tif (val.substr(0,1)==\'\\\\\') se_type=val.substr(1);\n
\t\telse se_type=\'textmarker\';\n
\n
\t\tif (!marker_types[se_type]) return; // an unknown type!\n
\t\t\n
 \t\t// create a generic marker\n
\t\tmarker = addElem({\n
\t\t\t"element": "marker",\n
\t\t\t"attr": {\n
\t\t\t"id": id,\n
\t\t\t"markerUnits": "strokeWidth",\n
\t\t\t"orient": "auto",\n
\t\t\t"style": "pointer-events:none",\n
\t\t\t"se_type": se_type\n
\t\t}\n
\t\t});\n
\n
\t\tif (se_type!=\'textmarker\') {\n
\t\t\tvar mel = addElem(marker_types[se_type]);\n
\t\t\tvar fillcolor = color;\n
\t\t\tif (se_type.substr(-2)==\'_o\') fillcolor=\'none\';\n
\t\t\tmel.setAttribute(\'fill\',fillcolor);\n
\t\t\tmel.setAttribute(\'stroke\',color);\n
\t\t\tmel.setAttribute(\'stroke-width\',strokeWidth);\n
\t\t\tmarker.appendChild(mel);\n
\t\t} else {\n
\t\t\tvar text = addElem(marker_types[se_type]);\n
\t\t\t// have to add text to get bounding box\n
\t\t\ttext.textContent = val;\n
\t\t\tvar tb=text.getBBox();\n
\t\t\t//alert( tb.x + " " + tb.y + " " + tb.width + " " + tb.height);\n
\t\t\tvar pad=1;\n
\t\t\tvar bb = tb;\n
\t\t\tbb.x = 0;\n
\t\t\tbb.y = 0;\n
\t\t\tbb.width += pad*2;\n
\t\t\tbb.height += pad*2;\n
\t\t\t// shift text according to its size\n
\t\t\ttext.setAttribute(\'x\', pad);\n
\t\t\ttext.setAttribute(\'y\', bb.height - pad - tb.height/4); // kludge?\n
\t\t\ttext.setAttribute(\'fill\',color);\n
\t\t\trefX = bb.width/2+pad;\n
\t\t\trefY = bb.height/2+pad;\n
\t\t\tviewBox = bb.x + " " + bb.y + " " + bb.width + " " + bb.height;\n
\t\t\tmarkerWidth =bb.width/10;\n
\t\t\tmarkerHeight = bb.height/10;\n
\n
\t\t\tvar box = addElem({\n
\t\t\t\t"element": "rect",\n
\t\t\t\t"attr": {\n
\t\t\t\t"x": bb.x,\n
\t\t\t\t"y": bb.y,\n
\t\t\t\t"width": bb.width,\n
\t\t\t\t"height": bb.height,\n
\t\t\t\t"fill": txt_box_bg,\n
\t\t\t\t"stroke": txt_box_border,\n
\t\t\t\t"stroke-width": txt_box_stroke_width\n
\t\t\t}\n
\t\t\t});\n
\t\t\tmarker.setAttribute("orient",0);\n
\t\t\tmarker.appendChild(box);\n
\t\t\tmarker.appendChild(text);\n
\t\t} \n
\n
\t\tmarker.setAttribute("viewBox",viewBox);\n
\t\tmarker.setAttribute("markerWidth", markerWidth);\n
\t\tmarker.setAttribute("markerHeight", markerHeight);\n
\t\tmarker.setAttribute("refX", refX);\n
\t\tmarker.setAttribute("refY", refY);\n
\t\tS.findDefs().appendChild(marker);\n
\n
\t\treturn marker;\n
\t}\n
\n
\n
\tfunction setMarker() {\n
\t\tvar poslist={\'start_marker\':\'start\',\'mid_marker\':\'mid\',\'end_marker\':\'end\'};\n
\t\tvar pos = poslist[this.id];\n
\t\tvar marker_name = \'marker-\'+pos;\n
\t\tvar val = this.value;\n
\t\tvar el = selElems[0];\n
\t\tvar marker = getLinked(el, marker_name);\n
\t\tif (marker) $(marker).remove();\n
\t\tel.removeAttribute(marker_name);\n
\t\tif (val==\'\') val=\'\\\\nomarker\';\n
\t\tif (val==\'\\\\nomarker\') {\n
\t\t\tsetIcon(pos,val);\n
\t\t\tS.call("changed", selElems);\n
\t\t\treturn;\n
\t\t}\n
\t\t// Set marker on element\n
\t\tvar id = marker_prefix + pos + \'_\' + el.id;\n
\t\taddMarker(id, val);\n
\t\tsvgCanvas.changeSelectedAttribute(marker_name, "url(#" + id + ")");\n
\t\tif (el.tagName == "line" && pos==\'mid\') el=convertline(el);\n
\t\tS.call("changed", selElems);\n
\t\tsetIcon(pos,val);\n
\t}\n
\n
\tfunction convertline(elem) {\n
\t\t// this routine came from the connectors extension\n
\t\t// it is needed because midpoint markers don\'t work with line elements\n
\t\tif (!(elem.tagName == "line")) return elem;\n
\n
\t\t// Convert to polyline to accept mid-arrow\n
\n
\t\tvar x1 = elem.getAttribute(\'x1\')-0;\n
\t\tvar x2 = elem.getAttribute(\'x2\')-0;\n
\t\tvar y1 = elem.getAttribute(\'y1\')-0;\n
\t\tvar y2 = elem.getAttribute(\'y2\')-0;\n
\t\tvar id = elem.id;\n
\n
\t\tvar mid_pt = (\' \'+((x1+x2)/2)+\',\'+((y1+y2)/2) + \' \');\n
\t\tvar pline = addElem({\n
\t\t\t"element": "polyline",\n
\t\t\t"attr": {\n
\t\t\t"points": (x1+\',\'+y1+ mid_pt +x2+\',\'+y2),\n
\t\t\t"stroke": elem.getAttribute(\'stroke\'),\n
\t\t\t"stroke-width": elem.getAttribute(\'stroke-width\'),\n
\t\t\t"fill": "none",\n
\t\t\t"opacity": elem.getAttribute(\'opacity\') || 1\n
\t\t}\n
\t\t});\n
\t\t$.each(mtypes, function(i, pos) { // get any existing marker definitions\n
\t\t\tvar nam = \'marker-\'+pos;\n
\t\t\tvar m = elem.getAttribute(nam);\n
\t\t\tif (m) pline.setAttribute(nam,elem.getAttribute(nam));\n
\t\t});\n
\t\t\n
\t\tvar batchCmd = new S.BatchCommand();\n
\t\tbatchCmd.addSubCommand(new S.RemoveElementCommand(elem, elem.parentNode));\n
\t\tbatchCmd.addSubCommand(new S.InsertElementCommand(pline));\n
\t\t\n
\t\t$(elem).after(pline).remove();\n
\t\tsvgCanvas.clearSelection();\n
\t\tpline.id = id;\n
\t\tsvgCanvas.addToSelection([pline]);\n
\t\tS.addCommandToHistory(batchCmd);\n
\t\treturn pline;\n
\t}\n
\n
\t// called when the main system modifies an object\n
\t// this routine changes the associated markers to be the same color\n
\tfunction colorChanged(elem) {\n
\t\tvar color = elem.getAttribute(\'stroke\');\n
\n
\t\t$.each(mtypes, function(i, pos) {\n
\t\t\tvar marker = getLinked(elem, \'marker-\'+pos);\n
\t\t\tif (!marker) return;\n
\t\t\tif (!marker.attributes.se_type) return; //not created by this extension\n
\t\t\tvar ch = marker.lastElementChild;\n
\t\t\tif (!ch) return;\n
\t\t\tvar curfill = ch.getAttribute("fill");\n
\t\t\tvar curstroke = ch.getAttribute("stroke")\n
\t\t\tif (curfill && curfill!=\'none\') ch.setAttribute("fill",color);\n
\t\t\tif (curstroke && curstroke!=\'none\') ch.setAttribute("stroke",color);\n
\t\t});\n
\t}\n
\n
\t// called when the main system creates or modifies an object\n
\t// primary purpose is create new markers for cloned objects\n
\tfunction updateReferences(el) {\n
\t\t$.each(mtypes, function (i,pos) {\n
\t\t\tvar id = marker_prefix + pos + \'_\' + el.id;\n
\t\t\tvar marker_name = \'marker-\'+pos;\n
\t\t\tvar marker = getLinked(el, marker_name);\n
\t\t\tif (!marker || !marker.attributes.se_type) return; //not created by this extension\n
\t\t\tvar url = el.getAttribute(marker_name);\n
\t\t\tif (url) {\n
\t\t\t\tvar len = el.id.length;\n
\t\t\t\tvar linkid = url.substr(-len-1,len);\n
\t\t\t\tif (el.id != linkid) {\n
\t\t\t\t\tvar val = $(\'#\'+pos+\'_marker\').attr(\'value\');\n
\t\t\t\t\taddMarker(id, val);\n
\t\t\t\t\tsvgCanvas.changeSelectedAttribute(marker_name, "url(#" + id + ")");\n
\t\t\t\t\tif (el.tagName == "line" && pos==\'mid\') el=convertline(el);\n
\t\t\t\t\tS.call("changed", selElems);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\t}\n
\n
\t// simulate a change event a text box that stores the current element\'s marker type\n
\tfunction triggerTextEntry(pos,val) {\n
\t\t$(\'#\'+pos+\'_marker\').val(val);\n
\t\t$(\'#\'+pos+\'_marker\').change();\n
\t\tvar txtbox = $(\'#\'+pos+\'_marker\');\n
\t\t//if (val.substr(0,1)==\'\\\\\') txtbox.hide();\n
\t\t//else txtbox.show();\n
\t}\n
\t\n
\tfunction setIcon(pos,id) {\n
\t\tif (id.substr(0,1)!=\'\\\\\') id=\'\\\\textmarker\'\n
\t\tvar ci = \'#\'+id_prefix+pos+\'_\'+id.substr(1);\n
\t\tsvgEditor.setIcon(\'#cur_\' + pos +\'_marker_list\', $(ci).children());\n
\t\t$(ci).addClass(\'current\').siblings().removeClass(\'current\');\n
\t}\n
\t\t\n
\tfunction setMarkerSet(obj) {\n
\t\tvar parts = this.id.split(\'_\');\n
\t\tvar set = parts[2];\n
\t\tswitch (set) {\n
\t\tcase \'off\':\n
\t\t\ttriggerTextEntry(\'start\',\'\\\\nomarker\');\n
\t\t\ttriggerTextEntry(\'mid\',\'\\\\nomarker\');\n
\t\t\ttriggerTextEntry(\'end\',\'\\\\nomarker\');\n
\t\t\tbreak;\n
\t\tcase \'dimension\':\n
\t\t\ttriggerTextEntry(\'start\',\'\\\\leftarrow\');\n
\t\t\ttriggerTextEntry(\'end\',\'\\\\rightarrow\');\n
\t\t\tshowTextPrompt(\'mid\');\n
\t\t\tbreak;\n
\t\tcase \'label\':\n
\t\t\ttriggerTextEntry(\'mid\',\'\\\\nomarker\');\n
\t\t\ttriggerTextEntry(\'end\',\'\\\\rightarrow\');\n
\t\t\tshowTextPrompt(\'start\');\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\t\t\n
\tfunction showTextPrompt(pos) {\n
\t\tvar def = $(\'#\'+pos+\'_marker\').val();\n
\t\tif (def.substr(0,1)==\'\\\\\') def=\'\';\n
\t\t$.prompt(\'Enter text for \' + pos + \' marker\', def , function(txt) { if (txt) triggerTextEntry(pos,txt); });\n
\t}\n
\t\n
\t// callback function for a toolbar button click\n
\tfunction setArrowFromButton(obj) {\n
\t\t\n
\t\tvar parts = this.id.split(\'_\');\n
\t\tvar pos = parts[1];\n
\t\tvar val = parts[2];\n
\t\tif (parts[3]) val+=\'_\'+parts[3];\n
\t\t\n
\t\tif (val!=\'textmarker\') {\n
\t\t\ttriggerTextEntry(pos,\'\\\\\'+val);\n
\t\t} else {\n
\t\t\tshowTextPrompt(pos);\n
\t\t}\n
\t}\n
\t\n
\tfunction getTitle(lang,id) {\n
\t\tvar list = lang_list[lang];\n
\t\tfor (var i in list) {\n
\t\t\tif (list[i].id==id) return list[i].title;\n
\t\t}\n
\t\treturn id;\n
\t}\n
\t\n
\t\n
\t// build the toolbar button array from the marker definitions\n
\t// TODO: need to incorporate language specific titles\n
\tfunction buildButtonList() {\n
\t\tvar buttons=[];\n
\t\tvar i=0;\n
/*\n
\t\tbuttons.push({\n
\t\t\tid:id_prefix + \'markers_off\',\n
\t\t\ttitle:\'Turn off all markers\',\n
\t\t\ttype:\'context\',\n
\t\t\tevents: { \'click\': setMarkerSet },\n
\t\t\tpanel: \'marker_panel\'\n
\t\t});\n
\t\tbuttons.push({\n
\t\t\tid:id_prefix + \'markers_dimension\',\n
\t\t\ttitle:\'Dimension\',\n
\t\t\ttype:\'context\',\n
\t\t\tevents: { \'click\': setMarkerSet },\n
\t\t\tpanel: \'marker_panel\'\n
\t\t});\n
\t\tbuttons.push({\n
\t\t\tid:id_prefix + \'markers_label\',\n
\t\t\ttitle:\'Label\',\n
\t\t\ttype:\'context\',\n
\t\t\tevents: { \'click\': setMarkerSet },\n
\t\t\tpanel: \'marker_panel\'\n
\t\t});\n
*/\n
\t\t$.each(mtypes,function(k,pos) {\n
\t\t\tvar listname = pos + "_marker_list";\n
\t\t\tvar def = true;\n
\t\t$.each(marker_types,function(id,v) {\n
\t\t\tvar title = getTitle(\'en\',id);\n
\t\t\tbuttons.push({\n
\t\t\t\t\tid:id_prefix + pos + "_" + id,\n
\t\t\t\t\tsvgicon:id,\n
\t\t\t\t\ttitle:title,\n
\t\t\t\t\ttype:\'context\',\n
\t\t\t\t\tevents: { \'click\': setArrowFromButton },\n
\t\t\t\t\tpanel:\'marker_panel\',\n
\t\t\t\t\tlist: listname,\n
\t\t\t\t\tisDefault: def\n
\t\t\t});\n
\t\t\tdef = false;\n
\t\t});\n
\t\t});\n
\t\treturn buttons;\n
\t}\n
\n
\treturn {\n
\t\tname: "Markers",\n
\t\tsvgicons: "jquery/plugin/svg-editor/extensions/markers-icons.xml",\n
\t\tbuttons: buildButtonList(),\n
\t\tcontext_tools: [\n
\t\t   {\n
\t\t\ttype: "input",\n
\t\t\tpanel: "marker_panel",\n
\t\t\ttitle: "Start marker",\n
\t\t\tid: "start_marker",\n
\t\t\tlabel: "s",\n
\t\t\tsize: 3,\n
\t\t\tevents: { change: setMarker }\n
\t\t},{\n
\t\t\ttype: "button-select",\n
\t\t\tpanel: "marker_panel",\n
\t\t\ttitle: getTitle(\'en\',\'start_marker_list\'),\n
\t\t\tid: "start_marker_list",\n
\t\t\tcolnum: 3,\n
\t\t\tevents: { change: setArrowFromButton }\n
\t\t},{\n
\t\t\ttype: "input",\n
\t\t\tpanel: "marker_panel",\n
\t\t\ttitle: "Middle marker",\n
\t\t\tid: "mid_marker",\n
\t\t\tlabel: "m",\n
\t\t\tdefval: "",\n
\t\t\tsize: 3,\n
\t\t\tevents: { change: setMarker }\n
\t\t},{\n
\t\t\ttype: "button-select",\n
\t\t\tpanel: "marker_panel",\n
\t\t\ttitle: getTitle(\'en\',\'mid_marker_list\'),\n
\t\t\tid: "mid_marker_list",\n
\t\t\tcolnum: 3,\n
\t\t\tevents: { change: setArrowFromButton }\n
\t\t},{\n
\t\t\ttype: "input",\n
\t\t\tpanel: "marker_panel",\n
\t\t\ttitle: "End marker",\n
\t\t\tid: "end_marker",\n
\t\t\tlabel: "e",\n
\t\t\tsize: 3,\n
\t\t\tevents: { change: setMarker }\n
\t\t},{\n
\t\t\ttype: "button-select",\n
\t\t\tpanel: "marker_panel",\n
\t\t\ttitle: getTitle(\'en\',\'end_marker_list\'),\n
\t\t\tid: "end_marker_list",\n
\t\t\tcolnum: 3,\n
\t\t\tevents: { change: setArrowFromButton }\n
\t\t} ],\n
\t\tcallback: function() {\n
\t\t\t$(\'#marker_panel\').addClass(\'toolset\').hide();\n
\t\t\t\n
\t\t},\n
\t\taddLangData: function(lang) {\n
\t\t\treturn { data: lang_list[lang] };\n
\t\t},\n
\n
\tselectedChanged: function(opts) {\n
\t\t// Use this to update the current selected elements\n
\t\t//console.log(\'selectChanged\',opts);\n
\t\tselElems = opts.elems;\n
\n
\t\tvar i = selElems.length;\n
\t\tvar marker_elems = [\'line\',\'path\',\'polyline\',\'polygon\'];\n
\n
\t\twhile(i--) {\n
\t\t\tvar elem = selElems[i];\n
\t\t\tif(elem && $.inArray(elem.tagName, marker_elems) != -1) {\n
\t\t\t\tif(opts.selectedElement && !opts.multiselected) {\n
\t\t\t\t\tshowPanel(true);\n
\t\t\t\t} else {\n
\t\t\t\t\tshowPanel(false);\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tshowPanel(false);\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\telementChanged: function(opts) {\t\t\n
\t\t//console.log(\'elementChanged\',opts);\n
\t\tvar elem = opts.elems[0];\n
\t\tif(elem && (\n
\t\t\t\telem.getAttribute("marker-start") ||\n
\t\t\t\telem.getAttribute("marker-mid") ||\n
\t\t\t\telem.getAttribute("marker-end")\n
\t\t)) {\n
\t\t\tcolorChanged(elem);\n
\t\t\tupdateReferences(elem);\n
\t\t}\n
\t\tchanging_flag = false;\n
\t}\n
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
            <value> <int>16245</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
