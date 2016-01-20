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
            <value> <string>ts52852027.26</string> </value>
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

/**\n
 * Package: svedit.select\n
 *\n
 * Licensed under the Apache License, Version 2\n
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
var svgedit = svgedit || {};\n
\n
(function() {\n
\n
if (!svgedit.select) {\n
  svgedit.select = {};\n
}\n
\n
var svgFactory_;\n
var config_;\n
var selectorManager_; // A Singleton\n
\n
// Class: svgedit.select.Selector\n
// Private class for DOM element selection boxes\n
// \n
// Parameters:\n
// id - integer to internally indentify the selector\n
// elem - DOM element associated with this selector\n
svgedit.select.Selector = function(id, elem) {\n
  // this is the selector\'s unique number\n
  this.id = id;\n
\n
  // this holds a reference to the element for which this selector is being used\n
  this.selectedElement = elem;\n
\n
  // this is a flag used internally to track whether the selector is being used or not\n
  this.locked = true;\n
\n
  // this holds a reference to the <g> element that holds all visual elements of the selector\n
  this.selectorGroup = svgFactory_.createSVGElement({\n
    \'element\': \'g\',\n
    \'attr\': {\'id\': (\'selectorGroup\' + this.id)}\n
  });\n
\n
  // this holds a reference to the path rect\n
  this.selectorRect = this.selectorGroup.appendChild(\n
    svgFactory_.createSVGElement({\n
      \'element\': \'path\',\n
      \'attr\': {\n
        \'id\': (\'selectedBox\' + this.id),\n
        \'fill\': \'none\',\n
        \'stroke\': \'#4F80FF\',\n
        \'stroke-width\': \'1\',\n
        \'shape-rendering\': \'crispEdges\',\n
        \'style\': \'pointer-events:none\'\n
      }\n
    })\n
  );\n
  \n
  if (svgedit.browser.isTouch()) {\n
    this.selectorRect.setAttribute("stroke-opacity", 0.3);\n
  }\n
\n
  // this holds a reference to the grip coordinates for this selector\n
  this.gripCoords = {\n
    \'nw\': null,\n
    \'n\' : null,\n
    \'ne\': null,\n
    \'e\' : null,\n
    \'se\': null,\n
    \'s\' : null,\n
    \'sw\': null,\n
    \'w\' : null\n
  };\n
\n
  this.reset(this.selectedElement);\n
};\n
\n
\n
// Function: svgedit.select.Selector.reset \n
// Used to reset the id and element that the selector is attached to\n
//\n
// Parameters: \n
// e - DOM element associated with this selector\n
svgedit.select.Selector.prototype.reset = function(e) {\n
  this.locked = true;\n
  this.selectedElement = e;\n
  this.resize();\n
  this.selectorGroup.setAttribute(\'display\', \'inline\');\n
};\n
\n
// Function: svgedit.select.Selector.updateGripCursors\n
// Updates cursors for corner grips on rotation so arrows point the right way\n
//\n
// Parameters:\n
// angle - Float indicating current rotation angle in degrees\n
svgedit.select.Selector.prototype.updateGripCursors = function(angle) {\n
  var dir_arr = [];\n
  var steps = Math.round(angle / 45);\n
  if(steps < 0) steps += 8;\n
  for (var dir in selectorManager_.selectorGrips) {\n
    dir_arr.push(dir);\n
  }\n
  while(steps > 0) {\n
    dir_arr.push(dir_arr.shift());\n
    steps--;\n
  }\n
  var i = 0;\n
  for (var dir in selectorManager_.selectorGrips) {\n
    selectorManager_.selectorGrips[dir].setAttribute(\'style\', (\'cursor:\' + dir_arr[i] + \'-resize\'));\n
    i++;\n
  };\n
};\n
\n
// Function: svgedit.select.Selector.showGrips\n
// Show the resize grips of this selector\n
//\n
// Parameters:\n
// show - boolean indicating whether grips should be shown or not\n
svgedit.select.Selector.prototype.showGrips = function(show) {\n
  var bShow = show ? \'inline\' : \'none\';\n
  selectorManager_.selectorGripsGroup.setAttribute(\'display\', bShow);\n
  var elem = this.selectedElement;\n
  this.hasGrips = show;\n
  if(elem && show) {\n
    this.selectorGroup.appendChild(selectorManager_.selectorGripsGroup);\n
    this.updateGripCursors(svgedit.utilities.getRotationAngle(elem));\n
  }\n
};\n
\n
// Function: svgedit.select.Selector.resize\n
// Updates the selector to match the element\'s size\n
svgedit.select.Selector.prototype.resize = function() {\n
  var selectedBox = this.selectorRect,\n
    mgr = selectorManager_,\n
    selectedGrips = mgr.selectorGrips,\n
    selected = this.selectedElement,\n
    sw = selected.getAttribute(\'stroke-width\'),\n
    current_zoom = svgFactory_.currentZoom();\n
  var offset = 1/current_zoom;\n
  if (selected.getAttribute(\'stroke\') !== \'none\' && !isNaN(sw)) {\n
    offset += (sw/2);\n
  }\n
\n
  var tagName = selected.tagName;\n
  if (tagName === \'text\') {\n
    offset += 2/current_zoom;\n
  }\n
\n
  // loop and transform our bounding box until we reach our first rotation\n
  var tlist = svgedit.transformlist.getTransformList(selected);\n
  var m = svgedit.math.transformListToTransform(tlist).matrix;\n
\n
  // This should probably be handled somewhere else, but for now\n
  // it keeps the selection box correctly positioned when zoomed\n
  m.e *= current_zoom;\n
  m.f *= current_zoom;\n
\n
  var bbox = svgedit.utilities.getBBox(selected);\n
  if(tagName === \'g\' && !$.data(selected, \'gsvg\')) {\n
    // The bbox for a group does not include stroke vals, so we\n
    // get the bbox based on its children. \n
    var stroked_bbox = svgFactory_.getStrokedBBox(selected.childNodes);\n
    if(stroked_bbox) {\n
      bbox = stroked_bbox;\n
    }\n
  }\n
\n
  // apply the transforms\n
  var l=bbox.x, t=bbox.y, w=bbox.width, h=bbox.height,\n
    bbox = {x:l, y:t, width:w, height:h};\n
\n
  // we need to handle temporary transforms too\n
  // if skewed, get its transformed box, then find its axis-aligned bbox\n
  \n
  //*\n
  offset *= current_zoom;\n
  \n
  var nbox = svgedit.math.transformBox(l*current_zoom, t*current_zoom, w*current_zoom, h*current_zoom, m),\n
    aabox = nbox.aabox,\n
    nbax = aabox.x - offset,\n
    nbay = aabox.y - offset,\n
    nbaw = aabox.width + (offset * 2),\n
    nbah = aabox.height + (offset * 2);\n
    \n
  // now if the shape is rotated, un-rotate it\n
  var cx = nbax + nbaw/2,\n
    cy = nbay + nbah/2;\n
\n
  var angle = svgedit.utilities.getRotationAngle(selected);\n
  if (angle) {\n
    var rot = svgFactory_.svgRoot().createSVGTransform();\n
    rot.setRotate(-angle,cx,cy);\n
    var rotm = rot.matrix;\n
    nbox.tl = svgedit.math.transformPoint(nbox.tl.x,nbox.tl.y,rotm);\n
    nbox.tr = svgedit.math.transformPoint(nbox.tr.x,nbox.tr.y,rotm);\n
    nbox.bl = svgedit.math.transformPoint(nbox.bl.x,nbox.bl.y,rotm);\n
    nbox.br = svgedit.math.transformPoint(nbox.br.x,nbox.br.y,rotm);\n
\n
    // calculate the axis-aligned bbox\n
    var tl = nbox.tl;\n
    var minx = tl.x,\n
      miny = tl.y,\n
      maxx = tl.x,\n
      maxy = tl.y;\n
\n
    var Min = Math.min, Max = Math.max;\n
\n
    minx = Min(minx, Min(nbox.tr.x, Min(nbox.bl.x, nbox.br.x) ) ) - offset;\n
    miny = Min(miny, Min(nbox.tr.y, Min(nbox.bl.y, nbox.br.y) ) ) - offset;\n
    maxx = Max(maxx, Max(nbox.tr.x, Max(nbox.bl.x, nbox.br.x) ) ) + offset;\n
    maxy = Max(maxy, Max(nbox.tr.y, Max(nbox.bl.y, nbox.br.y) ) ) + offset;\n
\n
    nbax = minx;\n
    nbay = miny;\n
    nbaw = (maxx-minx);\n
    nbah = (maxy-miny);\n
  }\n
\n
  var dstr = \'M\' + nbax + \',\' + nbay\n
        + \' L\' + (nbax+nbaw) + \',\' + nbay\n
        + \' \' + (nbax+nbaw) + \',\' + (nbay+nbah)\n
        + \' \' + nbax + \',\' + (nbay+nbah) + \'z\';\n
  selectedBox.setAttribute(\'d\', dstr);\n
  \n
  var xform = angle ? \'rotate(\' + [angle,cx,cy].join(\',\') + \')\' : \'\';\n
  this.selectorGroup.setAttribute(\'transform\', xform);\n
\n
    if(svgedit.browser.isTouch()) {\n
      nbax -= 15.75;\n
      nbay -= 15.75;\n
    }\n
    else {\n
      nbax -= 4;\n
      nbay -= 4;\n
    }\n
    this.gripCoords = {\n
      \'nw\': [nbax, nbay].map(Math.round),\n
      \'ne\': [nbax+nbaw, nbay].map(Math.round),\n
      \'sw\': [nbax, nbay+nbah].map(Math.round),\n
      \'se\': [nbax+nbaw, nbay+nbah].map(Math.round),\n
      \'n\':  [nbax + (nbaw)/2, nbay].map(Math.round),\n
      \'w\':  [nbax, nbay + (nbah)/2].map(Math.round),\n
      \'e\':  [nbax + nbaw, nbay + (nbah)/2].map(Math.round),\n
      \'s\':  [nbax + (nbaw)/2, nbay + nbah].map(Math.round)\n
    };\n
\n
    for(var dir in this.gripCoords) {\n
      var coords = this.gripCoords[dir];\n
      selectedGrips[dir].setAttribute(\'x\', coords[0]);\n
      selectedGrips[dir].setAttribute(\'y\', coords[1]);\n
    };\n
    \n
    this.rotateCoords = {\n
      \'nw\': [nbax, nbay],\n
      \'ne\': [nbax+nbaw+8, nbay],\n
      \'sw\': [nbax, nbay+nbah+8],\n
      \'se\': [nbax+nbaw+8, nbay+nbah+8]\n
    };\n
    \n
    for(var dir in this.rotateCoords) {\n
      var coords = this.rotateCoords[dir];\n
      mgr.rotateGrips[dir].setAttribute(\'cx\', coords[0]); \n
      mgr.rotateGrips[dir].setAttribute(\'cy\', coords[1]);\n
    }\n
\n
};\n
\n
\n
// Class: svgedit.select.SelectorManager\n
svgedit.select.SelectorManager = function() {\n
  // this will hold the <g> element that contains all selector rects/grips\n
  this.selectorParentGroup = null;\n
\n
  // this is a special rect that is used for multi-select\n
  this.rubberBandBox = null;\n
\n
  // this will hold objects of type svgedit.select.Selector (see above)\n
  this.selectors = [];\n
\n
  // this holds a map of SVG elements to their Selector object\n
  this.selectorMap = {};\n
\n
  // this holds a reference to the grip elements\n
  this.selectorGrips = {\n
    \'nw\': null,\n
    \'n\' :  null,\n
    \'ne\': null,\n
    \'e\' :  null,\n
    \'se\': null,\n
    \'s\' :  null,\n
    \'sw\': null,\n
    \'w\' :  null\n
  };\n
\n
  this.selectorGripsGroup = null;\n
  //this.rotateGripConnector = null;\n
  this.rotateGrips = {\n
    \'nw\': null,\n
    \'ne\': null,\n
    \'se\': null,\n
    \'sw\': null\n
  };\n
\n
  this.initGroup();\n
};\n
\n
// Function: svgedit.select.SelectorManager.initGroup\n
// Resets the parent selector group element\n
svgedit.select.SelectorManager.prototype.initGroup = function() {\n
  // remove old selector parent group if it existed\n
  if (this.selectorParentGroup && this.selectorParentGroup.parentNode) {\n
    this.selectorParentGroup.parentNode.removeChild(this.selectorParentGroup);\n
  }\n
\n
  // create parent selector group and add it to svgroot\n
  this.selectorParentGroup = svgFactory_.createSVGElement({\n
    \'element\': \'g\',\n
    \'attr\': {\'id\': \'selectorParentGroup\'}\n
  });\n
  this.selectorGripsGroup = svgFactory_.createSVGElement({\n
    \'element\': \'g\',\n
    \'attr\': {\'display\': \'none\'}\n
  });\n
  this.selectorParentGroup.appendChild(this.selectorGripsGroup);\n
  svgFactory_.svgRoot().appendChild(this.selectorParentGroup);\n
\n
  this.selectorMap = {};\n
  this.selectors = [];\n
  this.rubberBandBox = null;\n
\n
  for (var dir in this.rotateGrips) {\n
    var grip = svgFactory_.createSVGElement({\n
        \'element\': \'circle\',\n
        \'attr\': {\n
          \'id\': \'selectorGrip_rotate_\' + dir,\n
          \'fill\': \'#000\',\n
          \'r\': 8,\n
          \'stroke\': \'#000\',\n
          "fill-opacity": 0,\n
          "stroke-opacity": 0,\n
          \'stroke-width\': 0,\n
          \'style\': \'cursor:url(\' + config_.imgPath + \'rotate.png) 12 12, auto;\'\n
        }\n
    })\n
  $.data(grip, \'dir\', dir);\n
  $.data(grip, \'type\', \'rotate\');\n
  this.rotateGrips[dir] = this.selectorGripsGroup.appendChild(grip);\n
  }\n
\n
  // add the corner grips\n
  for (var dir in this.selectorGrips) {\n
    var grip = svgFactory_.createSVGElement({\n
      \'element\': \'rect\',\n
      \'attr\': {\n
        \'id\': (\'selectorGrip_resize_\' + dir),\n
        \'width\': 8,\n
        \'height\': 8,\n
        \'fill\': "#4F80FF",\n
        \'stroke\': "rgba(0,0,0,0)",\n
        \'stroke-width\': 1,\n
        \'style\': (\'cursor:\' + dir + \'-resize\'),\n
        \'pointer-events\': \'all\'\n
      }\n
    });\n
    if (svgedit.browser.isTouch()) {\n
      \n
      grip.setAttribute("width", 30.5)\n
      grip.setAttribute("height", 30.5)\n
      grip.setAttribute("fill-opacity", 0.3)\n
    }\n
    \n
    $.data(grip, \'dir\', dir);\n
    $.data(grip, \'type\', \'resize\');\n
    this.selectorGrips[dir] = this.selectorGripsGroup.appendChild(grip);\n
  }\n
\n
  if($(\'#canvasBackground\').length) return;\n
\n
  var dims = config_.dimensions;\n
  var canvasbg = svgFactory_.createSVGElement({\n
    \'element\': \'svg\',\n
    \'attr\': {\n
      \'id\': \'canvasBackground\',\n
      \'width\': dims[0],\n
      \'height\': dims[1],\n
      \'x\': 0,\n
      \'y\': 0,\n
      \'overflow\': (svgedit.browser.isWebkit() ? \'none\' : \'visible\'), // Chrome 7 has a problem with this when zooming out\n
      \'style\': \'pointer-events:none\'\n
    }\n
  });\n
\n
  var defs = svgFactory_.createSVGElement({\n
    \'element\': \'defs\',\n
    \'attr\': {\n
      \'id\': \'placeholder_defs\'\n
    }\n
  })\n
  \n
  var pattern = svgFactory_.createSVGElement({\n
    \'element\': \'pattern\',\n
    \'attr\': {\n
      \'id\': \'checkerPattern\',\n
      \'patternUnits\': \'userSpaceOnUse\',\n
      \'x\': 0,\n
      \'y\': 0,\n
      \'width\': 20,\n
      \'height\': 20,\n
      \'viewBox\': \'0 0 10 10\'\n
    }\n
  })\n
  \n
  var pattern_bg = svgFactory_.createSVGElement({\n
    \'element\': \'rect\',\n
    \'attr\': {\n
      \'x\': 0,\n
      \'y\': 0,\n
      \'width\': 10,\n
      \'height\': 10,\n
      \'fill\': "#fff"\n
    }\n
  })\n
\n
  var pattern_square1 = svgFactory_.createSVGElement({\n
    \'element\': \'rect\',\n
    \'attr\': {\n
      \'x\': 0,\n
      \'y\': 0,\n
      \'width\': 5,\n
      \'height\': 5,\n
      \'fill\': "#eee"\n
    }\n
  })\n
  \n
  var pattern_square2 = svgFactory_.createSVGElement({\n
    \'element\': \'rect\',\n
    \'attr\': {\n
      \'x\': 5,\n
      \'y\': 5,\n
      \'width\': 5,\n
      \'height\': 5,\n
      \'fill\': "#eee"\n
    }\n
  })\n
\n
  var rect = svgFactory_.createSVGElement({\n
    \'element\': \'rect\',\n
    \'attr\': {\n
      \'width\': \'100%\',\n
      \'height\': \'100%\',\n
      \'x\': 0,\n
      \'y\': 0,\n
      \'stroke-width\': 1,\n
      \'stroke\': \'#000\',\n
      \'fill\': \'url(#checkerPattern)\',\n
      \'style\': \'pointer-events:none\'\n
    }\n
  });\n
\n
  // Both Firefox and WebKit are too slow with this filter region (especially at higher\n
  // zoom levels) and Opera has at least one bug\n
//  if (!svgedit.browser.isOpera()) rect.setAttribute(\'filter\', \'url(#canvashadow)\');\n
  canvasbg.appendChild(defs);\n
  defs.appendChild(pattern);\n
  pattern.appendChild(pattern_bg);\n
  pattern.appendChild(pattern_square1);\n
  pattern.appendChild(pattern_square2);\n
  canvasbg.appendChild(rect);\n
\n
  svgFactory_.svgRoot().insertBefore(canvasbg, svgFactory_.svgContent());\n
};\n
\n
// Function: svgedit.select.SelectorManager.requestSelector\n
// Returns the selector based on the given element\n
//\n
// Parameters:\n
// elem - DOM element to get the selector for\n
svgedit.select.SelectorManager.prototype.requestSelector = function(elem) {\n
  if (elem == null) return null;\n
  var N = this.selectors.length;\n
  // If we\'ve already acquired one for this element, return it.\n
  if (typeof(this.selectorMap[elem.id]) == \'object\') {\n
    this.selectorMap[elem.id].locked = true;\n
    return this.selectorMap[elem.id];\n
  }\n
  for (var i = 0; i < N; ++i) {\n
    if (this.selectors[i] && !this.selectors[i].locked) {\n
      this.selectors[i].locked = true;\n
      this.selectors[i].reset(elem);\n
      this.selectorMap[elem.id] = this.selectors[i];\n
      return this.selectors[i];\n
    }\n
  }\n
  // if we reached here, no available selectors were found, we create one\n
  this.selectors[N] = new svgedit.select.Selector(N, elem);\n
  this.selectorParentGroup.appendChild(this.selectors[N].selectorGroup);\n
  this.selectorMap[elem.id] = this.selectors[N];\n
  return this.selectors[N];\n
};\n
\n
// Function: svgedit.select.SelectorManager.releaseSelector\n
// Removes the selector of the given element (hides selection box) \n
//\n
// Parameters:\n
// elem - DOM element to remove the selector for\n
svgedit.select.SelectorManager.prototype.releaseSelector = function(elem) {\n
  if (elem == null) return;\n
  var N = this.selectors.length,\n
    sel = this.selectorMap[elem.id];\n
  for (var i = 0; i < N; ++i) {\n
    if (this.selectors[i] && this.selectors[i] == sel) {\n
      if (sel.locked == false) {\n
        // TODO(codedread): Ensure this exists in this module.\n
        console.log(\'WARNING! selector was released but was already unlocked\');\n
      }\n
      delete this.selectorMap[elem.id];\n
      sel.locked = false;\n
      sel.selectedElement = null;\n
      sel.showGrips(false);\n
\n
      // remove from DOM and store reference in JS but only if it exists in the DOM\n
      try {\n
        sel.selectorGroup.setAttribute(\'display\', \'none\');\n
      } catch(e) { }\n
\n
      break;\n
    }\n
  }\n
};\n
\n
// Function: svgedit.select.SelectorManager.getRubberBandBox\n
// Returns the rubberBandBox DOM element. This is the rectangle drawn by the user for selecting/zooming\n
svgedit.select.SelectorManager.prototype.getRubberBandBox = function() {\n
  if (!this.rubberBandBox) {\n
    this.rubberBandBox = this.selectorParentGroup.appendChild(\n
      svgFactory_.createSVGElement({\n
        \'element\': \'rect\',\n
        \'attr\': {\n
          \'id\': \'selectorRubberBand\',\n
          \'fill\': \'none\',\n
          \'stroke\': \'#666\',\n
          \'stroke-width\': 1,\n
          \'stroke-dasharray\': \'3,2\', \n
          \'display\': \'none\',\n
          \'style\': \'pointer-events:none\'\n
        }\n
      })\n
    );\n
  }\n
  return this.rubberBandBox;\n
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
  config_ = config;\n
  svgFactory_ = svgFactory;\n
  selectorManager_ = new svgedit.select.SelectorManager();\n
  //for hovering elements\n
  svgFactory_.createSVGElement({\n
    \'element\': \'g\',\n
    \'attr\': {\n
      \'id\': \'hover_group\'\n
    }\n
  })\n
};\n
\n
/**\n
 * Function: svgedit.select.getSelectorManager\n
 *\n
 * Returns:\n
 * The SelectorManager instance.\n
 */\n
svgedit.select.getSelectorManager = function() {\n
  return selectorManager_;\n
};\n
\n
})();

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>17258</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
