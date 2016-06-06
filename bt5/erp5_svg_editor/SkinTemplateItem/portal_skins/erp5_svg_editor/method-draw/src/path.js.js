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
            <value> <string>anonymous_http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts52852042.19</string> </value>
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

/**\n
 * Package: svgedit.path\n
 *\n
 * Licensed under the Apache License, Version 2\n
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
var svgedit = svgedit || {};\n
\n
(function() {\n
\n
if (!svgedit.path) {\n
  svgedit.path = {};\n
}\n
\n
var svgns = "http://www.w3.org/2000/svg";\n
\n
var uiStrings = {\n
  "pathNodeTooltip": "Drag node to move it. Double-click node to change segment type",\n
  "pathCtrlPtTooltip": "Drag control point to adjust curve properties"\n
};\n
\n
var segData = {\n
  2: [\'x\',\'y\'],\n
  4: [\'x\',\'y\'],\n
  6: [\'x\',\'y\',\'x1\',\'y1\',\'x2\',\'y2\'],\n
  8: [\'x\',\'y\',\'x1\',\'y1\'],\n
  10: [\'x\',\'y\',\'r1\',\'r2\',\'angle\',\'largeArcFlag\',\'sweepFlag\'],\n
  12: [\'x\'],\n
  14: [\'y\'],\n
  16: [\'x\',\'y\',\'x2\',\'y2\'],\n
  18: [\'x\',\'y\']\n
};\n
\n
var pathFuncs = [];\n
\n
var link_control_pts = false;\n
\n
// Stores references to paths via IDs.\n
// TODO: Make this cross-document happy.\n
var pathData = {};\n
\n
svgedit.path.setLinkControlPoints = function(lcp) {\n
  link_control_pts = lcp;\n
};\n
\n
svgedit.path.path = null;\n
\n
var editorContext_ = null;\n
\n
svgedit.path.init = function(editorContext) {\n
  editorContext_ = editorContext;\n
  \n
  pathFuncs = [0,\'ClosePath\'];\n
  var pathFuncsStrs = [\'Moveto\', \'Lineto\', \'CurvetoCubic\', \'CurvetoQuadratic\', \'Arc\',\n
    \'LinetoHorizontal\', \'LinetoVertical\',\'CurvetoCubicSmooth\',\'CurvetoQuadraticSmooth\'];\n
  $.each(pathFuncsStrs, function(i,s) {\n
    pathFuncs.push(s+\'Abs\');\n
    pathFuncs.push(s+\'Rel\');\n
  });\n
};\n
\n
svgedit.path.insertItemBefore = function(elem, newseg, index) {\n
  var list = elem.pathSegList;\n
  list.insertItemBefore(newseg, index);\n
};\n
\n
// TODO: See if this should just live in replacePathSeg\n
svgedit.path.ptObjToArr = function(type, seg_item) {\n
  var arr = segData[type], len = arr.length;\n
  var out = Array(len);\n
  for(var i=0; i<len; i++) {\n
    out[i] = seg_item[arr[i]];\n
  }\n
  return out;\n
};\n
\n
svgedit.path.getGripPt = function(seg, alt_pt) {\n
  var out = {\n
    x: alt_pt? alt_pt.x : seg.item.x,\n
    y: alt_pt? alt_pt.y : seg.item.y\n
  }, path = seg.path;\n
\n
  if(path.matrix) {\n
    var pt = svgedit.math.transformPoint(out.x, out.y, path.matrix);\n
    out = pt;\n
  }\n
\n
  out.x *= editorContext_.getCurrentZoom();\n
  out.y *= editorContext_.getCurrentZoom();\n
\n
  return out;\n
};\n
\n
svgedit.path.getPointFromGrip = function(pt, path) {\n
  var out = {\n
    x: pt.x,\n
    y: pt.y\n
  }\n
\n
  if(path.matrix) {\n
    var pt = svgedit.math.transformPoint(out.x, out.y, path.imatrix);\n
    out.x = pt.x;\n
    out.y = pt.y;\n
  }\n
\n
  out.x /= editorContext_.getCurrentZoom();\n
  out.y /= editorContext_.getCurrentZoom();\n
\n
  return out;\n
};\n
\n
svgedit.path.addPointGrip = function(index, x, y) {\n
  // create the container of all the point grips\n
  var pointGripContainer = svgedit.path.getGripContainer();\n
\n
  var pointGrip = svgedit.utilities.getElem("pathpointgrip_"+index);\n
  // create it\n
  if (!pointGrip) {\n
    pointGrip = document.createElementNS(svgns, "rect");\n
    svgedit.utilities.assignAttributes(pointGrip, {\n
      \'id\': "pathpointgrip_" + index,\n
      \'display\': "none",\n
      \'width\': svgedit.browser.isTouch() ? 30 : 5,\n
      \'height\': svgedit.browser.isTouch() ? 30 : 5,\n
      \'fill\': "#fff",\n
      \'stroke\': "#4F80FF",\n
      \'shape-rendering\': "crispEdges",\n
      \'stroke-width\': 1,\n
      \'cursor\': \'move\',\n
      \'style\': \'pointer-events:all\',\n
      \'xlink:title\': uiStrings.pathNodeTooltip\n
    });\n
    pointGrip = pointGripContainer.appendChild(pointGrip);\n
\n
    var grip = $(\'#pathpointgrip_\'+index);\n
    grip.dblclick(function() {\n
      if(svgedit.path.path) svgedit.path.path.setSegType();\n
    });\n
  }\n
  if(x && y) {\n
    // set up the point grip element and display it\n
    svgedit.utilities.assignAttributes(pointGrip, {\n
      \'x\': x-(svgedit.browser.isTouch() ? 15 : 2.5),\n
      \'y\': y-(svgedit.browser.isTouch() ? 15 : 2.5),\n
      \'display\': "inline"\n
    });\n
  }\n
  return pointGrip;\n
};\n
\n
svgedit.path.getGripContainer = function() {\n
  var c = svgedit.utilities.getElem("pathpointgrip_container");\n
  if (!c) {\n
    var parent = svgedit.utilities.getElem("selectorParentGroup");\n
    c = parent.appendChild(document.createElementNS(svgns, "g"));\n
    c.id = "pathpointgrip_container";\n
  }\n
  return c;\n
};\n
\n
svgedit.path.addCtrlGrip = function(id) {\n
  var pointGrip = svgedit.utilities.getElem("ctrlpointgrip_"+id);\n
  if(pointGrip) return pointGrip;\n
    \n
  pointGrip = document.createElementNS(svgns, "circle");\n
  svgedit.utilities.assignAttributes(pointGrip, {\n
    \'id\': "ctrlpointgrip_" + id,\n
    \'display\': "none",\n
    \'r\': svgedit.browser.isTouch() ? 15 : 3,\n
    \'fill\': "#4F80FF",\n
    \'stroke\': \'#4F80FF\',\n
    \'stroke-opacity\': 0,\n
    \'stroke-width\': \'3\',\n
    \'cursor\': \'move\',\n
    \'style\': \'pointer-events:all\',\n
    \'xlink:title\': uiStrings.pathCtrlPtTooltip\n
  });\n
  svgedit.path.getGripContainer().appendChild(pointGrip);\n
  return pointGrip;\n
};\n
\n
svgedit.path.getCtrlLine = function(id) {\n
  var ctrlLine = svgedit.utilities.getElem("ctrlLine_"+id);\n
  if(ctrlLine) return ctrlLine;\n
\n
  ctrlLine = document.createElementNS(svgns, "line");\n
  svgedit.utilities.assignAttributes(ctrlLine, {\n
    \'id\': "ctrlLine_"+id,\n
    \'stroke\': "#4F80FF",\n
    \'stroke-width\': 1,\n
    "style": "pointer-events:none"\n
  });\n
  svgedit.path.getGripContainer().appendChild(ctrlLine);\n
  return ctrlLine;\n
};\n
\n
svgedit.path.getPointGrip = function(seg, update) {\n
  var index = seg.index;\n
  var pointGrip = svgedit.path.addPointGrip(index);\n
  if(update) {\n
    var pt = svgedit.path.getGripPt(seg);\n
    svgedit.utilities.assignAttributes(pointGrip, {\n
      \'x\': pt.x-(svgedit.browser.isTouch() ? 15 : 2.5),\n
      \'y\': pt.y-(svgedit.browser.isTouch() ? 15 : 2.5),\n
      \'display\': "inline"\n
    });\n
  }\n
\n
  return pointGrip;\n
};\n
\n
svgedit.path.getControlPoints = function(seg) {\n
  var item = seg.item;\n
  var index = seg.index;\n
  if(!item || !("x1" in item) || !("x2" in item)) return null;\n
  var cpt = {};     \n
  var pointGripContainer = svgedit.path.getGripContainer();\n
\n
  // Note that this is intentionally not seg.prev.item\n
  var prev = svgedit.path.path.segs[index-1].item;\n
\n
  var seg_items = [prev, item];\n
\n
  for(var i=1; i<3; i++) {\n
    var id = index + \'c\' + i;\n
\n
    var ctrlLine = cpt[\'c\' + i + \'_line\'] = svgedit.path.getCtrlLine(id);\n
\n
    var pt = svgedit.path.getGripPt(seg, {x:item[\'x\' + i], y:item[\'y\' + i]});\n
    var gpt = svgedit.path.getGripPt(seg, {x:seg_items[i-1].x, y:seg_items[i-1].y});\n
\n
    svgedit.utilities.assignAttributes(ctrlLine, {\n
      \'x1\': pt.x,\n
      \'y1\': pt.y,\n
      \'x2\': gpt.x,\n
      \'y2\': gpt.y,\n
      \'display\': "inline"\n
    });\n
\n
    cpt[\'c\' + i + \'_line\'] = ctrlLine;\n
\n
    // create it\n
    pointGrip = cpt[\'c\' + i] = svgedit.path.addCtrlGrip(id);\n
    svgedit.utilities.assignAttributes(pointGrip, {\n
      \'cx\': pt.x,\n
      \'cy\': pt.y,\n
      \'display\': "inline"\n
    });\n
    cpt[\'c\' + i] = pointGrip;\n
  }\n
  return cpt;\n
};\n
\n
// This replaces the segment at the given index. Type is given as number.\n
svgedit.path.replacePathSeg = function(type, index, pts, elem) {\n
  var path = elem || svgedit.path.path.elem;\n
  var func = \'createSVGPathSeg\' + pathFuncs[type];\n
  var seg = path[func].apply(path, pts);\n
  path.pathSegList.replaceItem(seg, index);\n
};\n
\n
svgedit.path.getSegSelector = function(seg, update) {\n
  var index = seg.index;\n
  var segLine = svgedit.utilities.getElem("segline_" + index);\n
  if(!segLine) {\n
    var pointGripContainer = svgedit.path.getGripContainer();\n
    // create segline\n
    segLine = document.createElementNS(svgns, "path");\n
    svgedit.utilities.assignAttributes(segLine, {\n
      \'id\': "segline_" + index,\n
      \'display\': \'none\',\n
      \'fill\': "none",\n
      \'stroke\': "#0ff",\n
      \'stroke-opacity\': 1,\n
      "shape-rendering": "crispEdges",\n
      \'stroke-width\': 2,\n
      \'style\':\'pointer-events:none\',\n
      \'d\': \'M0,0 0,0\'\n
    });\n
    pointGripContainer.appendChild(segLine);\n
  } \n
\n
  if(update) {\n
    var prev = seg.prev;\n
    if(!prev) {\n
      segLine.setAttribute("display", "none");\n
      return segLine;\n
    }\n
\n
    var pt = svgedit.path.getGripPt(prev);\n
    // Set start point\n
    svgedit.path.replacePathSeg(2, 0, [pt.x, pt.y], segLine);\n
\n
    var pts = svgedit.path.ptObjToArr(seg.type, seg.item, true);\n
    for(var i=0; i < pts.length; i+=2) {\n
      var pt = svgedit.path.getGripPt(seg, {x:pts[i], y:pts[i+1]});\n
      pts[i] = pt.x;\n
      pts[i+1] = pt.y;\n
    }\n
\n
    svgedit.path.replacePathSeg(seg.type, 1, pts, segLine);\n
  }\n
  return segLine;\n
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
svgedit.path.smoothControlPoints = this.smoothControlPoints = function(ct1, ct2, pt) {\n
  // each point must not be the origin\n
  var x1 = ct1.x - pt.x,\n
    y1 = ct1.y - pt.y,\n
    x2 = ct2.x - pt.x,\n
    y2 = ct2.y - pt.y;\n
    \n
  if ( (x1 != 0 || y1 != 0) && (x2 != 0 || y2 != 0) ) {\n
    var anglea = Math.atan2(y1,x1),\n
      angleb = Math.atan2(y2,x2),\n
      r1 = Math.sqrt(x1*x1+y1*y1),\n
      r2 = Math.sqrt(x2*x2+y2*y2),\n
      nct1 = editorContext_.getSVGRoot().createSVGPoint(),\n
      nct2 = editorContext_.getSVGRoot().createSVGPoint();        \n
    if (anglea < 0) { anglea += 2*Math.PI; }\n
    if (angleb < 0) { angleb += 2*Math.PI; }\n
    \n
    var angleBetween = Math.abs(anglea - angleb),\n
      angleDiff = Math.abs(Math.PI - angleBetween)/2;\n
    \n
    var new_anglea, new_angleb;\n
    if (anglea - angleb > 0) {\n
      new_anglea = angleBetween < Math.PI ? (anglea + angleDiff) : (anglea - angleDiff);\n
      new_angleb = angleBetween < Math.PI ? (angleb - angleDiff) : (angleb + angleDiff);\n
    }\n
    else {\n
      new_anglea = angleBetween < Math.PI ? (anglea - angleDiff) : (anglea + angleDiff);\n
      new_angleb = angleBetween < Math.PI ? (angleb + angleDiff) : (angleb - angleDiff);\n
    }\n
    \n
    // rotate the points\n
    nct1.x = r1 * Math.cos(new_anglea) + pt.x;\n
    nct1.y = r1 * Math.sin(new_anglea) + pt.y;\n
    nct2.x = r2 * Math.cos(new_angleb) + pt.x;\n
    nct2.y = r2 * Math.sin(new_angleb) + pt.y;\n
    \n
    return [nct1, nct2];\n
  }\n
  return undefined;\n
};\n
\n
svgedit.path.Segment = function(index, item) {\n
  this.selected = false;\n
  this.index = index;\n
  this.item = item;\n
  this.type = item.pathSegType;\n
  \n
  this.ctrlpts = [];\n
  this.ptgrip = null;\n
  this.segsel = null;\n
};\n
\n
svgedit.path.Segment.prototype.showCtrlPts = function(y) {\n
  for (var i in this.ctrlpts) {\n
    this.ctrlpts[i].setAttribute("display", y ? "inline" : "none");\n
  }\n
};\n
\n
svgedit.path.Segment.prototype.selectCtrls = function(y) {\n
  $(\'#ctrlpointgrip_\' + this.index + \'c1, #ctrlpointgrip_\' + this.index + \'c2\').\n
    attr(\'fill\', \'#4F80FF\');\n
};\n
\n
svgedit.path.Segment.prototype.show = function(y) {\n
  if(this.ptgrip) {\n
    this.ptgrip.setAttribute("display", y ? "inline" : "none");\n
    this.segsel.setAttribute("display", y ? "inline" : "none");\n
    // Show/hide all control points if available\n
    this.showCtrlPts(y);\n
  }\n
};\n
\n
svgedit.path.Segment.prototype.select = function(y) {\n
  if(this.ptgrip) {\n
    this.ptgrip.setAttribute("stroke", y ? "#4F80FF" : "#4F80FF");\n
    this.ptgrip.setAttribute("fill", y ? "#4F80FF" : "#fff");\n
    this.segsel.setAttribute("display", y ? "inline" : "none");\n
    if(this.ctrlpts) {\n
      this.selectCtrls(y);\n
    }\n
    this.selected = y;\n
  }\n
};\n
\n
svgedit.path.Segment.prototype.addGrip = function() {\n
  this.ptgrip = svgedit.path.getPointGrip(this, true);\n
  this.ctrlpts = svgedit.path.getControlPoints(this, true);\n
  this.segsel = svgedit.path.getSegSelector(this, true);\n
};\n
\n
svgedit.path.Segment.prototype.update = function(full) {\n
  if(this.ptgrip) {\n
    var pt = svgedit.path.getGripPt(this);\n
    var reposition = (svgedit.browser.isTouch() ? 15 : 2.5)\n
    var properties = (this.ptgrip.nodeName == "rect") ? {\'x\': pt.x-reposition, \'y\': pt.y-reposition} : {\'cx\': pt.x, \'cy\': pt.y};\n
    svgedit.utilities.assignAttributes(this.ptgrip, properties);\n
    svgedit.path.getSegSelector(this, true);\n
\n
    if(this.ctrlpts) {\n
      if(full) {\n
        this.item = svgedit.path.path.elem.pathSegList.getItem(this.index);\n
        this.type = this.item.pathSegType;\n
      }\n
      svgedit.path.getControlPoints(this);\n
    } \n
    // this.segsel.setAttribute("display", y?"inline":"none");\n
  }\n
};\n
\n
svgedit.path.Segment.prototype.move = function(dx, dy) {\n
  var item = this.item;\n
  // fix for path tool dom breakage, amending item does bad things now, so we take a copy and use that. Can probably improve to just take a shallow copy of object\n
  var cloneItem = $.extend({}, item);\n
  var cur_pts = (this.ctrlpts) \n
    ? [cloneItem.x += dx,  cloneItem.y += dy, \n
       cloneItem.x1,       cloneItem.y1, \n
       cloneItem.x2 += dx, cloneItem.y2 += dy]\n
    : [cloneItem.x += dx, cloneItem.y += dy];\n
  \n
  svgedit.path.replacePathSeg(this.type, this.index, cur_pts);\n
\n
  if(this.next && this.next.ctrlpts) {\n
    var next = this.next.item;\n
    var next_pts = [next.x, next.y, \n
      next.x1 += dx, next.y1 += dy, next.x2, next.y2];\n
    svgedit.path.replacePathSeg(this.next.type, this.next.index, next_pts);\n
  }\n
\n
  if(this.mate) {\n
    // The last point of a closed subpath has a "mate",\n
    // which is the "M" segment of the subpath\n
    var item = this.mate.item;\n
    var pts = [item.x += dx, item.y += dy];\n
    svgedit.path.replacePathSeg(this.mate.type, this.mate.index, pts);\n
    // Has no grip, so does not need "updating"?\n
  }\n
\n
  this.update(true);\n
  if(this.next) this.next.update(true);\n
};\n
\n
svgedit.path.Segment.prototype.setLinked = function(num) {\n
  var seg, anum, pt;\n
  if (num == 2) {\n
    anum = 1;\n
    seg = this.next;\n
    if(!seg) return;\n
    pt = this.item;\n
  } else {\n
    anum = 2;\n
    seg = this.prev;\n
    if(!seg) return;\n
    pt = seg.item;\n
  }\n
\n
  var item = seg.item;\n
  var cloneItem = $.extend({}, item);\n
  cloneItem[\'x\' + anum ] = pt.x + (pt.x - this.item[\'x\' + num]);\n
  cloneItem[\'y\' + anum ] = pt.y + (pt.y - this.item[\'y\' + num]);\n
\n
  var pts = [ \n
              cloneItem.x, cloneItem.y,\n
              cloneItem.x1, cloneItem.y1,\n
              cloneItem.x2, cloneItem.y2\n
            ];\n
\n
  svgedit.path.replacePathSeg(seg.type, seg.index, pts);\n
  seg.update(true);\n
};\n
\n
svgedit.path.Segment.prototype.moveCtrl = function(num, dx, dy) {\n
  var item = $.extend({}, this.item);\n
\n
  item[\'x\' + num] += dx;\n
  item[\'y\' + num] += dy;\n
\n
  var pts = [item.x,item.y,\n
    item.x1,item.y1, item.x2,item.y2];\n
    \n
  svgedit.path.replacePathSeg(this.type, this.index, pts);\n
  this.update(true);\n
};\n
\n
svgedit.path.Segment.prototype.setType = function(new_type, pts) {\n
  svgedit.path.replacePathSeg(new_type, this.index, pts);\n
  this.type = new_type;\n
  this.item = svgedit.path.path.elem.pathSegList.getItem(this.index);\n
  this.showCtrlPts(new_type === 6);\n
  this.ctrlpts = svgedit.path.getControlPoints(this);\n
  this.update(true);\n
};\n
\n
svgedit.path.Path = function(elem) {\n
  if(!elem || elem.tagName !== "path") {\n
    throw "svgedit.path.Path constructed without a <path> element";\n
  }\n
\n
  this.elem = elem;\n
  this.segs = [];\n
  this.selected_pts = [];\n
  svgedit.path.path = this;\n
\n
  this.init();\n
};\n
\n
// Reset path data\n
svgedit.path.Path.prototype.init = function() {\n
  // Hide all grips, etc\n
  $(svgedit.path.getGripContainer()).find("*").attr("display", "none");\n
  var segList = this.elem.pathSegList;\n
  var len = segList.numberOfItems;\n
  this.segs = [];\n
  this.selected_pts = [];\n
  this.first_seg = null;\n
  \n
  // Set up segs array\n
  for(var i=0; i < len; i++) {\n
    var item = segList.getItem(i);\n
    var segment = new svgedit.path.Segment(i, item);\n
    segment.path = this;\n
    this.segs.push(segment);\n
  } \n
  \n
  var segs = this.segs;\n
  var start_i = null;\n
\n
  for(var i=0; i < len; i++) {\n
    var seg = segs[i]; \n
    var next_seg = (i+1) >= len ? null : segs[i+1];\n
    var prev_seg = (i-1) < 0 ? null : segs[i-1];\n
    \n
    if(seg.type === 2) {\n
      if(prev_seg && prev_seg.type !== 1) {\n
        // New sub-path, last one is open,\n
        // so add a grip to last sub-path\'s first point\n
        var start_seg = segs[start_i];\n
        start_seg.next = segs[start_i+1];\n
        start_seg.next.prev = start_seg;\n
        start_seg.addGrip();\n
      }\n
      // Remember that this is a starter seg\n
      start_i = i;\n
    } else if(next_seg && next_seg.type === 1) {\n
      // This is the last real segment of a closed sub-path\n
      // Next is first seg after "M"\n
      seg.next = segs[start_i+1];\n
      \n
      // First seg after "M"\'s prev is this\n
      seg.next.prev = seg;\n
      seg.mate = segs[start_i];\n
      seg.addGrip();\n
      if(this.first_seg == null) {\n
        this.first_seg = seg;\n
      }\n
    } else if(!next_seg) {\n
      if(seg.type !== 1) {\n
        // Last seg, doesn\'t close so add a grip\n
        // to last sub-path\'s first point\n
        var start_seg = segs[start_i];\n
        start_seg.next = segs[start_i+1];\n
        start_seg.next.prev = start_seg;\n
        start_seg.addGrip();\n
        seg.addGrip();\n
\n
        if(!this.first_seg) {\n
          // Open path, so set first as real first and add grip\n
          this.first_seg = segs[start_i];\n
        }\n
      }\n
    } else if(seg.type !== 1){\n
      // Regular segment, so add grip and its "next"\n
      seg.addGrip();\n
      \n
      // Don\'t set its "next" if it\'s an "M"\n
      if(next_seg && next_seg.type !== 2) {\n
        seg.next = next_seg;\n
        seg.next.prev = seg;\n
      }\n
    }\n
  }\n
  return this;\n
};\n
\n
svgedit.path.Path.prototype.eachSeg = function(fn) {\n
  var len = this.segs.length\n
  for(var i=0; i < len; i++) {\n
    var ret = fn.call(this.segs[i], i);\n
    if(ret === false) break;\n
  }\n
};\n
\n
svgedit.path.Path.prototype.addSeg = function(index) {\n
  // Adds a new segment\n
  var seg = this.segs[index];\n
  if(!seg.prev) return;\n
\n
  var prev = seg.prev;\n
  var newseg;\n
  switch(seg.item.pathSegType) {\n
  case 4:\n
    var new_x = (seg.item.x + prev.item.x) / 2;\n
    var new_y = (seg.item.y + prev.item.y) / 2;\n
    newseg = this.elem.createSVGPathSegLinetoAbs(new_x, new_y);\n
    break;\n
  case 6: //make it a curved segment to preserve the shape (WRS)\n
    // http://en.wikipedia.org/wiki/De_Casteljau%27s_algorithm#Geometric_interpretation\n
    var p0_x = (prev.item.x + seg.item.x1)/2;\n
    var p1_x = (seg.item.x1 + seg.item.x2)/2;\n
    var p2_x = (seg.item.x2 + seg.item.x)/2;\n
    var p01_x = (p0_x + p1_x)/2;\n
    var p12_x = (p1_x + p2_x)/2;\n
    var new_x = (p01_x + p12_x)/2;\n
    var p0_y = (prev.item.y + seg.item.y1)/2;\n
    var p1_y = (seg.item.y1 + seg.item.y2)/2;\n
    var p2_y = (seg.item.y2 + seg.item.y)/2;\n
    var p01_y = (p0_y + p1_y)/2;\n
    var p12_y = (p1_y + p2_y)/2;\n
    var new_y = (p01_y + p12_y)/2;\n
    newseg = this.elem.createSVGPathSegCurvetoCubicAbs(new_x,new_y, p0_x,p0_y, p01_x,p01_y);\n
    var pts = [seg.item.x,seg.item.y,p12_x,p12_y,p2_x,p2_y];\n
    svgedit.path.replacePathSeg(seg.type,index,pts);\n
    break;\n
  }\n
\n
  svgedit.path.insertItemBefore(this.elem, newseg, index);\n
};\n
\n
svgedit.path.Path.prototype.deleteSeg = function(index) {\n
  var seg = this.segs[index];\n
  var list = this.elem.pathSegList;\n
  \n
  seg.show(false);\n
  var next = seg.next;\n
  if(seg.mate) {\n
    // Make the next point be the "M" point\n
    var pt = [next.item.x, next.item.y];\n
    svgedit.path.replacePathSeg(2, next.index, pt);\n
    \n
    // Reposition last node\n
    svgedit.path.replacePathSeg(4, seg.index, pt);\n
    \n
    list.removeItem(seg.mate.index);\n
  } else if(!seg.prev) {\n
    // First node of open path, make next point the M\n
    var item = seg.item;\n
    var pt = [next.item.x, next.item.y];\n
    svgedit.path.replacePathSeg(2, seg.next.index, pt);\n
    list.removeItem(index);\n
    \n
  } else {\n
    list.removeItem(index);\n
  }\n
};\n
\n
svgedit.path.Path.prototype.subpathIsClosed = function(index) {\n
  var closed = false;\n
  // Check if subpath is already open\n
  svgedit.path.path.eachSeg(function(i) {\n
    if(i <= index) return true;\n
    if(this.type === 2) {\n
      // Found M first, so open\n
      return false;\n
    } else if(this.type === 1) {\n
      // Found Z first, so closed\n
      closed = true;\n
      return false;\n
    }\n
  });\n
  \n
  return closed;\n
};\n
\n
svgedit.path.Path.prototype.removePtFromSelection = function(index) {\n
  var pos = this.selected_pts.indexOf(index);\n
  if(pos == -1) {\n
    return;\n
  } \n
  this.segs[index].select(false);\n
  this.selected_pts.splice(pos, 1);\n
};\n
\n
svgedit.path.Path.prototype.clearSelection = function() {\n
  this.eachSeg(function(i) {\n
    // \'this\' is the segment here\n
    this.select(false);\n
  });\n
  this.selected_pts = [];\n
};\n
\n
svgedit.path.Path.prototype.storeD = function() {\n
  this.last_d = this.elem.getAttribute(\'d\');\n
};\n
\n
svgedit.path.Path.prototype.show = function(y) {\n
  // Shows this path\'s segment grips\n
  this.eachSeg(function() {\n
    // \'this\' is the segment here\n
    this.show(y);\n
  });\n
  if(y) {\n
    this.selectPt(this.first_seg.index);\n
  }\n
  return this;\n
};\n
\n
// Move selected points \n
svgedit.path.Path.prototype.movePts = function(d_x, d_y) {\n
  var i = this.selected_pts.length;\n
  while(i--) {\n
    var seg = this.segs[this.selected_pts[i]];\n
    seg.move(d_x, d_y);\n
  }\n
};\n
\n
svgedit.path.Path.prototype.moveCtrl = function(d_x, d_y) {\n
  var seg = this.segs[this.selected_pts[0]];\n
  seg.moveCtrl(this.dragctrl, d_x, d_y);\n
  if(link_control_pts) {\n
    seg.setLinked(this.dragctrl);\n
  }\n
};\n
\n
svgedit.path.Path.prototype.setSegType = function(new_type) {\n
  this.storeD();\n
  var i = this.selected_pts.length;\n
  var text;\n
  while(i--) {\n
    var sel_pt = this.selected_pts[i];\n
    \n
    // Selected seg\n
    var cur = this.segs[sel_pt];\n
    var prev = cur.prev;\n
    if(!prev) continue;\n
    \n
    if(!new_type) { // double-click, so just toggle\n
      text = "Toggle Path Segment Type";\n
\n
      // Toggle segment to curve/straight line\n
      var old_type = cur.type;\n
      \n
      new_type = (old_type == 6) ? 4 : 6;\n
    } \n
    \n
    new_type = new_type-0;\n
    \n
    var cur_x = cur.item.x;\n
    var cur_y = cur.item.y;\n
    var prev_x = prev.item.x;\n
    var prev_y = prev.item.y;\n
    var points;\n
    switch ( new_type ) {\n
    case 6:\n
      if(cur.olditem) {\n
        var old = cur.olditem;\n
        points = [cur_x,cur_y, old.x1,old.y1, old.x2,old.y2];\n
      } else {\n
        var diff_x = cur_x - prev_x;\n
        var diff_y = cur_y - prev_y;\n
        // get control points from straight line segment\n
        /*\n
        var ct1_x = (prev_x + (diff_y/2));\n
        var ct1_y = (prev_y - (diff_x/2));\n
        var ct2_x = (cur_x + (diff_y/2));\n
        var ct2_y = (cur_y - (diff_x/2));\n
        */\n
        //create control points on the line to preserve the shape (WRS)\n
        var ct1_x = (prev_x + (diff_x/3));\n
        var ct1_y = (prev_y + (diff_y/3));\n
        var ct2_x = (cur_x - (diff_x/3));\n
        var ct2_y = (cur_y - (diff_y/3));\n
        points = [cur_x,cur_y, ct1_x,ct1_y, ct2_x,ct2_y];\n
      }\n
      break;\n
    case 4:\n
      points = [cur_x,cur_y];\n
      \n
      // Store original prevve segment nums\n
      cur.olditem = cur.item;\n
      break;\n
    }\n
    \n
    cur.setType(new_type, points);\n
  }\n
  svgedit.path.path.endChanges(text);\n
};\n
\n
svgedit.path.Path.prototype.selectPt = function(pt, ctrl_num) {\n
  this.clearSelection();\n
  if(pt == null) {\n
    this.eachSeg(function(i) {\n
      // \'this\' is the segment here.\n
      if(this.prev) {\n
        pt = i;\n
      }\n
    });\n
  }\n
  this.addPtsToSelection(pt);\n
  if(ctrl_num) {\n
    this.dragctrl = ctrl_num;\n
    \n
    if(link_control_pts) {\n
      this.segs[pt].setLinked(ctrl_num);\n
    }\n
  }\n
};\n
\n
// Update position of all points\n
svgedit.path.Path.prototype.update = function() {\n
  var elem = this.elem;\n
  if(svgedit.utilities.getRotationAngle(elem)) {\n
    this.matrix = svgedit.math.getMatrix(elem);\n
    this.imatrix = this.matrix.inverse();\n
  } else {\n
    this.matrix = null;\n
    this.imatrix = null;\n
  }\n
\n
  this.eachSeg(function(i) {\n
    this.item = elem.pathSegList.getItem(i);\n
    this.update();\n
  });\n
\n
  return this;\n
};\n
\n
svgedit.path.getPath_ = function(elem) {\n
  var p = pathData[elem.id];\n
  if(!p) p = pathData[elem.id] = new svgedit.path.Path(elem);\n
  return p;\n
};\n
\n
svgedit.path.removePath_ = function(id) {\n
  if(id in pathData) delete pathData[id];\n
};\n
\n
var getRotVals = function(x, y, oldcx, oldcy, newcx, newcy, angle) {\n
  dx = x - oldcx;\n
  dy = y - oldcy;\n
  \n
  // rotate the point around the old center\n
  r = Math.sqrt(dx*dx + dy*dy);\n
  theta = Math.atan2(dy,dx) + angle;\n
  dx = r * Math.cos(theta) + oldcx;\n
  dy = r * Math.sin(theta) + oldcy;\n
  \n
  // dx,dy should now hold the actual coordinates of each\n
  // point after being rotated\n
\n
  // now we want to rotate them around the new center in the reverse direction\n
  dx -= newcx;\n
  dy -= newcy;\n
  \n
  r = Math.sqrt(dx*dx + dy*dy);\n
  theta = Math.atan2(dy,dx) - angle;\n
  return {\'x\':(r * Math.cos(theta) + newcx)/1,\n
    \'y\':(r * Math.sin(theta) + newcy)/1};\n
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
  var current_path = svgedit.path.path.elem;\n
  var angle = svgedit.utilities.getRotationAngle(current_path, true);\n
  if(!angle) return;\n
//  selectedBBoxes[0] = svgedit.path.path.oldbbox;\n
  var box = svgedit.utilities.getBBox(current_path),\n
    oldbox = svgedit.path.path.oldbbox,//selectedBBoxes[0],\n
    oldcx = oldbox.x + oldbox.width/2,\n
    oldcy = oldbox.y + oldbox.height/2,\n
    newcx = box.x + box.width/2,\n
    newcy = box.y + box.height/2,\n
    \n
  // un-rotate the new center to the proper position\n
    dx = newcx - oldcx,\n
    dy = newcy - oldcy,\n
    r = Math.sqrt(dx*dx + dy*dy),\n
    theta = Math.atan2(dy,dx) + angle;\n
    \n
  newcx = r * Math.cos(theta) + oldcx;\n
  newcy = r * Math.sin(theta) + oldcy;\n
  \n
  var list = current_path.pathSegList,\n
    i = list.numberOfItems;\n
  while (i) {\n
    i -= 1;\n
    var seg = list.getItem(i),\n
      type = seg.pathSegType;\n
    if(type == 1) continue;\n
    \n
    var rvals = getRotVals(seg.x,seg.y, oldcx, oldcy, newcx, newcy, angle),\n
      points = [rvals.x, rvals.y];\n
    if(seg.x1 != null && seg.x2 != null) {\n
      c_vals1 = getRotVals(seg.x1, seg.y1, oldcx, oldcy, newcx, newcy, angle);\n
      c_vals2 = getRotVals(seg.x2, seg.y2, oldcx, oldcy, newcx, newcy, angle);\n
      points.splice(points.length, 0, c_vals1.x , c_vals1.y, c_vals2.x, c_vals2.y);\n
    }\n
    svgedit.path.replacePathSeg(type, i, points);\n
  } // loop for each point\n
\n
  box = svgedit.utilities.getBBox(current_path);            \n
//  selectedBBoxes[0].x = box.x; selectedBBoxes[0].y = box.y;\n
//  selectedBBoxes[0].width = box.width; selectedBBoxes[0].height = box.height;\n
  \n
  // now we must set the new transform to be rotated around the new center\n
  var R_nc = svgroot.createSVGTransform(),\n
    tlist = svgedit.transformlist.getTransformList(current_path);\n
  R_nc.setRotate((angle * 180.0 / Math.PI), newcx, newcy);\n
  tlist.replaceItem(R_nc,0);\n
};\n
\n
// ====================================\n
// Public API starts here\n
\n
svgedit.path.clearData =  function() {\n
  pathData = {};\n
};\n
\n
})();\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>27053</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
