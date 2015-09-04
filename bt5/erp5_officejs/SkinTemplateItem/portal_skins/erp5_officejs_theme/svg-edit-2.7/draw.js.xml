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
            <value> <string>ts40515059.46</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>draw.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgedit*/\n
/*jslint vars: true, eqeq: true, todo: true*/\n
/**\n
 * Package: svgedit.draw\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2011 Jeff Schiller\n
 */\n
\n
// Dependencies:\n
// 1) jQuery\n
// 2) browser.js\n
// 3) svgutils.js\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.draw) {\n
\tsvgedit.draw = {};\n
}\n
// alias\n
var NS = svgedit.NS;\n
\n
var visElems = \'a,circle,ellipse,foreignObject,g,image,line,path,polygon,polyline,rect,svg,text,tspan,use\'.split(\',\');\n
\n
var RandomizeModes = {\n
\tLET_DOCUMENT_DECIDE: 0,\n
\tALWAYS_RANDOMIZE: 1,\n
\tNEVER_RANDOMIZE: 2\n
};\n
var randomize_ids = RandomizeModes.LET_DOCUMENT_DECIDE;\n
\n
/**\n
 * This class encapsulates the concept of a layer in the drawing\n
 * @param {String} name - Layer name\n
 * @param {SVGGElement} child - Layer SVG group.\n
 */\n
svgedit.draw.Layer = function(name, group) {\n
\tthis.name_ = name;\n
\tthis.group_ = group;\n
};\n
\n
/**\n
 * @returns {string} The layer name\n
 */\n
svgedit.draw.Layer.prototype.getName = function() {\n
\treturn this.name_;\n
};\n
\n
/**\n
 * @returns {SVGGElement} The layer SVG group\n
 */\n
svgedit.draw.Layer.prototype.getGroup = function() {\n
\treturn this.group_;\n
};\n
\n
\n
/**\n
 * Called to ensure that drawings will or will not have randomized ids.\n
 * The currentDrawing will have its nonce set if it doesn\'t already.\n
 * @param {boolean} enableRandomization - flag indicating if documents should have randomized ids\n
 * @param {svgedit.draw.Drawing} currentDrawing\n
 */\n
svgedit.draw.randomizeIds = function(enableRandomization, currentDrawing) {\n
\trandomize_ids = enableRandomization === false ?\n
\t\tRandomizeModes.NEVER_RANDOMIZE :\n
\t\tRandomizeModes.ALWAYS_RANDOMIZE;\n
\n
\tif (randomize_ids == RandomizeModes.ALWAYS_RANDOMIZE && !currentDrawing.getNonce()) {\n
\t\tcurrentDrawing.setNonce(Math.floor(Math.random() * 100001));\n
\t} else if (randomize_ids == RandomizeModes.NEVER_RANDOMIZE && currentDrawing.getNonce()) {\n
\t\tcurrentDrawing.clearNonce();\n
\t}\n
};\n
\n
/**\n
 * This class encapsulates the concept of a SVG-edit drawing\n
 * @param {SVGSVGElement} svgElem - The SVG DOM Element that this JS object\n
 *     encapsulates.  If the svgElem has a se:nonce attribute on it, then\n
 *     IDs will use the nonce as they are generated.\n
 * @param {String=svg_} [opt_idPrefix] - The ID prefix to use.\n
 */\n
