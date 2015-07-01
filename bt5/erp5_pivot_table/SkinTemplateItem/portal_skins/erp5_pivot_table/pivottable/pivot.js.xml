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
            <value> <string>ts32626249.89</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>pivot.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

(function() {\n
  var callWithJQuery,\n
    indexOf = [].indexOf || function(item) { for (var i = 0, l = this.length; i < l; i++) { if (i in this && this[i] === item) return i; } return -1; },\n
    slice = [].slice,\n
    bind = function(fn, me){ return function(){ return fn.apply(me, arguments); }; },\n
    hasProp = {}.hasOwnProperty;\n
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
\n
    /*\n
    Utilities\n
     */\n
    var PivotData, addSeparators, aggregatorTemplates, aggregators, dayNamesEn, derivers, getSort, locales, mthNamesEn, naturalSort, numberFormat, pivotTableRenderer, renderers, sortAs, usFmt, usFmtInt, usFmtPct, zeroPad;\n
    addSeparators = function(nStr, thousandsSep, decimalSep) {\n
      var rgx, x, x1, x2;\n
      nStr += \'\';\n
      x = nStr.split(\'.\');\n
      x1 = x[0];\n
      x2 = x.length > 1 ? decimalSep + x[1] : \'\';\n
      rgx = /(\\d+)(\\d{3})/;\n
      while (rgx.test(x1)) {\n
        x1 = x1.replace(rgx, \'$1\' + thousandsSep + \'$2\');\n
      }\n
      return x1 + x2;\n
    };\n
    numberFormat = function(opts) {\n
      var defaults;\n
      defaults = {\n
        digitsAfterDecimal: 2,\n
        scaler: 1,\n
        thousandsSep: ",",\n
        decimalSep: ".",\n
        prefix: "",\n
        suffix: "",\n
        showZero: false\n
      };\n
      opts = $.extend(defaults, opts);\n
      return function(x) {\n
        var result;\n
        if (isNaN(x) || !isFinite(x)) {\n
          return "";\n
        }\n
        if (x === 0 && !opts.showZero) {\n
          return "";\n
        }\n
        result = addSeparators((opts.scaler * x).toFixed(opts.digitsAfterDecimal), opts.thousandsSep, opts.decimalSep);\n
        return "" + opts.prefix + result + opts.suffix;\n
      };\n
    };\n
    usFmt = numberFormat();\n
    usFmtInt = numberFormat({\n
      digitsAfterDecimal: 0\n
    });\n
    usFmtPct = numberFormat({\n
      digitsAfterDecimal: 1,\n
      scaler: 100,\n
      suffix: "%"\n
    });\n
    aggregatorTemplates = {\n
      count: function(formatter) {\n
        if (formatter == null) {\n
          formatter = usFmtInt;\n
        }\n
        return function() {\n
          return function(data, rowKey, colKey) {\n
            return {\n
              count: 0,\n
              push: function() {\n
                return this.count++;\n
              },\n
              value: function() {\n
                return this.count;\n
              },\n
              format: formatter\n
            };\n
          };\n
        };\n
      },\n
      countUnique: function(formatter) {\n
        if (formatter == null) {\n
          formatter = usFmtInt;\n
        }\n
        return function(arg) {\n
          var attr;\n
          attr = arg[0];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              uniq: [],\n
              push: function(record) {\n
                var ref;\n
                if (ref = record[attr], indexOf.call(this.uniq, ref) < 0) {\n
                  return this.uniq.push(record[attr]);\n
                }\n
              },\n
              value: function() {\n
                return this.uniq.length;\n
              },\n
              format: formatter,\n
              numInputs: attr != null ? 0 : 1\n
            };\n
          };\n
        };\n
      },\n
      listUnique: function(sep) {\n
        return function(arg) {\n
          var attr;\n
          attr = arg[0];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              uniq: [],\n
              push: function(record) {\n
                var ref;\n
                if (ref = record[attr], indexOf.call(this.uniq, ref) < 0) {\n
                  return this.uniq.push(record[attr]);\n
                }\n
              },\n
              value: function() {\n
                return this.uniq.join(sep);\n
              },\n
              format: function(x) {\n
                return x;\n
              },\n
              numInputs: attr != null ? 0 : 1\n
            };\n
          };\n
        };\n
      },\n
      sum: function(formatter) {\n
        if (formatter == null) {\n
          formatter = usFmt;\n
        }\n
        return function(arg) {\n
          var attr;\n
          attr = arg[0];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              sum: 0,\n
              push: function(record) {\n
                if (!isNaN(parseFloat(record[attr]))) {\n
                  return this.sum += parseFloat(record[attr]);\n
                }\n
              },\n
              value: function() {\n
                return this.sum;\n
              },\n
              format: formatter,\n
              numInputs: attr != null ? 0 : 1\n
            };\n
          };\n
        };\n
      },\n
      min: function(formatter) {\n
        if (formatter == null) {\n
          formatter = usFmt;\n
        }\n
        return function(arg) {\n
          var attr;\n
          attr = arg[0];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              val: null,\n
              push: function(record) {\n
                var ref, x;\n
                x = parseFloat(record[attr]);\n
                if (!isNaN(x)) {\n
                  return this.val = Math.min(x, (ref = this.val) != null ? ref : x);\n
                }\n
              },\n
              value: function() {\n
                return this.val;\n
              },\n
              format: formatter,\n
              numInputs: attr != null ? 0 : 1\n
            };\n
          };\n
        };\n
      },\n
      max: function(formatter) {\n
        if (formatter == null) {\n
          formatter = usFmt;\n
        }\n
        return function(arg) {\n
          var attr;\n
          attr = arg[0];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              val: null,\n
              push: function(record) {\n
                var ref, x;\n
                x = parseFloat(record[attr]);\n
                if (!isNaN(x)) {\n
                  return this.val = Math.max(x, (ref = this.val) != null ? ref : x);\n
                }\n
              },\n
              value: function() {\n
                return this.val;\n
              },\n
              format: formatter,\n
              numInputs: attr != null ? 0 : 1\n
            };\n
          };\n
        };\n
      },\n
      average: function(formatter) {\n
        if (formatter == null) {\n
          formatter = usFmt;\n
        }\n
        return function(arg) {\n
          var attr;\n
          attr = arg[0];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              sum: 0,\n
              len: 0,\n
              push: function(record) {\n
                if (!isNaN(parseFloat(record[attr]))) {\n
                  this.sum += parseFloat(record[attr]);\n
                  return this.len++;\n
                }\n
              },\n
              value: function() {\n
                return this.sum / this.len;\n
              },\n
              format: formatter,\n
              numInputs: attr != null ? 0 : 1\n
            };\n
          };\n
        };\n
      },\n
      sumOverSum: function(formatter) {\n
        if (formatter == null) {\n
          formatter = usFmt;\n
        }\n
        return function(arg) {\n
          var denom, num;\n
          num = arg[0], denom = arg[1];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              sumNum: 0,\n
              sumDenom: 0,\n
              push: function(record) {\n
                if (!isNaN(parseFloat(record[num]))) {\n
                  this.sumNum += parseFloat(record[num]);\n
                }\n
                if (!isNaN(parseFloat(record[denom]))) {\n
                  return this.sumDenom += parseFloat(record[denom]);\n
                }\n
              },\n
              value: function() {\n
                return this.sumNum / this.sumDenom;\n
              },\n
              format: formatter,\n
              numInputs: (num != null) && (denom != null) ? 0 : 2\n
            };\n
          };\n
        };\n
      },\n
      sumOverSumBound80: function(upper, formatter) {\n
        if (upper == null) {\n
          upper = true;\n
        }\n
        if (formatter == null) {\n
          formatter = usFmt;\n
        }\n
        return function(arg) {\n
          var denom, num;\n
          num = arg[0], denom = arg[1];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              sumNum: 0,\n
              sumDenom: 0,\n
              push: function(record) {\n
                if (!isNaN(parseFloat(record[num]))) {\n
                  this.sumNum += parseFloat(record[num]);\n
                }\n
                if (!isNaN(parseFloat(record[denom]))) {\n
                  return this.sumDenom += parseFloat(record[denom]);\n
                }\n
              },\n
              value: function() {\n
                var sign;\n
                sign = upper ? 1 : -1;\n
                return (0.821187207574908 / this.sumDenom + this.sumNum / this.sumDenom + 1.2815515655446004 * sign * Math.sqrt(0.410593603787454 / (this.sumDenom * this.sumDenom) + (this.sumNum * (1 - this.sumNum / this.sumDenom)) / (this.sumDenom * this.sumDenom))) / (1 + 1.642374415149816 / this.sumDenom);\n
              },\n
              format: formatter,\n
              numInputs: (num != null) && (denom != null) ? 0 : 2\n
            };\n
          };\n
        };\n
      },\n
      fractionOf: function(wrapped, type, formatter) {\n
        if (type == null) {\n
          type = "total";\n
        }\n
        if (formatter == null) {\n
          formatter = usFmtPct;\n
        }\n
        return function() {\n
          var x;\n
          x = 1 <= arguments.length ? slice.call(arguments, 0) : [];\n
          return function(data, rowKey, colKey) {\n
            return {\n
              selector: {\n
                total: [[], []],\n
                row: [rowKey, []],\n
                col: [[], colKey]\n
              }[type],\n
              inner: wrapped.apply(null, x)(data, rowKey, colKey),\n
              push: function(record) {\n
                return this.inner.push(record);\n
              },\n
              format: formatter,\n
              value: function() {\n
                return this.inner.value() / data.getAggregator.apply(data, this.selector).inner.value();\n
              },\n
              numInputs: wrapped.apply(null, x)().numInputs\n
            };\n
          };\n
        };\n
      }\n
    };\n
    aggregators = (function(tpl) {\n
      return {\n
        "Count": tpl.count(usFmtInt),\n
        "Count Unique Values": tpl.countUnique(usFmtInt),\n
        "List Unique Values": tpl.listUnique(", "),\n
        "Sum": tpl.sum(usFmt),\n
        "Integer Sum": tpl.sum(usFmtInt),\n
        "Average": tpl.average(usFmt),\n
        "Minimum": tpl.min(usFmt),\n
        "Maximum": tpl.max(usFmt),\n
        "Sum over Sum": tpl.sumOverSum(usFmt),\n
        "80% Upper Bound": tpl.sumOverSumBound80(true, usFmt),\n
        "80% Lower Bound": tpl.sumOverSumBound80(false, usFmt),\n
        "Sum as Fraction of Total": tpl.fractionOf(tpl.sum(), "total", usFmtPct),\n
        "Sum as Fraction of Rows": tpl.fractionOf(tpl.sum(), "row", usFmtPct),\n
        "Sum as Fraction of Columns": tpl.fractionOf(tpl.sum(), "col", usFmtPct),\n
        "Count as Fraction of Total": tpl.fractionOf(tpl.count(), "total", usFmtPct),\n
        "Count as Fraction of Rows": tpl.fractionOf(tpl.count(), "row", usFmtPct),\n
        "Count as Fraction of Columns": tpl.fractionOf(tpl.count(), "col", usFmtPct)\n
      };\n
    })(aggregatorTemplates);\n
    renderers = {\n
      "Table": function(pvtData, opts) {\n
        return pivotTableRenderer(pvtData, opts);\n
      },\n
      "Table Barchart": function(pvtData, opts) {\n
        return $(pivotTableRenderer(pvtData, opts)).barchart();\n
      },\n
      "Heatmap": function(pvtData, opts) {\n
        return $(pivotTableRenderer(pvtData, opts)).heatmap();\n
      },\n
      "Row Heatmap": function(pvtData, opts) {\n
        return $(pivotTableRenderer(pvtData, opts)).heatmap("rowheatmap");\n
      },\n
      "Col Heatmap": function(pvtData, opts) {\n
        return $(pivotTableRenderer(pvtData, opts)).heatmap("colheatmap");\n
      }\n
    };\n
    locales = {\n
      en: {\n
        aggregators: aggregators,\n
        renderers: renderers,\n
        localeStrings: {\n
          renderError: "An error occurred rendering the PivotTable results.",\n
          computeError: "An error occurred computing the PivotTable results.",\n
          uiRenderError: "An error occurred rendering the PivotTable UI.",\n
          selectAll: "Select All",\n
          selectNone: "Select None",\n
          tooMany: "(too many to list)",\n
          filterResults: "Filter results",\n
          totals: "Totals",\n
          vs: "vs",\n
          by: "by"\n
        }\n
      }\n
    };\n
    mthNamesEn = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];\n
    dayNamesEn = ["Sun", "Mon", "Tue", "Wed", "Thu", "Fri", "Sat"];\n
    zeroPad = function(number) {\n
      return ("0" + number).substr(-2, 2);\n
    };\n
    derivers = {\n
      bin: function(col, binWidth) {\n
        return function(record) {\n
          return record[col] - record[col] % binWidth;\n
        };\n
      },\n
      dateFormat: function(col, formatString, utcOutput, mthNames, dayNames) {\n
        var utc;\n
        if (utcOutput == null) {\n
          utcOutput = false;\n
        }\n
        if (mthNames == null) {\n
          mthNames = mthNamesEn;\n
        }\n
        if (dayNames == null) {\n
          dayNames = dayNamesEn;\n
        }\n
        utc = utcOutput ? "UTC" : "";\n
        return function(record) {\n
          var date;\n
          date = new Date(Date.parse(record[col]));\n
          if (isNaN(date)) {\n
            return "";\n
          }\n
          return formatString.replace(/%(.)/g, function(m, p) {\n
            switch (p) {\n
              case "y":\n
                return date["get" + utc + "FullYear"]();\n
              case "m":\n
                return zeroPad(date["get" + utc + "Month"]() + 1);\n
              case "n":\n
                return mthNames[date["get" + utc + "Month"]()];\n
              case "d":\n
                return zeroPad(date["get" + utc + "Date"]());\n
              case "w":\n
                return dayNames[date["get" + utc + "Day"]()];\n
              case "x":\n
                return date["get" + utc + "Day"]();\n
              case "H":\n
                return zeroPad(date["get" + utc + "Hours"]());\n
              case "M":\n
                return zeroPad(date["get" + utc + "Minutes"]());\n
              case "S":\n
                return zeroPad(date["get" + utc + "Seconds"]());\n
              default:\n
                return "%" + p;\n
            }\n
          });\n
        };\n
      }\n
    };\n
    naturalSort = (function(_this) {\n
      return function(as, bs) {\n
        var a, a1, b, b1, rd, rx, rz;\n
        rx = /(\\d+)|(\\D+)/g;\n
        rd = /\\d/;\n
        rz = /^0/;\n
        if (typeof as === "number" || typeof bs === "number") {\n
          if (isNaN(as)) {\n
            return 1;\n
          }\n
          if (isNaN(bs)) {\n
            return -1;\n
          }\n
          return as - bs;\n
        }\n
        a = String(as).toLowerCase();\n
        b = String(bs).toLowerCase();\n
        if (a === b) {\n
          return 0;\n
        }\n
        if (!(rd.test(a) && rd.test(b))) {\n
          return (a > b ? 1 : -1);\n
        }\n
        a = a.match(rx);\n
        b = b.match(rx);\n
        while (a.length && b.length) {\n
          a1 = a.shift();\n
          b1 = b.shift();\n
          if (a1 !== b1) {\n
            if (rd.test(a1) && rd.test(b1)) {\n
              return a1.replace(rz, ".0") - b1.replace(rz, ".0");\n
            } else {\n
              return (a1 > b1 ? 1 : -1);\n
            }\n
          }\n
        }\n
        return a.length - b.length;\n
      };\n
    })(this);\n
    sortAs = function(order) {\n
      var i, mapping, x;\n
      mapping = {};\n
      for (i in order) {\n
        x = order[i];\n
        mapping[x] = i;\n
      }\n
      return function(a, b) {\n
        if ((mapping[a] != null) && (mapping[b] != null)) {\n
          return mapping[a] - mapping[b];\n
        } else if (mapping[a] != null) {\n
          return -1;\n
        } else if (mapping[b] != null) {\n
          return 1;\n
        } else {\n
          return naturalSort(a, b);\n
        }\n
      };\n
    };\n
    getSort = function(sorters, attr) {\n
      var sort;\n
      sort = sorters(attr);\n
      if ($.isFunction(sort)) {\n
        return sort;\n
      } else {\n
        return naturalSort;\n
      }\n
    };\n
    $.pivotUtilities = {\n
      aggregatorTemplates: aggregatorTemplates,\n
      aggregators: aggregators,\n
      renderers: renderers,\n
      derivers: derivers,\n
      locales: locales,\n
      naturalSort: naturalSort,\n
      numberFormat: numberFormat,\n
      sortAs: sortAs\n
    };\n
