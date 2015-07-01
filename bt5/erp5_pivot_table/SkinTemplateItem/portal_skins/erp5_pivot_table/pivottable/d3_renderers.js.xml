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
            <value> <string>ts32626250.2</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>d3_renderers.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

(function() {\n
  var callWithJQuery;\n
\n
  callWithJQuery = function(pivotModule) {\n
    if (typeof exports === "object" && typeof module === "object") {\n
      return pivotModule(require("jquery"));\n
    } else if (typeof define === "function" && define.amd) {\n
      return define(["jquery"], pivotModule);\n
    } else {\n
      return pivotModule(jQuery);\n
    }\n
  };\n
\n
  callWithJQuery(function($) {\n
    return $.pivotUtilities.d3_renderers = {\n
      Treemap: function(pivotData, opts) {\n
        var addToTree, color, defaults, height, i, len, ref, result, rowKey, tree, treemap, value, width;\n
        defaults = {\n
          localeStrings: {},\n
          d3: {\n
            width: function() {\n
              return $(window).width() / 1.4;\n
            },\n
            height: function() {\n
              return $(window).height() / 1.4;\n
            }\n
          }\n
        };\n
        opts = $.extend(defaults, opts);\n
        result = $("<div>").css({\n
          width: "100%",\n
          height: "100%"\n
        });\n
        tree = {\n
          name: "All",\n
          children: []\n
        };\n
        addToTree = function(tree, path, value) {\n
          var child, i, len, newChild, ref, x;\n
          if (path.length === 0) {\n
            tree.value = value;\n
            return;\n
          }\n
          if (tree.children == null) {\n
            tree.children = [];\n
          }\n
          x = path.shift();\n
          ref = tree.children;\n
          for (i = 0, len = ref.length; i < len; i++) {\n
            child = ref[i];\n
            if (!(child.name === x)) {\n
              continue;\n
            }\n
            addToTree(child, path, value);\n
            return;\n
          }\n
          newChild = {\n
            name: x\n
          };\n
          addToTree(newChild, path, value);\n
          return tree.children.push(newChild);\n
        };\n
        ref = pivotData.getRowKeys();\n
        for (i = 0, len = ref.length; i < len; i++) {\n
          rowKey = ref[i];\n
          value = pivotData.getAggregator(rowKey, []).value();\n
          if (value != null) {\n
            addToTree(tree, rowKey, value);\n
          }\n
        }\n
        color = d3.scale.category10();\n
        width = opts.d3.width();\n
        height = opts.d3.height();\n
        treemap = d3.layout.treemap().size([width, height]).sticky(true).value(function(d) {\n
          return d.size;\n
        });\n
        d3.select(result[0]).append("div").style("position", "relative").style("width", width + "px").style("height", height + "px").datum(tree).selectAll(".node").data(treemap.padding([15, 0, 0, 0]).value(function(d) {\n
          return d.value;\n
        }).nodes).enter().append("div").attr("class", "node").style("background", function(d) {\n
          if (d.children != null) {\n
            return "lightgrey";\n
          } else {\n
            return color(d.name);\n
          }\n
        }).text(function(d) {\n
          return d.name;\n
        }).call(function() {\n
          this.style("left", function(d) {\n
            return d.x + "px";\n
          }).style("top", function(d) {\n
            return d.y + "px";\n
          }).style("width", function(d) {\n
            return Math.max(0, d.dx - 1) + "px";\n
          }).style("height", function(d) {\n
            return Math.max(0, d.dy - 1) + "px";\n
          });\n
        });\n
        return result;\n
      }\n
    };\n
  });\n
\n
}).call(this);\n
\n
//# sourceMappingURL=d3_renderers.js.map

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3334</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