svgedit.draw.Drawing = function(svgElem, opt_idPrefix) {\n
\tif (!svgElem || !svgElem.tagName || !svgElem.namespaceURI ||\n
\t\tsvgElem.tagName != \'svg\' || svgElem.namespaceURI != NS.SVG) {\n
\t\tthrow "Error: svgedit.draw.Drawing instance initialized without a <svg> element";\n
\t}\n
\n
\t/**\n
\t * The SVG DOM Element that represents this drawing.\n
\t * @type {SVGSVGElement}\n
\t */\n
\tthis.svgElem_ = svgElem;\n
\t\n
\t/**\n
\t * The latest object number used in this drawing.\n
\t * @type {number}\n
\t */\n
\tthis.obj_num = 0;\n
\t\n
\t/**\n
\t * The prefix to prepend to each element id in the drawing.\n
\t * @type {String}\n
\t */\n
\tthis.idPrefix = opt_idPrefix || "svg_";\n
\t\n
\t/**\n
\t * An array of released element ids to immediately reuse.\n
\t * @type {Array.<number>}\n
\t */\n
\tthis.releasedNums = [];\n
\n
\t/**\n
\t * The z-ordered array of tuples containing layer names and <g> elements.\n
\t * The first layer is the one at the bottom of the rendering.\n
\t * TODO: Turn this into an Array.<Layer>\n
\t * @type {Array.<Array.<String, SVGGElement>>}\n
\t */\n
\tthis.all_layers = [];\n
\n
\t/**\n
\t * The current layer being used.\n
\t * TODO: Make this a {Layer}.\n
\t * @type {SVGGElement}\n
\t */\n
\tthis.current_layer = null;\n
\n
\t/**\n
\t * The nonce to use to uniquely identify elements across drawings.\n
\t * @type {!String}\n
\t */\n
\tthis.nonce_ = \'\';\n
\tvar n = this.svgElem_.getAttributeNS(NS.SE, \'nonce\');\n
\t// If already set in the DOM, use the nonce throughout the document\n
\t// else, if randomizeIds(true) has been called, create and set the nonce.\n
\tif (!!n && randomize_ids != RandomizeModes.NEVER_RANDOMIZE) {\n
\t\tthis.nonce_ = n;\n
\t} else if (randomize_ids == RandomizeModes.ALWAYS_RANDOMIZE) {\n
\t\tthis.setNonce(Math.floor(Math.random() * 100001));\n
\t}\n
};\n
\n
/**\n
 * @param {string} id Element ID to retrieve\n
 * @returns {Element} SVG element within the root SVGSVGElement\n
*/\n
svgedit.draw.Drawing.prototype.getElem_ = function (id) {\n
\tif (this.svgElem_.querySelector) {\n
\t\t// querySelector lookup\n
\t\treturn this.svgElem_.querySelector(\'#\' + id);\n
\t}\n
\t// jQuery lookup: twice as slow as xpath in FF\n
\treturn $(this.svgElem_).find(\'[id=\' + id + \']\')[0];\n
};\n
\n
/**\n
 * @returns {SVGSVGElement}\n
 */\n
svgedit.draw.Drawing.prototype.getSvgElem = function () {\n
\treturn this.svgElem_;\n
};\n
\n
/**\n
 * @returns {!string|number} The previously set nonce\n
 */\n
svgedit.draw.Drawing.prototype.getNonce = function() {\n
\treturn this.nonce_;\n
};\n
\n
/**\n
 * @param {!string|number} n The nonce to set\n
 */\n
svgedit.draw.Drawing.prototype.setNonce = function(n) {\n
\tthis.svgElem_.setAttributeNS(NS.XMLNS, \'xmlns:se\', NS.SE);\n
\tthis.svgElem_.setAttributeNS(NS.SE, \'se:nonce\', n);\n
\tthis.nonce_ = n;\n
};\n
\n
/**\n
 * Clears any previously set nonce\n
 */\n
svgedit.draw.Drawing.prototype.clearNonce = function () {\n
\t// We deliberately leave any se:nonce attributes alone,\n
\t// we just don\'t use it to randomize ids.\n
\tthis.nonce_ = \'\';\n
};\n
\n
/**\n
 * Returns the latest object id as a string.\n
 * @return {String} The latest object Id.\n
 */\n
svgedit.draw.Drawing.prototype.getId = function () {\n
\treturn this.nonce_ ?\n
\t\tthis.idPrefix + this.nonce_ + \'_\' + this.obj_num :\n
\t\tthis.idPrefix + this.obj_num;\n
};\n
\n
/**\n
 * Returns the next object Id as a string.\n
 * @return {String} The next object Id to use.\n
 */\n
svgedit.draw.Drawing.prototype.getNextId = function () {\n
\tvar oldObjNum = this.obj_num;\n
\tvar restoreOldObjNum = false;\n
\n
\t// If there are any released numbers in the release stack, \n
\t// use the last one instead of the next obj_num.\n
\t// We need to temporarily use obj_num as that is what getId() depends on.\n
\tif (this.releasedNums.length > 0) {\n
\t\tthis.obj_num = this.releasedNums.pop();\n
\t\trestoreOldObjNum = true;\n
\t} else {\n
\t\t// If we are not using a released id, then increment the obj_num.\n
\t\tthis.obj_num++;\n
\t}\n
\n
\t// Ensure the ID does not exist.\n
\tvar id = this.getId();\n
\twhile (this.getElem_(id)) {\n
\t\tif (restoreOldObjNum) {\n
\t\t\tthis.obj_num = oldObjNum;\n
\t\t\trestoreOldObjNum = false;\n
\t\t}\n
\t\tthis.obj_num++;\n
\t\tid = this.getId();\n
\t}\n
\t// Restore the old object number if required.\n
\tif (restoreOldObjNum) {\n
\t\tthis.obj_num = oldObjNum;\n
\t}\n
\treturn id;\n
};\n
\n
/**\n
 * Releases the object Id, letting it be used as the next id in getNextId().\n
 * This method DOES NOT remove any elements from the DOM, it is expected\n
 * that client code will do this.\n
 * @param {string} id - The id to release.\n
 * @returns {boolean} True if the id was valid to be released, false otherwise.\n
*/\n
svgedit.draw.Drawing.prototype.releaseId = function (id) {\n
\t// confirm if this is a valid id for this Document, else return false\n
\tvar front = this.idPrefix + (this.nonce_ ? this.nonce_ + \'_\' : \'\');\n
\tif (typeof id !== \'string\' || id.indexOf(front) !== 0) {\n
\t\treturn false;\n
\t}\n
\t// extract the obj_num of this id\n
\tvar num = parseInt(id.substr(front.length), 10);\n
\n
\t// if we didn\'t get a positive number or we already released this number\n
\t// then return false.\n
\tif (typeof num !== \'number\' || num <= 0 || this.releasedNums.indexOf(num) != -1) {\n
\t\treturn false;\n
\t}\n
\t\n
\t// push the released number into the released queue\n
\tthis.releasedNums.push(num);\n
\n
\treturn true;\n
};\n
\n
/**\n
 * Returns the number of layers in the current drawing.\n
 * @returns {integer} The number of layers in the current drawing.\n
*/\n
svgedit.draw.Drawing.prototype.getNumLayers = function() {\n
\treturn this.all_layers.length;\n
};\n
\n
/**\n
 * Check if layer with given name already exists\n
 * @param {string} name - The layer name to check\n
*/\n
svgedit.draw.Drawing.prototype.hasLayer = function (name) {\n
\tvar i;\n
\tfor (i = 0; i < this.getNumLayers(); i++) {\n
\t\tif(this.all_layers[i][0] == name) {return true;}\n
\t}\n
\treturn false;\n
};\n
\n
\n
/**\n
 * Returns the name of the ith layer. If the index is out of range, an empty string is returned.\n
 * @param {integer} i - The zero-based index of the layer you are querying.\n
 * @returns {string} The name of the ith layer (or the empty string if none found)\n
*/\n
svgedit.draw.Drawing.prototype.getLayerName = function (i) {\n
\tif (i >= 0 && i < this.getNumLayers()) {\n
\t\treturn this.all_layers[i][0];\n
\t}\n
\treturn \'\';\n
};\n
\n
/**\n
 * @returns {SVGGElement} The SVGGElement representing the current layer.\n
 */\n
svgedit.draw.Drawing.prototype.getCurrentLayer = function() {\n
\treturn this.current_layer;\n
};\n
\n
/**\n
 * Returns the name of the currently selected layer. If an error occurs, an empty string \n
 * is returned.\n
 * @returns The name of the currently active layer (or the empty string if none found).\n
*/\n
svgedit.draw.Drawing.prototype.getCurrentLayerName = function () {\n
\tvar i;\n
\tfor (i = 0; i < this.getNumLayers(); ++i) {\n
\t\tif (this.all_layers[i][1] == this.current_layer) {\n
\t\t\treturn this.getLayerName(i);\n
\t\t}\n
\t}\n
\treturn \'\';\n
};\n
\n
/**\n
 * Sets the current layer. If the name is not a valid layer name, then this\n
 * function returns false. Otherwise it returns true. This is not an\n
 * undo-able action.\n
 * @param {string} name - The name of the layer you want to switch to.\n
 * @returns {boolean} true if the current layer was switched, otherwise false\n
 */\n
svgedit.draw.Drawing.prototype.setCurrentLayer = function(name) {\n
\tvar i;\n
\tfor (i = 0; i < this.getNumLayers(); ++i) {\n
\t\tif (name == this.getLayerName(i)) {\n
\t\t\tif (this.current_layer != this.all_layers[i][1]) {\n
\t\t\t\tthis.current_layer.setAttribute("style", "pointer-events:none");\n
\t\t\t\tthis.current_layer = this.all_layers[i][1];\n
\t\t\t\tthis.current_layer.setAttribute("style", "pointer-events:all");\n
\t\t\t}\n
\t\t\treturn true;\n
\t\t}\n
\t}\n
\treturn false;\n
};\n
\n
\n
/**\n
 * Deletes the current layer from the drawing and then clears the selection.\n
 * This function then calls the \'changed\' handler.  This is an undoable action.\n
 * @returns {SVGGElement} The SVGGElement of the layer removed or null.\n
 */\n
svgedit.draw.Drawing.prototype.deleteCurrentLayer = function() {\n
\tif (this.current_layer && this.getNumLayers() > 1) {\n
\t\t// actually delete from the DOM and return it\n
\t\tvar parent = this.current_layer.parentNode;\n
\t\tvar nextSibling = this.current_layer.nextSibling;\n
\t\tvar oldLayerGroup = parent.removeChild(this.current_layer);\n
\t\tthis.identifyLayers();\n
\t\treturn oldLayerGroup;\n
\t}\n
\treturn null;\n
};\n
\n
/**\n
 * Updates layer system and sets the current layer to the\n
 * top-most layer (last <g> child of this drawing).\n
*/\n
svgedit.draw.Drawing.prototype.identifyLayers = function() {\n
\tthis.all_layers = [];\n
\tvar numchildren = this.svgElem_.childNodes.length;\n
\t// loop through all children of SVG element\n
\tvar orphans = [], layernames = [];\n
\tvar a_layer = null;\n
\tvar childgroups = false;\n
\tvar i;\n
\tfor (i = 0; i < numchildren; ++i) {\n
\t\tvar child = this.svgElem_.childNodes.item(i);\n
\t\t// for each g, find its layer name\n
\t\tif (child && child.nodeType == 1) {\n
\t\t\tif (child.tagName == "g") {\n
\t\t\t\tchildgroups = true;\n
\t\t\t\tvar name = $("title", child).text();\n
\n
\t\t\t\t// Hack for Opera 10.60\n
\t\t\t\tif(!name && svgedit.browser.isOpera() && child.querySelectorAll) {\n
\t\t\t\t\tname = $(child.querySelectorAll(\'title\')).text();\n
\t\t\t\t}\n
\n
\t\t\t\t// store layer and name in global variable\n
\t\t\t\tif (name) {\n
\t\t\t\t\tlayernames.push(name);\n
\t\t\t\t\tthis.all_layers.push( [name, child] );\n
\t\t\t\t\ta_layer = child;\n
\t\t\t\t\tsvgedit.utilities.walkTree(child, function(e){e.setAttribute("style", "pointer-events:inherit");});\n
\t\t\t\t\ta_layer.setAttribute("style", "pointer-events:none");\n
\t\t\t\t}\n
\t\t\t\t// if group did not have a name, it is an orphan\n
\t\t\t\telse {\n
\t\t\t\t\torphans.push(child);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t// if child has is "visible" (i.e. not a <title> or <defs> element), then it is an orphan\n
\t\t\telse if(~visElems.indexOf(child.nodeName)) {\n
\t\t\t\tvar bb = svgedit.utilities.getBBox(child);\n
\t\t\t\torphans.push(child);\n
\t\t\t}\n
\t\t}\n
\t}\n
\t\n
\t// create a new layer and add all the orphans to it\n
\tvar svgdoc = this.svgElem_.ownerDocument;\n
\tif (orphans.length > 0 || !childgroups) {\n
\t\ti = 1;\n
\t\t// TODO(codedread): What about internationalization of "Layer"?\n
\t\twhile (layernames.indexOf(("Layer " + i)) >= 0) { i++; }\n
\t\tvar newname = "Layer " + i;\n
\t\ta_layer = svgdoc.createElementNS(NS.SVG, "g");\n
\t\tvar layer_title = svgdoc.createElementNS(NS.SVG, "title");\n
\t\tlayer_title.textContent = newname;\n
\t\ta_layer.appendChild(layer_title);\n
\t\tvar j;\n
\t\tfor (j = 0; j < orphans.length; ++j) {\n
\t\t\ta_layer.appendChild(orphans[j]);\n
\t\t}\n
\t\tthis.svgElem_.appendChild(a_layer);\n
\t\tthis.all_layers.push( [newname, a_layer] );\n
\t}\n
\tsvgedit.utilities.walkTree(a_layer, function(e){e.setAttribute("style", "pointer-events:inherit");});\n
\tthis.current_layer = a_layer;\n
\tthis.current_layer.setAttribute("style", "pointer-events:all");\n
};\n
\n
/**\n
 * Creates a new top-level layer in the drawing with the given name and \n
 * sets the current layer to it.\n
 * @param {string} name - The given name\n
 * @returns {SVGGElement} The SVGGElement of the new layer, which is\n
 * also the current layer of this drawing.\n
*/\n
svgedit.draw.Drawing.prototype.createLayer = function(name) {\n
\tvar svgdoc = this.svgElem_.ownerDocument;\n
\tvar new_layer = svgdoc.createElementNS(NS.SVG, "g");\n
\tvar layer_title = svgdoc.createElementNS(NS.SVG, "title");\n
\tlayer_title.textContent = name;\n
\tnew_layer.appendChild(layer_title);\n
\tthis.svgElem_.appendChild(new_layer);\n
\tthis.identifyLayers();\n
\treturn new_layer;\n
};\n
\n
/**\n
 * Returns whether the layer is visible.  If the layer name is not valid,\n
 * then this function returns false.\n
 * @param {string} layername - The name of the layer which you want to query.\n
 * @returns {boolean} The visibility state of the layer, or false if the layer name was invalid.\n
*/\n
svgedit.draw.Drawing.prototype.getLayerVisibility = function(layername) {\n
\t// find the layer\n
\tvar layer = null;\n
\tvar i;\n
\tfor (i = 0; i < this.getNumLayers(); ++i) {\n
\t\tif (this.getLayerName(i) == layername) {\n
\t\t\tlayer = this.all_layers[i][1];\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\tif (!layer) {return false;}\n
\treturn (layer.getAttribute(\'display\') !== \'none\');\n
};\n
\n
/**\n
 * Sets the visibility of the layer. If the layer name is not valid, this\n
 * function returns false, otherwise it returns true. This is an\n
 * undo-able action.\n
 * @param {string} layername - The name of the layer to change the visibility\n
 * @param {boolean} bVisible - Whether the layer should be visible\n
 * @returns {?SVGGElement} The SVGGElement representing the layer if the\n
 *   layername was valid, otherwise null.\n
*/\n
svgedit.draw.Drawing.prototype.setLayerVisibility = function(layername, bVisible) {\n
\tif (typeof bVisible !== \'boolean\') {\n
\t\treturn null;\n
\t}\n
\t// find the layer\n
\tvar layer = null;\n
\tvar i;\n
\tfor (i = 0; i < this.getNumLayers(); ++i) {\n
\t\tif (this.getLayerName(i) == layername) {\n
\t\t\tlayer = this.all_layers[i][1];\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\tif (!layer) {return null;}\n
\t\n
\tvar oldDisplay = layer.getAttribute("display");\n
\tif (!oldDisplay) {oldDisplay = "inline";}\n
\tlayer.setAttribute("display", bVisible ? "inline" : "none");\n
\treturn layer;\n
};\n
\n
\n
/**\n
 * Returns the opacity of the given layer.  If the input name is not a layer, null is returned.\n
 * @param {string} layername - name of the layer on which to get the opacity\n
 * @returns {?number} The opacity value of the given layer.  This will be a value between 0.0 and 1.0, or null\n
 * if layername is not a valid layer\n
*/\n
svgedit.draw.Drawing.prototype.getLayerOpacity = function(layername) {\n
\tvar i;\n
\tfor (i = 0; i < this.getNumLayers(); ++i) {\n
\t\tif (this.getLayerName(i) == layername) {\n
\t\t\tvar g = this.all_layers[i][1];\n
\t\t\tvar opacity = g.getAttribute(\'opacity\');\n
\t\t\tif (!opacity) {\n
\t\t\t\topacity = \'1.0\';\n
\t\t\t}\n
\t\t\treturn parseFloat(opacity);\n
\t\t}\n
\t}\n
\treturn null;\n
};\n
\n
/**\n
 * Sets the opacity of the given layer.  If the input name is not a layer,\n
 * nothing happens. If opacity is not a value between 0.0 and 1.0, then\n
 * nothing happens.\n
 * @param {string} layername - Name of the layer on which to set the opacity\n
 * @param {number} opacity - A float value in the range 0.0-1.0\n
*/\n
svgedit.draw.Drawing.prototype.setLayerOpacity = function(layername, opacity) {\n
\tif (typeof opacity !== \'number\' || opacity < 0.0 || opacity > 1.0) {\n
\t\treturn;\n
\t}\n
\tvar i;\n
\tfor (i = 0; i < this.getNumLayers(); ++i) {\n
\t\tif (this.getLayerName(i) == layername) {\n
\t\t\tvar g = this.all_layers[i][1];\n
\t\t\tg.setAttribute("opacity", opacity);\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
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
            <value> <int>16042</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
