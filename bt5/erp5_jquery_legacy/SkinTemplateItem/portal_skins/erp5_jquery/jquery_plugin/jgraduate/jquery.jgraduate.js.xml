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
            <value> <string>ts80003716.63</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.jgraduate.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\n
 * jGraduate 0.3.x\n
 *\n
 * jQuery Plugin for a gradient picker\n
 *\n
 * Copyright (c) 2010 Jeff Schiller\n
 * http://blog.codedread.com/\n
 * Copyright (c) 2010 Alexis Deveria\n
 * http://a.deveria.com/\n
 *\n
 * Apache 2 License\n
\n
jGraduate( options, okCallback, cancelCallback )\n
\n
where options is an object literal:\n
\t{\n
\t\twindow: { title: "Pick the start color and opacity for the gradient" },\n
\t\timages: { clientPath: "images/" },\n
\t\tpaint: a Paint object\n
\t}\n
 \n
- the Paint object is:\n
\tPaint {\n
\t\ttype: String, // one of "none", "solidColor", "linearGradient", "radialGradient"\n
\t\talpha: Number representing opacity (0-100),\n
\t\tsolidColor: String representing #RRGGBB hex of color,\n
\t\tlinearGradient: object of interface SVGLinearGradientElement,\n
\t\tradialGradient: object of interface SVGRadialGradientElement,\n
\t}\n
\n
$.jGraduate.Paint() -> constructs a \'none\' color\n
$.jGraduate.Paint({copy: o}) -> creates a copy of the paint o\n
$.jGraduate.Paint({hex: "#rrggbb"}) -> creates a solid color paint with hex = "#rrggbb"\n
$.jGraduate.Paint({linearGradient: o, a: 50}) -> creates a linear gradient paint with opacity=0.5\n
$.jGraduate.Paint({radialGradient: o, a: 7}) -> creates a radial gradient paint with opacity=0.07\n
$.jGraduate.Paint({hex: "#rrggbb", linearGradient: o}) -> throws an exception?\n
\n
- picker accepts the following object as input:\n
\t{\n
\t\tokCallback: function to call when Ok is pressed\n
\t\tcancelCallback: function to call when Cancel is pressed\n
\t\tpaint: object describing the paint to display initially, if not set, then default to opaque white\n
\t}\n
\n
- okCallback receives a Paint object\n
\n
 *\n
 */\n
 \n
