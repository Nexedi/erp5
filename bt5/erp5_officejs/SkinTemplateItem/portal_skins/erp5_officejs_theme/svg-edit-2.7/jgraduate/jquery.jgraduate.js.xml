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
            <value> <string>ts40515059.52</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.jgraduate.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

﻿/*\n
 * jGraduate 0.4\n
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
\t\tpaint: a Paint object,\n
\t\tnewstop: String of value "same", "inverse", "black" or "white" \n
\t\t\t\t OR object with one or both values {color: #Hex color, opac: number 0-1}\n
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
\n
$.jGraduate = { \n
\tPaint:\n
\t\tfunction(opt) {\n
\t\t\tvar options = opt || {};\n
\t\t\tthis.alpha = isNaN(options.alpha) ? 100 : options.alpha;\n
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
    \t\t\t\t\tthis.linearGradient = options.copy.linearGradient.cloneNode(true);\n
    \t\t\t\t\tbreak;\n
    \t\t\t\tcase "radialGradient":\n
    \t\t\t\t\tthis.radialGradient = options.copy.radialGradient.cloneNode(true);\n
    \t\t\t\t\tbreak;\n
    \t\t\t}\n
    \t\t}\n
    \t\t// create linear gradient paint\n
    \t\telse if (options.linearGradient) {\n
    \t\t\tthis.type = "linearGradient";\n
    \t\t\tthis.solidColor = null;\n
    \t\t\tthis.radialGradient = null;\n
    \t\t\tthis.linearGradient = options.linearGradient.cloneNode(true);\n
    \t\t}\n
    \t\t// create linear gradient paint\n
    \t\telse if (options.radialGradient) {\n
    \t\t\tthis.type = "radialGradient";\n
    \t\t\tthis.solidColor = null;\n
    \t\t\tthis.linearGradient = null;\n
    \t\t\tthis.radialGradient = options.radialGradient.cloneNode(true);\n
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
\t},\n
\tnewstop: \'inverse\' // same, inverse, black, white\n
};\n
\n
var isGecko = navigator.userAgent.indexOf(\'Gecko/\') >= 0;\n
\n
function setAttrs(elem, attrs) {\n
\tif(isGecko) {\n
\t\tfor (var aname in attrs) elem.setAttribute(aname, attrs[aname]);\n
\t} else {\n
\t\tfor (var aname in attrs) {\n
\t\t\tvar val = attrs[aname], prop = elem[aname];\n
\t\t\tif(prop && prop.constructor === \'SVGLength\') {\n
\t\t\t\tprop.baseVal.value = val;\n
\t\t\t} else {\n
\t\t\t\telem.setAttribute(aname, val);\n
\t\t\t}\n
\t\t}\n
\t}\n
}\n
\n
function mkElem(name, attrs, newparent) {\n
\tvar elem = document.createElementNS(ns.svg, name);\n
\tsetAttrs(elem, attrs);\n
\tif(newparent) newparent.appendChild(elem);\n
\treturn elem;\n
}\n
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
\t            switch ( $this.paint.type ) {\n
\t            \tcase "radialGradient":\n
\t            \t\t$this.paint.linearGradient = null;\n
\t            \t\tbreak;\n
\t            \tcase "linearGradient":\n
\t            \t\t$this.paint.radialGradient = null;\n
\t            \t\tbreak;\n
\t            \tcase "solidColor":\n
\t            \t\t$this.paint.radialGradient = $this.paint.linearGradient = null;\n
\t            \t\tbreak;\n
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
\t\t\tvar $win = $(window);\n
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
            \t\t\t\'<div class="jGraduate_gradPick"></div>\' +\n
\t\t\t\t\t\t\'<div class="jGraduate_LightBox"></div>\' +\n
\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_stopPicker" class="jGraduate_stopPicker"></div>\'\n
            \t\t\t\n
            \t\t\t\n
            \t\t\t);\n
\t\t\tvar colPicker = $(idref + \'> .jGraduate_colPick\');\n
\t\t\tvar gradPicker = $(idref + \'> .jGraduate_gradPick\');\n
\t\t\t\n
            gradPicker.html(\n
            \t\'<div id="\' + id + \'_jGraduate_Swatch" class="jGraduate_Swatch">\' +\n
            \t\t\'<h2 class="jGraduate_Title">\' + $settings.window.pickerTitle + \'</h2>\' +\n
            \t\t\'<div id="\' + id + \'_jGraduate_GradContainer" class="jGraduate_GradContainer"></div>\' +\n
            \t\t\'<div id="\' + id + \'_jGraduate_StopSlider" class="jGraduate_StopSlider"></div>\' +\n
            \t\'</div>\' + \n
            \t\'<div class="jGraduate_Form jGraduate_Points jGraduate_lg_field">\' +\n
            \t\t\'<div class="jGraduate_StopSection">\' +\n
\t            \t\t\'<label class="jGraduate_Form_Heading">Begin Point</label>\' +\n
    \t        \t\t\'<div class="jGraduate_Form_Section">\' +\n
        \t    \t\t\t\'<label>x:</label>\' +\n
            \t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_x1" size="3" title="Enter starting x value between 0.0 and 1.0"/>\' +\n
            \t\t\t\t\'<label>y:</label>\' +\n
            \t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_y1" size="3" title="Enter starting y value between 0.0 and 1.0"/>\' +\n
        \t   \t\t\t\'</div>\' +\n
        \t   \t\t\'</div>\' +\n
        \t   \t\t\'<div class="jGraduate_StopSection">\' +\n
\t            \t\t\'<label class="jGraduate_Form_Heading">End Point</label>\' +\n
    \t        \t\t\'<div class="jGraduate_Form_Section">\' +\n
\t    \t        \t\t\'<label>x:</label>\' +\n
\t\t    \t        \t\'<input type="text" id="\' + id + \'_jGraduate_x2" size="3" title="Enter ending x value between 0.0 and 1.0"/>\' +\n
    \t\t    \t    \t\'<label>y:</label>\' +\n
        \t\t    \t\t\'<input type="text" id="\' + id + \'_jGraduate_y2" size="3" title="Enter ending y value between 0.0 and 1.0"/>\' +\n
    \t    \t    \t\'</div>\' +\n
    \t    \t    \'</div>\' +\n
    \t       \t\'</div>\' +\n
            \t\'<div class="jGraduate_Form jGraduate_Points jGraduate_rg_field">\' +\n
\t\t\t\t\t\'<div class="jGraduate_StopSection">\' +\n
\t\t\t\t\t\t\'<label class="jGraduate_Form_Heading">Center Point</label>\' +\n
\t\t\t\t\t\t\'<div class="jGraduate_Form_Section">\' +\n
\t\t\t\t\t\t\t\'<label>x:</label>\' +\n
\t\t\t\t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_cx" size="3" title="Enter x value between 0.0 and 1.0"/>\' +\n
\t\t\t\t\t\t\t\'<label>y:</label>\' +\n
\t\t\t\t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_cy" size="3" title="Enter y value between 0.0 and 1.0"/>\' +\n
\t\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\t\'<div class="jGraduate_StopSection">\' +\n
\t\t\t\t\t\t\'<label class="jGraduate_Form_Heading">Focal Point</label>\' +\n
\t\t\t\t\t\t\'<div class="jGraduate_Form_Section">\' +\n
\t\t\t\t\t\t\t\'<label>Match center: <input type="checkbox" checked="checked" id="\' + id + \'_jGraduate_match_ctr"/></label><br/>\' +\n
\t\t\t\t\t\t\t\'<label>x:</label>\' +\n
\t\t\t\t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_fx" size="3" title="Enter x value between 0.0 and 1.0"/>\' +\n
\t\t\t\t\t\t\t\'<label>y:</label>\' +\n
\t\t\t\t\t\t\t\'<input type="text" id="\' + id + \'_jGraduate_fy" size="3" title="Enter y value between 0.0 and 1.0"/>\' +\n
\t\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\t\'</div>\' +\n
    \t       \t\'</div>\' +\n
\t\t\t\t\'<div class="jGraduate_StopSection jGraduate_SpreadMethod">\' +\n
\t\t\t\t\t\'<label class="jGraduate_Form_Heading">Spread method</label>\' +\n
\t\t\t\t\t\'<div class="jGraduate_Form_Section">\' +\n
\t\t\t\t\t\t\'<select class="jGraduate_spreadMethod">\' +\n
\t\t\t\t\t\t\t\'<option value=pad selected>Pad</option>\' +\n
\t\t\t\t\t\t\t\'<option value=reflect>Reflect</option>\' +\n
\t\t\t\t\t\t\t\'<option value=repeat>Repeat</option>\' +\n
\t\t\t\t\t\t\'</select>\' + \n
\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\'</div>\' +\n
            \t\'<div class="jGraduate_Form">\' +\n
        \t   \t\t\'<div class="jGraduate_Slider jGraduate_RadiusField jGraduate_rg_field">\' +\n
\t\t\t\t\t\t\'<label class="prelabel">Radius:</label>\' +\n
\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_Radius" class="jGraduate_SliderBar jGraduate_Radius" title="Click to set radius">\' +\n
\t\t\t\t\t\t\t\'<img id="\' + id + \'_jGraduate_RadiusArrows" class="jGraduate_RadiusArrows" src="\' + $settings.images.clientPath + \'rangearrows2.gif">\' +\n
\t\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\t\t\'<label><input type="text" id="\' + id + \'_jGraduate_RadiusInput" size="3" value="100"/>%</label>\' + \n
    \t    \t    \'</div>\' +\n
        \t   \t\t\'<div class="jGraduate_Slider jGraduate_EllipField jGraduate_rg_field">\' +\n
\t\t\t\t\t\t\'<label class="prelabel">Ellip:</label>\' +\n
\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_Ellip" class="jGraduate_SliderBar jGraduate_Ellip" title="Click to set Ellip">\' +\n
\t\t\t\t\t\t\t\'<img id="\' + id + \'_jGraduate_EllipArrows" class="jGraduate_EllipArrows" src="\' + $settings.images.clientPath + \'rangearrows2.gif">\' +\n
\t\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\t\t\'<label><input type="text" id="\' + id + \'_jGraduate_EllipInput" size="3" value="0"/>%</label>\' + \n
    \t    \t    \'</div>\' +\n
        \t   \t\t\'<div class="jGraduate_Slider jGraduate_AngleField jGraduate_rg_field">\' +\n
\t\t\t\t\t\t\'<label class="prelabel">Angle:</label>\' +\n
\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_Angle" class="jGraduate_SliderBar jGraduate_Angle" title="Click to set Angle">\' +\n
\t\t\t\t\t\t\t\'<img id="\' + id + \'_jGraduate_AngleArrows" class="jGraduate_AngleArrows" src="\' + $settings.images.clientPath + \'rangearrows2.gif">\' +\n
\t\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\t\t\'<label><input type="text" id="\' + id + \'_jGraduate_AngleInput" size="3" value="0"/>deg</label>\' + \n
    \t    \t    \'</div>\' +\n
        \t   \t\t\'<div class="jGraduate_Slider jGraduate_OpacField">\' +\n
\t\t\t\t\t\t\'<label class="prelabel">Opac:</label>\' +\n
\t\t\t\t\t\t\'<div id="\' + id + \'_jGraduate_Opac" class="jGraduate_SliderBar jGraduate_Opac" title="Click to set Opac">\' +\n
\t\t\t\t\t\t\t\'<img id="\' + id + \'_jGraduate_OpacArrows" class="jGraduate_OpacArrows" src="\' + $settings.images.clientPath + \'rangearrows2.gif">\' +\n
\t\t\t\t\t\t\'</div>\' +\n
\t\t\t\t\t\t\'<label><input type="text" id="\' + id + \'_jGraduate_OpacInput" size="3" value="100"/>%</label>\' + \n
    \t    \t    \'</div>\' +\n
    \t       \t\'</div>\' +\n
        \t    \'<div class="jGraduate_OkCancel">\' +\n
            \t\t\'<input type="button" id="\' + id + \'_jGraduate_Ok" class="jGraduate_Ok" value="OK"/>\' +\n
            \t\t\'<input type="button" id="\' + id + \'_jGraduate_Cancel" class="jGraduate_Cancel" value="Cancel"/>\' +\n
            \t\'</div>\');\n
            \t\n
\t\t\t// --------------\n
            // Set up all the SVG elements (the gradient, stops and rectangle)\n
            var MAX = 256, MARGINX = 0, MARGINY = 0, STOP_RADIUS = 15/2,\n
            \tSIZEX = MAX - 2*MARGINX, SIZEY = MAX - 2*MARGINY;\n
            \t\n
            var curType, curGradient, previewRect;\t\n
            \n
\t\t\tvar attr_input = {};\n
            \n
            var SLIDERW = 145;\n
            $(\'.jGraduate_SliderBar\').width(SLIDERW);\n
\t\t\t\n
\t\t\tvar container = $(\'#\' + id+\'_jGraduate_GradContainer\')[0];\n
\t\t\t\n
\t\t\tvar svg = mkElem(\'svg\', {\n
\t\t\t\tid: id + \'_jgraduate_svg\',\n
\t\t\t\twidth: MAX,\n
\t\t\t\theight: MAX,\n
\t\t\t\txmlns: ns.svg\n
\t\t\t}, container);\n
\t\t\t\n
\t\t\t// if we are sent a gradient, import it \n
\t\t\t\n
\t\t\tcurType = curType || $this.paint.type;\n
\t\t\t\n
\t\t\tvar grad = curGradient = $this.paint[curType];\n
\t\t\t\n
\t\t\tvar gradalpha = $this.paint.alpha;\n
\t\t\t\n
\t\t\tvar isSolid = curType === \'solidColor\';\n
\t\t\t\n
\t\t\t// Make any missing gradients\n
\t\t\tswitch ( curType ) {\n
\t\t\t\tcase "solidColor":\n
\t\t\t\t\t// fall through\n
\t\t\t\tcase "linearGradient":\n
\t\t\t\t\tif(!isSolid) {\n
\t\t\t\t\t\tcurGradient.id = id+\'_lg_jgraduate_grad\';\n
\t\t\t\t\t\tgrad = curGradient = svg.appendChild(curGradient);//.cloneNode(true));\n
\t\t\t\t\t}\n
\t\t\t\t\tmkElem(\'radialGradient\', {\n
\t\t\t\t\t\tid: id + \'_rg_jgraduate_grad\'\n
\t\t\t\t\t}, svg);\n
\t\t\t\t\tif(curType === "linearGradient") break;\n
\t\t\t\tcase "radialGradient":\n
\t\t\t\t\tif(!isSolid) {\n
\t\t\t\t\t\tcurGradient.id = id+\'_rg_jgraduate_grad\';\n
\t\t\t\t\t\tgrad = curGradient = svg.appendChild(curGradient);//.cloneNode(true));\n
\t\t\t\t\t}\n
\t\t\t\t\tmkElem(\'linearGradient\', {\n
\t\t\t\t\t\tid: id + \'_lg_jgraduate_grad\'\n
\t\t\t\t\t}, svg);\n
\t\t\t}\n
\t\t\t\n
\t\t\tif(isSolid) {\n
\t\t\t\tgrad = curGradient = $(\'#\' + id + \'_lg_jgraduate_grad\')[0];\n
\t\t\t\tvar color = $this.paint[curType];\n
\t\t\t\tmkStop(0, \'#\' + color, 1);\n
\t\t\t\t\n
\t\t\t\tvar type = typeof $settings.newstop;\n
\t\t\t\t\n
\t\t\t\tif(type === \'string\') {\n
\t\t\t\t\tswitch ( $settings.newstop ) {\n
\t\t\t\t\t\tcase \'same\':\n
\t\t\t\t\t\t\tmkStop(1, \'#\' + color, 1);\t\t\t\t\n
\t\t\t\t\t\t\tbreak;\n
\n
\t\t\t\t\t\tcase \'inverse\':\n
\t\t\t\t\t\t\t// Invert current color for second stop\n
\t\t\t\t\t\t\tvar inverted = \'\';\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\t\tfor(var i = 0; i < 6; i += 2) {\n
\t\t\t\t\t\t\t\tvar ch = color.substr(i, 2);\n
\t\t\t\t\t\t\t\tvar inv = (255 - parseInt(color.substr(i, 2), 16)).toString(16);\n
\t\t\t\t\t\t\t\tif(inv.length < 2) inv = 0 + inv;\n
\t\t\t\t\t\t\t\tinverted += inv;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tmkStop(1, \'#\' + inverted, 1);\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tcase \'white\':\n
\t\t\t\t\t\t\tmkStop(1, \'#ffffff\', 1);\n
\t\t\t\t\t\t\tbreak;\n
\t\n
\t\t\t\t\t\tcase \'black\':\n
\t\t\t\t\t\t\tmkStop(1, \'#000000\', 1);\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t} else if(type === \'object\'){\n
\t\t\t\t\tvar opac = (\'opac\' in $settings.newstop) ? $settings.newstop.opac : 1;\n
\t\t\t\t\tmkStop(1, ($settings.newstop.color || \'#\' + color), opac);\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t\n
\t\t\tvar x1 = parseFloat(grad.getAttribute(\'x1\')||0.0),\n
\t\t\t\ty1 = parseFloat(grad.getAttribute(\'y1\')||0.0),\n
\t\t\t\tx2 = parseFloat(grad.getAttribute(\'x2\')||1.0),\n
\t\t\t\ty2 = parseFloat(grad.getAttribute(\'y2\')||0.0);\n
\t\t\t\t\n
\t\t\tvar cx = parseFloat(grad.getAttribute(\'cx\')||0.5),\n
\t\t\t\tcy = parseFloat(grad.getAttribute(\'cy\')||0.5),\n
\t\t\t\tfx = parseFloat(grad.getAttribute(\'fx\')|| cx),\n
\t\t\t\tfy = parseFloat(grad.getAttribute(\'fy\')|| cy);\n
\n
\t\t\t\n
\t\t\tvar previewRect = mkElem(\'rect\', {\n
\t\t\t\tid: id + \'_jgraduate_rect\',\n
\t\t\t\tx: MARGINX,\n
\t\t\t\ty: MARGINY,\n
\t\t\t\twidth: SIZEX,\n
\t\t\t\theight: SIZEY,\n
\t\t\t\tfill: \'url(#\'+id+\'_jgraduate_grad)\',\n
\t\t\t\t\'fill-opacity\': gradalpha/100\n
\t\t\t}, svg);\n
\t\t\t\n
\t\t\t// stop visuals created here\n
\t\t\tvar beginCoord = $(\'<div/>\').attr({\n
\t\t\t\t\'class\': \'grad_coord jGraduate_lg_field\',\n
\t\t\t\ttitle: \'Begin Stop\'\n
\t\t\t}).text(1).css({\n
\t\t\t\ttop: y1 * MAX,\n
\t\t\t\tleft: x1 * MAX\n
\t\t\t}).data(\'coord\', \'start\').appendTo(container);\n
\t\t\t\n
\t\t\tvar endCoord = beginCoord.clone().text(2).css({\n
\t\t\t\ttop: y2 * MAX,\n
\t\t\t\tleft: x2 * MAX\n
\t\t\t}).attr(\'title\', \'End stop\').data(\'coord\', \'end\').appendTo(container);\n
\t\t\n
\t\t\tvar centerCoord = $(\'<div/>\').attr({\n
\t\t\t\t\'class\': \'grad_coord jGraduate_rg_field\',\n
\t\t\t\ttitle: \'Center stop\'\n
\t\t\t}).text(\'C\').css({\n
\t\t\t\ttop: cy * MAX,\n
\t\t\t\tleft: cx * MAX\n
\t\t\t}).data(\'coord\', \'center\').appendTo(container);\n
\t\t\t\n
\t\t\tvar focusCoord = centerCoord.clone().text(\'F\').css({\n
\t\t\t\ttop: fy * MAX,\n
\t\t\t\tleft: fx * MAX,\n
\t\t\t\tdisplay: \'none\'\n
\t\t\t}).attr(\'title\', \'Focus point\').data(\'coord\', \'focus\').appendTo(container);\n
\t\t\t\n
\t\t\tfocusCoord[0].id = id + \'_jGraduate_focusCoord\';\n
\t\t\t\n
\t\t\tvar coords = $(idref + \' .grad_coord\');\n
\t\t\t\n
// \t\t\t$(container).hover(function() {\n
// \t\t\t\tcoords.animate({\n
// \t\t\t\t\topacity: 1\n
// \t\t\t\t}, 500);\n
// \t\t\t}, function() {\n
// \t\t\t\tcoords.animate({\n
// \t\t\t\t\topacity: .2\n
// \t\t\t\t}, 500);\t\t\t\t\n
// \t\t\t});\n
\t\t\t\n
\t\t\t$.each([\'x1\', \'y1\', \'x2\', \'y2\', \'cx\', \'cy\', \'fx\', \'fy\'], function(i, attr) {\n
\t\t\t\tvar attrval = curGradient.getAttribute(attr);\n
\t\t\t\t\n
\t\t\t\tvar isRadial = isNaN(attr[1]);\n
\t\t\t\t\n
\t\t\t\tif(!attrval) {\n
\t\t\t\t\t// Set defaults\n
\t\t\t\t\tif(isRadial) {\n
\t\t\t\t\t\t// For radial points\n
\t\t\t\t\t\tattrval = "0.5";\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\t// Only x2 is 1\n
\t\t\t\t\t\tattrval = attr === \'x2\' ? "1.0" : "0.0";\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tattr_input[attr] = $(\'#\'+id+\'_jGraduate_\' + attr)\n
\t\t\t\t\t.val(attrval)\n
\t\t\t\t\t.change(function() {\n
\t\t\t\t\t\t// TODO: Support values < 0 and > 1 (zoomable preview?)\n
\t\t\t\t\t\tif (isNaN(parseFloat(this.value)) || this.value < 0) {\n
\t\t\t\t\t\t\tthis.value = 0.0; \n
\t\t\t\t\t\t} else if(this.value > 1) {\n
\t\t\t\t\t\t\tthis.value = 1.0;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tif(!(attr[0] === \'f\' && !showFocus)) {\n
\t\t\t\t\t\t\tif(isRadial && curType === \'radialGradient\' || !isRadial && curType === \'linearGradient\') {\n
\t\t\t\t\t\t\t\tcurGradient.setAttribute(attr, this.value);\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tif(isRadial) {\n
\t\t\t\t\t\t\tvar $elem = attr[0] === "c" ? centerCoord : focusCoord;\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tvar $elem = attr[1] === "1" ? beginCoord : endCoord;\t\t\t\t\t\t\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tvar cssName = attr.indexOf(\'x\') >= 0 ? \'left\' : \'top\';\n
\t\t\t\t\t\t\n
\t\t\t\t\t\t$elem.css(cssName, this.value * MAX);\n
\t\t\t\t}).change();\n
\t\t\t});\n
\n
\n
\t\t\t\n
\t\t\tfunction mkStop(n, color, opac, sel, stop_elem) {\n
\t\t\t\tvar stop = stop_elem || mkElem(\'stop\',{\'stop-color\':color,\'stop-opacity\':opac,offset:n}, curGradient);\n
\t\t\t\tif(stop_elem) {\n
\t\t\t\t\tcolor = stop_elem.getAttribute(\'stop-color\');\n
\t\t\t\t\topac = stop_elem.getAttribute(\'stop-opacity\');\n
\t\t\t\t\tn = stop_elem.getAttribute(\'offset\');\n
\t\t\t\t} else {\n
\t\t\t\t\tcurGradient.appendChild(stop);\n
\t\t\t\t}\n
\t\t\t\tif(opac === null) opac = 1;\n
\t\t\t\t\n
\t\t\t\tvar picker_d = \'M-6.2,0.9c3.6-4,6.7-4.3,6.7-12.4c-0.2,7.9,3.1,8.8,6.5,12.4c3.5,3.8,2.9,9.6,0,12.3c-3.1,2.8-10.4,2.7-13.2,0C-9.6,9.9-9.4,4.4-6.2,0.9z\';\n
\t\t\t\t\n
\t\t\t\tvar pathbg = mkElem(\'path\',{\n
\t\t\t\t\td: picker_d,\n
\t\t\t\t\tfill: \'url(#jGraduate_trans)\',\n
\t\t\t\t\ttransform: \'translate(\' + (10 + n * MAX) + \', 26)\'\n
\t\t\t\t}, stopGroup);\n
\t\t\t\t\n
\t\t\t\tvar path = mkElem(\'path\',{\n
\t\t\t\t\td: picker_d,\n
\t\t\t\t\tfill: color,\n
\t\t\t\t\t\'fill-opacity\': opac,\n
\t\t\t\t\ttransform: \'translate(\' + (10 + n * MAX) + \', 26)\',\n
\t\t\t\t\tstroke: \'#000\',\n
\t\t\t\t\t\'stroke-width\': 1.5\n
\t\t\t\t}, stopGroup);\n
\n
\t\t\t\t$(path).mousedown(function(e) {\n
\t\t\t\t\tselectStop(this);\n
\t\t\t\t\tdrag = cur_stop;\n
\t\t\t\t\t$win.mousemove(dragColor).mouseup(remDrags);\n
\t\t\t\t\tstop_offset = stopMakerDiv.offset();\n
\t\t\t\t\te.preventDefault();\n
\t\t\t\t\treturn false;\n
\t\t\t\t}).data(\'stop\', stop).data(\'bg\', pathbg).dblclick(function() {\n
\t\t\t\t\t$(\'div.jGraduate_LightBox\').show();\t\t\t\n
\t\t\t\t\tvar colorhandle = this;\n
\t\t\t\t\tvar stopOpacity = +stop.getAttribute(\'stop-opacity\') || 1;\n
\t\t\t\t\tvar stopColor = stop.getAttribute(\'stop-color\') || 1;\n
\t\t\t\t\tvar thisAlpha = (parseFloat(stopOpacity)*255).toString(16);\n
\t\t\t\t\twhile (thisAlpha.length < 2) { thisAlpha = "0" + thisAlpha; }\n
\t\t\t\t\tcolor = stopColor.substr(1) + thisAlpha;\n
\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').css({\'left\': 100, \'bottom\': 15}).jPicker({\n
\t\t\t\t\t\t\twindow: { title: "Pick the start color and opacity for the gradient" },\n
\t\t\t\t\t\t\timages: { clientPath: $settings.images.clientPath },\n
\t\t\t\t\t\t\tcolor: { active: color, alphaSupport: true }\n
\t\t\t\t\t\t}, function(color, arg2){\n
\t\t\t\t\t\t\tstopColor = color.val(\'hex\') ? (\'#\'+color.val(\'hex\')) : "none";\n
\t\t\t\t\t\t\tstopOpacity = color.val(\'a\') !== null ? color.val(\'a\')/256 : 1;\n
\t\t\t\t\t\t\tcolorhandle.setAttribute(\'fill\', stopColor);\n
\t\t\t\t\t\t\tcolorhandle.setAttribute(\'fill-opacity\', stopOpacity);\n
\t\t\t\t\t\t\tstop.setAttribute(\'stop-color\', stopColor);\n
\t\t\t\t\t\t\tstop.setAttribute(\'stop-opacity\', stopOpacity);\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t}, null, function() {\n
\t\t\t\t\t\t\t$(\'div.jGraduate_LightBox\').hide();\n
\t\t\t\t\t\t\t$(\'#\'+id+\'_jGraduate_stopPicker\').hide();\n
\t\t\t\t\t\t});\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\t$(curGradient).find(\'stop\').each(function() {\n
\t\t\t\t\tvar cur_s = $(this);\n
\t\t\t\t\tif(+this.getAttribute(\'offset\') > n) {\n
\t\t\t\t\t\tif(!color) {\n
\t\t\t\t\t\t\tvar newcolor = this.getAttribute(\'stop-color\');\n
\t\t\t\t\t\t\tvar newopac = this.getAttribute(\'stop-opacity\');\n
\t\t\t\t\t\t\tstop.setAttribute(\'stop-color\', newcolor);\n
\t\t\t\t\t\t\tpath.setAttribute(\'fill\', newcolor);\n
\t\t\t\t\t\t\tstop.setAttribute(\'stop-opacity\', newopac === null ? 1 : newopac);\n
\t\t\t\t\t\t\tpath.setAttribute(\'fill-opacity\', newopac === null ? 1 : newopac);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tcur_s.before(stop);\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\tif(sel) selectStop(path);\n
\t\t\t\treturn stop;\n
\t\t\t}\n
\t\t\t\n
\t\t\tfunction remStop() {\n
\t\t\t\tdelStop.setAttribute(\'display\', \'none\');\n
\t\t\t\tvar path = $(cur_stop);\n
\t\t\t\tvar stop = path.data(\'stop\');\n
\t\t\t\tvar bg = path.data(\'bg\');\n
\t\t\t\t$([cur_stop, stop, bg]).remove();\n
\t\t\t}\n
\t\t\t\n
\t\t\t\t\n
\t\t\tvar stops, stopGroup;\n
\t\t\t\n
\t\t\tvar stopMakerDiv = $(\'#\' + id + \'_jGraduate_StopSlider\');\n
\n
\t\t\tvar cur_stop, stopGroup, stopMakerSVG, drag;\n
\t\t\t\n
\t\t\tvar delStop = mkElem(\'path\',{\n
\t\t\t\td:\'m9.75,-6l-19.5,19.5m0,-19.5l19.5,19.5\',\n
\t\t\t\tfill:\'none\',\n
\t\t\t\tstroke:\'#D00\',\n
\t\t\t\t\'stroke-width\':5,\n
\t\t\t\tdisplay:\'none\'\n
\t\t\t}, stopMakerSVG);\n
\n
\t\t\t\n
\t\t\tfunction selectStop(item) {\n
\t\t\t\tif(cur_stop) cur_stop.setAttribute(\'stroke\', \'#000\');\n
\t\t\t\titem.setAttribute(\'stroke\', \'blue\');\n
\t\t\t\tcur_stop = item;\n
\t\t\t\tcur_stop.parentNode.appendChild(cur_stop);\n
\t\t\t// \tstops = $(\'stop\');\n
\t\t\t// \topac_select.val(cur_stop.attr(\'fill-opacity\') || 1);\n
\t\t\t// \troot.append(delStop);\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar stop_offset;\n
\t\t\t\n
\t\t\tfunction remDrags() {\n
\t\t\t\t$win.unbind(\'mousemove\', dragColor);\n
\t\t\t\tif(delStop.getAttribute(\'display\') !== \'none\') {\n
\t\t\t\t\tremStop();\n
\t\t\t\t}\n
\t\t\t\tdrag = null;\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar scale_x = 1, scale_y = 1, angle = 0;\n
\t\t\tvar c_x = cx;\n
\t\t\tvar c_y = cy;\n
\t\t\t\n
\t\t\tfunction xform() {\n
\t\t\t\tvar rot = angle?\'rotate(\' + angle + \',\' + c_x + \',\' + c_y + \') \':\'\';\n
\t\t\t\tif(scale_x === 1 && scale_y === 1) {\n
\t\t\t\t\tcurGradient.removeAttribute(\'gradientTransform\');\n
// \t\t\t\t\t$(\'#ang\').addClass(\'dis\');\n
\t\t\t\t} else {\n
\t\t\t\t\tvar x = -c_x * (scale_x-1);\n
\t\t\t\t\tvar y = -c_y * (scale_y-1);\n
\t\t\t\t\tcurGradient.setAttribute(\'gradientTransform\', rot + \'translate(\' + x + \',\' + y + \') scale(\' + scale_x + \',\' + scale_y + \')\');\n
// \t\t\t\t\t$(\'#ang\').removeClass(\'dis\');\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tfunction dragColor(evt) {\n
\n
\t\t\t\tvar x = evt.pageX - stop_offset.left;\n
\t\t\t\tvar y = evt.pageY - stop_offset.top;\n
\t\t\t\tx = x < 10 ? 10 : x > MAX + 10 ? MAX + 10: x;\n
\n
\t\t\t\tvar xf_str = \'translate(\' + x + \', 26)\';\n
\t\t\t\t\tif(y < -60 || y > 130) {\n
\t\t\t\t\t\tdelStop.setAttribute(\'display\', \'block\');\n
\t\t\t\t\t\tdelStop.setAttribute(\'transform\', xf_str);\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tdelStop.setAttribute(\'display\', \'none\');\n
\t\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tdrag.setAttribute(\'transform\', xf_str);\n
\t\t\t\t$.data(drag, \'bg\').setAttribute(\'transform\', xf_str);\n
\t\t\t\tvar stop = $.data(drag, \'stop\');\n
\t\t\t\tvar s_x = (x - 10) / MAX;\n
\t\t\t\t\n
\t\t\t\tstop.setAttribute(\'offset\', s_x);\n
\t\t\t\tvar last = 0;\n
\t\t\t\t\n
\t\t\t\t$(curGradient).find(\'stop\').each(function(i) {\n
\t\t\t\t\tvar cur = this.getAttribute(\'offset\');\n
\t\t\t\t\tvar t = $(this);\n
\t\t\t\t\tif(cur < last) {\n
\t\t\t\t\t\tt.prev().before(t);\n
\t\t\t\t\t\tstops = $(curGradient).find(\'stop\');\n
\t\t\t\t\t}\n
\t\t\t\t\tlast = cur;\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t}\n
\t\t\t\n
\t\t\tstopMakerSVG = mkElem(\'svg\', {\n
\t\t\t\twidth: \'100%\',\n
\t\t\t\theight: 45\n
\t\t\t}, stopMakerDiv[0]);\n
\t\t\t\n
\t\t\tvar trans_pattern = mkElem(\'pattern\', {\n
\t\t\t\twidth: 16,\n
\t\t\t\theight: 16,\n
\t\t\t\tpatternUnits: \'userSpaceOnUse\',\n
\t\t\t\tid: \'jGraduate_trans\'\n
\t\t\t}, stopMakerSVG);\n
\t\t\t\n
\t\t\tvar trans_img = mkElem(\'image\', {\n
\t\t\t\twidth: 16,\n
\t\t\t\theight: 16\n
\t\t\t}, trans_pattern);\n
\t\t\t\n
\t\t\tvar bg_image = $settings.images.clientPath + \'map-opacity.png\';\n
\n
\t\t\ttrans_img.setAttributeNS(ns.xlink, \'xlink:href\', bg_image);\n
\t\t\t\n
\t\t\t$(stopMakerSVG).click(function(evt) {\n
\t\t\t\tstop_offset = stopMakerDiv.offset();\n
\t\t\t\tvar target = evt.target;\n
\t\t\t\tif(target.tagName === \'path\') return;\n
\t\t\t\tvar x = evt.pageX - stop_offset.left - 8;\n
\t\t\t\tx = x < 10 ? 10 : x > MAX + 10 ? MAX + 10: x;\n
\t\t\t\tmkStop(x / MAX, 0, 0, true);\n
\t\t\t\tevt.stopPropagation();\n
\t\t\t});\n
\t\t\t\n
\t\t\t$(stopMakerSVG).mouseover(function() {\n
\t\t\t\tstopMakerSVG.appendChild(delStop);\n
\t\t\t});\n
\t\t\t\n
\t\t\tstopGroup = mkElem(\'g\', {}, stopMakerSVG);\n
\t\t\t\n
\t\t\tmkElem(\'line\', {\n
\t\t\t\tx1: 10,\n
\t\t\t\ty1: 15,\n
\t\t\t\tx2: MAX + 10,\n
\t\t\t\ty2: 15,\n
\t\t\t\t\'stroke-width\': 2,\n
\t\t\t\tstroke: \'#000\'\n
\t\t\t}, stopMakerSVG);\n
\t\t\t\n
\t\t\t\n
\t\t\tvar spreadMethodOpt = gradPicker.find(\'.jGraduate_spreadMethod\').change(function() {\n
\t\t\t\tcurGradient.setAttribute(\'spreadMethod\', $(this).val());\n
\t\t\t});\n
\t\t\t\n
\t\t\n
\t\t\t// handle dragging the stop around the swatch\n
\t\t\tvar draggingCoord = null;\n
\t\t\t\n
\t\t\tvar onCoordDrag = function(evt) {\n
\t\t\t\tvar x = evt.pageX - offset.left;\n
\t\t\t\tvar y = evt.pageY - offset.top;\n
\n
\t\t\t\t// clamp stop to the swatch\n
\t\t\t\tx = x < 0 ? 0 : x > MAX ? MAX : x;\n
\t\t\t\ty = y < 0 ? 0 : y > MAX ? MAX : y;\n
\t\t\t\t\n
\t\t\t\tdraggingCoord.css(\'left\', x).css(\'top\', y);\n
\n
\t\t\t\t// calculate stop offset            \t\t\n
\t\t\t\tvar fracx = x / SIZEX;\n
\t\t\t\tvar fracy = y / SIZEY;\n
\t\t\t\t\n
\t\t\t\tvar type = draggingCoord.data(\'coord\');\n
\t\t\t\tvar grad = curGradient;\n
\t\t\t\t\n
\t\t\t\tswitch ( type ) {\n
\t\t\t\t\tcase \'start\':\n
\t\t\t\t\t\tattr_input.x1.val(fracx);\n
\t\t\t\t\t\tattr_input.y1.val(fracy);\n
\t\t\t\t\t\tgrad.setAttribute(\'x1\', fracx);\n
\t\t\t\t\t\tgrad.setAttribute(\'y1\', fracy);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'end\':\n
\t\t\t\t\t\tattr_input.x2.val(fracx);\n
\t\t\t\t\t\tattr_input.y2.val(fracy);\n
\t\t\t\t\t\tgrad.setAttribute(\'x2\', fracx);\n
\t\t\t\t\t\tgrad.setAttribute(\'y2\', fracy);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'center\':\n
\t\t\t\t\t\tattr_input.cx.val(fracx);\n
\t\t\t\t\t\tattr_input.cy.val(fracy);\n
\t\t\t\t\t\tgrad.setAttribute(\'cx\', fracx);\n
\t\t\t\t\t\tgrad.setAttribute(\'cy\', fracy);\n
\t\t\t\t\t\tc_x = fracx;\n
\t\t\t\t\t\tc_y = fracy;\n
\t\t\t\t\t\txform();\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'focus\':\n
\t\t\t\t\t\tattr_input.fx.val(fracx);\n
\t\t\t\t\t\tattr_input.fy.val(fracy);\n
\t\t\t\t\t\tgrad.setAttribute(\'fx\', fracx);\n
\t\t\t\t\t\tgrad.setAttribute(\'fy\', fracy);\n
\t\t\t\t\t\txform();\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tevt.preventDefault();\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar onCoordUp = function() {\n
\t\t\t\tdraggingCoord = null;\n
\t\t\t\t$win.unbind(\'mousemove\', onCoordDrag).unbind(\'mouseup\', onCoordUp);\n
\t\t\t}\n
\t\t\t\n
\t\t\t// Linear gradient\n
// \t\t\t(function() {\n
\n
\t\t\t\n
\t\t\tstops = curGradient.getElementsByTagNameNS(ns.svg, \'stop\');\n
\n
\t\t\t// if there are not at least two stops, then \n
\t\t\tif (numstops < 2) {\n
\t\t\t\twhile (numstops < 2) {\n
\t\t\t\t\tcurGradient.appendChild( document.createElementNS(ns.svg, \'stop\') );\n
\t\t\t\t\t++numstops;\n
\t\t\t\t}\n
\t\t\t\tstops = curGradient.getElementsByTagNameNS(ns.svg, \'stop\');\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar numstops = stops.length;\t\t\t\t\n
\t\t\tfor(var i = 0; i < numstops; i++) {\n
\t\t\t\tmkStop(0, 0, 0, 0, stops[i]);\n
\t\t\t}\n
\t\t\t\n
\t\t\tspreadMethodOpt.val(curGradient.getAttribute(\'spreadMethod\') || \'pad\');\n
\n
\t\t\tvar offset;\n
\t\t\t\n
\t\t\t// No match, so show focus point\n
\t\t\tvar showFocus = false; \n
\t\t\t\n
\t\t\tpreviewRect.setAttribute(\'fill-opacity\', gradalpha/100);\n
\n
\t\t\t\n
\t\t\t$(\'#\' + id + \' div.grad_coord\').mousedown(function(evt) {\n
\t\t\t\tevt.preventDefault();\n
\t\t\t\tdraggingCoord = $(this);\n
\t\t\t\tvar s_pos = draggingCoord.offset();\n
\t\t\t\toffset = draggingCoord.parent().offset();\n
\t\t\t\t$win.mousemove(onCoordDrag).mouseup(onCoordUp);\n
\t\t\t});\n
\t\t\t\n
\t\t\t// bind GUI elements\n
\t\t\t$(\'#\'+id+\'_jGraduate_Ok\').bind(\'click\', function() {\n
\t\t\t\t$this.paint.type = curType;\n
\t\t\t\t$this.paint[curType] = curGradient.cloneNode(true);;\n
\t\t\t\t$this.paint.solidColor = null;\n
\t\t\t\tokClicked();\n
\t\t\t});\n
\t\t\t$(\'#\'+id+\'_jGraduate_Cancel\').bind(\'click\', function(paint) {\n
\t\t\t\tcancelClicked();\n
\t\t\t});\n
\n
\t\t\tif(curType === \'radialGradient\') {\n
\t\t\t\tif(showFocus) {\n
\t\t\t\t\tfocusCoord.show();\t\t\t\t\n
\t\t\t\t} else {\n
\t\t\t\t\tfocusCoord.hide();\n
\t\t\t\t\tattr_input.fx.val("");\n
\t\t\t\t\tattr_input.fy.val("");\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t$("#" + id + "_jGraduate_match_ctr")[0].checked = !showFocus;\n
\t\t\t\n
\t\t\tvar lastfx, lastfy;\n
\t\t\t\n
\t\t\t$("#" + id + "_jGraduate_match_ctr").change(function() {\n
\t\t\t\tshowFocus = !this.checked;\n
\t\t\t\tfocusCoord.toggle(showFocus);\n
\t\t\t\tattr_input.fx.val(\'\');\n
\t\t\t\tattr_input.fy.val(\'\');\n
\t\t\t\tvar grad = curGradient;\n
\t\t\t\tif(!showFocus) {\n
\t\t\t\t\tlastfx = grad.getAttribute(\'fx\');\n
\t\t\t\t\tlastfy = grad.getAttribute(\'fy\');\n
\t\t\t\t\tgrad.removeAttribute(\'fx\');\n
\t\t\t\t\tgrad.removeAttribute(\'fy\');\n
\t\t\t\t} else {\n
\t\t\t\t\tvar fx = lastfx || .5;\n
\t\t\t\t\tvar fy = lastfy || .5;\n
\t\t\t\t\tgrad.setAttribute(\'fx\', fx);\n
\t\t\t\t\tgrad.setAttribute(\'fy\', fy);\n
\t\t\t\t\tattr_input.fx.val(fx);\n
\t\t\t\t\tattr_input.fy.val(fy);\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\t\n
\t\t\tvar stops = curGradient.getElementsByTagNameNS(ns.svg, \'stop\');\n
\t\t\tvar numstops = stops.length;\n
\t\t\t// if there are not at least two stops, then \n
\t\t\tif (numstops < 2) {\n
\t\t\t\twhile (numstops < 2) {\n
\t\t\t\t\tcurGradient.appendChild( document.createElementNS(ns.svg, \'stop\') );\n
\t\t\t\t\t++numstops;\n
\t\t\t\t}\n
\t\t\t\tstops = curGradient.getElementsByTagNameNS(ns.svg, \'stop\');\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar slider;\n
\t\t\t\n
\t\t\tvar setSlider = function(e) {\n
\t\t\t\tvar offset = slider.offset;\n
\t\t\t\tvar div = slider.parent;\n
\t\t\t\tvar x = (e.pageX - offset.left - parseInt(div.css(\'border-left-width\')));\n
\t\t\t\tif (x > SLIDERW) x = SLIDERW;\n
\t\t\t\tif (x <= 0) x = 0;\n
\t\t\t\tvar posx = x - 5;\n
\t\t\t\tx /= SLIDERW;\n
\t\t\t\t\n
\t\t\t\tswitch ( slider.type ) {\n
\t\t\t\t\tcase \'radius\':\n
\t\t\t\t\t\tx = Math.pow(x * 2, 2.5);\n
\t\t\t\t\t\tif(x > .98 && x < 1.02) x = 1;\n
\t\t\t\t\t\tif (x <= .01) x = .01;\n
\t\t\t\t\t\tcurGradient.setAttribute(\'r\', x);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'opacity\':\n
\t\t\t\t\t\t$this.paint.alpha = parseInt(x*100);\n
\t\t\t\t\t\tpreviewRect.setAttribute(\'fill-opacity\', x);\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'ellip\':\n
\t\t\t\t\t\tscale_x = 1, scale_y = 1;\n
\t\t\t\t\t\tif(x < .5) {\n
\t\t\t\t\t\t\tx /= .5; // 0.001\n
\t\t\t\t\t\t\tscale_x = x <= 0 ? .01 : x;\n
\t\t\t\t\t\t} else if(x > .5) {\n
\t\t\t\t\t\t\tx /= .5; // 2\n
\t\t\t\t\t\t\tx = 2 - x;\n
\t\t\t\t\t\t\tscale_y = x <= 0 ? .01 : x;\n
\t\t\t\t\t\t} \n
\t\t\t\t\t\txform();\n
\t\t\t\t\t\tx -= 1;\n
\t\t\t\t\t\tif(scale_y === x + 1) {\n
\t\t\t\t\t\t\tx = Math.abs(x);\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase \'angle\':\n
\t\t\t\t\t\tx = x - .5;\n
\t\t\t\t\t\tangle = x *= 180;\n
\t\t\t\t\t\txform();\n
\t\t\t\t\t\tx /= 100;\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t\tslider.elem.css({\'margin-left\':posx});\n
\t\t\t\tx = Math.round(x*100);\n
\t\t\t\tslider.input.val(x);\n
\t\t\t};\n
\t\t\t\n
\t\t\tvar ellip_val = 0, angle_val = 0;\n
\t\t\t\n
\t\t\tif(curType === \'radialGradient\') {\n
\t\t\t\tvar tlist = curGradient.gradientTransform.baseVal;\n
\t\t\t\tif(tlist.numberOfItems === 2) {\n
\t\t\t\t\tvar t = tlist.getItem(0);\n
\t\t\t\t\tvar s = tlist.getItem(1);\n
\t\t\t\t\tif(t.type === 2 && s.type === 3) {\n
\t\t\t\t\t\tvar m = s.matrix;\n
\t\t\t\t\t\tif(m.a !== 1) {\n
\t\t\t\t\t\t\tellip_val = Math.round(-(1 - m.a) * 100);\t\n
\t\t\t\t\t\t} else if(m.d !== 1) {\n
\t\t\t\t\t\t\tellip_val = Math.round((1 - m.d) * 100);\n
\t\t\t\t\t\t} \n
\t\t\t\t\t}\n
\t\t\t\t} else if(tlist.numberOfItems === 3) {\n
\t\t\t\t\t// Assume [R][T][S]\n
\t\t\t\t\tvar r = tlist.getItem(0);\n
\t\t\t\t\tvar t = tlist.getItem(1);\n
\t\t\t\t\tvar s = tlist.getItem(2);\n
\t\t\t\t\t\n
\t\t\t\t\tif(r.type === 4 \n
\t\t\t\t\t\t&& t.type === 2 \n
\t\t\t\t\t\t&& s.type === 3) {\n
\n
\t\t\t\t\t\tangle_val = Math.round(r.angle);\n
\t\t\t\t\t\tvar m = s.matrix;\n
\t\t\t\t\t\tif(m.a !== 1) {\n
\t\t\t\t\t\t\tellip_val = Math.round(-(1 - m.a) * 100);\t\n
\t\t\t\t\t\t} else if(m.d !== 1) {\n
\t\t\t\t\t\t\tellip_val = Math.round((1 - m.d) * 100);\n
\t\t\t\t\t\t} \n
\t\t\t\t\t\t\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tvar sliders = {\n
\t\t\t\tradius: {\n
\t\t\t\t\thandle: \'#\' + id + \'_jGraduate_RadiusArrows\',\n
\t\t\t\t\tinput: \'#\' + id + \'_jGraduate_RadiusInput\',\n
\t\t\t\t\tval: (curGradient.getAttribute(\'r\') || .5) * 100\n
\t\t\t\t},\n
\t\t\t\topacity: {\n
\t\t\t\t\thandle: \'#\' + id + \'_jGraduate_OpacArrows\',\n
\t\t\t\t\tinput: \'#\' + id + \'_jGraduate_OpacInput\',\n
\t\t\t\t\tval: $this.paint.alpha || 100\n
\t\t\t\t},\n
\t\t\t\tellip: {\n
\t\t\t\t\thandle: \'#\' + id + \'_jGraduate_EllipArrows\',\n
\t\t\t\t\tinput: \'#\' + id + \'_jGraduate_EllipInput\',\n
\t\t\t\t\tval: ellip_val\n
\t\t\t\t},\n
\t\t\t\tangle: {\n
\t\t\t\t\thandle: \'#\' + id + \'_jGraduate_AngleArrows\',\n
\t\t\t\t\tinput: \'#\' + id + \'_jGraduate_AngleInput\',\n
\t\t\t\t\tval: angle_val\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\t$.each(sliders, function(type, data) {\n
\t\t\t\tvar handle = $(data.handle);\n
\t\t\t\thandle.mousedown(function(evt) {\n
\t\t\t\t\tvar parent = handle.parent();\n
\t\t\t\t\tslider = {\n
\t\t\t\t\t\ttype: type,\n
\t\t\t\t\t\telem: handle,\n
\t\t\t\t\t\tinput: $(data.input),\n
\t\t\t\t\t\tparent: parent,\n
\t\t\t\t\t\toffset: parent.offset()\n
\t\t\t\t\t};\n
\t\t\t\t\t$win.mousemove(dragSlider).mouseup(stopSlider);\n
\t\t\t\t\tevt.preventDefault();\n
\t\t\t\t});\n
\t\t\t\t\n
\t\t\t\t$(data.input).val(data.val).change(function() {\n
\t\t\t\t\tvar val = +this.value;\n
\t\t\t\t\tvar xpos = 0;\n
\t\t\t\t\tvar isRad = curType === \'radialGradient\';\n
\t\t\t\t\tswitch ( type ) {\n
\t\t\t\t\t\tcase \'radius\':\n
\t\t\t\t\t\t\tif(isRad) curGradient.setAttribute(\'r\', val / 100);\n
\t\t\t\t\t\t\txpos = (Math.pow(val / 100, 1 / 2.5) / 2) * SLIDERW;\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tcase \'opacity\':\n
\t\t\t\t\t\t\t$this.paint.alpha = val;\n
\t\t\t\t\t\t\tpreviewRect.setAttribute(\'fill-opacity\', val / 100);\n
\t\t\t\t\t\t\txpos = val * (SLIDERW / 100);\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\t\n
\t\t\t\t\t\tcase \'ellip\':\n
\t\t\t\t\t\t\tscale_x = scale_y = 1;\n
\t\t\t\t\t\t\tif(val === 0) {\n
\t\t\t\t\t\t\t\txpos = SLIDERW * .5;\n
\t\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tif(val > 99.5) val = 99.5;\n
\t\t\t\t\t\t\tif(val > 0) {\n
\t\t\t\t\t\t\t\tscale_y = 1 - (val / 100);\n
\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\tscale_x = - (val / 100) - 1;\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\txpos = SLIDERW * ((val + 100) / 2) / 100;\n
\t\t\t\t\t\t\tif(isRad) xform();\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tcase \'angle\':\n
\t\t\t\t\t\t\tangle = val;\n
\t\t\t\t\t\t\txpos = angle / 180;\n
\t\t\t\t\t\t\txpos += .5;\n
\t\t\t\t\t\t\txpos *= SLIDERW;\n
\t\t\t\t\t\t\tif(isRad) xform();\n
\t\t\t\t\t}\n
\t\t\t\t\tif(xpos > SLIDERW) {\n
\t\t\t\t\t\txpos = SLIDERW;\n
\t\t\t\t\t} else if(xpos < 0) {\n
\t\t\t\t\t\txpos = 0;\n
\t\t\t\t\t}\n
\t\t\t\t\thandle.css({\'margin-left\': xpos - 5});\n
\t\t\t\t}).change();\n
\t\t\t});\n
\t\t\t\n
\t\t\tvar dragSlider = function(evt) {\n
\t\t\t\tsetSlider(evt);\n
\t\t\t\tevt.preventDefault();\n
\t\t\t};\n
\t\t\t\n
\t\t\tvar stopSlider = function(evt) {\n
\t\t\t\t$win.unbind(\'mousemove\', dragSlider).unbind(\'mouseup\', stopSlider);\n
\t\t\t\tslider = null;\n
\t\t\t};\n
\t\t\t\n
\t\t\t\n
\t\t\t// --------------\n
\t\t\tvar thisAlpha = ($this.paint.alpha*255/100).toString(16);\n
\t\t\twhile (thisAlpha.length < 2) { thisAlpha = "0" + thisAlpha; }\n
\t\t\tthisAlpha = thisAlpha.split(".")[0];\n
\t\t\tcolor = $this.paint.solidColor == "none" ? "" : $this.paint.solidColor + thisAlpha;\n
\t\t\t\n
\t\t\tif(!isSolid) {\n
\t\t\t\tcolor = stops[0].getAttribute(\'stop-color\');\n
\t\t\t}\n
\t\t\t\n
\t\t\t// This should be done somewhere else, probably\n
\t\t\t$.extend($.fn.jPicker.defaults.window, {\n
\t\t\t\talphaSupport: true, effects: {type: \'show\',speed: 0}\n
\t\t\t});\n
\t\t\t\n
\t\t\tcolPicker.jPicker(\n
\t\t\t\t{\n
\t\t\t\t\twindow: { title: $settings.window.pickerTitle },\n
\t\t\t\t\timages: { clientPath: $settings.images.clientPath },\n
\t\t\t\t\tcolor: { active: color, alphaSupport: true }\n
\t\t\t\t},\n
\t\t\t\tfunction(color) {\n
\t\t\t\t\t$this.paint.type = "solidColor";\n
\t\t\t\t\t$this.paint.alpha = color.val(\'ahex\') ? Math.round((color.val(\'a\') / 255) * 100) : 100;\n
\t\t\t\t\t$this.paint.solidColor = color.val(\'hex\') ? color.val(\'hex\') : "none";\n
\t\t\t\t\t$this.paint.radialGradient = null;\n
\t\t\t\t\tokClicked(); \n
\t\t\t\t},\n
\t\t\t\tnull,\n
\t\t\t\tfunction(){ cancelClicked(); }\n
\t\t\t\t);\n
\n
\t\t\t\n
\t\t\tvar tabs = $(idref + \' .jGraduate_tabs li\');\n
\t\t\ttabs.click(function() {\n
\t\t\t\ttabs.removeClass(\'jGraduate_tab_current\');\n
\t\t\t\t$(this).addClass(\'jGraduate_tab_current\');\n
\t\t\t\t$(idref + " > div").hide();\n
\t\t\t\tvar type = $(this).attr(\'data-type\');\n
\t\t\t\tvar container = $(idref + \' .jGraduate_gradPick\').show();\n
\t\t\t\tif(type === \'rg\' || type === \'lg\') {\n
\t\t\t\t\t// Show/hide appropriate fields\n
\t\t\t\t\t$(\'.jGraduate_\' + type + \'_field\').show();\n
\t\t\t\t\t$(\'.jGraduate_\' + (type === \'lg\' ? \'rg\' : \'lg\') + \'_field\').hide();\n
\t\t\t\t\t\n
\t\t\t\t\t$(\'#\' + id + \'_jgraduate_rect\')[0].setAttribute(\'fill\', \'url(#\' + id + \'_\' + type + \'_jgraduate_grad)\');\n
\t\t\t\t\t\n
\t\t\t\t\t// Copy stops\n
\t\t\t\t\t\n
\t\t\t\t\tcurType = type === \'lg\' ? \'linearGradient\' : \'radialGradient\';\n
\t\t\t\t\t\n
\t\t\t\t\t$(\'#\' + id + \'_jGraduate_OpacInput\').val($this.paint.alpha).change();\n
\t\t\t\t\t\n
\t\t\t\t\tvar newGrad = $(\'#\' + id + \'_\' + type + \'_jgraduate_grad\')[0];\n
\t\t\t\t\t\n
\t\t\t\t\tif(curGradient !== newGrad) {\n
\t\t\t\t\t\tvar cur_stops = $(curGradient).find(\'stop\');\t\n
\t\t\t\t\t\t$(newGrad).empty().append(cur_stops);\n
\t\t\t\t\t\tcurGradient = newGrad;\n
\t\t\t\t\t\tvar sm = spreadMethodOpt.val();\n
\t\t\t\t\t\tcurGradient.setAttribute(\'spreadMethod\', sm);\n
\t\t\t\t\t}\n
\t\t\t\t\tshowFocus = type === \'rg\' && curGradient.getAttribute(\'fx\') != null && !(cx == fx && cy == fy);\n
\t\t\t\t\t$(\'#\' + id + \'_jGraduate_focusCoord\').toggle(showFocus);\n
\t\t\t\t\tif(showFocus) {\n
\t\t\t\t\t\t$(\'#\' + id + \'_jGraduate_match_ctr\')[0].checked = false;\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\t$(idref + \' .jGraduate_gradPick\').hide();\n
\t\t\t\t\t$(idref + \' .jGraduate_colPick\').show();\n
\t\t\t\t}\n
\t\t\t});\n
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
\t\t\t$this.show();\n
\t\t\t\n
\t\t\t// jPicker will try to show after a 0ms timeout, so need to fire this after that\n
\t\t\tsetTimeout(function() {\n
\t\t\t\ttab.addClass(\'jGraduate_tab_current\').click();\t\n
\t\t\t}, 10);\n
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
            <value> <int>37170</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