\n
    /*\n
    Data Model class\n
     */\n
    PivotData = (function() {\n
      function PivotData(input, opts) {\n
        this.getAggregator = bind(this.getAggregator, this);\n
        this.getRowKeys = bind(this.getRowKeys, this);\n
        this.getColKeys = bind(this.getColKeys, this);\n
        this.sortKeys = bind(this.sortKeys, this);\n
        this.arrSort = bind(this.arrSort, this);\n
        this.aggregator = opts.aggregator;\n
        this.aggregatorName = opts.aggregatorName;\n
        this.colAttrs = opts.cols;\n
        this.rowAttrs = opts.rows;\n
        this.valAttrs = opts.vals;\n
        this.sorters = opts.sorters;\n
        this.tree = {};\n
        this.rowKeys = [];\n
        this.colKeys = [];\n
        this.rowTotals = {};\n
        this.colTotals = {};\n
        this.allTotal = this.aggregator(this, [], []);\n
        this.sorted = false;\n
        PivotData.forEachRecord(input, opts.derivedAttributes, (function(_this) {\n
          return function(record) {\n
            if (opts.filter(record)) {\n
              return _this.processRecord(record);\n
            }\n
          };\n
        })(this));\n
      }\n
\n
      PivotData.forEachRecord = function(input, derivedAttributes, f) {\n
        var addRecord, compactRecord, i, j, k, l, len1, record, ref, results, results1, tblCols;\n
        if ($.isEmptyObject(derivedAttributes)) {\n
          addRecord = f;\n
        } else {\n
          addRecord = function(record) {\n
            var k, ref, v;\n
            for (k in derivedAttributes) {\n
              v = derivedAttributes[k];\n
              record[k] = (ref = v(record)) != null ? ref : record[k];\n
            }\n
            return f(record);\n
          };\n
        }\n
        if ($.isFunction(input)) {\n
          return input(addRecord);\n
        } else if ($.isArray(input)) {\n
          if ($.isArray(input[0])) {\n
            results = [];\n
            for (i in input) {\n
              if (!hasProp.call(input, i)) continue;\n
              compactRecord = input[i];\n
              if (!(i > 0)) {\n
                continue;\n
              }\n
              record = {};\n
              ref = input[0];\n
              for (j in ref) {\n
                if (!hasProp.call(ref, j)) continue;\n
                k = ref[j];\n
                record[k] = compactRecord[j];\n
              }\n
              results.push(addRecord(record));\n
            }\n
            return results;\n
          } else {\n
            results1 = [];\n
            for (l = 0, len1 = input.length; l < len1; l++) {\n
              record = input[l];\n
              results1.push(addRecord(record));\n
            }\n
            return results1;\n
          }\n
        } else if (input instanceof jQuery) {\n
          tblCols = [];\n
          $("thead > tr > th", input).each(function(i) {\n
            return tblCols.push($(this).text());\n
          });\n
          return $("tbody > tr", input).each(function(i) {\n
            record = {};\n
            $("td", this).each(function(j) {\n
              return record[tblCols[j]] = $(this).html();\n
            });\n
            return addRecord(record);\n
          });\n
        } else {\n
          throw new Error("unknown input format");\n
        }\n
      };\n
\n
      PivotData.convertToArray = function(input) {\n
        var result;\n
        result = [];\n
        PivotData.forEachRecord(input, {}, function(record) {\n
          return result.push(record);\n
        });\n
        return result;\n
      };\n
\n
      PivotData.prototype.arrSort = function(attrs) {\n
        var a, sortersArr;\n
        sortersArr = (function() {\n
          var l, len1, results;\n
          results = [];\n
          for (l = 0, len1 = attrs.length; l < len1; l++) {\n
            a = attrs[l];\n
            results.push(getSort(this.sorters, a));\n
          }\n
          return results;\n
        }).call(this);\n
        return function(a, b) {\n
          var comparison, i, sorter;\n
          for (i in sortersArr) {\n
            sorter = sortersArr[i];\n
            comparison = sorter(a[i], b[i]);\n
            if (comparison !== 0) {\n
              return comparison;\n
            }\n
          }\n
          return 0;\n
        };\n
      };\n
\n
      PivotData.prototype.sortKeys = function() {\n
        if (!this.sorted) {\n
          this.sorted = true;\n
          this.rowKeys.sort(this.arrSort(this.rowAttrs));\n
          return this.colKeys.sort(this.arrSort(this.colAttrs));\n
        }\n
      };\n
\n
      PivotData.prototype.getColKeys = function() {\n
        this.sortKeys();\n
        return this.colKeys;\n
      };\n
\n
      PivotData.prototype.getRowKeys = function() {\n
        this.sortKeys();\n
        return this.rowKeys;\n
      };\n
\n
      PivotData.prototype.processRecord = function(record) {\n
        var colKey, flatColKey, flatRowKey, l, len1, len2, n, ref, ref1, ref2, ref3, rowKey, x;\n
        colKey = [];\n
        rowKey = [];\n
        ref = this.colAttrs;\n
        for (l = 0, len1 = ref.length; l < len1; l++) {\n
          x = ref[l];\n
          colKey.push((ref1 = record[x]) != null ? ref1 : "null");\n
        }\n
        ref2 = this.rowAttrs;\n
        for (n = 0, len2 = ref2.length; n < len2; n++) {\n
          x = ref2[n];\n
          rowKey.push((ref3 = record[x]) != null ? ref3 : "null");\n
        }\n
        flatRowKey = rowKey.join(String.fromCharCode(0));\n
        flatColKey = colKey.join(String.fromCharCode(0));\n
        this.allTotal.push(record);\n
        if (rowKey.length !== 0) {\n
          if (!this.rowTotals[flatRowKey]) {\n
            this.rowKeys.push(rowKey);\n
            this.rowTotals[flatRowKey] = this.aggregator(this, rowKey, []);\n
          }\n
          this.rowTotals[flatRowKey].push(record);\n
        }\n
        if (colKey.length !== 0) {\n
          if (!this.colTotals[flatColKey]) {\n
            this.colKeys.push(colKey);\n
            this.colTotals[flatColKey] = this.aggregator(this, [], colKey);\n
          }\n
          this.colTotals[flatColKey].push(record);\n
        }\n
        if (colKey.length !== 0 && rowKey.length !== 0) {\n
          if (!this.tree[flatRowKey]) {\n
            this.tree[flatRowKey] = {};\n
          }\n
          if (!this.tree[flatRowKey][flatColKey]) {\n
            this.tree[flatRowKey][flatColKey] = this.aggregator(this, rowKey, colKey);\n
          }\n
          return this.tree[flatRowKey][flatColKey].push(record);\n
        }\n
      };\n
\n
      PivotData.prototype.getAggregator = function(rowKey, colKey) {\n
        var agg, flatColKey, flatRowKey;\n
        flatRowKey = rowKey.join(String.fromCharCode(0));\n
        flatColKey = colKey.join(String.fromCharCode(0));\n
        if (rowKey.length === 0 && colKey.length === 0) {\n
          agg = this.allTotal;\n
        } else if (rowKey.length === 0) {\n
          agg = this.colTotals[flatColKey];\n
        } else if (colKey.length === 0) {\n
          agg = this.rowTotals[flatRowKey];\n
        } else {\n
          agg = this.tree[flatRowKey][flatColKey];\n
        }\n
        return agg != null ? agg : {\n
          value: (function() {\n
            return null;\n
          }),\n
          format: function() {\n
            return "";\n
          }\n
        };\n
      };\n
\n
      return PivotData;\n
\n
    })();\n
