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
            <value> <string>browser.js</string> </value>
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
 * Package: svgedit.browser\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Jeff Schiller\n
 * Copyright(c) 2010 Alexis Deveria\n
 */\n
\n
// Dependencies:\n
// 1) jQuery (for $.alert())\n
\n
(function() {\'use strict\';\n
\n
if (!svgedit.browser) {\n
\tsvgedit.browser = {};\n
}\n
\n
// alias\n
var NS = svgedit.NS;\n
\n
var supportsSvg_ = (function() {\n
\treturn !!document.createElementNS && !!document.createElementNS(NS.SVG, \'svg\').createSVGRect;\n
}());\n
\n
svgedit.browser.supportsSvg = function() { return supportsSvg_; };\n
if(!svgedit.browser.supportsSvg()) {\n
\twindow.location = \'browser-not-supported.html\';\n
\treturn;\n
}\n
\n
var userAgent = navigator.userAgent;\n
var svg = document.createElementNS(NS.SVG, \'svg\');\n
\n
// Note: Browser sniffing should only be used if no other detection method is possible\n
var isOpera_ = !!window.opera;\n
var isWebkit_ = userAgent.indexOf(\'AppleWebKit\') >= 0;\n
var isGecko_ = userAgent.indexOf(\'Gecko/\') >= 0;\n
var isIE_ = userAgent.indexOf(\'MSIE\') >= 0;\n
var isChrome_ = userAgent.indexOf(\'Chrome/\') >= 0;\n
var isWindows_ = userAgent.indexOf(\'Windows\') >= 0;\n
var isMac_ = userAgent.indexOf(\'Macintosh\') >= 0;\n
var isTouch_ = \'ontouchstart\' in window;\n
\n
var supportsSelectors_ = (function() {\n
\treturn !!svg.querySelector;\n
}());\n
\n
var supportsXpath_ = (function() {\n
\treturn !!document.evaluate;\n
}());\n
\n
// segList functions (for FF1.5 and 2.0)\n
var supportsPathReplaceItem_ = (function() {\n
\tvar path = document.createElementNS(NS.SVG, \'path\');\n
\tpath.setAttribute(\'d\', \'M0,0 10,10\');\n
\tvar seglist = path.pathSegList;\n
\tvar seg = path.createSVGPathSegLinetoAbs(5,5);\n
\ttry {\n
\t\tseglist.replaceItem(seg, 0);\n
\t\treturn true;\n
\t} catch(err) {}\n
\treturn false;\n
}());\n
\n
var supportsPathInsertItemBefore_ = (function() {\n
\tvar path = document.createElementNS(NS.SVG, \'path\');\n
\tpath.setAttribute(\'d\', \'M0,0 10,10\');\n
\tvar seglist = path.pathSegList;\n
\tvar seg = path.createSVGPathSegLinetoAbs(5,5);\n
\ttry {\n
\t\tseglist.insertItemBefore(seg, 0);\n
\t\treturn true;\n
\t} catch(err) {}\n
\treturn false;\n
}());\n
\n
// text character positioning (for IE9)\n
var supportsGoodTextCharPos_ = (function() {\n
\tvar svgroot = document.createElementNS(NS.SVG, \'svg\');\n
\tvar svgcontent = document.createElementNS(NS.SVG, \'svg\');\n
\tdocument.documentElement.appendChild(svgroot);\n
\tsvgcontent.setAttribute(\'x\', 5);\n
\tsvgroot.appendChild(svgcontent);\n
\tvar text = document.createElementNS(NS.SVG, \'text\');\n
\ttext.textContent = \'a\';\n
\tsvgcontent.appendChild(text);\n
\tvar pos = text.getStartPositionOfChar(0).x;\n
\tdocument.documentElement.removeChild(svgroot);\n
\treturn (pos === 0);\n
}());\n
\n
var supportsPathBBox_ = (function() {\n
\tvar svgcontent = document.createElementNS(NS.SVG, \'svg\');\n
\tdocument.documentElement.appendChild(svgcontent);\n
\tvar path = document.createElementNS(NS.SVG, \'path\');\n
\tpath.setAttribute(\'d\', \'M0,0 C0,0 10,10 10,0\');\n
\tsvgcontent.appendChild(path);\n
\tvar bbox = path.getBBox();\n
\tdocument.documentElement.removeChild(svgcontent);\n
\treturn (bbox.height > 4 && bbox.height < 5);\n
}());\n
\n
// Support for correct bbox sizing on groups with horizontal/vertical lines\n
var supportsHVLineContainerBBox_ = (function() {\n
\tvar svgcontent = document.createElementNS(NS.SVG, \'svg\');\n
\tdocument.documentElement.appendChild(svgcontent);\n
\tvar path = document.createElementNS(NS.SVG, \'path\');\n
\tpath.setAttribute(\'d\', \'M0,0 10,0\');\n
\tvar path2 = document.createElementNS(NS.SVG, \'path\');\n
\tpath2.setAttribute(\'d\', \'M5,0 15,0\');\n
\tvar g = document.createElementNS(NS.SVG, \'g\');\n
\tg.appendChild(path);\n
\tg.appendChild(path2);\n
\tsvgcontent.appendChild(g);\n
\tvar bbox = g.getBBox();\n
\tdocument.documentElement.removeChild(svgcontent);\n
\t// Webkit gives 0, FF gives 10, Opera (correctly) gives 15\n
\treturn (bbox.width == 15);\n
}());\n
\n
var supportsEditableText_ = (function() {\n
\t// TODO: Find better way to check support for this\n
\treturn isOpera_;\n
}());\n
\n
var supportsGoodDecimals_ = (function() {\n
\t// Correct decimals on clone attributes (Opera < 10.5/win/non-en)\n
\tvar rect = document.createElementNS(NS.SVG, \'rect\');\n
\trect.setAttribute(\'x\', 0.1);\n
\tvar crect = rect.cloneNode(false);\n
\tvar retValue = (crect.getAttribute(\'x\').indexOf(\',\') == -1);\n
\tif(!retValue) {\n
\t\t$.alert(\'NOTE: This version of Opera is known to contain bugs in SVG-edit.\\n\'+\n
\t\t\'Please upgrade to the <a href="http://opera.com">latest version</a> in which the problems have been fixed.\');\n
\t}\n
\treturn retValue;\n
}());\n
\n
var supportsNonScalingStroke_ = (function() {\n
\tvar rect = document.createElementNS(NS.SVG, \'rect\');\n
\trect.setAttribute(\'style\', \'vector-effect:non-scaling-stroke\');\n
\treturn rect.style.vectorEffect === \'non-scaling-stroke\';\n
}());\n
\n
var supportsNativeSVGTransformLists_ = (function() {\n
\tvar rect = document.createElementNS(NS.SVG, \'rect\');\n
\tvar rxform = rect.transform.baseVal;\n
\tvar t1 = svg.createSVGTransform();\n
\trxform.appendItem(t1);\n
\treturn rxform.getItem(0) == t1;\n
}());\n
\n
// Public API\n
\n
svgedit.browser.isOpera = function() { return isOpera_; };\n
svgedit.browser.isWebkit = function() { return isWebkit_; };\n
svgedit.browser.isGecko = function() { return isGecko_; };\n
svgedit.browser.isIE = function() { return isIE_; };\n
svgedit.browser.isChrome = function() { return isChrome_; };\n
svgedit.browser.isWindows = function() { return isWindows_; };\n
svgedit.browser.isMac = function() { return isMac_; };\n
svgedit.browser.isTouch = function() { return isTouch_; };\n
\n
svgedit.browser.supportsSelectors = function() { return supportsSelectors_; };\n
svgedit.browser.supportsXpath = function() { return supportsXpath_; };\n
\n
svgedit.browser.supportsPathReplaceItem = function() { return supportsPathReplaceItem_; };\n
svgedit.browser.supportsPathInsertItemBefore = function() { return supportsPathInsertItemBefore_; };\n
svgedit.browser.supportsPathBBox = function() { return supportsPathBBox_; };\n
svgedit.browser.supportsHVLineContainerBBox = function() { return supportsHVLineContainerBBox_; };\n
svgedit.browser.supportsGoodTextCharPos = function() { return supportsGoodTextCharPos_; };\n
svgedit.browser.supportsEditableText = function() { return supportsEditableText_; };\n
svgedit.browser.supportsGoodDecimals = function() { return supportsGoodDecimals_; };\n
svgedit.browser.supportsNonScalingStroke = function() { return supportsNonScalingStroke_; };\n
svgedit.browser.supportsNativeTransformLists = function() { return supportsNativeSVGTransformLists_; };\n
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
            <value> <int>6298</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
