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
            <value> <string>ts32626248.09</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>export_renderers.js</string> </value>
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
    return $.pivotUtilities.export_renderers = {\n
      "TSV Export": function(pivotData, opts) {\n
        var agg, colAttrs, colKey, colKeys, defaults, i, j, k, l, len, len1, len2, len3, len4, len5, m, n, r, result, row, rowAttr, rowAttrs, rowKey, rowKeys, text;\n
        defaults = {\n
          localeStrings: {}\n
        };\n
        opts = $.extend(defaults, opts);\n
        rowKeys = pivotData.getRowKeys();\n
        if (rowKeys.length === 0) {\n
          rowKeys.push([]);\n
        }\n
        colKeys = pivotData.getColKeys();\n
        if (colKeys.length === 0) {\n
          colKeys.push([]);\n
        }\n
        rowAttrs = pivotData.rowAttrs;\n
        colAttrs = pivotData.colAttrs;\n
        result = [];\n
        row = [];\n
        for (i = 0, len = rowAttrs.length; i < len; i++) {\n
          rowAttr = rowAttrs[i];\n
          row.push(rowAttr);\n
        }\n
        if (colKeys.length === 1 && colKeys[0].length === 0) {\n
          row.push(pivotData.aggregatorName);\n
        } else {\n
          for (j = 0, len1 = colKeys.length; j < len1; j++) {\n
            colKey = colKeys[j];\n
            row.push(colKey.join("-"));\n
          }\n
        }\n
        result.push(row);\n
        for (k = 0, len2 = rowKeys.length; k < len2; k++) {\n
          rowKey = rowKeys[k];\n
          row = [];\n
          for (l = 0, len3 = rowKey.length; l < len3; l++) {\n
            r = rowKey[l];\n
            row.push(r);\n
          }\n
          for (m = 0, len4 = colKeys.length; m < len4; m++) {\n
            colKey = colKeys[m];\n
            agg = pivotData.getAggregator(rowKey, colKey);\n
            if (agg.value() != null) {\n
              row.push(agg.value());\n
            } else {\n
              row.push("");\n
            }\n
          }\n
          result.push(row);\n
        }\n
        text = "";\n
        for (n = 0, len5 = result.length; n < len5; n++) {\n
          r = result[n];\n
          text += r.join("\\t") + "\\n";\n
        }\n
        return $("<textarea>").text(text).css({\n
          width: ($(window).width() / 2) + "px",\n
          height: ($(window).height() / 2) + "px"\n
        });\n
      }\n
    };\n
  });\n
\n
}).call(this);\n
\n
//# sourceMappingURL=export_renderers.js.map

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2515</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