(function() {\n
 \n
var ns = { svg: \'http://www.w3.org/2000/svg\', xlink: \'http://www.w3.org/1999/xlink\' };\n
if(!window.console) {\n
  window.console = new function() {\n
    this.log = function(str) {};\n
    this.dir = function(str) {};\n
  };\n
}\n
$.cloneNode = function(el) {\n
\tif(!window.opera) return el.cloneNode(true);\n
\t// manually create a copy of the element\n
\topera.postError(ns.svg, el.nodeName);\n
\tvar new_el = document.createElementNS(ns.svg, el.nodeName);\n
\t$.each(el.attributes, function(i, attr) {\n
\t\tnew_el.setAttributeNS(ns.svg, attr.nodeName, attr.nodeValue);\n
\t});\n
\t$.each(el.childNodes, function(i, child) {\n
\t\tif(child.nodeType == 1) {\n
\t\t\tnew_el.appendChild($.cloneNode(child));\n
\t\t}\n
\t});\n
\treturn new_el;\n
}\n
\n
$.jGraduate = { \n
\tPaint:\n
\t\tfunction(opt) {\n
\t\t\tvar options = opt || {};\n
\t\t\tthis.alpha = options.alpha || 100;\n
\t\t\t// copy paint object\n
    \t\tif (options.copy) {\n
    \t\t\tthis.type = options.copy.type;\n
    \t\t\tthis.alpha = options.copy.alpha;\n
\t\t\t\tthis.solidColor = null;\n
\t\t\t\tthis.linearGradient = null;\n
\t\t\t\tthis.radialGradient = null;\n
\n
    \t\t\tswitch(this.type) {\n
    \t\t\t\tcase "none":\n
    \t\t\t\t\tbreak;\n
    \t\t\t\tcase "solidColor":\n
    \t\t\t\t\tthis.solidColor = options.copy.solidColor;\n
    \t\t\t\t\tbreak;\n
    \t\t\t\tcase "linearGradient":\n
    \t\t\t\t\tthis.linearGradient = $.cloneNode(options.copy.linearGradient);\n
    \t\t\t\t\tbreak;\n
    \t\t\t\tcase "radialGradient":\n
    \t\t\t\t\tthis.radialGradient = $.cloneNode(options.copy.radialGradient);\n
    \t\t\t\t\tbreak;\n
    \t\t\t}\n
    \t\t}\n
    \t\t// create linear gradient paint\n
    \t\telse if (options.linearGradient) {\n
    \t\t\tthis.type = "linearGradient";\n
    \t\t\tthis.solidColor = null;\n
    \t\t\tthis.radialGradient = null;\n
    \t\t\tthis.linearGradient = $.cloneNode(options.linearGradient);\n
    \t\t}\n
    \t\t// create linear gradient paint\n
    \t\telse if (options.radialGradient) {\n
    \t\t\tthis.type = "radialGradient";\n
    \t\t\tthis.solidColor = null;\n
    \t\t\tthis.linearGradient = null;\n
    \t\t\tthis.radialGradient = $.cloneNode(options.radialGradient);\n
    \t\t}\n
    \t\t// create solid color paint\n
    \t\telse if (options.solidColor) {\n
    \t\t\tthis.type = "solidColor";\n
    \t\t\tthis.solidColor = options.solidColor;\n
    \t\t}\n
    \t\t// create empty paint\n
\t    \telse {\n
\t    \t\tthis.type = "none";\n
    \t\t\tthis.solidColor = null;\n
    \t\t\tthis.linearGradient = null;\n
    \t\t\tthis.radialGradient = null;\n
\t    \t}\n
\t\t}\n
};\n
\n
jQuery.fn.jGraduateDefaults = {\n
\tpaint: new $.jGraduate.Paint(),\n
\twindow: {\n
\t\tpickerTitle: "Drag markers to pick a paint"\n
\t},\n
\timages: {\n
\t\tclientPath: "images/"\n
\t}\n
};\n
\n
jQuery.fn.jGraduate =\n
\tfunction(options) {\n
\t \tvar $arguments = arguments;\n
\t\treturn this.each( function() {\n
\t\t\tvar $this = $(this), $settings = $.extend(true, {}, jQuery.fn.jGraduateDefaults, options),\n
\t\t\t\tid = $this.attr(\'id\'),\n
\t\t\t\tidref = \'#\'+$this.attr(\'id\')+\' \';\n
\t\t\t\n
            if (!idref)\n
            {\n
              alert(\'Container element must have an id attribute to maintain unique id strings for sub-elements.\');\n
              return;\n
            }\n
            \n
            var okClicked = function() {\n
\t            // TODO: Fix this ugly hack\n
\t            if($this.paint.type == "radialGradient") {\n
\t            \t$this.paint.linearGradient = null;\n
\t            } else if($this.paint.type == "linearGradient") {\n
\t            \t$this.paint.radialGradient = null;\t            \n
\t            } else if($this.paint.type == "solidColor") {\n
\t            \t$this.paint.linearGradient = null;\n
\t            \t$this.paint.radialGradient = null;\n
\t            }\n
            \t$.isFunction($this.okCallback) && $this.okCallback($this.paint);\n
            \t$this.hide();\n
            },\n
            cancelClicked = function() {\n
            \t$.isFunction($this.cancelCallback) && $this.cancelCallback();\n
            \t$this.hide();\n
            };\n
\n
            $.extend(true, $this, // public properties, methods, and callbacks\n
              {\n
              \t// make a copy of the incoming paint\n
                paint: new $.jGraduate.Paint({copy: $settings.paint}),\n
                okCallback: $.isFunction($arguments[1]) && $arguments[1] || null,\n
                cancelCallback: $.isFunction($arguments[2]) && $arguments[2] || null\n
              });\n
\n
\t\t\tvar pos = $this.position(),\n
\t\t\t\tcolor = null;\n
\n
\t\t\tif ($this.paint.type == "none") {\n
\t\t\t\t$this.paint = $.jGraduate.Paint({solidColor: \'ffffff\'});\n
\t\t\t}\n
\t\t\t\n
            $this.addClass(\'jGraduate_Picker\');\n
            $this.html(\'<ul class="jGraduate_tabs">\' +\n
            \t\t\t\t\'<li class="jGraduate_tab_color jGraduate_tab_current" data-type="col">Solid Color</li>\' +\n
            \t\t\t\t\'<li class="jGraduate_tab_lingrad" data-type="lg">Linear Gradient</li>\' +\n
            \t\t\t\t\'<li class="jGraduate_tab_radgrad" data-type="rg">Radial Gradient</li>\' +\n
            \t\t\t\'</ul>\' +\n
            \t\t\t\'<div class="jGraduate_colPick"></div>\' +\n
            \t\t\t\'<div class="jGraduate_lgPick"></div>\' +\n
            \t\t\t\'<div class="jGraduate_rgPick"></div>\');\n
\t\t\tvar colPicker = $(idref + \'> .jGraduate_colPick\');\n
\t\t\tvar lgPicker = $(idref + \'> .jGraduate_lgPick\');\n
\t\t\tvar rgPicker = $(idref + \'> .jGraduate_rgPick\');\n
\t\t\t\n
            lgPicker.html(\n
            \t\'<div id="\' + id + \'_jGraduate_Swatch" class="jGraduate_Swatch">\' +\n
            \t\t\'<h2 class="jGraduate_Title">\' + $settings.window.pickerTitle + \'</h2>\' +\n
            \t\t\'<div id="\' + id + \'_lg_jGraduate_GradContainer" class="jGraduate_GradContainer"></div>\' +\n
            \t\t\'<div id="\' + id + \'_lg_jGraduate_Opacity" class="jGraduate_Opacity" title="Click to set overall opacity of the gradient paint">\' +\n
            \t\t\t\'<img id="\' + id + \'_lg_jGraduate_AlphaArrows" class="jGraduate_AlphaArrows" src="\' + $settings.images.clientPath + \'rangearrows2.gif"></img>\' +\n
            \t\t\'</div>\' +\n
            \t\'</div>\' + \n
            \t\'<div class="jGraduate_Form">\' +\n
            \t\t\'<div class="jGraduate_StopSection">\' +\n
\t            \t\t\'<label class="jGraduate_Form_Heading">Begin Stop</label>\' +\n
    \t        \t\t\'<div class="jGraduate_Form_Section">\' +\n
        \t    \t\t\t\'<label>x:</label>\' +\n
            \t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_x1" size="3" title="Enter starting x value between 0.0 and 1.0"/>\' +\n
            \t\t\t\t\'<label> y:</label>\' +\n
            \t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_y1" size="3" title="Enter starting y value between 0.0 and 1.0"/>\' +\n
\t        \t    \t\t\'<div id="\' + id + \'_jGraduate_colorBoxBegin" class="colorBox"></div>\' +\n
\t\t            \t\t\'<label id="\' + id + \'_jGraduate_beginOpacity"> 100%</label>\' +\n
        \t   \t\t\t\'</div>\' +\n
        \t   \t\t\'</div>\' +\n
        \t   \t\t\'<div class="jGraduate_StopSection">\' +\n
\t            \t\t\'<label class="jGraduate_Form_Heading">End Stop</label>\' +\n
    \t        \t\t\'<div class="jGraduate_Form_Section">\' +\n
\t    \t        \t\t\'<label>x:</label>\' +\n
\t\t    \t        \t\'<input type="text" id="\' + id + \'_jGraduate_x2" size="3" title="Enter ending x value between 0.0 and 1.0"/>\' +\n
    \t\t    \t    \t\'<label> y:</label>\' +\n
        \t\t    \t\t\'<input type="text" id="\' + id + \'_jGraduate_y2" size="3" title="Enter ending y value between 0.0 and 1.0"/>\' +\n
        \t    \t\t\t\'<div id="\' + id + \'_jGraduate_colorBoxEnd" class="colorBox"></div>\' +\n
\t\t\t            \t\'<label id="\' + id + \'_jGraduate_endOpacity">100%</label>\' +\n
    \t    \t    \t\'</div>\' +\n
    \t    \t    \'</div>\' +\n
    \t    \t    \'<div class="lg_jGraduate_OpacityField">\' +\n
    \t    \t    \t\'<label class="lg_jGraduate_OpacityLabel">A: </label>\' +\n
    \t    \t    \t\'<input type="text" id="\' + id + \'_lg_jGraduate_OpacityInput" class="jGraduate_OpacityInput" size="3" value="100"/>%\' +\n
    \t    \t    \'</div>\' +\n
    \t       \t\'</div>\' +\n
        \t    \'<div class="jGraduate_OkCancel">\' +\n
            \t\t\'<input type="button" id="\' + id + \'_lg_jGraduate_Ok" class="jGraduate_Ok" value="OK"/>\' +\n
            \t\t\'<input type="button" id="\' + id + \'_lg_jGraduate_Cancel" class="jGraduate_Cancel" value="Cancel"/>\' +\n
            \t\'</div>\' +\n
            \t\'<div class="jGraduate_LightBox"></div>\' +\n
            \t\'<div id="\' + id + \'_jGraduate_stopPicker" class="jGraduate_stopPicker"></div>\');\n
            \t\n
            rgPicker.html(\n
            \t\'<div class="jGraduate_Swatch">\' +\n
            \t\t\'<h2 class="jGraduate_Title">\' + $settings.window.pickerTitle + \'</h2>\' +\n
            \t\t\'<div id="\' + id + \'_rg_jGraduate_GradContainer" class="jGraduate_GradContainer"></div>\' +\n
            \t\t\'<div id="\' + id + \'_rg_jGraduate_Opacity" class="jGraduate_Opacity" title="Click to set overall opacity of the gradient paint">\' +\n
            \t\t\t\'<img id="\' + id + \'_rg_jGraduate_AlphaArrows" class="jGraduate_AlphaArrows" src="\' + $settings.images.clientPath + \'rangearrows2.gif"></img>\' +\n
            \t\t\'</div>\' +\n
            \t\'</div>\' + \n
\t\t\t\t\'<div id="jGraduate_radColors" class="jGraduate_StopSection">\' +\n
\t\t\t\t\t\'<label class="jGraduate_Form_Heading">Colors</label>\' +\n
\t\t\t\t\t\'<div class="jGraduate_Form_Section jGraduate_Colorblocks">\' +\n
\t\t\t\t\t\t\'<div class="jGraduate_colorblock"><span>Center:</span>\' +\n
\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_colorBoxCenter" class="colorBox"></div>\' +\n
\t\t\t\t\t\t\'<label id="\' + id + \'_rg_jGraduate_centerOpacity"> 100%</label></div>\' +\n
\n
\t\t\t\t\t\t\'<div class="jGraduate_colorblock"><span>Outer:</span>\' +\n
\t\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_colorBoxOuter" class="colorBox"></div>\' +\n
\t\t\t\t\t\t\t\'<label id="\' + id + \'_jGraduate_outerOpacity"> 100%</label></div>\' +\n
\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\'</div>\' +\n
\t\t\t\t\'<div class="jGraduate_StopSection">\' +\n
\t\t\t\t\'</div>\' +\n
            \t\'<div class="jGraduate_Form">\' +\n
        \t   \t\t\'<div class="jGraduate_StopSection">\' +\n
\t            \t\t\'<label class="jGraduate_Form_Heading">Center Point</label>\' +\n
    \t        \t\t\'<div class="jGraduate_Form_Section">\' +\n
\t    \t        \t\t\'<label>x:</label>\' +\n
\t\t    \t        \t\'<input type="text" id="\' + id + \'_jGraduate_cx" size="3" title="Enter x value between 0.0 and 1.0"/>\' +\n
    \t\t    \t    \t\'<label> y:</label>\' +\n
        \t\t    \t\t\'<input type="text" id="\' + id + \'_jGraduate_cy" size="3" title="Enter y value between 0.0 and 1.0"/>\' +\n
    \t    \t    \t\'</div>\' +\n
    \t    \t    \'</div>\' +\n
        \t   \t\t\'<div class="jGraduate_StopSection">\' +\n
\t            \t\t\'<label class="jGraduate_Form_Heading">Focal Point</label>\' +\n
    \t        \t\t\'<div class="jGraduate_Form_Section">\' +\n
\t    \t        \t\t\'<label>Match center: <input type="checkbox" checked="checked" id="\' + id + \'_jGraduate_match_ctr"/></label><br/>\' +\n
\t    \t        \t\t\'<label>x:</label>\' +\n
\t\t    \t        \t\'<input type="text" id="\' + id + \'_jGraduate_fx" size="3" title="Enter x value between 0.0 and 1.0"/>\' +\n
    \t\t    \t    \t\'<label> y:</label>\' +\n
        \t\t    \t\t\'<input type="text" id="\' + id + \'_jGraduate_fy" size="3" title="Enter y value between 0.0 and 1.0"/>\' +\n
    \t    \t    \t\'</div>\' +\n
    \t    \t    \'</div>\' +\n
        \t   \t\t\'<div class="jGraduate_RadiusField">\' +\n
\t            \t\t\'<label class="jGraduate_Form_Heading">Radius</label>\' +\n
    \t        \t\t\'<div class="jGraduate_Form_Section">\' +\n
\t\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_RadiusContainer" class="jGraduate_RadiusContainer"></div>\' +\n
\t\t\t\t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_RadiusInput" size="3" value="100"/>%\' +\n
\t\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_Radius" class="jGraduate_Radius" title="Click to set radius">\' +\n
\t\t\t\t\t\t\t\t\'<img id="\' + id + \'_jGraduate_RadiusArrows" class="jGraduate_RadiusArrows" src="\' + $settings.images.clientPath + \'rangearrows2.gif"></img>\' +\n
\t\t\t\t\t\t\t\'</div>\' +\n
    \t    \t    \t\'</div>\' +\n
    \t    \t    \'</div>\' +\n
    \t       \t\'</div>\' +\n
\t\t\t\t\'<div class="rg_jGraduate_OpacityField">\' +\n
\t\t\t\t\t\'<label class="rg_jGraduate_OpacityLabel">A: </label>\' +\n
\t\t\t\t\t\'<input type="text" id="\' + id + \'_rg_jGraduate_OpacityInput" class="jGraduate_OpacityInput" size="3" value="100"/>%\' +\n
\t\t\t\t\'</div>\' +\n
        \t    \'<div class="jGraduate_OkCancel">\' +\n
            \t\t\'<input type="button" id="\' + id + \'_rg_jGraduate_Ok" class="jGraduate_Ok" value="OK"/>\' +\n
            \t\t\'<input type="button" id="\' + id + \'_rg_jGraduate_Cancel" class="jGraduate_Cancel" value="Cancel"/>\' +\n
            \t\'</div>\' +\n
            \t\'<div class="jGraduate_LightBox"></div>\' +\n
            \t\'<div id="\' + id + \'_rg_jGraduate_stopPicker" class="jGraduate_stopPicker"></div>\');\n
\t\t\t\n
\t\t\t// --------------\n
            // Set up all the SVG elements (the gradient, stops and rectangle)\n
            var MAX = 256, MARGINX = 0, MARGINY = 0, STOP_RADIUS = 15/2,\n
            \tSIZEX = MAX - 2*MARGINX, SIZEY = MAX - 2*MARGINY;\n
            \t\n
            $.each([\'lg\', \'rg\'], function(i) {\n
            \tvar grad_id = id + \'_\' + this;\n
\t\t\t\tvar container = document.getElementById(grad_id+\'_jGraduate_GradContainer\');\n
\t\t\t\tvar svg = container.appendChild(document.createElementNS(ns.svg, \'svg\'));\n
\t\t\t\tsvg.id = grad_id + \'_jgraduate_svg\';            \n
\t\t\t\tsvg.setAttribute(\'width\', MAX);\n
\t\t\t\tsvg.setAttribute(\'height\', MAX);\n
\t\t\t\tsvg.setAttribute("xmlns", ns.svg);\n
            });\n
\t\t\t\n
\t\t\t\n
\t\t\t// Linear gradient\n
\t\t\t(function() {\n
\t\t\t\tvar svg = document.getElementById(id + \'_lg_jgraduate_svg\');\n
\t\t\t\t\n
\t\t\t\t// if we are sent a gradient, import it \n
\t\t\t\tif ($this.paint.type == "linearGradient") {\n
\t\t\t\t\t$this.paint.linearGradient.id = id+\'_jgraduate_grad\';\n
\t\t\t\t\t$this.paint.linearGradient = svg.appendChild($.cloneNode($this.paint.linearGradient));\n
\t\t\t\t} else { // we create a gradient\n
\t\t\t\t\tvar grad = svg.appendChild(document.createElementNS(ns.svg, \'linearGradient\'));\n
\t\t\t\t\tgrad.id = id+\'_jgraduate_grad\';\n
\t\t\t\t\tgrad.setAttribute(\'x1\',\'0.0\');\n
\t\t\t\t\tgrad.setAttribute(\'y1\',\'0.0\');\n
\t\t\t\t\tgrad.setAttribute(\'x2\',\'1.0\');\n
\t\t\t\t\tgrad.setAttribute(\'y2\',\'1.0\');\n
\t\t\t\t\t\n
\t\t\t\t\tvar begin = grad.appendChild(document.createElementNS(ns.svg, \'stop\'));\n
\t\t\t\t\tbegin.setAttribute(\'offset\', \'0.0\');\n
\t\t\t\t\tbegin.setAttribute(\'stop-color\', \'#ff0000\');\n
\t\n
\t\t\t\t\tvar end = grad.appendChild(document.createElementNS(ns.svg, \'stop\'));\n
\t\t\t\t\tend.setAttribute(\'offset\', \'1.0\');\n
\t\t\t\t\tend.setAttribute(\'stop-color\', \'#ffff00\');\n
\t\t\t\t\n
\t\t\t\t\t$this.paint.linearGradient = grad;\n
\t\t\t\t}\n
\t\n
\t\t\t\tvar gradalpha = $this.paint.alpha;\n
\t\t\t\t$(\'#\' + id + \'_lg_jGraduate_OpacityInput\').val(gradalpha);\n
\t\t\t\tvar posx = parseInt(255*(gradalpha/100)) - 4.5;\n
\t\t\t\t$(\'#\' + id + \'_lg_jGraduate_AlphaArrows\').css({\'margin-left\':posx});\n
\t\t\t\t\n
\t\t\t\tvar x1 = parseFloat($this.paint.linearGradient.getAttribute(\'x1\')||0.0),\n
\t\t\t\t\ty1 = parseFloat($this.paint.linearGradient.getAttribute(\'y1\')||0.0),\n
\t\t\t\t\tx2 = parseFloat($this.paint.linearGradient.getAttribute(\'x2\')||1.0),\n
\t\t\t\t\ty2 = parseFloat($this.paint.linearGradient.getAttribute(\'y2\')||0.0);\n
\t\t\t\t\n
\t\t\t\tvar rect = document.createElementNS(ns.svg, \'rect\');\n
\t\t\t\trect.id = id + \'_lg_jgraduate_rect\';\n
\t\t\t\trect.setAttribute(\'x\', MARGINX);\n
\t\t\t\trect.setAttribute(\'y\', MARGINY);\n
\t\t\t\trect.setAttribute(\'width\', SIZEY);\n
\t\t\t\trect.setAttribute(\'height\', SIZEY);\n
\t\t\t\trect.setAttribute(\'fill\', \'url(#\'+id+\'_jgraduate_grad)\');\n
\t\t\t\trect.setAttribute(\'fill-opacity\', \'1.0\');\n
\t\t\t\trect = svg.appendChild(rect);\n
\t\t\t\t$(\'#\' + id + \'_lg_jgraduate_rect\').attr(\'fill-opacity\', gradalpha/100);\n
\t\t\t\t\n
\t\t\t\t// stop visuals created here\n
\t\t\t\tvar beginStop = document.createElementNS(ns.svg, \'image\');\n
\t\t\t\tbeginStop.id = id + "_stop1";\n
\t\t\t\tbeginStop.setAttribute(\'class\', \'stop\');\n
\t\t\t\tbeginStop.setAttributeNS(ns.xlink, \'href\', $settings.images.clientPath + \'mappoint.gif\');\n
\t\t\t\tbeginStop.setAttributeNS(ns.xlink, "title", "Begin Stop");\n
\t\t\t\tbeginStop.appendChild(document.createElementNS(ns.svg, \'title\')).appendChild(\n
\t\t\t\t\tdocument.createTextNode("Begin Stop"));\n
\t\t\t\tbeginStop.setAttribute(\'width\', 18);\n
\t\t\t\tbeginStop.setAttribute(\'height\', 18);\n
\t\t\t\tbeginStop.setAttribute(\'x\', MARGINX + SIZEX*x1 - STOP_RADIUS);\n
\t\t\t\tbeginStop.setAttribute(\'y\', MARGINY + SIZEY*y1 - STOP_RADIUS);\n
\t\t\t\tbeginStop.setAttribute(\'cursor\', \'move\');\n
\t\t\t\t// must append only after setting all attributes due to Webkit Bug 27952\n
\t\t\t\t// https://bugs.webkit.org/show_bug.cgi?id=27592\n
\t\t\t\tbeginStop = svg.appendChild(beginStop);\n
\t\t\t\t\n
\t\t\t\tvar endStop = document.createElementNS(ns.svg, \'image\');\n
\t\t\t\tendStop.id = id + "_stop2";\n
\t\t\t\tendStop.setAttribute(\'class\', \'stop\');\n
\t\t\t\tendStop.setAttributeNS(ns.xlink, \'href\', $settings.images.clientPath + \'mappoint.gif\');\n
\t\t\t\tendStop.setAttributeNS(ns.xlink, "title", "End Stop");\n
\t\t\t\tendStop.appendChild(document.createElementNS(ns.svg, \'title\')).appendChild(\n
\t\t\t\t\tdocument.createTextNode("End Stop"));\n
\t\t\t\tendStop.setAttribute(\'width\', 18);\n
\t\t\t\tendStop.setAttribute(\'height\', 18);\n
\t\t\t\tendStop.setAttribute(\'x\', MARGINX + SIZEX*x2 - STOP_RADIUS);\n
\t\t\t\tendStop.setAttribute(\'y\', MARGINY + SIZEY*y2 - STOP_RADIUS);\n
\t\t\t\tendStop.setAttribute(\'cursor\', \'move\');\n
\t\t\t\tendStop = svg.appendChild(endStop);\n
\t\t\t\t\n
\t\t\t\t// bind GUI elements\n
\t\t\t\t$(\'#\'+id+\'_lg_jGraduate_Ok\').bind(\'click\', function() {\n
\t\t\t\t\t$this.paint.type = "linearGradient";\n
\t\t\t\t\t$this.paint.solidColor = null;\n
\t\t\t\t\tokClicked();\n
\t\t\t\t});\n
\t\t\t\t$(\'#\'+id+\'_lg_jGraduate_Cancel\').bind(\'click\', function(paint) {\n
\t\t\t\t\tcancelClicked();\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar x1 = $this.paint.linearGradient.getAttribute(\'x1\');\n
\t\t\t\tif(!x1) x1 = "0.0";\n
\t\t\t\tvar x1Input = $(\'#\'+id+\'_jGraduate_x1\');\n
\t\t\t\tx1Input.val(x1);\n
\t\t\t\tx1Input.change( function() {\n
\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0.0 || this.value > 1.0) { \n
\t\t\t\t\t\tthis.value = 0.0; \n
\t\t\t\t\t}\n
\t\t\t\t\t$this.paint.linearGradient.setAttribute(\'x1\', this.value);\n
\t\t\t\t\tbeginStop.setAttribute(\'x\', MARGINX + SIZEX*this.value - STOP_RADIUS);\n
\t\t\t\t});\n
\t\n
\t\t\t\tvar y1 = $this.paint.linearGradient.getAttribute(\'y1\');\n
\t\t\t\tif(!y1) y1 = "0.0";\n
\t\t\t\tvar y1Input = $(\'#\'+id+\'_jGraduate_y1\');\n
\t\t\t\ty1Input.val(y1);\n
\t\t\t\ty1Input.change( function() {\n
\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0.0 || this.value > 1.0) { \n
\t\t\t\t\t\tthis.value = 0.0; \n
\t\t\t\t\t}\n
\t\t\t\t\t$this.paint.linearGradient.setAttribute(\'y1\', this.value);\n
\t\t\t\t\tbeginStop.setAttribute(\'y\', MARGINY + SIZEY*this.value - STOP_RADIUS);\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar x2 = $this.paint.linearGradient.getAttribute(\'x2\');\n
\t\t\t\tif(!x2) x2 = "1.0";\n
\t\t\t\tvar x2Input = $(\'#\'+id+\'_jGraduate_x2\');\n
\t\t\t\tx2Input.val(x2);\n
\t\t\t\tx2Input.change( function() {\n
\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0.0 || this.value > 1.0) { \n
\t\t\t\t\t\tthis.value = 1.0;\n
\t\t\t\t\t}\n
\t\t\t\t\t$this.paint.linearGradient.setAttribute(\'x2\', this.value);\n
\t\t\t\t\tendStop.setAttribute(\'x\', MARGINX + SIZEX*this.value - STOP_RADIUS);\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar y2 = $this.paint.linearGradient.getAttribute(\'y2\');\n
\t\t\t\tif(!y2) y2 = "0.0";\n
\t\t\t\ty2Input = $(\'#\'+id+\'_jGraduate_y2\');\n
\t\t\t\ty2Input.val(y2);\n
\t\t\t\ty2Input.change( function() {\n
\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0.0 || this.value > 1.0) { \n
\t\t\t\t\t\tthis.value = 0.0;\n
\t\t\t\t\t}\n
\t\t\t\t\t$this.paint.linearGradient.setAttribute(\'y2\', this.value);\n
\t\t\t\t\tendStop.setAttribute(\'y\', MARGINY + SIZEY*this.value - STOP_RADIUS);\n
\t\t\t\t});            \n
\t\t\t\t\n
\t\t\t\tvar stops = $this.paint.linearGradient.getElementsByTagNameNS(ns.svg, \'stop\');\n
\t\t\t\tvar numstops = stops.length;\n
\t\t\t\t// if there are not at least two stops, then \n
\t\t\t\tif (numstops < 2) {\n
\t\t\t\t\twhile (numstops < 2) {\n
\t\t\t\t\t\t$this.paint.linearGradient.appendChild( document.createElementNS(ns.svg, \'stop\') );\n
\t\t\t\t\t\t++numstops;\n
\t\t\t\t\t}\n
\t\t\t\t\tstops = $this.paint.linearGradient.getElementsByTagNameNS(ns.svg, \'stop\');\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tvar setLgOpacitySlider = function(e, div) {\n
\t\t\t\t\tvar offset = div.offset();\n
\t\t\t\t\tvar x = (e.pageX - offset.left - parseInt(div.css(\'border-left-width\')));\n
\t\t\t\t\tif (x > 255) x = 255;\n
\t\t\t\t\tif (x < 0) x = 0;\n
\t\t\t\t\tvar posx = x - 4.5;\n
\t\t\t\t\tx /= 255;\n
\t\t\t\t\t$(\'#\' + id + \'_lg_jGraduate_AlphaArrows\').css({\'margin-left\':posx});\n
\t\t\t\t\t$(\'#\' + id + \'_lg_jgraduate_rect\').attr(\'fill-opacity\', x);\n
\t\t\t\t\tx = parseInt(x*100);\n
\t\t\t\t\t$(\'#\' + id + \'_lg_jGraduate_OpacityInput\').val(x);\n
\t\t\t\t\t$this.paint.alpha = x;\n
\t\t\t\t};\n
\t\t\t\t\n
\t\t\t\t// handle dragging on the opacity slider\n
\t\t\t\tvar bSlidingOpacity = false;\n
\t\t\t\t$(\'#\' + id + \'_lg_jGraduate_Opacity\').mousedown(function(evt) {\n
\t\t\t\t\tsetLgOpacitySlider(evt, $(this));\n
\t\t\t\t\tbSlidingOpacity = true;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t}).mousemove(function(evt) {\n
\t\t\t\t\tif (bSlidingOpacity) {\n
\t\t\t\t\t\tsetLgOpacitySlider(evt, $(this));\n
\t\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t\t}\n
\t\t\t\t}).mouseup(function(evt) {\n
\t\t\t\t\tsetLgOpacitySlider(evt, $(this));\n
\t\t\t\t\tbSlidingOpacity = false;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\t// handle dragging the stop around the swatch\n
\t\t\t\tvar draggingStop = null;\n
\t\t\t\tvar startx = -1, starty = -1;\n
\t\t\t\t// for whatever reason, Opera does not allow $(\'image.stop\') here,\n
\t\t\t\t// and Firefox 1.5 does not allow $(\'.stop\')\n
\t\t\t\t$(\'.stop, #color_picker_lg_jGraduate_GradContainer image\').mousedown(function(evt) {\n
\t\t\t\t\tdraggingStop = this;\n
\t\t\t\t\tstartx = evt.clientX;\n
\t\t\t\t\tstarty = evt.clientY;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t});\n
\t\t\t\t$(\'#\'+id+\'_lg_jgraduate_svg\').mousemove(function(evt) {\n
\t\t\t\t\tif (null != draggingStop) {\n
\t\t\t\t\t\tvar dx = evt.clientX - startx;\n
\t\t\t\t\t\tvar dy = evt.clientY - starty;\n
\t\t\t\t\t\tstartx += dx;\n
\t\t\t\t\t\tstarty += dy;\n
\t\t\t\t\t\tvar x = parseFloat(draggingStop.getAttribute(\'x\')) + dx;\n
\t\t\t\t\t\tvar y = parseFloat(draggingStop.getAttribute(\'y\')) + dy;\n
\t\n
\t\t\t\t\t\t// clamp stop to the swatch\n
\t\t\t\t\t\tif (x < MARGINX - STOP_RADIUS) x = MARGINX - STOP_RADIUS;\n
\t\t\t\t\t\tif (y < MARGINY - STOP_RADIUS) y = MARGINY - STOP_RADIUS;\n
\t\t\t\t\t\tif (x > MARGINX + SIZEX - STOP_RADIUS) x = MARGINX + SIZEX - STOP_RADIUS;\n
\t\t\t\t\t\tif (y > MARGINY + SIZEY - STOP_RADIUS) y = MARGINY + SIZEY - STOP_RADIUS;\n
\t\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t\tdraggingStop.setAttribute(\'x\', x);\n
\t\t\t\t\t\tdraggingStop.setAttribute(\'y\', y);\n
\t\n
\t\t\t\t\t\t// calculate stop offset            \t\t\n
\t\t\t\t\t\tvar fracx = (x - MARGINX + STOP_RADIUS)/SIZEX;\n
\t\t\t\t\t\tvar fracy = (y - MARGINY + STOP_RADIUS)/SIZEY;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tif (draggingStop.id == (id+\'_stop1\')) {\n
\t\t\t\t\t\t\tx1Input.val(fracx);\n
\t\t\t\t\t\t\ty1Input.val(fracy);\n
\t\t\t\t\t\t\t$this.paint.linearGradient.setAttribute(\'x1\', fracx);\n
\t\t\t\t\t\t\t$this.paint.linearGradient.setAttribute(\'y1\', fracy);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\tx2Input.val(fracx);\n
\t\t\t\t\t\t\ty2Input.val(fracy);\n
\t\t\t\t\t\t\t$this.paint.linearGradient.setAttribute(\'x2\', fracx);\n
\t\t\t\t\t\t\t$this.paint.linearGradient.setAttribute(\'y2\', fracy);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\t$(\'#\'+id+\'_lg_jgraduate_svg\').mouseup(function(evt) {\n
\t\t\t\t\tdraggingStop = null;\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar beginColor = stops[0].getAttribute(\'stop-color\');\n
\t\t\t\tif(!beginColor) beginColor = \'#000\';\n
\t\t\t\tbeginColorBox = $(\'#\'+id+\'_jGraduate_colorBoxBegin\');\n
\t\t\t\tbeginColorBox.css({\'background-color\':beginColor});\n
\t\n
\t\t\t\tvar beginOpacity = stops[0].getAttribute(\'stop-opacity\');\n
\t\t\t\tif(!beginOpacity) beginOpacity = \'1.0\';\n
\t\t\t\t$(\'#\'+id+\'lg_jGraduate_beginOpacity\').html( (beginOpacity*100)+\'%\' );\n
\t\n
\t\t\t\tvar endColor = stops[stops.length-1].getAttribute(\'stop-color\');\n
\t\t\t\tif(!endColor) endColor = \'#000\';\n
\t\t\t\tendColorBox = $(\'#\'+id+\'_jGraduate_colorBoxEnd\');\n
\t\t\t\tendColorBox.css({\'background-color\':endColor});\n
\t\n
\t\t\t\tvar endOpacity = stops[stops.length-1].getAttribute(\'stop-opacity\');\n
\t\t\t\tif(!endOpacity) endOpacity = \'1.0\';\n
\t\t\t\t$(\'#\'+id+\'jGraduate_endOpacity\').html( (endOpacity*100)+\'%\' );\n
\t\t\t\t\n
\t\t\t\t$(\'#\'+id+\'_jGraduate_colorBoxBegin\').click(function() {\n
\t\t\t\t\t$(\'div.jGraduate_LightBox\').show();\t\t\t\n
\t\t\t\t\tvar colorbox = $(this);\n
\t\t\t\t\tvar thisAlpha = (parseFloat(beginOpacity)*255).toString(16);\n
\t\t\t\t\twhile (thisAlpha.length < 2) { thisAlpha = "0" + thisAlpha; }\n
\t\t\t\t\tcolor = beginColor.substr(1) + thisAlpha;\n
\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').css({\'left\': 100, \'bottom\': 15}).jPicker({\n
\t\t\t\t\t\t\twindow: { title: "Pick the start color and opacity for the gradient" },\n
\t\t\t\t\t\t\timages: { clientPath: $settings.images.clientPath },\n
\t\t\t\t\t\t\tcolor: { active: color, alphaSupport: true }\n
\t\t\t\t\t\t}, function(color){\n
\t\t\t\t\t\t\tbeginColor = color.get_Hex() ? (\'#\'+color.get_Hex()) : "none";\n
\t\t\t\t\t\t\tbeginOpacity = color.get_A() ? color.get_A()/100 : 1;\n
\t\t\t\t\t\t\tcolorbox.css(\'background\', beginColor);\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_beginOpacity\').html(parseInt(beginOpacity*100)+\'%\');\n
\t\t\t\t\t\t\tstops[0].setAttribute(\'stop-color\', beginColor);\n
\t\t\t\t\t\t\tstops[0].setAttribute(\'stop-opacity\', beginOpacity);\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t}, null, function() {\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t});\n
\t\t\t\t});\n
\t\t\t\t$(\'#\'+id+\'_jGraduate_colorBoxEnd\').click(function() {\n
\t\t\t\t\t$(\'div.jGraduate_LightBox\').show();\n
\t\t\t\t\tvar colorbox = $(this);\n
\t\t\t\t\tvar thisAlpha = (parseFloat(endOpacity)*255).toString(16);\n
\t\t\t\t\twhile (thisAlpha.length < 2) { thisAlpha = "0" + thisAlpha; }\n
\t\t\t\t\tcolor = endColor.substr(1) + thisAlpha;\n
\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').css({\'left\': 100, \'top\': 15}).jPicker({\n
\t\t\t\t\t\t\twindow: { title: "Pick the end color and opacity for the gradient" },\n
\t\t\t\t\t\t\timages: { clientPath: $settings.images.clientPath },\n
\t\t\t\t\t\t\tcolor: { active: color, alphaSupport: true }\n
\t\t\t\t\t\t}, function(color){\n
\t\t\t\t\t\t\tendColor = color.get_Hex() ? (\'#\'+color.get_Hex()) : "none";\n
\t\t\t\t\t\t\tendOpacity = color.get_A() ? color.get_A()/100 : 1;\n
\t\t\t\t\t\t\tcolorbox.css(\'background\', endColor);\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_endOpacity\').html(parseInt(endOpacity*100)+\'%\');\n
\t\t\t\t\t\t\tstops[1].setAttribute(\'stop-color\', endColor);\n
\t\t\t\t\t\t\tstops[1].setAttribute(\'stop-opacity\', endOpacity);\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t}, null, function() {\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t});\n
\t\t\t\t});            \n
\t\t\t\t\n
\t\t\t\t// --------------\n
\t\t\t\tvar thisAlpha = ($this.paint.alpha*255/100).toString(16);\n
\t\t\t\twhile (thisAlpha.length < 2) { thisAlpha = "0" + thisAlpha; }\n
\t\t\t\tcolor = $this.paint.solidColor == "none" ? "" : $this.paint.solidColor + thisAlpha;\n
\t\t\t\tcolPicker.jPicker(\n
\t\t\t\t\t{\n
\t\t\t\t\t\twindow: { title: $settings.window.pickerTitle },\n
\t\t\t\t\t\timages: { clientPath: $settings.images.clientPath },\n
\t\t\t\t\t\tcolor: { active: color, alphaSupport: true }\n
\t\t\t\t\t},\n
\t\t\t\t\tfunction(color) {\n
\t\t\t\t\t\t$this.paint.type = "solidColor";\n
\t\t\t\t\t\t$this.paint.alpha = color.get_A() ? color.get_A() : 100;\n
\t\t\t\t\t\t$this.paint.solidColor = color.get_Hex() ? color.get_Hex() : "none";\n
\t\t\t\t\t\t$this.paint.linearGradient = null;\n
\t\t\t\t\t\tokClicked(); \n
\t\t\t\t\t},\n
\t\t\t\t\tnull,\n
\t\t\t\t\tfunction(){ cancelClicked(); }\n
\t\t\t\t\t);\n
\t\t\t}());\t\n
\t\t\t\n
\t\t\t\n
\t\t\t// Radial gradient\n
\t\t\t(function() {\n
\t\t\t\tvar svg = document.getElementById(id + \'_rg_jgraduate_svg\');\n
\t\t\t\t\n
\t\t\t\t// if we are sent a gradient, import it \n
\t\t\t\tif ($this.paint.type == "radialGradient") {\n
\t\t\t\t\t$this.paint.radialGradient.id = id+\'_rg_jgraduate_grad\';\n
\t\t\t\t\t$this.paint.radialGradient = svg.appendChild($.cloneNode($this.paint.radialGradient));\n
\t\t\t\t} else { // we create a gradient\n
\t\t\t\t\tvar grad = svg.appendChild(document.createElementNS(ns.svg, \'radialGradient\'));\n
\t\t\t\t\tgrad.id = id+\'_rg_jgraduate_grad\';\n
\t\t\t\t\tgrad.setAttribute(\'cx\',\'0.5\');\n
\t\t\t\t\tgrad.setAttribute(\'cy\',\'0.5\');\n
\t\t\t\t\tgrad.setAttribute(\'r\',\'0.5\');\n
\t\t\t\t\t\n
\t\t\t\t\tvar begin = grad.appendChild(document.createElementNS(ns.svg, \'stop\'));\n
\t\t\t\t\tbegin.setAttribute(\'offset\', \'0.0\');\n
\t\t\t\t\tbegin.setAttribute(\'stop-color\', \'#ff0000\');\n
\t\n
\t\t\t\t\tvar end = grad.appendChild(document.createElementNS(ns.svg, \'stop\'));\n
\t\t\t\t\tend.setAttribute(\'offset\', \'1.0\');\n
\t\t\t\t\tend.setAttribute(\'stop-color\', \'#ffff00\');\n
\t\t\t\t\n
\t\t\t\t\t$this.paint.radialGradient = grad;\n
\t\t\t\t}\n
\t\n
\t\t\t\tvar gradalpha = $this.paint.alpha;\n
\t\t\t\t$(\'#\' + id + \'_rg_jGraduate_OpacityInput\').val(gradalpha);\n
\t\t\t\tvar posx = parseInt(255*(gradalpha/100)) - 4.5;\n
\t\t\t\t$(\'#\' + id + \'_rg_jGraduate_AlphaArrows\').css({\'margin-left\':posx});\n
\t\t\t\t\n
\t\t\t\tvar grad = $this.paint.radialGradient;\n
\t\t\t\t\n
\t\t\t\tvar cx = parseFloat(grad.getAttribute(\'cx\')||0.5),\n
\t\t\t\t\tcy = parseFloat(grad.getAttribute(\'cy\')||0.5),\n
\t\t\t\t\tfx = parseFloat(grad.getAttribute(\'fx\')||0.5),\n
\t\t\t\t\tfy = parseFloat(grad.getAttribute(\'fy\')||0.5);\n
\t\t\t\t\n
\t\t\t\t// No match, so show focus point\n
\t\t\t\tvar showFocus = grad.getAttribute(\'fx\') != null && !(cx == fx && cy == fy);\n
\t\t\t\t\n
\t\t\t\tvar rect = document.createElementNS(ns.svg, \'rect\');\n
\t\t\t\trect.id = id + \'_rg_jgraduate_rect\';\n
\t\t\t\trect.setAttribute(\'x\', MARGINX);\n
\t\t\t\trect.setAttribute(\'y\', MARGINY);\n
\t\t\t\trect.setAttribute(\'width\', SIZEY);\n
\t\t\t\trect.setAttribute(\'height\', SIZEY);\n
\t\t\t\trect.setAttribute(\'fill\', \'url(#\'+id+\'_rg_jgraduate_grad)\');\n
\t\t\t\trect.setAttribute(\'fill-opacity\', \'1.0\');\n
\n
\t\t\t\trect = svg.appendChild(rect);\n
\t\t\t\t\n
\t\t\t\t$(\'#\' + id + \'_rg_jgraduate_rect\').attr(\'fill-opacity\', gradalpha/100);\n
\n
\t\t\t\t// stop visuals created here\n
\t\t\t\tvar centerPoint = document.createElementNS(ns.svg, \'image\');\n
\t\t\t\tcenterPoint.id = id + "_center_pt";\n
\t\t\t\tcenterPoint.setAttribute(\'class\', \'stop\');\n
\t\t\t\tcenterPoint.setAttributeNS(ns.xlink, \'href\', $settings.images.clientPath + \'mappoint_c.png\');\n
\t\t\t\tcenterPoint.setAttributeNS(ns.xlink, "title", "Center Point");\n
\t\t\t\tcenterPoint.appendChild(document.createElementNS(ns.svg, \'title\')).appendChild(\n
\t\t\t\t\tdocument.createTextNode("Center Point"));\n
\t\t\t\tcenterPoint.setAttribute(\'width\', 18);\n
\t\t\t\tcenterPoint.setAttribute(\'height\', 18);\n
\t\t\t\tcenterPoint.setAttribute(\'x\', MARGINX + SIZEX*cx - STOP_RADIUS);\n
\t\t\t\tcenterPoint.setAttribute(\'y\', MARGINY + SIZEY*cy - STOP_RADIUS);\n
\t\t\t\tcenterPoint.setAttribute(\'cursor\', \'move\');\n
\n
\t\t\t\t\n
\t\t\t\tvar focusPoint = document.createElementNS(ns.svg, \'image\');\n
\t\t\t\tfocusPoint.id = id + "_focus_pt";\n
\t\t\t\tfocusPoint.setAttribute(\'class\', \'stop\');\n
\t\t\t\tfocusPoint.setAttributeNS(ns.xlink, \'href\', $settings.images.clientPath + \'mappoint_f.png\');\n
\t\t\t\tfocusPoint.setAttributeNS(ns.xlink, "title", "Focus Point");\n
\t\t\t\tfocusPoint.appendChild(document.createElementNS(ns.svg, \'title\')).appendChild(\n
\t\t\t\t\tdocument.createTextNode("Focus Point"));\n
\t\t\t\tfocusPoint.setAttribute(\'width\', 18);\n
\t\t\t\tfocusPoint.setAttribute(\'height\', 18);\n
\t\t\t\tfocusPoint.setAttribute(\'x\', MARGINX + SIZEX*fx - STOP_RADIUS);\n
\t\t\t\tfocusPoint.setAttribute(\'y\', MARGINY + SIZEY*fy - STOP_RADIUS);\n
\t\t\t\tfocusPoint.setAttribute(\'cursor\', \'move\');\n
\t\t\t\t\n
\t\t\t\t// must append only after setting all attributes due to Webkit Bug 27952\n
\t\t\t\t// https://bugs.webkit.org/show_bug.cgi?id=27592\n
\t\t\t\t\n
\t\t\t\t// centerPoint is added last so it is moved first\n
\t\t\t\tfocusPoint = svg.appendChild(focusPoint);\n
\t\t\t\tcenterPoint = svg.appendChild(centerPoint);\n
\t\t\t\t\n
\t\t\t\t// bind GUI elements\n
\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_Ok\').bind(\'click\', function() {\n
\t\t\t\t\t$this.paint.type = "radialGradient";\n
\t\t\t\t\t$this.paint.solidColor = null;\n
\t\t\t\t\tokClicked();\n
\t\t\t\t});\n
\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_Cancel\').bind(\'click\', function(paint) {\n
\t\t\t\t\tcancelClicked();\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar cx = $this.paint.radialGradient.getAttribute(\'cx\');\n
\t\t\t\tif(!cx) cx = "0.0";\n
\t\t\t\tvar cxInput = $(\'#\'+id+\'_jGraduate_cx\');\n
\t\t\t\tcxInput.val(cx);\n
\t\t\t\tcxInput.change( function() {\n
\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0.0 || this.value > 1.0) { \n
\t\t\t\t\t\tthis.value = 0.0; \n
\t\t\t\t\t}\n
\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'cx\', this.value);\n
\t\t\t\t\tcenterPoint.setAttribute(\'x\', MARGINX + SIZEX*this.value - STOP_RADIUS);\n
\t\t\t\t});\n
\t\n
\t\t\t\tvar cy = $this.paint.radialGradient.getAttribute(\'cy\');\n
\t\t\t\tif(!cy) cy = "0.0";\n
\t\t\t\tvar cyInput = $(\'#\'+id+\'_jGraduate_cy\');\n
\t\t\t\tcyInput.val(cy);\n
\t\t\t\tcyInput.change( function() {\n
\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0.0 || this.value > 1.0) { \n
\t\t\t\t\t\tthis.value = 0.0; \n
\t\t\t\t\t}\n
\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'cy\', this.value);\n
\t\t\t\t\tcenterPoint.setAttribute(\'y\', MARGINY + SIZEY*this.value - STOP_RADIUS);\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar fx = $this.paint.radialGradient.getAttribute(\'fx\');\n
\t\t\t\tif(!fx) fx = "1.0";\n
\t\t\t\tvar fxInput = $(\'#\'+id+\'_jGraduate_fx\');\n
\t\t\t\tfxInput.val(fx);\n
\t\t\t\tfxInput.change( function() {\n
\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0.0 || this.value > 1.0) { \n
\t\t\t\t\t\tthis.value = 1.0;\n
\t\t\t\t\t}\n
\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'fx\', this.value);\n
\t\t\t\t\tfocusPoint.setAttribute(\'x\', MARGINX + SIZEX*this.value - STOP_RADIUS);\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar fy = $this.paint.radialGradient.getAttribute(\'fy\');\n
\t\t\t\tif(!fy) fy = "0.0";\n
\t\t\t\tvar fyInput = $(\'#\'+id+\'_jGraduate_fy\');\n
\t\t\t\tfyInput.val(fy);\n
\t\t\t\tfyInput.change( function() {\n
\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0.0 || this.value > 1.0) { \n
\t\t\t\t\t\tthis.value = 0.0;\n
\t\t\t\t\t}\n
\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'fy\', this.value);\n
\t\t\t\t\tfocusPoint.setAttribute(\'y\', MARGINY + SIZEY*this.value - STOP_RADIUS);\n
\t\t\t\t});      \n
\t\t\t\t\n
\t\t\t\tif(!showFocus) {\n
\t\t\t\t\tfocusPoint.setAttribute(\'display\', \'none\');\t\n
\t\t\t\t\tfxInput.val("");\n
\t\t\t\t\tfyInput.val("");\n
\t\t\t\t}\n
\n
\t\t\t\t$("#" + id + "_jGraduate_match_ctr")[0].checked = !showFocus;\n
\t\t\t\t\n
\t\t\t\tvar lastfx, lastfy;\n
\t\t\t\t\n
\t\t\t\t$("#" + id + "_jGraduate_match_ctr").change(function() {\n
\t\t\t\t\tshowFocus = !this.checked;\n
\t\t\t\t\tfocusPoint.setAttribute(\'display\', showFocus?\'inline\':\'none\');\n
\t\t\t\t\tfxInput.val("");\n
\t\t\t\t\tfyInput.val("");\n
\t\t\t\t\tvar grad = $this.paint.radialGradient;\n
\t\t\t\t\tif(!showFocus) {\n
\t\t\t\t\t\tlastfx = grad.getAttribute(\'fx\');\n
\t\t\t\t\t\tlastfy = grad.getAttribute(\'fy\');\n
\t\t\t\t\t\tgrad.removeAttribute(\'fx\');\n
\t\t\t\t\t\tgrad.removeAttribute(\'fy\');\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tvar fx = lastfx || .5;\n
\t\t\t\t\t\tvar fy = lastfy || .5;\n
\t\t\t\t\t\tgrad.setAttribute(\'fx\', fx);\n
\t\t\t\t\t\tgrad.setAttribute(\'fy\', fy);\n
\t\t\t\t\t\tfxInput.val(fx);\n
\t\t\t\t\t\tfyInput.val(fy);\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar stops = $this.paint.radialGradient.getElementsByTagNameNS(ns.svg, \'stop\');\n
\t\t\t\tvar numstops = stops.length;\n
\t\t\t\t// if there are not at least two stops, then \n
\t\t\t\tif (numstops < 2) {\n
\t\t\t\t\twhile (numstops < 2) {\n
\t\t\t\t\t\t$this.paint.radialGradient.appendChild( document.createElementNS(ns.svg, \'stop\') );\n
\t\t\t\t\t\t++numstops;\n
\t\t\t\t\t}\n
\t\t\t\t\tstops = $this.paint.radialGradient.getElementsByTagNameNS(ns.svg, \'stop\');\n
\t\t\t\t}\n
\t\t\t\tvar radius = $this.paint.radialGradient.getAttribute(\'r\')-0;\n
\t\t\t\tvar radiusx = parseInt((245/2)*(radius)) - 4.5;\n
\t\t\t\t$(\'#\' + id + \'_jGraduate_RadiusArrows\').css({\'margin-left\':radiusx});\n
\t\t\t\t$(\'#\' + id + \'_jGraduate_RadiusInput\').val(parseInt(radius*100)).change(function(e) {\n
\t\t\t\t\tvar x = this.value / 100;\n
\t\t\t\t\tif(x < 0.01) {\n
\t\t\t\t\t\tx = 0.01;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'r\', x);\n
\t\t\t\t\t// Allow higher value, but pretend it\'s the max for the slider\n
\t\t\t\t\tif(x > 2) x = 2;\n
\t\t\t\t\tvar posx = parseInt((245/2) * x) - 4.5;\n
\t\t\t\t\t$(\'#\' + id + \'_jGraduate_RadiusArrows\').css({\'margin-left\':posx});\n
\t\t\t\t\t\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar setRgOpacitySlider = function(e, div) {\n
\t\t\t\t\tvar offset = div.offset();\n
\t\t\t\t\tvar x = (e.pageX - offset.left - parseInt(div.css(\'border-left-width\')));\n
\t\t\t\t\tif (x > 255) x = 255;\n
\t\t\t\t\tif (x < 0) x = 0;\n
\t\t\t\t\tvar posx = x - 4.5;\n
\t\t\t\t\tx /= 255;\n
\t\t\t\t\t$(\'#\' + id + \'_rg_jGraduate_AlphaArrows\').css({\'margin-left\':posx});\n
\t\t\t\t\t$(\'#\' + id + \'_rg_jgraduate_rect\').attr(\'fill-opacity\', x);\n
\t\t\t\t\tx = parseInt(x*100);\n
\t\t\t\t\t$(\'#\' + id + \'_rg_jGraduate_OpacityInput\').val(x);\n
\t\t\t\t\t$this.paint.alpha = x;\n
\t\t\t\t};\n
\t\t\t\t\n
\t\t\t\t// handle dragging on the opacity slider\n
\t\t\t\tvar bSlidingOpacity = false;\n
\t\t\t\t$(\'#\' + id + \'_rg_jGraduate_Opacity\').mousedown(function(evt) {\n
\t\t\t\t\tsetRgOpacitySlider(evt, $(this));\n
\t\t\t\t\tbSlidingOpacity = true;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t}).mousemove(function(evt) {\n
\t\t\t\t\tif (bSlidingOpacity) {\n
\t\t\t\t\t\tsetRgOpacitySlider(evt, $(this));\n
\t\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t\t}\n
\t\t\t\t}).mouseup(function(evt) {\n
\t\t\t\t\tsetRgOpacitySlider(evt, $(this));\n
\t\t\t\t\tbSlidingOpacity = false;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar setRadiusSlider = function(e, div) {\n
\t\t\t\t\tvar offset = div.offset();\n
\t\t\t\t\tvar x = (e.pageX - offset.left - parseInt(div.css(\'border-left-width\')));\n
\t\t\t\t\tif (x > 245) x = 245;\n
\t\t\t\t\tif (x <= 1) x = 1;\n
\t\t\t\t\tvar posx = x - 5;\n
\t\t\t\t\tx /= (245/2);\n
\t\t\t\t\t$(\'#\' + id + \'_jGraduate_RadiusArrows\').css({\'margin-left\':posx});\n
\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'r\', x);\n
\t\t\t\t\tx = parseInt(x*100);\n
\t\t\t\t\t\n
\t\t\t\t\t$(\'#\' + id + \'_jGraduate_RadiusInput\').val(x);\n
\t\t\t\t};\n
\t\t\t\t\n
\t\t\t\t// handle dragging on the radius slider\n
\t\t\t\tvar bSlidingRadius = false;\n
\t\t\t\t$(\'#\' + id + \'_jGraduate_Radius\').mousedown(function(evt) {\n
\t\t\t\t\tsetRadiusSlider(evt, $(this));\n
\t\t\t\t\tbSlidingRadius = true;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t}).mousemove(function(evt) {\n
\t\t\t\t\tif (bSlidingRadius) {\n
\t\t\t\t\t\tsetRadiusSlider(evt, $(this));\n
\t\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t\t}\n
\t\t\t\t}).mouseup(function(evt) {\n
\t\t\t\t\tsetRadiusSlider(evt, $(this));\n
\t\t\t\t\tbSlidingRadius = false;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\t\n
\t\t\t\t// handle dragging the stop around the swatch\n
\t\t\t\tvar draggingStop = null;\n
\t\t\t\tvar startx = -1, starty = -1;\n
\t\t\t\t// for whatever reason, Opera does not allow $(\'image.stop\') here,\n
\t\t\t\t// and Firefox 1.5 does not allow $(\'.stop\')\n
\t\t\t\t$(\'.stop, #color_picker_rg_jGraduate_GradContainer image\').mousedown(function(evt) {\n
\t\t\t\t\tdraggingStop = this;\n
\t\t\t\t\tstartx = evt.clientX;\n
\t\t\t\t\tstarty = evt.clientY;\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t});\n
\t\t\t\t$(\'#\'+id+\'_rg_jgraduate_svg\').mousemove(function(evt) {\n
\t\t\t\t\tif (null != draggingStop) {\n
\t\t\t\t\t\tvar dx = evt.clientX - startx;\n
\t\t\t\t\t\tvar dy = evt.clientY - starty;\n
\t\t\t\t\t\tstartx += dx;\n
\t\t\t\t\t\tstarty += dy;\n
\t\t\t\t\t\tvar x = parseFloat(draggingStop.getAttribute(\'x\')) + dx;\n
\t\t\t\t\t\tvar y = parseFloat(draggingStop.getAttribute(\'y\')) + dy;\n
\t\n
\t\t\t\t\t\t// clamp stop to the swatch\n
\t\t\t\t\t\tif (x < MARGINX - STOP_RADIUS) x = MARGINX - STOP_RADIUS;\n
\t\t\t\t\t\tif (y < MARGINY - STOP_RADIUS) y = MARGINY - STOP_RADIUS;\n
\t\t\t\t\t\tif (x > MARGINX + SIZEX - STOP_RADIUS) x = MARGINX + SIZEX - STOP_RADIUS;\n
\t\t\t\t\t\tif (y > MARGINY + SIZEY - STOP_RADIUS) y = MARGINY + SIZEY - STOP_RADIUS;\n
\t\t\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t\tdraggingStop.setAttribute(\'x\', x);\n
\t\t\t\t\t\tdraggingStop.setAttribute(\'y\', y);\n
\t\n
\t\t\t\t\t\t// calculate stop offset            \t\t\n
\t\t\t\t\t\tvar fracx = (x - MARGINX + STOP_RADIUS)/SIZEX;\n
\t\t\t\t\t\tvar fracy = (y - MARGINY + STOP_RADIUS)/SIZEY;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tif (draggingStop.id == (id+\'_center_pt\')) {\n
\t\t\t\t\t\t\tcxInput.val(fracx);\n
\t\t\t\t\t\t\tcyInput.val(fracy);\n
\t\t\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'cx\', fracx);\n
\t\t\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'cy\', fracy);\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\tif(!showFocus) {\n
\t\t\t\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'fx\', fracx);\n
\t\t\t\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'fy\', fracy);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telse {\n
\t\t\t\t\t\t\tfxInput.val(fracx);\n
\t\t\t\t\t\t\tfyInput.val(fracy);\n
\t\t\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'fx\', fracx);\n
\t\t\t\t\t\t\t$this.paint.radialGradient.setAttribute(\'fy\', fracy);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\t$(\'#\'+id+\'_rg_jgraduate_svg\').mouseup(function(evt) {\n
\t\t\t\t\tdraggingStop = null;\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\tvar centerColor = stops[0].getAttribute(\'stop-color\');\n
\t\t\t\tif(!centerColor) centerColor = \'#000\';\n
\t\t\t\tcenterColorBox = $(\'#\'+id+\'_jGraduate_colorBoxCenter\');\n
\t\t\t\tcenterColorBox.css({\'background-color\':centerColor});\n
\t\n
\t\t\t\tvar centerOpacity = stops[0].getAttribute(\'stop-opacity\');\n
\t\t\t\tif(!centerOpacity) centerOpacity = \'1.0\';\n
\t\t\t\t$(\'#\'+id+\'jGraduate_centerOpacity\').html( (centerOpacity*100)+\'%\' );\n
\t\n
\t\t\t\tvar outerColor = stops[stops.length-1].getAttribute(\'stop-color\');\n
\t\t\t\tif(!outerColor) outerColor = \'#000\';\n
\t\t\t\touterColorBox = $(\'#\'+id+\'_jGraduate_colorBoxOuter\');\n
\t\t\t\touterColorBox.css({\'background-color\':outerColor});\n
\t\n
\t\t\t\tvar outerOpacity = stops[stops.length-1].getAttribute(\'stop-opacity\');\n
\t\t\t\tif(!outerOpacity) outerOpacity = \'1.0\';\n
\t\t\t\t$(\'#\'+id+\'rg_jGraduate_outerOpacity\').html( (outerOpacity*100)+\'%\' );\n
\t\t\t\t\n
\t\t\t\t$(\'#\'+id+\'_jGraduate_colorBoxCenter\').click(function() {\n
\t\t\t\t\t$(\'div.jGraduate_LightBox\').show();\t\t\t\n
\t\t\t\t\tvar colorbox = $(this);\n
\t\t\t\t\tvar thisAlpha = (parseFloat(centerOpacity)*255).toString(16);\n
\t\t\t\t\twhile (thisAlpha.length < 2) { thisAlpha = "0" + thisAlpha; }\n
\t\t\t\t\tcolor = centerColor.substr(1) + thisAlpha;\n
\t\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_stopPicker\').css({\'left\': 100, \'bottom\': 15}).jPicker({\n
\t\t\t\t\t\t\twindow: { title: "Pick the center color and opacity for the gradient" },\n
\t\t\t\t\t\t\timages: { clientPath: $settings.images.clientPath },\n
\t\t\t\t\t\t\tcolor: { active: color, alphaSupport: true }\n
\t\t\t\t\t\t}, function(color){\n
\t\t\t\t\t\t\tcenterColor = color.get_Hex() ? (\'#\'+color.get_Hex()) : "none";\n
\t\t\t\t\t\t\tcenterOpacity = color.get_A() ? color.get_A()/100 : 1;\n
\t\t\t\t\t\t\tcolorbox.css(\'background\', centerColor);\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_centerOpacity\').html(parseInt(centerOpacity*100)+\'%\');\n
\t\t\t\t\t\t\tstops[0].setAttribute(\'stop-color\', centerColor);\n
\t\t\t\t\t\t\tstops[0].setAttribute(\'stop-opacity\', centerOpacity);\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t}, null, function() {\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t});\n
\t\t\t\t});\n
\t\t\t\t$(\'#\'+id+\'_jGraduate_colorBoxOuter\').click(function() {\n
\t\t\t\t\t$(\'div.jGraduate_LightBox\').show();\n
\t\t\t\t\tvar colorbox = $(this);\n
\t\t\t\t\tvar thisAlpha = (parseFloat(outerOpacity)*255).toString(16);\n
\t\t\t\t\twhile (thisAlpha.length < 2) { thisAlpha = "0" + thisAlpha; }\n
\t\t\t\t\tcolor = outerColor.substr(1) + thisAlpha;\n
\t\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_stopPicker\').css({\'left\': 100, \'top\': 15}).jPicker({\n
\t\t\t\t\t\t\twindow: { title: "Pick the outer color and opacity for the gradient" },\n
\t\t\t\t\t\t\timages: { clientPath: $settings.images.clientPath },\n
\t\t\t\t\t\t\tcolor: { active: color, alphaSupport: true }\n
\t\t\t\t\t\t}, function(color){\n
\t\t\t\t\t\t\touterColor = color.get_Hex() ? (\'#\'+color.get_Hex()) : "none";\n
\t\t\t\t\t\t\touterOpacity = color.get_A() ? color.get_A()/100 : 1;\n
\t\t\t\t\t\t\tcolorbox.css(\'background\', outerColor);\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_outerOpacity\').html(parseInt(outerOpacity*100)+\'%\');\n
\t\t\t\t\t\t\tstops[1].setAttribute(\'stop-color\', outerColor);\n
\t\t\t\t\t\t\tstops[1].setAttribute(\'stop-opacity\', outerOpacity);\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t}, null, function() {\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_rg_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t});\n
\t\t\t\t});            \n
\t\t\t\t\n
\t\t\t\t// --------------\n
\t\t\t\tvar thisAlpha = ($this.paint.alpha*255/100).toString(16);\n
\t\t\t\twhile (thisAlpha.length < 2) { thisAlpha = "0" + thisAlpha; }\n
\t\t\t\tcolor = $this.paint.solidColor == "none" ? "" : $this.paint.solidColor + thisAlpha;\n
\t\t\t\tcolPicker.jPicker(\n
\t\t\t\t\t{\n
\t\t\t\t\t\twindow: { title: $settings.window.pickerTitle },\n
\t\t\t\t\t\timages: { clientPath: $settings.images.clientPath },\n
\t\t\t\t\t\tcolor: { active: color, alphaSupport: true }\n
\t\t\t\t\t},\n
\t\t\t\t\tfunction(color) {\n
\t\t\t\t\t\t$this.paint.type = "solidColor";\n
\t\t\t\t\t\t$this.paint.alpha = color.get_A() ? color.get_A() : 100;\n
\t\t\t\t\t\t$this.paint.solidColor = color.get_Hex() ? color.get_Hex() : "none";\n
\t\t\t\t\t\t$this.paint.radialGradient = null;\n
\t\t\t\t\t\tokClicked(); \n
\t\t\t\t\t},\n
\t\t\t\t\tnull,\n
\t\t\t\t\tfunction(){ cancelClicked(); }\n
\t\t\t\t\t);\n
\t\t\t}());\t\n
\t\t\t\n
\t\t\tvar tabs = $(idref + \' .jGraduate_tabs li\');\n
\t\t\ttabs.click(function() {\n
\t\t\t\ttabs.removeClass(\'jGraduate_tab_current\');\n
\t\t\t\t$(this).addClass(\'jGraduate_tab_current\');\n
\t\t\t\t$(idref + " > div").hide();\n
\t\t\t\t$(idref + \' .jGraduate_\' +  $(this).attr(\'data-type\') + \'Pick\').show();\n
\t\t\t});\n
\t\t\t\n
\t\t\t$(idref + " > div").hide();\n
\t\t\ttabs.removeClass(\'jGraduate_tab_current\');\n
\t\t\tvar tab;\n
\t\t\tswitch ( $this.paint.type ) {\n
\t\t\t\tcase \'linearGradient\':\n
\t\t\t\t\ttab = $(idref + \' .jGraduate_tab_lingrad\');\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase \'radialGradient\':\n
\t\t\t\t\ttab = $(idref + \' .jGraduate_tab_radgrad\');\n
\t\t\t\t\tbreak;\n
\t\t\t\tdefault:\n
\t\t\t\t\ttab = $(idref + \' .jGraduate_tab_color\');\n
\t\t\t\t\tbreak;\n
\t\t\t}\n
\t\t\ttab.addClass(\'jGraduate_tab_current\').click();\t\n
\n
\t\t\t$this.show();\n
\t\t});\n
\t};\n
})();

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>44285</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
