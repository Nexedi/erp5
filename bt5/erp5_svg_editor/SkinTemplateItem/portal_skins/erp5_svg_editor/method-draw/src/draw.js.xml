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
            <value> <string>ts52852083.62</string> </value>
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

/**\n
 * Package: svgedit.draw\n
 *\n
 * Licensed under the Apache License, Version 2\n
 *\n
 * Copyright(c) 2011 Jeff Schiller\n
 */\n
\n
// Dependencies:\n
// 1) jQuery\n
// 2) browser.js\n
// 3) svgutils.js\n
\n
var svgedit = svgedit || {};\n
\n
(function() {\n
\n
if (!svgedit.draw) {\n
  svgedit.draw = {};\n
}\n
\n
var svg_ns = "http://www.w3.org/2000/svg";\n
var se_ns = "http://svg-edit.googlecode.com";\n
var xmlns_ns = "http://www.w3.org/2000/xmlns/";\n
\n
var visElems = \'a,circle,ellipse,foreignObject,g,image,line,path,polygon,polyline,rect,svg,text,tspan,use\';\n
var visElems_arr = visElems.split(\',\');\n
\n
var RandomizeModes = {\n
  LET_DOCUMENT_DECIDE: 0,\n
  ALWAYS_RANDOMIZE: 1,\n
  NEVER_RANDOMIZE: 2\n
};\n
var randomize_ids = RandomizeModes.LET_DOCUMENT_DECIDE;\n
\n
/**\n
 * This class encapsulates the concept of a layer in the drawing\n
 * @param name {String} Layer name\n
 * @param child {SVGGElement} Layer SVG group.\n
 */\n
svgedit.draw.Layer = function(name, group) {\n
  this.name_ = name;\n
  this.group_ = group;\n
};\n
\n
svgedit.draw.Layer.prototype.getName = function() {\n
  return this.name_;\n
};\n
\n
svgedit.draw.Layer.prototype.getGroup = function() {\n
  return this.group_;\n
};\n
\n
\n
// Called to ensure that drawings will or will not have randomized ids.\n
// The current_drawing will have its nonce set if it doesn\'t already.\n
// \n
// Params:\n
// enableRandomization - flag indicating if documents should have randomized ids\n
svgedit.draw.randomizeIds = function(enableRandomization, current_drawing) {\n
  randomize_ids = enableRandomization == false ?\n
    RandomizeModes.NEVER_RANDOMIZE :\n
    RandomizeModes.ALWAYS_RANDOMIZE;\n
\n
  if (randomize_ids == RandomizeModes.ALWAYS_RANDOMIZE && !current_drawing.getNonce()) {\n
    current_drawing.setNonce(Math.floor(Math.random() * 100001));\n
  } else if (randomize_ids == RandomizeModes.NEVER_RANDOMIZE && current_drawing.getNonce()) {\n
    current_drawing.clearNonce();\n
  }\n
};\n
\n
/**\n
 * This class encapsulates the concept of a SVG-edit drawing\n
 *\n
 * @param svgElem {SVGSVGElement} The SVG DOM Element that this JS object\n
 *     encapsulates.  If the svgElem has a se:nonce attribute on it, then\n
 *     IDs will use the nonce as they are generated.\n
 * @param opt_idPrefix {String} The ID prefix to use.  Defaults to "svg_"\n
 *     if not specified.\n
 */\n
svgedit.draw.Drawing = function(svgElem, opt_idPrefix) {\n
  if (!svgElem || !svgElem.tagName || !svgElem.namespaceURI ||\n
    svgElem.tagName != \'svg\' || svgElem.namespaceURI != svg_ns) {\n
    throw "Error: svgedit.draw.Drawing instance initialized without a <svg> element";\n
  }\n
\n
  /**\n
   * The SVG DOM Element that represents this drawing.\n
   * @type {SVGSVGElement}\n
   */\n
  this.svgElem_ = svgElem;\n
  \n
  /**\n
   * The latest object number used in this drawing.\n
   * @type {number}\n
   */\n
  this.obj_num = 0;\n
  \n
  /**\n
   * The prefix to prepend to each element id in the drawing.\n
   * @type {String}\n
   */\n
  this.idPrefix = opt_idPrefix || "svg_";\n
  \n
  /**\n
   * An array of released element ids to immediately reuse.\n
   * @type {Array.<number>}\n
   */\n
  this.releasedNums = [];\n
\n
  /**\n
   * The z-ordered array of tuples containing layer names and <g> elements.\n
   * The first layer is the one at the bottom of the rendering.\n
   * TODO: Turn this into an Array.<Layer>\n
   * @type {Array.<Array.<String, SVGGElement>>}\n
   */\n
  this.all_layers = [];\n
\n
  /**\n
   * The current layer being used.\n
   * TODO: Make this a {Layer}.\n
   * @type {SVGGElement}\n
   */\n
  this.current_layer = null;\n
\n
  /**\n
   * The nonce to use to uniquely identify elements across drawings.\n
   * @type {!String}\n
   */\n
  this.nonce_ = "";\n
  var n = this.svgElem_.getAttributeNS(se_ns, \'nonce\');\n
  // If already set in the DOM, use the nonce throughout the document\n
  // else, if randomizeIds(true) has been called, create and set the nonce.\n
  if (!!n && randomize_ids != RandomizeModes.NEVER_RANDOMIZE) {\n
    this.nonce_ = n;\n
  } else if (randomize_ids == RandomizeModes.ALWAYS_RANDOMIZE) {\n
    this.setNonce(Math.floor(Math.random() * 100001));\n
  }\n
};\n
\n
svgedit.draw.Drawing.prototype.getElem_ = function(id) {\n
  if(this.svgElem_.querySelector) {\n
    // querySelector lookup\n
    return this.svgElem_.querySelector(\'#\'+id);\n
  } else {\n
    // jQuery lookup: twice as slow as xpath in FF\n
    return $(this.svgElem_).find(\'[id=\' + id + \']\')[0];\n
  }\n
};\n
\n
svgedit.draw.Drawing.prototype.getSvgElem = function() {\n
  return this.svgElem_;\n
};\n
\n
svgedit.draw.Drawing.prototype.getNonce = function() {\n
  return this.nonce_;\n
};\n
\n
svgedit.draw.Drawing.prototype.setNonce = function(n) {\n
  this.svgElem_.setAttributeNS(xmlns_ns, \'xmlns:se\', se_ns);\n
  this.svgElem_.setAttributeNS(se_ns, \'se:nonce\', n);\n
  this.nonce_ = n;\n
};\n
\n
svgedit.draw.Drawing.prototype.clearNonce = function() {\n
  // We deliberately leave any se:nonce attributes alone,\n
  // we just don\'t use it to randomize ids.\n
  this.nonce_ = "";\n
};\n
\n
/**\n
 * Returns the latest object id as a string.\n
 * @return {String} The latest object Id.\n
 */\n
svgedit.draw.Drawing.prototype.getId = function() {\n
  return this.nonce_ ?\n
    this.idPrefix + this.nonce_ +\'_\' + this.obj_num :\n
    this.idPrefix + this.obj_num;\n
};\n
\n
/**\n
 * Returns the next object Id as a string.\n
 * @return {String} The next object Id to use.\n
 */\n
svgedit.draw.Drawing.prototype.getNextId = function() {\n
  var oldObjNum = this.obj_num;\n
  var restoreOldObjNum = false;\n
\n
  // If there are any released numbers in the release stack, \n
  // use the last one instead of the next obj_num.\n
  // We need to temporarily use obj_num as that is what getId() depends on.\n
  if (this.releasedNums.length > 0) {\n
    this.obj_num = this.releasedNums.pop();\n
    restoreOldObjNum = true;\n
  } else {\n
    // If we are not using a released id, then increment the obj_num.\n
    this.obj_num++;\n
  }\n
\n
  // Ensure the ID does not exist.\n
  var id = this.getId();\n
  while (this.getElem_(id)) {\n
    if (restoreOldObjNum) {\n
      this.obj_num = oldObjNum;\n
      restoreOldObjNum = false;\n
    }\n
    this.obj_num++;\n
    id = this.getId();\n
  }\n
  // Restore the old object number if required.\n
  if (restoreOldObjNum) {\n
    this.obj_num = oldObjNum;\n
  }\n
  return id;\n
};\n
\n
// Function: svgedit.draw.Drawing.releaseId\n
// Releases the object Id, letting it be used as the next id in getNextId().\n
// This method DOES NOT remove any elements from the DOM, it is expected\n
// that client code will do this.\n
//\n
// Parameters:\n
// id - The id to release.\n
//\n
// Returns:\n
// True if the id was valid to be released, false otherwise.\n
svgedit.draw.Drawing.prototype.releaseId = function(id) {\n
  // confirm if this is a valid id for this Document, else return false\n
  var front = this.idPrefix + (this.nonce_ ? this.nonce_ +\'_\' : \'\');\n
  if (typeof id != typeof \'\' || id.indexOf(front) != 0) {\n
    return false;\n
  }\n
  // extract the obj_num of this id\n
  var num = parseInt(id.substr(front.length));\n
\n
  // if we didn\'t get a positive number or we already released this number\n
  // then return false.\n
  if (typeof num != typeof 1 || num <= 0 || this.releasedNums.indexOf(num) != -1) {\n
    return false;\n
  }\n
  \n
  // push the released number into the released queue\n
  this.releasedNums.push(num);\n
\n
  return true;\n
};\n
\n
// Function: svgedit.draw.Drawing.getNumLayers\n
// Returns the number of layers in the current drawing.\n
// \n
// Returns:\n
// The number of layers in the current drawing.\n
svgedit.draw.Drawing.prototype.getNumLayers = function() {\n
  return this.all_layers.length;\n
};\n
\n
// Function: svgedit.draw.Drawing.hasLayer\n
// Check if layer with given name already exists\n
svgedit.draw.Drawing.prototype.hasLayer = function(name) {\n
  for(var i = 0; i < this.getNumLayers(); i++) {\n
    if(this.all_layers[i][0] == name) return true;\n
  }\n
  return false;\n
};\n
\n
\n
// Function: svgedit.draw.Drawing.getLayerName\n
// Returns the name of the ith layer. If the index is out of range, an empty string is returned.\n
//\n
// Parameters:\n
// i - the zero-based index of the layer you are querying.\n
// \n
// Returns:\n
// The name of the ith layer\n
svgedit.draw.Drawing.prototype.getLayerName = function(i) {\n
  if (i >= 0 && i < this.getNumLayers()) {\n
    return this.all_layers[i][0];\n
  }\n
  return "";\n
};\n
\n
// Function: svgedit.draw.Drawing.getCurrentLayer\n
// Returns:\n
// The SVGGElement representing the current layer.\n
svgedit.draw.Drawing.prototype.getCurrentLayer = function() {\n
  return this.current_layer;\n
};\n
\n
// Function: getCurrentLayerName\n
// Returns the name of the currently selected layer. If an error occurs, an empty string \n
// is returned.\n
//\n
// Returns:\n
// The name of the currently active layer.\n
svgedit.draw.Drawing.prototype.getCurrentLayerName = function() {\n
  for (var i = 0; i < this.getNumLayers(); ++i) {\n
    if (this.all_layers[i][1] == this.current_layer) {\n
      return this.getLayerName(i);\n
    }\n
  }\n
  return "";\n
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
svgedit.draw.Drawing.prototype.setCurrentLayer = function(name) {\n
  for (var i = 0; i < this.getNumLayers(); ++i) {\n
    if (name == this.getLayerName(i)) {\n
      if (this.current_layer != this.all_layers[i][1]) {\n
        this.current_layer.setAttribute("style", "pointer-events:none");\n
        this.current_layer = this.all_layers[i][1];\n
        this.current_layer.setAttribute("style", "pointer-events:all");\n
      }\n
      return true;\n
    }\n
  }\n
  return false;\n
};\n
\n
\n
// Function: svgedit.draw.Drawing.deleteCurrentLayer\n
// Deletes the current layer from the drawing and then clears the selection. This function \n
// then calls the \'changed\' handler.  This is an undoable action.\n
// Returns:\n
// The SVGGElement of the layer removed or null.\n
svgedit.draw.Drawing.prototype.deleteCurrentLayer = function() {\n
  if (this.current_layer && this.getNumLayers() > 1) {\n
    // actually delete from the DOM and return it\n
    var parent = this.current_layer.parentNode;\n
    var nextSibling = this.current_layer.nextSibling;\n
    var oldLayerGroup = parent.removeChild(this.current_layer);\n
    this.identifyLayers();\n
    return oldLayerGroup;\n
  }\n
  return null;\n
};\n
\n
// Function: svgedit.draw.Drawing.identifyLayers\n
// Updates layer system and sets the current layer to the\n
// top-most layer (last <g> child of this drawing).\n
svgedit.draw.Drawing.prototype.identifyLayers = function() {\n
  this.all_layers = [];\n
  var numchildren = this.svgElem_.childNodes.length;\n
  // loop through all children of SVG element\n
  var orphans = [], layernames = [];\n
  var a_layer = null;\n
  var childgroups = false;\n
  for (var i = 0; i < numchildren; ++i) {\n
    var child = this.svgElem_.childNodes.item(i);\n
    // for each g, find its layer name\n
    if (child && child.nodeType == 1) {\n
      if (child.tagName == "g") {\n
        childgroups = true;\n
        var name = $("title",child).text();\n
        \n
        // Hack for Opera 10.60\n
        if(!name && svgedit.browser.isOpera() && child.querySelectorAll) {\n
          name = $(child.querySelectorAll(\'title\')).text();\n
        }\n
\n
        // store layer and name in global variable\n
        if (name) {\n
          layernames.push(name);\n
          this.all_layers.push( [name,child] );\n
          a_layer = child;\n
          svgedit.utilities.walkTree(child, function(e){e.setAttribute("style", "pointer-events:inherit");});\n
          a_layer.setAttribute("style", "pointer-events:none");\n
        }\n
        // if group did not have a name, it is an orphan\n
        else {\n
          orphans.push(child);\n
        }\n
      }\n
      // if child has is "visible" (i.e. not a <title> or <defs> element), then it is an orphan\n
      else if(~visElems_arr.indexOf(child.nodeName)) {\n
        var bb = svgedit.utilities.getBBox(child);\n
        orphans.push(child);\n
      }\n
    }\n
  }\n
  \n
  // create a new layer and add all the orphans to it\n
  var svgdoc = this.svgElem_.ownerDocument;\n
  if (orphans.length > 0 || !childgroups) {\n
    var i = 1;\n
    // TODO(codedread): What about internationalization of "Layer"?\n
    while (layernames.indexOf(("Layer " + i)) >= 0) { i++; }\n
    var newname = "Layer " + i;\n
    a_layer = svgdoc.createElementNS(svg_ns, "g");\n
    var layer_title = svgdoc.createElementNS(svg_ns, "title");\n
    layer_title.textContent = newname;\n
    a_layer.appendChild(layer_title);\n
    for (var j = 0; j < orphans.length; ++j) {\n
      a_layer.appendChild(orphans[j]);\n
    }\n
    this.svgElem_.appendChild(a_layer);\n
    this.all_layers.push( [newname, a_layer] );\n
  }\n
  svgedit.utilities.walkTree(a_layer, function(e){e.setAttribute("style","pointer-events:inherit");});\n
  if (a_layer.getAttribute("data-locked") === "true") {\n
    this.current_layer = this.all_layers.slice(-2)[0][1]\n
  }\n
  else {\n
    this.current_layer = a_layer\n
  }\n
  this.current_layer.setAttribute("style","pointer-events:all");\n
};\n
\n
// Function: svgedit.draw.Drawing.createLayer\n
// Creates a new top-level layer in the drawing with the given name and \n
// sets the current layer to it.\n
//\n
// Parameters:\n
// name - The given name\n
//\n
// Returns:\n
// The SVGGElement of the new layer, which is also the current layer\n
// of this drawing.\n
svgedit.draw.Drawing.prototype.createLayer = function(name) {\n
  var svgdoc = this.svgElem_.ownerDocument;\n
  var new_layer = svgdoc.createElementNS(svg_ns, "g");\n
  var layer_title = svgdoc.createElementNS(svg_ns, "title");\n
  layer_title.textContent = name;\n
  new_layer.appendChild(layer_title);\n
  this.svgElem_.appendChild(new_layer);\n
  this.identifyLayers();\n
  return new_layer;\n
};\n
\n
// Function: svgedit.draw.Drawing.getLayerVisibility\n
// Returns whether the layer is visible.  If the layer name is not valid, then this function\n
// returns false.\n
//\n
// Parameters:\n
// layername - the name of the layer which you want to query.\n
//\n
// Returns:\n
// The visibility state of the layer, or false if the layer name was invalid.\n
svgedit.draw.Drawing.prototype.getLayerVisibility = function(layername) {\n
  // find the layer\n
  var layer = null;\n
  for (var i = 0; i < this.getNumLayers(); ++i) {\n
    if (this.getLayerName(i) == layername) {\n
      layer = this.all_layers[i][1];\n
      break;\n
    }\n
  }\n
  if (!layer) return false;\n
  return (layer.getAttribute(\'display\') != \'none\');\n
};\n
\n
// Function: svgedit.draw.Drawing.setLayerVisibility\n
// Sets the visibility of the layer. If the layer name is not valid, this function return \n
// false, otherwise it returns true. This is an undo-able action.\n
//\n
// Parameters:\n
// layername - the name of the layer to change the visibility\n
// bVisible - true/false, whether the layer should be visible\n
//\n
// Returns:\n
// The SVGGElement representing the layer if the layername was valid, otherwise null.\n
svgedit.draw.Drawing.prototype.setLayerVisibility = function(layername, bVisible) {\n
  if (typeof bVisible != typeof true) {\n
    return null;\n
  }\n
  // find the layer\n
  var layer = null;\n
  for (var i = 0; i < this.getNumLayers(); ++i) {\n
    if (this.getLayerName(i) == layername) {\n
      layer = this.all_layers[i][1];\n
      break;\n
    }\n
  }\n
  if (!layer) return null;\n
  \n
  var oldDisplay = layer.getAttribute("display");\n
  if (!oldDisplay) oldDisplay = "inline";\n
  layer.setAttribute("display", bVisible ? "inline" : "none");\n
  return layer;\n
};\n
\n
\n
// Function: svgedit.draw.Drawing.getLayerOpacity\n
// Returns the opacity of the given layer.  If the input name is not a layer, null is returned.\n
//\n
// Parameters: \n
// layername - name of the layer on which to get the opacity\n
//\n
// Returns:\n
// The opacity value of the given layer.  This will be a value between 0.0 and 1.0, or null\n
// if layername is not a valid layer\n
svgedit.draw.Drawing.prototype.getLayerOpacity = function(layername) {\n
  for (var i = 0; i < this.getNumLayers(); ++i) {\n
    if (this.getLayerName(i) == layername) {\n
      var g = this.all_layers[i][1];\n
      var opacity = g.getAttribute(\'opacity\');\n
      if (!opacity) {\n
        opacity = \'1.0\';\n
      }\n
      return parseFloat(opacity);\n
    }\n
  }\n
  return null;\n
};\n
\n
// Function: svgedit.draw.Drawing.setLayerOpacity\n
// Sets the opacity of the given layer.  If the input name is not a layer, nothing happens.\n
// If opacity is not a value between 0.0 and 1.0, then nothing happens.\n
//\n
// Parameters:\n
// layername - name of the layer on which to set the opacity\n
// opacity - a float value in the range 0.0-1.0\n
svgedit.draw.Drawing.prototype.setLayerOpacity = function(layername, opacity) {\n
  if (typeof opacity != typeof 1.0 || opacity < 0.0 || opacity > 1.0) {\n
    return;\n
  }\n
  for (var i = 0; i < this.getNumLayers(); ++i) {\n
    if (this.getLayerName(i) == layername) {\n
      var g = this.all_layers[i][1];\n
      g.setAttribute("opacity", opacity);\n
      break;\n
    }\n
  }\n
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
            <value> <int>16624</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