\n
    /*\n
    Default Renderer for hierarchical table layout\n
     */\n
    pivotTableRenderer = function(pivotData, opts) {\n
      var aggregator, c, colAttrs, colKey, colKeys, defaults, i, j, r, result, rowAttrs, rowKey, rowKeys, spanSize, td, th, totalAggregator, tr, txt, val, x;\n
      defaults = {\n
        localeStrings: {\n
          totals: "Totals"\n
        }\n
      };\n
      opts = $.extend(defaults, opts);\n
      colAttrs = pivotData.colAttrs;\n
      rowAttrs = pivotData.rowAttrs;\n
      rowKeys = pivotData.getRowKeys();\n
      colKeys = pivotData.getColKeys();\n
      result = document.createElement("table");\n
      result.className = "pvtTable";\n
      spanSize = function(arr, i, j) {\n
        var l, len, n, noDraw, ref, ref1, stop, x;\n
        if (i !== 0) {\n
          noDraw = true;\n
          for (x = l = 0, ref = j; 0 <= ref ? l <= ref : l >= ref; x = 0 <= ref ? ++l : --l) {\n
            if (arr[i - 1][x] !== arr[i][x]) {\n
              noDraw = false;\n
            }\n
          }\n
          if (noDraw) {\n
            return -1;\n
          }\n
        }\n
        len = 0;\n
        while (i + len < arr.length) {\n
          stop = false;\n
          for (x = n = 0, ref1 = j; 0 <= ref1 ? n <= ref1 : n >= ref1; x = 0 <= ref1 ? ++n : --n) {\n
            if (arr[i][x] !== arr[i + len][x]) {\n
              stop = true;\n
            }\n
          }\n
          if (stop) {\n
            break;\n
          }\n
          len++;\n
        }\n
        return len;\n
      };\n
      for (j in colAttrs) {\n
        if (!hasProp.call(colAttrs, j)) continue;\n
        c = colAttrs[j];\n
        tr = document.createElement("tr");\n
        if (parseInt(j) === 0 && rowAttrs.length !== 0) {\n
          th = document.createElement("th");\n
          th.setAttribute("colspan", rowAttrs.length);\n
          th.setAttribute("rowspan", colAttrs.length);\n
          tr.appendChild(th);\n
        }\n
        th = document.createElement("th");\n
        th.className = "pvtAxisLabel";\n
        th.innerHTML = c;\n
        tr.appendChild(th);\n
        for (i in colKeys) {\n
          if (!hasProp.call(colKeys, i)) continue;\n
          colKey = colKeys[i];\n
          x = spanSize(colKeys, parseInt(i), parseInt(j));\n
          if (x !== -1) {\n
            th = document.createElement("th");\n
            th.className = "pvtColLabel";\n
            th.innerHTML = colKey[j];\n
            th.setAttribute("colspan", x);\n
            if (parseInt(j) === colAttrs.length - 1 && rowAttrs.length !== 0) {\n
              th.setAttribute("rowspan", 2);\n
            }\n
            tr.appendChild(th);\n
          }\n
        }\n
        if (parseInt(j) === 0) {\n
          th = document.createElement("th");\n
          th.className = "pvtTotalLabel";\n
          th.innerHTML = opts.localeStrings.totals;\n
          th.setAttribute("rowspan", colAttrs.length + (rowAttrs.length === 0 ? 0 : 1));\n
          tr.appendChild(th);\n
        }\n
        result.appendChild(tr);\n
      }\n
      if (rowAttrs.length !== 0) {\n
        tr = document.createElement("tr");\n
        for (i in rowAttrs) {\n
          if (!hasProp.call(rowAttrs, i)) continue;\n
          r = rowAttrs[i];\n
          th = document.createElement("th");\n
          th.className = "pvtAxisLabel";\n
          th.innerHTML = r;\n
          tr.appendChild(th);\n
        }\n
        th = document.createElement("th");\n
        if (colAttrs.length === 0) {\n
          th.className = "pvtTotalLabel";\n
          th.innerHTML = opts.localeStrings.totals;\n
        }\n
        tr.appendChild(th);\n
        result.appendChild(tr);\n
      }\n
      for (i in rowKeys) {\n
        if (!hasProp.call(rowKeys, i)) continue;\n
        rowKey = rowKeys[i];\n
        tr = document.createElement("tr");\n
        for (j in rowKey) {\n
          if (!hasProp.call(rowKey, j)) continue;\n
          txt = rowKey[j];\n
          x = spanSize(rowKeys, parseInt(i), parseInt(j));\n
          if (x !== -1) {\n
            th = document.createElement("th");\n
            th.className = "pvtRowLabel";\n
            th.innerHTML = txt;\n
            th.setAttribute("rowspan", x);\n
            if (parseInt(j) === rowAttrs.length - 1 && colAttrs.length !== 0) {\n
              th.setAttribute("colspan", 2);\n
            }\n
            tr.appendChild(th);\n
          }\n
        }\n
        for (j in colKeys) {\n
          if (!hasProp.call(colKeys, j)) continue;\n
          colKey = colKeys[j];\n
          aggregator = pivotData.getAggregator(rowKey, colKey);\n
          val = aggregator.value();\n
          td = document.createElement("td");\n
          td.className = "pvtVal row" + i + " col" + j;\n
          td.innerHTML = aggregator.format(val);\n
          td.setAttribute("data-value", val);\n
          tr.appendChild(td);\n
        }\n
        totalAggregator = pivotData.getAggregator(rowKey, []);\n
        val = totalAggregator.value();\n
        td = document.createElement("td");\n
        td.className = "pvtTotal rowTotal";\n
        td.innerHTML = totalAggregator.format(val);\n
        td.setAttribute("data-value", val);\n
        td.setAttribute("data-for", "row" + i);\n
        tr.appendChild(td);\n
        result.appendChild(tr);\n
      }\n
      tr = document.createElement("tr");\n
      th = document.createElement("th");\n
      th.className = "pvtTotalLabel";\n
      th.innerHTML = opts.localeStrings.totals;\n
      th.setAttribute("colspan", rowAttrs.length + (colAttrs.length === 0 ? 0 : 1));\n
      tr.appendChild(th);\n
      for (j in colKeys) {\n
        if (!hasProp.call(colKeys, j)) continue;\n
        colKey = colKeys[j];\n
        totalAggregator = pivotData.getAggregator([], colKey);\n
        val = totalAggregator.value();\n
        td = document.createElement("td");\n
        td.className = "pvtTotal colTotal";\n
        td.innerHTML = totalAggregator.format(val);\n
        td.setAttribute("data-value", val);\n
        td.setAttribute("data-for", "col" + j);\n
        tr.appendChild(td);\n
      }\n
      totalAggregator = pivotData.getAggregator([], []);\n
      val = totalAggregator.value();\n
      td = document.createElement("td");\n
      td.className = "pvtGrandTotal";\n
      td.innerHTML = totalAggregator.format(val);\n
      td.setAttribute("data-value", val);\n
      tr.appendChild(td);\n
      result.appendChild(tr);\n
      result.setAttribute("data-numrows", rowKeys.length);\n
      result.setAttribute("data-numcols", colKeys.length);\n
      return result;\n
    };\n
