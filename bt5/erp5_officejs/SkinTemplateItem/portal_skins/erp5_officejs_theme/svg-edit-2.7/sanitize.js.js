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
            <value> <string>sanitize.js</string> </value>
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
 * Package: svgedit.sanitize\n
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
// 3) svgutils.js\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.sanitize) {\n
  svgedit.sanitize = {};\n
}\n
\n
var NS = svgedit.NS,\n
  REVERSE_NS = svgedit.getReverseNS();\n
\n
// this defines which elements and attributes that we support\n
var svgWhiteList_ = {\n
  // SVG Elements\n
  "a": ["class", "clip-path", "clip-rule", "fill", "fill-opacity", "fill-rule", "filter", "id", "mask", "opacity", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform", "xlink:href", "xlink:title"],\n
  "circle": ["class", "clip-path", "clip-rule", "cx", "cy", "fill", "fill-opacity", "fill-rule", "filter", "id", "mask", "opacity", "r", "requiredFeatures", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform"],\n
  "clipPath": ["class", "clipPathUnits", "id"],\n
  "defs": [],\n
  "style" : ["type"],\n
  "desc": [],\n
  "ellipse": ["class", "clip-path", "clip-rule", "cx", "cy", "fill", "fill-opacity", "fill-rule", "filter", "id", "mask", "opacity", "requiredFeatures", "rx", "ry", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform"],\n
  "feGaussianBlur": ["class", "color-interpolation-filters", "id", "requiredFeatures", "stdDeviation"],\n
  "filter": ["class", "color-interpolation-filters", "filterRes", "filterUnits", "height", "id", "primitiveUnits", "requiredFeatures", "width", "x", "xlink:href", "y"],\n
  "foreignObject": ["class", "font-size", "height", "id", "opacity", "requiredFeatures", "style", "transform", "width", "x", "y"],\n
  "g": ["class", "clip-path", "clip-rule", "id", "display", "fill", "fill-opacity", "fill-rule", "filter", "mask", "opacity", "requiredFeatures", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform", "font-family", "font-size", "font-style", "font-weight", "text-anchor"],\n
  "image": ["class", "clip-path", "clip-rule", "filter", "height", "id", "mask", "opacity", "requiredFeatures", "style", "systemLanguage", "transform", "width", "x", "xlink:href", "xlink:title", "y"],\n
  "line": ["class", "clip-path", "clip-rule", "fill", "fill-opacity", "fill-rule", "filter", "id", "marker-end", "marker-mid", "marker-start", "mask", "opacity", "requiredFeatures", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform", "x1", "x2", "y1", "y2"],\n
  "linearGradient": ["class", "id", "gradientTransform", "gradientUnits", "requiredFeatures", "spreadMethod", "systemLanguage", "x1", "x2", "xlink:href", "y1", "y2"],\n
  "marker": ["id", "class", "markerHeight", "markerUnits", "markerWidth", "orient", "preserveAspectRatio", "refX", "refY", "systemLanguage", "viewBox"],\n
  "mask": ["class", "height", "id", "maskContentUnits", "maskUnits", "width", "x", "y"],\n
  "metadata": ["class", "id"],\n
  "path": ["class", "clip-path", "clip-rule", "d", "fill", "fill-opacity", "fill-rule", "filter", "id", "marker-end", "marker-mid", "marker-start", "mask", "opacity", "requiredFeatures", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform"],\n
  "pattern": ["class", "height", "id", "patternContentUnits", "patternTransform", "patternUnits", "requiredFeatures", "style", "systemLanguage", "viewBox", "width", "x", "xlink:href", "y"],\n
  "polygon": ["class", "clip-path", "clip-rule", "id", "fill", "fill-opacity", "fill-rule", "filter", "id", "class", "marker-end", "marker-mid", "marker-start", "mask", "opacity", "points", "requiredFeatures", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform"],\n
  "polyline": ["class", "clip-path", "clip-rule", "id", "fill", "fill-opacity", "fill-rule", "filter", "marker-end", "marker-mid", "marker-start", "mask", "opacity", "points", "requiredFeatures", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform"],\n
  "radialGradient": ["class", "cx", "cy", "fx", "fy", "gradientTransform", "gradientUnits", "id", "r", "requiredFeatures", "spreadMethod", "systemLanguage", "xlink:href"],\n
  "rect": ["class", "clip-path", "clip-rule", "fill", "fill-opacity", "fill-rule", "filter", "height", "id", "mask", "opacity", "requiredFeatures", "rx", "ry", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform", "width", "x", "y"],\n
  "stop": ["class", "id", "offset", "requiredFeatures", "stop-color", "stop-opacity", "style", "systemLanguage"],\n
  "svg": ["class", "clip-path", "clip-rule", "filter", "id", "height", "mask", "preserveAspectRatio", "requiredFeatures", "style", "systemLanguage", "viewBox", "width", "x", "xmlns", "xmlns:se", "xmlns:xlink", "y"],\n
  "switch": ["class", "id", "requiredFeatures", "systemLanguage"],\n
  "symbol": ["class", "fill", "fill-opacity", "fill-rule", "filter", "font-family", "font-size", "font-style", "font-weight", "id", "opacity", "preserveAspectRatio", "requiredFeatures", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "transform", "viewBox"],\n
  "text": ["class", "clip-path", "clip-rule", "fill", "fill-opacity", "fill-rule", "filter", "font-family", "font-size", "font-style", "font-weight", "id", "mask", "opacity", "requiredFeatures", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "text-anchor", "transform", "x", "xml:space", "y"],\n
  "textPath": ["class", "id", "method", "requiredFeatures", "spacing", "startOffset", "style", "systemLanguage", "transform", "xlink:href"],\n
  "title": [],\n
  "tspan": ["class", "clip-path", "clip-rule", "dx", "dy", "fill", "fill-opacity", "fill-rule", "filter", "font-family", "font-size", "font-style", "font-weight", "id", "mask", "opacity", "requiredFeatures", "rotate", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "systemLanguage", "text-anchor", "textLength", "transform", "x", "xml:space", "y"],\n
  "use": ["class", "clip-path", "clip-rule", "fill", "fill-opacity", "fill-rule", "filter", "height", "id", "mask", "stroke", "stroke-dasharray", "stroke-dashoffset", "stroke-linecap", "stroke-linejoin", "stroke-miterlimit", "stroke-opacity", "stroke-width", "style", "transform", "width", "x", "xlink:href", "y"],\n
\n
  // MathML Elements\n
  "annotation": ["encoding"],\n
  "annotation-xml": ["encoding"],\n
  "maction": ["actiontype", "other", "selection"],\n
  "math": ["class", "id", "display", "xmlns"],\n
  "menclose": ["notation"],\n
  "merror": [],\n
  "mfrac": ["linethickness"],\n
  "mi": ["mathvariant"],\n
  "mmultiscripts": [],\n
  "mn": [],\n
  "mo": ["fence", "lspace", "maxsize", "minsize", "rspace", "stretchy"],\n
  "mover": [],\n
  "mpadded": ["lspace", "width", "height", "depth", "voffset"],\n
  "mphantom": [],\n
  "mprescripts": [],\n
  "mroot": [],\n
  "mrow": ["xlink:href", "xlink:type", "xmlns:xlink"],\n
  "mspace": ["depth", "height", "width"],\n
  "msqrt": [],\n
  "mstyle": ["displaystyle", "mathbackground", "mathcolor", "mathvariant", "scriptlevel"],\n
  "msub": [],\n
  "msubsup": [],\n
  "msup": [],\n
  "mtable": ["align", "columnalign", "columnlines", "columnspacing", "displaystyle", "equalcolumns", "equalrows", "frame", "rowalign", "rowlines", "rowspacing", "width"],\n
  "mtd": ["columnalign", "columnspan", "rowalign", "rowspan"],\n
  "mtext": [],\n
  "mtr": ["columnalign", "rowalign"],\n
  "munder": [],\n
  "munderover": [],\n
  "none": [],\n
  "semantics": []\n
};\n
\n
// Produce a Namespace-aware version of svgWhitelist\n
var svgWhiteListNS_ = {};\n
$.each(svgWhiteList_, function(elt, atts){\n
  var attNS = {};\n
  $.each(atts, function(i, att){\n
    if (att.indexOf(\':\') >= 0) {\n
      var v = att.split(\':\');\n
      attNS[v[1]] = NS[(v[0]).toUpperCase()];\n
    } else {\n
      attNS[att] = att == \'xmlns\' ? NS.XMLNS : null;\n
    }\n
  });\n
  svgWhiteListNS_[elt] = attNS;\n
});\n
\n
// Function: svgedit.sanitize.sanitizeSvg\n
// Sanitizes the input node and its children\n
// It only keeps what is allowed from our whitelist defined above\n
//\n
// Parameters:\n
// node - The DOM element to be checked (we\'ll also check its children)\n
svgedit.sanitize.sanitizeSvg = function(node) {\n
  // Cleanup text nodes\n
  if (node.nodeType == 3) { // 3 == TEXT_NODE\n
    // Trim whitespace\n
    node.nodeValue = node.nodeValue.replace(/^\\s+|\\s+$/g, \'\');\n
    // Remove if empty\n
    if (node.nodeValue.length === 0) {\n
      node.parentNode.removeChild(node);\n
    }\n
  }\n
\n
  // We only care about element nodes.\n
  // Automatically return for all non-element nodes, such as comments, etc.\n
  if (node.nodeType != 1) { // 1 == ELEMENT_NODE\n
    return;\n
  }\n
\n
  var doc = node.ownerDocument;\n
  var parent = node.parentNode;\n
  // can parent ever be null here?  I think the root node\'s parent is the document...\n
  if (!doc || !parent) {\n
    return;\n
  }\n
\n
  var allowedAttrs = svgWhiteList_[node.nodeName];\n
  var allowedAttrsNS = svgWhiteListNS_[node.nodeName];\n
  var i;\n
  // if this element is supported, sanitize it\n
  if (typeof allowedAttrs !== \'undefined\') {\n
\n
    var seAttrs = [];\n
    i = node.attributes.length;\n
    while (i--) {\n
      // if the attribute is not in our whitelist, then remove it\n
      // could use jQuery\'s inArray(), but I don\'t know if that\'s any better\n
      var attr = node.attributes.item(i);\n
      var attrName = attr.nodeName;\n
      var attrLocalName = attr.localName;\n
      var attrNsURI = attr.namespaceURI;\n
      // Check that an attribute with the correct localName in the correct namespace is on \n
      // our whitelist or is a namespace declaration for one of our allowed namespaces\n
      if (!(allowedAttrsNS.hasOwnProperty(attrLocalName) && attrNsURI == allowedAttrsNS[attrLocalName] && attrNsURI != NS.XMLNS) &&\n
        !(attrNsURI == NS.XMLNS && REVERSE_NS[attr.nodeValue]) )\n
      {\n
        // TODO(codedread): Programmatically add the se: attributes to the NS-aware whitelist.\n
        // Bypassing the whitelist to allow se: prefixes.\n
        // Is there a more appropriate way to do this?\n
        if (attrName.indexOf(\'se:\') === 0) {\n
          seAttrs.push([attrName, attr.nodeValue]);\n
        }\n
        node.removeAttributeNS(attrNsURI, attrLocalName);\n
      }\n
\n
      // Add spaces before negative signs where necessary\n
      if (svgedit.browser.isGecko()) {\n
        switch (attrName) {\n
        case \'transform\':\n
        case \'gradientTransform\':\n
        case \'patternTransform\':\n
          var val = attr.nodeValue.replace(/(\\d)-/g, \'$1 -\');\n
          node.setAttribute(attrName, val);\n
          break;\n
        }\n
      }\n
\n
      // For the style attribute, rewrite it in terms of XML presentational attributes\n
      if (attrName == \'style\') {\n
        var props = attr.nodeValue.split(\';\'),\n
          p = props.length;\n
        while (p--) {\n
          var nv = props[p].split(\':\');\n
          var styleAttrName = $.trim(nv[0]);\n
          var styleAttrVal = $.trim(nv[1]);\n
          // Now check that this attribute is supported\n
          if (allowedAttrs.indexOf(styleAttrName) >= 0) {\n
            node.setAttribute(styleAttrName, styleAttrVal);\n
          }\n
        }\n
        node.removeAttribute(\'style\');\n
      }\n
    }\n
\n
    $.each(seAttrs, function(i, attr) {\n
      node.setAttributeNS(NS.SE, attr[0], attr[1]);\n
    });\n
\n
    // for some elements that have a xlink:href, ensure the URI refers to a local element\n
    // (but not for links)\n
    var href = svgedit.utilities.getHref(node);\n
    if (href &&\n
      [\'filter\', \'linearGradient\', \'pattern\',\n
      \'radialGradient\', \'textPath\', \'use\'].indexOf(node.nodeName) >= 0) {\n
      // TODO: we simply check if the first character is a #, is this bullet-proof?\n
      if (href[0] != \'#\') {\n
        // remove the attribute (but keep the element)\n
        svgedit.utilities.setHref(node, \'\');\n
        node.removeAttributeNS(NS.XLINK, \'href\');\n
      }\n
    }\n
\n
    // Safari crashes on a <use> without a xlink:href, so we just remove the node here\n
    if (node.nodeName == \'use\' && !svgedit.utilities.getHref(node)) {\n
      parent.removeChild(node);\n
      return;\n
    }\n
    // if the element has attributes pointing to a non-local reference,\n
    // need to remove the attribute\n
    $.each([\'clip-path\', \'fill\', \'filter\', \'marker-end\', \'marker-mid\', \'marker-start\', \'mask\', \'stroke\'], function(i, attr) {\n
      var val = node.getAttribute(attr);\n
      if (val) {\n
        val = svgedit.utilities.getUrlFromAttr(val);\n
        // simply check for first character being a \'#\'\n
        if (val && val[0] !== \'#\') {\n
          node.setAttribute(attr, \'\');\n
          node.removeAttribute(attr);\n
        }\n
      }\n
    });\n
\n
    // recurse to children\n
    i = node.childNodes.length;\n
    while (i--) { svgedit.sanitize.sanitizeSvg(node.childNodes.item(i)); }\n
  }\n
  // else (element not supported), remove it\n
  else {\n
    // remove all children from this node and insert them before this node\n
    // FIXME: in the case of animation elements this will hardly ever be correct\n
    var children = [];\n
    while (node.hasChildNodes()) {\n
      children.push(parent.insertBefore(node.firstChild, node));\n
    }\n
\n
    // remove this node from the document altogether\n
    parent.removeChild(node);\n
\n
    // call sanitizeSvg on each of those children\n
    i = children.length;\n
    while (i--) { svgedit.sanitize.sanitizeSvg(children[i]); }\n
  }\n
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
            <value> <int>14371</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
