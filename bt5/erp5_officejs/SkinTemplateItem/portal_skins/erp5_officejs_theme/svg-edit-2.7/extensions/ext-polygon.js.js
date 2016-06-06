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
            <value> <string>ext-polygon.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgCanvas, svgedit, $*/\n
/*jslint vars: true, eqeq: true, todo: true */\n
/*\n
 * ext-polygon.js\n
 *\n
 *\n
 * Copyright(c) 2010 CloudCanvas, Inc.\n
 * All rights reserved\n
 *\n
 */\n
svgEditor.addExtension("polygon", function(S) {\'use strict\';\n
\n
    var // NS = svgedit.NS,\n
\t\t// svgcontent = S.svgcontent,\n
\t\t// addElem = S.addSvgElementFromJson,\n
\t\tselElems,\n
\t\teditingitex = false,\n
\t\t// svgdoc = S.svgroot.parentNode.ownerDocument,\n
\t\t// newFOG, newFOGParent, newDef, newImageName, newMaskID, modeChangeG,\n
\t\t// edg = 0,\n
\t\t// undoCommand = "Not image";\n
\t\tstarted, newFO;\n
    \n
    // var ccZoom;\n
    // var wEl, hEl;\n
    // var wOffset, hOffset;\n
    // var ccRBG;\n
\tvar ccRgbEl;\n
    // var ccOpacity;\n
    // var brushW, brushH;\n
\tvar shape;\n
    \n
    // var ccDebug = document.getElementById(\'debugpanel\');\n
    \n
    /* var properlySourceSizeTextArea = function(){\n
     // TODO: remove magic numbers here and get values from CSS\n
     var height = $(\'#svg_source_container\').height() - 80;\n
     $(\'#svg_source_textarea\').css(\'height\', height);\n
     }; */\n
    function showPanel(on){\n
        var fc_rules = $(\'#fc_rules\');\n
        if (!fc_rules.length) {\n
            fc_rules = $(\'<style id="fc_rules"><\\/style>\').appendTo(\'head\');\n
        }\n
        fc_rules.text(!on ? "" : " #tool_topath { display: none !important; }");\n
        $(\'#polygon_panel\').toggle(on);\n
    }\n
    \n
\t/*\n
    function toggleSourceButtons(on){\n
        $(\'#tool_source_save, #tool_source_cancel\').toggle(!on);\n
        $(\'#polygon_save, #polygon_cancel\').toggle(on);\n
    }\n
\t*/\n
    \n
    function setAttr(attr, val){\n
        svgCanvas.changeSelectedAttribute(attr, val);\n
        S.call("changed", selElems);\n
    }\n
    \n
    function cot(n){\n
        return 1 / Math.tan(n);\n
    }\n
    \n
    function sec(n){\n
        return 1 / Math.cos(n);\n
    }\n
\n
\t/**\n
\t* Obtained from http://code.google.com/p/passenger-top/source/browse/instiki/public/svg-edit/editor/extensions/ext-itex.js?r=3\n
\t* This function sets the content of of the currently-selected foreignObject element,\n
\t*   based on the itex contained in string.\n
\t* @param {string} tex The itex text.\n
\t* @returns This function returns false if the set was unsuccessful, true otherwise.\n
\t*/\n
\t/*\n
\tfunction setItexString(tex) {\n
\t\tvar mathns = \'http://www.w3.org/1998/Math/MathML\',\n
\t\t\txmlnsns = \'http://www.w3.org/2000/xmlns/\',\n
\t\t\tajaxEndpoint = \'../../itex\';\n
\t\tvar elt = selElems[0];\n
\t\ttry {\n
\t\t\tvar math = svgdoc.createElementNS(mathns, \'math\');\n
\t\t\tmath.setAttributeNS(xmlnsns, \'xmlns\', mathns);\n
\t\t\tmath.setAttribute(\'display\', \'inline\');\n
\t\t\tvar semantics = document.createElementNS(mathns, \'semantics\');\n
\t\t\tvar annotation = document.createElementNS(mathns, \'annotation\');\n
\t\t\tannotation.setAttribute(\'encoding\', \'application/x-tex\');\n
\t\t\tannotation.textContent = tex;\n
\t\t\tvar mrow = document.createElementNS(mathns, \'mrow\');\n
\t\t\tsemantics.appendChild(mrow);\n
\t\t\tsemantics.appendChild(annotation);\n
\t\t\tmath.appendChild(semantics);\n
\t\t\t// make an AJAX request to the server, to get the MathML\n
\t\t\t$.post(ajaxEndpoint, {\'tex\': tex, \'display\': \'inline\'}, function(data){\n
\t\t\t\tvar children = data.documentElement.childNodes;\n
\t\t\t\twhile (children.length > 0) {\n
\t\t\t\t     mrow.appendChild(svgdoc.adoptNode(children[0], true));\n
\t\t\t\t}\n
\t\t\t\tS.sanitizeSvg(math);\n
\t\t\t\tS.call("changed", [elt]);\n
\t\t\t});\n
\t\t\telt.replaceChild(math, elt.firstChild);\n
\t\t\tS.call("changed", [elt]);\n
\t\t\tsvgCanvas.clearSelection();\n
\t\t} catch(e) {\n
\t\t\tconsole.log(e);\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\treturn true;\n
\t}\n
\t*/\n
    return {\n
        name: "polygon",\n
        svgicons: svgEditor.curConfig.extPath + "polygon-icons.svg",\n
        buttons: [{\n
            id: "tool_polygon",\n
            type: "mode",\n
            title: "Polygon Tool",\n
            position: 11,\n
            events: {\n
                \'click\': function(){\n
                    svgCanvas.setMode(\'polygon\');\n
\t\t\t\t\tshowPanel(true);\n
                }\n
            }\n
        }],\n
        \n
        context_tools: [{\n
            type: "input",\n
            panel: "polygon_panel",\n
            title: "Number of Sides",\n
            id: "polySides",\n
            label: "sides",\n
            size: 3,\n
            defval: 5,\n
            events: {\n
                change: function(){\n
                    setAttr(\'sides\', this.value);\n
\t\t\t\t\t\n
                }\n
            }\n
        }],\n
        \n
        callback: function(){\n
        \n
            $(\'#polygon_panel\').hide();\n
            \n
            var endChanges = function(){\n
            };\n
            \n
            // TODO: Needs to be done after orig icon loads\n
            setTimeout(function(){\n
                // Create source save/cancel buttons\n
                var save = $(\'#tool_source_save\').clone().hide().attr(\'id\', \'polygon_save\').unbind().appendTo("#tool_source_back").click(function(){\n
                \n
                    if (!editingitex) {\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\t\t\t\t\t// Todo: Uncomment the setItexString() function above and handle ajaxEndpoint?\n
                    if (!setItexString($(\'#svg_source_textarea\').val())) {\n
                        $.confirm("Errors found. Revert to original?", function(ok){\n
                            if (!ok) {\n
\t\t\t\t\t\t\t\treturn false;\n
\t\t\t\t\t\t\t}\n
                            endChanges();\n
                        });\n
                    }\n
                    else {\n
                        endChanges();\n
                    }\n
                    // setSelectMode();\t\n
                });\n
                \n
                var cancel = $(\'#tool_source_cancel\').clone().hide().attr(\'id\', \'polygon_cancel\').unbind().appendTo("#tool_source_back").click(function(){\n
                    endChanges();\n
                });\n
                \n
            }, 3000);\n
        },\n
        mouseDown: function(opts){\n
            // var e = opts.event;\n
            var rgb = svgCanvas.getColor("fill");\n
            ccRgbEl = rgb.substring(1, rgb.length);\n
            var sRgb = svgCanvas.getColor("stroke");\n
            // ccSRgbEl = sRgb.substring(1, rgb.length);\n
            var sWidth = svgCanvas.getStrokeWidth();\n
            \n
            if (svgCanvas.getMode() == "polygon") {\n
                started = true;\n
                \n
                newFO = S.addSvgElementFromJson({\n
                    "element": "polygon",\n
                    "attr": {\n
                        "cx": opts.start_x,\n
                        "cy": opts.start_y,\n
                        "id": S.getNextId(),\n
                        "shape": "regularPoly",\n
                        "sides": document.getElementById("polySides").value,\n
                        "orient": "x",\n
                        "edge": 0,\n
                        "fill": rgb,\n
                        "strokecolor": sRgb,\n
                        "strokeWidth": sWidth\n
                    }\n
                });\n
                \n
                return {\n
                    started: true\n
                };\n
            }\n
        },\n
        mouseMove: function(opts){\n
            if (!started) {\n
                return;\n
\t\t\t}\n
            if (svgCanvas.getMode() == "polygon") {\n
                // var e = opts.event;\n
                var x = opts.mouse_x;\n
                var y = opts.mouse_y;\n
                var c = $(newFO).attr(["cx", "cy", "sides", "orient", "fill", "strokecolor", "strokeWidth"]);\n
                var cx = c.cx, cy = c.cy, fill = c.fill, strokecolor = c.strokecolor, strokewidth = c.strokeWidth, sides = c.sides,\n
\t\t\t\t\t// orient = c.orient,\n
\t\t\t\t\tedg = (Math.sqrt((x - cx) * (x - cx) + (y - cy) * (y - cy))) / 1.5;\n
                newFO.setAttributeNS(null, "edge", edg);\n
                \n
                var inradius = (edg / 2) * cot(Math.PI / sides);\n
                var circumradius = inradius * sec(Math.PI / sides);\n
                var points = \'\';\n
\t\t\t\tvar s;\n
                for (s = 0; sides >= s; s++) {\n
                    var angle = 2.0 * Math.PI * s / sides;\n
                    x = (circumradius * Math.cos(angle)) + cx;\n
                    y = (circumradius * Math.sin(angle)) + cy;\n
                    \n
                    points += x + \',\' + y + \' \';\n
                }\n
                \n
                //var poly = newFO.createElementNS(NS.SVG, \'polygon\');\n
                newFO.setAttributeNS(null, \'points\', points);\n
                newFO.setAttributeNS(null, \'fill\', fill);\n
                newFO.setAttributeNS(null, \'stroke\', strokecolor);\n
                newFO.setAttributeNS(null, \'stroke-width\', strokewidth);\n
\t\t\t\t// newFO.setAttributeNS(null, \'transform\', "rotate(-90)");\n
                shape = newFO.getAttributeNS(null, \'shape\');\n
                //newFO.appendChild(poly);\n
                //DrawPoly(cx, cy, sides, edg, orient);\n
                return {\n
                    started: true\n
                };\n
            }\n
            \n
        },\n
        \n
        mouseUp: function(opts){\n
            if (svgCanvas.getMode() == "polygon") {\n
                var attrs = $(newFO).attr("edge");\n
                var keep = (attrs.edge != 0);\n
               // svgCanvas.addToSelection([newFO], true);\n
                return {\n
                    keep: keep,\n
                    element: newFO\n
                };\n
            }\n
            \n
        },\n
        selectedChanged: function(opts){\n
            // Use this to update the current selected elements\n
            selElems = opts.elems;\n
            \n
            var i = selElems.length;\n
            \n
            while (i--) {\n
                var elem = selElems[i];\n
                if (elem && elem.getAttributeNS(null, \'shape\') === \'regularPoly\') {\n
                    if (opts.selectedElement && !opts.multiselected) {\n
                        $(\'#polySides\').val(elem.getAttribute("sides"));\n
                        \n
                        showPanel(true);\n
                    }\n
                    else {\n
                        showPanel(false);\n
                    }\n
                }\n
                else {\n
                    showPanel(false);\n
                }\n
            }\n
        },\n
        elementChanged: function(opts){\n
            // var elem = opts.elems[0];\n
        }\n
    };\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>10003</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
