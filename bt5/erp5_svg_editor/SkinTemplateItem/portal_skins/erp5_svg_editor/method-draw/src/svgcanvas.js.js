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
            <value> <string>ts52852016.04</string> </value>
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
            <value> <int>286891</int> </value>
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

/*\n
 * svgcanvas.js\n
 *\n
 * Licensed under the Apache License, Version 2\n
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
\n
/*jslint browser: true*/\n
\n
if(!window.console) {\n
  window.console = {};\n
  window.console.log = function(str) {};\n
  window.console.dir = function(str) {};\n
}\n
\n
if(window.opera) {\n
  window.console.log = function(str) { opera.postError(str); };\n
  window.console.dir = function(str) {};\n
}\n
\n
(function() {\n
\n
  // This fixes $(...).attr() to work as expected with SVG elements.\n
  // Does not currently use *AttributeNS() since we rarely need that.\n
  \n
  // See http://api.jquery.com/attr/ for basic documentation of .attr()\n
  \n
  // Additional functionality: \n
  // - When getting attributes, a string that\'s a number is return as type number.\n
  // - If an array is supplied as first parameter, multiple values are returned\n
  // as an object with values for each given attributes\n
\n
  var proxied = jQuery.fn.attr, svgns = "http://www.w3.org/2000/svg";\n
  jQuery.fn.attr = function(key, value) {\n
    var len = this.length;\n
    if(!len) return proxied.apply(this, arguments);\n
    for(var i=0; i<len; i++) {\n
      var elem = this[i];\n
      // set/get SVG attribute\n
      if(elem.namespaceURI === svgns) {\n
        // Setting attribute\n
        if(value !== undefined) {\n
          elem.setAttribute(key, value);\n
        } else if($.isArray(key)) {\n
          // Getting attributes from array\n
          var j = key.length, obj = {};\n
\n
          while(j--) {\n
            var aname = key[j];\n
            var attr = elem.getAttribute(aname);\n
            // This returns a number when appropriate\n
            if(attr || attr === "0") {\n
              attr = isNaN(attr)?attr:attr-0;\n
            }\n
            obj[aname] = attr;\n
          }\n
          return obj;\n
        \n
        } else if(typeof key === "object") {\n
          // Setting attributes form object\n
          for(var v in key) {\n
            elem.setAttribute(v, key[v]);\n
          }\n
        // Getting attribute\n
        } else {\n
          var attr = elem.getAttribute(key);\n
          if(attr || attr === "0") {\n
            attr = isNaN(attr)?attr:attr-0;\n
          }\n
\n
          return attr;\n
        }\n
      } else {\n
        return proxied.apply(this, arguments);\n
      }\n
    }\n
    return this;\n
  };\n
  \n
}());\n
\n
// Class: SvgCanvas\n
// The main SvgCanvas class that manages all SVG-related functions\n
//\n
// Parameters:\n
// container - The container HTML element that should hold the SVG root element\n
// config - An object that contains configuration data\n
$.SvgCanvas = function(container, config)\n
{\n
// Namespace constants\n
var svgns = "http://www.w3.org/2000/svg",\n
  xlinkns = "http://www.w3.org/1999/xlink",\n
  xmlns = "http://www.w3.org/XML/1998/namespace",\n
  xmlnsns = "http://www.w3.org/2000/xmlns/", // see http://www.w3.org/TR/REC-xml-names/#xmlReserved\n
  se_ns = "http://svg-edit.googlecode.com",\n
  htmlns = "http://www.w3.org/1999/xhtml",\n
  mathns = "http://www.w3.org/1998/Math/MathML";\n
\n
// Default configuration options\n
var curConfig = {\n
  show_outside_canvas: true,\n
  selectNew: true,\n
  dimensions: [640, 480]\n
};\n
\n
// Update config with new one if given\n
if(config) {\n
  $.extend(curConfig, config);\n
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
    \'<svg id="svgroot" xmlns="\' + svgns + \'" xlinkns="\' + xlinkns + \'" \' +\n
      \'width="\' + dimensions[0] + \'" height="\' + dimensions[1] + \'" x="\' + dimensions[0] + \'" y="\' + dimensions[1] + \'" overflow="visible">\' +\n
      \'<defs>\' +\n
        \'<filter id="canvashadow" filterUnits="objectBoundingBox">\' +\n
          \'<feGaussianBlur in="SourceAlpha" stdDeviation="4" result="blur"/>\'+\n
          \'<feOffset in="blur" dx="5" dy="5" result="offsetBlur"/>\'+\n
          \'<feMerge>\'+\n
            \'<feMergeNode in="offsetBlur"/>\'+\n
            \'<feMergeNode in="SourceGraphic"/>\'+\n
          \'</feMerge>\'+\n
        \'</filter>\'+\n
      \'</defs>\'+\n
    \'</svg>\').documentElement, true);\n
container.appendChild(svgroot);\n
\n
// The actual element that represents the final output SVG element\n
var svgcontent = svgdoc.createElementNS(svgns, "svg");\n
\n
// This function resets the svgcontent element while keeping it in the DOM.\n
var clearSvgContentElement = canvas.clearSvgContentElement = function() {\n
  while (svgcontent.firstChild) { svgcontent.removeChild(svgcontent.firstChild); }\n
\n
  // TODO: Clear out all other attributes first?\n
  $(svgcontent).attr({\n
    id: \'svgcontent\',\n
    width: dimensions[0],\n
    height: dimensions[1],\n
    x: dimensions[0],\n
    y: dimensions[1],\n
    overflow: curConfig.show_outside_canvas ? \'visible\' : \'hidden\',\n
    xmlns: svgns,\n
    "xmlns:se": se_ns,\n
    "xmlns:xlink": xlinkns\n
  }).appendTo(svgroot);\n
\n
  // TODO: make this string optional and set by the client\n
  var comment = svgdoc.createComment(" Created with Method Draw - http://github.com/duopixel/Method-Draw/ ");\n
  svgcontent.appendChild(comment);\n
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
  idprefix = p;\n
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
  return canvas.current_drawing_;\n
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
  shape: {\n
    fill: (curConfig.initFill.color == \'none\' ? \'\' : \'#\') + curConfig.initFill.color,\n
    fill_paint: null,\n
    fill_opacity: curConfig.initFill.opacity,\n
    stroke: "#" + curConfig.initStroke.color,\n
    stroke_paint: null,\n
    stroke_opacity: curConfig.initStroke.opacity,\n
    stroke_width: curConfig.initStroke.width,\n
    stroke_dasharray: \'none\',\n
    opacity: curConfig.initOpacity\n
  }\n
};\n
\n
all_properties.text = $.extend(true, {}, all_properties.shape);\n
$.extend(all_properties.text, {\n
  fill: "#000000",\n
  stroke_width: 0,\n
  font_size: 24,\n
  font_family: \'Helvetica, Arial, sans-serif\'\n
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
  var shape = svgedit.utilities.getElem(data.attr.id);\n
  // if shape is a path but we need to create a rect/ellipse, then remove the path\n
  var current_layer = getCurrentDrawing().getCurrentLayer();\n
  if (shape && data.element != shape.tagName) {\n
    current_layer.removeChild(shape);\n
    shape = null;\n
  }\n
  if (!shape) {\n
    shape = svgdoc.createElementNS(svgns, data.element);\n
    if (current_layer) {\n
      (current_group || current_layer).appendChild(shape);\n
    }\n
  }\n
  if(data.curStyles) {\n
    svgedit.utilities.assignAttributes(shape, {\n
      "fill": cur_shape.fill,\n
      "stroke": cur_shape.stroke,\n
      "stroke-width": cur_shape.stroke_width,\n
      "stroke-dasharray": cur_shape.stroke_dasharray,\n
      "stroke-opacity": cur_shape.stroke_opacity,\n
      "fill-opacity": cur_shape.fill_opacity,\n
      "opacity": cur_shape.opacity / 2,\n
      "style": "pointer-events:inherit"\n
    }, 100);\n
  }\n
  svgedit.utilities.assignAttributes(shape, data.attr, 100);\n
  svgedit.utilities.cleanupElement(shape);\n
  return shape;\n
};\n
\n
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
  getBaseUnit: function() { return curConfig.baseUnit; },\n
  getElement: svgedit.utilities.getElem,\n
  getHeight: function() { return svgcontent.getAttribute("height")/current_zoom; },\n
  getWidth: function() { return svgcontent.getAttribute("width")/current_zoom; },\n
  getRoundDigits: function() { return save_options.round_digits; }\n
});\n
// import from units.js\n
var convertToNum = canvas.convertToNum = svgedit.units.convertToNum;\n
\n
// import from svgutils.js\n
svgedit.utilities.init({\n
  getDOMDocument: function() { return svgdoc; },\n
  getDOMContainer: function() { return container; },\n
  getSVGRoot: function() { return svgroot; },\n
  // TODO: replace this mostly with a way to get the current drawing.\n
  getSelectedElements: function() { return selectedElements; },\n
  getSVGContent: function() { return svgcontent; }\n
});\n
var getUrlFromAttr = canvas.getUrlFromAttr = svgedit.utilities.getUrlFromAttr;\n
var getHref = canvas.getHref = svgedit.utilities.getHref;\n
var setHref = canvas.setHref = svgedit.utilities.setHref;\n
var getPathBBox = svgedit.utilities.getPathBBox;\n
var getBBox = canvas.getBBox = svgedit.utilities.getBBox;\n
var getRotationAngle = canvas.getRotationAngle = svgedit.utilities.getRotationAngle;\n
var getElem = canvas.getElem = svgedit.utilities.getElem;\n
var assignAttributes = canvas.assignAttributes = svgedit.utilities.assignAttributes;\n
var cleanupElement = this.cleanupElement = svgedit.utilities.cleanupElement;\n
\n
// import from sanitize.js\n
var nsMap = svgedit.sanitize.getNSMap();\n
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
  handleHistoryEvent: function(eventType, cmd) {\n
    var EventTypes = svgedit.history.HistoryEventTypes;\n
    // TODO: handle setBlurOffsets.\n
    if (eventType == EventTypes.BEFORE_UNAPPLY || eventType == EventTypes.BEFORE_APPLY) {\n
      canvas.clearSelection();\n
    } else if (eventType == EventTypes.AFTER_APPLY || eventType == EventTypes.AFTER_UNAPPLY) {\n
      var elems = cmd.elements();\n
      canvas.pathActions.clear();\n
      call("changed", elems);\n
      \n
      var cmdType = cmd.type();\n
      var isApply = (eventType == EventTypes.AFTER_APPLY);\n
      if (cmdType == MoveElementCommand.type()) {\n
        var parent = isApply ? cmd.newParent : cmd.oldParent;\n
        if (parent == svgcontent) {\n
          canvas.identifyLayers();\n
        }\n
      } else if (cmdType == InsertElementCommand.type() ||\n
          cmdType == RemoveElementCommand.type()) {\n
        if (cmd.parent == svgcontent) {\n
          canvas.identifyLayers();\n
        }\n
        if (cmdType == InsertElementCommand.type()) {\n
          if (isApply) restoreRefElems(cmd.elem);\n
        } else {\n
          if (!isApply) restoreRefElems(cmd.elem);\n
        }\n
        \n
        if(cmd.elem.tagName === \'use\') {\n
          setUseData(cmd.elem);\n
        }\n
      } else if (cmdType == ChangeElementCommand.type()) {\n
        // if we are changing layer names, re-identify all layers\n
        if (cmd.elem.tagName == "title" && cmd.elem.parentNode.parentNode == svgcontent) {\n
          canvas.identifyLayers();\n
        }\n
        var values = isApply ? cmd.newValues : cmd.oldValues;\n
        // If stdDeviation was changed, update the blur.\n
        if (values["stdDeviation"]) {\n
          canvas.setBlurOffsets(cmd.elem.parentNode, values["stdDeviation"]);\n
        }\n
        \n
        // Remove & Re-add hack for Webkit (issue 775) \n
        //if(cmd.elem.tagName === \'use\' && svgedit.browser.isWebkit()) {\n
        //  var elem = cmd.elem;\n
        //  if(!elem.getAttribute(\'x\') && !elem.getAttribute(\'y\')) {\n
        //    var parent = elem.parentNode;\n
        //    var sib = elem.nextSibling;\n
        //    parent.removeChild(elem);\n
        //    parent.insertBefore(elem, sib);\n
        //  }\n
        //}\n
      }\n
    }\n
  }\n
});\n
var addCommandToHistory = function(cmd) {\n
  canvas.undoMgr.addCommandToHistory(cmd);\n
};\n
\n
// import from select.js\n
svgedit.select.init(curConfig, {\n
  createSVGElement: function(jsonMap) { return canvas.addSvgElementFromJson(jsonMap); },\n
  svgRoot: function() { return svgroot; },\n
  svgContent: function() { return svgcontent; },\n
  currentZoom: function() { return current_zoom; },\n
  // TODO(codedread): Remove when getStrokedBBox() has been put into svgutils.js.\n
  getStrokedBBox: function(elems) { return canvas.getStrokedBBox([elems]); }\n
});\n
// this object manages selectors for us\n
var selectorManager = this.selectorManager = svgedit.select.getSelectorManager();\n
// this object manages selectors for us\n
\n
// Import from path.js\n
svgedit.path.init({\n
  getCurrentZoom: function() { return current_zoom; },\n
  getSVGRoot: function() { return svgroot; }\n
});\n
\n
// Function: snapToGrid\n
// round value to for snapping\n
// NOTE: This function did not move to svgutils.js since it depends on curConfig.\n
svgedit.utilities.snapToGrid = function(value){\n
  var stepSize = curConfig.snappingStep;\n
  var unit = curConfig.baseUnit;\n
  if(unit !== "px") {\n
  stepSize *= svgedit.units.getTypeMap()[unit];\n
  }\n
  value = Math.round(value/stepSize)*stepSize;\n
  return value;\n
};\n
var snapToGrid = svgedit.utilities.snapToGrid;\n
\n
// Interface strings, usually for title elements\n
var uiStrings = {\n
  "exportNoBlur": "Blurred elements will appear as un-blurred",\n
  "exportNoforeignObject": "foreignObject elements will not appear",\n
  "exportNoDashArray": "Strokes will appear filled",\n
  "exportNoText": "Text may not appear as expected"\n
};\n
\n
var visElems = \'a,circle,ellipse,foreignObject,g,image,line,path,polygon,polyline,rect,svg,text,tspan,use\';\n
var ref_attrs = ["clip-path", "fill", "filter", "marker-end", "marker-mid", "marker-start", "mask", "stroke"];\n
\n
var elData = $.data;\n
\n
// Animation element to change the opacity of any newly created element\n
var opac_ani = false; //document.createElementNS(svgns, \'animate\');\n
//$(opac_ani).attr({\n
//  attributeName: \'opacity\',\n
//  begin: \'indefinite\',\n
//  dur: 0,\n
//  fill: \'freeze\'\n
//}).appendTo(svgroot);\n
\n
var restoreRefElems = function(elem) {\n
  // Look for missing reference elements, restore any found\n
  var attrs = $(elem).attr(ref_attrs);\n
  for(var o in attrs) {\n
    var val = attrs[o];\n
    if (val && val.indexOf(\'url(\') === 0) {\n
      var id = getUrlFromAttr(val).substr(1);\n
      var ref = getElem(id);\n
      if(!ref) {\n
        findDefs().appendChild(removedElements[id]);\n
        delete removedElements[id];\n
      }\n
    }\n
  }\n
  \n
  var childs = elem.getElementsByTagName(\'*\');\n
  \n
  if(childs.length) {\n
    for(var i = 0, l = childs.length; i < l; i++) {\n
      restoreRefElems(childs[i]);\n
    }\n
  }\n
};\n
\n
(function() {\n
  // TODO For Issue 208: this is a start on a thumbnail\n
  //  var svgthumb = svgdoc.createElementNS(svgns, "use");\n
  //  svgthumb.setAttribute(\'width\', \'100\');\n
  //  svgthumb.setAttribute(\'height\', \'100\');\n
  //  svgedit.utilities.setHref(svgthumb, \'#svgcontent\');\n
  //  svgroot.appendChild(svgthumb);\n
\n
})();\n
\n
// Object to contain image data for raster images that were found encodable\n
var encodableImages = {},\n
  \n
  // String with image URL of last loadable image\n
  last_good_img_url = curConfig.imgPath + \'logo.png\',\n
  \n
  // Array with current disabled elements (for in-group editing)\n
  disabled_elems = [],\n
  \n
  // Object with save options\n
  save_options = {round_digits: 5},\n
  \n
  // Boolean indicating whether or not a draw action has been started\n
  started = false,\n
  \n
  // String with an element\'s initial transform attribute value\n
  start_transform = null,\n
  \n
  // String indicating the current editor mode\n
  current_mode = "select",\n
  \n
  // String with the current direction in which an element is being resized\n
  current_resize_mode = "none",\n
  \n
  // Object with IDs for imported files, to see if one was already added\n
  import_ids = {};\n
\n
// Current text style properties\n
var cur_text = all_properties.text,\n
  \n
  // Current general properties\n
  cur_properties = cur_shape,\n
  \n
  // Array with selected elements\' Bounding box object\n
//  selectedBBoxes = new Array(1),\n
  \n
  // The DOM element that was just selected\n
  justSelected = null,\n
  \n
  // DOM element for selection rectangle drawn by the user\n
  rubberBox = null,\n
  \n
  // Array of current BBoxes (still needed?)\n
  curBBoxes = [],\n
  \n
  // Object to contain all included extensions\n
  extensions = {},\n
  \n
  // Canvas point for the most recent right click\n
  lastClickPoint = null,\n
  \n
  // Map of deleted reference elements\n
  removedElements = {}\n
\n
// Clipboard for cut, copy&pasted elements\n
canvas.clipBoard = [];\n
\n
// Should this return an array by default, so extension results aren\'t overwritten?\n
var runExtensions = this.runExtensions = function(action, vars, returnArray) {\n
  var result = false;\n
  if(returnArray) result = [];\n
  $.each(extensions, function(name, opts) {\n
    if(action in opts) {\n
      if(returnArray) {\n
        result.push(opts[action](vars))\n
      } else {\n
        result = opts[action](vars);\n
      }\n
    }\n
  });\n
  return result;\n
}\n
\n
\n
// Function: addExtension\n
// Add an extension to the editor\n
// \n
// Parameters:\n
// name - String with the ID of the extension\n
// ext_func - Function supplied by the extension with its data\n
this.addExtension = function(name, ext_func) {\n
  if(!(name in extensions)) {\n
    // Provide private vars/funcs here. Is there a better way to do this?\n
    \n
    if($.isFunction(ext_func)) {\n
    var ext = ext_func($.extend(canvas.getPrivateMethods(), {\n
      svgroot: svgroot,\n
      svgcontent: svgcontent,\n
      nonce: getCurrentDrawing().getNonce(),\n
      selectorManager: selectorManager\n
    }));\n
    } else {\n
      var ext = ext_func;\n
    }\n
    extensions[name] = ext;\n
    call("extension_added", ext);\n
  } else {\n
    console.log(\'Cannot add extension "\' + name + \'", an extension by that name already exists"\');\n
  }\n
};\n
  \n
// This method rounds the incoming value to the nearest value based on the current_zoom\n
var round = this.round = function(val) {\n
  return parseInt(val*current_zoom)/current_zoom;\n
};\n
\n
// This method sends back an array or a NodeList full of elements that\n
// intersect the multi-select rubber-band-box on the current_layer only.\n
// \n
// Since the only browser that supports the SVG DOM getIntersectionList is Opera, \n
// we need to provide an implementation here.  We brute-force it for now.\n
// \n
// Reference:\n
// Firefox does not implement getIntersectionList(), see https://bugzilla.mozilla.org/show_bug.cgi?id=501421\n
// Webkit does not implement getIntersectionList(), see https://bugs.webkit.org/show_bug.cgi?id=11274\n
var getIntersectionList = this.getIntersectionList = function(rect) {\n
  if (rubberBox == null) { return null; }\n
\n
  var parent = current_group || getCurrentDrawing().getCurrentLayer();\n
  \n
  if(!curBBoxes.length) {\n
    // Cache all bboxes\n
    curBBoxes = getVisibleElementsAndBBoxes(parent);\n
  }\n
  \n
  var resultList = null;\n
  try {\n
    resultList = parent.getIntersectionList(rect, null);\n
  } catch(e) { }\n
\n
  if (resultList == null || typeof(resultList.item) != "function") {\n
    resultList = [];\n
    \n
    if(!rect) {\n
      var rubberBBox = rubberBox.getBBox();\n
      var bb = {};\n
      \n
      for(var o in rubberBBox) {\n
        bb[o] = rubberBBox[o] / current_zoom;\n
      }\n
      rubberBBox = bb;\n
      \n
    } else {\n
      var rubberBBox = rect;\n
    }\n
    var i = curBBoxes.length;\n
    while (i--) {\n
      if(!rubberBBox.width || !rubberBBox.width) continue;\n
      if (svgedit.math.rectsIntersect(rubberBBox, curBBoxes[i].bbox))  {\n
        resultList.push(curBBoxes[i].elem);\n
      }\n
    }\n
  }\n
  // addToSelection expects an array, but it\'s ok to pass a NodeList \n
  // because using square-bracket notation is allowed: \n
  // http://www.w3.org/TR/DOM-Level-2-Core/ecma-script-binding.html\n
  return resultList;\n
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
  if(!elems) elems = getVisibleElements();\n
  if(!elems.length) return false;\n
  \n
  // Make sure the expected BBox is returned if the element is a group\n
  var getCheckedBBox = function(elem) {\n
  \n
    try {\n
      // TODO: Fix issue with rotated groups. Currently they work\n
      // fine in FF, but not in other browsers (same problem mentioned\n
      // in Issue 339 comment #2).\n
      \n
      var bb = svgedit.utilities.getBBox(elem);\n
      \n
      var angle = svgedit.utilities.getRotationAngle(elem);\n
      if ((angle && angle % 90) ||\n
          svgedit.math.hasMatrixTransform(svgedit.transformlist.getTransformList(elem))) {\n
        // Accurate way to get BBox of rotated element in Firefox:\n
        // Put element in group and get its BBox\n
        \n
        var good_bb = false;\n
        \n
        // Get the BBox from the raw path for these elements\n
        var elemNames = [\'ellipse\',\'path\',\'line\',\'polyline\',\'polygon\'];\n
        if(elemNames.indexOf(elem.tagName) >= 0) {\n
          bb = good_bb = canvas.convertToPath(elem, true);\n
        } else if(elem.tagName == \'rect\') {\n
          // Look for radius\n
          var rx = elem.getAttribute(\'rx\');\n
          var ry = elem.getAttribute(\'ry\');\n
          if(rx || ry) {\n
            bb = good_bb = canvas.convertToPath(elem, true);\n
          }\n
        }\n
        \n
        if(!good_bb) {\n
          // Must use clone else FF freaks out\n
          var clone = elem.cloneNode(true); \n
          var g = document.createElementNS(svgns, "g");\n
          var parent = elem.parentNode;\n
          parent.appendChild(g);\n
          g.appendChild(clone);\n
          bb = svgedit.utilities.bboxToObj(g.getBBox());\n
          parent.removeChild(g);\n
        }\n
        \n
\n
        // Old method: Works by giving the rotated BBox,\n
        // this is (unfortunately) what Opera and Safari do\n
        // natively when getting the BBox of the parent group\n
//            var angle = angle * Math.PI / 180.0;\n
//            var rminx = Number.MAX_VALUE, rminy = Number.MAX_VALUE, \n
//              rmaxx = Number.MIN_VALUE, rmaxy = Number.MIN_VALUE;\n
//            var cx = round(bb.x + bb.width/2),\n
//              cy = round(bb.y + bb.height/2);\n
//            var pts = [ [bb.x - cx, bb.y - cy], \n
//                  [bb.x + bb.width - cx, bb.y - cy],\n
//                  [bb.x + bb.width - cx, bb.y + bb.height - cy],\n
//                  [bb.x - cx, bb.y + bb.height - cy] ];\n
//            var j = 4;\n
//            while (j--) {\n
//              var x = pts[j][0],\n
//                y = pts[j][1],\n
//                r = Math.sqrt( x*x + y*y );\n
//              var theta = Math.atan2(y,x) + angle;\n
//              x = round(r * Math.cos(theta) + cx);\n
//              y = round(r * Math.sin(theta) + cy);\n
//    \n
//              // now set the bbox for the shape after it\'s been rotated\n
//              if (x < rminx) rminx = x;\n
//              if (y < rminy) rminy = y;\n
//              if (x > rmaxx) rmaxx = x;\n
//              if (y > rmaxy) rmaxy = y;\n
//            }\n
//            \n
//            bb.x = rminx;\n
//            bb.y = rminy;\n
//            bb.width = rmaxx - rminx;\n
//            bb.height = rmaxy - rminy;\n
      }\n
      return bb;\n
    } catch(e) { \n
      console.log(elem, e);\n
    } \n
  };\n
\n
  var full_bb;\n
  $.each(elems, function() {\n
    if(full_bb) return;\n
    if(!this.parentNode) return;\n
    full_bb = getCheckedBBox(this);\n
  });\n
  \n
  // This shouldn\'t ever happen...\n
  if(full_bb == null) return null;\n
  \n
  // full_bb doesn\'t include the stoke, so this does no good!\n
//    if(elems.length == 1) return full_bb;\n
  \n
  var max_x = full_bb.x + full_bb.width;\n
  var max_y = full_bb.y + full_bb.height;\n
  var min_x = full_bb.x;\n
  var min_y = full_bb.y;\n
  \n
  // FIXME: same re-creation problem with this function as getCheckedBBox() above\n
  var getOffset = function(elem) {\n
    var sw = elem.getAttribute("stroke-width");\n
    var offset = 0;\n
    if (elem.getAttribute("stroke") != "none" && !isNaN(sw)) {\n
      offset += sw/2;\n
    }\n
    return offset;\n
  }\n
  var bboxes = [];\n
  $.each(elems, function(i, elem) {\n
    var cur_bb = getCheckedBBox(elem);\n
    if(cur_bb) {\n
      var offset = getOffset(elem);\n
      min_x = Math.min(min_x, cur_bb.x - offset);\n
      min_y = Math.min(min_y, cur_bb.y - offset);\n
      bboxes.push(cur_bb);\n
    }\n
  });\n
  \n
  full_bb.x = min_x;\n
  full_bb.y = min_y;\n
  \n
  $.each(elems, function(i, elem) {\n
    var cur_bb = bboxes[i];\n
    // ensure that elem is really an element node\n
    if (cur_bb && elem.nodeType == 1) {\n
      var offset = getOffset(elem);\n
      max_x = Math.max(max_x, cur_bb.x + cur_bb.width + offset);\n
      max_y = Math.max(max_y, cur_bb.y + cur_bb.height + offset);\n
    }\n
  });\n
  \n
  full_bb.width = max_x - min_x;\n
  full_bb.height = max_y - min_y;\n
  return full_bb;\n
}\n
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
  if(!parent) parent = $(svgcontent).children(); // Prevent layers from being included\n
  if (parent.find("#canvas_background").length) parent.splice(0, 1) // Prevent background from being included\n
  var contentElems = [];\n
  $(parent).children().each(function(i, elem) {\n
    try {\n
      if (elem.getBBox()) {\n
        contentElems.push(elem);\n
      }\n
    } catch(e) {}\n
  });\n
  return contentElems.reverse();\n
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
  if(!parent) parent = $(svgcontent).children(); // Prevent layers from being included\n
  \n
  var contentElems = [];\n
  $(parent).children().each(function(i, elem) {\n
    try {\n
      if (elem.getBBox()) {\n
        contentElems.push({\'elem\':elem, \'bbox\':getStrokedBBox([elem])});\n
      }\n
    } catch(e) {}\n
  });\n
  return contentElems.reverse();\n
};\n
\n
// Function: groupSvgElem\n
// Wrap an SVG element into a group element, mark the group as \'gsvg\'\n
//\n
// Parameters:\n
// elem - SVG element to wrap\n
var groupSvgElem = this.groupSvgElem = function(elem) {\n
  var g = document.createElementNS(svgns, "g");\n
  elem.parentNode.replaceChild(g, elem);\n
  $(g).append(elem).data(\'gsvg\', elem)[0].id = getNextId();\n
}\n
\n
// Function: copyElem\n
// Create a clone of an element, updating its ID and its children\'s IDs when needed\n
//\n
// Parameters:\n
// el - DOM element to clone\n
//\n
// Returns: The cloned element\n
var copyElem = function(el) {\n
  var new_el = document.createElementNS(el.namespaceURI, el.nodeName);\n
  // set the copied element\'s new id\n
  new_el.removeAttribute("id");\n
  // manually create a copy of the element\n
  $.each(el.attributes, function(i, attr) {\n
    if (attr.localName != \'-moz-math-font-style\') {\n
      new_el.setAttributeNS(attr.namespaceURI, attr.nodeName, attr.nodeValue);\n
    }\n
  });\n
  \n
  // Opera\'s "d" value needs to be reset for Opera/Win/non-EN\n
  // Also needed for webkit (else does not keep curved segments on clone)\n
  if(svgedit.browser.isWebkit() && el.nodeName == \'path\') {\n
    var fixed_d = pathActions.convertPath(el);\n
    new_el.setAttribute(\'d\', fixed_d);\n
  }\n
\n
  // now create copies of all children\n
  $.each(el.childNodes, function(i, child) {\n
    switch(child.nodeType) {\n
      case 1: // element node\n
        new_el.appendChild(copyElem(child));\n
        break;\n
      case 3: // text node\n
        new_el.textContent = child.nodeValue;\n
        break;\n
      default:\n
        break;\n
    }\n
  });\n
  \n
  if($(el).data(\'gsvg\')) {\n
    $(new_el).data(\'gsvg\', new_el.firstChild);\n
  } else if($(el).data(\'symbol\')) {\n
    var ref = $(el).data(\'symbol\');\n
    $(new_el).data(\'ref\', ref).data(\'symbol\', ref);\n
  }\n
  else if(new_el.tagName == \'image\') {\n
    preventClickDefault(new_el);\n
  }\n
  new_el.id = getNextId();\n
  return new_el;\n
};\n
\n
// Set scope for these functions\n
var getId, getNextId, call;\n
\n
(function(c) {\n
\n
  // Object to contain editor event names and callback functions\n
  var events = {};\n
\n
  getId = c.getId = function() { return getCurrentDrawing().getId(); };\n
  getNextId = c.getNextId = function() { return getCurrentDrawing().getNextId(); };\n
  \n
  // Function: call\n
  // Run the callback function associated with the given event\n
  //\n
  // Parameters:\n
  // event - String with the event name\n
  // arg - Argument to pass through to the callback function\n
  call = c.call = function(event, arg) {\n
    if (events[event]) {\n
      return events[event](this, arg);\n
    }\n
  };\n
  \n
  // Function: bind\n
  // Attaches a callback function to an event\n
  //\n
  // Parameters:\n
  // event - String indicating the name of the event\n
  // f - The callback function to bind to the event\n
  // \n
  // Return:\n
  // The previous event\n
  c.bind = function(event, f) {\n
    var old = events[event];\n
    events[event] = f;\n
    return old;\n
  };\n
  \n
}(canvas));\n
\n
// Function: canvas.prepareSvg\n
// Runs the SVG Document through the sanitizer and then updates its paths.\n
//\n
// Parameters:\n
// newDoc - The SVG DOM document\n
this.prepareSvg = function(newDoc) {\n
  this.sanitizeSvg(newDoc.documentElement);\n
\n
  // convert paths into absolute commands\n
  var paths = newDoc.getElementsByTagNameNS(svgns, "path");\n
  for (var i = 0, len = paths.length; i < len; ++i) {\n
    var path = paths[i];\n
    path.setAttribute(\'d\', pathActions.convertPath(path));\n
    pathActions.fixEnd(path);\n
  }\n
};\n
\n
// Function getRefElem\n
// Get the reference element associated with the given attribute value\n
//\n
// Parameters:\n
// attrVal - The attribute value as a string\n
var getRefElem = this.getRefElem = function(attrVal) {\n
  return getElem(getUrlFromAttr(attrVal).substr(1));\n
}\n
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
  if(!svgedit.browser.isGecko()) return elem;\n
  var clone = elem.cloneNode(true)\n
  elem.parentNode.insertBefore(clone, elem);\n
  elem.parentNode.removeChild(elem);\n
  selectorManager.releaseSelector(elem);\n
  selectedElements[0] = clone;\n
  selectorManager.requestSelector(clone).showGrips(true);\n
  return clone;\n
}\n
\n
\n
// this.each is deprecated, if any extension used this it can be recreated by doing this:\n
// $(canvas.getRootElem()).children().each(...)\n
\n
// this.each = function(cb) {\n
//  $(svgroot).children().each(cb);\n
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
  // ensure val is the proper type\n
  val = parseFloat(val);\n
  var elem = selectedElements[0];\n
  if (!elem) return;\n
  var oldTransform = elem.getAttribute("transform");\n
  var bbox = svgedit.utilities.getBBox(elem);\n
  var cx = bbox.x+bbox.width/2, cy = bbox.y+bbox.height/2;\n
  var tlist = getTransformList(elem);\n
  \n
  // only remove the real rotational transform if present (i.e. at index=0)\n
  if (tlist.numberOfItems > 0) {\n
    var xform = tlist.getItem(0);\n
    if (xform.type == 4) {\n
      tlist.removeItem(0);\n
    }\n
  }\n
  // find R_nc and insert it\n
  if (val != 0) {\n
    var center = transformPoint(cx,cy,transformListToTransform(tlist).matrix);\n
    var R_nc = svgroot.createSVGTransform();\n
    R_nc.setRotate(val, center.x, center.y);\n
    if(tlist.numberOfItems) {\n
      tlist.insertItemBefore(R_nc, 0);\n
    } else {\n
      tlist.appendItem(R_nc);\n
    }\n
  }\n
  else if (tlist.numberOfItems == 0) {\n
    elem.removeAttribute("transform");\n
  }\n
  \n
  if (!preventUndo) {\n
    // we need to undo it, then redo it so it can be undo-able! :)\n
    // TODO: figure out how to make changes to transform list undo-able cross-browser?\n
    var newTransform = elem.getAttribute("transform");\n
    elem.setAttribute("transform", oldTransform);\n
    changeSelectedAttribute("transform",newTransform,selectedElements);\n
    call("changed", selectedElements);\n
  }\n
  var pointGripContainer = getElem("pathpointgrip_container");\n
//    if(elem.nodeName == "path" && pointGripContainer) {\n
//      pathActions.setPointContainerTransform(elem.getAttribute("transform"));\n
//    }\n
  var selector = selectorManager.requestSelector(selectedElements[0]);\n
  selector.resize();\n
  selector.updateGripCursors(val);\n
};\n
\n
// Function: recalculateAllSelectedDimensions\n
// Runs recalculateDimensions on the selected elements, \n
// adding the changes to a single batch command\n
var recalculateAllSelectedDimensions = this.recalculateAllSelectedDimensions = function() {\n
  var text = (current_resize_mode == "none" ? "position" : "size");\n
  var batchCmd = new BatchCommand(text);\n
\n
  var i = selectedElements.length;\n
  while(i--) {\n
    var elem = selectedElements[i];\n
//      if(getRotationAngle(elem) && !hasMatrixTransform(getTransformList(elem))) continue;\n
    var cmd = recalculateDimensions(elem);\n
    if (cmd) {\n
      batchCmd.addSubCommand(cmd);\n
    }\n
  }\n
\n
  if (!batchCmd.isEmpty()) {\n
    addCommandToHistory(batchCmd);\n
    call("changed", selectedElements);\n
  }\n
};\n
\n
// this is how we map paths to our preferred relative segment types\n
var pathMap = [0, \'z\', \'M\', \'m\', \'L\', \'l\', \'C\', \'c\', \'Q\', \'q\', \'A\', \'a\', \n
          \'H\', \'h\', \'V\', \'v\', \'S\', \'s\', \'T\', \'t\'];\n
          \n
// Debug tool to easily see the current matrix in the browser\'s console\n
var logMatrix = function(m) {\n
  console.log([m.a,m.b,m.c,m.d,m.e,m.f]);\n
};\n
\n
// Function: remapElement\n
// Applies coordinate changes to an element based on the given matrix\n
//\n
// Parameters:\n
// selected - DOM element to be changed\n
// changes - Object with changes to be remapped\n
// m - Matrix object to use for remapping coordinates\n
var remapElement = this.remapElement = function(selected,changes,m) {\n
\n
  var remap = function(x,y) { return transformPoint(x,y,m); },\n
    scalew = function(w) { return m.a*w; },\n
    scaleh = function(h) { return m.d*h; },\n
    doSnapping = curConfig.gridSnapping && selected.parentNode.parentNode.localName === "svg",\n
    finishUp = function() {\n
      if(doSnapping) for(var o in changes) changes[o] = snapToGrid(changes[o]);\n
      assignAttributes(selected, changes, 1000, true);\n
    }\n
    box = svgedit.utilities.getBBox(selected);\n
  \n
  for(var i = 0; i < 2; i++) {\n
    var type = i === 0 ? \'fill\' : \'stroke\';\n
    var attrVal = selected.getAttribute(type);\n
    if(attrVal && attrVal.indexOf(\'url(\') === 0) {\n
      if(m.a < 0 || m.d < 0) {\n
        var grad = getRefElem(attrVal);\n
        var newgrad = grad.cloneNode(true);\n
  \n
        if(m.a < 0) {\n
          //flip x\n
          var x1 = newgrad.getAttribute(\'x1\');\n
          var x2 = newgrad.getAttribute(\'x2\');\n
          newgrad.setAttribute(\'x1\', -(x1 - 1));\n
          newgrad.setAttribute(\'x2\', -(x2 - 1));\n
        } \n
        \n
        if(m.d < 0) {\n
          //flip y\n
          var y1 = newgrad.getAttribute(\'y1\');\n
          var y2 = newgrad.getAttribute(\'y2\');\n
          newgrad.setAttribute(\'y1\', -(y1 - 1));\n
          newgrad.setAttribute(\'y2\', -(y2 - 1));\n
        }\n
        newgrad.id = getNextId();\n
        findDefs().appendChild(newgrad);\n
        selected.setAttribute(type, \'url(#\' + newgrad.id + \')\');\n
      }\n
      \n
      // Not really working :(\n
//      if(selected.tagName === \'path\') {\n
//        reorientGrads(selected, m);\n
//      }\n
    }\n
  }\n
\n
\n
  var elName = selected.tagName;\n
  if(elName === "g" || elName === "text" || elName === "use") {\n
    // if it was a translate, then just update x,y\n
    if (m.a == 1 && m.b == 0 && m.c == 0 && m.d == 1 && \n
      (m.e != 0 || m.f != 0) ) \n
    {\n
      // [T][M] = [M][T\']\n
      // therefore [T\'] = [M_inv][T][M]\n
      var existing = transformListToTransform(selected).matrix,\n
        t_new = matrixMultiply(existing.inverse(), m, existing);\n
      changes.x = parseFloat(changes.x) + t_new.e;\n
      changes.y = parseFloat(changes.y) + t_new.f;\n
    }\n
    else {\n
      // we just absorb all matrices into the element and don\'t do any remapping\n
      var chlist = getTransformList(selected);\n
      var mt = svgroot.createSVGTransform();\n
      mt.setMatrix(matrixMultiply(transformListToTransform(chlist).matrix,m));\n
      chlist.clear();\n
      chlist.appendItem(mt);\n
    }\n
  }\n
  \n
  // now we have a set of changes and an applied reduced transform list\n
  // we apply the changes directly to the DOM\n
  switch (elName)\n
  {\n
    case "foreignObject":\n
    case "rect":\n
    case "image":\n
      \n
      // Allow images to be inverted (give them matrix when flipped)\n
      if(elName === \'image\' && (m.a < 0 || m.d < 0)) {\n
        // Convert to matrix\n
        var chlist = getTransformList(selected);\n
        var mt = svgroot.createSVGTransform();\n
        mt.setMatrix(matrixMultiply(transformListToTransform(chlist).matrix,m));\n
        chlist.clear();\n
        chlist.appendItem(mt);\n
      } else {\n
        var pt1 = remap(changes.x,changes.y);\n
        \n
        changes.width = scalew(changes.width);\n
        changes.height = scaleh(changes.height);\n
        \n
        changes.x = pt1.x + Math.min(0,changes.width);\n
        changes.y = pt1.y + Math.min(0,changes.height);\n
        changes.width = Math.abs(changes.width);\n
        changes.height = Math.abs(changes.height);\n
      }\n
      finishUp();\n
      break;\n
    case "ellipse":\n
      var c = remap(changes.cx,changes.cy);\n
      changes.cx = c.x;\n
      changes.cy = c.y;\n
      changes.rx = scalew(changes.rx);\n
      changes.ry = scaleh(changes.ry);\n
    \n
      changes.rx = Math.abs(changes.rx);\n
      changes.ry = Math.abs(changes.ry);\n
      finishUp();\n
      break;\n
    case "circle":\n
      var c = remap(changes.cx,changes.cy);\n
      changes.cx = c.x;\n
      changes.cy = c.y;\n
      // take the minimum of the new selected box\'s dimensions for the new circle radius\n
      var tbox = svgedit.math.transformBox(box.x, box.y, box.width, box.height, m);\n
      var w = tbox.tr.x - tbox.tl.x, h = tbox.bl.y - tbox.tl.y;\n
      changes.r = Math.min(w/2, h/2);\n
\n
      if(changes.r) changes.r = Math.abs(changes.r);\n
      finishUp();\n
      break;\n
    case "line":\n
      var pt1 = remap(changes.x1,changes.y1),\n
        pt2 = remap(changes.x2,changes.y2);\n
      changes.x1 = pt1.x;\n
      changes.y1 = pt1.y;\n
      changes.x2 = pt2.x;\n
      changes.y2 = pt2.y;\n
      \n
    case "text":\n
      var tspan = selected.querySelectorAll(\'tspan\');\n
      var i = tspan.length\n
      while(i--) {\n
        var selX = convertToNum("x", selected.getAttribute(\'x\'));\n
        var tx = convertToNum("x", tspan[i].getAttribute(\'x\'));\n
        var selY = convertToNum("y", selected.getAttribute(\'y\'));\n
        var ty = convertToNum("y", tspan[i].getAttribute(\'y\'));\n
        var offset = new Object();\n
        if (!isNaN(selX) && !isNaN(tx) && selX!=0 && tx!=0 && changes.x)\n
          offset.x = changes.x - (selX - tx);\n
        if (!isNaN(selY) && !isNaN(ty) && selY!=0 && ty!=0 && changes.y)\n
          offset.y = changes.y - (selY - ty);\n
        if (offset.x || offset.y)\n
          assignAttributes(tspan[i], offset, 1000, true);\n
      }\n
      finishUp();\n
      break;\n
    case "use":\n
      finishUp();\n
      break;\n
    case "g":\n
      var gsvg = $(selected).data(\'gsvg\');\n
      if(gsvg) {\n
        assignAttributes(gsvg, changes, 1000, true);\n
      }\n
      break;\n
    case "polyline":\n
    case "polygon":\n
      var len = changes.points.length;\n
      for (var i = 0; i < len; ++i) {\n
        var pt = changes.points[i];\n
        pt = remap(pt.x,pt.y);\n
        changes.points[i].x = pt.x;\n
        changes.points[i].y = pt.y;\n
      }\n
\n
      var len = changes.points.length;\n
      var pstr = "";\n
      for (var i = 0; i < len; ++i) {\n
        var pt = changes.points[i];\n
        pstr += pt.x + "," + pt.y + " ";\n
      }\n
      selected.setAttribute("points", pstr);\n
      break;\n
    case "path":\n
    \n
      var segList = selected.pathSegList;\n
      var len = segList.numberOfItems;\n
      changes.d = new Array(len);\n
      for (var i = 0; i < len; ++i) {\n
        var seg = segList.getItem(i);\n
        changes.d[i] = {\n
          type: seg.pathSegType,\n
          x: seg.x,\n
          y: seg.y,\n
          x1: seg.x1,\n
          y1: seg.y1,\n
          x2: seg.x2,\n
          y2: seg.y2,\n
          r1: seg.r1,\n
          r2: seg.r2,\n
          angle: seg.angle,\n
          largeArcFlag: seg.largeArcFlag,\n
          sweepFlag: seg.sweepFlag\n
        };\n
      }\n
      \n
      var len = changes.d.length,\n
        firstseg = changes.d[0],\n
        currentpt = remap(firstseg.x,firstseg.y);\n
      changes.d[0].x = currentpt.x;\n
      changes.d[0].y = currentpt.y;\n
      for (var i = 1; i < len; ++i) {\n
        var seg = changes.d[i];\n
        var type = seg.type;\n
        // if absolute or first segment, we want to remap x, y, x1, y1, x2, y2\n
        // if relative, we want to scalew, scaleh\n
        if (type % 2 == 0) { // absolute\n
          var thisx = (seg.x != undefined) ? seg.x : currentpt.x, // for V commands\n
            thisy = (seg.y != undefined) ? seg.y : currentpt.y, // for H commands\n
            pt = remap(thisx,thisy),\n
            pt1 = remap(seg.x1,seg.y1),\n
            pt2 = remap(seg.x2,seg.y2);\n
          seg.x = pt.x;\n
          seg.y = pt.y;\n
          seg.x1 = pt1.x;\n
          seg.y1 = pt1.y;\n
          seg.x2 = pt2.x;\n
          seg.y2 = pt2.y;\n
          seg.r1 = scalew(seg.r1),\n
          seg.r2 = scaleh(seg.r2);\n
        }\n
        else { // relative\n
          seg.x = scalew(seg.x);\n
          seg.y = scaleh(seg.y);\n
          seg.x1 = scalew(seg.x1);\n
          seg.y1 = scaleh(seg.y1);\n
          seg.x2 = scalew(seg.x2);\n
          seg.y2 = scaleh(seg.y2);\n
          seg.r1 = scalew(seg.r1),\n
          seg.r2 = scaleh(seg.r2);\n
        }\n
      } // for each segment\n
    \n
      var dstr = "";\n
      var len = changes.d.length;\n
      for (var i = 0; i < len; ++i) {\n
        var seg = changes.d[i];\n
        var type = seg.type;\n
        dstr += pathMap[type];\n
        switch(type) {\n
          case 13: // relative horizontal line (h)\n
          case 12: // absolute horizontal line (H)\n
            dstr += seg.x + " ";\n
            break;\n
          case 15: // relative vertical line (v)\n
          case 14: // absolute vertical line (V)\n
            dstr += seg.y + " ";\n
            break;\n
          case 3: // relative move (m)\n
          case 5: // relative line (l)\n
          case 19: // relative smooth quad (t)\n
          case 2: // absolute move (M)\n
          case 4: // absolute line (L)\n
          case 18: // absolute smooth quad (T)\n
            dstr += seg.x + "," + seg.y + " ";\n
            break;\n
          case 7: // relative cubic (c)\n
          case 6: // absolute cubic (C)\n
            dstr += seg.x1 + "," + seg.y1 + " " + seg.x2 + "," + seg.y2 + " " +\n
               seg.x + "," + seg.y + " ";\n
            break;\n
          case 9: // relative quad (q) \n
          case 8: // absolute quad (Q)\n
            dstr += seg.x1 + "," + seg.y1 + " " + seg.x + "," + seg.y + " ";\n
            break;\n
          case 11: // relative elliptical arc (a)\n
          case 10: // absolute elliptical arc (A)\n
            dstr += seg.r1 + "," + seg.r2 + " " + seg.angle + " " + (+seg.largeArcFlag) +\n
              " " + (+seg.sweepFlag) + " " + seg.x + "," + seg.y + " ";\n
            break;\n
          case 17: // relative smooth cubic (s)\n
          case 16: // absolute smooth cubic (S)\n
            dstr += seg.x2 + "," + seg.y2 + " " + seg.x + "," + seg.y + " ";\n
            break;\n
        }\n
      }\n
\n
      selected.setAttribute("d", dstr);\n
      break;\n
  }\n
};\n
\n
// Function: updateClipPath\n
// Updates a <clipPath>s values based on the given translation of an element\n
//\n
// Parameters:\n
// attr - The clip-path attribute value with the clipPath\'s ID\n
// tx - The translation\'s x value\n
// ty - The translation\'s y value\n
var updateClipPath = function(attr, tx, ty) {\n
  var path = getRefElem(attr).firstChild;\n
  \n
  var cp_xform = getTransformList(path);\n
  \n
  var newxlate = svgroot.createSVGTransform();\n
  newxlate.setTranslate(tx, ty);\n
\n
  cp_xform.appendItem(newxlate);\n
  \n
  // Update clipPath\'s dimensions\n
  recalculateDimensions(path);\n
}\n
\n
// Function: recalculateDimensions\n
// Decides the course of action based on the element\'s transform list\n
//\n
// Parameters:\n
// selected - The DOM element to recalculate\n
//\n
// Returns: \n
// Undo command object with the resulting change\n
var recalculateDimensions = this.recalculateDimensions = function(selected) {\n
  if (selected == null) return null;\n
  \n
  var tlist = getTransformList(selected);\n
  \n
  // remove any unnecessary transforms\n
  if (tlist && tlist.numberOfItems > 0) {\n
    var k = tlist.numberOfItems;\n
    while (k--) {\n
      var xform = tlist.getItem(k);\n
      if (xform.type === 0) {\n
        tlist.removeItem(k);\n
      }\n
      // remove identity matrices\n
      else if (xform.type === 1) {\n
        if (svgedit.math.isIdentity(xform.matrix)) {\n
          tlist.removeItem(k);\n
        }\n
      }\n
      // remove zero-degree rotations\n
      else if (xform.type === 4) {\n
        if (xform.angle === 0) {\n
          tlist.removeItem(k);\n
        }\n
      }\n
    }\n
    // End here if all it has is a rotation\n
    if(tlist.numberOfItems === 1 && getRotationAngle(selected)) return null;\n
  }\n
  \n
  // if this element had no transforms, we are done\n
  if (!tlist || tlist.numberOfItems == 0) {\n
    selected.removeAttribute("transform");\n
    return null;\n
  }\n
  \n
  // TODO: Make this work for more than 2\n
  if (tlist) {\n
    var k = tlist.numberOfItems;\n
    var mxs = [];\n
    while (k--) {\n
      var xform = tlist.getItem(k);\n
      if (xform.type === 1) {\n
        mxs.push([xform.matrix, k]);\n
      } else if(mxs.length) {\n
        mxs = [];\n
      }\n
    }\n
    if(mxs.length === 2) {\n
      var m_new = svgroot.createSVGTransformFromMatrix(matrixMultiply(mxs[1][0], mxs[0][0]));\n
      tlist.removeItem(mxs[0][1]);\n
      tlist.removeItem(mxs[1][1]);\n
      tlist.insertItemBefore(m_new, mxs[1][1]);\n
    }\n
    \n
    // combine matrix + translate\n
    k = tlist.numberOfItems;\n
    if(k >= 2 && tlist.getItem(k-2).type === 1 && tlist.getItem(k-1).type === 2) {\n
      var mt = svgroot.createSVGTransform();\n
      \n
      var m = matrixMultiply(\n
        tlist.getItem(k-2).matrix, \n
        tlist.getItem(k-1).matrix\n
      );    \n
      mt.setMatrix(m);\n
      tlist.removeItem(k-2);\n
      tlist.removeItem(k-2);\n
      tlist.appendItem(mt);\n
    }\n
  }\n
  \n
  // If it still has a single [M] or [R][M], return null too (prevents BatchCommand from being returned).\n
  switch ( selected.tagName ) {\n
    // Ignore these elements, as they can absorb the [M]\n
    case \'line\':\n
    case \'polyline\':\n
    case \'polygon\':\n
    case \'path\':\n
      break;\n
    default:\n
      if(\n
        (tlist.numberOfItems === 1 && tlist.getItem(0).type === 1)\n
        ||  (tlist.numberOfItems === 2 && tlist.getItem(0).type === 1 && tlist.getItem(0).type === 4)\n
      ) {\n
        return null;\n
      }\n
  }\n
  \n
  // Grouped SVG element \n
  var gsvg = $(selected).data(\'gsvg\');\n
  \n
  // we know we have some transforms, so set up return variable   \n
  var batchCmd = new BatchCommand("Transform");\n
  \n
  // store initial values that will be affected by reducing the transform list\n
  var changes = {}, initial = null, attrs = [];\n
  switch (selected.tagName)\n
  {\n
    case "line":\n
      attrs = ["x1", "y1", "x2", "y2"];\n
      break;\n
    case "circle":\n
      attrs = ["cx", "cy", "r"];\n
      break;\n
    case "ellipse":\n
      attrs = ["cx", "cy", "rx", "ry"];\n
      break;\n
    case "foreignObject":\n
    case "rect":\n
    case "image":\n
      attrs = ["width", "height", "x", "y"];\n
      break;\n
    case "use":\n
    case "text":\n
    case "tspan":\n
      attrs = ["x", "y"];\n
      break;\n
    case "polygon":\n
    case "polyline":\n
      initial = {};\n
      initial["points"] = selected.getAttribute("points");\n
      var list = selected.points;\n
      var len = list.numberOfItems;\n
      changes["points"] = new Array(len);\n
      for (var i = 0; i < len; ++i) {\n
        var pt = list.getItem(i);\n
        changes["points"][i] = {x:pt.x,y:pt.y};\n
      }\n
      break;\n
    case "path":\n
      initial = {};\n
      initial["d"] = selected.getAttribute("d");\n
      changes["d"] = selected.getAttribute("d");\n
      break;\n
  } // switch on element type to get initial values\n
  \n
  if(attrs.length) {\n
    changes = $(selected).attr(attrs);\n
    $.each(changes, function(attr, val) {\n
      changes[attr] = convertToNum(attr, val);\n
    });\n
  } else if(gsvg) {\n
    // GSVG exception\n
    changes = {\n
      x: $(gsvg).attr(\'x\') || 0,\n
      y: $(gsvg).attr(\'y\') || 0\n
    };\n
  }\n
  \n
  // if we haven\'t created an initial array in polygon/polyline/path, then \n
  // make a copy of initial values and include the transform\n
  if (initial == null) {\n
    initial = $.extend(true, {}, changes);\n
    $.each(initial, function(attr, val) {\n
      initial[attr] = convertToNum(attr, val);\n
    });\n
  }\n
  // save the start transform value too\n
  initial["transform"] = start_transform ? start_transform : "";\n
  \n
  // if it\'s a regular group, we have special processing to flatten transforms\n
  if ((selected.tagName == "g" && !gsvg) || selected.tagName == "a") {\n
    var box = svgedit.utilities.getBBox(selected),\n
      oldcenter = {x: box.x+box.width/2, y: box.y+box.height/2},\n
      newcenter = transformPoint(box.x+box.width/2, box.y+box.height/2,\n
              transformListToTransform(tlist).matrix),\n
      m = svgroot.createSVGMatrix();\n
    \n
    \n
    // temporarily strip off the rotate and save the old center\n
    var gangle = getRotationAngle(selected);\n
    if (gangle) {\n
      var a = gangle * Math.PI / 180;\n
      if ( Math.abs(a) > (1.0e-10) ) {\n
        var s = Math.sin(a)/(1 - Math.cos(a));\n
      } else {\n
        // FIXME: This blows up if the angle is exactly 0!\n
        var s = 2/a;\n
      }\n
      for (var i = 0; i < tlist.numberOfItems; ++i) {\n
        var xform = tlist.getItem(i);\n
        if (xform.type == 4) {\n
          // extract old center through mystical arts\n
          var rm = xform.matrix;\n
          oldcenter.y = (s*rm.e + rm.f)/2;\n
          oldcenter.x = (rm.e - s*rm.f)/2;\n
          tlist.removeItem(i);\n
          break;\n
        }\n
      }\n
    }\n
    var tx = 0, ty = 0,\n
      operation = 0,\n
      N = tlist.numberOfItems;\n
\n
    if(N) {\n
      var first_m = tlist.getItem(0).matrix;\n
    }\n
\n
    // first, if it was a scale then the second-last transform will be it\n
    if (N >= 3 && tlist.getItem(N-2).type == 3 && \n
      tlist.getItem(N-3).type == 2 && tlist.getItem(N-1).type == 2) \n
    {\n
      operation = 3; // scale\n
    \n
      // if the children are unrotated, pass the scale down directly\n
      // otherwise pass the equivalent matrix() down directly\n
      var tm = tlist.getItem(N-3).matrix,\n
        sm = tlist.getItem(N-2).matrix,\n
        tmn = tlist.getItem(N-1).matrix;\n
    \n
      var children = selected.childNodes;\n
      var c = children.length;\n
      while (c--) {\n
        var child = children.item(c);\n
        tx = 0;\n
        ty = 0;\n
        if (child.nodeType == 1) {\n
          var childTlist = getTransformList(child);\n
\n
          // some children might not have a transform (<metadata>, <defs>, etc)\n
          if (!childTlist) continue;\n
\n
          var m = transformListToTransform(childTlist).matrix;\n
\n
          // Convert a matrix to a scale if applicable\n
//          if(hasMatrixTransform(childTlist) && childTlist.numberOfItems == 1) {\n
//            if(m.b==0 && m.c==0 && m.e==0 && m.f==0) {\n
//              childTlist.removeItem(0);\n
//              var translateOrigin = svgroot.createSVGTransform(),\n
//                scale = svgroot.createSVGTransform(),\n
//                translateBack = svgroot.createSVGTransform();\n
//              translateOrigin.setTranslate(0, 0);\n
//              scale.setScale(m.a, m.d);\n
//              translateBack.setTranslate(0, 0);\n
//              childTlist.appendItem(translateBack);\n
//              childTlist.appendItem(scale);\n
//              childTlist.appendItem(translateOrigin);\n
//            }\n
//          }\n
        \n
          var angle = getRotationAngle(child);\n
          var old_start_transform = start_transform;\n
          var childxforms = [];\n
          start_transform = child.getAttribute("transform");\n
          if(angle || hasMatrixTransform(childTlist)) {\n
            var e2t = svgroot.createSVGTransform();\n
            e2t.setMatrix(matrixMultiply(tm, sm, tmn, m));\n
            childTlist.clear();\n
            childTlist.appendItem(e2t);\n
            childxforms.push(e2t);\n
          }\n
          // if not rotated or skewed, push the [T][S][-T] down to the child\n
          else {\n
            // update the transform list with translate,scale,translate\n
            \n
            // slide the [T][S][-T] from the front to the back\n
            // [T][S][-T][M] = [M][T2][S2][-T2]\n
            \n
            // (only bringing [-T] to the right of [M])\n
            // [T][S][-T][M] = [T][S][M][-T2]\n
            // [-T2] = [M_inv][-T][M]\n
            var t2n = matrixMultiply(m.inverse(), tmn, m);\n
            // [T2] is always negative translation of [-T2]\n
            var t2 = svgroot.createSVGMatrix();\n
            t2.e = -t2n.e;\n
            t2.f = -t2n.f;\n
            \n
            // [T][S][-T][M] = [M][T2][S2][-T2]\n
            // [S2] = [T2_inv][M_inv][T][S][-T][M][-T2_inv]\n
            var s2 = matrixMultiply(t2.inverse(), m.inverse(), tm, sm, tmn, m, t2n.inverse());\n
\n
            var translateOrigin = svgroot.createSVGTransform(),\n
              scale = svgroot.createSVGTransform(),\n
              translateBack = svgroot.createSVGTransform();\n
            translateOrigin.setTranslate(t2n.e, t2n.f);\n
            scale.setScale(s2.a, s2.d);\n
            translateBack.setTranslate(t2.e, t2.f);\n
            childTlist.appendItem(translateBack);\n
            childTlist.appendItem(scale);\n
            childTlist.appendItem(translateOrigin);\n
            childxforms.push(translateBack);\n
            childxforms.push(scale);\n
            childxforms.push(translateOrigin);\n
//            logMatrix(translateBack.matrix);\n
//            logMatrix(scale.matrix);\n
          } // not rotated\n
          batchCmd.addSubCommand( recalculateDimensions(child) );\n
          // TODO: If any <use> have this group as a parent and are \n
          // referencing this child, then we need to impose a reverse \n
          // scale on it so that when it won\'t get double-translated\n
//            var uses = selected.getElementsByTagNameNS(svgns, "use");\n
//            var href = "#"+child.id;\n
//            var u = uses.length;\n
//            while (u--) {\n
//              var useElem = uses.item(u);\n
//              if(href == getHref(useElem)) {\n
//                var usexlate = svgroot.createSVGTransform();\n
//                usexlate.setTranslate(-tx,-ty);\n
//                getTransformList(useElem).insertItemBefore(usexlate,0);\n
//                batchCmd.addSubCommand( recalculateDimensions(useElem) );\n
//              }\n
//            }\n
          start_transform = old_start_transform;\n
        } // element\n
      } // for each child\n
      // Remove these transforms from group\n
      tlist.removeItem(N-1);\n
      tlist.removeItem(N-2);\n
      tlist.removeItem(N-3);\n
    }\n
    else if (N >= 3 && tlist.getItem(N-1).type == 1)\n
    {\n
      operation = 3; // scale\n
      m = transformListToTransform(tlist).matrix;\n
      var e2t = svgroot.createSVGTransform();\n
      e2t.setMatrix(m);\n
      tlist.clear();\n
      tlist.appendItem(e2t);\n
    }     \n
    // next, check if the first transform was a translate \n
    // if we had [ T1 ] [ M ] we want to transform this into [ M ] [ T2 ]\n
    // therefore [ T2 ] = [ M_inv ] [ T1 ] [ M ]\n
    else if ( (N == 1 || (N > 1 && tlist.getItem(1).type != 3)) && \n
      tlist.getItem(0).type == 2) \n
    {\n
      operation = 2; // translate\n
      var T_M = transformListToTransform(tlist).matrix;\n
      tlist.removeItem(0);\n
      var M_inv = transformListToTransform(tlist).matrix.inverse();\n
      var M2 = matrixMultiply( M_inv, T_M );\n
      \n
      tx = M2.e;\n
      ty = M2.f;\n
\n
      if (tx != 0 || ty != 0) {\n
        // we pass the translates down to the individual children\n
        var children = selected.childNodes;\n
        var c = children.length;\n
        \n
        var clipPaths_done = [];\n
        \n
        while (c--) {\n
          var child = children.item(c);\n
          if (child.nodeType == 1) {\n
          \n
            // Check if child has clip-path\n
            if(child.getAttribute(\'clip-path\')) {\n
              // tx, ty\n
              var attr = child.getAttribute(\'clip-path\');\n
              if(clipPaths_done.indexOf(attr) === -1) {\n
                updateClipPath(attr, tx, ty);\n
                clipPaths_done.push(attr);\n
              }             \n
            }\n
\n
            var old_start_transform = start_transform;\n
            start_transform = child.getAttribute("transform");\n
            \n
            var childTlist = getTransformList(child);\n
            // some children might not have a transform (<metadata>, <defs>, etc)\n
            if (childTlist) {\n
              var newxlate = svgroot.createSVGTransform();\n
              newxlate.setTranslate(tx,ty);\n
              if(childTlist.numberOfItems) {\n
                childTlist.insertItemBefore(newxlate, 0);\n
              } else {\n
                childTlist.appendItem(newxlate);\n
              }\n
              batchCmd.addSubCommand( recalculateDimensions(child) );\n
              // If any <use> have this group as a parent and are \n
              // referencing this child, then impose a reverse translate on it\n
              // so that when it won\'t get double-translated\n
              var uses = selected.getElementsByTagNameNS(svgns, "use");\n
              var href = "#"+child.id;\n
              var u = uses.length;\n
              while (u--) {\n
                var useElem = uses.item(u);\n
                if(href == getHref(useElem)) {\n
                  var usexlate = svgroot.createSVGTransform();\n
                  usexlate.setTranslate(-tx,-ty);\n
                  getTransformList(useElem).insertItemBefore(usexlate,0);\n
                  batchCmd.addSubCommand( recalculateDimensions(useElem) );\n
                }\n
              }\n
              start_transform = old_start_transform;\n
            }\n
          }\n
        }\n
        \n
        clipPaths_done = [];\n
        \n
        start_transform = old_start_transform;\n
      }\n
    }\n
    // else, a matrix imposition from a parent group\n
    // keep pushing it down to the children\n
    else if (N == 1 && tlist.getItem(0).type == 1 && !gangle) {\n
      operation = 1;\n
      var m = tlist.getItem(0).matrix,\n
        children = selected.childNodes,\n
        c = children.length;\n
      while (c--) {\n
        var child = children.item(c);\n
        if (child.nodeType == 1) {\n
          var old_start_transform = start_transform;\n
          start_transform = child.getAttribute("transform");\n
          var childTlist = getTransformList(child);\n
          \n
          if (!childTlist) continue;\n
          \n
          var em = matrixMultiply(m, transformListToTransform(childTlist).matrix);\n
          var e2m = svgroot.createSVGTransform();\n
          e2m.setMatrix(em);\n
          childTlist.clear();\n
          childTlist.appendItem(e2m,0);\n
          \n
          batchCmd.addSubCommand( recalculateDimensions(child) );\n
          start_transform = old_start_transform;\n
          \n
          // Convert stroke\n
          // TODO: Find out if this should actually happen somewhere else\n
          var sw = child.getAttribute("stroke-width");\n
          if (child.getAttribute("stroke") !== "none" && !isNaN(sw)) {\n
            var avg = (Math.abs(em.a) + Math.abs(em.d)) / 2;\n
            child.setAttribute(\'stroke-width\', sw * avg);\n
          }\n
\n
        }\n
      }\n
      tlist.clear();\n
    }\n
    // else it was just a rotate\n
    else {\n
      if (gangle) {\n
        var newRot = svgroot.createSVGTransform();\n
        newRot.setRotate(gangle,newcenter.x,newcenter.y);\n
        if(tlist.numberOfItems) {\n
          tlist.insertItemBefore(newRot, 0);\n
        } else {\n
          tlist.appendItem(newRot);\n
        }\n
      }\n
      if (tlist.numberOfItems == 0) {\n
        selected.removeAttribute("transform");\n
      }\n
      return null;      \n
    }\n
    \n
    // if it was a translate, put back the rotate at the new center\n
    if (operation == 2) {\n
      if (gangle) {\n
        newcenter = {\n
          x: oldcenter.x + first_m.e,\n
          y: oldcenter.y + first_m.f\n
        };\n
      \n
        var newRot = svgroot.createSVGTransform();\n
        newRot.setRotate(gangle,newcenter.x,newcenter.y);\n
        if(tlist.numberOfItems) {\n
          tlist.insertItemBefore(newRot, 0);\n
        } else {\n
          tlist.appendItem(newRot);\n
        }\n
      }\n
    }\n
    // if it was a resize\n
    else if (operation == 3) {\n
      var m = transformListToTransform(tlist).matrix;\n
      var roldt = svgroot.createSVGTransform();\n
      roldt.setRotate(gangle, oldcenter.x, oldcenter.y);\n
      var rold = roldt.matrix;\n
      var rnew = svgroot.createSVGTransform();\n
      rnew.setRotate(gangle, newcenter.x, newcenter.y);\n
      var rnew_inv = rnew.matrix.inverse(),\n
        m_inv = m.inverse(),\n
        extrat = matrixMultiply(m_inv, rnew_inv, rold, m);\n
\n
      tx = extrat.e;\n
      ty = extrat.f;\n
\n
      if (tx != 0 || ty != 0) {\n
        // now push this transform down to the children\n
        // we pass the translates down to the individual children\n
        var children = selected.childNodes;\n
        var c = children.length;\n
        while (c--) {\n
          var child = children.item(c);\n
          if (child.nodeType == 1) {\n
            var old_start_transform = start_transform;\n
            start_transform = child.getAttribute("transform");\n
            var childTlist = getTransformList(child);\n
            var newxlate = svgroot.createSVGTransform();\n
            newxlate.setTranslate(tx,ty);\n
            if(childTlist.numberOfItems) {\n
              childTlist.insertItemBefore(newxlate, 0);\n
            } else {\n
              childTlist.appendItem(newxlate);\n
            }\n
\n
            batchCmd.addSubCommand( recalculateDimensions(child) );\n
            start_transform = old_start_transform;\n
          }\n
        }\n
      }\n
      \n
      if (gangle) {\n
        if(tlist.numberOfItems) {\n
          tlist.insertItemBefore(rnew, 0);\n
        } else {\n
          tlist.appendItem(rnew);\n
        }\n
      }\n
    }\n
  }\n
  // else, it\'s a non-group\n
  else {\n
\n
    // FIXME: box might be null for some elements (<metadata> etc), need to handle this\n
    var box = svgedit.utilities.getBBox(selected);\n
\n
    // Paths (and possbly other shapes) will have no BBox while still in <defs>,\n
    // but we still may need to recalculate them (see issue 595).\n
    // TODO: Figure out how to get BBox from these elements in case they\n
    // have a rotation transform\n
    \n
    if(!box && selected.tagName != \'path\') return null;\n
    \n
\n
    var m = svgroot.createSVGMatrix(),\n
      // temporarily strip off the rotate and save the old center\n
      angle = getRotationAngle(selected);\n
    if (angle) {\n
      var oldcenter = {x: box.x+box.width/2, y: box.y+box.height/2},\n
      newcenter = transformPoint(box.x+box.width/2, box.y+box.height/2,\n
              transformListToTransform(tlist).matrix);\n
    \n
      var a = angle * Math.PI / 180;\n
      if ( Math.abs(a) > (1.0e-10) ) {\n
        var s = Math.sin(a)/(1 - Math.cos(a));\n
      } else {\n
        // FIXME: This blows up if the angle is exactly 0!\n
        var s = 2/a;\n
      }\n
      for (var i = 0; i < tlist.numberOfItems; ++i) {\n
        var xform = tlist.getItem(i);\n
        if (xform.type == 4) {\n
          // extract old center through mystical arts\n
          var rm = xform.matrix;\n
          oldcenter.y = (s*rm.e + rm.f)/2;\n
          oldcenter.x = (rm.e - s*rm.f)/2;\n
          tlist.removeItem(i);\n
          break;\n
        }\n
      }\n
    }\n
    \n
    // 2 = translate, 3 = scale, 4 = rotate, 1 = matrix imposition\n
    var operation = 0;\n
    var N = tlist.numberOfItems;\n
    \n
    // Check if it has a gradient with userSpaceOnUse, in which case\n
    // adjust it by recalculating the matrix transform.\n
    // TODO: Make this work in Webkit using svgedit.transformlist.SVGTransformList\n
    if(!svgedit.browser.isWebkit()) {\n
      var fill = selected.getAttribute(\'fill\');\n
      if(fill && fill.indexOf(\'url(\') === 0) {\n
        var paint = getRefElem(fill);\n
        var type = \'pattern\';\n
        if(paint.tagName !== type) type = \'gradient\';\n
        var attrVal = paint.getAttribute(type + \'Units\');\n
        if(attrVal === \'userSpaceOnUse\') {\n
          //Update the userSpaceOnUse element\n
          m = transformListToTransform(tlist).matrix;\n
          var gtlist = getTransformList(paint);\n
          var gmatrix = transformListToTransform(gtlist).matrix;\n
          m = matrixMultiply(m, gmatrix);\n
          var m_str = "matrix(" + [m.a,m.b,m.c,m.d,m.e,m.f].join(",") + ")";\n
          paint.setAttribute(type + \'Transform\', m_str);\n
        }\n
      }\n
    }\n
\n
    // first, if it was a scale of a non-skewed element, then the second-last  \n
    // transform will be the [S]\n
    // if we had [M][T][S][T] we want to extract the matrix equivalent of\n
    // [T][S][T] and push it down to the element\n
    if (N >= 3 && tlist.getItem(N-2).type == 3 && \n
      tlist.getItem(N-3).type == 2 && tlist.getItem(N-1).type == 2) \n
      \n
      // Removed this so a <use> with a given [T][S][T] would convert to a matrix. \n
      // Is that bad?\n
      //  && selected.nodeName != "use"\n
    {\n
      operation = 3; // scale\n
      m = transformListToTransform(tlist,N-3,N-1).matrix;\n
      tlist.removeItem(N-1);\n
      tlist.removeItem(N-2);\n
      tlist.removeItem(N-3);\n
    } // if we had [T][S][-T][M], then this was a skewed element being resized\n
    // Thus, we simply combine it all into one matrix\n
    else if(N == 4 && tlist.getItem(N-1).type == 1) {\n
      operation = 3; // scale\n
      m = transformListToTransform(tlist).matrix;\n
      var e2t = svgroot.createSVGTransform();\n
      e2t.setMatrix(m);\n
      tlist.clear();\n
      tlist.appendItem(e2t);\n
      // reset the matrix so that the element is not re-mapped\n
      m = svgroot.createSVGMatrix();\n
    } // if we had [R][T][S][-T][M], then this was a rotated matrix-element  \n
    // if we had [T1][M] we want to transform this into [M][T2]\n
    // therefore [ T2 ] = [ M_inv ] [ T1 ] [ M ] and we can push [T2] \n
    // down to the element\n
    else if ( (N == 1 || (N > 1 && tlist.getItem(1).type != 3)) && \n
      tlist.getItem(0).type == 2) \n
    {\n
      operation = 2; // translate\n
      var oldxlate = tlist.getItem(0).matrix,\n
        meq = transformListToTransform(tlist,1).matrix,\n
        meq_inv = meq.inverse();\n
      m = matrixMultiply( meq_inv, oldxlate, meq );\n
      tlist.removeItem(0);\n
    }\n
    // else if this child now has a matrix imposition (from a parent group)\n
    // we might be able to simplify\n
    else if (N == 1 && tlist.getItem(0).type == 1 && !angle) {\n
      // Remap all point-based elements\n
      m = transformListToTransform(tlist).matrix;\n
      switch (selected.tagName) {\n
        case \'line\':\n
          changes = $(selected).attr(["x1","y1","x2","y2"]);\n
        case \'polyline\':\n
        case \'polygon\':\n
          changes.points = selected.getAttribute("points");\n
          if(changes.points) {\n
            var list = selected.points;\n
            var len = list.numberOfItems;\n
            changes.points = new Array(len);\n
            for (var i = 0; i < len; ++i) {\n
              var pt = list.getItem(i);\n
              changes.points[i] = {x:pt.x,y:pt.y};\n
            }\n
          }\n
        case \'path\':\n
          changes.d = selected.getAttribute("d");\n
          operation = 1;\n
          tlist.clear();\n
          break;\n
        default:\n
          break;\n
      }\n
    }\n
    // if it was a rotation, put the rotate back and return without a command\n
    // (this function has zero work to do for a rotate())\n
    else {\n
      operation = 4; // rotation\n
      if (angle) {\n
        var newRot = svgroot.createSVGTransform();\n
        newRot.setRotate(angle,newcenter.x,newcenter.y);\n
        \n
        if(tlist.numberOfItems) {\n
          tlist.insertItemBefore(newRot, 0);\n
        } else {\n
          tlist.appendItem(newRot);\n
        }\n
      }\n
      if (tlist.numberOfItems == 0) {\n
        selected.removeAttribute("transform");\n
      }\n
      return null;\n
    }\n
    \n
    // if it was a translate or resize, we need to remap the element and absorb the xform\n
    if (operation == 1 || operation == 2 || operation == 3) {\n
      remapElement(selected,changes,m);\n
    } // if we are remapping\n
    \n
    // if it was a translate, put back the rotate at the new center\n
    if (operation == 2) {\n
      if (angle) {\n
        if(!hasMatrixTransform(tlist)) {\n
          newcenter = {\n
            x: oldcenter.x + m.e,\n
            y: oldcenter.y + m.f\n
          };\n
        }\n
        var newRot = svgroot.createSVGTransform();\n
        newRot.setRotate(angle, newcenter.x, newcenter.y);\n
        if(tlist.numberOfItems) {\n
          tlist.insertItemBefore(newRot, 0);\n
        } else {\n
          tlist.appendItem(newRot);\n
        }\n
      }\n
    }\n
    // [Rold][M][T][S][-T] became [Rold][M]\n
    // we want it to be [Rnew][M][Tr] where Tr is the\n
    // translation required to re-center it\n
    // Therefore, [Tr] = [M_inv][Rnew_inv][Rold][M]\n
    else if (operation == 3 && angle) {\n
      var m = transformListToTransform(tlist).matrix;\n
      var roldt = svgroot.createSVGTransform();\n
      roldt.setRotate(angle, oldcenter.x, oldcenter.y);\n
      var rold = roldt.matrix;\n
      var rnew = svgroot.createSVGTransform();\n
      rnew.setRotate(angle, newcenter.x, newcenter.y);\n
      var rnew_inv = rnew.matrix.inverse();\n
      var m_inv = m.inverse();\n
      var extrat = matrixMultiply(m_inv, rnew_inv, rold, m);\n
    \n
      remapElement(selected,changes,extrat);\n
      if (angle) {\n
        if(tlist.numberOfItems) {\n
          tlist.insertItemBefore(rnew, 0);\n
        } else {\n
          tlist.appendItem(rnew);\n
        }\n
      }\n
    }\n
  } // a non-group\n
\n
  // if the transform list has been emptied, remove it\n
  if (tlist.numberOfItems == 0) {\n
    selected.removeAttribute("transform");\n
  }\n
  \n
  batchCmd.addSubCommand(new ChangeElementCommand(selected, initial));\n
  \n
  return batchCmd;\n
};\n
\n
// Root Current Transformation Matrix in user units\n
var root_sctm = null;\n
\n
// Group: Selection\n
\n
// Function: clearSelection\n
// Clears the selection.  The \'selected\' handler is then called.\n
// Parameters: \n
// noCall - Optional boolean that when true does not call the "selected" handler\n
var clearSelection = this.clearSelection = function(noCall) {\n
  if (selectedElements[0] != null) {\n
    var len = selectedElements.length;\n
    for (var i = 0; i < len; ++i) {\n
      var elem = selectedElements[i];\n
      if (elem == null) break;\n
      selectorManager.releaseSelector(elem);\n
      selectedElements[i] = null;\n
    }\n
//    selectedBBoxes[0] = null;\n
  }\n
  if(!noCall) call("selected", selectedElements);\n
};\n
\n
// TODO: do we need to worry about selectedBBoxes here?\n
\n
\n
// Function: addToSelection\n
// Adds a list of elements to the selection.  The \'selected\' handler is then called.\n
//\n
// Parameters:\n
// elemsToAdd - an array of DOM elements to add to the selection\n
// showGrips - a boolean flag indicating whether the resize grips should be shown\n
var addToSelection = this.addToSelection = function(elemsToAdd, showGrips) {\n
  if (elemsToAdd.length == 0) { return; }\n
  // find the first null in our selectedElements array\n
  var j = 0;\n
  \n
  while (j < selectedElements.length) {\n
    if (selectedElements[j] == null) { \n
      break;\n
    }\n
    ++j;\n
  }\n
\n
  // now add each element consecutively\n
  var i = elemsToAdd.length;\n
  while (i--) {\n
    var elem = elemsToAdd[i];\n
    if (!elem || !svgedit.utilities.getBBox(elem)) continue;\n
\n
    if(elem.tagName === \'a\' && elem.childNodes.length === 1) {\n
      // Make "a" element\'s child be the selected element \n
      elem = elem.firstChild;\n
    }\n
\n
    // if it\'s not already there, add it\n
    if (selectedElements.indexOf(elem) == -1) {\n
\n
      selectedElements[j] = elem;\n
\n
      // only the first selectedBBoxes element is ever used in the codebase these days\n
//      if (j == 0) selectedBBoxes[0] = svgedit.utilities.getBBox(elem);\n
      j++;\n
      var sel = selectorManager.requestSelector(elem);\n
  \n
      if (selectedElements.length > 1) {\n
        sel.showGrips(false);\n
      }\n
    }\n
  }\n
  call("selected", selectedElements);\n
  if (showGrips || selectedElements.length == 1) selectorManager.requestSelector(selectedElements[0]).showGrips(true)\n
  else selectorManager.requestSelector(selectedElements[0]).showGrips(false);\n
\n
  // make sure the elements are in the correct order\n
  // See: http://www.w3.org/TR/DOM-Level-3-Core/core.html#Node3-compareDocumentPosition\n
\n
  selectedElements.sort(function(a,b) {\n
    if(a && b && a.compareDocumentPosition) {\n
      return 3 - (b.compareDocumentPosition(a) & 6);  \n
    } else if(a == null) {\n
      return 1;\n
    }\n
  });\n
  \n
  // Make sure first elements are not null\n
  while(selectedElements[0] == null) selectedElements.shift(0);\n
};\n
\n
// Function: selectOnly()\n
// Selects only the given elements, shortcut for clearSelection(); addToSelection()\n
//\n
// Parameters:\n
// elems - an array of DOM elements to be selected\n
var selectOnly = this.selectOnly = function(elems, showGrips) {\n
  clearSelection(true);\n
  addToSelection(elems, showGrips);\n
}\n
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
  if (selectedElements[0] == null) { return; }\n
  if (elemsToRemove.length == 0) { return; }\n
\n
  // find every element and remove it from our array copy\n
  var newSelectedItems = new Array(selectedElements.length);\n
    j = 0,\n
    len = selectedElements.length;\n
  for (var i = 0; i < len; ++i) {\n
    var elem = selectedElements[i];\n
    if (elem) {\n
      // keep the item\n
      if (elemsToRemove.indexOf(elem) == -1) {\n
        newSelectedItems[j] = elem;\n
        j++;\n
      }\n
      else { // remove the item and its selector\n
        selectorManager.releaseSelector(elem);\n
      }\n
    }\n
  }\n
  // the copy becomes the master now\n
  selectedElements = newSelectedItems;\n
};\n
\n
// Function: selectAllInCurrentLayer\n
// Clears the selection, then adds all elements in the current layer to the selection.\n
this.selectAllInCurrentLayer = function() {\n
  var current_layer = getCurrentDrawing().getCurrentLayer();\n
  if (current_layer) {\n
    current_mode = "select";\n
    selectOnly($(current_group || current_layer).children());\n
  }\n
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
  if (evt == null || evt.target == null) {\n
    return null;\n
  }\n
  var mouse_target = evt.target;\n
  \n
  // if it was a <use>, Opera and WebKit return the SVGElementInstance\n
  if (mouse_target.correspondingUseElement) mouse_target = mouse_target.correspondingUseElement;\n
  \n
  // for foreign content, go up until we find the foreignObject\n
  // WebKit browsers set the mouse target to the svgcanvas div \n
  if ([mathns, htmlns].indexOf(mouse_target.namespaceURI) >= 0 && \n
    mouse_target.id != "svgcanvas") \n
  {\n
    while (mouse_target.nodeName != "foreignObject") {\n
      mouse_target = mouse_target.parentNode;\n
      if(!mouse_target) return svgroot;\n
    }\n
  }\n
  \n
  // Get the desired mouse_target with jQuery selector-fu\n
  // If it\'s root-like, select the root\n
  var current_layer = getCurrentDrawing().getCurrentLayer();\n
  if([svgroot, container, svgcontent, current_layer].indexOf(mouse_target) >= 0) {\n
    return svgroot;\n
  }\n
  \n
  var $target = $(mouse_target);\n
\n
  // If it\'s a selection grip, return the grip parent\n
  if($target.closest(\'#selectorParentGroup\').length) {\n
    // While we could instead have just returned mouse_target, \n
    // this makes it easier to indentify as being a selector grip\n
    return selectorManager.selectorParentGroup;\n
  }\n
\n
  while (mouse_target.parentNode && mouse_target.parentNode !== (current_group || current_layer)) {\n
    mouse_target = mouse_target.parentNode;\n
  }\n
  \n
//  \n
//  // go up until we hit a child of a layer\n
//  while (mouse_target.parentNode.parentNode.tagName == \'g\') {\n
//    mouse_target = mouse_target.parentNode;\n
//  }\n
  // Webkit bubbles the mouse event all the way up to the div, so we\n
  // set the mouse_target to the svgroot like the other browsers\n
//  if (mouse_target.nodeName.toLowerCase() == "div") {\n
//    mouse_target = svgroot;\n
//  }\n
  \n
  return mouse_target;\n
};\n
\n
// Mouse events\n
(function() {\n
  var d_attr = null,\n
    start_x = null,\n
    start_y = null,\n
    r_start_x = null,\n
    r_start_y = null,\n
    init_bbox = {},\n
    freehand = {\n
      minx: null,\n
      miny: null,\n
      maxx: null,\n
      maxy: null\n
    };\n
  \n
  // - when we are in a create mode, the element is added to the canvas\n
  //   but the action is not recorded until mousing up\n
  // - when we are in select mode, select the element, remember the position\n
  //   and do nothing else\n
  var mouseDown = function(evt)\n
  {\n
    if (canvas.spaceKey) return;\n
    var right_click = evt.button === 2;\n
\n
    root_sctm = svgcontent.querySelector("g").getScreenCTM().inverse();\n
\n
    var pt = transformPoint( evt.pageX, evt.pageY, root_sctm ),\n
      mouse_x = pt.x * current_zoom,\n
      mouse_y = pt.y * current_zoom;\n
      \n
\n
    evt.preventDefault();\n
\n
    if(right_click) {\n
      current_mode = "select";\n
      lastClickPoint = pt;\n
    }\n
    \n
    var x = mouse_x / current_zoom,\n
      y = mouse_y / current_zoom,\n
      mouse_target = getMouseTarget(evt);\n
    \n
    if(mouse_target.tagName === \'a\' && mouse_target.childNodes.length === 1) {\n
      mouse_target = mouse_target.firstChild;\n
    }\n
    \n
    // real_x/y ignores grid-snap value\n
    var real_x = r_start_x = start_x = x;\n
    var real_y = r_start_y = start_y = y;\n
\n
    if(curConfig.gridSnapping){\n
      x = snapToGrid(x);\n
      y = snapToGrid(y);\n
      start_x = snapToGrid(start_x);\n
      start_y = snapToGrid(start_y);\n
    }\n
\n
    // if it is a selector grip, then it must be a single element selected, \n
    // set the mouse_target to that and update the mode to rotate/resize\n
    \n
    if (mouse_target == selectorManager.selectorParentGroup && selectedElements[0] != null) {\n
      var grip = evt.target;\n
      var griptype = elData(grip, "type");\n
      // rotating\n
      if (griptype == "rotate") {\n
        current_mode = "rotate";\n
        current_rotate_mode = elData(grip, "dir");\n
      }\n
      // resizing\n
      else if(griptype == "resize") {\n
        current_mode = "resize";\n
        current_resize_mode = elData(grip, "dir");\n
      }\n
      mouse_target = selectedElements[0];\n
    }\n
    \n
    start_transform = mouse_target.getAttribute("transform");\n
    var tlist = getTransformList(mouse_target);\n
    switch (current_mode) {\n
      case "select":\n
        started = true;\n
        current_resize_mode = "none";\n
        if(right_click) started = false;\n
        \n
        if (mouse_target != svgroot) {\n
          // if this element is not yet selected, clear selection and select it\n
          if (selectedElements.indexOf(mouse_target) == -1) {\n
            // only clear selection if shift is not pressed (otherwise, add \n
            // element to selection)\n
            if (!evt.shiftKey) {\n
              // No need to do the call here as it will be done on addToSelection\n
              clearSelection(true);\n
            }\n
            addToSelection([mouse_target]);\n
            justSelected = mouse_target;\n
            pathActions.clear();\n
          }\n
          // else if it\'s a path, go into pathedit mode in mouseup\n
          \n
          if(!right_click) {\n
            // insert a dummy transform so if the element(s) are moved it will have\n
            // a transform to use for its translate\n
            for (var i = 0; i < selectedElements.length; ++i) {\n
              if(selectedElements[i] == null) continue;\n
              var slist = getTransformList(selectedElements[i]);\n
              if(slist.numberOfItems) {\n
                slist.insertItemBefore(svgroot.createSVGTransform(), 0);\n
              } else {\n
                slist.appendItem(svgroot.createSVGTransform());\n
              }\n
            }\n
          }\n
        }\n
        else if(!right_click){\n
          clearSelection();\n
          current_mode = "multiselect";\n
          if (rubberBox == null) {\n
            rubberBox = selectorManager.getRubberBandBox();\n
          }\n
          r_start_x *= current_zoom;\n
          r_start_y *= current_zoom;\n
//          console.log(\'p\',[evt.pageX, evt.pageY]);          \n
//          console.log(\'c\',[evt.clientX, evt.clientY]);  \n
//          console.log(\'o\',[evt.offsetX, evt.offsetY]);  \n
//          console.log(\'s\',[start_x, start_y]);\n
          \n
          assignAttributes(rubberBox, {\n
            \'x\': r_start_x,\n
            \'y\': r_start_y,\n
            \'width\': 0,\n
            \'height\': 0,\n
            \'display\': \'inline\'\n
          }, 100);\n
        }\n
        break;\n
      case "zoom": \n
        started = true;\n
        if (rubberBox == null) {\n
          rubberBox = selectorManager.getRubberBandBox();\n
        }\n
        assignAttributes(rubberBox, {\n
            \'x\': real_x * current_zoom,\n
            \'y\': real_x * current_zoom,\n
            \'width\': 0,\n
            \'height\': 0,\n
            \'display\': \'inline\'\n
        }, 100);\n
        break;\n
      case "resize":\n
        started = true;\n
        start_x = x;\n
        start_y = y;\n
        \n
        // Getting the BBox from the selection box, since we know we\n
        // want to orient around it\n
        init_bbox = svgedit.utilities.getBBox($(\'#selectedBox0\')[0]);\n
        var bb = {};\n
        $.each(init_bbox, function(key, val) {\n
          bb[key] = val/current_zoom;\n
        });\n
        init_bbox = bb;\n
        // append three dummy transforms to the tlist so that\n
        // we can translate,scale,translate in mousemove\n
        var pos = getRotationAngle(mouse_target)?1:0;\n
        \n
        if(hasMatrixTransform(tlist)) {\n
          tlist.insertItemBefore(svgroot.createSVGTransform(), pos);\n
          tlist.insertItemBefore(svgroot.createSVGTransform(), pos);\n
          tlist.insertItemBefore(svgroot.createSVGTransform(), pos);\n
        } else {\n
          tlist.appendItem(svgroot.createSVGTransform());\n
          tlist.appendItem(svgroot.createSVGTransform());\n
          tlist.appendItem(svgroot.createSVGTransform());\n
          \n
          if(svgedit.browser.supportsNonScalingStroke()) {\n
            //Handle crash for newer Webkit: https://code.google.com/p/svg-edit/issues/detail?id=904\n
            //Chromium issue: https://code.google.com/p/chromium/issues/detail?id=114625\n
            // TODO: Remove this workaround (all isChrome blocks) once vendor fixes the issue\n
            var isWebkit = svgedit.browser.isWebkit();\n
            if(isWebkit) {\n
              var delayedStroke = function(ele) {\n
                var _stroke = ele.getAttributeNS(null, \'stroke\');\n
                ele.removeAttributeNS(null, \'stroke\');\n
                //Re-apply stroke after delay. Anything higher than 1 seems to cause flicker\n
                setTimeout(function() { ele.setAttributeNS(null, \'stroke\', _stroke) }, 0);\n
              }\n
            }\n
            mouse_target.style.vectorEffect = \'non-scaling-stroke\';\n
            if(isWebkit) delayedStroke(mouse_target);\n
\n
            var all = mouse_target.getElementsByTagName(\'*\'),\n
                len = all.length;\n
            for(var i = 0; i < len; i++) {\n
              all[i].style.vectorEffect = \'non-scaling-stroke\';\n
              if(isWebkit) delayedStroke(all[i]);\n
            }\n
          }\n
        }\n
        break;\n
      case "fhellipse":\n
      case "fhrect":\n
      case "fhpath":\n
        started = true;\n
        d_attr = real_x + "," + real_y + " ";\n
        var stroke_w = cur_shape.stroke_width == 0?1:cur_shape.stroke_width;\n
        addSvgElementFromJson({\n
          "element": "polyline",\n
          "curStyles": true,\n
          "attr": {\n
            "points": d_attr,\n
            "id": getNextId(),\n
            "fill": "none",\n
            "opacity": cur_shape.opacity / 2,\n
            "stroke-linecap": "round",\n
            "style": "pointer-events:none"\n
          }\n
        });\n
        freehand.minx = real_x;\n
        freehand.maxx = real_x;\n
        freehand.miny = real_y;\n
        freehand.maxy = real_y;\n
        break;\n
      case "image":\n
        started = true;\n
        var newImage = addSvgElementFromJson({\n
          "element": "image",\n
          "attr": {\n
            "x": x,\n
            "y": y,\n
            "width": 0,\n
            "height": 0,\n
            "id": getNextId(),\n
            "opacity": cur_shape.opacity / 2,\n
            "style": "pointer-events:inherit"\n
          }\n
        });\n
        setHref(newImage, last_good_img_url);\n
        preventClickDefault(newImage);\n
        break;\n
      case "square":\n
        // FIXME: once we create the rect, we lose information that this was a square\n
        // (for resizing purposes this could be important)\n
      case "rect":\n
        started = true;\n
        start_x = x;\n
        start_y = y;\n
        addSvgElementFromJson({\n
          "element": "rect",\n
          "curStyles": true,\n
          "attr": {\n
            "x": x,\n
            "y": y,\n
            "width": 0,\n
            "height": 0,\n
            "id": getNextId(),\n
            "opacity": cur_shape.opacity / 2\n
          }\n
        });\n
        break;\n
      case "line":\n
        started = true;\n
        var stroke_w = cur_shape.stroke_width == 0?1:cur_shape.stroke_width;\n
        addSvgElementFromJson({\n
          "element": "line",\n
          "curStyles": true,\n
          "attr": {\n
            "x1": x,\n
            "y1": y,\n
            "x2": x,\n
            "y2": y,\n
            "id": getNextId(),\n
            "stroke": cur_shape.stroke,\n
            "stroke-width": stroke_w,\n
            "stroke-dasharray": cur_shape.stroke_dasharray,\n
            "stroke-linejoin": cur_shape.stroke_linejoin,\n
            "stroke-linecap": cur_shape.stroke_linecap,\n
            "stroke-opacity": cur_shape.stroke_opacity,\n
            "fill": "none",\n
            "opacity": cur_shape.opacity / 2,\n
            "style": "pointer-events:none"\n
          }\n
        });\n
        break;\n
      case "circle":\n
        started = true;\n
        addSvgElementFromJson({\n
          "element": "circle",\n
          "curStyles": true,\n
          "attr": {\n
            "cx": x,\n
            "cy": y,\n
            "r": 0,\n
            "id": getNextId(),\n
            "opacity": cur_shape.opacity / 2\n
          }\n
        });\n
        break;\n
      case "ellipse":\n
        started = true;\n
        addSvgElementFromJson({\n
          "element": "ellipse",\n
          "curStyles": true,\n
          "attr": {\n
            "cx": x,\n
            "cy": y,\n
            "rx": 0,\n
            "ry": 0,\n
            "id": getNextId(),\n
            "opacity": cur_shape.opacity / 2\n
          }\n
        });\n
        break;\n
      case "text":\n
        started = true;\n
        var newText = addSvgElementFromJson({\n
          "element": "text",\n
          "curStyles": true,\n
          "attr": {\n
            "x": x,\n
            "y": y,\n
            "id": getNextId(),\n
            "fill": cur_text.fill,\n
            "stroke-width": cur_text.stroke_width,\n
            "font-size": cur_text.font_size,\n
            "font-family": cur_text.font_family,\n
            "text-anchor": "start",\n
            "xml:space": "preserve",\n
            "opacity": cur_shape.opacity\n
          }\n
        });\n
//          newText.textContent = "text";\n
        break;\n
      case "path":\n
        // Fall through\n
      case "pathedit":\n
        start_x *= current_zoom;\n
        start_y *= current_zoom;\n
        pathActions.mouseDown(evt, mouse_target, start_x, start_y);\n
        started = true;\n
        break;\n
      case "textedit":\n
        start_x *= current_zoom;\n
        start_y *= current_zoom;\n
        textActions.mouseDown(evt, mouse_target, start_x, start_y);\n
        started = true;\n
        break;\n
      case "rotate":\n
        started = true;\n
        // we are starting an undoable change (a drag-rotation)\n
        canvas.undoMgr.beginUndoableCh

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
            <value> <string encoding="cdata"><![CDATA[

ange("transform", selectedElements);\n
        document.getElementById("workarea").className = "rotate";\n
        break;\n
      default:\n
        // This could occur in an extension\n
        break;\n
    }\n
    \n
    var ext_result = runExtensions("mouseDown", {\n
      event: evt,\n
      start_x: start_x,\n
      start_y: start_y,\n
      selectedElements: selectedElements\n
    }, true);\n
    \n
    $.each(ext_result, function(i, r) {\n
      if(r && r.started) {\n
        started = true;\n
      }\n
    });\n
    if (current_mode) {\n
      document.getElementById("workarea").className = \n
        (current_mode == "resize")\n
        ? evt.target.style.cursor\n
        : current_mode\n
      }\n
  };\n
  \n
  // in this function we do not record any state changes yet (but we do update\n
  // any elements that are still being created, moved or resized on the canvas)\n
  var mouseMove = function(evt) {\n
    if (evt.originalEvent.touches && evt.originalEvent.touches.length > 1) return;\n
    if (!started) return;\n
    if(evt.button === 1 || canvas.spaceKey) return;\n
    var selected = selectedElements[0],\n
      pt = transformPoint( evt.pageX, evt.pageY, root_sctm ),\n
      mouse_x = pt.x * current_zoom,\n
      mouse_y = pt.y * current_zoom,\n
      shape = getElem(getId());\n
\n
    var real_x = x = mouse_x / current_zoom;\n
    var real_y = y = mouse_y / current_zoom;\n
\n
    if(curConfig.gridSnapping){\n
      x = snapToGrid(x);\n
      y = snapToGrid(y);\n
    }\n
\n
    evt.preventDefault();\n
    \n
    switch (current_mode)\n
    {\n
      case "select":\n
        // we temporarily use a translate on the element(s) being dragged\n
        // this transform is removed upon mousing up and the element is \n
        // relocated to the new location\n
        if (selectedElements[0] !== null) {\n
          var dx = x - start_x;\n
          var dy = y - start_y;\n
          \n
          if(curConfig.gridSnapping){\n
            dx = snapToGrid(dx);\n
            dy = snapToGrid(dy);\n
          }\n
          \n
          if(evt.shiftKey) { \n
            var xya = snapToAngle(start_x,start_y,x,y); x=xya.x; y=xya.y;\n
         }\n
          if (dx != 0 || dy != 0) {\n
            var len = selectedElements.length;\n
            for (var i = 0; i < len; ++i) {\n
              var selected = selectedElements[i];\n
              if (selected == null) break;\n
//              if (i==0) {\n
//                var box = svgedit.utilities.getBBox(selected);\n
//                  selectedBBoxes[i].x = box.x + dx;\n
//                  selectedBBoxes[i].y = box.y + dy;\n
//              }\n
\n
              // update the dummy transform in our transform list\n
              // to be a translate\n
              var xform = svgroot.createSVGTransform();\n
              var tlist = getTransformList(selected);\n
              // Note that if Webkit and there\'s no ID for this\n
              // element, the dummy transform may have gotten lost.\n
              // This results in unexpected behaviour\n
              if (xya) {\n
                dx = xya.x - start_x\n
                dy = xya.y - start_y\n
              }\n
              xform.setTranslate(dx,dy);\n
              if(tlist.numberOfItems) {\n
                tlist.replaceItem(xform, 0);\n
              } else {\n
                tlist.appendItem(xform);\n
              }\n
              \n
              // update our internal bbox that we\'re tracking while dragging\n
              selectorManager.requestSelector(selected).resize();\n
            }\n
\n
            //duplicate only once\n
            // alt drag = create a clone and save the reference             \n
            if(evt.altKey) {\n
              //clone doesn\'t exist yet\n
              if (!canvas.addClones) {\n
                canvas.addClones = canvas.cloneSelectedElements(0,0, xform);\n
                canvas.removeClones = function(){\n
                  if (canvas.addClones) {\n
                    canvas.addClones.forEach(function(clone){\n
                      if (clone.parentNode) clone.parentNode.removeChild(clone)\n
                      canvas.addClones = false;\n
                    })\n
                  }\n
                }\n
                window.addEventListener("keyup", canvas.removeClones)\n
              }\n
            }\n
      \n
            call("transition", selectedElements);\n
          }\n
          \n
\n
\n
          \n
          \n
        }\n
        break;\n
      case "multiselect":\n
        real_x *= current_zoom;\n
        real_y *= current_zoom;\n
        assignAttributes(rubberBox, {\n
          \'x\': Math.min(r_start_x, real_x),\n
          \'y\': Math.min(r_start_y, real_y),\n
          \'width\': Math.abs(real_x - r_start_x),\n
          \'height\': Math.abs(real_y - r_start_y)\n
        },100);\n
\n
        // for each selected:\n
        // - if newList contains selected, do nothing\n
        // - if newList doesn\'t contain selected, remove it from selected\n
        // - for any newList that was not in selectedElements, add it to selected\n
        var elemsToRemove = [], elemsToAdd = [],\n
          newList = getIntersectionList(),\n
          len = selectedElements.length;\n
        \n
        for (var i = 0; i < len; ++i) {\n
          var ind = newList.indexOf(selectedElements[i]);\n
          if (ind == -1) {\n
            elemsToRemove.push(selectedElements[i]);\n
          }\n
          else {\n
            newList[ind] = null;\n
          }\n
        }\n
        \n
        len = newList.length;\n
        for (i = 0; i < len; ++i) { if (newList[i]) elemsToAdd.push(newList[i]); }\n
        \n
        if (elemsToRemove.length > 0) \n
          canvas.removeFromSelection(elemsToRemove);\n
        \n
        if (elemsToAdd.length > 0) \n
          addToSelection(elemsToAdd);\n
          \n
        break;\n
      case "resize":\n
        // we track the resize bounding box and translate/scale the selected element\n
        // while the mouse is down, when mouse goes up, we use this to recalculate\n
        // the shape\'s coordinates\n
        var tlist = getTransformList(selected),\n
          hasMatrix = hasMatrixTransform(tlist),\n
          box = hasMatrix ? init_bbox : svgedit.utilities.getBBox(selected), \n
          left=box.x, top=box.y, width=box.width,\n
          height=box.height, dx=(x-start_x), dy=(y-start_y);\n
        \n
        if(curConfig.gridSnapping){\n
          dx = snapToGrid(dx);\n
          dy = snapToGrid(dy);\n
          height = snapToGrid(height);\n
          width = snapToGrid(width);\n
        }\n
\n
        // if rotated, adjust the dx,dy values\n
        var angle = getRotationAngle(selected);\n
        if (angle) {\n
          var r = Math.sqrt( dx*dx + dy*dy ),\n
            theta = Math.atan2(dy,dx) - angle * Math.PI / 180.0;\n
          dx = r * Math.cos(theta);\n
          dy = r * Math.sin(theta);\n
        }\n
\n
        // if not stretching in y direction, set dy to 0\n
        // if not stretching in x direction, set dx to 0\n
        if(current_resize_mode.indexOf("n")==-1 && current_resize_mode.indexOf("s")==-1) {\n
          dy = 0;\n
        }\n
        if(current_resize_mode.indexOf("e")==-1 && current_resize_mode.indexOf("w")==-1) {\n
          dx = 0;\n
        }       \n
        \n
        var ts = null,\n
          tx = 0, ty = 0,\n
          sy = height ? (height+dy)/height : 1, \n
          sx = width ? (width+dx)/width : 1;\n
        // if we are dragging on the north side, then adjust the scale factor and ty\n
        if(current_resize_mode.indexOf("n") >= 0) {\n
          sy = height ? (height-dy)/height : 1;\n
          ty = height;\n
        }\n
        \n
        // if we dragging on the east side, then adjust the scale factor and tx\n
        if(current_resize_mode.indexOf("w") >= 0) {\n
          sx = width ? (width-dx)/width : 1;\n
          tx = width;\n
        }\n
        \n
        // update the transform list with translate,scale,translate\n
        var translateOrigin = svgroot.createSVGTransform(),\n
          scale = svgroot.createSVGTransform(),\n
          translateBack = svgroot.createSVGTransform();\n
\n
        if(curConfig.gridSnapping){\n
          left = snapToGrid(left);\n
          tx = snapToGrid(tx);\n
          top = snapToGrid(top);\n
          ty = snapToGrid(ty);\n
        }\n
\n
        translateOrigin.setTranslate(-(left+tx),-(top+ty));\n
        if(evt.shiftKey) {\n
          if(sx == 1) sx = sy\n
          else sy = sx;\n
        }\n
        scale.setScale(sx,sy);\n
        \n
        translateBack.setTranslate(left+tx,top+ty);\n
        if(hasMatrix) {\n
          var diff = angle?1:0;\n
          tlist.replaceItem(translateOrigin, 2+diff);\n
          tlist.replaceItem(scale, 1+diff);\n
          tlist.replaceItem(translateBack, 0+diff);\n
        } else {\n
          var N = tlist.numberOfItems;\n
          tlist.replaceItem(translateBack, N-3);\n
          tlist.replaceItem(scale, N-2);\n
          tlist.replaceItem(translateOrigin, N-1);\n
        }\n
\n
        selectorManager.requestSelector(selected).resize();\n
        \n
        call("transition", selectedElements);\n
        \n
        break;\n
      case "zoom":\n
        real_x *= current_zoom;\n
        real_y *= current_zoom;\n
        assignAttributes(rubberBox, {\n
          \'x\': Math.min(r_start_x*current_zoom, real_x),\n
          \'y\': Math.min(r_start_y*current_zoom, real_y),\n
          \'width\': Math.abs(real_x - r_start_x*current_zoom),\n
          \'height\': Math.abs(real_y - r_start_y*current_zoom)\n
        },100);     \n
        break;\n
      case "text":\n
        assignAttributes(shape,{\n
          \'x\': x,\n
          \'y\': y\n
        },1000);\n
        break;\n
      case "line":\n
        if(curConfig.gridSnapping){\n
          x = snapToGrid(x);\n
          y = snapToGrid(y);\n
        }\n
\n
        var x2 = x;\n
        var y2 = y;         \n
\n
        if(evt.shiftKey) { var xya = snapToAngle(start_x,start_y,x2,y2); x2=xya.x; y2=xya.y; }\n
        \n
        shape.setAttributeNS(null, "x2", x2);\n
        shape.setAttributeNS(null, "y2", y2);\n
        break;\n
      case "foreignObject":\n
        // fall through\n
      case "square":\n
        // fall through\n
      case "rect":\n
      case "image":\n
        var square = (current_mode == \'square\') || evt.shiftKey,\n
          w = Math.abs(x - start_x),\n
          h = Math.abs(y - start_y),\n
          new_x, new_y;\n
        if(square) {\n
          w = h = Math.max(w, h);\n
          new_x = start_x < x ? start_x : start_x - w;\n
          new_y = start_y < y ? start_y : start_y - h;\n
        } else {\n
          new_x = Math.min(start_x,x);\n
          new_y = Math.min(start_y,y);\n
        }\n
        if (evt.altKey){\n
          w *=2;\n
          h *=2; \n
          new_x = start_x - w/2;\n
          new_y = start_y - h/2;\n
        }\n
  \n
        if(curConfig.gridSnapping){\n
          w = snapToGrid(w);\n
          h = snapToGrid(h);\n
          new_x = snapToGrid(new_x);\n
          new_y = snapToGrid(new_y);\n
        }\n
\n
        assignAttributes(shape,{\n
          \'width\': w,\n
          \'height\': h,\n
          \'x\': new_x,\n
          \'y\': new_y\n
        },1000);\n
        \n
        break;\n
      case "circle":\n
        var c = $(shape).attr(["cx", "cy"]);\n
        var cx = c.cx, cy = c.cy,\n
          rad = Math.sqrt( (x-cx)*(x-cx) + (y-cy)*(y-cy) );\n
        if(curConfig.gridSnapping){\n
          rad = snapToGrid(rad);\n
        }\n
        shape.setAttributeNS(null, "r", rad);\n
        break;\n
      case "ellipse":\n
        var c = $(shape).attr(["cx", "cy"]);\n
        var cx = Math.abs(start_x + (x - start_x)/2)\n
        var cy = Math.abs(start_y + (y - start_y)/2);\n
        if(curConfig.gridSnapping){\n
          x = snapToGrid(x);\n
          cx = snapToGrid(cx);\n
          y = snapToGrid(y);\n
          cy = snapToGrid(cy);\n
        }\n
        var rx = Math.abs(start_x - cx)\n
        var ry = Math.abs(start_y - cy);\n
        if (evt.shiftKey) {\n
          ry = rx\n
          cy = (y > start_y) ? start_y + rx : start_y - rx\n
          \n
        }\n
        if (evt.altKey) {\n
          cx = start_x\n
          cy = start_y\n
          rx = Math.abs(x - cx)\n
          ry = evt.shiftKey ? rx : Math.abs(y - cy);\n
        }\n
        shape.setAttributeNS(null, "rx", rx );\n
        shape.setAttributeNS(null, "ry", ry );\n
        shape.setAttributeNS(null, "cx", cx );\n
        shape.setAttributeNS(null, "cy", cy );\n
        break;\n
      case "fhellipse":\n
      case "fhrect":\n
        freehand.minx = Math.min(real_x, freehand.minx);\n
        freehand.maxx = Math.max(real_x, freehand.maxx);\n
        freehand.miny = Math.min(real_y, freehand.miny);\n
        freehand.maxy = Math.max(real_y, freehand.maxy);\n
      // break; missing on purpose\n
      case "fhpath":\n
        d_attr += + real_x + "," + real_y + " ";\n
        shape.setAttributeNS(null, "points", d_attr);\n
        break;\n
      // update path stretch line coordinates\n
      case "path":\n
        // fall through\n
      case "pathedit":\n
        x *= current_zoom;\n
        y *= current_zoom;\n
        \n
        if(curConfig.gridSnapping){\n
          x = snapToGrid(x);\n
          y = snapToGrid(y);\n
          start_x = snapToGrid(start_x);\n
          start_y = snapToGrid(start_y);\n
        }\n
        if(evt.shiftKey) {\n
          var path = svgedit.path.path;\n
          if(path) {\n
            var x1 = path.dragging?path.dragging[0]:start_x;\n
            var y1 = path.dragging?path.dragging[1]:start_y;\n
          } else {\n
            var x1 = start_x;\n
            var y1 = start_y;\n
          }\n
          var xya = snapToAngle(x1,y1,x,y);\n
          x=xya.x; y=xya.y;\n
        }\n
        \n
        if(rubberBox && rubberBox.getAttribute(\'display\') !== \'none\') {\n
          real_x *= current_zoom;\n
          real_y *= current_zoom;\n
          assignAttributes(rubberBox, {\n
            \'x\': Math.min(r_start_x*current_zoom, real_x),\n
            \'y\': Math.min(r_start_y*current_zoom, real_y),\n
            \'width\': Math.abs(real_x - r_start_x*current_zoom),\n
            \'height\': Math.abs(real_y - r_start_y*current_zoom)\n
          },100); \n
        }\n
        pathActions.mouseMove(evt, x, y);\n
        \n
        break;\n
      case "textedit":\n
        x *= current_zoom;\n
        y *= current_zoom;\n
//          if(rubberBox && rubberBox.getAttribute(\'display\') != \'none\') {\n
//            assignAttributes(rubberBox, {\n
//              \'x\': Math.min(start_x,x),\n
//              \'y\': Math.min(start_y,y),\n
//              \'width\': Math.abs(x-start_x),\n
//              \'height\': Math.abs(y-start_y)\n
//            },100);\n
//          }\n
        \n
        textActions.mouseMove(mouse_x, mouse_y);\n
        \n
        break;\n
      case "rotate":\n
        var box = svgedit.utilities.getBBox(selected),\n
          cx = box.x + box.width/2, \n
          cy = box.y + box.height/2,\n
          m = getMatrix(selected),\n
          center = transformPoint(cx,cy,m);\n
        cx = center.x;\n
        cy = center.y;\n
        var ccx = box.x // ne\n
        var ccy = box.y // ne\n
        if (current_rotate_mode == "nw")  ccx = box.x + box.width;\n
        if (current_rotate_mode == "se")  ccy = box.y + box.height;\n
        if (current_rotate_mode == "sw"){ ccx = box.x + box.width; ccy = box.y + box.height;  }\n
        compensation_angle = ((Math.atan2(cy-ccy,cx-ccx)  * (180/Math.PI))-90) % 360;\n
        var angle = ((Math.atan2(cy-y,cx-x)  * (180/Math.PI))-90) % 360;\n
        angle += compensation_angle;\n
        if(curConfig.gridSnapping){\n
          angle = snapToGrid(angle);\n
        }\n
        if(evt.shiftKey) { // restrict rotations to nice angles (WRS)\n
          var snap = 45;\n
          angle= Math.round(angle/snap)*snap;\n
        }\n
\n
        canvas.setRotationAngle(angle<-180?(360+angle):angle, true);\n
        call("transition", selectedElements);\n
        break;\n
      default:\n
        break;\n
    }\n
    \n
    runExtensions("mouseMove", {\n
      event: evt,\n
      mouse_x: mouse_x,\n
      mouse_y: mouse_y,\n
      selected: selected\n
    });\n
\n
  }; // mouseMove()\n
  \n
  \n
  /* mouseover mode\n
  var mouseOver = function(evt) {\n
    \n
    if(canvas.spaceKey || evt.button === 1 || current_mode != "select") return;\n
    evt.stopPropagation();\n
    mouse_target = getMouseTarget(evt);\n
    if (svghover.lastChild) svghover.removeChild(svghover.lastChild);\n
    \n
    if (mouse_target.id == "svgroot") return\n
    switch (mouse_target.nodeName) {\n
      case "polyline":\n
      case "line":\n
      case "path":\n
      case "ellipse":\n
      case "rect":\n
          var clone = mouse_target.cloneNode(true); \n
          clone.setAttribute("stroke", "#c00")\n
          clone.setAttribute("stroke-width", "1")\n
          clone.setAttribute("stroke-opacity", "1")\n
          clone.setAttribute("shape-rendering", "crispEdges")\n
          clone.setAttribute("fill", "none")\n
          hover_group.appendChild(clone);\n
      break;\n
        \n
      default:\n
      break;\n
    }\n
  }\n
  */\n
  \n
  // - in create mode, the element\'s opacity is set properly, we create an InsertElementCommand\n
  //   and store it on the Undo stack\n
  // - in move/resize mode, the element\'s attributes which were affected by the move/resize are\n
  //   identified, a ChangeElementCommand is created and stored on the stack for those attrs\n
  //   this is done in when we recalculate the selected dimensions()\n
  var mouseUp = function(evt)\n
  {\n
    canvas.addClones = false;\n
    window.removeEventListener("keyup", canvas.removeClones)\n
    selectedElements = selectedElements.filter(Boolean)\n
    if(evt.button === 2) return;\n
    var tempJustSelected = justSelected;\n
    justSelected = null;\n
    if (!started) return;\n
    var pt = transformPoint( evt.pageX, evt.pageY, root_sctm ),\n
      mouse_x = pt.x * current_zoom,\n
      mouse_y = pt.y * current_zoom,\n
      x = mouse_x / current_zoom,\n
      y = mouse_y / current_zoom,\n
      element = getElem(getId()),\n
      keep = false;\n
\n
    var real_x = x;\n
    var real_y = y;\n
\n
    // TODO: Make true when in multi-unit mode\n
    var useUnit = false; // (curConfig.baseUnit !== \'px\');\n
    started = false;\n
    switch (current_mode)\n
    {\n
      // intentionally fall-through to select here\n
      case "resize":\n
      case "multiselect":\n
        if (rubberBox != null) {\n
          rubberBox.setAttribute("display", "none");\n
          curBBoxes = [];\n
        }\n
        current_mode = "select";\n
      case "select":\n
        if (selectedElements[0] != null) {\n
          // if we only have one selected element\n
          if (selectedElements.length == 1) {\n
            // set our current stroke/fill properties to the element\'s\n
            var selected = selectedElements[0];\n
            switch ( selected.tagName ) {\n
              case "g":\n
              case "use":\n
              case "image":\n
              case "foreignObject":\n
                break;\n
              default:\n
                cur_properties.fill = selected.getAttribute("fill");\n
                cur_properties.fill_opacity = selected.getAttribute("fill-opacity");\n
                cur_properties.stroke = selected.getAttribute("stroke");\n
                cur_properties.stroke_opacity = selected.getAttribute("stroke-opacity");\n
                cur_properties.stroke_width = selected.getAttribute("stroke-width");\n
                cur_properties.stroke_dasharray = selected.getAttribute("stroke-dasharray");\n
                cur_properties.stroke_linejoin = selected.getAttribute("stroke-linejoin");\n
                cur_properties.stroke_linecap = selected.getAttribute("stroke-linecap");\n
            }\n
            if (selected.tagName == "text") {\n
              cur_text.font_size = selected.getAttribute("font-size");\n
              cur_text.font_family = selected.getAttribute("font-family");\n
            }\n
            selectorManager.requestSelector(selected).showGrips(true);\n
            \n
            // This shouldn\'t be necessary as it was done on mouseDown...\n
//              call("selected", [selected]);\n
          }\n
          // always recalculate dimensions to strip off stray identity transforms\n
          recalculateAllSelectedDimensions();\n
\n
          // if it was being dragged/resized\n
          r_start_x = r_start_x; \n
          r_start_y = r_start_y; \n
          var difference_x = Math.abs(real_x-r_start_x);\n
          var difference_y = Math.abs(real_y-r_start_y);\n
\n
          if (difference_y > 1 || difference_y > 1) {\n
            var len = selectedElements.length;\n
            for (var i = 0; i < len; ++i) {\n
              if (selectedElements[i] == null) break;\n
              if(!selectedElements[i].firstChild) {\n
                // Not needed for groups (incorrectly resizes elems), possibly not needed at all?\n
                selectorManager.requestSelector(selectedElements[i]).resize();\n
              }\n
            }\n
          }\n
          // no change in position/size, so maybe we should move to pathedit\n
          else {\n
            var t = evt.target;\n
            if (selectedElements[0].nodeName === "path" && selectedElements[1] == null) {\n
              pathActions.select(selectedElements[0]);\n
            } // if it was a path\n
            // else, if it was selected and this is a shift-click, remove it from selection\n
            else if (evt.shiftKey) {\n
              if(tempJustSelected != t) {\n
                canvas.removeFromSelection([t]);\n
              }\n
            }\n
          } // no change in mouse position\n
          \n
          // Remove non-scaling stroke\n
          if(svgedit.browser.supportsNonScalingStroke()) {\n
            var elem = selectedElements[0];\n
            if (elem) {\n
              elem.removeAttribute(\'style\');\n
              svgedit.utilities.walkTree(elem, function(elem) {\n
                elem.removeAttribute(\'style\');\n
              });\n
            }\n
          }\n
\n
        }\n
        return;\n
        break;\n
      case "zoom":\n
        if (rubberBox != null) {\n
          rubberBox.setAttribute("display", "none");\n
        }\n
        var factor = evt.altKey?.5:2;\n
        call("zoomed", {\n
          \'x\': Math.min(r_start_x, real_x),\n
          \'y\': Math.min(r_start_y, real_y),\n
          \'width\': Math.abs(real_x - r_start_x),\n
          \'height\': Math.abs(real_y - r_start_y),\n
          \'factor\': factor\n
        });\n
        return;\n
      case "fhpath":\n
        // Check that the path contains at least 2 points; a degenerate one-point path\n
        // causes problems.\n
        // Webkit ignores how we set the points attribute with commas and uses space\n
        // to separate all coordinates, see https://bugs.webkit.org/show_bug.cgi?id=29870\n
        var coords = element.getAttribute(\'points\');\n
        var commaIndex = coords.indexOf(\',\');\n
        if (commaIndex >= 0) {\n
          keep = coords.indexOf(\',\', commaIndex+1) >= 0;\n
        } else {\n
          keep = coords.indexOf(\' \', coords.indexOf(\' \')+1) >= 0;\n
        }\n
        if (keep) {\n
          element = pathActions.smoothPolylineIntoPath(element);\n
        }\n
        break;\n
      case "line":\n
        var attrs = $(element).attr(["x1", "x2", "y1", "y2"]);\n
        keep = (attrs.x1 != attrs.x2 || attrs.y1 != attrs.y2);\n
        break;\n
      case "foreignObject":\n
      case "square":\n
      case "rect":\n
      case "image":\n
        var attrs = $(element).attr(["width", "height"]);\n
        // Image should be kept regardless of size (use inherit dimensions later)\n
        keep = (attrs.width != 0 || attrs.height != 0) || current_mode === "image";\n
        break;\n
      case "circle":\n
        keep = (element.getAttribute(\'r\') != 0);\n
        break;\n
      case "ellipse":\n
        var attrs = $(element).attr(["rx", "ry"]);\n
        keep = (attrs.rx != null || attrs.ry != null);\n
        break;\n
      case "fhellipse":\n
        if ((freehand.maxx - freehand.minx) > 0 &&\n
          (freehand.maxy - freehand.miny) > 0) {\n
          element = addSvgElementFromJson({\n
            "element": "ellipse",\n
            "curStyles": true,\n
            "attr": {\n
              "cx": (freehand.minx + freehand.maxx) / 2,\n
              "cy": (freehand.miny + freehand.maxy) / 2,\n
              "rx": (freehand.maxx - freehand.minx) / 2,\n
              "ry": (freehand.maxy - freehand.miny) / 2,\n
              "id": getId()\n
            }\n
          });\n
          call("changed",[element]);\n
          keep = true;\n
        }\n
        break;\n
      case "fhrect":\n
        if ((freehand.maxx - freehand.minx) > 0 &&\n
          (freehand.maxy - freehand.miny) > 0) {\n
          element = addSvgElementFromJson({\n
            "element": "rect",\n
            "curStyles": true,\n
            "attr": {\n
              "x": freehand.minx,\n
              "y": freehand.miny,\n
              "width": (freehand.maxx - freehand.minx),\n
              "height": (freehand.maxy - freehand.miny),\n
              "id": getId()\n
            }\n
          });\n
          call("changed",[element]);\n
          keep = true;\n
        }\n
        break;\n
      case "text":\n
        keep = true;\n
        selectOnly([element]);\n
        textActions.start(element);\n
        break;\n
      case "path":\n
        // set element to null here so that it is not removed nor finalized\n
        element = null;\n
        // continue to be set to true so that mouseMove happens\n
        started = true;\n
        \n
        var res = pathActions.mouseUp(evt, element, mouse_x, mouse_y);\n
        element = res.element;\n
        keep = res.keep;\n
        break;\n
      case "pathedit":\n
        keep = true;\n
        element = null;\n
        pathActions.mouseUp(evt);\n
        break;\n
      case "textedit":\n
        keep = false;\n
        element = null;\n
        textActions.mouseUp(evt, mouse_x, mouse_y);\n
        break;\n
      case "rotate":\n
        keep = true;\n
        element = null;\n
        current_mode = "select";\n
        var batchCmd = canvas.undoMgr.finishUndoableChange();\n
        if (!batchCmd.isEmpty()) { \n
          addCommandToHistory(batchCmd);\n
        }\n
        // perform recalculation to weed out any stray identity transforms that might get stuck\n
        recalculateAllSelectedDimensions();\n
        call("changed", selectedElements);\n
        break;\n
      default:\n
        // This could occur in an extension\n
        break;\n
    }\n
    \n
    var ext_result = runExtensions("mouseUp", {\n
      event: evt,\n
      mouse_x: mouse_x,\n
      mouse_y: mouse_y\n
    }, true);\n
    \n
    $.each(ext_result, function(i, r) {\n
      if(r) {\n
        keep = r.keep || keep;\n
        element = r.element;\n
        started = r.started || started;\n
      }\n
    });\n
    \n
    if (!keep && element != null) {\n
      getCurrentDrawing().releaseId(getId());\n
      element.parentNode.removeChild(element);\n
      element = null;\n
      \n
      var t = evt.target;\n
      \n
      // if this element is in a group, go up until we reach the top-level group \n
      // just below the layer groups\n
      // TODO: once we implement links, we also would have to check for <a> elements\n
      while (t.parentNode.parentNode.tagName == "g") {\n
        t = t.parentNode;\n
      }\n
      // if we are not in the middle of creating a path, and we\'ve clicked on some shape, \n
      // then go to Select mode.\n
      // WebKit returns <div> when the canvas is clicked, Firefox/Opera return <svg>\n
      if ( (current_mode != "path" || !drawn_path) &&\n
        t.parentNode.id != "selectorParentGroup" &&\n
        t.id != "svgcanvas" && t.id != "svgroot") \n
      {\n
        // switch into "select" mode if we\'ve clicked on an element\n
        canvas.setMode("select");\n
        selectOnly([t], true);\n
      }\n
      \n
    } else if (element != null) {\n
      canvas.addedNew = true;\n
      \n
      if(useUnit) svgedit.units.convertAttrs(element);\n
      \n
      var ani_dur = .2, c_ani;\n
      if(opac_ani.beginElement && element.getAttribute(\'opacity\') != cur_shape.opacity) {\n
        c_ani = $(opac_ani).clone().attr({\n
          to: cur_shape.opacity,\n
          dur: ani_dur\n
        }).appendTo(element);\n
        try {\n
          // Fails in FF4 on foreignObject\n
          c_ani[0].beginElement();\n
        } catch(e){}\n
      } else {\n
        ani_dur = 0;\n
      }\n
      \n
      // Ideally this would be done on the endEvent of the animation,\n
      // but that doesn\'t seem to be supported in Webkit\n
      setTimeout(function() {\n
        if(c_ani) c_ani.remove();\n
        element.setAttribute("opacity", cur_shape.opacity);\n
        element.setAttribute("style", "pointer-events:inherit");\n
        cleanupElement(element);\n
        if(current_mode === "path") {\n
          pathActions.toEditMode(element);\n
        } else {\n
          if(curConfig.selectNew) {\n
            selectOnly([element], true);\n
          }\n
        }\n
        // we create the insert command that is stored on the stack\n
        // undo means to call cmd.unapply(), redo means to call cmd.apply()\n
        addCommandToHistory(new InsertElementCommand(element));\n
        \n
        call("changed",[element]);\n
      }, ani_dur * 1000);\n
    }\n
    \n
    start_transform = null;\n
  };\n
  \n
  var dblClick = function(evt) {\n
    var evt_target = evt.target;\n
    var parent = evt_target.parentNode;\n
    var mouse_target = getMouseTarget(evt);\n
    var tagName = mouse_target.tagName;\n
\n
    if(parent === current_group) return;\n
    \n
    if(tagName === \'text\' && current_mode !== \'textedit\') {\n
      var pt = transformPoint( evt.pageX, evt.pageY, root_sctm );\n
      textActions.select(mouse_target, pt.x, pt.y);\n
    }\n
    \n
    if((tagName === "g" || tagName === "a") && getRotationAngle(mouse_target)) {\n
      // TODO: Allow method of in-group editing without having to do \n
      // this (similar to editing rotated paths)\n
    \n
      // Ungroup and regroup\n
      pushGroupProperties(mouse_target);\n
      mouse_target = selectedElements[0];\n
      clearSelection(true);\n
    }\n
    // Reset context\n
    if(current_group) {\n
      leaveContext();\n
    }\n
    \n
    if((parent.tagName !== \'g\' && parent.tagName !== \'a\') ||\n
      parent === getCurrentDrawing().getCurrentLayer() ||\n
      mouse_target === selectorManager.selectorParentGroup)\n
    {\n
      // Escape from in-group edit\n
      return;\n
    }\n
    setContext(mouse_target);\n
  }\n
\n
  // prevent links from being followed in the canvas\n
  var handleLinkInCanvas = function(e) {\n
    e.preventDefault();\n
    return false;\n
  };\n
  \n
  // Added mouseup to the container here.\n
  // TODO(codedread): Figure out why after the Closure compiler, the window mouseup is ignored.\n
  $(container).mousedown(mouseDown).mousemove(mouseMove).click(handleLinkInCanvas).dblclick(dblClick).mouseup(mouseUp);\n
//  $(window).mouseup(mouseUp);\n
  \n
  $(container).bind("mousewheel DOMMouseScroll", function(e){\n
    if(!e.shiftKey) return;\n
    e.preventDefault();\n
\n
    root_sctm = svgcontent.getScreenCTM().inverse();\n
    var pt = transformPoint( e.pageX, e.pageY, root_sctm );\n
    var bbox = {\n
      \'x\': pt.x,\n
      \'y\': pt.y,\n
      \'width\': 0,\n
      \'height\': 0\n
    };\n
\n
    // Respond to mouse wheel in IE/Webkit/Opera.\n
    // (It returns up/dn motion in multiples of 120)\n
    if(e.wheelDelta) {\n
      if (e.wheelDelta >= 120) {\n
        bbox.factor = 2;\n
      } else if (e.wheelDelta <= -120) {\n
        bbox.factor = .5;\n
      }\n
    } else if(e.detail) {\n
      if (e.detail > 0) {\n
        bbox.factor = .5;\n
      } else if (e.detail < 0) {\n
        bbox.factor = 2;      \n
      }       \n
    }\n
    \n
    if(!bbox.factor) return;\n
    call("zoomed", bbox);\n
  });\n
  \n
}());\n
\n
// Function: preventClickDefault\n
// Prevents default browser click behaviour on the given element\n
//\n
// Parameters:\n
// img - The DOM element to prevent the cilck on\n
var preventClickDefault = function(img) {\n
  $(img).click(function(e){e.preventDefault()});\n
}\n
\n
// Group: Text edit functions\n
// Functions relating to editing text elements\n
var textActions = canvas.textActions = function() {\n
  var curtext;\n
  var textinput;\n
  var cursor;\n
  var selblock;\n
  var blinker;\n
  var chardata = [];\n
  var textbb, transbb;\n
  var matrix;\n
  var last_x, last_y;\n
  var allow_dbl;\n
  \n
  function setCursor(index) {\n
    var empty = (textinput.value === "");\n
    $(textinput).focus();\n
  \n
    if(!arguments.length) {\n
      if(empty) {\n
        index = 0;\n
      } else {\n
        if(textinput.selectionEnd !== textinput.selectionStart) return;\n
        index = textinput.selectionEnd;\n
      }\n
    }\n
    \n
    var charbb;\n
    charbb = chardata[index];\n
    if(!empty) {\n
      textinput.setSelectionRange(index, index);\n
    }\n
    cursor = getElem("text_cursor");\n
    if (!cursor) {\n
      cursor = document.createElementNS(svgns, "line");\n
      assignAttributes(cursor, {\n
        \'id\': "text_cursor",\n
        \'stroke\': "#333",\n
        \'stroke-width\': 1\n
      });\n
      cursor = getElem("selectorParentGroup").appendChild(cursor);\n
    }\n
    \n
    if(!blinker) {\n
      blinker = setInterval(function() {\n
        var show = (cursor.getAttribute(\'display\') === \'none\');\n
        cursor.setAttribute(\'display\', show?\'inline\':\'none\');\n
      }, 600);\n
\n
    }\n
    \n
    \n
    var start_pt = ptToScreen(charbb.x, textbb.y);\n
    var end_pt = ptToScreen(charbb.x, (textbb.y + textbb.height));\n
    \n
    assignAttributes(cursor, {\n
      x1: start_pt.x,\n
      y1: start_pt.y,\n
      x2: end_pt.x,\n
      y2: end_pt.y,\n
      visibility: \'visible\',\n
      display: \'inline\'\n
    });\n
    \n
    if(selblock) selblock.setAttribute(\'d\', \'M 0 0\');\n
  }\n
  \n
  function setSelection(start, end, skipInput) {\n
    if(start === end) {\n
      setCursor(end);\n
      return;\n
    }\n
  \n
    if(!skipInput) {\n
      textinput.setSelectionRange(start, end);\n
    }\n
    \n
    selblock = getElem("text_selectblock");\n
    if (!selblock) {\n
\n
      selblock = document.createElementNS(svgns, "path");\n
      assignAttributes(selblock, {\n
        \'id\': "text_selectblock",\n
        \'fill\': "green",\n
        \'opacity\': .5,\n
        \'style\': "pointer-events:none"\n
      });\n
      getElem("selectorParentGroup").appendChild(selblock);\n
    }\n
\n
    \n
    var startbb = chardata[start];\n
    \n
    var endbb = chardata[end];\n
    \n
    cursor.setAttribute(\'visibility\', \'hidden\');\n
    \n
    var tl = ptToScreen(startbb.x, textbb.y),\n
      tr = ptToScreen(startbb.x + (endbb.x - startbb.x), textbb.y),\n
      bl = ptToScreen(startbb.x, textbb.y + textbb.height),\n
      br = ptToScreen(startbb.x + (endbb.x - startbb.x), textbb.y + textbb.height);\n
    \n
    \n
    var dstr = "M" + tl.x + "," + tl.y\n
          + " L" + tr.x + "," + tr.y\n
          + " " + br.x + "," + br.y\n
          + " " + bl.x + "," + bl.y + "z";\n
    \n
    assignAttributes(selblock, {\n
      d: dstr,\n
      \'display\': \'inline\'\n
    });\n
  }\n
  \n
  function getIndexFromPoint(mouse_x, mouse_y) {\n
    // Position cursor here\n
    var pt = svgroot.createSVGPoint();\n
    pt.x = mouse_x;\n
    pt.y = mouse_y;\n
\n
    // No content, so return 0\n
    if(chardata.length == 1) return 0;\n
    // Determine if cursor should be on left or right of character\n
    var charpos = curtext.getCharNumAtPosition(pt);\n
    if(charpos < 0) {\n
      // Out of text range, look at mouse coords\n
      charpos = chardata.length - 2;\n
      if(mouse_x <= chardata[0].x) {\n
        charpos = 0;\n
      }\n
    } else if(charpos >= chardata.length - 2) {\n
      charpos = chardata.length - 2;\n
    }\n
    var charbb = chardata[charpos];\n
    var mid = charbb.x + (charbb.width/2);\n
    if(mouse_x > mid) {\n
      charpos++;\n
    }\n
    return charpos;\n
  }\n
  \n
  function setCursorFromPoint(mouse_x, mouse_y) {\n
    setCursor(getIndexFromPoint(mouse_x, mouse_y));\n
  }\n
  \n
  function setEndSelectionFromPoint(x, y, apply) {\n
    var i1 = textinput.selectionStart;\n
    var i2 = getIndexFromPoint(x, y);\n
    \n
    var start = Math.min(i1, i2);\n
    var end = Math.max(i1, i2);\n
    setSelection(start, end, !apply);\n
  }\n
    \n
  function screenToPt(x_in, y_in) {\n
    var out = {\n
      x: x_in,\n
      y: y_in\n
    }\n
    \n
    out.x /= current_zoom;\n
    out.y /= current_zoom;      \n
\n
    if(matrix) {\n
      var pt = transformPoint(out.x, out.y, matrix.inverse());\n
      out.x = pt.x;\n
      out.y = pt.y;\n
    }\n
    \n
    return out;\n
  } \n
  \n
  function ptToScreen(x_in, y_in) {\n
    var out = {\n
      x: x_in,\n
      y: y_in\n
    }\n
    \n
    if(matrix) {\n
      var pt = transformPoint(out.x, out.y, matrix);\n
      out.x = pt.x;\n
      out.y = pt.y;\n
    }\n
    \n
    out.x *= current_zoom;\n
    out.y *= current_zoom;\n
    \n
    return out;\n
  }\n
  \n
  function hideCursor() {\n
    if(cursor) {\n
      cursor.setAttribute(\'visibility\', \'hidden\');\n
    }\n
  }\n
  \n
  function selectAll(evt) {\n
    setSelection(0, curtext.textContent.length);\n
    $(this).unbind(evt);\n
  }\n
\n
  function selectWord(evt) {\n
    if(!allow_dbl || !curtext) return;\n
  \n
    var ept = transformPoint( evt.pageX, evt.pageY, root_sctm ),\n
      mouse_x = ept.x * current_zoom,\n
      mouse_y = ept.y * current_zoom;\n
    var pt = screenToPt(mouse_x, mouse_y);\n
    \n
    var index = getIndexFromPoint(pt.x, pt.y);\n
    var str = curtext.textContent;\n
    var first = str.substr(0, index).replace(/[a-z0-9]+$/i, \'\').length;\n
    var m = str.substr(index).match(/^[a-z0-9]+/i);\n
    var last = (m?m[0].length:0) + index;\n
    setSelection(first, last);\n
    \n
    // Set tripleclick\n
    $(evt.target).click(selectAll);\n
    setTimeout(function() {\n
      $(evt.target).unbind(\'click\', selectAll);\n
    }, 300);\n
    \n
  }\n
\n
  return {\n
    select: function(target, x, y) {\n
      curtext = target;\n
      textActions.toEditMode(x, y);\n
    },\n
    start: function(elem) {\n
      curtext = elem;\n
      textActions.toEditMode();\n
    },\n
    mouseDown: function(evt, mouse_target, start_x, start_y) {\n
      var pt = screenToPt(start_x, start_y);\n
    \n
      textinput.focus();\n
      setCursorFromPoint(pt.x, pt.y);\n
      last_x = start_x;\n
      last_y = start_y;\n
      \n
      // TODO: Find way to block native selection\n
    },\n
    mouseMove: function(mouse_x, mouse_y) {\n
      var pt = screenToPt(mouse_x, mouse_y);\n
      setEndSelectionFromPoint(pt.x, pt.y);\n
    },      \n
    mouseUp: function(evt, mouse_x, mouse_y) {\n
      var pt = screenToPt(mouse_x, mouse_y);\n
      \n
      setEndSelectionFromPoint(pt.x, pt.y, true);\n
      \n
      // TODO: Find a way to make this work: Use transformed BBox instead of evt.target \n
//        if(last_x === mouse_x && last_y === mouse_y\n
//          && !svgedit.math.rectsIntersect(transbb, {x: pt.x, y: pt.y, width:0, height:0})) {\n
//          textActions.toSelectMode(true);       \n
//        }\n
\n
      if(\n
        evt.target !== curtext\n
        &&  mouse_x < last_x + 2\n
        && mouse_x > last_x - 2\n
        &&  mouse_y < last_y + 2\n
        && mouse_y > last_y - 2) {\n
\n
        textActions.toSelectMode(true);\n
      }\n
\n
    },\n
    setCursor: setCursor,\n
    toEditMode: function(x, y) {\n
      selectOnly([curtext], false)\n
      allow_dbl = false;\n
      current_mode = "textedit";\n
      selectorManager.requestSelector(curtext).showGrips(false);\n
    \n
      // Make selector group accept clicks\n
      var sel = selectorManager.requestSelector(curtext).selectorRect;\n
      \n
      textActions.init();\n
\n
      $(curtext).css(\'cursor\', \'text\');\n
      \n
      if(!arguments.length) {\n
        setCursor();\n
      } else {\n
        var pt = screenToPt(x, y);\n
        setCursorFromPoint(pt.x, pt.y);\n
      }\n
      \n
      setTimeout(function() {\n
        allow_dbl = true;\n
      }, 300);\n
    },\n
    toSelectMode: function(selectElem) {\n
      current_mode = "select";\n
      clearInterval(blinker);\n
      blinker = null;\n
      if(selblock) $(selblock).attr(\'display\',\'none\');\n
      if(cursor) $(cursor).attr(\'visibility\',\'hidden\');\n
      $(curtext).css(\'cursor\', \'move\');\n
      \n
      if(selectElem) {\n
        clearSelection();\n
        $(curtext).css(\'cursor\', \'move\');\n
        \n
        call("selected", [curtext]);\n
        addToSelection([curtext], true);\n
      }\n
      if(curtext && !curtext.textContent.length) {\n
        // No content, so delete\n
        canvas.deleteSelectedElements();\n
      }\n
      \n
      $(textinput).blur();\n
      \n
      curtext = false;\n
      \n
//        if(svgedit.browser.supportsEditableText()) {\n
//          curtext.removeAttribute(\'editable\');\n
//        }\n
    },\n
    setInputElem: function(elem) {\n
      textinput = elem;\n
//      $(textinput).blur(hideCursor);\n
    },\n
    clear: function() {\n
      if(current_mode == "textedit") {\n
        textActions.toSelectMode();\n
      }\n
    },\n
    init: function(inputElem) {\n
      if(!curtext) return;\n
\n
//        if(svgedit.browser.supportsEditableText()) {\n
//          curtext.select();\n
//          return;\n
//        }\n
    \n
      if(!curtext.parentNode) {\n
        // Result of the ffClone, need to get correct element\n
        curtext = selectedElements[0];\n
        selectorManager.requestSelector(curtext).showGrips(false);\n
      }\n
      \n
      var str = curtext.textContent;\n
      var len = str.length;\n
      \n
      var xform = curtext.getAttribute(\'transform\');\n
\n
      textbb = svgedit.utilities.getBBox(curtext);\n
      \n
      matrix = xform?getMatrix(curtext):null;\n
\n
      chardata = Array(len);\n
      textinput.focus();\n
      \n
      $(curtext).unbind(\'dblclick\', selectWord).dblclick(selectWord);\n
      \n
      if(!len) {\n
        var end = {x: textbb.x + (textbb.width/2), width: 0};\n
      }\n
      \n
      for(var i=0; i<len; i++) {\n
        var start = curtext.getStartPositionOfChar(i);\n
        var end = curtext.getEndPositionOfChar(i);\n
        \n
        if(!svgedit.browser.supportsGoodTextCharPos()) {\n
          var offset = canvas.contentW * current_zoom;\n
          start.x -= offset;\n
          end.x -= offset;\n
          \n
          start.x /= current_zoom;\n
          end.x /= current_zoom;\n
        }\n
        \n
        // Get a "bbox" equivalent for each character. Uses the\n
        // bbox data of the actual text for y, height purposes\n
        \n
        // TODO: Decide if y, width and height are actually necessary\n
        chardata[i] = {\n
          x: start.x,\n
          y: textbb.y, // start.y?\n
          width: end.x - start.x,\n
          height: textbb.height\n
        };\n
      }\n
      \n
      // Add a last bbox for cursor at end of text\n
      chardata.push({\n
        x: end.x,\n
        width: 0\n
      });\n
      setSelection(textinput.selectionStart, textinput.selectionEnd, true);\n
    }\n
  }\n
}();\n
\n
// TODO: Migrate all of this code into path.js\n
// Group: Path edit functions\n
// Functions relating to editing path elements\n
var pathActions = canvas.pathActions = function() {\n
  \n
  var subpath = false;\n
  var current_path;\n
  var newPoint, firstCtrl;\n
  \n
  function resetD(p) {\n
    p.setAttribute("d", pathActions.convertPath(p));\n
  }\n
\n
  // TODO: Move into path.js\n
    svgedit.path.Path.prototype.endChanges = function(text) {\n
      if(svgedit.browser.isWebkit()) resetD(this.elem);\n
      var cmd = new ChangeElementCommand(this.elem, {d: this.last_d}, text);\n
      addCommandToHistory(cmd);\n
      call("changed", [this.elem]);\n
    }\n
\n
    svgedit.path.Path.prototype.addPtsToSelection = function(indexes) {\n
      if(!$.isArray(indexes)) indexes = [indexes];\n
      for(var i=0; i< indexes.length; i++) {\n
        var index = indexes[i];\n
        var seg = this.segs[index];\n
        if(seg.ptgrip) {\n
          if(this.selected_pts.indexOf(index) == -1 && index >= 0) {\n
            this.selected_pts.push(index);\n
          }\n
        }\n
      };\n
      this.selected_pts.sort();\n
      var i = this.selected_pts.length,\n
        grips = new Array(i);\n
      // Loop through points to be selected and highlight each\n
      while(i--) {\n
        var pt = this.selected_pts[i];\n
        var seg = this.segs[pt];\n
        seg.select(true);\n
        grips[i] = seg.ptgrip;\n
      }\n
      // TODO: Correct this:\n
      pathActions.canDeleteNodes = true;\n
      \n
      pathActions.closed_subpath = this.subpathIsClosed(this.selected_pts[0]);\n
      \n
      call("selected", grips);\n
    }\n
\n
  var current_path = null,\n
    drawn_path = null,\n
    hasMoved = false,\n
    stretchy = null;\n
\n
  this.lastCtrlPoint = [0, 0];\n
  \n
  // This function converts a polyline (created by the fh_path tool) into\n
  // a path element and coverts every three line segments into a single bezier\n
  // curve in an attempt to smooth out the free-hand\n
  var smoothPolylineIntoPath = function(element) {\n
    var points = element.points;\n
    var N = points.numberOfItems;\n
    if (N >= 4) {\n
      // loop through every 3 points and convert to a cubic bezier curve segment\n
      // \n
      // NOTE: this is cheating, it means that every 3 points has the potential to \n
      // be a corner instead of treating each point in an equal manner.  In general,\n
      // this technique does not look that good.\n
      // \n
      // I am open to better ideas!\n
      // \n
      // Reading:\n
      // - http://www.efg2.com/Lab/Graphics/Jean-YvesQueinecBezierCurves.htm\n
      // - http://www.codeproject.com/KB/graphics/BezierSpline.aspx?msg=2956963\n
      // - http://www.ian-ko.com/ET_GeoWizards/UserGuide/smooth.htm\n
      // - http://www.cs.mtu.edu/~shene/COURSES/cs3621/NOTES/spline/Bezier/bezier-der.html\n
      var curpos = points.getItem(0), prevCtlPt = null;\n
      var d = [];\n
      d.push(["M",curpos.x,",",curpos.y," C"].join(""));\n
      for (var i = 1; i <= (N-4); i += 3) {\n
        var ct1 = points.getItem(i);\n
        var ct2 = points.getItem(i+1);\n
        var end = points.getItem(i+2);\n
        \n
        // if the previous segment had a control point, we want to smooth out\n
        // the control points on both sides\n
        if (prevCtlPt) {\n
          var newpts = svgedit.path.smoothControlPoints( prevCtlPt, ct1, curpos );\n
          if (newpts && newpts.length == 2) {\n
            var prevArr = d[d.length-1].split(\',\');\n
            prevArr[2] = newpts[0].x;\n
            prevArr[3] = newpts[0].y;\n
            d[d.length-1] = prevArr.join(\',\');\n
            ct1 = newpts[1];\n
          }\n
        }\n
        \n
        d.push([ct1.x,ct1.y,ct2.x,ct2.y,end.x,end.y].join(\',\'));\n
        \n
        curpos = end;\n
        prevCtlPt = ct2;\n
      }\n
      // handle remaining line segments\n
      d.push("L");\n
      for(;i < N;++i) {\n
        var pt = points.getItem(i);\n
        d.push([pt.x,pt.y].join(","));\n
      }\n
      d = d.join(" ");\n
\n
      // create new path element\n
      element = addSvgElementFromJson({\n
        "element": "path",\n
        "curStyles": true,\n
        "attr": {\n
          "id": getId(),\n
          "d": d,\n
          "fill": "none"\n
        }\n
      });\n
      // No need to call "changed", as this is already done under mouseUp\n
    }\n
    return element;\n
  };\n
\n
  return {\n
    mouseDown: function(evt, mouse_target, start_x, start_y) {\n
      if(current_mode === "path") {\n
        mouse_x = start_x;\n
        mouse_y = start_y;\n
        \n
        var x = mouse_x/current_zoom,\n
          y = mouse_y/current_zoom,\n
          stretchy = getElem("path_stretch_line");\n
        newPoint = [x, y];  \n
        \n
        if(curConfig.gridSnapping){\n
          x = snapToGrid(x);\n
          y = snapToGrid(y);\n
          mouse_x = snapToGrid(mouse_x);\n
          mouse_y = snapToGrid(mouse_y);\n
        }\n
\n
        if (!stretchy) {\n
          stretchy = document.createElementNS(svgns, "path");\n
          assignAttributes(stretchy, {\n
            \'id\': "path_stretch_line",\n
            \'stroke\': "#22C",\n
            \'stroke-width\': "0.5",\n
            \'fill\': \'none\'\n
          });\n
          stretchy = getElem("selectorParentGroup").appendChild(stretchy);\n
        }\n
        stretchy.setAttribute("display", "inline");\n
\n
        this.stretchy = stretchy;\n
        \n
        var keep = null;\n
        \n
        // if pts array is empty, create path element with M at current point\n
        if (!drawn_path) {\n
          d_attr = "M" + x + "," + y + " ";\n
          drawn_path = addSvgElementFromJson({\n
            "element": "path",\n
            "curStyles": true,\n
            "attr": {\n
              "d": d_attr,\n
              "id": getNextId(),\n
              "opacity": cur_shape.opacity / 2\n
            }\n
          });\n
          // set stretchy line to first point\n
          stretchy.setAttribute(\'d\', [\'M\', mouse_x, mouse_y, mouse_x, mouse_y].join(\' \'));\n
          var index = subpath ? svgedit.path.path.segs.length : 0;\n
          svgedit.path.addPointGrip(index, mouse_x, mouse_y);\n
          svgedit.path.first_grip = null;\n
        }\n
        else {\n
          // determine if we clicked on an existing point\n
          var seglist = drawn_path.pathSegList;\n
          var i = seglist.numberOfItems;\n
          var FUZZ = 6/current_zoom;\n
          var clickOnPoint = false;\n
          while(i) {\n
            i --;\n
            var item = seglist.getItem(i);\n
            var px = item.x, py = item.y;\n
            // found a matching point\n
            if ( x >= (px-FUZZ) && x <= (px+FUZZ) && y >= (py-FUZZ) && y <= (py+FUZZ) ) {\n
              clickOnPoint = true;\n
              break;\n
            }\n
          }\n
          \n
          // get path element that we are in the process of creating\n
          var id = getId();\n
        \n
          // Remove previous path object if previously created\n
          svgedit.path.removePath_(id);\n
          \n
          var newpath = getElem(id);\n
          \n
          var len = seglist.numberOfItems;\n
          // if we clicked on an existing point, then we are done this path, commit it\n
          // (i,i+1) are the x,y that were clicked on\n
          if (clickOnPoint) {\n
            // if clicked on any other point but the first OR\n
            // the first point was clicked on and there are less than 3 points\n
            // then leave the path open\n
            // otherwise, close the path\n
            if (i <= 1 && len >= 2) {\n
\n
              // Create end segment\n
              var abs_x = seglist.getItem(0).x;\n
              var abs_y = seglist.getItem(0).y;\n
              var grip_x = svgedit.path.first_grip ? svgedit.path.first_grip[0]/current_zoom : seglist.getItem(0).x;\n
              var grip_y = svgedit.path.first_grip ? svgedit.path.first_grip[1]/current_zoom : seglist.getItem(0).y;\n
              \n
\n
              var s_seg = stretchy.pathSegList.getItem(1);\n
              if(s_seg.pathSegType === 4) {\n
                var newseg = drawn_path.createSVGPathSegLinetoAbs(abs_x, abs_y);\n
              } else {\n
                var newseg = drawn_path.createSVGPathSegCurvetoCubicAbs(\n
                  abs_x,\n
                  abs_y,\n
                  s_seg.x1 / current_zoom,\n
                  s_seg.y1 / current_zoom,\n
                  grip_x,\n
                  grip_y\n
                );\n
              }\n
              var endseg = drawn_path.createSVGPathSegClosePath();\n
              seglist.appendItem(newseg);\n
              seglist.appendItem(endseg);\n
            } else if(len < 3) {\n
              keep = false;\n
              return keep;\n
            }\n
            $(stretchy).remove();\n
            \n
            // this will signal to commit the path\n
            element = newpath;\n
            drawn_path = null;\n
            started = false;\n
            if(subpath) {\n
\n
              if(svgedit.path.path.matrix) {\n
                remapElement(newpath, {}, svgedit.path.path.matrix.inverse());\n
              }\n
            \n
              var new_d = newpath.getAttribute("d");\n
              var orig_d = $(svgedit.path.path.elem).attr("d");\n
              $(svgedit.path.path.elem).attr("d", orig_d + new_d);\n
              $(newpath).remove();\n
              if(svgedit.path.path.matrix) {\n
                svgedit.path.recalcRotatedPath();\n
              }\n
              svgedit.path.path.init();\n
              pathActions.toEditMode(svgedit.path.path.elem);\n
              svgedit.path.path.selectPt();\n
              return false;\n
            }\n
\n
          }\n
          // else, create a new point, update path element\n
          else {\n
            // Checks if current target or parents are #svgcontent\n
            if(!$.contains(container, getMouseTarget(evt))) {\n
              // Clicked outside canvas, so don\'t make point\n
              console.log("Clicked outside canvas");\n
              return false;\n
            }\n
\n
            var num = drawn_path.pathSegList.numberOfItems;\n
            var last = drawn_path.pathSegList.getItem(num -1);\n
            var lastx = last.x, lasty = last.y;\n
\n
            if(evt.shiftKey) { var xya = snapToAngle(lastx,lasty,x,y); x=xya.x; y=xya.y; }\n
            \n
            // Use the segment defined by stretchy\n
            var s_seg = stretchy.pathSegList.getItem(1);\n
            if(s_seg.pathSegType === 4) {\n
              var newseg = drawn_path.createSVGPathSegLinetoAbs(round(x), round(y));\n
            } else {\n
              var newseg = drawn_path.createSVGPathSegCurvetoCubicAbs(\n
                round(x),\n
                round(y),\n
                s_seg.x1 / current_zoom,\n
                s_seg.y1 / current_zoom,\n
                s_seg.x2 / current_zoom,\n
                s_seg.y2 / current_zoom\n
              );\n
            }\n
            \n
            drawn_path.pathSegList.appendItem(newseg);\n
            \n
            x *= current_zoom;\n
            y *= current_zoom;\n
            \n
            // update everything to the latest point\n
            stretchy.setAttribute(\'d\', [\'M\', x, y, x, y].join(\' \'));\n
            var pointGrip1 = svgedit.path.addCtrlGrip(\'1c1\');\n
            var pointGrip2 = svgedit.path.addCtrlGrip(\'0c2\');\n
            var ctrlLine = svgedit.path.getCtrlLine(1);\n
            var ctrlLine2 = svgedit.path.getCtrlLine(2);\n
\n
            pointGrip1.setAttribute(\'cx\', x);\n
            pointGrip1.setAttribute(\'cy\', y);\n
            pointGrip2.setAttribute(\'cx\', x);\n
            pointGrip2.setAttribute(\'cy\', y);\n
\n
            ctrlLine.setAttribute(\'x1\', x);\n
            ctrlLine.setAttribute(\'x2\', x);\n
            ctrlLine.setAttribute(\'y1\', y);\n
            ctrlLine.setAttribute(\'y2\', y);\n
\n
            ctrlLine2.setAttribute(\'x1\', x);\n
            ctrlLine2.setAttribute(\'x2\', x);\n
            ctrlLine2.setAttribute(\'y1\', y);\n
            ctrlLine2.setAttribute(\'y2\', y);\n
\n
            var index = num;\n
            if(subpath) index += svgedit.path.path.segs.length;\n
            svgedit.path.addPointGrip(index, x, y);\n
          }\n
            keep = true;\n
        }\n
        return;\n
      }\n
      \n
      // TODO: Make sure current_path isn\'t null at this point\n
      if(!svgedit.path.path) return;\n
      \n
      svgedit.path.path.storeD();\n
      \n
      var id = evt.target.id;\n
      if (id.substr(0,14) == "pathpointgrip_") {\n
        // Select this point\n
        var cur_pt = svgedit.path.path.cur_pt = parseInt(id.substr(14));\n
        svgedit.path.path.dragging = [start_x, start_y];\n
        var seg = svgedit.path.path.segs[cur_pt];\n
        \n
        // only clear selection if shift is not pressed (otherwise, add \n
        // node to selection)\n
        if (!evt.shiftKey) {\n
          if(svgedit.path.path.selected_pts.length <= 1 || !seg.selected) {\n
            svgedit.path.path.clearSelection();\n
          }\n
          svgedit.path.path.addPtsToSelection(cur_pt);\n
        } else if(seg.selected) {\n
          svgedit.path.path.removePtFromSelection(cur_pt);\n
        } else {\n
          svgedit.path.path.addPtsToSelection(cur_pt);\n
        }\n
      } else if(id.indexOf("ctrlpointgrip_") == 0) {\n
        svgedit.path.path.dragging = [start_x, start_y];\n
        \n
        var parts = id.split(\'_\')[1].split(\'c\');\n
        var cur_pt = parts[0]-0;\n
        var ctrl_num = parts[1]-0;\n
        var num = ctrl_num;\n
        var path = svgedit.path.path.segs[cur_pt];\n
\n
        svgedit.path.path.selectPt(cur_pt, ctrl_num);\n
\n
        /////////////////\n
        //check if linked\n
        var seg, anum, pt;\n
        if (num == 2) {\n
          anum = 1;\n
          seg = path.next;\n
          if(!seg) return;\n
          pt = path.item;\n
        } else {\n
          anum = 2;\n
          seg = path.prev;\n
          if(!seg) return;\n
          pt = seg.item;\n
        }\n
\n
        var get_distance = function(pt1, pt2) {\n
          var a = pt1.x - pt2.x;\n
          var b = pt1.y - pt2.y;\n
          return Math.sqrt(Math.pow(a, 2) + Math.pow(b, 2));\n
        }\n
\n
        function get_angle(pt1, pt2)\n
        {\n
          var dy = pt1.y - pt2.y;\n
          var dx = pt1.x - pt2.x;\n
          var theta = Math.atan2(dy, dx);\n
          return theta *= 180/Math.PI // rads to degs\n
        }\n
\n
        var grip = {\n
          x: path.item["x" + num],\n
          y: path.item["y" + num]\n
        }\n
\n
        if (num == 2) {\n
          var node = {\n
            x: path.item["x"],\n
            y: path.item["y"]\n
          }\n
        }\n
        else {\n
          var node = {\n
            x: seg.item["x"],\n
            y: seg.item["y"]\n
          }\n
        }\n
\n
        var pair = {\n
          x: seg.item["x" + anum],\n
          y: seg.item["y" + anum]\n
        }\n
\n
        var distance_between_node_grip = get_distance(grip, node);\n
        var distance_between_pair_grip = get_distance(pair, node);\n
        var angle_grip = Math.round(get_angle(grip, node), 0);\n
        var angle_pair = Math.round(get_angle(pair, node), 0);\n
        var is_complementary = (Math.abs(angle_grip - angle_pair) == 180);\n
        //console.log("distance: " + Math.abs(distance_between_node_grip - distance_between_pair_grip) + " angle = " + (Math.round(Math.abs(get_angle(grip, node)) + Math.abs(get_angle(pair, node)), 0)))\n
        if (Math.abs(distance_between_node_grip - distance_between_pair_grip) < 5 && is_complementary) {\n
          svgedit.path.setLinkControlPoints(true);\n
          svgedit.path.is_linked = true;\n
        }\n
        else {\n
          svgedit.path.setLinkControlPoints(false);\n
          svgedit.path.is_linked = false;\n
        }\n
\n
\n
        ///////\n
\n
\n
      }\n
\n
      // Start selection box\n
      if(!svgedit.path.path.dragging) {\n
        if (rubberBox == null) {\n
          rubberBox = selectorManager.getRubberBandBox();\n
        }\n
        assignAttributes(rubberBox, {\n
            \'x\': start_x * current_zoom,\n
            \'y\': start_y * current_zoom,\n
            \'width\': 0,\n
            \'height\': 0,\n
            \'display\': \'inline\'\n
        }, 100);\n
      }\n
    },\n
    mouseMove: function(evt, mouse_x, mouse_y) {\n
      hasMoved = true;\n
      var is_linked = !evt.altKey;\n
      if(current_mode === "path") {\n
        if(!drawn_path) return;\n
        var seglist = drawn_path.pathSegList;\n
        var index = seglist.numberOfItems - 1;\n
        var pointGrip1 = svgedit.path.addCtrlGrip(\'1c1\'); \n
        var pointGrip2 = svgedit.path.addCtrlGrip(\'0c2\');\n
\n
        if(newPoint) {\n
          // First point\n
\n
          // Set control points\n
          var current_pointGrip2_x = pointGrip2.getAttribute(\'cx\') / current_zoom || 0;\n
          var current_pointGrip2_y = pointGrip2.getAttribute(\'cy\') / current_zoom || 0;\n
\n
          // dragging pointGrip1\n
          pointGrip1.setAttribute(\'cx\', mouse_x);\n
          pointGrip1.setAttribute(\'cy\', mouse_y);\n
          pointGrip1.setAttribute(\'display\', \'inline\');\n
\n
          var pt_x = newPoint[0];\n
          var pt_y = newPoint[1];\n
          \n
          // set curve\n
          var seg = seglist.getItem(index);\n
          var cur_x = mouse_x / current_zoom;\n
          var cur_y = mouse_y / current_zoom;\n
          var alt_x = (is_linked) ?  (pt_x + (pt_x - cur_x)) : current_pointGrip2_x;\n
          var alt_y = (is_linked) ?  (pt_y + (pt_y - cur_y)) : current_pointGrip2_y;\n
          \n
          \n
          pointGrip2.setAttribute(\'cx\', alt_x * current_zoom);\n
          pointGrip2.setAttribute(\'cy\', alt_y * current_zoom);\n
          pointGrip2.setAttribute(\'display\', \'inline\');\n
          \n
          \n
          var ctrlLine = svgedit.path.getCtrlLine(1);\n
          var ctrlLine2 = svgedit.path.getCtrlLine(2);\n
          assignAttributes(ctrlLine, {\n
            x1: mouse_x,\n
            y1: mouse_y,\n
            x2: pt_x * current_zoom,\n
            y2: pt_y * current_zoom,\n
            display: \'inline\'\n
          });\n
          \n
\n
          assignAttributes(ctrlLine2, {\n
            x1: alt_x * current_zoom,\n
            y1: alt_y * current_zoom,\n
            x2: pt_x  * current_zoom,\n
            y2: pt_y * current_zoom,\n
            display: \'inline\'\n
          });\n
\n
\n
          if(index === 0) {\n
            firstCtrl = [mouse_x, mouse_y];\n
          } else {\n
            var last_x, last_y;\n
            \n
            var last = seglist.getItem(index - 1);\n
            var last_x = last.x;\n
            var last_y = last.y\n
  \n
            if(last.pathSegType === 6) {\n
              last_x += (last_x - last.x2);\n
              last_y += (last_y - last.y2);\n
            } else if(firstCtrl) {\n
              last_x = firstCtrl[0]/current_zoom;\n
              last_y = firstCtrl[1]/current_zoom;\n
            }\n
            svgedit.path.replacePathSeg(6, index, [pt_x, pt_y, this.lastCtrlPoint[0]/current_zoom, this.lastCtrlPoint[1]/current_zoom, alt_x, alt_y], drawn_path);\n
          }\n
        } else {\n
          var stretchy = this.stretchy;\n
          if (stretchy) {\n
            var prev = seglist.getItem(index);\n
            var lastpoint = (evt.target.id === \'pathpointgrip_0\');\n
            var lastgripx = mouse_x;\n
            var lastgripy = mouse_y;\n
\n
            if (lastpoint && svgedit.path.first_grip) {\n
              lastgripx = svgedit.path.first_grip[0];\n
              lastgripy = svgedit.path.first_grip[1];\n
            }\n
\n
            if(prev.pathSegType === 6) {\n
              var prev_x = this.lastCtrlPoint[0]/current_zoom || prev.x + (prev.x - prev.x2);\n
              var prev_y = this.lastCtrlPoint[1]/current_zoom || prev.y + (prev.y - prev.y2);\n
              svgedit.path.replacePathSeg(6, 1, [mouse_x, mouse_y, prev_x * current_zoom, prev_y * current_zoom, lastgripx, lastgripy], stretchy);              \n
            } else if(firstCtrl) {\n
              svgedit.path.replacePathSeg(6, 1, [mouse_x, mouse_y, firstCtrl[0], firstCtrl[1], mouse_x, mouse_y], stretchy);\n
            } else {\n
              svgedit.path.replacePathSeg(4, 1, [mouse_x, mouse_y], stretchy);\n
            }\n
          }\n
        }\n
        return;\n
      }\n
      // if we are dragging a point, let\'s move it\n
      if (svgedit.path.path.dragging) {\n
        var pt = svgedit.path.getPointFromGrip({\n
          x: svgedit.path.path.dragging[0],\n
          y: svgedit.path.path.dragging[1]\n
        }, svgedit.path.path);\n
        var mpt = svgedit.path.getPointFromGrip({\n
          x: mouse_x,\n
          y: mouse_y\n
        }, svgedit.path.path);\n
        var diff_x = mpt.x - pt.x;\n
        var diff_y = mpt.y - pt.y;\n
\n
        svgedit.path.path.dragging = [mouse_x, mouse_y];\n
        if (!is_linked || !svgedit.path.is_linked) svgedit.path.setLinkControlPoints(false);\n
        else svgedit.path.setLinkControlPoints(true);\n
\n
        if(svgedit.path.path.dragctrl) {\n
          svgedit.path.path.moveCtrl(diff_x, diff_y);\n
        } else {\n
          svgedit.path.path.movePts(diff_x, diff_y);\n
        }\n
      } else {\n
        //select\n
        svgedit.path.path.selected_pts = [];\n
        svgedit.path.path.eachSeg(function(i) {\n
          var seg = this;\n
          if(!seg.next && !seg.prev) return;\n
          var item = seg.item;\n
          var rbb = rubberBox.getBBox();\n
          \n
          var pt = svgedit.path.getGripPt(seg);\n
          var pt_bb = {\n
            x: pt.x,\n
            y: pt.y,\n
            width: 0,\n
            height: 0\n
          };\n
        \n
          var sel = svgedit.math.rectsIntersect(rbb, pt_bb);\n
\n
          this.select(sel);\n
          //Note that addPtsToSelection is not being run\n
          if(sel) svgedit.path.path.selected_pts.push(seg.index);\n
        });\n
\n
      }\n
    }, \n
    mouseUp: function(evt, element, mouse_x, mouse_y) {\n
      var lastpointgrip = getElem(\'ctrlpointgrip_1c1\');\n
      var firstpointgrip = getElem(\'ctrlpointgrip_0c2\');\n
      if (lastpointgrip)\n
        this.lastCtrlPoint = [lastpointgrip.getAttribute(\'cx\'), lastpointgrip.getAttribute(\'cy\')];\n
      else\n
        this.lastCtrlPoint = [mouse_x, mouse_y]\n
      if (!svgedit.path.first_grip) {\n
        if  (firstpointgrip) {\n
          svgedit.path.first_grip = [firstpointgrip.getAttribute(\'cx\'), firstpointgrip.getAttribute(\'cy\')];\n
        }\n
        else {\n
          svgedit.path.first_grip = [mouse_x, mouse_y];\n
        }\n
      }\n
      // Create mode\n
      if(current_mode === "path") {\n
        newPoint = null;\n
        if(!drawn_path) {\n
          element = getElem(getId());\n
          started = false;\n
          firstCtrl = null;\n
        }\n
\n
        return {\n
          keep: true,\n
          element: element\n
        }\n
      }\n
      \n
      // Edit mode\n
      \n
      if (svgedit.path.path.dragging) {\n
        var last_pt = svgedit.path.path.cur_pt;\n
\n
        svgedit.path.path.dragging = false;\n
        svgedit.path.path.dragctrl = false;\n
        svgedit.path.path.update();\n
        \n
      \n
        if(hasMoved) {\n
          svgedit.path.path.endChanges("Move path point(s)");\n
        } \n
        \n
        if(!evt.shiftKey && !hasMoved) {\n
          svgedit.path.path.selectPt(last_pt);\n
        } \n
      }\n
      else if(rubberBox && rubberBox.getAttribute(\'display\') != \'none\') {\n
        // Done with multi-node-select\n
        rubberBox.setAttribute("display", "none");\n
        \n
        if(rubberBox.getAttribute(\'width\') <= 2 && rubberBox.getAttribute(\'height\') <= 2) {\n
          pathActions.toSelectMode(evt.target);\n
        }\n
        \n
      // else, move back to select mode \n
      } else {\n
        pathActions.toSelectMode(evt.target);\n
      }\n
      hasMoved = false;\n
    },\n
    toEditMode: function(element) {\n
      svgedit.path.path = svgedit.path.getPath_(element);\n
      current_mode = "pathedit";\n
      clearSelection();\n
      svgedit.path.path.show(true).update();\n
      svgedit.path.path.oldbbox = svgedit.utilities.getBBox(svgedit.path.path.elem);\n
      subpath = false;\n
    },\n
    toSelectMode: function(elem) {\n
      var selPath = (elem == svgedit.path.path.elem);\n
      current_mode = "select";\n
      svgedit.path.path.show(false);\n
      current_path = false;\n
      clearSelection();\n
      \n
      if(svgedit.path.path.matrix) {\n
        // Rotated, so may need to re-calculate the center\n
        svgedit.path.recalcRotatedPath();\n
      }\n
      \n
      if(selPath) {\n
        call("selected", [elem]);\n
        addToSelection([elem], true);\n
      }\n
    },\n
    addSubPath: function(on) {\n
      if(on) {\n
        // Internally we go into "path" mode, but in the UI it will\n
        // still appear as if in "pathedit" mode.\n
        current_mode = "path";\n
        subpath = true;\n
      } else {\n
        pathActions.clear(true);\n
        pathActions.toEditMode(svgedit.path.path.elem);\n
      }\n
    },\n
    select: function(target) {\n
      if (current_path === target) {\n
        pathActions.toEditMode(target);\n
        current_mode = "pathedit";\n
      } // going into pathedit mode\n
      else {\n
        current_path = target;\n
      } \n
    },\n
    reorient: function() {\n
      var elem = selectedElements[0];\n
      if(!elem) return;\n
      var angle 

]]></string> </value>
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
            <value> <string>= getRotationAngle(elem);\n
      if(angle == 0) return;\n
      \n
      var batchCmd = new BatchCommand("Reorient path");\n
      var changes = {\n
        d: elem.getAttribute(\'d\'),\n
        transform: elem.getAttribute(\'transform\')\n
      };\n
      batchCmd.addSubCommand(new ChangeElementCommand(elem, changes));\n
      clearSelection();\n
      this.resetOrientation(elem);\n
      \n
      addCommandToHistory(batchCmd);\n
\n
      // Set matrix to null\n
      svgedit.path.getPath_(elem).show(false).matrix = null; \n
\n
      this.clear();\n
  \n
      addToSelection([elem], true);\n
      call("changed", selectedElements);\n
    },\n
    \n
    clear: function(remove) {\n
      current_path = null;\n
      if (drawn_path) {\n
        var elem = getElem(getId());\n
        $(getElem("path_stretch_line")).remove();\n
        if (remove) $(elem).remove();\n
        $(getElem("pathpointgrip_container")).find(\'*\').attr(\'display\', \'none\');\n
        drawn_path = firstCtrl = null;\n
        started = false;\n
      } else if (current_mode == "pathedit") {\n
        this.toSelectMode();\n
      }\n
      if(svgedit.path.path) svgedit.path.path.init().show(false);\n
    },\n
    resetOrientation: function(path) {\n
      if(path == null || path.nodeName != \'path\') return false;\n
      var tlist = getTransformList(path);\n
      var m = transformListToTransform(tlist).matrix;\n
      tlist.clear();\n
      path.removeAttribute("transform");\n
      var segList = path.pathSegList;\n
      \n
      // Opera/win/non-EN throws an error here.\n
      // TODO: Find out why!\n
      // Presumed fixed in Opera 10.5, so commented out for now\n
      \n
//      try {\n
        var len = segList.numberOfItems;\n
//      } catch(err) {\n
//        var fixed_d = pathActions.convertPath(path);\n
//        path.setAttribute(\'d\', fixed_d);\n
//        segList = path.pathSegList;\n
//        var len = segList.numberOfItems;\n
//      }\n
      var last_x, last_y;\n
\n
\n
      for (var i = 0; i \074 len; ++i) {\n
        var seg = segList.getItem(i);\n
        var type = seg.pathSegType;\n
        if(type == 1) continue;\n
        var pts = [];\n
        $.each([\'\',1,2], function(j, n) {\n
          var x = seg[\'x\'+n], y = seg[\'y\'+n];\n
          if(x !== undefined \046\046 y !== undefined) {\n
            var pt = transformPoint(x, y, m);\n
            pts.splice(pts.length, 0, pt.x, pt.y);\n
          }\n
        });\n
        svgedit.path.replacePathSeg(type, i, pts, path);\n
      }\n
      \n
      reorientGrads(path, m);\n
\n
\n
    },\n
    zoomChange: function() {\n
      if(current_mode == "pathedit") {\n
        svgedit.path.path.update();\n
      }\n
    },\n
    getNodePoint: function() {\n
      if (!svgedit.path.path) return;\n
      var sel_pt = svgedit.path.path.selected_pts.length ? svgedit.path.path.selected_pts[0] : 1;\n
\n
      var seg = svgedit.path.path.segs[sel_pt];\n
      return {\n
        x: seg.item.x,\n
        y: seg.item.y,\n
        type: seg.type\n
      };\n
    }, \n
    linkControlPoints: function(linkPoints) {\n
      svgedit.path.setLinkControlPoints(linkPoints);\n
    },\n
    clonePathNode: function() {\n
      svgedit.path.path.storeD();\n
      \n
      var sel_pts = svgedit.path.path.selected_pts;\n
      var segs = svgedit.path.path.segs;\n
      \n
      var i = sel_pts.length;\n
      var nums = [];\n
\n
      while(i--) {\n
        var pt = sel_pts[i];\n
        svgedit.path.path.addSeg(pt);\n
        nums.push(pt + i);\n
        nums.push(pt + i + 1);\n
      }\n
      \n
      svgedit.path.path.init().addPtsToSelection(nums);\n
\n
      svgedit.path.path.endChanges("Clone path node(s)");\n
    },\n
    opencloseSubPath: function() {\n
      var sel_pts = svgedit.path.path.selected_pts;\n
      // Only allow one selected node for now\n
      if(sel_pts.length !== 1) return;\n
      \n
      var elem = svgedit.path.path.elem;\n
      var list = elem.pathSegList;\n
\n
      var len = list.numberOfItems;\n
\n
      var index = sel_pts[0];\n
      \n
      var open_pt = null;\n
      var start_item = null;\n
\n
      // Check if subpath is already open\n
      svgedit.path.path.eachSeg(function(i) {\n
        if(this.type === 2 \046\046 i \074= index) {\n
          start_item = this.item;\n
        }\n
        if(i \074= index) return true;\n
        if(this.type === 2) {\n
          // Found M first, so open\n
          open_pt = i;\n
          return false;\n
        } else if(this.type === 1) {\n
          // Found Z first, so closed\n
          open_pt = false;\n
          return false;\n
        }\n
      });\n
      \n
      if(open_pt == null) {\n
        // Single path, so close last seg\n
        open_pt = svgedit.path.path.segs.length - 1;\n
      }\n
\n
      if(open_pt !== false) {\n
        // Close this path\n
        \n
        // Create a line going to the previous "M"\n
        var newseg = elem.createSVGPathSegLinetoAbs(start_item.x, start_item.y);\n
      \n
        var closer = elem.createSVGPathSegClosePath();\n
        if(open_pt == svgedit.path.path.segs.length) {\n
          list.appendItem(newseg);\n
          list.appendItem(closer);\n
        } else {\n
          svgedit.path.insertItemBefore(elem, closer, open_pt);\n
          svgedit.path.insertItemBefore(elem, newseg, open_pt);\n
        }\n
        \n
        svgedit.path.path.init().selectPt(open_pt+1);\n
        return;\n
      }\n
      \n
      \n
\n
      // M 1,1 L 2,2 L 3,3 L 1,1 z // open at 2,2\n
      // M 2,2 L 3,3 L 1,1\n
      \n
      // M 1,1 L 2,2 L 1,1 z M 4,4 L 5,5 L6,6 L 5,5 z \n
      // M 1,1 L 2,2 L 1,1 z [M 4,4] L 5,5 L(M)6,6 L 5,5 z \n
      \n
      var seg = svgedit.path.path.segs[index];\n
      \n
      if(seg.mate) {\n
        list.removeItem(index); // Removes last "L"\n
        list.removeItem(index); // Removes the "Z"\n
        svgedit.path.path.init().selectPt(index - 1);\n
        return;\n
      }\n
      \n
      var last_m, z_seg;\n
      \n
      // Find this sub-path\'s closing point and remove\n
      for(var i=0; i\074list.numberOfItems; i++) {\n
        var item = list.getItem(i);\n
\n
        if(item.pathSegType === 2) {\n
          // Find the preceding M\n
          last_m = i;\n
        } else if(i === index) {\n
          // Remove it\n
          list.removeItem(last_m);\n
//            index--;\n
        } else if(item.pathSegType === 1 \046\046 index \074 i) {\n
          // Remove the closing seg of this subpath\n
          z_seg = i-1;\n
          list.removeItem(i);\n
          break;\n
        }\n
      }\n
      \n
      var num = (index - last_m) - 1;\n
      \n
      while(num--) {\n
        svgedit.path.insertItemBefore(elem, list.getItem(last_m), z_seg);\n
      }\n
      \n
      var pt = list.getItem(last_m);\n
      \n
      // Make this point the new "M"\n
      svgedit.path.replacePathSeg(2, last_m, [pt.x, pt.y]);\n
      \n
      var i = index\n
      \n
      svgedit.path.path.init().selectPt(0);\n
    },\n
    deletePathNode: function() {\n
      if(!pathActions.canDeleteNodes) return;\n
      svgedit.path.path.storeD();\n
      \n
      var sel_pts = svgedit.path.path.selected_pts;\n
      var i = sel_pts.length;\n
\n
      while(i--) {\n
        var pt = sel_pts[i];\n
        svgedit.path.path.deleteSeg(pt);\n
      }\n
      \n
      // Cleanup\n
      var cleanup = function() {\n
        var segList = svgedit.path.path.elem.pathSegList;\n
        var len = segList.numberOfItems;\n
        \n
        var remItems = function(pos, count) {\n
          while(count--) {\n
            segList.removeItem(pos);\n
          }\n
        }\n
\n
        if(len \074= 1) return true;\n
        \n
        while(len--) {\n
          var item = segList.getItem(len);\n
          if(item.pathSegType === 1) {\n
            var prev = segList.getItem(len-1);\n
            var nprev = segList.getItem(len-2);\n
            if(prev.pathSegType === 2) {\n
              remItems(len-1, 2);\n
              cleanup();\n
              break;\n
            } else if(nprev.pathSegType === 2) {\n
              remItems(len-2, 3);\n
              cleanup();\n
              break;\n
            }\n
\n
          } else if(item.pathSegType === 2) {\n
            if(len \076 0) {\n
              var prev_type = segList.getItem(len-1).pathSegType;\n
              // Path has M M  \n
              if(prev_type === 2) {\n
                remItems(len-1, 1);\n
                cleanup();\n
                break;\n
              // Entire path ends with Z M \n
              } else if(prev_type === 1 \046\046 segList.numberOfItems-1 === len) {\n
                remItems(len, 1);\n
                cleanup();\n
                break;\n
              }\n
            }\n
          }\n
        } \n
        return false;\n
      }\n
      \n
      cleanup();\n
      \n
      // Completely delete a path with 1 or 0 segments\n
      if(svgedit.path.path.elem.pathSegList.numberOfItems \074= 1) {\n
        canvas.setMode("select")\n
        canvas.deleteSelectedElements();\n
        return;\n
      }\n
      \n
      svgedit.path.path.init();\n
      \n
      svgedit.path.path.clearSelection();\n
      \n
      // TODO: Find right way to select point now\n
      // path.selectPt(sel_pt);\n
      if(window.opera) { // Opera repaints incorrectly\n
        var cp = $(svgedit.path.path.elem); cp.attr(\'d\',cp.attr(\'d\'));\n
      }\n
      svgedit.path.path.endChanges("Delete path node(s)");\n
    },\n
    smoothPolylineIntoPath: smoothPolylineIntoPath,\n
    setSegType: function(v) {\n
      svgedit.path.path.setSegType(v);\n
    },\n
    moveNode: function(attr, newValue) {\n
      var sel_pts = svgedit.path.path.selected_pts;\n
      if(!sel_pts.length) return;\n
      \n
      svgedit.path.path.storeD();\n
      \n
      // Get first selected point\n
      var seg = svgedit.path.path.segs[sel_pts[0]];\n
      var diff = {x:0, y:0};\n
      diff[attr] = newValue - seg.item[attr];\n
      \n
      seg.move(diff.x, diff.y);\n
      svgedit.path.path.endChanges("Move path point");\n
    },\n
    fixEnd: function(elem) {\n
      // Adds an extra segment if the last seg before a Z doesn\'t end\n
      // at its M point\n
      // M0,0 L0,100 L100,100 z\n
      var segList = elem.pathSegList;\n
      var len = segList.numberOfItems;\n
      var last_m;\n
      for (var i = 0; i \074 len; ++i) {\n
        var item = segList.getItem(i);\n
        if(item.pathSegType === 2) {\n
          last_m = item;\n
        }\n
        \n
        if(item.pathSegType === 1) {\n
          var prev = segList.getItem(i-1);\n
          if(prev.x != last_m.x || prev.y != last_m.y) {\n
            // Add an L segment here\n
            var newseg = elem.createSVGPathSegLinetoAbs(last_m.x, last_m.y);\n
            svgedit.path.insertItemBefore(elem, newseg, i);\n
            // Can this be done better?\n
            pathActions.fixEnd(elem);\n
            break;\n
          }\n
          \n
        }\n
      }\n
      if(svgedit.browser.isWebkit()) resetD(elem);\n
    },\n
    // Convert a path to one with only absolute or relative values\n
    convertPath: function(path, toRel) {\n
      var segList = path.pathSegList;\n
      var len = segList.numberOfItems;\n
      var curx = 0, cury = 0;\n
      var d = "";\n
      var last_m = null;\n
      \n
      for (var i = 0; i \074 len; ++i) {\n
        var seg = segList.getItem(i);\n
        // if these properties are not in the segment, set them to zero\n
        var x = seg.x || 0,\n
          y = seg.y || 0,\n
          x1 = seg.x1 || 0,\n
          y1 = seg.y1 || 0,\n
          x2 = seg.x2 || 0,\n
          y2 = seg.y2 || 0;\n
  \n
        var type = seg.pathSegType;\n
        var letter = pathMap[type][\'to\'+(toRel?\'Lower\':\'Upper\')+\'Case\']();\n
        \n
        var addToD = function(pnts, more, last) {\n
          var str = \'\';\n
          var more = more?\' \'+more.join(\' \'):\'\';\n
          var last = last?\' \'+svgedit.units.shortFloat(last):\'\';\n
          $.each(pnts, function(i, pnt) {\n
            pnts[i] = svgedit.units.shortFloat(pnt);\n
          });\n
          d += letter + pnts.join(\' \') + more + last;\n
        }\n
        \n
        switch (type) {\n
          case 1: // z,Z closepath (Z/z)\n
            d += "z";\n
            break;\n
          case 12: // absolute horizontal line (H)\n
            x -= curx;\n
          case 13: // relative horizontal line (h)\n
            if(toRel) {\n
              curx += x;\n
              letter = \'l\';\n
            } else {\n
              x += curx;\n
              curx = x;\n
              letter = \'L\';\n
            }\n
            // Convert to "line" for easier editing\n
            addToD([[x, cury]]);\n
            break;\n
          case 14: // absolute vertical line (V)\n
            y -= cury;\n
          case 15: // relative vertical line (v)\n
            if(toRel) {\n
              cury += y;\n
              letter = \'l\';\n
            } else {\n
              y += cury;\n
              cury = y;\n
              letter = \'L\';\n
            }\n
            // Convert to "line" for easier editing\n
            addToD([[curx, y]]);\n
            break;\n
          case 2: // absolute move (M)\n
          case 4: // absolute line (L)\n
          case 18: // absolute smooth quad (T)\n
            x -= curx;\n
            y -= cury;\n
          case 5: // relative line (l)\n
          case 3: // relative move (m)\n
            // If the last segment was a "z", this must be relative to \n
            if(last_m \046\046 segList.getItem(i-1).pathSegType === 1 \046\046 !toRel) {\n
              curx = last_m[0];\n
              cury = last_m[1];\n
            }\n
          \n
          case 19: // relative smooth quad (t)\n
            if(toRel) {\n
              curx += x;\n
              cury += y;\n
            } else {\n
              x += curx;\n
              y += cury;\n
              curx = x;\n
              cury = y;\n
            }\n
            if(type === 3) last_m = [curx, cury];\n
            \n
            addToD([[x,y]]);\n
            break;\n
          case 6: // absolute cubic (C)\n
            x -= curx; x1 -= curx; x2 -= curx;\n
            y -= cury; y1 -= cury; y2 -= cury;\n
          case 7: // relative cubic (c)\n
            if(toRel) {\n
              curx += x;\n
              cury += y;\n
            } else {\n
              x += curx; x1 += curx; x2 += curx;\n
              y += cury; y1 += cury; y2 += cury;\n
              curx = x;\n
              cury = y;\n
            }\n
            addToD([[x1,y1],[x2,y2],[x,y]]);\n
            break;\n
          case 8: // absolute quad (Q)\n
            x -= curx; x1 -= curx;\n
            y -= cury; y1 -= cury;\n
          case 9: // relative quad (q) \n
            if(toRel) {\n
              curx += x;\n
              cury += y;\n
            } else {\n
              x += curx; x1 += curx;\n
              y += cury; y1 += cury;\n
              curx = x;\n
              cury = y;\n
            }\n
            addToD([[x1,y1],[x,y]]);\n
            break;\n
          case 10: // absolute elliptical arc (A)\n
            x -= curx;\n
            y -= cury;\n
          case 11: // relative elliptical arc (a)\n
            if(toRel) {\n
              curx += x;\n
              cury += y;\n
            } else {\n
              x += curx;\n
              y += cury;\n
              curx = x;\n
              cury = y;\n
            }\n
            addToD([[seg.r1,seg.r2]], [\n
                seg.angle,\n
                (seg.largeArcFlag ? 1 : 0),\n
                (seg.sweepFlag ? 1 : 0)\n
              ],[x,y]\n
            );\n
            break;\n
          case 16: // absolute smooth cubic (S)\n
            x -= curx; x2 -= curx;\n
            y -= cury; y2 -= cury;\n
          case 17: // relative smooth cubic (s)\n
            if(toRel) {\n
              curx += x;\n
              cury += y;\n
            } else {\n
              x += curx; x2 += curx;\n
              y += cury; y2 += cury;\n
              curx = x;\n
              cury = y;\n
            }\n
            addToD([[x2,y2],[x,y]]);\n
            break;\n
        } // switch on path segment type\n
      } // for each segment\n
      return d;\n
    }\n
  }\n
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
  var defs = svgcontent.getElementsByTagNameNS(svgns, "defs");\n
  if(!defs || !defs.length) return 0;\n
  \n
//  if(!defs.firstChild) return;\n
  \n
  var defelem_uses = [],\n
    numRemoved = 0;\n
  var attrs = [\'fill\', \'stroke\', \'filter\', \'marker-start\', \'marker-mid\', \'marker-end\'];\n
  var alen = attrs.length;\n
  \n
  var all_els = svgcontent.getElementsByTagNameNS(svgns, \'*\');\n
  var all_len = all_els.length;\n
  \n
  for(var i=0; i\074all_len; i++) {\n
    var el = all_els[i];\n
    for(var j = 0; j \074 alen; j++) {\n
      if(el) {\n
        var ref = getUrlFromAttr(el.getAttribute(attrs[j]));\n
        if(ref) {\n
          defelem_uses.push(ref.substr(1));\n
        }\n
      }\n
    }\n
    \n
    // gradients can refer to other gradients\n
    var href = getHref(el);\n
    if (href \046\046 href.indexOf(\'#\') === 0) {\n
      defelem_uses.push(href.substr(1));\n
    }\n
  };\n
  \n
  var defelems = $(defs).find("linearGradient, radialGradient, filter, marker, svg, symbol");\n
    defelem_ids = [],\n
    i = defelems.length;\n
  while (i--) {\n
    var defelem = defelems[i];\n
    var id = defelem.id;\n
    if(defelem_uses.indexOf(id) \074 0) {\n
      // Not found, so remove (but remember)\n
      removedElements[id] = defelem;\n
      defelem.parentNode.removeChild(defelem);\n
      numRemoved++;\n
    }\n
  }\n
\n
  return numRemoved;\n
}\n
\n
// Function: svgCanvasToString\n
// Main function to set up the SVG content for output \n
//\n
// Returns: \n
// String containing the SVG image for output\n
this.svgCanvasToString = function() {\n
  // keep calling it until there are none to remove\n
  while (removeUnusedDefElems() \076 0) {};\n
  \n
  pathActions.clear(true);\n
  \n
  // Keep SVG-Edit comment on top\n
  $.each(svgcontent.childNodes, function(i, node) {\n
    if(i \046\046 node.nodeType === 8 \046\046 node.data.indexOf(\'Created with\') \076= 0) {\n
      svgcontent.insertBefore(node, svgcontent.firstChild);\n
    }\n
  });\n
  \n
  // Move out of in-group editing mode\n
  if(current_group) {\n
    leaveContext();\n
    selectOnly([current_group]);\n
  }\n
  \n
  //hide grid, otherwise shows a black canvas\n
  $(\'#canvasGrid\').attr(\'display\', \'none\');\n
  \n
  var naked_svgs = [];\n
  \n
  // Unwrap gsvg if it has no special attributes (only id and style)\n
  $(svgcontent).find(\'g:data(gsvg)\').each(function() {\n
    var attrs = this.attributes;\n
    var len = attrs.length;\n
    for(var i=0; i\074len; i++) {\n
      if(attrs[i].nodeName == \'id\' || attrs[i].nodeName == \'style\') {\n
        len--;\n
      }\n
    }\n
    // No significant attributes, so ungroup\n
    if(len \074= 0) {\n
      var svg = this.firstChild;\n
      naked_svgs.push(svg);\n
      $(this).replaceWith(svg);\n
    }\n
  });\n
  var output = this.svgToString(svgcontent, 0);\n
  \n
  // Rewrap gsvg\n
  if(naked_svgs.length) {\n
    $(naked_svgs).each(function() {\n
      groupSvgElem(this);\n
    });\n
  }\n
  \n
  return output;\n
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
  var out = new Array(), toXml = svgedit.utilities.toXml;\n
  var unit = curConfig.baseUnit;\n
  var unit_re = new RegExp(\'^-?[\\\\d\\\\.]+\' + unit + \'$\');\n
\n
  if (elem) {\n
    cleanupElement(elem);\n
    var attrs = elem.attributes,\n
      attr,\n
      i,\n
      childs = elem.childNodes;\n
    \n
    for (var i=0; i\074indent; i++) out.push(" ");\n
    out.push("\074"); out.push(elem.nodeName);\n
    if(elem.id === \'svgcontent\') {\n
      // Process root element separately\n
      var res = getResolution();\n
      \n
      var vb = "";\n
      // TODO: Allow this by dividing all values by current baseVal\n
      // Note that this also means we should properly deal with this on import\n
//      if(curConfig.baseUnit !== "px") {\n
//        var unit = curConfig.baseUnit;\n
//        var unit_m = svgedit.units.getTypeMap()[unit];\n
//        res.w = svgedit.units.shortFloat(res.w / unit_m)\n
//        res.h = svgedit.units.shortFloat(res.h / unit_m)\n
//        vb = \' viewBox="\' + [0, 0, res.w, res.h].join(\' \') + \'"\';       \n
//        res.w += unit;\n
//        res.h += unit;\n
//      }\n
      \n
      if(unit !== "px") {\n
        res.w = svgedit.units.convertUnit(res.w, unit) + unit;\n
        res.h = svgedit.units.convertUnit(res.h, unit) + unit;\n
      }\n
      \n
      out.push(\' width="\' + res.w + \'" height="\' + res.h + \'"\' + vb + \' xmlns="\'+svgns+\'"\');\n
      \n
      var nsuris = {};\n
      \n
      // Check elements for namespaces, add if found\n
      $(elem).find(\'*\').andSelf().each(function() {\n
        var el = this;\n
        $.each(this.attributes, function(i, attr) {\n
          var uri = attr.namespaceURI;\n
          if(uri \046\046 !nsuris[uri] \046\046 nsMap[uri] !== \'xmlns\' \046\046 nsMap[uri] !== \'xml\' ) {\n
            nsuris[uri] = true;\n
            out.push(" xmlns:" + nsMap[uri] + \'="\' + uri +\'"\');\n
          }\n
        });\n
      });\n
      \n
      var i = attrs.length;\n
      var attr_names = [\'width\',\'height\',\'xmlns\',\'x\',\'y\',\'viewBox\',\'id\',\'overflow\'];\n
      while (i--) {\n
        attr = attrs.item(i);\n
        var attrVal = toXml(attr.nodeValue);\n
        \n
        // Namespaces have already been dealt with, so skip\n
        if(attr.nodeName.indexOf(\'xmlns:\') === 0) continue;\n
\n
        // only serialize attributes we don\'t use internally\n
        if (attrVal != "" \046\046 attr_names.indexOf(attr.localName) == -1) \n
        {\n
\n
          if(!attr.namespaceURI || nsMap[attr.namespaceURI]) {\n
            out.push(\' \'); \n
            out.push(attr.nodeName); out.push("=\\"");\n
            out.push(attrVal); out.push("\\"");\n
          }\n
        }\n
      }\n
    } else {\n
      // Skip empty defs\n
      if(elem.nodeName === \'defs\' \046\046 !elem.firstChild) return;\n
    \n
      var moz_attrs = [\'-moz-math-font-style\', \'_moz-math-font-style\'];\n
      for (var i=attrs.length-1; i\076=0; i--) {\n
        attr = attrs.item(i);\n
        var attrVal = toXml(attr.nodeValue);\n
        //remove bogus attributes added by Gecko\n
        if (moz_attrs.indexOf(attr.localName) \076= 0) continue;\n
        if (attrVal != "") {\n
          if(attrVal.indexOf(\'pointer-events\') === 0) continue;\n
          if(attr.localName === "class" \046\046 attrVal.indexOf(\'se_\') === 0) continue;\n
          out.push(" "); \n
          if(attr.localName === \'d\') attrVal = pathActions.convertPath(elem, true);\n
          if(!isNaN(attrVal)) {\n
            attrVal = svgedit.units.shortFloat(attrVal);\n
          } else if(unit_re.test(attrVal)) {\n
            attrVal = svgedit.units.shortFloat(attrVal) + unit;\n
          }\n
          \n
          // Embed images when saving \n
          if(save_options.apply\n
            \046\046 elem.nodeName === \'image\' \n
            \046\046 attr.localName === \'href\'\n
            \046\046 save_options.images\n
            \046\046 save_options.images === \'embed\') \n
          {\n
            var img = encodableImages[attrVal];\n
            if(img) attrVal = img;\n
          }\n
          \n
          // map various namespaces to our fixed namespace prefixes\n
          // (the default xmlns attribute itself does not get a prefix)\n
          if(!attr.namespaceURI || attr.namespaceURI == svgns || nsMap[attr.namespaceURI]) {\n
            out.push(attr.nodeName); out.push("=\\"");\n
            out.push(attrVal); out.push("\\"");\n
          }\n
        }\n
      }\n
    }\n
\n
    if (elem.hasChildNodes()) {\n
      out.push("\076");\n
      indent++;\n
      var bOneLine = false;\n
      \n
      for (var i=0; i\074childs.length; i++)\n
      {\n
        var child = childs.item(i);\n
        switch(child.nodeType) {\n
        case 1: // element node\n
          out.push("\\n");\n
          out.push(this.svgToString(childs.item(i), indent));\n
          break;\n
        case 3: // text node\n
          var str = child.nodeValue.replace(/^\\s+|\\s+$/g, "");\n
          if (str != "") {\n
            bOneLine = true;\n
            out.push(toXml(str) + "");\n
          }\n
          break;\n
        case 4: // cdata node\n
          out.push("\\n");\n
          out.push(new Array(indent+1).join(" "));\n
          out.push("\074![CDATA[");\n
          out.push(child.nodeValue);\n
          out.push("]]\076");\n
          break;\n
        case 8: // comment\n
          out.push("\\n");\n
          out.push(new Array(indent+1).join(" "));\n
          out.push("\074!--");\n
          out.push(child.data);\n
          out.push("--\076");\n
          break;\n
        } // switch on node type\n
      }\n
      indent--;\n
      if (!bOneLine) {\n
        out.push("\\n");\n
        for (var i=0; i\074indent; i++) out.push(" ");\n
      }\n
      out.push("\074/"); out.push(elem.nodeName); out.push("\076");\n
    } else {\n
      out.push("/\076");\n
    }\n
  }\n
  return out.join(\'\');\n
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
\n
  // load in the image and once it\'s loaded, get the dimensions\n
  $(new Image()).load(function() {\n
    // create a canvas the same size as the raster image\n
    var canvas = document.createElement("canvas");\n
    canvas.width = this.width;\n
    canvas.height = this.height;\n
    // load the raster image into the canvas\n
    canvas.getContext("2d").drawImage(this,0,0);\n
    // retrieve the data: URL\n
    try {\n
      var urldata = \';svgedit_url=\' + encodeURIComponent(val);\n
      urldata = canvas.toDataURL().replace(\';base64\',urldata+\';base64\');\n
      encodableImages[val] = urldata;\n
    } catch(e) {\n
      encodableImages[val] = false;\n
    }\n
    last_good_img_url = val;\n
    if(callback) callback(encodableImages[val]);\n
  }).attr(\'src\',val);\n
}\n
\n
// Function: setGoodImage\n
// Sets a given URL to be a "last good image" URL\n
this.setGoodImage = function(val) {\n
  last_good_img_url = val;\n
}\n
\n
this.open = function() {\n
  // Nothing by default, handled by optional widget/extension\n
};\n
\n
// Function: save\n
// Serializes the current drawing into SVG XML text and returns it to the \'saved\' handler.\n
// This function also includes the XML prolog.  Clients of the SvgCanvas bind their save\n
// function to the \'saved\' event.\n
//\n
// Returns: \n
// Nothing\n
this.save = function(opts) {\n
  // remove the selected outline before serializing\n
  clearSelection();\n
  // Update save options if provided\n
  if(opts) $.extend(save_options, opts);\n
  save_options.apply = true;\n
  \n
  // no need for doctype, see http://jwatt.org/svg/authoring/#doctype-declaration\n
  var str = this.svgCanvasToString();\n
  if (svgedit.browser.supportsBlobs()) {\n
    var blob = new Blob([ str ], {type: "image/svg+xml;charset=utf-8"});\n
    var dropAutoBOM = true;\n
    saveAs(blob, "method-draw-image.svg", dropAutoBOM);\n
  }\n
  else {\n
    call("saved", str);\n
  }\n
};\n
\n
// Function: rasterExport\n
// Generates a PNG Data URL based on the current image, then calls "exported" \n
// with an object including the string and any issues found\n
this.rasterExport = function() {\n
  // remove the selected outline before serializing\n
  clearSelection();\n
  \n
  // Check for known CanVG issues \n
  var issues = [];\n
  \n
  // Selector and notice\n
  var issue_list = {\n
    \'feGaussianBlur\': uiStrings.exportNoBlur,\n
    \'foreignObject\': uiStrings.exportNoforeignObject,\n
    \'[stroke-dasharray]\': uiStrings.exportNoDashArray\n
  };\n
  var content = $(svgcontent);\n
  \n
  // Add font/text check if Canvas Text API is not implemented\n
  if(!("font" in $(\'\074canvas\076\')[0].getContext(\'2d\'))) {\n
    issue_list[\'text\'] = uiStrings.exportNoText;\n
  }\n
  \n
  $.each(issue_list, function(sel, descr) {\n
    if(content.find(sel).length) {\n
      issues.push(descr);\n
    }\n
  });\n
\n
  var str = this.svgCanvasToString();\n
  call("exported", {svg: str, issues: issues});\n
};\n
\n
// Function: getSvgString\n
// Returns the current drawing as raw SVG XML text.\n
//\n
// Returns:\n
// The current drawing as raw SVG XML text.\n
this.getSvgString = function() {\n
  save_options.apply = false;\n
  return this.svgCanvasToString();\n
};\n
\n
// Function: randomizeIds\n
// This function determines whether to use a nonce in the prefix, when\n
// generating IDs for future documents in SVG-Edit.\n
// \n
//  Parameters:\n
//   an opional boolean, which, if true, adds a nonce to the prefix. Thus\n
//     svgCanvas.randomizeIds()  \074==\076 svgCanvas.randomizeIds(true)\n
//\n
// if you\'re controlling SVG-Edit externally, and want randomized IDs, call\n
// this BEFORE calling svgCanvas.setSvgString\n
//\n
this.randomizeIds = function() {\n
  if (arguments.length \076 0 \046\046 arguments[0] == false) {\n
    svgedit.draw.randomizeIds(false, getCurrentDrawing());\n
  } else {\n
    svgedit.draw.randomizeIds(true, getCurrentDrawing());\n
  }\n
};\n
\n
// Function: uniquifyElems\n
// Ensure each element has a unique ID\n
//\n
// Parameters:\n
// g - The parent element of the tree to give unique IDs\n
var uniquifyElems = this.uniquifyElems = function(g) {\n
  var ids = {};\n
  // TODO: Handle markers and connectors.  These are not yet re-identified properly\n
  // as their referring elements do not get remapped.\n
  //\n
  // \074marker id=\'se_marker_end_svg_7\'/\076\n
  // \074polyline id=\'svg_7\' se:connector=\'svg_1 svg_6\' marker-end=\'url(#se_marker_end_svg_7)\'/\076\n
  // \n
  // Problem #1: if svg_1 gets renamed, we do not update the polyline\'s se:connector attribute\n
  // Problem #2: if the polyline svg_7 gets renamed, we do not update the marker id nor the polyline\'s marker-end attribute\n
  var ref_elems = ["filter", "linearGradient", "pattern", "radialGradient", "symbol", "textPath", "use"];\n
  \n
  svgedit.utilities.walkTree(g, function(n) {\n
    // if it\'s an element node\n
    if (n.nodeType == 1) {\n
      // and the element has an ID\n
      if (n.id) {\n
        // and we haven\'t tracked this ID yet\n
        if (!(n.id in ids)) {\n
          // add this id to our map\n
          ids[n.id] = {elem:null, attrs:[], hrefs:[]};\n
        }\n
        ids[n.id]["elem"] = n;\n
      }\n
      \n
      // now search for all attributes on this element that might refer\n
      // to other elements\n
      $.each(ref_attrs,function(i,attr) {\n
        var attrnode = n.getAttributeNode(attr);\n
        if (attrnode) {\n
          // the incoming file has been sanitized, so we should be able to safely just strip off the leading #\n
          var url = svgedit.utilities.getUrlFromAttr(attrnode.value),\n
            refid = url ? url.substr(1) : null;\n
          if (refid) {\n
            if (!(refid in ids)) {\n
              // add this id to our map\n
              ids[refid] = {elem:null, attrs:[], hrefs:[]};\n
            }\n
            ids[refid]["attrs"].push(attrnode);\n
          }\n
        }\n
      });\n
      \n
      // check xlink:href now\n
      var href = svgedit.utilities.getHref(n);\n
      // TODO: what if an \074image\076 or \074a\076 element refers to an element internally?\n
      if(href \046\046 ref_elems.indexOf(n.nodeName) \076= 0)\n
      {\n
        var refid = href.substr(1);\n
        if (refid) {\n
          if (!(refid in ids)) {\n
            // add this id to our map\n
            ids[refid] = {elem:null, attrs:[], hrefs:[]};\n
          }\n
          ids[refid]["hrefs"].push(n);\n
        }\n
      }           \n
    }\n
  });\n
  \n
  // in ids, we now have a map of ids, elements and attributes, let\'s re-identify\n
  for (var oldid in ids) {\n
    if (!oldid) continue;\n
    var elem = ids[oldid]["elem"];\n
    if (elem) {\n
      var newid = getNextId();\n
      \n
      // assign element its new id\n
      elem.id = newid;\n
      \n
      // remap all url() attributes\n
      var attrs = ids[oldid]["attrs"];\n
      var j = attrs.length;\n
      while (j--) {\n
        var attr = attrs[j];\n
        attr.ownerElement.setAttribute(attr.name, "url(#" + newid + ")");\n
      }\n
      \n
      // remap all href attributes\n
      var hreffers = ids[oldid]["hrefs"];\n
      var k = hreffers.length;\n
      while (k--) {\n
        var hreffer = hreffers[k];\n
        svgedit.utilities.setHref(hreffer, "#"+newid);\n
      }\n
    }\n
  }\n
}\n
\n
// Function setUseData\n
// Assigns reference data for each use element\n
var setUseData = this.setUseData = function(parent) {\n
  var elems = $(parent);\n
  \n
  if(parent.tagName !== \'use\') {\n
    elems = elems.find(\'use\');\n
  }\n
  \n
  elems.each(function() {\n
    var id = getHref(this).substr(1);\n
    var ref_elem = getElem(id);\n
    if(!ref_elem) return;\n
    $(this).data(\'ref\', ref_elem);\n
    if(ref_elem.tagName == \'symbol\' || ref_elem.tagName == \'svg\') {\n
      $(this).data(\'symbol\', ref_elem).data(\'ref\', ref_elem);\n
    }\n
  });\n
}\n
\n
// Function convertGradients\n
// Converts gradients from userSpaceOnUse to objectBoundingBox\n
var convertGradients = this.convertGradients = function(elem) {\n
  var elems = $(elem).find(\'linearGradient, radialGradient\');\n
  if(!elems.length \046\046 svgedit.browser.isWebkit()) {\n
    // Bug in webkit prevents regular *Gradient selector search\n
    elems = $(elem).find(\'*\').filter(function() {\n
      return (this.tagName.indexOf(\'Gradient\') \076= 0);\n
    });\n
  }\n
  \n
  elems.each(function() {\n
    var grad = this;\n
    if($(grad).attr(\'gradientUnits\') === \'userSpaceOnUse\') {\n
      // TODO: Support more than one element with this ref by duplicating parent grad\n
      var elems = $(svgcontent).find(\'[fill="url(#\' + grad.id + \')"],[stroke="url(#\' + grad.id + \')"]\');\n
      if(!elems.length) return;\n
      \n
      // get object\'s bounding box\n
      var bb = svgedit.utilities.getBBox(elems[0]);\n
      \n
      // This will occur if the element is inside a \074defs\076 or a \074symbol\076,\n
      // in which we shouldn\'t need to convert anyway.\n
      if(!bb) return;\n
      \n
      if(grad.tagName === \'linearGradient\') {\n
        var g_coords = $(grad).attr([\'x1\', \'y1\', \'x2\', \'y2\']);\n
        \n
        // If has transform, convert\n
        var tlist = grad.gradientTransform.baseVal;\n
        if(tlist \046\046 tlist.numberOfItems \076 0) {\n
          var m = transformListToTransform(tlist).matrix;\n
          var pt1 = transformPoint(g_coords.x1, g_coords.y1, m);\n
          var pt2 = transformPoint(g_coords.x2, g_coords.y2, m);\n
          \n
          g_coords.x1 = pt1.x;\n
          g_coords.y1 = pt1.y;\n
          g_coords.x2 = pt2.x;\n
          g_coords.y2 = pt2.y;\n
          grad.removeAttribute(\'gradientTransform\');\n
        }\n
        \n
        $(grad).attr({\n
          x1: (g_coords.x1 - bb.x) / bb.width,\n
          y1: (g_coords.y1 - bb.y) / bb.height,\n
          x2: (g_coords.x2 - bb.x) / bb.width,\n
          y2: (g_coords.y2 - bb.y) / bb.height\n
        });\n
        grad.removeAttribute(\'gradientUnits\');\n
      } else {\n
        // Note: radialGradient elements cannot be easily converted \n
        // because userSpaceOnUse will keep circular gradients, while\n
        // objectBoundingBox will x/y scale the gradient according to\n
        // its bbox. \n
        \n
        // For now we\'ll do nothing, though we should probably have\n
        // the gradient be updated as the element is moved, as \n
        // inkscape/illustrator do.\n
      \n
//                var g_coords = $(grad).attr([\'cx\', \'cy\', \'r\']);\n
//                \n
//            $(grad).attr({\n
//              cx: (g_coords.cx - bb.x) / bb.width,\n
//              cy: (g_coords.cy - bb.y) / bb.height,\n
//              r: g_coords.r\n
//            });\n
//            \n
//                grad.removeAttribute(\'gradientUnits\');\n
      }\n
      \n
\n
    }\n
  });\n
}\n
\n
// Function: convertToGroup\n
// Converts selected/given \074use\076 or child SVG element to a group\n
var convertToGroup = this.convertToGroup = function(elem) {\n
  if(!elem) {\n
    elem = selectedElements[0];\n
  }\n
  var $elem = $(elem);\n
  \n
  var batchCmd = new BatchCommand();\n
  \n
  var ts;\n
  \n
  if($elem.data(\'gsvg\')) {\n
    // Use the gsvg as the new group\n
    var svg = elem.firstChild;\n
    var pt = $(svg).attr([\'x\', \'y\']);\n
    \n
    $(elem.firstChild.firstChild).unwrap();\n
    $(elem).removeData(\'gsvg\');\n
    \n
    var tlist = getTransformList(elem);\n
    var xform = svgroot.createSVGTransform();\n
    xform.setTranslate(pt.x, pt.y);\n
    tlist.appendItem(xform);\n
    recalculateDimensions(elem);\n
    call("selected", [elem]);\n
  } else if($elem.data(\'symbol\')) {\n
    elem = $elem.data(\'symbol\');\n
    \n
    ts = $elem.attr(\'transform\');\n
    var pos = $elem.attr([\'x\',\'y\']);\n
\n
    var vb = elem.getAttribute(\'viewBox\');\n
    \n
    if(vb) {\n
      var nums = vb.split(\' \');\n
      pos.x -= +nums[0];\n
      pos.y -= +nums[1];\n
    }\n
    \n
    // Not ideal, but works\n
    ts += " translate(" + (pos.x || 0) + "," + (pos.y || 0) + ")";\n
    \n
    var prev = $elem.prev();\n
    \n
    // Remove \074use\076 element\n
    batchCmd.addSubCommand(new RemoveElementCommand($elem[0], $elem[0].nextSibling, $elem[0].parentNode));\n
    $elem.remove();\n
    \n
    // See if other elements reference this symbol\n
    var has_more = $(svgcontent).find(\'use:data(symbol)\').length;\n
      \n
    var g = svgdoc.createElementNS(svgns, "g");\n
    var childs = elem.childNodes;\n
    \n
    for(var i = 0; i \074 childs.length; i++) {\n
      g.appendChild(childs[i].cloneNode(true));\n
    }\n
    \n
    // Duplicate the gradients for Gecko, since they weren\'t included in the \074symbol\076\n
    if(svgedit.browser.isGecko()) {\n
      var dupeGrads = $(findDefs()).children(\'linearGradient,radialGradient,pattern\').clone();\n
      $(g).append(dupeGrads);\n
    }\n
    \n
    if (ts) {\n
      g.setAttribute("transform", ts);\n
    }\n
    \n
    var parent = elem.parentNode;\n
    \n
    uniquifyElems(g);\n
    \n
    // Put the dupe gradients back into \074defs\076 (after uniquifying them)\n
    if(svgedit.browser.isGecko()) {\n
      $(findDefs()).append( $(g).find(\'linearGradient,radialGradient,pattern\') );\n
    }\n
  \n
    // now give the g itself a new id\n
    g.id = getNextId();\n
    \n
    prev.after(g);\n
    \n
    if(parent) {\n
      if(!has_more) {\n
        // remove symbol/svg element\n
        var nextSibling = elem.nextSibling;\n
        parent.removeChild(elem);\n
        batchCmd.addSubCommand(new RemoveElementCommand(elem, nextSibling, parent));\n
      }\n
      batchCmd.addSubCommand(new InsertElementCommand(g));\n
    }\n
    \n
    setUseData(g);\n
    \n
    if(svgedit.browser.isGecko()) {\n
      convertGradients(findDefs());\n
    } else {\n
      convertGradients(g);\n
    }\n
    \n
    // recalculate dimensions on the top-level children so that unnecessary transforms\n
    // are removed\n
    svgedit.utilities.walkTreePost(g, function(n){try{recalculateDimensions(n)}catch(e){console.log(e)}});\n
    \n
    // Give ID for any visible element missing one\n
    $(g).find(visElems).each(function() {\n
      if(!this.id) this.id = getNextId();\n
    });\n
    \n
    selectOnly([g]);\n
    \n
    var cm = pushGroupProperties(g, true);\n
    if(cm) {\n
      batchCmd.addSubCommand(cm);\n
    }\n
\n
    addCommandToHistory(batchCmd);\n
    \n
  } else {\n
    console.log(\'Unexpected element to ungroup:\', elem);\n
  }\n
}\n
\n
//   \n
// Function: setSvgString\n
// This function sets the current drawing as the input SVG XML.\n
//\n
// Parameters:\n
// xmlString - The SVG as XML text.\n
//\n
// Returns:\n
// This function returns false if the set was unsuccessful, true otherwise.\n
this.setSvgString = function(xmlString) {\n
  try {\n
    // convert string into XML document\n
    var newDoc = svgedit.utilities.text2xml(xmlString);\n
\n
    this.prepareSvg(newDoc);\n
\n
    var batchCmd = new BatchCommand("Change Source");\n
\n
    // remove old svg document\n
    var nextSibling = svgcontent.nextSibling;\n
    var oldzoom = svgroot.removeChild(svgcontent);\n
    batchCmd.addSubCommand(new RemoveElementCommand(oldzoom, nextSibling, svgroot));\n
  \n
    // set new svg document\n
    // If DOM3 adoptNode() available, use it. Otherwise fall back to DOM2 importNode()\n
    if(svgdoc.adoptNode) {\n
      svgcontent = svgdoc.adoptNode(newDoc.documentElement);\n
    }\n
    else {\n
      svgcontent = svgdoc.importNode(newDoc.documentElement, true);\n
    }\n
    \n
    svgroot.appendChild(svgcontent);\n
    var content = $(svgcontent);\n
    \n
    canvas.current_drawing_ = new svgedit.draw.Drawing(svgcontent, idprefix);\n
    \n
    // retrieve or set the nonce\n
    var nonce = getCurrentDrawing().getNonce();\n
    if (nonce) {\n
      call("setnonce", nonce);\n
    } else {\n
      call("unsetnonce");\n
    }\n
    \n
    // change image href vals if possible\n
    content.find(\'image\').each(function() {\n
      var image = this;\n
      preventClickDefault(image);\n
      var val = getHref(this);\n
      if(val.indexOf(\'data:\') === 0) {\n
        // Check if an SVG-edit data URI\n
        var m = val.match(/svgedit_url=(.*?);/);\n
        if(m) {\n
          var url = decodeURIComponent(m[1]);\n
          $(new Image()).load(function() {\n
            image.setAttributeNS(xlinkns,\'xlink:href\',url);\n
          }).attr(\'src\',url);\n
        }\n
      }\n
      // Add to encodableImages if it loads\n
      canvas.embedImage(val);\n
    });\n
  \n
    // Wrap child SVGs in group elements\n
    content.find(\'svg\').each(function() {\n
      // Skip if it\'s in a \074defs\076\n
      if($(this).closest(\'defs\').length) return;\n
    \n
      uniquifyElems(this);\n
    \n
      // Check if it already has a gsvg group\n
      var pa = this.parentNode;\n
      if(pa.childNodes.length === 1 \046\046 pa.nodeName === \'g\') {\n
        $(pa).data(\'gsvg\', this);\n
        pa.id = pa.id || getNextId();\n
      } else {\n
        groupSvgElem(this);\n
      }\n
    });\n
    \n
    // Put all paint elems in defs\n
    \n
    content.find(\'linearGradient, radialGradient, pattern\').appendTo(findDefs());\n
    \n
    // Set ref element for \074use\076 elements\n
    \n
    // TODO: This should also be done if the object is re-added through "redo"\n
    setUseData(content);\n
    \n
    convertGradients(content[0]);\n
    \n
    // recalculate dimensions on the top-level children so that unnecessary transforms\n
    // are removed\n
    svgedit.utilities.walkTreePost(svgcontent, function(n){try{recalculateDimensions(n)}catch(e){console.log(e)}});\n
    \n
    var attrs = {\n
      id: \'svgcontent\',\n
      overflow: curConfig.show_outside_canvas?\'visible\':\'hidden\'\n
    };\n
    \n
    var percs = false;\n
    \n
    // determine proper size\n
    if (content.attr("viewBox")) {\n
      var vb = content.attr("viewBox").split(\' \');\n
      attrs.width = vb[2];\n
      attrs.height = vb[3];\n
    }\n
    // handle content that doesn\'t have a viewBox\n
    else {\n
      $.each([\'width\', \'height\'], function(i, dim) {\n
        // Set to 100 if not given\n
        var val = content.attr(dim);\n
        \n
        if(!val) val = \'100%\';\n
        \n
        if((val+\'\').substr(-1) === "%") {\n
          // Use user units if percentage given\n
          percs = true;\n
        } else {\n
          attrs[dim] = convertToNum(dim, val);\n
        }\n
      });\n
    }\n
    \n
    // identify layers\n
    identifyLayers();\n
    \n
    // Give ID for any visible layer children missing one\n
    content.children().find(visElems).each(function() {\n
      if(!this.id) this.id = getNextId();\n
    });\n
    \n
    // Percentage width/height, so let\'s base it on visible elements\n
    if(percs) {\n
      var bb = getStrokedBBox();\n
      attrs.width = bb.width + bb.x;\n
      attrs.height = bb.height + bb.y;\n
    }\n
    \n
    // Just in case negative numbers are given or \n
    // result from the percs calculation\n
    if(attrs.width \074= 0) attrs.width = 200;\n
    if(attrs.height \074= 0) attrs.height = 200;\n
    \n
    content.attr(attrs);\n
    this.contentW = attrs[\'width\'];\n
    this.contentH = attrs[\'height\'];\n
    \n
    $("#canvas_width").val(this.contentW)\n
    $("#canvas_height").val(this.contentH)\n
    var background = $("#canvas_background")\n
    if (background.length) {\n
      var opacity = background.attr("fill-opacity")\n
      opacity = opacity ? parseInt(opacity)*100 : 100\n
      fill = this.getPaint(background.attr("fill"), opacity, "canvas")\n
      methodDraw.paintBox.canvas.setPaint(fill)\n
    }\n
    else {\n
      fill = this.getPaint("none", 100, "canvas")\n
      methodDraw.paintBox.canvas.setPaint(fill)\n
    }\n
\n
    batchCmd.addSubCommand(new InsertElementCommand(svgcontent));\n
    // update root to the correct size\n
    var changes = content.attr(["width", "height"]);\n
    batchCmd.addSubCommand(new ChangeElementCommand(svgroot, changes));\n
    \n
    // reset zoom\n
    current_zoom = 1;\n
    \n
    // reset transform lists\n
    svgedit.transformlist.resetListMap();\n
    clearSelection();\n
    svgedit.path.clearData();\n
    svgroot.appendChild(selectorManager.selectorParentGroup);\n
    \n
    addCommandToHistory(batchCmd);\n
    call("changed", [svgcontent]);\n
  } catch(e) {\n
    console.log(e);\n
    return false;\n
  }\n
\n
  return true;\n
};\n
\n
\n
this.getPaint = function(color, opac, type) {\n
  // update the editor\'s fill paint\n
  var opts = null;\n
  if (color.indexOf("url(#") === 0) {\n
    var refElem = svgCanvas.getRefElem(color);\n
    if(refElem) {\n
      refElem = refElem.cloneNode(true);\n
    } else {\n
      refElem =  $("#" + type + "_color defs *")[0];\n
    }\n
\n
    opts = { alpha: opac };\n
    opts[refElem.tagName] = refElem;\n
  } \n
  else if (color.indexOf("#") === 0) {\n
    opts = {\n
      alpha: opac,\n
      solidColor: color.substr(1)\n
    };\n
  }\n
  else {\n
    opts = {\n
      alpha: opac,\n
      solidColor: \'none\'\n
    };\n
  }\n
  return new $.jGraduate.Paint(opts);\n
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
// * import should happen in top-left of current zoomed viewport  \n
this.importSvgString = function(xmlString) {\n
\n
  try {\n
    // Get unique ID\n
    var uid = svgedit.utilities.encode64(xmlString.length + xmlString).substr(0,32);\n
    \n
    var useExisting = false;\n
\n
    // Look for symbol and make sure symbol exists in image\n
    if(import_ids[uid]) {\n
      if( $(import_ids[uid].symbol).parents(\'#svgroot\').length ) {\n
        useExisting = true;\n
      }\n
    }\n
    \n
    var batchCmd = new BatchCommand("Import SVG");\n
  \n
    if(useExisting) {\n
      var symbol = import_ids[uid].symbol;\n
      var ts = import_ids[uid].xform;\n
    } else {\n
      // convert string into XML document\n
      var newDoc = svgedit.utilities.text2xml(xmlString);\n
  \n
      this.prepareSvg(newDoc);\n
  \n
      // import new svg document into our document\n
      var svg;\n
      // If DOM3 adoptNode() available, use it. Otherwise fall back to DOM2 importNode()\n
      if(svgdoc.adoptNode) {\n
        svg = svgdoc.adoptNode(newDoc.documentElement);\n
      }\n
      else {\n
        svg = svgdoc.importNode(newDoc.documentElement, true);\n
      }\n
      \n
      uniquifyElems(svg);\n
      \n
      var innerw = convertToNum(\'width\', svg.getAttribute("width")),\n
        innerh = convertToNum(\'height\', svg.getAttribute("height")),\n
        innervb = svg.getAttribute("viewBox"),\n
        // if no explicit viewbox, create one out of the width and height\n
        vb = innervb ? innervb.split(" ") : [0,0,innerw,innerh];\n
      for (var j = 0; j \074 4; ++j)\n
        vb[j] = +(vb[j]);\n
  \n
      // TODO: properly handle preserveAspectRatio\n
      var canvasw = +svgcontent.getAttribute("width"),\n
        canvash = +svgcontent.getAttribute("height");\n
      // imported content should be 1/3 of the canvas on its largest dimension\n
      \n
      if (innerh \076 innerw) {\n
        var ts = "scale(" + (canvash/3)/vb[3] + ")";\n
      }\n
      else {\n
        var ts = "scale(" + (canvash/3)/vb[2] + ")";\n
      }\n
      \n
      // Hack to make recalculateDimensions understand how to scale\n
      ts = "translate(0) " + ts + " translate(0)";\n
      \n
      var symbol = svgdoc.createElementNS(svgns, "symbol");\n
      var defs = findDefs();\n
      \n
      if(svgedit.browser.isGecko()) {\n
        // Move all gradients into root for Firefox, workaround for this bug:\n
        // https://bugzilla.mozilla.org/show_bug.cgi?id=353575\n
        // TODO: Make this properly undo-able.\n
        $(svg).find(\'linearGradient, radialGradient, pattern\').appendTo(defs);\n
      }\n
  \n
      while (svg.firstChild) {\n
        var first = svg.firstChild;\n
        symbol.appendChild(first);\n
      }\n
      var attrs = svg.attributes;\n
      for(var i=0; i \074 attrs.length; i++) {\n
        var attr = attrs[i];\n
        symbol.setAttribute(attr.nodeName, attr.nodeValue);\n
      }\n
      symbol.id = getNextId();\n
      \n
      // Store data\n
      import_ids[uid] = {\n
        symbol: symbol,\n
        xform: ts\n
      }\n
      \n
      findDefs().appendChild(symbol);\n
      batchCmd.addSubCommand(new InsertElementCommand(symbol));\n
    }\n
    \n
    \n
    var use_el = svgdoc.createElementNS(svgns, "use");\n
    use_el.id = getNextId();\n
    setHref(use_el, "#" + symbol.id);\n
    \n
    (current_group || getCurrentDrawing().getCurrentLayer()).appendChild(use_el);\n
    batchCmd.addSubCommand(new InsertElementCommand(use_el));\n
    clearSelection();\n
    \n
    use_el.setAttribute("transform", ts);\n
    recalculateDimensions(use_el);\n
    $(use_el).data(\'symbol\', symbol).data(\'ref\', symbol);\n
    addToSelection([use_el]);\n
    \n
    // TODO: Find way to add this in a recalculateDimensions-parsable way\n
//        if (vb[0] != 0 || vb[1] != 0)\n
//          ts = "translate(" + (-vb[0]) + "," + (-vb[1]) + ") " + ts;\n
    addCommandToHistory(batchCmd);\n
    call("changed", [svgcontent]);\n
\n
  } catch(e) {\n
    console.log(e);\n
    return false;\n
  }\n
\n
  return true;\n
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
  leaveContext();\n
  getCurrentDrawing().identifyLayers();\n
};\n
\n
// Function: createLayer\n
// Creates a new top-level layer in the drawing with the given name, sets the current layer \n
// to it, and then clears the selection  This function then calls the \'changed\' handler.\n
// This is an undoable action.\n
//\n
// Parameters:\n
// name - The given name\n
this.createLayer = function(name) {\n
  var batchCmd = new BatchCommand("Create Layer");\n
  var new_layer = getCurrentDrawing().createLayer(name);\n
  batchCmd.addSubCommand(new InsertElementCommand(new_layer));\n
  addCommandToHistory(batchCmd);\n
  clearSelection();\n
  call("changed", [new_layer]);\n
};\n
\n
// Function: cloneLayer\n
// Creates a new top-level layer in the drawing with the given name, copies all the current layer\'s contents\n
// to it, and then clears the selection  This function then calls the \'changed\' handler.\n
// This is an undoable action.\n
//\n
// Parameters:\n
// name - The given name\n
this.cloneLayer = function(name) {\n
  var batchCmd = new BatchCommand("Duplicate Layer");\n
  var new_layer = svgdoc.createElementNS(svgns, "g");\n
  var layer_title = svgdoc.createElementNS(svgns, "title");\n
  layer_title.textContent = name;\n
  new_layer.appendChild(layer_title);\n
  var current_layer = getCurrentDrawing().getCurrentLayer();\n
  $(current_layer).after(new_layer);\n
  var childs = current_layer.childNodes;\n
  for(var i = 0; i \074 childs.length; i++) {\n
    var ch = childs[i];\n
    if(ch.localName == \'title\') continue;\n
    new_layer.appendChild(copyElem(ch));\n
  }\n
  \n
  clearSelection();\n
  identifyLayers();\n
\n
  batchCmd.addSubCommand(new InsertElementCommand(new_layer));\n
  addCommandToHistory(batchCmd);\n
  canvas.setCurrentLayer(name);\n
  call("changed", [new_layer]);\n
};\n
\n
// Function: deleteCurrentLayer\n
// Deletes the current layer from the drawing and then clears the selection. This function \n
// then calls the \'changed\' handler.  This is an undoable action.\n
this.deleteCurrentLayer = function() {\n
  var current_layer = getCurrentDrawing().getCurrentLayer();\n
  var nextSibling = current_layer.nextSibling;\n
  var parent = current_layer.parentNode;\n
  current_layer = getCurrentDrawing().deleteCurrentLayer();\n
  if (current_layer) {\n
    var batchCmd = new BatchCommand("Delete Layer");\n
    // store in our Undo History\n
    batchCmd.addSubCommand(new RemoveElementCommand(current_layer, nextSibling, parent));\n
    addCommandToHistory(batchCmd);\n
    clearSelection();\n
    call("changed", [parent]);\n
    return true;\n
  }\n
  return false;\n
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
  var result = getCurrentDrawing().setCurrentLayer(svgedit.utilities.toXml(name));\n
  if (result) {\n
    clearSelection();\n
  }\n
  return result;\n
};\n
\n
// Function: renameCurrentLayer\n
// Renames the current layer. If the layer name is not valid (i.e. unique), then this function \n
// does nothing and returns false, otherwise it returns true. This is an undo-able action.\n
// \n
// Parameters:\n
// newname - the new name you want to give the current layer.  This name must be unique \n
// among all layer names.\n
//\n
// Returns:\n
// true if the rename succeeded, false otherwise.\n
this.renameCurrentLayer = function(newname) {\n
  var drawing = getCurrentDrawing();\n
  if (drawing.current_layer) {\n
    var oldLayer = drawing.current_layer;\n
    // setCurrentLayer will return false if the name doesn\'t already exist\n
    // this means we are free to rename our oldLayer\n
    if (!canvas.setCurrentLayer(newname)) {\n
      var batchCmd = new BatchCommand("Rename Layer");\n
      // find the index of the layer\n
      for (var i = 0; i \074 drawing.getNumLayers(); ++i) {\n
        if (drawing.all_layers[i][1] == oldLayer) break;\n
      }\n
      var oldname = drawing.getLayerName(i);\n
      drawing.all_layers[i][0] = svgedit.utilities.toXml(newname);\n
    \n
      // now change the underlying title element contents\n
      var len = oldLayer.childNodes.length;\n
      for (var i = 0; i \074 len; ++i) {\n
        var child = oldLayer.childNodes.item(i);\n
        // found the \074title\076 element, now append all the\n
        if (child \046\046 child.tagName == "title") {\n
          // wipe out old name \n
          while (child.firstChild) { child.removeChild(child.firstChild); }\n
          child.textContent = newname;\n
\n
          batchCmd.addSubCommand(new ChangeElementCommand(child, {"#text":oldname}));\n
          addCommandToHistory(batchCmd);\n
          call("changed", [oldLayer]);\n
          return true;\n
        }\n
      }\n
    }\n
    drawing.current_layer = oldLayer;\n
  }\n
  return false;\n
};\n
\n
// Function: setCurrentLayerPosition\n
// Changes the position of the current layer to the new value. If the new index is not valid, \n
// this function does nothing and returns false, otherwise it returns true. This is an\n
// undo-able action.\n
//\n
// Parameters:\n
// newpos - The zero-based index of the new position of the layer.  This should be between\n
// 0 and (number of layers - 1)\n
// \n
// Returns:\n
// true if the current layer position was changed, false otherwise.\n
this.setCurrentLayerPosition = function(newpos) {\n
  var drawing = getCurrentDrawing();\n
  if (drawing.current_layer \046\046 newpos \076= 0 \046\046 newpos \074 drawing.getNumLayers()) {\n
    for (var oldpos = 0; oldpos \074 drawing.getNumLayers(); ++oldpos) {\n
      if (drawing.all_layers[oldpos][1] == drawing.current_layer) break;\n
    }\n
    // some unknown error condition (current_layer not in all_layers)\n
    if (oldpos == drawing.getNumLayers()) { return false; }\n
    \n
    if (oldpos != newpos) {\n
      // if our new position is below us, we need to insert before the node after newpos\n
      var refLayer = null;\n
      var oldNextSibling = drawing.current_layer.nextSibling;\n
      if (newpos \076 oldpos ) {\n
        if (newpos \074 drawing.getNumLayers()-1) {\n
          refLayer = drawing.all_layers[newpos+1][1];\n
        }\n
      }\n
      // if our new position is above us, we need to insert before the node at newpos\n
      else {\n
        refLayer = drawing.all_layers[newpos][1];\n
      }\n
      svgcontent.insertBefore(drawing.current_layer, refLayer);\n
      addCommandToHistory(new MoveElementCommand(drawing.current_layer, oldNextSibling, svgcontent));\n
      \n
      identifyLayers();\n
      canvas.setCurrentLayer(drawing.getLayerName(newpos));\n
      \n
      return true;\n
    }\n
  }\n
  \n
  return false;\n
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
  var drawing = getCurrentDrawing();\n
  var prevVisibility = drawing.getLayerVisibility(layername);\n
  var layer = drawing.setLayerVisibility(layername, bVisible);\n
  if (layer) {\n
    var oldDisplay = prevVisibility ? \'inline\' : \'none\';\n
    addCommandToHistory(new ChangeElementCommand(layer, {\'display\':oldDisplay}, \'Layer Visibility\'));\n
  } else {\n
    return false;\n
  }\n
  \n
  if (layer == drawing.getCurrentLayer()) {\n
    clearSelection();\n
    pathActions.clear();\n
  }\n
//    call("changed", [selected]);  \n
  return true;\n
};\n
\n
// Function: moveSelectedToLayer\n
// Moves the selected elements to layername. If the name is not a valid layer name, then false \n
// is returned.  Otherwise it returns true. This is an undo-able action.\n
//\n
// Parameters:\n
// layername - the name of the layer you want to which you want to move the selected elements\n
//\n
// Returns:\n
// true if the selected elements were moved to the layer, false otherwise.\n
this.moveSelectedToLayer = function(layername) {\n
  // find the layer\n
  var layer = null;\n
  var drawing = getCurrentDrawing();\n
  for (var i = 0; i \074 drawing.getNumLayers(); ++i) {\n
    if (drawing.getLayerName(i) == layername) {\n
      layer = drawing.all_layers[i][1];\n
      break;\n
    }\n
  }\n
  if (!layer) return false;\n
  \n
  var batchCmd = new BatchCommand("Move Elements to Layer");\n
  \n
  // loop for each selected element and move it\n
  var selElems = selectedElements;\n
  var i = selElems.length;\n
  while (i--) {\n
    var elem = selElems[i];\n
    if (!elem) continue;\n
    var oldNextSibling = elem.nextSibling;\n
    // TODO: this is pretty brittle!\n
    var oldLayer = elem.parentNode;\n
    layer.appendChild(elem);\n
    batchCmd.addSubCommand(new MoveElementCommand(elem, oldNextSibling, oldLayer));\n
  }\n
  \n
  addCommandToHistory(batchCmd);\n
  \n
  return true;\n
};\n
\n
this.mergeLayer = function(skipHistory) {\n
  var batchCmd = new BatchCommand("Merge Layer");\n
  var drawing = getCurrentDrawing();\n
  var prev = $(drawing.current_layer).prev()[0];\n
  if(!prev) return;\n
  var childs = drawing.current_layer.childNodes;\n
  var len = childs.length;\n
  var layerNextSibling = drawing.current_layer.nextSibling;\n
  batchCmd.addSubCommand(new RemoveElementCommand(drawing.current_layer, layerNextSibling, svgcontent));\n
\n
  while(drawing.current_layer.firstChild) {\n
    var ch = drawing.current_layer.firstChild;\n
    if(ch.localName == \'title\') {\n
      var chNextSibling = ch.nextSibling;\n
      batchCmd.addSubCommand(new RemoveElementCommand(ch, chNextSibling, drawing.current_layer));\n
      drawing.current_layer.removeChild(ch);\n
      continue;\n
    }\n
    var oldNextSibling = ch.nextSibling;\n
    prev.appendChild(ch);\n
    batchCmd.addSubCommand(new MoveElementCommand(ch, oldNextSibling, drawing.current_layer));\n
  }\n
  \n
  // Remove current layer\n
  svgcontent.removeChild(drawing.current_layer);\n
  \n
  if(!skipHistory) {\n
    clearSelection();\n
    identifyLayers();\n
\n
    call("changed", [svgcontent]);\n
    \n
    addCommandToHistory(batchCmd);\n
  }\n
  \n
  drawing.current_layer = prev;\n
  return batchCmd;\n
}\n
\n
this.mergeAllLayers = function() {\n
  var batchCmd = new BatchCommand("Merge all Layers");\n
  var drawing = getCurrentDrawing();\n
  drawing.current_layer = drawing.all_layers[drawing.getNumLayers()-1][1];\n
  while($(svgcontent).children(\'g\').length \076 1) {\n
    batchCmd.addSubCommand(canvas.mergeLayer(true));\n
  }\n
  \n
  clearSelection();\n
  identifyLayers();\n
  call("changed", [svgcontent]);\n
  addCommandToHistory(batchCmd);\n
}\n
\n
// Function: leaveContext\n
// Return from a group context to the regular kind, make any previously\n
// disabled elements enabled again\n
var leaveContext = this.leaveContext = function() {\n
  var len = disabled_elems.length;\n
  if(len) {\n
    for(var i = 0; i \074 len; i++) {\n
      var elem = disabled_elems[i];\n
      \n
      var orig = elData(elem, \'orig_opac\');\n
      if(orig !== 1) {\n
        elem.setAttribute(\'opacity\', orig);\n
      } else {\n
        elem.removeAttribute(\'opacity\');\n
      }\n
      elem.setAttribute(\'style\', \'pointer-events: inherit\');\n
    }\n
    disabled_elems = [];\n
    clearSelection(true);\n
    call("contextset", null);\n
  }\n
  current_group = null;\n
}\n
\n
// Function: setContext\n
// Set the current context (for in-group editing)\n
var setContext = this.setContext = function(elem) {\n
  leaveContext();\n
  if(typeof elem === \'string\') {\n
    elem = getElem(elem);\n
  }\n
\n
  // Edit inside this group\n
  current_group = elem;\n
  \n
  // Disable other elements\n
  $(elem).parentsUntil(\'#svgcontent\').andSelf().siblings().each(function() {\n
    var opac = this.getAttribute(\'opacity\') || 1;\n
    // Store the original\'s opacity\n
    elData(this, \'orig_opac\', opac);\n
    this.setAttribute(\'opacity\', opac * .33);\n
    this.setAttribute(\'style\', \'pointer-events: none\');\n
    disabled_elems.push(this);\n
  });\n
\n
  clearSelection();\n
  call("contextset", current_group);\n
}\n
\n
// Group: Document functions\n
\n
// Function: clear\n
// Clears the current document.  This is not an undoable action.\n
this.clear = function() {\n
  pathActions.clear();\n
\n
  clearSelection();\n
\n
  // clear the svgcontent node\n
  canvas.clearSvgContentElement();\n
\n
  // create new document\n
  canvas.current_drawing_ = new svgedit.draw.Drawing(svgcontent);\n
\n
  // create empty first layer\n
  canvas.createLayer("Layer 1");\n
  \n
  // clear the undo stack\n
  canvas.undoMgr.resetUndoStack();\n
\n
  // reset the selector manager\n
  selectorManager.initGroup();\n
\n
  // reset the rubber band box\n
  rubberBox = selectorManager.getRubberBandBox();\n
\n
  call("cleared");\n
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
//    var vb = svgcontent.getAttribute("viewBox").split(\' \');\n
//    return {\'w\':vb[2], \'h\':vb[3], \'zoom\': current_zoom};\n
  \n
  var width = svgcontent.getAttribute("width")/current_zoom;\n
  var height = svgcontent.getAttribute("height")/current_zoom;\n
  \n
  return {\n
    \'w\': width,\n
    \'h\': height,\n
    \'zoom\': current_zoom\n
  };\n
};\n
\n
// Function: getZoom\n
// Returns the current zoom level\n
this.getZoom = function(){return current_zoom;};\n
\n
// Function: getVersion\n
// Returns a string which describes the revision number of SvgCanvas.\n
this.getVersion = function() {\n
  return "svgcanvas.js ($Rev: 2082 $)";\n
};\n
\n
// Function: setUiStrings\n
// Update interface strings with given values\n
//\n
// Parameters:\n
// strs - Object with strings (see uiStrings for examples)\n
this.setUiStrings = function(strs) {\n
  $.extend(uiStrings, strs.notification);\n
}\n
\n
// Function: setConfig\n
// Update configuration options with given values\n
//\n
// Parameters:\n
// opts - Object with options (see curConfig for examples)\n
this.setConfig = function(opts) {\n
  $.extend(curConfig, opts);\n
}\n
\n
// Function: getTitle\n
// Returns the current group/SVG\'s title contents\n
this.getTitle = function(elem) {\n
  elem = elem || selectedElements[0];\n
  if(!elem) return;\n
  elem = $(elem).data(\'gsvg\') || $(elem).data(\'symbol\') || elem;\n
  var childs = elem.childNodes;\n
  for (var i=0; i\074childs.length; i++) {\n
    if(childs[i].nodeName == \'title\') {\n
      return childs[i].textContent;\n
    }\n
  }\n
  return \'\';\n
}\n
\n
// Function: setGroupTitle\n
// Sets the group/SVG\'s title content\n
// TODO: Combine this with setDocumentTitle\n
this.setGroupTitle = function(val) {\n
  var elem = selectedElements[0];\n
  elem = $(elem).data(\'gsvg\') || elem;\n
  \n
  var ts = $(elem).children(\'title\');\n
  \n
  var batchCmd = new BatchCommand("Set Label");\n
  \n
  if(!val.length) {\n
    // Remove title element\n
    var tsNextSibling = ts.nextSibling;\n
    batchCmd.addSubCommand(new RemoveElementCommand(ts[0], tsNextSibling, elem));\n
    ts.remove();\n
  } else if(ts.length) {\n
    // Change title contents\n
    var title = ts[0];\n
    batchCmd.addSubCommand(new ChangeElementCommand(title, {\'#text\': title.textContent}));\n
    title.textContent = val;\n
  } else {\n
    // Add title element\n
    title = svgdoc.createElementNS(svgns, "title");\n
    title.textContent = val;\n
    $(elem).prepend(title);\n
    batchCmd.addSubCommand(new InsertElementCommand(title));\n
  }\n
\n
  addCommandToHistory(batchCmd);\n
}\n
\n
// Function: getDocumentTitle\n
// Returns the current document title or an empty string if not found\n
this.getDocumentTitle = function() {\n
  return canvas.getTitle(svgcontent);\n
}\n
\n
// Function: setDocumentTitle\n
// Adds/updates a title element for the document with the given name.\n
// This is an undoable action\n
//\n
// Parameters:\n
// newtitle - String with the new title\n
this.setDocumentTitle = function(newtitle) {\n
  var childs = svgcontent.childNodes, doc_title = false, old_title = \'\';\n
  \n
  var batchCmd = new BatchCommand("Change Image Title");\n
  \n
  for (var i=0; i\074childs.length; i++) {\n
    if(childs[i].nodeName == \'title\') {\n
      doc_title = childs[i];\n
      old_title = doc_title.textContent;\n
      break;\n
    }\n
  }\n
  if(!doc_title) {\n
    doc_title = svgdoc.createElementNS(svgns, "title");\n
    svgcontent.insertBefore(doc_title, svgcontent.firstChild);\n
  } \n
  \n
  if(newtitle.length) {\n
    doc_title.textContent = newtitle;\n
  } else {\n
    // No title given, so element is not necessary\n
    doc_title.parentNode.removeChild(doc_title);\n
  }\n
  batchCmd.addSubCommand(new ChangeElementCommand(doc_title, {\'#text\': old_title}));\n
  addCommandToHistory(batchCmd);\n
}\n
\n
// Function: getEditorNS\n
// Returns the editor\'s namespace URL, optionally adds it to root element\n
//\n
// Parameters:\n
// add - Boolean to i</string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAU=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="5" aka="AAAAAAAAAAU=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

ndicate whether or not to add the namespace value\n
this.getEditorNS = function(add) {\n
  if(add) {\n
    svgcontent.setAttribute(\'xmlns:se\', se_ns);\n
  }\n
  return se_ns;\n
}\n
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
  var res = getResolution();\n
  var w = res.w, h = res.h;\n
  var batchCmd;\n
\n
  if(x == \'fit\') {\n
    // Get bounding box\n
    var bbox = getStrokedBBox();\n
    \n
    if(bbox) {\n
      batchCmd = new BatchCommand("Fit Canvas to Content");\n
      var visEls = getVisibleElements();\n
      addToSelection(visEls);\n
      var dx = [], dy = [];\n
      $.each(visEls, function(i, item) {\n
        dx.push(bbox.x*-1);\n
        dy.push(bbox.y*-1);\n
      });\n
      \n
      var cmd = canvas.moveSelectedElements(dx, dy, true);\n
      batchCmd.addSubCommand(cmd);\n
      clearSelection();\n
      \n
      x = Math.round(bbox.width);\n
      y = Math.round(bbox.height);\n
    } else {\n
      return false;\n
    }\n
  }\n
  if (x != w || y != h) {\n
    if(!batchCmd) {\n
      batchCmd = new BatchCommand("Change Image Dimensions");\n
    }\n
\n
    x = convertToNum(\'width\', x);\n
    y = convertToNum(\'height\', y);\n
    \n
    svgcontent.setAttribute(\'width\', x);\n
    svgcontent.setAttribute(\'height\', y);\n
    \n
    this.contentW = x;\n
    this.contentH = y;\n
    batchCmd.addSubCommand(new ChangeElementCommand(svgcontent, {"width":w, "height":h}));\n
\n
    svgcontent.setAttribute("viewBox", [0, 0, x/current_zoom, y/current_zoom].join(\' \'));\n
    batchCmd.addSubCommand(new ChangeElementCommand(svgcontent, {"viewBox": ["0 0", w, h].join(\' \')}));\n
  \n
    addCommandToHistory(batchCmd);\n
    background = document.getElementById("canvas_background");\n
    if (background) {\n
      background.setAttribute("x", -1)\n
      background.setAttribute("y", -1)\n
      background.setAttribute("width", x+2)\n
      background.setAttribute("height", y+2)\n
    }\n
    call("changed", [svgcontent]);\n
  }\n
  return [x,y];\n
};\n
\n
// Function: getOffset\n
// Returns an object with x, y values indicating the svgcontent element\'s\n
// position in the editor\'s canvas.\n
this.getOffset = function() {\n
  return $(svgcontent).attr([\'x\', \'y\']);\n
}\n
\n
// Function: setBBoxZoom\n
// Sets the zoom level on the canvas-side based on the given value\n
// \n
// Parameters:\n
// val - Bounding box object to zoom to or string indicating zoom option \n
// editor_w - Integer with the editor\'s workarea box\'s width\n
// editor_h - Integer with the editor\'s workarea box\'s height\n
this.setBBoxZoom = function(val, editor_w, editor_h) {\n
  var spacer = .85;\n
  var bb;\n
  var calcZoom = function(bb) {\n
    if(!bb) return false;\n
    var w_zoom = Math.round((editor_w / bb.width)*100 * spacer)/100;\n
    var h_zoom = Math.round((editor_h / bb.height)*100 * spacer)/100; \n
    var zoomlevel = Math.min(w_zoom,h_zoom);\n
    canvas.setZoom(zoomlevel);\n
    return {\'zoom\': zoomlevel, \'bbox\': bb};\n
  }\n
  \n
  if(typeof val == \'object\') {\n
    bb = val;\n
    if(bb.width == 0 || bb.height == 0) {\n
      var newzoom = bb.zoom?bb.zoom:current_zoom * bb.factor;\n
      canvas.setZoom(newzoom);\n
      return {\'zoom\': current_zoom, \'bbox\': bb};\n
    }\n
    return calcZoom(bb);\n
  }\n
\n
  switch (val) {\n
    case \'selection\':\n
      if(!selectedElements[0]) return;\n
      var sel_elems = $.map(selectedElements, function(n){ if(n) return n; });\n
      bb = getStrokedBBox(sel_elems);\n
      break;\n
    case \'canvas\':\n
      var res = getResolution();\n
      spacer = .95;\n
      bb = {width:res.w, height:res.h ,x:0, y:0};\n
      break;\n
    case \'content\':\n
      bb = getStrokedBBox();\n
      break;\n
    case \'layer\':\n
      bb = getStrokedBBox(getVisibleElements(getCurrentDrawing().getCurrentLayer()));\n
      break;\n
    default:\n
      return;\n
  }\n
  return calcZoom(bb);\n
}\n
\n
// Function: setZoom\n
// Sets the zoom to the given level\n
//\n
// Parameters:\n
// zoomlevel - Float indicating the zoom level to change to\n
this.setZoom = function(zoomlevel) {\n
  var res = getResolution();\n
  svgcontent.setAttribute("viewBox", "0 0 " + res.w/zoomlevel + " " + res.h/zoomlevel);\n
  current_zoom = zoomlevel;\n
  $.each(selectedElements, function(i, elem) {\n
    if(!elem) return;\n
    selectorManager.requestSelector(elem).resize();\n
  });\n
  pathActions.zoomChange();\n
  runExtensions("zoomChanged", zoomlevel);\n
}\n
\n
// Function: getMode\n
// Returns the current editor mode string\n
this.getMode = function() {\n
  return current_mode;\n
};\n
\n
// Function: setMode\n
// Sets the editor\'s mode to the given string\n
//\n
// Parameters:\n
// name - String with the new mode to change to\n
this.setMode = function(name) {\n
  \n
  pathActions.clear();\n
  textActions.clear();\n
  $("#workarea").attr("class", name);\n
  cur_properties = (selectedElements[0] && selectedElements[0].nodeName == \'text\') ? cur_text : cur_shape;\n
  current_mode = name;\n
};\n
\n
// Group: Element Styling\n
\n
// Function: getColor\n
// Returns the current fill/stroke option\n
this.getColor = function(type) {\n
  return cur_properties[type];\n
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
  cur_shape[type] = val;\n
  cur_properties[type + \'_paint\'] = {type:"solidColor"};\n
  var elems = [];\n
  var i = selectedElements.length;\n
  while (i--) {\n
    var elem = selectedElements[i];\n
    if (elem) {\n
      if (elem.tagName == "g")\n
        svgedit.utilities.walkTree(elem, function(e){if(e.nodeName!="g") elems.push(e);});\n
      else {\n
        if(type == \'fill\') {\n
          if(elem.tagName != "polyline" && elem.tagName != "line") {\n
            elems.push(elem);\n
          }\n
        } else {\n
          elems.push(elem);\n
        }\n
      }\n
    }\n
  }\n
  if (elems.length > 0) {\n
    if (!preventUndo) {\n
      changeSelectedAttribute(type, val, elems);\n
      call("changed", elems);\n
    } else \n
      changeSelectedAttributeNoUndo(type, val, elems);\n
  }\n
}\n
\n
\n
// Function: findDefs\n
// Return the document\'s <defs> element, create it first if necessary\n
var findDefs = function() {\n
  var defs = svgcontent.getElementsByTagNameNS(svgns, "defs");\n
  if (defs.length > 0) {\n
    defs = defs[0];\n
  }\n
  else {\n
    defs = svgdoc.createElementNS(svgns, "defs" );\n
    if(svgcontent.firstChild) {\n
      // first child is a comment, so call nextSibling\n
      svgcontent.insertBefore( defs, svgcontent.firstChild.nextSibling);\n
    } else {\n
      svgcontent.appendChild(defs);\n
    }\n
  }\n
  return defs;\n
};\n
\n
// Function: setGradient\n
// Apply the current gradient to selected element\'s fill or stroke\n
//\n
// Parameters\n
// type - String indicating "fill" or "stroke" to apply to an element\n
var setGradient = this.setGradient = function(type) {\n
  if(!cur_properties[type + \'_paint\'] || cur_properties[type + \'_paint\'].type == "solidColor") return;\n
  var grad = canvas[type + \'Grad\'];\n
  // find out if there is a duplicate gradient already in the defs\n
  var duplicate_grad = findDuplicateGradient(grad);\n
  var defs = findDefs();\n
  // no duplicate found, so import gradient into defs\n
  if (!duplicate_grad) {\n
    var orig_grad = grad;\n
    grad = defs.appendChild( svgdoc.importNode(grad, true) );\n
    // get next id and set it on the grad\n
    grad.id = getNextId();\n
  }\n
  else { // use existing gradient\n
    grad = duplicate_grad;\n
  }\n
  canvas.setColor(type, "url(#" + grad.id + ")");\n
  if (type == "canvas") {\n
    var background = document.getElementById("canvas_background");\n
    if (background) {\n
      background.setAttribute(\'fill\', "url(#" + grad.id + ")")\n
    }\n
  }\n
}\n
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
  var defs = findDefs();\n
  var existing_grads = $(defs).find("linearGradient, radialGradient");\n
  var i = existing_grads.length;\n
  var rad_attrs = [\'r\',\'cx\',\'cy\',\'fx\',\'fy\'];\n
  while (i--) {\n
    var og = existing_grads[i];\n
    if(grad.tagName == "linearGradient") {\n
      if (grad.getAttribute(\'x1\') != og.getAttribute(\'x1\') ||\n
        grad.getAttribute(\'y1\') != og.getAttribute(\'y1\') ||\n
        grad.getAttribute(\'x2\') != og.getAttribute(\'x2\') ||\n
        grad.getAttribute(\'y2\') != og.getAttribute(\'y2\')) \n
      {\n
        continue;\n
      }\n
    } else {\n
      var grad_attrs = $(grad).attr(rad_attrs);\n
      var og_attrs = $(og).attr(rad_attrs);\n
      \n
      var diff = false;\n
      $.each(rad_attrs, function(i, attr) {\n
        if(grad_attrs[attr] != og_attrs[attr]) diff = true;\n
      });\n
      \n
      if(diff) continue;\n
    }\n
    \n
    // else could be a duplicate, iterate through stops\n
    var stops = grad.getElementsByTagNameNS(svgns, "stop");\n
    var ostops = og.getElementsByTagNameNS(svgns, "stop");\n
\n
    if (stops.length != ostops.length) {\n
      continue;\n
    }\n
\n
    var j = stops.length;\n
    while(j--) {\n
      var stop = stops[j];\n
      var ostop = ostops[j];\n
\n
      if (stop.getAttribute(\'offset\') != ostop.getAttribute(\'offset\') ||\n
        stop.getAttribute(\'stop-opacity\') != ostop.getAttribute(\'stop-opacity\') ||\n
        stop.getAttribute(\'stop-color\') != ostop.getAttribute(\'stop-color\')) \n
      {\n
        break;\n
      }\n
    }\n
\n
    if (j == -1) {\n
      return og;\n
    }\n
  } // for each gradient in defs\n
\n
  return null;\n
};\n
\n
function reorientGrads(elem, m) {\n
  var bb = svgedit.utilities.getBBox(elem);\n
  for(var i = 0; i < 2; i++) {\n
    var type = i === 0 ? \'fill\' : \'stroke\';\n
    var attrVal = elem.getAttribute(type);\n
    if(attrVal && attrVal.indexOf(\'url(\') === 0) {\n
      var grad = getRefElem(attrVal);\n
      if(grad.tagName === \'linearGradient\') {\n
        var x1 = grad.getAttribute(\'x1\') || 0;\n
        var y1 = grad.getAttribute(\'y1\') || 0;\n
        var x2 = grad.getAttribute(\'x2\') || 1;\n
        var y2 = grad.getAttribute(\'y2\') || 0;\n
        \n
        // Convert to USOU points\n
        x1 = (bb.width * x1) + bb.x;\n
        y1 = (bb.height * y1) + bb.y;\n
        x2 = (bb.width * x2) + bb.x;\n
        y2 = (bb.height * y2) + bb.y;\n
      \n
        // Transform those points\n
        var pt1 = transformPoint(x1, y1, m);\n
        var pt2 = transformPoint(x2, y2, m);\n
        \n
        // Convert back to BB points\n
        var g_coords = {};\n
        \n
        g_coords.x1 = (pt1.x - bb.x) / bb.width;\n
        g_coords.y1 = (pt1.y - bb.y) / bb.height;\n
        g_coords.x2 = (pt2.x - bb.x) / bb.width;\n
        g_coords.y2 = (pt2.y - bb.y) / bb.height;\n
    \n
        var newgrad = grad.cloneNode(true);\n
        $(newgrad).attr(g_coords);\n
  \n
        newgrad.id = getNextId();\n
        findDefs().appendChild(newgrad);\n
        elem.setAttribute(type, \'url(#\' + newgrad.id + \')\');\n
      }\n
    }\n
  }\n
}\n
\n
// Function: setPaint\n
// Set a color/gradient to a fill/stroke\n
//\n
// Parameters: \n
// type - String with "fill" or "stroke"\n
// paint - The jGraduate paint object to apply\n
this.setPaint = function(type, paint) {\n
  // make a copy\n
  var p = new $.jGraduate.Paint(paint);\n
  this.setPaintOpacity(type, p.alpha/100, true);\n
  // now set the current paint object\n
  cur_properties[type + \'_paint\'] = p;\n
  switch ( p.type ) {\n
    case "solidColor":\n
      \n
      if (p.solidColor != "none" && p.solidColor != "#none") {\n
        this.setColor(type, "#"+p.solidColor)\n
      }\n
      else {\n
        this.setColor(type, "none");\n
        var selector = (type == "fill") ? "#fill_color rect" : "#stroke_color rect" \n
        document.querySelector(selector).setAttribute(\'fill\', \'none\');\n
      }\n
      break;\n
    case "linearGradient":\n
    case "radialGradient":\n
      canvas[type + \'Grad\'] = p[p.type];\n
      setGradient(type);\n
      break;\n
    default:\n
//      console.log("none!");\n
  }\n
};\n
\n
\n
// this.setStrokePaint = function(p) {\n
//  // make a copy\n
//  var p = new $.jGraduate.Paint(p);\n
//  this.setStrokeOpacity(p.alpha/100);\n
// \n
//  // now set the current paint object\n
//  cur_properties.stroke_paint = p;\n
//  switch ( p.type ) {\n
//    case "solidColor":\n
//      this.setColor(\'stroke\', p.solidColor != "none" ? "#"+p.solidColor : "none");;\n
//      break;\n
//    case "linearGradient"\n
//    case "radialGradient"\n
//      canvas.strokeGrad = p[p.type];\n
//      setGradient(type); \n
//    default:\n
// //     console.log("none!");\n
//  }\n
// };\n
// \n
// this.setFillPaint = function(p, addGrad) {\n
//  // make a copy\n
//  var p = new $.jGraduate.Paint(p);\n
//  this.setFillOpacity(p.alpha/100, true);\n
// \n
//  // now set the current paint object\n
//  cur_properties.fill_paint = p;\n
//  if (p.type == "solidColor") {\n
//    this.setColor(\'fill\', p.solidColor != "none" ? "#"+p.solidColor : "none");\n
//  }\n
//  else if(p.type == "linearGradient") {\n
//    canvas.fillGrad = p.linearGradient;\n
//    if(addGrad) setGradient(); \n
//  }\n
//  else if(p.type == "radialGradient") {\n
//    canvas.fillGrad = p.radialGradient;\n
//    if(addGrad) setGradient(); \n
//  }\n
//  else {\n
// //     console.log("none!");\n
//  }\n
// };\n
\n
// Function: getStrokeWidth\n
// Returns the current stroke-width value\n
this.getStrokeWidth = function() {\n
  return cur_properties.stroke_width;\n
};\n
\n
// Function: setStrokeWidth\n
// Sets the stroke width for the current selected elements\n
// When attempting to set a line\'s width to 0, this changes it to 1 instead\n
//\n
// Parameters:\n
// val - A Float indicating the new stroke width value\n
this.setStrokeWidth = function(val) {\n
  if(val == 0 && [\'line\', \'path\'].indexOf(current_mode) >= 0) {\n
    canvas.setStrokeWidth(1);\n
    return;\n
  }\n
  cur_properties.stroke_width = val;\n
  \n
  var elems = [];\n
  var i = selectedElements.length;\n
  while (i--) {\n
    var elem = selectedElements[i];\n
    if (elem) {\n
      if (elem.tagName == "g")\n
        svgedit.utilities.walkTree(elem, function(e){if(e.nodeName!="g") elems.push(e);});\n
      else \n
        elems.push(elem);\n
    }\n
  }   \n
  if (elems.length > 0) {\n
    changeSelectedAttribute("stroke-width", val, elems);\n
    call("changed", selectedElements);\n
  }\n
};\n
\n
// Function: setStrokeAttr\n
// Set the given stroke-related attribute the given value for selected elements\n
//\n
// Parameters:\n
// attr - String with the attribute name\n
// val - String or number with the attribute value\n
this.setStrokeAttr = function(attr, val) {\n
  cur_shape[attr.replace(\'-\',\'_\')] = val;\n
  var elems = [];\n
  var i = selectedElements.length;\n
  while (i--) {\n
    var elem = selectedElements[i];\n
    if (elem) {\n
      if (elem.tagName == "g")\n
        svgedit.utilities.walkTree(elem, function(e){if(e.nodeName!="g") elems.push(e);});\n
      else \n
        elems.push(elem);\n
    }\n
  }   \n
  if (elems.length > 0) {\n
    changeSelectedAttribute(attr, val, elems);\n
    call("changed", selectedElements);\n
  }\n
};\n
\n
// Function: getStyle\n
// Returns current style options\n
this.getStyle = function() {\n
  return cur_shape;\n
}\n
\n
// Function: getOpacity\n
// Returns the current opacity\n
this.getOpacity = function() {\n
  return cur_shape.opacity;\n
};\n
\n
// Function: setOpacity\n
// Sets the given opacity to the current selected elements\n
this.setOpacity = function(val) {\n
  cur_shape.opacity = val;\n
  changeSelectedAttribute("opacity", val);\n
};\n
\n
// Function: getOpacity\n
// Returns the current fill opacity\n
this.getFillOpacity = function() {\n
  return cur_shape.fill_opacity;\n
};\n
\n
// Function: getStrokeOpacity\n
// Returns the current stroke opacity\n
this.getStrokeOpacity = function() {\n
  return cur_shape.stroke_opacity;\n
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
  cur_shape[type + \'_opacity\'] = val;\n
  if (!preventUndo)\n
    changeSelectedAttribute(type + "-opacity", val);\n
  else\n
    changeSelectedAttributeNoUndo(type + "-opacity", val);\n
};\n
\n
// Function: getBlur\n
// Gets the stdDeviation blur value of the given element\n
//\n
// Parameters:\n
// elem - The element to check the blur value for\n
this.getBlur = function(elem) {\n
  var val = 0;\n
//    var elem = selectedElements[0];\n
  \n
  if(elem) {\n
    var filter_url = elem.getAttribute(\'filter\');\n
    if(filter_url) {\n
      var blur = getElem(elem.id + \'_blur\');\n
      if(blur) {\n
        val = blur.firstChild.getAttribute(\'stdDeviation\');\n
      }\n
    }\n
  }\n
  return val;\n
};\n
\n
(function() {\n
  var cur_command = null;\n
  var filter = null;\n
  var filterHidden = false;\n
  \n
  // Function: setBlurNoUndo\n
  // Sets the stdDeviation blur value on the selected element without being undoable\n
  //\n
  // Parameters:\n
  // val - The new stdDeviation value\n
  canvas.setBlurNoUndo = function(val) {\n
    if(!filter) {\n
      canvas.setBlur(val);\n
      return;\n
    }\n
    if(val === 0) {\n
      // Don\'t change the StdDev, as that will hide the element.\n
      // Instead, just remove the value for "filter"\n
      changeSelectedAttributeNoUndo("filter", "");\n
      filterHidden = true;\n
    } else {\n
      var elem = selectedElements[0];\n
      if(filterHidden) {\n
        changeSelectedAttributeNoUndo("filter", \'url(#\' + elem.id + \'_blur)\');\n
      }\n
      if(svgedit.browser.isWebkit()) {\n
        elem.removeAttribute(\'filter\');\n
        elem.setAttribute(\'filter\', \'url(#\' + elem.id + \'_blur)\');\n
      }\n
      changeSelectedAttributeNoUndo("stdDeviation", val, [filter.firstChild]);\n
      canvas.setBlurOffsets(filter, val);\n
    }\n
  }\n
  \n
  function finishChange() {\n
    var bCmd = canvas.undoMgr.finishUndoableChange();\n
    cur_command.addSubCommand(bCmd);\n
    addCommandToHistory(cur_command);\n
    cur_command = null; \n
    filter = null;\n
  }\n
\n
  // Function: setBlurOffsets\n
  // Sets the x, y, with, height values of the filter element in order to\n
  // make the blur not be clipped. Removes them if not neeeded\n
  //\n
  // Parameters:\n
  // filter - The filter DOM element to update\n
  // stdDev - The standard deviation value on which to base the offset size\n
  canvas.setBlurOffsets = function(filter, stdDev) {\n
    if(stdDev > 3) {\n
      // TODO: Create algorithm here where size is based on expected blur\n
      assignAttributes(filter, {\n
        x: \'-50%\',\n
        y: \'-50%\',\n
        width: \'200%\',\n
        height: \'200%\'\n
      }, 100);\n
    } else {\n
      // Removing these attributes hides text in Chrome (see Issue 579)\n
      if(!svgedit.browser.isWebkit()) {\n
        filter.removeAttribute(\'x\');\n
        filter.removeAttribute(\'y\');\n
        filter.removeAttribute(\'width\');\n
        filter.removeAttribute(\'height\');\n
      }\n
    }\n
  }\n
\n
  // Function: setBlur \n
  // Adds/updates the blur filter to the selected element\n
  //\n
  // Parameters:\n
  // val - Float with the new stdDeviation blur value\n
  // complete - Boolean indicating whether or not the action should be completed (to add to the undo manager)\n
  canvas.setBlur = function(val, complete) {\n
    if(cur_command) {\n
      finishChange();\n
      return;\n
    }\n
  \n
    // Looks for associated blur, creates one if not found\n
    var elem = selectedElements[0];\n
    var elem_id = elem.id;\n
    filter = getElem(elem_id + \'_blur\');\n
    \n
    val -= 0;\n
    \n
    var batchCmd = new BatchCommand();\n
    \n
    // Blur found!\n
    if(filter) {\n
      if(val === 0) {\n
        filter = null;\n
      }\n
    } else {\n
      // Not found, so create\n
      var newblur = addSvgElementFromJson({ "element": "feGaussianBlur",\n
        "attr": {\n
          "in": \'SourceGraphic\',\n
          "stdDeviation": val\n
        }\n
      });\n
      \n
      filter = addSvgElementFromJson({ "element": "filter",\n
        "attr": {\n
          "id": elem_id + \'_blur\'\n
        }\n
      });\n
      \n
      filter.appendChild(newblur);\n
      findDefs().appendChild(filter);\n
      \n
      batchCmd.addSubCommand(new InsertElementCommand(filter));\n
    }\n
\n
    var changes = {filter: elem.getAttribute(\'filter\')};\n
    \n
    if(val === 0) {\n
      elem.removeAttribute("filter");\n
      batchCmd.addSubCommand(new ChangeElementCommand(elem, changes));\n
      return;\n
    } else {\n
      changeSelectedAttribute("filter", \'url(#\' + elem_id + \'_blur)\');\n
      \n
      batchCmd.addSubCommand(new ChangeElementCommand(elem, changes));\n
      \n
      canvas.setBlurOffsets(filter, val);\n
    }\n
    \n
    cur_command = batchCmd;\n
    canvas.undoMgr.beginUndoableChange("stdDeviation", [filter?filter.firstChild:null]);\n
    if(complete) {\n
      canvas.setBlurNoUndo(val);\n
      finishChange();\n
    }\n
  };\n
}());\n
\n
// Function: getBold\n
// Check whether selected element is bold or not\n
//\n
// Returns:\n
// Boolean indicating whether or not element is bold\n
this.getBold = function() {\n
  var selectedElems = selectedElements.filter(Boolean)\n
  var isBold = true\n
  selectedElems.forEach(function(el){\n
    if (el.getAttribute("font-weight") != "bold") isBold = false;\n
  });\n
  return isBold;\n
};\n
\n
// Function: setBold\n
// Make the selected element bold or normal\n
//\n
// Parameters:\n
// b - Boolean indicating bold (true) or normal (false)\n
this.setBold = function(b) {\n
  var selectedElems = selectedElements.filter(Boolean)\n
  selectedElems.forEach(function(selected){\n
    if (selected != null && selected.tagName  == "text") changeSelectedAttribute("font-weight", b ? "bold" : "normal");\n
  });\n
  if (!selectedElems[0].textContent)  textActions.setCursor();\n
};\n
\n
// Function: getItalic\n
// Check whether selected element is italic or not\n
//\n
// Returns:\n
// Boolean indicating whether or not element is italic\n
this.getItalic = function() {\n
  var selectedElems = selectedElements.filter(Boolean)\n
  var isItalic = true\n
  selectedElems.forEach(function(el){\n
    if (el.getAttribute("font-style") != "italic") isItalic = false;\n
  });\n
  return isItalic;\n
};\n
\n
// Function: setItalic\n
// Make the selected element italic or normal\n
//\n
// Parameters:\n
// b - Boolean indicating italic (true) or normal (false)\n
this.setItalic = function(i) {\n
  var selectedElems = selectedElements.filter(Boolean)\n
  selectedElems.forEach(function(selected){\n
    if (selected != null && selected.tagName  == "text") changeSelectedAttribute("font-style", i ? "italic" : "normal");\n
  });\n
  if (!selectedElems[0].textContent) textActions.setCursor();\n
};\n
\n
// Function: getFontFamily\n
// Returns the current font family\n
this.getFontFamily = function() {\n
  return cur_text.font_family;\n
};\n
\n
// Function: setFontFamily\n
// Set the new font family\n
//\n
// Parameters:\n
// val - String with the new font family\n
this.setFontFamily = function(val) {\n
  cur_text.font_family = val;\n
  changeSelectedAttribute("font-family", val);\n
  if(selectedElements[0] && !selectedElements[0].textContent) {\n
    textActions.setCursor();\n
  }\n
};\n
\n
\n
// Function: setFontColor\n
// Set the new font color\n
//\n
// Parameters:\n
// val - String with the new font color\n
this.setFontColor = function(val) {\n
  cur_text.fill = val;\n
  changeSelectedAttribute("fill", val);\n
};\n
\n
// Function: getFontColor\n
// Returns the current font color\n
this.getFontSize = function() {\n
  return cur_text.fill;\n
};\n
\n
// Function: getFontSize\n
// Returns the current font size\n
this.getFontSize = function() {\n
  return cur_text.font_size;\n
};\n
\n
// Function: setFontSize\n
// Applies the given font size to the selected element\n
//\n
// Parameters:\n
// val - Float with the new font size\n
this.setFontSize = function(val) {\n
  cur_text.font_size = val;\n
  changeSelectedAttribute("font-size", val);\n
  if(!selectedElements[0].textContent) {\n
    textActions.setCursor();\n
  }\n
};\n
\n
// Function: getText\n
// Returns the current text (textContent) of the selected element\n
this.getText = function() {\n
  var selected = selectedElements[0];\n
  if (selected == null) { return ""; }\n
  return selected.textContent;\n
};\n
\n
// Function: setTextContent\n
// Updates the text element with the given string\n
//\n
// Parameters:\n
// val - String with the new text\n
this.setTextContent = function(val) {\n
  changeSelectedAttribute("#text", val);\n
  textActions.init(val);\n
  textActions.setCursor();\n
};\n
\n
// Function: setImageURL\n
// Sets the new image URL for the selected image element. Updates its size if\n
// a new URL is given\n
// \n
// Parameters:\n
// val - String with the image URL/path\n
this.setImageURL = function(val) {\n
  var elem = selectedElements[0];\n
  if(!elem) return;\n
  \n
  var attrs = $(elem).attr([\'width\', \'height\']);\n
  var setsize = (!attrs.width || !attrs.height);\n
\n
  var cur_href = getHref(elem);\n
  \n
  // Do nothing if no URL change or size change\n
  if(cur_href !== val) {\n
    setsize = true;\n
  } else if(!setsize) return;\n
\n
  var batchCmd = new BatchCommand("Change Image URL");\n
\n
  setHref(elem, val);\n
  batchCmd.addSubCommand(new ChangeElementCommand(elem, {\n
    "#href": cur_href\n
  }));\n
\n
  if(setsize) {\n
    $(new Image()).load(function() {\n
      var changes = $(elem).attr([\'width\', \'height\']);\n
    \n
      $(elem).attr({\n
        width: this.width,\n
        height: this.height\n
      });\n
      \n
      selectorManager.requestSelector(elem).resize();\n
      \n
      batchCmd.addSubCommand(new ChangeElementCommand(elem, changes));\n
      addCommandToHistory(batchCmd);\n
      call("changed", [elem]);\n
    }).attr(\'src\',val);\n
  } else {\n
    addCommandToHistory(batchCmd);\n
  }\n
};\n
\n
// Function: setLinkURL\n
// Sets the new link URL for the selected anchor element.\n
// \n
// Parameters:\n
// val - String with the link URL/path\n
this.setLinkURL = function(val) {\n
  var elem = selectedElements[0];\n
  if(!elem) return;\n
  if(elem.tagName !== \'a\') {\n
    // See if parent is an anchor\n
    var parents_a = $(elem).parents(\'a\');\n
    if(parents_a.length) {\n
      elem = parents_a[0];\n
    } else {\n
      return;\n
    }\n
  }\n
  \n
  var cur_href = getHref(elem);\n
  \n
  if(cur_href === val) return;\n
  \n
  var batchCmd = new BatchCommand("Change Link URL");\n
\n
  setHref(elem, val);\n
  batchCmd.addSubCommand(new ChangeElementCommand(elem, {\n
    "#href": cur_href\n
  }));\n
\n
  addCommandToHistory(batchCmd);\n
};\n
\n
\n
// Function elementAreSame\n
// Checks if all the selected Elements are the same type\n
// \n
// Parameters:\n
// None\n
\n
this.elementsAreSame = function(elements) {\n
  if (!elements.length || elements[0] == null) return null\n
  else {\n
    var isSameElement = function(el) { \n
      if (el && selectedElements[0])\n
        return (el.nodeName == selectedElements[0].nodeName);\n
      else return null;\n
    }\n
    return selectedElements.every(isSameElement);\n
  }\n
}\n
\n
\n
// Function: setRectRadius\n
// Sets the rx & ry values to the selected rect element to change its corner radius\n
// \n
// Parameters:\n
// val - The new radius\n
this.setRectRadius = function(val) {\n
  if (canvas.elementsAreSame(selectedElements) && selectedElements[0].tagName == "rect") {\n
    var assign_rr = function(selected){\n
    var r = selected.getAttribute("rx");\n
      if (r != val) {\n
        selected.setAttribute("rx", val);\n
        selected.setAttribute("ry", val);\n
        addCommandToHistory(new ChangeElementCommand(selected, {"rx":r, "ry":r}, "Radius"));\n
        call("changed", [selected]);\n
      }\n
    }\n
    selectedElements.forEach(assign_rr)\n
  }\n
};\n
\n
// Function: makeHyperlink\n
// Wraps the selected element(s) in an anchor element or converts group to one\n
this.makeHyperlink = function(url) {\n
  canvas.groupSelectedElements(\'a\', url);\n
  \n
  // TODO: If element is a single "g", convert to "a"\n
  //  if(selectedElements.length > 1 && selectedElements[1]) {\n
\n
}\n
\n
// Function: removeHyperlink\n
this.removeHyperlink = function() {\n
  canvas.ungroupSelectedElement();\n
}\n
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
  pathActions.setSegType(new_type);\n
}\n
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
  if(elem == null) {\n
    var elems = selectedElements;\n
    $.each(selectedElements, function(i, elem) {\n
      if(elem) canvas.convertToPath(elem);\n
    });\n
    return;\n
  }\n
  \n
  if(!getBBox) {\n
    var batchCmd = new BatchCommand("Convert element to Path");\n
  }\n
  \n
  var attrs = getBBox?{}:{\n
    "fill": cur_shape.fill,\n
    "fill-opacity": cur_shape.fill_opacity,\n
    "stroke": cur_shape.stroke,\n
    "stroke-width": cur_shape.stroke_width,\n
    "stroke-dasharray": cur_shape.stroke_dasharray,\n
    "stroke-linejoin": cur_shape.stroke_linejoin,\n
    "stroke-linecap": cur_shape.stroke_linecap,\n
    "stroke-opacity": cur_shape.stroke_opacity,\n
    "opacity": cur_shape.opacity,\n
    "visibility":"hidden"\n
  };\n
  \n
  // any attribute on the element not covered by the above\n
  // TODO: make this list global so that we can properly maintain it\n
  // TODO: what about @transform, @clip-rule, @fill-rule, etc?\n
  $.each([\'marker-start\', \'marker-end\', \'marker-mid\', \'filter\', \'clip-path\'], function() {\n
    if (elem.getAttribute(this)) {\n
      attrs[this] = elem.getAttribute(this);\n
    }\n
  });\n
  \n
  var path = addSvgElementFromJson({\n
    "element": "path",\n
    "attr": attrs\n
  });\n
  \n
  var eltrans = elem.getAttribute("transform");\n
  if(eltrans) {\n
    path.setAttribute("transform",eltrans);\n
  }\n
  \n
  var id = elem.id;\n
  var parent = elem.parentNode;\n
  if(elem.nextSibling) {\n
    parent.insertBefore(path, elem);\n
  } else {\n
    parent.appendChild(path);\n
  }\n
  \n
  var d = \'\';\n
  \n
  var joinSegs = function(segs) {\n
    $.each(segs, function(j, seg) {\n
      var l = seg[0], pts = seg[1];\n
      d += l;\n
      for(var i=0; i < pts.length; i+=2) {\n
        d += (pts[i] +\',\'+pts[i+1]) + \' \';\n
      }\n
    });\n
  }\n
\n
  // Possibly the cubed root of 6, but 1.81 works best\n
  var num = 1.81;\n
\n
  switch (elem.tagName) {\n
  case \'ellipse\':\n
  case \'circle\':\n
    var a = $(elem).attr([\'rx\', \'ry\', \'cx\', \'cy\']);\n
    var cx = a.cx, cy = a.cy, rx = a.rx, ry = a.ry;\n
    if(elem.tagName == \'circle\') {\n
      rx = ry = $(elem).attr(\'r\');\n
    }\n
  \n
    joinSegs([\n
      [\'M\',[(cx-rx),(cy)]],\n
      [\'C\',[(cx-rx),(cy-ry/num), (cx-rx/num),(cy-ry), (cx),(cy-ry)]],\n
      [\'C\',[(cx+rx/num),(cy-ry), (cx+rx),(cy-ry/num), (cx+rx),(cy)]],\n
      [\'C\',[(cx+rx),(cy+ry/num), (cx+rx/num),(cy+ry), (cx),(cy+ry)]],\n
      [\'C\',[(cx-rx/num),(cy+ry), (cx-rx),(cy+ry/num), (cx-rx),(cy)]],\n
      [\'Z\',[]]\n
    ]);\n
    break;\n
  case \'path\':\n
    d = elem.getAttribute(\'d\');\n
    break;\n
  case \'line\':\n
    var a = $(elem).attr(["x1", "y1", "x2", "y2"]);\n
    d = "M"+a.x1+","+a.y1+"L"+a.x2+","+a.y2;\n
    break;\n
  case \'polyline\':\n
  case \'polygon\':\n
    d = "M" + elem.getAttribute(\'points\');\n
    break;\n
  case \'rect\':\n
    var r = $(elem).attr([\'rx\', \'ry\']);\n
    var rx = r.rx, ry = r.ry;\n
    var b = elem.getBBox();\n
    var x = b.x, y = b.y, w = b.width, h = b.height;\n
    var num = 4-num; // Why? Because!\n
    if(!rx && !ry) {\n
      // Regular rect\n
      joinSegs([\n
        [\'M\',[x, y]],\n
        [\'L\',[x+w, y]],\n
        [\'L\',[x+w, y+h]],\n
        [\'L\',[x, y+h]],\n
        [\'L\',[x, y]],\n
        [\'Z\',[]]\n
      ]);\n
    } else {\n
      if (!ry) ry = rx\n
      joinSegs([\n
        [\'M\',[x, y+ry]],\n
        [\'C\',[x,y+ry/num, x+rx/num,y, x+rx,y]],\n
        [\'L\',[x+w-rx, y]],\n
        [\'C\',[x+w-rx/num,y, x+w,y+ry/num, x+w,y+ry]],\n
        [\'L\',[x+w, y+h-ry]],\n
        [\'C\',[x+w, y+h-ry/num, x+w-rx/num,y+h, x+w-rx,y+h]],\n
        [\'L\',[x+rx, y+h]],\n
        [\'C\',[x+rx/num, y+h, x,y+h-ry/num, x,y+h-ry]],\n
        [\'L\',[x, y+ry]],\n
        [\'Z\',[]]\n
      ]);\n
    }\n
    break;\n
  default:\n
    path.parentNode.removeChild(path);\n
    break;\n
  }\n
  \n
  if(d) {\n
    path.setAttribute(\'d\',d);\n
  }\n
  \n
  if(!getBBox) {\n
    // Replace the current element with the converted one\n
    \n
    // Reorient if it has a matrix\n
    if(eltrans) {\n
      var tlist = getTransformList(path);\n
      if(hasMatrixTransform(tlist)) {\n
        pathActions.resetOrientation(path);\n
      }\n
    }\n
    \n
    var nextSibling = elem.nextSibling;\n
    batchCmd.addSubCommand(new RemoveElementCommand(elem, nextSibling, parent));\n
    batchCmd.addSubCommand(new InsertElementCommand(path));\n
\n
    clearSelection();\n
    elem.parentNode.removeChild(elem)\n
    path.setAttribute(\'id\', id);\n
    path.removeAttribute("visibility");\n
    addToSelection([path], true);\n
    \n
    addCommandToHistory(batchCmd);\n
    \n
  } else {\n
    // Get the correct BBox of the new path, then discard it\n
    pathActions.resetOrientation(path);\n
    var bb = false;\n
    try {\n
      bb = path.getBBox();\n
    } catch(e) {\n
      // Firefox fails\n
    }\n
    path.parentNode.removeChild(path);\n
    return bb;\n
  }\n
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
var changeSelectedAttributeNoUndo = this.changeSelectedAttributeNoUndo = function(attr, newValue, elems) {\n
    if(current_mode == \'pathedit\') {\n
      // Editing node\n
      pathActions.moveNode(attr, newValue);\n
    }\n
    var elems = elems || selectedElements;\n
    var i = elems.length;\n
    var no_xy_elems = [\'g\', \'polyline\', \'path\'];\n
    var good_g_attrs = [\'transform\', \'opacity\', \'filter\'];\n
    while (i--) {\n
      var elem = elems[i];\n
      if (elem == null) continue;\n
      // Go into "select" mode for text changes\n
      if(current_mode === "textedit" && attr !== "#text" && elem.textContent.length) {\n
        textActions.toSelectMode(elem);\n
      }\n
\n
      // Set x,y vals on elements that don\'t have them\n
      if((attr === \'x\' || attr === \'y\') && no_xy_elems.indexOf(elem.tagName) >= 0) {\n
        var bbox = getStrokedBBox([elem]);\n
        var diff_x = attr === \'x\' ? newValue - bbox.x : 0;\n
        var diff_y = attr === \'y\' ? newValue - bbox.y : 0;\n
        canvas.moveSelectedElements(diff_x*current_zoom, diff_y*current_zoom, true);\n
        continue;\n
      }\n
\n
      var oldval = attr === "#text" ? elem.textContent : elem.getAttribute(attr);\n
      if (oldval == null)  oldval = "";\n
      if (oldval !== String(newValue)) {\n
        if (attr == "#text") {\n
          var old_w = svgedit.utilities.getBBox(elem).width;\n
          elem.textContent = newValue;\n
\n
        } else if (attr == "#href") {\n
          setHref(elem, newValue);\n
        }\n
        else elem.setAttribute(attr, newValue);\n
\n
        // Timeout needed for Opera & Firefox\n
        // codedread: it is now possible for this function to be called with elements\n
        // that are not in the selectedElements array, we need to only request a\n
        // selector if the element is in that array\n
        if (selectedElements.indexOf(elem) >= 0) {\n
          setTimeout(function() {\n
            // Due to element replacement, this element may no longer\n
            // be part of the DOM\n
            if(!elem.parentNode) return;\n
            selectorManager.requestSelector(elem).resize();\n
          },0);\n
        }\n
        // if this element was rotated, and we changed the position of this element\n
        // we need to update the rotational transform attribute \n
        var angle = getRotationAngle(elem);\n
        if (angle != 0 && attr != "transform") {\n
          var tlist = getTransformList(elem);\n
          var n = tlist.numberOfItems;\n
          while (n--) {\n
            var xform = tlist.getItem(n);\n
            if (xform.type == 4) {\n
              // remove old rotate\n
              tlist.removeItem(n);\n
\n
              var box = svgedit.utilities.getBBox(elem);\n
              var center = transformPoint(box.x+box.width/2, box.y+box.height/2, transformListToTransform(tlist).matrix);\n
              var cx = center.x,\n
                cy = center.y;\n
              var newrot = svgroot.createSVGTransform();\n
              newrot.setRotate(angle, cx, cy);\n
              tlist.insertItemBefore(newrot, n);\n
              break;\n
            }\n
          }\n
        }\n
      } // if oldValue != newValue\n
    } // for each elem\n
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
  var elems = elems || selectedElements;\n
  canvas.undoMgr.beginUndoableChange(attr, elems);\n
  var i = elems.length;\n
\n
  changeSelectedAttributeNoUndo(attr, val, elems);\n
\n
  var batchCmd = canvas.undoMgr.finishUndoableChange();\n
  if (!batchCmd.isEmpty()) { \n
    addCommandToHistory(batchCmd);\n
  }\n
};\n
\n
// Function: deleteSelectedElements\n
// Removes all selected elements from the DOM and adds the change to the \n
// history stack\n
this.deleteSelectedElements = function() {\n
  var batchCmd = new BatchCommand("Delete Elements");\n
  var len = selectedElements.length;\n
  var selectedCopy = []; //selectedElements is being deleted\n
  for (var i = 0; i < len; ++i) {\n
    var selected = selectedElements[i];\n
    if (selected == null) break;\n
\n
    var parent = selected.parentNode;\n
    var t = selected;\n
    \n
    // this will unselect the element and remove the selectedOutline\n
    selectorManager.releaseSelector(t);\n
    \n
    // Remove the path if present.\n
    svgedit.path.removePath_(t.id);\n
    \n
    // Get the parent if it\'s a single-child anchor\n
    if(parent.tagName === \'a\' && parent.childNodes.length === 1) {\n
      t = parent;\n
      parent = parent.parentNode;\n
    }\n
    \n
    var nextSibling = t.nextSibling;\n
    var elem = parent.removeChild(t);\n
    selectedCopy.push(selected); //for the copy\n
    selectedElements[i] = null;\n
    batchCmd.addSubCommand(new RemoveElementCommand(elem, nextSibling, parent));\n
  }\n
  if (!batchCmd.isEmpty()) addCommandToHistory(batchCmd);\n
  call("changed", selectedCopy);\n
  clearSelection();\n
};\n
\n
// Function: cutSelectedElements\n
// Removes all selected elements from the DOM and adds the change to the \n
// history stack. Remembers removed elements on the clipboard\n
\n
// TODO: Combine similar code with deleteSelectedElements\n
this.cutSelectedElements = function() {\n
  var batchCmd = new BatchCommand("Cut Elements");\n
  var len = selectedElements.length;\n
  var selectedCopy = []; //selectedElements is being deleted\n
  for (var i = 0; i < len; ++i) {\n
    var selected = selectedElements[i];\n
    if (selected == null) break;\n
\n
    var parent = selected.parentNode;\n
    var t = selected;\n
\n
    // this will unselect the element and remove the selectedOutline\n
    selectorManager.releaseSelector(t);\n
\n
    // Remove the path if present.\n
    svgedit.path.removePath_(t.id);\n
\n
    var nextSibling = t.nextSibling;\n
    var elem = parent.removeChild(t);\n
    selectedCopy.push(selected); //for the copy\n
    selectedElements[i] = null;\n
    batchCmd.addSubCommand(new RemoveElementCommand(elem, nextSibling, parent));\n
  }\n
  if (!batchCmd.isEmpty()) addCommandToHistory(batchCmd);\n
  call("changed", selectedCopy);\n
  clearSelection();\n
  \n
  canvas.clipBoard = selectedCopy;\n
};\n
\n
// Function: copySelectedElements\n
// Remembers the current selected elements on the clipboard\n
this.copySelectedElements = function() {\n
  canvas.clipBoard = $.merge([], selectedElements);\n
};\n
\n
this.pasteElements = function(type, x, y) {\n
  var cb = canvas.clipBoard;\n
  var len = cb.length;\n
  if(!len) return;\n
  \n
  var pasted = [];\n
  var batchCmd = new BatchCommand(\'Paste elements\');\n
  \n
  // Move elements to lastClickPoint\n
\n
  while (len--) {\n
    var elem = cb[len];\n
    if(!elem) continue;\n
    var copy = copyElem(elem);\n
\n
    // See if elem with elem ID is in the DOM already\n
    if(!getElem(elem.id)) copy.id = elem.id;\n
    pasted.push(copy);\n
    (current_group || getCurrentDrawing().getCurrentLayer()).appendChild(copy);\n
    batchCmd.addSubCommand(new InsertElementCommand(copy));\n
  }\n
  svgCanvas.clearSelection();\n
  setTimeout(function(){selectOnly(pasted)},100);\n
  \n
\n
  \n
  addCommandToHistory(batchCmd);\n
  call("changed", pasted);\n
}\n
\n
// Function: groupSelectedElements\n
// Wraps all the selected elements in a group (g) element\n
\n
// Parameters: \n
// type - type of element to group into, defaults to <g>\n
this.groupSelectedElements = function(type) {\n
  if(!type) type = \'g\';\n
  var cmd_str = \'\';\n
  \n
  switch ( type ) {\n
    case "a":\n
      cmd_str = "Make hyperlink";\n
      var url = \'\';\n
      if(arguments.length > 1) {\n
        url = arguments[1];\n
      }\n
      break;\n
    default:\n
      type = \'g\';\n
      cmd_str = "Group Elements";\n
      break;\n
  }\n
  \n
  var batchCmd = new BatchCommand(cmd_str);\n
  \n
  // create and insert the group element\n
  var g = addSvgElementFromJson({\n
              "element": type,\n
              "attr": {\n
                "id": getNextId()\n
              }\n
            });\n
  if(type === \'a\') {\n
    setHref(g, url);\n
  }\n
  batchCmd.addSubCommand(new InsertElementCommand(g));\n
  \n
  // now move all children into the group\n
  var i = selectedElements.length;\n
  while (i--) {\n
    var elem = selectedElements[i];\n
    if (elem == null) continue;\n
    \n
    if (elem.parentNode.tagName === \'a\' && elem.parentNode.childNodes.length === 1) {\n
      elem = elem.parentNode;\n
    }\n
    \n
    var oldNextSibling = elem.nextSibling;\n
    var oldParent = elem.parentNode;\n
    g.appendChild(elem);\n
    batchCmd.addSubCommand(new MoveElementCommand(elem, oldNextSibling, oldParent));      \n
  }\n
  if (!batchCmd.isEmpty()) addCommandToHistory(batchCmd);\n
  \n
  // update selection\n
  selectOnly([g], true);\n
};\n
\n
\n
// Function: pushGroupProperties\n
// Pushes all appropriate parent group properties down to its children, then\n
// removes them from the group\n
var pushGroupProperties = this.pushGroupProperties = function(g, undoable) {\n
\n
  var children = g.childNodes;\n
  var len = children.length;\n
  var xform = g.getAttribute("transform");\n
\n
  var glist = getTransformList(g);\n
  var m = transformListToTransform(glist).matrix;\n
  \n
  var batchCmd = new BatchCommand("Push group properties");\n
\n
  // TODO: get all fill/stroke properties from the group that we are about to destroy\n
  // "fill", "fill-opacity", "fill-rule", "stroke", "stroke-dasharray", "stroke-dashoffset", \n
  // "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", \n
  // "stroke-width"\n
  // and then for each child, if they do not have the attribute (or the value is \'inherit\')\n
  // then set the child\'s attribute\n
  \n
  var i = 0;\n
  var gangle = getRotationAngle(g);\n
  \n
  var gattrs = $(g).attr([\'filter\', \'opacity\']);\n
  var gfilter, gblur;\n
  \n
  for(var i = 0; i < len; i++) {\n
    var elem = children[i];\n
    \n
    if(elem.nodeType !== 1) continue;\n
    \n
    if(gattrs.opacity !== null && gattrs.opacity !== 1) {\n
      var c_opac = elem.getAttribute(\'opacity\') || 1;\n
      var new_opac = Math.round((elem.getAttribute(\'opacity\') || 1) * gattrs.opacity * 100)/100;\n
      changeSelectedAttribute(\'opacity\', new_opac, [elem]);\n
    }\n
\n
    if(gattrs.filter) {\n
      var cblur = this.getBlur(elem);\n
      var orig_cblur = cblur;\n
      if(!gblur) gblur = this.getBlur(g);\n
      if(cblur) {\n
        // Is this formula correct?\n
        cblur = (gblur-0) + (cblur-0);\n
      } else if(cblur === 0) {\n
        cblur = gblur;\n
      }\n
      \n
      // If child has no current filter, get group\'s filter or clone it.\n
      if(!orig_cblur) {\n
        // Set group\'s filter to use first child\'s ID\n
        if(!gfilter) {\n
          gfilter = getRefElem(gattrs.filter);\n
        } else {\n
          // Clone the group\'s filter\n
          gfilter = copyElem(gfilter);\n
          findDefs().appendChild(gfilter);\n
        }\n
      } else {\n
        gfilter = getRefElem(elem.getAttribute(\'filter\'));\n
      }\n
\n
      // Change this in future for different filters\n
      var suffix = (gfilter.firstChild.tagName === \'feGaussianBlur\')?\'blur\':\'filter\'; \n
      gfilter.id = elem.id + \'_\' + suffix;\n
      changeSelectedAttribute(\'filter\', \'url(#\' + gfilter.id + \')\', [elem]);\n
      \n
      // Update blur value \n
      if(cblur) {\n
        changeSelectedAttribute(\'stdDeviation\', cblur, [gfilter.firstChild]);\n
        canvas.setBlurOffsets(gfilter, cblur);\n
      }\n
    }\n
    \n
    var chtlist = getTransformList(elem);\n
\n
    // Don\'t process gradient transforms\n
    if(~elem.tagName.indexOf(\'Gradient\')) chtlist = null;\n
    \n
    // Hopefully not a problem to add this. Necessary for elements like <desc/>\n
    if(!chtlist) continue;\n
    \n
    // Apparently <defs> can get get a transformlist, but we don\'t want it to have one!\n
    if(elem.tagName === \'defs\') continue;\n
    \n
    if (glist.numberOfItems) {\n
      // TODO: if the group\'s transform is just a rotate, we can always transfer the\n
      // rotate() down to the children (collapsing consecutive rotates and factoring\n
      // out any translates)\n
      if (gangle && glist.numberOfItems == 1) {\n
        // [Rg] [Rc] [Mc]\n
        // we want [Tr] [Rc2] [Mc] where:\n
        //  - [Rc2] is at the child\'s current center but has the \n
        //    sum of the group and child\'s rotation angles\n
        //  - [Tr] is the equivalent translation that this child \n
        //    undergoes if the group wasn\'t there\n
        \n
        // [Tr] = [Rg] [Rc] [Rc2_inv]\n
        \n
        // get group\'s rotation matrix (Rg)\n
        var rgm = glist.getItem(0).matrix;\n
        \n
        // get child\'s rotation matrix (Rc)\n
        var rcm = svgroot.createSVGMatrix();\n
        var cangle = getRotationAngle(elem);\n
        if (cangle) {\n
          rcm = chtlist.getItem(0).matrix;\n
        }\n
        \n
        // get child\'s old center of rotation\n
        var cbox = svgedit.utilities.getBBox(elem);\n
        var ceqm = transformListToTransform(chtlist).matrix;\n
        var coldc = transformPoint(cbox.x+cbox.width/2, cbox.y+cbox.height/2,ceqm);\n
        \n
        // sum group and child\'s angles\n
        var sangle = gangle + cangle;\n
        \n
        // get child\'s rotation at the old center (Rc2_inv)\n
        var r2 = svgroot.createSVGTransform();\n
        r2.setRotate(sangle, coldc.x, coldc.y);\n
        \n
        // calculate equivalent translate\n
        var trm = matrixMultiply(rgm, rcm, r2.matrix.inverse());\n
        \n
        // set up tlist\n
        if (cangle) {\n
          chtlist.removeItem(0);\n
        }\n
        \n
        if (sangle) {\n
          if(chtlist.numberOfItems) {\n
            chtlist.insertItemBefore(r2, 0);\n
          } else {\n
            chtlist.appendItem(r2);\n
          }\n
        }\n
\n
        if (trm.e || trm.f) {\n
          var tr = svgroot.createSVGTransform();\n
          tr.setTranslate(trm.e, trm.f);\n
          if(chtlist.numberOfItems) {\n
            chtlist.insertItemBefore(tr, 0);\n
          } else {\n
            chtlist.appendItem(tr);\n
          }\n
        }\n
      }\n
      else { // more complicated than just a rotate\n
      \n
        // transfer the group\'s transform down to each child and then\n
        // call recalculateDimensions()       \n
        var oldxform = elem.getAttribute("transform");\n
        var changes = {};\n
        changes["transform"] = oldxform ? oldxform : "";\n
\n
        var newxform = svgroot.createSVGTransform();\n
\n
        // [ gm ] [ chm ] = [ chm ] [ gm\' ]\n
        // [ gm\' ] = [ chm_inv ] [ gm ] [ chm ]\n
        var chm = transformListToTransform(chtlist).matrix,\n
          chm_inv = chm.inverse();\n
        var gm = matrixMultiply( chm_inv, m, chm );\n
        newxform.setMatrix(gm);\n
        chtlist.appendItem(newxform);\n
      }\n
      var cmd = recalculateDimensions(elem);\n
      if(cmd) batchCmd.addSubCommand(cmd);\n
    }\n
  }\n
\n
  \n
  // remove transform and make it undo-able\n
  if (xform) {\n
    var changes = {};\n
    changes["transform"] = xform;\n
    g.setAttribute("transform", "");\n
    g.removeAttribute("transform");       \n
    batchCmd.addSubCommand(new ChangeElementCommand(g, changes));\n
  }\n
  \n
  if (undoable && !batchCmd.isEmpty()) {\n
    return batchCmd;\n
  }\n
}\n
\n
\n
// Function: ungroupSelectedElement\n
// Unwraps all the elements in a selected group (g) element. This requires\n
// significant recalculations to apply group\'s transforms, etc to its children\n
this.ungroupSelectedElement = function() {\n
  var g = selectedElements[0];\n
  if($(g).data(\'gsvg\') || $(g).data(\'symbol\')) {\n
    // Is svg, so actually convert to group\n
\n
    convertToGroup(g);\n
    return;\n
  } else if(g.tagName === \'use\') {\n
    // Somehow doesn\'t have data set, so retrieve\n
    var symbol = getElem(getHref(g).substr(1));\n
    $(g).data(\'symbol\', symbol).data(\'ref\', symbol);\n
    convertToGroup(g);\n
    return;\n
  }\n
  var parents_a = $(g).parents(\'a\');\n
  if(parents_a.length) {\n
    g = parents_a[0];\n
  }\n
  \n
  // Look for parent "a"\n
  if (g.tagName === "g" || g.tagName === "a") {\n
    \n
    var batchCmd = new BatchCommand("Ungroup Elements");\n
    var cmd = pushGroupProperties(g, true);\n
    if(cmd) batchCmd.addSubCommand(cmd);\n
    \n
    var parent = g.parentNode;\n
    var anchor = g.nextSibling;\n
    var children = new Array(g.childNodes.length);\n
    \n
    var i = 0;\n
    \n
    while (g.firstChild) {\n
      var elem = g.firstChild;\n
      var oldNextSibling = elem.nextSibling;\n
      var oldParent = elem.parentNode;\n
      \n
      // Remove child title elements\n
      if(elem.tagName === \'title\') {\n
        var nextSibling = elem.nextSibling;\n
        batchCmd.addSubCommand(new RemoveElementCommand(elem, nextSibling, oldParent));\n
        oldParent.removeChild(elem);\n
        continue;\n
      }\n
      \n
      children[i++] = elem = parent.insertBefore(elem, anchor);\n
      batchCmd.addSubCommand(new MoveElementCommand(elem, oldNextSibling, oldParent));\n
    }\n
\n
    // remove the group from the selection      \n
    clearSelection();\n
    \n
    // delete the group element (but make undo-able)\n
    var gNextSibling = g.nextSibling;\n
    g = parent.removeChild(g);\n
    batchCmd.addSubCommand(new RemoveElementCommand(g, gNextSibling, parent));\n
\n
    if (!batchCmd.isEmpty()) addCommandToHistory(batchCmd);\n
    \n
    // update selection\n
    addToSelection(children);\n
  }\n
};\n
\n
// Function: moveToTopSelectedElement\n
// Repositions the selected element to the bottom in the DOM to appear on top of\n
// other elements\n
this.moveToTopSelectedElement = function() {\n
  var selected = selectedElements.filter(Boolean).reverse();\n
  var batchCmd = new BatchCommand("Move to top");\n
  selected.forEach(function(element){\n
    var t = element;\n
    var oldParent = t.parentNode;\n
    var oldNextSibling = t.nextSibling;\n
    t = t.parentNode.appendChild(t);\n
    // If the element actually moved position, add the command and fire the changed\n
    // event handler.\n
    if (oldNextSibling != t.nextSibling) {\n
      batchCmd.addSubCommand(new MoveElementCommand(t, oldNextSibling, oldParent, "top"));\n
      call("changed", [t]);\n
    }\n
    if (!batchCmd.isEmpty()) addCommandToHistory(batchCmd);\n
  })\n
};\n
\n
// Function: moveToBottomSelectedElement\n
// Repositions the selected element to the top in the DOM to appear under \n
// other elements\n
this.moveToBottomSelectedElement = function() {\n
  var selected = selectedElements.filter(Boolean).reverse();\n
  var batchCmd = new BatchCommand("Move to top");\n
  selected.forEach(function(element){\n
    var t = element;\n
    var oldParent = t.parentNode;\n
    var oldNextSibling = t.nextSibling;\n
    var firstChild = t.parentNode.firstChild;\n
    if (firstChild.tagName == \'title\') {\n
      firstChild = firstChild.nextSibling;\n
    }\n
    // This can probably be removed, as the defs should not ever apppear\n
    // inside a layer group\n
    if (firstChild.tagName == \'defs\') {\n
      firstChild = firstChild.nextSibling;\n
    }\n
    t = t.parentNode.insertBefore(t, firstChild);\n
    // If the element actually moved position, add the command and fire the changed\n
    // event handler.\n
    if (oldNextSibling != t.nextSibling) {\n
      batchCmd.addSubCommand(new MoveElementCommand(t, oldNextSibling, oldParent, "bottom"));\n
      call("changed", [t]);\n
    }\n
  })\n
  if (!batchCmd.isEmpty()) addCommandToHistory(batchCmd);\n
};\n
\n
// Function: moveUpDownSelected\n
// Moves the select element up or down the stack, based on the visibly\n
// intersecting elements\n
//\n
// Parameters: \n
// dir - String that\'s either \'Up\' or \'Down\'\n
this.moveUpDownSelected = function(dir) {\n
  var selected = selectedElements.filter(Boolean);\n
  if(dir == \'Down\') selected.reverse();\n
  var batchCmd = new BatchCommand("Move " + dir);\n
  selected.forEach(function(selected){\n
    curBBoxes = [];\n
    var closest, found_cur;\n
    // jQuery sorts this list\n
    var list = $(getIntersectionList(getStrokedBBox([selected]))).toArray();\n
    if(dir == \'Down\') list.reverse();\n
\n
    $.each(list, function() {\n
      if(!found_cur) {\n
        if(this == selected) {\n
          found_cur = true;\n
        }\n
        return;\n
      }\n
      closest = this;\n
      return false;\n
    });\n
    if(!closest) return;\n
    \n
    var t = selected;\n
    var oldParent = t.parentNode;\n
    var oldNextSibling = t.nextSibling;\n
    $(closest)[dir == \'Down\'?\'before\':\'after\'](t);\n
    // If the element actually moved position, add the command and fire the changed\n
    // event handler.\n
    if (oldNextSibling != t.nextSibling) {\n
      batchCmd.addSubCommand(new MoveElementCommand(t, oldNextSibling, oldParent, "Move " + dir));\n
      call("changed", [t]);\n
    }\n
  });\n
  if (!batchCmd.isEmpty()) addCommandToHistory(batchCmd);\n
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
  // if undoable is not sent, default to true\n
  // if single values, scale them to the zoom\n
  if (dx.constructor != Array) {\n
    dx /= current_zoom;\n
    dy /= current_zoom;\n
  }\n
  var undoable = undoable || true;\n
  var batchCmd = new BatchCommand("position");\n
  var i = selectedElements.length;\n
  while (i--) {\n
    var selected = selectedElements[i];\n
    if (selected != null) {\n
//      if (i==0)\n
//        selectedBBoxes[0] = svgedit.utilities.getBBox(selected);\n
      \n
//      var b = {};\n
//      for(var j in selectedBBoxes[i]) b[j] = selectedBBoxes[i][j];\n
//      selectedBBoxes[i] = b;\n
      \n
      var xform = svgroot.createSVGTransform();\n
      var tlist = getTransformList(selected);\n
      \n
      // dx and dy could be arrays\n
      if (dx.constructor == Array) {\n
//        if (i==0) {\n
//          selectedBBoxes[0].x += dx[0];\n
//          selectedBBoxes[0].y += dy[0];\n
//        }\n
        xform.setTranslate(dx[i],dy[i]);\n
      } else {\n
//        if (i==0) {\n
//          selectedBBoxes[0].x += dx;\n
//          selectedBBoxes[0].y += dy;\n
//        }\n
        xform.setTranslate(dx,dy);\n
      }\n
\n
      if(tlist.numberOfItems) {\n
        tlist.insertItemBefore(xform, 0);\n
      } else {\n
        tlist.appendItem(xform);\n
      }\n
      \n
      var cmd = recalculateDimensions(selected);\n
      if (cmd) {\n
        batchCmd.addSubCommand(cmd);\n
      }\n
      \n
      selectorManager.requestSelector(selected).resize();\n
    }\n
  }\n
  if (!batchCmd.isEmpty()) {\n
    if (undoable)\n
      addCommandToHistory(batchCmd);\n
    call("changed", selectedElements);\n
    return batchCmd;\n
  }\n
};\n
\n
// Function: cloneSelectedElements\n
// Create deep DOM copies (clones) of all selected elements and move them slightly \n
// from their originals\n
this.cloneSelectedElements = function(x,y, drag) {\n
  var batchCmd = new BatchCommand("Clone Elements");\n
  // find all the elements selected (stop at first null)\n
  var len = selectedElements.length;\n
  for (var i = 0; i < len; ++i) {\n
    var elem = selectedElements[i];\n
    if (elem == null) break;\n
  }\n
  // use slice to quickly get the subset of elements we need\n
  var copiedElements = selectedElements.slice(0,i);\n
  this.clearSelection(true);\n
  // note that we loop in the reverse way because of the way elements are added\n
  // to the selectedElements array (top-first)\n
  var i = copiedElements.length;\n
  clones = []\n
  while (i--) {\n
    // clone each element and replace it within copiedElements\n
    var elem = copiedElements[i] \n
    var clone = copyElem(copiedElements[i]);\n
    var parent = (current_group || getCurrentDrawing().getCurrentLayer())\n
    if (drag) {\n
      //removed the dragged transform until that moment\n
      tlist = getTransformList(clone)\n
          tlist.removeItem(drag)\n
      recalculateDimensions(clone)\n
      parent.insertBefore(clone, elem);\n
    }\n
    else {\n
      parent.appendChild(clone);\n
    }\n
    clones.push(clone)\n
    batchCmd.addSubCommand(new InsertElementCommand(clone));\n
  }\n
  \n
  if (!batchCmd.isEmpty()) {\n
    addToSelection(copiedElements.reverse()); // Need to reverse for correct selection-adding\n
    if (!drag) this.moveSelectedElements(x,y,false);\n
    addCommandToHistory(batchCmd);\n
  }\n
  return clones\n
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
  var bboxes = [], angles = [];\n
  var minx = Number.MAX_VALUE, maxx = Number.MIN_VALUE, miny = Number.MAX_VALUE, maxy = Number.MIN_VALUE;\n
  var curwidth = Number.MIN_VALUE, curheight = Number.MIN_VALUE;\n
  var len = selectedElements.length;\n
  if (!len) return;\n
  for (var i = 0; i < len; ++i) {\n
    if (selectedElements[i] == null) break;\n
    var elem = selectedElements[i];\n
    bboxes[i] = getStrokedBBox([elem]);\n
    \n
    // now bbox is axis-aligned and handles rotation\n
    switch (relative_to) {\n
      case \'smallest\':\n
        if ( (type == \'l\' || type == \'c\' || type == \'r\') && (curwidth == Number.MIN_VALUE || curwidth > bboxes[i].width) ||\n
           (type == \'t\' || type == \'m\' || type == \'b\') && (curheight == Number.MIN_VALUE || curheight > bboxes[i].height) ) {\n
          minx = bboxes[i].x;\n
          miny = bboxes[i].y;\n
          maxx = bboxes[i].x + bboxes[i].width;\n
          maxy = bboxes[i].y + bboxes[i].height;\n
          curwidth = bboxes[i].width;\n
          curheight = bboxes[i].height;\n
        }\n
        break;\n
      case \'largest\':\n
        if ( (type == \'l\' || type == \'c\' || type == \'r\') && (curwidth == Number.MIN_VALUE || curwidth < bboxes[i].width) ||\n
           (type == \'t\' || type == \'m\' || type == \'b\') && (curheight == Number.MIN_VALUE || curheight < bboxes[i].height) ) {\n
          minx = bboxes[i].x;\n
          miny = bboxes[i].y;\n
          maxx = bboxes[i].x + bboxes[i].width;\n
          maxy = bboxes[i].y + bboxes[i].height;\n
          curwidth = bboxes[i].width;\n
          curheight = bboxes[i].height;\n
        }\n
        break;\n
      default: // \'selected\'\n
        if (bboxes[i].x < minx) minx = bboxes[i].x;\n
        if (bboxes[i].y < miny) miny = bboxes[i].y;\n
        if (bboxes[i].x + bboxes[i].width > maxx) maxx = bboxes[i].x + bboxes[i].width;\n
        if (bboxes[i].y + bboxes[i].height > maxy) maxy = bboxes[i].y + bboxes[i].height;\n
        break;\n
    }\n
  } // loop for each element to find the bbox and adjust min/max\n
\n
  if (relative_to == \'page\') {\n
    minx = 0;\n
    miny = 0;\n
    maxx = canvas.contentW;\n
    maxy = canvas.contentH;\n
  }\n
\n
  var dx = new Array(len);\n
  var dy = new Array(len);\n
  for (var i = 0; i < len; ++i) {\n
    if (selectedElements[i] == null) break;\n
    var elem = selectedElements[i];\n
    var bbox = bboxes[i];\n
    dx[i] = 0;\n
    dy[i] = 0;\n
    switch (type) {\n
      case \'l\': // left (horizontal)\n
        dx[i] = minx - bbox.x;\n
        break;\n
      case \'c\': // center (horizontal)\n
        dx[i] = (minx+maxx)/2 - (bbox.x + bbox.width/2);\n
        break;\n
      case \'r\': // right (horizontal)\n
        dx[i] = maxx - (bbox.x + bbox.width);\n
        break;\n
      case \'t\': // top (vertical)\n
        dy[i] = miny - bbox.y;\n
        break;\n
      case \'m\': // middle (vertical)\n
        dy[i] = (miny+maxy)/2 - (bbox.y + bbox.height/2);\n
        break;\n
      case \'b\': // bottom (vertical)\n
        dy[i] = maxy - (bbox.y + bbox.height);\n
        break;\n
    }\n
  }\n
  this.moveSelectedElements(dx,dy);\n
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
  svgroot.setAttribute("width", w);\n
  svgroot.setAttribute("height", h);\n
  var bg = $(\'#canvasBackground\')[0];\n
  var old_x = svgcontent.getAttribute(\'x\');\n
  var old_y = svgcontent.getAttribute(\'y\');\n
  var x = (w/2 - this.contentW*current_zoom/2);\n
  var y = (h/2 - this.contentH*current_zoom/2);\n
\n
  assignAttributes(svgcontent, {\n
    width: this.contentW*current_zoom,\n
    height: this.contentH*current_zoom,\n
    \'x\': x,\n
    \'y\': y,\n
    "viewBox" : "0 0 " + this.contentW + " " + this.contentH\n
  });\n
  \n
  assignAttributes(bg, {\n
    width: svgcontent.getAttribute(\'width\'),\n
    height: svgcontent.getAttribute(\'height\'),\n
    x: x,\n
    y: y\n
  });\n
\n
  var bg_img = getElem(\'background_image\');\n
  if (bg_img) {\n
    assignAttributes(bg_img, {\n
      \'width\': \'100%\',\n
      \'height\': \'100%\'\n
    });\n
  }\n
  \n
  selectorManager.selectorParentGroup.setAttribute("transform","translate(" + x + "," + y + ")");\n
  \n
  return {x:x, y:y, old_x:old_x, old_y:old_y, d_x:x - old_x, d_y:y - old_y};\n
}\n
\n
// Function: setBackground\n
// Set the background of the editor (NOT the actual document)\n
//\n
// Parameters:\n
// color - String with fill color to apply\n
// url - URL or path to image to use\n
this.setBackground = function(color, url) {\n
  var bg =  getElem(\'canvasBackground\');\n
  var border = $(bg).find(\'rect\')[0];\n
  var bg_img = getElem(\'background_image\');\n
  border.setAttribute(\'fill\',color);\n
  if(url) {\n
    if(!bg_img) {\n
      bg_img = svgdoc.createElementNS(svgns, "image");\n
      assignAttributes(bg_img, {\n
        \'id\': \'background_image\',\n
        \'width\': \'100%\',\n
        \'height\': \'100%\',\n
        \'preserveAspectRatio\': \'xMinYMin\',\n
        \'style\':\'pointer-events:none\'\n
      });\n
    }\n
    setHref(bg_img, url);\n
    bg.appendChild(bg_img);\n
  } else if(bg_img) {\n
    bg_img.parentNode.removeChild(bg_img);\n
  }\n
}\n
\n
// Function: cycleElement\n
// Select the next/previous element within the current layer\n
//\n
// Parameters:\n
// next - Boolean where true = next and false = previous element\n
this.cycleElement = function(next) {\n
  var cur_elem = selectedElements[0];\n
  var elem = false;\n
  var all_elems = getVisibleElements(current_group || getCurrentDrawing().getCurrentLayer());\n
  if(!all_elems.length) return;\n
  if (cur_elem == null) {\n
    var num = next?all_elems.length-1:0;\n
    elem = all_elems[num];\n
  } else {\n
    var i = all_elems.length;\n
    while(i--) {\n
      if(all_elems[i] == cur_elem) {\n
        var num = next?i-1:i+1;\n
        if(num >= all_elems.length) {\n
          num = 0;\n
        } else if(num < 0) {\n
          num = all_elems.length-1;\n
        } \n
        elem = all_elems[num];\n
        break;\n
      } \n
    }\n
  }   \n
  selectOnly([elem], true);\n
  call("selected", selectedElements);\n
}\n
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
  var obj = {\n
    addCommandToHistory: addCommandToHistory,\n
    setGradient: setGradient,\n
    addSvgElementFromJson: addSvgElementFromJson,\n
    assignAttributes: assignAttributes,\n
    BatchCommand: BatchCommand,\n
    call: call,\n
    ChangeElementCommand: ChangeElementCommand,\n
    copyElem: copyElem,\n
    ffClone: ffClone,\n
    findDefs: findDefs,\n
    findDuplicateGradient: findDuplicateGradient,\n
    getElem: getElem,\n
    getId: getId,\n
    getIntersectionList: getIntersectionList,\n
    getMouseTarget: getMouseTarget,\n
    getNextId: getNextId,\n
    getPathBBox: getPathBBox,\n
    getUrlFromAttr: getUrlFromAttr,\n
    hasMatrixTransform: hasMatrixTransform,\n
    identifyLayers: identifyLayers,\n
    InsertElementCommand: InsertElementCommand,\n
    isIdentity: svgedit.math.isIdentity,\n
    logMatrix: logMatrix,\n
    matrixMultiply: matrixMultiply,\n
    MoveElementCommand: MoveElementCommand,\n
    preventClickDefault: preventClickDefault,\n
    recalculateAllSelectedDimensions: recalculateAllSelectedDimensions,\n
    recalculateDimensions: recalculateDimensions,\n
    remapElement: remapElement,\n
    RemoveElementCommand: RemoveElementCommand,\n
    removeUnusedDefElems: removeUnusedDefElems,\n
    round: round,\n
    runExtensions: runExtensions,\n
    sanitizeSvg: sanitizeSvg,\n
    SVGEditTransformList: svgedit.transformlist.SVGTransformList,\n
    toString: toString,\n
    transformBox: svgedit.math.transformBox,\n
    transformListToTransform: transformListToTransform,\n
    transformPoint: transformPoint,\n
    walkTree: svgedit.utilities.walkTree\n
  }\n
  return obj;\n
};\n
\n
}\n


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
