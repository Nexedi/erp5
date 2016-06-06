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
            <value> <string>path.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgedit, svgroot*/\n
/*jslint vars: true, eqeq: true, continue: true*/\n
/**\n
 * Package: svgedit.path\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2011 Alexis Deveria\n
 * Copyright(c) 2011 Jeff Schiller\n
 */\n
\n
// Dependencies:\n
// 1) jQuery\n
// 2) browser.js\n
// 3) math.js\n
// 4) svgutils.js\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.path) {\n
\tsvgedit.path = {};\n
}\n
\n
var NS = svgedit.NS;\n
var uiStrings = {\n
\t\'pathNodeTooltip\': \'Drag node to move it. Double-click node to change segment type\',\n
\t\'pathCtrlPtTooltip\': \'Drag control point to adjust curve properties\'\n
};\n
\n
var segData = {\n
\t2: [\'x\', \'y\'],\n
\t4: [\'x\', \'y\'],\n
\t6: [\'x\', \'y\', \'x1\', \'y1\', \'x2\', \'y2\'],\n
\t8: [\'x\', \'y\', \'x1\', \'y1\'],\n
\t10: [\'x\', \'y\', \'r1\', \'r2\', \'angle\', \'largeArcFlag\', \'sweepFlag\'],\n
\t12: [\'x\'],\n
\t14: [\'y\'],\n
\t16: [\'x\', \'y\', \'x2\', \'y2\'],\n
\t18: [\'x\', \'y\']\n
};\n
\n
var pathFuncs = [];\n
\n
var link_control_pts = true;\n
\n
// Stores references to paths via IDs.\n
// TODO: Make this cross-document happy.\n
var pathData = {};\n
\n
svgedit.path.setLinkControlPoints = function(lcp) {\n
\tlink_control_pts = lcp;\n
};\n
\n
svgedit.path.path = null;\n
\n
var editorContext_ = null;\n
\n
svgedit.path.init = function(editorContext) {\n
\teditorContext_ = editorContext;\n
\n
\tpathFuncs = [0, \'ClosePath\'];\n
\tvar pathFuncsStrs = [\'Moveto\', \'Lineto\', \'CurvetoCubic\', \'CurvetoQuadratic\', \'Arc\',\n
\t\t\'LinetoHorizontal\', \'LinetoVertical\', \'CurvetoCubicSmooth\', \'CurvetoQuadraticSmooth\'];\n
\t$.each(pathFuncsStrs, function(i, s) {\n
\t\tpathFuncs.push(s+\'Abs\');\n
\t\tpathFuncs.push(s+\'Rel\');\n
\t});\n
};\n
\n
svgedit.path.insertItemBefore = function(elem, newseg, index) {\n
\t// Support insertItemBefore on paths for FF2\n
\tvar list = elem.pathSegList;\n
\n
\tif (svgedit.browser.supportsPathInsertItemBefore()) {\n
\t\tlist.insertItemBefore(newseg, index);\n
\t\treturn;\n
\t}\n
\tvar len = list.numberOfItems;\n
\tvar arr = [];\n
\tvar i;\n
\tfor (i=0; i < len; i++) {\n
\t\tvar cur_seg = list.getItem(i);\n
\t\tarr.push(cur_seg);\n
\t}\n
\tlist.clear();\n
\tfor (i=0; i < len; i++) {\n
\t\tif (i == index) { //index+1\n
\t\t\tlist.appendItem(newseg);\n
\t\t}\n
\t\tlist.appendItem(arr[i]);\n
\t}\n
};\n
\n
// TODO: See if this should just live in replacePathSeg\n
svgedit.path.ptObjToArr = function(type, seg_item) {\n
\tvar arr = segData[type], len = arr.length;\n
\tvar i, out = [];\n
\tfor (i = 0; i < len; i++) {\n
\t\tout[i] = seg_item[arr[i]];\n
\t}\n
\treturn out;\n
};\n
\n
svgedit.path.getGripPt = function(seg, alt_pt) {\n
\tvar out = {\n
\t\tx: alt_pt? alt_pt.x : seg.item.x,\n
\t\ty: alt_pt? alt_pt.y : seg.item.y\n
\t}, path = seg.path;\n
\n
\tif (path.matrix) {\n
\t\tvar pt = svgedit.math.transformPoint(out.x, out.y, path.matrix);\n
\t\tout = pt;\n
\t}\n
\n
\tout.x *= editorContext_.getCurrentZoom();\n
\tout.y *= editorContext_.getCurrentZoom();\n
\n
\treturn out;\n
};\n
\n
svgedit.path.getPointFromGrip = function(pt, path) {\n
\tvar out = {\n
\t\tx: pt.x,\n
\t\ty: pt.y\n
\t};\n
\n
\tif (path.matrix) {\n
\t\tpt = svgedit.math.transformPoint(out.x, out.y, path.imatrix);\n
\t\tout.x = pt.x;\n
\t\tout.y = pt.y;\n
\t}\n
\n
\tout.x /= editorContext_.getCurrentZoom();\n
\tout.y /= editorContext_.getCurrentZoom();\n
\n
\treturn out;\n
};\n
\n
svgedit.path.addPointGrip = function(index, x, y) {\n
\t// create the container of all the point grips\n
\tvar pointGripContainer = svgedit.path.getGripContainer();\n
\n
\tvar pointGrip = svgedit.utilities.getElem(\'pathpointgrip_\'+index);\n
\t// create it\n
\tif (!pointGrip) {\n
\t\tpointGrip = document.createElementNS(NS.SVG, \'circle\');\n
\t\tsvgedit.utilities.assignAttributes(pointGrip, {\n
\t\t\t\'id\': \'pathpointgrip_\' + index,\n
\t\t\t\'display\': \'none\',\n
\t\t\t\'r\': 4,\n
\t\t\t\'fill\': \'#0FF\',\n
\t\t\t\'stroke\': \'#00F\',\n
\t\t\t\'stroke-width\': 2,\n
\t\t\t\'cursor\': \'move\',\n
\t\t\t\'style\': \'pointer-events:all\',\n
\t\t\t\'xlink:title\': uiStrings.pathNodeTooltip\n
\t\t});\n
\t\tpointGrip = pointGripContainer.appendChild(pointGrip);\n
\n
\t\tvar grip = $(\'#pathpointgrip_\'+index);\n
\t\tgrip.dblclick(function() {\n
\t\t\tif (svgedit.path.path) {\n
\t\t\t\tsvgedit.path.path.setSegType();\n
\t\t\t}\n
\t\t});\n
\t}\n
\tif (x && y) {\n
\t\t// set up the point grip element and display it\n
\t\tsvgedit.utilities.assignAttributes(pointGrip, {\n
\t\t\t\'cx\': x,\n
\t\t\t\'cy\': y,\n
\t\t\t\'display\': \'inline\'\n
\t\t});\n
\t}\n
\treturn pointGrip;\n
};\n
\n
svgedit.path.getGripContainer = function() {\n
\tvar c = svgedit.utilities.getElem(\'pathpointgrip_container\');\n
\tif (!c) {\n
\t\tvar parent = svgedit.utilities.getElem(\'selectorParentGroup\');\n
\t\tc = parent.appendChild(document.createElementNS(NS.SVG, \'g\'));\n
\t\tc.id = \'pathpointgrip_container\';\n
\t}\n
\treturn c;\n
};\n
\n
svgedit.path.addCtrlGrip = function(id) {\n
\tvar pointGrip = svgedit.utilities.getElem(\'ctrlpointgrip_\'+id);\n
\tif (pointGrip) {return pointGrip;}\n
\n
\tpointGrip = document.createElementNS(NS.SVG, \'circle\');\n
\tsvgedit.utilities.assignAttributes(pointGrip, {\n
\t\t\'id\': \'ctrlpointgrip_\' + id,\n
\t\t\'display\': \'none\',\n
\t\t\'r\': 4,\n
\t\t\'fill\': \'#0FF\',\n
\t\t\'stroke\': \'#55F\',\n
\t\t\'stroke-width\': 1,\n
\t\t\'cursor\': \'move\',\n
\t\t\'style\': \'pointer-events:all\',\n
\t\t\'xlink:title\': uiStrings.pathCtrlPtTooltip\n
\t});\n
\tsvgedit.path.getGripContainer().appendChild(pointGrip);\n
\treturn pointGrip;\n
};\n
\n
svgedit.path.getCtrlLine = function(id) {\n
\tvar ctrlLine = svgedit.utilities.getElem(\'ctrlLine_\'+id);\n
\tif (ctrlLine) {return ctrlLine;}\n
\n
\tctrlLine = document.createElementNS(NS.SVG, \'line\');\n
\tsvgedit.utilities.assignAttributes(ctrlLine, {\n
\t\t\'id\': \'ctrlLine_\'+id,\n
\t\t\'stroke\': \'#555\',\n
\t\t\'stroke-width\': 1,\n
\t\t\'style\': \'pointer-events:none\'\n
\t});\n
\tsvgedit.path.getGripContainer().appendChild(ctrlLine);\n
\treturn ctrlLine;\n
};\n
\n
svgedit.path.getPointGrip = function(seg, update) {\n
\tvar index = seg.index;\n
\tvar pointGrip = svgedit.path.addPointGrip(index);\n
\n
\tif (update) {\n
\t\tvar pt = svgedit.path.getGripPt(seg);\n
\t\tsvgedit.utilities.assignAttributes(pointGrip, {\n
\t\t\t\'cx\': pt.x,\n
\t\t\t\'cy\': pt.y,\n
\t\t\t\'display\': \'inline\'\n
\t\t});\n
\t}\n
\n
\treturn pointGrip;\n
};\n
\n
svgedit.path.getControlPoints = function(seg) {\n
\tvar item = seg.item;\n
\tvar index = seg.index;\n
\tif (!(\'x1\' in item) || !(\'x2\' in item)) {return null;}\n
\tvar cpt = {};\n
\tvar pointGripContainer = svgedit.path.getGripContainer();\n
\n
\t// Note that this is intentionally not seg.prev.item\n
\tvar prev = svgedit.path.path.segs[index-1].item;\n
\n
\tvar seg_items = [prev, item];\n
\n
\tvar i;\n
\tfor (i = 1; i < 3; i++) {\n
\t\tvar id = index + \'c\' + i;\n
\n
\t\tvar ctrlLine = cpt[\'c\' + i + \'_line\'] = svgedit.path.getCtrlLine(id);\n
\n
\t\tvar pt = svgedit.path.getGripPt(seg, {x:item[\'x\' + i], y:item[\'y\' + i]});\n
\t\tvar gpt = svgedit.path.getGripPt(seg, {x:seg_items[i-1].x, y:seg_items[i-1].y});\n
\n
\t\tsvgedit.utilities.assignAttributes(ctrlLine, {\n
\t\t\t\'x1\': pt.x,\n
\t\t\t\'y1\': pt.y,\n
\t\t\t\'x2\': gpt.x,\n
\t\t\t\'y2\': gpt.y,\n
\t\t\t\'display\': \'inline\'\n
\t\t});\n
\n
\t\tcpt[\'c\' + i + \'_line\'] = ctrlLine;\n
\n
\t\t// create it\n
\t\tvar pointGrip = cpt[\'c\' + i] = svgedit.path.addCtrlGrip(id);\n
\n
\t\tsvgedit.utilities.assignAttributes(pointGrip, {\n
\t\t\t\'cx\': pt.x,\n
\t\t\t\'cy\': pt.y,\n
\t\t\t\'display\': \'inline\'\n
\t\t});\n
\t\tcpt[\'c\' + i] = pointGrip;\n
\t}\n
\treturn cpt;\n
};\n
\n
// This replaces the segment at the given index. Type is given as number.\n
svgedit.path.replacePathSeg = function(type, index, pts, elem) {\n
\tvar path = elem || svgedit.path.path.elem;\n
\tvar func = \'createSVGPathSeg\' + pathFuncs[type];\n
\tvar seg = path[func].apply(path, pts);\n
\n
\tif (svgedit.browser.supportsPathReplaceItem()) {\n
\t\tpath.pathSegList.replaceItem(seg, index);\n
\t} else {\n
\t\tvar segList = path.pathSegList;\n
\t\tvar len = segList.numberOfItems;\n
\t\tvar arr = [];\n
\t\tvar i;\n
\t\tfor (i = 0; i < len; i++) {\n
\t\t\tvar cur_seg = segList.getItem(i);\n
\t\t\tarr.push(cur_seg);\n
\t\t}\n
\t\tsegList.clear();\n
\t\tfor (i = 0; i < len; i++) {\n
\t\t\tif (i == index) {\n
\t\t\t\tsegList.appendItem(seg);\n
\t\t\t} else {\n
\t\t\t\tsegList.appendItem(arr[i]);\n
\t\t\t}\n
\t\t}\n
\t}\n
};\n
\n
svgedit.path.getSegSelector = function(seg, update) {\n
\tvar index = seg.index;\n
\tvar segLine = svgedit.utilities.getElem(\'segline_\' + index);\n
\tif (!segLine) {\n
\t\tvar pointGripContainer = svgedit.path.getGripContainer();\n
\t\t// create segline\n
\t\tsegLine = document.createElementNS(NS.SVG, \'path\');\n
\t\tsvgedit.utilities.assignAttributes(segLine, {\n
\t\t\t\'id\': \'segline_\' + index,\n
\t\t\t\'display\': \'none\',\n
\t\t\t\'fill\': \'none\',\n
\t\t\t\'stroke\': \'#0FF\',\n
\t\t\t\'stroke-width\': 2,\n
\t\t\t\'style\':\'pointer-events:none\',\n
\t\t\t\'d\': \'M0,0 0,0\'\n
\t\t});\n
\t\tpointGripContainer.appendChild(segLine);\n
\t}\n
\n
\tif (update) {\n
\t\tvar prev = seg.prev;\n
\t\tif (!prev) {\n
\t\t\tsegLine.setAttribute(\'display\', \'none\');\n
\t\t\treturn segLine;\n
\t\t}\n
\n
\t\tvar pt = svgedit.path.getGripPt(prev);\n
\t\t// Set start point\n
\t\tsvgedit.path.replacePathSeg(2, 0, [pt.x, pt.y], segLine);\n
\n
\t\tvar pts = svgedit.path.ptObjToArr(seg.type, seg.item, true);\n
\t\tvar i;\n
\t\tfor (i = 0; i < pts.length; i += 2) {\n
\t\t\tpt = svgedit.path.getGripPt(seg, {x:pts[i], y:pts[i+1]});\n
\t\t\tpts[i] = pt.x;\n
\t\t\tpts[i+1] = pt.y;\n
\t\t}\n
\n
\t\tsvgedit.path.replacePathSeg(seg.type, 1, pts, segLine);\n
\t}\n
\treturn segLine;\n
};\n
\n
// Function: smoothControlPoints\n
// Takes three points and creates a smoother line based on them\n
// \n
// Parameters: \n
// ct1 - Object with x and y values (first control point)\n
// ct2 - Object with x and y values (second control point)\n
// pt - Object with x and y values (third point)\n
//\n
// Returns: \n
// Array of two "smoothed" point objects\n
svgedit.path.smoothControlPoints = function(ct1, ct2, pt) {\n
\t// each point must not be the origin\n
\tvar x1 = ct1.x - pt.x,\n
\t\ty1 = ct1.y - pt.y,\n
\t\tx2 = ct2.x - pt.x,\n
\t\ty2 = ct2.y - pt.y;\n
\n
\tif ( (x1 != 0 || y1 != 0) && (x2 != 0 || y2 != 0) ) {\n
\t\tvar anglea = Math.atan2(y1, x1),\n
\t\t\tangleb = Math.atan2(y2, x2),\n
\t\t\tr1 = Math.sqrt(x1*x1+y1*y1),\n
\t\t\tr2 = Math.sqrt(x2*x2+y2*y2),\n
\t\t\tnct1 = editorContext_.getSVGRoot().createSVGPoint(),\n
\t\t\tnct2 = editorContext_.getSVGRoot().createSVGPoint();\n
\t\tif (anglea < 0) { anglea += 2*Math.PI; }\n
\t\tif (angleb < 0) { angleb += 2*Math.PI; }\n
\n
\t\tvar angleBetween = Math.abs(anglea - angleb),\n
\t\t\tangleDiff = Math.abs(Math.PI - angleBetween)/2;\n
\n
\t\tvar new_anglea, new_angleb;\n
\t\tif (anglea - angleb > 0) {\n
\t\t\tnew_anglea = angleBetween < Math.PI ? (anglea + angleDiff) : (anglea - angleDiff);\n
\t\t\tnew_angleb = angleBetween < Math.PI ? (angleb - angleDiff) : (angleb + angleDiff);\n
\t\t}\n
\t\telse {\n
\t\t\tnew_anglea = angleBetween < Math.PI ? (anglea - angleDiff) : (anglea + angleDiff);\n
\t\t\tnew_angleb = angleBetween < Math.PI ? (angleb + angleDiff) : (angleb - angleDiff);\n
\t\t}\n
\n
\t\t// rotate the points\n
\t\tnct1.x = r1 * Math.cos(new_anglea) + pt.x;\n
\t\tnct1.y = r1 * Math.sin(new_anglea) + pt.y;\n
\t\tnct2.x = r2 * Math.cos(new_angleb) + pt.x;\n
\t\tnct2.y = r2 * Math.sin(new_angleb) + pt.y;\n
\n
\t\treturn [nct1, nct2];\n
\t}\n
\treturn undefined;\n
};\n
\n
svgedit.path.Segment = function(index, item) {\n
\tthis.selected = false;\n
\tthis.index = index;\n
\tthis.item = item;\n
\tthis.type = item.pathSegType;\n
\n
\tthis.ctrlpts = [];\n
\tthis.ptgrip = null;\n
\tthis.segsel = null;\n
};\n
\n
svgedit.path.Segment.prototype.showCtrlPts = function(y) {\n
\tvar i;\n
\tfor (i in this.ctrlpts) {\n
\t\tif (this.ctrlpts.hasOwnProperty(i)) {\n
\t\t\tthis.ctrlpts[i].setAttribute(\'display\', y ? \'inline\' : \'none\');\n
\t\t}\n
\t}\n
};\n
\n
svgedit.path.Segment.prototype.selectCtrls = function(y) {\n
\t$(\'#ctrlpointgrip_\' + this.index + \'c1, #ctrlpointgrip_\' + this.index + \'c2\').\n
\t\tattr(\'fill\', y ? \'#0FF\' : \'#EEE\');\n
};\n
\n
svgedit.path.Segment.prototype.show = function(y) {\n
\tif (this.ptgrip) {\n
\t\tthis.ptgrip.setAttribute(\'display\', y ? \'inline\' : \'none\');\n
\t\tthis.segsel.setAttribute(\'display\', y ? \'inline\' : \'none\');\n
\t\t// Show/hide all control points if available\n
\t\tthis.showCtrlPts(y);\n
\t}\n
};\n
\n
svgedit.path.Segment.prototype.select = function(y) {\n
\tif (this.ptgrip) {\n
\t\tthis.ptgrip.setAttribute(\'stroke\', y ? \'#0FF\' : \'#00F\');\n
\t\tthis.segsel.setAttribute(\'display\', y ? \'inline\' : \'none\');\n
\t\tif (this.ctrlpts) {\n
\t\t\tthis.selectCtrls(y);\n
\t\t}\n
\t\tthis.selected = y;\n
\t}\n
};\n
\n
svgedit.path.Segment.prototype.addGrip = function() {\n
\tthis.ptgrip = svgedit.path.getPointGrip(this, true);\n
\tthis.ctrlpts = svgedit.path.getControlPoints(this, true);\n
\tthis.segsel = svgedit.path.getSegSelector(this, true);\n
};\n
\n
svgedit.path.Segment.prototype.update = function(full) {\n
\tif (this.ptgrip) {\n
\t\tvar pt = svgedit.path.getGripPt(this);\n
\t\tsvgedit.utilities.assignAttributes(this.ptgrip, {\n
\t\t\t\'cx\': pt.x,\n
\t\t\t\'cy\': pt.y\n
\t\t});\n
\n
\t\tsvgedit.path.getSegSelector(this, true);\n
\n
\t\tif (this.ctrlpts) {\n
\t\t\tif (full) {\n
\t\t\t\tthis.item = svgedit.path.path.elem.pathSegList.getItem(this.index);\n
\t\t\t\tthis.type = this.item.pathSegType;\n
\t\t\t}\n
\t\t\tsvgedit.path.getControlPoints(this);\n
\t\t}\n
\t\t// this.segsel.setAttribute(\'display\', y?\'inline\':\'none\');\n
\t}\n
};\n
\n
svgedit.path.Segment.prototype.move = function(dx, dy) {\n
\tvar cur_pts, item = this.item;\n
\n
\tif (this.ctrlpts) {\n
\t\tcur_pts = [item.x += dx, item.y += dy, \n
\t\t\titem.x1, item.y1, item.x2 += dx, item.y2 += dy];\n
\t} else {\n
\t\tcur_pts = [item.x += dx, item.y += dy];\n
\t}\n
\tsvgedit.path.replacePathSeg(this.type, this.index, cur_pts);\n
\n
\tif (this.next && this.next.ctrlpts) {\n
\t\tvar next = this.next.item;\n
\t\tvar next_pts = [next.x, next.y, \n
\t\t\tnext.x1 += dx, next.y1 += dy, next.x2, next.y2];\n
\t\tsvgedit.path.replacePathSeg(this.next.type, this.next.index, next_pts);\n
\t}\n
\n
\tif (this.mate) {\n
\t\t// The last point of a closed subpath has a \'mate\',\n
\t\t// which is the \'M\' segment of the subpath\n
\t\titem = this.mate.item;\n
\t\tvar pts = [item.x += dx, item.y += dy];\n
\t\tsvgedit.path.replacePathSeg(this.mate.type, this.mate.index, pts);\n
\t\t// Has no grip, so does not need \'updating\'?\n
\t}\n
\n
\tthis.update(true);\n
\tif (this.next) {this.next.update(true);}\n
};\n
\n
svgedit.path.Segment.prototype.setLinked = function(num) {\n
\tvar seg, anum, pt;\n
\tif (num == 2) {\n
\t\tanum = 1;\n
\t\tseg = this.next;\n
\t\tif (!seg) {return;}\n
\t\tpt = this.item;\n
\t} else {\n
\t\tanum = 2;\n
\t\tseg = this.prev;\n
\t\tif (!seg) {return;}\n
\t\tpt = seg.item;\n
\t}\n
\n
\tvar item = seg.item;\n
\n
\titem[\'x\' + anum] = pt.x + (pt.x - this.item[\'x\' + num]);\n
\titem[\'y\' + anum] = pt.y + (pt.y - this.item[\'y\' + num]);\n
\n
\tvar pts = [item.x, item.y,\n
\t\titem.x1, item.y1,\n
\t\titem.x2, item.y2];\n
\n
\tsvgedit.path.replacePathSeg(seg.type, seg.index, pts);\n
\tseg.update(true);\n
};\n
\n
svgedit.path.Segment.prototype.moveCtrl = function(num, dx, dy) {\n
\tvar item = this.item;\n
\n
\titem[\'x\' + num] += dx;\n
\titem[\'y\' + num] += dy;\n
\n
\tvar pts = [item.x, item.y, item.x1, item.y1, item.x2, item.y2];\n
\n
\tsvgedit.path.replacePathSeg(this.type, this.index, pts);\n
\tthis.update(true);\n
};\n
\n
svgedit.path.Segment.prototype.setType = function(new_type, pts) {\n
\tsvgedit.path.replacePathSeg(new_type, this.index, pts);\n
\tthis.type = new_type;\n
\tthis.item = svgedit.path.path.elem.pathSegList.getItem(this.index);\n
\tthis.showCtrlPts(new_type === 6);\n
\tthis.ctrlpts = svgedit.path.getControlPoints(this);\n
\tthis.update(true);\n
};\n
\n
svgedit.path.Path = function(elem) {\n
\tif (!elem || elem.tagName !== \'path\') {\n
\t\tthrow \'svgedit.path.Path constructed without a <path> element\';\n
\t}\n
\n
\tthis.elem = elem;\n
\tthis.segs = [];\n
\tthis.selected_pts = [];\n
\tsvgedit.path.path = this;\n
\n
\tthis.init();\n
};\n
\n
// Reset path data\n
svgedit.path.Path.prototype.init = function() {\n
\t// Hide all grips, etc\n
\t$(svgedit.path.getGripContainer()).find(\'*\').attr(\'display\', \'none\');\n
\tvar segList = this.elem.pathSegList;\n
\tvar len = segList.numberOfItems;\n
\tthis.segs = [];\n
\tthis.selected_pts = [];\n
\tthis.first_seg = null;\n
\n
\t// Set up segs array\n
\tvar i;\n
\tfor (i = 0; i < len; i++) {\n
\t\tvar item = segList.getItem(i);\n
\t\tvar segment = new svgedit.path.Segment(i, item);\n
\t\tsegment.path = this;\n
\t\tthis.segs.push(segment);\n
\t}\n
\n
\tvar segs = this.segs;\n
\tvar start_i = null;\n
\n
\tfor (i = 0; i < len; i++) {\n
\t\tvar seg = segs[i];\n
\t\tvar next_seg = (i+1) >= len ? null : segs[i+1];\n
\t\tvar prev_seg = (i-1) < 0 ? null : segs[i-1];\n
\t\tvar start_seg;\n
\t\tif (seg.type === 2) {\n
\t\t\tif (prev_seg && prev_seg.type !== 1) {\n
\t\t\t\t// New sub-path, last one is open,\n
\t\t\t\t// so add a grip to last sub-path\'s first point\n
\t\t\t\tstart_seg = segs[start_i];\n
\t\t\t\tstart_seg.next = segs[start_i+1];\n
\t\t\t\tstart_seg.next.prev = start_seg;\n
\t\t\t\tstart_seg.addGrip();\n
\t\t\t}\n
\t\t\t// Remember that this is a starter seg\n
\t\t\tstart_i = i;\n
\t\t} else if (next_seg && next_seg.type === 1) {\n
\t\t\t// This is the last real segment of a closed sub-path\n
\t\t\t// Next is first seg after "M"\n
\t\t\tseg.next = segs[start_i+1];\n
\n
\t\t\t// First seg after "M"\'s prev is this\n
\t\t\tseg.next.prev = seg;\n
\t\t\tseg.mate = segs[start_i];\n
\t\t\tseg.addGrip();\n
\t\t\tif (this.first_seg == null) {\n
\t\t\t\tthis.first_seg = seg;\n
\t\t\t}\n
\t\t} else if (!next_seg) {\n
\t\t\tif (seg.type !== 1) {\n
\t\t\t\t// Last seg, doesn\'t close so add a grip\n
\t\t\t\t// to last sub-path\'s first point\n
\t\t\t\tstart_seg = segs[start_i];\n
\t\t\t\tstart_seg.next = segs[start_i+1];\n
\t\t\t\tstart_seg.next.prev = start_seg;\n
\t\t\t\tstart_seg.addGrip();\n
\t\t\t\tseg.addGrip();\n
\n
\t\t\t\tif (!this.first_seg) {\n
\t\t\t\t\t// Open path, so set first as real first and add grip\n
\t\t\t\t\tthis.first_seg = segs[start_i];\n
\t\t\t\t}\n
\t\t\t}\n
\t\t} else if (seg.type !== 1){\n
\t\t\t// Regular segment, so add grip and its "next"\n
\t\t\tseg.addGrip();\n
\n
\t\t\t// Don\'t set its "next" if it\'s an "M"\n
\t\t\tif (next_seg && next_seg.type !== 2) {\n
\t\t\t\tseg.next = next_seg;\n
\t\t\t\tseg.next.prev = seg;\n
\t\t\t}\n
\t\t}\n
\t}\n
\treturn this;\n
};\n
\n
svgedit.path.Path.prototype.eachSeg = function(fn) {\n
\tvar i;\n
\tvar len = this.segs.length;\n
\tfor (i = 0; i < len; i++) {\n
\t\tvar ret = fn.call(this.segs[i], i);\n
\t\tif (ret === false) {break;}\n
\t}\n
};\n
\n
svgedit.path.Path.prototype.addSeg = function(index) {\n
\t// Adds a new segment\n
\tvar seg = this.segs[index];\n
\tif (!seg.prev) {return;}\n
\n
\tvar prev = seg.prev;\n
\tvar newseg, new_x, new_y;\n
\tswitch(seg.item.pathSegType) {\n
\tcase 4:\n
\t\tnew_x = (seg.item.x + prev.item.x) / 2;\n
\t\tnew_y = (seg.item.y + prev.item.y) / 2;\n
\t\tnewseg = this.elem.createSVGPathSegLinetoAbs(new_x, new_y);\n
\t\tbreak;\n
\tcase 6: //make it a curved segment to preserve the shape (WRS)\n
\t\t// http://en.wikipedia.org/wiki/De_Casteljau%27s_algorithm#Geometric_interpretation\n
\t\tvar p0_x = (prev.item.x + seg.item.x1)/2;\n
\t\tvar p1_x = (seg.item.x1 + seg.item.x2)/2;\n
\t\tvar p2_x = (seg.item.x2 + seg.item.x)/2;\n
\t\tvar p01_x = (p0_x + p1_x)/2;\n
\t\tvar p12_x = (p1_x + p2_x)/2;\n
\t\tnew_x = (p01_x + p12_x)/2;\n
\t\tvar p0_y = (prev.item.y + seg.item.y1)/2;\n
\t\tvar p1_y = (seg.item.y1 + seg.item.y2)/2;\n
\t\tvar p2_y = (seg.item.y2 + seg.item.y)/2;\n
\t\tvar p01_y = (p0_y + p1_y)/2;\n
\t\tvar p12_y = (p1_y + p2_y)/2;\n
\t\tnew_y = (p01_y + p12_y)/2;\n
\t\tnewseg = this.elem.createSVGPathSegCurvetoCubicAbs(new_x, new_y, p0_x, p0_y, p01_x, p01_y);\n
\t\tvar pts = [seg.item.x, seg.item.y, p12_x, p12_y, p2_x, p2_y];\n
\t\tsvgedit.path.replacePathSeg(seg.type, index, pts);\n
\t\tbreak;\n
\t}\n
\n
\tsvgedit.path.insertItemBefore(this.elem, newseg, index);\n
};\n
\n
svgedit.path.Path.prototype.deleteSeg = function(index) {\n
\tvar seg = this.segs[index];\n
\tvar list = this.elem.pathSegList;\n
\n
\tseg.show(false);\n
\tvar next = seg.next;\n
\tvar pt;\n
\tif (seg.mate) {\n
\t\t// Make the next point be the "M" point\n
\t\tpt = [next.item.x, next.item.y];\n
\t\tsvgedit.path.replacePathSeg(2, next.index, pt);\n
\n
\t\t// Reposition last node\n
\t\tsvgedit.path.replacePathSeg(4, seg.index, pt);\n
\n
\t\tlist.removeItem(seg.mate.index);\n
\t} else if (!seg.prev) {\n
\t\t// First node of open path, make next point the M\n
\t\tvar item = seg.item;\n
\t\tpt = [next.item.x, next.item.y];\n
\t\tsvgedit.path.replacePathSeg(2, seg.next.index, pt);\n
\t\tlist.removeItem(index);\n
\t} else {\n
\t\tlist.removeItem(index);\n
\t}\n
};\n
\n
svgedit.path.Path.prototype.subpathIsClosed = function(index) {\n
\tvar closed = false;\n
\t// Check if subpath is already open\n
\tsvgedit.path.path.eachSeg(function(i) {\n
\t\tif (i <= index) {return true;}\n
\t\tif (this.type === 2) {\n
\t\t\t// Found M first, so open\n
\t\t\treturn false;\n
\t\t}\n
\t\tif (this.type === 1) {\n
\t\t\t// Found Z first, so closed\n
\t\t\tclosed = true;\n
\t\t\treturn false;\n
\t\t}\n
\t});\n
\n
\treturn closed;\n
};\n
\n
svgedit.path.Path.prototype.removePtFromSelection = function(index) {\n
\tvar pos = this.selected_pts.indexOf(index);\n
\tif (pos == -1) {\n
\t\treturn;\n
\t}\n
\tthis.segs[index].select(false);\n
\tthis.selected_pts.splice(pos, 1);\n
};\n
\n
svgedit.path.Path.prototype.clearSelection = function() {\n
\tthis.eachSeg(function() {\n
\t\t// \'this\' is the segment here\n
\t\tthis.select(false);\n
\t});\n
\tthis.selected_pts = [];\n
};\n
\n
svgedit.path.Path.prototype.storeD = function() {\n
\tthis.last_d = this.elem.getAttribute(\'d\');\n
};\n
\n
svgedit.path.Path.prototype.show = function(y) {\n
\t// Shows this path\'s segment grips\n
\tthis.eachSeg(function() {\n
\t\t// \'this\' is the segment here\n
\t\tthis.show(y);\n
\t});\n
\tif (y) {\n
\t\tthis.selectPt(this.first_seg.index);\n
\t}\n
\treturn this;\n
};\n
\n
// Move selected points\n
svgedit.path.Path.prototype.movePts = function(d_x, d_y) {\n
\tvar i = this.selected_pts.length;\n
\twhile(i--) {\n
\t\tvar seg = this.segs[this.selected_pts[i]];\n
\t\tseg.move(d_x, d_y);\n
\t}\n
};\n
\n
svgedit.path.Path.prototype.moveCtrl = function(d_x, d_y) {\n
\tvar seg = this.segs[this.selected_pts[0]];\n
\tseg.moveCtrl(this.dragctrl, d_x, d_y);\n
\tif (link_control_pts) {\n
\t\tseg.setLinked(this.dragctrl);\n
\t}\n
};\n
\n
svgedit.path.Path.prototype.setSegType = function(new_type) {\n
\tthis.storeD();\n
\tvar i = this.selected_pts.length;\n
\tvar text;\n
\twhile(i--) {\n
\t\tvar sel_pt = this.selected_pts[i];\n
\n
\t\t// Selected seg\n
\t\tvar cur = this.segs[sel_pt];\n
\t\tvar prev = cur.prev;\n
\t\tif (!prev) {continue;}\n
\n
\t\tif (!new_type) { // double-click, so just toggle\n
\t\t\ttext = \'Toggle Path Segment Type\';\n
\n
\t\t\t// Toggle segment to curve/straight line\n
\t\t\tvar old_type = cur.type;\n
\n
\t\t\tnew_type = (old_type == 6) ? 4 : 6;\n
\t\t}\n
\n
\t\tnew_type = Number(new_type);\n
\n
\t\tvar cur_x = cur.item.x;\n
\t\tvar cur_y = cur.item.y;\n
\t\tvar prev_x = prev.item.x;\n
\t\tvar prev_y = prev.item.y;\n
\t\tvar points;\n
\t\tswitch ( new_type ) {\n
\t\tcase 6:\n
\t\t\tif (cur.olditem) {\n
\t\t\t\tvar old = cur.olditem;\n
\t\t\t\tpoints = [cur_x, cur_y, old.x1, old.y1, old.x2, old.y2];\n
\t\t\t} else {\n
\t\t\t\tvar diff_x = cur_x - prev_x;\n
\t\t\t\tvar diff_y = cur_y - prev_y;\n
\t\t\t\t// get control points from straight line segment\n
\t\t\t\t/*\n
\t\t\t\tvar ct1_x = (prev_x + (diff_y/2));\n
\t\t\t\tvar ct1_y = (prev_y - (diff_x/2));\n
\t\t\t\tvar ct2_x = (cur_x + (diff_y/2));\n
\t\t\t\tvar ct2_y = (cur_y - (diff_x/2));\n
\t\t\t\t*/\n
\t\t\t\t//create control points on the line to preserve the shape (WRS)\n
\t\t\t\tvar ct1_x = (prev_x + (diff_x/3));\n
\t\t\t\tvar ct1_y = (prev_y + (diff_y/3));\n
\t\t\t\tvar ct2_x = (cur_x - (diff_x/3));\n
\t\t\t\tvar ct2_y = (cur_y - (diff_y/3));\n
\t\t\t\tpoints = [cur_x, cur_y, ct1_x, ct1_y, ct2_x, ct2_y];\n
\t\t\t}\n
\t\t\tbreak;\n
\t\tcase 4:\n
\t\t\tpoints = [cur_x, cur_y];\n
\n
\t\t\t// Store original prevve segment nums\n
\t\t\tcur.olditem = cur.item;\n
\t\t\tbreak;\n
\t\t}\n
\n
\t\tcur.setType(new_type, points);\n
\t}\n
\tsvgedit.path.path.endChanges(text);\n
};\n
\n
svgedit.path.Path.prototype.selectPt = function(pt, ctrl_num) {\n
\tthis.clearSelection();\n
\tif (pt == null) {\n
\t\tthis.eachSeg(function(i) {\n
\t\t\t// \'this\' is the segment here.\n
\t\t\tif (this.prev) {\n
\t\t\t\tpt = i;\n
\t\t\t}\n
\t\t});\n
\t}\n
\tthis.addPtsToSelection(pt);\n
\tif (ctrl_num) {\n
\t\tthis.dragctrl = ctrl_num;\n
\n
\t\tif (link_control_pts) {\n
\t\t\tthis.segs[pt].setLinked(ctrl_num);\n
\t\t}\n
\t}\n
};\n
\n
// Update position of all points\n
svgedit.path.Path.prototype.update = function() {\n
\tvar elem = this.elem;\n
\tif (svgedit.utilities.getRotationAngle(elem)) {\n
\t\tthis.matrix = svgedit.math.getMatrix(elem);\n
\t\tthis.imatrix = this.matrix.inverse();\n
\t} else {\n
\t\tthis.matrix = null;\n
\t\tthis.imatrix = null;\n
\t}\n
\n
\tthis.eachSeg(function(i) {\n
\t\tthis.item = elem.pathSegList.getItem(i);\n
\t\tthis.update();\n
\t});\n
\n
\treturn this;\n
};\n
\n
svgedit.path.getPath_ = function(elem) {\n
\tvar p = pathData[elem.id];\n
\tif (!p) {\n
\t\tp = pathData[elem.id] = new svgedit.path.Path(elem);\n
\t}\n
\treturn p;\n
};\n
\n
svgedit.path.removePath_ = function(id) {\n
\tif (id in pathData) {delete pathData[id];}\n
};\n
var newcx, newcy, oldcx, oldcy, angle;\n
var getRotVals = function(x, y) {\n
\tvar dx = x - oldcx;\n
\tvar dy = y - oldcy;\n
\n
\t// rotate the point around the old center\n
\tvar r = Math.sqrt(dx*dx + dy*dy);\n
\tvar theta = Math.atan2(dy, dx) + angle;\n
\tdx = r * Math.cos(theta) + oldcx;\n
\tdy = r * Math.sin(theta) + oldcy;\n
\n
\t// dx,dy should now hold the actual coordinates of each\n
\t// point after being rotated\n
\n
\t// now we want to rotate them around the new center in the reverse direction\n
\tdx -= newcx;\n
\tdy -= newcy;\n
\n
\tr = Math.sqrt(dx*dx + dy*dy);\n
\ttheta = Math.atan2(dy, dx) - angle;\n
\n
\treturn {\'x\': r * Math.cos(theta) + newcx,\n
\t\t\'y\': r * Math.sin(theta) + newcy};\n
};\n
\n
// If the path was rotated, we must now pay the piper:\n
// Every path point must be rotated into the rotated coordinate system of \n
// its old center, then determine the new center, then rotate it back\n
// This is because we want the path to remember its rotation\n
\n
// TODO: This is still using ye olde transform methods, can probably\n
// be optimized or even taken care of by recalculateDimensions\n
svgedit.path.recalcRotatedPath = function() {\n
\tvar current_path = svgedit.path.path.elem;\n
\tangle = svgedit.utilities.getRotationAngle(current_path, true);\n
\tif (!angle) {return;}\n
//\tselectedBBoxes[0] = svgedit.path.path.oldbbox;\n
\tvar box = svgedit.utilities.getBBox(current_path),\n
\t\toldbox = svgedit.path.path.oldbbox; //selectedBBoxes[0],\n
\toldcx = oldbox.x + oldbox.width/2;\n
\toldcy = oldbox.y + oldbox.height/2;\n
\tnewcx = box.x + box.width/2;\n
\tnewcy = box.y + box.height/2;\n
\n
\t// un-rotate the new center to the proper position\n
\tvar dx = newcx - oldcx,\n
\t\tdy = newcy - oldcy,\n
\t\tr = Math.sqrt(dx*dx + dy*dy),\n
\t\ttheta = Math.atan2(dy, dx) + angle;\n
\n
\tnewcx = r * Math.cos(theta) + oldcx;\n
\tnewcy = r * Math.sin(theta) + oldcy;\n
\n
\tvar list = current_path.pathSegList,\n
\t\ti = list.numberOfItems;\n
\twhile (i) {\n
\t\ti -= 1;\n
\t\tvar seg = list.getItem(i),\n
\t\t\ttype = seg.pathSegType;\n
\t\tif (type == 1) {continue;}\n
\n
\t\tvar rvals = getRotVals(seg.x, seg.y),\n
\t\t\tpoints = [rvals.x, rvals.y];\n
\t\tif (seg.x1 != null && seg.x2 != null) {\n
\t\t\tvar c_vals1 = getRotVals(seg.x1, seg.y1);\n
\t\t\tvar c_vals2 = getRotVals(seg.x2, seg.y2);\n
\t\t\tpoints.splice(points.length, 0, c_vals1.x , c_vals1.y, c_vals2.x, c_vals2.y);\n
\t\t}\n
\t\tsvgedit.path.replacePathSeg(type, i, points);\n
\t} // loop for each point\n
\n
\tbox = svgedit.utilities.getBBox(current_path);\n
//\tselectedBBoxes[0].x = box.x; selectedBBoxes[0].y = box.y;\n
//\tselectedBBoxes[0].width = box.width; selectedBBoxes[0].height = box.height;\n
\n
\t// now we must set the new transform to be rotated around the new center\n
\tvar R_nc = svgroot.createSVGTransform(),\n
\t\ttlist = svgedit.transformlist.getTransformList(current_path);\n
\tR_nc.setRotate((angle * 180.0 / Math.PI), newcx, newcy);\n
\ttlist.replaceItem(R_nc,0);\n
};\n
\n
// ====================================\n
// Public API starts here\n
\n
svgedit.path.clearData =  function() {\n
\tpathData = {};\n
};\n
\n
}());\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>25612</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
