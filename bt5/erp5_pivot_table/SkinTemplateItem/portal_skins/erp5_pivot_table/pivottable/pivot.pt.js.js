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
            <value> <string>ts32626249.5</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>pivot.pt.js</string> </value>
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
    $.pivotUtilities.locales.pt = {\n
      localeStrings: {\n
        renderError: "Ocorreu um error ao renderizar os resultados da Tabela Din&atilde;mica.",\n
        computeError: "Ocorreu um error ao computar os resultados da Tabela Din&atilde;mica.",\n
        uiRenderError: "Ocorreu um error ao renderizar a interface da Tabela Din&atilde;mica.",\n
        selectAll: "Selecionar Tudo",\n
        selectNone: "Selecionar Nenhum",\n
        tooMany: "(demais para listar)",\n
        filterResults: "Filtrar resultados",\n
        totals: "Totais",\n
        vs: "vs",\n
        by: "por"\n
      },\n
      aggregators: {\n
        "Contagem": tpl.count(frFmtInt),\n
        "Contagem de Valores &uacute;nicos": tpl.countUnique(frFmtInt),\n
        "Lista de Valores &uacute;nicos": tpl.listUnique(", "),\n
        "Soma": tpl.sum(frFmt),\n
        "Soma de Inteiros": tpl.sum(frFmtInt),\n
        "Média": tpl.average(frFmt),\n
        "Mínimo": tpl.min(frFmt),\n
        "Máximo": tpl.max(frFmt),\n
        "Soma sobre Soma": tpl.sumOverSum(frFmt),\n
        "Limite Superior a 80%": tpl.sumOverSumBound80(true, frFmt),\n
        "Limite Inferior a 80%": tpl.sumOverSumBound80(false, frFmt),\n
        "Soma como Fra&ccedil;&atilde;o do Total": tpl.fractionOf(tpl.sum(), "total", frFmtPct),\n
        "Soma como Fra&ccedil;&atilde;o da Linha": tpl.fractionOf(tpl.sum(), "row", frFmtPct),\n
        "Soma como Fra&ccedil;&atilde;o da Coluna": tpl.fractionOf(tpl.sum(), "col", frFmtPct),\n
        "Contagem como Fra&ccedil;&atilde;o do Total": tpl.fractionOf(tpl.count(), "total", frFmtPct),\n
        "Contagem como Fra&ccedil;&atilde;o da Linha": tpl.fractionOf(tpl.count(), "row", frFmtPct),\n
        "Contagem como Fra&ccedil;&atilde;o da Coluna": tpl.fractionOf(tpl.count(), "col", frFmtPct)\n
      },\n
      renderers: {\n
        "Tabela": r["Table"],\n
        "Tabela com Barras": r["Table Barchart"],\n
        "Mapa de Calor": r["Heatmap"],\n
        "Mapa de Calor por Linhas": r["Row Heatmap"],\n
        "Mapa de Calor por Colunas": r["Col Heatmap"]\n
      }\n
    };\n
    if (gcr) {\n
      $.pivotUtilities.locales.pt.gchart_renderers = {\n
        "Gr&aacute;fico de Linhas": gcr["Line Chart"],\n
        "Gr&aacute;fico de Barras": gcr["Bar Chart"],\n
        "Gr&aacute;fico de Barras Empilhadas": gcr["Stacked Bar Chart"],\n
        "Gr&aacute;fico de &Aacute;rea": gcr["Area Chart"]\n
      };\n
    }\n
    if (d3r) {\n
      $.pivotUtilities.locales.pt.d3_renderers = {\n
        "Mapa de Árvore": d3r["Treemap"]\n
      };\n
    }\n
    if (c3r) {\n
      $.pivotUtilities.locales.pt.c3_renderers = {\n
        "Gr&aacute;fico de Linhas": c3r["Line Chart C3"],\n
        "Gr&aacute;fico de Barras": c3r["Bar Chart C3"]\n
      };\n
    }\n
    return $.pivotUtilities.locales.pt;\n
  });\n
\n
}).call(this);\n
\n
//# sourceMappingURL=pivot.pt.js.map

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3784</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
