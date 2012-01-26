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
            <value> <string>http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts27579717.97</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-eyedropper.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * ext-eyedropper.js\n
 *\n
 * Licensed under the Apache License, Version 2\n
 *\n
 * Copyright(c) 2010 Jeff Schiller\n
 *\n
 */\n
\n
svgEditor.addExtension("eyedropper", function(S) {\n
\t\tvar svgcontent = S.svgcontent,\n
\t\t\tsvgns = "http://www.w3.org/2000/svg",\n
\t\t\tsvgdoc = S.svgroot.parentNode.ownerDocument,\n
\t\t\tChangeElementCommand = svgCanvas.getPrivateMethods().ChangeElementCommand,\n
\t\t\taddToHistory = svgCanvas.getPrivateMethods().addCommandToHistory,\n
\t\t\tcurrentStyle = {fillPaint: "red", fillOpacity: 1.0,\n
\t\t\t\t\t\t\tstrokePaint: "black", strokeOpacity: 1.0, \n
\t\t\t\t\t\t\tstrokeWidth: 5, strokeDashArray: null,\n
\t\t\t\t\t\t\topacity: 1.0,\n
\t\t\t\t\t\t\tstrokeLinecap: \'butt\',\n
\t\t\t\t\t\t\tstrokeLinejoin: \'miter\',\n
\t\t\t\t\t\t\t};\n
\t\t\t\t\t\t\t\n
\t\tfunction getStyle(opts) {\n
\t\t\t// if we are in eyedropper mode, we don\'t want to disable the eye-dropper tool\n
\t\t\tvar mode = svgCanvas.getMode();\n
\t\t\tif (mode == "eyedropper") return;\n
\n
\t\t\tvar elem = null;\n
\t\t\tvar tool = $(\'#tool_eyedropper\');\n
\t\t\t// enable-eye-dropper if one element is selected\n
\t\t\tif (opts.elems.length == 1 && opts.elems[0] && \n
\t\t\t\t$.inArray(opts.elems[0].nodeName, [\'svg\', \'g\', \'use\']) == -1) \n
\t\t\t{\n
\t\t\t\telem = opts.elems[0];\n
\t\t\t\ttool.removeClass(\'disabled\');\n
\t\t\t\t// grab the current style\n
\t\t\t\tcurrentStyle.fillPaint = elem.getAttribute("fill") || "black";\n
\t\t\t\tcurrentStyle.fillOpacity = elem.getAttribute("fill-opacity") || 1.0;\n
\t\t\t\tcurrentStyle.strokePaint = elem.getAttribute("stroke");\n
\t\t\t\tcurrentStyle.strokeOpacity = elem.getAttribute("stroke-opacity") || 1.0;\n
\t\t\t\tcurrentStyle.strokeWidth = elem.getAttribute("stroke-width");\n
\t\t\t\tcurrentStyle.strokeDashArray = elem.getAttribute("stroke-dasharray");\n
\t\t\t\tcurrentStyle.strokeLinecap = elem.getAttribute("stroke-linecap");\n
\t\t\t\tcurrentStyle.strokeLinejoin = elem.getAttribute("stroke-linejoin");\n
\t\t\t\tcurrentStyle.opacity = elem.getAttribute("opacity") || 1.0;\n
\t\t\t}\n
\t\t\t// disable eye-dropper tool\n
\t\t\telse {\n
\t\t\t\ttool.addClass(\'disabled\');\n
\t\t\t}\n
\n
\t\t}\n
\t\t\n
\t\treturn {\n
\t\t\tname: "eyedropper",\n
\t\t\tsvgicons: "jquery/plugin/svg-editor/extensions/eyedropper-icon.xml",\n
\t\t\tbuttons: [{\n
\t\t\t\tid: "tool_eyedropper",\n
\t\t\t\ttype: "mode",\n
\t\t\t\ttitle: "Eye Dropper Tool",\n
\t\t\t\tevents: {\n
\t\t\t\t\t"click": function() {\n
\t\t\t\t\t\tsvgCanvas.setMode("eyedropper");\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}],\n
\t\t\t\n
\t\t\t// if we have selected an element, grab its paint and enable the eye dropper button\n
\t\t\tselectedChanged: getStyle,\n
\t\t\telementChanged: getStyle,\n
\t\t\t\n
\t\t\tmouseDown: function(opts) {\n
\t\t\t\tvar mode = svgCanvas.getMode();\n
\t\t\t\tif (mode == "eyedropper") {\n
\t\t\t\t\tvar e = opts.event;\n
\t\t\t\t\tvar target = e.target;\n
\t\t\t\t\tif ($.inArray(target.nodeName, [\'svg\', \'g\', \'use\']) == -1) {\n
\t\t\t\t\t\tvar changes = {};\n
\n
\t\t\t\t\t\tvar change = function(elem, attrname, newvalue) {\n
\t\t\t\t\t\t\tchanges[attrname] = elem.getAttribute(attrname);\n
\t\t\t\t\t\t\telem.setAttribute(attrname, newvalue);\n
\t\t\t\t\t\t};\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tif (currentStyle.fillPaint) \t\tchange(target, "fill", currentStyle.fillPaint);\n
\t\t\t\t\t\tif (currentStyle.fillOpacity) \t\tchange(target, "fill-opacity", currentStyle.fillOpacity);\n
\t\t\t\t\t\tif (currentStyle.strokePaint) \t\tchange(target, "stroke", currentStyle.strokePaint);\n
\t\t\t\t\t\tif (currentStyle.strokeOpacity) \tchange(target, "stroke-opacity", currentStyle.strokeOpacity);\n
\t\t\t\t\t\tif (currentStyle.strokeWidth) \t\tchange(target, "stroke-width", currentStyle.strokeWidth);\n
\t\t\t\t\t\tif (currentStyle.strokeDashArray) \tchange(target, "stroke-dasharray", currentStyle.strokeDashArray);\n
\t\t\t\t\t\tif (currentStyle.opacity) \t\t\tchange(target, "opacity", currentStyle.opacity);\n
\t\t\t\t\t\tif (currentStyle.strokeLinecap) \tchange(target, "stroke-linecap", currentStyle.strokeLinecap);\n
\t\t\t\t\t\tif (currentStyle.strokeLinejoin) \tchange(target, "stroke-linejoin", currentStyle.strokeLinejoin);\n
\t\t\t\t\t\t\n
\t\t\t\t\t\taddToHistory(new ChangeElementCommand(target, changes));\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t},\n
\t\t};\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3740</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
