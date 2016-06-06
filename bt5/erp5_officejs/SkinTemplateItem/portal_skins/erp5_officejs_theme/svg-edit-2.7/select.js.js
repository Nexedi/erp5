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
            <value> <string>select.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgedit*/\n
/*jslint vars: true, eqeq: true, forin: true*/\n
/**\n
 * Package: svedit.select\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 * Copyright(c) 2010 Jeff Schiller\n
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
if (!svgedit.select) {\n
\tsvgedit.select = {};\n
}\n
\n
var svgFactory_;\n
var config_;\n
var selectorManager_; // A Singleton\n
var gripRadius = svgedit.browser.isTouch() ? 10 : 4;\n
\n
// Class: svgedit.select.Selector\n
// Private class for DOM element selection boxes\n
//\n
// Parameters:\n
// id - integer to internally indentify the selector\n
// elem - DOM element associated with this selector\n
svgedit.select.Selector = function(id, elem) {\n
\t// this is the selector\'s unique number\n
\tthis.id = id;\n
\n
\t// this holds a reference to the element for which this selector is being used\n
\tthis.selectedElement = elem;\n
\n
\t// this is a flag used internally to track whether the selector is being used or not\n
\tthis.locked = true;\n
\n
\t// this holds a reference to the <g> element that holds all visual elements of the selector\n
\tthis.selectorGroup = svgFactory_.createSVGElement({\n
\t\t\'element\': \'g\',\n
\t\t\'attr\': {\'id\': (\'selectorGroup\' + this.id)}\n
\t});\n
\n
\t// this holds a reference to the path rect\n
\tthis.selectorRect = this.selectorGroup.appendChild(\n
\t\tsvgFactory_.createSVGElement({\n
\t\t\t\'element\': \'path\',\n
\t\t\t\'attr\': {\n
\t\t\t\t\'id\': (\'selectedBox\' + this.id),\n
\t\t\t\t\'fill\': \'none\',\n
\t\t\t\t\'stroke\': \'#22C\',\n
\t\t\t\t\'stroke-width\': \'1\',\n
\t\t\t\t\'stroke-dasharray\': \'5,5\',\n
\t\t\t\t// need to specify this so that the rect is not selectable\n
\t\t\t\t\'style\': \'pointer-events:none\'\n
\t\t\t}\n
\t\t})\n
\t);\n
\n
\t// this holds a reference to the grip coordinates for this selector\n
\tthis.gripCoords = {\n
\t\t\'nw\': null,\n
\t\t\'n\' : null,\n
\t\t\'ne\': null,\n
\t\t\'e\' : null,\n
\t\t\'se\': null,\n
\t\t\'s\' : null,\n
\t\t\'sw\': null,\n
\t\t\'w\' : null\n
\t};\n
\n
\tthis.reset(this.selectedElement);\n
};\n
\n
\n
// Function: svgedit.select.Selector.reset\n
// Used to reset the id and element that the selector is attached to\n
//\n
// Parameters:\n
// e - DOM element associated with this selector\n
svgedit.select.Selector.prototype.reset = function(e) {\n
\tthis.locked = true;\n
\tthis.selectedElement = e;\n
\tthis.resize();\n
\tthis.selectorGroup.setAttribute(\'display\', \'inline\');\n
};\n
\n
// Function: svgedit.select.Selector.updateGripCursors\n
// Updates cursors for corner grips on rotation so arrows point the right way\n
//\n
// Parameters:\n
// angle - Float indicating current rotation angle in degrees\n
svgedit.select.Selector.prototype.updateGripCursors = function(angle) {\n
\tvar dir,\n
\t\tdir_arr = [],\n
\t\tsteps = Math.round(angle / 45);\n
\tif (steps < 0) {steps += 8;}\n
\tfor (dir in selectorManager_.selectorGrips) {\n
\t\tdir_arr.push(dir);\n
\t}\n
\twhile (steps > 0) {\n
\t\tdir_arr.push(dir_arr.shift());\n
\t\tsteps--;\n
\t}\n
\tvar i = 0;\n
\tfor (dir in selectorManager_.selectorGrips) {\n
\t\tselectorManager_.selectorGrips[dir].setAttribute(\'style\', (\'cursor:\' + dir_arr[i] + \'-resize\'));\n
\t\ti++;\n
\t}\n
};\n
\n
// Function: svgedit.select.Selector.showGrips\n
// Show the resize grips of this selector\n
//\n
// Parameters:\n
// show - boolean indicating whether grips should be shown or not\n
svgedit.select.Selector.prototype.showGrips = function(show) {\n
\t// TODO: use suspendRedraw() here\n
\tvar bShow = show ? \'inline\' : \'none\';\n
\tselectorManager_.selectorGripsGroup.setAttribute(\'display\', bShow);\n
\tvar elem = this.selectedElement;\n
\tthis.hasGrips = show;\n
\tif (elem && show) {\n
\t\tthis.selectorGroup.appendChild(selectorManager_.selectorGripsGroup);\n
\t\tthis.updateGripCursors(svgedit.utilities.getRotationAngle(elem));\n
\t}\n
};\n
\n
// Function: svgedit.select.Selector.resize\n
// Updates the selector to match the element\'s size\n
svgedit.select.Selector.prototype.resize = function() {\n
\tvar selectedBox = this.selectorRect,\n
\t\tmgr = selectorManager_,\n
\t\tselectedGrips = mgr.selectorGrips,\n
\t\tselected = this.selectedElement,\n
\t\tsw = selected.getAttribute(\'stroke-width\'),\n
\t\tcurrent_zoom = svgFactory_.currentZoom();\n
\tvar offset = 1/current_zoom;\n
\tif (selected.getAttribute(\'stroke\') !== \'none\' && !isNaN(sw)) {\n
\t\toffset += (sw/2);\n
\t}\n
\n
\tvar tagName = selected.tagName;\n
\tif (tagName === \'text\') {\n
\t\toffset += 2/current_zoom;\n
\t}\n
\n
\t// loop and transform our bounding box until we reach our first rotation\n
\tvar tlist = svgedit.transformlist.getTransformList(selected);\n
\tvar m = svgedit.math.transformListToTransform(tlist).matrix;\n
\n
\t// This should probably be handled somewhere else, but for now\n
\t// it keeps the selection box correctly positioned when zoomed\n
\tm.e *= current_zoom;\n
\tm.f *= current_zoom;\n
\n
\tvar bbox = svgedit.utilities.getBBox(selected);\n
\tif (tagName === \'g\' && !$.data(selected, \'gsvg\')) {\n
\t\t// The bbox for a group does not include stroke vals, so we\n
\t\t// get the bbox based on its children.\n
\t\tvar stroked_bbox = svgFactory_.getStrokedBBox(selected.childNodes);\n
\t\tif (stroked_bbox) {\n
\t\t\tbbox = stroked_bbox;\n
\t\t}\n
\t}\n
\n
\t// apply the transforms\n
\tvar l = bbox.x, t = bbox.y, w = bbox.width, h = bbox.height;\n
\tbbox = {x:l, y:t, width:w, height:h};\n
\n
\t// we need to handle temporary transforms too\n
\t// if skewed, get its transformed box, then find its axis-aligned bbox\n
\n
\t//*\n
\toffset *= current_zoom;\n
\n
\tvar nbox = svgedit.math.transformBox(l*current_zoom, t*current_zoom, w*current_zoom, h*current_zoom, m),\n
\t\taabox = nbox.aabox,\n
\t\tnbax = aabox.x - offset,\n
\t\tnbay = aabox.y - offset,\n
\t\tnbaw = aabox.width + (offset * 2),\n
\t\tnbah = aabox.height + (offset * 2);\n
\n
\t// now if the shape is rotated, un-rotate it\n
\tvar cx = nbax + nbaw/2,\n
\t\tcy = nbay + nbah/2;\n
\n
\tvar angle = svgedit.utilities.getRotationAngle(selected);\n
\tif (angle) {\n
\t\tvar rot = svgFactory_.svgRoot().createSVGTransform();\n
\t\trot.setRotate(-angle, cx, cy);\n
\t\tvar rotm = rot.matrix;\n
\t\tnbox.tl = svgedit.math.transformPoint(nbox.tl.x, nbox.tl.y, rotm);\n
\t\tnbox.tr = svgedit.math.transformPoint(nbox.tr.x, nbox.tr.y, rotm);\n
\t\tnbox.bl = svgedit.math.transformPoint(nbox.bl.x, nbox.bl.y, rotm);\n
\t\tnbox.br = svgedit.math.transformPoint(nbox.br.x, nbox.br.y, rotm);\n
\n
\t\t// calculate the axis-aligned bbox\n
\t\tvar tl = nbox.tl;\n
\t\tvar minx = tl.x,\n
\t\t\tminy = tl.y,\n
\t\t\tmaxx = tl.x,\n
\t\t\tmaxy = tl.y;\n
\n
\t\tvar min = Math.min, max = Math.max;\n
\n
\t\tminx = min(minx, min(nbox.tr.x, min(nbox.bl.x, nbox.br.x) ) ) - offset;\n
\t\tminy = min(miny, min(nbox.tr.y, min(nbox.bl.y, nbox.br.y) ) ) - offset;\n
\t\tmaxx = max(maxx, max(nbox.tr.x, max(nbox.bl.x, nbox.br.x) ) ) + offset;\n
\t\tmaxy = max(maxy, max(nbox.tr.y, max(nbox.bl.y, nbox.br.y) ) ) + offset;\n
\n
\t\tnbax = minx;\n
\t\tnbay = miny;\n
\t\tnbaw = (maxx-minx);\n
\t\tnbah = (maxy-miny);\n
\t}\n
\tvar sr_handle = svgFactory_.svgRoot().suspendRedraw(100);\n
\n
\tvar dstr = \'M\' + nbax + \',\' + nbay\n
\t\t\t\t+ \' L\' + (nbax+nbaw) + \',\' + nbay\n
\t\t\t\t+ \' \' + (nbax+nbaw) + \',\' + (nbay+nbah)\n
\t\t\t\t+ \' \' + nbax + \',\' + (nbay+nbah) + \'z\';\n
\tselectedBox.setAttribute(\'d\', dstr);\n
\n
\tvar xform = angle ? \'rotate(\' + [angle, cx, cy].join(\',\') + \')\' : \'\';\n
\tthis.selectorGroup.setAttribute(\'transform\', xform);\n
\n
\t// TODO(codedread): Is this if needed?\n
//\tif (selected === selectedElements[0]) {\n
\t\tthis.gripCoords = {\n
\t\t\t\'nw\': [nbax, nbay],\n
\t\t\t\'ne\': [nbax+nbaw, nbay],\n
\t\t\t\'sw\': [nbax, nbay+nbah],\n
\t\t\t\'se\': [nbax+nbaw, nbay+nbah],\n
\t\t\t\'n\':  [nbax + (nbaw)/2, nbay],\n
\t\t\t\'w\':\t[nbax, nbay + (nbah)/2],\n
\t\t\t\'e\':\t[nbax + nbaw, nbay + (nbah)/2],\n
\t\t\t\'s\':\t[nbax + (nbaw)/2, nbay + nbah]\n
\t\t};\n
\t\tvar dir;\n
\t\tfor (dir in this.gripCoords) {\n
\t\t\tvar coords = this.gripCoords[dir];\n
\t\t\tselectedGrips[dir].setAttribute(\'cx\', coords[0]);\n
\t\t\tselectedGrips[dir].setAttribute(\'cy\', coords[1]);\n
\t\t}\n
\n
\t\t// we want to go 20 pixels in the negative transformed y direction, ignoring scale\n
\t\tmgr.rotateGripConnector.setAttribute(\'x1\', nbax + (nbaw)/2);\n
\t\tmgr.rotateGripConnector.setAttribute(\'y1\', nbay);\n
\t\tmgr.rotateGripConnector.setAttribute(\'x2\', nbax + (nbaw)/2);\n
\t\tmgr.rotateGripConnector.setAttribute(\'y2\', nbay - (gripRadius*5));\n
\n
\t\tmgr.rotateGrip.setAttribute(\'cx\', nbax + (nbaw)/2);\n
\t\tmgr.rotateGrip.setAttribute(\'cy\', nbay - (gripRadius*5));\n
//\t}\n
\n
\tsvgFactory_.svgRoot().unsuspendRedraw(sr_handle);\n
};\n
\n
\n
// Class: svgedit.select.SelectorManager\n
svgedit.select.SelectorManager = function() {\n
\t// this will hold the <g> element that contains all selector rects/grips\n
\tthis.selectorParentGroup = null;\n
\n
\t// this is a special rect that is used for multi-select\n
\tthis.rubberBandBox = null;\n
\n
\t// this will hold objects of type svgedit.select.Selector (see above)\n
\tthis.selectors = [];\n
\n
\t// this holds a map of SVG elements to their Selector object\n
\tthis.selectorMap = {};\n
\n
\t// this holds a reference to the grip elements\n
\tthis.selectorGrips = {\n
\t\t\'nw\': null,\n
\t\t\'n\' :  null,\n
\t\t\'ne\': null,\n
\t\t\'e\' :  null,\n
\t\t\'se\': null,\n
\t\t\'s\' :  null,\n
\t\t\'sw\': null,\n
\t\t\'w\' :  null\n
\t};\n
\n
\tthis.selectorGripsGroup = null;\n
\tthis.rotateGripConnector = null;\n
\tthis.rotateGrip = null;\n
\n
\tthis.initGroup();\n
};\n
\n
// Function: svgedit.select.SelectorManager.initGroup\n
// Resets the parent selector group element\n
svgedit.select.SelectorManager.prototype.initGroup = function() {\n
\t// remove old selector parent group if it existed\n
\tif (this.selectorParentGroup && this.selectorParentGroup.parentNode) {\n
\t\tthis.selectorParentGroup.parentNode.removeChild(this.selectorParentGroup);\n
\t}\n
\n
\t// create parent selector group and add it to svgroot\n
\tthis.selectorParentGroup = svgFactory_.createSVGElement({\n
\t\t\'element\': \'g\',\n
\t\t\'attr\': {\'id\': \'selectorParentGroup\'}\n
\t});\n
\tthis.selectorGripsGroup = svgFactory_.createSVGElement({\n
\t\t\'element\': \'g\',\n
\t\t\'attr\': {\'display\': \'none\'}\n
\t});\n
\tthis.selectorParentGroup.appendChild(this.selectorGripsGroup);\n
\tsvgFactory_.svgRoot().appendChild(this.selectorParentGroup);\n
\n
\tthis.selectorMap = {};\n
\tthis.selectors = [];\n
\tthis.rubberBandBox = null;\n
\n
\t// add the corner grips\n
\tvar dir;\n
\tfor (dir in this.selectorGrips) {\n
\t\tvar grip = svgFactory_.createSVGElement({\n
\t\t\t\'element\': \'circle\',\n
\t\t\t\'attr\': {\n
\t\t\t\t\'id\': (\'selectorGrip_resize_\' + dir),\n
\t\t\t\t\'fill\': \'#22C\',\n
\t\t\t\t\'r\': gripRadius,\n
\t\t\t\t\'style\': (\'cursor:\' + dir + \'-resize\'),\n
\t\t\t\t// This expands the mouse-able area of the grips making them\n
\t\t\t\t// easier to grab with the mouse.\n
\t\t\t\t// This works in Opera and WebKit, but does not work in Firefox\n
\t\t\t\t// see https://bugzilla.mozilla.org/show_bug.cgi?id=500174\n
\t\t\t\t\'stroke-width\': 2,\n
\t\t\t\t\'pointer-events\': \'all\'\n
\t\t\t}\n
\t\t});\n
\n
\t\t$.data(grip, \'dir\', dir);\n
\t\t$.data(grip, \'type\', \'resize\');\n
\t\tthis.selectorGrips[dir] = this.selectorGripsGroup.appendChild(grip);\n
\t}\n
\n
\t// add rotator elems\n
\tthis.rotateGripConnector = this.selectorGripsGroup.appendChild(\n
\t\tsvgFactory_.createSVGElement({\n
\t\t\t\'element\': \'line\',\n
\t\t\t\'attr\': {\n
\t\t\t\t\'id\': (\'selectorGrip_rotateconnector\'),\n
\t\t\t\t\'stroke\': \'#22C\',\n
\t\t\t\t\'stroke-width\': \'1\'\n
\t\t\t}\n
\t\t})\n
\t);\n
\n
\tthis.rotateGrip = this.selectorGripsGroup.appendChild(\n
\t\tsvgFactory_.createSVGElement({\n
\t\t\t\'element\': \'circle\',\n
\t\t\t\'attr\': {\n
\t\t\t\t\'id\': \'selectorGrip_rotate\',\n
\t\t\t\t\'fill\': \'lime\',\n
\t\t\t\t\'r\': gripRadius,\n
\t\t\t\t\'stroke\': \'#22C\',\n
\t\t\t\t\'stroke-width\': 2,\n
\t\t\t\t\'style\': \'cursor:url(\' + config_.imgPath + \'rotate.png) 12 12, auto;\'\n
\t\t\t}\n
\t\t})\n
\t);\n
\t$.data(this.rotateGrip, \'type\', \'rotate\');\n
\n
\tif ($(\'#canvasBackground\').length) {return;}\n
\n
\tvar dims = config_.dimensions;\n
\tvar canvasbg = svgFactory_.createSVGElement({\n
\t\t\'element\': \'svg\',\n
\t\t\'attr\': {\n
\t\t\t\'id\': \'canvasBackground\',\n
\t\t\t\'width\': dims[0],\n
\t\t\t\'height\': dims[1],\n
\t\t\t\'x\': 0,\n
\t\t\t\'y\': 0,\n
\t\t\t\'overflow\': (svgedit.browser.isWebkit() ? \'none\' : \'visible\'), // Chrome 7 has a problem with this when zooming out\n
\t\t\t\'style\': \'pointer-events:none\'\n
\t\t}\n
\t});\n
\n
\tvar rect = svgFactory_.createSVGElement({\n
\t\t\'element\': \'rect\',\n
\t\t\'attr\': {\n
\t\t\t\'width\': \'100%\',\n
\t\t\t\'height\': \'100%\',\n
\t\t\t\'x\': 0,\n
\t\t\t\'y\': 0,\n
\t\t\t\'stroke-width\': 1,\n
\t\t\t\'stroke\': \'#000\',\n
\t\t\t\'fill\': \'#FFF\',\n
\t\t\t\'style\': \'pointer-events:none\'\n
\t\t}\n
\t});\n
\n
\t// Both Firefox and WebKit are too slow with this filter region (especially at higher\n
\t// zoom levels) and Opera has at least one bug\n
//\tif (!svgedit.browser.isOpera()) rect.setAttribute(\'filter\', \'url(#canvashadow)\');\n
\tcanvasbg.appendChild(rect);\n
\tsvgFactory_.svgRoot().insertBefore(canvasbg, svgFactory_.svgContent());\n
};\n
\n
// Function: svgedit.select.SelectorManager.requestSelector\n
// Returns the selector based on the given element\n
//\n
// Parameters:\n
// elem - DOM element to get the selector for\n
svgedit.select.SelectorManager.prototype.requestSelector = function(elem) {\n
\tif (elem == null) {return null;}\n
\tvar i,\n
\t\tN = this.selectors.length;\n
\t// If we\'ve already acquired one for this element, return it.\n
\tif (typeof(this.selectorMap[elem.id]) == \'object\') {\n
\t\tthis.selectorMap[elem.id].locked = true;\n
\t\treturn this.selectorMap[elem.id];\n
\t}\n
\tfor (i = 0; i < N; ++i) {\n
\t\tif (this.selectors[i] && !this.selectors[i].locked) {\n
\t\t\tthis.selectors[i].locked = true;\n
\t\t\tthis.selectors[i].reset(elem);\n
\t\t\tthis.selectorMap[elem.id] = this.selectors[i];\n
\t\t\treturn this.selectors[i];\n
\t\t}\n
\t}\n
\t// if we reached here, no available selectors were found, we create one\n
\tthis.selectors[N] = new svgedit.select.Selector(N, elem);\n
\tthis.selectorParentGroup.appendChild(this.selectors[N].selectorGroup);\n
\tthis.selectorMap[elem.id] = this.selectors[N];\n
\treturn this.selectors[N];\n
};\n
\n
// Function: svgedit.select.SelectorManager.releaseSelector\n
// Removes the selector of the given element (hides selection box)\n
//\n
// Parameters:\n
// elem - DOM element to remove the selector for\n
svgedit.select.SelectorManager.prototype.releaseSelector = function(elem) {\n
\tif (elem == null) {return;}\n
\tvar i,\n
\t\tN = this.selectors.length,\n
\t\tsel = this.selectorMap[elem.id];\n
\tfor (i = 0; i < N; ++i) {\n
\t\tif (this.selectors[i] && this.selectors[i] == sel) {\n
\t\t\tif (sel.locked == false) {\n
\t\t\t\t// TODO(codedread): Ensure this exists in this module.\n
\t\t\t\tconsole.log(\'WARNING! selector was released but was already unlocked\');\n
\t\t\t}\n
\t\t\tdelete this.selectorMap[elem.id];\n
\t\t\tsel.locked = false;\n
\t\t\tsel.selectedElement = null;\n
\t\t\tsel.showGrips(false);\n
\n
\t\t\t// remove from DOM and store reference in JS but only if it exists in the DOM\n
\t\t\ttry {\n
\t\t\t\tsel.selectorGroup.setAttribute(\'display\', \'none\');\n
\t\t\t} catch(e) { }\n
\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
};\n
\n
// Function: svgedit.select.SelectorManager.getRubberBandBox\n
// Returns the rubberBandBox DOM element. This is the rectangle drawn by the user for selecting/zooming\n
svgedit.select.SelectorManager.prototype.getRubberBandBox = function() {\n
\tif (!this.rubberBandBox) {\n
\t\tthis.rubberBandBox = this.selectorParentGroup.appendChild(\n
\t\t\tsvgFactory_.createSVGElement({\n
\t\t\t\t\'element\': \'rect\',\n
\t\t\t\t\'attr\': {\n
\t\t\t\t\t\'id\': \'selectorRubberBand\',\n
\t\t\t\t\t\'fill\': \'#22C\',\n
\t\t\t\t\t\'fill-opacity\': 0.15,\n
\t\t\t\t\t\'stroke\': \'#22C\',\n
\t\t\t\t\t\'stroke-width\': 0.5,\n
\t\t\t\t\t\'display\': \'none\',\n
\t\t\t\t\t\'style\': \'pointer-events:none\'\n
\t\t\t\t}\n
\t\t\t})\n
\t\t);\n
\t}\n
\treturn this.rubberBandBox;\n
};\n
\n
\n
/**\n
 * Interface: svgedit.select.SVGFactory\n
 * An object that creates SVG elements for the canvas.\n
 *\n
 * interface svgedit.select.SVGFactory {\n
 *   SVGElement createSVGElement(jsonMap);\n
 *   SVGSVGElement svgRoot();\n
 *   SVGSVGElement svgContent();\n
 *\n
 *   Number currentZoom();\n
 *   Object getStrokedBBox(Element[]); // TODO(codedread): Remove when getStrokedBBox() has been put into svgutils.js\n
 * }\n
 */\n
\n
/**\n
 * Function: svgedit.select.init()\n
 * Initializes this module.\n
 *\n
 * Parameters:\n
 * config - an object containing configurable parameters (imgPath)\n
 * svgFactory - an object implementing the SVGFactory interface (see above).\n
 */\n
svgedit.select.init = function(config, svgFactory) {\n
\tconfig_ = config;\n
\tsvgFactory_ = svgFactory;\n
\tselectorManager_ = new svgedit.select.SelectorManager();\n
};\n
\n
/**\n
 * Function: svgedit.select.getSelectorManager\n
 *\n
 * Returns:\n
 * The SelectorManager instance.\n
 */\n
svgedit.select.getSelectorManager = function() {\n
\treturn selectorManager_;\n
};\n
\n
}());

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>15486</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
