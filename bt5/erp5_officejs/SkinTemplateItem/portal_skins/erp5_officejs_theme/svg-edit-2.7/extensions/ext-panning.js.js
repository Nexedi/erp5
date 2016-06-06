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
            <value> <string>ext-panning.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string>/*globals svgEditor, svgCanvas*/\n
/*jslint eqeq: true*/\n
/*\n
 * ext-panning.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2013 Luis Aguirre\n
 *\n
 */\n
 \n
/* \n
\tThis is a very basic SVG-Edit extension to let tablet/mobile devices panning without problem\n
*/\n
\n
svgEditor.addExtension(\'ext-panning\', function() {\'use strict\';\n
\treturn {\n
\t\tname: \'Extension Panning\',\n
\t\tsvgicons: svgEditor.curConfig.extPath + \'ext-panning.xml\',\n
\t\tbuttons: [{\n
\t\t\tid: \'ext-panning\',\n
\t\t\ttype: \'mode\',\n
\t\t\ttitle: \'Panning\',\n
\t\t\tevents: {\n
\t\t\t\tclick: function() {\n
\t\t\t\t\tsvgCanvas.setMode(\'ext-panning\');\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}],\n
\t\tmouseDown: function() {\n
\t\t\tif (svgCanvas.getMode() == \'ext-panning\') {\n
\t\t\t\tsvgEditor.setPanning(true);\n
\t\t\t\treturn {started: true};\n
\t\t\t}\n
\t\t},\n
\t\tmouseUp: function() {\n
\t\t\tif (svgCanvas.getMode() == \'ext-panning\') {\n
\t\t\t\tsvgEditor.setPanning(false);\n
\t\t\t\treturn {\n
\t\t\t\t\tkeep: false,\n
\t\t\t\t\telement: null\n
\t\t\t\t};\n
\t\t\t}\n
\t\t}\n
\t};\n
});\n
</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>913</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
