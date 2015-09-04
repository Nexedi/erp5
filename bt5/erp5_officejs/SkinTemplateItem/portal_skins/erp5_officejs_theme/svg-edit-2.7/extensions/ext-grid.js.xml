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
            <value> <string>ext-grid.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgedit, svgCanvas, $*/\n
/*jslint vars: true*/\n
/*\n
 * ext-grid.js\n
 *\n
 * Licensed under the Apache License, Version 2\n
 *\n
 * Copyright(c) 2010 Redou Mine\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
\n
// Dependencies:\n
// 1) units.js\n
// 2) everything else\n
\n
svgEditor.addExtension(\'view_grid\', function() { \'use strict\';\n
\n
\tvar NS = svgedit.NS,\n
\t\tsvgdoc = document.getElementById(\'svgcanvas\').ownerDocument,\n
\t\tshowGrid = false,\n
\t\tassignAttributes = svgCanvas.assignAttributes,\n
\t\thcanvas = document.createElement(\'canvas\'),\n
\t\tcanvBG = $(\'#canvasBackground\'),\n
\t\tunits = svgedit.units.getTypeMap(),\n
\t\tintervals = [0.01, 0.1, 1, 10, 100, 1000];\n
\n
\t$(hcanvas).hide().appendTo(\'body\');\n
\n
\tvar canvasGrid = svgdoc.createElementNS(NS.SVG, \'svg\');\n
\tassignAttributes(canvasGrid, {\n
\t\t\'id\': \'canvasGrid\',\n
\t\t\'width\': \'100%\',\n
\t\t\'height\': \'100%\',\n
\t\t\'x\': 0,\n
\t\t\'y\': 0,\n
\t\t\'overflow\': \'visible\',\n
\t\t\'display\': \'none\'\n
\t});\n
\tcanvBG.append(canvasGrid);\n
\n
\t// grid-pattern\n
\tvar gridPattern = svgdoc.createElementNS(NS.SVG, \'pattern\');\n
\tassignAttributes(gridPattern, {\n
\t\t\'id\': \'gridpattern\',\n
\t\t\'patternUnits\': \'userSpaceOnUse\',\n
\t\t\'x\': 0, //-(value.strokeWidth / 2), // position for strokewidth\n
\t\t\'y\': 0, //-(value.strokeWidth / 2), // position for strokewidth\n
\t\t\'width\': 100,\n
\t\t\'height\': 100\n
\t});\n
\n
\tvar gridimg = svgdoc.createElementNS(NS.SVG, \'image\');\n
\tassignAttributes(gridimg, {\n
\t\t\'x\': 0,\n
\t\t\'y\': 0,\n
\t\t\'width\': 100,\n
\t\t\'height\': 100\n
\t});\n
\tgridPattern.appendChild(gridimg);\n
\t$(\'#svgroot defs\').append(gridPattern);\n
\n
\t// grid-box\n
\tvar gridBox = svgdoc.createElementNS(NS.SVG, \'rect\');\n
\tassignAttributes(gridBox, {\n
\t\t\'width\': \'100%\',\n
\t\t\'height\': \'100%\',\n
\t\t\'x\': 0,\n
\t\t\'y\': 0,\n
\t\t\'stroke-width\': 0,\n
\t\t\'stroke\': \'none\',\n
\t\t\'fill\': \'url(#gridpattern)\',\n
\t\t\'style\': \'pointer-events: none; display:visible;\'\n
\t});\n
\t$(\'#canvasGrid\').append(gridBox);\n
\n
\tfunction updateGrid(zoom) {\n
\t\tvar i;\n
\t\t// TODO: Try this with <line> elements, then compare performance difference\n
\t\tvar unit = units[svgEditor.curConfig.baseUnit]; // 1 = 1px\n
\t\tvar u_multi = unit * zoom;\n
\t\t// Calculate the main number interval\n
\t\tvar raw_m = 100 / u_multi;\n
\t\tvar multi = 1;\n
\t\tfor (i = 0; i < intervals.length; i++) {\n
\t\t\tvar num = intervals[i];\n
\t\t\tmulti = num;\n
\t\t\tif (raw_m <= num) {\n
\t\t\t\tbreak;\n
\t\t\t}\n
\t\t}\n
\t\tvar big_int = multi * u_multi;\n
\n
\t\t// Set the canvas size to the width of the container\n
\t\thcanvas.width = big_int;\n
\t\thcanvas.height = big_int;\n
\t\tvar ctx = hcanvas.getContext(\'2d\');\n
\t\tvar cur_d = 0.5;\n
\t\tvar part = big_int / 10;\n
\n
\t\tctx.globalAlpha = 0.2;\n
\t\tctx.strokeStyle = svgEditor.curConfig.gridColor;\n
\t\tfor (i = 1; i < 10; i++) {\n
\t\t\tvar sub_d = Math.round(part * i) + 0.5;\n
\t\t\t// var line_num = (i % 2)?12:10;\n
\t\t\tvar line_num = 0;\n
\t\t\tctx.moveTo(sub_d, big_int);\n
\t\t\tctx.lineTo(sub_d, line_num);\n
\t\t\tctx.moveTo(big_int, sub_d);\n
\t\t\tctx.lineTo(line_num ,sub_d);\n
\t\t}\n
\t\tctx.stroke();\n
\t\tctx.beginPath();\n
\t\tctx.globalAlpha = 0.5;\n
\t\tctx.moveTo(cur_d, big_int);\n
\t\tctx.lineTo(cur_d, 0);\n
\n
\t\tctx.moveTo(big_int, cur_d);\n
\t\tctx.lineTo(0, cur_d);\n
\t\tctx.stroke();\n
\n
\t\tvar datauri = hcanvas.toDataURL(\'image/png\');\n
\t\tgridimg.setAttribute(\'width\', big_int);\n
\t\tgridimg.setAttribute(\'height\', big_int);\n
\t\tgridimg.parentNode.setAttribute(\'width\', big_int);\n
\t\tgridimg.parentNode.setAttribute(\'height\', big_int);\n
\t\tsvgCanvas.setHref(gridimg, datauri);\n
\t}\n
\n
\treturn {\n
\t\tname: \'view_grid\',\n
\t\tsvgicons: svgEditor.curConfig.extPath + \'grid-icon.xml\',\n
\n
\t\tzoomChanged: function(zoom) {\n
\t\t\tif (showGrid) {updateGrid(zoom);}\n
\t\t},\n
\n
\t\tbuttons: [{\n
\t\t\tid: \'view_grid\',\n
\t\t\ttype: \'context\',\n
\t\t\tpanel: \'editor_panel\',\n
\t\t\ttitle: \'Show/Hide Grid\',\n
\t\t\tevents: {\n
\t\t\t\tclick: function() {\n
\t\t\t\t\tsvgEditor.curConfig.showGrid = showGrid = !showGrid;\n
\t\t\t\t\tif (showGrid) {\n
\t\t\t\t\t\tupdateGrid(svgCanvas.getZoom());\n
\t\t\t\t\t}\n
\t\t\t\t\t$(\'#canvasGrid\').toggle(showGrid);\n
\t\t\t\t\t$(\'#view_grid\').toggleClass(\'push_button_pressed tool_button\');\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}]\n
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
            <value> <int>3844</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