\n
    /*\n
    Pivot Table core: create PivotData object and call Renderer on it\n
     */\n
    $.fn.pivot = function(input, opts) {\n
      var defaults, e, pivotData, result, x;\n
      defaults = {\n
        cols: [],\n
        rows: [],\n
        vals: [],\n
        filter: function() {\n
          return true;\n
        },\n
        aggregator: aggregatorTemplates.count()(),\n
        aggregatorName: "Count",\n
        sorters: function() {},\n
        derivedAttributes: {},\n
        renderer: pivotTableRenderer,\n
        rendererOptions: null,\n
        localeStrings: locales.en.localeStrings\n
      };\n
      opts = $.extend(defaults, opts);\n
      result = null;\n
      try {\n
        pivotData = new PivotData(input, opts);\n
        try {\n
          result = opts.renderer(pivotData, opts.rendererOptions);\n
        } catch (_error) {\n
          e = _error;\n
          if (typeof console !== "undefined" && console !== null) {\n
            console.error(e.stack);\n
          }\n
          result = $("<span>").html(opts.localeStrings.renderError);\n
        }\n
      } catch (_error) {\n
        e = _error;\n
        if (typeof console !== "undefined" && console !== null) {\n
          console.error(e.stack);\n
        }\n
        result = $("<span>").html(opts.localeStrings.computeError);\n
      }\n
      x = this[0];\n
      while (x.hasChildNodes()) {\n
        x.removeChild(x.lastChild);\n
      }\n
      return this.append(result);\n
    };\n
