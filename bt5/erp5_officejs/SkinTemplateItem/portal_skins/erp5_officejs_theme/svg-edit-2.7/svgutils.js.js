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
            <value> <string>svgutils.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgedit, unescape, DOMParser, ActiveXObject, getStrokedBBox*/\n
/*jslint vars: true, eqeq: true, bitwise: true, continue: true, forin: true*/\n
/**\n
 * Package: svgedit.utilities\n
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
// 3) svgtransformlist.js\n
// 4) units.js\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.utilities) {\n
\tsvgedit.utilities = {};\n
}\n
\n
// Constants\n
\n
// String used to encode base64.\n
var KEYSTR = \'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=\';\n
var NS = svgedit.NS;\n
\n
// Much faster than running getBBox() every time\n
var visElems = \'a,circle,ellipse,foreignObject,g,image,line,path,polygon,polyline,rect,svg,text,tspan,use\';\n
var visElems_arr = visElems.split(\',\');\n
//var hidElems = \'clipPath,defs,desc,feGaussianBlur,filter,linearGradient,marker,mask,metadata,pattern,radialGradient,stop,switch,symbol,title,textPath\';\n
\n
var editorContext_ = null;\n
var domdoc_ = null;\n
var domcontainer_ = null;\n
var svgroot_ = null;\n
\n
svgedit.utilities.init = function(editorContext) {\n
\teditorContext_ = editorContext;\n
\tdomdoc_ = editorContext.getDOMDocument();\n
\tdomcontainer_ = editorContext.getDOMContainer();\n
\tsvgroot_ = editorContext.getSVGRoot();\n
};\n
\n
// Function: svgedit.utilities.toXml\n
// Converts characters in a string to XML-friendly entities.\n
//\n
// Example: \'&\' becomes \'&amp;\'\n
//\n
// Parameters:\n
// str - The string to be converted\n
//\n
// Returns:\n
// The converted string\n
svgedit.utilities.toXml = function(str) {\n
\t// &apos; is ok in XML, but not HTML\n
\t// &gt; does not normally need escaping, though it can if within a CDATA expression (and preceded by "]]")\n
\treturn str.replace(/&/g, \'&amp;\').replace(/</g, \'&lt;\').replace(/>/g, \'&gt;\').replace(/"/g, \'&quot;\').replace(/\'/, \'&#x27;\');\n
};\n
\n
// Function: svgedit.utilities.fromXml\n
// Converts XML entities in a string to single characters.\n
// Example: \'&amp;\' becomes \'&\'\n
//\n
// Parameters:\n
// str - The string to be converted\n
//\n
// Returns:\n
// The converted string\n
svgedit.utilities.fromXml = function(str) {\n
\treturn $(\'<p/>\').html(str).text();\n
};\n
\n
// This code was written by Tyler Akins and has been placed in the\n
// public domain.  It would be nice if you left this header intact.\n
// Base64 code from Tyler Akins -- http://rumkin.com\n
\n
// schiller: Removed string concatenation in favour of Array.join() optimization,\n
//\t\t\t\talso precalculate the size of the array needed.\n
\n
// Function: svgedit.utilities.encode64\n
// Converts a string to base64\n
svgedit.utilities.encode64 = function(input) {\n
\t// base64 strings are 4/3 larger than the original string\n
\tinput = svgedit.utilities.encodeUTF8(input); // convert non-ASCII characters\n
\t// input = svgedit.utilities.convertToXMLReferences(input);\n
\tif (window.btoa) {\n
\t\treturn window.btoa(input); // Use native if available\n
  }\n
\tvar output = new Array( Math.floor( (input.length + 2) / 3 ) * 4 );\n
\tvar chr1, chr2, chr3;\n
\tvar enc1, enc2, enc3, enc4;\n
\tvar i = 0, p = 0;\n
\n
\tdo {\n
\t\tchr1 = input.charCodeAt(i++);\n
\t\tchr2 = input.charCodeAt(i++);\n
\t\tchr3 = input.charCodeAt(i++);\n
\n
\t\tenc1 = chr1 >> 2;\n
\t\tenc2 = ((chr1 & 3) << 4) | (chr2 >> 4);\n
\t\tenc3 = ((chr2 & 15) << 2) | (chr3 >> 6);\n
\t\tenc4 = chr3 & 63;\n
\n
\t\tif (isNaN(chr2)) {\n
\t\t\tenc3 = enc4 = 64;\n
\t\t} else if (isNaN(chr3)) {\n
\t\t\tenc4 = 64;\n
\t\t}\n
\n
\t\toutput[p++] = KEYSTR.charAt(enc1);\n
\t\toutput[p++] = KEYSTR.charAt(enc2);\n
\t\toutput[p++] = KEYSTR.charAt(enc3);\n
\t\toutput[p++] = KEYSTR.charAt(enc4);\n
\t} while (i < input.length);\n
\n
\treturn output.join(\'\');\n
};\n
\n
// Function: svgedit.utilities.decode64\n
// Converts a string from base64\n
svgedit.utilities.decode64 = function(input) {\n
\tif(window.atob) {\n
        return window.atob(input);\n
    }\n
\tvar output = \'\';\n
\tvar chr1, chr2, chr3 = \'\';\n
\tvar enc1, enc2, enc3, enc4 = \'\';\n
\tvar i = 0;\n
\n
\t// remove all characters that are not A-Z, a-z, 0-9, +, /, or =\n
\tinput = input.replace(/[^A-Za-z0-9\\+\\/\\=]/g, \'\');\n
\n
\tdo {\n
\t\tenc1 = KEYSTR.indexOf(input.charAt(i++));\n
\t\tenc2 = KEYSTR.indexOf(input.charAt(i++));\n
\t\tenc3 = KEYSTR.indexOf(input.charAt(i++));\n
\t\tenc4 = KEYSTR.indexOf(input.charAt(i++));\n
\n
\t\tchr1 = (enc1 << 2) | (enc2 >> 4);\n
\t\tchr2 = ((enc2 & 15) << 4) | (enc3 >> 2);\n
\t\tchr3 = ((enc3 & 3) << 6) | enc4;\n
\n
\t\toutput = output + String.fromCharCode(chr1);\n
\n
\t\tif (enc3 != 64) {\n
\t\t\toutput = output + String.fromCharCode(chr2);\n
\t\t}\n
\t\tif (enc4 != 64) {\n
\t\t\toutput = output + String.fromCharCode(chr3);\n
\t\t}\n
\n
\t\tchr1 = chr2 = chr3 = \'\';\n
\t\tenc1 = enc2 = enc3 = enc4 = \'\';\n
\n
\t} while (i < input.length);\n
\treturn unescape(output);\n
};\n
\n
// based on http://phpjs.org/functions/utf8_encode\n
// codedread:does not seem to work with webkit-based browsers on OSX // Brettz9: please test again as function upgraded\n
svgedit.utilities.encodeUTF8 = function (argString) {\n
\t//return unescape(encodeURIComponent(input)); //may or may not work\n
  if (argString === null || typeof argString === \'undefined\') {\n
    return \'\';\n
  }\n
\n
  // .replace(/\\r\\n/g, "\\n").replace(/\\r/g, "\\n");\n
  var string = String(argString);\n
  var utftext = \'\',\n
    start, end, stringl = 0;\n
\n
  start = end = 0;\n
  stringl = string.length;\n
  var n;\n
  for (n = 0; n < stringl; n++) {\n
    var c1 = string.charCodeAt(n);\n
    var enc = null;\n
\n
    if (c1 < 128) {\n
      end++;\n
    } else if (c1 > 127 && c1 < 2048) {\n
      enc = String.fromCharCode(\n
        (c1 >> 6) | 192, (c1 & 63) | 128\n
      );\n
    } else if ((c1 & 0xF800) != 0xD800) {\n
      enc = String.fromCharCode(\n
        (c1 >> 12) | 224, ((c1 >> 6) & 63) | 128, (c1 & 63) | 128\n
      );\n
    } else {\n
      // surrogate pairs\n
      if ((c1 & 0xFC00) != 0xD800) {\n
        throw new RangeError(\'Unmatched trail surrogate at \' + n);\n
      }\n
      var c2 = string.charCodeAt(++n);\n
      if ((c2 & 0xFC00) != 0xDC00) {\n
        throw new RangeError(\'Unmatched lead surrogate at \' + (n - 1));\n
      }\n
      c1 = ((c1 & 0x3FF) << 10) + (c2 & 0x3FF) + 0x10000;\n
      enc = String.fromCharCode(\n
        (c1 >> 18) | 240, ((c1 >> 12) & 63) | 128, ((c1 >> 6) & 63) | 128, (c1 & 63) | 128\n
      );\n
    }\n
    if (enc !== null) {\n
      if (end > start) {\n
        utftext += string.slice(start, end);\n
      }\n
      utftext += enc;\n
      start = end = n + 1;\n
    }\n
  }\n
\n
  if (end > start) {\n
    utftext += string.slice(start, stringl);\n
  }\n
\n
  return utftext;\n
};\n
\n
// Function: svgedit.utilities.convertToXMLReferences\n
// Converts a string to use XML references\n
svgedit.utilities.convertToXMLReferences = function(input) {\n
\tvar n,\n
\t\toutput = \'\';\n
\tfor (n = 0; n < input.length; n++){\n
\t\tvar c = input.charCodeAt(n);\n
\t\tif (c < 128) {\n
\t\t\toutput += input[n];\n
\t\t} else if(c > 127) {\n
\t\t\toutput += (\'&#\' + c + \';\');\n
\t\t}\n
\t}\n
\treturn output;\n
};\n
\n
// Function: svgedit.utilities.text2xml\n
// Cross-browser compatible method of converting a string to an XML tree\n
// found this function here: http://groups.google.com/group/jquery-dev/browse_thread/thread/c6d11387c580a77f\n
svgedit.utilities.text2xml = function(sXML) {\n
\tif(sXML.indexOf(\'<svg:svg\') >= 0) {\n
\t\tsXML = sXML.replace(/<(\\/?)svg:/g, \'<$1\').replace(\'xmlns:svg\', \'xmlns\');\n
\t}\n
\n
\tvar out, dXML;\n
\ttry{\n
\t\tdXML = (window.DOMParser)?new DOMParser():new ActiveXObject(\'Microsoft.XMLDOM\');\n
\t\tdXML.async = false;\n
\t} catch(e){\n
\t\tthrow new Error(\'XML Parser could not be instantiated\');\n
\t}\n
\ttry{\n
\t\tif (dXML.loadXML) {\n
\t\t\tout = (dXML.loadXML(sXML)) ? dXML : false;\n
\t\t}\n
\t\telse {\n
\t\t\tout = dXML.parseFromString(sXML, \'text/xml\');\n
\t\t}\n
\t}\n
\tcatch(e2){ throw new Error(\'Error parsing XML string\'); }\n
\treturn out;\n
};\n
\n
// Function: svgedit.utilities.bboxToObj\n
// Converts a SVGRect into an object.\n
// \n
// Parameters:\n
// bbox - a SVGRect\n
// \n
// Returns:\n
// An object with properties names x, y, width, height.\n
svgedit.utilities.bboxToObj = function(bbox) {\n
\treturn {\n
\t\tx: bbox.x,\n
\t\ty: bbox.y,\n
\t\twidth: bbox.width,\n
\t\theight: bbox.height\n
\t};\n
};\n
\n
// Function: svgedit.utilities.walkTree\n
// Walks the tree and executes the callback on each element in a top-down fashion\n
//\n
// Parameters:\n
// elem - DOM element to traverse\n
// cbFn - Callback function to run on each element\n
svgedit.utilities.walkTree = function(elem, cbFn){\n
\tif (elem && elem.nodeType == 1) {\n
\t\tcbFn(elem);\n
\t\tvar i = elem.childNodes.length;\n
\t\twhile (i--) {\n
\t\t\tsvgedit.utilities.walkTree(elem.childNodes.item(i), cbFn);\n
\t\t}\n
\t}\n
};\n
\n
// Function: svgedit.utilities.walkTreePost\n
// Walks the tree and executes the callback on each element in a depth-first fashion\n
// TODO: FIXME: Shouldn\'t this be calling walkTreePost?\n
//\n
// Parameters:\n
// elem - DOM element to traverse\n
// cbFn - Callback function to run on each element\n
svgedit.utilities.walkTreePost = function(elem, cbFn) {\n
\tif (elem && elem.nodeType == 1) {\n
\t\tvar i = elem.childNodes.length;\n
\t\twhile (i--) {\n
\t\t\tsvgedit.utilities.walkTree(elem.childNodes.item(i), cbFn);\n
\t\t}\n
\t\tcbFn(elem);\n
\t}\n
};\n
\n
// Function: svgedit.utilities.getUrlFromAttr\n
// Extracts the URL from the url(...) syntax of some attributes.\n
// Three variants:\n
//  * <circle fill="url(someFile.svg#foo)" />\n
//  * <circle fill="url(\'someFile.svg#foo\')" />\n
//  * <circle fill=\'url("someFile.svg#foo")\' />\n
//\n
// Parameters:\n
// attrVal - The attribute value as a string\n
//\n
// Returns:\n
// String with just the URL, like someFile.svg#foo\n
svgedit.utilities.getUrlFromAttr = function(attrVal) {\n
\tif (attrVal) {\n
\t\t// url("#somegrad")\n
\t\tif (attrVal.indexOf(\'url("\') === 0) {\n
\t\t\treturn attrVal.substring(5, attrVal.indexOf(\'"\',6));\n
\t\t}\n
\t\t// url(\'#somegrad\')\n
\t\tif (attrVal.indexOf("url(\'") === 0) {\n
\t\t\treturn attrVal.substring(5, attrVal.indexOf("\'",6));\n
\t\t}\n
\t\tif (attrVal.indexOf("url(") === 0) {\n
\t\t\treturn attrVal.substring(4, attrVal.indexOf(\')\'));\n
\t\t}\n
\t}\n
\treturn null;\n
};\n
\n
// Function: svgedit.utilities.getHref\n
// Returns the given element\'s xlink:href value\n
svgedit.utilities.getHref = function(elem) {\n
\treturn elem.getAttributeNS(NS.XLINK, \'href\');\n
};\n
\n
// Function: svgedit.utilities.setHref\n
// Sets the given element\'s xlink:href value\n
svgedit.utilities.setHref = function(elem, val) {\n
\telem.setAttributeNS(NS.XLINK, \'xlink:href\', val);\n
};\n
\n
// Function: findDefs\n
//\n
// Returns:\n
// The document\'s <defs> element, create it first if necessary\n
svgedit.utilities.findDefs = function() {\n
\tvar svgElement = editorContext_.getSVGContent();\n
\tvar defs = svgElement.getElementsByTagNameNS(NS.SVG, \'defs\');\n
\tif (defs.length > 0) {\n
\t\tdefs = defs[0];\n
\t} else {\n
\t\tdefs = svgElement.ownerDocument.createElementNS(NS.SVG, \'defs\');\n
\t\tif (svgElement.firstChild) {\n
\t\t\t// first child is a comment, so call nextSibling\n
\t\t\tsvgElement.insertBefore(defs, svgElement.firstChild.nextSibling);\n
\t\t} else {\n
\t\t\tsvgElement.appendChild(defs);\n
\t\t}\n
\t}\n
\treturn defs;\n
};\n
\n
// TODO(codedread): Consider moving the next to functions to bbox.js\n
\n
// Function: svgedit.utilities.getPathBBox\n
// Get correct BBox for a path in Webkit\n
// Converted from code found here:\n
// http://blog.hackers-cafe.net/2009/06/how-to-calculate-bezier-curves-bounding.html\n
//\n
// Parameters:\n
// path - The path DOM element to get the BBox for\n
//\n
// Returns:\n
// A BBox-like object\n
svgedit.utilities.getPathBBox = function(path) {\n
\tvar seglist = path.pathSegList;\n
\tvar tot = seglist.numberOfItems;\n
\n
\tvar bounds = [[], []];\n
\tvar start = seglist.getItem(0);\n
\tvar P0 = [start.x, start.y];\n
\n
\tvar i;\n
\tfor (i = 0; i < tot; i++) {\n
\t\tvar seg = seglist.getItem(i);\n
\n
\t\tif(typeof seg.x === \'undefined\') {continue;}\n
\n
\t\t// Add actual points to limits\n
\t\tbounds[0].push(P0[0]);\n
\t\tbounds[1].push(P0[1]);\n
\n
\t\tif(seg.x1) {\n
\t\t\tvar P1 = [seg.x1, seg.y1],\n
\t\t\t\tP2 = [seg.x2, seg.y2],\n
\t\t\t\tP3 = [seg.x, seg.y];\n
\n
\t\t\tvar j;\n
\t\t\tfor (j = 0; j < 2; j++) {\n
\n
\t\t\t\tvar calc = function(t) {\n
\t\t\t\t\treturn Math.pow(1-t,3) * P0[j]\n
\t\t\t\t\t\t+ 3 * Math.pow(1-t,2) * t * P1[j]\n
\t\t\t\t\t\t+ 3 * (1-t) * Math.pow(t, 2) * P2[j]\n
\t\t\t\t\t\t+ Math.pow(t,3) * P3[j];\n
\t\t\t\t};\n
\n
\t\t\t\tvar b = 6 * P0[j] - 12 * P1[j] + 6 * P2[j];\n
\t\t\t\tvar a = -3 * P0[j] + 9 * P1[j] - 9 * P2[j] + 3 * P3[j];\n
\t\t\t\tvar c = 3 * P1[j] - 3 * P0[j];\n
\n
\t\t\t\tif (a == 0) {\n
\t\t\t\t\tif (b == 0) {\n
\t\t\t\t\t\tcontinue;\n
\t\t\t\t\t}\n
\t\t\t\t\tvar t = -c / b;\n
\t\t\t\t\tif (0 < t && t < 1) {\n
\t\t\t\t\t\tbounds[j].push(calc(t));\n
\t\t\t\t\t}\n
\t\t\t\t\tcontinue;\n
\t\t\t\t}\n
\t\t\t\tvar b2ac = Math.pow(b,2) - 4 * c * a;\n
\t\t\t\tif (b2ac < 0) {continue;}\n
\t\t\t\tvar t1 = (-b + Math.sqrt(b2ac))/(2 * a);\n
\t\t\t\tif (0 < t1 && t1 < 1) {bounds[j].push(calc(t1));}\n
\t\t\t\tvar t2 = (-b - Math.sqrt(b2ac))/(2 * a);\n
\t\t\t\tif (0 < t2 && t2 < 1) {bounds[j].push(calc(t2));}\n
\t\t\t}\n
\t\t\tP0 = P3;\n
\t\t} else {\n
\t\t\tbounds[0].push(seg.x);\n
\t\t\tbounds[1].push(seg.y);\n
\t\t}\n
\t}\n
\n
\tvar x = Math.min.apply(null, bounds[0]);\n
\tvar w = Math.max.apply(null, bounds[0]) - x;\n
\tvar y = Math.min.apply(null, bounds[1]);\n
\tvar h = Math.max.apply(null, bounds[1]) - y;\n
\treturn {\n
\t\t\'x\': x,\n
\t\t\'y\': y,\n
\t\t\'width\': w,\n
\t\t\'height\': h\n
\t};\n
};\n
\n
// Function: groupBBFix\n
// Get the given/selected element\'s bounding box object, checking for\n
// horizontal/vertical lines (see issue 717)\n
// Note that performance is currently terrible, so some way to improve would\n
// be great.\n
//\n
// Parameters:\n
// selected - Container or <use> DOM element\n
function groupBBFix(selected) {\n
\tif(svgedit.browser.supportsHVLineContainerBBox()) {\n
\t\ttry { return selected.getBBox();} catch(e){}\n
\t}\n
\tvar ref = $.data(selected, \'ref\');\n
\tvar matched = null;\n
\tvar ret, copy;\n
\n
\tif(ref) {\n
\t\tcopy = $(ref).children().clone().attr(\'visibility\', \'hidden\');\n
\t\t$(svgroot_).append(copy);\n
\t\tmatched = copy.filter(\'line, path\');\n
\t} else {\n
\t\tmatched = $(selected).find(\'line, path\');\n
\t}\n
\n
\tvar issue = false;\n
\tif(matched.length) {\n
\t\tmatched.each(function() {\n
\t\t\tvar bb = this.getBBox();\n
\t\t\tif(!bb.width || !bb.height) {\n
\t\t\t\tissue = true;\n
\t\t\t}\n
\t\t});\n
\t\tif(issue) {\n
\t\t\tvar elems = ref ? copy : $(selected).children();\n
\t\t\tret = getStrokedBBox(elems); // getStrokedBBox defined in svgcanvas\n
\t\t} else {\n
\t\t\tret = selected.getBBox();\n
\t\t}\n
\t} else {\n
\t\tret = selected.getBBox();\n
\t}\n
\tif(ref) {\n
\t\tcopy.remove();\n
\t}\n
\treturn ret;\n
}\n
\n
// Function: svgedit.utilities.getBBox\n
// Get the given/selected element\'s bounding box object, convert it to be more\n
// usable when necessary\n
//\n
// Parameters:\n
// elem - Optional DOM element to get the BBox for\n
svgedit.utilities.getBBox = function(elem) {\n
\tvar selected = elem || editorContext_.geSelectedElements()[0];\n
\tif (elem.nodeType != 1) {return null;}\n
\tvar ret = null;\n
\tvar elname = selected.nodeName;\n
\n
\tswitch ( elname ) {\n
\tcase \'text\':\n
\t\tif(selected.textContent === \'\') {\n
\t\t\tselected.textContent = \'a\'; // Some character needed for the selector to use.\n
\t\t\tret = selected.getBBox();\n
\t\t\tselected.textContent = \'\';\n
\t\t} else {\n
\t\t\ttry { ret = selected.getBBox();} catch(e){}\n
\t\t}\n
\t\tbreak;\n
\tcase \'path\':\n
\t\tif(!svgedit.browser.supportsPathBBox()) {\n
\t\t\tret = svgedit.utilities.getPathBBox(selected);\n
\t\t} else {\n
\t\t\ttry { ret = selected.getBBox();} catch(e2){}\n
\t\t}\n
\t\tbreak;\n
\tcase \'g\':\n
\tcase \'a\':\n
\t\tret = groupBBFix(selected);\n
\t\tbreak;\n
\tdefault:\n
\n
\t\tif(elname === \'use\') {\n
\t\t\tret = groupBBFix(selected, true);\n
\t\t}\n
\t\tif(elname === \'use\' || ( elname === \'foreignObject\' && svgedit.browser.isWebkit() ) ) {\n
\t\t\tif(!ret) {ret = selected.getBBox();}\n
\t\t\t// This is resolved in later versions of webkit, perhaps we should\n
\t\t\t// have a featured detection for correct \'use\' behavior?\n
\t\t\t// ——————————\n
\t\t\t//if(!svgedit.browser.isWebkit()) {\n
\t\t\t\tvar bb = {};\n
\t\t\t\tbb.width = ret.width;\n
\t\t\t\tbb.height = ret.height;\n
\t\t\t\tbb.x = ret.x + parseFloat(selected.getAttribute(\'x\')||0);\n
\t\t\t\tbb.y = ret.y + parseFloat(selected.getAttribute(\'y\')||0);\n
\t\t\t\tret = bb;\n
\t\t\t//}\n
\t\t} else if(~visElems_arr.indexOf(elname)) {\n
\t\t\ttry { ret = selected.getBBox();}\n
\t\t\tcatch(e3) {\n
\t\t\t\t// Check if element is child of a foreignObject\n
\t\t\t\tvar fo = $(selected).closest(\'foreignObject\');\n
\t\t\t\tif(fo.length) {\n
\t\t\t\t\ttry {\n
\t\t\t\t\t\tret = fo[0].getBBox();\n
\t\t\t\t\t} catch(e4) {\n
\t\t\t\t\t\tret = null;\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tret = null;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
\tif(ret) {\n
\t\tret = svgedit.utilities.bboxToObj(ret);\n
\t}\n
\n
\t// get the bounding box from the DOM (which is in that element\'s coordinate system)\n
\treturn ret;\n
};\n
\n
// Function: svgedit.utilities.getRotationAngle\n
// Get the rotation angle of the given/selected DOM element\n
//\n
// Parameters:\n
// elem - Optional DOM element to get the angle for\n
// to_rad - Boolean that when true returns the value in radians rather than degrees\n
//\n
// Returns:\n
// Float with the angle in degrees or radians\n
svgedit.utilities.getRotationAngle = function(elem, to_rad) {\n
\tvar selected = elem || editorContext_.getSelectedElements()[0];\n
\t// find the rotation transform (if any) and set it\n
\tvar tlist = svgedit.transformlist.getTransformList(selected);\n
\tif(!tlist) {return 0;} // <svg> elements have no tlist\n
\tvar N = tlist.numberOfItems;\n
\tvar i;\n
\tfor (i = 0; i < N; ++i) {\n
\t\tvar xform = tlist.getItem(i);\n
\t\tif (xform.type == 4) {\n
\t\t\treturn to_rad ? xform.angle * Math.PI / 180.0 : xform.angle;\n
\t\t}\n
\t}\n
\treturn 0.0;\n
};\n
\n
// Function getRefElem\n
// Get the reference element associated with the given attribute value\n
//\n
// Parameters:\n
// attrVal - The attribute value as a string\n
svgedit.utilities.getRefElem = function(attrVal) {\n
\treturn svgedit.utilities.getElem(svgedit.utilities.getUrlFromAttr(attrVal).substr(1));\n
};\n
\n
// Function: getElem\n
// Get a DOM element by ID within the SVG root element.\n
//\n
// Parameters:\n
// id - String with the element\'s new ID\n
if (svgedit.browser.supportsSelectors()) {\n
\tsvgedit.utilities.getElem = function(id) {\n
\t\t// querySelector lookup\n
\t\treturn svgroot_.querySelector(\'#\'+id);\n
\t};\n
} else if (svgedit.browser.supportsXpath()) {\n
\tsvgedit.utilities.getElem = function(id) {\n
\t\t// xpath lookup\n
\t\treturn domdoc_.evaluate(\n
\t\t\t\'svg:svg[@id="svgroot"]//svg:*[@id="\'+id+\'"]\',\n
\t\t\tdomcontainer_,\n
\t\t\tfunction() { return svgedit.NS.SVG; },\n
\t\t\t9,\n
\t\t\tnull).singleNodeValue;\n
\t};\n
} else {\n
\tsvgedit.utilities.getElem = function(id) {\n
\t\t// jQuery lookup: twice as slow as xpath in FF\n
\t\treturn $(svgroot_).find(\'[id=\' + id + \']\')[0];\n
\t};\n
}\n
\n
// Function: assignAttributes\n
// Assigns multiple attributes to an element.\n
//\n
// Parameters: \n
// node - DOM element to apply new attribute values to\n
// attrs - Object with attribute keys/values\n
// suspendLength - Optional integer of milliseconds to suspend redraw\n
// unitCheck - Boolean to indicate the need to use svgedit.units.setUnitAttr\n
svgedit.utilities.assignAttributes = function(node, attrs, suspendLength, unitCheck) {\n
\tif(!suspendLength) {suspendLength = 0;}\n
\t// Opera has a problem with suspendRedraw() apparently\n
\tvar handle = null;\n
\tif (!svgedit.browser.isOpera()) {svgroot_.suspendRedraw(suspendLength);}\n
\n
\tvar i;\n
\tfor (i in attrs) {\n
\t\tvar ns = (i.substr(0,4) === \'xml:\' ? NS.XML :\n
\t\t\ti.substr(0,6) === \'xlink:\' ? NS.XLINK : null);\n
\n
\t\tif(ns) {\n
\t\t\tnode.setAttributeNS(ns, i, attrs[i]);\n
\t\t} else if(!unitCheck) {\n
\t\t\tnode.setAttribute(i, attrs[i]);\n
\t\t} else {\n
\t\t\tsvgedit.units.setUnitAttr(node, i, attrs[i]);\n
\t\t}\n
\t}\n
\tif (!svgedit.browser.isOpera()) {svgroot_.unsuspendRedraw(handle);}\n
};\n
\n
// Function: cleanupElement\n
// Remove unneeded (default) attributes, makes resulting SVG smaller\n
//\n
// Parameters:\n
// element - DOM element to clean up\n
svgedit.utilities.cleanupElement = function(element) {\n
\tvar handle = svgroot_.suspendRedraw(60);\n
\tvar defaults = {\n
\t\t\'fill-opacity\':1,\n
\t\t\'stop-opacity\':1,\n
\t\t\'opacity\':1,\n
\t\t\'stroke\':\'none\',\n
\t\t\'stroke-dasharray\':\'none\',\n
\t\t\'stroke-linejoin\':\'miter\',\n
\t\t\'stroke-linecap\':\'butt\',\n
\t\t\'stroke-opacity\':1,\n
\t\t\'stroke-width\':1,\n
\t\t\'rx\':0,\n
\t\t\'ry\':0\n
\t};\n
\n
\tvar attr;\n
\tfor (attr in defaults) {\n
\t\tvar val = defaults[attr];\n
\t\tif(element.getAttribute(attr) == val) {\n
\t\t\telement.removeAttribute(attr);\n
\t\t}\n
\t}\n
\n
\tsvgroot_.unsuspendRedraw(handle);\n
};\n
\n
// Function: snapToGrid\n
// round value to for snapping\n
// NOTE: This function did not move to svgutils.js since it depends on curConfig.\n
svgedit.utilities.snapToGrid = function(value) {\n
\tvar stepSize = editorContext_.getSnappingStep();\n
\tvar unit = editorContext_.getBaseUnit();\n
\tif (unit !== "px") {\n
\t\tstepSize *= svgedit.units.getTypeMap()[unit];\n
\t}\n
\tvalue = Math.round(value/stepSize)*stepSize;\n
\treturn value;\n
};\n
\n
svgedit.utilities.preg_quote = function (str, delimiter) {\n
  // From: http://phpjs.org/functions\n
  return String(str).replace(new RegExp(\'[.\\\\\\\\+*?\\\\[\\\\^\\\\]$(){}=!<>|:\\\\\' + (delimiter || \'\') + \'-]\', \'g\'), \'\\\\$&\');\n
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
            <value> <int>19934</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
