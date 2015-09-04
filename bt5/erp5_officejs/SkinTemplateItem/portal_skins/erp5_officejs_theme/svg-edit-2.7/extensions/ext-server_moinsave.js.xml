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
            <value> <string>ext-server_moinsave.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgedit, svgCanvas, canvg, $, top*/\n
/*jslint vars: true*/\n
/*\n
 * ext-server_moinsave.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 *              2011 MoinMoin:ReimarBauer\n
 *                   adopted for moinmoins item storage. it sends in one post png and svg data\n
 *                   (I agree to dual license my work to additional GPLv2 or later)\n
 *\n
 */\n
\n
svgEditor.addExtension("server_opensave", {\n
\tcallback: function() {\'use strict\';\n
\n
\t\tvar save_svg_action = \'/+modify\';\n
\t\t\n
\t\t// Create upload target (hidden iframe)\n
\t\tvar target = $(\'<iframe name="output_frame" src="#"/>\').hide().appendTo(\'body\');\n
\t\n
\t\tsvgEditor.setCustomHandlers({\n
\t\t\tsave: function(win, data) {\n
\t\t\t\tvar svg = "<?xml version=\\"1.0\\"?>\\n" + data;\n
\t\t\t\tvar qstr = $.param.querystring();\n
\t\t\t\tvar name = qstr.substr(9).split(\'/+get/\')[1];\n
\t\t\t\tvar svg_data = svgedit.utilities.encode64(svg);\n
\t\t\t\tif(!$(\'#export_canvas\').length) {\n
\t\t\t\t\t$(\'<canvas>\', {id: \'export_canvas\'}).hide().appendTo(\'body\');\n
\t\t\t\t}\n
\t\t\t\tvar c = $(\'#export_canvas\')[0];\n
\t\t\t\tc.width = svgCanvas.contentW;\n
\t\t\t\tc.height = svgCanvas.contentH;\n
\t\t\t\t$.getScript(\'canvg/canvg.js\', function() {\n
\t\t\t\t\tcanvg(c, svg, {renderCallback: function() {\n
\t\t\t\t\t\tvar datauri = c.toDataURL(\'image/png\');\n
\t\t\t\t\t\t// var uiStrings = svgEditor.uiStrings;\n
\t\t\t\t\t\tvar png_data = svgedit.utilities.encode64(datauri);\n
\t\t\t\t\t\tvar form = $(\'<form>\').attr({\n
\t\t\t\t\t\tmethod: \'post\',\n
\t\t\t\t\t\taction: save_svg_action + \'/\' + name,\n
\t\t\t\t\t\ttarget: \'output_frame\'\n
\t\t\t\t\t}).append(\'<input type="hidden" name="png_data" value="\' + png_data + \'">\')\n
\t\t\t\t\t\t.append(\'<input type="hidden" name="filepath" value="\' + svg_data + \'">\')\n
\t\t\t\t\t\t.append(\'<input type="hidden" name="filename" value="\' + \'drawing.svg">\')\n
\t\t\t\t\t\t.append(\'<input type="hidden" name="contenttype" value="application/x-svgdraw">\')\n
\t\t\t\t\t\t.appendTo(\'body\')\n
\t\t\t\t\t\t.submit().remove();\n
\t\t\t\t\t}});\n
\t\t\t\t});\n
\t\t\t\talert("Saved! Return to Item View!");\n
\t\t\t\ttop.window.location = \'/\'+name;\n
\t\t\t}\n
\t\t});\n
\t\n
\t}\n
});\n
\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2003</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
