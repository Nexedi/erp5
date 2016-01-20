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
            <value> <string>ts52850649.25</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-arrows.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * ext-arrows.js\n
 *\n
 * Licensed under the Apache License, Version 2\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
\n
 \n
methodDraw.addExtension("Arrows", function(S) {\n
    var svgcontent = S.svgcontent,\n
      addElem = S.addSvgElementFromJson,\n
      nonce = S.nonce,\n
      randomize_ids = S.randomize_ids,\n
      selElems;\n
\n
    svgCanvas.bind(\'setnonce\', setArrowNonce);\n
    svgCanvas.bind(\'unsetnonce\', unsetArrowNonce);\n
      \n
    var lang_list = {\n
      "en":[\n
        {"id": "arrow_none", "textContent": "No arrow" }\n
      ],\n
      "fr":[\n
        {"id": "arrow_none", "textContent": "Sans flèche" }\n
      ]\n
    };\n
    \n
    var prefix = \'se_arrow_\';\n
    if (randomize_ids) {\n
      var arrowprefix = prefix + nonce + \'_\';\n
    } else {\n
      var arrowprefix = prefix;\n
    }\n
\n
    var pathdata = {\n
      fw: {d:"m0,0l10,5l-10,5l5,-5l-5,-5z", refx:8,  id: arrowprefix + \'fw\'},\n
      bk: {d:"m10,0l-10,5l10,5l-5,-5l5,-5z", refx:2, id: arrowprefix + \'bk\'}\n
    }\n
    \n
    function setArrowNonce(window, n) {\n
        randomize_ids = true;\n
        arrowprefix = prefix + n + \'_\';\n
      pathdata.fw.id = arrowprefix + \'fw\';\n
      pathdata.bk.id = arrowprefix + \'bk\';\n
    }\n
\n
    function unsetArrowNonce(window) {\n
        randomize_ids = false;\n
        arrowprefix = prefix;\n
      pathdata.fw.id = arrowprefix + \'fw\';\n
      pathdata.bk.id = arrowprefix + \'bk\';\n
    }\n
\n
    function getLinked(elem, attr) {\n
      var str = elem.getAttribute(attr);\n
      if(!str) return null;\n
      var m = str.match(/\\(\\#(.*)\\)/);\n
      if(!m || m.length !== 2) {\n
        return null;\n
      }\n
      return S.getElem(m[1]);\n
    }\n
    \n
    function showPanel(on) {\n
      $(\'#arrow_panel\').toggle(on);\n
      \n
      if(on) {\n
        var el = selElems[0];\n
        var end = el.getAttribute("marker-end");\n
        var start = el.getAttribute("marker-start");\n
        var mid = el.getAttribute("marker-mid");\n
        var val;\n
        \n
        if(end && start) {\n
          val = "both";\n
        } else if(end) {\n
          val = "end";\n
        } else if(start) {\n
          val = "start";\n
        } else if(mid) {\n
          val = "mid";\n
          if(mid.indexOf("bk") != -1) {\n
            val = "mid_bk";\n
          }\n
        }\n
        \n
        if(!start && !mid && !end) {\n
          val = "none";\n
        }\n
        \n
        $("#arrow_list").val(val);\n
      }\n
    }\n
    \n
    function resetMarker() {\n
      var el = selElems[0];\n
      el.removeAttribute("marker-start");\n
      el.removeAttribute("marker-mid");\n
      el.removeAttribute("marker-end");\n
    }\n
    \n
    function addMarker(dir, type, id) {\n
      // TODO: Make marker (or use?) per arrow type, since refX can be different\n
      id = id || arrowprefix + dir;\n
      \n
      var marker = S.getElem(id);\n
\n
      var data = pathdata[dir];\n
      \n
      if(type == "mid") {\n
        data.refx = 5;\n
      }\n
\n
      if(!marker) {\n
        marker = addElem({\n
          "element": "marker",\n
          "attr": {\n
            "viewBox": "0 0 10 10",\n
            "id": id,\n
            "refY": 5,\n
            "markerUnits": "strokeWidth",\n
            "markerWidth": 5,\n
            "markerHeight": 5,\n
            "orient": "auto",\n
            "style": "pointer-events:none" // Currently needed for Opera\n
          }\n
        });\n
        var arrow = addElem({\n
          "element": "path",\n
          "attr": {\n
            "d": data.d,\n
            "fill": "#000000"\n
          }\n
        });\n
        marker.appendChild(arrow);\n
        S.findDefs().appendChild(marker);\n
      } \n
      \n
      marker.setAttribute(\'refX\', data.refx);\n
      \n
      return marker;\n
    }\n
    \n
    function setArrow() {\n
      var type = this.value;\n
      resetMarker();\n
    \n
      if(type == "none") {\n
        return;\n
      }\n
    \n
      // Set marker on element\n
      var dir = "fw";\n
      if(type == "mid_bk") {\n
        type = "mid";\n
        dir = "bk";\n
      } else if(type == "both") {\n
        addMarker("bk", type);\n
        svgCanvas.changeSelectedAttribute("marker-start", "url(#" + pathdata.bk.id + ")");\n
        type = "end";\n
        dir = "fw";\n
      } else if (type == "start") {\n
        dir = "bk";\n
      }\n
      \n
      addMarker(dir, type);\n
      svgCanvas.changeSelectedAttribute("marker-"+type, "url(#" + pathdata[dir].id + ")");\n
      S.call("changed", selElems);\n
    }\n
    \n
    function colorChanged(elem) {\n
      var color = elem.getAttribute(\'stroke\');\n
      \n
      var mtypes = [\'start\',\'mid\',\'end\'];\n
      var defs = S.findDefs();\n
      \n
      $.each(mtypes, function(i, type) {\n
        var marker = getLinked(elem, \'marker-\'+type);\n
        if(!marker) return;\n
        \n
        var cur_color = $(marker).children().attr(\'fill\');\n
        var cur_d = $(marker).children().attr(\'d\');\n
        var new_marker = null;\n
        if(cur_color === color) return;\n
        \n
        var all_markers = $(defs).find(\'marker\');\n
        // Different color, check if already made\n
        all_markers.each(function() {\n
          var attrs = $(this).children().attr([\'fill\', \'d\']);\n
          if(attrs.fill === color && attrs.d === cur_d) {\n
            // Found another marker with this color and this path\n
            new_marker = this;\n
          }\n
        });\n
        \n
        if(!new_marker) {\n
          // Create a new marker with this color\n
          var last_id = marker.id;\n
          var dir = last_id.indexOf(\'_fw\') !== -1?\'fw\':\'bk\';\n
          \n
          new_marker = addMarker(dir, type, arrowprefix + dir + all_markers.length);\n
\n
          $(new_marker).children().attr(\'fill\', color);\n
        }\n
        \n
        $(elem).attr(\'marker-\'+type, "url(#" + new_marker.id + ")");\n
        \n
        // Check if last marker can be removed\n
        var remove = true;\n
        $(S.svgcontent).find(\'line, polyline, path, polygon\').each(function() {\n
          var elem = this;\n
          $.each(mtypes, function(j, mtype) {\n
            if($(elem).attr(\'marker-\' + mtype) === "url(#" + marker.id + ")") {\n
              return remove = false;\n
            }\n
          });\n
          if(!remove) return false;\n
        });\n
        \n
        // Not found, so can safely remove\n
        if(remove) {\n
          $(marker).remove();\n
        }\n
\n
      });\n
      \n
    }\n
    \n
    return {\n
      name: "Arrows",\n
      context_tools: [{\n
        type: "select",\n
        panel: "arrow_panel",\n
        title: "Select arrow type",\n
        id: "arrow_list",\n
        options: {\n
          none: "No arrow",\n
          end: "----&gt;",\n
          start: "&lt;----",\n
          both: "&lt;---&gt;",\n
          mid: "--&gt;--",\n
          mid_bk: "--&lt;--"\n
        },\n
        defval: "none",\n
        events: {\n
          change: setArrow\n
        }\n
      }],\n
      callback: function() {\n
        $(\'#arrow_panel\').hide();\n
        // Set ID so it can be translated in locale file\n
        $(\'#arrow_list option\')[0].id = \'connector_no_arrow\';\n
      },\n
      addLangData: function(lang) {\n
        return {\n
          data: lang_list[lang]\n
        };\n
      },\n
      selectedChanged: function(opts) {\n
        \n
        // Use this to update the current selected elements\n
        selElems = opts.elems;\n
        \n
        var i = selElems.length;\n
        var marker_elems = [\'line\',\'path\',\'polyline\',\'polygon\'];\n
        \n
        while(i--) {\n
          var elem = selElems[i];\n
          if(elem && $.inArray(elem.tagName, marker_elems) != -1) {\n
            if(opts.selectedElement && !opts.multiselected) {\n
              showPanel(true);\n
            } else {\n
              showPanel(false);\n
            }\n
          } else {\n
            showPanel(false);\n
          }\n
        }\n
      },\n
      elementChanged: function(opts) {\n
        var elem = opts.elems[0];\n
        if(elem && (\n
          elem.getAttribute("marker-start") ||\n
          elem.getAttribute("marker-mid") ||\n
          elem.getAttribute("marker-end")\n
        )) {\n
  //                var start = elem.getAttribute("marker-start");\n
  //                var mid = elem.getAttribute("marker-mid");\n
  //                var end = elem.getAttribute("marker-end");\n
          // Has marker, so see if it should match color\n
          colorChanged(elem);\n
        }\n
        \n
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
            <value> <int>8060</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