\n
    /*\n
    Pivot Table UI: calls Pivot Table core above with options set by user\n
     */\n
    $.fn.pivotUI = function(input, inputOpts, overwrite, locale) {\n
      var a, aggregator, attrLength, axisValues, c, colList, defaults, e, existingOpts, fn, i, initialRender, k, l, len1, len2, len3, len4, n, o, opts, pivotTable, q, ref, ref1, ref2, ref3, ref4, refresh, refreshDelayed, renderer, rendererControl, shownAttributes, tblCols, tr1, tr2, uiTable, unusedAttrsVerticalAutoCutoff, unusedAttrsVerticalAutoOverride, x;\n
      if (overwrite == null) {\n
        overwrite = false;\n
      }\n
      if (locale == null) {\n
        locale = "en";\n
      }\n
      defaults = {\n
        derivedAttributes: {},\n
        aggregators: locales[locale].aggregators,\n
        renderers: locales[locale].renderers,\n
        hiddenAttributes: [],\n
        menuLimit: 200,\n
        cols: [],\n
        rows: [],\n
        vals: [],\n
        exclusions: {},\n
        unusedAttrsVertical: 85,\n
        autoSortUnusedAttrs: false,\n
        rendererOptions: {\n
          localeStrings: locales[locale].localeStrings\n
        },\n
        onRefresh: null,\n
        filter: function() {\n
          return true;\n
        },\n
        sorters: function() {},\n
        localeStrings: locales[locale].localeStrings\n
      };\n
      existingOpts = this.data("pivotUIOptions");\n
      if ((existingOpts == null) || overwrite) {\n
        opts = $.extend(defaults, inputOpts);\n
      } else {\n
        opts = existingOpts;\n
      }\n
      try {\n
        input = PivotData.convertToArray(input);\n
        tblCols = (function() {\n
          var ref, results;\n
          ref = input[0];\n
          results = [];\n
          for (k in ref) {\n
            if (!hasProp.call(ref, k)) continue;\n
            results.push(k);\n
          }\n
          return results;\n
        })();\n
        ref = opts.derivedAttributes;\n
        for (c in ref) {\n
          if (!hasProp.call(ref, c)) continue;\n
          if ((indexOf.call(tblCols, c) < 0)) {\n
            tblCols.push(c);\n
          }\n
        }\n
        axisValues = {};\n
        for (l = 0, len1 = tblCols.length; l < len1; l++) {\n
          x = tblCols[l];\n
          axisValues[x] = {};\n
        }\n
        PivotData.forEachRecord(input, opts.derivedAttributes, function(record) {\n
          var base, results, v;\n
          results = [];\n
          for (k in record) {\n
            if (!hasProp.call(record, k)) continue;\n
            v = record[k];\n
            if (!(opts.filter(record))) {\n
              continue;\n
            }\n
            if (v == null) {\n
              v = "null";\n
            }\n
            if ((base = axisValues[k])[v] == null) {\n
              base[v] = 0;\n
            }\n
            results.push(axisValues[k][v]++);\n
          }\n
          return results;\n
        });\n
        uiTable = $("<table>", {\n
          "class": "pvtUi"\n
        }).attr("cellpadding", 5);\n
        rendererControl = $("<td>");\n
        renderer = $("<select>").addClass(\'pvtRenderer\').appendTo(rendererControl).bind("change", function() {\n
          return refresh();\n
        });\n
        ref1 = opts.renderers;\n
        for (x in ref1) {\n
          if (!hasProp.call(ref1, x)) continue;\n
          $("<option>").val(x).html(x).appendTo(renderer);\n
        }\n
        colList = $("<td>").addClass(\'pvtAxisContainer pvtUnused\');\n
        shownAttributes = (function() {\n
          var len2, n, results;\n
          results = [];\n
          for (n = 0, len2 = tblCols.length; n < len2; n++) {\n
            c = tblCols[n];\n
            if (indexOf.call(opts.hiddenAttributes, c) < 0) {\n
              results.push(c);\n
            }\n
          }\n
          return results;\n
        })();\n
        unusedAttrsVerticalAutoOverride = false;\n
        if (opts.unusedAttrsVertical === "auto") {\n
          unusedAttrsVerticalAutoCutoff = 120;\n
        } else {\n
          unusedAttrsVerticalAutoCutoff = parseInt(opts.unusedAttrsVertical);\n
        }\n
        if (!isNaN(unusedAttrsVerticalAutoCutoff)) {\n
          attrLength = 0;\n
          for (n = 0, len2 = shownAttributes.length; n < len2; n++) {\n
            a = shownAttributes[n];\n
            attrLength += a.length;\n
          }\n
          unusedAttrsVerticalAutoOverride = attrLength > unusedAttrsVerticalAutoCutoff;\n
        }\n
        if (opts.unusedAttrsVertical === true || unusedAttrsVerticalAutoOverride) {\n
          colList.addClass(\'pvtVertList\');\n
        } else {\n
          colList.addClass(\'pvtHorizList\');\n
        }\n
        fn = function(c) {\n
          var attrElem, btns, checkContainer, filterItem, filterItemExcluded, hasExcludedItem, keys, len3, o, ref2, showFilterList, triangleLink, updateFilter, v, valueList;\n
          keys = (function() {\n
            var results;\n
            results = [];\n
            for (k in axisValues[c]) {\n
              results.push(k);\n
            }\n
            return results;\n
          })();\n
          hasExcludedItem = false;\n
          valueList = $("<div>").addClass(\'pvtFilterBox\').hide();\n
          valueList.append($("<h4>").text(c + " (" + keys.length + ")"));\n
          if (keys.length > opts.menuLimit) {\n
            valueList.append($("<p>").html(opts.localeStrings.tooMany));\n
          } else {\n
            btns = $("<p>").appendTo(valueList);\n
            btns.append($("<button>", {\n
              type: "button"\n
            }).html(opts.localeStrings.selectAll).bind("click", function() {\n
              return valueList.find("input:visible").prop("checked", true);\n
            }));\n
            btns.append($("<button>", {\n
              type: "button"\n
            }).html(opts.localeStrings.selectNone).bind("click", function() {\n
              return valueList.find("input:visible").prop("checked", false);\n
            }));\n
            btns.append($("<br>"));\n
            btns.append($("<input>", {\n
              type: "text",\n
              placeholder: opts.localeStrings.filterResults,\n
              "class": "pvtSearch"\n
            }).bind("keyup", function() {\n
              var filter;\n
              filter = $(this).val().toLowerCase();\n
              return valueList.find(\'.pvtCheckContainer p\').each(function() {\n
                var testString;\n
                testString = $(this).text().toLowerCase().indexOf(filter);\n
                if (testString !== -1) {\n
                  return $(this).show();\n
                } else {\n
                  return $(this).hide();\n
                }\n
              });\n
            }));\n
            checkContainer = $("<div>").addClass("pvtCheckContainer").appendTo(valueList);\n
            ref2 = keys.sort(getSort(opts.sorters, c));\n
            for (o = 0, len3 = ref2.length; o < len3; o++) {\n
              k = ref2[o];\n
              v = axisValues[c][k];\n
              filterItem = $("<label>");\n
              filterItemExcluded = opts.exclusions[c] ? (indexOf.call(opts.exclusions[c], k) >= 0) : false;\n
              hasExcludedItem || (hasExcludedItem = filterItemExcluded);\n
              $("<input>").attr("type", "checkbox").addClass(\'pvtFilter\').attr("checked", !filterItemExcluded).data("filter", [c, k]).appendTo(filterItem);\n
              filterItem.append($("<span>").html(k));\n
              filterItem.append($("<span>").text(" (" + v + ")"));\n
              checkContainer.append($("<p>").append(filterItem));\n
            }\n
          }\n
          updateFilter = function() {\n
            var unselectedCount;\n
            unselectedCount = valueList.find("[type=\'checkbox\']").length - valueList.find("[type=\'checkbox\']:checked").length;\n
            if (unselectedCount > 0) {\n
              attrElem.addClass("pvtFilteredAttribute");\n
            } else {\n
              attrElem.removeClass("pvtFilteredAttribute");\n
            }\n
            if (keys.length > opts.menuLimit) {\n
              return valueList.toggle();\n
            } else {\n
              return valueList.toggle(0, refresh);\n
            }\n
          };\n
          $("<p>").appendTo(valueList).append($("<button>", {\n
            type: "button"\n
          }).text("OK").bind("click", updateFilter));\n
          showFilterList = function(e) {\n
            valueList.css({\n
              left: e.pageX,\n
              top: e.pageY\n
            }).toggle();\n
            valueList.find(\'.pvtSearch\').val(\'\');\n
            return valueList.find(\'.pvtCheckContainer p\').show();\n
          };\n
          triangleLink = $("<span>").addClass(\'pvtTriangle\').html(" &#x25BE;").bind("click", showFilterList);\n
          attrElem = $("<li>").addClass("axis_" + i).append($("<span>").addClass(\'pvtAttr\').text(c).data("attrName", c).append(triangleLink));\n
          if (hasExcludedItem) {\n
            attrElem.addClass(\'pvtFilteredAttribute\');\n
          }\n
          colList.append(attrElem).append(valueList);\n
          return attrElem.bind("dblclick", showFilterList);\n
        };\n
        for (i in shownAttributes) {\n
          if (!hasProp.call(shownAttributes, i)) continue;\n
          c = shownAttributes[i];\n
          fn(c);\n
        }\n
        tr1 = $("<tr>").appendTo(uiTable);\n
        aggregator = $("<select>").addClass(\'pvtAggregator\').bind("change", function() {\n
          return refresh();\n
        });\n
        ref2 = opts.aggregators;\n
        for (x in ref2) {\n
          if (!hasProp.call(ref2, x)) continue;\n
          aggregator.append($("<option>").val(x).html(x));\n
        }\n
        $("<td>").addClass(\'pvtVals\').appendTo(tr1).append(aggregator).append($("<br>"));\n
        $("<td>").addClass(\'pvtAxisContainer pvtHorizList pvtCols\').appendTo(tr1);\n
        tr2 = $("<tr>").appendTo(uiTable);\n
        tr2.append($("<td>").addClass(\'pvtAxisContainer pvtRows\').attr("valign", "top"));\n
        pivotTable = $("<td>").attr("valign", "top").addClass(\'pvtRendererArea\').appendTo(tr2);\n
        if (opts.unusedAttrsVertical === true || unusedAttrsVerticalAutoOverride) {\n
          uiTable.find(\'tr:nth-child(1)\').prepend(rendererControl);\n
          uiTable.find(\'tr:nth-child(2)\').prepend(colList);\n
        } else {\n
          uiTable.prepend($("<tr>").append(rendererControl).append(colList));\n
        }\n
        this.html(uiTable);\n
        ref3 = opts.cols;\n
        for (o = 0, len3 = ref3.length; o < len3; o++) {\n
          x = ref3[o];\n
          this.find(".pvtCols").append(this.find(".axis_" + ($.inArray(x, shownAttributes))));\n
        }\n
        ref4 = opts.rows;\n
        for (q = 0, len4 = ref4.length; q < len4; q++) {\n
          x = ref4[q];\n
          this.find(".pvtRows").append(this.find(".axis_" + ($.inArray(x, shownAttributes))));\n
        }\n
        if (opts.aggregatorName != null) {\n
          this.find(".pvtAggregator").val(opts.aggregatorName);\n
        }\n
        if (opts.rendererName != null) {\n
          this.find(".pvtRenderer").val(opts.rendererName);\n
        }\n
        initialRender = true;\n
        refreshDelayed = (function(_this) {\n
          return function() {\n
            var attr, exclusions, inclusions, len5, newDropdown, numInputsToProcess, pivotUIOptions, pvtVals, ref5, ref6, s, subopts, t, unusedAttrsContainer, vals;\n
            subopts = {\n
              derivedAttributes: opts.derivedAttributes,\n
              localeStrings: opts.localeStrings,\n
              rendererOptions: opts.rendererOptions,\n
              sorters: opts.sorters,\n
              cols: [],\n
              rows: []\n
            };\n
            numInputsToProcess = (ref5 = opts.aggregators[aggregator.val()]([])().numInputs) != null ? ref5 : 0;\n
            vals = [];\n
            _this.find(".pvtRows li span.pvtAttr").each(function() {\n
              return subopts.rows.push($(this).data("attrName"));\n
            });\n
            _this.find(".pvtCols li span.pvtAttr").each(function() {\n
              return subopts.cols.push($(this).data("attrName"));\n
            });\n
            _this.find(".pvtVals select.pvtAttrDropdown").each(function() {\n
              if (numInputsToProcess === 0) {\n
                return $(this).remove();\n
              } else {\n
                numInputsToProcess--;\n
                if ($(this).val() !== "") {\n
                  return vals.push($(this).val());\n
                }\n
              }\n
            });\n
            if (numInputsToProcess !== 0) {\n
              pvtVals = _this.find(".pvtVals");\n
              for (x = s = 0, ref6 = numInputsToProcess; 0 <= ref6 ? s < ref6 : s > ref6; x = 0 <= ref6 ? ++s : --s) {\n
                newDropdown = $("<select>").addClass(\'pvtAttrDropdown\').append($("<option>")).bind("change", function() {\n
                  return refresh();\n
                });\n
                for (t = 0, len5 = shownAttributes.length; t < len5; t++) {\n
                  attr = shownAttributes[t];\n
                  newDropdown.append($("<option>").val(attr).text(attr));\n
                }\n
                pvtVals.append(newDropdown);\n
              }\n
            }\n
            if (initialRender) {\n
              vals = opts.vals;\n
              i = 0;\n
              _this.find(".pvtVals select.pvtAttrDropdown").each(function() {\n
                $(this).val(vals[i]);\n
                return i++;\n
              });\n
              initialRender = false;\n
            }\n
            subopts.aggregatorName = aggregator.val();\n
            subopts.vals = vals;\n
            subopts.aggregator = opts.aggregators[aggregator.val()](vals);\n
            subopts.renderer = opts.renderers[renderer.val()];\n
            exclusions = {};\n
            _this.find(\'input.pvtFilter\').not(\':checked\').each(function() {\n
              var filter;\n
              filter = $(this).data("filter");\n
              if (exclusions[filter[0]] != null) {\n
                return exclusions[filter[0]].push(filter[1]);\n
              } else {\n
                return exclusions[filter[0]] = [filter[1]];\n
              }\n
            });\n
            inclusions = {};\n
            _this.find(\'input.pvtFilter:checked\').each(function() {\n
              var filter;\n
              filter = $(this).data("filter");\n
              if (exclusions[filter[0]] != null) {\n
                if (inclusions[filter[0]] != null) {\n
                  return inclusions[filter[0]].push(filter[1]);\n
                } else {\n
                  return inclusions[filter[0]] = [filter[1]];\n
                }\n
              }\n
            });\n
            subopts.filter = function(record) {\n
              var excludedItems, ref7;\n
              if (!opts.filter(record)) {\n
                return false;\n
              }\n
              for (k in exclusions) {\n
                excludedItems = exclusions[k];\n
                if (ref7 = "" + record[k], indexOf.call(excludedItems, ref7) >= 0) {\n
                  return false;\n
                }\n
              }\n
              return true;\n
            };\n
            pivotTable.pivot(input, subopts);\n
            pivotUIOptions = $.extend(opts, {\n
              cols: subopts.cols,\n
              rows: subopts.rows,\n
              vals: vals,\n
              exclusions: exclusions,\n
              inclusionsInfo: inclusions,\n
              aggregatorName: aggregator.val(),\n
              rendererName: renderer.val()\n
            });\n
            _this.data("pivotUIOptions", pivotUIOptions);\n
            if (opts.autoSortUnusedAttrs) {\n
              unusedAttrsContainer = _this.find("td.pvtUnused.pvtAxisContainer");\n
              $(unusedAttrsContainer).children("li").sort(function(a, b) {\n
                return naturalSort($(a).text(), $(b).text());\n
              }).appendTo(unusedAttrsContainer);\n
            }\n
            pivotTable.css("opacity", 1);\n
            if (opts.onRefresh != null) {\n
              return opts.onRefresh(pivotUIOptions);\n
            }\n
          };\n
        })(this);\n
        refresh = (function(_this) {\n
          return function() {\n
            pivotTable.css("opacity", 0.5);\n
            return setTimeout(refreshDelayed, 10);\n
          };\n
        })(this);\n
        refresh();\n
        this.find(".pvtAxisContainer").sortable({\n
          update: function(e, ui) {\n
            if (ui.sender == null) {\n
              return refresh();\n
            }\n
          },\n
          connectWith: this.find(".pvtAxisContainer"),\n
          items: \'li\',\n
          placeholder: \'pvtPlaceholder\'\n
        });\n
      } catch (_error) {\n
        e = _error;\n
        if (typeof console !== "undefined" && console !== null) {\n
          console.error(e.stack);\n
        }\n
        this.html(opts.localeStrings.uiRenderError);\n
      }\n
      return this;\n
    };\n
\n
    /*\n
    Heatmap post-processing\n
     */\n
    $.fn.heatmap = function(scope) {\n
      var colorGen, heatmapper, i, j, l, n, numCols, numRows, ref, ref1;\n
      if (scope == null) {\n
        scope = "heatmap";\n
      }\n
      numRows = this.data("numrows");\n
      numCols = this.data("numcols");\n
      colorGen = function(color, min, max) {\n
        var hexGen;\n
        hexGen = (function() {\n
          switch (color) {\n
            case "red":\n
              return function(hex) {\n
                return "ff" + hex + hex;\n
              };\n
            case "green":\n
              return function(hex) {\n
                return hex + "ff" + hex;\n
              };\n
            case "blue":\n
              return function(hex) {\n
                return "" + hex + hex + "ff";\n
              };\n
          }\n
        })();\n
        return function(x) {\n
          var hex, intensity;\n
          intensity = 255 - Math.round(255 * (x - min) / (max - min));\n
          hex = intensity.toString(16).split(".")[0];\n
          if (hex.length === 1) {\n
            hex = 0 + hex;\n
          }\n
          return hexGen(hex);\n
        };\n
      };\n
      heatmapper = (function(_this) {\n
        return function(scope, color) {\n
          var colorFor, forEachCell, values;\n
          forEachCell = function(f) {\n
            return _this.find(scope).each(function() {\n
              var x;\n
              x = $(this).data("value");\n
              if ((x != null) && isFinite(x)) {\n
                return f(x, $(this));\n
              }\n
            });\n
          };\n
          values = [];\n
          forEachCell(function(x) {\n
            return values.push(x);\n
          });\n
          colorFor = colorGen(color, Math.min.apply(Math, values), Math.max.apply(Math, values));\n
          return forEachCell(function(x, elem) {\n
            return elem.css("background-color", "#" + colorFor(x));\n
          });\n
        };\n
      })(this);\n
      switch (scope) {\n
        case "heatmap":\n
          heatmapper(".pvtVal", "red");\n
          break;\n
        case "rowheatmap":\n
          for (i = l = 0, ref = numRows; 0 <= ref ? l < ref : l > ref; i = 0 <= ref ? ++l : --l) {\n
            heatmapper(".pvtVal.row" + i, "red");\n
          }\n
          break;\n
        case "colheatmap":\n
          for (j = n = 0, ref1 = numCols; 0 <= ref1 ? n < ref1 : n > ref1; j = 0 <= ref1 ? ++n : --n) {\n
            heatmapper(".pvtVal.col" + j, "red");\n
          }\n
      }\n
      heatmapper(".pvtTotal.rowTotal", "red");\n
      heatmapper(".pvtTotal.colTotal", "red");\n
      return this;\n
    };\n
\n
    /*\n
    Barchart post-processing\n
     */\n
    return $.fn.barchart = function() {\n
      var barcharter, i, l, numCols, numRows, ref;\n
      numRows = this.data("numrows");\n
      numCols = this.data("numcols");\n
      barcharter = (function(_this) {\n
        return function(scope) {\n
          var forEachCell, max, scaler, values;\n
          forEachCell = function(f) {\n
            return _this.find(scope).each(function() {\n
              var x;\n
              x = $(this).data("value");\n
              if ((x != null) && isFinite(x)) {\n
                return f(x, $(this));\n
              }\n
            });\n
          };\n
          values = [];\n
          forEachCell(function(x) {\n
            return values.push(x);\n
          });\n
          max = Math.max.apply(Math, values);\n
          scaler = function(x) {\n
            return 100 * x / (1.4 * max);\n
          };\n
          return forEachCell(function(x, elem) {\n
            var text, wrapper;\n
            text = elem.text();\n
            wrapper = $("<div>").css({\n
              "position": "relative",\n
              "height": "55px"\n
            });\n
            wrapper.append($("<div>").css({\n
              "position": "absolute",\n
              "bottom": 0,\n
              "left": 0,\n
              "right": 0,\n
              "height": scaler(x) + "%",\n
              "background-color": "gray"\n
            }));\n
            wrapper.append($("<div>").text(text).css({\n
              "position": "relative",\n
              "padding-left": "5px",\n
              "padding-right": "5px"\n
            }));\n
            return elem.css({\n
              "padding": 0,\n
              "padding-top": "5px",\n
              "text-align": "center"\n
            }).html(wrapper);\n
          });\n
        };\n
      })(this);\n
      for (i = l = 0, ref = numRows; 0 <= ref ? l < ref : l > ref; i = 0 <= ref ? ++l : --l) {\n
        barcharter(".pvtVal.row" + i);\n
      }\n
      barcharter(".pvtTotal.colTotal");\n
      return this;\n
    };\n
  });\n
\n
}).call(this);\n
\n
//# sourceMappingURL=pivot.js.map

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>51802</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
