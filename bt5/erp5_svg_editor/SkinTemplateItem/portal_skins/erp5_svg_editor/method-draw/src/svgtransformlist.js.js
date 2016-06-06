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
            <value> <string>ts52851998.15</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>svgtransformlist.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/**\n
 * SVGTransformList\n
 *\n
 * Licensed under the Apache License, Version 2\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 * Copyright(c) 2010 Jeff Schiller\n
 */\n
\n
// Dependencies:\n
// 1) browser.js\n
\n
var svgedit = svgedit || {};\n
\n
(function() {\n
\n
if (!svgedit.transformlist) {\n
  svgedit.transformlist = {};\n
}\n
\n
var svgroot = document.createElementNS(\'http://www.w3.org/2000/svg\', \'svg\');\n
\n
// Helper function.\n
function transformToString(xform) {\n
  var m = xform.matrix,\n
    text = "";\n
  switch(xform.type) {\n
    case 1: // MATRIX\n
      text = "matrix(" + [m.a,m.b,m.c,m.d,m.e,m.f].join(",") + ")";\n
      break;\n
    case 2: // TRANSLATE\n
      text = "translate(" + m.e + "," + m.f + ")";\n
      break;\n
    case 3: // SCALE\n
      if (m.a == m.d) text = "scale(" + m.a + ")";\n
      else text = "scale(" + m.a + "," + m.d + ")";\n
      break;\n
    case 4: // ROTATE\n
      var cx = 0, cy = 0;\n
      // this prevents divide by zero\n
      if (xform.angle != 0) {\n
        var K = 1 - m.a;\n
        cy = ( K * m.f + m.b*m.e ) / ( K*K + m.b*m.b );\n
        cx = ( m.e - m.b * cy ) / K;\n
      }\n
      text = "rotate(" + xform.angle + " " + cx + "," + cy + ")";\n
      break;\n
  }\n
  return text;\n
};\n
\n
\n
/**\n
 * Map of SVGTransformList objects.\n
 */\n
var listMap_ = {};\n
\n
\n
// **************************************************************************************\n
// SVGTransformList implementation for Webkit \n
// These methods do not currently raise any exceptions.\n
// These methods also do not check that transforms are being inserted.  This is basically\n
// implementing as much of SVGTransformList that we need to get the job done.\n
//\n
//  interface SVGEditTransformList { \n
//    attribute unsigned long numberOfItems;\n
//    void   clear (  )\n
//    SVGTransform initialize ( in SVGTransform newItem )\n
//    SVGTransform getItem ( in unsigned long index ) (DOES NOT THROW DOMException, INDEX_SIZE_ERR)\n
//    SVGTransform insertItemBefore ( in SVGTransform newItem, in unsigned long index ) (DOES NOT THROW DOMException, INDEX_SIZE_ERR)\n
//    SVGTransform replaceItem ( in SVGTransform newItem, in unsigned long index ) (DOES NOT THROW DOMException, INDEX_SIZE_ERR)\n
//    SVGTransform removeItem ( in unsigned long index ) (DOES NOT THROW DOMException, INDEX_SIZE_ERR)\n
//    SVGTransform appendItem ( in SVGTransform newItem )\n
//    NOT IMPLEMENTED: SVGTransform createSVGTransformFromMatrix ( in SVGMatrix matrix );\n
//    NOT IMPLEMENTED: SVGTransform consolidate (  );\n
//  }\n
// **************************************************************************************\n
svgedit.transformlist.SVGTransformList = function(elem) {\n
  this._elem = elem || null;\n
  this._xforms = [];\n
  // TODO: how do we capture the undo-ability in the changed transform list?\n
  this._update = function() {\n
    var tstr = "";\n
    var concatMatrix = svgroot.createSVGMatrix();\n
    for (var i = 0; i < this.numberOfItems; ++i) {\n
      var xform = this._list.getItem(i);\n
      tstr += transformToString(xform) + " ";\n
    }\n
    this._elem.setAttribute("transform", tstr);\n
  };\n
  this._list = this;\n
  this._init = function() {\n
    // Transform attribute parser\n
    var str = this._elem.getAttribute("transform");\n
    if(!str) return;\n
    \n
    // TODO: Add skew support in future\n
    var re = /\\s*((scale|matrix|rotate|translate)\\s*\\(.*?\\))\\s*,?\\s*/;\n
    var arr = [];\n
    var m = true;\n
    while(m) {\n
      m = str.match(re);\n
      str = str.replace(re,\'\');\n
      if(m && m[1]) {\n
        var x = m[1];\n
        var bits = x.split(/\\s*\\(/);\n
        var name = bits[0];\n
        var val_bits = bits[1].match(/\\s*(.*?)\\s*\\)/);\n
        val_bits[1] = val_bits[1].replace(/(\\d)-/g, "$1 -");\n
        var val_arr = val_bits[1].split(/[, ]+/);\n
        var letters = \'abcdef\'.split(\'\');\n
        var mtx = svgroot.createSVGMatrix();\n
        $.each(val_arr, function(i, item) {\n
          val_arr[i] = parseFloat(item);\n
          if(name == \'matrix\') {\n
            mtx[letters[i]] = val_arr[i];\n
          }\n
        });\n
        var xform = svgroot.createSVGTransform();\n
        var fname = \'set\' + name.charAt(0).toUpperCase() + name.slice(1);\n
        var values = name==\'matrix\'?[mtx]:val_arr;\n
        \n
        if (name == \'scale\' && values.length == 1) {\n
          values.push(values[0]);\n
        } else if (name == \'translate\' && values.length == 1) {\n
          values.push(0);\n
        } else if (name == \'rotate\' && values.length == 1) {\n
          values.push(0);\n
          values.push(0);\n
        }\n
        xform[fname].apply(xform, values);\n
        this._list.appendItem(xform);\n
      }\n
    }\n
  };\n
  this._removeFromOtherLists = function(item) {\n
    if (item) {\n
      // Check if this transform is already in a transformlist, and\n
      // remove it if so.\n
      var found = false;\n
      for (var id in listMap_) {\n
        var tl = listMap_[id];\n
        for (var i = 0, len = tl._xforms.length; i < len; ++i) {\n
          if(tl._xforms[i] == item) {\n
            found = true;\n
            tl.removeItem(i);\n
            break;\n
          }\n
        }\n
        if (found) {\n
          break;\n
        }\n
      }\n
    }\n
  };\n
  \n
  this.numberOfItems = 0;\n
  this.clear = function() { \n
    this.numberOfItems = 0;\n
    this._xforms = [];\n
  };\n
  \n
  this.initialize = function(newItem) {\n
    this.numberOfItems = 1;\n
    this._removeFromOtherLists(newItem);\n
    this._xforms = [newItem];\n
  };\n
  \n
  this.getItem = function(index) {\n
    if (index < this.numberOfItems && index >= 0) {\n
      return this._xforms[index];\n
    }\n
    throw {code: 1}; // DOMException with code=INDEX_SIZE_ERR\n
  };\n
  \n
  this.insertItemBefore = function(newItem, index) {\n
    var retValue = null;\n
    if (index >= 0) {\n
      if (index < this.numberOfItems) {\n
        this._removeFromOtherLists(newItem);\n
        var newxforms = new Array(this.numberOfItems + 1);\n
        // TODO: use array copying and slicing\n
        for ( var i = 0; i < index; ++i) {\n
          newxforms[i] = this._xforms[i];\n
        }\n
        newxforms[i] = newItem;\n
        for ( var j = i+1; i < this.numberOfItems; ++j, ++i) {\n
          newxforms[j] = this._xforms[i];\n
        }\n
        this.numberOfItems++;\n
        this._xforms = newxforms;\n
        retValue = newItem;\n
        this._list._update();\n
      }\n
      else {\n
        retValue = this._list.appendItem(newItem);\n
      }\n
    }\n
    return retValue;\n
  };\n
  \n
  this.replaceItem = function(newItem, index) {\n
    var retValue = null;\n
    if (index < this.numberOfItems && index >= 0) {\n
      this._removeFromOtherLists(newItem);\n
      this._xforms[index] = newItem;\n
      retValue = newItem;\n
      this._list._update();\n
    }\n
    return retValue;\n
  };\n
  \n
  this.removeItem = function(index) {\n
    if (index < this.numberOfItems && index >= 0) {\n
      var retValue = this._xforms[index];\n
      var newxforms = new Array(this.numberOfItems - 1);\n
      for (var i = 0; i < index; ++i) {\n
        newxforms[i] = this._xforms[i];\n
      }\n
      for (var j = i; j < this.numberOfItems-1; ++j, ++i) {\n
        newxforms[j] = this._xforms[i+1];\n
      }\n
      this.numberOfItems--;\n
      this._xforms = newxforms;\n
      this._list._update();\n
      return retValue;\n
    } else {\n
      throw {code: 1}; // DOMException with code=INDEX_SIZE_ERR\n
    }\n
  };\n
  \n
  this.appendItem = function(newItem) {\n
    this._removeFromOtherLists(newItem);\n
    this._xforms.push(newItem);\n
    this.numberOfItems++;\n
    this._list._update();\n
    return newItem;\n
  };\n
};\n
\n
\n
svgedit.transformlist.resetListMap = function() {\n
  listMap_ = {};\n
};\n
\n
/**\n
 * Removes transforms of the given element from the map.\n
 * Parameters:\n
 * elem - a DOM Element\n
 */\n
svgedit.transformlist.removeElementFromListMap = function(elem) {\n
  if (elem.id && listMap_[elem.id]) {\n
    delete listMap_[elem.id];\n
  }\n
};\n
\n
// Function: getTransformList\n
// Returns an object that behaves like a SVGTransformList for the given DOM element\n
//\n
// Parameters:\n
// elem - DOM element to get a transformlist from\n
svgedit.transformlist.getTransformList = function(elem) {\n
  if (!svgedit.browser.supportsNativeTransformLists()) {\n
    var id = elem.id;\n
    if(!id) {\n
      // Get unique ID for temporary element\n
      id = \'temp\';\n
    }\n
    var t = listMap_[id];\n
    if (!t || id == \'temp\') {\n
      listMap_[id] = new svgedit.transformlist.SVGTransformList(elem);\n
      listMap_[id]._init();\n
      t = listMap_[id];\n
    }\n
    return t;\n
  }\n
  else if (elem.transform) {\n
    return elem.transform.baseVal;\n
  }\n
  else if (elem.gradientTransform) {\n
    return elem.gradientTransform.baseVal;\n
  }\n
  else if (elem.patternTransform) {\n
    return elem.patternTransform.baseVal;\n
  }\n
\n
  return null;\n
};\n
\n
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
            <value> <int>8522</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
