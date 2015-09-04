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
            <value> <string>ts40515059.57</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>svgcanvas.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>227916</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgedit, svgCanvas*/\n
/*jslint vars: true, eqeq: true, todo: true, bitwise: true, continue: true, forin: true */\n
/*\n
 * svgcanvas.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 * Copyright(c) 2010 Pavol Rusnak\n
 * Copyright(c) 2010 Jeff Schiller\n
 *\n
 */\n
\n
// Dependencies:\n
// 1) jQuery\n
// 2) browser.js\n
// 3) svgtransformlist.js\n
// 4) math.js\n
// 5) units.js\n
// 6) svgutils.js\n
// 7) sanitize.js\n
// 8) history.js\n
// 9) select.js\n
// 10) draw.js\n
// 11) path.js\n
// 12) coords.js\n
// 13) recalculate.js\n
\n
(function () {\n
\n
if (!window.console) {\n
\twindow.console = {};\n
\twindow.console.log = function(str) {};\n
\twindow.console.dir = function(str) {};\n
}\n
\n
if (window.opera) {\n
\twindow.console.log = function(str) { opera.postError(str); };\n
\twindow.console.dir = function(str) {};\n
}\n
\n
}());\n
\n
// Class: SvgCanvas\n
// The main SvgCanvas class that manages all SVG-related functions\n
//\n
// Parameters:\n
// container - The container HTML element that should hold the SVG root element\n
// config - An object that contains configuration data\n
$.SvgCanvas = function(container, config) {\n
// Alias Namespace constants\n
var NS = svgedit.NS;\n
\n
// Default configuration options\n
var curConfig = {\n
\tshow_outside_canvas: true,\n
\tselectNew: true,\n
\tdimensions: [640, 480]\n
};\n
\n
// Update config with new one if given\n
if (config) {\n
\t$.extend(curConfig, config);\n
}\n
\n
// Array with width/height of canvas\n
var dimensions = curConfig.dimensions;\n
\n
var canvas = this;\n
\n
// "document" element associated with the container (same as window.document using default svg-editor.js)\n
// NOTE: This is not actually a SVG document, but a HTML document.\n
var svgdoc = container.ownerDocument;\n
\n
// This is a container for the document being edited, not the document itself.\n
var svgroot = svgdoc.importNode(svgedit.utilities.text2xml(\n
\t\t\'<svg id="svgroot" xmlns="\' + NS.SVG + \'" xlinkns="\' + NS.XLINK + \'" \' +\n
\t\t\t\'width="\' + dimensions[0] + \'" height="\' + dimensions[1] + \'" x="\' + dimensions[0] + \'" y="\' + dimensions[1] + \'" overflow="visible">\' +\n
\t\t\t\'<defs>\' +\n
\t\t\t\t\'<filter id="canvashadow" filterUnits="objectBoundingBox">\' +\n
\t\t\t\t\t\'<feGaussianBlur in="SourceAlpha" stdDeviation="4" result="blur"/>\'+\n
\t\t\t\t\t\'<feOffset in="blur" dx="5" dy="5" result="offsetBlur"/>\'+\n
\t\t\t\t\t\'<feMerge>\'+\n
\t\t\t\t\t\t\'<feMergeNode in="offsetBlur"/>\'+\n
\t\t\t\t\t\t\'<feMergeNode in="SourceGraphic"/>\'+\n
\t\t\t\t\t\'</feMerge>\'+\n
\t\t\t\t\'</filter>\'+\n
\t\t\t\'</defs>\'+\n
\t\t\'</svg>\').documentElement, true);\n
container.appendChild(svgroot);\n
\n
// The actual element that represents the final output SVG element\n
var svgcontent = svgdoc.createElementNS(NS.SVG, "svg");\n
\n
// This function resets the svgcontent element while keeping it in the DOM.\n
var clearSvgContentElement = canvas.clearSvgContentElement = function() {\n
\twhile (svgcontent.firstChild) { svgcontent.removeChild(svgcontent.firstChild); }\n
\n
\t// TODO: Clear out all other attributes first?\n
\t$(svgcontent).attr({\n
\t\tid: \'svgcontent\',\n
\t\twidth: dimensions[0],\n
\t\theight: dimensions[1],\n
\t\tx: dimensions[0],\n
\t\ty: dimensions[1],\n
\t\toverflow: curConfig.show_outside_canvas ? \'visible\' : \'hidden\',\n
\t\txmlns: NS.SVG,\n
\t\t"xmlns:se": NS.SE,\n
\t\t"xmlns:xlink": NS.XLINK\n
\t}).appendTo(svgroot);\n
\n
\t// TODO: make this string optional and set by the client\n
\tvar comment = svgdoc.createComment(" Created with SVG-edit - http://svg-edit.googlecode.com/ ");\n
\tsvgcontent.appendChild(comment);\n
};\n
clearSvgContentElement();\n
\n
// Prefix string for element IDs\n
var idprefix = "svg_";\n
\n
// Function: setIdPrefix\n
// Changes the ID prefix to the given value\n
//\n
// Parameters: \n
// p - String with the new prefix \n
canvas.setIdPrefix = function(p) {\n
\tidprefix = p;\n
};\n
\n
// Current svgedit.draw.Drawing object\n
// @type {svgedit.draw.Drawing}\n
canvas.current_drawing_ = new svgedit.draw.Drawing(svgcontent, idprefix);\n
\n
// Function: getCurrentDrawing\n
// Returns the current Drawing.\n
// @return {svgedit.draw.Drawing}\n
var getCurrentDrawing = canvas.getCurrentDrawing = function() {\n
\treturn canvas.current_drawing_;\n
};\n
\n
// Float displaying the current zoom level (1 = 100%, .5 = 50%, etc)\n
var current_zoom = 1;\n
\n
// pointer to current group (for in-group editing)\n
var current_group = null;\n
\n
// Object containing data for the currently selected styles\n
var all_properties = {\n
\tshape: {\n
\t\tfill: (curConfig.initFill.color == \'none\' ? \'\' : \'#\') + curConfig.initFill.color,\n
\t\tfill_paint: null,\n
\t\tfill_opacity: curConfig.initFill.opacity,\n
\t\tstroke: "#" + curConfig.initStroke.color,\n
\t\tstroke_paint: null,\n
\t\tstroke_opacity: curConfig.initStroke.opacity,\n
\t\tstroke_width: curConfig.initStroke.width,\n
\t\tstroke_dasharray: \'none\',\n
\t\tstroke_linejoin: \'miter\',\n
\t\tstroke_linecap: \'butt\',\n
\t\topacity: curConfig.initOpacity\n
\t}\n
};\n
\n
all_properties.text = $.extend(true, {}, all_properties.shape);\n
$.extend(all_properties.text, {\n
\tfill: "#000000",\n
\tstroke_width: 0,\n
\tfont_size: 24,\n
\tfont_family: \'serif\'\n
});\n
\n
// Current shape style properties\n
var cur_shape = all_properties.shape;\n
\n
// Array with all the currently selected elements\n
// default size of 1 until it needs to grow bigger\n
var selectedElements = new Array(1);\n
\n
// Function: addSvgElementFromJson\n
// Create a new SVG element based on the given object keys/values and add it to the current layer\n
// The element will be ran through cleanupElement before being returned \n
//\n
// Parameters:\n
// data - Object with the following keys/values:\n
// * element - tag name of the SVG element to create\n
// * attr - Object with attributes key-values to assign to the new element\n
// * curStyles - Boolean indicating that current style attributes should be applied first\n
//\n
// Returns: The new element\n
var addSvgElementFromJson = this.addSvgElementFromJson = function(data) {\n
\tvar shape = svgedit.utilities.getElem(data.attr.id);\n
\t// if shape is a path but we need to create a rect/ellipse, then remove the path\n
\tvar current_layer = getCurrentDrawing().getCurrentLayer();\n
\tif (shape && data.element != shape.tagName) {\n
\t\tcurrent_layer.removeChild(shape);\n
\t\tshape = null;\n
\t}\n
\tif (!shape) {\n
\t\tshape = svgdoc.createElementNS(NS.SVG, data.element);\n
\t\tif (current_layer) {\n
\t\t\t(current_group || current_layer).appendChild(shape);\n
\t\t}\n
\t}\n
\tif (data.curStyles) {\n
\t\tsvgedit.utilities.assignAttributes(shape, {\n
\t\t\t"fill": cur_shape.fill,\n
\t\t\t"stroke": cur_shape.stroke,\n
\t\t\t"stroke-width": cur_shape.stroke_width,\n
\t\t\t"stroke-dasharray": cur_shape.stroke_dasharray,\n
\t\t\t"stroke-linejoin": cur_shape.stroke_linejoin,\n
\t\t\t"stroke-linecap": cur_shape.stroke_linecap,\n
\t\t\t"stroke-opacity": cur_shape.stroke_opacity,\n
\t\t\t"fill-opacity": cur_shape.fill_opacity,\n
\t\t\t"opacity": cur_shape.opacity / 2,\n
\t\t\t"style": "pointer-events:inherit"\n
\t\t}, 100);\n
\t}\n
\tsvgedit.utilities.assignAttributes(shape, data.attr, 100);\n
\tsvgedit.utilities.cleanupElement(shape);\n
\treturn shape;\n
};\n
\n
// import svgtransformlist.js\n
var getTransformList = canvas.getTransformList = svgedit.transformlist.getTransformList;\n
\n
// import from math.js.\n
var transformPoint = svgedit.math.transformPoint;\n
var matrixMultiply = canvas.matrixMultiply = svgedit.math.matrixMultiply;\n
var hasMatrixTransform = canvas.hasMatrixTransform = svgedit.math.hasMatrixTransform;\n
var transformListToTransform = canvas.transformListToTransform = svgedit.math.transformListToTransform;\n
var snapToAngle = svgedit.math.snapToAngle;\n
var getMatrix = svgedit.math.getMatrix;\n
\n
// initialize from units.js\n
// send in an object implementing the ElementContainer interface (see units.js)\n
svgedit.units.init({\n
\tgetBaseUnit: function() { return curConfig.baseUnit; },\n
\tgetElement: svgedit.utilities.getElem,\n
\tgetHeight: function() { return svgcontent.getAttribute("height")/current_zoom; },\n
\tgetWidth: function() { return svgcontent.getAttribute("width")/current_zoom; },\n
\tgetRoundDigits: function() { return save_options.round_digits; }\n
});\n
// import from units.js\n
var convertToNum = canvas.convertToNum = svgedit.units.convertToNum;\n
\n
// import from svgutils.js\n
svgedit.utilities.init({\n
\tgetDOMDocument: function() { return svgdoc; },\n
\tgetDOMContainer: function() { return container; },\n
\tgetSVGRoot: function() { return svgroot; },\n
\t// TODO: replace this mostly with a way to get the current drawing.\n
\tgetSelectedElements: function() { return selectedElements; },\n
\tgetSVGContent: function() { return svgcontent; },\n
\tgetBaseUnit: function() { return curConfig.baseUnit; },\n
\tgetStepSize: function() { return curConfig.stepSize; }\n
});\n
var findDefs = canvas.findDefs = svgedit.utilities.findDefs;\n
var getUrlFromAttr = canvas.getUrlFromAttr = svgedit.utilities.getUrlFromAttr;\n
var getHref = canvas.getHref = svgedit.utilities.getHref;\n
var setHref = canvas.setHref = svgedit.utilities.setHref;\n
var getPathBBox = svgedit.utilities.getPathBBox;\n
var getBBox = canvas.getBBox = svgedit.utilities.getBBox;\n
var getRotationAngle = canvas.getRotationAngle = svgedit.utilities.getRotationAngle;\n
var getElem = canvas.getElem = svgedit.utilities.getElem;\n
var getRefElem = canvas.getRefElem = svgedit.utilities.getRefElem;\n
var assignAttributes = canvas.assignAttributes = svgedit.utilities.assignAttributes;\n
var cleanupElement = this.cleanupElement = svgedit.utilities.cleanupElement;\n
\n
// import from coords.js\n
svgedit.coords.init({\n
\tgetDrawing: function() { return getCurrentDrawing(); },\n
\tgetGridSnapping: function() { return curConfig.gridSnapping; }\n
});\n
var remapElement = this.remapElement = svgedit.coords.remapElement;\n
\n
// import from recalculate.js\n
svgedit.recalculate.init({\n
\tgetSVGRoot: function() { return svgroot; },\n
\tgetStartTransform: function() { return startTransform; },\n
\tsetStartTransform: function(transform) { startTransform = transform; }\n
});\n
var recalculateDimensions = this.recalculateDimensions = svgedit.recalculate.recalculateDimensions;\n
\n
// import from sanitize.js\n
var nsMap = svgedit.getReverseNS();\n
var sanitizeSvg = canvas.sanitizeSvg = svgedit.sanitize.sanitizeSvg;\n
\n
// import from history.js\n
var MoveElementCommand = svgedit.history.MoveElementCommand;\n
var InsertElementCommand = svgedit.history.InsertElementCommand;\n
var RemoveElementCommand = svgedit.history.RemoveElementCommand;\n
var ChangeElementCommand = svgedit.history.ChangeElementCommand;\n
var BatchCommand = svgedit.history.BatchCommand;\n
// Implement the svgedit.history.HistoryEventHandler interface.\n
canvas.undoMgr = new svgedit.history.UndoManager({\n
\thandleHistoryEvent: function(eventType, cmd) {\n
\t\tvar EventTypes = svgedit.history.HistoryEventTypes;\n
\t\t// TODO: handle setBlurOffsets.\n
\t\tif (eventType == EventTypes.BEFORE_UNAPPLY || eventType == EventTypes.BEFORE_APPLY) {\n
\t\t\tcanvas.clearSelection();\n
\t\t} else if (eventType == EventTypes.AFTER_APPLY || eventType == EventTypes.AFTER_UNAPPLY) {\n
\t\t\tvar elems = cmd.elements();\n
\t\t\tcanvas.pathActions.clear();\n
\t\t\tcall("changed", elems);\n
\t\t\tvar cmdType = cmd.type();\n
\t\t\tvar isApply = (eventType == EventTypes.AFTER_APPLY);\n
\t\t\tif (cmdType == MoveElementCommand.type()) {\n
\t\t\t\tvar parent = isApply ? cmd.newParent : cmd.oldParent;\n
\t\t\t\tif (parent == svgcontent) {\n
\t\t\t\t\tcanvas.identifyLayers();\n
\t\t\t\t}\n
\t\t\t} else if (cmdType == InsertElementCommand.type() ||\n
\t\t\t\t\tcmdType == RemoveElementCommand.type()) {\n
\t\t\t\tif (cmd.parent == svgcontent) {\n
\t\t\t\t\tcanvas.identifyLayers();\n
\t\t\t\t}\n
\t\t\t\tif (cmdType == InsertElementCommand.type()) {\n
\t\t\t\t\tif (isApply) {restoreRefElems(cmd.elem);}\n
\t\t\t\t} else {\n
\t\t\t\t\tif (!isApply) {restoreRefElems(cmd.elem);}\n
\t\t\t\t}\n
\t\t\t\tif (cmd.elem.tagName === \'use\') {\n
\t\t\t\t\tsetUseData(cmd.elem);\n
\t\t\t\t}\n
\t\t\t} else if (cmdType == ChangeElementCommand.type()) {\n
\t\t\t\t// if we are changing layer names, re-identify all layers\n
\t\t\t\tif (cmd.elem.tagName == "title" && cmd.elem.parentNode.parentNode == svgcontent) {\n
\t\t\t\t\tcanvas.identifyLayers();\n
\t\t\t\t}\n
\t\t\t\tvar values = isApply ? cmd.newValues : cmd.oldValues;\n
\t\t\t\t// If stdDeviation was changed, update the blur.\n
\t\t\t\tif (values.stdDeviation) {\n
\t\t\t\t\tcanvas.setBlurOffsets(cmd.elem.parentNode, values.stdDeviation);\n
\t\t\t\t}\n
\t\t\t\t// This is resolved in later versions of webkit, perhaps we should\n
\t\t\t\t// have a featured detection for correct \'use\' behavior?\n
\t\t\t\t// ——————————\n
\t\t\t\t// Remove & Re-add hack for Webkit (issue 775) \n
\t\t\t\t//if (cmd.elem.tagName === \'use\' && svgedit.browser.isWebkit()) {\n
\t\t\t\t//\tvar elem = cmd.elem;\n
\t\t\t\t//\tif (!elem.getAttribute(\'x\') && !elem.getAttribute(\'y\')) {\n
\t\t\t\t//\t\tvar parent = elem.parentNode;\n
\t\t\t\t//\t\tvar sib = elem.nextSibling;\n
\t\t\t\t//\t\tparent.removeChild(elem);\n
\t\t\t\t//\t\tparent.insertBefore(elem, sib);\n
\t\t\t\t//\t}\n
\t\t\t\t//}\n
\t\t\t}\n
\t\t}\n
\t}\n
});\n
var addCommandToHistory = function(cmd) {\n
\tcanvas.undoMgr.addCommandToHistory(cmd);\n
};\n
\n
// import from select.js\n
svgedit.select.init(curConfig, {\n
\tcreateSVGElement: function(jsonMap) { return canvas.addSvgElementFromJson(jsonMap); },\n
\tsvgRoot: function() { return svgroot; },\n
\tsvgContent: function() { return svgcontent; },\n
\tcurrentZoom: function() { return current_zoom; },\n
\t// TODO(codedread): Remove when getStrokedBBox() has been put into svgutils.js.\n
\tgetStrokedBBox: function(elems) { return canvas.getStrokedBBox([elems]); }\n
});\n
// this object manages selectors for us\n
var selectorManager = this.selectorManager = svgedit.select.getSelectorManager();\n
\n
// Import from path.js\n
svgedit.path.init({\n
\tgetCurrentZoom: function() { return current_zoom; },\n
\tgetSVGRoot: function() { return svgroot; }\n
});\n
\n
// Interface strings, usually for title elements\n
var uiStrings = {\n
\t"exportNoBlur": "Blurred elements will appear as un-blurred",\n
\t"exportNoforeignObject": "foreignObject elements will not appear",\n
\t"exportNoDashArray": "Strokes will appear filled",\n
\t"exportNoText": "Text may not appear as expected"\n
};\n
\n
var visElems = \'a,circle,ellipse,foreignObject,g,image,line,path,polygon,polyline,rect,svg,text,tspan,use\';\n
var ref_attrs = ["clip-path", "fill", "filter", "marker-end", "marker-mid", "marker-start", "mask", "stroke"];\n
\n
var elData = $.data;\n
\n
// Animation element to change the opacity of any newly created element\n
var opac_ani = document.createElementNS(NS.SVG, \'animate\');\n
$(opac_ani).attr({\n
\tattributeName: \'opacity\',\n
\tbegin: \'indefinite\',\n
\tdur: 1,\n
\tfill: \'freeze\'\n
}).appendTo(svgroot);\n
\n
var restoreRefElems = function(elem) {\n
\t// Look for missing reference elements, restore any found\n
\tvar o, i,\n
\t\tattrs = $(elem).attr(ref_attrs);\n
\tfor (o in attrs) {\n
\t\tvar val = attrs[o];\n
\t\tif (val && val.indexOf(\'url(\') === 0) {\n
\t\t\tvar id = svgedit.utilities.getUrlFromAttr(val).substr(1);\n
\t\t\tvar ref = getElem(id);\n
\t\t\tif (!ref) {\n
\t\t\t\tsvgedit.utilities.findDefs().appendChild(removedElements[id]);\n
\t\t\t\tdelete removedElements[id];\n
\t\t\t}\n
\t\t}\n
\t}\n
\t\n
\tvar childs = elem.getElementsByTagName(\'*\');\n
\t\n
\tif (childs.length) {\n
\t\tfor (i = 0, l = childs.length; i < l; i++) {\n
\t\t\trestoreRefElems(childs[i]);\n
\t\t}\n
\t}\n
};\n
\n
(function() {\n
\t// TODO For Issue 208: this is a start on a thumbnail\n
\t//\tvar svgthumb = svgdoc.createElementNS(NS.SVG, "use");\n
\t//\tsvgthumb.setAttribute(\'width\', \'100\');\n
\t//\tsvgthumb.setAttribute(\'height\', \'100\');\n
\t//\tsvgedit.utilities.setHref(svgthumb, \'#svgcontent\');\n
\t//\tsvgroot.appendChild(svgthumb);\n
\n
}());\n
\n
// Object to contain image data for raster images that were found encodable\n
var encodableImages = {},\n
\t\n
\t// String with image URL of last loadable image\n
\tlast_good_img_url = curConfig.imgPath + \'logo.png\',\n
\t\n
\t// Array with current disabled elements (for in-group editing)\n
\tdisabled_elems = [],\n
\t\n
\t// Object with save options\n
\tsave_options = {round_digits: 5},\n
\t\n
\t// Boolean indicating whether or not a draw action has been started\n
\tstarted = false,\n
\t\n
\t// String with an element\'s initial transform attribute value\n
\tstartTransform = null,\n
\t\n
\t// String indicating the current editor mode\n
\tcurrent_mode = "select",\n
\t\n
\t// String with the current direction in which an element is being resized\n
\tcurrent_resize_mode = "none",\n
\t\n
\t// Object with IDs for imported files, to see if one was already added\n
\timport_ids = {},\n
\n
\t// Current text style properties\n
\tcur_text = all_properties.text,\n
\t\n
\t// Current general properties\n
\tcur_properties = cur_shape,\n
\t\n
\t// Array with selected elements\' Bounding box object\n
//\tselectedBBoxes = new Array(1),\n
\t\n
\t// The DOM element that was just selected\n
\tjustSelected = null,\n
\t\n
\t// DOM element for selection rectangle drawn by the user\n
\trubberBox = null,\n
\t\n
\t// Array of current BBoxes (still needed?)\n
\tcurBBoxes = [],\n
\t\n
\t// Object to contain all included extensions\n
\textensions = {},\n
\t\n
\t// Canvas point for the most recent right click\n
\tlastClickPoint = null,\n
\t\n
\t// Map of deleted reference elements\n
\tremovedElements = {};\n
\n
// Clipboard for cut, copy&pasted elements\n
canvas.clipBoard = [];\n
\n
// Should this return an array by default, so extension results aren\'t overwritten?\n
var runExtensions = this.runExtensions = function(action, vars, returnArray) {\n
\tvar result = returnArray ? [] : false;\n
\t$.each(extensions, function(name, opts) {\n
\t\tif (opts && action in opts) {\n
\t\t\tif (returnArray) {\n
\t\t\t\tresult.push(opts[action](vars));\n
\t\t\t} else {\n
\t\t\t\tresult = opts[action](vars);\n
\t\t\t}\n
\t\t}\n
\t});\n
\treturn result;\n
};\n
\n
// Function: addExtension\n
// Add an extension to the editor\n
// \n
// Parameters:\n
// name - String with the ID of the extension\n
// ext_func - Function supplied by the extension with its data\n
this.addExtension = function(name, ext_func) {\n
\tvar ext;\n
\tif (!(name in extensions)) {\n
\t\t// Provide private vars/funcs here. Is there a better way to do this?\n
\t\tif ($.isFunction(ext_func)) {\n
\t\t\text = ext_func($.extend(canvas.getPrivateMethods(), {\n
\t\t\t\tsvgroot: svgroot,\n
\t\t\t\tsvgcontent: svgcontent,\n
\t\t\t\tnonce: getCurrentDrawing().getNonce(),\n
\t\t\t\tselectorManager: selectorManager\n
\t\t\t}));\n
\t\t} else {\n
\t\t\text = ext_func;\n
\t\t}\n
\t\textensions[name] = ext;\n
\t\tcall("extension_added", ext);\n
\t} else {\n
\t\tconsole.log(\'Cannot add extension "\' + name + \'", an extension by that name already exists"\');\n
\t}\n
};\n
\t\n
// This method rounds the incoming value to the nearest value based on the current_zoom\n
var round = this.round = function(val) {\n
\treturn parseInt(val*current_zoom, 10)/current_zoom;\n
};\n
\n
// This method sends back an array or a NodeList full of elements that\n
// intersect the multi-select rubber-band-box on the current_layer only.\n
// \n
// Since the only browser that supports the SVG DOM getIntersectionList is Opera, \n
// we need to provide an implementation here. We brute-force it for now.\n
// \n
// Reference:\n
// Firefox does not implement getIntersectionList(), see https://bugzilla.mozilla.org/show_bug.cgi?id=501421\n
// Webkit does not implement getIntersectionList(), see https://bugs.webkit.org/show_bug.cgi?id=11274\n
var getIntersectionList = this.getIntersectionList = function(rect) {\n
\tif (rubberBox == null) { return null; }\n
\n
\tvar parent = current_group || getCurrentDrawing().getCurrentLayer();\n
\t\n
\tif (!curBBoxes.length) {\n
\t\t// Cache all bboxes\n
\t\tcurBBoxes = getVisibleElementsAndBBoxes(parent);\n
\t}\n
\t\n
\tvar resultList = null;\n
\ttry {\n
\t\tresultList = parent.getIntersectionList(rect, null);\n
\t} catch(e) { }\n
\n
\tif (resultList == null || typeof(resultList.item) != "function") {\n
\t\tresultList = [];\n
\t\tvar rubberBBox;\n
\t\tif (!rect) {\n
\t\t\trubberBBox = rubberBox.getBBox();\n
\t\t\tvar o,\n
\t\t\t\tbb = {};\n
\t\t\t\n
\t\t\tfor (o in rubberBBox) {\n
\t\t\t\tbb[o] = rubberBBox[o] / current_zoom;\n
\t\t\t}\n
\t\t\trubberBBox = bb;\n
\t\t\t\n
\t\t} else {\n
\t\t\trubberBBox = rect;\n
\t\t}\n
\t\tvar i = curBBoxes.length;\n
\t\twhile (i--) {\n
\t\t\tif (!rubberBBox.width) {continue;}\n
\t\t\tif (svgedit.math.rectsIntersect(rubberBBox, curBBoxes[i].bbox)) {\n
\t\t\t\tresultList.push(curBBoxes[i].elem);\n
\t\t\t}\n
\t\t}\n
\t}\n
\t// addToSelection expects an array, but it\'s ok to pass a NodeList \n
\t// because using square-bracket notation is allowed: \n
\t// http://www.w3.org/TR/DOM-Level-2-Core/ecma-script-binding.html\n
\treturn resultList;\n
};\n
\n
// TODO(codedread): Migrate this into svgutils.js\n
// Function: getStrokedBBox\n
// Get the bounding box for one or more stroked and/or transformed elements\n
// \n
// Parameters:\n
// elems - Array with DOM elements to check\n
// \n
// Returns:\n
// A single bounding box object\n
getStrokedBBox = this.getStrokedBBox = function(elems) {\n
\tif (!elems) {elems = getVisibleElements();}\n
\tif (!elems.length) {return false;}\n
\t// Make sure the expected BBox is returned if the element is a group\n
\tvar getCheckedBBox = function(elem) {\n
\n
\t\ttry {\n
\t\t\t// TODO: Fix issue with rotated groups. Currently they work\n
\t\t\t// fine in FF, but not in other browsers (same problem mentioned\n
\t\t\t// in Issue 339 comment #2).\n
\n
\t\t\tvar bb = svgedit.utilities.getBBox(elem);\n
\t\t\tvar angle = svgedit.utilities.getRotationAngle(elem);\n
\n
\t\t\tif ((angle && angle % 90) ||\n
\t\t\t\tsvgedit.math.hasMatrixTransform(svgedit.transformlist.getTransformList(elem))) {\n
\t\t\t\t// Accurate way to get BBox of rotated element in Firefox:\n
\t\t\t\t// Put element in group and get its BBox\n
\t\t\t\tvar good_bb = false;\n
\t\t\t\t// Get the BBox from the raw path for these elements\n
\t\t\t\tvar elemNames = [\'ellipse\', \'path\', \'line\', \'polyline\', \'polygon\'];\n
\t\t\t\tif (elemNames.indexOf(elem.tagName) >= 0) {\n
\t\t\t\t\tbb = good_bb = canvas.convertToPath(elem, true);\n
\t\t\t\t} else if (elem.tagName == \'rect\') {\n
\t\t\t\t\t// Look for radius\n
\t\t\t\t\tvar rx = elem.getAttribute(\'rx\');\n
\t\t\t\t\tvar ry = elem.getAttribute(\'ry\');\n
\t\t\t\t\tif (rx || ry) {\n
\t\t\t\t\t\tbb = good_bb = canvas.convertToPath(elem, true);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tif (!good_bb) {\n
\t\t\t\t\t// Must use clone else FF freaks out\n
\t\t\t\t\tvar clone = elem.cloneNode(true);\n
\t\t\t\t\tvar g = document.createElementNS(NS.SVG, "g");\n
\t\t\t\t\tvar parent = elem.parentNode;\n
\t\t\t\t\tparent.appendChild(g);\n
\t\t\t\t\tg.appendChild(clone);\n
\t\t\t\t\tbb = svgedit.utilities.bboxToObj(g.getBBox());\n
\t\t\t\t\tparent.removeChild(g);\n
\t\t\t\t}\n
\n
\t\t\t\t// Old method: Works by giving the rotated BBox,\n
\t\t\t\t// this is (unfortunately) what Opera and Safari do\n
\t\t\t\t// natively when getting the BBox of the parent group\n
//\t\t\t\t\t\tvar angle = angle * Math.PI / 180.0;\n
//\t\t\t\t\t\tvar rminx = Number.MAX_VALUE, rminy = Number.MAX_VALUE, \n
//\t\t\t\t\t\t\trmaxx = Number.MIN_VALUE, rmaxy = Number.MIN_VALUE;\n
//\t\t\t\t\t\tvar cx = round(bb.x + bb.width/2),\n
//\t\t\t\t\t\t\tcy = round(bb.y + bb.height/2);\n
//\t\t\t\t\t\tvar pts = [ [bb.x - cx, bb.y - cy], \n
//\t\t\t\t\t\t\t\t\t[bb.x + bb.width - cx, bb.y - cy],\n
//\t\t\t\t\t\t\t\t\t[bb.x + bb.width - cx, bb.y + bb.height - cy],\n
//\t\t\t\t\t\t\t\t\t[bb.x - cx, bb.y + bb.height - cy] ];\n
//\t\t\t\t\t\tvar j = 4;\n
//\t\t\t\t\t\twhile (j--) {\n
//\t\t\t\t\t\t\tvar x = pts[j][0],\n
//\t\t\t\t\t\t\t\ty = pts[j][1],\n
//\t\t\t\t\t\t\t\tr = Math.sqrt( x*x + y*y );\n
//\t\t\t\t\t\t\tvar theta = Math.atan2(y,x) + angle;\n
//\t\t\t\t\t\t\tx = round(r * Math.cos(theta) + cx);\n
//\t\t\t\t\t\t\ty = round(r * Math.sin(theta) + cy);\n
//\t\t\n
//\t\t\t\t\t\t\t// now set the bbox for the shape after it\'s been rotated\n
//\t\t\t\t\t\t\tif (x < rminx) rminx = x;\n
//\t\t\t\t\t\t\tif (y < rminy) rminy = y;\n
//\t\t\t\t\t\t\tif (x > rmaxx) rmaxx = x;\n
//\t\t\t\t\t\t\tif (y > rmaxy) rmaxy = y;\n
//\t\t\t\t\t\t}\n
//\t\t\t\t\t\t\n
//\t\t\t\t\t\tbb.x = rminx;\n
//\t\t\t\t\t\tbb.y = rminy;\n
//\t\t\t\t\t\tbb.width = rmaxx - rminx;\n
//\t\t\t\t\t\tbb.height = rmaxy - rminy;\n
\t\t\t}\n
\t\t\treturn bb;\n
\t\t} catch(e) {\n
\t\t\tconsole.log(elem, e);\n
\t\t\treturn null;\n
\t\t}\n
\t};\n
\n
\tvar full_bb;\n
\t$.each(elems, function() {\n
\t\tif (full_bb) {return;}\n
\t\tif (!this.parentNode) {return;}\n
\t\tfull_bb = getCheckedBBox(this);\n
\t});\n
\n
\t// This shouldn\'t ever happen...\n
\tif (full_bb == null) {return null;}\n
\n
\t// full_bb doesn\'t include the stoke, so this does no good!\n
//\t\tif (elems.length == 1) return full_bb;\n
\n
\tvar max_x = full_bb.x + full_bb.width;\n
\tvar max_y = full_bb.y + full_bb.height;\n
\tvar min_x = full_bb.x;\n
\tvar min_y = full_bb.y;\n
\n
\t// FIXME: same re-creation problem with this function as getCheckedBBox() above\n
\tvar getOffset = function(elem) {\n
\t\tvar sw = elem.getAttribute("stroke-width");\n
\t\tvar offset = 0;\n
\t\tif (elem.getAttribute("stroke") != "none" && !isNaN(sw)) {\n
\t\t\toffset += sw/2;\n
\t\t}\n
\t\treturn offset;\n
\t};\n
\tvar bboxes = [];\n
\t$.each(elems, function(i, elem) {\n
\t\tvar cur_bb = getCheckedBBox(elem);\n
\t\tif (cur_bb) {\n
\t\t\tvar offset = getOffset(elem);\n
\t\t\tmin_x = Math.min(min_x, cur_bb.x - offset);\n
\t\t\tmin_y = Math.min(min_y, cur_bb.y - offset);\n
\t\t\tbboxes.push(cur_bb);\n
\t\t}\n
\t});\n
\t\n
\tfull_bb.x = min_x;\n
\tfull_bb.y = min_y;\n
\t\n
\t$.each(elems, function(i, elem) {\n
\t\tvar cur_bb = bboxes[i];\n
\t\t// ensure that elem is really an element node\n
\t\tif (cur_bb && elem.nodeType == 1) {\n
\t\t\tvar offset = getOffset(elem);\n
\t\t\tmax_x = Math.max(max_x, cur_bb.x + cur_bb.width + offset);\n
\t\t\tmax_y = Math.max(max_y, cur_bb.y + cur_bb.height + offset);\n
\t\t}\n
\t});\n
\t\n
\tfull_bb.width = max_x - min_x;\n
\tfull_bb.height = max_y - min_y;\n
\treturn full_bb;\n
};\n
\n
// Function: getVisibleElements\n
// Get all elements that have a BBox (excludes <defs>, <title>, etc).\n
// Note that 0-opacity, off-screen etc elements are still considered "visible"\n
// for this function\n
//\n
// Parameters:\n
// parent - The parent DOM element to search within\n
//\n
// Returns:\n
// An array with all "visible" elements.\n
var getVisibleElements = this.getVisibleElements = function(parent) {\n
\tif (!parent) {\n
\t\tparent = $(svgcontent).children(); // Prevent layers from being included\n
\t}\n
\t\n
\tvar contentElems = [];\n
\t$(parent).children().each(function(i, elem) {\n
\t\ttry {\n
\t\t\tif (elem.getBBox()) {\n
\t\t\t\tcontentElems.push(elem);\n
\t\t\t}\n
\t\t} catch(e) {}\n
\t});\n
\treturn contentElems.reverse();\n
};\n
\n
// Function: getVisibleElementsAndBBoxes\n
// Get all elements that have a BBox (excludes <defs>, <title>, etc).\n
// Note that 0-opacity, off-screen etc elements are still considered "visible"\n
// for this function\n
//\n
// Parameters:\n
// parent - The parent DOM element to search within\n
//\n
// Returns:\n
// An array with objects that include:\n
// * elem - The element\n
// * bbox - The element\'s BBox as retrieved from getStrokedBBox\n
var getVisibleElementsAndBBoxes = this.getVisibleElementsAndBBoxes = function(parent) {\n
\tif (!parent) {\n
\t\tparent = $(svgcontent).children(); // Prevent layers from being included\n
\t}\n
\tvar contentElems = [];\n
\t$(parent).children().each(function(i, elem) {\n
\t\ttry {\n
\t\t\tif (elem.getBBox()) {\n
\t\t\t\tcontentElems.push({\'elem\':elem, \'bbox\':getStrokedBBox([elem])});\n
\t\t\t}\n
\t\t} catch(e) {}\n
\t});\n
\treturn contentElems.reverse();\n
};\n
\n
// Function: groupSvgElem\n
// Wrap an SVG element into a group element, mark the group as \'gsvg\'\n
//\n
// Parameters:\n
// elem - SVG element to wrap\n
var groupSvgElem = this.groupSvgElem = function(elem) {\n
\tvar g = document.createElementNS(NS.SVG, "g");\n
\telem.parentNode.replaceChild(g, elem);\n
\t$(g).append(elem).data(\'gsvg\', elem)[0].id = getNextId();\n
};\n
\n
// Function: copyElem\n
// Create a clone of an element, updating its ID and its children\'s IDs when needed\n
//\n
// Parameters:\n
// el - DOM element to clone\n
//\n
// Returns: The cloned element\n
var copyElem = function(el) {\n
\t// manually create a copy of the element\n
\tvar new_el = document.createElementNS(el.namespaceURI, el.nodeName);\n
\t$.each(el.attributes, function(i, attr) {\n
\t\tif (attr.localName != \'-moz-math-font-style\') {\n
\t\t\tnew_el.setAttributeNS(attr.namespaceURI, attr.nodeName, attr.nodeValue);\n
\t\t}\n
\t});\n
\t// set the copied element\'s new id\n
\tnew_el.removeAttribute("id");\n
\tnew_el.id = getNextId();\n
\t\n
\t// Opera\'s "d" value needs to be reset for Opera/Win/non-EN\n
\t// Also needed for webkit (else does not keep curved segments on clone)\n
\tif (svgedit.browser.isWebkit() && el.nodeName == \'path\') {\n
\t\tvar fixed_d = pathActions.convertPath(el);\n
\t\tnew_el.setAttribute(\'d\', fixed_d);\n
\t}\n
\n
\t// now create copies of all children\n
\t$.each(el.childNodes, function(i, child) {\n
\t\tswitch(child.nodeType) {\n
\t\t\tcase 1: // element node\n
\t\t\t\tnew_el.appendChild(copyElem(child));\n
\t\t\t\tbreak;\n
\t\t\tcase 3: // text node\n
\t\t\t\tnew_el.textContent = child.nodeValue;\n
\t\t\t\tbreak;\n
\t\t\tdefault:\n
\t\t\t\tbreak;\n
\t\t}\n
\t});\n
\t\n
\tif ($(el).data(\'gsvg\')) {\n
\t\t$(new_el).data(\'gsvg\', new_el.firstChild);\n
\t} else if ($(el).data(\'symbol\')) {\n
\t\tvar ref = $(el).data(\'symbol\');\n
\t\t$(new_el).data(\'ref\', ref).data(\'symbol\', ref);\n
\t} else if (new_el.tagName == \'image\') {\n
\t\tpreventClickDefault(new_el);\n
\t}\n
\treturn new_el;\n
};\n
\n
// Set scope for these functions\n
var getId, getNextId, call;\n
var textActions, pathActions;\n
\n
(function(c) {\n
\n
\t// Object to contain editor event names and callback functions\n
\tvar events = {};\n
\n
\tgetId = c.getId = function() { return getCurrentDrawing().getId(); };\n
\tgetNextId = c.getNextId = function() { return getCurrentDrawing().getNextId(); };\n
\n
\t// Function: call\n
\t// Run the callback function associated with the given event\n
\t//\n
\t// Parameters:\n
\t// event - String with the event name\n
\t// arg - Argument to pass through to the callback function\n
\tcall = c.call = function(event, arg) {\n
\t\tif (events[event]) {\n
\t\t\treturn events[event](this, arg);\n
\t\t}\n
\t};\n
\n
\t// Function: bind\n
\t// Attaches a callback function to an event\n
\t//\n
\t// Parameters:\n
\t// event - String indicating the name of the event\n
\t// f - The callback function to bind to the event\n
\t//\n
\t// Return:\n
\t// The previous event\n
\tc.bind = function(event, f) {\n
\t\tvar old = events[event];\n
\t\tevents[event] = f;\n
\t\treturn old;\n
\t};\n
\n
}(canvas));\n
\n
// Function: canvas.prepareSvg\n
// Runs the SVG Document through the sanitizer and then updates its paths.\n
//\n
// Parameters:\n
// newDoc - The SVG DOM document\n
this.prepareSvg = function(newDoc) {\n
\tthis.sanitizeSvg(newDoc.documentElement);\n
\n
\t// convert paths into absolute commands\n
\tvar i, path, len,\n
\t\tpaths = newDoc.getElementsByTagNameNS(NS.SVG, "path");\n
\tfor (i = 0, len = paths.length; i < len; ++i) {\n
\t\tpath = paths[i];\n
\t\tpath.setAttribute(\'d\', pathActions.convertPath(path));\n
\t\tpathActions.fixEnd(path);\n
\t}\n
};\n
\n
// Function: ffClone\n
// Hack for Firefox bugs where text element features aren\'t updated or get \n
// messed up. See issue 136 and issue 137.\n
// This function clones the element and re-selects it \n
// TODO: Test for this bug on load and add it to "support" object instead of \n
// browser sniffing\n
//\n
// Parameters: \n
// elem - The (text) DOM element to clone\n
var ffClone = function(elem) {\n
\tif (!svgedit.browser.isGecko()) {return elem;}\n
\tvar clone = elem.cloneNode(true);\n
\telem.parentNode.insertBefore(clone, elem);\n
\telem.parentNode.removeChild(elem);\n
\tselectorManager.releaseSelector(elem);\n
\tselectedElements[0] = clone;\n
\tselectorManager.requestSelector(clone).showGrips(true);\n
\treturn clone;\n
};\n
\n
\n
// this.each is deprecated, if any extension used this it can be recreated by doing this:\n
// $(canvas.getRootElem()).children().each(...)\n
\n
// this.each = function(cb) {\n
//\t$(svgroot).children().each(cb);\n
// };\n
\n
\n
// Function: setRotationAngle\n
// Removes any old rotations if present, prepends a new rotation at the\n
// transformed center\n
//\n
// Parameters:\n
// val - The new rotation angle in degrees\n
// preventUndo - Boolean indicating whether the action should be undoable or not\n
this.setRotationAngle = function(val, preventUndo) {\n
\t// ensure val is the proper type\n
\tval = parseFloat(val);\n
\tvar elem = selectedElements[0];\n
\tvar oldTransform = elem.getAttribute("transform");\n
\tvar bbox = svgedit.utilities.getBBox(elem);\n
\tvar cx = bbox.x+bbox.width/2, cy = bbox.y+bbox.height/2;\n
\tvar tlist = svgedit.transformlist.getTransformList(elem);\n
\t\n
\t// only remove the real rotational transform if present (i.e. at index=0)\n
\tif (tlist.numberOfItems > 0) {\n
\t\tvar xform = tlist.getItem(0);\n
\t\tif (xform.type == 4) {\n
\t\t\ttlist.removeItem(0);\n
\t\t}\n
\t}\n
\t// find R_nc and insert it\n
\tif (val != 0) {\n
\t\tvar center = svgedit.math.transformPoint(cx, cy, svgedit.math.transformListToTransform(tlist).matrix);\n
\t\tvar R_nc = svgroot.createSVGTransform();\n
\t\tR_nc.setRotate(val, center.x, center.y);\n
\t\tif (tlist.numberOfItems) {\n
\t\t\ttlist.insertItemBefore(R_nc, 0);\n
\t\t} else {\n
\t\t\ttlist.appendItem(R_nc);\n
\t\t}\n
\t} else if (tlist.numberOfItems == 0) {\n
\t\telem.removeAttribute("transform");\n
\t}\n
\t\n
\tif (!preventUndo) {\n
\t\t// we need to undo it, then redo it so it can be undo-able! :)\n
\t\t// TODO: figure out how to make changes to transform list undo-able cross-browser?\n
\t\tvar newTransform = elem.getAttribute("transform");\n
\t\telem.setAttribute("transform", oldTransform);\n
\t\tchangeSelectedAttribute("transform", newTransform, selectedElements);\n
\t\tcall("changed", selectedElements);\n
\t}\n
\tvar pointGripContainer = svgedit.utilities.getElem("pathpointgrip_container");\n
//\t\tif (elem.nodeName == "path" && pointGripContainer) {\n
//\t\t\tpathActions.setPointContainerTransform(elem.getAttribute("transform"));\n
//\t\t}\n
\tvar selector = selectorManager.requestSelector(selectedElements[0]);\n
\tselector.resize();\n
\tselector.updateGripCursors(val);\n
};\n
\n
// Function: recalculateAllSelectedDimensions\n
// Runs recalculateDimensions on the selected elements, \n
// adding the changes to a single batch command\n
var recalculateAllSelectedDimensions = this.recalculateAllSelectedDimensions = function() {\n
\tvar text = (current_resize_mode == "none" ? "position" : "size");\n
\tvar batchCmd = new svgedit.history.BatchCommand(text);\n
\n
\tvar i = selectedElements.length;\n
\twhile (i--) {\n
\t\tvar elem = selectedElements[i];\n
//\t\t\tif (svgedit.utilities.getRotationAngle(elem) && !svgedit.math.hasMatrixTransform(getTransformList(elem))) {continue;}\n
\t\tvar cmd = svgedit.recalculate.recalculateDimensions(elem);\n
\t\tif (cmd) {\n
\t\t\tbatchCmd.addSubCommand(cmd);\n
\t\t}\n
\t}\n
\n
\tif (!batchCmd.isEmpty()) {\n
\t\taddCommandToHistory(batchCmd);\n
\t\tcall("changed", selectedElements);\n
\t}\n
};\n
\n
// this is how we map paths to our preferred relative segment types\n
var pathMap = [0, \'z\', \'M\', \'m\', \'L\', \'l\', \'C\', \'c\', \'Q\', \'q\', \'A\', \'a\', \n
\t\t\t\t\t\'H\', \'h\', \'V\', \'v\', \'S\', \'s\', \'T\', \'t\'];\n
\t\t\t\t\t\n
// Debug tool to easily see the current matrix in the browser\'s console\n
var logMatrix = function(m) {\n
\tconsole.log([m.a, m.b, m.c, m.d, m.e, m.f]);\n
};\n
\n
// Root Current Transformation Matrix in user units\n
var root_sctm = null;\n
\n
// Group: Selection\n
\n
// Function: clearSelection\n
// Clears the selection. The \'selected\' handler is then called.\n
// Parameters: \n
// noCall - Optional boolean that when true does not call the "selected" handler\n
var clearSelection = this.clearSelection = function(noCall) {\n
\tif (selectedElements[0] != null) {\n
\t\tvar i, elem,\n
\t\t\tlen = selectedElements.length;\n
\t\tfor (i = 0; i < len; ++i) {\n
\t\t\telem = selectedElements[i];\n
\t\t\tif (elem == null) {break;}\n
\t\t\tselectorManager.releaseSelector(elem);\n
\t\t\tselectedElements[i] = null;\n
\t\t}\n
//\t\tselectedBBoxes[0] = null;\n
\t}\n
\tif (!noCall) {call("selected", selectedElements);}\n
};\n
\n
// TODO: do we need to worry about selectedBBoxes here?\n
\n
\n
// Function: addToSelection\n
// Adds a list of elements to the selection. The \'selected\' handler is then called.\n
//\n
// Parameters:\n
// elemsToAdd - an array of DOM elements to add to the selection\n
// showGrips - a boolean flag indicating whether the resize grips should be shown\n
var addToSelection = this.addToSelection = function(elemsToAdd, showGrips) {\n
\tif (elemsToAdd.length == 0) { return; }\n
\t// find the first null in our selectedElements array\n
\tvar j = 0;\n
\t\n
\twhile (j < selectedElements.length) {\n
\t\tif (selectedElements[j] == null) { \n
\t\t\tbreak;\n
\t\t}\n
\t\t++j;\n
\t}\n
\n
\t// now add each element consecutively\n
\tvar i = elemsToAdd.length;\n
\twhile (i--) {\n
\t\tvar elem = elemsToAdd[i];\n
\t\tif (!elem || !svgedit.utilities.getBBox(elem)) {continue;}\n
\n
\t\tif (elem.tagName === \'a\' && elem.childNodes.length === 1) {\n
\t\t\t// Make "a" element\'s child be the selected element \n
\t\t\telem = elem.firstChild;\n
\t\t}\n
\n
\t\t// if it\'s not already there, add it\n
\t\tif (selectedElements.indexOf(elem) == -1) {\n
\n
\t\t\tselectedElements[j] = elem;\n
\n
\t\t\t// only the first selectedBBoxes element is ever used in the codebase these days\n
//\t\t\tif (j == 0) selectedBBoxes[0] = svgedit.utilities.getBBox(elem);\n
\t\t\tj++;\n
\t\t\tvar sel = selectorManager.requestSelector(elem);\n
\t\n
\t\t\tif (selectedElements.length > 1) {\n
\t\t\t\tsel.showGrips(false);\n
\t\t\t}\n
\t\t}\n
\t}\n
\tcall("selected", selectedElements);\n
\t\n
\tif (showGrips || selectedElements.length == 1) {\n
\t\tselectorManager.requestSelector(selectedElements[0]).showGrips(true);\n
\t}\n
\telse {\n
\t\tselectorManager.requestSelector(selectedElements[0]).showGrips(false);\n
\t}\n
\n
\t// make sure the elements are in the correct order\n
\t// See: http://www.w3.org/TR/DOM-Level-3-Core/core.html#Node3-compareDocumentPosition\n
\n
\tselectedElements.sort(function(a, b) {\n
\t\tif (a && b && a.compareDocumentPosition) {\n
\t\t\treturn 3 - (b.compareDocumentPosition(a) & 6);\t\n
\t\t}\n
\t\tif (a == null) {\n
\t\t\treturn 1;\n
\t\t}\n
\t});\n
\t\n
\t// Make sure first elements are not null\n
\twhile (selectedElements[0] == null) {\n
\t\tselectedElements.shift(0);\n
\t}\n
};\n
\n
// Function: selectOnly()\n
// Selects only the given elements, shortcut for clearSelection(); addToSelection()\n
//\n
// Parameters:\n
// elems - an array of DOM elements to be selected\n
var selectOnly = this.selectOnly = function(elems, showGrips) {\n
\tclearSelection(true);\n
\taddToSelection(elems, showGrips);\n
};\n
\n
// TODO: could use slice here to make this faster?\n
// TODO: should the \'selected\' handler\n
\n
// Function: removeFromSelection\n
// Removes elements from the selection.\n
//\n
// Parameters:\n
// elemsToRemove - an array of elements to remove from selection\n
var removeFromSelection = this.removeFromSelection = function(elemsToRemove) {\n
\tif (selectedElements[0] == null) { return; }\n
\tif (elemsToRemove.length == 0) { return; }\n
\n
\t// find every element and remove it from our array copy\n
\tvar i,\n
\t\tj = 0,\n
\t\tnewSelectedItems = new Array(selectedElements.length),\n
\t\tlen = selectedElements.length;\n
\tfor (i = 0; i < len; ++i) {\n
\t\tvar elem = selectedElements[i];\n
\t\tif (elem) {\n
\t\t\t// keep the item\n
\t\t\tif (elemsToRemove.indexOf(elem) == -1) {\n
\t\t\t\tnewSelectedItems[j] = elem;\n
\t\t\t\tj++;\n
\t\t\t} else { // remove the item and its selector\n
\t\t\t\tselectorManager.releaseSelector(elem);\n
\t\t\t}\n
\t\t}\n
\t}\n
\t// the copy becomes the master now\n
\tselectedElements = newSelectedItems;\n
};\n
\n
// Function: selectAllInCurrentLayer\n
// Clears the selection, then adds all elements in the current layer to the selection.\n
this.selectAllInCurrentLayer = function() {\n
\tvar current_layer = getCurrentDrawing().getCurrentLayer();\n
\tif (current_layer) {\n
\t\tcurrent_mode = "select";\n
\t\tselectOnly($(current_group || current_layer).children());\n
\t}\n
};\n
\n
// Function: getMouseTarget\n
// Gets the desired element from a mouse event\n
// \n
// Parameters:\n
// evt - Event object from the mouse event\n
// \n
// Returns:\n
// DOM element we want\n
var getMouseTarget = this.getMouseTarget = function(evt) {\n
\tif (evt == null) {\n
\t\treturn null;\n
\t}\n
\tvar mouse_target = evt.target;\n
\t\n
\t// if it was a <use>, Opera and WebKit return the SVGElementInstance\n
\tif (mouse_target.correspondingUseElement) {mouse_target = mouse_target.correspondingUseElement;}\n
\t\n
\t// for foreign content, go up until we find the foreignObject\n
\t// WebKit browsers set the mouse target to the svgcanvas div \n
\tif ([NS.MATH, NS.HTML].indexOf(mouse_target.namespaceURI) >= 0 && \n
\t\tmouse_target.id != "svgcanvas") \n
\t{\n
\t\twhile (mouse_target.nodeName != "foreignObject") {\n
\t\t\tmouse_target = mouse_target.parentNode;\n
\t\t\tif (!mouse_target) {return svgroot;}\n
\t\t}\n
\t}\n
\t\n
\t// Get the desired mouse_target with jQuery selector-fu\n
\t// If it\'s root-like, select the root\n
\tvar current_layer = getCurrentDrawing().getCurrentLayer();\n
\tif ([svgroot, container, svgcontent, current_layer].indexOf(mouse_target) >= 0) {\n
\t\treturn svgroot;\n
\t}\n
\t\n
\tvar $target = $(mouse_target);\n
\n
\t// If it\'s a selection grip, return the grip parent\n
\tif ($target.closest(\'#selectorParentGroup\').length) {\n
\t\t// While we could instead have just returned mouse_target, \n
\t\t// this makes it easier to indentify as being a selector grip\n
\t\treturn selectorManager.selectorParentGroup;\n
\t}\n
\n
\twhile (mouse_target.parentNode !== (current_group || current_layer)) {\n
\t\tmouse_target = mouse_target.parentNode;\n
\t}\n
\t\n
//\t\n
//\t// go up until we hit a child of a layer\n
//\twhile (mouse_target.parentNode.parentNode.tagName == \'g\') {\n
//\t\tmouse_target = mouse_target.parentNode;\n
//\t}\n
\t// Webkit bubbles the mouse event all the way up to the div, so we\n
\t// set the mouse_target to the svgroot like the other browsers\n
//\tif (mouse_target.nodeName.toLowerCase() == "div") {\n
//\t\tmouse_target = svgroot;\n
//\t}\n
\t\n
\treturn mouse_target;\n
};\n
\n
// Mouse events\n
(function() {\n
\tvar d_attr = null,\n
\t\tstart_x = null,\n
\t\tstart_y = null,\n
\t\tr_start_x = null,\n
\t\tr_start_y = null,\n
\t\tinit_bbox = {},\n
\t\tfreehand = {\n
\t\t\tminx: null,\n
\t\t\tminy: null,\n
\t\t\tmaxx: null,\n
\t\t\tmaxy: null\n
\t\t},\n
\t\tsumDistance = 0,\n
\t\tcontrollPoint2 = {x:0, y:0},\n
\t\tcontrollPoint1 = {x:0, y:0},\n
\t\tstart = {x:0, y:0},\n
\t\tend = {x:0, y:0},\n
\t\tparameter,\n
\t\tnextParameter,\n
\t\tbSpline = {x:0, y:0},\n
\t\tnextPos = {x:0, y:0},\n
\t\tTHRESHOLD_DIST = 0.8,\n
\t\tSTEP_COUNT = 10;\n
\n
\tvar getBsplinePoint = function(t) {\n
\t\tvar spline = {x:0, y:0},\n
\t\t\tp0 = controllPoint2,\n
\t\t\tp1 = controllPoint1,\n
\t\t\tp2 = start,\n
\t\t\tp3 = end,\n
\t\t\tS = 1.0 / 6.0,\n
\t\t\tt2 = t * t,\n
\t\t\tt3 = t2 * t;\n
\n
\t\tvar m = [\n
\t\t\t\t[-1, 3, -3, 1],\n
\t\t\t\t[3, -6, 3, 0],\n
\t\t\t\t[-3, 0, 3, 0],\n
\t\t\t\t[1, 4, 1, 0]\n
\t\t\t];\n
\n
\t\tspline.x = S * (\n
\t\t\t(p0.x * m[0][0] + p1.x * m[0][1] + p2.x * m[0][2] + p3.x * m[0][3] ) * t3 +\n
\t\t\t\t(p0.x * m[1][0] + p1.x * m[1][1] + p2.x * m[1][2] + p3.x * m[1][3] ) * t2 +\n
\t\t\t\t(p0.x * m[2][0] + p1.x * m[2][1] + p2.x * m[2][2] + p3.x * m[2][3] ) * t +\n
\t\t\t\t(p0.x * m[3][0] + p1.x * m[3][1] + p2.x * m[3][2] + p3.x * m[3][3] )\n
\t\t);\n
\t\tspline.y = S * (\n
\t\t\t(p0.y * m[0][0] + p1.y * m[0][1] + p2.y * m[0][2] + p3.y * m[0][3] ) * t3 +\n
\t\t\t\t(p0.y * m[1][0] + p1.y * m[1][1] + p2.y * m[1][2] + p3.y * m[1][3] ) * t2 +\n
\t\t\t\t(p0.y * m[2][0] + p1.y * m[2][1] + p2.y * m[2][2] + p3.y * m[2][3] ) * t +\n
\t\t\t\t(p0.y * m[3][0] + p1.y * m[3][1] + p2.y * m[3][2] + p3.y * m[3][3] )\n
\t\t);\n
\n
\t\treturn {\n
\t\t\tx:spline.x,\n
\t\t\ty:spline.y\n
\t\t};\n
\t};\n
\t// - when we are in a create mode, the element is added to the canvas\n
\t// but the action is not recorded until mousing up\n
\t// - when we are in select mode, select the element, remember the position\n
\t// and do nothing else\n
\tvar mouseDown = function(evt) {\n
\t\tif (canvas.spaceKey || evt.button === 1) {return;}\n
\n
\t\tvar right_click = evt.button === 2;\n
\t\n
\t\tif (evt.altKey) { // duplicate when dragging\n
\t\t\tsvgCanvas.cloneSelectedElements(0, 0);\n
\t\t}\n
\t\n
\t\troot_sctm = $(\'#svgcontent g\')[0].getScreenCTM().inverse();\n
\t\t\n
\t\tvar pt = svgedit.math.transformPoint( evt.pageX, evt.pageY, root_sctm ),\n
\t\t\tmouse_x = pt.x * current_zoom,\n
\t\t\tmouse_y = pt.y * current_zoom;\n
\t\t\t\n
\t\tevt.preventDefault();\n
\n
\t\tif (right_click) {\n
\t\t\tcurrent_mode = "select";\n
\t\t\tlastClickPoint = pt;\n
\t\t}\n
\t\t\n
\t\t// This would seem to be unnecessary...\n
//\t\tif ([\'select\', \'resize\'].indexOf(current_mode) == -1) {\n
//\t\t\tsetGradient();\n
//\t\t}\n
\t\t\n
\t\tvar x = mouse_x / current_zoom,\n
\t\t\ty = mouse_y / current_zoom,\n
\t\t\tmouse_target = getMouseTarget(evt);\n
\t\t\n
\t\tif (mouse_target.tagName === \'a\' && mouse_target.childNodes.length === 1) {\n
\t\t\tmouse_target = mouse_target.firstChild;\n
\t\t}\n
\t\t\n
\t\t// real_x/y ignores grid-snap value\n
\t\tvar real_x = x;\n
\t\tr_start_x = start_x = x;\n
\t\tvar real_y = y;\n
\t\tr_start_y = start_y = y;\n
\n
\t\tif (curConfig.gridSnapping){\n
\t\t\tx = svgedit.utilities.snapToGrid(x);\n
\t\t\ty = svgedit.utilities.snapToGrid(y);\n
\t\t\tstart_x = svgedit.utilities.snapToGrid(start_x);\n
\t\t\tstart_y = svgedit.utilities.snapToGrid(start_y);\n
\t\t}\n
\n
\t\t// if it is a selector grip, then it must be a single element selected, \n
\t\t// set the mouse_target to that and update the mode to rotate/resize\n
\t\t\n
\t\tif (mouse_target == selectorManager.selectorParentGroup && selectedElements[0] != null) {\n
\t\t\tvar grip = evt.target;\n
\t\t\tvar griptype = elData(grip, "type");\n
\t\t\t// rotating\n
\t\t\tif (griptype == "rotate") {\n
\t\t\t\tcurrent_mode = "rotate";\n
\t\t\t}\n
\t\t\t// resizing\n
\t\t\telse if (griptype == "resize") {\n
\t\t\t\tcurrent_mode = "resize";\n
\t\t\t\tcurrent_resize_mode = elData(grip, "dir");\n
\t\t\t}\n
\t\t\tmouse_target = selectedElements[0];\n
\t\t}\n
\t\t\n
\t\tstartTransform = mouse_target.getAttribute("transform");\n
\t\tvar i, stroke_w,\n
\t\t\ttlist = svgedit.transformlist.getTransformList(mouse_target);\n
\t\tswitch (current_mode) {\n
\t\t\tcase "select":\n
\t\t\t\tstarted = true;\n
\t\t\t\tcurrent_resize_mode = "none";\n
\t\t\t\tif (right_click) {started = false;}\n
\t\t\t\t\n
\t\t\t\tif (mouse_target != svgroot) {\n
\t\t\t\t\t// if this element is not yet selected, clear selection and select it\n
\t\t\t\t\tif (selectedElements.indexOf(mouse_target) == -1) {\n
\t\t\t\t\t\t// only clear selection if shift is not pressed (otherwise, add \n
\t\t\t\t\t\t// element to selection)\n
\t\t\t\t\t\tif (!evt.shiftKey) {\n
\t\t\t\t\t\t\t// No need to do the call here as it will be done on addToSelection\n
\t\t\t\t\t\t\tclearSelection(true);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\taddToSelection([mouse_target]);\n
\t\t\t\t\t\tjustSelected = mouse_target;\n
\t\t\t\t\t\tpathActions.clear();\n
\t\t\t\t\t}\n
\t\t\t\t\t// else if it\'s a path, go into pathedit mode in mouseup\n
\t\t\t\t\t\n
\t\t\t\t\tif (!right_click) {\n
\t\t\t\t\t\t// insert a dummy transform so if the element(s) are moved it will have\n
\t\t\t\t\t\t// a transform to use for its translate\n
\t\t\t\t\t\tfor (i = 0; i < selectedElements.length; ++i) {\n
\t\t\t\t\t\t\tif (selectedElements[i] == null) {continue;}\n
\t\t\t\t\t\t\tvar slist = svgedit.transformlist.getTransformList(selectedElements[i]);\n
\t\t\t\t\t\t\tif (slist.numberOfItems) {\n
\t\t\t\t\t\t\t\tslist.insertItemBefore(svgroot.createSVGTransform(), 0);\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tslist.appendItem(svgroot.createSVGTransform());\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t} else if (!right_click){\n
\t\t\t\t\tclearSelection();\n
\t\t\t\t\tcurrent_mode = "multiselect";\n
\t\t\t\t\tif (rubberBox == null) {\n
\t\t\t\t\t\trubberBox = selectorManager.getRubberBandBox();\n
\t\t\t\t\t}\n
\t\t\t\t\tr_start_x *= current_zoom;\n
\t\t\t\t\tr_start_y *= current_zoom;\n
//\t\t\t\t\tconsole.log(\'p\',[evt.pageX, evt.pageY]);\t\t\t\t\t\n
//\t\t\t\t\tconsole.log(\'c\',[evt.clientX, evt.clientY]);\t\n
//\t\t\t\t\tconsole.log(\'o\',[evt.offsetX, evt.offsetY]);\t\n
//\t\t\t\t\tconsole.log(\'s\',[start_x, start_y]);\n
\t\t\t\t\t\n
\t\t\t\t\tsvgedit.utilities.assignAttributes(rubberBox, {\n
\t\t\t\t\t\t\'x\': r_start_x,\n
\t\t\t\t\t\t\'y\': r_start_y,\n
\t\t\t\t\t\t\'width\': 0,\n
\t\t\t\t\t\t\'height\': 0,\n
\t\t\t\t\t\t\'display\': \'inline\'\n
\t\t\t\t\t}, 100);\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "zoom": \n
\t\t\t\tstarted = true;\n
\t\t\t\tif (rubberBox == null) {\n
\t\t\t\t\trubberBox = selectorManager.getRubberBandBox();\n
\t\t\t\t}\n
\t\t\t\tsvgedit.utilities.assignAttributes(rubberBox, {\n
\t\t\t\t\t\t\'x\': real_x * current_zoom,\n
\t\t\t\t\t\t\'y\': real_x * current_zoom,\n
\t\t\t\t\t\t\'width\': 0,\n
\t\t\t\t\t\t\'height\': 0,\n
\t\t\t\t\t\t\'display\': \'inline\'\n
\t\t\t\t}, 100);\n
\t\t\t\tbreak;\n
\t\t\tcase "resize":\n
\t\t\t\tstarted = true;\n
\t\t\t\tstart_x = x;\n
\t\t\t\tstart_y = y;\n
\t\t\t\t\n
\t\t\t\t// Getting the BBox from the selection box, since we know we\n
\t\t\t\t// want to orient around it\n
\t\t\t\tinit_bbox = svgedit.utilities.getBBox($(\'#selectedBox0\')[0]);\n
\t\t\t\tvar bb = {};\n
\t\t\t\t$.each(init_bbox, function(key, val) {\n
\t\t\t\t\tbb[key] = val/current_zoom;\n
\t\t\t\t});\n
\t\t\t\tinit_bbox = bb;\n
\t\t\t\t\n
\t\t\t\t// append three dummy transforms to the tlist so that\n
\t\t\t\t// we can translate,scale,translate in mousemove\n
\t\t\t\tvar pos = svgedit.utilities.getRotationAngle(mouse_target) ? 1 : 0;\n
\t\t\t\t\n
\t\t\t\tif (svgedit.math.hasMatrixTransform(tlist)) {\n
\t\t\t\t\ttlist.insertItemBefore(svgroot.createSVGTransform(), pos);\n
\t\t\t\t\ttlist.insertItemBefore(svgroot.createSVGTransform(), pos);\n
\t\t\t\t\ttlist.insertItemBefore(svgroot.createSVGTransform(), pos);\n
\t\t\t\t} else {\n
\t\t\t\t\ttlist.appendItem(svgroot.createSVGTransform());\n
\t\t\t\t\ttlist.appendItem(svgroot.createSVGTransform());\n
\t\t\t\t\ttlist.appendItem(svgroot.createSVGTransform());\n
\t\t\t\t\t\n
\t\t\t\t\tif (svgedit.browser.supportsNonScalingStroke()) {\n
\t\t\t\t\t\t// Handle crash for newer Chrome and Safari 6 (Mobile and Desktop): \n
\t\t\t\t\t\t// https://code.google.com/p/svg-edit/issues/detail?id=904\n
\t\t\t\t\t\t// Chromium issue: https://code.google.com/p/chromium/issues/detail?id=114625\n
\t\t\t\t\t\t// TODO: Remove this workaround once vendor fixes the issue\n
\t\t\t\t\t\tvar isWebkit = svgedit.browser.isWebkit();\n
\n
\t\t\t\t\t\tif (isWebkit) {\n
\t\t\t\t\t\t\tvar delayedStroke = function(ele) {\n
\t\t\t\t\t\t\t\tvar _stroke = ele.getAttributeNS(null, \'stroke\');\n
\t\t\t\t\t\t\t\tele.removeAttributeNS(null, \'stroke\');\n
\t\t\t\t\t\t\t\t//Re-apply stroke after delay. Anything higher than 1 seems to cause flicker\n
\t\t\t\t\t\t\t\tsetTimeout(function() { ele.setAttributeNS(null, \'stroke\', _stroke); }, 0);\n
\t\t\t\t\t\t\t};\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tmouse_target.style.vectorEffect = \'non-scaling-stroke\';\n
\t\t\t\t\t\tif (isWebkit) {delayedStroke(mouse_target);}\n
\n
\t\t\t\t\t\tvar all = mouse_target.getElementsByTagName(\'*\'),\n
\t\t\t\t\t\t\tlen = all.length;\n
\t\t\t\t\t\tfor (i = 0; i < len; i++) {\n
\t\t\t\t\t\t\tall[i].style.vectorEffect = \'non-scaling-stroke\';\n
\t\t\t\t\t\t\tif (isWebkit) {delayedStroke(all[i]);}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "fhellipse":\n
\t\t\tcase "fhrect":\n
\t\t\tcase "fhpath":\n
\t\t\t\tstart.x = real_x;\n
\t\t\t\tstart.y = real_y;\n
\t\t\t\tstarted = true;\n
\t\t\t\td_attr = real_x + "," + real_y + " ";\n
\t\t\t\tstroke_w = cur_shape.stroke_width == 0 ? 1 : cur_shape.stroke_width;\n
\t\t\t\taddSvgElementFromJson({\n
\t\t\t\t\t"element": "polyline",\n
\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t"points": d_attr,\n
\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t"fill": "none",\n
\t\t\t\t\t\t"opacity": cur_shape.opacity / 2,\n
\t\t\t\t\t\t"stroke-linecap": "round",\n
\t\t\t\t\t\t"style": "pointer-events:none"\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tfreehand.minx = real_x;\n
\t\t\t\tfreehand.maxx = real_x;\n
\t\t\t\tfreehand.miny = real_y;\n
\t\t\t\tfreehand.maxy = real_y;\n
\t\t\t\tbreak;\n
\t\t\tcase "image":\n
\t\t\t\tstarted = true;\n
\t\t\t\tvar newImage = addSvgElementFromJson({\n
\t\t\t\t\t"element": "image",\n
\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t"x": x,\n
\t\t\t\t\t\t"y": y,\n
\t\t\t\t\t\t"width": 0,\n
\t\t\t\t\t\t"height": 0,\n
\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t"opacity": cur_shape.opacity / 2,\n
\t\t\t\t\t\t"style": "pointer-events:inherit"\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tsetHref(newImage, last_good_img_url);\n
\t\t\t\tpreventClickDefault(newImage);\n
\t\t\t\tbreak;\n
\t\t\tcase "square":\n
\t\t\t\t// FIXME: once we create the rect, we lose information that this was a square\n
\t\t\t\t// (for resizing purposes this could be important)\n
\t\t\tcase "rect":\n
\t\t\t\tstarted = true;\n
\t\t\t\tstart_x = x;\n
\t\t\t\tstart_y = y;\n
\t\t\t\taddSvgElementFromJson({\n
\t\t\t\t\t"element": "rect",\n
\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t"x": x,\n
\t\t\t\t\t\t"y": y,\n
\t\t\t\t\t\t"width": 0,\n
\t\t\t\t\t\t"height": 0,\n
\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t"opacity": cur_shape.opacity / 2\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tbreak;\n
\t\t\tcase "line":\n
\t\t\t\tstarted = true;\n
\t\t\t\tstroke_w = cur_shape.stroke_width == 0 ? 1 : cur_shape.stroke_width;\n
\t\t\t\taddSvgElementFromJson({\n
\t\t\t\t\t"element": "line",\n
\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t"x1": x,\n
\t\t\t\t\t\t"y1": y,\n
\t\t\t\t\t\t"x2": x,\n
\t\t\t\t\t\t"y2": y,\n
\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t"stroke": cur_shape.stroke,\n
\t\t\t\t\t\t"stroke-width": stroke_w,\n
\t\t\t\t\t\t"stroke-dasharray": cur_shape.stroke_dasharray,\n
\t\t\t\t\t\t"stroke-linejoin": cur_shape.stroke_linejoin,\n
\t\t\t\t\t\t"stroke-linecap": cur_shape.stroke_linecap,\n
\t\t\t\t\t\t"stroke-opacity": cur_shape.stroke_opacity,\n
\t\t\t\t\t\t"fill": "none",\n
\t\t\t\t\t\t"opacity": cur_shape.opacity / 2,\n
\t\t\t\t\t\t"style": "pointer-events:none"\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tbreak;\n
\t\t\tcase "circle":\n
\t\t\t\tstarted = true;\n
\t\t\t\taddSvgElementFromJson({\n
\t\t\t\t\t"element": "circle",\n
\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t"cx": x,\n
\t\t\t\t\t\t"cy": y,\n
\t\t\t\t\t\t"r": 0,\n
\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t"opacity": cur_shape.opacity / 2\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tbreak;\n
\t\t\tcase "ellipse":\n
\t\t\t\tstarted = true;\n
\t\t\t\taddSvgElementFromJson({\n
\t\t\t\t\t"element": "ellipse",\n
\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t"cx": x,\n
\t\t\t\t\t\t"cy": y,\n
\t\t\t\t\t\t"rx": 0,\n
\t\t\t\t\t\t"ry": 0,\n
\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t"opacity": cur_shape.opacity / 2\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tbreak;\n
\t\t\tcase "text":\n
\t\t\t\tstarted = true;\n
\t\t\t\tvar newText = addSvgElementFromJson({\n
\t\t\t\t\t"element": "text",\n
\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t"x": x,\n
\t\t\t\t\t\t"y": y,\n
\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t"fill": cur_text.fill,\n
\t\t\t\t\t\t"stroke-width": cur_text.stroke_width,\n
\t\t\t\t\t\t"font-size": cur_text.font_size,\n
\t\t\t\t\t\t"font-family": cur_text.font_family,\n
\t\t\t\t\t\t"text-anchor": "middle",\n
\t\t\t\t\t\t"xml:space": "preserve",\n
\t\t\t\t\t\t"opacity": cur_shape.opacity\n
\t\t\t\t\t}\n
\t\t\t\t});\n
//\t\t\t\t\tnewText.textContent = "text";\n
\t\t\t\tbreak;\n
\t\t\tcase "path":\n
\t\t\t\t// Fall through\n
\t\t\tcase "pathedit":\n
\t\t\t\tstart_x *= current_zoom;\n
\t\t\t\tstart_y *= current_zoom;\n
\t\t\t\tpathActions.mouseDown(evt, mouse_target, start_x, start_y);\n
\t\t\t\tstarted = true;\n
\t\t\t\tbreak;\n
\t\t\tcase "textedit":\n
\t\t\t\tstart_x *= current_zoom;\n
\t\t\t\tstart_y *= current_zoom;\n
\t\t\t\ttextActions.mouseDown(evt, mouse_target, start_x, start_y);\n
\t\t\t\tstarted = true;\n
\t\t\t\tbreak;\n
\t\t\tcase "rotate":\n
\t\t\t\tstarted = true;\n
\t\t\t\t// we are starting an undoable change (a drag-rotation)\n
\t\t\t\tcanvas.undoMgr.beginUndoableChange("transform", selectedElements);\n
\t\t\t\tbreak;\n
\t\t\tdefault:\n
\t\t\t\t// This could occur in an extension\n
\t\t\t\tbreak;\n
\t\t}\n
\t\t\n
\t\tvar ext_result = runExtensions("mouseDown", {\n
\t\t\tevent: evt,\n
\t\t\tstart_x: start_x,\n
\t\t\tstart_y: start_y,\n
\t\t\tselectedElements: selectedElements\n
\t\t}, true);\n
\t\t\n
\t\t$.each(ext_result, function(i, r) {\n
\t\t\tif (r && r.started) {\n
\t\t\t\tstarted = true;\n
\t\t\t}\n
\t\t});\n
\t};\n
\t\n
\t// in this function we do not record any state changes yet (but we do update\n
\t// any elements that are still being created, moved or resized on the canvas)\n
\tvar mouseMove = function(evt) {\n
\t\tif (!started) {return;}\n
\t\tif (evt.button === 1 || canvas.spaceKey) {return;}\n
\n
\t\tvar i, xya, c, cx, cy, dx, dy, len, angle, box,\n
\t\t\tselected = selectedElements[0],\n
\t\t\tpt = svgedit.math.transformPoint( evt.pageX, evt.pageY, root_sctm ),\n
\t\t\tmouse_x = pt.x * current_zoom,\n
\t\t\tmouse_y = pt.y * current_zoom,\n
\t\t\tshape = svgedit.utilities.getElem(getId());\n
\n
\t\tvar real_x = mouse_x / current_zoom;\n
\t\tx = real_x;\n
\t\tvar real_y = mouse_y / current_zoom;\n
\t\ty = real_y;\n
\t\n
\t\tif (curConfig.gridSnapping){\n
\t\t\tx = svgedit.utilities.snapToGrid(x);\n
\t\t\ty = svgedit.utilities.snapToGrid(y);\n
\t\t}\n
\n
\t\tevt.preventDefault();\n
\t\tvar tlist;\n
\t\tswitch (current_mode) {\n
\t\t\tcase "select":\n
\t\t\t\t// we temporarily use a translate on the element(s) being dragged\n
\t\t\t\t// this transform is removed upon mousing up and the element is \n
\t\t\t\t// relocated to the new location\n
\t\t\t\tif (selectedElements[0] !== null) {\n
\t\t\t\t\tdx = x - start_x;\n
\t\t\t\t\tdy = y - start_y;\n
\t\t\t\t\t\n
\t\t\t\t\tif (curConfig.gridSnapping){\n
\t\t\t\t\t\tdx = svgedit.utilities.snapToGrid(dx);\n
\t\t\t\t\t\tdy = svgedit.utilities.snapToGrid(dy);\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif (evt.shiftKey) { \n
\t\t\t\t\t\txya = svgedit.math.snapToAngle(start_x, start_y, x, y);\n
\t\t\t\t\t\tx = xya.x;\n
\t\t\t\t\t\ty = xya.y; \n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif (dx != 0 || dy != 0) {\n
\t\t\t\t\t\tlen = selectedElements.length;\n
\t\t\t\t\t\tfor (i = 0; i < len; ++i) {\n
\t\t\t\t\t\t\tselected = selectedElements[i];\n
\t\t\t\t\t\t\tif (selected == null) {break;}\n
//\t\t\t\t\t\t\tif (i==0) {\n
//\t\t\t\t\t\t\t\tvar box = svgedit.utilities.getBBox(selected);\n
//\t\t\t\t\t\t\t\t\tselectedBBoxes[i].x = box.x + dx;\n
//\t\t\t\t\t\t\t\t\tselectedBBoxes[i].y = box.y + dy;\n
//\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t// update the dummy transform in our transform list\n
\t\t\t\t\t\t\t// to be a translate\n
\t\t\t\t\t\t\tvar xform = svgroot.createSVGTransform();\n
\t\t\t\t\t\t\ttlist = svgedit.transformlist.getTransformList(selected);\n
\t\t\t\t\t\t\t// Note that if Webkit and there\'s no ID for this\n
\t\t\t\t\t\t\t// element, the dummy transform may have gotten lost.\n
\t\t\t\t\t\t\t// This results in unexpected behaviour\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\txform.setTranslate(dx, dy);\n
\t\t\t\t\t\t\tif (tlist.numberOfItems) {\n
\t\t\t\t\t\t\t\ttlist.replaceItem(xform, 0);\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\ttlist.appendItem(xform);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\t// update our internal bbox that we\'re tracking while dragging\n
\t\t\t\t\t\t\tselectorManager.requestSelector(selected).resize();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tcall("transition", selectedElements);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "multiselect":\n
\t\t\t\treal_x *= current_zoom;\n
\t\t\t\treal_y *= current_zoom;\n
\t\t\t\tsvgedit.utilities.assignAttributes(rubberBox, {\n
\t\t\t\t\t\'x\': Math.min(r_start_x, real_x),\n
\t\t\t\t\t\'y\': Math.min(r_start_y, real_y),\n
\t\t\t\t\t\'width\': Math.abs(real_x - r_start_x),\n
\t\t\t\t\t\'height\': Math.abs(real_y - r_start_y)\n
\t\t\t\t}, 100);\n
\n
\t\t\t\t// for each selected:\n
\t\t\t\t// - if newList contains selected, do nothing\n
\t\t\t\t// - if newList doesn\'t contain selected, remove it from selected\n
\t\t\t\t// - for any newList that was not in selectedElements, add it to selected\n
\t\t\t\tvar elemsToRemove = [], elemsToAdd = [],\n
\t\t\t\t\tnewList = getIntersectionList();\n
\t\t\t\tlen = selectedElements.length;\n
\t\t\t\t\n
\t\t\t\tfor (i = 0; i < len; ++i) {\n
\t\t\t\t\tvar ind = newList.indexOf(selectedElements[i]);\n
\t\t\t\t\tif (ind == -1) {\n
\t\t\t\t\t\telemsToRemove.push(selectedElements[i]);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tnewList[ind] = null;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tlen = newList.length;\n
\t\t\t\tfor (i = 0; i < len; ++i) {\n
\t\t\t\t\tif (newList[i]) {elemsToAdd.push(newList[i]);}\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif (elemsToRemove.length > 0) {\n
\t\t\t\t\tcanvas.removeFromSelection(elemsToRemove);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif (elemsToAdd.length > 0) {\n
\t\t\t\t\taddToSelection(elemsToAdd);\n
\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\tbreak;\n
\t\t\tcase "resize":\n
\t\t\t\t// we track the resize bounding box and translate/scale the selected element\n
\t\t\t\t// while the mouse is down, when mouse goes up, we use this to recalculate\n
\t\t\t\t// the shape\'s coordinates\n
\t\t\t\ttlist = svgedit.transformlist.getTransformList(selected);\n
\t\t\t\tvar hasMatrix = svgedit.math.hasMatrixTransform(tlist);\n
\t\t\t\tbox = hasMatrix ? init_bbox : svgedit.utilities.getBBox(selected);\n
\t\t\t\tvar left = box.x, top = box.y, width = box.width,\n
\t\t\t\t\theight = box.height;\n
\t\t\t\t\tdx = (x-start_x);\n
\t\t\t\t\tdy = (y-start_y);\n
\t\t\t\t\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\tdx = svgedit.utilities.snapToGrid(dx);\n
\t\t\t\t\tdy = svgedit.utilities.snapToGrid(dy);\n
\t\t\t\t\theight = svgedit.utilities.snapToGrid(height);\n
\t\t\t\t\twidth = svgedit.utilities.snapToGrid(width);\n
\t\t\t\t}\n
\n
\t\t\t\t// if rotated, adjust the dx,dy values\n
\t\t\t\tangle = svgedit.utilities.getRotationAngle(selected);\n
\t\t\t\tif (angle) {\n
\t\t\t\t\tvar r = Math.sqrt( dx*dx + dy*dy ),\n
\t\t\t\t\t\ttheta = Math.atan2(dy, dx) - angle * Math.PI / 180.0;\n
\t\t\t\t\tdx = r * Math.cos(theta);\n
\t\t\t\t\tdy = r * Math.sin(theta);\n
\t\t\t\t}\n
\n
\t\t\t\t// if not stretching in y direction, set dy to 0\n
\t\t\t\t// if not stretching in x direction, set dx to 0\n
\t\t\t\tif (current_resize_mode.indexOf("n")==-1 && current_resize_mode.indexOf("s")==-1) {\n
\t\t\t\t\tdy = 0;\n
\t\t\t\t}\n
\t\t\t\tif (current_resize_mode.indexOf("e")==-1 && current_resize_mode.indexOf("w")==-1) {\n
\t\t\t\t\tdx = 0;\n
\t\t\t\t}\t\t\t\t\n
\t\t\t\t\n
\t\t\t\tvar ts = null,\n
\t\t\t\t\ttx = 0, ty = 0,\n
\t\t\t\t\tsy = height ? (height+dy)/height : 1, \n
\t\t\t\t\tsx = width ? (width+dx)/width : 1;\n
\t\t\t\t// if we are dragging on the north side, then adjust the scale factor and ty\n
\t\t\t\tif (current_resize_mode.indexOf("n") >= 0) {\n
\t\t\t\t\tsy = height ? (height-dy)/height : 1;\n
\t\t\t\t\tty = height;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// if we dragging on the east side, then adjust the scale factor and tx\n
\t\t\t\tif (current_resize_mode.indexOf("w") >= 0) {\n
\t\t\t\t\tsx = width ? (width-dx)/width : 1;\n
\t\t\t\t\ttx = width;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// update the transform list with translate,scale,translate\n
\t\t\t\tvar translateOrigin = svgroot.createSVGTransform(),\n
\t\t\t\t\tscale = svgroot.createSVGTransform(),\n
\t\t\t\t\ttranslateBack = svgroot.createSVGTransform();\n
\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\tleft = svgedit.utilities.snapToGrid(left);\n
\t\t\t\t\ttx = svgedit.utilities.snapToGrid(tx);\n
\t\t\t\t\ttop = svgedit.utilities.snapToGrid(top);\n
\t\t\t\t\tty = svgedit.utilities.snapToGrid(ty);\n
\t\t\t\t}\n
\n
\t\t\t\ttranslateOrigin.setTranslate(-(left+tx), -(top+ty));\n
\t\t\t\tif (evt.shiftKey) {\n
\t\t\t\t\tif (sx == 1) {sx = sy;}\n
\t\t\t\t\telse {sy = sx;}\n
\t\t\t\t}\n
\t\t\t\tscale.setScale(sx, sy);\n
\t\t\t\t\n
\t\t\t\ttranslateBack.setTranslate(left+tx, top+ty);\n
\t\t\t\tif (hasMatrix) {\n
\t\t\t\t\tvar diff = angle ? 1 : 0;\n
\t\t\t\t\ttlist.replaceItem(translateOrigin, 2+diff);\n
\t\t\t\t\ttlist.replaceItem(scale, 1+diff);\n
\t\t\t\t\ttlist.replaceItem(translateBack, Number(diff));\n
\t\t\t\t} else {\n
\t\t\t\t\tvar N = tlist.numberOfItems;\n
\t\t\t\t\ttlist.replaceItem(translateBack, N-3);\n
\t\t\t\t\ttlist.replaceItem(scale, N-2);\n
\t\t\t\t\ttlist.replaceItem(translateOrigin, N-1);\n
\t\t\t\t}\n
\n
\t\t\t\tselectorManager.requestSelector(selected).resize();\n
\t\t\t\t\n
\t\t\t\tcall("transition", selectedElements);\n
\t\t\t\t\n
\t\t\t\tbreak;\n
\t\t\tcase "zoom":\n
\t\t\t\treal_x *= current_zoom;\n
\t\t\t\treal_y *= current_zoom;\n
\t\t\t\tsvgedit.utilities.assignAttributes(rubberBox, {\n
\t\t\t\t\t\'x\': Math.min(r_start_x*current_zoom, real_x),\n
\t\t\t\t\t\'y\': Math.min(r_start_y*current_zoom, real_y),\n
\t\t\t\t\t\'width\': Math.abs(real_x - r_start_x*current_zoom),\n
\t\t\t\t\t\'height\': Math.abs(real_y - r_start_y*current_zoom)\n
\t\t\t\t}, 100);\t\t\t\n
\t\t\t\tbreak;\n
\t\t\tcase "text":\n
\t\t\t\tsvgedit.utilities.assignAttributes(shape,{\n
\t\t\t\t\t\'x\': x,\n
\t\t\t\t\t\'y\': y\n
\t\t\t\t}, 1000);\n
\t\t\t\tbreak;\n
\t\t\tcase "line":\n
\t\t\t\t// Opera has a problem with suspendRedraw() apparently\n
\t\t\t\tvar handle = null;\n
\t\t\t\tif (!window.opera) {svgroot.suspendRedraw(1000);}\n
\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\tx = svgedit.utilities.snapToGrid(x);\n
\t\t\t\t\ty = svgedit.utilities.snapToGrid(y);\n
\t\t\t\t}\n
\n
\t\t\t\tvar x2 = x;\n
\t\t\t\tvar y2 = y;\t\t\t\t\t\n
\n
\t\t\t\tif (evt.shiftKey) {\n
\t\t\t\t\txya = svgedit.math.snapToAngle(start_x, start_y, x2, y2);\n
\t\t\t\t\tx2 = xya.x;\n
\t\t\t\t\ty2 = xya.y;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tshape.setAttributeNS(null, "x2", x2);\n
\t\t\t\tshape.setAttributeNS(null, "y2", y2);\n
\t\t\t\tif (!window.opera) {svgroot.unsuspendRedraw(handle);}\n
\t\t\t\tbreak;\n
\t\t\tcase "foreignObject":\n
\t\t\t\t// fall through\n
\t\t\tcase "square":\n
\t\t\t\t// fall through\n
\t\t\tcase "rect":\n
\t\t\t\t// fall through\n
\t\t\tcase "image":\n
\t\t\t\tvar square = (current_mode == \'square\') || evt.shiftKey,\n
\t\t\t\t\tw = Math.abs(x - start_x),\n
\t\t\t\t\th = Math.abs(y - start_y),\n
\t\t\t\t\tnew_x, new_y;\n
\t\t\t\tif (square) {\n
\t\t\t\t\tw = h = Math.max(w, h);\n
\t\t\t\t\tnew_x = start_x < x ? start_x : start_x - w;\n
\t\t\t\t\tnew_y = start_y < y ? start_y : start_y - h;\n
\t\t\t\t} else {\n
\t\t\t\t\tnew_x = Math.min(start_x, x);\n
\t\t\t\t\tnew_y = Math.min(start_y, y);\n
\t\t\t\t}\n
\t\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\tw = svgedit.utilities.snapToGrid(w);\n
\t\t\t\t\th = svgedit.utilities.snapToGrid(h);\n
\t\t\t\t\tnew_x = svgedit.utilities.snapToGrid(new_x);\n
\t\t\t\t\tnew_y = svgedit.utilities.snapToGrid(new_y);\n
\t\t\t\t}\n
\n
\t\t\t\tsvgedit.utilities.assignAttributes(shape,{\n
\t\t\t\t\t\'width\': w,\n
\t\t\t\t\t\'height\': h,\n
\t\t\t\t\t\'x\': new_x,\n
\t\t\t\t\t\'y\': new_y\n
\t\t\t\t},1000);\n
\t\t\t\t\n
\t\t\t\tbreak;\n
\t\t\tcase "circle":\n
\t\t\t\tc = $(shape).attr(["cx", "cy"]);\n
\t\t\t\tcx = c.cx;\n
\t\t\t\tcy = c.cy;\n
\t\t\t\tvar rad = Math.sqrt( (x-cx)*(x-cx) + (y-cy)*(y-cy) );\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\trad = svgedit.utilities.snapToGrid(rad);\n
\t\t\t\t}\n
\t\t\t\tshape.setAttributeNS(null, "r", rad);\n
\t\t\t\tbreak;\n
\t\t\tcase "ellipse":\n
\t\t\t\tc = $(shape).attr(["cx", "cy"]);\n
\t\t\t\tcx = c.cx;\n
\t\t\t\tcy = c.cy;\n
\t\t\t\t// Opera has a problem with suspendRedraw() apparently\n
\t\t\t\t\thandle = null;\n
\t\t\t\tif (!window.opera) {svgroot.suspendRedraw(1000);}\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\tx = svgedit.utilities.snapToGrid(x);\n
\t\t\t\t\tcx = svgedit.utilities.snapToGrid(cx);\n
\t\t\t\t\ty = svgedit.utilities.snapToGrid(y);\n
\t\t\t\t\tcy = svgedit.utilities.snapToGrid(cy);\n
\t\t\t\t}\n
\t\t\t\tshape.setAttributeNS(null, "rx", Math.abs(x - cx) );\n
\t\t\t\tvar ry = Math.abs(evt.shiftKey?(x - cx):(y - cy));\n
\t\t\t\tshape.setAttributeNS(null, "ry", ry );\n
\t\t\t\tif (!window.opera) {svgroot.unsuspendRedraw(handle);}\n
\t\t\t\tbreak;\n
\t\t\tcase "fhellipse":\n
\t\t\tcase "fhrect":\n
\t\t\t\tfreehand.minx = Math.min(real_x, freehand.minx);\n
\t\t\t\tfreehand.maxx = Math.max(real_x, freehand.maxx);\n
\t\t\t\tfreehand.miny = Math.min(real_y, freehand.miny);\n
\t\t\t\tfreehand.maxy = Math.max(real_y, freehand.maxy);\n
\t\t\t// break; missing on purpose\n
\t\t\tcase "fhpath":\n
//\t\t\t\td_attr += + real_x + "," + real_y + " ";\n
//\t\t\t\tshape.setAttributeNS(null, "points", d_attr);\n
\t\t\t\tend.x = real_x; end.y = real_y;\n
\t\t\t\tif (controllPoint2.x && controllPoint2.y) {\n
\t\t\t\t\tfor (i = 0; i < STEP_COUNT - 1; i++) {\n
\t\t\t\t\t\tparameter = i / STEP_COUNT;\n
\t\t\t\t\t\tnextParameter = (i + 1) / STEP_COUNT;\n
\t\t\t\t\t\tbSpline = getBsplinePoint(nextParameter);\n
\t\t\t\t\t\tnextPos = bSpline;\n
\t\t\t\t\t\tbSpline = getBsplinePoint(parameter);\n
\t\t\t\t\t\tsumDistance += Math.sqrt((nextPos.x - bSpline.x) * (nextPos.x - bSpline.x) + (nextPos.y - bSpline.y) * (nextPos.y - bSpline.y));\n
\t\t\t\t\t\tif (sumDistance > THRESHOLD_DIST) {\n
\t\t\t\t\t\t\td_attr += + bSpline.x + "," + bSpline.y + " ";\n
\t\t\t\t\t\t\tshape.setAttributeNS(null, "points", d_attr);\n
\t\t\t\t\t\t\tsumDistance -= THRESHOLD_DIST;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tcontrollPoint2 = {x:controllPoint1.x, y:controllPoint1.y};\n
\t\t\t\tcontrollPoint1 = {x:start.x, y:start.y};\n
\t\t\t\tstart = {x:end.x, y:end.y};\n
\t\t\t\tbreak;\n
\t\t\t// update path stretch line coordinates\n
\t\t\tcase "path":\n
\t\t\t\t// fall through\n
\t\t\tcase "pathedit":\n
\t\t\t\tx *= current_zoom;\n
\t\t\t\ty *= current_zoom;\n
\t\t\t\t\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\tx = svgedit.utilities.snapToGrid(x);\n
\t\t\t\t\ty = svgedit.utilities.snapToGrid(y);\n
\t\t\t\t\tstart_x = svgedit.utilities.snapToGrid(start_x);\n
\t\t\t\t\tstart_y = svgedit.utilities.snapToGrid(start_y);\n
\t\t\t\t}\n
\t\t\t\tif (evt.shiftKey) {\n
\t\t\t\t\tvar path = svgedit.path.path;\n
\t\t\t\t\tvar x1, y1;\n
\t\t\t\t\tif (path) {\n
\t\t\t\t\t\tx1 = path.dragging?path.dragging[0]:start_x;\n
\t\t\t\t\t\ty1 = path.dragging?path.dragging[1]:start_y;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tx1 = start_x;\n
\t\t\t\t\t\ty1 = start_y;\n
\t\t\t\t\t}\n
\t\t\t\t\txya = svgedit.math.snapToAngle(x1, y1, x, y);\n
\t\t\t\t\tx = xya.x;\n
\t\t\t\t\ty = xya.y;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif (rubberBox && rubberBox.getAttribute(\'display\') !== \'none\') {\n
\t\t\t\t\treal_x *= current_zoom;\n
\t\t\t\t\treal_y *= current_zoom;\n
\t\t\t\t\tsvgedit.utilities.assignAttributes(rubberBox, {\n
\t\t\t\t\t\t\'x\': Math.min(r_start_x*current_zoom, real_x),\n
\t\t\t\t\t\t\'y\': Math.min(r_start_y*current_zoom, real_y),\n
\t\t\t\t\t\t\'width\': Math.abs(real_x - r_start_x*current_zoom),\n
\t\t\t\t\t\t\'height\': Math.abs(real_y - r_start_y*current_zoom)\n
\t\t\t\t\t},100);\t\n
\t\t\t\t}\n
\t\t\t\tpathActions.mouseMove(x, y);\n
\t\t\t\t\n
\t\t\t\tbreak;\n
\t\t\tcase "textedit":\n
\t\t\t\tx *= current_zoom;\n
\t\t\t\ty *= current_zoom;\n
//\t\t\t\t\tif (rubberBox && rubberBox.getAttribute(\'display\') != \'none\') {\n
//\t\t\t\t\t\tsvgedit.utilities.assignAttributes(rubberBox, {\n
//\t\t\t\t\t\t\t\'x\': Math.min(start_x,x),\n
//\t\t\t\t\t\t\t\'y\': Math.min(start_y,y),\n
//\t\t\t\t\t\t\t\'width\': Math.abs(x-start_x),\n
//\t\t\t\t\t\t\t\'height\': Math.abs(y-start_y)\n
//\t\t\t\t\t\t},100);\n
//\t\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\ttextActions.mouseMove(mouse_x, mouse_y);\n
\t\t\t\t\n
\t\t\t\tbreak;\n
\t\t\tcase "rotate":\n
\t\t\t\tbox = svgedit.utilities.getBBox(selected);\n
\t\t\t\tcx = box.x + box.width/2;\n
\t\t\t\tcy = box.y + box.height/2;\n
\t\t\t\tvar m = svgedit.math.getMatrix(selected),\n
\t\t\t\t\tcenter = svgedit.math.transformPoint(cx, cy, m);\n
\t\t\t\tcx = center.x;\n
\t\t\t\tcy = center.y;\n
\t\t\t\tangle = ((Math.atan2(cy-y, cx-x) * (180/Math.PI))-90) % 360;\n
\t\t\t\tif (curConfig.gridSnapping) {\n
\t\t\t\t\tangle = svgedit.utilities.snapToGrid(angle);\n
\t\t\t\t}\n
\t\t\t\tif (evt.shiftKey) { // restrict rotations to nice angles (WRS)\n
\t\t\t\t\tvar snap = 45;\n
\t\t\t\t\tangle= Math.round(angle/snap)*snap;\n
\t\t\t\t}\n
\n
\t\t\t\tcanvas.setRotationAngle(angle<-180?(360+angle):angle, true);\n
\t\t\t\tcall("transition", selectedElements);\n
\t\t\t\tbreak;\n
\t\t\tdefault:\n
\t\t\t\tbreak;\n
\t\t}\n
\t\t\n
\t\trunExtensions("mouseMove", {\n
\t\t\tevent: evt,\n
\t\t\tmouse_x: mouse_x,\n
\t\t\tmouse_y: mouse_y,\n
\t\t\tselected: selected\n
\t\t});\n
\n
\t}; // mouseMove()\n
\t\n
\t// - in create mode, the element\'s opacity is set properly, we create an InsertElementCommand\n
\t// and store it on the Undo stack\n
\t// - in move/resize mode, the element\'s attributes which were affected by the move/resize are\n
\t// identified, a ChangeElementCommand is created and stored on the stack for those attrs\n
\t// this is done in when we recalculate the selected dimensions()\n
\tvar mouseUp = function(evt) {\n
\t\tif (evt.button === 2) {return;}\n
\t\tvar tempJustSelected = justSelected;\n
\t\tjustSelected = null;\n
\t\tif (!started) {return;}\n
\t\tvar pt = svgedit.math.transformPoint(evt.pageX, evt.pageY, root_sctm),\n
\t\t\tmouse_x = pt.x * current_zoom,\n
\t\t\tmouse_y = pt.y * current_zoom,\n
\t\t\tx = mouse_x / current_zoom,\n
\t\t\ty = mouse_y / current_zoom,\n
\t\t\telement = svgedit.utilities.getElem(getId()),\n
\t\t\tkeep = false;\n
\n
\t\tvar real_x = x;\n
\t\tvar real_y = y;\n
\n
\t\t// TODO: Make true when in multi-unit mode\n
\t\tvar useUnit = false; // (curConfig.baseUnit !== \'px\');\n
\t\tstarted = false;\n
\t\tvar attrs, t;\n
\t\tswitch (current_mode) {\n
\t\t\t// intentionally fall-through to select here\n
\t\t\tcase "resize":\n
\t\t\tcase "multiselect":\n
\t\t\t\tif (rubberBox != null) {\n
\t\t\t\t\trubberBox.setAttribute("display", "none");\n
\t\t\t\t\tcurBBoxes = [];\n
\t\t\t\t}\n
\t\t\t\tcurrent_mode = "select";\n
\t\t\tcase "select":\n
\t\t\t\tif (selectedElements[0] != null) {\n
\t\t\t\t\t// if we only have one selected element\n
\t\t\t\t\tif (selectedElements[1] == null) {\n
\t\t\t\t\t\t// set our current stroke/fill properties to the element\'s\n
\t\t\t\t\t\tvar selected = selectedElements[0];\n
\t\t\t\t\t\tswitch ( selected.tagName ) {\n
\t\t\t\t\t\t\tcase "g":\n
\t\t\t\t\t\t\tcase "use":\n
\t\t\t\t\t\t\tcase "image":\n
\t\t\t\t\t\t\tcase "foreignObject":\n
\t\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\tdefault:\n
\t\t\t\t\t\t\t\tcur_properties.fill = selected.getAttribute("fill");\n
\t\t\t\t\t\t\t\tcur_properties.fill_opacity = selected.getAttribute("fill-opacity");\n
\t\t\t\t\t\t\t\tcur_properties.stroke = selected.getAttribute("stroke");\n
\t\t\t\t\t\t\t\tcur_properties.stroke_opacity = selected.getAttribute("stroke-opacity");\n
\t\t\t\t\t\t\t\tcur_properties.stroke_width = selected.getAttribute("stroke-width");\n
\t\t\t\t\t\t\t\tcur_properties.stroke_dasharray = selected.getAttribute("stroke-dasharray");\n
\t\t\t\t\t\t\t\tcur_properties.stroke_linejoin = selected.getAttribute("stroke-linejoin");\n
\t\t\t\t\t\t\t\tcur_properties.stroke_linecap = selected.getAttribute("stroke-linecap");\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif (selected.tagName == "text") {\n
\t\t\t\t\t\t\tcur_text.font_size = selected.getAttribute("font-size");\n
\t\t\t\t\t\t\tcur_text.font_family = selected.getAttribute("font-family");\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tselectorManager.requestSelector(selected).showGrips(true);\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// This shouldn\'t be necessary as it was done on mouseDown...\n
//\t\t\t\t\t\t\tcall("selected", [selected]);\n
\t\t\t\t\t}\n
\t\t\t\t\t// always recalculate dimensions to strip off stray identity transforms\n
\t\t\t\t\trecalculateAllSelectedDimensions();\n
\t\t\t\t\t// if it was being dragged/resized\n
\t\t\t\t\tif (real_x != r_start_x || real_y != r_start_y) {\n
\t\t\t\t\t\tvar i, len = selectedElements.length;\n
\t\t\t\t\t\tfor (i = 0; i < len; ++i) {\n
\t\t\t\t\t\t\tif (selectedElements[i] == null) {break;}\n
\t\t\t\t\t\t\tif (!selectedElements[i].firstChild) {\n
\t\t\t\t\t\t\t\t// Not needed for groups (incorrectly resizes elems), possibly not needed at all?\n
\t\t\t\t\t\t\t\tselectorManager.requestSelector(selectedElements[i]).resize();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\t// no change in position/size, so maybe we should move to pathedit\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tt = evt.target;\n
\t\t\t\t\t\tif (selectedElements[0].nodeName === "path" && selectedElements[1] == null) {\n
\t\t\t\t\t\t\tpathActions.select(selectedElements[0]);\n
\t\t\t\t\t\t} // if it was a path\n
\t\t\t\t\t\t// else, if it was selected and this is a shift-click, remove it from selection\n
\t\t\t\t\t\telse if (evt.shiftKey) {\n
\t\t\t\t\t\t\tif (tempJustSelected != t) {\n
\t\t\t\t\t\t\t\tcanvas.removeFromSelection([t]);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t} // no change in mouse position\n
\t\t\t\t\t\n
\t\t\t\t\t// Remove non-scaling stroke\n
\t\t\t\t\tif (svgedit.browser.supportsNonScalingStroke()) {\n
\t\t\t\t\t\tvar elem = selectedElements[0];\n
\t\t\t\t\t\tif (elem) {\n
\t\t\t\t\t\t\telem.removeAttribute(\'style\');\n
\t\t\t\t\t\t\tsvgedit.utilities.walkTree(elem, function(elem) {\n
\t\t\t\t\t\t\t\telem.removeAttribute(\'style\');\n
\t\t\t\t\t\t\t});\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t}\n
\t\t\t\treturn;\n
\t\t\tcase "zoom":\n
\t\t\t\tif (rubberBox != null) {\n
\t\t\t\t\trubberBox.setAttribute("display", "none");\n
\t\t\t\t}\n
\t\t\t\tvar factor = evt.shiftKey ? 0.5 : 2;\n
\t\t\t\tcall("zoomed", {\n
\t\t\t\t\t\'x\': Math.min(r_start_x, real_x),\n
\t\t\t\t\t\'y\': Math.min(r_start_y, real_y),\n
\t\t\t\t\t\'width\': Math.abs(real_x - r_start_x),\n
\t\t\t\t\t\'height\': Math.abs(real_y - r_start_y),\n
\t\t\t\t\t\'factor\': factor\n
\t\t\t\t});\n
\t\t\t\treturn;\n
\t\t\tcase "fhpath":\n
\t\t\t\t// Check that the path contains at least 2 points; a degenerate one-point path\n
\t\t\t\t// causes problems.\n
\t\t\t\t// Webkit ignores how we set the points attribute with commas and uses space\n
\t\t\t\t// to separate all coordinates, see https://bugs.webkit.org/show_bug.cgi?id=29870\n
\t\t\t\tsumDistance = 0;\n
\t\t\t\tcontrollPoint2 = {x:0, y:0};\n
\t\t\t\tcontrollPoint1 = {x:0, y:0};\n
\t\t\t\tstart = {x:0, y:0};\n
\t\t\t\tend = {x:0, y:0};\n
\t\t\t\tvar coords = element.getAttribute(\'points\');\n
\t\t\t\tvar commaIndex = coords.indexOf(\',\');\n
\t\t\t\tif (commaIndex >= 0) {\n
\t\t\t\t\tkeep = coords.indexOf(\',\', commaIndex+1) >= 0;\n
\t\t\t\t} else {\n
\t\t\t\t\tkeep = coords.indexOf(\' \', coords.indexOf(\' \')+1) >= 0;\n
\t\t\t\t}\n
\t\t\t\tif (keep) {\n
\t\t\t\t\telement = pathActions.smoothPolylineIntoPath(element);\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "line":\n
\t\t\t\tattrs = $(element).attr(["x1", "x2", "y1", "y2"]);\n
\t\t\t\tkeep = (attrs.x1 != attrs.x2 || attrs.y1 != attrs.y2);\n
\t\t\t\tbreak;\n
\t\t\tcase "foreignObject":\n
\t\t\tcase "square":\n
\t\t\tcase "rect":\n
\t\t\tcase "image":\n
\t\t\t\tattrs = $(element).attr(["width", "height"]);\n
\t\t\t\t// Image should be kept regardless of size (use inherit dimensions later)\n
\t\t\t\tkeep = (attrs.width != 0 || attrs.height != 0) || current_mode === "image";\n
\t\t\t\tbreak;\n
\t\t\tcase "circle":\n
\t\t\t\tkeep = (element.getAttribute(\'r\') != 0);\n
\t\t\t\tbreak;\n
\t\t\tcase "ellipse":\n
\t\t\t\tattrs = $(element).attr(["rx", "ry"]);\n
\t\t\t\tkeep = (attrs.rx != null || attrs.ry != null);\n
\t\t\t\tbreak;\n
\t\t\tcase "fhellipse":\n
\t\t\t\tif ((freehand.maxx - freehand.minx) > 0 &&\n
\t\t\t\t\t(freehand.maxy - freehand.miny) > 0) {\n
\t\t\t\t\telement = addSvgElementFromJson({\n
\t\t\t\t\t\t"element": "ellipse",\n
\t\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t\t"cx": (freehand.minx + freehand.maxx) / 2,\n
\t\t\t\t\t\t\t"cy": (freehand.miny + freehand.maxy) / 2,\n
\t\t\t\t\t\t\t"rx": (freehand.maxx - freehand.minx) / 2,\n
\t\t\t\t\t\t\t"ry": (freehand.maxy - freehand.miny) / 2,\n
\t\t\t\t\t\t\t"id": getId()\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t\tcall("changed",[element]);\n
\t\t\t\t\tkeep = true;\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "fhrect":\n
\t\t\t\tif ((freehand.maxx - freehand.minx) > 0 &&\n
\t\t\t\t\t(freehand.maxy - freehand.miny) > 0) {\n
\t\t\t\t\telement = addSvgElementFromJson({\n
\t\t\t\t\t\t"element": "rect",\n
\t\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t\t"x": freehand.minx,\n
\t\t\t\t\t\t\t"y": freehand.miny,\n
\t\t\t\t\t\t\t"width": (freehand.maxx - freehand.minx),\n
\t\t\t\t\t\t\t"height": (freehand.maxy - freehand.miny),\n
\t\t\t\t\t\t\t"id": getId()\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t\tcall("changed",[element]);\n
\t\t\t\t\tkeep = true;\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "text":\n
\t\t\t\tkeep = true;\n
\t\t\t\tselectOnly([element]);\n
\t\t\t\ttextActions.start(element);\n
\t\t\t\tbreak;\n
\t\t\tcase "path":\n
\t\t\t\t// set element to null here so that it is not removed nor finalized\n
\t\t\t\telement = null;\n
\t\t\t\t// continue to be set to true so that mouseMove happens\n
\t\t\t\tstarted = true;\n
\t\t\t\t\n
\t\t\t\tvar res = pathActions.mouseUp(evt, element, mouse_x, mouse_y);\n
\t\t\t\telement = res.element;\n
\t\t\t\tkeep = res.keep;\n
\t\t\t\tbreak;\n
\t\t\tcase "pathedit":\n
\t\t\t\tkeep = true;\n
\t\t\t\telement = null;\n
\t\t\t\tpathActions.mouseUp(evt);\n
\t\t\t\tbreak;\n
\t\t\tcase "textedit":\n
\t\t\t\tkeep = false;\n
\t\t\t\telement = null;\n
\t\t\t\ttextActions.mouseUp(evt, mouse_x, mouse_y);\n
\t\t\t\tbreak;\n
\t\t\tcase "rotate":\n
\t\t\t\tkeep = true;\n
\t\t\t\telement = null;\n
\t\t\t\tcurrent_mode = "select";\n
\t\t\t\tvar batchCmd = canvas.undoMgr.finishUndoableChange();\n
\t\t\t\tif (!batchCmd.isEmpty()) { \n
\t\t\t\t\taddCommandToHistory(batchCmd);\n
\t\t\t\t}\n
\t\t\t\t// perform recalculation to weed out any stray identity transforms that might get stuck\n
\t\t\t\trecalculateAllSelectedDimensions();\n
\t\t\t\tcall("changed", selectedElements);\n
\t\t\t\tbreak;\n
\t\t\tdefault:\n
\t\t\t\t// This could occur in an extension\n
\t\t\t\tbreak;\n
\t\t}\n
\t\t\n
\t\tvar ext_result = runExtensions("mouseUp", {\n
\t\t\tevent: evt,\n
\t\t\tmouse_x: mouse_x,\n
\t\t\tmouse_y: mouse_y\n
\t\t}, true);\n
\t\t\n
\t\t$.each(ext_result, function(i, r) {\n
\t\t\tif (r) {\n
\t\t\t\tkeep = r.keep || keep;\n
\t\t\t\telement = r.element;\n
\t\t\t\tstarted = r.started || started;\n
\t\t\t}\n
\t\t});\n
\t\t\n
\t\tif (!keep && element != null) {\n
\t\t\tgetCurrentDrawing().releaseId(getId());\n
\t\t\telement.parentNode.removeChild(element);\n
\t\t\telement = null;\n
\t\t\t\n
\t\t\tt = evt.target;\n
\t\t\t\n
\t\t\t// if this element is in a group, go up until we reach the top-level group \n
\t\t\t// just below the layer groups\n
\t\t\t// TODO: once we implement links, we also would have to check for <a> elements\n
\t\t\twhile (t.parentNode.parentNode.tagName == "g") {\n
\t\t\t\tt = t.parentNode;\n
\t\t\t}\n
\t\t\t// if we are not in the middle of creating a path, and we\'ve clicked on some shape, \n
\t\t\t// then go to Select mode.\n
\t\t\t// WebKit returns <div> when the canvas is clicked, Firefox/Opera return <svg>\n
\t\t\tif ( (current_mode != "path" || !drawn_path) &&\n
\t\t\t\tt.parentNode.id != "selectorParentGroup" &&\n
\t\t\t\tt.id != "svgcanvas" && t.id != "svgroot") \n
\t\t\t{\n
\t\t\t\t// switch into "select" mode if we\'ve clicked on an element\n
\t\t\t\tcanvas.setMode("select");\n
\t\t\t\tselectOnly([t], true);\n
\t\t\t}\n
\t\t\t\n
\t\t} else if (element != null) {\n
\t\t\tcanvas.addedNew = true;\n
\t\t\t\n
\t\t\tif (useUnit) {svgedit.units.convertAttrs(element);}\n
\t\t\t\n
\t\t\tvar ani_dur = 0.2, c_ani;\n
\t\t\tif (opac_ani.beginElement && element.getAttribute(\'opacity\') != cur_shape.opacity) {\n
\t\t\t\tc_ani = $(opac_ani).clone().attr({\n
\t\t\t\t\tto: cur_shape.opacity,\n
\t\t\t\t\tdur: ani_dur\n
\t\t\t\t}).appendTo(element);\n
\t\t\t\ttry {\n
\t\t\t\t\t// Fails in FF4 on foreignObject\n
\t\t\t\t\tc_ani[0].beginElement();\n
\t\t\t\t} catch(e){}\n
\t\t\t} else {\n
\t\t\t\tani_dur = 0;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// Ideally this would be done on the endEvent of the animation,\n
\t\t\t// but that doesn\'t seem to be supported in Webkit\n
\t\t\tsetTimeout(function() {\n
\t\t\t\tif (c_ani) {c_ani.remove();}\n
\t\t\t\telement.setAttribute("opacity", cur_shape.opacity);\n
\t\t\t\telement.setAttribute("style", "pointer-events:inherit");\n
\t\t\t\tcleanupElement(element);\n
\t\t\t\tif (current_mode === "path") {\n
\t\t\t\t\tpathActions.toEditMode(element);\n
\t\t\t\t} else if (curConfig.selectNew) {\n
\t\t\t\t\tselectOnly([element], true);\n
\t\t\t\t}\n
\t\t\t\t// we create the insert command that is stored on the stack\n
\t\t\t\t// undo means to call cmd.unapply(), redo means to call cmd.apply()\n
\t\t\t\taddCommandToHistory(new svgedit.history.InsertElementCommand(element));\n
\t\t\t\t\n
\t\t\t\tcall("changed",[element]);\n
\t\t\t}, ani_dur * 1000);\n
\t\t}\n
\t\t\n
\t\tstartTransform = null;\n
\t};\n
\t\n
\tvar dblClick = function(evt) {\n
\t\tvar evt_target = evt.target;\n
\t\tvar parent = evt_target.parentNode;\n
\t\t\n
\t\t// Do nothing if already in current group\n
\t\tif (parent === current_group) {return;}\n
\t\t\n
\t\tvar mouse_target = getMouseTarget(evt);\n
\t\tvar tagName = mouse_target.tagName;\n
\t\t\n
\t\tif (tagName === \'text\' && current_mode !== \'textedit\') {\n
\t\t\tvar pt = svgedit.math.transformPoint( evt.pageX, evt.pageY, root_sctm );\n
\t\t\ttextActions.select(mouse_target, pt.x, pt.y);\n
\t\t}\n
\t\t\n
\t\tif ((tagName === "g" || tagName === "a") && svgedit.utilities.getRotationAngle(mouse_target)) {\n
\t\t\t// TODO: Allow method of in-group editing without having to do \n
\t\t\t// this (similar to editing rotated paths)\n
\t\t\n
\t\t\t// Ungroup and regroup\n
\t\t\tpushGroupProperties(mouse_target);\n
\t\t\tmouse_target = selectedElements[0];\n
\t\t\tclearSelection(true);\n
\t\t}\n
\t\t// Reset context\n
\t\tif (current_group) {\n
\t\t\tleaveContext();\n
\t\t}\n
\t\t\n
\t\tif ((parent.tagName !== \'g\' && parent.tagName !== \'a\') ||\n
\t\t\tparent === getCurrentDrawing().getCurrentLayer() ||\n
\t\t\tmouse_target === selectorManager.selectorParentGroup)\n
\t\t{\n
\t\t\t// Escape from in-group edit\n
\t\t\treturn;\n
\t\t}\n
\t\tsetContext(mouse_target);\n
\t};\n
\n
\t// prevent links from being followed in the canvas\n
\tvar handleLinkInCanvas = function(e) {\n
\t\te.preventDefault();\n
\t\treturn false;\n
\t};\n
\t\n
\t// Added mouseup to the container here.\n
\t// TODO(codedread): Figure out why after the Closure compiler, the window mouseup is ignored.\n
\t$(container).mousedown(mouseDown).mousemove(mouseMove).click(handleLinkInCanvas).dblclick(dblClick).mouseup(mouseUp);\n
//\t$(window).mouseup(mouseUp);\n
\t\n
\t //TODO(rafaelcastrocouto): User preference for shift key and zoom factor\n
\t$(container).bind("mousewheel DOMMouseScroll", function(e){\n
\t\t//if (!e.shiftKey) {return;}\n
\t\te.preventDefault();\n
\t\tvar evt = e.originalEvent;\n
\n
\t\troot_sctm = $(\'#svgcontent g\')[0].getScreenCTM().inverse();\n
\t\tvar pt = svgedit.math.transformPoint( evt.pageX, evt.pageY, root_sctm );\n
\n
\t\tvar bbox = {\n
\t\t\t\'x\': pt.x,\n
\t\t\t\'y\': pt.y,\n
\t\t\t\'width\': 0,\n
\t\t\t\'height\': 0\n
\t\t};\n
\n
\t\tvar delta = (evt.wheelDelta) ? evt.wheelDelta : (evt.detail) ? -evt.detail : 0;\n
\t\tif (!delta) {return;}\n
\n
\t\tbbox.factor = Math.max(3/4, Math.min(4/3, (delta)));\n
\t\n
\t\tcall("zoomed", bbox);\n
\t});\n
\t\n
}());\n
\n
// Function: preventClickDefault\n
// Prevents default browser click behaviour on the given element\n
//\n
// Parameters:\n
// img - The DOM element to prevent the cilck on\n
var preventClickDefault = function(img) {\n
\t$(img).click(function(e){e.preventDefault();});\n
};\n
\n
// Group: Text edit functions\n
// Functions relating to editing text elements\n
textActions = canvas.textActions = (function() {\n
\tvar curtext;\n
\tvar textinput;\n
\tvar cursor;\n
\tvar selblock;\n
\tvar blinker;\n
\tvar chardata = [];\n
\tvar textbb, transbb;\n
\tvar matrix;\n
\tvar last_x, last_y;\n
\tvar allow_dbl;\n
\t\n
\tfunction setCursor(index) {\n
\t\tvar empty = (textinput.value === "");\n
\t\t$(textinput).focus();\n
\t\n
\t\tif (!arguments.length) {\n
\t\t\tif (empty) {\n
\t\t\t\tindex = 0;\n
\t\t\t} else {\n
\t\t\t\tif (textinput.selectionEnd !== textinput.selectionStart) {return;}\n
\t\t\t\tindex = textinput.selectionEnd;\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\tvar charbb;\n
\t\tcharbb = chardata[index];\n
\t\tif (!empty) {\n
\t\t\ttextinput.setSelectionRange(index, index);\n
\t\t}\n
\t\tcursor = svgedit.utilities.getElem("text_cursor");\n
\t\tif (!cursor) {\n
\t\t\tcursor = document.createElementNS(NS.SVG, "line");\n
\t\t\tsvgedit.utilities.assignAttributes(cursor, {\n
\t\t\t\t\'id\': "text_cursor",\n
\t\t\t\t\'stroke\': "#333",\n
\t\t\t\t\'stroke-width\': 1\n
\t\t\t});\n
\t\t\tcursor = svgedit.utilities.getElem("selectorParentGroup").appendChild(cursor);\n
\t\t}\n
\t\t\n
\t\tif (!blinker) {\n
\t\t\tblinker = setInterval(function() {\n
\t\t\t\tvar show = (cursor.getAttribute(\'display\') === \'none\');\n
\t\t\t\tcursor.setAttribute(\'display\', show?\'inline\':\'none\');\n
\t\t\t}, 600);\n
\t\t}\n
\t\t\n
\t\tvar start_pt = ptToScreen(charbb.x, textbb.y);\n
\t\tvar end_pt = ptToScreen(charbb.x, (textbb.y + textbb.height));\n
\t\t\n
\t\tsvgedit.utilities.assignAttributes(cursor, {\n
\t\t\tx1: start_pt.x,\n
\t\t\ty1: start_pt.y,\n
\t\t\tx2: end_pt.x,\n
\t\t\ty2: end_pt.y,\n
\t\t\tvisibility: \'visible\',\n
\t\t\tdisplay: \'inline\'\n
\t\t});\n
\t\t\n
\t\tif (selblock) {selblock.setAttribute(\'d\', \'\');}\n
\t}\n
\t\n
\tfunction setSelection(start, end, skipInput) {\n
\t\tif (start === end) {\n
\t\t\tsetCursor(end);\n
\t\t\treturn;\n
\t\t}\n
\t\n
\t\tif (!skipInput) {\n
\t\t\ttextinput.setSelectionRange(start, end);\n
\t\t}\n
\t\t\n
\t\tselblock = svgedit.utilities.getElem("text_selectblock");\n
\t\tif (!selblock) {\n
\n
\t\t\tselblock = document.createElementNS(NS.SVG, "path");\n
\t\t\tsvgedit.utilities.assignAttributes(selblock, {\n
\t\t\t\t\'id\': "text_selectblock",\n
\t\t\t\t\'fill\': "green",\n
\t\t\t\t\'opacity\': 0.5,\n
\t\t\t\t\'style\': "pointer-events:none"\n
\t\t\t});\n
\t\t\tsvgedit.utilities.getElem("selectorParentGroup").appendChild(selblock);\n
\t\t}\n
\n
\t\tvar startbb = chardata[start];\t\t\n
\t\tvar endbb = chardata[end];\n
\t\t\n
\t\tcursor.setAttribute(\'visibility\', \'hidden\');\n
\t\t\n
\t\tvar tl = ptToScreen(startbb.x, textbb.y),\n
\t\t\ttr = ptToScreen(startbb.x + (endbb.x - startbb.x), textbb.y),\n
\t\t\tbl = ptToScreen(startbb.x, textbb.y + textbb.height),\n
\t\t\tbr = ptToScreen(startbb.x + (endbb.x - startbb.x), textbb.y + textbb.height);\n
\t\t\n
\t\tvar dstr = "M" + tl.x + "," + tl.y\n
\t\t\t\t\t+ " L" + tr.x + "," + tr.y\n
\t\t\t\t\t+ " " + br.x + "," + br.y\n
\t\t\t\t\t+ " " + bl.x + "," + bl.y + "z";\n
\t\t\n
\t\tsvgedit.utilities.assignAttributes(selblock, {\n
\t\t\td: dstr,\n
\t\t\t\'display\': \'inline\'\n
\t\t});\n
\t}\n
\t\n
\tfunction getIndexFromPoint(mouse_x, mouse_y) {\n
\t\t// Position cursor here\n
\t\tvar pt = svgroot.createSVGPoint();\n
\t\tpt.x = mouse_x;\n
\t\tpt.y = mouse_y;\n
\n
\t\t// No content, so return 0\n
\t\tif (chardata.length == 1) {return 0;}\n
\t\t// Determine if cursor should be on left or right of character\n
\t\tvar charpos = curtext.getCharNumAtPosition(pt);\n
\t\tif (charpos < 0) {\n
\t\t\t// Out of text range, look at mouse coords\n
\t\t\tcharpos = chardata.length - 2;\n
\t\t\tif (mouse_x <= chardata[0].x) {\n
\t\t\t\tcharpos = 0;\n
\t\t\t}\n
\t\t} else if (charpos >= chardata.length - 2) {\n
\t\t\tcharpos = chardata.length - 2;\n
\t\t}\n
\t\tvar charbb = chardata[charpos];\n
\t\tvar mid = charbb.x + (charbb.width/2);\n
\t\tif (mouse_x > mid) {\n
\t\t\tcharpos++;\n
\t\t}\n
\t\treturn charpos;\n
\t}\n
\t\n
\tfunction setCursorFromPoint(mouse_x, mouse_y) {\n
\t\tsetCursor(getIndexFromPoint(mouse_x, mouse_y));\n
\t}\n
\t\n
\tfunction setEndSelectionFromPoint(x, y, apply) {\n
\t\tvar i1 = textinput.selectionStart;\n
\t\tvar i2 = getIndexFromPoint(x, y);\n
\t\t\n
\t\tvar start = Math.min(i1, i2);\n
\t\tvar end = Math.max(i1, i2);\n
\t\tsetSelection(start, end, !apply);\n
\t}\n
\t\t\n
\tfunction screenToPt(x_in, y_in) {\n
\t\tvar out = {\n
\t\t\tx: x_in,\n
\t\t\ty: y_in\n
\t\t};\n
\t\t\n
\t\tout.x /= current_zoom;\n
\t\tout.y /= current_zoom;\t\t\t\n
\n
\t\tif (matrix) {\n
\t\t\tvar pt = svgedit.math.transformPoint(out.x, out.y, matrix.inverse());\n
\t\t\tout.x = pt.x;\n
\t\t\tout.y = pt.y;\n
\t\t}\n
\t\t\n
\t\treturn out;\n
\t}\t\n
\t\n
\tfunction ptToScreen(x_in, y_in) {\n
\t\tvar out = {\n
\t\t\tx: x_in,\n
\t\t\ty: y_in\n
\t\t};\n
\t\t\n
\t\tif (matrix) {\n
\t\t\tvar pt = svgedit.math.transformPoint(out.x, out.y, matrix);\n
\t\t\tout.x = pt.x;\n
\t\t\tout.y = pt.y;\n
\t\t}\n
\t\t\n
\t\tout.x *= current_zoom;\n
\t\tout.y *= current_zoom;\n
\t\t\n
\t\treturn out;\n
\t}\n
\t\n
\tfunction hideCursor() {\n
\t\tif (cursor) {\n
\t\t\tcursor.setAttribute(\'visibility\', \'hidden\');\n
\t\t}\n
\t}\n
\t\n
\tfunction selectAll(evt) {\n
\t\tsetSelection(0, curtext.textContent.length);\n
\t\t$(this).unbind(evt);\n
\t}\n
\n
\tfunction selectWord(evt) {\n
\t\tif (!allow_dbl || !curtext) {return;}\n
\t\n
\t\tvar ept = svgedit.math.transformPoint( evt.pageX, evt.pageY, root_sctm ),\n
\t\t\tmouse_x = ept.x * current_zoom,\n
\t\t\tmouse_y = ept.y * current_zoom;\n
\t\tvar pt = screenToPt(mouse_x, mouse_y);\n
\t\t\n
\t\tvar index = getIndexFromPoint(pt.x, pt.y);\n
\t\tvar str = curtext.textContent;\n
\t\tvar first = str.substr(0, index).replace(/[a-z0-9]+$/i, \'\').length;\n
\t\tvar m = str.substr(index).match(/^[a-z0-9]+/i);\n
\t\tvar last = (m?m[0].length:0) + index;\n
\t\tsetSelection(first, last);\n
\t\t\n
\t\t// Set tripleclick\n
\t\t$(evt.target).click(selectAll);\n
\t\tsetTimeout(function() {\n
\t\t\t$(evt.target).unbind(\'click\', selectAll);\n
\t\t}, 300);\n
\t\t\n
\t}\n
\n
\treturn {\n
\t\tselect: function(target, x, y) {\n
\t\t\tcurtext = target;\n
\t\t\ttextActions.toEditMode(x, y);\n
\t\t},\n
\t\tstart: function(elem) {\n
\t\t\tcurtext = elem;\n
\t\t\ttextActions.toEditMode();\n
\t\t},\n
\t\tmouseDown: function(evt, mouse_target, start_x, start_y) {\n
\t\t\tvar pt = screenToPt(start_x, start_y);\n
\t\t\n
\t\t\ttextinput.focus();\n
\t\t\tsetCursorFromPoint(pt.x, pt.y);\n
\t\t\tlast_x = start_x;\n
\t\t\tlast_y = start_y;\n
\t\t\t\n
\t\t\t// TODO: Find way to block native selection\n
\t\t},\n
\t\tmouseMove: function(mouse_x, mouse_y) {\n
\t\t\tvar pt = screenToPt(mouse_x, mouse_y);\n
\t\t\tsetEndSelectionFromPoint(pt.x, pt.y);\n
\t\t},\t\t\t\n
\t\tmouseUp: function(evt, mouse_x, mouse_y) {\n
\t\t\tvar pt = screenToPt(mouse_x, mouse_y);\n
\t\t\t\n
\t\t\tsetEndSelectionFromPoint(pt.x, pt.y, true);\n
\t\t\t\n
\t\t\t// TODO: Find a way to make this work: Use transformed BBox instead of evt.target \n
//\t\t\t\tif (last_x === mouse_x && last_y === mouse_y\n
//\t\t\t\t\t&& !svgedit.math.rectsIntersect(transbb, {x: pt.x, y: pt.y, width:0, height:0})) {\n
//\t\t\t\t\ttextActions.toSelectMode(true);\t\t\t\t\n
//\t\t\t\t}\n
\n
\t\t\tif (\n
\t\t\t\tevt.target !== curtext\n
\t\t\t\t&&\tmouse_x < last_x + 2\n
\t\t\t\t&& mouse_x > last_x - 2\n
\t\t\t\t&&\tmouse_y < last_y + 2\n
\t\t\t\t&& mouse_y > last_y - 2) {\n
\n
\t\t\t\ttextActions.toSelectMode(true);\n
\t\t\t}\n
\n
\t\t},\n
\t\tsetCursor: setCursor,\n
\t\ttoEditMode: function(x, y) {\n
\t\t\tallow_dbl = false;\n
\t\t\tcurrent_mode = "textedit";\n
\t\t\tselectorManager.requestSelector(curtext).showGrips(false);\n
\t\t\t// Make selector group accept clicks\n
\t\t\tvar sel = selectorManager.requestSelector(curtext).selectorRect;\n
\t\t\t\n
\t\t\ttextActions.init();\n
\n
\t\t\t$(curtext).css(\'cursor\', \'text\');\n
\t\t\t\n
//\t\t\t\tif (svgedit.browser.supportsEditableText()) {\n
//\t\t\t\t\tcurtext.setAttribute(\'editable\', \'simple\');\n
//\t\t\t\t\treturn;\n
//\t\t\t\t}\n
\t\t\t\n
\t\t\tif (!arguments.length) {\n
\t\t\t\tsetCursor();\n
\t\t\t} else {\n
\t\t\t\tvar pt = screenToPt(x, y);\n
\t\t\t\tsetCursorFromPoint(pt.x, pt.y);\n
\t\t\t}\n
\t\t\t\n
\t\t\tsetTimeout(function() {\n
\t\t\t\tallow_dbl = true;\n
\t\t\t}, 300);\n
\t\t},\n
\t\ttoSelectMode: function(selectElem) {\n
\t\t\tcurrent_mode = "select";\n
\t\t\tclearInterval(blinker);\n
\t\t\tblinker = null;\n
\t\t\tif (selblock) {$(selblock).attr(\'display\', \'none\');}\n
\t\t\tif (cursor) {$(cursor).attr(\'visibility\', \'hidden\');}\n
\t\t\t$(curtext).css(\'cursor\', \'move\');\n
\t\t\t\n
\t\t\tif (selectElem) {\n
\t\t\t\tclearSelection();\n
\t\t\t\t$(curtext).css(\'cursor\', \'move\');\n
\t\t\t\t\n
\t\t\t\tcall("selected", [curtext]);\n
\t\t\t\taddToSelection([curtext], true);\n
\t\t\t}\n
\t\t\tif (curtext && !curtext.textContent.length) {\n
\t\t\t\t// No content, so delete\n
\t\t\t\tcanvas.deleteSelectedElements();\n
\t\t\t}\n
\t\t\t\n
\t\t\t$(textinput).blur();\n
\t\t\t\n
\t\t\tcurtext = false;\n
\t\t\t\n
//\t\t\t\tif (svgedit.browser.supportsEditableText()) {\n
//\t\t\t\t\tcurtext.removeAttribute(\'editable\');\n
//\t\t\t\t}\n
\t\t},\n
\t\tsetInputElem: function(elem) {\n
\t\t\ttextinput = elem;\n
//\t\t\t$(textinput).blur(hideCursor);\n
\t\t},\n
\t\tclear: function() {\n
\t\t\tif (current_mode == "textedit") {\n
\t\t\t\ttextActions.toSelectMode();\n
\t\t\t}\n
\t\t},\n
\t\tinit: function(inputElem) {\n
\t\t\tif (!curtext) {return;}\n
\t\t\tvar i, end;\n
//\t\t\t\tif (svgedit.browser.supportsEditableText()) {\n
//\t\t\t\t\tcurtext.select();\n
//\t\t\t\t\treturn;\n
//\t\t\t\t}\n
\t\t\n
\t\t\tif (!curtext.parentNode) {\n
\t\t\t\t// Result of the ffClone, need to get correct element\n
\t\t\t\tcurtext = selectedElements[0];\n
\t\t\t\tselectorManager.requestSelector(curtext).showGrips(false);\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar str = curtext.textContent;\n
\t\t\tvar len = str.length;\n
\t\t\t\n
\t\t\tvar xform = curtext.getAttribute(\'transform\');\n
\n
\t\t\ttextbb = svgedit.utilities.getBBox(curtext);\n
\t\t\t\n
\t\t\tmatrix = xform ? svgedit.math.getMatrix(curtext) : null;\n
\n
\t\t\tchardata = new Array(len);\n
\t\t\ttextinput.focus();\n
\t\t\t\n
\t\t\t$(curtext).unbind(\'dblclick\', selectWord).dblclick(selectWord);\n
\t\t\t\n
\t\t\tif (!len) {\n
\t\t\t\tend = {x: textbb.x + (textbb.width/2), width: 0};\n
\t\t\t}\n
\t\t\t\n
\t\t\tfor (i=0; i<len; i++) {\n
\t\t\t\tvar start = curtext.getStartPositionOfChar(i);\n
\t\t\t\tend = curtext.getEndPositionOfChar(i);\n
\t\t\t\t\n
\t\t\t\tif (!svgedit.browser.supportsGoodTextCharPos()) {\n
\t\t\t\t\tvar offset = canvas.contentW * current_zoom;\n
\t\t\t\t\tstart.x -= offset;\n
\t\t\t\t\tend.x -= offset;\n
\t\t\t\t\t\n
\t\t\t\t\tstart.x /= current_zoom;\n
\t\t\t\t\tend.x /= current_zoom;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// Get a "bbox" equivalent for each character. Uses the\n
\t\t\t\t// bbox data of the actual text for y, height purposes\n
\t\t\t\t\n
\t\t\t\t// TODO: Decide if y, width and height are actually necessary\n
\t\t\t\tchardata[i] = {\n
\t\t\t\t\tx: start.x,\n
\t\t\t\t\ty: textbb.y, // start.y?\n
\t\t\t\t\twidth: end.x - start.x,\n
\t\t\t\t\theight: textbb.height\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\t\n
\t\t\t// Add a last bbox for cursor at end of text\n
\t\t\tchardata.push({\n
\t\t\t\tx: end.x,\n
\t\t\t\twidth: 0\n
\t\t\t});\n
\t\t\tsetSelection(textinput.selectionStart, textinput.selectionEnd, true);\n
\t\t}\n
\t};\n
}());\n
\n
// TODO: Migrate all of this code into path.js\n
// Group: Path edit functions\n
// Functions relating to editing path elements\n
pathActions = canvas.pathActions = function() {\n
\t\n
\tvar subpath = false;\n
\tvar current_path;\n
\tvar newPoint, firstCtrl;\n
\t\n
\tfunction resetD(p) {\n
\t\tp.setAttribute("d", pathActions.convertPath(p));\n
\t}\n
\n
\t// TODO: Move into path.js\n
\tsvgedit.path.Path.prototype.endChanges = function(text) {\n
\t\tif (svgedit.browser.isWebkit()) {resetD(this.elem);}\n
\t\tvar cmd = new svgedit.history.ChangeElementCommand(this.elem, {d: this.last_d}, text);\n
\t\taddCommandToHistory(cmd);\n
\t\tcall("changed", [this.elem]);\n
\t};\n
\n
\tsvgedit.path.Path.prototype.addPtsToSelection = function(indexes) {\n
\t\tvar i, seg;\n
\t\tif (!$.isArray(indexes)) {indexes = [indexes];}\n
\t\tfor (i = 0; i< indexes.length; i++) {\n
\t\t\tvar index = indexes[i];\n
\t\t\tseg = this.segs[index];\n
\t\t\tif (seg.ptgrip) {\n
\t\t\t\tif (this.selected_pts.indexOf(index) == -1 && index >= 0) {\n
\t\t\t\t\tthis.selected_pts.push(index);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t\tthis.selected_pts.sort();\n
\t\ti = this.selected_pts.length;\n
\t\tvar grips = new Array(i);\n
\t\t// Loop through points to be selected and highlight each\n
\t\twhile (i--) {\n
\t\t\tvar pt = this.selected_pts[i];\n
\t\t\tseg = this.segs[pt];\n
\t\t\tseg.select(true);\n
\t\t\tgrips[i] = seg.ptgrip;\n
\t\t}\n
\t\t// TODO: Correct this:\n
\t\tpathActions.canDeleteNodes = true;\n
\t\t\n
\t\tpathActions.closed_subpath = this.subpathIsClosed(this.selected_pts[0]);\n
\t\t\n
\t\tcall("selected", grips);\n
\t};\n
\n
\tcurrent_path = null;\n
\tvar drawn_path = null,\n
\t\thasMoved = false;\n
\t\n
\t// This function converts a polyline (created by the fh_path tool) into\n
\t// a path element and coverts every three line segments into a single bezier\n
\t// curve in an attempt to smooth out the free-hand\n
\tvar smoothPolylineIntoPath = function(element) {\n
\t\tvar i, points = element.points;\n
\t\tvar N = points.numberOfItems;\n
\t\tif (N >= 4) {\n
\t\t\t// loop through every 3 points and convert to a cubic bezier curve segment\n
\t\t\t// \n
\t\t\t// NOTE: this is cheating, it means that every 3 points has the potential to \n
\t\t\t// be a corner instead of treating each point in an equal manner. In general,\n
\t\t\t// this technique does not look that good.\n
\t\t\t// \n
\t\t\t// I am open to better ideas!\n
\t\t\t// \n
\t\t\t// Reading:\n
\t\t\t// - http://www.efg2.com/Lab/Graphics/Jean-YvesQueinecBezierCurves.htm\n
\t\t\t// - http://www.codeproject.com/KB/graphics/BezierSpline.aspx?msg=2956963\n
\t\t\t// - http://www.ian-ko.com/ET_GeoWizards/UserGuide/smooth.htm\n
\t\t\t// - http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/Bezier/bezier-der.html\n
\t\t\tvar curpos = points.getItem(0), prevCtlPt = null;\n
\t\t\tvar d = [];\n
\t\t\td.push(["M", curpos.x, ",", curpos.y, " C"].join(""));\n
\t\t\tfor (i = 1; i <= (N-4); i += 3) {\n
\t\t\t\tvar ct1 = points.getItem(i);\n
\t\t\t\tvar ct2 = points.getItem(i+1);\n
\t\t\t\tvar end = points.getItem(i+2);\n
\t\t\t\t\n
\t\t\t\t// if the previous segment had a control point, we want to smooth out\n
\t\t\t\t// the control points on both sides\n
\t\t\t\tif (prevCtlPt) {\n
\t\t\t\t\tvar newpts = svgedit.path.smoothControlPoints( prevCtlPt, ct1, curpos );\n
\t\t\t\t\tif (newpts && newpts.length == 2) {\n
\t\t\t\t\t\tvar prevArr = d[d.length-1].split(\',\');\n
\t\t\t\t\t\tprevArr[2] = newpts[0].x;\n
\t\t\t\t\t\tprevArr[3] = newpts[0].y;\n
\t\t\t\t\t\td[d.length-1] = prevArr.join(\',\');\n
\t\t\t\t\t\tct1 = newpts[1];\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\td.push([ct1.x, ct1.y, ct2.x, ct2.y, end.x, end.y].join(\',\'));\n
\t\t\t\t\n
\t\t\t\tcurpos = end;\n
\t\t\t\tprevCtlPt = ct2;\n
\t\t\t}\n
\t\t\t// handle remaining line segments\n
\t\t\td.push("L");\n
\t\t\twhile (i < N) {\n
\t\t\t\tvar pt = points.getItem(i);\n
\t\t\t\td.push([pt.x, pt.y].join(","));\n
\t\t\t\ti++;\n
\t\t\t}\n
\t\t\td = d.join(" ");\n
\n
\t\t\t// create new path element\n
\t\t\telement = addSvgElementFromJson({\n
\t\t\t\t"element": "path",\n
\t\t\t\t"curStyles": true,\n
\t\t\t\t"attr": {\n
\t\t\t\t\t"id": getId(),\n
\t\t\t\t\t"d": d,\n
\t\t\t\t\t"fill": "none"\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\t// No need to call "changed", as this is already done under mouseUp\n
\t\t}\n
\t\treturn element;\n
\t};\n
\n
\treturn {\n
\t\tmouseDown: function(evt, mouse_target, start_x, start_y) {\n
\t\t\tvar id;\n
\t\t\tif (current_mode === "path") {\n
\t\t\t\tmouse_x = start_x;\n
\t\t\t\tmouse_y = start_y;\n
\t\t\t\t\n
\t\t\t\tvar x = mouse_x/current_zoom,\n
\t\t\t\t\ty = mouse_y/current_zoom,\n
\t\t\t\t\tstretchy = svgedit.utilities.getElem("path_stretch_line");\n
\t\t\t\tnewPoint = [x, y];\t\n
\t\t\t\t\n
\t\t\t\tif (curConfig.gridSnapping){\n
\t\t\t\t\tx = svgedit.utilities.snapToGrid(x);\n
\t\t\t\t\ty = svgedit.utilities.snapToGrid(y);\n
\t\t\t\t\tmouse_x = svgedit.utilities.snapToGrid(mouse_x);\n
\t\t\t\t\tmouse_y = svgedit.utilities.snapToGrid(mouse_y);\n
\t\t\t\t}\n
\n
\t\t\t\tif (!stretchy) {\n
\t\t\t\t\tstretchy = document.createElementNS(NS.SVG, "path");\n
\t\t\t\t\tsvgedit.utilities.assignAttributes(stretchy, {\n
\t\t\t\t\t\t\'id\': "path_stretch_line",\n
\t\t\t\t\t\t\'stroke\': "#22C",\n
\t\t\t\t\t\t\'stroke-width\': "0.5",\n
\t\t\t\t\t\t\'fill\': \'none\'\n
\t\t\t\t\t});\n
\t\t\t\t\tstretchy = svgedit.utilities.getElem("selectorParentGroup").appendChild(stretchy);\n
\t\t\t\t}\n
\t\t\t\tstretchy.setAttribute("display", "inline");\n
\t\t\t\t\n
\t\t\t\tvar keep = null;\n
\t\t\t\tvar index;\n
\t\t\t\t// if pts array is empty, create path element with M at current point\n
\t\t\t\tif (!drawn_path) {\n
\t\t\t\t\td_attr = "M" + x + "," + y + " ";\n
\t\t\t\t\tdrawn_path = addSvgElementFromJson({\n
\t\t\t\t\t\t"element": "path",\n
\t\t\t\t\t\t"curStyles": true,\n
\t\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t\t"d": d_attr,\n
\t\t\t\t\t\t\t"id": getNextId(),\n
\t\t\t\t\t\t\t"opacity": cur_shape.opacity / 2\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t\t// set stretchy line to first point\n
\t\t\t\t\tstretchy.setAttribute(\'d\', [\'M\', mouse_x, mouse_y, mouse_x, mouse_y].join(\' \'));\n
\t\t\t\t\tindex = subpath ? svgedit.path.path.segs.length : 0;\n
\t\t\t\t\tsvgedit.path.addPointGrip(index, mouse_x, mouse_y);\n
\t\t\t\t} else {\n
\t\t\t\t\t// determine if we clicked on an existing point\n
\t\t\t\t\tvar seglist = drawn_path.pathSegList;\n
\t\t\t\t\tvar i = seglist.numberOfItems;\n
\t\t\t\t\tvar FUZZ = 6/current_zoom;\n
\t\t\t\t\tvar clickOnPoint = false;\n
\t\t\t\t\twhile (i) {\n
\t\t\t\t\t\ti --;\n
\t\t\t\t\t\tvar item = seglist.getItem(i);\n
\t\t\t\t\t\tvar px = item.x, py = item.y;\n
\t\t\t\t\t\t// found a matching point\n
\t\t\t\t\t\tif ( x >= (px-FUZZ) && x <= (px+FUZZ) && y >= (py-FUZZ) && y <= (py+FUZZ) ) {\n
\t\t\t\t\t\t\tclickOnPoint = true;\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\t// get path element that we are in the process of creating\n
\t\t\t\t\tid = getId();\n
\t\t\t\t\n
\t\t\t\t\t// Remove previous path object if previously created\n
\t\t\t\t\tsvgedit.path.removePath_(id);\n
\t\t\t\t\t\n
\t\t\t\t\tvar newpath = svgedit.utilities.getElem(id);\n
\t\t\t\t\tvar newseg;\n
\t\t\t\t\tvar s_seg;\n
\t\t\t\t\tvar len = seglist.numberOfItems;\n
\t\t\t\t\t// if we clicked on an existing point, then we are done this path, commit it\n
\t\t\t\t\t// (i, i+1) are the x,y that were clicked on\n
\t\t\t\t\tif (clickOnPoint) {\n
\t\t\t\t\t\t// if clicked on any other point but the first OR\n
\t\t\t\t\t\t// the first point was clicked on and there are less than 3 points\n
\t\t\t\t\t\t// then leave the path open\n
\t\t\t\t\t\t// otherwise, close the path\n
\t\t\t\t\t\tif (i <= 1 && len >= 2) {\n
\t\t\t\t\t\t\t// Create end segment\n
\t\t\t\t\t\t\tvar abs_x = seglist.getItem(0).x;\n
\t\t\t\t\t\t\tvar abs_y = seglist.getItem(0).y;\n
\t\t\t\t\t\t\t\n
\n
\t\t\t\t\t\t\ts_seg = stretchy.pathSegList.getItem(1);\n
\t\t\t\t\t\t\tif (s_seg.pathSegType === 4) {\n
\t\t\t\t\t\t\t\tnewseg = drawn_path.createSVGPathSegLinetoAbs(abs_x, abs_y);\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tnewseg = drawn_path.createSVGPathSegCurvetoCubicAbs(\n
\t\t\t\t\t\t\t\t\tabs_x,\n
\t\t\t\t\t\t\t\t\tabs_y,\n
\t\t\t\t\t\t\t\t\ts_seg.x1 / current_zoom,\n
\t\t\t\t\t\t\t\t\ts_seg.y1 / current_zoom,\n
\t\t\t\t\t\t\t\t\tabs_x,\n
\t\t\t\t\t\t\t\t\tabs_y\n
\t\t\t\t\t\t\t\t);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\tvar endseg = drawn_path.createSVGPathSegClosePath();\n
\t\t\t\t\t\t\tseglist.appendItem(newseg);\n
\t\t\t\t\t\t\tseglist.appendItem(endseg);\n
\t\t\t\t\t\t} else if (len < 3) {\n
\t\t\t\t\t\t\tkeep = false;\n
\t\t\t\t\t\t\treturn keep;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t$(stretchy).remove();\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// This will signal to commit the path\n
\t\t\t\t\t\telement = newpath;\n
\t\t\t\t\t\tdrawn_path = null;\n
\t\t\t\t\t\tstarted = false;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tif (subpath) {\n
\t\t\t\t\t\t\tif (svgedit.path.path.matrix) {\n
\t\t\t\t\t\t\t\tsvgedit.coords.remapElement(newpath, {}, svgedit.path.path.matrix.inverse());\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t\tvar new_d = newpath.getAttribute("d");\n
\t\t\t\t\t\t\tvar orig_d = $(svgedit.path.path.elem).attr("d");\n
\t\t\t\t\t\t\t$(svgedit.path.path.elem).attr("d", orig_d + new_d);\n
\t\t\t\t\t\t\t$(newpath).remove();\n
\t\t\t\t\t\t\tif (svgedit.path.path.matrix) {\n
\t\t\t\t\t\t\t\tsvgedit.path.recalcRotatedPath();\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tsvgedit.path.path.init();\n
\t\t\t\t\t\t\tpathActions.toEditMode(svgedit.path.path.elem);\n
\t\t\t\t\t\t\tsvgedit.path.path.selectPt();\n
\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\t// else, create a new point, update path element\n
\t\t\t\t\telse {\n
\t\t\t\t\t\t// Checks if current target or parents are #svgcontent\n
\t\t\t\t\t\tif (!$.contains(container, getMouseTarget(evt))) {\n
\t\t\t\t\t\t\t// Clicked outside canvas, so don\'t make point\n
\t\t\t\t\t\t\tconsole.log("Clicked outside canvas");\n
\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tvar num = drawn_path.pathSegList.numberOfItems;\n
\t\t\t\t\t\tvar last = drawn_path.pathSegList.getItem(num -1);\n
\t\t\t\t\t\tvar lastx = last.x, lasty = last.y;\n
\n
\t\t\t\t\t\tif (evt.shiftKey) {\n
\t\t\t\t\t\t\tvar xya = svgedit.math.snapToAngle(lastx, lasty, x, y);\n
\t\t\t\t\t\t\tx = xya.x;\n
\t\t\t\t\t\t\ty = xya.y;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// Use the segment defined by stretchy\n
\t\t\t\t\t\ts_seg = stretchy.pathSegList.getItem(1);\n
\t\t\t\t\t\tif (s_seg.pathSegType === 4) {\n
\t\t\t\t\t\t\tnewseg = drawn_path.createSVGPathSegLinetoAbs(round(x), round(y));\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tnewseg = drawn_path.createSVGPathSegCurvetoCubicAbs(\n
\t\t\t\t\t\t\t\tround(x),\n
\t\t\t\t\t\t\t\tround(y),\n
\t\t\t\t\t\t\t\ts_seg.x1 / current_zoom,\n
\t\t\t\t\t\t\t\ts_seg.y1 / current_zoom,\n
\t\t\t\t\t\t\t\ts_seg.x2 / current_zoom,\n
\t\t\t\t\t\t\t\ts_seg.y2 / current_zoom\n
\t\t\t\t\t\t\t);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tdrawn_path.pathSegList.appendItem(newseg);\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tx *= current_zoom;\n
\t\t\t\t\t\ty *= current_zoom;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t// set stretchy line to latest point\n
\t\t\t\t\t\tstretchy.setAttribute(\'d\', [\'M\', x, y, x, y].join(\' \'));\n
\t\t\t\t\t\tindex = num;\n
\t\t\t\t\t\tif (subpath) {index += svgedit.path.path.segs.length;}\n
\t\t\t\t\t\tsvgedit.path.addPointGrip(index, x, y);\n
\t\t\t\t\t}\n
//\t\t\t\t\tkeep = true;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// TODO: Make sure current_path isn\'t null at this point\n
\t\t\tif (!svgedit.path.path) {return;}\n
\t\t\t\n
\t\t\tsvgedit.path.path.storeD();\n
\t\t\t\n
\t\t\tid = evt.target.id;\n
\t\t\tvar cur_pt;\n
\t\t\tif (id.substr(0,14) == "pathpointgrip_") {\n
\t\t\t\t// Select this point\n
\t\t\t\tcur_pt = svgedit.path.path.cur_p

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAM=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="3" aka="AAAAAAAAAAM=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string>t = parseInt(id.substr(14));\n
\t\t\t\tsvgedit.path.path.dragging = [start_x, start_y];\n
\t\t\t\tvar seg = svgedit.path.path.segs[cur_pt];\n
\t\t\t\t\n
\t\t\t\t// only clear selection if shift is not pressed (otherwise, add \n
\t\t\t\t// node to selection)\n
\t\t\t\tif (!evt.shiftKey) {\n
\t\t\t\t\tif (svgedit.path.path.selected_pts.length \074= 1 || !seg.selected) {\n
\t\t\t\t\t\tsvgedit.path.path.clearSelection();\n
\t\t\t\t\t}\n
\t\t\t\t\tsvgedit.path.path.addPtsToSelection(cur_pt);\n
\t\t\t\t} else if (seg.selected) {\n
\t\t\t\t\tsvgedit.path.path.removePtFromSelection(cur_pt);\n
\t\t\t\t} else {\n
\t\t\t\t\tsvgedit.path.path.addPtsToSelection(cur_pt);\n
\t\t\t\t}\n
\t\t\t} else if (id.indexOf("ctrlpointgrip_") == 0) {\n
\t\t\t\tsvgedit.path.path.dragging = [start_x, start_y];\n
\t\t\t\t\n
\t\t\t\tvar parts = id.split(\'_\')[1].split(\'c\');\n
\t\t\t\tcur_pt = Number(parts[0]);\n
\t\t\t\tvar ctrl_num = Number(parts[1]);\n
\t\t\t\tsvgedit.path.path.selectPt(cur_pt, ctrl_num);\n
\t\t\t}\n
\n
\t\t\t// Start selection box\n
\t\t\tif (!svgedit.path.path.dragging) {\n
\t\t\t\tif (rubberBox == null) {\n
\t\t\t\t\trubberBox = selectorManager.getRubberBandBox();\n
\t\t\t\t}\n
\t\t\t\tsvgedit.utilities.assignAttributes(rubberBox, {\n
\t\t\t\t\t\t\'x\': start_x * current_zoom,\n
\t\t\t\t\t\t\'y\': start_y * current_zoom,\n
\t\t\t\t\t\t\'width\': 0,\n
\t\t\t\t\t\t\'height\': 0,\n
\t\t\t\t\t\t\'display\': \'inline\'\n
\t\t\t\t}, 100);\n
\t\t\t}\n
\t\t},\n
\t\tmouseMove: function(mouse_x, mouse_y) {\n
\t\t\thasMoved = true;\n
\t\t\tif (current_mode === "path") {\n
\t\t\t\tif (!drawn_path) {return;}\n
\t\t\t\tvar seglist = drawn_path.pathSegList;\n
\t\t\t\tvar index = seglist.numberOfItems - 1;\n
\n
\t\t\t\tif (newPoint) {\n
\t\t\t\t\t// First point\n
//\t\t\t\t\tif (!index) {return;}\n
\n
\t\t\t\t\t// Set control points\n
\t\t\t\t\tvar pointGrip1 = svgedit.path.addCtrlGrip(\'1c1\');\n
\t\t\t\t\tvar pointGrip2 = svgedit.path.addCtrlGrip(\'0c2\');\n
\t\t\t\t\t\n
\t\t\t\t\t// dragging pointGrip1\n
\t\t\t\t\tpointGrip1.setAttribute(\'cx\', mouse_x);\n
\t\t\t\t\tpointGrip1.setAttribute(\'cy\', mouse_y);\n
\t\t\t\t\tpointGrip1.setAttribute(\'display\', \'inline\');\n
\n
\t\t\t\t\tvar pt_x = newPoint[0];\n
\t\t\t\t\tvar pt_y = newPoint[1];\n
\t\t\t\t\t\n
\t\t\t\t\t// set curve\n
\t\t\t\t\tvar seg = seglist.getItem(index);\n
\t\t\t\t\tvar cur_x = mouse_x / current_zoom;\n
\t\t\t\t\tvar cur_y = mouse_y / current_zoom;\n
\t\t\t\t\tvar alt_x = (pt_x + (pt_x - cur_x));\n
\t\t\t\t\tvar alt_y = (pt_y + (pt_y - cur_y));\n
\t\t\t\t\t\n
\t\t\t\t\tpointGrip2.setAttribute(\'cx\', alt_x * current_zoom);\n
\t\t\t\t\tpointGrip2.setAttribute(\'cy\', alt_y * current_zoom);\n
\t\t\t\t\tpointGrip2.setAttribute(\'display\', \'inline\');\n
\t\t\t\t\t\n
\t\t\t\t\tvar ctrlLine = svgedit.path.getCtrlLine(1);\n
\t\t\t\t\tsvgedit.utilities.assignAttributes(ctrlLine, {\n
\t\t\t\t\t\tx1: mouse_x,\n
\t\t\t\t\t\ty1: mouse_y,\n
\t\t\t\t\t\tx2: alt_x * current_zoom,\n
\t\t\t\t\t\ty2: alt_y * current_zoom,\n
\t\t\t\t\t\tdisplay: \'inline\'\n
\t\t\t\t\t});\n
\n
\t\t\t\t\tif (index === 0) {\n
\t\t\t\t\t\tfirstCtrl = [mouse_x, mouse_y];\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tvar last = seglist.getItem(index - 1);\n
\t\t\t\t\t\tvar last_x = last.x;\n
\t\t\t\t\t\tvar last_y = last.y;\n
\t\n
\t\t\t\t\t\tif (last.pathSegType === 6) {\n
\t\t\t\t\t\t\tlast_x += (last_x - last.x2);\n
\t\t\t\t\t\t\tlast_y += (last_y - last.y2);\n
\t\t\t\t\t\t} else if (firstCtrl) {\n
\t\t\t\t\t\t\tlast_x = firstCtrl[0]/current_zoom;\n
\t\t\t\t\t\t\tlast_y = firstCtrl[1]/current_zoom;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tsvgedit.path.replacePathSeg(6, index, [pt_x, pt_y, last_x, last_y, alt_x, alt_y], drawn_path);\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tvar stretchy = svgedit.utilities.getElem("path_stretch_line");\n
\t\t\t\t\tif (stretchy) {\n
\t\t\t\t\t\tvar prev = seglist.getItem(index);\n
\t\t\t\t\t\tif (prev.pathSegType === 6) {\n
\t\t\t\t\t\t\tvar prev_x = prev.x + (prev.x - prev.x2);\n
\t\t\t\t\t\t\tvar prev_y = prev.y + (prev.y - prev.y2);\n
\t\t\t\t\t\t\tsvgedit.path.replacePathSeg(6, 1, [mouse_x, mouse_y, prev_x * current_zoom, prev_y * current_zoom, mouse_x, mouse_y], stretchy);\t\t\t\t\t\t\t\n
\t\t\t\t\t\t} else if (firstCtrl) {\n
\t\t\t\t\t\t\tsvgedit.path.replacePathSeg(6, 1, [mouse_x, mouse_y, firstCtrl[0], firstCtrl[1], mouse_x, mouse_y], stretchy);\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tsvgedit.path.replacePathSeg(4, 1, [mouse_x, mouse_y], stretchy);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\t// if we are dragging a point, let\'s move it\n
\t\t\tif (svgedit.path.path.dragging) {\n
\t\t\t\tvar pt = svgedit.path.getPointFromGrip({\n
\t\t\t\t\tx: svgedit.path.path.dragging[0],\n
\t\t\t\t\ty: svgedit.path.path.dragging[1]\n
\t\t\t\t}, svgedit.path.path);\n
\t\t\t\tvar mpt = svgedit.path.getPointFromGrip({\n
\t\t\t\t\tx: mouse_x,\n
\t\t\t\t\ty: mouse_y\n
\t\t\t\t}, svgedit.path.path);\n
\t\t\t\tvar diff_x = mpt.x - pt.x;\n
\t\t\t\tvar diff_y = mpt.y - pt.y;\n
\t\t\t\tsvgedit.path.path.dragging = [mouse_x, mouse_y];\n
\t\t\t\t\n
\t\t\t\tif (svgedit.path.path.dragctrl) {\n
\t\t\t\t\tsvgedit.path.path.moveCtrl(diff_x, diff_y);\n
\t\t\t\t} else {\n
\t\t\t\t\tsvgedit.path.path.movePts(diff_x, diff_y);\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tsvgedit.path.path.selected_pts = [];\n
\t\t\t\tsvgedit.path.path.eachSeg(function(i) {\n
\t\t\t\t\tvar seg = this;\n
\t\t\t\t\tif (!seg.next \046\046 !seg.prev) {return;}\n
\t\t\t\t\t\t\n
\t\t\t\t\tvar item = seg.item;\n
\t\t\t\t\tvar rbb = rubberBox.getBBox();\n
\t\t\t\t\t\n
\t\t\t\t\tvar pt = svgedit.path.getGripPt(seg);\n
\t\t\t\t\tvar pt_bb = {\n
\t\t\t\t\t\tx: pt.x,\n
\t\t\t\t\t\ty: pt.y,\n
\t\t\t\t\t\twidth: 0,\n
\t\t\t\t\t\theight: 0\n
\t\t\t\t\t};\n
\t\t\t\t\n
\t\t\t\t\tvar sel = svgedit.math.rectsIntersect(rbb, pt_bb);\n
\n
\t\t\t\t\tthis.select(sel);\n
\t\t\t\t\t//Note that addPtsToSelection is not being run\n
\t\t\t\t\tif (sel) {svgedit.path.path.selected_pts.push(seg.index);}\n
\t\t\t\t});\n
\n
\t\t\t}\n
\t\t}, \n
\t\tmouseUp: function(evt, element, mouse_x, mouse_y) {\n
\t\t\t\n
\t\t\t// Create mode\n
\t\t\tif (current_mode === "path") {\n
\t\t\t\tnewPoint = null;\n
\t\t\t\tif (!drawn_path) {\n
\t\t\t\t\telement = svgedit.utilities.getElem(getId());\n
\t\t\t\t\tstarted = false;\n
\t\t\t\t\tfirstCtrl = null;\n
\t\t\t\t}\n
\n
\t\t\t\treturn {\n
\t\t\t\t\tkeep: true,\n
\t\t\t\t\telement: element\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\t\n
\t\t\t// Edit mode\n
\t\t\t\n
\t\t\tif (svgedit.path.path.dragging) {\n
\t\t\t\tvar last_pt = svgedit.path.path.cur_pt;\n
\n
\t\t\t\tsvgedit.path.path.dragging = false;\n
\t\t\t\tsvgedit.path.path.dragctrl = false;\n
\t\t\t\tsvgedit.path.path.update();\n
\t\t\t\t\n
\t\t\t\tif (hasMoved) {\n
\t\t\t\t\tsvgedit.path.path.endChanges("Move path point(s)");\n
\t\t\t\t} \n
\t\t\t\t\n
\t\t\t\tif (!evt.shiftKey \046\046 !hasMoved) {\n
\t\t\t\t\tsvgedit.path.path.selectPt(last_pt);\n
\t\t\t\t} \n
\t\t\t} else if (rubberBox \046\046 rubberBox.getAttribute(\'display\') != \'none\') {\n
\t\t\t\t// Done with multi-node-select\n
\t\t\t\trubberBox.setAttribute("display", "none");\n
\t\t\t\t\n
\t\t\t\tif (rubberBox.getAttribute(\'width\') \074= 2 \046\046 rubberBox.getAttribute(\'height\') \074= 2) {\n
\t\t\t\t\tpathActions.toSelectMode(evt.target);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t// else, move back to select mode\t\n
\t\t\t} else {\n
\t\t\t\tpathActions.toSelectMode(evt.target);\n
\t\t\t}\n
\t\t\thasMoved = false;\n
\t\t},\n
\t\ttoEditMode: function(element) {\n
\t\t\tsvgedit.path.path = svgedit.path.getPath_(element);\n
\t\t\tcurrent_mode = "pathedit";\n
\t\t\tclearSelection();\n
\t\t\tsvgedit.path.path.show(true).update();\n
\t\t\tsvgedit.path.path.oldbbox = svgedit.utilities.getBBox(svgedit.path.path.elem);\n
\t\t\tsubpath = false;\n
\t\t},\n
\t\ttoSelectMode: function(elem) {\n
\t\t\tvar selPath = (elem == svgedit.path.path.elem);\n
\t\t\tcurrent_mode = "select";\n
\t\t\tsvgedit.path.path.show(false);\n
\t\t\tcurrent_path = false;\n
\t\t\tclearSelection();\n
\t\t\t\n
\t\t\tif (svgedit.path.path.matrix) {\n
\t\t\t\t// Rotated, so may need to re-calculate the center\n
\t\t\t\tsvgedit.path.recalcRotatedPath();\n
\t\t\t}\n
\t\t\t\n
\t\t\tif (selPath) {\n
\t\t\t\tcall("selected", [elem]);\n
\t\t\t\taddToSelection([elem], true);\n
\t\t\t}\n
\t\t},\n
\t\taddSubPath: function(on) {\n
\t\t\tif (on) {\n
\t\t\t\t// Internally we go into "path" mode, but in the UI it will\n
\t\t\t\t// still appear as if in "pathedit" mode.\n
\t\t\t\tcurrent_mode = "path";\n
\t\t\t\tsubpath = true;\n
\t\t\t} else {\n
\t\t\t\tpathActions.clear(true);\n
\t\t\t\tpathActions.toEditMode(svgedit.path.path.elem);\n
\t\t\t}\n
\t\t},\n
\t\tselect: function(target) {\n
\t\t\tif (current_path === target) {\n
\t\t\t\tpathActions.toEditMode(target);\n
\t\t\t\tcurrent_mode = "pathedit";\n
\t\t\t} // going into pathedit mode\n
\t\t\telse {\n
\t\t\t\tcurrent_path = target;\n
\t\t\t}\t\n
\t\t},\n
\t\treorient: function() {\n
\t\t\tvar elem = selectedElements[0];\n
\t\t\tif (!elem) {return;}\n
\t\t\tvar angle = svgedit.utilities.getRotationAngle(elem);\n
\t\t\tif (angle == 0) {return;}\n
\t\t\t\n
\t\t\tvar batchCmd = new svgedit.history.BatchCommand("Reorient path");\n
\t\t\tvar changes = {\n
\t\t\t\td: elem.getAttribute(\'d\'),\n
\t\t\t\ttransform: elem.getAttribute(\'transform\')\n
\t\t\t};\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(elem, changes));\n
\t\t\tclearSelection();\n
\t\t\tthis.resetOrientation(elem);\n
\t\t\t\n
\t\t\taddCommandToHistory(batchCmd);\n
\n
\t\t\t// Set matrix to null\n
\t\t\tsvgedit.path.getPath_(elem).show(false).matrix = null; \n
\n
\t\t\tthis.clear();\n
\t\n
\t\t\taddToSelection([elem], true);\n
\t\t\tcall("changed", selectedElements);\n
\t\t},\n
\t\t\n
\t\tclear: function(remove) {\n
\t\t\tcurrent_path = null;\n
\t\t\tif (drawn_path) {\n
\t\t\t\tvar elem = svgedit.utilities.getElem(getId());\n
\t\t\t\t$(svgedit.utilities.getElem("path_stretch_line")).remove();\n
\t\t\t\t$(elem).remove();\n
\t\t\t\t$(svgedit.utilities.getElem("pathpointgrip_container")).find(\'*\').attr(\'display\', \'none\');\n
\t\t\t\tdrawn_path = firstCtrl = null;\n
\t\t\t\tstarted = false;\n
\t\t\t} else if (current_mode == "pathedit") {\n
\t\t\t\tthis.toSelectMode();\n
\t\t\t}\n
\t\t\tif (svgedit.path.path) {svgedit.path.path.init().show(false);}\n
\t\t},\n
\t\tresetOrientation: function(path) {\n
\t\t\tif (path == null || path.nodeName != \'path\') {return false;}\n
\t\t\tvar tlist = svgedit.transformlist.getTransformList(path);\n
\t\t\tvar m = svgedit.math.transformListToTransform(tlist).matrix;\n
\t\t\ttlist.clear();\n
\t\t\tpath.removeAttribute("transform");\n
\t\t\tvar segList = path.pathSegList;\n
\t\t\t\n
\t\t\t// Opera/win/non-EN throws an error here.\n
\t\t\t// TODO: Find out why!\n
\t\t\t// Presumed fixed in Opera 10.5, so commented out for now\n
\t\t\t\n
//\t\t\ttry {\n
\t\t\t\tvar len = segList.numberOfItems;\n
//\t\t\t} catch(err) {\n
//\t\t\t\tvar fixed_d = pathActions.convertPath(path);\n
//\t\t\t\tpath.setAttribute(\'d\', fixed_d);\n
//\t\t\t\tsegList = path.pathSegList;\n
//\t\t\t\tvar len = segList.numberOfItems;\n
//\t\t\t}\n
\t\t\tvar i, last_x, last_y;\n
\n
\t\t\tfor (i = 0; i \074 len; ++i) {\n
\t\t\t\tvar seg = segList.getItem(i);\n
\t\t\t\tvar type = seg.pathSegType;\n
\t\t\t\tif (type == 1) {continue;}\n
\t\t\t\tvar pts = [];\n
\t\t\t\t$.each([\'\',1,2], function(j, n) {\n
\t\t\t\t\tvar x = seg[\'x\'+n], y = seg[\'y\'+n];\n
\t\t\t\t\tif (x !== undefined \046\046 y !== undefined) {\n
\t\t\t\t\t\tvar pt = svgedit.math.transformPoint(x, y, m);\n
\t\t\t\t\t\tpts.splice(pts.length, 0, pt.x, pt.y);\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tsvgedit.path.replacePathSeg(type, i, pts, path);\n
\t\t\t}\n
\t\t\t\n
\t\t\treorientGrads(path, m);\n
\t\t},\n
\t\tzoomChange: function() {\n
\t\t\tif (current_mode == "pathedit") {\n
\t\t\t\tsvgedit.path.path.update();\n
\t\t\t}\n
\t\t},\n
\t\tgetNodePoint: function() {\n
\t\t\tvar sel_pt = svgedit.path.path.selected_pts.length ? svgedit.path.path.selected_pts[0] : 1;\n
\n
\t\t\tvar seg = svgedit.path.path.segs[sel_pt];\n
\t\t\treturn {\n
\t\t\t\tx: seg.item.x,\n
\t\t\t\ty: seg.item.y,\n
\t\t\t\ttype: seg.type\n
\t\t\t};\n
\t\t}, \n
\t\tlinkControlPoints: function(linkPoints) {\n
\t\t\tsvgedit.path.setLinkControlPoints(linkPoints);\n
\t\t},\n
\t\tclonePathNode: function() {\n
\t\t\tsvgedit.path.path.storeD();\n
\t\t\t\n
\t\t\tvar sel_pts = svgedit.path.path.selected_pts;\n
\t\t\tvar segs = svgedit.path.path.segs;\n
\t\t\t\n
\t\t\tvar i = sel_pts.length;\n
\t\t\tvar nums = [];\n
\n
\t\t\twhile (i--) {\n
\t\t\t\tvar pt = sel_pts[i];\n
\t\t\t\tsvgedit.path.path.addSeg(pt);\n
\t\t\t\t\n
\t\t\t\tnums.push(pt + i);\n
\t\t\t\tnums.push(pt + i + 1);\n
\t\t\t}\n
\t\t\tsvgedit.path.path.init().addPtsToSelection(nums);\n
\n
\t\t\tsvgedit.path.path.endChanges("Clone path node(s)");\n
\t\t},\n
\t\topencloseSubPath: function() {\n
\t\t\tvar sel_pts = svgedit.path.path.selected_pts;\n
\t\t\t// Only allow one selected node for now\n
\t\t\tif (sel_pts.length !== 1) {return;}\n
\t\t\t\n
\t\t\tvar elem = svgedit.path.path.elem;\n
\t\t\tvar list = elem.pathSegList;\n
\n
\t\t\tvar len = list.numberOfItems;\n
\n
\t\t\tvar index = sel_pts[0];\n
\t\t\t\n
\t\t\tvar open_pt = null;\n
\t\t\tvar start_item = null;\n
\n
\t\t\t// Check if subpath is already open\n
\t\t\tsvgedit.path.path.eachSeg(function(i) {\n
\t\t\t\tif (this.type === 2 \046\046 i \074= index) {\n
\t\t\t\t\tstart_item = this.item;\n
\t\t\t\t}\n
\t\t\t\tif (i \074= index) {return true;}\n
\t\t\t\tif (this.type === 2) {\n
\t\t\t\t\t// Found M first, so open\n
\t\t\t\t\topen_pt = i;\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\t\t\t\tif (this.type === 1) {\n
\t\t\t\t\t// Found Z first, so closed\n
\t\t\t\t\topen_pt = false;\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\t\n
\t\t\tif (open_pt == null) {\n
\t\t\t\t// Single path, so close last seg\n
\t\t\t\topen_pt = svgedit.path.path.segs.length - 1;\n
\t\t\t}\n
\n
\t\t\tif (open_pt !== false) {\n
\t\t\t\t// Close this path\n
\t\t\t\t\n
\t\t\t\t// Create a line going to the previous "M"\n
\t\t\t\tvar newseg = elem.createSVGPathSegLinetoAbs(start_item.x, start_item.y);\n
\t\t\t\n
\t\t\t\tvar closer = elem.createSVGPathSegClosePath();\n
\t\t\t\tif (open_pt == svgedit.path.path.segs.length - 1) {\n
\t\t\t\t\tlist.appendItem(newseg);\n
\t\t\t\t\tlist.appendItem(closer);\n
\t\t\t\t} else {\n
\t\t\t\t\tsvgedit.path.insertItemBefore(elem, closer, open_pt);\n
\t\t\t\t\tsvgedit.path.insertItemBefore(elem, newseg, open_pt);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tsvgedit.path.path.init().selectPt(open_pt+1);\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// M 1,1 L 2,2 L 3,3 L 1,1 z // open at 2,2\n
\t\t\t// M 2,2 L 3,3 L 1,1\n
\t\t\t\n
\t\t\t// M 1,1 L 2,2 L 1,1 z M 4,4 L 5,5 L6,6 L 5,5 z \n
\t\t\t// M 1,1 L 2,2 L 1,1 z [M 4,4] L 5,5 L(M)6,6 L 5,5 z \n
\t\t\t\n
\t\t\tvar seg = svgedit.path.path.segs[index];\n
\t\t\t\n
\t\t\tif (seg.mate) {\n
\t\t\t\tlist.removeItem(index); // Removes last "L"\n
\t\t\t\tlist.removeItem(index); // Removes the "Z"\n
\t\t\t\tsvgedit.path.path.init().selectPt(index - 1);\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar i, last_m, z_seg;\n
\t\t\t\n
\t\t\t// Find this sub-path\'s closing point and remove\n
\t\t\tfor (i = 0; i\074list.numberOfItems; i++) {\n
\t\t\t\tvar item = list.getItem(i);\n
\n
\t\t\t\tif (item.pathSegType === 2) {\n
\t\t\t\t\t// Find the preceding M\n
\t\t\t\t\tlast_m = i;\n
\t\t\t\t} else if (i === index) {\n
\t\t\t\t\t// Remove it\n
\t\t\t\t\tlist.removeItem(last_m);\n
//\t\t\t\t\t\tindex--;\n
\t\t\t\t} else if (item.pathSegType === 1 \046\046 index \074 i) {\n
\t\t\t\t\t// Remove the closing seg of this subpath\n
\t\t\t\t\tz_seg = i-1;\n
\t\t\t\t\tlist.removeItem(i);\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar num = (index - last_m) - 1;\n
\t\t\t\n
\t\t\twhile (num--) {\n
\t\t\t\tsvgedit.path.insertItemBefore(elem, list.getItem(last_m), z_seg);\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar pt = list.getItem(last_m);\n
\t\t\t\n
\t\t\t// Make this point the new "M"\n
\t\t\tsvgedit.path.replacePathSeg(2, last_m, [pt.x, pt.y]);\n
\t\t\t\n
\t\t\ti = index; // i is local here, so has no effect; what is the reason for this?\n
\t\t\t\n
\t\t\tsvgedit.path.path.init().selectPt(0);\n
\t\t},\n
\t\tdeletePathNode: function() {\n
\t\t\tif (!pathActions.canDeleteNodes) {return;}\n
\t\t\tsvgedit.path.path.storeD();\n
\t\t\t\n
\t\t\tvar sel_pts = svgedit.path.path.selected_pts;\n
\t\t\tvar i = sel_pts.length;\n
\n
\t\t\twhile (i--) {\n
\t\t\t\tvar pt = sel_pts[i];\n
\t\t\t\tsvgedit.path.path.deleteSeg(pt);\n
\t\t\t}\n
\t\t\t\n
\t\t\t// Cleanup\n
\t\t\tvar cleanup = function() {\n
\t\t\t\tvar segList = svgedit.path.path.elem.pathSegList;\n
\t\t\t\tvar len = segList.numberOfItems;\n
\t\t\t\t\n
\t\t\t\tvar remItems = function(pos, count) {\n
\t\t\t\t\twhile (count--) {\n
\t\t\t\t\t\tsegList.removeItem(pos);\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\n
\t\t\t\tif (len \074= 1) {return true;}\n
\t\t\t\t\n
\t\t\t\twhile (len--) {\n
\t\t\t\t\tvar item = segList.getItem(len);\n
\t\t\t\t\tif (item.pathSegType === 1) {\n
\t\t\t\t\t\tvar prev = segList.getItem(len-1);\n
\t\t\t\t\t\tvar nprev = segList.getItem(len-2);\n
\t\t\t\t\t\tif (prev.pathSegType === 2) {\n
\t\t\t\t\t\t\tremItems(len-1, 2);\n
\t\t\t\t\t\t\tcleanup();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t} else if (nprev.pathSegType === 2) {\n
\t\t\t\t\t\t\tremItems(len-2, 3);\n
\t\t\t\t\t\t\tcleanup();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t} else if (item.pathSegType === 2) {\n
\t\t\t\t\t\tif (len \076 0) {\n
\t\t\t\t\t\t\tvar prev_type = segList.getItem(len-1).pathSegType;\n
\t\t\t\t\t\t\t// Path has M M\n
\t\t\t\t\t\t\tif (prev_type === 2) {\n
\t\t\t\t\t\t\t\tremItems(len-1, 1);\n
\t\t\t\t\t\t\t\tcleanup();\n
\t\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\t// Entire path ends with Z M \n
\t\t\t\t\t\t\t} else if (prev_type === 1 \046\046 segList.numberOfItems-1 === len) {\n
\t\t\t\t\t\t\t\tremItems(len, 1);\n
\t\t\t\t\t\t\t\tcleanup();\n
\t\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\t\n
\t\t\t\treturn false;\n
\t\t\t};\n
\t\t\t\n
\t\t\tcleanup();\n
\t\t\t\n
\t\t\t// Completely delete a path with 1 or 0 segments\n
\t\t\tif (svgedit.path.path.elem.pathSegList.numberOfItems \074= 1) {\n
\t\t\t\tpathActions.toSelectMode(svgedit.path.path.elem);\n
\t\t\t\tcanvas.deleteSelectedElements();\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\t\n
\t\t\tsvgedit.path.path.init();\n
\t\t\tsvgedit.path.path.clearSelection();\n
\t\t\t\n
\t\t\t// TODO: Find right way to select point now\n
\t\t\t// path.selectPt(sel_pt);\n
\t\t\tif (window.opera) { // Opera repaints incorrectly\n
\t\t\t\tvar cp = $(svgedit.path.path.elem); \n
\t\t\t\tcp.attr(\'d\', cp.attr(\'d\'));\n
\t\t\t}\n
\t\t\tsvgedit.path.path.endChanges("Delete path node(s)");\n
\t\t},\n
\t\tsmoothPolylineIntoPath: smoothPolylineIntoPath,\n
\t\tsetSegType: function(v) {\n
\t\t\tsvgedit.path.path.setSegType(v);\n
\t\t},\n
\t\tmoveNode: function(attr, newValue) {\n
\t\t\tvar sel_pts = svgedit.path.path.selected_pts;\n
\t\t\tif (!sel_pts.length) {return;}\n
\t\t\t\n
\t\t\tsvgedit.path.path.storeD();\n
\t\t\t\n
\t\t\t// Get first selected point\n
\t\t\tvar seg = svgedit.path.path.segs[sel_pts[0]];\n
\t\t\tvar diff = {x:0, y:0};\n
\t\t\tdiff[attr] = newValue - seg.item[attr];\n
\t\t\t\n
\t\t\tseg.move(diff.x, diff.y);\n
\t\t\tsvgedit.path.path.endChanges("Move path point");\n
\t\t},\n
\t\tfixEnd: function(elem) {\n
\t\t\t// Adds an extra segment if the last seg before a Z doesn\'t end\n
\t\t\t// at its M point\n
\t\t\t// M0,0 L0,100 L100,100 z\n
\t\t\tvar segList = elem.pathSegList;\n
\t\t\tvar len = segList.numberOfItems;\n
\t\t\tvar i, last_m;\n
\t\t\tfor (i = 0; i \074 len; ++i) {\n
\t\t\t\tvar item = segList.getItem(i);\n
\t\t\t\tif (item.pathSegType === 2) {\n
\t\t\t\t\tlast_m = item;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif (item.pathSegType === 1) {\n
\t\t\t\t\tvar prev = segList.getItem(i-1);\n
\t\t\t\t\tif (prev.x != last_m.x || prev.y != last_m.y) {\n
\t\t\t\t\t\t// Add an L segment here\n
\t\t\t\t\t\tvar newseg = elem.createSVGPathSegLinetoAbs(last_m.x, last_m.y);\n
\t\t\t\t\t\tsvgedit.path.insertItemBefore(elem, newseg, i);\n
\t\t\t\t\t\t// Can this be done better?\n
\t\t\t\t\t\tpathActions.fixEnd(elem);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\tif (svgedit.browser.isWebkit()) {resetD(elem);}\n
\t\t},\n
\t\t// Convert a path to one with only absolute or relative values\n
\t\tconvertPath: function(path, toRel) {\n
\t\t\tvar i;\n
\t\t\tvar segList = path.pathSegList;\n
\t\t\tvar len = segList.numberOfItems;\n
\t\t\tvar curx = 0, cury = 0;\n
\t\t\tvar d = "";\n
\t\t\tvar last_m = null;\n
\t\t\t\n
\t\t\tfor (i = 0; i \074 len; ++i) {\n
\t\t\t\tvar seg = segList.getItem(i);\n
\t\t\t\t// if these properties are not in the segment, set them to zero\n
\t\t\t\tvar x = seg.x || 0,\n
\t\t\t\t\ty = seg.y || 0,\n
\t\t\t\t\tx1 = seg.x1 || 0,\n
\t\t\t\t\ty1 = seg.y1 || 0,\n
\t\t\t\t\tx2 = seg.x2 || 0,\n
\t\t\t\t\ty2 = seg.y2 || 0;\n
\t\n
\t\t\t\tvar type = seg.pathSegType;\n
\t\t\t\tvar letter = pathMap[type][\'to\'+(toRel?\'Lower\':\'Upper\')+\'Case\']();\n
\t\t\t\t\n
\t\t\t\tvar addToD = function(pnts, more, last) {\n
\t\t\t\t\tvar str = \'\';\n
\t\t\t\t\tmore = more ? \' \' + more.join(\' \') : \'\';\n
\t\t\t\t\tlast = last ? \' \' + svgedit.units.shortFloat(last) : \'\';\n
\t\t\t\t\t$.each(pnts, function(i, pnt) {\n
\t\t\t\t\t\tpnts[i] = svgedit.units.shortFloat(pnt);\n
\t\t\t\t\t});\n
\t\t\t\t\td += letter + pnts.join(\' \') + more + last;\n
\t\t\t\t};\n
\t\t\t\t\n
\t\t\t\tswitch (type) {\n
\t\t\t\t\tcase 1: // z,Z closepath (Z/z)\n
\t\t\t\t\t\td += "z";\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase 12: // absolute horizontal line (H)\n
\t\t\t\t\t\tx -= curx;\n
\t\t\t\t\tcase 13: // relative horizontal line (h)\n
\t\t\t\t\t\tif (toRel) {\n
\t\t\t\t\t\t\tcurx += x;\n
\t\t\t\t\t\t\tletter = \'l\';\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tx += curx;\n
\t\t\t\t\t\t\tcurx = x;\n
\t\t\t\t\t\t\tletter = \'L\';\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t// Convert to "line" for easier editing\n
\t\t\t\t\t\taddToD([[x, cury]]);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase 14: // absolute vertical line (V)\n
\t\t\t\t\t\ty -= cury;\n
\t\t\t\t\tcase 15: // relative vertical line (v)\n
\t\t\t\t\t\tif (toRel) {\n
\t\t\t\t\t\t\tcury += y;\n
\t\t\t\t\t\t\tletter = \'l\';\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\ty += cury;\n
\t\t\t\t\t\t\tcury = y;\n
\t\t\t\t\t\t\tletter = \'L\';\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t// Convert to "line" for easier editing\n
\t\t\t\t\t\taddToD([[curx, y]]);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase 2: // absolute move (M)\n
\t\t\t\t\tcase 4: // absolute line (L)\n
\t\t\t\t\tcase 18: // absolute smooth quad (T)\n
\t\t\t\t\t\tx -= curx;\n
\t\t\t\t\t\ty -= cury;\n
\t\t\t\t\tcase 5: // relative line (l)\n
\t\t\t\t\tcase 3: // relative move (m)\n
\t\t\t\t\t\t// If the last segment was a "z", this must be relative to \n
\t\t\t\t\t\tif (last_m \046\046 segList.getItem(i-1).pathSegType === 1 \046\046 !toRel) {\n
\t\t\t\t\t\t\tcurx = last_m[0];\n
\t\t\t\t\t\t\tcury = last_m[1];\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tcase 19: // relative smooth quad (t)\n
\t\t\t\t\t\tif (toRel) {\n
\t\t\t\t\t\t\tcurx += x;\n
\t\t\t\t\t\t\tcury += y;\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tx += curx;\n
\t\t\t\t\t\t\ty += cury;\n
\t\t\t\t\t\t\tcurx = x;\n
\t\t\t\t\t\t\tcury = y;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif (type === 3) {last_m = [curx, cury];}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\taddToD([[x, y]]);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase 6: // absolute cubic (C)\n
\t\t\t\t\t\tx -= curx; x1 -= curx; x2 -= curx;\n
\t\t\t\t\t\ty -= cury; y1 -= cury; y2 -= cury;\n
\t\t\t\t\tcase 7: // relative cubic (c)\n
\t\t\t\t\t\tif (toRel) {\n
\t\t\t\t\t\t\tcurx += x;\n
\t\t\t\t\t\t\tcury += y;\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tx += curx; x1 += curx; x2 += curx;\n
\t\t\t\t\t\t\ty += cury; y1 += cury; y2 += cury;\n
\t\t\t\t\t\t\tcurx = x;\n
\t\t\t\t\t\t\tcury = y;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\taddToD([[x1, y1], [x2, y2], [x, y]]);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase 8: // absolute quad (Q)\n
\t\t\t\t\t\tx -= curx; x1 -= curx;\n
\t\t\t\t\t\ty -= cury; y1 -= cury;\n
\t\t\t\t\tcase 9: // relative quad (q) \n
\t\t\t\t\t\tif (toRel) {\n
\t\t\t\t\t\t\tcurx += x;\n
\t\t\t\t\t\t\tcury += y;\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tx += curx; x1 += curx;\n
\t\t\t\t\t\t\ty += cury; y1 += cury;\n
\t\t\t\t\t\t\tcurx = x;\n
\t\t\t\t\t\t\tcury = y;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\taddToD([[x1, y1],[x, y]]);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase 10: // absolute elliptical arc (A)\n
\t\t\t\t\t\tx -= curx;\n
\t\t\t\t\t\ty -= cury;\n
\t\t\t\t\tcase 11: // relative elliptical arc (a)\n
\t\t\t\t\t\tif (toRel) {\n
\t\t\t\t\t\t\tcurx += x;\n
\t\t\t\t\t\t\tcury += y;\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tx += curx;\n
\t\t\t\t\t\t\ty += cury;\n
\t\t\t\t\t\t\tcurx = x;\n
\t\t\t\t\t\t\tcury = y;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\taddToD([[seg.r1, seg.r2]], [\n
\t\t\t\t\t\t\t\tseg.angle,\n
\t\t\t\t\t\t\t\t(seg.largeArcFlag ? 1 : 0),\n
\t\t\t\t\t\t\t\t(seg.sweepFlag ? 1 : 0)\n
\t\t\t\t\t\t\t], [x, y]\n
\t\t\t\t\t\t);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase 16: // absolute smooth cubic (S)\n
\t\t\t\t\t\tx -= curx; x2 -= curx;\n
\t\t\t\t\t\ty -= cury; y2 -= cury;\n
\t\t\t\t\tcase 17: // relative smooth cubic (s)\n
\t\t\t\t\t\tif (toRel) {\n
\t\t\t\t\t\t\tcurx += x;\n
\t\t\t\t\t\t\tcury += y;\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tx += curx; x2 += curx;\n
\t\t\t\t\t\t\ty += cury; y2 += cury;\n
\t\t\t\t\t\t\tcurx = x;\n
\t\t\t\t\t\t\tcury = y;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\taddToD([[x2, y2],[x, y]]);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t} // switch on path segment type\n
\t\t\t} // for each segment\n
\t\t\treturn d;\n
\t\t}\n
\t};\n
}();\n
// end pathActions\n
\n
// Group: Serialization\n
\n
// Function: removeUnusedDefElems\n
// Looks at DOM elements inside the \074defs\076 to see if they are referred to,\n
// removes them from the DOM if they are not.\n
// \n
// Returns:\n
// The amount of elements that were removed\n
var removeUnusedDefElems = this.removeUnusedDefElems = function() {\n
\tvar defs = svgcontent.getElementsByTagNameNS(NS.SVG, "defs");\n
\tif (!defs || !defs.length) {return 0;}\n
\t\n
//\tif (!defs.firstChild) {return;}\n
\t\n
\tvar defelem_uses = [],\n
\t\tnumRemoved = 0;\n
\tvar attrs = [\'fill\', \'stroke\', \'filter\', \'marker-start\', \'marker-mid\', \'marker-end\'];\n
\tvar alen = attrs.length;\n
\t\n
\tvar all_els = svgcontent.getElementsByTagNameNS(NS.SVG, \'*\');\n
\tvar all_len = all_els.length;\n
\t\n
\tvar i, j;\n
\tfor (i = 0; i \074 all_len; i++) {\n
\t\tvar el = all_els[i];\n
\t\tfor (j = 0; j \074 alen; j++) {\n
\t\t\tvar ref = svgedit.utilities.getUrlFromAttr(el.getAttribute(attrs[j]));\n
\t\t\tif (ref) {\n
\t\t\t\tdefelem_uses.push(ref.substr(1));\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\t// gradients can refer to other gradients\n
\t\tvar href = getHref(el);\n
\t\tif (href \046\046 href.indexOf(\'#\') === 0) {\n
\t\t\tdefelem_uses.push(href.substr(1));\n
\t\t}\n
\t}\n
\t\n
\tvar defelems = $(defs).find("linearGradient, radialGradient, filter, marker, svg, symbol");\n
\ti = defelems.length;\n
\twhile (i--) {\n
\t\tvar defelem = defelems[i];\n
\t\tvar id = defelem.id;\n
\t\tif (defelem_uses.indexOf(id) \074 0) {\n
\t\t\t// Not found, so remove (but remember)\n
\t\t\tremovedElements[id] = defelem;\n
\t\t\tdefelem.parentNode.removeChild(defelem);\n
\t\t\tnumRemoved++;\n
\t\t}\n
\t}\n
\n
\treturn numRemoved;\n
};\n
\n
// Function: svgCanvasToString\n
// Main function to set up the SVG content for output \n
//\n
// Returns: \n
// String containing the SVG image for output\n
this.svgCanvasToString = function() {\n
\t// keep calling it until there are none to remove\n
\twhile (removeUnusedDefElems() \076 0) {}\n
\t\n
\tpathActions.clear(true);\n
\t\n
\t// Keep SVG-Edit comment on top\n
\t$.each(svgcontent.childNodes, function(i, node) {\n
\t\tif (i \046\046 node.nodeType === 8 \046\046 node.data.indexOf(\'Created with\') \076= 0) {\n
\t\t\tsvgcontent.insertBefore(node, svgcontent.firstChild);\n
\t\t}\n
\t});\n
\t\n
\t// Move out of in-group editing mode\n
\tif (current_group) {\n
\t\tleaveContext();\n
\t\tselectOnly([current_group]);\n
\t}\n
\t\n
\tvar naked_svgs = [];\n
\t\n
\t// Unwrap gsvg if it has no special attributes (only id and style)\n
\t$(svgcontent).find(\'g:data(gsvg)\').each(function() {\n
\t\tvar attrs = this.attributes;\n
\t\tvar len = attrs.length;\n
\t\tvar i;\n
\t\tfor (i = 0; i \074 len; i++) {\n
\t\t\tif (attrs[i].nodeName == \'id\' || attrs[i].nodeName == \'style\') {\n
\t\t\t\tlen--;\n
\t\t\t}\n
\t\t}\n
\t\t// No significant attributes, so ungroup\n
\t\tif (len \074= 0) {\n
\t\t\tvar svg = this.firstChild;\n
\t\t\tnaked_svgs.push(svg);\n
\t\t\t$(this).replaceWith(svg);\n
\t\t}\n
\t});\n
\tvar output = this.svgToString(svgcontent, 0);\n
\t\n
\t// Rewrap gsvg\n
\tif (naked_svgs.length) {\n
\t\t$(naked_svgs).each(function() {\n
\t\t\tgroupSvgElem(this);\n
\t\t});\n
\t}\n
\t\n
\treturn output;\n
};\n
\n
// Function: svgToString\n
// Sub function ran on each SVG element to convert it to a string as desired\n
// \n
// Parameters: \n
// elem - The SVG element to convert\n
// indent - Integer with the amount of spaces to indent this tag\n
//\n
// Returns: \n
// String with the given element as an SVG tag\n
this.svgToString = function(elem, indent) {\n
\tvar out = [], \n
\t\ttoXml = svgedit.utilities.toXml;\n
\tvar unit = curConfig.baseUnit;\n
\tvar unit_re = new RegExp(\'^-?[\\\\d\\\\.]+\' + unit + \'$\');\n
\n
\tif (elem) {\n
\t\tcleanupElement(elem);\n
\t\tvar attrs = elem.attributes,\n
\t\t\tattr,\n
\t\t\ti,\n
\t\t\tchilds = elem.childNodes;\n
\t\t\n
\t\tfor (i = 0; i \074 indent; i++) {out.push(\' \');}\n
\t\tout.push("\074"); out.push(elem.nodeName);\n
\t\tif (elem.id === \'svgcontent\') {\n
\t\t\t// Process root element separately\n
\t\t\tvar res = getResolution();\n
\t\t\t\n
\t\t\tvar vb = "";\n
\t\t\t// TODO: Allow this by dividing all values by current baseVal\n
\t\t\t// Note that this also means we should properly deal with this on import\n
//\t\t\tif (curConfig.baseUnit !== "px") {\n
//\t\t\t\tvar unit = curConfig.baseUnit;\n
//\t\t\t\tvar unit_m = svgedit.units.getTypeMap()[unit];\n
//\t\t\t\tres.w = svgedit.units.shortFloat(res.w / unit_m)\n
//\t\t\t\tres.h = svgedit.units.shortFloat(res.h / unit_m)\n
//\t\t\t\tvb = \' viewBox="\' + [0, 0, res.w, res.h].join(\' \') + \'"\';\n
//\t\t\t\tres.w += unit;\n
//\t\t\t\tres.h += unit;\n
//\t\t\t}\n
\t\t\t\n
\t\t\tif (unit !== "px") {\n
\t\t\t\tres.w = svgedit.units.convertUnit(res.w, unit) + unit;\n
\t\t\t\tres.h = svgedit.units.convertUnit(res.h, unit) + unit;\n
\t\t\t}\n
\t\t\t\n
\t\t\tout.push(\' width="\' + res.w + \'" height="\' + res.h + \'"\' + vb + \' xmlns="\'+NS.SVG+\'"\');\n
\t\t\t\n
\t\t\tvar nsuris = {};\n
\t\t\t\n
\t\t\t// Check elements for namespaces, add if found\n
\t\t\t$(elem).find(\'*\').andSelf().each(function() {\n
\t\t\t\tvar el = this;\n
\t\t\t\t// for some elements have no attribute\n
\t\t\t\tvar uri = this.namespaceURI;\n
\t\t\t\tif(uri \046\046 !nsuris[uri] \046\046 nsMap[uri] \046\046 nsMap[uri] !== \'xmlns\' \046\046 nsMap[uri] !== \'xml\' ) {\n
\t\t\t\t\tnsuris[uri] = true;\n
\t\t\t\t\tout.push(" xmlns:" + nsMap[uri] + \'="\' + uri +\'"\');\n
\t\t\t\t}\n
\t\t\n
\t\t\t\t$.each(this.attributes, function(i, attr) {\n
\t\t\t\t\tvar uri = attr.namespaceURI;\n
\t\t\t\t\tif (uri \046\046 !nsuris[uri] \046\046 nsMap[uri] !== \'xmlns\' \046\046 nsMap[uri] !== \'xml\' ) {\n
\t\t\t\t\t\tnsuris[uri] = true;\n
\t\t\t\t\t\tout.push(" xmlns:" + nsMap[uri] + \'="\' + uri +\'"\');\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t});\n
\t\t\t\n
\t\t\ti = attrs.length;\n
\t\t\tvar attr_names = [\'width\', \'height\', \'xmlns\', \'x\', \'y\', \'viewBox\', \'id\', \'overflow\'];\n
\t\t\twhile (i--) {\n
\t\t\t\tattr = attrs.item(i);\n
\t\t\t\tvar attrVal = toXml(attr.nodeValue);\n
\t\t\t\t\n
\t\t\t\t// Namespaces have already been dealt with, so skip\n
\t\t\t\tif (attr.nodeName.indexOf(\'xmlns:\') === 0) {continue;}\n
\n
\t\t\t\t// only serialize attributes we don\'t use internally\n
\t\t\t\tif (attrVal != "" \046\046 attr_names.indexOf(attr.localName) == -1) {\n
\n
\t\t\t\t\tif (!attr.namespaceURI || nsMap[attr.namespaceURI]) {\n
\t\t\t\t\t\tout.push(\' \'); \n
\t\t\t\t\t\tout.push(attr.nodeName); out.push("=\\"");\n
\t\t\t\t\t\tout.push(attrVal); out.push("\\"");\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t} else {\n
\t\t\t// Skip empty defs\n
\t\t\tif (elem.nodeName === \'defs\' \046\046 !elem.firstChild) {return;}\n
\t\t\n
\t\t\tvar moz_attrs = [\'-moz-math-font-style\', \'_moz-math-font-style\'];\n
\t\t\tfor (i = attrs.length - 1; i \076= 0; i--) {\n
\t\t\t\tattr = attrs.item(i);\n
\t\t\t\tvar attrVal = toXml(attr.nodeValue);\n
\t\t\t\t//remove bogus attributes added by Gecko\n
\t\t\t\tif (moz_attrs.indexOf(attr.localName) \076= 0) {continue;}\n
\t\t\t\tif (attrVal != "") {\n
\t\t\t\t\tif (attrVal.indexOf(\'pointer-events\') === 0) {continue;}\n
\t\t\t\t\tif (attr.localName === "class" \046\046 attrVal.indexOf(\'se_\') === 0) {continue;}\n
\t\t\t\t\tout.push(" "); \n
\t\t\t\t\tif (attr.localName === \'d\') {attrVal = pathActions.convertPath(elem, true);}\n
\t\t\t\t\tif (!isNaN(attrVal)) {\n
\t\t\t\t\t\tattrVal = svgedit.units.shortFloat(attrVal);\n
\t\t\t\t\t} else if (unit_re.test(attrVal)) {\n
\t\t\t\t\t\tattrVal = svgedit.units.shortFloat(attrVal) + unit;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\t// Embed images when saving \n
\t\t\t\t\tif (save_options.apply\n
\t\t\t\t\t\t\046\046 elem.nodeName === \'image\' \n
\t\t\t\t\t\t\046\046 attr.localName === \'href\'\n
\t\t\t\t\t\t\046\046 save_options.images\n
\t\t\t\t\t\t\046\046 save_options.images === \'embed\') \n
\t\t\t\t\t{\n
\t\t\t\t\t\tvar img = encodableImages[attrVal];\n
\t\t\t\t\t\tif (img) {attrVal = img;}\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\t// map various namespaces to our fixed namespace prefixes\n
\t\t\t\t\t// (the default xmlns attribute itself does not get a prefix)\n
\t\t\t\t\tif (!attr.namespaceURI || attr.namespaceURI == NS.SVG || nsMap[attr.namespaceURI]) {\n
\t\t\t\t\t\tout.push(attr.nodeName); out.push("=\\"");\n
\t\t\t\t\t\tout.push(attrVal); out.push("\\"");\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\tif (elem.hasChildNodes()) {\n
\t\t\tout.push("\076");\n
\t\t\tindent++;\n
\t\t\tvar bOneLine = false;\n
\t\t\t\n
\t\t\tfor (i = 0; i \074 childs.length; i++) {\n
\t\t\t\tvar child = childs.item(i);\n
\t\t\t\tswitch(child.nodeType) {\n
\t\t\t\tcase 1: // element node\n
\t\t\t\t\tout.push("\\n");\n
\t\t\t\t\tout.push(this.svgToString(childs.item(i), indent));\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase 3: // text node\n
\t\t\t\t\tvar str = child.nodeValue.replace(/^\\s+|\\s+$/g, "");\n
\t\t\t\t\tif (str != "") {\n
\t\t\t\t\t\tbOneLine = true;\n
\t\t\t\t\t\tout.push(String(toXml(str)));\n
\t\t\t\t\t}\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase 4: // cdata node\n
\t\t\t\t\tout.push("\\n");\n
\t\t\t\t\tout.push(new Array(indent+1).join(" "));\n
\t\t\t\t\tout.push("\074![CDATA[");\n
\t\t\t\t\tout.push(child.nodeValue);\n
\t\t\t\t\tout.push("]]\076");\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase 8: // comment\n
\t\t\t\t\tout.push("\\n");\n
\t\t\t\t\tout.push(new Array(indent+1).join(" "));\n
\t\t\t\t\tout.push("\074!--");\n
\t\t\t\t\tout.push(child.data);\n
\t\t\t\t\tout.push("--\076");\n
\t\t\t\t\tbreak;\n
\t\t\t\t} // switch on node type\n
\t\t\t}\n
\t\t\tindent--;\n
\t\t\tif (!bOneLine) {\n
\t\t\t\tout.push("\\n");\n
\t\t\t\tfor (i = 0; i \074 indent; i++) {out.push(\' \');}\n
\t\t\t}\n
\t\t\tout.push("\074/"); out.push(elem.nodeName); out.push("\076");\n
\t\t} else {\n
\t\t\tout.push("/\076");\n
\t\t}\n
\t}\n
\treturn out.join(\'\');\n
}; // end svgToString()\n
\n
// Function: embedImage\n
// Converts a given image file to a data URL when possible, then runs a given callback\n
//\n
// Parameters: \n
// val - String with the path/URL of the image\n
// callback - Optional function to run when image data is found, supplies the\n
// result (data URL or false) as first parameter.\n
this.embedImage = function(val, callback) {\n
\t// load in the image and once it\'s loaded, get the dimensions\n
\t$(new Image()).load(function() {\n
\t\t// create a canvas the same size as the raster image\n
\t\tvar canvas = document.createElement("canvas");\n
\t\tcanvas.width = this.width;\n
\t\tcanvas.height = this.height;\n
\t\t// load the raster image into the canvas\n
\t\tcanvas.getContext("2d").drawImage(this, 0, 0);\n
\t\t// retrieve the data: URL\n
\t\ttry {\n
\t\t\tvar urldata = \';svgedit_url=\' + encodeURIComponent(val);\n
\t\t\turldata = canvas.toDataURL().replace(\';base64\', urldata+\';base64\');\n
\t\t\tencodableImages[val] = urldata;\n
\t\t} catch(e) {\n
\t\t\tencodableImages[val] = false;\n
\t\t}\n
\t\tlast_good_img_url = val;\n
\t\tif (callback) {callback(encodableImages[val]);}\n
\t}).attr(\'src\', val);\n
};\n
\n
// Function: setGoodImage\n
// Sets a given URL to be a "last good image" URL\n
this.setGoodImage = function(val) {\n
\tlast_good_img_url = val;\n
};\n
\n
this.open = function() {\n
\t// Nothing by default, handled by optional widget/extension\n
};\n
\n
// Function: save\n
// Serializes the current drawing into SVG XML text and returns it to the \'saved\' handler.\n
// This function also includes the XML prolog. Clients of the SvgCanvas bind their save\n
// function to the \'saved\' event.\n
//\n
// Returns: \n
// Nothing\n
this.save = function(opts) {\n
\t// remove the selected outline before serializing\n
\tclearSelection();\n
\t// Update save options if provided\n
\tif (opts) {$.extend(save_options, opts);}\n
\tsave_options.apply = true;\n
\t\n
\t// no need for doctype, see http://jwatt.org/svg/authoring/#doctype-declaration\n
\tvar str = this.svgCanvasToString();\n
\tcall("saved", str);\n
};\n
\n
// Function: rasterExport\n
// Generates a Data URL based on the current image, then calls "exported" \n
// with an object including the string, image information, and any issues found\n
this.rasterExport = function(imgType, quality) {\n
\tvar mimeType = \'image/\' + imgType.toLowerCase();\n
\n
\t// remove the selected outline before serializing\n
\tclearSelection();\n
\t\n
\t// Check for known CanVG issues \n
\tvar issues = [];\n
\t\n
\t// Selector and notice\n
\tvar issue_list = {\n
\t\t\'feGaussianBlur\': uiStrings.exportNoBlur,\n
\t\t\'foreignObject\': uiStrings.exportNoforeignObject,\n
\t\t\'[stroke-dasharray]\': uiStrings.exportNoDashArray\n
\t};\n
\tvar content = $(svgcontent);\n
\t\n
\t// Add font/text check if Canvas Text API is not implemented\n
\tif (!("font" in $(\'\074canvas\076\')[0].getContext(\'2d\'))) {\n
\t\tissue_list.text = uiStrings.exportNoText;\n
\t}\n
\t\n
\t$.each(issue_list, function(sel, descr) {\n
\t\tif (content.find(sel).length) {\n
\t\t\tissues.push(descr);\n
\t\t}\n
\t});\n
\n
\tvar str = this.svgCanvasToString();\n
\tcall("exported", {svg: str, issues: issues, type: imgType, mimeType: mimeType, quality: quality});\n
};\n
\n
// Function: getSvgString\n
// Returns the current drawing as raw SVG XML text.\n
//\n
// Returns:\n
// The current drawing as raw SVG XML text.\n
this.getSvgString = function() {\n
\tsave_options.apply = false;\n
\treturn this.svgCanvasToString();\n
};\n
\n
// Function: randomizeIds\n
// This function determines whether to use a nonce in the prefix, when\n
// generating IDs for future documents in SVG-Edit.\n
// \n
// Parameters:\n
// an optional boolean, which, if true, adds a nonce to the prefix. Thus\n
// svgCanvas.randomizeIds() \074==\076 svgCanvas.randomizeIds(true)\n
//\n
// if you\'re controlling SVG-Edit externally, and want randomized IDs, call\n
// this BEFORE calling svgCanvas.setSvgString\n
//\n
this.randomizeIds = function(enableRandomization) {\n
\tif (arguments.length \076 0 \046\046 enableRandomization == false) {\n
\t\tsvgedit.draw.randomizeIds(false, getCurrentDrawing());\n
\t} else {\n
\t\tsvgedit.draw.randomizeIds(true, getCurrentDrawing());\n
\t}\n
};\n
\n
// Function: uniquifyElems\n
// Ensure each element has a unique ID\n
//\n
// Parameters:\n
// g - The parent element of the tree to give unique IDs\n
var uniquifyElems = this.uniquifyElems = function(g) {\n
\tvar ids = {};\n
\t// TODO: Handle markers and connectors. These are not yet re-identified properly\n
\t// as their referring elements do not get remapped.\n
\t//\n
\t// \074marker id=\'se_marker_end_svg_7\'/\076\n
\t// \074polyline id=\'svg_7\' se:connector=\'svg_1 svg_6\' marker-end=\'url(#se_marker_end_svg_7)\'/\076\n
\t// \n
\t// Problem #1: if svg_1 gets renamed, we do not update the polyline\'s se:connector attribute\n
\t// Problem #2: if the polyline svg_7 gets renamed, we do not update the marker id nor the polyline\'s marker-end attribute\n
\tvar ref_elems = ["filter", "linearGradient", "pattern",\t"radialGradient", "symbol", "textPath", "use"];\n
\t\n
\tsvgedit.utilities.walkTree(g, function(n) {\n
\t\t// if it\'s an element node\n
\t\tif (n.nodeType == 1) {\n
\t\t\t// and the element has an ID\n
\t\t\tif (n.id) {\n
\t\t\t\t// and we haven\'t tracked this ID yet\n
\t\t\t\tif (!(n.id in ids)) {\n
\t\t\t\t\t// add this id to our map\n
\t\t\t\t\tids[n.id] = {elem:null, attrs:[], hrefs:[]};\n
\t\t\t\t}\n
\t\t\t\tids[n.id].elem = n;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// now search for all attributes on this element that might refer\n
\t\t\t// to other elements\n
\t\t\t$.each(ref_attrs, function(i, attr) {\n
\t\t\t\tvar attrnode = n.getAttributeNode(attr);\n
\t\t\t\tif (attrnode) {\n
\t\t\t\t\t// the incoming file has been sanitized, so we should be able to safely just strip off the leading #\n
\t\t\t\t\tvar url = svgedit.utilities.getUrlFromAttr(attrnode.value),\n
\t\t\t\t\t\trefid = url ? url.substr(1) : null;\n
\t\t\t\t\tif (refid) {\n
\t\t\t\t\t\tif (!(refid in ids)) {\n
\t\t\t\t\t\t\t// add this id to our map\n
\t\t\t\t\t\t\tids[refid] = {elem:null, attrs:[], hrefs:[]};\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tids[refid].attrs.push(attrnode);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\t\n
\t\t\t// check xlink:href now\n
\t\t\tvar href = svgedit.utilities.getHref(n);\n
\t\t\t// TODO: what if an \074image\076 or \074a\076 element refers to an element internally?\n
\t\t\tif (href \046\046 ref_elems.indexOf(n.nodeName) \076= 0) {\n
\t\t\t\tvar refid = href.substr(1);\n
\t\t\t\tif (refid) {\n
\t\t\t\t\tif (!(refid in ids)) {\n
\t\t\t\t\t\t// add this id to our map\n
\t\t\t\t\t\tids[refid] = {elem:null, attrs:[], hrefs:[]};\n
\t\t\t\t\t}\n
\t\t\t\t\tids[refid].hrefs.push(n);\n
\t\t\t\t}\n
\t\t\t}\t\t\t\t\t\t\n
\t\t}\n
\t});\n
\t\n
\t// in ids, we now have a map of ids, elements and attributes, let\'s re-identify\n
\tvar oldid;\n
\tfor (oldid in ids) {\n
\t\tif (!oldid) {continue;}\n
\t\tvar elem = ids[oldid].elem;\n
\t\tif (elem) {\n
\t\t\tvar newid = getNextId();\n
\t\t\t\n
\t\t\t// assign element its new id\n
\t\t\telem.id = newid;\n
\t\t\t\n
\t\t\t// remap all url() attributes\n
\t\t\tvar attrs = ids[oldid].attrs;\n
\t\t\tvar j = attrs.length;\n
\t\t\twhile (j--) {\n
\t\t\t\tvar attr = attrs[j];\n
\t\t\t\tattr.ownerElement.setAttribute(attr.name, "url(#" + newid + ")");\n
\t\t\t}\n
\t\t\t\n
\t\t\t// remap all href attributes\n
\t\t\tvar hreffers = ids[oldid].hrefs;\n
\t\t\tvar k = hreffers.length;\n
\t\t\twhile (k--) {\n
\t\t\t\tvar hreffer = hreffers[k];\n
\t\t\t\tsvgedit.utilities.setHref(hreffer, "#"+newid);\n
\t\t\t}\n
\t\t}\n
\t}\n
};\n
\n
// Function setUseData\n
// Assigns reference data for each use element\n
var setUseData = this.setUseData = function(parent) {\n
\tvar elems = $(parent);\n
\t\n
\tif (parent.tagName !== \'use\') {\n
\t\telems = elems.find(\'use\');\n
\t}\n
\t\n
\telems.each(function() {\n
\t\tvar id = getHref(this).substr(1);\n
\t\tvar ref_elem = svgedit.utilities.getElem(id);\n
\t\tif (!ref_elem) {return;}\n
\t\t$(this).data(\'ref\', ref_elem);\n
\t\tif (ref_elem.tagName == \'symbol\' || ref_elem.tagName == \'svg\') {\n
\t\t\t$(this).data(\'symbol\', ref_elem).data(\'ref\', ref_elem);\n
\t\t}\n
\t});\n
};\n
\n
// Function convertGradients\n
// Converts gradients from userSpaceOnUse to objectBoundingBox\n
var convertGradients = this.convertGradients = function(elem) {\n
\tvar elems = $(elem).find(\'linearGradient, radialGradient\');\n
\tif (!elems.length \046\046 svgedit.browser.isWebkit()) {\n
\t\t// Bug in webkit prevents regular *Gradient selector search\n
\t\telems = $(elem).find(\'*\').filter(function() {\n
\t\t\treturn (this.tagName.indexOf(\'Gradient\') \076= 0);\n
\t\t});\n
\t}\n
\t\n
\telems.each(function() {\n
\t\tvar grad = this;\n
\t\tif ($(grad).attr(\'gradientUnits\') === \'userSpaceOnUse\') {\n
\t\t\t// TODO: Support more than one element with this ref by duplicating parent grad\n
\t\t\tvar elems = $(svgcontent).find(\'[fill="url(#\' + grad.id + \')"],[stroke="url(#\' + grad.id + \')"]\');\n
\t\t\tif (!elems.length) {return;}\n
\t\t\t\n
\t\t\t// get object\'s bounding box\n
\t\t\tvar bb = svgedit.utilities.getBBox(elems[0]);\n
\t\t\t\n
\t\t\t// This will occur if the element is inside a \074defs\076 or a \074symbol\076,\n
\t\t\t// in which we shouldn\'t need to convert anyway.\n
\t\t\tif (!bb) {return;}\n
\t\t\t\n
\t\t\tif (grad.tagName === \'linearGradient\') {\n
\t\t\t\tvar g_coords = $(grad).attr([\'x1\', \'y1\', \'x2\', \'y2\']);\n
\t\t\t\t\n
\t\t\t\t// If has transform, convert\n
\t\t\t\tvar tlist = grad.gradientTransform.baseVal;\n
\t\t\t\tif (tlist \046\046 tlist.numberOfItems \076 0) {\n
\t\t\t\t\tvar m = svgedit.math.transformListToTransform(tlist).matrix;\n
\t\t\t\t\tvar pt1 = svgedit.math.transformPoint(g_coords.x1, g_coords.y1, m);\n
\t\t\t\t\tvar pt2 = svgedit.math.transformPoint(g_coords.x2, g_coords.y2, m);\n
\t\t\t\t\t\n
\t\t\t\t\tg_coords.x1 = pt1.x;\n
\t\t\t\t\tg_coords.y1 = pt1.y;\n
\t\t\t\t\tg_coords.x2 = pt2.x;\n
\t\t\t\t\tg_coords.y2 = pt2.y;\n
\t\t\t\t\tgrad.removeAttribute(\'gradientTransform\');\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t$(grad).attr({\n
\t\t\t\t\tx1: (g_coords.x1 - bb.x) / bb.width,\n
\t\t\t\t\ty1: (g_coords.y1 - bb.y) / bb.height,\n
\t\t\t\t\tx2: (g_coords.x2 - bb.x) / bb.width,\n
\t\t\t\t\ty2: (g_coords.y2 - bb.y) / bb.height\n
\t\t\t\t});\n
\t\t\t\tgrad.removeAttribute(\'gradientUnits\');\n
\t\t\t}\n
\t\t\t// else {\n
\t\t\t\t// Note: radialGradient elements cannot be easily converted \n
\t\t\t\t// because userSpaceOnUse will keep circular gradients, while\n
\t\t\t\t// objectBoundingBox will x/y scale the gradient according to\n
\t\t\t\t// its bbox. \n
\t\t\t\t\n
\t\t\t\t// For now we\'ll do nothing, though we should probably have\n
\t\t\t\t// the gradient be updated as the element is moved, as \n
\t\t\t\t// inkscape/illustrator do.\n
\t\t\t\n
//\t\t\t\t\t\tvar g_coords = $(grad).attr([\'cx\', \'cy\', \'r\']);\n
//\t\t\t\t\t\t\n
//\t\t\t\t\t\t$(grad).attr({\n
//\t\t\t\t\t\t\tcx: (g_coords.cx - bb.x) / bb.width,\n
//\t\t\t\t\t\t\tcy: (g_coords.cy - bb.y) / bb.height,\n
//\t\t\t\t\t\t\tr: g_coords.r\n
//\t\t\t\t\t\t});\n
//\t\t\t\t\t\t\n
//\t\t\t\t\t\tgrad.removeAttribute(\'gradientUnits\');\n
\t\t\t// }\n
\t\t}\n
\t});\n
};\n
\n
// Function: convertToGroup\n
// Converts selected/given \074use\076 or child SVG element to a group\n
var convertToGroup = this.convertToGroup = function(elem) {\n
\tif (!elem) {\n
\t\telem = selectedElements[0];\n
\t}\n
\tvar $elem = $(elem);\n
\tvar batchCmd = new svgedit.history.BatchCommand();\n
\tvar ts;\n
\t\n
\tif ($elem.data(\'gsvg\')) {\n
\t\t// Use the gsvg as the new group\n
\t\tvar svg = elem.firstChild;\n
\t\tvar pt = $(svg).attr([\'x\', \'y\']);\n
\t\t\n
\t\t$(elem.firstChild.firstChild).unwrap();\n
\t\t$(elem).removeData(\'gsvg\');\n
\t\t\n
\t\tvar tlist = svgedit.transformlist.getTransformList(elem);\n
\t\tvar xform = svgroot.createSVGTransform();\n
\t\txform.setTranslate(pt.x, pt.y);\n
\t\ttlist.appendItem(xform);\n
\t\tsvgedit.recalculate.recalculateDimensions(elem);\n
\t\tcall("selected", [elem]);\n
\t} else if ($elem.data(\'symbol\')) {\n
\t\telem = $elem.data(\'symbol\');\n
\t\t\n
\t\tts = $elem.attr(\'transform\');\n
\t\tvar pos = $elem.attr([\'x\', \'y\']);\n
\n
\t\tvar vb = elem.getAttribute(\'viewBox\');\n
\t\t\n
\t\tif (vb) {\n
\t\t\tvar nums = vb.split(\' \');\n
\t\t\tpos.x -= +nums[0];\n
\t\t\tpos.y -= +nums[1];\n
\t\t}\n
\t\t\n
\t\t// Not ideal, but works\n
\t\tts += " translate(" + (pos.x || 0) + "," + (pos.y || 0) + ")";\n
\t\t\n
\t\tvar prev = $elem.prev();\n
\t\t\n
\t\t// Remove \074use\076 element\n
\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand($elem[0], $elem[0].nextSibling, $elem[0].parentNode));\n
\t\t$elem.remove();\n
\t\t\n
\t\t// See if other elements reference this symbol\n
\t\tvar has_more = $(svgcontent).find(\'use:data(symbol)\').length;\n
\t\t\t\n
\t\tvar g = svgdoc.createElementNS(NS.SVG, "g");\n
\t\tvar childs = elem.childNodes;\n
\t\t\n
\t\tvar i;\n
\t\tfor (i = 0; i \074 childs.length; i++) {\n
\t\t\tg.appendChild(childs[i].cloneNode(true));\n
\t\t}\n
\t\t\n
\t\t// Duplicate the gradients for Gecko, since they weren\'t included in the \074symbol\076\n
\t\tif (svgedit.browser.isGecko()) {\n
\t\t\tvar dupeGrads = $(svgedit.utilities.findDefs()).children(\'linearGradient,radialGradient,pattern\').clone();\n
\t\t\t$(g).append(dupeGrads);\n
\t\t}\n
\t\t\n
\t\tif (ts) {\n
\t\t\tg.setAttribute("transform", ts);\n
\t\t}\n
\t\t\n
\t\tvar parent = elem.parentNode;\n
\t\t\n
\t\tuniquifyElems(g);\n
\t\t\n
\t\t// Put the dupe gradients back into \074defs\076 (after uniquifying them)\n
\t\tif (svgedit.browser.isGecko()) {\n
\t\t\t$(findDefs()).append( $(g).find(\'linearGradient,radialGradient,pattern\') );\n
\t\t}\n
\t\n
\t\t// now give the g itself a new id\n
\t\tg.id = getNextId();\n
\t\t\n
\t\tprev.after(g);\n
\t\t\n
\t\tif (parent) {\n
\t\t\tif (!has_more) {\n
\t\t\t\t// remove symbol/svg element\n
\t\t\t\tvar nextSibling = elem.nextSibling;\n
\t\t\t\tparent.removeChild(elem);\n
\t\t\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(elem, nextSibling, parent));\n
\t\t\t}\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(g));\n
\t\t}\n
\t\t\n
\t\tsetUseData(g);\n
\t\t\n
\t\tif (svgedit.browser.isGecko()) {\n
\t\t\tconvertGradients(svgedit.utilities.findDefs());\n
\t\t} else {\n
\t\t\tconvertGradients(g);\n
\t\t}\n
\t\t\n
\t\t// recalculate dimensions on the top-level children so that unnecessary transforms\n
\t\t// are removed\n
\t\tsvgedit.utilities.walkTreePost(g, function(n){\n
\t\t\ttry {\n
\t\t\t\tsvgedit.recalculate.recalculateDimensions(n);\n
\t\t\t} catch(e) {\n
\t\t\t\tconsole.log(e);\n
\t\t\t}\n
\t\t});\n
\t\t\n
\t\t// Give ID for any visible element missing one\n
\t\t$(g).find(visElems).each(function() {\n
\t\t\tif (!this.id) {this.id = getNextId();}\n
\t\t});\n
\t\t\n
\t\tselectOnly([g]);\n
\t\t\n
\t\tvar cm = pushGroupProperties(g, true);\n
\t\tif (cm) {\n
\t\t\tbatchCmd.addSubCommand(cm);\n
\t\t}\n
\n
\t\taddCommandToHistory(batchCmd);\n
\t\t\n
\t} else {\n
\t\tconsole.log(\'Unexpected element to ungroup:\', elem);\n
\t}\n
};\n
\n
//\n
// Function: setSvgString\n
// This function sets the current drawing as the input SVG XML.\n
//\n
// Parameters:\n
// xmlString - The SVG as XML text.\n
//\n
// Returns:\n
// This function returns false if the set was unsuccessful, true otherwise.\n
this.setSvgString = function(xmlString) {\n
\ttry {\n
\t\t// convert string into XML document\n
\t\tvar newDoc = svgedit.utilities.text2xml(xmlString);\n
\n
\t\tthis.prepareSvg(newDoc);\n
\n
\t\tvar batchCmd = new svgedit.history.BatchCommand("Change Source");\n
\n
\t\t// remove old svg document\n
\t\tvar nextSibling = svgcontent.nextSibling;\n
\t\tvar oldzoom = svgroot.removeChild(svgcontent);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(oldzoom, nextSibling, svgroot));\n
\t\n
\t\t// set new svg document\n
\t\t// If DOM3 adoptNode() available, use it. Otherwise fall back to DOM2 importNode()\n
\t\tif (svgdoc.adoptNode) {\n
\t\t\tsvgcontent = svgdoc.adoptNode(newDoc.documentElement);\n
\t\t}\n
\t\telse {\n
\t\t\tsvgcontent = svgdoc.importNode(newDoc.documentElement, true);\n
\t\t}\n
\t\t\n
\t\tsvgroot.appendChild(svgcontent);\n
\t\tvar content = $(svgcontent);\n
\t\t\n
\t\tcanvas.current_drawing_ = new svgedit.draw.Drawing(svgcontent, idprefix);\n
\t\t\n
\t\t// retrieve or set the nonce\n
\t\tvar nonce = getCurrentDrawing().getNonce();\n
\t\tif (nonce) {\n
\t\t\tcall("setnonce", nonce);\n
\t\t} else {\n
\t\t\tcall("unsetnonce");\n
\t\t}\n
\t\t\n
\t\t// change image href vals if possible\n
\t\tcontent.find(\'image\').each(function() {\n
\t\t\tvar image = this;\n
\t\t\tpreventClickDefault(image);\n
\t\t\tvar val = getHref(this);\n
\t\t\tif (val) {\n
\t\t\t\tif (val.indexOf(\'data:\') === 0) {\n
\t\t\t\t\t// Check if an SVG-edit data URI\n
\t\t\t\t\tvar m = val.match(/svgedit_url=(.*?);/);\n
\t\t\t\t\tif (m) {\n
\t\t\t\t\t\tvar url = decodeURIComponent(m[1]);\n
\t\t\t\t\t\t$(new Image()).load(function () {\n
\t\t\t\t\t\t\timage.setAttributeNS(NS.XLINK, \'xlink:href\', url);\n
\t\t\t\t\t\t}).attr(\'src\', url);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t// Add to encodableImages if it loads\n
\t\t\t\tcanvas.embedImage(val);\n
\t\t\t}\n
\t\t});\n
\t\n
\t\t// Wrap child SVGs in group elements\n
\t\tcontent.find(\'svg\').each(function() {\n
\t\t\t// Skip if it\'s in a \074defs\076\n
\t\t\tif ($(this).closest(\'defs\').length) {return;}\n
\t\t\n
\t\t\tuniquifyElems(this);\n
\t\t\n
\t\t\t// Check if it already has a gsvg group\n
\t\t\tvar pa = this.parentNode;\n
\t\t\tif (pa.childNodes.length === 1 \046\046 pa.nodeName === \'g\') {\n
\t\t\t\t$(pa).data(\'gsvg\', this);\n
\t\t\t\tpa.id = pa.id || getNextId();\n
\t\t\t} else {\n
\t\t\t\tgroupSvgElem(this);\n
\t\t\t}\n
\t\t});\n
\t\t\n
\t\t// For Firefox: Put all paint elems in defs\n
\t\tif (svgedit.browser.isGecko()) {\n
\t\t\tcontent.find(\'linearGradient, radialGradient, pattern\').appendTo(svgedit.utilities.findDefs());\n
\t\t}\n
\n
\t\t// Set ref element for \074use\076 elements\n
\t\t\n
\t\t// TODO: This should also be done if the object is re-added through "redo"\n
\t\tsetUseData(content);\n
\t\t\n
\t\tconvertGradients(content[0]);\n
\t\t\n
\t\t// recalculate dimensions on the top-level children so that unnecessary transforms\n
\t\t// are removed\n
\t\tsvgedit.utilities.walkTreePost(svgcontent, function(n) {\n
\t\t\ttry {\n
\t\t\t\tsvgedit.recalculate.recalculateDimensions(n);\n
\t\t\t} catch(e) {\n
\t\t\t\tconsole.log(e);\n
\t\t\t}\n
\t\t});\n
\t\t\n
\t\tvar attrs = {\n
\t\t\tid: \'svgcontent\',\n
\t\t\toverflow: curConfig.show_outside_canvas ? \'visible\' : \'hidden\'\n
\t\t};\n
\t\t\n
\t\tvar percs = false;\n
\t\t\n
\t\t// determine proper size\n
\t\tif (content.attr("viewBox")) {\n
\t\t\tvar vb = content.attr("viewBox").split(\' \');\n
\t\t\tattrs.width = vb[2];\n
\t\t\tattrs.height = vb[3];\n
\t\t}\n
\t\t// handle content that doesn\'t have a viewBox\n
\t\telse {\n
\t\t\t$.each([\'width\', \'height\'], function(i, dim) {\n
\t\t\t\t// Set to 100 if not given\n
\t\t\t\tvar val = content.attr(dim);\n
\t\t\t\t\n
\t\t\t\tif (!val) {val = \'100%\';}\n
\t\t\t\t\n
\t\t\t\tif (String(val).substr(-1) === "%") {\n
\t\t\t\t\t// Use user units if percentage given\n
\t\t\t\t\tpercs = true;\n
\t\t\t\t} else {\n
\t\t\t\t\tattrs[dim] = svgedit.units.convertToNum(dim, val);\n
\t\t\t\t}\n
\t\t\t});\n
\t\t}\n
\t\t\n
\t\t// identify layers\n
\t\tidentifyLayers();\n
\t\t\n
\t\t// Give ID for any visible layer children missing one\n
\t\tcontent.children().find(visElems).each(function() {\n
\t\t\tif (!this.id) {this.id = getNextId();}\n
\t\t});\n
\t\t\n
\t\t// Percentage width/height, so let\'s base it on visible elements\n
\t\tif (percs) {\n
\t\t\tvar bb = getStrokedBBox();\n
\t\t\tattrs.width = bb.width + bb.x;\n
\t\t\tattrs.height = bb.height + bb.y;\n
\t\t}\n
\t\t\n
\t\t// Just in case negative numbers are given or \n
\t\t// result from the percs calculation\n
\t\tif (attrs.width \074= 0) {attrs.width = 100;}\n
\t\tif (attrs.height \074= 0) {attrs.height = 100;}\n
\t\t\n
\t\tcontent.attr(attrs);\n
\t\tthis.contentW = attrs.width;\n
\t\tthis.contentH = attrs.height;\n
\t\t\n
\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(svgcontent));\n
\t\t// update root to the correct size\n
\t\tvar changes = content.attr(["width", "height"]);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(svgroot, changes));\n
\t\t\n
\t\t// reset zoom\n
\t\tcurrent_zoom = 1;\n
\t\t\n
\t\t// reset transform lists\n
\t\tsvgedit.transformlist.resetListMap();\n
\t\tclearSelection();\n
\t\tsvgedit.path.clearData();\n
\t\tsvgroot.appendChild(selectorManager.selectorParentGroup);\n
\t\t\n
\t\taddCommandToHistory(batchCmd);\n
\t\tcall("changed", [svgcontent]);\n
\t} catch(e) {\n
\t\tconsole.log(e);\n
\t\treturn false;\n
\t}\n
\n
\treturn true;\n
};\n
\n
// Function: importSvgString\n
// This function imports the input SVG XML as a \074symbol\076 in the \074defs\076, then adds a\n
// \074use\076 to the current layer.\n
//\n
// Parameters:\n
// xmlString - The SVG as XML text.\n
//\n
// Returns:\n
// This function returns false if the import was unsuccessful, true otherwise.\n
// TODO: \n
// * properly handle if namespace is introduced by imported content (must add to svgcontent\n
// and update all prefixes in the imported node)\n
// * properly handle recalculating dimensions, recalculateDimensions() doesn\'t handle\n
// arbitrary transform lists, but makes some assumptions about how the transform list \n
// was obtained\n
// * import should happen in top-left of current zoomed viewport\t\n
this.importSvgString = function(xmlString) {\n
\tvar j, ts;\n
\ttry {\n
\t\t// Get unique ID\n
\t\tvar uid = svgedit.utilities.encode64(xmlString.length + xmlString).substr(0,32);\n
\t\t\n
\t\tvar useExisting = false;\n
\n
\t\t// Look for symbol and make sure symbol exists in image\n
\t\tif (import_ids[uid]) {\n
\t\t\tif ( $(import_ids[uid].symbol).parents(\'#svgroot\').length ) {\n
\t\t\t\tuseExisting = true;\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\tvar batchCmd = new svgedit.history.BatchCommand("Import SVG");\n
\t\tvar symbol;\n
\t\tif (useExisting) {\n
\t\t\tsymbol = import_ids[uid].symbol;\n
\t\t\tts = import_ids[uid].xform;\n
\t\t} else {\n
\t\t\t// convert string into XML document\n
\t\t\tvar newDoc = svgedit.utilities.text2xml(xmlString);\n
\t\n
\t\t\tthis.prepareSvg(newDoc);\n
\t\n
\t\t\t// import new svg document into our document\n
\t\t\tvar svg;\n
\t\t\t// If DOM3 adoptNode() available, use it. Otherwise fall back to DOM2 importNode()\n
\t\t\tif (svgdoc.adoptNode) {\n
\t\t\t\tsvg = svgdoc.adoptNode(newDoc.documentElement);\n
\t\t\t} else {\n
\t\t\t\tsvg = svgdoc.importNode(newDoc.documentElement, true);\n
\t\t\t}\n
\t\t\t\n
\t\t\tuniquifyElems(svg);\n
\t\t\t\n
\t\t\tvar innerw = svgedit.units.convertToNum(\'width\', svg.getAttribute("width")),\n
\t\t\t\tinnerh = svgedit.units.convertToNum(\'height\', svg.getAttribute("height")),\n
\t\t\t\tinnervb = svg.getAttribute("viewBox"),\n
\t\t\t\t// if no explicit viewbox, create one out of the width and height\n
\t\t\t\tvb = innervb ? innervb.split(" ") : [0, 0, innerw, innerh];\n
\t\t\tfor (j = 0; j \074 4; ++j) {\n
\t\t\t\tvb[j] = +(vb[j]);\n
\t\t\t}\n
\t\n
\t\t\t// TODO: properly handle preserveAspectRatio\n
\t\t\tvar canvasw = +svgcontent.getAttribute("width"),\n
\t\t\t\tcanvash = +svgcontent.getAttribute("height");\n
\t\t\t// imported content should be 1/3 of the canvas on its largest dimension\n
\t\t\t\n
\t\t\tif (innerh \076 innerw) {\n
\t\t\t\tts = "scale(" + (canvash/3)/vb[3] + ")";\n
\t\t\t} else {\n
\t\t\t\tts = "scale(" + (canvash/3)/vb[2] + ")";\n
\t\t\t}\n
\t\t\t\n
\t\t\t// Hack to make recalculateDimensions understand how to scale\n
\t\t\tts = "translate(0) " + ts + " translate(0)";\n
\t\t\t\n
\t\t\tsymbol = svgdoc.createElementNS(NS.SVG, "symbol");\n
\t\t\tvar defs = svgedit.utilities.findDefs();\n
\t\t\t\n
\t\t\tif (svgedit.browser.isGecko()) {\n
\t\t\t\t// Move all gradients into root for Firefox, workaround for this bug:\n
\t\t\t\t// https://bugzilla.mozilla.org/show_bug.cgi?id=353575\n
\t\t\t\t// TODO: Make this properly undo-able.\n
\t\t\t\t$(svg).find(\'linearGradient, radialGradient, pattern\').appendTo(defs);\n
\t\t\t}\n
\t\n
\t\t\twhile (svg.firstChild) {\n
\t\t\t\tvar first = svg.firstChild;\n
\t\t\t\tsymbol.appendChild(first);\n
\t\t\t}\n
\t\t\tvar attrs = svg.attributes;\n
\t\t\tvar i;\n
\t\t\tfor (i = 0; i \074 attrs.length; i++) {\n
\t\t\t\tvar attr = attrs[i];\n
\t\t\t\tsymbol.setAttribute(attr.nodeName, attr.nodeValue);\n
\t\t\t}\n
\t\t\tsymbol.id = getNextId();\n
\t\t\t\n
\t\t\t// Store data\n
\t\t\timport_ids[uid] = {\n
\t\t\t\tsymbol: symbol,\n
\t\t\t\txform: ts\n
\t\t\t};\n
\t\t\t\n
\t\t\tsvgedit.utilities.findDefs().appendChild(symbol);\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(symbol));\n
\t\t}\n
\t\t\n
\t\tvar use_el = svgdoc.createElementNS(NS.SVG, "use");\n
\t\tuse_el.id = getNextId();\n
\t\tsetHref(use_el, "#" + symbol.id);\n
\t\t\n
\t\t(current_group || getCurrentDrawing().getCurrentLayer()).appendChild(use_el);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(use_el));\n
\t\tclearSelection();\n
\t\t\n
\t\tuse_el.setAttribute("transform", ts);\n
\t\tsvgedit.recalculate.recalculateDimensions(use_el);\n
\t\t$(use_el).data(\'symbol\', symbol).data(\'ref\', symbol);\n
\t\taddToSelection([use_el]);\n
\t\t\n
\t\t// TODO: Find way to add this in a recalculateDimensions-parsable way\n
//\t\t\t\tif (vb[0] != 0 || vb[1] != 0)\n
//\t\t\t\t\tts = "translate(" + (-vb[0]) + "," + (-vb[1]) + ") " + ts;\n
\t\taddCommandToHistory(batchCmd);\n
\t\tcall("changed", [svgcontent]);\n
\n
\t} catch(e) {\n
\t\tconsole.log(e);\n
\t\treturn false;\n
\t}\n
\n
\treturn true;\n
};\n
\n
// TODO(codedread): Move all layer/context functions in draw.js\n
// Layer API Functions\n
\n
// Group: Layers\n
\n
// Function: identifyLayers\n
// Updates layer system\n
var identifyLayers = canvas.identifyLayers = function() {\n
\tleaveContext();\n
\tgetCurrentDrawing().identifyLayers();\n
};\n
\n
// Function: createLayer\n
// Creates a new top-level layer in the drawing with the given name, sets the current layer \n
// to it, and then clears the selection. This function then calls the \'changed\' handler.\n
// This is an undoable action.\n
//\n
// Parameters:\n
// name - The given name\n
this.createLayer = function(name) {\n
\tvar batchCmd = new svgedit.history.BatchCommand("Create Layer");\n
\tvar new_layer = getCurrentDrawing().createLayer(name);\n
\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(new_layer));\n
\taddCommandToHistory(batchCmd);\n
\tclearSelection();\n
\tcall("changed", [new_layer]);\n
};\n
\n
// Function: cloneLayer\n
// Creates a new top-level layer in the drawing with the given name, copies all the current layer\'s contents\n
// to it, and then clears the selection. This function then calls the \'changed\' handler.\n
// This is an undoable action.\n
//\n
// Parameters:\n
// name - The given name\n
this.cloneLayer = function(name) {\n
\tvar batchCmd = new svgedit.history.BatchCommand("Duplicate Layer");\n
\tvar new_layer = svgdoc.createElementNS(NS.SVG, "g");\n
\tvar layer_title = svgdoc.createElementNS(NS.SVG, "title");\n
\tlayer_title.textContent = name;\n
\tnew_layer.appendChild(layer_title);\n
\tvar current_layer = getCurrentDrawing().getCurrentLayer();\n
\t$(current_layer).after(new_layer);\n
\tvar childs = current_layer.childNodes;\n
\tvar i;\n
\tfor (i = 0; i \074 childs.length; i++) {\n
\t\tvar ch = childs[i];\n
\t\tif (ch.localName == \'title\') {continue;}\n
\t\tnew_layer.appendChild(copyElem(ch));\n
\t}\n
\t\n
\tclearSelection();\n
\tidentifyLayers();\n
\n
\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(new_layer));\n
\taddCommandToHistory(batchCmd);\n
\tcanvas.setCurrentLayer(name);\n
\tcall("changed", [new_layer]);\n
};\n
\n
// Function: deleteCurrentLayer\n
// Deletes the current layer from the drawing and then clears the selection. This function \n
// then calls the \'changed\' handler. This is an undoable action.\n
this.deleteCurrentLayer = function() {\n
\tvar current_layer = getCurrentDrawing().getCurrentLayer();\n
\tvar nextSibling = current_layer.nextSibling;\n
\tvar parent = current_layer.parentNode;\n
\tcurrent_layer = getCurrentDrawing().deleteCurrentLayer();\n
\tif (current_layer) {\n
\t\tvar batchCmd = new svgedit.history.BatchCommand("Delete Layer");\n
\t\t// store in our Undo History\n
\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(current_layer, nextSibling, parent));\n
\t\taddCommandToHistory(batchCmd);\n
\t\tclearSelection();\n
\t\tcall("changed", [parent]);\n
\t\treturn true;\n
\t}\n
\treturn false;\n
};\n
\n
// Function: setCurrentLayer\n
// Sets the current layer. If the name is not a valid layer name, then this function returns\n
// false. Otherwise it returns true. This is not an undo-able action.\n
//\n
// Parameters:\n
// name - the name of the layer you want to switch to.\n
//\n
// Returns:\n
// true if the current layer was switched, otherwise false\n
this.setCurrentLayer = function(name) {\n
\tvar result = getCurrentDrawing().setCurrentLayer(svgedit.utilities.toXml(name));\n
\tif (result) {\n
\t\tclearSelection();\n
\t}\n
\treturn result;\n
};\n
\n
// Function: renameCurrentLayer\n
// Renames the current layer. If the layer name is not valid (i.e. unique), then this function \n
// does nothing and returns false, otherwise it returns true. This is an undo-able action.\n
// \n
// Parameters:\n
// newname - the new name you want to give the current layer. This name must be unique \n
// among all layer names.\n
//\n
// Returns:\n
// true if the rename succeeded, false otherwise.\n
this.renameCurrentLayer = function(newname) {\n
\tvar i;\n
\tvar drawing = getCurrentDrawing();\n
\tif (drawing.current_layer) {\n
\t\tvar oldLayer = drawing.current_layer;\n
\t\t// setCurrentLayer will return false if the name doesn\'t already exist\n
\t\t// this means we are free to rename our oldLayer\n
\t\tif (!canvas.setCurrentLayer(newname)) {\n
\t\t\tvar batchCmd = new svgedit.history.BatchCommand("Rename Layer");\n
\t\t\t// find the index of the layer\n
\t\t\tfor (i = 0; i \074 drawing.getNumLayers(); ++i) {\n
\t\t\t\tif (drawing.all_layers[i][1] == oldLayer) {break;}\n
\t\t\t}\n
\t\t\tvar oldname = drawing.getLayerName(i);\n
\t\t\tdrawing.all_layers[i][0] = svgedit.utilities.toXml(newname);\n
\t\t\n
\t\t\t// now change the underlying title element contents\n
\t\t\tvar len = oldLayer.childNodes.length;\n
\t\t\tfor (i = 0; i \074 len; ++i) {\n
\t\t\t\tvar child = oldLayer.childNodes.item(i);\n
\t\t\t\t// found the \074title\076 element, now append all the\n
\t\t\t\tif (child \046\046 child.tagName == "title") {\n
\t\t\t\t\t// wipe out old name \n
\t\t\t\t\twhile (child.firstChild) { child.removeChild(child.firstChild); }\n
\t\t\t\t\tchild.textContent = newname;\n
\n
\t\t\t\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(child, {"#text":oldname}));\n
\t\t\t\t\taddCommandToHistory(batchCmd);\n
\t\t\t\t\tcall("changed", [oldLayer]);\n
\t\t\t\t\treturn true;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t\tdrawing.current_layer = oldLayer;\n
\t}\n
\treturn false;\n
};\n
\n
// Function: setCurrentLayerPosition\n
// Changes the position of the current layer to the new value. If the new index is not valid, \n
// this function does nothing and returns false, otherwise it returns true. This is an\n
// undo-able action.\n
//\n
// Parameters:\n
// newpos - The zero-based index of the new position of the layer. This should be between\n
// 0 and (number of layers - 1)\n
// \n
// Returns:\n
// true if the current layer position was changed, false otherwise.\n
this.setCurrentLayerPosition = function(newpos) {\n
\tvar oldpos, drawing = getCurrentDrawing();\n
\tif (drawing.current_layer \046\046 newpos \076= 0 \046\046 newpos \074 drawing.getNumLayers()) {\n
\t\tfor (oldpos = 0; oldpos \074 drawing.getNumLayers(); ++oldpos) {\n
\t\t\tif (drawing.all_layers[oldpos][1] == drawing.current_layer) {break;}\n
\t\t}\n
\t\t// some unknown error condition (current_layer not in all_layers)\n
\t\tif (oldpos == drawing.getNumLayers()) { return false; }\n
\t\t\n
\t\tif (oldpos != newpos) {\n
\t\t\t// if our new position is below us, we need to insert before the node after newpos\n
\t\t\tvar refLayer = null;\n
\t\t\tvar oldNextSibling = drawing.current_layer.nextSibling;\n
\t\t\tif (newpos \076 oldpos ) {\n
\t\t\t\tif (newpos \074 drawing.getNumLayers()-1) {\n
\t\t\t\t\trefLayer = drawing.all_layers[newpos+1][1];\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t// if our new position is above us, we need to insert before the node at newpos\n
\t\t\telse {\n
\t\t\t\trefLayer = drawing.all_layers[newpos][1];\n
\t\t\t}\n
\t\t\tsvgcontent.insertBefore(drawing.current_layer, refLayer);\n
\t\t\taddCommandToHistory(new svgedit.history.MoveElementCommand(drawing.current_layer, oldNextSibling, svgcontent));\n
\t\t\t\n
\t\t\tidentifyLayers();\n
\t\t\tcanvas.setCurrentLayer(drawing.getLayerName(newpos));\n
\t\t\t\n
\t\t\treturn true;\n
\t\t}\n
\t}\n
\t\n
\treturn false;\n
};\n
\n
// Function: setLayerVisibility\n
// Sets the visibility of the layer. If the layer name is not valid, this function return \n
// false, otherwise it returns true. This is an undo-able action.\n
//\n
// Parameters:\n
// layername - the name of the layer to change the visibility\n
// bVisible - true/false, whether the layer should be visible\n
//\n
// Returns:\n
// true if the layer\'s visibility was set, false otherwise\n
this.setLayerVisibility = function(layername, bVisible) {\n
\tvar drawing = getCurrentDrawing();\n
\tvar prevVisibility = drawing.getLayerVisibility(layername);\n
\tvar layer = drawing.setLayerVisibility(layername, bVisible);\n
\tif (layer) {\n
\t\tvar oldDisplay = prevVisibility ? \'inline\' : \'none\';\n
\t\taddCommandToHistory(new svgedit.history.ChangeElementCommand(layer, {\'display\':oldDisplay}, \'Layer Visibility\'));\n
\t} else {\n
\t\treturn false;\n
\t}\n
\t\n
\tif (layer == drawing.getCurrentLayer()) {\n
\t\tclearSelection();\n
\t\tpathActions.clear();\n
\t}\n
//\t\tcall("changed", [selected]);\t\n
\treturn true;\n
};\n
\n
// Function: moveSelectedToLayer\n
// Moves the selected elements to layername. If the name is not a valid layer name, then false \n
// is returned. Otherwise it returns true. This is an undo-able action.\n
//\n
// Parameters:\n
// layername - the name of the layer you want to which you want to move the selected elements\n
//\n
// Returns:\n
// true if the selected elements were moved to the layer, false otherwise.\n
this.moveSelectedToLayer = function(layername) {\n
\t// find the layer\n
\tvar i;\n
\tvar layer = null;\n
\tvar drawing = getCurrentDrawing();\n
\tfor (i = 0; i \074 drawing.getNumLayers(); ++i) {\n
\t\tif (drawing.getLayerName(i) == layername) {\n
\t\t\tlayer = drawing.all_layers[i][1];\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\tif (!layer) {return false;}\n
\t\n
\tvar batchCmd = new svgedit.history.BatchCommand("Move Elements to Layer");\n
\t\n
\t// loop for each selected element and move it\n
\tvar selElems = selectedElements;\n
\ti = selElems.length;\n
\twhile (i--) {\n
\t\tvar elem = selElems[i];\n
\t\tif (!elem) {continue;}\n
\t\tvar oldNextSibling = elem.nextSibling;\n
\t\t// TODO: this is pretty brittle!\n
\t\tvar oldLayer = elem.parentNode;\n
\t\tlayer.appendChild(elem);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.MoveElementCommand(elem, oldNextSibling, oldLayer));\n
\t}\n
\t\n
\taddCommandToHistory(batchCmd);\n
\t\n
\treturn true;\n
};\n
\n
this.mergeLayer = function(skipHistory) {\n
\tvar batchCmd = new svgedit.history.BatchCommand("Merge Layer");\n
\tvar drawing = getCurrentDrawing();\n
\tvar prev = $(drawing.current_layer).prev()[0];\n
\tif (!prev) {return;}\n
\tvar childs = drawing.current_layer.childNodes;\n
\tvar len = childs.length;\n
\tvar layerNextSibling = drawing.current_layer.nextSibling;\n
\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(drawing.current_layer, layerNextSibling, svgcontent));\n
\n
\twhile (drawing.current_layer.firstChild) {\n
\t\tvar ch = drawing.current_layer.firstChild;\n
\t\tif (ch.localName == \'title\') {\n
\t\t\tvar chNextSibling = ch.nextSibling;\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(ch, chNextSibling, drawing.current_layer));\n
\t\t\tdrawing.current_layer.removeChild(ch);\n
\t\t\tcontinue;\n
\t\t}\n
\t\tvar oldNextSibling = ch.nextSibling;\n
\t\tprev.appendChild(ch);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.MoveElementCommand(ch, oldNextSibling, drawing.current_layer));\n
\t}\n
\t\n
\t// Remove current layer\n
\tsvgcontent.removeChild(drawing.current_layer);\n
\t\n
\tif (!skipHistory) {\n
\t\tclearSelection();\n
\t\tidentifyLayers();\n
\n
\t\tcall("changed", [svgcontent]);\n
\t\t\n
\t\taddCommandToHistory(batchCmd);\n
\t}\n
\t\n
\tdrawing.current_layer = prev;\n
\treturn batchCmd;\n
};\n
\n
this.mergeAllLayers = function() {\n
\tvar batchCmd = new svgedit.history.BatchCommand("Merge all Layers");\n
\tvar drawing = getCurrentDrawing();\n
\tdrawing.current_layer = drawing.all_layers[drawing.getNumLayers()-1][1];\n
\twhile ($(svgcontent).children(\'g\').length \076 1) {\n
\t\tbatchCmd.addSubCommand(canvas.mergeLayer(true));\n
\t}\n
\t\n
\tclearSelection();\n
\tidentifyLayers();\n
\tcall("changed", [svgcontent]);\n
\taddCommandToHistory(batchCmd);\n
};\n
\n
// Function: leaveContext\n
// Return from a group context to the regular kind, make any previously\n
// disabled elements enabled again\n
var leaveContext = this.leaveContext = function() {\n
\tvar i, len = disabled_elems.length;\n
\tif (len) {\n
\t\tfor (i = 0; i \074 len; i++) {\n
\t\t\tvar elem = disabled_elems[i];\n
\t\t\tvar orig = elData(elem, \'orig_opac\');\n
\t\t\tif (orig !== 1) {\n
\t\t\t\telem.setAttribute(\'opacity\', orig);\n
\t\t\t} else {\n
\t\t\t\telem.removeAttribute(\'opacity\');\n
\t\t\t}\n
\t\t\telem.setAttribute(\'style\', \'pointer-events: inherit\');\n
\t\t}\n
\t\tdisabled_elems = [];\n
\t\tclearSelection(true);\n
\t\tcall("contextset", null);\n
\t}\n
\tcurrent_group = null;\n
};\n
\n
// Function: setContext\n
// Set the current context (for in-group editing)\n
var setContext = this.setContext = function(elem) {\n
\tleaveContext();\n
\tif (typeof elem === \'string\') {\n
\t\telem = svgedit.utilities.getElem(elem);\n
\t}\n
\n
\t// Edit inside this group\n
\tcurrent_group = elem;\n
\t\n
\t// Disable other elements\n
\t$(elem).parentsUntil(\'#svgcontent\').andSelf().siblings().each(function() {\n
\t\tvar opac = this.getAttribute(\'opacity\') || 1;\n
\t\t// Store the original\'s opacity\n
\t\telData(this, \'orig_opac\', opac);\n
\t\tthis.setAttribute(\'opacity\', opac * 0.33);\n
\t\tthis.setAttribute(\'style\', \'pointer-events: none\');\n
\t\tdisabled_elems.push(this);\n
\t});\n
\n
\tclearSelection();\n
\tcall("contextset", current_group);\n
};\n
\n
// Group: Document functions\n
\n
// Function: clear\n
// Clears the current document. This is not an undoable action.\n
this.clear = function() {\n
\tpathActions.clear();\n
\n
\tclearSelection();\n
\n
\t// clear the svgcontent node\n
\tcanvas.clearSvgContentElement();\n
\n
\t// create new document\n
\tcanvas.current_drawing_ = new svgedit.draw.Drawing(svgcontent);\n
\n
\t// create empty first layer\n
\tcanvas.createLayer("Layer 1");\n
\t\n
\t// clear the undo stack\n
\tcanvas.undoMgr.resetUndoStack();\n
\n
\t// reset the selector manager\n
\tselectorManager.initGroup();\n
\n
\t// reset the rubber band box\n
\trubberBox = selectorManager.getRubberBandBox();\n
\n
\tcall("cleared");\n
};\n
\n
// Function: linkControlPoints\n
// Alias function\n
this.linkControlPoints = pathActions.linkControlPoints;\n
\n
// Function: getContentElem\n
// Returns the content DOM element\n
this.getContentElem = function() { return svgcontent; };\n
\n
// Function: getRootElem\n
// Returns the root DOM element\n
this.getRootElem = function() { return svgroot; };\n
\n
// Function: getSelectedElems\n
// Returns the array with selected DOM elements\n
this.getSelectedElems = function() { return selectedElements; };\n
\n
// Function: getResolution\n
// Returns the current dimensions and zoom level in an object\n
var getResolution = this.getResolution = function() {\n
//\t\tvar vb = svgcontent.getAttribute("viewBox").split(\' \');\n
//\t\treturn {\'w\':vb[2], \'h\':vb[3], \'zoom\': current_zoom};\n
\t\n
\tvar width = svgcontent.getAttribute("width")/current_zoom;\n
\tvar height = svgcontent.getAttribute("height")/current_zoom;\n
\t\n
\treturn {\n
\t\t\'w\': width,\n
\t\t\'h\': height,\n
\t\t\'zoom\': current_zoom\n
\t};\n
};\n
\n
// Function: getZoom\n
// Returns the current zoom level\n
this.getZoom = function(){return current_zoom;};\n
\n
// Function: getVersion\n
// Returns a string which describes the revision number of SvgCanvas.\n
this.getVersion = function() {\n
\treturn "svgcanvas.js ($Rev: 2705 $)";\n
};\n
\n
// Function: setUiStrings\n
// Update interface strings with given values\n
//\n
// Parameters:\n
// strs - Object with strings (see uiStrings for examples)\n
this.setUiStrings = function(strs) {\n
\t$.extend(uiStrings, strs.notification);\n
};\n
\n
// Function: setConfig\n
// Update configuration options with given values\n
//\n
// Parameters:\n
// opts - Object with options (see curConfig for examples)\n
this.setConfig = function(opts) {\n
\t$.extend(c</string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAQ=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="4" aka="AAAAAAAAAAQ=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

urConfig, opts);\n
};\n
\n
// Function: getTitle\n
// Returns the current group/SVG\'s title contents\n
this.getTitle = function(elem) {\n
\tvar i;\n
\telem = elem || selectedElements[0];\n
\tif (!elem) {return;}\n
\telem = $(elem).data(\'gsvg\') || $(elem).data(\'symbol\') || elem;\n
\tvar childs = elem.childNodes;\n
\tfor (i = 0; i < childs.length; i++) {\n
\t\tif (childs[i].nodeName == \'title\') {\n
\t\t\treturn childs[i].textContent;\n
\t\t}\n
\t}\n
\treturn \'\';\n
};\n
\n
// Function: setGroupTitle\n
// Sets the group/SVG\'s title content\n
// TODO: Combine this with setDocumentTitle\n
this.setGroupTitle = function(val) {\n
\tvar elem = selectedElements[0];\n
\telem = $(elem).data(\'gsvg\') || elem;\n
\t\n
\tvar ts = $(elem).children(\'title\');\n
\t\n
\tvar batchCmd = new svgedit.history.BatchCommand("Set Label");\n
\t\n
\tif (!val.length) {\n
\t\t// Remove title element\n
\t\tvar tsNextSibling = ts.nextSibling;\n
\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(ts[0], tsNextSibling, elem));\n
\t\tts.remove();\n
\t} else if (ts.length) {\n
\t\t// Change title contents\n
\t\tvar title = ts[0];\n
\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(title, {\'#text\': title.textContent}));\n
\t\ttitle.textContent = val;\n
\t} else {\n
\t\t// Add title element\n
\t\ttitle = svgdoc.createElementNS(NS.SVG, "title");\n
\t\ttitle.textContent = val;\n
\t\t$(elem).prepend(title);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(title));\n
\t}\n
\n
\taddCommandToHistory(batchCmd);\n
};\n
\n
// Function: getDocumentTitle\n
// Returns the current document title or an empty string if not found\n
this.getDocumentTitle = function() {\n
\treturn canvas.getTitle(svgcontent);\n
};\n
\n
// Function: setDocumentTitle\n
// Adds/updates a title element for the document with the given name.\n
// This is an undoable action\n
//\n
// Parameters:\n
// newtitle - String with the new title\n
this.setDocumentTitle = function(newtitle) {\n
\tvar i;\n
\tvar childs = svgcontent.childNodes, doc_title = false, old_title = \'\';\n
\t\n
\tvar batchCmd = new svgedit.history.BatchCommand("Change Image Title");\n
\t\n
\tfor (i = 0; i < childs.length; i++) {\n
\t\tif (childs[i].nodeName == \'title\') {\n
\t\t\tdoc_title = childs[i];\n
\t\t\told_title = doc_title.textContent;\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\tif (!doc_title) {\n
\t\tdoc_title = svgdoc.createElementNS(NS.SVG, "title");\n
\t\tsvgcontent.insertBefore(doc_title, svgcontent.firstChild);\n
\t} \n
\t\n
\tif (newtitle.length) {\n
\t\tdoc_title.textContent = newtitle;\n
\t} else {\n
\t\t// No title given, so element is not necessary\n
\t\tdoc_title.parentNode.removeChild(doc_title);\n
\t}\n
\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(doc_title, {\'#text\': old_title}));\n
\taddCommandToHistory(batchCmd);\n
};\n
\n
// Function: getEditorNS\n
// Returns the editor\'s namespace URL, optionally adds it to root element\n
//\n
// Parameters:\n
// add - Boolean to indicate whether or not to add the namespace value\n
this.getEditorNS = function(add) {\n
\tif (add) {\n
\t\tsvgcontent.setAttribute(\'xmlns:se\', NS.SE);\n
\t}\n
\treturn NS.SE;\n
};\n
\n
// Function: setResolution\n
// Changes the document\'s dimensions to the given size\n
//\n
// Parameters: \n
// x - Number with the width of the new dimensions in user units. \n
// Can also be the string "fit" to indicate "fit to content"\n
// y - Number with the height of the new dimensions in user units. \n
//\n
// Returns:\n
// Boolean to indicate if resolution change was succesful. \n
// It will fail on "fit to content" option with no content to fit to.\n
this.setResolution = function(x, y) {\n
\tvar res = getResolution();\n
\tvar w = res.w, h = res.h;\n
\tvar batchCmd;\n
\n
\tif (x == \'fit\') {\n
\t\t// Get bounding box\n
\t\tvar bbox = getStrokedBBox();\n
\t\t\n
\t\tif (bbox) {\n
\t\t\tbatchCmd = new svgedit.history.BatchCommand("Fit Canvas to Content");\n
\t\t\tvar visEls = getVisibleElements();\n
\t\t\taddToSelection(visEls);\n
\t\t\tvar dx = [], dy = [];\n
\t\t\t$.each(visEls, function(i, item) {\n
\t\t\t\tdx.push(bbox.x*-1);\n
\t\t\t\tdy.push(bbox.y*-1);\n
\t\t\t});\n
\t\t\t\n
\t\t\tvar cmd = canvas.moveSelectedElements(dx, dy, true);\n
\t\t\tbatchCmd.addSubCommand(cmd);\n
\t\t\tclearSelection();\n
\t\t\t\n
\t\t\tx = Math.round(bbox.width);\n
\t\t\ty = Math.round(bbox.height);\n
\t\t} else {\n
\t\t\treturn false;\n
\t\t}\n
\t}\n
\tif (x != w || y != h) {\n
\t\tvar handle = svgroot.suspendRedraw(1000);\n
\t\tif (!batchCmd) {\n
\t\t\tbatchCmd = new svgedit.history.BatchCommand("Change Image Dimensions");\n
\t\t}\n
\n
\t\tx = svgedit.units.convertToNum(\'width\', x);\n
\t\ty = svgedit.units.convertToNum(\'height\', y);\n
\t\t\n
\t\tsvgcontent.setAttribute(\'width\', x);\n
\t\tsvgcontent.setAttribute(\'height\', y);\n
\t\t\n
\t\tthis.contentW = x;\n
\t\tthis.contentH = y;\n
\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(svgcontent, {"width":w, "height":h}));\n
\n
\t\tsvgcontent.setAttribute("viewBox", [0, 0, x/current_zoom, y/current_zoom].join(\' \'));\n
\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(svgcontent, {"viewBox": ["0 0", w, h].join(\' \')}));\n
\t\n
\t\taddCommandToHistory(batchCmd);\n
\t\tsvgroot.unsuspendRedraw(handle);\n
\t\tcall("changed", [svgcontent]);\n
\t}\n
\treturn true;\n
};\n
\n
// Function: getOffset\n
// Returns an object with x, y values indicating the svgcontent element\'s\n
// position in the editor\'s canvas.\n
this.getOffset = function() {\n
\treturn $(svgcontent).attr([\'x\', \'y\']);\n
};\n
\n
// Function: setBBoxZoom\n
// Sets the zoom level on the canvas-side based on the given value\n
// \n
// Parameters:\n
// val - Bounding box object to zoom to or string indicating zoom option \n
// editor_w - Integer with the editor\'s workarea box\'s width\n
// editor_h - Integer with the editor\'s workarea box\'s height\n
this.setBBoxZoom = function(val, editor_w, editor_h) {\n
\tvar spacer = 0.85;\n
\tvar bb;\n
\tvar calcZoom = function(bb) {\n
\t\tif (!bb) {return false;}\n
\t\tvar w_zoom = Math.round((editor_w / bb.width)*100 * spacer)/100;\n
\t\tvar h_zoom = Math.round((editor_h / bb.height)*100 * spacer)/100;\t\n
\t\tvar zoomlevel = Math.min(w_zoom, h_zoom);\n
\t\tcanvas.setZoom(zoomlevel);\n
\t\treturn {\'zoom\': zoomlevel, \'bbox\': bb};\n
\t};\n
\t\n
\tif (typeof val == \'object\') {\n
\t\tbb = val;\n
\t\tif (bb.width == 0 || bb.height == 0) {\n
\t\t\tvar newzoom = bb.zoom ? bb.zoom : current_zoom * bb.factor;\n
\t\t\tcanvas.setZoom(newzoom);\n
\t\t\treturn {\'zoom\': current_zoom, \'bbox\': bb};\n
\t\t}\n
\t\treturn calcZoom(bb);\n
\t}\n
\n
\tswitch (val) {\n
\t\tcase \'selection\':\n
\t\t\tif (!selectedElements[0]) {return;}\n
\t\t\tvar sel_elems = $.map(selectedElements, function(n){ if (n) {return n;} });\n
\t\t\tbb = getStrokedBBox(sel_elems);\n
\t\t\tbreak;\n
\t\tcase \'canvas\':\n
\t\t\tvar res = getResolution();\n
\t\t\tspacer = 0.95;\n
\t\t\tbb = {width:res.w, height:res.h , x:0, y:0};\n
\t\t\tbreak;\n
\t\tcase \'content\':\n
\t\t\tbb = getStrokedBBox();\n
\t\t\tbreak;\n
\t\tcase \'layer\':\n
\t\t\tbb = getStrokedBBox(getVisibleElements(getCurrentDrawing().getCurrentLayer()));\n
\t\t\tbreak;\n
\t\tdefault:\n
\t\t\treturn;\n
\t}\n
\treturn calcZoom(bb);\n
};\n
\n
// Function: setZoom\n
// Sets the zoom to the given level\n
//\n
// Parameters:\n
// zoomlevel - Float indicating the zoom level to change to\n
this.setZoom = function(zoomlevel) {\n
\tvar res = getResolution();\n
\tsvgcontent.setAttribute("viewBox", "0 0 " + res.w/zoomlevel + " " + res.h/zoomlevel);\n
\tcurrent_zoom = zoomlevel;\n
\t$.each(selectedElements, function(i, elem) {\n
\t\tif (!elem) {return;}\n
\t\tselectorManager.requestSelector(elem).resize();\n
\t});\n
\tpathActions.zoomChange();\n
\trunExtensions("zoomChanged", zoomlevel);\n
};\n
\n
// Function: getMode\n
// Returns the current editor mode string\n
this.getMode = function() {\n
\treturn current_mode;\n
};\n
\n
// Function: setMode\n
// Sets the editor\'s mode to the given string\n
//\n
// Parameters:\n
// name - String with the new mode to change to\n
this.setMode = function(name) {\n
\tpathActions.clear(true);\n
\ttextActions.clear();\n
\tcur_properties = (selectedElements[0] && selectedElements[0].nodeName == \'text\') ? cur_text : cur_shape;\n
\tcurrent_mode = name;\n
};\n
\n
// Group: Element Styling\n
\n
// Function: getColor\n
// Returns the current fill/stroke option\n
this.getColor = function(type) {\n
\treturn cur_properties[type];\n
};\n
\n
// Function: setColor\n
// Change the current stroke/fill color/gradient value\n
// \n
// Parameters:\n
// type - String indicating fill or stroke\n
// val - The value to set the stroke attribute to\n
// preventUndo - Boolean indicating whether or not this should be and undoable option\n
this.setColor = function(type, val, preventUndo) {\n
\tcur_shape[type] = val;\n
\tcur_properties[type + \'_paint\'] = {type:"solidColor"};\n
\tvar elems = [];\n
\tfunction addNonG (e) {\n
\t\tif (e.nodeName != "g") {\n
\t\t\telems.push(e);\n
\t\t}\n
\t}\n
\tvar i = selectedElements.length;\n
\twhile (i--) {\n
\t\tvar elem = selectedElements[i];\n
\t\tif (elem) {\n
\t\t\tif (elem.tagName == "g") {\n
\t\t\t\tsvgedit.utilities.walkTree(elem, addNonG);\n
\t\t\t} else {\n
\t\t\t\tif (type == \'fill\') {\n
\t\t\t\t\tif (elem.tagName != "polyline" && elem.tagName != "line") {\n
\t\t\t\t\t\telems.push(elem);\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\telems.push(elem);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
\tif (elems.length > 0) {\n
\t\tif (!preventUndo) {\n
\t\t\tchangeSelectedAttribute(type, val, elems);\n
\t\t\tcall("changed", elems);\n
\t\t} else {\n
\t\t\tchangeSelectedAttributeNoUndo(type, val, elems);\n
\t\t}\n
\t}\n
};\n
\n
// Function: setGradient\n
// Apply the current gradient to selected element\'s fill or stroke\n
//\n
// Parameters\n
// type - String indicating "fill" or "stroke" to apply to an element\n
var setGradient = this.setGradient = function(type) {\n
\tif (!cur_properties[type + \'_paint\'] || cur_properties[type + \'_paint\'].type == "solidColor") {return;}\n
\tvar grad = canvas[type + \'Grad\'];\n
\t// find out if there is a duplicate gradient already in the defs\n
\tvar duplicate_grad = findDuplicateGradient(grad);\n
\tvar defs = svgedit.utilities.findDefs();\n
\t// no duplicate found, so import gradient into defs\n
\tif (!duplicate_grad) {\n
\t\tvar orig_grad = grad;\n
\t\tgrad = defs.appendChild( svgdoc.importNode(grad, true) );\n
\t\t// get next id and set it on the grad\n
\t\tgrad.id = getNextId();\n
\t} else { // use existing gradient\n
\t\tgrad = duplicate_grad;\n
\t}\n
\tcanvas.setColor(type, "url(#" + grad.id + ")");\n
};\n
\n
// Function: findDuplicateGradient\n
// Check if exact gradient already exists\n
//\n
// Parameters:\n
// grad - The gradient DOM element to compare to others\n
//\n
// Returns:\n
// The existing gradient if found, null if not\n
var findDuplicateGradient = function(grad) {\n
\tvar defs = svgedit.utilities.findDefs();\n
\tvar existing_grads = $(defs).find("linearGradient, radialGradient");\n
\tvar i = existing_grads.length;\n
\tvar rad_attrs = [\'r\', \'cx\', \'cy\', \'fx\', \'fy\'];\n
\twhile (i--) {\n
\t\tvar og = existing_grads[i];\n
\t\tif (grad.tagName == "linearGradient") {\n
\t\t\tif (grad.getAttribute(\'x1\') != og.getAttribute(\'x1\') ||\n
\t\t\t\tgrad.getAttribute(\'y1\') != og.getAttribute(\'y1\') ||\n
\t\t\t\tgrad.getAttribute(\'x2\') != og.getAttribute(\'x2\') ||\n
\t\t\t\tgrad.getAttribute(\'y2\') != og.getAttribute(\'y2\')) \n
\t\t\t{\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\t\t} else {\n
\t\t\tvar grad_attrs = $(grad).attr(rad_attrs);\n
\t\t\tvar og_attrs = $(og).attr(rad_attrs);\n
\t\t\t\n
\t\t\tvar diff = false;\n
\t\t\t$.each(rad_attrs, function(i, attr) {\n
\t\t\t\tif (grad_attrs[attr] != og_attrs[attr]) {diff = true;}\n
\t\t\t});\n
\t\t\t\n
\t\t\tif (diff) {continue;}\n
\t\t}\n
\t\t\n
\t\t// else could be a duplicate, iterate through stops\n
\t\tvar stops = grad.getElementsByTagNameNS(NS.SVG, "stop");\n
\t\tvar ostops = og.getElementsByTagNameNS(NS.SVG, "stop");\n
\n
\t\tif (stops.length != ostops.length) {\n
\t\t\tcontinue;\n
\t\t}\n
\n
\t\tvar j = stops.length;\n
\t\twhile (j--) {\n
\t\t\tvar stop = stops[j];\n
\t\t\tvar ostop = ostops[j];\n
\n
\t\t\tif (stop.getAttribute(\'offset\') != ostop.getAttribute(\'offset\') ||\n
\t\t\t\tstop.getAttribute(\'stop-opacity\') != ostop.getAttribute(\'stop-opacity\') ||\n
\t\t\t\tstop.getAttribute(\'stop-color\') != ostop.getAttribute(\'stop-color\')) \n
\t\t\t{\n
\t\t\t\tbreak;\n
\t\t\t}\n
\t\t}\n
\n
\t\tif (j == -1) {\n
\t\t\treturn og;\n
\t\t}\n
\t} // for each gradient in defs\n
\n
\treturn null;\n
};\n
\n
function reorientGrads(elem, m) {\n
\tvar i;\n
\tvar bb = svgedit.utilities.getBBox(elem);\n
\tfor (i = 0; i < 2; i++) {\n
\t\tvar type = i === 0 ? \'fill\' : \'stroke\';\n
\t\tvar attrVal = elem.getAttribute(type);\n
\t\tif (attrVal && attrVal.indexOf(\'url(\') === 0) {\n
\t\t\tvar grad = svgedit.utilities.getRefElem(attrVal);\n
\t\t\tif (grad.tagName === \'linearGradient\') {\n
\t\t\t\tvar x1 = grad.getAttribute(\'x1\') || 0;\n
\t\t\t\tvar y1 = grad.getAttribute(\'y1\') || 0;\n
\t\t\t\tvar x2 = grad.getAttribute(\'x2\') || 1;\n
\t\t\t\tvar y2 = grad.getAttribute(\'y2\') || 0;\n
\t\t\t\t\n
\t\t\t\t// Convert to USOU points\n
\t\t\t\tx1 = (bb.width * x1) + bb.x;\n
\t\t\t\ty1 = (bb.height * y1) + bb.y;\n
\t\t\t\tx2 = (bb.width * x2) + bb.x;\n
\t\t\t\ty2 = (bb.height * y2) + bb.y;\n
\t\t\t\n
\t\t\t\t// Transform those points\n
\t\t\t\tvar pt1 = svgedit.math.transformPoint(x1, y1, m);\n
\t\t\t\tvar pt2 = svgedit.math.transformPoint(x2, y2, m);\n
\t\t\t\t\n
\t\t\t\t// Convert back to BB points\n
\t\t\t\tvar g_coords = {};\n
\t\t\t\t\n
\t\t\t\tg_coords.x1 = (pt1.x - bb.x) / bb.width;\n
\t\t\t\tg_coords.y1 = (pt1.y - bb.y) / bb.height;\n
\t\t\t\tg_coords.x2 = (pt2.x - bb.x) / bb.width;\n
\t\t\t\tg_coords.y2 = (pt2.y - bb.y) / bb.height;\n
\t\t\n
\t\t\t\tvar newgrad = grad.cloneNode(true);\n
\t\t\t\t$(newgrad).attr(g_coords);\n
\t\n
\t\t\t\tnewgrad.id = getNextId();\n
\t\t\t\tsvgedit.utilities.findDefs().appendChild(newgrad);\n
\t\t\t\telem.setAttribute(type, \'url(#\' + newgrad.id + \')\');\n
\t\t\t}\n
\t\t}\n
\t}\n
}\n
\n
// Function: setPaint\n
// Set a color/gradient to a fill/stroke\n
//\n
// Parameters:\n
// type - String with "fill" or "stroke"\n
// paint - The jGraduate paint object to apply\n
this.setPaint = function(type, paint) {\n
\t// make a copy\n
\tvar p = new $.jGraduate.Paint(paint);\n
\tthis.setPaintOpacity(type, p.alpha / 100, true);\n
\n
\t// now set the current paint object\n
\tcur_properties[type + \'_paint\'] = p;\n
\tswitch (p.type) {\n
\t\tcase \'solidColor\':\n
\t\t\tthis.setColor(type, p.solidColor != \'none\' ? \'#\' + p.solidColor : \'none\');\n
\t\t\tbreak;\n
\t\tcase \'linearGradient\':\n
\t\tcase \'radialGradient\':\n
\t\t\tcanvas[type + \'Grad\'] = p[p.type];\n
\t\t\tsetGradient(type);\n
\t\t\tbreak;\n
\t}\n
};\n
\n
// alias\n
this.setStrokePaint = function(paint) {\n
\tthis.setPaint(\'stroke\', paint);\n
};\n
\n
this.setFillPaint = function(paint) {\n
\tthis.setPaint(\'fill\', paint);\n
};\n
\n
// Function: getStrokeWidth\n
// Returns the current stroke-width value\n
this.getStrokeWidth = function() {\n
\treturn cur_properties.stroke_width;\n
};\n
\n
// Function: setStrokeWidth\n
// Sets the stroke width for the current selected elements\n
// When attempting to set a line\'s width to 0, this changes it to 1 instead\n
//\n
// Parameters:\n
// val - A Float indicating the new stroke width value\n
this.setStrokeWidth = function(val) {\n
\tif (val == 0 && [\'line\', \'path\'].indexOf(current_mode) >= 0) {\n
\t\tcanvas.setStrokeWidth(1);\n
\t\treturn;\n
\t}\n
\tcur_properties.stroke_width = val;\n
\n
\tvar elems = [];\n
\tfunction addNonG (e) {\n
\t\tif (e.nodeName != \'g\') {\n
\t\t\telems.push(e);\n
\t\t}\n
\t}\n
\tvar i = selectedElements.length;\n
\twhile (i--) {\n
\t\tvar elem = selectedElements[i];\n
\t\tif (elem) {\n
\t\t\tif (elem.tagName == "g") {\n
\t\t\t\tsvgedit.utilities.walkTree(elem, addNonG);\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\telems.push(elem);\n
\t\t\t}\n
\t\t}\n
\t}\n
\tif (elems.length > 0) {\n
\t\tchangeSelectedAttribute("stroke-width", val, elems);\n
\t\tcall("changed", selectedElements);\n
\t}\n
};\n
\n
// Function: setStrokeAttr\n
// Set the given stroke-related attribute the given value for selected elements\n
//\n
// Parameters:\n
// attr - String with the attribute name\n
// val - String or number with the attribute value\n
this.setStrokeAttr = function(attr, val) {\n
\tcur_shape[attr.replace(\'-\', \'_\')] = val;\n
\tvar elems = [];\n
\tfunction addNonG (e) {\n
\t\tif (e.nodeName != \'g\') {\n
\t\t\telems.push(e);\n
\t\t}\n
\t}\n
\tvar i = selectedElements.length;\n
\twhile (i--) {\n
\t\tvar elem = selectedElements[i];\n
\t\tif (elem) {\n
\t\t\tif (elem.tagName == "g") {\n
\t\t\t\tsvgedit.utilities.walkTree(elem, function(e){if (e.nodeName!="g") {elems.push(e);}});\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\telems.push(elem);\n
\t\t\t}\n
\t\t}\n
\t}\n
\tif (elems.length > 0) {\n
\t\tchangeSelectedAttribute(attr, val, elems);\n
\t\tcall("changed", selectedElements);\n
\t}\n
};\n
\n
// Function: getStyle\n
// Returns current style options\n
this.getStyle = function() {\n
\treturn cur_shape;\n
};\n
\n
// Function: getOpacity\n
// Returns the current opacity\n
this.getOpacity = function() {\n
\treturn cur_shape.opacity;\n
};\n
\n
// Function: setOpacity\n
// Sets the given opacity to the current selected elements\n
this.setOpacity = function(val) {\n
\tcur_shape.opacity = val;\n
\tchangeSelectedAttribute("opacity", val);\n
};\n
\n
// Function: getOpacity\n
// Returns the current fill opacity\n
this.getFillOpacity = function() {\n
\treturn cur_shape.fill_opacity;\n
};\n
\n
// Function: getStrokeOpacity\n
// Returns the current stroke opacity\n
this.getStrokeOpacity = function() {\n
\treturn cur_shape.stroke_opacity;\n
};\n
\n
// Function: setPaintOpacity\n
// Sets the current fill/stroke opacity\n
//\n
// Parameters:\n
// type - String with "fill" or "stroke"\n
// val - Float with the new opacity value\n
// preventUndo - Boolean indicating whether or not this should be an undoable action\n
this.setPaintOpacity = function(type, val, preventUndo) {\n
\tcur_shape[type + \'_opacity\'] = val;\n
\tif (!preventUndo) {\n
\t\tchangeSelectedAttribute(type + "-opacity", val);\n
\t}\n
\telse {\n
\t\tchangeSelectedAttributeNoUndo(type + "-opacity", val);\n
\t}\n
};\n
\n
// Function: getPaintOpacity\n
// Gets the current fill/stroke opacity\n
//\n
// Parameters:\n
// type - String with "fill" or "stroke"\n
this.getPaintOpacity = function(type) {\n
\treturn type === \'fill\' ? this.getFillOpacity() : this.getStrokeOpacity();\n
};\n
\n
// Function: getBlur\n
// Gets the stdDeviation blur value of the given element\n
//\n
// Parameters:\n
// elem - The element to check the blur value for\n
this.getBlur = function(elem) {\n
\tvar val = 0;\n
//\tvar elem = selectedElements[0];\n
\n
\tif (elem) {\n
\t\tvar filter_url = elem.getAttribute(\'filter\');\n
\t\tif (filter_url) {\n
\t\t\tvar blur = svgedit.utilities.getElem(elem.id + \'_blur\');\n
\t\t\tif (blur) {\n
\t\t\t\tval = blur.firstChild.getAttribute(\'stdDeviation\');\n
\t\t\t}\n
\t\t}\n
\t}\n
\treturn val;\n
};\n
\n
(function() {\n
\tvar cur_command = null;\n
\tvar filter = null;\n
\tvar filterHidden = false;\n
\t\n
\t// Function: setBlurNoUndo\n
\t// Sets the stdDeviation blur value on the selected element without being undoable\n
\t//\n
\t// Parameters:\n
\t// val - The new stdDeviation value\n
\tcanvas.setBlurNoUndo = function(val) {\n
\t\tif (!filter) {\n
\t\t\tcanvas.setBlur(val);\n
\t\t\treturn;\n
\t\t}\n
\t\tif (val === 0) {\n
\t\t\t// Don\'t change the StdDev, as that will hide the element.\n
\t\t\t// Instead, just remove the value for "filter"\n
\t\t\tchangeSelectedAttributeNoUndo("filter", "");\n
\t\t\tfilterHidden = true;\n
\t\t} else {\n
\t\t\tvar elem = selectedElements[0];\n
\t\t\tif (filterHidden) {\n
\t\t\t\tchangeSelectedAttributeNoUndo("filter", \'url(#\' + elem.id + \'_blur)\');\n
\t\t\t}\n
\t\t\tif (svgedit.browser.isWebkit()) {\n
\t\t\t\tconsole.log(\'e\', elem);\n
\t\t\t\telem.removeAttribute(\'filter\');\n
\t\t\t\telem.setAttribute(\'filter\', \'url(#\' + elem.id + \'_blur)\');\n
\t\t\t}\n
\t\t\tchangeSelectedAttributeNoUndo("stdDeviation", val, [filter.firstChild]);\n
\t\t\tcanvas.setBlurOffsets(filter, val);\n
\t\t}\n
\t};\n
\t\n
\tfunction finishChange() {\n
\t\tvar bCmd = canvas.undoMgr.finishUndoableChange();\n
\t\tcur_command.addSubCommand(bCmd);\n
\t\taddCommandToHistory(cur_command);\n
\t\tcur_command = null;\t\n
\t\tfilter = null;\n
\t}\n
\n
\t// Function: setBlurOffsets\n
\t// Sets the x, y, with, height values of the filter element in order to\n
\t// make the blur not be clipped. Removes them if not neeeded\n
\t//\n
\t// Parameters:\n
\t// filter - The filter DOM element to update\n
\t// stdDev - The standard deviation value on which to base the offset size\n
\tcanvas.setBlurOffsets = function(filter, stdDev) {\n
\t\tif (stdDev > 3) {\n
\t\t\t// TODO: Create algorithm here where size is based on expected blur\n
\t\t\tsvgedit.utilities.assignAttributes(filter, {\n
\t\t\t\tx: \'-50%\',\n
\t\t\t\ty: \'-50%\',\n
\t\t\t\twidth: \'200%\',\n
\t\t\t\theight: \'200%\'\n
\t\t\t}, 100);\n
\t\t} else {\n
\t\t\t// Removing these attributes hides text in Chrome (see Issue 579)\n
\t\t\tif (!svgedit.browser.isWebkit()) {\n
\t\t\t\tfilter.removeAttribute(\'x\');\n
\t\t\t\tfilter.removeAttribute(\'y\');\n
\t\t\t\tfilter.removeAttribute(\'width\');\n
\t\t\t\tfilter.removeAttribute(\'height\');\n
\t\t\t}\n
\t\t}\n
\t};\n
\n
\t// Function: setBlur \n
\t// Adds/updates the blur filter to the selected element\n
\t//\n
\t// Parameters:\n
\t// val - Float with the new stdDeviation blur value\n
\t// complete - Boolean indicating whether or not the action should be completed (to add to the undo manager)\n
\tcanvas.setBlur = function(val, complete) {\n
\t\tif (cur_command) {\n
\t\t\tfinishChange();\n
\t\t\treturn;\n
\t\t}\n
\t\n
\t\t// Looks for associated blur, creates one if not found\n
\t\tvar elem = selectedElements[0];\n
\t\tvar elem_id = elem.id;\n
\t\tfilter = svgedit.utilities.getElem(elem_id + \'_blur\');\n
\t\t\n
\t\tval -= 0;\n
\t\t\n
\t\tvar batchCmd = new svgedit.history.BatchCommand();\n
\t\t\n
\t\t// Blur found!\n
\t\tif (filter) {\n
\t\t\tif (val === 0) {\n
\t\t\t\tfilter = null;\n
\t\t\t}\n
\t\t} else {\n
\t\t\t// Not found, so create\n
\t\t\tvar newblur = addSvgElementFromJson({ "element": "feGaussianBlur",\n
\t\t\t\t"attr": {\n
\t\t\t\t\t"in": \'SourceGraphic\',\n
\t\t\t\t\t"stdDeviation": val\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\t\n
\t\t\tfilter = addSvgElementFromJson({ "element": "filter",\n
\t\t\t\t"attr": {\n
\t\t\t\t\t"id": elem_id + \'_blur\'\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\t\n
\t\t\tfilter.appendChild(newblur);\n
\t\t\tsvgedit.utilities.findDefs().appendChild(filter);\n
\t\t\t\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(filter));\n
\t\t}\n
\n
\t\tvar changes = {filter: elem.getAttribute(\'filter\')};\n
\t\t\n
\t\tif (val === 0) {\n
\t\t\telem.removeAttribute("filter");\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(elem, changes));\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tchangeSelectedAttribute("filter", \'url(#\' + elem_id + \'_blur)\');\n
\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(elem, changes));\n
\t\tcanvas.setBlurOffsets(filter, val);\n
\t\t\n
\t\tcur_command = batchCmd;\n
\t\tcanvas.undoMgr.beginUndoableChange("stdDeviation", [filter?filter.firstChild:null]);\n
\t\tif (complete) {\n
\t\t\tcanvas.setBlurNoUndo(val);\n
\t\t\tfinishChange();\n
\t\t}\n
\t};\n
}());\n
\n
// Function: getBold\n
// Check whether selected element is bold or not\n
//\n
// Returns:\n
// Boolean indicating whether or not element is bold\n
this.getBold = function() {\n
\t// should only have one element selected\n
\tvar selected = selectedElements[0];\n
\tif (selected != null && selected.tagName == "text" &&\n
\t\tselectedElements[1] == null) \n
\t{\n
\t\treturn (selected.getAttribute("font-weight") == "bold");\n
\t}\n
\treturn false;\n
};\n
\n
// Function: setBold\n
// Make the selected element bold or normal\n
//\n
// Parameters:\n
// b - Boolean indicating bold (true) or normal (false)\n
this.setBold = function(b) {\n
\tvar selected = selectedElements[0];\n
\tif (selected != null && selected.tagName == "text" &&\n
\t\tselectedElements[1] == null) \n
\t{\n
\t\tchangeSelectedAttribute("font-weight", b ? "bold" : "normal");\n
\t}\n
\tif (!selectedElements[0].textContent) {\n
\t\ttextActions.setCursor();\n
\t}\n
};\n
\n
// Function: getItalic\n
// Check whether selected element is italic or not\n
//\n
// Returns:\n
// Boolean indicating whether or not element is italic\n
this.getItalic = function() {\n
\tvar selected = selectedElements[0];\n
\tif (selected != null && selected.tagName == "text" &&\n
\t\tselectedElements[1] == null) \n
\t{\n
\t\treturn (selected.getAttribute("font-style") == "italic");\n
\t}\n
\treturn false;\n
};\n
\n
// Function: setItalic\n
// Make the selected element italic or normal\n
//\n
// Parameters:\n
// b - Boolean indicating italic (true) or normal (false)\n
this.setItalic = function(i) {\n
\tvar selected = selectedElements[0];\n
\tif (selected != null && selected.tagName == "text" &&\n
\t\tselectedElements[1] == null) \n
\t{\n
\t\tchangeSelectedAttribute("font-style", i ? "italic" : "normal");\n
\t}\n
\tif (!selectedElements[0].textContent) {\n
\t\ttextActions.setCursor();\n
\t}\n
};\n
\n
// Function: getFontFamily\n
// Returns the current font family\n
this.getFontFamily = function() {\n
\treturn cur_text.font_family;\n
};\n
\n
// Function: setFontFamily\n
// Set the new font family\n
//\n
// Parameters:\n
// val - String with the new font family\n
this.setFontFamily = function(val) {\n
\tcur_text.font_family = val;\n
\tchangeSelectedAttribute("font-family", val);\n
\tif (selectedElements[0] && !selectedElements[0].textContent) {\n
\t\ttextActions.setCursor();\n
\t}\n
};\n
\n
\n
// Function: setFontColor\n
// Set the new font color\n
//\n
// Parameters:\n
// val - String with the new font color\n
this.setFontColor = function(val) {\n
\tcur_text.fill = val;\n
\tchangeSelectedAttribute("fill", val);\n
};\n
\n
// Function: getFontColor\n
// Returns the current font color\n
this.getFontColor = function() {\n
\treturn cur_text.fill;\n
};\n
\n
// Function: getFontSize\n
// Returns the current font size\n
this.getFontSize = function() {\n
\treturn cur_text.font_size;\n
};\n
\n
// Function: setFontSize\n
// Applies the given font size to the selected element\n
//\n
// Parameters:\n
// val - Float with the new font size\n
this.setFontSize = function(val) {\n
\tcur_text.font_size = val;\n
\tchangeSelectedAttribute("font-size", val);\n
\tif (!selectedElements[0].textContent) {\n
\t\ttextActions.setCursor();\n
\t}\n
};\n
\n
// Function: getText\n
// Returns the current text (textContent) of the selected element\n
this.getText = function() {\n
\tvar selected = selectedElements[0];\n
\tif (selected == null) { return ""; }\n
\treturn selected.textContent;\n
};\n
\n
// Function: setTextContent\n
// Updates the text element with the given string\n
//\n
// Parameters:\n
// val - String with the new text\n
this.setTextContent = function(val) {\n
\tchangeSelectedAttribute("#text", val);\n
\ttextActions.init(val);\n
\ttextActions.setCursor();\n
};\n
\n
// Function: setImageURL\n
// Sets the new image URL for the selected image element. Updates its size if\n
// a new URL is given\n
// \n
// Parameters:\n
// val - String with the image URL/path\n
this.setImageURL = function(val) {\n
\tvar elem = selectedElements[0];\n
\tif (!elem) {return;}\n
\t\n
\tvar attrs = $(elem).attr([\'width\', \'height\']);\n
\tvar setsize = (!attrs.width || !attrs.height);\n
\n
\tvar cur_href = getHref(elem);\n
\t\n
\t// Do nothing if no URL change or size change\n
\tif (cur_href !== val) {\n
\t\tsetsize = true;\n
\t} else if (!setsize) {return;}\n
\n
\tvar batchCmd = new svgedit.history.BatchCommand("Change Image URL");\n
\n
\tsetHref(elem, val);\n
\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(elem, {\n
\t\t"#href": cur_href\n
\t}));\n
\n
\tif (setsize) {\n
\t\t$(new Image()).load(function() {\n
\t\t\tvar changes = $(elem).attr([\'width\', \'height\']);\n
\t\t\n
\t\t\t$(elem).attr({\n
\t\t\t\twidth: this.width,\n
\t\t\t\theight: this.height\n
\t\t\t});\n
\t\t\t\n
\t\t\tselectorManager.requestSelector(elem).resize();\n
\t\t\t\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(elem, changes));\n
\t\t\taddCommandToHistory(batchCmd);\n
\t\t\tcall("changed", [elem]);\n
\t\t}).attr(\'src\', val);\n
\t} else {\n
\t\taddCommandToHistory(batchCmd);\n
\t}\n
};\n
\n
// Function: setLinkURL\n
// Sets the new link URL for the selected anchor element.\n
// \n
// Parameters:\n
// val - String with the link URL/path\n
this.setLinkURL = function(val) {\n
\tvar elem = selectedElements[0];\n
\tif (!elem) {return;}\n
\tif (elem.tagName !== \'a\') {\n
\t\t// See if parent is an anchor\n
\t\tvar parents_a = $(elem).parents(\'a\');\n
\t\tif (parents_a.length) {\n
\t\t\telem = parents_a[0];\n
\t\t} else {\n
\t\t\treturn;\n
\t\t}\n
\t}\n
\t\n
\tvar cur_href = getHref(elem);\n
\t\n
\tif (cur_href === val) {return;}\n
\t\n
\tvar batchCmd = new svgedit.history.BatchCommand("Change Link URL");\n
\n
\tsetHref(elem, val);\n
\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(elem, {\n
\t\t"#href": cur_href\n
\t}));\n
\n
\taddCommandToHistory(batchCmd);\n
};\n
\n
\n
// Function: setRectRadius\n
// Sets the rx & ry values to the selected rect element to change its corner radius\n
// \n
// Parameters:\n
// val - The new radius\n
this.setRectRadius = function(val) {\n
\tvar selected = selectedElements[0];\n
\tif (selected != null && selected.tagName == "rect") {\n
\t\tvar r = selected.getAttribute("rx");\n
\t\tif (r != val) {\n
\t\t\tselected.setAttribute("rx", val);\n
\t\t\tselected.setAttribute("ry", val);\n
\t\t\taddCommandToHistory(new svgedit.history.ChangeElementCommand(selected, {"rx":r, "ry":r}, "Radius"));\n
\t\t\tcall("changed", [selected]);\n
\t\t}\n
\t}\n
};\n
\n
// Function: makeHyperlink\n
// Wraps the selected element(s) in an anchor element or converts group to one\n
this.makeHyperlink = function(url) {\n
\tcanvas.groupSelectedElements(\'a\', url);\n
\t\n
\t// TODO: If element is a single "g", convert to "a"\n
\t//\tif (selectedElements.length > 1 && selectedElements[1]) {\n
\n
};\n
\n
// Function: removeHyperlink\n
this.removeHyperlink = function() {\n
\tcanvas.ungroupSelectedElement();\n
};\n
\n
// Group: Element manipulation\n
\n
// Function: setSegType\n
// Sets the new segment type to the selected segment(s). \n
//\n
// Parameters:\n
// new_type - Integer with the new segment type\n
// See http://www.w3.org/TR/SVG/paths.html#InterfaceSVGPathSeg for list\n
this.setSegType = function(new_type) {\n
\tpathActions.setSegType(new_type);\n
};\n
\n
// TODO(codedread): Remove the getBBox argument and split this function into two.\n
// Function: convertToPath\n
// Convert selected element to a path, or get the BBox of an element-as-path\n
//\n
// Parameters: \n
// elem - The DOM element to be converted\n
// getBBox - Boolean on whether or not to only return the path\'s BBox\n
//\n
// Returns:\n
// If the getBBox flag is true, the resulting path\'s bounding box object.\n
// Otherwise the resulting path element is returned.\n
this.convertToPath = function(elem, getBBox) {\n
\tif (elem == null) {\n
\t\tvar elems = selectedElements;\n
\t\t$.each(selectedElements, function(i, elem) {\n
\t\t\tif (elem) {canvas.convertToPath(elem);}\n
\t\t});\n
\t\treturn;\n
\t}\n
\t\n
\tif (!getBBox) {\n
\t\tvar batchCmd = new svgedit.history.BatchCommand("Convert element to Path");\n
\t}\n
\t\n
\tvar attrs = getBBox?{}:{\n
\t\t"fill": cur_shape.fill,\n
\t\t"fill-opacity": cur_shape.fill_opacity,\n
\t\t"stroke": cur_shape.stroke,\n
\t\t"stroke-width": cur_shape.stroke_width,\n
\t\t"stroke-dasharray": cur_shape.stroke_dasharray,\n
\t\t"stroke-linejoin": cur_shape.stroke_linejoin,\n
\t\t"stroke-linecap": cur_shape.stroke_linecap,\n
\t\t"stroke-opacity": cur_shape.stroke_opacity,\n
\t\t"opacity": cur_shape.opacity,\n
\t\t"visibility":"hidden"\n
\t};\n
\t\n
\t// any attribute on the element not covered by the above\n
\t// TODO: make this list global so that we can properly maintain it\n
\t// TODO: what about @transform, @clip-rule, @fill-rule, etc?\n
\t$.each([\'marker-start\', \'marker-end\', \'marker-mid\', \'filter\', \'clip-path\'], function() {\n
\t\tif (elem.getAttribute(this)) {\n
\t\t\tattrs[this] = elem.getAttribute(this);\n
\t\t}\n
\t});\n
\t\n
\tvar path = addSvgElementFromJson({\n
\t\t"element": "path",\n
\t\t"attr": attrs\n
\t});\n
\t\n
\tvar eltrans = elem.getAttribute("transform");\n
\tif (eltrans) {\n
\t\tpath.setAttribute("transform", eltrans);\n
\t}\n
\t\n
\tvar id = elem.id;\n
\tvar parent = elem.parentNode;\n
\tif (elem.nextSibling) {\n
\t\tparent.insertBefore(path, elem);\n
\t} else {\n
\t\tparent.appendChild(path);\n
\t}\n
\t\n
\tvar d = \'\';\n
\t\n
\tvar joinSegs = function(segs) {\n
\t\t$.each(segs, function(j, seg) {\n
\t\t\tvar i;\n
\t\t\tvar l = seg[0], pts = seg[1];\n
\t\t\td += l;\n
\t\t\tfor (i = 0; i < pts.length; i+=2) {\n
\t\t\t\td += (pts[i] +\',\'+pts[i+1]) + \' \';\n
\t\t\t}\n
\t\t});\n
\t};\n
\n
\t// Possibly the cubed root of 6, but 1.81 works best\n
\tvar num = 1.81;\n
\tvar a, rx;\n
\tswitch (elem.tagName) {\n
\tcase \'ellipse\':\n
\tcase \'circle\':\n
\t\ta = $(elem).attr([\'rx\', \'ry\', \'cx\', \'cy\']);\n
\t\tvar cx = a.cx, cy = a.cy;\n
\t\trx = a.rx;\n
\t\try = a.ry;\n
\t\tif (elem.tagName == \'circle\') {\n
\t\t\trx = ry = $(elem).attr(\'r\');\n
\t\t}\n
\t\n
\t\tjoinSegs([\n
\t\t\t[\'M\',[(cx-rx),(cy)]],\n
\t\t\t[\'C\',[(cx-rx),(cy-ry/num), (cx-rx/num),(cy-ry), (cx),(cy-ry)]],\n
\t\t\t[\'C\',[(cx+rx/num),(cy-ry), (cx+rx),(cy-ry/num), (cx+rx),(cy)]],\n
\t\t\t[\'C\',[(cx+rx),(cy+ry/num), (cx+rx/num),(cy+ry), (cx),(cy+ry)]],\n
\t\t\t[\'C\',[(cx-rx/num),(cy+ry), (cx-rx),(cy+ry/num), (cx-rx),(cy)]],\n
\t\t\t[\'Z\',[]]\n
\t\t]);\n
\t\tbreak;\n
\tcase \'path\':\n
\t\td = elem.getAttribute(\'d\');\n
\t\tbreak;\n
\tcase \'line\':\n
\t\ta = $(elem).attr(["x1", "y1", "x2", "y2"]);\n
\t\td = "M"+a.x1+","+a.y1+"L"+a.x2+","+a.y2;\n
\t\tbreak;\n
\tcase \'polyline\':\n
\tcase \'polygon\':\n
\t\td = "M" + elem.getAttribute(\'points\');\n
\t\tbreak;\n
\tcase \'rect\':\n
\t\tvar r = $(elem).attr([\'rx\', \'ry\']);\n
\t\trx = r.rx;\n
\t\try = r.ry;\n
\t\tvar b = elem.getBBox();\n
\t\tvar x = b.x, y = b.y, w = b.width, h = b.height;\n
\t\tnum = 4 - num; // Why? Because!\n
\t\t\n
\t\tif (!rx && !ry) {\n
\t\t\t// Regular rect\n
\t\t\tjoinSegs([\n
\t\t\t\t[\'M\',[x, y]],\n
\t\t\t\t[\'L\',[x+w, y]],\n
\t\t\t\t[\'L\',[x+w, y+h]],\n
\t\t\t\t[\'L\',[x, y+h]],\n
\t\t\t\t[\'L\',[x, y]],\n
\t\t\t\t[\'Z\',[]]\n
\t\t\t]);\n
\t\t} else {\n
\t\t\tjoinSegs([\n
\t\t\t\t[\'M\',[x, y+ry]],\n
\t\t\t\t[\'C\',[x, y+ry/num, x+rx/num, y, x+rx, y]],\n
\t\t\t\t[\'L\',[x+w-rx, y]],\n
\t\t\t\t[\'C\',[x+w-rx/num, y, x+w, y+ry/num, x+w, y+ry]],\n
\t\t\t\t[\'L\',[x+w, y+h-ry]],\n
\t\t\t\t[\'C\',[x+w, y+h-ry/num, x+w-rx/num, y+h, x+w-rx, y+h]],\n
\t\t\t\t[\'L\',[x+rx, y+h]],\n
\t\t\t\t[\'C\',[x+rx/num, y+h, x, y+h-ry/num, x, y+h-ry]],\n
\t\t\t\t[\'L\',[x, y+ry]],\n
\t\t\t\t[\'Z\',[]]\n
\t\t\t]);\n
\t\t}\n
\t\tbreak;\n
\tdefault:\n
\t\tpath.parentNode.removeChild(path);\n
\t\tbreak;\n
\t}\n
\t\n
\tif (d) {\n
\t\tpath.setAttribute(\'d\', d);\n
\t}\n
\t\n
\tif (!getBBox) {\n
\t\t// Replace the current element with the converted one\n
\t\t\n
\t\t// Reorient if it has a matrix\n
\t\tif (eltrans) {\n
\t\t\tvar tlist = svgedit.transformlist.getTransformList(path);\n
\t\t\tif (svgedit.math.hasMatrixTransform(tlist)) {\n
\t\t\t\tpathActions.resetOrientation(path);\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\tvar nextSibling = elem.nextSibling;\n
\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(elem, nextSibling, parent));\n
\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(path));\n
\n
\t\tclearSelection();\n
\t\telem.parentNode.removeChild(elem);\n
\t\tpath.setAttribute(\'id\', id);\n
\t\tpath.removeAttribute("visibility");\n
\t\taddToSelection([path], true);\n
\t\t\n
\t\taddCommandToHistory(batchCmd);\n
\t\t\n
\t} else {\n
\t\t// Get the correct BBox of the new path, then discard it\n
\t\tpathActions.resetOrientation(path);\n
\t\tvar bb = false;\n
\t\ttry {\n
\t\t\tbb = path.getBBox();\n
\t\t} catch(e) {\n
\t\t\t// Firefox fails\n
\t\t}\n
\t\tpath.parentNode.removeChild(path);\n
\t\treturn bb;\n
\t}\n
};\n
\n
\n
// Function: changeSelectedAttributeNoUndo\n
// This function makes the changes to the elements. It does not add the change\n
// to the history stack. \n
// \n
// Parameters:\n
// attr - String with the attribute name\n
// newValue - String or number with the new attribute value\n
// elems - The DOM elements to apply the change to\n
var changeSelectedAttributeNoUndo = function(attr, newValue, elems) {\n
\tvar handle = svgroot.suspendRedraw(1000);\n
\tif (current_mode == \'pathedit\') {\n
\t\t// Editing node\n
\t\tpathActions.moveNode(attr, newValue);\n
\t}\n
\telems = elems || selectedElements;\n
\tvar i = elems.length;\n
\tvar no_xy_elems = [\'g\', \'polyline\', \'path\'];\n
\tvar good_g_attrs = [\'transform\', \'opacity\', \'filter\'];\n
\t\n
\twhile (i--) {\n
\t\tvar elem = elems[i];\n
\t\tif (elem == null) {continue;}\n
\t\t\n
\t\t// Set x,y vals on elements that don\'t have them\n
\t\tif ((attr === \'x\' || attr === \'y\') && no_xy_elems.indexOf(elem.tagName) >= 0) {\n
\t\t\tvar bbox = getStrokedBBox([elem]);\n
\t\t\tvar diff_x = attr === \'x\' ? newValue - bbox.x : 0;\n
\t\t\tvar diff_y = attr === \'y\' ? newValue - bbox.y : 0;\n
\t\t\tcanvas.moveSelectedElements(diff_x*current_zoom, diff_y*current_zoom, true);\n
\t\t\tcontinue;\n
\t\t}\n
\t\t\n
\t\t// only allow the transform/opacity/filter attribute to change on <g> elements, slightly hacky\n
\t\t// TODO: FIXME: This doesn\'t seem right. Where\'s the body of this if statement?\n
\t\tif (elem.tagName === "g" && good_g_attrs.indexOf(attr) >= 0) {}\n
\t\tvar oldval = attr === "#text" ? elem.textContent : elem.getAttribute(attr);\n
\t\tif (oldval == null) {oldval = "";}\n
\t\tif (oldval !== String(newValue)) {\n
\t\t\tif (attr == "#text") {\n
\t\t\t\tvar old_w = svgedit.utilities.getBBox(elem).width;\n
\t\t\t\telem.textContent = newValue;\n
\t\t\t\t\n
\t\t\t\t// FF bug occurs on on rotated elements\n
\t\t\t\tif (/rotate/.test(elem.getAttribute(\'transform\'))) {\n
\t\t\t\t\telem = ffClone(elem);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// Hoped to solve the issue of moving text with text-anchor="start",\n
\t\t\t\t// but this doesn\'t actually fix it. Hopefully on the right track, though. -Fyrd\n
\t\t\t\t\n
//\t\t\t\t\tvar box=getBBox(elem), left=box.x, top=box.y, width=box.width,\n
//\t\t\t\t\t\theight=box.height, dx = width - old_w, dy=0;\n
//\t\t\t\t\tvar angle = svgedit.utilities.getRotationAngle(elem, true);\n
//\t\t\t\t\tif (angle) {\n
//\t\t\t\t\t\tvar r = Math.sqrt( dx*dx + dy*dy );\n
//\t\t\t\t\t\tvar theta = Math.atan2(dy,dx) - angle;\n
//\t\t\t\t\t\tdx = r * Math.cos(theta);\n
//\t\t\t\t\t\tdy = r * Math.sin(theta);\n
//\t\t\t\t\t\t\n
//\t\t\t\t\t\telem.setAttribute(\'x\', elem.getAttribute(\'x\')-dx);\n
//\t\t\t\t\t\telem.setAttribute(\'y\', elem.getAttribute(\'y\')-dy);\n
//\t\t\t\t\t}\n
\t\t\t\t\n
\t\t\t} else if (attr == "#href") {\n
\t\t\t\tsetHref(elem, newValue);\n
\t\t\t}\n
\t\t\telse {elem.setAttribute(attr, newValue);}\n
\n
\t\t\t// Go into "select" mode for text changes\n
\t\t\t// NOTE: Important that this happens AFTER elem.setAttribute() or else attributes like\n
\t\t\t// font-size can get reset to their old value, ultimately by svgEditor.updateContextPanel(),\n
\t\t\t// after calling textActions.toSelectMode() below\n
\t\t\tif (current_mode === "textedit" && attr !== "#text" && elem.textContent.length) {\n
\t\t\t\ttextActions.toSelectMode(elem);\n
\t\t\t}\n
\n
//\t\t\tif (i==0)\n
//\t\t\t\tselectedBBoxes[0] = svgedit.utilities.getBBox(elem);\n
\t\t\t// Use the Firefox ffClone hack for text elements with gradients or\n
\t\t\t// where other text attributes are changed. \n
\t\t\tif (svgedit.browser.isGecko() && elem.nodeName === \'text\' && /rotate/.test(elem.getAttribute(\'transform\'))) {\n
\t\t\t\tif (String(newValue).indexOf(\'url\') === 0 || ([\'font-size\', \'font-family\', \'x\', \'y\'].indexOf(attr) >= 0 && elem.textContent)) {\n
\t\t\t\t\telem = ffClone(elem);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t// Timeout needed for Opera & Firefox\n
\t\t\t// codedread: it is now possible for this function to be called with elements\n
\t\t\t// that are not in the selectedElements array, we need to only request a\n
\t\t\t// selector if the element is in that array\n
\t\t\tif (selectedElements.indexOf(elem) >= 0) {\n
\t\t\t\tsetTimeout(function() {\n
\t\t\t\t\t// Due to element replacement, this element may no longer\n
\t\t\t\t\t// be part of the DOM\n
\t\t\t\t\tif (!elem.parentNode) {return;}\n
\t\t\t\t\tselectorManager.requestSelector(elem).resize();\n
\t\t\t\t}, 0);\n
\t\t\t}\n
\t\t\t// if this element was rotated, and we changed the position of this element\n
\t\t\t// we need to update the rotational transform attribute \n
\t\t\tvar angle = svgedit.utilities.getRotationAngle(elem);\n
\t\t\tif (angle != 0 && attr != "transform") {\n
\t\t\t\tvar tlist = svgedit.transformlist.getTransformList(elem);\n
\t\t\t\tvar n = tlist.numberOfItems;\n
\t\t\t\twhile (n--) {\n
\t\t\t\t\tvar xform = tlist.getItem(n);\n
\t\t\t\t\tif (xform.type == 4) {\n
\t\t\t\t\t\t// remove old rotate\n
\t\t\t\t\t\ttlist.removeItem(n);\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tvar box = svgedit.utilities.getBBox(elem);\n
\t\t\t\t\t\tvar center = svgedit.math.transformPoint(box.x+box.width/2, box.y+box.height/2, svgedit.math.transformListToTransform(tlist).matrix);\n
\t\t\t\t\t\tvar cx = center.x,\n
\t\t\t\t\t\t\tcy = center.y;\n
\t\t\t\t\t\tvar newrot = svgroot.createSVGTransform();\n
\t\t\t\t\t\tnewrot.setRotate(angle, cx, cy);\n
\t\t\t\t\t\ttlist.insertItemBefore(newrot, n);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t} // if oldValue != newValue\n
\t} // for each elem\n
\tsvgroot.unsuspendRedraw(handle);\t\n
};\n
\n
// Function: changeSelectedAttribute\n
// Change the given/selected element and add the original value to the history stack\n
// If you want to change all selectedElements, ignore the elems argument.\n
// If you want to change only a subset of selectedElements, then send the\n
// subset to this function in the elems argument.\n
// \n
// Parameters:\n
// attr - String with the attribute name\n
// newValue - String or number with the new attribute value\n
// elems - The DOM elements to apply the change to\n
var changeSelectedAttribute = this.changeSelectedAttribute = function(attr, val, elems) {\n
\telems = elems || selectedElements;\n
\tcanvas.undoMgr.beginUndoableChange(attr, elems);\n
\tvar i = elems.length;\n
\n
\tchangeSelectedAttributeNoUndo(attr, val, elems);\n
\n
\tvar batchCmd = canvas.undoMgr.finishUndoableChange();\n
\tif (!batchCmd.isEmpty()) { \n
\t\taddCommandToHistory(batchCmd);\n
\t}\n
};\n
\n
// Function: deleteSelectedElements\n
// Removes all selected elements from the DOM and adds the change to the \n
// history stack\n
this.deleteSelectedElements = function() {\n
\tvar i;\n
\tvar batchCmd = new svgedit.history.BatchCommand("Delete Elements");\n
\tvar len = selectedElements.length;\n
\tvar selectedCopy = []; //selectedElements is being deleted\n
\tfor (i = 0; i < len; ++i) {\n
\t\tvar selected = selectedElements[i];\n
\t\tif (selected == null) {break;}\n
\n
\t\tvar parent = selected.parentNode;\n
\t\tvar t = selected;\n
\t\t\n
\t\t// this will unselect the element and remove the selectedOutline\n
\t\tselectorManager.releaseSelector(t);\n
\t\t\n
\t\t// Remove the path if present.\n
\t\tsvgedit.path.removePath_(t.id);\n
\t\t\n
\t\t// Get the parent if it\'s a single-child anchor\n
\t\tif (parent.tagName === \'a\' && parent.childNodes.length === 1) {\n
\t\t\tt = parent;\n
\t\t\tparent = parent.parentNode;\n
\t\t}\n
\t\t\n
\t\tvar nextSibling = t.nextSibling;\n
\t\tvar elem = parent.removeChild(t);\n
\t\tselectedCopy.push(selected); //for the copy\n
\t\tselectedElements[i] = null;\n
\t\tbatchCmd.addSubCommand(new RemoveElementCommand(elem, nextSibling, parent));\n
\t}\n
\tif (!batchCmd.isEmpty()) {addCommandToHistory(batchCmd);}\n
\tcall("changed", selectedCopy);\n
\tclearSelection();\n
};\n
\n
// Function: cutSelectedElements\n
// Removes all selected elements from the DOM and adds the change to the \n
// history stack. Remembers removed elements on the clipboard\n
\n
// TODO: Combine similar code with deleteSelectedElements\n
this.cutSelectedElements = function() {\n
\tvar i;\n
\tvar batchCmd = new svgedit.history.BatchCommand("Cut Elements");\n
\tvar len = selectedElements.length;\n
\tvar selectedCopy = []; //selectedElements is being deleted\n
\tfor (i = 0; i < len; ++i) {\n
\t\tvar selected = selectedElements[i];\n
\t\tif (selected == null) {break;}\n
\n
\t\tvar parent = selected.parentNode;\n
\t\tvar t = selected;\n
\n
\t\t// this will unselect the element and remove the selectedOutline\n
\t\tselectorManager.releaseSelector(t);\n
\n
\t\t// Remove the path if present.\n
\t\tsvgedit.path.removePath_(t.id);\n
\n
\t\tvar nextSibling = t.nextSibling;\n
\t\tvar elem = parent.removeChild(t);\n
\t\tselectedCopy.push(selected); //for the copy\n
\t\tselectedElements[i] = null;\n
\t\tbatchCmd.addSubCommand(new RemoveElementCommand(elem, nextSibling, parent));\n
\t}\n
\tif (!batchCmd.isEmpty()) {addCommandToHistory(batchCmd);}\n
\tcall("changed", selectedCopy);\n
\tclearSelection();\n
\t\n
\tcanvas.clipBoard = selectedCopy;\n
};\n
\n
// Function: copySelectedElements\n
// Remembers the current selected elements on the clipboard\n
this.copySelectedElements = function() {\n
\tcanvas.clipBoard = $.merge([], selectedElements);\n
};\n
\n
this.pasteElements = function(type, x, y) {\n
\tvar cb = canvas.clipBoard;\n
\tvar len = cb.length;\n
\tif (!len) {return;}\n
\t\n
\tvar pasted = [];\n
\tvar batchCmd = new svgedit.history.BatchCommand(\'Paste elements\');\n
\t\n
\t// Move elements to lastClickPoint\n
\n
\twhile (len--) {\n
\t\tvar elem = cb[len];\n
\t\tif (!elem) {continue;}\n
\t\tvar copy = copyElem(elem);\n
\n
\t\t// See if elem with elem ID is in the DOM already\n
\t\tif (!svgedit.utilities.getElem(elem.id)) {copy.id = elem.id;}\n
\t\t\n
\t\tpasted.push(copy);\n
\t\t(current_group || getCurrentDrawing().getCurrentLayer()).appendChild(copy);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(copy));\n
\t}\n
\t\n
\tselectOnly(pasted);\n
\t\n
\tif (type !== \'in_place\') {\n
\t\t\n
\t\tvar ctr_x, ctr_y;\n
\t\t\n
\t\tif (!type) {\n
\t\t\tctr_x = lastClickPoint.x;\n
\t\t\tctr_y = lastClickPoint.y;\n
\t\t} else if (type === \'point\') {\n
\t\t\tctr_x = x;\n
\t\t\tctr_y = y;\n
\t\t} \n
\t\t\n
\t\tvar bbox = getStrokedBBox(pasted);\n
\t\tvar cx = ctr_x - (bbox.x + bbox.width/2),\n
\t\t\tcy = ctr_y - (bbox.y + bbox.height/2),\n
\t\t\tdx = [],\n
\t\t\tdy = [];\n
\t\n
\t\t$.each(pasted, function(i, item) {\n
\t\t\tdx.push(cx);\n
\t\t\tdy.push(cy);\n
\t\t});\n
\t\t\n
\t\tvar cmd = canvas.moveSelectedElements(dx, dy, false);\n
\t\tbatchCmd.addSubCommand(cmd);\n
\t}\n
\n
\taddCommandToHistory(batchCmd);\n
\tcall("changed", pasted);\n
};\n
\n
// Function: groupSelectedElements\n
// Wraps all the selected elements in a group (g) element\n
\n
// Parameters: \n
// type - type of element to group into, defaults to <g>\n
this.groupSelectedElements = function(type, urlArg) {\n
\tif (!type) {type = \'g\';}\n
\tvar cmd_str = \'\';\n
\t\n
\tswitch (type) {\n
\t\tcase "a":\n
\t\t\tcmd_str = "Make hyperlink";\n
\t\t\tvar url = \'\';\n
\t\t\tif (arguments.length > 1) {\n
\t\t\t\turl = urlArg;\n
\t\t\t}\n
\t\t\tbreak;\n
\t\tdefault:\n
\t\t\ttype = \'g\';\n
\t\t\tcmd_str = "Group Elements";\n
\t\t\tbreak;\n
\t}\n
\t\n
\tvar batchCmd = new svgedit.history.BatchCommand(cmd_str);\n
\t\n
\t// create and insert the group element\n
\tvar g = addSvgElementFromJson({\n
\t\t\t\t\t\t\t"element": type,\n
\t\t\t\t\t\t\t"attr": {\n
\t\t\t\t\t\t\t\t"id": getNextId()\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t});\n
\tif (type === \'a\') {\n
\t\tsetHref(g, url);\n
\t}\n
\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(g));\n
\t\n
\t// now move all children into the group\n
\tvar i = selectedElements.length;\n
\twhile (i--) {\n
\t\tvar elem = selectedElements[i];\n
\t\tif (elem == null) {continue;}\n
\t\t\n
\t\tif (elem.parentNode.tagName === \'a\' && elem.parentNode.childNodes.length === 1) {\n
\t\t\telem = elem.parentNode;\n
\t\t}\n
\t\t\n
\t\tvar oldNextSibling = elem.nextSibling;\n
\t\tvar oldParent = elem.parentNode;\n
\t\tg.appendChild(elem);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.MoveElementCommand(elem, oldNextSibling, oldParent));\t\t\t\n
\t}\n
\tif (!batchCmd.isEmpty()) {addCommandToHistory(batchCmd);}\n
\t\n
\t// update selection\n
\tselectOnly([g], true);\n
};\n
\n
\n
// Function: pushGroupProperties\n
// Pushes all appropriate parent group properties down to its children, then\n
// removes them from the group\n
var pushGroupProperties = this.pushGroupProperties = function(g, undoable) {\n
\n
\tvar children = g.childNodes;\n
\tvar len = children.length;\n
\tvar xform = g.getAttribute("transform");\n
\n
\tvar glist = svgedit.transformlist.getTransformList(g);\n
\tvar m = svgedit.math.transformListToTransform(glist).matrix;\n
\t\n
\tvar batchCmd = new svgedit.history.BatchCommand("Push group properties");\n
\n
\t// TODO: get all fill/stroke properties from the group that we are about to destroy\n
\t// "fill", "fill-opacity", "fill-rule", "stroke", "stroke-dasharray", "stroke-dashoffset", \n
\t// "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", \n
\t// "stroke-width"\n
\t// and then for each child, if they do not have the attribute (or the value is \'inherit\')\n
\t// then set the child\'s attribute\n
\t\n
\tvar i = 0;\n
\tvar gangle = svgedit.utilities.getRotationAngle(g);\n
\t\n
\tvar gattrs = $(g).attr([\'filter\', \'opacity\']);\n
\tvar gfilter, gblur, changes;\n
\t\n
\tfor (i = 0; i < len; i++) {\n
\t\tvar elem = children[i];\n
\t\t\n
\t\tif (elem.nodeType !== 1) {continue;}\n
\t\t\n
\t\tif (gattrs.opacity !== null && gattrs.opacity !== 1) {\n
\t\t\tvar c_opac = elem.getAttribute(\'opacity\') || 1;\n
\t\t\tvar new_opac = Math.round((elem.getAttribute(\'opacity\') || 1) * gattrs.opacity * 100)/100;\n
\t\t\tchangeSelectedAttribute(\'opacity\', new_opac, [elem]);\n
\t\t}\n
\n
\t\tif (gattrs.filter) {\n
\t\t\tvar cblur = this.getBlur(elem);\n
\t\t\tvar orig_cblur = cblur;\n
\t\t\tif (!gblur) {gblur = this.getBlur(g);}\n
\t\t\tif (cblur) {\n
\t\t\t\t// Is this formula correct?\n
\t\t\t\tcblur = Number(gblur) + Number(cblur);\n
\t\t\t} else if (cblur === 0) {\n
\t\t\t\tcblur = gblur;\n
\t\t\t}\n
\t\t\t\n
\t\t\t// If child has no current filter, get group\'s filter or clone it.\n
\t\t\tif (!orig_cblur) {\n
\t\t\t\t// Set group\'s filter to use first child\'s ID\n
\t\t\t\tif (!gfilter) {\n
\t\t\t\t\tgfilter = svgedit.utilities.getRefElem(gattrs.filter);\n
\t\t\t\t} else {\n
\t\t\t\t\t// Clone the group\'s filter\n
\t\t\t\t\tgfilter = copyElem(gfilter);\n
\t\t\t\t\tsvgedit.utilities.findDefs().appendChild(gfilter);\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tgfilter = svgedit.utilities.getRefElem(elem.getAttribute(\'filter\'));\n
\t\t\t}\n
\n
\t\t\t// Change this in future for different filters\n
\t\t\tvar suffix = (gfilter.firstChild.tagName === \'feGaussianBlur\')?\'blur\':\'filter\'; \n
\t\t\tgfilter.id = elem.id + \'_\' + suffix;\n
\t\t\tchangeSelectedAttribute(\'filter\', \'url(#\' + gfilter.id + \')\', [elem]);\n
\t\t\t\n
\t\t\t// Update blur value \n
\t\t\tif (cblur) {\n
\t\t\t\tchangeSelectedAttribute(\'stdDeviation\', cblur, [gfilter.firstChild]);\n
\t\t\t\tcanvas.setBlurOffsets(gfilter, cblur);\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\tvar chtlist = svgedit.transformlist.getTransformList(elem);\n
\n
\t\t// Don\'t process gradient transforms\n
\t\tif (~elem.tagName.indexOf(\'Gradient\')) {chtlist = null;}\n
\t\t\n
\t\t// Hopefully not a problem to add this. Necessary for elements like <desc/>\n
\t\tif (!chtlist) {continue;}\n
\t\t\n
\t\t// Apparently <defs> can get get a transformlist, but we don\'t want it to have one!\n
\t\tif (elem.tagName === \'defs\') {continue;}\n
\t\t\n
\t\tif (glist.numberOfItems) {\n
\t\t\t// TODO: if the group\'s transform is just a rotate, we can always transfer the\n
\t\t\t// rotate() down to the children (collapsing consecutive rotates and factoring\n
\t\t\t// out any translates)\n
\t\t\tif (gangle && glist.numberOfItems == 1) {\n
\t\t\t\t// [Rg] [Rc] [Mc]\n
\t\t\t\t// we want [Tr] [Rc2] [Mc] where:\n
\t\t\t\t//\t- [Rc2] is at the child\'s current center but has the \n
\t\t\t\t// sum of the group and child\'s rotation angles\n
\t\t\t\t//\t- [Tr] is the equivalent translation that this child \n
\t\t\t\t// undergoes if the group wasn\'t there\n
\t\t\t\t\n
\t\t\t\t// [Tr] = [Rg] [Rc] [Rc2_inv]\n
\t\t\t\t\n
\t\t\t\t// get group\'s rotation matrix (Rg)\n
\t\t\t\tvar rgm = glist.getItem(0).matrix;\n
\t\t\t\t\n
\t\t\t\t// get child\'s rotation matrix (Rc)\n
\t\t\t\tvar rcm = svgroot.createSVGMatrix();\n
\t\t\t\tvar cangle = svgedit.utilities.getRotationAngle(elem);\n
\t\t\t\tif (cangle) {\n
\t\t\t\t\trcm = chtlist.getItem(0).matrix;\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\t// get child\'s old center of rotation\n
\t\t\t\tvar cbox = svgedit.utilities.getBBox(elem);\n
\t\t\t\tvar ceqm = svgedit.math.transformListToTransform(chtlist).matrix;\n
\t\t\t\tvar coldc = svgedit.math.transformPoint(cbox.x+cbox.width/2, cbox.y+cbox.height/2, ceqm);\n
\t\t\t\t\n
\t\t\t\t// sum group and child\'s angles\n
\t\t\t\tvar sangle = gangle + cangle;\n
\t\t\t\t\n
\t\t\t\t// get child\'s rotation at the old center (Rc2_inv)\n
\t\t\t\tvar r2 = svgroot.createSVGTransform();\n
\t\t\t\tr2.setRotate(sangle, coldc.x, coldc.y);\n
\t\t\t\t\n
\t\t\t\t// calculate equivalent translate\n
\t\t\t\tvar trm = svgedit.math.matrixMultiply(rgm, rcm, r2.matrix.inverse());\n
\t\t\t\t\n
\t\t\t\t// set up tlist\n
\t\t\t\tif (cangle) {\n
\t\t\t\t\tchtlist.removeItem(0);\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif (sangle) {\n
\t\t\t\t\tif (chtlist.numberOfItems) {\n
\t\t\t\t\t\tchtlist.insertItemBefore(r2, 0);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tchtlist.appendItem(r2);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tif (trm.e || trm.f) {\n
\t\t\t\t\tvar tr = svgroot.createSVGTransform();\n
\t\t\t\t\ttr.setTranslate(trm.e, trm.f);\n
\t\t\t\t\tif (chtlist.numberOfItems) {\n
\t\t\t\t\t\tchtlist.insertItemBefore(tr, 0);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tchtlist.appendItem(tr);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t} else { // more complicated than just a rotate\n
\t\t\t\n
\t\t\t\t// transfer the group\'s transform down to each child and then\n
\t\t\t\t// call svgedit.recalculate.recalculateDimensions()\t\t\t\t\n
\t\t\t\tvar oldxform = elem.getAttribute("transform");\n
\t\t\t\tchanges = {};\n
\t\t\t\tchanges.transform = oldxform || \'\';\n
\n
\t\t\t\tvar newxform = svgroot.createSVGTransform();\n
\n
\t\t\t\t// [ gm ] [ chm ] = [ chm ] [ gm\' ]\n
\t\t\t\t// [ gm\' ] = [ chm_inv ] [ gm ] [ chm ]\n
\t\t\t\tvar chm = svgedit.math.transformListToTransform(chtlist).matrix,\n
\t\t\t\t\tchm_inv = chm.inverse();\n
\t\t\t\tvar gm = svgedit.math.matrixMultiply( chm_inv, m, chm );\n
\t\t\t\tnewxform.setMatrix(gm);\n
\t\t\t\tchtlist.appendItem(newxform);\n
\t\t\t}\n
\t\t\tvar cmd = svgedit.recalculate.recalculateDimensions(elem);\n
\t\t\tif (cmd) {batchCmd.addSubCommand(cmd);}\n
\t\t}\n
\t}\n
\n
\t\n
\t// remove transform and make it undo-able\n
\tif (xform) {\n
\t\tchanges = {};\n
\t\tchanges["transform"] = xform;\n
\t\tg.setAttribute("transform", "");\n
\t\tg.removeAttribute("transform");\t\t\t\t\n
\t\tbatchCmd.addSubCommand(new svgedit.history.ChangeElementCommand(g, changes));\n
\t}\n
\t\n
\tif (undoable && !batchCmd.isEmpty()) {\n
\t\treturn batchCmd;\n
\t}\n
};\n
\n
\n
// Function: ungroupSelectedElement\n
// Unwraps all the elements in a selected group (g) element. This requires\n
// significant recalculations to apply group\'s transforms, etc to its children\n
this.ungroupSelectedElement = function() {\n
\tvar g = selectedElements[0];\n
\tif ($(g).data(\'gsvg\') || $(g).data(\'symbol\')) {\n
\t\t// Is svg, so actually convert to group\n
\t\tconvertToGroup(g);\n
\t\treturn;\n
\t}\n
\tif (g.tagName === \'use\') {\n
\t\t// Somehow doesn\'t have data set, so retrieve\n
\t\tvar symbol = svgedit.utilities.getElem(getHref(g).substr(1));\n
\t\t$(g).data(\'symbol\', symbol).data(\'ref\', symbol);\n
\t\tconvertToGroup(g);\n
\t\treturn;\n
\t}\n
\tvar parents_a = $(g).parents(\'a\');\n
\tif (parents_a.length) {\n
\t\tg = parents_a[0];\n
\t}\n
\t\n
\t// Look for parent "a"\n
\tif (g.tagName === "g" || g.tagName === "a") {\n
\t\t\n
\t\tvar batchCmd = new svgedit.history.BatchCommand("Ungroup Elements");\n
\t\tvar cmd = pushGroupProperties(g, true);\n
\t\tif (cmd) {batchCmd.addSubCommand(cmd);}\n
\t\t\n
\t\tvar parent = g.parentNode;\n
\t\tvar anchor = g.nextSibling;\n
\t\tvar children = new Array(g.childNodes.length);\n
\t\t\n
\t\tvar i = 0;\n
\t\t\n
\t\twhile (g.firstChild) {\n
\t\t\tvar elem = g.firstChild;\n
\t\t\tvar oldNextSibling = elem.nextSibling;\n
\t\t\tvar oldParent = elem.parentNode;\n
\t\t\t\n
\t\t\t// Remove child title elements\n
\t\t\tif (elem.tagName === \'title\') {\n
\t\t\t\tvar nextSibling = elem.nextSibling;\n
\t\t\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(elem, nextSibling, oldParent));\n
\t\t\t\toldParent.removeChild(elem);\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\t\t\t\n
\t\t\tchildren[i++] = elem = parent.insertBefore(elem, anchor);\n
\t\t\tbatchCmd.addSubCommand(new svgedit.history.MoveElementCommand(elem, oldNextSibling, oldParent));\n
\t\t}\n
\n
\t\t// remove the group from the selection\t\t\t\n
\t\tclearSelection();\n
\t\t\n
\t\t// delete the group element (but make undo-able)\n
\t\tvar gNextSibling = g.nextSibling;\n
\t\tg = parent.removeChild(g);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.RemoveElementCommand(g, gNextSibling, parent));\n
\n
\t\tif (!batchCmd.isEmpty()) {addCommandToHistory(batchCmd);}\n
\t\t\n
\t\t// update selection\n
\t\taddToSelection(children);\n
\t}\n
};\n
\n
// Function: moveToTopSelectedElement\n
// Repositions the selected element to the bottom in the DOM to appear on top of\n
// other elements\n
this.moveToTopSelectedElement = function() {\n
\tvar selected = selectedElements[0];\n
\tif (selected != null) {\n
\t\tvar t = selected;\n
\t\tvar oldParent = t.parentNode;\n
\t\tvar oldNextSibling = t.nextSibling;\n
\t\tt = t.parentNode.appendChild(t);\n
\t\t// If the element actually moved position, add the command and fire the changed\n
\t\t// event handler.\n
\t\tif (oldNextSibling != t.nextSibling) {\n
\t\t\taddCommandToHistory(new svgedit.history.MoveElementCommand(t, oldNextSibling, oldParent, "top"));\n
\t\t\tcall("changed", [t]);\n
\t\t}\n
\t}\n
};\n
\n
// Function: moveToBottomSelectedElement\n
// Repositions the selected element to the top in the DOM to appear under \n
// other elements\n
this.moveToBottomSelectedElement = function() {\n
\tvar selected = selectedElements[0];\n
\tif (selected != null) {\n
\t\tvar t = selected;\n
\t\tvar oldParent = t.parentNode;\n
\t\tvar oldNextSibling = t.nextSibling;\n
\t\tvar firstChild = t.parentNode.firstChild;\n
\t\tif (firstChild.tagName == \'title\') {\n
\t\t\tfirstChild = firstChild.nextSibling;\n
\t\t}\n
\t\t// This can probably be removed, as the defs should not ever apppear\n
\t\t// inside a layer group\n
\t\tif (firstChild.tagName == \'defs\') {\n
\t\t\tfirstChild = firstChild.nextSibling;\n
\t\t}\n
\t\tt = t.parentNode.insertBefore(t, firstChild);\n
\t\t// If the element actually moved position, add the command and fire the changed\n
\t\t// event handler.\n
\t\tif (oldNextSibling != t.nextSibling) {\n
\t\t\taddCommandToHistory(new svgedit.history.MoveElementCommand(t, oldNextSibling, oldParent, "bottom"));\n
\t\t\tcall("changed", [t]);\n
\t\t}\n
\t}\n
};\n
\n
// Function: moveUpDownSelected\n
// Moves the select element up or down the stack, based on the visibly\n
// intersecting elements\n
//\n
// Parameters: \n
// dir - String that\'s either \'Up\' or \'Down\'\n
this.moveUpDownSelected = function(dir) {\n
\tvar selected = selectedElements[0];\n
\tif (!selected) {return;}\n
\t\n
\tcurBBoxes = [];\n
\tvar closest, found_cur;\n
\t// jQuery sorts this list\n
\tvar list = $(getIntersectionList(getStrokedBBox([selected]))).toArray();\n
\tif (dir == \'Down\') {list.reverse();}\n
\n
\t$.each(list, function() {\n
\t\tif (!found_cur) {\n
\t\t\tif (this == selected) {\n
\t\t\t\tfound_cur = true;\n
\t\t\t}\n
\t\t\treturn;\n
\t\t}\n
\t\tclosest = this;\n
\t\treturn false;\n
\t});\n
\tif (!closest) {return;}\n
\t\n
\tvar t = selected;\n
\tvar oldParent = t.parentNode;\n
\tvar oldNextSibling = t.nextSibling;\n
\t$(closest)[dir == \'Down\'?\'before\':\'after\'](t);\n
\t// If the element actually moved position, add the command and fire the changed\n
\t// event handler.\n
\tif (oldNextSibling != t.nextSibling) {\n
\t\taddCommandToHistory(new svgedit.history.MoveElementCommand(t, oldNextSibling, oldParent, "Move " + dir));\n
\t\tcall("changed", [t]);\n
\t}\n
};\n
\n
// Function: moveSelectedElements\n
// Moves selected elements on the X/Y axis \n
//\n
// Parameters:\n
// dx - Float with the distance to move on the x-axis\n
// dy - Float with the distance to move on the y-axis\n
// undoable - Boolean indicating whether or not the action should be undoable\n
//\n
// Returns:\n
// Batch command for the move\n
this.moveSelectedElements = function(dx, dy, undoable) {\n
\t// if undoable is not sent, default to true\n
\t// if single values, scale them to the zoom\n
\tif (dx.constructor != Array) {\n
\t\tdx /= current_zoom;\n
\t\tdy /= current_zoom;\n
\t}\n
\tundoable = undoable || true;\n
\tvar batchCmd = new svgedit.history.BatchCommand("position");\n
\tvar i = selectedElements.length;\n
\twhile (i--) {\n
\t\tvar selected = selectedElements[i];\n
\t\tif (selected != null) {\n
//\t\t\tif (i==0)\n
//\t\t\t\tselectedBBoxes[0] = svgedit.utilities.getBBox(selected);\n
\t\t\t\n
//\t\t\tvar b = {};\n
//\t\t\tfor (var j in selectedBBoxes[i]) b[j] = selectedBBoxes[i][j];\n
//\t\t\tselectedBBoxes[i] = b;\n
\t\t\t\n
\t\t\tvar xform = svgroot.createSVGTransform();\n
\t\t\tvar tlist = svgedit.transformlist.getTransformList(selected);\n
\t\t\t\n
\t\t\t// dx and dy could be arrays\n
\t\t\tif (dx.constructor == Array) {\n
//\t\t\t\tif (i==0) {\n
//\t\t\t\t\tselectedBBoxes[0].x += dx[0];\n
//\t\t\t\t\tselectedBBoxes[0].y += dy[0];\n
//\t\t\t\t}\n
\t\t\t\txform.setTranslate(dx[i], dy[i]);\n
\t\t\t} else {\n
//\t\t\t\tif (i==0) {\n
//\t\t\t\t\tselectedBBoxes[0].x += dx;\n
//\t\t\t\t\tselectedBBoxes[0].y += dy;\n
//\t\t\t\t}\n
\t\t\t\txform.setTranslate(dx, dy);\n
\t\t\t}\n
\n
\t\t\tif (tlist.numberOfItems) {\n
\t\t\t\ttlist.insertItemBefore(xform, 0);\n
\t\t\t} else {\n
\t\t\t\ttlist.appendItem(xform);\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar cmd = svgedit.recalculate.recalculateDimensions(selected);\n
\t\t\tif (cmd) {\n
\t\t\t\tbatchCmd.addSubCommand(cmd);\n
\t\t\t}\n
\t\t\t\n
\t\t\tselectorManager.requestSelector(selected).resize();\n
\t\t}\n
\t}\n
\tif (!batchCmd.isEmpty()) {\n
\t\tif (undoable) {\n
\t\t\taddCommandToHistory(batchCmd);\n
\t\t}\n
\t\tcall("changed", selectedElements);\n
\t\treturn batchCmd;\n
\t}\n
};\n
\n
// Function: cloneSelectedElements\n
// Create deep DOM copies (clones) of all selected elements and move them slightly \n
// from their originals\n
this.cloneSelectedElements = function(x, y) {\n
\tvar i, elem;\n
\tvar batchCmd = new svgedit.history.BatchCommand("Clone Elements");\n
\t// find all the elements selected (stop at first null)\n
\tvar len = selectedElements.length;\n
\tfunction sortfunction(a, b){\n
\t\treturn ($(b).index() - $(a).index()); //causes an array to be sorted numerically and ascending\n
\t}\n
\tselectedElements.sort(sortfunction);\n
\tfor (i = 0; i < len; ++i) {\n
\t\telem = selectedElements[i];\n
\t\tif (elem == null) {break;}\n
\t}\n
\t// use slice to quickly get the subset of elements we need\n
\tvar copiedElements = selectedElements.slice(0, i);\n
\tthis.clearSelection(true);\n
\t// note that we loop in the reverse way because of the way elements are added\n
\t// to the selectedElements array (top-first)\n
\ti = copiedElements.length;\n
\twhile (i--) {\n
\t\t// clone each element and replace it within copiedElements\n
\t\telem = copiedElements[i] = copyElem(copiedElements[i]);\n
\t\t(current_group || getCurrentDrawing().getCurrentLayer()).appendChild(elem);\n
\t\tbatchCmd.addSubCommand(new svgedit.history.InsertElementCommand(elem));\n
\t}\n
\t\n
\tif (!batchCmd.isEmpty()) {\n
\t\taddToSelection(copiedElements.reverse()); // Need to reverse for correct selection-adding\n
\t\tthis.moveSelectedElements(x, y, false);\n
\t\taddCommandToHistory(batchCmd);\n
\t}\n
};\n
\n
// Function: alignSelectedElements\n
// Aligns selected elements\n
//\n
// Parameters:\n
// type - String with single character indicating the alignment type\n
// relative_to - String that must be one of the following: \n
// "selected", "largest", "smallest", "page"\n
this.alignSelectedElements = function(type, relative_to) {\n
\tvar i, elem;\n
\tvar bboxes = [], angles = [];\n
\tvar minx = Number.MAX_VALUE, maxx = Number.MIN_VALUE, miny = Number.MAX_VALUE, maxy = Number.MIN_VALUE;\n
\tvar curwidth = Number.MIN_VALUE, curheight = Number.MIN_VALUE;\n
\tvar len = selectedElements.length;\n
\tif (!len) {return;}\n
\tfor (i = 0; i < len; ++i) {\n
\t\tif (selectedElements[i] == null) {break;}\n
\t\telem = selectedElements[i];\n
\t\tbboxes[i] = getStrokedBBox([elem]);\n
\t\t\n
\t\t// now bbox is axis-aligned and handles rotation\n
\t\tswitch (relative_to) {\n
\t\t\tcase \'smallest\':\n
\t\t\t\tif ( (type == \'l\' || type == \'c\' || type == \'r\') && (curwidth == Number.MIN_VALUE || curwidth > bboxes[i].width) ||\n
\t\t\t\t\t (type == \'t\' || type == \'m\' || type == \'b\') && (curheight == Number.MIN_VALUE || curheight > bboxes[i].height) ) {\n
\t\t\t\t\tminx = bboxes[i].x;\n
\t\t\t\t\tminy = bboxes[i].y;\n
\t\t\t\t\tmaxx = bboxes[i].x + bboxes[i].width;\n
\t\t\t\t\tmaxy = bboxes[i].y + bboxes[i].height;\n
\t\t\t\t\tcurwidth = bboxes[i].width;\n
\t\t\t\t\tcurheight = bboxes[i].height;\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase \'largest\':\n
\t\t\t\tif ( (type == \'l\' || type == \'c\' || type == \'r\') && (curwidth == Number.MIN_VALUE || curwidth < bboxes[i].width) ||\n
\t\t\t\t\t (type == \'t\' || type == \'m\' || type == \'b\') && (curheight == Number.MIN_VALUE || curheight < bboxes[i].height) ) {\n
\t\t\t\t\tminx = bboxes[i].x;\n
\t\t\t\t\tminy = bboxes[i].y;\n
\t\t\t\t\tmaxx = bboxes[i].x + bboxes[i].width;\n
\t\t\t\t\tmaxy = bboxes[i].y + bboxes[i].height;\n
\t\t\t\t\tcurwidth = bboxes[i].width;\n
\t\t\t\t\tcurheight = bboxes[i].height;\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tdefault: // \'selected\'\n
\t\t\t\tif (bboxes[i].x < minx) {minx = bboxes[i].x;}\n
\t\t\t\tif (bboxes[i].y < miny) {miny = bboxes[i].y;}\n
\t\t\t\tif (bboxes[i].x + bboxes[i].width > maxx) {maxx = bboxes[i].x + bboxes[i].width;}\n
\t\t\t\tif (bboxes[i].y + bboxes[i].height > maxy) {maxy = bboxes[i].y + bboxes[i].height;}\n
\t\t\t\tbreak;\n
\t\t}\n
\t} // loop for each element to find the bbox and adjust min/max\n
\n
\tif (relative_to == \'page\') {\n
\t\tminx = 0;\n
\t\tminy = 0;\n
\t\tmaxx = canvas.contentW;\n
\t\tmaxy = canvas.contentH;\n
\t}\n
\n
\tvar dx = new Array(len);\n
\tvar dy = new Array(len);\n
\tfor (i = 0; i < len; ++i) {\n
\t\tif (selectedElements[i] == null) {break;}\n
\t\telem = selectedElements[i];\n
\t\tvar bbox = bboxes[i];\n
\t\tdx[i] = 0;\n
\t\tdy[i] = 0;\n
\t\tswitch (type) {\n
\t\t\tcase \'l\': // left (horizontal)\n
\t\t\t\tdx[i] = minx - bbox.x;\n
\t\t\t\tbreak;\n
\t\t\tcase \'c\': // center (horizontal)\n
\t\t\t\tdx[i] = (minx+maxx)/2 - (bbox.x + bbox.width/2);\n
\t\t\t\tbreak;\n
\t\t\tcase \'r\': // right (horizontal)\n
\t\t\t\tdx[i] = maxx - (bbox.x + bbox.width);\n
\t\t\t\tbreak;\n
\t\t\tcase \'t\': // top (vertical)\n
\t\t\t\tdy[i] = miny - bbox.y;\n
\t\t\t\tbreak;\n
\t\t\tcase \'m\': // middle (vertical)\n
\t\t\t\tdy[i] = (miny+maxy)/2 - (bbox.y + bbox.height/2);\n
\t\t\t\tbreak;\n
\t\t\tcase \'b\': // bottom (vertical)\n
\t\t\t\tdy[i] = maxy - (bbox.y + bbox.height);\n
\t\t\t\tbreak;\n
\t\t}\n
\t}\n
\tthis.moveSelectedElements(dx, dy);\n
};\n
\n
// Group: Additional editor tools\n
\n
this.contentW = getResolution().w;\n
this.contentH = getResolution().h;\n
\n
// Function: updateCanvas\n
// Updates the editor canvas width/height/position after a zoom has occurred \n
//\n
// Parameters:\n
// w - Float with the new width\n
// h - Float with the new height\n
//\n
// Returns: \n
// Object with the following values:\n
// * x - The canvas\' new x coordinate\n
// * y - The canvas\' new y coordinate\n
// * old_x - The canvas\' old x coordinate\n
// * old_y - The canvas\' old y coordinate\n
// * d_x - The x position difference\n
// * d_y - The y position difference\n
this.updateCanvas = function(w, h) {\n
\tsvgroot.setAttribute("width", w);\n
\tsvgroot.setAttribute("height", h);\n
\tvar bg = $(\'#canvasBackground\')[0];\n
\tvar old_x = svgcontent.getAttribute(\'x\');\n
\tvar old_y = svgcontent.getAttribute(\'y\');\n
\tvar x = (w/2 - this.contentW*current_zoom/2);\n
\tvar y = (h/2 - this.contentH*current_zoom/2);\n
\n
\tsvgedit.utilities.assignAttributes(svgcontent, {\n
\t\twidth: this.contentW*current_zoom,\n
\t\theight: this.contentH*current_zoom,\n
\t\t\'x\': x,\n
\t\t\'y\': y,\n
\t\t"viewBox" : "0 0 " + this.contentW + " " + this.contentH\n
\t});\n
\t\n
\tsvgedit.utilities.assignAttributes(bg, {\n
\t\twidth: svgcontent.getAttribute(\'width\'),\n
\t\theight: svgcontent.getAttribute(\'height\'),\n
\t\tx: x,\n
\t\ty: y\n
\t});\n
\n
\tvar bg_img = svgedit.utilities.getElem(\'background_image\');\n
\tif (bg_img) {\n
\t\tsvgedit.utilities.assignAttributes(bg_img, {\n
\t\t\t\'width\': \'100%\',\n
\t\t\t\'height\': \'100%\'\n
\t\t});\n
\t}\n
\t\n
\tselectorManager.selectorParentGroup.setAttribute("transform", "translate(" + x + "," + y + ")");\n
\t runExtensions("canvasUpdated",{new_x:x, new_y:y, old_x:old_x, old_y:old_y, d_x:x - old_x, d_y:y - old_y});\n
\treturn {x:x, y:y, old_x:old_x, old_y:old_y, d_x:x - old_x, d_y:y - old_y};\n
};\n
\n
// Function: setBackground\n
// Set the background of the editor (NOT the actual document)\n
//\n
// Parameters:\n
// color - String with fill color to apply\n
// url - URL or path to image to use\n
this.setBackground = function(color, url) {\n
\tvar bg = svgedit.utilities.getElem(\'canvasBackground\');\n
\tvar border = $(bg).find(\'rect\')[0];\n
\tvar bg_img = svgedit.utilities.getElem(\'background_image\');\n
\tborder.setAttribute(\'fill\', color);\n
\tif (url) {\n
\t\tif (!bg_img) {\n
\t\t\tbg_img = svgdoc.createElementNS(NS.SVG, "image");\n
\t\t\tsvgedit.utilities.assignAttributes(bg_img, {\n
\t\t\t\t\'id\': \'background_image\',\n
\t\t\t\t\'width\': \'100%\',\n
\t\t\t\t\'height\': \'100%\',\n
\t\t\t\t\'preserveAspectRatio\': \'xMinYMin\',\n
\t\t\t\t\'style\':\'pointer-events:none\'\n
\t\t\t});\n
\t\t}\n
\t\tsetHref(bg_img, url);\n
\t\tbg.appendChild(bg_img);\n
\t} else if (bg_img) {\n
\t\tbg_img.parentNode.removeChild(bg_img);\n
\t}\n
};\n
\n
// Function: cycleElement\n
// Select the next/previous element within the current layer\n
//\n
// Parameters:\n
// next - Boolean where true = next and false = previous element\n
this.cycleElement = function(next) {\n
\tvar num;\n
\tvar cur_elem = selectedElements[0];\n
\tvar elem = false;\n
\tvar all_elems = getVisibleElements(current_group || getCurrentDrawing().getCurrentLayer());\n
\tif (!all_elems.length) {return;}\n
\tif (cur_elem == null) {\n
\t\tnum = next?all_elems.length-1:0;\n
\t\telem = all_elems[num];\n
\t} else {\n
\t\tvar i = all_elems.length;\n
\t\twhile (i--) {\n
\t\t\tif (all_elems[i] == cur_elem) {\n
\t\t\t\tnum = next ? i - 1 : i + 1;\n
\t\t\t\tif (num >= all_elems.length) {\n
\t\t\t\t\tnum = 0;\n
\t\t\t\t} else if (num < 0) {\n
\t\t\t\t\tnum = all_elems.length-1;\n
\t\t\t\t} \n
\t\t\t\telem = all_elems[num];\n
\t\t\t\tbreak;\n
\t\t\t} \n
\t\t}\n
\t}\t\t\n
\tselectOnly([elem], true);\n
\tcall("selected", selectedElements);\n
};\n
\n
this.clear();\n
\n
\n
// DEPRECATED: getPrivateMethods \n
// Since all methods are/should be public somehow, this function should be removed\n
\n
// Being able to access private methods publicly seems wrong somehow,\n
// but currently appears to be the best way to allow testing and provide\n
// access to them to plugins.\n
this.getPrivateMethods = function() {\n
\tvar obj = {\n
\t\taddCommandToHistory: addCommandToHistory,\n
\t\tsetGradient: setGradient,\n
\t\taddSvgElementFromJson: addSvgElementFromJson,\n
\t\tassignAttributes: assignAttributes,\n
\t\tBatchCommand: BatchCommand,\n
\t\tcall: call,\n
\t\tChangeElementCommand: ChangeElementCommand,\n
\t\tcopyElem: copyElem,\n
\t\tffClone: ffClone,\n
\t\tfindDefs: findDefs,\n
\t\tfindDuplicateGradient: findDuplicateGradient,\n
\t\tgetElem: getElem,\n
\t\tgetId: getId,\n
\t\tgetIntersectionList: getIntersectionList,\n
\t\tgetMouseTarget: getMouseTarget,\n
\t\tgetNextId: getNextId,\n
\t\tgetPathBBox: getPathBBox,\n
\t\tgetUrlFromAttr: getUrlFromAttr,\n
\t\thasMatrixTransform: hasMatrixTransform,\n
\t\tidentifyLayers: identifyLayers,\n
\t\tInsertElementCommand: InsertElementCommand,\n
\t\tisIdentity: svgedit.math.isIdentity,\n
\t\tlogMatrix: logMatrix,\n
\t\tmatrixMultiply: matrixMultiply,\n
\t\tMoveElementCommand: MoveElementCommand,\n
\t\tpreventClickDefault: preventClickDefault,\n
\t\trecalculateAllSelectedDimensions: recalculateAllSelectedDimensions,\n
\t\trecalculateDimensions: recalculateDimensions,\n
\t\tremapElement: remapElement,\n
\t\tRemoveElementCommand: RemoveElementCommand,\n
\t\tremoveUnusedDefElems: removeUnusedDefElems,\n
\t\tround: round,\n
\t\trunExtensions: runExtensions,\n
\t\tsanitizeSvg: sanitizeSvg,\n
\t\tSVGEditTransformList: svgedit.transformlist.SVGTransformList,\n
\t\ttoString: toString,\n
\t\ttransformBox: svgedit.math.transformBox,\n
\t\ttransformListToTransform: transformListToTransform,\n
\t\ttransformPoint: transformPoint,\n
\t\twalkTree: svgedit.utilities.walkTree\n
\t};\n
\treturn obj;\n
};\n
\n
};\n


]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <none/>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
