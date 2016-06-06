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
            <value> <string>ts32626247.13</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>pivot.tr.js</string> </value>
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
    var c3r, d3r, frFmt, frFmtInt, frFmtPct, gcr, nf, r, tpl;\n
    nf = $.pivotUtilities.numberFormat;\n
    tpl = $.pivotUtilities.aggregatorTemplates;\n
    r = $.pivotUtilities.renderers;\n
    gcr = $.pivotUtilities.gchart_renderers;\n
    d3r = $.pivotUtilities.d3_renderers;\n
    c3r = $.pivotUtilities.c3_renderers;\n
    frFmt = nf({\n
      thousandsSep: ".",\n
      decimalSep: ","\n
    });\n
    frFmtInt = nf({\n
      digitsAfterDecimal: 0,\n
      thousandsSep: ".",\n
      decimalSep: ","\n
    });\n
    frFmtPct = nf({\n
      digitsAfterDecimal: 2,\n
      scaler: 100,\n
      suffix: "%",\n
      thousandsSep: ".",\n
      decimalSep: ","\n
    });\n
    $.pivotUtilities.locales.tr = {\n
      localeStrings: {\n
        renderError: "PivotTable sonu&ccedil;lar&#305;n&#305; olu&#351;tuturken hata olu&#351;tu",\n
        computeError: "PivotTable sonu&ccedil;lar&#305;n&#305; i&#351;lerken hata olu&#351;tu",\n
        uiRenderError: "PivotTable UI sonu&ccedil;lar&#305;n&#305; olu&#351;tuturken hata olu&#351;tu",\n
        selectAll: "T&uuml;m&uuml;n&uuml; Se&ccedil;",\n
        selectNone: "T&uuml;m&uuml;n&uuml; B&#305;rak",\n
        tooMany: "(listelemek i&ccedil;in fazla)",\n
        filterResults: "Sonu&ccedil;lar&#305; filtrele",\n
        totals: "Toplam",\n
        vs: "vs",\n
        by: "ile"\n
      },\n
      aggregators: {\n
        "Say&#305;": tpl.count(frFmtInt),\n
        "Benzersiz de&#287;erler say&#305;s&#305;": tpl.countUnique(frFmtInt),\n
        "Benzersiz de&#287;erler listesi": tpl.listUnique(", "),\n
        "Toplam": tpl.sum(frFmt),\n
        "Toplam (tam say&#305;)": tpl.sum(frFmtInt),\n
        "Ortalama": tpl.average(frFmt),\n
        "Min": tpl.min(frFmt),\n
        "Maks": tpl.max(frFmt),\n
        "Miktarlar&#305;n toplam&#305;": tpl.sumOverSum(frFmt),\n
        "%80 daha y&uuml;ksek": tpl.sumOverSumBound80(true, frFmt),\n
        "%80 daha d&uuml;&#351;&uuml;k": tpl.sumOverSumBound80(false, frFmt),\n
        "Toplam oran&#305; (toplam)": tpl.fractionOf(tpl.sum(), "total", frFmtPct),\n
        "Sat&#305;r oran&#305; (toplam)": tpl.fractionOf(tpl.sum(), "row", frFmtPct),\n
        "S&uuml;tunun oran&#305; (toplam)": tpl.fractionOf(tpl.sum(), "col", frFmtPct),\n
        "Toplam oran&#305; (say&#305;)": tpl.fractionOf(tpl.count(), "total", frFmtPct),\n
        "Sat&#305;r oran&#305; (say&#305;)": tpl.fractionOf(tpl.count(), "row", frFmtPct),\n
        "S&uuml;tunun oran&#305; (say&#305;)": tpl.fractionOf(tpl.count(), "col", frFmtPct)\n
      },\n
      renderers: {\n
        "Tablo": r["Table"],\n
        "Tablo (&Ccedil;ubuklar)": r["Table Barchart"],\n
        "&#304;lgi haritas&#305;": r["Heatmap"],\n
        "Sat&#305;r ilgi haritas&#305;": r["Row Heatmap"],\n
        "S&uuml;tun ilgi haritas&#305;": r["Col Heatmap"]\n
      }\n
    };\n
    if (gcr) {\n
      $.pivotUtilities.locales.tr.gchart_renderers = {\n
        "&Ccedil;izgi Grafi&#287;i (gchart)": gcr["Line Chart"],\n
        "Bar Grafi&#287;i (gchart)": gcr["Bar Chart"],\n
        "Y&#305;&#287;&#305;lm&#305;&#351; &Ccedil;ubuk Grafik (gchart)": gcr["Stacked Bar Chart"],\n
        "Alan Grafi&#287;i (gchart)": gcr["Area Chart"]\n
      };\n
    }\n
    if (d3r) {\n
      $.pivotUtilities.locales.tr.d3_renderers = {\n
        "Hiyerar&#351;ik Alan Grafi&#287;i (Treemap)": d3r["Treemap"]\n
      };\n
    }\n
    if (c3r) {\n
      $.pivotUtilities.locales.tr.c3_renderers = {\n
        "&Ccedil;izgi Grafi&#287;i (C3)": c3r["Line Chart C3"],\n
        "Bar Grafi&#287;i (C3)": c3r["Bar Chart C3"]\n
      };\n
    }\n
    return $.pivotUtilities.locales.tr;\n
  });\n
\n
}).call(this);\n
\n
//# sourceMappingURL=pivot.tr.js.map

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3910</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
