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
            <value> <string>anonymous_http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts52850614.83</string> </value>
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

/*\n
 * ext-eyedropper.js\n
 *\n
 * Licensed under the Apache License, Version 2\n
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
methodDraw.addExtension("eyedropper", function(S) {\n
    var svgcontent = S.svgcontent,\n
      svgns = "http://www.w3.org/2000/svg",\n
      svgdoc = S.svgroot.parentNode.ownerDocument,\n
      svgCanvas = methodDraw.canvas,\n
      ChangeElementCommand = svgedit.history.ChangeElementCommand,\n
      addToHistory = function(cmd) { svgCanvas.undoMgr.addCommandToHistory(cmd); },\n
      currentStyle = {fillPaint: "red", fillOpacity: 1.0,\n
              strokePaint: "black", strokeOpacity: 1.0, \n
              strokeWidth: 5, strokeDashArray: null,\n
              opacity: 1.0,\n
              strokeLinecap: \'butt\',\n
              strokeLinejoin: \'miter\'\n
              };\n
    function getStyle(opts) {\n
      // if we are in eyedropper mode, we don\'t want to disable the eye-dropper tool\n
      var mode = svgCanvas.getMode();\n
      if (mode == "eyedropper") return;\n
      var tool = $(\'#tool_eyedropper\');\n
\n
    }\n
    \n
    var getPaint = function(color, opac, type) {\n
      // update the editor\'s fill paint\n
      var opts = null;\n
      if (color.indexOf("url(#") === 0) {\n
        var refElem = svgCanvas.getRefElem(color);\n
        if(refElem) {\n
          refElem = refElem.cloneNode(true);\n
        } else {\n
          refElem =  $("#" + type + "_color defs *")[0];\n
        }\n
\n
        opts = { alpha: opac };\n
        opts[refElem.tagName] = refElem;\n
      } \n
      else if (color.indexOf("#") === 0) {\n
        opts = {\n
          alpha: opac,\n
          solidColor: color.substr(1)\n
        };\n
      }\n
      else {\n
        opts = {\n
          alpha: opac,\n
          solidColor: \'none\'\n
        };\n
      }\n
      return new $.jGraduate.Paint(opts);\n
    };\n
    \n
    return {\n
      name: "eyedropper",\n
      svgicons: "extensions/eyedropper-icon.xml",\n
      buttons: [{\n
        id: "tool_eyedropper",\n
        type: "mode",\n
        title: "Eye Dropper Tool",\n
        position: 8,\n
        key: "I",\n
        icon: "extensions/eyedropper.png",\n
        events: {\n
          "click": function() {\n
            svgCanvas.setMode("eyedropper");\n
          }\n
        }\n
      }],\n
      \n
      mouseDown: function(opts) {\n
        var mode = svgCanvas.getMode();\n
        var e = opts.event;\n
        var target = (e.target.id === "svgroot") ? document.getElementById(\'canvas_background\') : e.target;\n
        if (mode == "eyedropper" && target) {\n
          currentStyle.fillPaint = target.getAttribute("fill") || "white";\n
          currentStyle.fillOpacity = target.getAttribute("fill-opacity") || 1.0;\n
          currentStyle.strokePaint = target.getAttribute("stroke") || \'none\';\n
          currentStyle.strokeOpacity = target.getAttribute("stroke-opacity") || 1.0;\n
          currentStyle.strokeWidth = target.getAttribute("stroke-width");\n
          currentStyle.strokeDashArray = target.getAttribute("stroke-dasharray");\n
          currentStyle.strokeLinecap = target.getAttribute("stroke-linecap");\n
          currentStyle.strokeLinejoin = target.getAttribute("stroke-linejoin");\n
          currentStyle.opacity = target.getAttribute("opacity") || 1.0;\n
          opts.selectedElements = opts.selectedElements.filter(Boolean)\n
          if (!opts.selectedElements.length) { //nothing selected, just update colors\n
            var fill = getPaint(currentStyle.fillPaint, currentStyle.fillOpacity*100, "fill");\n
            var stroke = getPaint(currentStyle.strokePaint, currentStyle.strokeOpacity*100, "stroke");\n
            methodDraw.paintBox.fill.setPaint(fill)\n
            methodDraw.paintBox.stroke.setPaint(stroke)\n
            return;\n
          }\n
          if ($.inArray(opts.selectedElements.nodeName, [\'g\', \'use\']) == -1) {\n
            var changes = {};\n
            var change = function(elem, attrname, newvalue) {\n
              changes[attrname] = elem.getAttribute(attrname);\n
              elem.setAttribute(attrname, newvalue);\n
            };\n
            var batchCmd = new S.BatchCommand();\n
            opts.selectedElements.forEach(function(element){\n
              if (currentStyle.fillPaint)       change(element, "fill", currentStyle.fillPaint);\n
              if (currentStyle.fillOpacity)     change(element, "fill-opacity", currentStyle.fillOpacity);\n
              if (currentStyle.strokePaint)     change(element, "stroke", currentStyle.strokePaint);\n
              if (currentStyle.strokeOpacity)   change(element, "stroke-opacity", currentStyle.strokeOpacity);\n
              if (currentStyle.strokeWidth)     change(element, "stroke-width", currentStyle.strokeWidth);\n
              if (currentStyle.strokeDashArray) change(element, "stroke-dasharray", currentStyle.strokeDashArray);\n
              if (currentStyle.opacity)         change(element, "opacity", currentStyle.opacity);\n
              if (currentStyle.strokeLinecap)   change(element, "stroke-linecap", currentStyle.strokeLinecap);\n
              if (currentStyle.strokeLinejoin)  change(element, "stroke-linejoin", currentStyle.strokeLinejoin);\n
              batchCmd.addSubCommand(new ChangeElementCommand(element, changes));\n
              changes = {};\n
            });\n
            var fill = getPaint(currentStyle.fillPaint, currentStyle.fillOpacity*100, "fill")\n
            var stroke = getPaint(currentStyle.strokePaint, currentStyle.strokeOpacity*100, "stroke")\n
            methodDraw.paintBox.fill.update(true)\n
            methodDraw.paintBox.stroke.update(true)\n
            addToHistory(batchCmd);\n
          }\n
        }\n
      }\n
    };\n
});

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>5585</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
