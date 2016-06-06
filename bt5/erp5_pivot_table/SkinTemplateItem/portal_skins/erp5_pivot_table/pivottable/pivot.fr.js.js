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
            <value> <string>ts32626243.45</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>pivot.fr.js</string> </value>
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
    var frFmt, frFmtInt, frFmtPct, nf, tpl;\n
    nf = $.pivotUtilities.numberFormat;\n
    tpl = $.pivotUtilities.aggregatorTemplates;\n
    frFmt = nf({\n
      thousandsSep: " ",\n
      decimalSep: ","\n
    });\n
    frFmtInt = nf({\n
      digitsAfterDecimal: 0,\n
      thousandsSep: " ",\n
      decimalSep: ","\n
    });\n
    frFmtPct = nf({\n
      digitsAfterDecimal: 1,\n
      scaler: 100,\n
      suffix: "%",\n
      thousandsSep: " ",\n
      decimalSep: ","\n
    });\n
    return $.pivotUtilities.locales.fr = {\n
      localeStrings: {\n
        renderError: "Une erreur est survenue en dessinant le tableau crois&eacute;.",\n
        computeError: "Une erreur est survenue en calculant le tableau crois&eacute;.",\n
        uiRenderError: "Une erreur est survenue en dessinant l\'interface du tableau crois&eacute; dynamique.",\n
        selectAll: "S&eacute;lectionner tout",\n
        selectNone: "S&eacute;lectionner rien",\n
        tooMany: "(trop de valeurs &agrave; afficher)",\n
        filterResults: "Filtrer les valeurs",\n
        totals: "Totaux",\n
        vs: "sur",\n
        by: "par"\n
      },\n
      aggregators: {\n
        "Nombre": tpl.count(frFmtInt),\n
        "Nombre de valeurs uniques": tpl.countUnique(frFmtInt),\n
        "Liste de valeurs uniques": tpl.listUnique(", "),\n
        "Somme": tpl.sum(frFmt),\n
        "Somme en entiers": tpl.sum(frFmtInt),\n
        "Moyenne": tpl.average(frFmt),\n
        "Minimum": tpl.min(frFmt),\n
        "Maximum": tpl.max(frFmt),\n
        "Ratio de sommes": tpl.sumOverSum(frFmt),\n
        "Borne sup&eacute;rieure 80%": tpl.sumOverSumBound80(true, frFmt),\n
        "Borne inf&eacute;rieure 80%": tpl.sumOverSumBound80(false, frFmt),\n
        "Somme en proportion du totale": tpl.fractionOf(tpl.sum(), "total", frFmtPct),\n
        "Somme en proportion de la ligne": tpl.fractionOf(tpl.sum(), "row", frFmtPct),\n
        "Somme en proportion de la colonne": tpl.fractionOf(tpl.sum(), "col", frFmtPct),\n
        "Nombre en proportion du totale": tpl.fractionOf(tpl.count(), "total", frFmtPct),\n
        "Nombre en proportion de la ligne": tpl.fractionOf(tpl.count(), "row", frFmtPct),\n
        "Nombre en proportion de la colonne": tpl.fractionOf(tpl.count(), "col", frFmtPct)\n
      },\n
      renderers: {\n
        "Table": $.pivotUtilities.renderers["Table"],\n
        "Table avec barres": $.pivotUtilities.renderers["Table Barchart"],\n
        "Carte de chaleur": $.pivotUtilities.renderers["Heatmap"],\n
        "Carte de chaleur par ligne": $.pivotUtilities.renderers["Row Heatmap"],\n
        "Carte de chaleur par colonne": $.pivotUtilities.renderers["Col Heatmap"]\n
      }\n
    };\n
  });\n
\n
}).call(this);\n
\n
//# sourceMappingURL=pivot.fr.js.map

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3029</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
