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
            <value> <string>ext-star.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgedit, svgCanvas, $*/\n
/*jslint vars: true, eqeq: true*/\n
/*\n
 * ext-star.js\n
 *\n
 *\n
 * Copyright(c) 2010 CloudCanvas, Inc.\n
 * All rights reserved\n
 *\n
 */\n
\n
svgEditor.addExtension(\'star\', function(S){\'use strict\';\n
\n
\tvar // NS = svgedit.NS,\n
\t\t// svgcontent = S.svgcontent,\n
\t\tselElems,\n
\t\t// editingitex = false,\n
\t\t// svgdoc = S.svgroot.parentNode.ownerDocument,\n
\t\tstarted,\n
\t\tnewFO,\n
\t\t// edg = 0,\n
\t\t// newFOG, newFOGParent, newDef, newImageName, newMaskID,\n
\t\t// undoCommand = \'Not image\',\n
\t\t// modeChangeG, ccZoom, wEl, hEl, wOffset, hOffset, ccRgbEl, brushW, brushH,\n
\t\tshape;\n
\n
\tfunction showPanel(on){\n
\t\tvar fc_rules = $(\'#fc_rules\');\n
\t\tif (!fc_rules.length) {\n
\t\t\tfc_rules = $(\'<style id="fc_rules"><\\/style>\').appendTo(\'head\');\n
\t\t}\n
\t\tfc_rules.text(!on ? \'\' : \' #tool_topath { display: none !important; }\');\n
\t\t$(\'#star_panel\').toggle(on);\n
\t}\n
\n
\t/*\n
\tfunction toggleSourceButtons(on){\n
\t\t$(\'#star_save, #star_cancel\').toggle(on);\n
\t}\n
\t*/\n
\n
\tfunction setAttr(attr, val){\n
\t\tsvgCanvas.changeSelectedAttribute(attr, val);\n
\t\tS.call(\'changed\', selElems);\n
\t}\n
\n
\t/*\n
\tfunction cot(n){\n
\t\treturn 1 / Math.tan(n);\n
\t}\n
\n
\tfunction sec(n){\n
\t\treturn 1 / Math.cos(n);\n
\t}\n
\t*/\n
\n
\treturn {\n
\t\tname: \'star\',\n
\t\tsvgicons: svgEditor.curConfig.extPath + \'star-icons.svg\',\n
\t\tbuttons: [{\n
\t\t\tid: \'tool_star\',\n
\t\t\ttype: \'mode\',\n
\t\t\ttitle: \'Star Tool\',\n
\t\t\tposition: 12,\n
\t\t\tevents: {\n
\t\t\t\tclick: function(){\n
\t\t\t\t\tshowPanel(true);\n
\t\t\t\t\tsvgCanvas.setMode(\'star\');\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}],\n
\n
\t\tcontext_tools: [{\n
\t\t\ttype: \'input\',\n
\t\t\tpanel: \'star_panel\',\n
\t\t\ttitle: \'Number of Sides\',\n
\t\t\tid: \'starNumPoints\',\n
\t\t\tlabel: \'points\',\n
\t\t\tsize: 3,\n
\t\t\tdefval: 5,\n
\t\t\tevents: {\n
\t\t\t\tchange: function(){\n
\t\t\t\t\tsetAttr(\'point\', this.value);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}, {\n
\t\t\ttype: \'input\',\n
\t\t\tpanel: \'star_panel\',\n
\t\t\ttitle: \'Pointiness\',\n
\t\t\tid: \'starRadiusMulitplier\',\n
\t\t\tlabel: \'Pointiness\',\n
\t\t\tsize: 3,\n
\t\t\tdefval: 2.5\n
\t\t}, {\n
\t\t\ttype: \'input\',\n
\t\t\tpanel: \'star_panel\',\n
\t\t\ttitle: \'Twists the star\',\n
\t\t\tid: \'radialShift\',\n
\t\t\tlabel: \'Radial Shift\',\n
\t\t\tsize: 3,\n
\t\t\tdefval: 0,\n
\t\t\tevents: {\n
\t\t\t\tchange: function(){\n
\t\t\t\t\tsetAttr(\'radialshift\', this.value);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}],\n
\t\tcallback: function(){\n
\t\t\t$(\'#star_panel\').hide();\n
\t\t\t// var endChanges = function(){};\n
\t\t},\n
\t\tmouseDown: function(opts){\n
\t\t\tvar rgb = svgCanvas.getColor(\'fill\');\n
\t\t\t// var ccRgbEl = rgb.substring(1, rgb.length);\n
\t\t\tvar sRgb = svgCanvas.getColor(\'stroke\');\n
\t\t\t// var ccSRgbEl = sRgb.substring(1, rgb.length);\n
\t\t\tvar sWidth = svgCanvas.getStrokeWidth();\n
\n
\t\t\tif (svgCanvas.getMode() == \'star\') {\n
\t\t\t\tstarted = true;\n
\n
\t\t\t\tnewFO = S.addSvgElementFromJson({\n
\t\t\t\t\t\'element\': \'polygon\',\n
\t\t\t\t\t\'attr\': {\n
\t\t\t\t\t\t\'cx\': opts.start_x,\n
\t\t\t\t\t\t\'cy\': opts.start_y,\n
\t\t\t\t\t\t\'id\': S.getNextId(),\n
\t\t\t\t\t\t\'shape\': \'star\',\n
\t\t\t\t\t\t\'point\': document.getElementById(\'starNumPoints\').value,\n
\t\t\t\t\t\t\'r\': 0,\n
\t\t\t\t\t\t\'radialshift\': document.getElementById(\'radialShift\').value,\n
\t\t\t\t\t\t\'r2\': 0,\n
\t\t\t\t\t\t\'orient\': \'point\',\n
\t\t\t\t\t\t\'fill\': rgb,\n
\t\t\t\t\t\t\'strokecolor\': sRgb,\n
\t\t\t\t\t\t\'strokeWidth\': sWidth\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\treturn {\n
\t\t\t\t\tstarted: true\n
\t\t\t\t};\n
\t\t\t}\n
\t\t},\n
\t\tmouseMove: function(opts){\n
\t\t\tif (!started) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tif (svgCanvas.getMode() == \'star\') {\n
\t\t\t\tvar x = opts.mouse_x;\n
\t\t\t\tvar y = opts.mouse_y;\n
\t\t\t\tvar c = $(newFO).attr([\'cx\', \'cy\', \'point\', \'orient\', \'fill\', \'strokecolor\', \'strokeWidth\', \'radialshift\']);\n
\n
\t\t\t\tvar cx = c.cx, cy = c.cy, fill = c.fill, strokecolor = c.strokecolor, strokewidth = c.strokeWidth, radialShift = c.radialshift, point = c.point, orient = c.orient, circumradius = (Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy))) / 1.5, inradius = circumradius / document.getElementById(\'starRadiusMulitplier\').value;\n
\t\t\t\tnewFO.setAttributeNS(null, \'r\', circumradius);\n
\t\t\t\tnewFO.setAttributeNS(null, \'r2\', inradius);\n
\n
\t\t\t\tvar polyPoints = \'\';\n
\t\t\t\tvar s;\n
\t\t\t\tfor (s = 0; point >= s; s++) {\n
\t\t\t\t\tvar angle = 2.0 * Math.PI * (s / point);\n
\t\t\t\t\tif (\'point\' == orient) {\n
\t\t\t\t\t\tangle -= (Math.PI / 2);\n
\t\t\t\t\t} else if (\'edge\' == orient) {\n
\t\t\t\t\t\tangle = (angle + (Math.PI / point)) - (Math.PI / 2);\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tx = (circumradius * Math.cos(angle)) + cx;\n
\t\t\t\t\ty = (circumradius * Math.sin(angle)) + cy;\n
\n
\t\t\t\t\tpolyPoints += x + \',\' + y + \' \';\n
\n
\t\t\t\t\tif (null != inradius) {\n
\t\t\t\t\t\tangle = (2.0 * Math.PI * (s / point)) + (Math.PI / point);\n
\t\t\t\t\t\tif (\'point\' == orient) {\n
\t\t\t\t\t\t\tangle -= (Math.PI / 2);\n
\t\t\t\t\t\t} else if (\'edge\' == orient) {\n
\t\t\t\t\t\t\tangle = (angle + (Math.PI / point)) - (Math.PI / 2);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tangle += radialShift;\n
\n
\t\t\t\t\t\tx = (inradius * Math.cos(angle)) + cx;\n
\t\t\t\t\t\ty = (inradius * Math.sin(angle)) + cy;\n
\n
\t\t\t\t\t\tpolyPoints += x + \',\' + y + \' \';\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tnewFO.setAttributeNS(null, \'points\', polyPoints);\n
\t\t\t\tnewFO.setAttributeNS(null, \'fill\', fill);\n
\t\t\t\tnewFO.setAttributeNS(null, \'stroke\', strokecolor);\n
\t\t\t\tnewFO.setAttributeNS(null, \'stroke-width\', strokewidth);\n
\t\t\t\tshape = newFO.getAttributeNS(null, \'shape\');\n
\n
\t\t\t\treturn {\n
\t\t\t\t\tstarted: true\n
\t\t\t\t};\n
\t\t\t}\n
\n
\t\t},\n
\t\tmouseUp: function(){\n
\t\t\tif (svgCanvas.getMode() == \'star\') {\n
\t\t\t\tvar attrs = $(newFO).attr([\'r\']);\n
\t\t\t\t// svgCanvas.addToSelection([newFO], true);\n
\t\t\t\treturn {\n
\t\t\t\t\tkeep: (attrs.r != 0),\n
\t\t\t\t\telement: newFO\n
\t\t\t\t};\n
\t\t\t}\n
\t\t},\n
\t\tselectedChanged: function(opts){\n
\t\t\t// Use this to update the current selected elements\n
\t\t\tselElems = opts.elems;\n
\n
\t\t\tvar i = selElems.length;\n
\n
\t\t\twhile (i--) {\n
\t\t\t\tvar elem = selElems[i];\n
\t\t\t\tif (elem && elem.getAttributeNS(null, \'shape\') === \'star\') {\n
\t\t\t\t\tif (opts.selectedElement && !opts.multiselected) {\n
\t\t\t\t\t\t// $(\'#starRadiusMulitplier\').val(elem.getAttribute(\'r2\'));\n
\t\t\t\t\t\t$(\'#starNumPoints\').val(elem.getAttribute(\'point\'));\n
\t\t\t\t\t\t$(\'#radialShift\').val(elem.getAttribute(\'radialshift\'));\n
\t\t\t\t\t\tshowPanel(true);\n
\t\t\t\t\t}\n
\t\t\t\t\telse {\n
\t\t\t\t\t\tshowPanel(false);\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tshowPanel(false);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\telementChanged: function(opts){\n
\t\t\t// var elem = opts.elems[0];\n
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
            <value> <int>5807</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
