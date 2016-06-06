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
            <value> <string>ext-php_savefile.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgCanvas, svgEditor*/\n
/*jslint regexp:true*/\n
// TODO: Might add support for "exportImage" custom\n
//   handler as in "ext-server_opensave.js" (and in savefile.php)\n
\n
svgEditor.addExtension("php_savefile", {\n
\tcallback: function() {\n
\t\t\'use strict\';\n
\t\tfunction getFileNameFromTitle () {\n
\t\t\tvar title = svgCanvas.getDocumentTitle();\n
\t\t\treturn $.trim(title);\n
\t\t}\n
\t\tvar save_svg_action = svgEditor.curConfig.extPath + \'savefile.php\';\n
\t\tsvgEditor.setCustomHandlers({\n
\t\t\tsave: function(win, data) {\n
\t\t\t\tvar svg = \'<?xml version="1.0" encoding="UTF-8"?>\\n\' + data,\n
\t\t\t\t\tfilename = getFileNameFromTitle();\n
\n
\t\t\t\t$.post(save_svg_action, {output_svg: svg, filename: filename});\n
\t\t\t}\n
\t\t});\n
\t}\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>695</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
