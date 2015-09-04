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
            <value> <string>ts40515059.58</string> </value>
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

/*globals $, svgedit*/\n
/*jslint vars: true, eqeq: true*/\n
/**\n
 * SVGTransformList\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 * Copyright(c) 2010 Jeff Schiller\n
 */\n
\n
// Dependencies:\n
// 1) browser.js\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.transformlist) {\n
\tsvgedit.transformlist = {};\n
}\n
\n
var svgroot = document.createElementNS(svgedit.NS.SVG, \'svg\');\n
\n
// Helper function.\n
function transformToString(xform) {\n
\tvar m = xform.matrix,\n
\t\ttext = \'\';\n
\tswitch(xform.type) {\n
\t\tcase 1: // MATRIX\n
\t\t\ttext = \'matrix(\' + [m.a, m.b, m.c, m.d, m.e, m.f].join(\',\') + \')\';\n
\t\t\tbreak;\n
\t\tcase 2: // TRANSLATE\n
\t\t\ttext = \'translate(\' + m.e + \',\' + m.f + \')\';\n
\t\t\tbreak;\n
\t\tcase 3: // SCALE\n
\t\t\tif (m.a == m.d) {text = \'scale(\' + m.a + \')\';}\n
\t\t\telse {text = \'scale(\' + m.a + \',\' + m.d + \')\';}\n
\t\t\tbreak;\n
\t\tcase 4: // ROTATE\n
\t\t\tvar cx = 0, cy = 0;\n
\t\t\t// this prevents divide by zero\n
\t\t\tif (xform.angle != 0) {\n
\t\t\t\tvar K = 1 - m.a;\n
\t\t\t\tcy = ( K * m.f + m.b*m.e ) / ( K*K + m.b*m.b );\n
\t\t\t\tcx = ( m.e - m.b * cy ) / K;\n
\t\t\t}\n
\t\t\ttext = \'rotate(\' + xform.angle + \' \' + cx + \',\' + cy + \')\';\n
\t\t\tbreak;\n
\t}\n
\treturn text;\n
}\n
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
//\t\tattribute unsigned long numberOfItems;\n
//\t\tvoid   clear (  )\n
//\t\tSVGTransform initialize ( in SVGTransform newItem )\n
//\t\tSVGTransform getItem ( in unsigned long index ) (DOES NOT THROW DOMException, INDEX_SIZE_ERR)\n
//\t\tSVGTransform insertItemBefore ( in SVGTransform newItem, in unsigned long index ) (DOES NOT THROW DOMException, INDEX_SIZE_ERR)\n
//\t\tSVGTransform replaceItem ( in SVGTransform newItem, in unsigned long index ) (DOES NOT THROW DOMException, INDEX_SIZE_ERR)\n
//\t\tSVGTransform removeItem ( in unsigned long index ) (DOES NOT THROW DOMException, INDEX_SIZE_ERR)\n
//\t\tSVGTransform appendItem ( in SVGTransform newItem )\n
//\t\tNOT IMPLEMENTED: SVGTransform createSVGTransformFromMatrix ( in SVGMatrix matrix );\n
//\t\tNOT IMPLEMENTED: SVGTransform consolidate (  );\n
//\t}\n
// **************************************************************************************\n
svgedit.transformlist.SVGTransformList = function(elem) {\n
\tthis._elem = elem || null;\n
\tthis._xforms = [];\n
\t// TODO: how do we capture the undo-ability in the changed transform list?\n
\tthis._update = function() {\n
\t\tvar tstr = \'\';\n
\t\tvar concatMatrix = svgroot.createSVGMatrix();\n
\t\tvar i;\n
\t\tfor (i = 0; i < this.numberOfItems; ++i) {\n
\t\t\tvar xform = this._list.getItem(i);\n
\t\t\ttstr += transformToString(xform) + \' \';\n
\t\t}\n
\t\tthis._elem.setAttribute(\'transform\', tstr);\n
\t};\n
\tthis._list = this;\n
\tthis._init = function() {\n
\t\t// Transform attribute parser\n
\t\tvar str = this._elem.getAttribute(\'transform\');\n
\t\tif (!str) {return;}\n
\n
\t\t// TODO: Add skew support in future\n
\t\tvar re = /\\s*((scale|matrix|rotate|translate)\\s*\\(.*?\\))\\s*,?\\s*/;\n
\t\tvar m = true;\n
\t\twhile (m) {\n
\t\t\tm = str.match(re);\n
\t\t\tstr = str.replace(re, \'\');\n
\t\t\tif (m && m[1]) {\n
\t\t\t\tvar x = m[1];\n
\t\t\t\tvar bits = x.split(/\\s*\\(/);\n
\t\t\t\tvar name = bits[0];\n
\t\t\t\tvar val_bits = bits[1].match(/\\s*(.*?)\\s*\\)/);\n
\t\t\t\tval_bits[1] = val_bits[1].replace(/(\\d)-/g, \'$1 -\');\n
\t\t\t\tvar val_arr = val_bits[1].split(/[, ]+/);\n
\t\t\t\tvar letters = \'abcdef\'.split(\'\');\n
\t\t\t\tvar mtx = svgroot.createSVGMatrix();\n
\t\t\t\t$.each(val_arr, function(i, item) {\n
\t\t\t\t\tval_arr[i] = parseFloat(item);\n
\t\t\t\t\tif (name == \'matrix\') {\n
\t\t\t\t\t\tmtx[letters[i]] = val_arr[i];\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tvar xform = svgroot.createSVGTransform();\n
\t\t\t\tvar fname = \'set\' + name.charAt(0).toUpperCase() + name.slice(1);\n
\t\t\t\tvar values = name == \'matrix\' ? [mtx] : val_arr;\n
\n
\t\t\t\tif (name == \'scale\' && values.length == 1) {\n
\t\t\t\t\tvalues.push(values[0]);\n
\t\t\t\t} else if (name == \'translate\' && values.length == 1) {\n
\t\t\t\t\tvalues.push(0);\n
\t\t\t\t} else if (name == \'rotate\' && values.length == 1) {\n
\t\t\t\t\tvalues.push(0, 0);\n
\t\t\t\t}\n
\t\t\t\txform[fname].apply(xform, values);\n
\t\t\t\tthis._list.appendItem(xform);\n
\t\t\t}\n
\t\t}\n
\t};\n
\tthis._removeFromOtherLists = function(item) {\n
\t\tif (item) {\n
\t\t\t// Check if this transform is already in a transformlist, and\n
\t\t\t// remove it if so.\n
\t\t\tvar found = false;\n
\t\t\tvar id;\n
\t\t\tfor (id in listMap_) {\n
\t\t\t\tvar tl = listMap_[id];\n
\t\t\t\tvar i, len;\n
\t\t\t\tfor (i = 0, len = tl._xforms.length; i < len; ++i) {\n
\t\t\t\t\tif (tl._xforms[i] == item) {\n
\t\t\t\t\t\tfound = true;\n
\t\t\t\t\t\ttl.removeItem(i);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tif (found) {\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t};\n
\n
\tthis.numberOfItems = 0;\n
\tthis.clear = function() {\n
\t\tthis.numberOfItems = 0;\n
\t\tthis._xforms = [];\n
\t};\n
\n
\tthis.initialize = function(newItem) {\n
\t\tthis.numberOfItems = 1;\n
\t\tthis._removeFromOtherLists(newItem);\n
\t\tthis._xforms = [newItem];\n
\t};\n
\n
\tthis.getItem = function(index) {\n
\t\tif (index < this.numberOfItems && index >= 0) {\n
\t\t\treturn this._xforms[index];\n
\t\t}\n
\t\tthrow {code: 1}; // DOMException with code=INDEX_SIZE_ERR\n
\t};\n
\n
\tthis.insertItemBefore = function(newItem, index) {\n
\t\tvar retValue = null;\n
\t\tif (index >= 0) {\n
\t\t\tif (index < this.numberOfItems) {\n
\t\t\t\tthis._removeFromOtherLists(newItem);\n
\t\t\t\tvar newxforms = new Array(this.numberOfItems + 1);\n
\t\t\t\t// TODO: use array copying and slicing\n
\t\t\t\tvar i;\n
\t\t\t\tfor (i = 0; i < index; ++i) {\n
\t\t\t\t\tnewxforms[i] = this._xforms[i];\n
\t\t\t\t}\n
\t\t\t\tnewxforms[i] = newItem;\n
\t\t\t\tvar j;\n
\t\t\t\tfor (j = i+1; i < this.numberOfItems; ++j, ++i) {\n
\t\t\t\t\tnewxforms[j] = this._xforms[i];\n
\t\t\t\t}\n
\t\t\t\tthis.numberOfItems++;\n
\t\t\t\tthis._xforms = newxforms;\n
\t\t\t\tretValue = newItem;\n
\t\t\t\tthis._list._update();\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t\tretValue = this._list.appendItem(newItem);\n
\t\t\t}\n
\t\t}\n
\t\treturn retValue;\n
\t};\n
\n
\tthis.replaceItem = function(newItem, index) {\n
\t\tvar retValue = null;\n
\t\tif (index < this.numberOfItems && index >= 0) {\n
\t\t\tthis._removeFromOtherLists(newItem);\n
\t\t\tthis._xforms[index] = newItem;\n
\t\t\tretValue = newItem;\n
\t\t\tthis._list._update();\n
\t\t}\n
\t\treturn retValue;\n
\t};\n
\n
\tthis.removeItem = function(index) {\n
\t\tif (index < this.numberOfItems && index >= 0) {\n
\t\t\tvar retValue = this._xforms[index];\n
\t\t\tvar newxforms = new Array(this.numberOfItems - 1);\n
\t\t\tvar i, j;\n
\t\t\tfor (i = 0; i < index; ++i) {\n
\t\t\t\tnewxforms[i] = this._xforms[i];\n
\t\t\t}\n
\t\t\tfor (j = i; j < this.numberOfItems-1; ++j, ++i) {\n
\t\t\t\tnewxforms[j] = this._xforms[i+1];\n
\t\t\t}\n
\t\t\tthis.numberOfItems--;\n
\t\t\tthis._xforms = newxforms;\n
\t\t\tthis._list._update();\n
\t\t\treturn retValue;\n
\t\t}\n
\t\tthrow {code: 1}; // DOMException with code=INDEX_SIZE_ERR\n
\t};\n
\n
\tthis.appendItem = function(newItem) {\n
\t\tthis._removeFromOtherLists(newItem);\n
\t\tthis._xforms.push(newItem);\n
\t\tthis.numberOfItems++;\n
\t\tthis._list._update();\n
\t\treturn newItem;\n
\t};\n
};\n
\n
\n
svgedit.transformlist.resetListMap = function() {\n
\tlistMap_ = {};\n
};\n
\n
/**\n
 * Removes transforms of the given element from the map.\n
 * Parameters:\n
 * elem - a DOM Element\n
 */\n
svgedit.transformlist.removeElementFromListMap = function(elem) {\n
\tif (elem.id && listMap_[elem.id]) {\n
\t\tdelete listMap_[elem.id];\n
\t}\n
};\n
\n
// Function: getTransformList\n
// Returns an object that behaves like a SVGTransformList for the given DOM element\n
//\n
// Parameters:\n
// elem - DOM element to get a transformlist from\n
svgedit.transformlist.getTransformList = function(elem) {\n
\tif (!svgedit.browser.supportsNativeTransformLists()) {\n
\t\tvar id = elem.id || \'temp\';\n
\t\tvar t = listMap_[id];\n
\t\tif (!t || id === \'temp\') {\n
\t\t\tlistMap_[id] = new svgedit.transformlist.SVGTransformList(elem);\n
\t\t\tlistMap_[id]._init();\n
\t\t\tt = listMap_[id];\n
\t\t}\n
\t\treturn t;\n
\t}\n
\tif (elem.transform) {\n
\t\treturn elem.transform.baseVal;\n
\t}\n
\tif (elem.gradientTransform) {\n
\t\treturn elem.gradientTransform.baseVal;\n
\t}\n
\tif (elem.patternTransform) {\n
\t\treturn elem.patternTransform.baseVal;\n
\t}\n
\n
\treturn null;\n
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
            <value> <int>7871</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
