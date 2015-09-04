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
            <value> <string>ts40515059.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-eyedropper.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgedit, $*/\n
/*jslint vars: true, eqeq: true*/\n
/*\n
 * ext-eyedropper.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Jeff Schiller\n
 *\n
 */\n
\n
// Dependencies:\n
// 1) jQuery\n
// 2) history.js\n
// 3) svg_editor.js\n
// 4) svgcanvas.js\n
\n
svgEditor.addExtension("eyedropper", function(S) {\'use strict\';\n
\tvar // NS = svgedit.NS,\n
\t\t// svgcontent = S.svgcontent,\n
\t\t// svgdoc = S.svgroot.parentNode.ownerDocument,\n
\t\tsvgCanvas = svgEditor.canvas,\n
\t\tChangeElementCommand = svgedit.history.ChangeElementCommand,\n
\t\taddToHistory = function(cmd) { svgCanvas.undoMgr.addCommandToHistory(cmd); },\n
\t\tcurrentStyle = {\n
\t\t\tfillPaint: "red", fillOpacity: 1.0,\n
\t\t\tstrokePaint: "black", strokeOpacity: 1.0, \n
\t\t\tstrokeWidth: 5, strokeDashArray: null,\n
\t\t\topacity: 1.0,\n
\t\t\tstrokeLinecap: \'butt\',\n
\t\t\tstrokeLinejoin: \'miter\'\n
\t\t};\n
\n
\tfunction getStyle(opts) {\n
\t\t// if we are in eyedropper mode, we don\'t want to disable the eye-dropper tool\n
\t\tvar mode = svgCanvas.getMode();\n
\t\tif (mode == "eyedropper") {return;}\n
\n
\t\tvar elem = null;\n
\t\tvar tool = $(\'#tool_eyedropper\');\n
\t\t// enable-eye-dropper if one element is selected\n
\t\tif (!opts.multiselected && opts.elems[0] &&\n
\t\t\t$.inArray(opts.elems[0].nodeName, [\'svg\', \'g\', \'use\']) === -1\n
\t\t) {\n
\t\t\telem = opts.elems[0];\n
\t\t\ttool.removeClass(\'disabled\');\n
\t\t\t// grab the current style\n
\t\t\tcurrentStyle.fillPaint = elem.getAttribute("fill") || "black";\n
\t\t\tcurrentStyle.fillOpacity = elem.getAttribute("fill-opacity") || 1.0;\n
\t\t\tcurrentStyle.strokePaint = elem.getAttribute("stroke");\n
\t\t\tcurrentStyle.strokeOpacity = elem.getAttribute("stroke-opacity") || 1.0;\n
\t\t\tcurrentStyle.strokeWidth = elem.getAttribute("stroke-width");\n
\t\t\tcurrentStyle.strokeDashArray = elem.getAttribute("stroke-dasharray");\n
\t\t\tcurrentStyle.strokeLinecap = elem.getAttribute("stroke-linecap");\n
\t\t\tcurrentStyle.strokeLinejoin = elem.getAttribute("stroke-linejoin");\n
\t\t\tcurrentStyle.opacity = elem.getAttribute("opacity") || 1.0;\n
\t\t}\n
\t\t// disable eye-dropper tool\n
\t\telse {\n
\t\t\ttool.addClass(\'disabled\');\n
\t\t}\n
\n
\t}\n
\t\n
\treturn {\n
\t\tname: "eyedropper",\n
\t\tsvgicons: svgEditor.curConfig.extPath + "eyedropper-icon.xml",\n
\t\tbuttons: [{\n
\t\t\tid: "tool_eyedropper",\n
\t\t\ttype: "mode",\n
\t\t\ttitle: "Eye Dropper Tool",\n
\t\t\tkey: "I",\n
\t\t\tevents: {\n
\t\t\t\t"click": function() {\n
\t\t\t\t\tsvgCanvas.setMode("eyedropper");\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}],\n
\t\t\n
\t\t// if we have selected an element, grab its paint and enable the eye dropper button\n
\t\tselectedChanged: getStyle,\n
\t\telementChanged: getStyle,\n
\t\t\n
\t\tmouseDown: function(opts) {\n
\t\t\tvar mode = svgCanvas.getMode();\n
\t\t\tif (mode == "eyedropper") {\n
\t\t\t\tvar e = opts.event;\n
\t\t\t\tvar target = e.target;\n
\t\t\t\tif ($.inArray(target.nodeName, [\'svg\', \'g\', \'use\']) === -1) {\n
\t\t\t\t\tvar changes = {};\n
\n
\t\t\t\t\tvar change = function(elem, attrname, newvalue) {\n
\t\t\t\t\t\tchanges[attrname] = elem.getAttribute(attrname);\n
\t\t\t\t\t\telem.setAttribute(attrname, newvalue);\n
\t\t\t\t\t};\n
\t\t\t\t\t\n
\t\t\t\t\tif (currentStyle.fillPaint) {change(target, "fill", currentStyle.fillPaint);}\n
\t\t\t\t\tif (currentStyle.fillOpacity) {change(target, "fill-opacity", currentStyle.fillOpacity);}\n
\t\t\t\t\tif (currentStyle.strokePaint) {change(target, "stroke", currentStyle.strokePaint);}\n
\t\t\t\t\tif (currentStyle.strokeOpacity) {change(target, "stroke-opacity", currentStyle.strokeOpacity);}\n
\t\t\t\t\tif (currentStyle.strokeWidth) {change(target, "stroke-width", currentStyle.strokeWidth);}\n
\t\t\t\t\tif (currentStyle.strokeDashArray) {change(target, "stroke-dasharray", currentStyle.strokeDashArray);}\n
\t\t\t\t\tif (currentStyle.opacity) {change(target, "opacity", currentStyle.opacity);}\n
\t\t\t\t\tif (currentStyle.strokeLinecap) {change(target, "stroke-linecap", currentStyle.strokeLinecap);}\n
\t\t\t\t\tif (currentStyle.strokeLinejoin) {change(target, "stroke-linejoin", currentStyle.strokeLinejoin);}\n
\t\t\t\t\t\n
\t\t\t\t\taddToHistory(new ChangeElementCommand(target, changes));\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t};\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3812</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
