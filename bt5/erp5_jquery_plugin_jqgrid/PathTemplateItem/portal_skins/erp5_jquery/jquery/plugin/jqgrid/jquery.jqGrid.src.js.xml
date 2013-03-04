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
            <value> <string>ts58176234.25</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.jqGrid.src.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAI=</string> </persistent>
            </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>441297</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>jquery.jqGrid.src.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="2" aka="AAAAAAAAAAI=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// ==ClosureCompiler==\r\n
// @compilation_level SIMPLE_OPTIMIZATIONS\r\n
\r\n
/**\r\n
 * @license jqGrid  4.4.1  - jQuery Grid\r\n
 * Copyright (c) 2008, Tony Tomov, tony@trirand.com\r\n
 * Dual licensed under the MIT and GPL licenses\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
 * Date: 2012-08-28\r\n
 */\r\n
//jsHint options\r\n
/*global document, window, jQuery, DOMParser, ActiveXObject, $, alert */\r\n
\r\n
(function ($) {\r\n
"use strict";\r\n
$.jgrid = $.jgrid || {};\r\n
$.extend($.jgrid,{\r\n
\tversion : "4.4.1",\r\n
\thtmlDecode : function(value){\r\n
\t\tif(value && (value==\'&nbsp;\' || value==\'&#160;\' || (value.length===1 && value.charCodeAt(0)===160))) { return "";}\r\n
\t\treturn !value ? value : String(value).replace(/&gt;/g, ">").replace(/&lt;/g, "<").replace(/&quot;/g, \'"\').replace(/&amp;/g, "&");\t\t\r\n
\t},\r\n
\thtmlEncode : function (value){\r\n
\t\treturn !value ? value : String(value).replace(/&/g, "&amp;").replace(/\\"/g, "&quot;").replace(/</g, "&lt;").replace(/>/g, "&gt;");\r\n
\t},\r\n
\tformat : function(format){ //jqgformat\r\n
\t\tvar args = $.makeArray(arguments).slice(1);\r\n
\t\tif(format===undefined) { format = ""; }\r\n
\t\treturn format.replace(/\\{(\\d+)\\}/g, function(m, i){\r\n
\t\t\treturn args[i];\r\n
\t\t});\r\n
\t},\r\n
\tgetCellIndex : function (cell) {\r\n
\t\tvar c = $(cell);\r\n
\t\tif (c.is(\'tr\')) { return -1; }\r\n
\t\tc = (!c.is(\'td\') && !c.is(\'th\') ? c.closest("td,th") : c)[0];\r\n
\t\tif ($.browser.msie) { return $.inArray(c, c.parentNode.cells); }\r\n
\t\treturn c.cellIndex;\r\n
\t},\r\n
\tstripHtml : function(v) {\r\n
\t\tv = v+"";\r\n
\t\tvar regexp = /<("[^"]*"|\'[^\']*\'|[^\'">])*>/gi;\r\n
\t\tif (v) {\r\n
\t\t\tv = v.replace(regexp,"");\r\n
\t\t\treturn (v && v !== \'&nbsp;\' && v !== \'&#160;\') ? v.replace(/\\"/g,"\'") : "";\r\n
\t\t} else {\r\n
\t\t\treturn v;\r\n
\t\t}\r\n
\t},\r\n
\tstripPref : function (pref, id) {\r\n
\t\tvar obj = $.type( pref );\r\n
\t\tif( obj == "string" || obj =="number") {\r\n
\t\t\tpref =  String(pref);\r\n
\t\t\tid = pref !== "" ? String(id).replace(String(pref), "") : id;\r\n
\t\t}\r\n
\t\treturn id;\r\n
\t},\r\n
\tstringToDoc : function (xmlString) {\r\n
\t\tvar xmlDoc;\r\n
\t\tif(typeof xmlString !== \'string\') { return xmlString; }\r\n
\t\ttry\t{\r\n
\t\t\tvar parser = new DOMParser();\r\n
\t\t\txmlDoc = parser.parseFromString(xmlString,"text/xml");\r\n
\t\t}\r\n
\t\tcatch(e) {\r\n
\t\t\txmlDoc = new ActiveXObject("Microsoft.XMLDOM");\r\n
\t\t\txmlDoc.async=false;\r\n
\t\t\txmlDoc.loadXML(xmlString);\r\n
\t\t}\r\n
\t\treturn (xmlDoc && xmlDoc.documentElement && xmlDoc.documentElement.tagName != \'parsererror\') ? xmlDoc : null;\r\n
\t},\r\n
\tparse : function(jsonString) {\r\n
\t\tvar js = jsonString;\r\n
\t\tif (js.substr(0,9) == "while(1);") { js = js.substr(9); }\r\n
\t\tif (js.substr(0,2) == "/*") { js = js.substr(2,js.length-4); }\r\n
\t\tif(!js) { js = "{}"; }\r\n
\t\treturn ($.jgrid.useJSON===true && typeof (JSON) === \'object\' && typeof (JSON.parse) === \'function\') ?\r\n
\t\t\tJSON.parse(js) :\r\n
\t\t\teval(\'(\' + js + \')\');\r\n
\t},\r\n
\tparseDate : function(format, date) {\r\n
\t\tvar tsp = {m : 1, d : 1, y : 1970, h : 0, i : 0, s : 0, u:0},k,hl,dM, regdate = /[\\\\\\/:_;.,\\t\\T\\s-]/;\r\n
\t\tif(date && date !== null && date !== undefined){\r\n
\t\t\tdate = $.trim(date);\r\n
\t\t\tdate = date.split(regdate);\r\n
\t\t\tif ($.jgrid.formatter.date.masks[format] !== undefined) {\r\n
\t\t\t\tformat = $.jgrid.formatter.date.masks[format];\r\n
\t\t\t}\r\n
\t\t\tformat = format.split(regdate);\r\n
\t\t\tvar dfmt  = $.jgrid.formatter.date.monthNames;\r\n
\t\t\tvar afmt  = $.jgrid.formatter.date.AmPm;\r\n
\t\t\tvar h12to24 = function(ampm, h){\r\n
\t\t\t\tif (ampm === 0){ if (h === 12) { h = 0;} }\r\n
\t\t\t\telse { if (h !== 12) { h += 12; } }\r\n
\t\t\t\treturn h;\r\n
\t\t\t};\r\n
\t\t\tfor(k=0,hl=format.length;k<hl;k++){\r\n
\t\t\t\tif(format[k] == \'M\') {\r\n
\t\t\t\t\tdM = $.inArray(date[k],dfmt);\r\n
\t\t\t\t\tif(dM !== -1 && dM < 12){\r\n
\t\t\t\t\t\tdate[k] = dM+1;\r\n
\t\t\t\t\t\ttsp.m = date[k];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(format[k] == \'F\') {\r\n
\t\t\t\t\tdM = $.inArray(date[k],dfmt);\r\n
\t\t\t\t\tif(dM !== -1 && dM > 11){\r\n
\t\t\t\t\t\tdate[k] = dM+1-12;\r\n
\t\t\t\t\t\ttsp.m = date[k];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(format[k] == \'a\') {\r\n
\t\t\t\t\tdM = $.inArray(date[k],afmt);\r\n
\t\t\t\t\tif(dM !== -1 && dM < 2 && date[k] == afmt[dM]){\r\n
\t\t\t\t\t\tdate[k] = dM;\r\n
\t\t\t\t\t\ttsp.h = h12to24(date[k], tsp.h);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(format[k] == \'A\') {\r\n
\t\t\t\t\tdM = $.inArray(date[k],afmt);\r\n
\t\t\t\t\tif(dM !== -1 && dM > 1 && date[k] == afmt[dM]){\r\n
\t\t\t\t\t\tdate[k] = dM-2;\r\n
\t\t\t\t\t\ttsp.h = h12to24(date[k], tsp.h);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif (format[k] === \'g\') {\r\n
\t\t\t\t\ttsp.h = parseInt(date[k], 10);\r\n
\t\t\t\t}\r\n
\t\t\t\tif(date[k] !== undefined) {\r\n
\t\t\t\t\ttsp[format[k].toLowerCase()] = parseInt(date[k],10);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\ttsp.m = parseInt(tsp.m,10)-1;\r\n
\t\t\tvar ty = tsp.y;\r\n
\t\t\tif (ty >= 70 && ty <= 99) {tsp.y = 1900+tsp.y;}\r\n
\t\t\telse if (ty >=0 && ty <=69) {tsp.y= 2000+tsp.y;}\r\n
\t\t\tif(tsp.j !== undefined) { tsp.d = tsp.j; }\r\n
\t\t\tif(tsp.n !== undefined) { tsp.m = parseInt(tsp.n,10)-1; }\r\n
\t\t}\r\n
\t\treturn new Date(tsp.y, tsp.m, tsp.d, tsp.h, tsp.i, tsp.s, tsp.u);\r\n
\t},\r\n
\tjqID : function(sid){\r\n
\t\treturn String(sid).replace(/[!"#$%&\'()*+,.\\/:;<=>?@\\[\\\\\\]\\^`{|}~]/g,"\\\\$&");\r\n
\t},\r\n
\tguid : 1,\r\n
\tuidPref: \'jqg\',\r\n
\trandId : function( prefix )\t{\r\n
\t\treturn (prefix? prefix: $.jgrid.uidPref) + ($.jgrid.guid++);\r\n
\t},\r\n
\tgetAccessor : function(obj, expr) {\r\n
\t\tvar ret,p,prm = [], i;\r\n
\t\tif( typeof expr === \'function\') { return expr(obj); }\r\n
\t\tret = obj[expr];\r\n
\t\tif(ret===undefined) {\r\n
\t\t\ttry {\r\n
\t\t\t\tif ( typeof expr === \'string\' ) {\r\n
\t\t\t\t\tprm = expr.split(\'.\');\r\n
\t\t\t\t}\r\n
\t\t\t\ti = prm.length;\r\n
\t\t\t\tif( i ) {\r\n
\t\t\t\t\tret = obj;\r\n
\t\t\t\t\twhile (ret && i--) {\r\n
\t\t\t\t\t\tp = prm.shift();\r\n
\t\t\t\t\t\tret = ret[p];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t} catch (e) {}\r\n
\t\t}\r\n
\t\treturn ret;\r\n
\t},\r\n
\tgetXmlData: function (obj, expr, returnObj) {\r\n
\t\tvar ret, m = typeof (expr) === \'string\' ? expr.match(/^(.*)\\[(\\w+)\\]$/) : null;\r\n
\t\tif (typeof (expr) === \'function\') { return expr(obj); }\r\n
\t\tif (m && m[2]) {\r\n
\t\t\t// m[2] is the attribute selector\r\n
\t\t\t// m[1] is an optional element selector\r\n
\t\t\t// examples: "[id]", "rows[page]"\r\n
\t\t\treturn m[1] ? $(m[1], obj).attr(m[2]) : $(obj).attr(m[2]);\r\n
\t\t} else {\r\n
\t\t\tret = $(expr, obj);\r\n
\t\t\tif (returnObj) { return ret; }\r\n
\t\t\t//$(expr, obj).filter(\':last\'); // we use \':last\' to be more compatible with old version of jqGrid\r\n
\t\t\treturn ret.length > 0 ? $(ret).text() : undefined;\r\n
\t\t}\r\n
\t},\r\n
\tcellWidth : function () {\r\n
\t\tvar $testDiv = $("<div class=\'ui-jqgrid\' style=\'left:10000px\'><table class=\'ui-jqgrid-btable\' style=\'width:5px;\'><tr class=\'jqgrow\'><td style=\'width:5px;\'></td></tr></table></div>"),\r\n
\t\ttestCell = $testDiv.appendTo("body")\r\n
\t\t\t.find("td")\r\n
\t\t\t.width();\r\n
\t\t$testDiv.remove();\r\n
\t\treturn testCell !== 5;\r\n
\t},\r\n
\tajaxOptions: {},\r\n
\tfrom : function(source){\r\n
\t\t// Original Author Hugo Bonacci\r\n
\t\t// License MIT http://jlinq.codeplex.com/license\r\n
\t\tvar QueryObject=function(d,q){\r\n
\t\tif(typeof(d)=="string"){\r\n
\t\t\td=$.data(d);\r\n
\t\t}\r\n
\t\tvar self=this,\r\n
\t\t_data=d,\r\n
\t\t_usecase=true,\r\n
\t\t_trim=false,\r\n
\t\t_query=q,\r\n
\t\t_stripNum = /[\\$,%]/g,\r\n
\t\t_lastCommand=null,\r\n
\t\t_lastField=null,\r\n
\t\t_orDepth=0,\r\n
\t\t_negate=false,\r\n
\t\t_queuedOperator="",\r\n
\t\t_sorting=[],\r\n
\t\t_useProperties=true;\r\n
\t\tif(typeof(d)=="object"&&d.push) {\r\n
\t\t\tif(d.length>0){\r\n
\t\t\t\tif(typeof(d[0])!="object"){\r\n
\t\t\t\t\t_useProperties=false;\r\n
\t\t\t\t}else{\r\n
\t\t\t\t\t_useProperties=true;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}else{\r\n
\t\t\tthrow "data provides is not an array";\r\n
\t\t}\r\n
\t\tthis._hasData=function(){\r\n
\t\t\treturn _data===null?false:_data.length===0?false:true;\r\n
\t\t};\r\n
\t\tthis._getStr=function(s){\r\n
\t\t\tvar phrase=[];\r\n
\t\t\tif(_trim){\r\n
\t\t\t\tphrase.push("jQuery.trim(");\r\n
\t\t\t}\r\n
\t\t\tphrase.push("String("+s+")");\r\n
\t\t\tif(_trim){\r\n
\t\t\t\tphrase.push(")");\r\n
\t\t\t}\r\n
\t\t\tif(!_usecase){\r\n
\t\t\t\tphrase.push(".toLowerCase()");\r\n
\t\t\t}\r\n
\t\t\treturn phrase.join("");\r\n
\t\t};\r\n
\t\tthis._strComp=function(val){\r\n
\t\t\tif(typeof(val)=="string"){\r\n
\t\t\t\treturn".toString()";\r\n
\t\t\t}else{\r\n
\t\t\t\treturn"";\r\n
\t\t\t}\r\n
\t\t};\r\n
\t\tthis._group=function(f,u){\r\n
\t\t\treturn({field:f.toString(),unique:u,items:[]});\r\n
\t\t};\r\n
\t\tthis._toStr=function(phrase){\r\n
\t\t\tif(_trim){\r\n
\t\t\t\tphrase=$.trim(phrase);\r\n
\t\t\t}\r\n
\t\t\tphrase=phrase.toString().replace(/\\\\/g,\'\\\\\\\\\').replace(/\\"/g,\'\\\\"\');\r\n
\t\t\treturn _usecase ? phrase : phrase.toLowerCase();\r\n
\t\t};\r\n
\t\tthis._funcLoop=function(func){\r\n
\t\t\tvar results=[];\r\n
\t\t\t$.each(_data,function(i,v){\r\n
\t\t\t\tresults.push(func(v));\r\n
\t\t\t});\r\n
\t\t\treturn results;\r\n
\t\t};\r\n
\t\tthis._append=function(s){\r\n
\t\t\tvar i;\r\n
\t\t\tif(_query===null){\r\n
\t\t\t\t_query="";\r\n
\t\t\t} else {\r\n
\t\t\t\t_query+=_queuedOperator === "" ? " && " :_queuedOperator;\r\n
\t\t\t}\r\n
\t\t\tfor (i=0;i<_orDepth;i++){\r\n
\t\t\t\t_query+="(";\r\n
\t\t\t}\r\n
\t\t\tif(_negate){\r\n
\t\t\t\t_query+="!";\r\n
\t\t\t}\r\n
\t\t\t_query+="("+s+")";\r\n
\t\t\t_negate=false;\r\n
\t\t\t_queuedOperator="";\r\n
\t\t\t_orDepth=0;\r\n
\t\t};\r\n
\t\tthis._setCommand=function(f,c){\r\n
\t\t\t_lastCommand=f;\r\n
\t\t\t_lastField=c;\r\n
\t\t};\r\n
\t\tthis._resetNegate=function(){\r\n
\t\t\t_negate=false;\r\n
\t\t};\r\n
\t\tthis._repeatCommand=function(f,v){\r\n
\t\t\tif(_lastCommand===null){\r\n
\t\t\t\treturn self;\r\n
\t\t\t}\r\n
\t\t\tif(f!==null&&v!==null){\r\n
\t\t\t\treturn _lastCommand(f,v);\r\n
\t\t\t}\r\n
\t\t\tif(_lastField===null){\r\n
\t\t\t\treturn _lastCommand(f);\r\n
\t\t\t}\r\n
\t\t\tif(!_useProperties){\r\n
\t\t\t\treturn _lastCommand(f);\r\n
\t\t\t}\r\n
\t\t\treturn _lastCommand(_lastField,f);\r\n
\t\t};\r\n
\t\tthis._equals=function(a,b){\r\n
\t\t\treturn(self._compare(a,b,1)===0);\r\n
\t\t};\r\n
\t\tthis._compare=function(a,b,d){\r\n
\t\t\tvar toString = Object.prototype.toString;\r\n
\t\t\tif( d === undefined) { d = 1; }\r\n
\t\t\tif(a===undefined) { a = null; }\r\n
\t\t\tif(b===undefined) { b = null; }\r\n
\t\t\tif(a===null && b===null){\r\n
\t\t\t\treturn 0;\r\n
\t\t\t}\r\n
\t\t\tif(a===null&&b!==null){\r\n
\t\t\t\treturn 1;\r\n
\t\t\t}\r\n
\t\t\tif(a!==null&&b===null){\r\n
\t\t\t\treturn -1;\r\n
\t\t\t}\r\n
\t\t\tif (toString.call(a) === \'[object Date]\' && toString.call(b) === \'[object Date]\') {\r\n
\t\t\t\tif (a < b) { return -d; }\r\n
\t\t\t\tif (a > b) { return d; }\r\n
\t\t\t\treturn 0;\r\n
\t\t\t}\r\n
\t\t\tif(!_usecase && typeof(a) !== "number" && typeof(b) !== "number" ) {\r\n
\t\t\t\ta=String(a).toLowerCase();\r\n
\t\t\t\tb=String(b).toLowerCase();\r\n
\t\t\t}\r\n
\t\t\tif(a<b){return -d;}\r\n
\t\t\tif(a>b){return d;}\r\n
\t\t\treturn 0;\r\n
\t\t};\r\n
\t\tthis._performSort=function(){\r\n
\t\t\tif(_sorting.length===0){return;}\r\n
\t\t\t_data=self._doSort(_data,0);\r\n
\t\t};\r\n
\t\tthis._doSort=function(d,q){\r\n
\t\t\tvar by=_sorting[q].by,\r\n
\t\t\tdir=_sorting[q].dir,\r\n
\t\t\ttype = _sorting[q].type,\r\n
\t\t\tdfmt = _sorting[q].datefmt;\r\n
\t\t\tif(q==_sorting.length-1){\r\n
\t\t\t\treturn self._getOrder(d, by, dir, type, dfmt);\r\n
\t\t\t}\r\n
\t\t\tq++;\r\n
\t\t\tvar values=self._getGroup(d,by,dir,type,dfmt);\r\n
\t\t\tvar results=[];\r\n
\t\t\tfor(var i=0;i<values.length;i++){\r\n
\t\t\t\tvar sorted=self._doSort(values[i].items,q);\r\n
\t\t\t\tfor(var j=0;j<sorted.length;j++){\r\n
\t\t\t\t\tresults.push(sorted[j]);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\treturn results;\r\n
\t\t};\r\n
\t\tthis._getOrder=function(data,by,dir,type, dfmt){\r\n
\t\t\tvar sortData=[],_sortData=[], newDir = dir=="a" ? 1 : -1, i,ab,j,\r\n
\t\t\tfindSortKey;\r\n
\r\n
\t\t\tif(type === undefined ) { type = "text"; }\r\n
\t\t\tif (type == \'float\' || type== \'number\' || type== \'currency\' || type== \'numeric\') {\r\n
\t\t\t\tfindSortKey = function($cell) {\r\n
\t\t\t\t\tvar key = parseFloat( String($cell).replace(_stripNum, \'\'));\r\n
\t\t\t\t\treturn isNaN(key) ? 0.00 : key;\r\n
\t\t\t\t};\r\n
\t\t\t} else if (type==\'int\' || type==\'integer\') {\r\n
\t\t\t\tfindSortKey = function($cell) {\r\n
\t\t\t\t\treturn $cell ? parseFloat(String($cell).replace(_stripNum, \'\')) : 0;\r\n
\t\t\t\t};\r\n
\t\t\t} else if(type == \'date\' || type == \'datetime\') {\r\n
\t\t\t\tfindSortKey = function($cell) {\r\n
\t\t\t\t\treturn $.jgrid.parseDate(dfmt,$cell).getTime();\r\n
\t\t\t\t};\r\n
\t\t\t} else if($.isFunction(type)) {\r\n
\t\t\t\tfindSortKey = type;\r\n
\t\t\t} else {\r\n
\t\t\t\tfindSortKey = function($cell) {\r\n
\t\t\t\t\tif(!$cell) {$cell ="";}\r\n
\t\t\t\t\treturn $.trim(String($cell).toUpperCase());\r\n
\t\t\t\t};\r\n
\t\t\t}\r\n
\t\t\t$.each(data,function(i,v){\r\n
\t\t\t\tab = by!=="" ? $.jgrid.getAccessor(v,by) : v;\r\n
\t\t\t\tif(ab === undefined) { ab = ""; }\r\n
\t\t\t\tab = findSortKey(ab, v);\r\n
\t\t\t\t_sortData.push({ \'vSort\': ab,\'index\':i});\r\n
\t\t\t});\r\n
\r\n
\t\t\t_sortData.sort(function(a,b){\r\n
\t\t\t\ta = a.vSort;\r\n
\t\t\t\tb = b.vSort;\r\n
\t\t\t\treturn self._compare(a,b,newDir);\r\n
\t\t\t});\r\n
\t\t\tj=0;\r\n
\t\t\tvar nrec= data.length;\r\n
\t\t\t// overhead, but we do not change the original data.\r\n
\t\t\twhile(j<nrec) {\r\n
\t\t\t\ti = _sortData[j].index;\r\n
\t\t\t\tsortData.push(data[i]);\r\n
\t\t\t\tj++;\r\n
\t\t\t}\r\n
\t\t\treturn sortData;\r\n
\t\t};\r\n
\t\tthis._getGroup=function(data,by,dir,type, dfmt){\r\n
\t\t\tvar results=[],\r\n
\t\t\tgroup=null,\r\n
\t\t\tlast=null, val;\r\n
\t\t\t$.each(self._getOrder(data,by,dir,type, dfmt),function(i,v){\r\n
\t\t\t\tval = $.jgrid.getAccessor(v, by);\r\n
\t\t\t\tif(val === undefined) { val = ""; }\r\n
\t\t\t\tif(!self._equals(last,val)){\r\n
\t\t\t\t\tlast=val;\r\n
\t\t\t\t\tif(group !== null){\r\n
\t\t\t\t\t\tresults.push(group);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tgroup=self._group(by,val);\r\n
\t\t\t\t}\r\n
\t\t\t\tgroup.items.push(v);\r\n
\t\t\t});\r\n
\t\t\tif(group !== null){\r\n
\t\t\t\tresults.push(group);\r\n
\t\t\t}\r\n
\t\t\treturn results;\r\n
\t\t};\r\n
\t\tthis.ignoreCase=function(){\r\n
\t\t\t_usecase=false;\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.useCase=function(){\r\n
\t\t\t_usecase=true;\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.trim=function(){\r\n
\t\t\t_trim=true;\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.noTrim=function(){\r\n
\t\t\t_trim=false;\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.execute=function(){\r\n
\t\t\tvar match=_query, results=[];\r\n
\t\t\tif(match === null){\r\n
\t\t\t\treturn self;\r\n
\t\t\t}\r\n
\t\t\t$.each(_data,function(){\r\n
\t\t\t\tif(eval(match)){results.push(this);}\r\n
\t\t\t});\r\n
\t\t\t_data=results;\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.data=function(){\r\n
\t\t\treturn _data;\r\n
\t\t};\r\n
\t\tthis.select=function(f){\r\n
\t\t\tself._performSort();\r\n
\t\t\tif(!self._hasData()){ return[]; }\r\n
\t\t\tself.execute();\r\n
\t\t\tif($.isFunction(f)){\r\n
\t\t\t\tvar results=[];\r\n
\t\t\t\t$.each(_data,function(i,v){\r\n
\t\t\t\t\tresults.push(f(v));\r\n
\t\t\t\t});\r\n
\t\t\t\treturn results;\r\n
\t\t\t}\r\n
\t\t\treturn _data;\r\n
\t\t};\r\n
\t\tthis.hasMatch=function(){\r\n
\t\t\tif(!self._hasData()) { return false; }\r\n
\t\t\tself.execute();\r\n
\t\t\treturn _data.length>0;\r\n
\t\t};\r\n
\t\tthis.andNot=function(f,v,x){\r\n
\t\t\t_negate=!_negate;\r\n
\t\t\treturn self.and(f,v,x);\r\n
\t\t};\r\n
\t\tthis.orNot=function(f,v,x){\r\n
\t\t\t_negate=!_negate;\r\n
\t\t\treturn self.or(f,v,x);\r\n
\t\t};\r\n
\t\tthis.not=function(f,v,x){\r\n
\t\t\treturn self.andNot(f,v,x);\r\n
\t\t};\r\n
\t\tthis.and=function(f,v,x){\r\n
\t\t\t_queuedOperator=" && ";\r\n
\t\t\tif(f===undefined){\r\n
\t\t\t\treturn self;\r\n
\t\t\t}\r\n
\t\t\treturn self._repeatCommand(f,v,x);\r\n
\t\t};\r\n
\t\tthis.or=function(f,v,x){\r\n
\t\t\t_queuedOperator=" || ";\r\n
\t\t\tif(f===undefined) { return self; }\r\n
\t\t\treturn self._repeatCommand(f,v,x);\r\n
\t\t};\r\n
\t\tthis.orBegin=function(){\r\n
\t\t\t_orDepth++;\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.orEnd=function(){\r\n
\t\t\tif (_query !== null){\r\n
\t\t\t\t_query+=")";\r\n
\t\t\t}\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.isNot=function(f){\r\n
\t\t\t_negate=!_negate;\r\n
\t\t\treturn self.is(f);\r\n
\t\t};\r\n
\t\tthis.is=function(f){\r\n
\t\t\tself._append(\'this.\'+f);\r\n
\t\t\tself._resetNegate();\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis._compareValues=function(func,f,v,how,t){\r\n
\t\t\tvar fld;\r\n
\t\t\tif(_useProperties){\r\n
\t\t\t\tfld=\'jQuery.jgrid.getAccessor(this,\\\'\'+f+\'\\\')\';\r\n
\t\t\t}else{\r\n
\t\t\t\tfld=\'this\';\r\n
\t\t\t}\r\n
\t\t\tif(v===undefined) { v = null; }\r\n
\t\t\t//var val=v===null?f:v,\r\n
\t\t\tvar val =v,\r\n
\t\t\tswst = t.stype === undefined ? "text" : t.stype;\r\n
\t\t\tif(v !== null) {\r\n
\t\t\tswitch(swst) {\r\n
\t\t\t\tcase \'int\':\r\n
\t\t\t\tcase \'integer\':\r\n
\t\t\t\t\tval = (isNaN(Number(val)) || val==="") ? \'0\' : val; // To be fixed with more inteligent code\r\n
\t\t\t\t\tfld = \'parseInt(\'+fld+\',10)\';\r\n
\t\t\t\t\tval = \'parseInt(\'+val+\',10)\';\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'float\':\r\n
\t\t\t\tcase \'number\':\r\n
\t\t\t\tcase \'numeric\':\r\n
\t\t\t\t\tval = String(val).replace(_stripNum, \'\');\r\n
\t\t\t\t\tval = (isNaN(Number(val)) || val==="") ? \'0\' : val; // To be fixed with more inteligent code\r\n
\t\t\t\t\tfld = \'parseFloat(\'+fld+\')\';\r\n
\t\t\t\t\tval = \'parseFloat(\'+val+\')\';\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'date\':\r\n
\t\t\t\tcase \'datetime\':\r\n
\t\t\t\t\tval = String($.jgrid.parseDate(t.newfmt || \'Y-m-d\',val).getTime());\r\n
\t\t\t\t\tfld = \'jQuery.jgrid.parseDate("\'+t.srcfmt+\'",\'+fld+\').getTime()\';\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tdefault :\r\n
\t\t\t\t\tfld=self._getStr(fld);\r\n
\t\t\t\t\tval=self._getStr(\'"\'+self._toStr(val)+\'"\');\r\n
\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tself._append(fld+\' \'+how+\' \'+val);\r\n
\t\t\tself._setCommand(func,f);\r\n
\t\t\tself._resetNegate();\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.equals=function(f,v,t){\r\n
\t\t\treturn self._compareValues(self.equals,f,v,"==",t);\r\n
\t\t};\r\n
\t\tthis.notEquals=function(f,v,t){\r\n
\t\t\treturn self._compareValues(self.equals,f,v,"!==",t);\r\n
\t\t};\r\n
\t\tthis.isNull = function(f,v,t){\r\n
\t\t\treturn self._compareValues(self.equals,f,null,"===",t);\r\n
\t\t};\r\n
\t\tthis.greater=function(f,v,t){\r\n
\t\t\treturn self._compareValues(self.greater,f,v,">",t);\r\n
\t\t};\r\n
\t\tthis.less=function(f,v,t){\r\n
\t\t\treturn self._compareValues(self.less,f,v,"<",t);\r\n
\t\t};\r\n
\t\tthis.greaterOrEquals=function(f,v,t){\r\n
\t\t\treturn self._compareValues(self.greaterOrEquals,f,v,">=",t);\r\n
\t\t};\r\n
\t\tthis.lessOrEquals=function(f,v,t){\r\n
\t\t\treturn self._compareValues(self.lessOrEquals,f,v,"<=",t);\r\n
\t\t};\r\n
\t\tthis.startsWith=function(f,v){\r\n
\t\t\tvar val = (v===undefined || v===null) ? f: v,\r\n
\t\t\tlength=_trim ? $.trim(val.toString()).length : val.toString().length;\r\n
\t\t\tif(_useProperties){\r\n
\t\t\t\tself._append(self._getStr(\'jQuery.jgrid.getAccessor(this,\\\'\'+f+\'\\\')\')+\'.substr(0,\'+length+\') == \'+self._getStr(\'"\'+self._toStr(v)+\'"\'));\r\n
\t\t\t}else{\r\n
\t\t\t\tlength=_trim?$.trim(v.toString()).length:v.toString().length;\r\n
\t\t\t\tself._append(self._getStr(\'this\')+\'.substr(0,\'+length+\') == \'+self._getStr(\'"\'+self._toStr(f)+\'"\'));\r\n
\t\t\t}\r\n
\t\t\tself._setCommand(self.startsWith,f);\r\n
\t\t\tself._resetNegate();\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.endsWith=function(f,v){\r\n
\t\t\tvar val = (v===undefined || v===null) ? f: v,\r\n
\t\t\tlength=_trim ? $.trim(val.toString()).length:val.toString().length;\r\n
\t\t\tif(_useProperties){\r\n
\t\t\t\tself._append(self._getStr(\'jQuery.jgrid.getAccessor(this,\\\'\'+f+\'\\\')\')+\'.substr(\'+self._getStr(\'jQuery.jgrid.getAccessor(this,\\\'\'+f+\'\\\')\')+\'.length-\'+length+\',\'+length+\') == "\'+self._toStr(v)+\'"\');\r\n
\t\t\t} else {\r\n
\t\t\t\tself._append(self._getStr(\'this\')+\'.substr(\'+self._getStr(\'this\')+\'.length-"\'+self._toStr(f)+\'".length,"\'+self._toStr(f)+\'".length) == "\'+self._toStr(f)+\'"\');\r\n
\t\t\t}\r\n
\t\t\tself._setCommand(self.endsWith,f);self._resetNegate();\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.contains=function(f,v){\r\n
\t\t\tif(_useProperties){\r\n
\t\t\t\tself._append(self._getStr(\'jQuery.jgrid.getAccessor(this,\\\'\'+f+\'\\\')\')+\'.indexOf("\'+self._toStr(v)+\'",0) > -1\');\r\n
\t\t\t}else{\r\n
\t\t\t\tself._append(self._getStr(\'this\')+\'.indexOf("\'+self._toStr(f)+\'",0) > -1\');\r\n
\t\t\t}\r\n
\t\t\tself._setCommand(self.contains,f);\r\n
\t\t\tself._resetNegate();\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\tthis.groupBy=function(by,dir,type, datefmt){\r\n
\t\t\tif(!self._hasData()){\r\n
\t\t\t\treturn null;\r\n
\t\t\t}\r\n
\t\t\treturn self._getGroup(_data,by,dir,type, datefmt);\r\n
\t\t};\r\n
\t\tthis.orderBy=function(by,dir,stype, dfmt){\r\n
\t\t\tdir =  dir === undefined || dir === null ? "a" :$.trim(dir.toString().toLowerCase());\r\n
\t\t\tif(stype === null || stype === undefined) { stype = "text"; }\r\n
\t\t\tif(dfmt === null || dfmt === undefined) { dfmt = "Y-m-d"; }\r\n
\t\t\tif(dir=="desc"||dir=="descending"){dir="d";}\r\n
\t\t\tif(dir=="asc"||dir=="ascending"){dir="a";}\r\n
\t\t\t_sorting.push({by:by,dir:dir,type:stype, datefmt: dfmt});\r\n
\t\t\treturn self;\r\n
\t\t};\r\n
\t\treturn self;\r\n
\t\t};\r\n
\treturn new QueryObject(source,null);\r\n
\t},\r\n
\textend : function(methods) {\r\n
\t\t$.extend($.fn.jqGrid,methods);\r\n
\t\tif (!this.no_legacy_api) {\r\n
\t\t\t$.fn.extend(methods);\r\n
\t\t}\r\n
\t}\r\n
});\r\n
\r\n
$.fn.jqGrid = function( pin ) {\r\n
\tif (typeof pin == \'string\') {\r\n
\t\t//var fn = $.fn.jqGrid[pin];\r\n
\t\tvar fn = $.jgrid.getAccessor($.fn.jqGrid,pin);\r\n
\t\tif (!fn) {\r\n
\t\t\tthrow ("jqGrid - No such method: " + pin);\r\n
\t\t}\r\n
\t\tvar args = $.makeArray(arguments).slice(1);\r\n
\t\treturn fn.apply(this,args);\r\n
\t}\r\n
\treturn this.each( function() {\r\n
\t\tif(this.grid) {return;}\r\n
\r\n
\t\tvar p = $.extend(true,{\r\n
\t\t\turl: "",\r\n
\t\t\theight: 150,\r\n
\t\t\tpage: 1,\r\n
\t\t\trowNum: 20,\r\n
\t\t\trowTotal : null,\r\n
\t\t\trecords: 0,\r\n
\t\t\tpager: "",\r\n
\t\t\tpgbuttons: true,\r\n
\t\t\tpginput: true,\r\n
\t\t\tcolModel: [],\r\n
\t\t\trowList: [],\r\n
\t\t\tcolNames: [],\r\n
\t\t\tsortorder: "asc",\r\n
\t\t\tsortname: "",\r\n
\t\t\tdatatype: "xml",\r\n
\t\t\tmtype: "GET",\r\n
\t\t\taltRows: false,\r\n
\t\t\tselarrrow: [],\r\n
\t\t\tsavedRow: [],\r\n
\t\t\tshrinkToFit: true,\r\n
\t\t\txmlReader: {},\r\n
\t\t\tjsonReader: {},\r\n
\t\t\tsubGrid: false,\r\n
\t\t\tsubGridModel :[],\r\n
\t\t\treccount: 0,\r\n
\t\t\tlastpage: 0,\r\n
\t\t\tlastsort: 0,\r\n
\t\t\tselrow: null,\r\n
\t\t\tbeforeSelectRow: null,\r\n
\t\t\tonSelectRow: null,\r\n
\t\t\tonSortCol: null,\r\n
\t\t\tondblClickRow: null,\r\n
\t\t\tonRightClickRow: null,\r\n
\t\t\tonPaging: null,\r\n
\t\t\tonSelectAll: null,\r\n
\t\t\tloadComplete: null,\r\n
\t\t\tgridComplete: null,\r\n
\t\t\tloadError: null,\r\n
\t\t\tloadBeforeSend: null,\r\n
\t\t\tafterInsertRow: null,\r\n
\t\t\tbeforeRequest: null,\r\n
\t\t\tbeforeProcessing : null,\r\n
\t\t\tonHeaderClick: null,\r\n
\t\t\tviewrecords: false,\r\n
\t\t\tloadonce: false,\r\n
\t\t\tmultiselect: false,\r\n
\t\t\tmultikey: false,\r\n
\t\t\tediturl: null,\r\n
\t\t\tsearch: false,\r\n
\t\t\tcaption: "",\r\n
\t\t\thidegrid: true,\r\n
\t\t\thiddengrid: false,\r\n
\t\t\tpostData: {},\r\n
\t\t\tuserData: {},\r\n
\t\t\ttreeGrid : false,\r\n
\t\t\ttreeGridModel : \'nested\',\r\n
\t\t\ttreeReader : {},\r\n
\t\t\ttreeANode : -1,\r\n
\t\t\tExpandColumn: null,\r\n
\t\t\ttree_root_level : 0,\r\n
\t\t\tprmNames: {page:"page",rows:"rows", sort: "sidx",order: "sord", search:"_search", nd:"nd", id:"id",oper:"oper",editoper:"edit",addoper:"add",deloper:"del", subgridid:"id", npage: null, totalrows:"totalrows"},\r\n
\t\t\tforceFit : false,\r\n
\t\t\tgridstate : "visible",\r\n
\t\t\tcellEdit: false,\r\n
\t\t\tcellsubmit: "remote",\r\n
\t\t\tnv:0,\r\n
\t\t\tloadui: "enable",\r\n
\t\t\ttoolbar: [false,""],\r\n
\t\t\tscroll: false,\r\n
\t\t\tmultiboxonly : false,\r\n
\t\t\tdeselectAfterSort : true,\r\n
\t\t\tscrollrows : false,\r\n
\t\t\tautowidth: false,\r\n
\t\t\tscrollOffset :18,\r\n
\t\t\tcellLayout: 5,\r\n
\t\t\tsubGridWidth: 20,\r\n
\t\t\tmultiselectWidth: 20,\r\n
\t\t\tgridview: false,\r\n
\t\t\trownumWidth: 25,\r\n
\t\t\trownumbers : false,\r\n
\t\t\tpagerpos: \'center\',\r\n
\t\t\trecordpos: \'right\',\r\n
\t\t\tfooterrow : false,\r\n
\t\t\tuserDataOnFooter : false,\r\n
\t\t\thoverrows : true,\r\n
\t\t\taltclass : \'ui-priority-secondary\',\r\n
\t\t\tviewsortcols : [false,\'vertical\',true],\r\n
\t\t\tresizeclass : \'\',\r\n
\t\t\tautoencode : false,\r\n
\t\t\tremapColumns : [],\r\n
\t\t\tajaxGridOptions :{},\r\n
\t\t\tdirection : "ltr",\r\n
\t\t\ttoppager: false,\r\n
\t\t\theadertitles: false,\r\n
\t\t\tscrollTimeout: 40,\r\n
\t\t\tdata : [],\r\n
\t\t\t_index : {},\r\n
\t\t\tgrouping : false,\r\n
\t\t\tgroupingView : {groupField:[],groupOrder:[], groupText:[],groupColumnShow:[],groupSummary:[], showSummaryOnHide: false, sortitems:[], sortnames:[], summary:[],summaryval:[], plusicon: \'ui-icon-circlesmall-plus\', minusicon: \'ui-icon-circlesmall-minus\'},\r\n
\t\t\tignoreCase : false,\r\n
\t\t\tcmTemplate : {},\r\n
\t\t\tidPrefix : ""\r\n
\t\t}, $.jgrid.defaults, pin || {});\r\n
\t\tvar ts= this, grid={\r\n
\t\t\theaders:[],\r\n
\t\t\tcols:[],\r\n
\t\t\tfooters: [],\r\n
\t\t\tdragStart: function(i,x,y) {\r\n
\t\t\t\tthis.resizing = { idx: i, startX: x.clientX, sOL : y[0]};\r\n
\t\t\t\tthis.hDiv.style.cursor = "col-resize";\r\n
\t\t\t\tthis.curGbox = $("#rs_m"+$.jgrid.jqID(p.id),"#gbox_"+$.jgrid.jqID(p.id));\r\n
\t\t\t\tthis.curGbox.css({display:"block",left:y[0],top:y[1],height:y[2]});\r\n
\t\t\t\t$(ts).triggerHandler("jqGridResizeStart", [x, i]);\r\n
\t\t\t\tif($.isFunction(p.resizeStart)) { p.resizeStart.call(this,x,i); }\r\n
\t\t\t\tdocument.onselectstart=function(){return false;};\r\n
\t\t\t},\r\n
\t\t\tdragMove: function(x) {\r\n
\t\t\t\tif(this.resizing) {\r\n
\t\t\t\t\tvar diff = x.clientX-this.resizing.startX,\r\n
\t\t\t\t\th = this.headers[this.resizing.idx],\r\n
\t\t\t\t\tnewWidth = p.direction === "ltr" ? h.width + diff : h.width - diff, hn, nWn;\r\n
\t\t\t\t\tif(newWidth > 33) {\r\n
\t\t\t\t\t\tthis.curGbox.css({left:this.resizing.sOL+diff});\r\n
\t\t\t\t\t\tif(p.forceFit===true ){\r\n
\t\t\t\t\t\t\thn = this.headers[this.resizing.idx+p.nv];\r\n
\t\t\t\t\t\t\tnWn = p.direction === "ltr" ? hn.width - diff : hn.width + diff;\r\n
\t\t\t\t\t\t\tif(nWn >33) {\r\n
\t\t\t\t\t\t\t\th.newWidth = newWidth;\r\n
\t\t\t\t\t\t\t\thn.newWidth = nWn;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tthis.newWidth = p.direction === "ltr" ? p.tblwidth+diff : p.tblwidth-diff;\r\n
\t\t\t\t\t\t\th.newWidth = newWidth;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t},\r\n
\t\t\tdragEnd: function() {\r\n
\t\t\t\tthis.hDiv.style.cursor = "default";\r\n
\t\t\t\tif(this.resizing) {\r\n
\t\t\t\t\tvar idx = this.resizing.idx,\r\n
\t\t\t\t\tnw = this.headers[idx].newWidth || this.headers[idx].width;\r\n
\t\t\t\t\tnw = parseInt(nw,10);\r\n
\t\t\t\t\tthis.resizing = false;\r\n
\t\t\t\t\t$("#rs_m"+$.jgrid.jqID(p.id)).css("display","none");\r\n
\t\t\t\t\tp.colModel[idx].width = nw;\r\n
\t\t\t\t\tthis.headers[idx].width = nw;\r\n
\t\t\t\t\tthis.headers[idx].el.style.width = nw + "px";\r\n
\t\t\t\t\tthis.cols[idx].style.width = nw+"px";\r\n
\t\t\t\t\tif(this.footers.length>0) {this.footers[idx].style.width = nw+"px";}\r\n
\t\t\t\t\tif(p.forceFit===true){\r\n
\t\t\t\t\t\tnw = this.headers[idx+p.nv].newWidth || this.headers[idx+p.nv].width;\r\n
\t\t\t\t\t\tthis.headers[idx+p.nv].width = nw;\r\n
\t\t\t\t\t\tthis.headers[idx+p.nv].el.style.width = nw + "px";\r\n
\t\t\t\t\t\tthis.cols[idx+p.nv].style.width = nw+"px";\r\n
\t\t\t\t\t\tif(this.footers.length>0) {this.footers[idx+p.nv].style.width = nw+"px";}\r\n
\t\t\t\t\t\tp.colModel[idx+p.nv].width = nw;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tp.tblwidth = this.newWidth || p.tblwidth;\r\n
\t\t\t\t\t\t$(\'table:first\',this.bDiv).css("width",p.tblwidth+"px");\r\n
\t\t\t\t\t\t$(\'table:first\',this.hDiv).css("width",p.tblwidth+"px");\r\n
\t\t\t\t\t\tthis.hDiv.scrollLeft = this.bDiv.scrollLeft;\r\n
\t\t\t\t\t\tif(p.footerrow) {\r\n
\t\t\t\t\t\t\t$(\'table:first\',this.sDiv).css("width",p.tblwidth+"px");\r\n
\t\t\t\t\t\t\tthis.sDiv.scrollLeft = this.bDiv.scrollLeft;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridResizeStop", [nw, idx]);\r\n
\t\t\t\t\tif($.isFunction(p.resizeStop)) { p.resizeStop.call(this,nw,idx); }\r\n
\t\t\t\t}\r\n
\t\t\t\tthis.curGbox = null;\r\n
\t\t\t\tdocument.onselectstart=function(){return true;};\r\n
\t\t\t},\r\n
\t\t\tpopulateVisible: function() {\r\n
\t\t\t\tif (grid.timer) { clearTimeout(grid.timer); }\r\n
\t\t\t\tgrid.timer = null;\r\n
\t\t\t\tvar dh = $(grid.bDiv).height();\r\n
\t\t\t\tif (!dh) { return; }\r\n
\t\t\t\tvar table = $("table:first", grid.bDiv);\r\n
\t\t\t\tvar rows, rh;\r\n
\t\t\t\tif(table[0].rows.length) {\r\n
\t\t\t\t\ttry {\r\n
\t\t\t\t\t\trows = table[0].rows[1];\r\n
\t\t\t\t\t\trh = rows ? $(rows).outerHeight() || grid.prevRowHeight : grid.prevRowHeight;\r\n
\t\t\t\t\t} catch (pv) {\r\n
\t\t\t\t\t\trh = grid.prevRowHeight;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif (!rh) { return; }\r\n
\t\t\t\tgrid.prevRowHeight = rh;\r\n
\t\t\t\tvar rn = p.rowNum;\r\n
\t\t\t\tvar scrollTop = grid.scrollTop = grid.bDiv.scrollTop;\r\n
\t\t\t\tvar ttop = Math.round(table.position().top) - scrollTop;\r\n
\t\t\t\tvar tbot = ttop + table.height();\r\n
\t\t\t\tvar div = rh * rn;\r\n
\t\t\t\tvar page, npage, empty;\r\n
\t\t\t\tif ( tbot < dh && ttop <= 0 &&\r\n
\t\t\t\t\t(p.lastpage===undefined||parseInt((tbot + scrollTop + div - 1) / div,10) <= p.lastpage))\r\n
\t\t\t\t{\r\n
\t\t\t\t\tnpage = parseInt((dh - tbot + div - 1) / div,10);\r\n
\t\t\t\t\tif (tbot >= 0 || npage < 2 || p.scroll === true) {\r\n
\t\t\t\t\t\tpage = Math.round((tbot + scrollTop) / div) + 1;\r\n
\t\t\t\t\t\tttop = -1;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tttop = 1;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif (ttop > 0) {\r\n
\t\t\t\t\tpage = parseInt(scrollTop / div,10) + 1;\r\n
\t\t\t\t\tnpage = parseInt((scrollTop + dh) / div,10) + 2 - page;\r\n
\t\t\t\t\tempty = true;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (npage) {\r\n
\t\t\t\t\tif (p.lastpage && page > p.lastpage || p.lastpage==1 || (page === p.page && page===p.lastpage) ) {\r\n
\t\t\t\t\t\treturn;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (grid.hDiv.loading) {\r\n
\t\t\t\t\t\tgrid.timer = setTimeout(grid.populateVisible, p.scrollTimeout);\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tp.page = page;\r\n
\t\t\t\t\t\tif (empty) {\r\n
\t\t\t\t\t\t\tgrid.selectionPreserver(table[0]);\r\n
\t\t\t\t\t\t\tgrid.emptyRows.call(table[0], false, false);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tgrid.populate(npage);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t},\r\n
\t\t\tscrollGrid: function( e ) {\r\n
\t\t\t\tif(p.scroll) {\r\n
\t\t\t\t\tvar scrollTop = grid.bDiv.scrollTop;\r\n
\t\t\t\t\tif(grid.scrollTop === undefined) { grid.scrollTop = 0; }\r\n
\t\t\t\t\tif (scrollTop != grid.scrollTop) {\r\n
\t\t\t\t\t\tgrid.scrollTop = scrollTop;\r\n
\t\t\t\t\t\tif (grid.timer) { clearTimeout(grid.timer); }\r\n
\t\t\t\t\t\tgrid.timer = setTimeout(grid.populateVisible, p.scrollTimeout);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tgrid.hDiv.scrollLeft = grid.bDiv.scrollLeft;\r\n
\t\t\t\tif(p.footerrow) {\r\n
\t\t\t\t\tgrid.sDiv.scrollLeft = grid.bDiv.scrollLeft;\r\n
\t\t\t\t}\r\n
\t\t\t\tif( e ) { e.stopPropagation(); }\r\n
\t\t\t},\r\n
\t\t\tselectionPreserver : function(ts) {\r\n
\t\t\t\tvar p = ts.p,\r\n
\t\t\t\tsr = p.selrow, sra = p.selarrrow ? $.makeArray(p.selarrrow) : null,\r\n
\t\t\t\tleft = ts.grid.bDiv.scrollLeft,\r\n
\t\t\t\trestoreSelection = function() {\r\n
\t\t\t\t\tvar i;\r\n
\t\t\t\t\tp.selrow = null;\r\n
\t\t\t\t\tp.selarrrow = [];\r\n
\t\t\t\t\tif(p.multiselect && sra && sra.length>0) {\r\n
\t\t\t\t\t\tfor(i=0;i<sra.length;i++){\r\n
\t\t\t\t\t\t\tif (sra[i] != sr) {\r\n
\t\t\t\t\t\t\t\t$(ts).jqGrid("setSelection",sra[i],false, null);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (sr) {\r\n
\t\t\t\t\t\t$(ts).jqGrid("setSelection",sr,false,null);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tts.grid.bDiv.scrollLeft = left;\r\n
\t\t\t\t\t$(ts).unbind(\'.selectionPreserver\', restoreSelection);\r\n
\t\t\t\t};\r\n
\t\t\t\t$(ts).bind(\'jqGridGridComplete.selectionPreserver\', restoreSelection);\t\t\t\t\r\n
\t\t\t}\r\n
\t\t};\r\n
\t\tif(this.tagName.toUpperCase()!=\'TABLE\') {\r\n
\t\t\talert("Element is not a table");\r\n
\t\t\treturn;\r\n
\t\t}\r\n
\t\tif(document.documentMode !== undefined ) { // IE only\r\n
\t\t\tif(document.documentMode <= 5) {\r\n
\t\t\t\talert("Grid can not be used in this (\'quirks\') mode!");\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\t$(this).empty().attr("tabindex","1");\r\n
\t\tthis.p = p ;\r\n
\t\tthis.p.useProp = !!$.fn.prop;\r\n
\t\tvar i, dir;\r\n
\t\tif(this.p.colNames.length === 0) {\r\n
\t\t\tfor (i=0;i<this.p.colModel.length;i++){\r\n
\t\t\t\tthis.p.colNames[i] = this.p.colModel[i].label || this.p.colModel[i].name;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tif( this.p.colNames.length !== this.p.colModel.length ) {\r\n
\t\t\talert($.jgrid.errors.model);\r\n
\t\t\treturn;\r\n
\t\t}\r\n
\t\tvar gv = $("<div class=\'ui-jqgrid-view\'></div>"), ii,\r\n
\t\tisMSIE = $.browser.msie ? true:false;\r\n
\t\tts.p.direction = $.trim(ts.p.direction.toLowerCase());\r\n
\t\tif($.inArray(ts.p.direction,["ltr","rtl"]) == -1) { ts.p.direction = "ltr"; }\r\n
\t\tdir = ts.p.direction;\r\n
\r\n
\t\t$(gv).insertBefore(this);\r\n
\t\t$(this).appendTo(gv).removeClass("scroll");\r\n
\t\tvar eg = $("<div class=\'ui-jqgrid ui-widget ui-widget-content ui-corner-all\'></div>");\r\n
\t\t$(eg).insertBefore(gv).attr({"id" : "gbox_"+this.id,"dir":dir});\r\n
\t\t$(gv).appendTo(eg).attr("id","gview_"+this.id);\r\n
\t\tif (isMSIE && $.browser.version <= 6) {\r\n
\t\t\tii = \'<iframe style="display:block;position:absolute;z-index:-1;filter:Alpha(Opacity=\\\'0\\\');" src="javascript:false;"></iframe>\';\r\n
\t\t} else { ii="";}\r\n
\t\t$("<div class=\'ui-widget-overlay jqgrid-overlay\' id=\'lui_"+this.id+"\'></div>").append(ii).insertBefore(gv);\r\n
\t\t$("<div class=\'loading ui-state-default ui-state-active\' id=\'load_"+this.id+"\'>"+this.p.loadtext+"</div>").insertBefore(gv);\r\n
\t\t$(this).attr({cellspacing:"0",cellpadding:"0",border:"0","role":"grid","aria-multiselectable":!!this.p.multiselect,"aria-labelledby":"gbox_"+this.id});\r\n
\t\tvar sortkeys = ["shiftKey","altKey","ctrlKey"],\r\n
\t\tintNum = function(val,defval) {\r\n
\t\t\tval = parseInt(val,10);\r\n
\t\t\tif (isNaN(val)) { return defval ? defval : 0;}\r\n
\t\t\telse {return val;}\r\n
\t\t},\r\n
\t\tformatCol = function (pos, rowInd, tv, rawObject, rowId, rdata){\r\n
\t\t\tvar cm = ts.p.colModel[pos],\r\n
\t\t\tral = cm.align, result="style=\\"", clas = cm.classes, nm = cm.name, celp, acp=[];\r\n
\t\t\tif(ral) { result += "text-align:"+ral+";"; }\r\n
\t\t\tif(cm.hidden===true) { result += "display:none;"; }\r\n
\t\t\tif(rowInd===0) {\r\n
\t\t\t\tresult += "width: "+grid.headers[pos].width+"px;";\r\n
\t\t\t} else if (cm.cellattr && $.isFunction(cm.cellattr))\r\n
\t\t\t{\r\n
\t\t\t\tcelp = cm.cellattr.call(ts, rowId, tv, rawObject, cm, rdata);\r\n
\t\t\t\tif(celp && typeof(celp) === "string") {\r\n
\t\t\t\t\tcelp = celp.replace(/style/i,\'style\').replace(/title/i,\'title\');\r\n
\t\t\t\t\tif(celp.indexOf(\'title\') > -1) { cm.title=false;}\r\n
\t\t\t\t\tif(celp.indexOf(\'class\') > -1) { clas = undefined;}\r\n
\t\t\t\t\tacp = celp.split("style");\r\n
\t\t\t\t\tif(acp.length === 2 ) {\r\n
\t\t\t\t\t\tacp[1] =  $.trim(acp[1].replace("=",""));\r\n
\t\t\t\t\t\tif(acp[1].indexOf("\'") === 0 || acp[1].indexOf(\'"\') === 0) {\r\n
\t\t\t\t\t\t\tacp[1] = acp[1].substring(1);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tresult += acp[1].replace(/\'/gi,\'"\');\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tresult += "\\"";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(!acp.length) { acp[0] = ""; result += "\\"";}\r\n
\t\t\tresult += (clas !== undefined ? (" class=\\""+clas+"\\"") :"") + ((cm.title && tv) ? (" title=\\""+$.jgrid.stripHtml(tv)+"\\"") :"");\r\n
\t\t\tresult += " aria-describedby=\\""+ts.p.id+"_"+nm+"\\"";\r\n
\t\t\treturn result + acp[0];\r\n
\t\t},\r\n
\t\tcellVal =  function (val) {\r\n
\t\t\treturn val === undefined || val === null || val === "" ? "&#160;" : (ts.p.autoencode ? $.jgrid.htmlEncode(val) : val+"");\r\n
\t\t},\r\n
\t\tformatter = function (rowId, cellval , colpos, rwdat, _act){\r\n
\t\t\tvar cm = ts.p.colModel[colpos],v;\r\n
\t\t\tif(typeof cm.formatter !== \'undefined\') {\r\n
\t\t\t\tvar opts= {rowId: rowId, colModel:cm, gid:ts.p.id, pos:colpos };\r\n
\t\t\t\tif($.isFunction( cm.formatter ) ) {\r\n
\t\t\t\t\tv = cm.formatter.call(ts,cellval,opts,rwdat,_act);\r\n
\t\t\t\t} else if($.fmatter){\r\n
\t\t\t\t\tv = $.fn.fmatter.call(ts,cm.formatter,cellval,opts,rwdat,_act);\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tv = cellVal(cellval);\r\n
\t\t\t\t}\r\n
\t\t\t} else {\r\n
\t\t\t\tv = cellVal(cellval);\r\n
\t\t\t}\r\n
\t\t\treturn v;\r\n
\t\t},\r\n
\t\taddCell = function(rowId,cell,pos,irow, srvr) {\r\n
\t\t\tvar v,prp;\r\n
\t\t\tv = formatter(rowId,cell,pos,srvr,\'add\');\r\n
\t\t\tprp = formatCol( pos,irow, v, srvr, rowId, true);\r\n
\t\t\treturn "<td role=\\"gridcell\\" "+prp+">"+v+"</td>";\r\n
\t\t},\r\n
\t\taddMulti = function(rowid,pos,irow,checked){\r\n
\t\t\tvar\tv = "<input role=\\"checkbox\\" type=\\"checkbox\\""+" id=\\"jqg_"+ts.p.id+"_"+rowid+"\\" class=\\"cbox\\" name=\\"jqg_"+ts.p.id+"_"+rowid+"\\"" + ((checked) ? "checked=\\"checked\\"" : "")+"/>",\r\n
\t\t\tprp = formatCol( pos,irow,\'\',null, rowid, true);\r\n
\t\t\treturn "<td role=\\"gridcell\\" "+prp+">"+v+"</td>";\r\n
\t\t},\r\n
\t\taddRowNum = function (pos,irow,pG,rN) {\r\n
\t\t\tvar v =  (parseInt(pG,10)-1)*parseInt(rN,10)+1+irow,\r\n
\t\t\tprp = formatCol( pos,irow,v, null, irow, true);\r\n
\t\t\treturn "<td role=\\"gridcell\\" class=\\"ui-state-default jqgrid-rownum\\" "+prp+">"+v+"</td>";\r\n
\t\t},\r\n
\t\treader = function (datatype) {\r\n
\t\t\tvar field, f=[], j=0, i;\r\n
\t\t\tfor(i =0; i<ts.p.colModel.length; i++){\r\n
\t\t\t\tfield = ts.p.colModel[i];\r\n
\t\t\t\tif (field.name !== \'cb\' && field.name !==\'subgrid\' && field.name !==\'rn\') {\r\n
\t\t\t\t\tf[j]= datatype == "local" ?\r\n
\t\t\t\t\tfield.name :\r\n
\t\t\t\t\t( (datatype=="xml" || datatype === "xmlstring") ? field.xmlmap || field.name : field.jsonmap || field.name );\r\n
\t\t\t\t\tj++;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\treturn f;\r\n
\t\t},\r\n
\t\torderedCols = function (offset) {\r\n
\t\t\tvar order = ts.p.remapColumns;\r\n
\t\t\tif (!order || !order.length) {\r\n
\t\t\t\torder = $.map(ts.p.colModel, function(v,i) { return i; });\r\n
\t\t\t}\r\n
\t\t\tif (offset) {\r\n
\t\t\t\torder = $.map(order, function(v) { return v<offset?null:v-offset; });\r\n
\t\t\t}\r\n
\t\t\treturn order;\r\n
\t\t},\r\n
\t\temptyRows = function (scroll, locdata) {\r\n
\t\t\tvar firstrow;\r\n
\t\t\tif (this.p.deepempty) {\r\n
\t\t\t\t$(this.rows).slice(1).remove();\r\n
\t\t\t} else {\r\n
\t\t\t\tfirstrow = this.rows.length > 0 ? this.rows[0] : null;\r\n
\t\t\t\t$(this.firstChild).empty().append(firstrow);\r\n
\t\t\t}\r\n
\t\t\tif (scroll && this.p.scroll) {\r\n
\t\t\t\t$(this.grid.bDiv.firstChild).css({height: "auto"});\r\n
\t\t\t\t$(this.grid.bDiv.firstChild.firstChild).css({height: 0, display: "none"});\r\n
\t\t\t\tif (this.grid.bDiv.scrollTop !== 0) {\r\n
\t\t\t\t\tthis.grid.bDiv.scrollTop = 0;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(locdata === true && this.p.treeGrid) {\r\n
\t\t\t\tthis.p.data = []; this.p._index = {};\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\trefreshIndex = function() {\r\n
\t\t\tvar datalen = ts.p.data.length, idname, i, val,\r\n
\t\t\tni = ts.p.rownumbers===true ? 1 :0,\r\n
\t\t\tgi = ts.p.multiselect ===true ? 1 :0,\r\n
\t\t\tsi = ts.p.subGrid===true ? 1 :0;\r\n
\r\n
\t\t\tif(ts.p.keyIndex === false || ts.p.loadonce === true) {\r\n
\t\t\t\tidname = ts.p.localReader.id;\r\n
\t\t\t} else {\r\n
\t\t\t\tidname = ts.p.colModel[ts.p.keyIndex+gi+si+ni].name;\r\n
\t\t\t}\r\n
\t\t\tfor(i =0;i < datalen; i++) {\r\n
\t\t\t\tval = $.jgrid.getAccessor(ts.p.data[i],idname);\r\n
\t\t\t\tts.p._index[val] = i;\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\tconstructTr = function(id, hide, altClass, rd, cur, selected) {\r\n
\t\t\tvar tabindex = \'-1\', restAttr = \'\', attrName, style = hide ? \'display:none;\' : \'\',\r\n
\t\t\t\tclasses = \'ui-widget-content jqgrow ui-row-\' + ts.p.direction + altClass + ((selected) ? \' ui-state-highlight\' : \'\'),\r\n
\t\t\t\trowAttrObj = $.isFunction(ts.p.rowattr) ? ts.p.rowattr.call(ts, rd, cur) : {};\r\n
\t\t\tif(!$.isEmptyObject( rowAttrObj )) {\r\n
\t\t\t\tif (rowAttrObj.hasOwnProperty("id")) {\r\n
\t\t\t\t\tid = rowAttrObj.id;\r\n
\t\t\t\t\tdelete rowAttrObj.id;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (rowAttrObj.hasOwnProperty("tabindex")) {\r\n
\t\t\t\t\ttabindex = rowAttrObj.tabindex;\r\n
\t\t\t\t\tdelete rowAttrObj.tabindex;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (rowAttrObj.hasOwnProperty("style")) {\r\n
\t\t\t\t\tstyle += rowAttrObj.style;\r\n
\t\t\t\t\tdelete rowAttrObj.style;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (rowAttrObj.hasOwnProperty("class")) {\r\n
\t\t\t\t\tclasses += \' \' + rowAttrObj[\'class\'];\r\n
\t\t\t\t\tdelete rowAttrObj[\'class\'];\r\n
\t\t\t\t}\r\n
\t\t\t\t// dot\'t allow to change role attribute\r\n
\t\t\t\ttry { delete rowAttrObj.role; } catch(ra){}\r\n
\t\t\t\tfor (attrName in rowAttrObj) {\r\n
\t\t\t\t\tif (rowAttrObj.hasOwnProperty(attrName)) {\r\n
\t\t\t\t\t\trestAttr += \' \' + attrName + \'=\' + rowAttrObj[attrName];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\treturn \'<tr role="row" id="\' + id + \'" tabindex="\' + tabindex + \'" class="\' + classes + \'"\' +\r\n
\t\t\t\t(style === \'\' ? \'\' : \' style="\' + style + \'"\') + restAttr + \'>\';\r\n
\t\t},\r\n
\t\taddXmlData = function (xml,t, rcnt, more, adjust) {\r\n
\t\t\tvar startReq = new Date(),\r\n
\t\t\tlocdata = (ts.p.datatype != "local" && ts.p.loadonce) || ts.p.datatype == "xmlstring",\r\n
\t\t\txmlid = "_id_", xmlRd = ts.p.xmlReader,\r\n
\t\t\tfrd = ts.p.datatype == "local" ? "local" : "xml";\r\n
\t\t\tif(locdata) {\r\n
\t\t\t\tts.p.data = [];\r\n
\t\t\t\tts.p._index = {};\r\n
\t\t\t\tts.p.localReader.id = xmlid;\r\n
\t\t\t}\r\n
\t\t\tts.p.reccount = 0;\r\n
\t\t\tif($.isXMLDoc(xml)) {\r\n
\t\t\t\tif(ts.p.treeANode===-1 && !ts.p.scroll) {\r\n
\t\t\t\t\temptyRows.call(ts, false, true);\r\n
\t\t\t\t\trcnt=1;\r\n
\t\t\t\t} else { rcnt = rcnt > 1 ? rcnt :1; }\r\n
\t\t\t} else { return; }\r\n
\t\t\tvar i,fpos,ir=0,v,gi=ts.p.multiselect===true?1:0,si=ts.p.subGrid===true?1:0,ni=ts.p.rownumbers===true?1:0,idn, getId,f=[],F,rd ={}, xmlr,rid, rowData=[], cn=(ts.p.altRows === true) ? " "+ts.p.altclass:"",cn1;\r\n
\t\t\tif(!xmlRd.repeatitems) {f = reader(frd);}\r\n
\t\t\tif( ts.p.keyIndex===false) {\r\n
\t\t\t\tidn = $.isFunction( xmlRd.id ) ?  xmlRd.id.call(ts, xml) : xmlRd.id;\r\n
\t\t\t} else {\r\n
\t\t\t\tidn = ts.p.keyIndex;\r\n
\t\t\t}\r\n
\t\t\tif(f.length>0 && !isNaN(idn)) {\r\n
\t\t\t\tif (ts.p.remapColumns && ts.p.remapColumns.length) {\r\n
\t\t\t\t\tidn = $.inArray(idn, ts.p.remapColumns);\r\n
\t\t\t\t}\r\n
\t\t\t\tidn=f[idn];\r\n
\t\t\t}\r\n
\t\t\tif( (idn+"").indexOf("[") === -1 ) {\r\n
\t\t\t\tif (f.length) {\r\n
\t\t\t\t\tgetId = function( trow, k) {return $(idn,trow).text() || k;};\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tgetId = function( trow, k) {return $(xmlRd.cell,trow).eq(idn).text() || k;};\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\telse {\r\n
\t\t\t\tgetId = function( trow, k) {return trow.getAttribute(idn.replace(/[\\[\\]]/g,"")) || k;};\r\n
\t\t\t}\r\n
\t\t\tts.p.userData = {};\r\n
\t\t\tts.p.page = $.jgrid.getXmlData( xml,xmlRd.page ) || ts.p.page || 0;\r\n
\t\t\tts.p.lastpage = $.jgrid.getXmlData( xml,xmlRd.total );\r\n
\t\t\tif(ts.p.lastpage===undefined) { ts.p.lastpage=1; }\r\n
\t\t\tts.p.records = $.jgrid.getXmlData( xml,xmlRd.records ) || 0;\r\n
\t\t\tif($.isFunction(xmlRd.userdata)) {\r\n
\t\t\t\tts.p.userData = xmlRd.userdata.call(ts, xml) || {};\r\n
\t\t\t} else {\r\n
\t\t\t\t$.jgrid.getXmlData(xml, xmlRd.userdata, true).each(function() {ts.p.userData[this.getAttribute("name")]= $(this).text();});\r\n
\t\t\t}\r\n
\t\t\tvar gxml = $.jgrid.getXmlData( xml, xmlRd.root, true);\r\n
\t\t\tgxml = $.jgrid.getXmlData( gxml, xmlRd.row, true);\r\n
\t\t\tif (!gxml) { gxml = []; }\r\n
\t\t\tvar gl = gxml.length, j=0, grpdata=[], rn = parseInt(ts.p.rowNum,10);\r\n
\t\t\tif (gl > 0 &&  ts.p.page <= 0) { ts.p.page = 1; }\r\n
\t\t\tif(gxml && gl){\r\n
\t\t\tvar br=ts.p.scroll?$.jgrid.randId():1,altr;\r\n
\t\t\tif (adjust) { rn *= adjust+1; }\r\n
\t\t\tvar afterInsRow = $.isFunction(ts.p.afterInsertRow), hiderow=ts.p.grouping && ts.p.groupingView.groupCollapse === true;\r\n
\t\t\twhile (j<gl) {\r\n
\t\t\t\txmlr = gxml[j];\r\n
\t\t\t\trid = getId(xmlr,br+j);\r\n
\t\t\t\trid  = ts.p.idPrefix + rid;\r\n
\t\t\t\taltr = rcnt === 0 ? 0 : rcnt+1;\r\n
\t\t\t\tcn1 = (altr+j)%2 == 1 ? cn : \'\';\r\n
\t\t\t\tvar iStartTrTag = rowData.length;\r\n
\t\t\t\trowData.push("");\r\n
\t\t\t\tif( ni ) {\r\n
\t\t\t\t\trowData.push( addRowNum(0,j,ts.p.page,ts.p.rowNum) );\r\n
\t\t\t\t}\r\n
\t\t\t\tif( gi ) {\r\n
\t\t\t\t\trowData.push( addMulti(rid,ni,j, false) );\r\n
\t\t\t\t}\r\n
\t\t\t\tif( si ) {\r\n
\t\t\t\t\trowData.push( $(ts).jqGrid("addSubGridCell",gi+ni,j+rcnt) );\r\n
\t\t\t\t}\r\n
\t\t\t\tif(xmlRd.repeatitems){\r\n
\t\t\t\t\tif (!F) { F=orderedCols(gi+si+ni); }\r\n
\t\t\t\t\tvar cells = $.jgrid.getXmlData( xmlr, xmlRd.cell, true);\r\n
\t\t\t\t\t$.each(F, function (k) {\r\n
\t\t\t\t\t\tvar cell = cells[this];\r\n
\t\t\t\t\t\tif (!cell) { return false; }\r\n
\t\t\t\t\t\tv = cell.textContent || cell.text;\r\n
\t\t\t\t\t\trd[ts.p.colModel[k+gi+si+ni].name] = v;\r\n
\t\t\t\t\t\trowData.push( addCell(rid,v,k+gi+si+ni,j+rcnt,xmlr) );\r\n
\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tfor(i = 0; i < f.length;i++) {\r\n
\t\t\t\t\t\tv = $.jgrid.getXmlData( xmlr, f[i]);\r\n
\t\t\t\t\t\trd[ts.p.colModel[i+gi+si+ni].name] = v;\r\n
\t\t\t\t\t\trowData.push( addCell(rid, v, i+gi+si+ni, j+rcnt, xmlr) );\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\trowData[iStartTrTag] = constructTr(rid, hiderow, cn1, rd, xmlr, false);\r\n
\t\t\t\trowData.push("</tr>");\r\n
\t\t\t\tif(ts.p.grouping) {\r\n
\t\t\t\t\tgrpdata = $(ts).jqGrid(\'groupingPrepare\',rowData, grpdata, rd, j);\r\n
\t\t\t\t\trowData = [];\r\n
\t\t\t\t}\r\n
\t\t\t\tif(locdata || ts.p.treeGrid === true) {\r\n
\t\t\t\t\trd[xmlid] = rid;\r\n
\t\t\t\t\tts.p.data.push(rd);\r\n
\t\t\t\t\tts.p._index[rid] = ts.p.data.length-1;\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ts.p.gridview === false ) {\r\n
\t\t\t\t\t$("tbody:first",t).append(rowData.join(\'\'));\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridAfterInsertRow", [rid, rd, xmlr]);\r\n
\t\t\t\t\tif(afterInsRow) {ts.p.afterInsertRow.call(ts,rid,rd,xmlr);}\r\n
\t\t\t\t\trowData=[];\r\n
\t\t\t\t}\r\n
\t\t\t\trd={};\r\n
\t\t\t\tir++;\r\n
\t\t\t\tj++;\r\n
\t\t\t\tif(ir==rn) {break;}\r\n
\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.gridview === true) {\r\n
\t\t\t\tfpos = ts.p.treeANode > -1 ? ts.p.treeANode: 0;\r\n
\t\t\t\tif(ts.p.grouping) {\r\n
\t\t\t\t\t$(ts).jqGrid(\'groupingRender\',grpdata,ts.p.colModel.length);\r\n
\t\t\t\t\tgrpdata = null;\r\n
\t\t\t\t} else if(ts.p.treeGrid === true && fpos > 0) {\r\n
\t\t\t\t\t$(ts.rows[fpos]).after(rowData.join(\'\'));\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$("tbody:first",t).append(rowData.join(\'\'));\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.subGrid === true ) {\r\n
\t\t\t\ttry {$(ts).jqGrid("addSubGrid",gi+ni);} catch (_){}\r\n
\t\t\t}\r\n
\t\t\tts.p.totaltime = new Date() - startReq;\r\n
\t\t\tif(ir>0) { if(ts.p.records===0) { ts.p.records=gl;} }\r\n
\t\t\trowData =null;\r\n
\t\t\tif( ts.p.treeGrid === true) {\r\n
\t\t\t\ttry {$(ts).jqGrid("setTreeNode", fpos+1, ir+fpos+1);} catch (e) {}\r\n
\t\t\t}\r\n
\t\t\tif(!ts.p.treeGrid && !ts.p.scroll) {ts.grid.bDiv.scrollTop = 0;}\r\n
\t\t\tts.p.reccount=ir;\r\n
\t\t\tts.p.treeANode = -1;\r\n
\t\t\tif(ts.p.userDataOnFooter) { $(ts).jqGrid("footerData","set",ts.p.userData,true); }\r\n
\t\t\tif(locdata) {\r\n
\t\t\t\tts.p.records = gl;\r\n
\t\t\t\tts.p.lastpage = Math.ceil(gl/ rn);\r\n
\t\t\t}\r\n
\t\t\tif (!more) { ts.updatepager(false,true); }\r\n
\t\t\tif(locdata) {\r\n
\t\t\t\twhile (ir<gl) {\r\n
\t\t\t\t\txmlr = gxml[ir];\r\n
\t\t\t\t\trid = getId(xmlr,ir+br);\r\n
\t\t\t\t\trid  = ts.p.idPrefix + rid;\r\n
\t\t\t\t\tif(xmlRd.repeatitems){\r\n
\t\t\t\t\t\tif (!F) { F=orderedCols(gi+si+ni); }\r\n
\t\t\t\t\t\tvar cells2 = $.jgrid.getXmlData( xmlr, xmlRd.cell, true);\r\n
\t\t\t\t\t\t$.each(F, function (k) {\r\n
\t\t\t\t\t\t\tvar cell = cells2[this];\r\n
\t\t\t\t\t\t\tif (!cell) { return false; }\r\n
\t\t\t\t\t\t\tv = cell.textContent || cell.text;\r\n
\t\t\t\t\t\t\trd[ts.p.colModel[k+gi+si+ni].name] = v;\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tfor(i = 0; i < f.length;i++) {\r\n
\t\t\t\t\t\t\tv = $.jgrid.getXmlData( xmlr, f[i]);\r\n
\t\t\t\t\t\t\trd[ts.p.colModel[i+gi+si+ni].name] = v;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\trd[xmlid] = rid;\r\n
\t\t\t\t\tts.p.data.push(rd);\r\n
\t\t\t\t\tts.p._index[rid] = ts.p.data.length-1;\r\n
\t\t\t\t\trd = {};\r\n
\t\t\t\t\tir++;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\taddJSONData = function(data,t, rcnt, more, adjust) {\r\n
\t\t\tvar startReq = new Date();\r\n
\t\t\tif(data) {\r\n
\t\t\t\tif(ts.p.treeANode === -1 && !ts.p.scroll) {\r\n
\t\t\t\t\temptyRows.call(ts, false, true);\r\n
\t\t\t\t\trcnt=1;\r\n
\t\t\t\t} else { rcnt = rcnt > 1 ? rcnt :1; }\r\n
\t\t\t} else { return; }\r\n
\r\n
\t\t\tvar dReader, locid = "_id_", frd,\r\n
\t\t\tlocdata = (ts.p.datatype != "local" && ts.p.loadonce) || ts.p.datatype == "jsonstring";\r\n
\t\t\tif(locdata) { ts.p.data = []; ts.p._index = {}; ts.p.localReader.id = locid;}\r\n
\t\t\tts.p.reccount = 0;\r\n
\t\t\tif(ts.p.datatype == "local") {\r\n
\t\t\t\tdReader =  ts.p.localReader;\r\n
\t\t\t\tfrd= \'local\';\r\n
\t\t\t} else {\r\n
\t\t\t\tdReader =  ts.p.jsonReader;\r\n
\t\t\t\tfrd=\'json\';\r\n
\t\t\t}\r\n
\t\t\tvar ir=0,v,i,j,f=[],F,cur,gi=ts.p.multiselect?1:0,si=ts.p.subGrid?1:0,ni=ts.p.rownumbers===true?1:0,len,drows,idn,rd={}, fpos, idr,rowData=[],cn=(ts.p.altRows === true) ? " "+ts.p.altclass:"",cn1,lp;\r\n
\t\t\tts.p.page = $.jgrid.getAccessor(data,dReader.page) || ts.p.page || 0;\r\n
\t\t\tlp = $.jgrid.getAccessor(data,dReader.total);\r\n
\t\t\tts.p.lastpage = lp === undefined ? 1 : lp;\r\n
\t\t\tts.p.records = $.jgrid.getAccessor(data,dReader.records) || 0;\r\n
\t\t\tts.p.userData = $.jgrid.getAccessor(data,dReader.userdata) || {};\r\n
\t\t\tif(!dReader.repeatitems) {\r\n
\t\t\t\tF = f = reader(frd);\r\n
\t\t\t}\r\n
\t\t\tif( ts.p.keyIndex===false ) {\r\n
\t\t\t\tidn = $.isFunction(dReader.id) ? dReader.id.call(ts, data) : dReader.id; \r\n
\t\t\t} else {\r\n
\t\t\t\tidn = ts.p.keyIndex;\r\n
\t\t\t}\r\n
\t\t\tif(f.length>0 && !isNaN(idn)) {\r\n
\t\t\t\tif (ts.p.remapColumns && ts.p.remapColumns.length) {\r\n
\t\t\t\t\tidn = $.inArray(idn, ts.p.remapColumns);\r\n
\t\t\t\t}\r\n
\t\t\t\tidn=f[idn];\r\n
\t\t\t}\r\n
\t\t\tdrows = $.jgrid.getAccessor(data,dReader.root);\r\n
\t\t\tif (!drows) { drows = []; }\r\n
\t\t\tlen = drows.length; i=0;\r\n
\t\t\tif (len > 0 && ts.p.page <= 0) { ts.p.page = 1; }\r\n
\t\t\tvar rn = parseInt(ts.p.rowNum,10),br=ts.p.scroll?$.jgrid.randId():1, altr, selected=false, selr;\r\n
\t\t\tif (adjust) { rn *= adjust+1; }\r\n
\t\t\tif(ts.p.datatype === "local" && !ts.p.deselectAfterSort) {\r\n
\t\t\t\tselected = true;\r\n
\t\t\t}\r\n
\t\t\tvar afterInsRow = $.isFunction(ts.p.afterInsertRow), grpdata=[], hiderow=ts.p.grouping && ts.p.groupingView.groupCollapse === true;\r\n
\t\t\twhile (i<len) {\r\n
\t\t\t\tcur = drows[i];\r\n
\t\t\t\tidr = $.jgrid.getAccessor(cur,idn);\r\n
\t\t\t\tif(idr === undefined) {\r\n
\t\t\t\t\tidr = br+i;\r\n
\t\t\t\t\tif(f.length===0){\r\n
\t\t\t\t\t\tif(dReader.cell){\r\n
\t\t\t\t\t\t\tvar ccur = $.jgrid.getAccessor(cur,dReader.cell);\r\n
\t\t\t\t\t\t\tidr = ccur !== undefined ? ccur[idn] || idr : idr;\r\n
\t\t\t\t\t\t\tccur=null;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tidr  = ts.p.idPrefix + idr;\r\n
\t\t\t\taltr = rcnt === 1 ? 0 : rcnt;\r\n
\t\t\t\tcn1 = (altr+i)%2 == 1 ? cn : \'\';\r\n
\t\t\t\tif( selected) {\r\n
\t\t\t\t\tif( ts.p.multiselect) {\r\n
\t\t\t\t\t\tselr = ($.inArray(idr, ts.p.selarrrow) !== -1);\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tselr = (idr === ts.p.selrow);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tvar iStartTrTag = rowData.length;\r\n
\t\t\t\trowData.push("");\r\n
\t\t\t\tif( ni ) {\r\n
\t\t\t\t\trowData.push( addRowNum(0,i,ts.p.page,ts.p.rowNum) );\r\n
\t\t\t\t}\r\n
\t\t\t\tif( gi ){\r\n
\t\t\t\t\trowData.push( addMulti(idr,ni,i,selr) );\r\n
\t\t\t\t}\r\n
\t\t\t\tif( si ) {\r\n
\t\t\t\t\trowData.push( $(ts).jqGrid("addSubGridCell",gi+ni,i+rcnt) );\r\n
\t\t\t\t}\r\n
\t\t\t\tif (dReader.repeatitems) {\r\n
\t\t\t\t\tif(dReader.cell) {cur = $.jgrid.getAccessor(cur,dReader.cell);}\r\n
\t\t\t\t\tif (!F) { F=orderedCols(gi+si+ni); }\r\n
\t\t\t\t}\r\n
\t\t\t\tfor (j=0;j<F.length;j++) {\r\n
\t\t\t\t\tv = $.jgrid.getAccessor(cur,F[j]);\r\n
\t\t\t\t\trowData.push( addCell(idr,v,j+gi+si+ni,i+rcnt,cur) );\r\n
\t\t\t\t\trd[ts.p.colModel[j+gi+si+ni].name] = v;\r\n
\t\t\t\t}\r\n
\t\t\t\trowData[iStartTrTag] = constructTr(idr, hiderow, cn1, rd, cur, selr);\r\n
\t\t\t\trowData.push( "</tr>" );\r\n
\t\t\t\tif(ts.p.grouping) {\r\n
\t\t\t\t\tgrpdata = $(ts).jqGrid(\'groupingPrepare\',rowData, grpdata, rd, i);\r\n
\t\t\t\t\trowData = [];\r\n
\t\t\t\t}\r\n
\t\t\t\tif(locdata || ts.p.treeGrid===true) {\r\n
\t\t\t\t\trd[locid] = idr;\r\n
\t\t\t\t\tts.p.data.push(rd);\r\n
\t\t\t\t\tts.p._index[idr] = ts.p.data.length-1;\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ts.p.gridview === false ) {\r\n
\t\t\t\t\t$("#"+$.jgrid.jqID(ts.p.id)+" tbody:first").append(rowData.join(\'\'));\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridAfterInsertRow", [idr, rd, cur]);\r\n
\t\t\t\t\tif(afterInsRow) {ts.p.afterInsertRow.call(ts,idr,rd,cur);}\r\n
\t\t\t\t\trowData=[];//ari=0;\r\n
\t\t\t\t}\r\n
\t\t\t\trd={};\r\n
\t\t\t\tir++;\r\n
\t\t\t\ti++;\r\n
\t\t\t\tif(ir==rn) { break; }\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.gridview === true ) {\r\n
\t\t\t\tfpos = ts.p.treeANode > -1 ? ts.p.treeANode: 0;\r\n
\t\t\t\tif(ts.p.grouping) {\r\n
\t\t\t\t\t$(ts).jqGrid(\'groupingRender\',grpdata,ts.p.colModel.length);\r\n
\t\t\t\t\tgrpdata = null;\r\n
\t\t\t\t} else if(ts.p.treeGrid === true && fpos > 0) {\r\n
\t\t\t\t\t$(ts.rows[fpos]).after(rowData.join(\'\'));\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$("#"+$.jgrid.jqID(ts.p.id)+" tbody:first").append(rowData.join(\'\'));\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.subGrid === true ) {\r\n
\t\t\t\ttry { $(ts).jqGrid("addSubGrid",gi+ni);} catch (_){}\r\n
\t\t\t}\r\n
\t\t\tts.p.totaltime = new Date() - startReq;\r\n
\t\t\tif(ir>0) {\r\n
\t\t\t\tif(ts.p.records===0) { ts.p.records=len; }\r\n
\t\t\t}\r\n
\t\t\trowData = null;\r\n
\t\t\tif( ts.p.treeGrid === true) {\r\n
\t\t\t\ttry {$(ts).jqGrid("setTreeNode", fpos+1, ir+fpos+1);} catch (e) {}\r\n
\t\t\t}\r\n
\t\t\tif(!ts.p.treeGrid && !ts.p.scroll) {ts.grid.bDiv.scrollTop = 0;}\r\n
\t\t\tts.p.reccount=ir;\r\n
\t\t\tts.p.treeANode = -1;\r\n
\t\t\tif(ts.p.userDataOnFooter) { $(ts).jqGrid("footerData","set",ts.p.userData,true); }\r\n
\t\t\tif(locdata) {\r\n
\t\t\t\tts.p.records = len;\r\n
\t\t\t\tts.p.lastpage = Math.ceil(len/ rn);\r\n
\t\t\t}\r\n
\t\t\tif (!more) { ts.updatepager(false,true); }\r\n
\t\t\tif(locdata) {\r\n
\t\t\t\twhile (ir<len && drows[ir]) {\r\n
\t\t\t\t\tcur = drows[ir];\r\n
\t\t\t\t\tidr = $.jgrid.getAccessor(cur,idn);\r\n
\t\t\t\t\tif(idr === undefined) {\r\n
\t\t\t\t\t\tidr = br+ir;\r\n
\t\t\t\t\t\tif(f.length===0){\r\n
\t\t\t\t\t\t\tif(dReader.cell){\r\n
\t\t\t\t\t\t\t\tvar ccur2 = $.jgrid.getAccessor(cur,dReader.cell);\r\n
\t\t\t\t\t\t\t\tidr = ccur2[idn] || idr;\r\n
\t\t\t\t\t\t\t\tccur2=null;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(cur) {\r\n
\t\t\t\t\t\tidr  = ts.p.idPrefix + idr;\r\n
\t\t\t\t\t\tif (dReader.repeatitems) {\r\n
\t\t\t\t\t\t\tif(dReader.cell) {cur = $.jgrid.getAccessor(cur,dReader.cell);}\r\n
\t\t\t\t\t\t\tif (!F) { F=orderedCols(gi+si+ni); }\r\n
\t\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\t\tfor (j=0;j<F.length;j++) {\r\n
\t\t\t\t\t\t\tv = $.jgrid.getAccessor(cur,F[j]);\r\n
\t\t\t\t\t\t\trd[ts.p.colModel[j+gi+si+ni].name] = v;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\trd[locid] = idr;\r\n
\t\t\t\t\t\tts.p.data.push(rd);\r\n
\t\t\t\t\t\tts.p._index[idr] = ts.p.data.length-1;\r\n
\t\t\t\t\t\trd = {};\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tir++;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\taddLocalData = function() {\r\n
\t\t\tvar st, fndsort=false, cmtypes={}, grtypes=[], grindexes=[], srcformat, sorttype, newformat;\r\n
\t\t\tif(!$.isArray(ts.p.data)) {\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t\tvar grpview = ts.p.grouping ? ts.p.groupingView : false, lengrp, gin;\r\n
\t\t\t$.each(ts.p.colModel,function(){\r\n
\t\t\t\tsorttype = this.sorttype || "text";\r\n
\t\t\t\tif(sorttype == "date" || sorttype == "datetime") {\r\n
\t\t\t\t\tif(this.formatter && typeof(this.formatter) === \'string\' && this.formatter == \'date\') {\r\n
\t\t\t\t\t\tif(this.formatoptions && this.formatoptions.srcformat) {\r\n
\t\t\t\t\t\t\tsrcformat = this.formatoptions.srcformat;\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tsrcformat = $.jgrid.formatter.date.srcformat;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(this.formatoptions && this.formatoptions.newformat) {\r\n
\t\t\t\t\t\t\tnewformat = this.formatoptions.newformat;\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tnewformat = $.jgrid.formatter.date.newformat;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tsrcformat = newformat = this.datefmt || "Y-m-d";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tcmtypes[this.name] = {"stype": sorttype, "srcfmt": srcformat,"newfmt":newformat};\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tcmtypes[this.name] = {"stype": sorttype, "srcfmt":\'\',"newfmt":\'\'};\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ts.p.grouping ) {\r\n
\t\t\t\t\tfor(gin =0, lengrp = grpview.groupField.length; gin< lengrp; gin++) {\r\n
\t\t\t\t\t\tif( this.name == grpview.groupField[gin]) {\r\n
\t\t\t\t\t\t\tvar grindex = this.name;\r\n
\t\t\t\t\t\t\tif (typeof this.index != \'undefined\') {\r\n
\t\t\t\t\t\t\t\tgrindex = this.index;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tgrtypes[gin] = cmtypes[grindex];\r\n
\t\t\t\t\t\t\tgrindexes[gin]= grindex;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(!fndsort && (this.index == ts.p.sortname || this.name == ts.p.sortname)){\r\n
\t\t\t\t\tst = this.name; // ???\r\n
\t\t\t\t\tfndsort = true;\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\tif(ts.p.treeGrid) {\r\n
\t\t\t\t$(ts).jqGrid("SortTree", st, ts.p.sortorder, cmtypes[st].stype, cmtypes[st].srcfmt);\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t\tvar compareFnMap = {\r\n
\t\t\t\t\'eq\':function(queryObj) {return queryObj.equals;},\r\n
\t\t\t\t\'ne\':function(queryObj) {return queryObj.notEquals;},\r\n
\t\t\t\t\'lt\':function(queryObj) {return queryObj.less;},\r\n
\t\t\t\t\'le\':function(queryObj) {return queryObj.lessOrEquals;},\r\n
\t\t\t\t\'gt\':function(queryObj) {return queryObj.greater;},\r\n
\t\t\t\t\'ge\':function(queryObj) {return queryObj.greaterOrEquals;},\r\n
\t\t\t\t\'cn\':function(queryObj) {return queryObj.contains;},\r\n
\t\t\t\t\'nc\':function(queryObj,op) {return op === "OR" ? queryObj.orNot().contains : queryObj.andNot().contains;},\r\n
\t\t\t\t\'bw\':function(queryObj) {return queryObj.startsWith;},\r\n
\t\t\t\t\'bn\':function(queryObj,op) {return op === "OR" ? queryObj.orNot().startsWith : queryObj.andNot().startsWith;},\r\n
\t\t\t\t\'en\':function(queryObj,op) {return op === "OR" ? queryObj.orNot().endsWith : queryObj.andNot().endsWith;},\r\n
\t\t\t\t\'ew\':function(queryObj) {return queryObj.endsWith;},\r\n
\t\t\t\t\'ni\':function(queryObj,op) {return op === "OR" ? queryObj.orNot().equals : queryObj.andNot().equals;},\r\n
\t\t\t\t\'in\':function(queryObj) {return queryObj.equals;},\r\n
\t\t\t\t\'nu\':function(queryObj) {return queryObj.isNull;},\r\n
\t\t\t\t\'nn\':function(queryObj,op) {return op === "OR" ? queryObj.orNot().isNull : queryObj.andNot().isNull;}\r\n
\r\n
\t\t\t},\r\n
\t\t\tquery = $.jgrid.from(ts.p.data);\r\n
\t\t\tif (ts.p.ignoreCase) { query = query.ignoreCase(); }\r\n
\t\t\tfunction tojLinq ( group ) {\r\n
\t\t\t\tvar s = 0, index, gor, ror, opr, rule;\r\n
\t\t\t\tif (group.groups !== undefined) {\r\n
\t\t\t\t\tgor = group.groups.length && group.groupOp.toString().toUpperCase() === "OR";\r\n
\t\t\t\t\tif (gor) {\r\n
\t\t\t\t\t\tquery.orBegin();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tfor (index = 0; index < group.groups.length; index++) {\r\n
\t\t\t\t\t\tif (s > 0 && gor) {\r\n
\t\t\t\t\t\t\tquery.or();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\ttojLinq(group.groups[index]);\r\n
\t\t\t\t\t\t} catch (e) {alert(e);}\r\n
\t\t\t\t\t\ts++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (gor) {\r\n
\t\t\t\t\t\tquery.orEnd();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif (group.rules !== undefined) {\r\n
\t\t\t\t\tif(s>0) {\r\n
\t\t\t\t\t\tvar result = query.select();\r\n
\t\t\t\t\t\tquery = $.jgrid.from( result);\r\n
\t\t\t\t\t\tif (ts.p.ignoreCase) { query = query.ignoreCase(); } \r\n
\t\t\t\t\t}\r\n
\t\t\t\t\ttry{\r\n
\t\t\t\t\t\tror = group.rules.length && group.groupOp.toString().toUpperCase() === "OR";\r\n
\t\t\t\t\t\tif (ror) {\r\n
\t\t\t\t\t\t\tquery.orBegin();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tfor (index = 0; index < group.rules.length; index++) {\r\n
\t\t\t\t\t\t\trule = group.rules[index];\r\n
\t\t\t\t\t\t\topr = group.groupOp.toString().toUpperCase();\r\n
\t\t\t\t\t\t\tif (compareFnMap[rule.op] && rule.field ) {\r\n
\t\t\t\t\t\t\t\tif(s > 0 && opr && opr === "OR") {\r\n
\t\t\t\t\t\t\t\t\tquery = query.or();\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tquery = compareFnMap[rule.op](query, opr)(rule.field, rule.data, cmtypes[rule.field]);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\ts++;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif (ror) {\r\n
\t\t\t\t\t\t\tquery.orEnd();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} catch (g) {alert(g);}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tif (ts.p.search === true) {\r\n
\t\t\t\tvar srules = ts.p.postData.filters;\r\n
\t\t\t\tif(srules) {\r\n
\t\t\t\t\tif(typeof srules == "string") { srules = $.jgrid.parse(srules);}\r\n
\t\t\t\t\ttojLinq( srules );\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\ttry {\r\n
\t\t\t\t\t\tquery = compareFnMap[ts.p.postData.searchOper](query)(ts.p.postData.searchField, ts.p.postData.searchString,cmtypes[ts.p.postData.searchField]);\r\n
\t\t\t\t\t} catch (se){}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.grouping) {\r\n
\t\t\t\tfor(gin=0; gin<lengrp;gin++) {\r\n
\t\t\t\t\tquery.orderBy(grindexes[gin],grpview.groupOrder[gin],grtypes[gin].stype, grtypes[gin].srcfmt);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif (st && ts.p.sortorder && fndsort) {\r\n
\t\t\t\tif(ts.p.sortorder.toUpperCase() == "DESC") {\r\n
\t\t\t\t\tquery.orderBy(ts.p.sortname, "d", cmtypes[st].stype, cmtypes[st].srcfmt);\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tquery.orderBy(ts.p.sortname, "a", cmtypes[st].stype, cmtypes[st].srcfmt);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tvar queryResults = query.select(),\r\n
\t\t\trecordsperpage = parseInt(ts.p.rowNum,10),\r\n
\t\t\ttotal = queryResults.length,\r\n
\t\t\tpage = parseInt(ts.p.page,10),\r\n
\t\t\ttotalpages = Math.ceil(total / recordsperpage),\r\n
\t\t\tretresult = {};\r\n
\t\t\tqueryResults = queryResults.slice( (page-1)*recordsperpage , page*recordsperpage );\r\n
\t\t\tquery = null;\r\n
\t\t\tcmtypes = null;\r\n
\t\t\tretresult[ts.p.localReader.total] = totalpages;\r\n
\t\t\tretresult[ts.p.localReader.page] = page;\r\n
\t\t\tretresult[ts.p.localReader.records] = total;\r\n
\t\t\tretresult[ts.p.localReader.root] = queryResults;\r\n
\t\t\tretresult[ts.p.localReader.userdata] = ts.p.userData;\r\n
\t\t\tqueryResults = null;\r\n
\t\t\treturn  retresult;\r\n
\t\t},\r\n
\t\tupdatepager = function(rn, dnd) {\r\n
\t\t\tvar cp, last, base, from,to,tot,fmt, pgboxes = "", sppg,\r\n
\t\t\ttspg = ts.p.pager ? "_"+$.jgrid.jqID(ts.p.pager.substr(1)) : "",\r\n
\t\t\ttspg_t = ts.p.toppager ? "_"+ts.p.toppager.substr(1) : "";\r\n
\t\t\tbase = parseInt(ts.p.page,10)-1;\r\n
\t\t\tif(base < 0) { base = 0; }\r\n
\t\t\tbase = base*parseInt(ts.p.rowNum,10);\r\n
\t\t\tto = base + ts.p.reccount;\r\n
\t\t\tif (ts.p.scroll) {\r\n
\t\t\t\tvar rows = $("tbody:first > tr:gt(0)", ts.grid.bDiv);\r\n
\t\t\t\tbase = to - rows.length;\r\n
\t\t\t\tts.p.reccount = rows.length;\r\n
\t\t\t\tvar rh = rows.outerHeight() || ts.grid.prevRowHeight;\r\n
\t\t\t\tif (rh) {\r\n
\t\t\t\t\tvar top = base * rh;\r\n
\t\t\t\t\tvar height = parseInt(ts.p.records,10) * rh;\r\n
\t\t\t\t\t$(">div:first",ts.grid.bDiv).css({height : height}).children("div:first").css({height:top,display:top?"":"none"});\r\n
\t\t\t\t}\r\n
\t\t\t\tts.grid.bDiv.scrollLeft = ts.grid.hDiv.scrollLeft;\r\n
\t\t\t}\r\n
\t\t\tpgboxes = ts.p.pager ? ts.p.pager : "";\r\n
\t\t\tpgboxes += ts.p.toppager ?  (pgboxes ? "," + ts.p.toppager : ts.p.toppager) : "";\r\n
\t\t\tif(pgboxes) {\r\n
\t\t\t\tfmt = $.jgrid.formatter.integer || {};\r\n
\t\t\t\tcp = intNum(ts.p.page);\r\n
\t\t\t\tlast = intNum(ts.p.lastpage);\r\n
\t\t\t\t$(".selbox",pgboxes)[ this.p.useProp ? \'prop\' : \'attr\' ]("disabled",false);\r\n
\t\t\t\tif(ts.p.pginput===true) {\r\n
\t\t\t\t\t$(\'.ui-pg-input\',pgboxes).val(ts.p.page);\r\n
\t\t\t\t\tsppg = ts.p.toppager ? \'#sp_1\'+tspg+",#sp_1"+tspg_t : \'#sp_1\'+tspg;\r\n
\t\t\t\t\t$(sppg).html($.fmatter ? $.fmatter.util.NumberFormat(ts.p.lastpage,fmt):ts.p.lastpage);\r\n
\r\n
\t\t\t\t}\r\n
\t\t\t\tif (ts.p.viewrecords){\r\n
\t\t\t\t\tif(ts.p.reccount === 0) {\r\n
\t\t\t\t\t\t$(".ui-paging-info",pgboxes).html(ts.p.emptyrecords);\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tfrom = base+1;\r\n
\t\t\t\t\t\ttot=ts.p.records;\r\n
\t\t\t\t\t\tif($.fmatter) {\r\n
\t\t\t\t\t\t\tfrom = $.fmatter.util.NumberFormat(from,fmt);\r\n
\t\t\t\t\t\t\tto = $.fmatter.util.NumberFormat(to,fmt);\r\n
\t\t\t\t\t\t\ttot = $.fmatter.util.NumberFormat(tot,fmt);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t$(".ui-paging-info",pgboxes).html($.jgrid.format(ts.p.recordtext,from,to,tot));\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ts.p.pgbuttons===true) {\r\n
\t\t\t\t\tif(cp<=0) {cp = last = 0;}\r\n
\t\t\t\t\tif(cp==1 || cp === 0) {\r\n
\t\t\t\t\t\t$("#first"+tspg+", #prev"+tspg).addClass(\'ui-state-disabled\').removeClass(\'ui-state-hover\');\r\n
\t\t\t\t\t\tif(ts.p.toppager) { $("#first_t"+tspg_t+", #prev_t"+tspg_t).addClass(\'ui-state-disabled\').removeClass(\'ui-state-hover\'); }\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$("#first"+tspg+", #prev"+tspg).removeClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\tif(ts.p.toppager) { $("#first_t"+tspg_t+", #prev_t"+tspg_t).removeClass(\'ui-state-disabled\'); }\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(cp==last || cp === 0) {\r\n
\t\t\t\t\t\t$("#next"+tspg+", #last"+tspg).addClass(\'ui-state-disabled\').removeClass(\'ui-state-hover\');\r\n
\t\t\t\t\t\tif(ts.p.toppager) { $("#next_t"+tspg_t+", #last_t"+tspg_t).addClass(\'ui-state-disabled\').removeClass(\'ui-state-hover\'); }\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$("#next"+tspg+", #last"+tspg).removeClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\tif(ts.p.toppager) { $("#next_t"+tspg_t+", #last_t"+tspg_t).removeClass(\'ui-state-disabled\'); }\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(rn===true && ts.p.rownumbers === true) {\r\n
\t\t\t\t$("td.jqgrid-rownum",ts.rows).each(function(i){\r\n
\t\t\t\t\t$(this).html(base+1+i);\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tif(dnd && ts.p.jqgdnd) { $(ts).jqGrid(\'gridDnD\',\'updateDnD\');}\r\n
\t\t\t$(ts).triggerHandler("jqGridGridComplete");\r\n
\t\t\tif($.isFunction(ts.p.gridComplete)) {ts.p.gridComplete.call(ts);}\r\n
\t\t\t$(ts).triggerHandler("jqGridAfterGridComplete");\r\n
\t\t},\r\n
\t\tbeginReq = function() {\r\n
\t\t\tts.grid.hDiv.loading = true;\r\n
\t\t\tif(ts.p.hiddengrid) { return;}\r\n
\t\t\tswitch(ts.p.loadui) {\r\n
\t\t\t\tcase "disable":\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase "enable":\r\n
\t\t\t\t\t$("#load_"+$.jgrid.jqID(ts.p.id)).show();\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase "block":\r\n
\t\t\t\t\t$("#lui_"+$.jgrid.jqID(ts.p.id)).show();\r\n
\t\t\t\t\t$("#load_"+$.jgrid.jqID(ts.p.id)).show();\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\tendReq = function() {\r\n
\t\t\tts.grid.hDiv.loading = false;\r\n
\t\t\tswitch(ts.p.loadui) {\r\n
\t\t\t\tcase "disable":\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase "enable":\r\n
\t\t\t\t\t$("#load_"+$.jgrid.jqID(ts.p.id)).hide();\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase "block":\r\n
\t\t\t\t\t$("#lui_"+$.jgrid.jqID(ts.p.id)).hide();\r\n
\t\t\t\t\t$("#load_"+$.jgrid.jqID(ts.p.id)).hide();\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\tpopulate = function (npage) {\r\n
\t\t\tif(!ts.grid.hDiv.loading) {\r\n
\t\t\t\tvar pvis = ts.p.scroll && npage === false,\r\n
\t\t\t\tprm = {}, dt, dstr, pN=ts.p.prmNames;\r\n
\t\t\t\tif(ts.p.page <=0) { ts.p.page = 1; }\r\n
\t\t\t\tif(pN.search !== null) {prm[pN.search] = ts.p.search;} if(pN.nd !== null) {prm[pN.nd] = new Date().getTime();}\r\n
\t\t\t\tif(pN.rows !== null) {prm[pN.rows]= ts.p.rowNum;} if(pN.page !== null) {prm[pN.page]= ts.p.page;}\r\n
\t\t\t\tif(pN.sort !== null) {prm[pN.sort]= ts.p.sortname;} if(pN.order !== null) {prm[pN.order]= ts.p.sortorder;}\r\n
\t\t\t\tif(ts.p.rowTotal !== null && pN.totalrows !== null) { prm[pN.totalrows]= ts.p.rowTotal; }\r\n
\t\t\t\tvar lcf = $.isFunction(ts.p.loadComplete), lc = lcf ? ts.p.loadComplete : null;\r\n
\t\t\t\tvar adjust = 0;\r\n
\t\t\t\tnpage = npage || 1;\r\n
\t\t\t\tif (npage > 1) {\r\n
\t\t\t\t\tif(pN.npage !== null) {\r\n
\t\t\t\t\t\tprm[pN.npage] = npage;\r\n
\t\t\t\t\t\tadjust = npage - 1;\r\n
\t\t\t\t\t\tnpage = 1;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tlc = function(req) {\r\n
\t\t\t\t\t\t\tts.p.page++;\r\n
\t\t\t\t\t\t\tts.grid.hDiv.loading = false;\r\n
\t\t\t\t\t\t\tif (lcf) {\r\n
\t\t\t\t\t\t\t\tts.p.loadComplete.call(ts,req);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tpopulate(npage-1);\r\n
\t\t\t\t\t\t};\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else if (pN.npage !== null) {\r\n
\t\t\t\t\tdelete ts.p.postData[pN.npage];\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ts.p.grouping) {\r\n
\t\t\t\t\t$(ts).jqGrid(\'groupingSetup\');\r\n
\t\t\t\t\tvar grp = ts.p.groupingView, gi, gs="";\r\n
\t\t\t\t\tfor(gi=0;gi<grp.groupField.length;gi++) {\r\n
\t\t\t\t\t\tvar index = grp.groupField[gi];\r\n
\t\t\t\t\t\t$.each(ts.p.colModel, function(cmIndex, cmValue) {\r\n
\t\t\t\t\t\t\tif (cmValue.name == index && cmValue.index){\r\n
\t\t\t\t\t\t\t\tindex = cmValue.index;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t} );\r\n
\t\t\t\t\t\tgs += index +" "+grp.groupOrder[gi]+", ";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tprm[pN.sort] = gs + prm[pN.sort];\r\n
\t\t\t\t}\r\n
\t\t\t\t$.extend(ts.p.postData,prm);\r\n
\t\t\t\tvar rcnt = !ts.p.scroll ? 1 : ts.rows.length-1;\r\n
\t\t\t\tvar bfr = $(ts).triggerHandler("jqGridBeforeRequest");\r\n
\t\t\t\tif (bfr === false || bfr === \'stop\') { return; }\r\n
\t\t\t\tif ($.isFunction(ts.p.datatype)) { ts.p.datatype.call(ts,ts.p.postData,"load_"+ts.p.id); return;}\r\n
\t\t\t\telse if($.isFunction(ts.p.beforeRequest)) {\r\n
\t\t\t\t\tbfr = ts.p.beforeRequest.call(ts);\r\n
\t\t\t\t\tif(bfr === undefined) { bfr = true; }\r\n
\t\t\t\t\tif ( bfr === false ) { return; }\r\n
\t\t\t\t}\r\n
\t\t\t\tdt = ts.p.datatype.toLowerCase();\r\n
\t\t\t\tswitch(dt)\r\n
\t\t\t\t{\r\n
\t\t\t\tcase "json":\r\n
\t\t\t\tcase "jsonp":\r\n
\t\t\t\tcase "xml":\r\n
\t\t\t\tcase "script":\r\n
\t\t\t\t\t$.ajax($.extend({\r\n
\t\t\t\t\t\turl:ts.p.url,\r\n
\t\t\t\t\t\ttype:ts.p.mtype,\r\n
\t\t\t\t\t\tdataType: dt ,\r\n
\t\t\t\t\t\tdata: $.isFunction(ts.p.serializeGridData)? ts.p.serializeGridData.call(ts,ts.p.postData) : ts.p.postData,\r\n
\t\t\t\t\t\tsuccess:function(data,st, xhr) {\r\n
\t\t\t\t\t\t\tif ($.isFunction(ts.p.beforeProcessing)) {\r\n
\t\t\t\t\t\t\t\tif (ts.p.beforeProcessing.call(ts, data, st, xhr) === false) {\r\n
\t\t\t\t\t\t\t\t\tendReq();\r\n
\t\t\t\t\t\t\t\t\treturn;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(dt === "xml") { addXmlData(data,ts.grid.bDiv,rcnt,npage>1,adjust); }\r\n
\t\t\t\t\t\t\telse { addJSONData(data,ts.grid.bDiv,rcnt,npage>1,adjust); }\r\n
\t\t\t\t\t\t\t$(ts).triggerHandler("jqGridLoadComplete", [data]);\r\n
\t\t\t\t\t\t\tif(lc) { lc.call(ts,data); }\r\n
\t\t\t\t\t\t\t$(ts).triggerHandler("jqGridAfterLoadComplete", [data]);\r\n
\t\t\t\t\t\t\tif (pvis) { ts.grid.populateVisible(); }\r\n
\t\t\t\t\t\t\tif( ts.p.loadonce || ts.p.treeGrid) {ts.p.datatype = "local";}\r\n
\t\t\t\t\t\t\tdata=null;\r\n
\t\t\t\t\t\t\tif (npage === 1) { endReq(); }\r\n
\t\t\t\t\t\t},\r\n
\t\t\t\t\t\terror:function(xhr,st,err){\r\n
\t\t\t\t\t\t\tif($.isFunction(ts.p.loadError)) { ts.p.loadError.call(ts,xhr,st,err); }\r\n
\t\t\t\t\t\t\tif (npage === 1) { endReq(); }\r\n
\t\t\t\t\t\t\txhr=null;\r\n
\t\t\t\t\t\t},\r\n
\t\t\t\t\t\tbeforeSend: function(xhr, settings ){\r\n
\t\t\t\t\t\t\tvar gotoreq = true;\r\n
\t\t\t\t\t\t\tif($.isFunction(ts.p.loadBeforeSend)) {\r\n
\t\t\t\t\t\t\t\tgotoreq = ts.p.loadBeforeSend.call(ts,xhr, settings); \r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(gotoreq === undefined) { gotoreq = true; }\r\n
\t\t\t\t\t\t\tif(gotoreq === false) {\r\n
\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tbeginReq();\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t},$.jgrid.ajaxOptions, ts.p.ajaxGridOptions));\r\n
\t\t\t\tbreak;\r\n
\t\t\t\tcase "xmlstring":\r\n
\t\t\t\t\tbeginReq();\r\n
\t\t\t\t\tdstr = $.jgrid.stringToDoc(ts.p.datastr);\r\n
\t\t\t\t\taddXmlData(dstr,ts.grid.bDiv);\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridLoadComplete", [dstr]);\r\n
\t\t\t\t\tif(lcf) {ts.p.loadComplete.call(ts,dstr);}\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridAfterLoadComplete", [dstr]);\r\n
\t\t\t\t\tts.p.datatype = "local";\r\n
\t\t\t\t\tts.p.datastr = null;\r\n
\t\t\t\t\tendReq();\r\n
\t\t\t\tbreak;\r\n
\t\t\t\tcase "jsonstring":\r\n
\t\t\t\t\tbeginReq();\r\n
\t\t\t\t\tif(typeof ts.p.datastr == \'string\') { dstr = $.jgrid.parse(ts.p.datastr); }\r\n
\t\t\t\t\telse { dstr = ts.p.datastr; }\r\n
\t\t\t\t\taddJSONData(dstr,ts.grid.bDiv);\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridLoadComplete", [dstr]);\r\n
\t\t\t\t\tif(lcf) {ts.p.loadComplete.call(ts,dstr);}\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridAfterLoadComplete", [dstr]);\r\n
\t\t\t\t\tts.p.datatype = "local";\r\n
\t\t\t\t\tts.p.datastr = null;\r\n
\t\t\t\t\tendReq();\r\n
\t\t\t\tbreak;\r\n
\t\t\t\tcase "local":\r\n
\t\t\t\tcase "clientside":\r\n
\t\t\t\t\tbeginReq();\r\n
\t\t\t\t\tts.p.datatype = "local";\r\n
\t\t\t\t\tvar req = addLocalData();\r\n
\t\t\t\t\taddJSONData(req,ts.grid.bDiv,rcnt,npage>1,adjust);\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridLoadComplete", [req]);\r\n
\t\t\t\t\tif(lc) { lc.call(ts,req); }\r\n
\t\t\t\t\t$(ts).triggerHandler("jqGridAfterLoadComplete", [req]);\r\n
\t\t\t\t\tif (pvis) { ts.grid.populateVisible(); }\r\n
\t\t\t\t\tendReq();\r\n
\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\tsetHeadCheckBox = function ( checked ) {\r\n
\t\t\t$(\'#cb_\'+$.jgrid.jqID(ts.p.id),ts.grid.hDiv)[ts.p.useProp ? \'prop\': \'attr\']("checked", checked);\r\n
\t\t\tvar fid = ts.p.frozenColumns ? ts.p.id+"_frozen" : "";\r\n
\t\t\tif(fid) {\r\n
\t\t\t\t$(\'#cb_\'+$.jgrid.jqID(ts.p.id),ts.grid.fhDiv)[ts.p.useProp ? \'prop\': \'attr\']("checked", checked);\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\tsetPager = function (pgid, tp){\r\n
\t\t\t// TBD - consider escaping pgid with pgid = $.jgrid.jqID(pgid);\r\n
\t\t\tvar sep = "<td class=\'ui-pg-button ui-state-disabled\' style=\'width:4px;\'><span class=\'ui-separator\'></span></td>",\r\n
\t\t\tpginp = "",\r\n
\t\t\tpgl="<table cellspacing=\'0\' cellpadding=\'0\' border=\'0\' style=\'table-layout:auto;\' class=\'ui-pg-table\'><tbody><tr>",\r\n
\t\t\tstr="", pgcnt, lft, cent, rgt, twd, tdw, i,\r\n
\t\t\tclearVals = function(onpaging){\r\n
\t\t\t\tvar ret;\r\n
\t\t\t\tif ($.isFunction(ts.p.onPaging) ) { ret = ts.p.onPaging.call(ts,onpaging); }\r\n
\t\t\t\tts.p.selrow = null;\r\n
\t\t\t\tif(ts.p.multiselect) {ts.p.selarrrow =[]; setHeadCheckBox( false );}\r\n
\t\t\t\tts.p.savedRow = [];\r\n
\t\t\t\tif(ret==\'stop\') {return false;}\r\n
\t\t\t\treturn true;\r\n
\t\t\t};\r\n
\t\t\tpgid = pgid.substr(1);\r\n
\t\t\ttp += "_" + pgid;\r\n
\t\t\tpgcnt = "pg_"+pgid;\r\n
\t\t\tlft = pgid+"_left"; cent = pgid+"_center"; rgt = pgid+"_right";\r\n
\t\t\t$("#"+$.jgrid.jqID(pgid) )\r\n
\t\t\t.append("<div id=\'"+pgcnt+"\' class=\'ui-pager-control\' role=\'group\'><table cellspacing=\'0\' cellpadding=\'0\' border=\'0\' class=\'ui-pg-table\' style=\'width:100%;table-layout:fixed;height:100%;\' role=\'row\'><tbody><tr><td id=\'"+lft+"\' align=\'left\'></td><td id=\'"+cent+"\' align=\'center\' style=\'white-space:pre;\'></td><td id=\'"+rgt+"\' align=\'right\'></td></tr></tbody></table></div>")\r\n
\t\t\t.attr("dir","ltr"); //explicit setting\r\n
\t\t\tif(ts.p.rowList.length >0){\r\n
\t\t\t\tstr = "<td dir=\'"+dir+"\'>";\r\n
\t\t\t\tstr +="<select class=\'ui-pg-selbox\' role=\'listbox\'>";\r\n
\t\t\t\tfor(i=0;i<ts.p.rowList.length;i++){\r\n
\t\t\t\t\tstr +="<option role=\\"option\\" value=\\""+ts.p.rowList[i]+"\\""+((ts.p.rowNum == ts.p.rowList[i])?" selected=\\"selected\\"":"")+">"+ts.p.rowList[i]+"</option>";\r\n
\t\t\t\t}\r\n
\t\t\t\tstr +="</select></td>";\r\n
\t\t\t}\r\n
\t\t\tif(dir=="rtl") { pgl += str; }\r\n
\t\t\tif(ts.p.pginput===true) { pginp= "<td dir=\'"+dir+"\'>"+$.jgrid.format(ts.p.pgtext || "","<input class=\'ui-pg-input\' type=\'text\' size=\'2\' maxlength=\'7\' value=\'0\' role=\'textbox\'/>","<span id=\'sp_1_"+$.jgrid.jqID(pgid)+"\'></span>")+"</td>";}\r\n
\t\t\tif(ts.p.pgbuttons===true) {\r\n
\t\t\t\tvar po=["first"+tp,"prev"+tp, "next"+tp,"last"+tp]; if(dir=="rtl") { po.reverse(); }\r\n
\t\t\t\tpgl += "<td id=\'"+po[0]+"\' class=\'ui-pg-button ui-corner-all\'><span class=\'ui-icon ui-icon-seek-first\'></span></td>";\r\n
\t\t\t\tpgl += "<td id=\'"+po[1]+"\' class=\'ui-pg-button ui-corner-all\'><span class=\'ui-icon ui-icon-seek-prev\'></span></td>";\r\n
\t\t\t\tpgl += pginp !== "" ? sep+pginp+sep:"";\r\n
\t\t\t\tpgl += "<td id=\'"+po[2]+"\' class=\'ui-pg-button ui-corner-all\'><span class=\'ui-icon ui-icon-seek-next\'></span></td>";\r\n
\t\t\t\tpgl += "<td id=\'"+po[3]+"\' class=\'ui-pg-button ui-corner-all\'><span class=\'ui-icon ui-icon-seek-end\'></span></td>";\r\n
\t\t\t} else if (pginp !== "") { pgl += pginp; }\r\n
\t\t\tif(dir=="ltr") { pgl += str; }\r\n
\t\t\tpgl += "</tr></tbody></table>";\r\n
\t\t\tif(ts.p.viewrecords===true) {$("td#"+pgid+"_"+ts.p.recordpos,"#"+pgcnt).append("<div dir=\'"+dir+"\' style=\'text-align:"+ts.p.recordpos+"\' class=\'ui-paging-info\'></div>");}\r\n
\t\t\t$("td#"+pgid+"_"+ts.p.pagerpos,"#"+pgcnt).append(pgl);\r\n
\t\t\ttdw = $(".ui-jqgrid").css("font-size") || "11px";\r\n
\t\t\t$(document.body).append("<div id=\'testpg\' class=\'ui-jqgrid ui-widget ui-widget-content\' style=\'font-size:"+tdw+";visibility:hidden;\' ></div>");\r\n
\t\t\ttwd = $(pgl).clone().appendTo("#testpg").width();\r\n
\t\t\t$("#testpg").remove();\r\n
\t\t\tif(twd > 0) {\r\n
\t\t\t\tif(pginp !== "") { twd += 50; } //should be param\r\n
\t\t\t\t$("td#"+pgid+"_"+ts.p.pagerpos,"#"+pgcnt).width(twd);\r\n
\t\t\t}\r\n
\t\t\tts.p._nvtd = [];\r\n
\t\t\tts.p._nvtd[0] = twd ? Math.floor((ts.p.width - twd)/2) : Math.floor(ts.p.width/3);\r\n
\t\t\tts.p._nvtd[1] = 0;\r\n
\t\t\tpgl=null;\r\n
\t\t\t$(\'.ui-pg-selbox\',"#"+pgcnt).bind(\'change\',function() {\r\n
\t\t\t\tts.p.page = Math.round(ts.p.rowNum*(ts.p.page-1)/this.value-0.5)+1;\r\n
\t\t\t\tts.p.rowNum = this.value;\r\n
\t\t\t\tif(ts.p.pager) { $(\'.ui-pg-selbox\',ts.p.pager).val(this.value); }\r\n
\t\t\t\tif(ts.p.toppager) { $(\'.ui-pg-selbox\',ts.p.toppager).val(this.value); }\r\n
\t\t\t\tif(!clearVals(\'records\')) { return false; }\r\n
\t\t\t\tpopulate();\r\n
\t\t\t\treturn false;\r\n
\t\t\t});\r\n
\t\t\tif(ts.p.pgbuttons===true) {\r\n
\t\t\t$(".ui-pg-button","#"+pgcnt).hover(function(){\r\n
\t\t\t\tif($(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\tthis.style.cursor=\'default\';\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$(this).addClass(\'ui-state-hover\');\r\n
\t\t\t\t\tthis.style.cursor=\'pointer\';\r\n
\t\t\t\t}\r\n
\t\t\t},function() {\r\n
\t\t\t\tif(!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t$(this).removeClass(\'ui-state-hover\');\r\n
\t\t\t\t\tthis.style.cursor= "default";\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\t$("#first"+$.jgrid.jqID(tp)+", #prev"+$.jgrid.jqID(tp)+", #next"+$.jgrid.jqID(tp)+", #last"+$.jgrid.jqID(tp)).click( function() {\r\n
\t\t\t\tvar cp = intNum(ts.p.page,1),\r\n
\t\t\t\tlast = intNum(ts.p.lastpage,1), selclick = false,\r\n
\t\t\t\tfp=true, pp=true, np=true,lp=true;\r\n
\t\t\t\tif(last ===0 || last===1) {fp=false;pp=false;np=false;lp=false; }\r\n
\t\t\t\telse if( last>1 && cp >=1) {\r\n
\t\t\t\t\tif( cp === 1) { fp=false; pp=false; }\r\n
\t\t\t\t\t//else if( cp>1 && cp <last){ }\r\n
\t\t\t\t\telse if( cp===last){ np=false;lp=false; }\r\n
\t\t\t\t} else if( last>1 && cp===0 ) { np=false;lp=false; cp=last-1;}\r\n
\t\t\t\tif( this.id === \'first\'+tp && fp ) { ts.p.page=1; selclick=true;}\r\n
\t\t\t\tif( this.id === \'prev\'+tp && pp) { ts.p.page=(cp-1); selclick=true;}\r\n
\t\t\t\tif( this.id === \'next\'+tp && np) { ts.p.page=(cp+1); selclick=true;}\r\n
\t\t\t\tif( this.id === \'last\'+tp && lp) { ts.p.page=last; selclick=true;}\r\n
\t\t\t\tif(selclick) {\r\n
\t\t\t\t\tif(!clearVals(this.id)) { return false; }\r\n
\t\t\t\t\tpopulate();\r\n
\t\t\t\t}\r\n
\t\t\t\treturn false;\r\n
\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.pginput===true) {\r\n
\t\t\t$(\'input.ui-pg-input\',"#"+pgcnt).keypress( function(e) {\r\n
\t\t\t\tvar key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;\r\n
\t\t\t\tif(key == 13) {\r\n
\t\t\t\t\tts.p.page = ($(this).val()>0) ? $(this).val():ts.p.page;\r\n
\t\t\t\t\tif(!clearVals(\'user\')) { return false; }\r\n
\t\t\t\t\tpopulate();\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t}\r\n
\t\t\t\treturn this;\r\n
\t\t\t});\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\tsortData = function (index, idxcol,reload,sor){\r\n
\t\t\tif(!ts.p.colModel[idxcol].sortable) { return; }\r\n
\t\t\tvar so;\r\n
\t\t\tif(ts.p.savedRow.length > 0) {return;}\r\n
\t\t\tif(!reload) {\r\n
\t\t\t\tif( ts.p.lastsort == idxcol ) {\r\n
\t\t\t\t\tif( ts.p.sortorder == \'asc\') {\r\n
\t\t\t\t\t\tts.p.sortorder = \'desc\';\r\n
\t\t\t\t\t} else if(ts.p.sortorder == \'desc\') { ts.p.sortorder = \'asc\';}\r\n
\t\t\t\t} else { ts.p.sortorder = ts.p.colModel[idxcol].firstsortorder || \'asc\'; }\r\n
\t\t\t\tts.p.page = 1;\r\n
\t\t\t}\r\n
\t\t\tif(sor) {\r\n
\t\t\t\tif(ts.p.lastsort == idxcol && ts.p.sortorder == sor && !reload) { return; }\r\n
\t\t\t\telse { ts.p.sortorder = sor; }\r\n
\t\t\t}\r\n
\t\t\tvar previousSelectedTh = ts.grid.headers[ts.p.lastsort].el, newSelectedTh = ts.grid.headers[idxcol].el;\r\n
\r\n
\t\t\t$("span.ui-grid-ico-sort",previousSelectedTh).addClass(\'ui-state-disabled\');\r\n
\t\t\t$(previousSelectedTh).attr("aria-selected","false");\r\n
\t\t\t$("span.ui-icon-"+ts.p.sortorder,newSelectedTh).removeClass(\'ui-state-disabled\');\r\n
\t\t\t$(newSelectedTh).attr("aria-selected","true");\r\n
\t\t\tif(!ts.p.viewsortcols[0]) {\r\n
\t\t\t\tif(ts.p.lastsort != idxcol) {\r\n
\t\t\t\t\t$("span.s-ico",previousSelectedTh).hide();\r\n
\t\t\t\t\t$("span.s-ico",newSelectedTh).show();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tindex = index.substring(5 + ts.p.id.length + 1); // bad to be changed!?!\r\n
\t\t\tts.p.sortname = ts.p.colModel[idxcol].index || index;\r\n
\t\t\tso = ts.p.sortorder;\r\n
\t\t\tif ($(ts).triggerHandler("jqGridSortCol", [index, idxcol, so]) === \'stop\') {\r\n
\t\t\t\tts.p.lastsort = idxcol;\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t\tif($.isFunction(ts.p.onSortCol)) {if (ts.p.onSortCol.call(ts,index,idxcol,so)==\'stop\') {ts.p.lastsort = idxcol; return;}}\r\n
\t\t\tif(ts.p.datatype == "local") {\r\n
\t\t\t\tif(ts.p.deselectAfterSort) {$(ts).jqGrid("resetSelection");}\r\n
\t\t\t} else {\r\n
\t\t\t\tts.p.selrow = null;\r\n
\t\t\t\tif(ts.p.multiselect){setHeadCheckBox( false );}\r\n
\t\t\t\tts.p.selarrrow =[];\r\n
\t\t\t\tts.p.savedRow =[];\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.scroll) {\r\n
\t\t\t\tvar sscroll = ts.grid.bDiv.scrollLeft;\r\n
\t\t\t\temptyRows.call(ts, true, false);\r\n
\t\t\t\tts.grid.hDiv.scrollLeft = sscroll;\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.subGrid && ts.p.datatype==\'local\') {\r\n
\t\t\t\t$("td.sgexpanded","#"+$.jgrid.jqID(ts.p.id)).each(function(){\r\n
\t\t\t\t\t$(this).trigger("click");\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tpopulate();\r\n
\t\t\tts.p.lastsort = idxcol;\r\n
\t\t\tif(ts.p.sortname != index && idxcol) {ts.p.lastsort = idxcol;}\r\n
\t\t},\r\n
\t\tsetColWidth = function () {\r\n
\t\t\tvar initwidth = 0, brd=$.jgrid.cellWidth()? 0: intNum(ts.p.cellLayout,0), vc=0, lvc, scw=intNum(ts.p.scrollOffset,0),cw,hs=false,aw,gw=0,\r\n
\t\t\tcl = 0, cr;\r\n
\t\t\t$.each(ts.p.colModel, function() {\r\n
\t\t\t\tif(typeof this.hidden === \'undefined\') {this.hidden=false;}\r\n
\t\t\t\tthis.widthOrg = cw = intNum(this.width,0);\r\n
\t\t\t\tif(this.hidden===false){\r\n
\t\t\t\t\tinitwidth += cw+brd;\r\n
\t\t\t\t\tif(this.fixed) {\r\n
\t\t\t\t\t\tgw += cw+brd;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tvc++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tcl++;\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\tif(isNaN(ts.p.width)) {\r\n
\t\t\t\tts.p.width  = initwidth + ((ts.p.shrinkToFit ===false && !isNaN(ts.p.height)) ? scw : 0);\r\n
\t\t\t}\r\n
\t\t\tgrid.width = ts.p.width;\r\n
\t\t\tts.p.tblwidth = initwidth;\r\n
\t\t\tif(ts.p.shrinkToFit ===false && ts.p.forceFit === true) {ts.p.forceFit=false;}\r\n
\t\t\tif(ts.p.shrinkToFit===true && vc > 0) {\r\n
\t\t\t\taw = grid.width-brd*vc-gw;\r\n
\t\t\t\tif(!isNaN(ts.p.height)) {\r\n
\t\t\t\t\taw -= scw;\r\n
\t\t\t\t\ths = true;\r\n
\t\t\t\t}\r\n
\t\t\t\tinitwidth =0;\r\n
\t\t\t\t$.each(ts.p.colModel, function(i) {\r\n
\t\t\t\t\tif(this.hidden === false && !this.fixed){\r\n
\t\t\t\t\t\tcw = Math.round(aw*this.width/(ts.p.tblwidth-brd*vc-gw));\r\n
\t\t\t\t\t\tthis.width =cw;\r\n
\t\t\t\t\t\tinitwidth += cw;\r\n
\t\t\t\t\t\tlvc = i;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tcr =0;\r\n
\t\t\t\tif (hs) {\r\n
\t\t\t\t\tif(grid.width-gw-(initwidth+brd*vc) !== scw){\r\n
\t\t\t\t\t\tcr = grid.width-gw-(initwidth+brd*vc)-scw;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else if(!hs && Math.abs(grid.width-gw-(initwidth+brd*vc)) !== 1) {\r\n
\t\t\t\t\tcr = grid.width-gw-(initwidth+brd*vc);\r\n
\t\t\t\t}\r\n
\t\t\t\tts.p.colModel[lvc].width += cr;\r\n
\t\t\t\tts.p.tblwidth = initwidth+cr+brd*vc+gw;\r\n
\t\t\t\tif(ts.p.tblwidth > ts.p.width) {\r\n
\t\t\t\t\tts.p.colModel[lvc].width -= (ts.p.tblwidth - parseInt(ts.p.width,10));\r\n
\t\t\t\t\tts.p.tblwidth = ts.p.width;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\tnextVisible= function(iCol) {\r\n
\t\t\tvar ret = iCol, j=iCol, i;\r\n
\t\t\tfor (i = iCol+1;i<ts.p.colModel.length;i++){\r\n
\t\t\t\tif(ts.p.colModel[i].hidden !== true ) {\r\n
\t\t\t\t\tj=i; break;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\treturn j-ret;\r\n
\t\t},\r\n
\t\tgetOffset = function (iCol) {\r\n
\t\t\tvar i, ret = {}, brd1 = $.jgrid.cellWidth() ? 0 : ts.p.cellLayout;\r\n
\t\t\tret[0] =  ret[1] = ret[2] = 0;\r\n
\t\t\tfor(i=0;i<=iCol;i++){\r\n
\t\t\t\tif(ts.p.colModel[i].hidden === false ) {\r\n
\t\t\t\t\tret[0] += ts.p.colModel[i].width+brd1;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.direction=="rtl") { ret[0] = ts.p.width - ret[0]; }\r\n
\t\t\tret[0] = ret[0] - ts.grid.bDiv.scrollLeft;\r\n
\t\t\tif($(ts.grid.cDiv).is(":visible")) {ret[1] += $(ts.grid.cDiv).height() +parseInt($(ts.grid.cDiv).css("padding-top"),10)+parseInt($(ts.grid.cDiv).css("padding-bottom"),10);}\r\n
\t\t\tif(ts.p.toolbar[0]===true && (ts.p.toolbar[1]==\'top\' || ts.p.toolbar[1]==\'both\')) {ret[1] += $(ts.grid.uDiv).height()+parseInt($(ts.grid.uDiv).css("border-top-width"),10)+parseInt($(ts.grid.uDiv).css("border-bottom-width"),10);}\r\n
\t\t\tif(ts.p.toppager) {ret[1] += $(ts.grid.topDiv).height()+parseInt($(ts.grid.topDiv).css("border-bottom-width"),10);}\r\n
\t\t\tret[2] += $(ts.grid.bDiv).height() + $(ts.grid.hDiv).height();\r\n
\t\t\treturn ret;\r\n
\t\t},\r\n
\t\tgetColumnHeaderIndex = function (th) {\r\n
\t\t\tvar i, headers = ts.grid.headers, ci = $.jgrid.getCellIndex(th);\r\n
\t\t\tfor (i = 0; i < headers.length; i++) {\r\n
\t\t\t\tif (th === headers[i].el) {\r\n
\t\t\t\t\tci = i;\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\treturn ci;\r\n
\t\t};\r\n
\t\tthis.p.id = this.id;\r\n
\t\tif ($.inArray(ts.p.multikey,sortkeys) == -1 ) {ts.p.multikey = false;}\r\n
\t\tts.p.keyIndex=false;\r\n
\t\tfor (i=0; i<ts.p.colModel.length;i++) {\r\n
\t\t\tts.p.colModel[i] = $.extend(true, {}, ts.p.cmTemplate, ts.p.colModel[i].template || {}, ts.p.colModel[i]);\r\n
\t\t\tif (ts.p.keyIndex === false && ts.p.colModel[i].key===true) {\r\n
\t\t\t\tts.p.keyIndex = i;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tts.p.sortorder = ts.p.sortorder.toLowerCase();\r\n
\t\tif(ts.p.grouping===true) {\r\n
\t\t\tts.p.scroll = false;\r\n
\t\t\tts.p.rownumbers = false;\r\n
\t\t\t//ts.p.subGrid = false; expiremental\r\n
\t\t\tts.p.treeGrid = false;\r\n
\t\t\tts.p.gridview = true;\r\n
\t\t}\r\n
\t\tif(this.p.treeGrid === true) {\r\n
\t\t\ttry { $(this).jqGrid("setTreeGrid");} catch (_) {}\r\n
\t\t\tif(ts.p.datatype != "local") { ts.p.localReader = {id: "_id_"};\t}\r\n
\t\t}\r\n
\t\tif(this.p.subGrid) {\r\n
\t\t\ttry { $(ts).jqGrid("setSubGrid");} catch (s){}\r\n
\t\t}\r\n
\t\tif(this.p.multiselect) {\r\n
\t\t\tthis.p.colNames.unshift("<input role=\'checkbox\' id=\'cb_"+this.p.id+"\' class=\'cbox\' type=\'checkbox\'/>");\r\n
\t\t\tthis.p.colModel.unshift({name:\'cb\',width:$.jgrid.cellWidth() ? ts.p.multiselectWidth+ts.p.cellLayout : ts.p.multiselectWidth,sortable:false,resizable:false,hidedlg:true,search:false,align:\'center\',fixed:true});\r\n
\t\t}\r\n
\t\tif(this.p.rownumbers) {\r\n
\t\t\tthis.p.colNames.unshift("");\r\n
\t\t\tthis.p.colModel.unshift({name:\'rn\',width:ts.p.rownumWidth,sortable:false,resizable:false,hidedlg:true,search:false,align:\'center\',fixed:true});\r\n
\t\t}\r\n
\t\tts.p.xmlReader = $.extend(true,{\r\n
\t\t\troot: "rows",\r\n
\t\t\trow: "row",\r\n
\t\t\tpage: "rows>page",\r\n
\t\t\ttotal: "rows>total",\r\n
\t\t\trecords : "rows>records",\r\n
\t\t\trepeatitems: true,\r\n
\t\t\tcell: "cell",\r\n
\t\t\tid: "[id]",\r\n
\t\t\tuserdata: "userdata",\r\n
\t\t\tsubgrid: {root:"rows", row: "row", repeatitems: true, cell:"cell"}\r\n
\t\t}, ts.p.xmlReader);\r\n
\t\tts.p.jsonReader = $.extend(true,{\r\n
\t\t\troot: "rows",\r\n
\t\t\tpage: "page",\r\n
\t\t\ttotal: "total",\r\n
\t\t\trecords: "records",\r\n
\t\t\trepeatitems: true,\r\n
\t\t\tcell: "cell",\r\n
\t\t\tid: "id",\r\n
\t\t\tuserdata: "userdata",\r\n
\t\t\tsubgrid: {root:"rows", repeatitems: true, cell:"cell"}\r\n
\t\t},ts.p.jsonReader);\r\n
\t\tts.p.localReader = $.extend(true,{\r\n
\t\t\troot: "rows",\r\n
\t\t\tpage: "page",\r\n
\t\t\ttotal: "total",\r\n
\t\t\trecords: "records",\r\n
\t\t\trepeatitems: false,\r\n
\t\t\tcell: "cell",\r\n
\t\t\tid: "id",\r\n
\t\t\tuserdata: "userdata",\r\n
\t\t\tsubgrid: {root:"rows", repeatitems: true, cell:"cell"}\r\n
\t\t},ts.p.localReader);\r\n
\t\tif(ts.p.scroll){\r\n
\t\t\tts.p.pgbuttons = false; ts.p.pginput=false; ts.p.rowList=[];\r\n
\t\t}\r\n
\t\tif(ts.p.data.length) { refreshIndex(); }\r\n
\t\tvar thead = "<thead><tr class=\'ui-jqgrid-labels\' role=\'rowheader\'>",\r\n
\t\ttdc, idn, w, res, sort,\r\n
\t\ttd, ptr, tbody, imgs,iac="",idc="";\r\n
\t\tif(ts.p.shrinkToFit===true && ts.p.forceFit===true) {\r\n
\t\t\tfor (i=ts.p.colModel.length-1;i>=0;i--){\r\n
\t\t\t\tif(!ts.p.colModel[i].hidden) {\r\n
\t\t\t\t\tts.p.colModel[i].resizable=false;\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tif(ts.p.viewsortcols[1] == \'horizontal\') {iac=" ui-i-asc";idc=" ui-i-desc";}\r\n
\t\ttdc = isMSIE ?  "class=\'ui-th-div-ie\'" :"";\r\n
\t\timgs = "<span class=\'s-ico\' style=\'display:none\'><span sort=\'asc\' class=\'ui-grid-ico-sort ui-icon-asc"+iac+" ui-state-disabled ui-icon ui-icon-triangle-1-n ui-sort-"+dir+"\'></span>";\r\n
\t\timgs += "<span sort=\'desc\' class=\'ui-grid-ico-sort ui-icon-desc"+idc+" ui-state-disabled ui-icon ui-icon-triangle-1-s ui-sort-"+dir+"\'></span></span>";\r\n
\t\tfor(i=0;i<this.p.colNames.length;i++){\r\n
\t\t\tvar tooltip = ts.p.headertitles ? (" title=\\""+$.jgrid.stripHtml(ts.p.colNames[i])+"\\"") :"";\r\n
\t\t\tthead += "<th id=\'"+ts.p.id+"_"+ts.p.colModel[i].name+"\' role=\'columnheader\' class=\'ui-state-default ui-th-column ui-th-"+dir+"\'"+ tooltip+">";\r\n
\t\t\tidn = ts.p.colModel[i].index || ts.p.colModel[i].name;\r\n
\t\t\tthead += "<div id=\'jqgh_"+ts.p.id+"_"+ts.p.colModel[i].name+"\' "+tdc+">"+ts.p.colNames[i];\r\n
\t\t\tif(!ts.p.colModel[i].width)  { ts.p.colModel[i].width = 150; }\r\n
\t\t\telse { ts.p.colModel[i].width = parseInt(ts.p.colModel[i].width,10); }\r\n
\t\t\tif(typeof(ts.p.colModel[i].title) !== "boolean") { ts.p.colModel[i].title = true; }\r\n
\t\t\tif (idn == ts.p.sortname) {\r\n
\t\t\t\tts.p.lastsort = i;\r\n
\t\t\t}\r\n
\t\t\tthead += imgs+"</div></th>";\r\n
\t\t}\r\n
\t\tthead += "</tr></thead>";\r\n
\t\timgs = null;\r\n
\t\t$(this).append(thead);\r\n
\t\t$("thead tr:first th",this).hover(function(){$(this).addClass(\'ui-state-hover\');},function(){$(this).removeClass(\'ui-state-hover\');});\r\n
\t\tif(this.p.multiselect) {\r\n
\t\t\tvar emp=[], chk;\r\n
\t\t\t$(\'#cb_\'+$.jgrid.jqID(ts.p.id),this).bind(\'click\',function(){\r\n
\t\t\t\tts.p.selarrrow = [];\r\n
\t\t\t\tvar froz = ts.p.frozenColumns === true ? ts.p.id + "_frozen" : "";\r\n
\t\t\t\tif (this.checked) {\r\n
\t\t\t\t\t$(ts.rows).each(function(i) {\r\n
\t\t\t\t\t\tif (i>0) {\r\n
\t\t\t\t\t\t\tif(!$(this).hasClass("ui-subgrid") && !$(this).hasClass("jqgroup") && !$(this).hasClass(\'ui-state-disabled\')){\r\n
\t\t\t\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(ts.p.id)+"_"+$.jgrid.jqID(this.id) )[ts.p.useProp ? \'prop\': \'attr\']("checked",true);\r\n
\t\t\t\t\t\t\t\t$(this).addClass("ui-state-highlight").attr("aria-selected","true");  \r\n
\t\t\t\t\t\t\t\tts.p.selarrrow.push(this.id);\r\n
\t\t\t\t\t\t\t\tts.p.selrow = this.id;\r\n
\t\t\t\t\t\t\t\tif(froz) {\r\n
\t\t\t\t\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(ts.p.id)+"_"+$.jgrid.jqID(this.id), ts.grid.fbDiv )[ts.p.useProp ? \'prop\': \'attr\']("checked",true);\r\n
\t\t\t\t\t\t\t\t\t$("#"+$.jgrid.jqID(this.id), ts.grid.fbDiv).addClass("ui-state-highlight");\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tchk=true;\r\n
\t\t\t\t\temp=[];\r\n
\t\t\t\t}\r\n
\t\t\t\telse {\r\n
\t\t\t\t\t$(ts.rows).each(function(i) {\r\n
\t\t\t\t\t\tif(i>0) {\r\n
\t\t\t\t\t\t\tif(!$(this).hasClass("ui-subgrid") && !$(this).hasClass(\'ui-state-disabled\')){\r\n
\t\t\t\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(ts.p.id)+"_"+$.jgrid.jqID(this.id) )[ts.p.useProp ? \'prop\': \'attr\']("checked", false);\r\n
\t\t\t\t\t\t\t\t$(this).removeClass("ui-state-highlight").attr("aria-selected","false");\r\n
\t\t\t\t\t\t\t\temp.push(this.id);\r\n
\t\t\t\t\t\t\t\tif(froz) {\r\n
\t\t\t\t\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(ts.p.id)+"_"+$.jgrid.jqID(this.id), ts.grid.fbDiv )[ts.p.useProp ? \'prop\': \'attr\']("checked",false);\r\n
\t\t\t\t\t\t\t\t\t$("#"+$.jgrid.jqID(this.id), ts.grid.fbDiv).removeClass("ui-state-highlight");\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tts.p.selrow = null;\r\n
\t\t\t\t\tchk=false;\r\n
\t\t\t\t}\r\n
\t\t\t\t$(ts).triggerHandler("jqGridSelectAll", [chk ? ts.p.selarrrow : emp, chk]);\r\n
\t\t\t\tif($.isFunction(ts.p.onSelectAll)) {ts.p.onSelectAll.call(ts, chk ? ts.p.selarrrow : emp,chk);}\r\n
\t\t\t});\r\n
\t\t}\r\n
\r\n
\t\tif(ts.p.autowidth===true) {\r\n
\t\t\tvar pw = $(eg).innerWidth();\r\n
\t\t\tts.p.width = pw > 0?  pw: \'nw\';\r\n
\t\t}\r\n
\t\tsetColWidth();\r\n
\t\t$(eg).css("width",grid.width+"px").append("<div class=\'ui-jqgrid-resize-mark\' id=\'rs_m"+ts.p.id+"\'>&#160;</div>");\r\n
\t\t$(gv).css("width",grid.width+"px");\r\n
\t\tthead = $("thead:first",ts).get(0);\r\n
\t\tvar\ttfoot = "";\r\n
\t\tif(ts.p.footerrow) { tfoot += "<table role=\'grid\' style=\'width:"+ts.p.tblwidth+"px\' class=\'ui-jqgrid-ftable\' cellspacing=\'0\' cellpadding=\'0\' border=\'0\'><tbody><tr role=\'row\' class=\'ui-widget-content footrow footrow-"+dir+"\'>"; }\r\n
\t\tvar thr = $("tr:first",thead),\r\n
\t\tfirstr = "<tr class=\'jqgfirstrow\' role=\'row\' style=\'height:auto\'>";\r\n
\t\tts.p.disableClick=false;\r\n
\t\t$("th",thr).each(function ( j ) {\r\n
\t\t\tw = ts.p.colModel[j].width;\r\n
\t\t\tif(typeof ts.p.colModel[j].resizable === \'undefined\') {ts.p.colModel[j].resizable = true;}\r\n
\t\t\tif(ts.p.colModel[j].resizable){\r\n
\t\t\t\tres = document.createElement("span");\r\n
\t\t\t\t$(res).html("&#160;").addClass(\'ui-jqgrid-resize ui-jqgrid-resize-\'+dir);\r\n
\t\t\t\tif(!$.browser.opera) { $(res).css("cursor","col-resize"); }\r\n
\t\t\t\t$(this).addClass(ts.p.resizeclass);\r\n
\t\t\t} else {\r\n
\t\t\t\tres = "";\r\n
\t\t\t}\r\n
\t\t\t$(this).css("width",w+"px").prepend(res);\r\n
\t\t\tvar hdcol = "";\r\n
\t\t\tif( ts.p.colModel[j].hidden ) {\r\n
\t\t\t\t$(this).css("display","none");\r\n
\t\t\t\thdcol = "display:none;";\r\n
\t\t\t}\r\n
\t\t\tfirstr += "<td role=\'gridcell\' style=\'height:0px;width:"+w+"px;"+hdcol+"\'></td>";\r\n
\t\t\tgrid.headers[j] = { width: w, el: this };\r\n
\t\t\tsort = ts.p.colModel[j].sortable;\r\n
\t\t\tif( typeof sort !== \'boolean\') {ts.p.colModel[j].sortable =  true; sort=true;}\r\n
\t\t\tvar nm = ts.p.colModel[j].name;\r\n
\t\t\tif( !(nm == \'cb\' || nm==\'subgrid\' || nm==\'rn\') ) {\r\n
\t\t\t\tif(ts.p.viewsortcols[2]){\r\n
\t\t\t\t\t$(">div",this).addClass(\'ui-jqgrid-sortable\');\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(sort) {\r\n
\t\t\t\tif(ts.p.viewsortcols[0]) {$("div span.s-ico",this).show(); if(j==ts.p.lastsort){ $("div span.ui-icon-"+ts.p.sortorder,this).removeClass("ui-state-disabled");}}\r\n
\t\t\t\telse if( j == ts.p.lastsort) {$("div span.s-ico",this).show();$("div span.ui-icon-"+ts.p.sortorder,this).removeClass("ui-state-disabled");}\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.footerrow) { tfoot += "<td role=\'gridcell\' "+formatCol(j,0,\'\', null, \'\', false)+">&#160;</td>"; }\r\n
\t\t}).mousedown(function(e) {\r\n
\t\t\tif ($(e.target).closest("th>span.ui-jqgrid-resize").length != 1) { return; }\r\n
\t\t\tvar ci = getColumnHeaderIndex(this);\r\n
\t\t\tif(ts.p.forceFit===true) {ts.p.nv= nextVisible(ci);}\r\n
\t\t\tgrid.dragStart(ci, e, getOffset(ci));\r\n
\t\t\treturn false;\r\n
\t\t}).click(function(e) {\r\n
\t\t\tif (ts.p.disableClick) {\r\n
\t\t\t\tts.p.disableClick = false;\r\n
\t\t\t\treturn false;\r\n
\t\t\t}\r\n
\t\t\tvar s = "th>div.ui-jqgrid-sortable",r,d;\r\n
\t\t\tif (!ts.p.viewsortcols[2]) { s = "th>div>span>span.ui-grid-ico-sort"; }\r\n
\t\t\tvar t = $(e.target).closest(s);\r\n
\t\t\tif (t.length != 1) { return; }\r\n
\t\t\tvar ci = getColumnHeaderIndex(this);\r\n
\t\t\tif (!ts.p.viewsortcols[2]) { r=true;d=t.attr("sort"); }\r\n
\t\t\tsortData( $(\'div\',this)[0].id, ci, r, d);\r\n
\t\t\treturn false;\r\n
\t\t});\r\n
\t\tif (ts.p.sortable && $.fn.sortable) {\r\n
\t\t\ttry {\r\n
\t\t\t\t$(ts).jqGrid("sortableColumns", thr);\r\n
\t\t\t} catch (e){}\r\n
\t\t}\r\n
\t\tif(ts.p.footerrow) { tfoot += "</tr></tbody></table>"; }\r\n
\t\tfirstr += "</tr>";\r\n
\t\ttbody = document.createElement("tbody");\r\n
\t\tthis.appendChild(tbody);\r\n
\t\t$(this).addClass(\'ui-jqgrid-btable\').append(firstr);\r\n
\t\tfirstr = null;\r\n
\t\tvar hTable = $("<table class=\'ui-jqgrid-htable\' style=\'width:"+ts.p.tblwidth+"px\' role=\'grid\' aria-labelledby=\'gbox_"+this.id+"\' cellspacing=\'0\' cellpadding=\'0\' border=\'0\'></table>").append(thead),\r\n
\t\thg = (ts.p.caption && ts.p.hiddengrid===true) ? true : false,\r\n
\t\thb = $("<div class=\'ui-jqgrid-hbox" + (dir=="rtl" ? "-rtl" : "" )+"\'></div>");\r\n
\t\tthead = null;\r\n
\t\tgrid.hDiv = document.createElement("div");\r\n
\t\t$(grid.hDiv)\r\n
\t\t\t.css({ width: grid.width+"px"})\r\n
\t\t\t.addClass("ui-state-default ui-jqgrid-hdiv")\r\n
\t\t\t.append(hb);\r\n
\t\t$(hb).append(hTable);\r\n
\t\thTable = null;\r\n
\t\tif(hg) { $(grid.hDiv).hide(); }\r\n
\t\tif(ts.p.pager){\r\n
\t\t\t// TBD -- escape ts.p.pager here?\r\n
\t\t\tif(typeof ts.p.pager == "string") {if(ts.p.pager.substr(0,1) !="#") { ts.p.pager = "#"+ts.p.pager;} }\r\n
\t\t\telse { ts.p.pager = "#"+ $(ts.p.pager).attr("id");}\r\n
\t\t\t$(ts.p.pager).css({width: grid.width+"px"}).appendTo(eg).addClass(\'ui-state-default ui-jqgrid-pager ui-corner-bottom\');\r\n
\t\t\tif(hg) {$(ts.p.pager).hide();}\r\n
\t\t\tsetPager(ts.p.pager,\'\');\r\n
\t\t}\r\n
\t\tif( ts.p.cellEdit === false && ts.p.hoverrows === true) {\r\n
\t\t$(ts).bind(\'mouseover\',function(e) {\r\n
\t\t\tptr = $(e.target).closest("tr.jqgrow");\r\n
\t\t\tif($(ptr).attr("class") !== "ui-subgrid") {\r\n
\t\t\t\t$(ptr).addClass("ui-state-hover");\r\n
\t\t\t}\r\n
\t\t}).bind(\'mouseout\',function(e) {\r\n
\t\t\tptr = $(e.target).closest("tr.jqgrow");\r\n
\t\t\t$(ptr).removeClass("ui-state-hover");\r\n
\t\t});\r\n
\t\t}\r\n
\t\tvar ri,ci, tdHtml;\r\n
\t\t$(ts).before(grid.hDiv).click(function(e) {\r\n
\t\t\ttd = e.target;\r\n
\t\t\tptr = $(td,ts.rows).closest("tr.jqgrow");\r\n
\t\t\tif($(ptr).length === 0 || ptr[0].className.indexOf( \'ui-state-disabled\' ) > -1 || ($(td,ts).closest("table.ui-jqgrid-btable").attr(\'id\') || \'\').replace("_frozen","") !== ts.id ) {\r\n
\t\t\t\treturn this;\r\n
\t\t\t}\r\n
\t\t\tvar scb = $(td).hasClass("cbox"),\r\n
\t\t\tcSel = $(ts).triggerHandler("jqGridBeforeSelectRow", [ptr[0].id, e]);\r\n
\t\t\tcSel = (cSel === false || cSel === \'stop\') ? false : true;\r\n
\t\t\tif(cSel && $.isFunction(ts.p.beforeSelectRow)) { cSel = ts.p.beforeSelectRow.call(ts,ptr[0].id, e); }\r\n
\t\t\tif (td.tagName == \'A\' || ((td.tagName == \'INPUT\' || td.tagName == \'TEXTAREA\' || td.tagName == \'OPTION\' || td.tagName == \'SELECT\' ) && !scb) ) { return; }\r\n
\t\t\tif(cSel === true) {\r\n
\t\t\t\tri = ptr[0].id;\r\n
\t\t\t\tci = $.jgrid.getCellIndex(td);\r\n
\t\t\t\ttdHtml = $(td).closest("td,th").html();\r\n
\t\t\t\t$(ts).triggerHandler("jqGridCellSelect", [ri,ci,tdHtml,e]);\r\n
\t\t\t\tif($.isFunction(ts.p.onCellSelect)) {\r\n
\t\t\t\t\tts.p.onCellSelect.call(ts,ri,ci,tdHtml,e);\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ts.p.cellEdit === true) {\r\n
\t\t\t\t\tif(ts.p.multiselect && scb){\r\n
\t\t\t\t\t\t$(ts).jqGrid("setSelection", ri ,true,e);\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tri = ptr[0].rowIndex;\r\n
\t\t\t\t\t\ttry {$(ts).jqGrid("editCell",ri,ci,true);} catch (_) {}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else if ( !ts.p.multikey ) {\r\n
\t\t\t\t\tif(ts.p.multiselect && ts.p.multiboxonly) {\r\n
\t\t\t\t\t\tif(scb){$(ts).jqGrid("setSelection",ri,true,e);}\r\n
\t\t\t\t\t\telse {\r\n
\t\t\t\t\t\t\tvar frz = ts.p.frozenColumns ? ts.p.id+"_frozen" : "";\r\n
\t\t\t\t\t\t\t$(ts.p.selarrrow).each(function(i,n){\r\n
\t\t\t\t\t\t\t\tvar ind = ts.rows.namedItem(n);\r\n
\t\t\t\t\t\t\t\t$(ind).removeClass("ui-state-highlight");\r\n
\t\t\t\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(ts.p.id)+"_"+$.jgrid.jqID(n))[ts.p.useProp ? \'prop\': \'attr\']("checked", false);\r\n
\t\t\t\t\t\t\t\tif(frz) {\r\n
\t\t\t\t\t\t\t\t\t$("#"+$.jgrid.jqID(n), "#"+$.jgrid.jqID(frz)).removeClass("ui-state-highlight");\r\n
\t\t\t\t\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(ts.p.id)+"_"+$.jgrid.jqID(n), "#"+$.jgrid.jqID(frz))[ts.p.useProp ? \'prop\': \'attr\']("checked", false);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\tts.p.selarrrow = [];\r\n
\t\t\t\t\t\t\t$(ts).jqGrid("setSelection",ri,true,e);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$(ts).jqGrid("setSelection",ri,true,e);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tif(e[ts.p.multikey]) {\r\n
\t\t\t\t\t\t$(ts).jqGrid("setSelection",ri,true,e);\r\n
\t\t\t\t\t} else if(ts.p.multiselect && scb) {\r\n
\t\t\t\t\t\tscb = $("#jqg_"+$.jgrid.jqID(ts.p.id)+"_"+ri).is(":checked");\r\n
\t\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(ts.p.id)+"_"+ri)[ts.p.useProp ? \'prop\' : \'attr\']("checked", scb);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}).bind(\'reloadGrid\', function(e,opts) {\r\n
\t\t\tif(ts.p.treeGrid ===true) {\tts.p.datatype = ts.p.treedatatype;}\r\n
\t\t\tif (opts && opts.current) {\r\n
\t\t\t\tts.grid.selectionPreserver(ts);\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.datatype=="local"){ $(ts).jqGrid("resetSelection");  if(ts.p.data.length) { refreshIndex();} }\r\n
\t\t\telse if(!ts.p.treeGrid) {\r\n
\t\t\t\tts.p.selrow=null;\r\n
\t\t\t\tif(ts.p.multiselect) {ts.p.selarrrow =[];setHeadCheckBox(false);}\r\n
\t\t\t\tts.p.savedRow = [];\r\n
\t\t\t}\r\n
\t\t\tif(ts.p.scroll) {emptyRows.call(ts, true, false);}\r\n
\t\t\tif (opts && opts.page) {\r\n
\t\t\t\tvar page = opts.page;\r\n
\t\t\t\tif (page > ts.p.lastpage) { page = ts.p.lastpage; }\r\n
\t\t\t\tif (page < 1) { page = 1; }\r\n
\t\t\t\tts.p.page = page;\r\n
\t\t\t\tif (ts.grid.prevRowHeight) {\r\n
\t\t\t\t\tts.grid.bDiv.scrollTop = (page - 1) * ts.grid.prevRowHeight * ts.p.rowNum;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tts.grid.bDiv.scrollTop = 0;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif (ts.grid.prevRowHeight && ts.p.scroll) {\r\n
\t\t\t\tdelete ts.p.lastpage;\r\n
\t\t\t\tts.grid.populateVisible();\r\n
\t\t\t} else {\r\n
\t\t\t\tts.grid.populate();\r\n
\t\t\t}\r\n
\t\t\tif(ts.p._inlinenav===true) {$(ts).jqGrid(\'showAddEditButtons\');}\r\n
\t\t\treturn false;\r\n
\t\t})\r\n
\t\t.dblclick(function(e) {\r\n
\t\t\ttd = e.target;\r\n
\t\t\tptr = $(td,ts.rows).closest("tr.jqgrow");\r\n
\t\t\tif($(ptr).length === 0 ){return;}\r\n
\t\t\tri = ptr[0].rowIndex;\r\n
\t\t\tci = $.jgrid.getCellIndex(td);\r\n
\t\t\t$(ts).triggerHandler("jqGridDblClickRow", [$(ptr).attr("id"),ri,ci,e]);\r\n
\t\t\tif ($.isFunction(this.p.ondblClickRow)) { ts.p.ondblClickRow.call(ts,$(ptr).attr("id"),ri,ci, e); }\r\n
\t\t})\r\n
\t\t.bind(\'contextmenu\', function(e) {\r\n
\t\t\ttd = e.target;\r\n
\t\t\tptr = $(td,ts.rows).closest("tr.jqgrow");\r\n
\t\t\tif($(ptr).length === 0 ){return;}\r\n
\t\t\tif(!ts.p.multiselect) {\t$(ts).jqGrid("setSelection",ptr[0].id,true,e);\t}\r\n
\t\t\tri = ptr[0].rowIndex;\r\n
\t\t\tci = $.jgrid.getCellIndex(td);\r\n
\t\t\t$(ts).triggerHandler("jqGridRightClickRow", [$(ptr).attr("id"),ri,ci,e]);\r\n
\t\t\tif ($.isFunction(this.p.onRightClickRow)) { ts.p.onRightClickRow.call(ts,$(ptr).attr("id"),ri,ci, e); }\r\n
\t\t});\r\n
\t\tgrid.bDiv = document.createElement("div");\r\n
\t\tif(isMSIE) { if(String(ts.p.height).toLowerCase() === "auto") { ts.p.height = "100%"; } }\r\n
\t\t$(grid.bDiv)\r\n
\t\t\t.append($(\'<div style="position:relative;\'+(isMSIE && $.browser.version < 8 ? "height:0.01%;" : "")+\'"></div>\').append(\'<div></div>\').append(this))\r\n
\t\t\t.addClass("ui-jqgrid-bdiv")\r\n
\t\t\t.css({ height: ts.p.height+(isNaN(ts.p.height)?"":"px"), width: (grid.width)+"px"})\r\n
\t\t\t.scroll(grid.scrollGrid);\r\n
\t\t$("table:first",grid.bDiv).css({width:ts.p.tblwidth+"px"});\r\n
\t\tif( isMSIE ) {\r\n
\t\t\tif( $("tbody",this).length == 2 ) { $("tbody:gt(0)",this).remove();}\r\n
\t\t\tif( ts.p.multikey) {$(grid.bDiv).bind("selectstart",function(){return false;});}\r\n
\t\t} else {\r\n
\t\t\tif( ts.p.multikey) {$(grid.bDiv).bind("mousedown",function(){return false;});}\r\n
\t\t}\r\n
\t\tif(hg) {$(grid.bDiv).hide();}\r\n
\t\tgrid.cDiv = document.createElement("div");\r\n
\t\tvar arf = ts.p.hidegrid===true ? $("<a role=\'link\' href=\'javascript:void(0)\'/>").addClass(\'ui-jqgrid-titlebar-close HeaderButton\').hover(\r\n
\t\t\tfunction(){ arf.addClass(\'ui-state-hover\');},\r\n
\t\t\tfunction() {arf.removeClass(\'ui-state-hover\');})\r\n
\t\t.append("<span class=\'ui-icon ui-icon-circle-triangle-n\'></span>").css((dir=="rtl"?"left":"right"),"0px") : "";\r\n
\t\t$(grid.cDiv).append(arf).append("<span class=\'ui-jqgrid-title"+(dir=="rtl" ? "-rtl" :"" )+"\'>"+ts.p.caption+"</span>")\r\n
\t\t.addClass("ui-jqgrid-titlebar ui-widget-header ui-corner-top ui-helper-clearfix");\r\n
\t\t$(grid.cDiv).insertBefore(grid.hDiv);\r\n
\t\tif( ts.p.toolbar[0] ) {\r\n
\t\t\tgrid.uDiv = document.createElement("div");\r\n
\t\t\tif(ts.p.toolbar[1] == "top") {$(grid.uDiv).insertBefore(grid.hDiv);}\r\n
\t\t\telse if (ts.p.toolbar[1]=="bottom" ) {$(grid.uDiv).insertAfter(grid.hDiv);}\r\n
\t\t\tif(ts.p.toolbar[1]=="both") {\r\n
\t\t\t\tgrid.ubDiv = document.createElement("div");\r\n
\t\t\t\t$(grid.uDiv).insertBefore(grid.hDiv).addClass("ui-userdata ui-state-default").attr("id","t_"+this.id);\r\n
\t\t\t\t$(grid.ubDiv).insertAfter(grid.hDiv).addClass("ui-userdata ui-state-default").attr("id","tb_"+this.id);\r\n
\t\t\t\tif(hg)  {$(grid.ubDiv).hide();}\r\n
\t\t\t} else {\r\n
\t\t\t\t$(grid.uDiv).width(grid.width).addClass("ui-userdata ui-state-default").attr("id","t_"+this.id);\r\n
\t\t\t}\r\n
\t\t\tif(hg) {$(grid.uDiv).hide();}\r\n
\t\t}\r\n
\t\tif(ts.p.toppager) {\r\n
\t\t\tts.p.toppager = $.jgrid.jqID(ts.p.id)+"_toppager";\r\n
\t\t\tgrid.topDiv = $("<div id=\'"+ts.p.toppager+"\'></div>")[0];\r\n
\t\t\tts.p.toppager = "#"+ts.p.toppager;\r\n
\t\t\t$(grid.topDiv).insertBefore(grid.hDiv).addClass(\'ui-state-default ui-jqgrid-toppager\').width(grid.width);\r\n
\t\t\tsetPager(ts.p.toppager,\'_t\');\r\n
\t\t}\r\n
\t\tif(ts.p.footerrow) {\r\n
\t\t\tgrid.sDiv = $("<div class=\'ui-jqgrid-sdiv\'></div>")[0];\r\n
\t\t\thb = $("<div class=\'ui-jqgrid-hbox"+(dir=="rtl"?"-rtl":"")+"\'></div>");\r\n
\t\t\t$(grid.sDiv).append(hb).insertAfter(grid.hDiv).width(grid.width);\r\n
\t\t\t$(hb).append(tfoot);\r\n
\t\t\tgrid.footers = $(".ui-jqgrid-ftable",grid.sDiv)[0].rows[0].cells;\r\n
\t\t\tif(ts.p.rownumbers) { grid.footers[0].className = \'ui-state-default jqgrid-rownum\'; }\r\n
\t\t\tif(hg) {$(grid.sDiv).hide();}\r\n
\t\t}\r\n
\t\thb = null;\r\n
\t\tif(ts.p.caption) {\r\n
\t\t\tvar tdt = ts.p.datatype;\r\n
\t\t\tif(ts.p.hidegrid===true) {\r\n
\t\t\t\t$(".ui-jqgrid-titlebar-close",grid.cDiv).click( function(e){\r\n
\t\t\t\t\tvar onHdCl = $.isFunction(ts.p.onHeaderClick),\r\n
\t\t\t\t\telems = ".ui-jqgrid-bdiv, .ui-jqgrid-hdiv, .ui-jqgrid-pager, .ui-jqgrid-sdiv",\r\n
\t\t\t\t\tcounter, self = this;\r\n
\t\t\t\t\tif(ts.p.toolbar[0]===true) {\r\n
\t\t\t\t\t\tif( ts.p.toolbar[1]==\'both\') {\r\n
\t\t\t\t\t\t\telems += \', #\' + $(grid.ubDiv).attr(\'id\');\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\telems += \', #\' + $(grid.uDiv).attr(\'id\');\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tcounter = $(elems,"#gview_"+$.jgrid.jqID(ts.p.id)).length;\r\n
\r\n
\t\t\t\t\tif(ts.p.gridstate == \'visible\') {\r\n
\t\t\t\t\t\t$(elems,"#gbox_"+$.jgrid.jqID(ts.p.id)).slideUp("fast", function() {\r\n
\t\t\t\t\t\t\tcounter--;\r\n
\t\t\t\t\t\t\tif (counter === 0) {\r\n
\t\t\t\t\t\t\t\t$("span",self).removeClass("ui-icon-circle-triangle-n").addClass("ui-icon-circle-triangle-s");\r\n
\t\t\t\t\t\t\t\tts.p.gridstate = \'hidden\';\r\n
\t\t\t\t\t\t\t\tif($("#gbox_"+$.jgrid.jqID(ts.p.id)).hasClass("ui-resizable")) { $(".ui-resizable-handle","#gbox_"+$.jgrid.jqID(ts.p.id)).hide(); }\r\n
\t\t\t\t\t\t\t\t$(ts).triggerHandler("jqGridHeaderClick", [ts.p.gridstate,e]);\r\n
\t\t\t\t\t\t\t\tif(onHdCl) {if(!hg) {ts.p.onHeaderClick.call(ts,ts.p.gridstate,e);}}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t} else if(ts.p.gridstate == \'hidden\'){\r\n
\t\t\t\t\t\t$(elems,"#gbox_"+$.jgrid.jqID(ts.p.id)).slideDown("fast", function() {\r\n
\t\t\t\t\t\t\tcounter--;\r\n
\t\t\t\t\t\t\tif (counter === 0) {\r\n
\t\t\t\t\t\t\t\t$("span",self).removeClass("ui-icon-circle-triangle-s").addClass("ui-icon-circle-triangle-n");\r\n
\t\t\t\t\t\t\t\tif(hg) {ts.p.datatype = tdt;populate();hg=false;}\r\n
\t\t\t\t\t\t\t\tts.p.gridstate = \'visible\';\r\n
\t\t\t\t\t\t\t\tif($("#gbox_"+$.jgrid.jqID(ts.p.id)).hasClass("ui-resizable")) { $(".ui-resizable-handle","#gbox_"+$.jgrid.jqID(ts.p.id)).show(); }\r\n
\t\t\t\t\t\t\t\t$(ts).triggerHandler("jqGridHeaderClick", [ts.p.gridstate,e]);\r\n
\t\t\t\t\t\t\t\tif(onHdCl) {if(!hg) {ts.p.onHeaderClick.call(ts,ts.p.gridstate,e);}}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\tif(hg) {ts.p.datatype="local"; $(".ui-jqgrid-titlebar-close",grid.cDiv).trigger("click");}\r\n
\t\t\t}\r\n
\t\t} else {$(grid.cDiv).hide();}\r\n
\t\t$(grid.hDiv).after(grid.bDiv)\r\n
\t\t.mousemove(function (e) {\r\n
\t\t\tif(grid.resizing){grid.dragMove(e);return false;}\r\n
\t\t});\r\n
\t\t$(".ui-jqgrid-labels",grid.hDiv).bind("selectstart", function () { return false; });\r\n
\t\t$(document).mouseup(function () {\r\n
\t\t\tif(grid.resizing) {\tgrid.dragEnd(); return false;}\r\n
\t\t\treturn true;\r\n
\t\t});\r\n
\t\tts.formatCol = formatCol;\r\n
\t\tts.sortData = sortData;\r\n
\t\tts.updatepager = updatepager;\r\n
\t\tts.refreshIndex = refreshIndex;\r\n
\t\tts.setHeadCheckBox = setHeadCheckBox;\r\n
\t\tts.constructTr = constructTr;\r\n
\t\tts.formatter = function ( rowId, cellval , colpos, rwdat, act){return formatter(rowId, cellval , colpos, rwdat, act);};\r\n
\t\t$.extend(grid,{populate : populate, emptyRows: emptyRows});\r\n
\t\tthis.grid = grid;\r\n
\t\tts.addXmlData = function(d) {addXmlData(d,ts.grid.bDiv);};\r\n
\t\tts.addJSONData = function(d) {addJSONData(d,ts.grid.bDiv);};\r\n
\t\tthis.grid.cols = this.rows[0].cells;\r\n
\r\n
\t\tpopulate();ts.p.hiddengrid=false;\r\n
\t});\r\n
};\r\n
$.jgrid.extend({\r\n
\tgetGridParam : function(pName) {\r\n
\t\tvar $t = this[0];\r\n
\t\tif (!$t || !$t.grid) {return;}\r\n
\t\tif (!pName) { return $t.p; }\r\n
\t\telse {return typeof($t.p[pName]) != "undefined" ? $t.p[pName] : null;}\r\n
\t},\r\n
\tsetGridParam : function (newParams){\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif (this.grid && typeof(newParams) === \'object\') {$.extend(true,this.p,newParams);}\r\n
\t\t});\r\n
\t},\r\n
\tgetDataIDs : function () {\r\n
\t\tvar ids=[], i=0, len, j=0;\r\n
\t\tthis.each(function(){\r\n
\t\t\tlen = this.rows.length;\r\n
\t\t\tif(len && len>0){\r\n
\t\t\t\twhile(i<len) {\r\n
\t\t\t\t\tif($(this.rows[i]).hasClass(\'jqgrow\')) {\r\n
\t\t\t\t\t\tids[j] = this.rows[i].id;\r\n
\t\t\t\t\t\tj++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\ti++;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn ids;\r\n
\t},\r\n
\tsetSelection : function(selection,onsr, e) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this, stat,pt, ner, ia, tpsr, fid;\r\n
\t\t\tif(selection === undefined) { return; }\r\n
\t\t\tonsr = onsr === false ? false : true;\r\n
\t\t\tpt=$t.rows.namedItem(selection+"");\r\n
\t\t\tif(!pt || !pt.className || pt.className.indexOf( \'ui-state-disabled\' ) > -1 ) { return; }\r\n
\t\t\tfunction scrGrid(iR){\r\n
\t\t\t\tvar ch = $($t.grid.bDiv)[0].clientHeight,\r\n
\t\t\t\tst = $($t.grid.bDiv)[0].scrollTop,\r\n
\t\t\t\trpos = $($t.rows[iR]).position().top,\r\n
\t\t\t\trh = $t.rows[iR].clientHeight;\r\n
\t\t\t\tif(rpos+rh >= ch+st) { $($t.grid.bDiv)[0].scrollTop = rpos-(ch+st)+rh+st; }\r\n
\t\t\t\telse if(rpos < ch+st) {\r\n
\t\t\t\t\tif(rpos < st) {\r\n
\t\t\t\t\t\t$($t.grid.bDiv)[0].scrollTop = rpos;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif($t.p.scrollrows===true) {\r\n
\t\t\t\tner = $t.rows.namedItem(selection).rowIndex;\r\n
\t\t\t\tif(ner >=0 ){\r\n
\t\t\t\t\tscrGrid(ner);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif($t.p.frozenColumns === true ) {\r\n
\t\t\t\tfid = $t.p.id+"_frozen";\r\n
\t\t\t}\r\n
\t\t\tif(!$t.p.multiselect) {\t\r\n
\t\t\t\tif(pt.className !== "ui-subgrid") {\r\n
\t\t\t\t\tif( $t.p.selrow != pt.id) {\r\n
\t\t\t\t\t\t$($t.rows.namedItem($t.p.selrow)).removeClass("ui-state-highlight").attr({"aria-selected":"false", "tabindex" : "-1"});\r\n
\t\t\t\t\t\t$(pt).addClass("ui-state-highlight").attr({"aria-selected":"true", "tabindex" : "0"});//.focus();\r\n
\t\t\t\t\t\tif(fid) {\r\n
\t\t\t\t\t\t\t$("#"+$.jgrid.jqID($t.p.selrow), "#"+$.jgrid.jqID(fid)).removeClass("ui-state-highlight");\r\n
\t\t\t\t\t\t\t$("#"+$.jgrid.jqID(selection), "#"+$.jgrid.jqID(fid)).addClass("ui-state-highlight");\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tstat = true;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tstat = false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$t.p.selrow = pt.id;\r\n
\t\t\t\t\t$($t).triggerHandler("jqGridSelectRow", [pt.id, stat, e]);\r\n
\t\t\t\t\tif( $t.p.onSelectRow && onsr) { $t.p.onSelectRow.call($t, pt.id, stat, e); }\r\n
\t\t\t\t}\r\n
\t\t\t} else {\r\n
\t\t\t\t//unselect selectall checkbox when deselecting a specific row\r\n
\t\t\t\t$t.setHeadCheckBox( false );\r\n
\t\t\t\t$t.p.selrow = pt.id;\r\n
\t\t\t\tia = $.inArray($t.p.selrow,$t.p.selarrrow);\r\n
\t\t\t\tif (  ia === -1 ){\r\n
\t\t\t\t\tif(pt.className !== "ui-subgrid") { $(pt).addClass("ui-state-highlight").attr("aria-selected","true");}\r\n
\t\t\t\t\tstat = true;\r\n
\t\t\t\t\t$t.p.selarrrow.push($t.p.selrow);\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tif(pt.className !== "ui-subgrid") { $(pt).removeClass("ui-state-highlight").attr("aria-selected","false");}\r\n
\t\t\t\t\tstat = false;\r\n
\t\t\t\t\t$t.p.selarrrow.splice(ia,1);\r\n
\t\t\t\t\ttpsr = $t.p.selarrrow[0];\r\n
\t\t\t\t\t$t.p.selrow = (tpsr === undefined) ? null : tpsr;\r\n
\t\t\t\t}\r\n
\t\t\t\t$("#jqg_"+$.jgrid.jqID($t.p.id)+"_"+$.jgrid.jqID(pt.id))[$t.p.useProp ? \'prop\': \'attr\']("checked",stat);\r\n
\t\t\t\tif(fid) {\r\n
\t\t\t\t\tif(ia === -1) {\r\n
\t\t\t\t\t\t$("#"+$.jgrid.jqID(selection), "#"+$.jgrid.jqID(fid)).addClass("ui-state-highlight");\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$("#"+$.jgrid.jqID(selection), "#"+$.jgrid.jqID(fid)).removeClass("ui-state-highlight");\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$("#jqg_"+$.jgrid.jqID($t.p.id)+"_"+$.jgrid.jqID(selection), "#"+$.jgrid.jqID(fid))[$t.p.useProp ? \'prop\': \'attr\']("checked",stat);\r\n
\t\t\t\t}\r\n
\t\t\t\t$($t).triggerHandler("jqGridSelectRow", [pt.id, stat, e]);\r\n
\t\t\t\tif( $t.p.onSelectRow && onsr) { $t.p.onSelectRow.call($t, pt.id , stat, e); }\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tresetSelection : function( rowid ){\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar t = this, ind, sr, fid;\r\n
\t\t\tif( t.p.frozenColumns === true ) {\r\n
\t\t\t\tfid = t.p.id+"_frozen";\r\n
\t\t\t}\r\n
\t\t\tif(typeof(rowid) !== "undefined" ) {\r\n
\t\t\t\tsr = rowid === t.p.selrow ? t.p.selrow : rowid;\r\n
\t\t\t\t$("#"+$.jgrid.jqID(t.p.id)+" tbody:first tr#"+$.jgrid.jqID(sr)).removeClass("ui-state-highlight").attr("aria-selected","false");\r\n
\t\t\t\tif (fid) { $("#"+$.jgrid.jqID(sr), "#"+$.jgrid.jqID(fid)).removeClass("ui-state-highlight"); }\r\n
\t\t\t\tif(t.p.multiselect) {\r\n
\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(t.p.id)+"_"+$.jgrid.jqID(sr), "#"+$.jgrid.jqID(t.p.id))[t.p.useProp ? \'prop\': \'attr\']("checked",false);\r\n
\t\t\t\t\tif(fid) { $("#jqg_"+$.jgrid.jqID(t.p.id)+"_"+$.jgrid.jqID(sr), "#"+$.jgrid.jqID(fid))[t.p.useProp ? \'prop\': \'attr\']("checked",false); }\r\n
\t\t\t\t\tt.setHeadCheckBox( false);\r\n
\t\t\t\t}\r\n
\t\t\t\tsr = null;\r\n
\t\t\t} else if(!t.p.multiselect) {\r\n
\t\t\t\tif(t.p.selrow) {\r\n
\t\t\t\t\t$("#"+$.jgrid.jqID(t.p.id)+" tbody:first tr#"+$.jgrid.jqID(t.p.selrow)).removeClass("ui-state-highlight").attr("aria-selected","false");\r\n
\t\t\t\t\tif(fid) { $("#"+$.jgrid.jqID(t.p.selrow), "#"+$.jgrid.jqID(fid)).removeClass("ui-state-highlight"); }\r\n
\t\t\t\t\tt.p.selrow = null;\r\n
\t\t\t\t}\r\n
\t\t\t} else {\r\n
\t\t\t\t$(t.p.selarrrow).each(function(i,n){\r\n
\t\t\t\t\tind = t.rows.namedItem(n);\r\n
\t\t\t\t\t$(ind).removeClass("ui-state-highlight").attr("aria-selected","false");\r\n
\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(t.p.id)+"_"+$.jgrid.jqID(n))[t.p.useProp ? \'prop\': \'attr\']("checked",false);\r\n
\t\t\t\t\tif(fid) { \r\n
\t\t\t\t\t\t$("#"+$.jgrid.jqID(n), "#"+$.jgrid.jqID(fid)).removeClass("ui-state-highlight"); \r\n
\t\t\t\t\t\t$("#jqg_"+$.jgrid.jqID(t.p.id)+"_"+$.jgrid.jqID(n), "#"+$.jgrid.jqID(fid))[t.p.useProp ? \'prop\': \'attr\']("checked",false);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tt.setHeadCheckBox( false );\r\n
\t\t\t\tt.p.selarrrow = [];\r\n
\t\t\t}\r\n
\t\t\tif(t.p.cellEdit === true) {\r\n
\t\t\t\tif(parseInt(t.p.iCol,10)>=0  && parseInt(t.p.iRow,10)>=0) {\r\n
\t\t\t\t\t$("td:eq("+t.p.iCol+")",t.rows[t.p.iRow]).removeClass("edit-cell ui-state-highlight");\r\n
\t\t\t\t\t$(t.rows[t.p.iRow]).removeClass("selected-row ui-state-hover");\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tt.p.savedRow = [];\r\n
\t\t});\r\n
\t},\r\n
\tgetRowData : function( rowid ) {\r\n
\t\tvar res = {}, resall, getall=false, len, j=0;\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this,nm,ind;\r\n
\t\t\tif(typeof(rowid) == \'undefined\') {\r\n
\t\t\t\tgetall = true;\r\n
\t\t\t\tresall = [];\r\n
\t\t\t\tlen = $t.rows.length;\r\n
\t\t\t} else {\r\n
\t\t\t\tind = $t.rows.namedItem(rowid);\r\n
\t\t\t\tif(!ind) { return res; }\r\n
\t\t\t\tlen = 2;\r\n
\t\t\t}\r\n
\t\t\twhile(j<len){\r\n
\t\t\t\tif(getall) { ind = $t.rows[j]; }\r\n
\t\t\t\tif( $(ind).hasClass(\'jqgrow\') ) {\r\n
\t\t\t\t\t$(\'td[role="gridcell"]\',ind).each( function(i) {\r\n
\t\t\t\t\t\tnm = $t.p.colModel[i].name;\r\n
\t\t\t\t\t\tif ( nm !== \'cb\' && nm !== \'subgrid\' && nm !== \'rn\') {\r\n
\t\t\t\t\t\t\tif($t.p.treeGrid===true && nm == $t.p.ExpandColumn) {\r\n
\t\t\t\t\t\t\t\tres[nm] = $.jgrid.htmlDecode($("span:first",this).html());\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\tres[nm] = $.unformat.call($t,this,{rowId:ind.id, colModel:$t.p.colModel[i]},i);\r\n
\t\t\t\t\t\t\t\t} catch (e){\r\n
\t\t\t\t\t\t\t\t\tres[nm] = $.jgrid.htmlDecode($(this).html());\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tif(getall) { resall.push(res); res={}; }\r\n
\t\t\t\t}\r\n
\t\t\t\tj++;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn resall ? resall: res;\r\n
\t},\r\n
\tdelRowData : function(rowid) {\r\n
\t\tvar success = false, rowInd, ia, ri;\r\n
\t\tthis.each(function() {\r\n
\t\t\tvar $t = this;\r\n
\t\t\trowInd = $t.rows.namedItem(rowid);\r\n
\t\t\tif(!rowInd) {return false;}\r\n
\t\t\telse {\r\n
\t\t\t\tri = rowInd.rowIndex;\r\n
\t\t\t\t$(rowInd).remove();\r\n
\t\t\t\t$t.p.records--;\r\n
\t\t\t\t$t.p.reccount--;\r\n
\t\t\t\t$t.updatepager(true,false);\r\n
\t\t\t\tsuccess=true;\r\n
\t\t\t\tif($t.p.multiselect) {\r\n
\t\t\t\t\tia = $.inArray(rowid,$t.p.selarrrow);\r\n
\t\t\t\t\tif(ia != -1) { $t.p.selarrrow.splice(ia,1);}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(rowid == $t.p.selrow) {$t.p.selrow=null;}\r\n
\t\t\t}\r\n
\t\t\tif($t.p.datatype == \'local\') {\r\n
\t\t\t\tvar id = $.jgrid.stripPref($t.p.idPrefix, rowid),\r\n
\t\t\t\tpos = $t.p._index[id];\r\n
\t\t\t\tif(typeof(pos) != \'undefined\') {\r\n
\t\t\t\t\t$t.p.data.splice(pos,1);\r\n
\t\t\t\t\t$t.refreshIndex();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif( $t.p.altRows === true && success ) {\r\n
\t\t\t\tvar cn = $t.p.altclass;\r\n
\t\t\t\t$($t.rows).each(function(i){\r\n
\t\t\t\t\tif(i % 2 ==1) { $(this).addClass(cn); }\r\n
\t\t\t\t\telse { $(this).removeClass(cn); }\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn success;\r\n
\t},\r\n
\tsetRowData : function(rowid, data, cssp) {\r\n
\t\tvar nm, success=true, title;\r\n
\t\tthis.each(function(){\r\n
\t\t\tif(!this.grid) {return false;}\r\n
\t\t\tvar t = this, vl, ind, cp = typeof cssp, lcdata={};\r\n
\t\t\tind = t.rows.namedItem(rowid);\r\n
\t\t\tif(!ind) { return false; }\r\n
\t\t\tif( data ) {\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\t$(this.p.colModel).each(function(i){\r\n
\t\t\t\t\t\tnm = this.name;\r\n
\t\t\t\t\t\tif( data[nm] !== undefined) {\r\n
\t\t\t\t\t\t\tlcdata[nm] = this.formatter && typeof(this.formatter) === \'string\' && this.formatter == \'date\' ? $.unformat.date.call(t,data[nm],this) : data[nm];\r\n
\t\t\t\t\t\t\tvl = t.formatter( rowid, data[nm], i, data, \'edit\');\r\n
\t\t\t\t\t\t\ttitle = this.title ? {"title":$.jgrid.stripHtml(vl)} : {};\r\n
\t\t\t\t\t\t\tif(t.p.treeGrid===true && nm == t.p.ExpandColumn) {\r\n
\t\t\t\t\t\t\t\t$("td:eq("+i+") > span:first",ind).html(vl).attr(title);\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$("td:eq("+i+")",ind).html(vl).attr(title);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tif(t.p.datatype == \'local\') {\r\n
\t\t\t\t\t\tvar id = $.jgrid.stripPref(t.p.idPrefix, rowid),\r\n
\t\t\t\t\t\tpos = t.p._index[id];\r\n
\t\t\t\t\t\tif(t.p.treeGrid) {\r\n
\t\t\t\t\t\t\tfor(var key in t.p.treeReader ){\r\n
\t\t\t\t\t\t\t\tif(lcdata.hasOwnProperty(t.p.treeReader[key])) {\r\n
\t\t\t\t\t\t\t\t\tdelete lcdata[t.p.treeReader[key]];\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(typeof(pos) != \'undefined\') {\r\n
\t\t\t\t\t\t\tt.p.data[pos] = $.extend(true, t.p.data[pos], lcdata);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tlcdata = null;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} catch (e) {\r\n
\t\t\t\t\tsuccess = false;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(success) {\r\n
\t\t\t\tif(cp === \'string\') {$(ind).addClass(cssp);} else if(cp === \'object\') {$(ind).css(cssp);}\r\n
\t\t\t\t$(t).triggerHandler("jqGridAfterGridComplete");\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn success;\r\n
\t},\r\n
\taddRowData : function(rowid,rdata,pos,src) {\r\n
\t\tif(!pos) {pos = "last";}\r\n
\t\tvar success = false, nm, row, gi, si, ni,sind, i, v, prp="", aradd, cnm, cn, data, cm, id;\r\n
\t\tif(rdata) {\r\n
\t\t\tif($.isArray(rdata)) {\r\n
\t\t\t\taradd=true;\r\n
\t\t\t\tpos = "last";\r\n
\t\t\t\tcnm = rowid;\r\n
\t\t\t} else {\r\n
\t\t\t\trdata = [rdata];\r\n
\t\t\t\taradd = false;\r\n
\t\t\t}\r\n
\t\t\tthis.each(function() {\r\n
\t\t\t\tvar t = this, datalen = rdata.length;\r\n
\t\t\t\tni = t.p.rownumbers===true ? 1 :0;\r\n
\t\t\t\tgi = t.p.multiselect ===true ? 1 :0;\r\n
\t\t\t\tsi = t.p.subGrid===true ? 1 :0;\r\n
\t\t\t\tif(!aradd) {\r\n
\t\t\t\t\tif(typeof(rowid) != \'undefined\') { rowid = rowid+"";}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\trowid = $.jgrid.randId();\r\n
\t\t\t\t\t\tif(t.p.keyIndex !== false) {\r\n
\t\t\t\t\t\t\tcnm = t.p.colModel[t.p.keyIndex+gi+si+ni].name;\r\n
\t\t\t\t\t\t\tif(typeof rdata[0][cnm] != "undefined") { rowid = rdata[0][cnm]; }\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tcn = t.p.altclass;\r\n
\t\t\t\tvar k = 0, cna ="", lcdata = {},\r\n
\t\t\t\tair = $.isFunction(t.p.afterInsertRow) ? true : false;\r\n
\t\t\t\twhile(k < datalen) {\r\n
\t\t\t\t\tdata = rdata[k];\r\n
\t\t\t\t\trow=[];\r\n
\t\t\t\t\tif(aradd) {\r\n
\t\t\t\t\t\ttry {rowid = data[cnm];}\r\n
\t\t\t\t\t\tcatch (e) {rowid = $.jgrid.randId();}\r\n
\t\t\t\t\t\tcna = t.p.altRows === true ?  (t.rows.length-1)%2 === 0 ? cn : "" : "";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tid = rowid;\r\n
\t\t\t\t\trowid  = t.p.idPrefix + rowid;\r\n
\t\t\t\t\tif(ni){\r\n
\t\t\t\t\t\tprp = t.formatCol(0,1,\'\',null,rowid, true);\r\n
\t\t\t\t\t\trow[row.length] = "<td role=\\"gridcell\\" class=\\"ui-state-default jqgrid-rownum\\" "+prp+">0</td>";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(gi) {\r\n
\t\t\t\t\t\tv = "<input role=\\"checkbox\\" type=\\"checkbox\\""+" id=\\"jqg_"+t.p.id+"_"+rowid+"\\" class=\\"cbox\\"/>";\r\n
\t\t\t\t\t\tprp = t.formatCol(ni,1,\'\', null, rowid, true);\r\n
\t\t\t\t\t\trow[row.length] = "<td role=\\"gridcell\\" "+prp+">"+v+"</td>";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(si) {\r\n
\t\t\t\t\t\trow[row.length] = $(t).jqGrid("addSubGridCell",gi+ni,1);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tfor(i = gi+si+ni; i < t.p.colModel.length;i++){\r\n
\t\t\t\t\t\tcm = t.p.colModel[i];\r\n
\t\t\t\t\t\tnm = cm.name;\r\n
\t\t\t\t\t\tlcdata[nm] = data[nm];\r\n
\t\t\t\t\t\tv = t.formatter( rowid, $.jgrid.getAccessor(data,nm), i, data );\r\n
\t\t\t\t\t\tprp = t.formatCol(i,1,v, data, rowid, true);\r\n
\t\t\t\t\t\trow[row.length] = "<td role=\\"gridcell\\" "+prp+">"+v+"</td>";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\trow.unshift( t.constructTr(rowid, false, cna, lcdata, data, false ) );\r\n
\t\t\t\t\trow[row.length] = "</tr>";\r\n
\t\t\t\t\tif(t.rows.length === 0){\r\n
\t\t\t\t\t\t$("table:first",t.grid.bDiv).append(row.join(\'\'));\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\tswitch (pos) {\r\n
\t\t\t\t\t\tcase \'last\':\r\n
\t\t\t\t\t\t\t$(t.rows[t.rows.length-1]).after(row.join(\'\'));\r\n
\t\t\t\t\t\t\tsind = t.rows.length-1;\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase \'first\':\r\n
\t\t\t\t\t\t\t$(t.rows[0]).after(row.join(\'\'));\r\n
\t\t\t\t\t\t\tsind = 1;\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase \'after\':\r\n
\t\t\t\t\t\t\tsind = t.rows.namedItem(src);\r\n
\t\t\t\t\t\t\tif (sind) {\r\n
\t\t\t\t\t\t\t\tif($(t.rows[sind.rowIndex+1]).hasClass("ui-subgrid")) { $(t.rows[sind.rowIndex+1]).after(row); }\r\n
\t\t\t\t\t\t\t\telse { $(sind).after(row.join(\'\')); }\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tsind++;\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase \'before\':\r\n
\t\t\t\t\t\t\tsind = t.rows.namedItem(src);\r\n
\t\t\t\t\t\t\tif(sind) {$(sind).before(row.join(\'\'));sind=sind.rowIndex;}\r\n
\t\t\t\t\t\t\tsind--;\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(t.p.subGrid===true) {\r\n
\t\t\t\t\t\t$(t).jqGrid("addSubGrid",gi+ni, sind);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tt.p.records++;\r\n
\t\t\t\t\tt.p.reccount++;\r\n
\t\t\t\t\t$(t).triggerHandler("jqGridAfterInsertRow", [rowid,data,data]);\r\n
\t\t\t\t\tif(air) { t.p.afterInsertRow.call(t,rowid,data,data); }\r\n
\t\t\t\t\tk++;\r\n
\t\t\t\t\tif(t.p.datatype == \'local\') {\r\n
\t\t\t\t\t\tlcdata[t.p.localReader.id] = id;\r\n
\t\t\t\t\t\tt.p._index[id] = t.p.data.length;\r\n
\t\t\t\t\t\tt.p.data.push(lcdata);\r\n
\t\t\t\t\t\tlcdata = {};\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif( t.p.altRows === true && !aradd) {\r\n
\t\t\t\t\tif (pos == "last") {\r\n
\t\t\t\t\t\tif ((t.rows.length-1)%2 == 1)  {$(t.rows[t.rows.length-1]).addClass(cn);}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$(t.rows).each(function(i){\r\n
\t\t\t\t\t\t\tif(i % 2 ==1) { $(this).addClass(cn); }\r\n
\t\t\t\t\t\t\telse { $(this).removeClass(cn); }\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tt.updatepager(true,true);\r\n
\t\t\t\tsuccess = true;\r\n
\t\t\t});\r\n
\t\t}\r\n
\t\treturn success;\r\n
\t},\r\n
\tfooterData : function(action,data, format) {\r\n
\t\tvar nm, success=false, res={}, title;\r\n
\t\tfunction isEmpty(obj) {\r\n
\t\t\tfor(var i in obj) {\r\n
\t\t\t\tif (obj.hasOwnProperty(i)) { return false; }\r\n
\t\t\t}\r\n
\t\t\treturn true;\r\n
\t\t}\r\n
\t\tif(typeof(action) == "undefined") { action = "get"; }\r\n
\t\tif(typeof(format) != "boolean") { format  = true; }\r\n
\t\taction = action.toLowerCase();\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar t = this, vl;\r\n
\t\t\tif(!t.grid || !t.p.footerrow) {return false;}\r\n
\t\t\tif(action == "set") { if(isEmpty(data)) { return false; } }\r\n
\t\t\tsuccess=true;\r\n
\t\t\t$(this.p.colModel).each(function(i){\r\n
\t\t\t\tnm = this.name;\r\n
\t\t\t\tif(action == "set") {\r\n
\t\t\t\t\tif( data[nm] !== undefined) {\r\n
\t\t\t\t\t\tvl = format ? t.formatter( "", data[nm], i, data, \'edit\') : data[nm];\r\n
\t\t\t\t\t\ttitle = this.title ? {"title":$.jgrid.stripHtml(vl)} : {};\r\n
\t\t\t\t\t\t$("tr.footrow td:eq("+i+")",t.grid.sDiv).html(vl).attr(title);\r\n
\t\t\t\t\t\tsuccess = true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else if(action == "get") {\r\n
\t\t\t\t\tres[nm] = $("tr.footrow td:eq("+i+")",t.grid.sDiv).html();\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t});\r\n
\t\treturn action == "get" ? res : success;\r\n
\t},\r\n
\tshowHideCol : function(colname,show) {\r\n
\t\treturn this.each(function() {\r\n
\t\t\tvar $t = this, fndh=false, brd=$.jgrid.cellWidth()? 0: $t.p.cellLayout, cw;\r\n
\t\t\tif (!$t.grid ) {return;}\r\n
\t\t\tif( typeof colname === \'string\') {colname=[colname];}\r\n
\t\t\tshow = show != "none" ? "" : "none";\r\n
\t\t\tvar sw = show === "" ? true :false,\r\n
\t\t\tgh = $t.p.groupHeader && (typeof $t.p.groupHeader === \'object\' || $.isFunction($t.p.groupHeader) );\r\n
\t\t\tif(gh) { $($t).jqGrid(\'destroyGroupHeader\', false); }\r\n
\t\t\t$(this.p.colModel).each(function(i) {\r\n
\t\t\t\tif ($.inArray(this.name,colname) !== -1 && this.hidden === sw) {\r\n
\t\t\t\t\tif($t.p.frozenColumns === true && this.frozen === true) {\r\n
\t\t\t\t\t\treturn true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$("tr",$t.grid.hDiv).each(function(){\r\n
\t\t\t\t\t\t$(this.cells[i]).css("display", show);\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\t$($t.rows).each(function(){\r\n
\t\t\t\t\t\tif (!$(this).hasClass("jqgroup")) {\r\n
\t\t\t\t\t\t\t$(this.cells[i]).css("display", show);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tif($t.p.footerrow) { $("tr.footrow td:eq("+i+")", $t.grid.sDiv).css("display", show); }\r\n
\t\t\t\t\tcw =  parseInt(this.width,10);\r\n
\t\t\t\t\tif(show === "none") {\r\n
\t\t\t\t\t\t$t.p.tblwidth -= cw+brd;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$t.p.tblwidth += cw+brd;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tthis.hidden = !sw;\r\n
\t\t\t\t\tfndh=true;\r\n
\t\t\t\t\t$($t).triggerHandler("jqGridShowHideCol", [sw,this.name,i]);\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\tif(fndh===true) {\r\n
\t\t\t\tif($t.p.shrinkToFit === true && !isNaN($t.p.height)) { $t.p.tblwidth += parseInt($t.p.scrollOffset,10);}\r\n
\t\t\t\t$($t).jqGrid("setGridWidth",$t.p.shrinkToFit === true ? $t.p.tblwidth : $t.p.width );\r\n
\t\t\t}\r\n
\t\t\tif( gh )  {\r\n
\t\t\t\t$($t).jqGrid(\'setGroupHeaders\',$t.p.groupHeader);\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\thideCol : function (colname) {\r\n
\t\treturn this.each(function(){$(this).jqGrid("showHideCol",colname,"none");});\r\n
\t},\r\n
\tshowCol : function(colname) {\r\n
\t\treturn this.each(function(){$(this).jqGrid("showHideCol",colname,"");});\r\n
\t},\r\n
\tremapColumns : function(permutation, updateCells, keepHeader)\r\n
\t{\r\n
\t\tfunction resortArray(a) {\r\n
\t\t\tvar ac;\r\n
\t\t\tif (a.length) {\r\n
\t\t\t\tac = $.makeArray(a);\r\n
\t\t\t} else {\r\n
\t\t\t\tac = $.extend({}, a);\r\n
\t\t\t}\r\n
\t\t\t$.each(permutation, function(i) {\r\n
\t\t\t\ta[i] = ac[this];\r\n
\t\t\t});\r\n
\t\t}\r\n
\t\tvar ts = this.get(0);\r\n
\t\tfunction resortRows(parent, clobj) {\r\n
\t\t\t$(">tr"+(clobj||""), parent).each(function() {\r\n
\t\t\t\tvar row = this;\r\n
\t\t\t\tvar elems = $.makeArray(row.cells);\r\n
\t\t\t\t$.each(permutation, function() {\r\n
\t\t\t\t\tvar e = elems[this];\r\n
\t\t\t\t\tif (e) {\r\n
\t\t\t\t\t\trow.appendChild(e);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t});\r\n
\t\t}\r\n
\t\tresortArray(ts.p.colModel);\r\n
\t\tresortArray(ts.p.colNames);\r\n
\t\tresortArray(ts.grid.headers);\r\n
\t\tresortRows($("thead:first", ts.grid.hDiv), keepHeader && ":not(.ui-jqgrid-labels)");\r\n
\t\tif (updateCells) {\r\n
\t\t\tresortRows($("#"+$.jgrid.jqID(ts.p.id)+" tbody:first"), ".jqgfirstrow, tr.jqgrow, tr.jqfoot");\r\n
\t\t}\r\n
\t\tif (ts.p.footerrow) {\r\n
\t\t\tresortRows($("tbody:first", ts.grid.sDiv));\r\n
\t\t}\r\n
\t\tif (ts.p.remapColumns) {\r\n
\t\t\tif (!ts.p.remapColumns.length){\r\n
\t\t\t\tts.p.remapColumns = $.makeArray(permutation);\r\n
\t\t\t} else {\r\n
\t\t\t\tresortArray(ts.p.remapColumns);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tts.p.lastsort = $.inArray(ts.p.lastsort, permutation);\r\n
\t\tif(ts.p.treeGrid) { ts.p.expColInd = $.inArray(ts.p.expColInd, permutation); }\r\n
\t\t$(ts).triggerHandler("jqGridRemapColumns", [permutation, updateCells, keepHeader]);\r\n
\t},\r\n
\tsetGridWidth : function(nwidth, shrink) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif (!this.grid ) {return;}\r\n
\t\t\tvar $t = this, cw,\r\n
\t\t\tinitwidth = 0, brd=$.jgrid.cellWidth() ? 0: $t.p.cellLayout, lvc, vc=0, hs=false, scw=$t.p.scrollOffset, aw, gw=0,\r\n
\t\t\tcl = 0,cr;\r\n
\t\t\tif(typeof shrink != \'boolean\') {\r\n
\t\t\t\tshrink=$t.p.shrinkToFit;\r\n
\t\t\t}\r\n
\t\t\tif(isNaN(nwidth)) {return;}\r\n
\t\t\tnwidth = parseInt(nwidth,10); \r\n
\t\t\t$t.grid.width = $t.p.width = nwidth;\r\n
\t\t\t$("#gbo

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAM=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="3" aka="AAAAAAAAAAM=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string>x_"+$.jgrid.jqID($t.p.id)).css("width",nwidth+"px");\r\n
\t\t\t$("#gview_"+$.jgrid.jqID($t.p.id)).css("width",nwidth+"px");\r\n
\t\t\t$($t.grid.bDiv).css("width",nwidth+"px");\r\n
\t\t\t$($t.grid.hDiv).css("width",nwidth+"px");\r\n
\t\t\tif($t.p.pager ) {$($t.p.pager).css("width",nwidth+"px");}\r\n
\t\t\tif($t.p.toppager ) {$($t.p.toppager).css("width",nwidth+"px");}\r\n
\t\t\tif($t.p.toolbar[0] === true){\r\n
\t\t\t\t$($t.grid.uDiv).css("width",nwidth+"px");\r\n
\t\t\t\tif($t.p.toolbar[1]=="both") {$($t.grid.ubDiv).css("width",nwidth+"px");}\r\n
\t\t\t}\r\n
\t\t\tif($t.p.footerrow) { $($t.grid.sDiv).css("width",nwidth+"px"); }\r\n
\t\t\tif(shrink ===false \046\046 $t.p.forceFit === true) {$t.p.forceFit=false;}\r\n
\t\t\tif(shrink===true) {\r\n
\t\t\t\t$.each($t.p.colModel, function() {\r\n
\t\t\t\t\tif(this.hidden===false){\r\n
\t\t\t\t\t\tcw = this.widthOrg;\r\n
\t\t\t\t\t\tinitwidth += cw+brd;\r\n
\t\t\t\t\t\tif(this.fixed) {\r\n
\t\t\t\t\t\t\tgw += cw+brd;\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tvc++;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tcl++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tif(vc  === 0) { return; }\r\n
\t\t\t\t$t.p.tblwidth = initwidth;\r\n
\t\t\t\taw = nwidth-brd*vc-gw;\r\n
\t\t\t\tif(!isNaN($t.p.height)) {\r\n
\t\t\t\t\tif($($t.grid.bDiv)[0].clientHeight \074 $($t.grid.bDiv)[0].scrollHeight || $t.rows.length === 1){\r\n
\t\t\t\t\t\ths = true;\r\n
\t\t\t\t\t\taw -= scw;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tinitwidth =0;\r\n
\t\t\t\tvar cle = $t.grid.cols.length \0760;\r\n
\t\t\t\t$.each($t.p.colModel, function(i) {\r\n
\t\t\t\t\tif(this.hidden === false \046\046 !this.fixed){\r\n
\t\t\t\t\t\tcw = this.widthOrg;\r\n
\t\t\t\t\t\tcw = Math.round(aw*cw/($t.p.tblwidth-brd*vc-gw));\r\n
\t\t\t\t\t\tif (cw \074 0) { return; }\r\n
\t\t\t\t\t\tthis.width =cw;\r\n
\t\t\t\t\t\tinitwidth += cw;\r\n
\t\t\t\t\t\t$t.grid.headers[i].width=cw;\r\n
\t\t\t\t\t\t$t.grid.headers[i].el.style.width=cw+"px";\r\n
\t\t\t\t\t\tif($t.p.footerrow) { $t.grid.footers[i].style.width = cw+"px"; }\r\n
\t\t\t\t\t\tif(cle) { $t.grid.cols[i].style.width = cw+"px"; }\r\n
\t\t\t\t\t\tlvc = i;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\r\n
\t\t\t\tif (!lvc) { return; }\r\n
\r\n
\t\t\t\tcr =0;\r\n
\t\t\t\tif (hs) {\r\n
\t\t\t\t\tif(nwidth-gw-(initwidth+brd*vc) !== scw){\r\n
\t\t\t\t\t\tcr = nwidth-gw-(initwidth+brd*vc)-scw;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else if( Math.abs(nwidth-gw-(initwidth+brd*vc)) !== 1) {\r\n
\t\t\t\t\tcr = nwidth-gw-(initwidth+brd*vc);\r\n
\t\t\t\t}\r\n
\t\t\t\t$t.p.colModel[lvc].width += cr;\r\n
\t\t\t\t$t.p.tblwidth = initwidth+cr+brd*vc+gw;\r\n
\t\t\t\tif($t.p.tblwidth \076 nwidth) {\r\n
\t\t\t\t\tvar delta = $t.p.tblwidth - parseInt(nwidth,10);\r\n
\t\t\t\t\t$t.p.tblwidth = nwidth;\r\n
\t\t\t\t\tcw = $t.p.colModel[lvc].width = $t.p.colModel[lvc].width-delta;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tcw= $t.p.colModel[lvc].width;\r\n
\t\t\t\t}\r\n
\t\t\t\t$t.grid.headers[lvc].width = cw;\r\n
\t\t\t\t$t.grid.headers[lvc].el.style.width=cw+"px";\r\n
\t\t\t\tif(cle) { $t.grid.cols[lvc].style.width = cw+"px"; }\r\n
\t\t\t\tif($t.p.footerrow) {\r\n
\t\t\t\t\t$t.grid.footers[lvc].style.width = cw+"px";\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif($t.p.tblwidth) {\r\n
\t\t\t\t$(\'table:first\',$t.grid.bDiv).css("width",$t.p.tblwidth+"px");\r\n
\t\t\t\t$(\'table:first\',$t.grid.hDiv).css("width",$t.p.tblwidth+"px");\r\n
\t\t\t\t$t.grid.hDiv.scrollLeft = $t.grid.bDiv.scrollLeft;\r\n
\t\t\t\tif($t.p.footerrow) {\r\n
\t\t\t\t\t$(\'table:first\',$t.grid.sDiv).css("width",$t.p.tblwidth+"px");\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tsetGridHeight : function (nh) {\r\n
\t\treturn this.each(function (){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid) {return;}\r\n
\t\t\tvar bDiv = $($t.grid.bDiv);\r\n
\t\t\tbDiv.css({height: nh+(isNaN(nh)?"":"px")});\r\n
\t\t\tif($t.p.frozenColumns === true){\r\n
\t\t\t\t//follow the original set height to use 16, better scrollbar width detection\r\n
\t\t\t\t$(\'#\'+$.jgrid.jqID($t.p.id)+"_frozen").parent().height(bDiv.height() - 16);\r\n
\t\t\t}\r\n
\t\t\t$t.p.height = nh;\r\n
\t\t\tif ($t.p.scroll) { $t.grid.populateVisible(); }\r\n
\t\t});\r\n
\t},\r\n
\tsetCaption : function (newcap){\r\n
\t\treturn this.each(function(){\r\n
\t\t\tthis.p.caption=newcap;\r\n
\t\t\t$("span.ui-jqgrid-title, span.ui-jqgrid-title-rtl",this.grid.cDiv).html(newcap);\r\n
\t\t\t$(this.grid.cDiv).show();\r\n
\t\t});\r\n
\t},\r\n
\tsetLabel : function(colname, nData, prop, attrp ){\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this, pos=-1;\r\n
\t\t\tif(!$t.grid) {return;}\r\n
\t\t\tif(typeof(colname) != "undefined") {\r\n
\t\t\t\t$($t.p.colModel).each(function(i){\r\n
\t\t\t\t\tif (this.name == colname) {\r\n
\t\t\t\t\t\tpos = i;return false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t} else { return; }\r\n
\t\t\tif(pos\076=0) {\r\n
\t\t\t\tvar thecol = $("tr.ui-jqgrid-labels th:eq("+pos+")",$t.grid.hDiv);\r\n
\t\t\t\tif (nData){\r\n
\t\t\t\t\tvar ico = $(".s-ico",thecol);\r\n
\t\t\t\t\t$("[id^=jqgh_]",thecol).empty().html(nData).append(ico);\r\n
\t\t\t\t\t$t.p.colNames[pos] = nData;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (prop) {\r\n
\t\t\t\t\tif(typeof prop === \'string\') {$(thecol).addClass(prop);} else {$(thecol).css(prop);}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(typeof attrp === \'object\') {$(thecol).attr(attrp);}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tsetCell : function(rowid,colname,nData,cssp,attrp, forceupd) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this, pos =-1,v, title;\r\n
\t\t\tif(!$t.grid) {return;}\r\n
\t\t\tif(isNaN(colname)) {\r\n
\t\t\t\t$($t.p.colModel).each(function(i){\r\n
\t\t\t\t\tif (this.name == colname) {\r\n
\t\t\t\t\t\tpos = i;return false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t} else {pos = parseInt(colname,10);}\r\n
\t\t\tif(pos\076=0) {\r\n
\t\t\t\tvar ind = $t.rows.namedItem(rowid);\r\n
\t\t\t\tif (ind){\r\n
\t\t\t\t\tvar tcell = $("td:eq("+pos+")",ind);\r\n
\t\t\t\t\tif(nData !== "" || forceupd === true) {\r\n
\t\t\t\t\t\tv = $t.formatter(rowid, nData, pos,ind,\'edit\');\r\n
\t\t\t\t\t\ttitle = $t.p.colModel[pos].title ? {"title":$.jgrid.stripHtml(v)} : {};\r\n
\t\t\t\t\t\tif($t.p.treeGrid \046\046 $(".tree-wrap",$(tcell)).length\0760) {\r\n
\t\t\t\t\t\t\t$("span",$(tcell)).html(v).attr(title);\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$(tcell).html(v).attr(title);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif($t.p.datatype == "local") {\r\n
\t\t\t\t\t\t\tvar cm = $t.p.colModel[pos], index;\r\n
\t\t\t\t\t\t\tnData = cm.formatter \046\046 typeof(cm.formatter) === \'string\' \046\046 cm.formatter == \'date\' ? $.unformat.date.call($t,nData,cm) : nData;\r\n
\t\t\t\t\t\t\tindex = $t.p._index[rowid];\r\n
\t\t\t\t\t\t\tif(typeof index  != "undefined") {\r\n
\t\t\t\t\t\t\t\t$t.p.data[index][cm.name] = nData;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(typeof cssp === \'string\'){\r\n
\t\t\t\t\t\t$(tcell).addClass(cssp);\r\n
\t\t\t\t\t} else if(cssp) {\r\n
\t\t\t\t\t\t$(tcell).css(cssp);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(typeof attrp === \'object\') {$(tcell).attr(attrp);}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tgetCell : function(rowid,col) {\r\n
\t\tvar ret = false;\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t=this, pos=-1;\r\n
\t\t\tif(!$t.grid) {return;}\r\n
\t\t\tif(isNaN(col)) {\r\n
\t\t\t\t$($t.p.colModel).each(function(i){\r\n
\t\t\t\t\tif (this.name === col) {\r\n
\t\t\t\t\t\tpos = i;return false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t} else {pos = parseInt(col,10);}\r\n
\t\t\tif(pos\076=0) {\r\n
\t\t\t\tvar ind = $t.rows.namedItem(rowid);\r\n
\t\t\t\tif(ind) {\r\n
\t\t\t\t\ttry {\r\n
\t\t\t\t\t\tret = $.unformat.call($t,$("td:eq("+pos+")",ind),{rowId:ind.id, colModel:$t.p.colModel[pos]},pos);\r\n
\t\t\t\t\t} catch (e){\r\n
\t\t\t\t\t\tret = $.jgrid.htmlDecode($("td:eq("+pos+")",ind).html());\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn ret;\r\n
\t},\r\n
\tgetCol : function (col, obj, mathopr) {\r\n
\t\tvar ret = [], val, sum=0, min, max, v;\r\n
\t\tobj = typeof (obj) != \'boolean\' ? false : obj;\r\n
\t\tif(typeof mathopr == \'undefined\') { mathopr = false; }\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t=this, pos=-1;\r\n
\t\t\tif(!$t.grid) {return;}\r\n
\t\t\tif(isNaN(col)) {\r\n
\t\t\t\t$($t.p.colModel).each(function(i){\r\n
\t\t\t\t\tif (this.name === col) {\r\n
\t\t\t\t\t\tpos = i;return false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t} else {pos = parseInt(col,10);}\r\n
\t\t\tif(pos\076=0) {\r\n
\t\t\t\tvar ln = $t.rows.length, i =0;\r\n
\t\t\t\tif (ln \046\046 ln\0760){\r\n
\t\t\t\t\twhile(i\074ln){\r\n
\t\t\t\t\t\tif($($t.rows[i]).hasClass(\'jqgrow\')) {\r\n
\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\tval = $.unformat.call($t,$($t.rows[i].cells[pos]),{rowId:$t.rows[i].id, colModel:$t.p.colModel[pos]},pos);\r\n
\t\t\t\t\t\t\t} catch (e) {\r\n
\t\t\t\t\t\t\t\tval = $.jgrid.htmlDecode($t.rows[i].cells[pos].innerHTML);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(mathopr) {\r\n
\t\t\t\t\t\t\t\tv = parseFloat(val);\r\n
\t\t\t\t\t\t\t\tsum += v;\r\n
\t\t\t\t\t\t\t\tif (max === undefined) {max = min = v}\r\n
\t\t\t\t\t\t\t\tmin = Math.min(min, v);\r\n
\t\t\t\t\t\t\t\tmax = Math.max(max, v);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\telse if(obj) { ret.push( {id:$t.rows[i].id,value:val} ); }\r\n
\t\t\t\t\t\t\telse { ret.push( val ); }\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ti++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(mathopr) {\r\n
\t\t\t\t\t\tswitch(mathopr.toLowerCase()){\r\n
\t\t\t\t\t\t\tcase \'sum\': ret =sum; break;\r\n
\t\t\t\t\t\t\tcase \'avg\': ret = sum/ln; break;\r\n
\t\t\t\t\t\t\tcase \'count\': ret = ln; break;\r\n
\t\t\t\t\t\t\tcase \'min\': ret = min; break;\r\n
\t\t\t\t\t\t\tcase \'max\': ret = max; break;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn ret;\r\n
\t},\r\n
\tclearGridData : function(clearfooter) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid) {return;}\r\n
\t\t\tif(typeof clearfooter != \'boolean\') { clearfooter = false; }\r\n
\t\t\tif($t.p.deepempty) {$("#"+$.jgrid.jqID($t.p.id)+" tbody:first tr:gt(0)").remove();}\r\n
\t\t\telse {\r\n
\t\t\t\tvar trf = $("#"+$.jgrid.jqID($t.p.id)+" tbody:first tr:first")[0];\r\n
\t\t\t\t$("#"+$.jgrid.jqID($t.p.id)+" tbody:first").empty().append(trf);\r\n
\t\t\t}\r\n
\t\t\tif($t.p.footerrow \046\046 clearfooter) { $(".ui-jqgrid-ftable td",$t.grid.sDiv).html("\046#160;"); }\r\n
\t\t\t$t.p.selrow = null; $t.p.selarrrow= []; $t.p.savedRow = [];\r\n
\t\t\t$t.p.records = 0;$t.p.page=1;$t.p.lastpage=0;$t.p.reccount=0;\r\n
\t\t\t$t.p.data = []; $t.p._index = {};\r\n
\t\t\t$t.updatepager(true,false);\r\n
\t\t});\r\n
\t},\r\n
\tgetInd : function(rowid,rc){\r\n
\t\tvar ret =false,rw;\r\n
\t\tthis.each(function(){\r\n
\t\t\trw = this.rows.namedItem(rowid);\r\n
\t\t\tif(rw) {\r\n
\t\t\t\tret = rc===true ? rw: rw.rowIndex;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn ret;\r\n
\t},\r\n
\tbindKeys : function( settings ){\r\n
\t\tvar o = $.extend({\r\n
\t\t\tonEnter: null,\r\n
\t\t\tonSpace: null,\r\n
\t\t\tonLeftKey: null,\r\n
\t\t\tonRightKey: null,\r\n
\t\t\tscrollingRows : true\r\n
\t\t},settings || {});\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif( !$(\'body\').is(\'[role]\') ){$(\'body\').attr(\'role\',\'application\');}\r\n
\t\t\t$t.p.scrollrows = o.scrollingRows;\r\n
\t\t\t$($t).keydown(function(event){\r\n
\t\t\t\tvar target = $($t).find(\'tr[tabindex=0]\')[0], id, r, mind,\r\n
\t\t\t\texpanded = $t.p.treeReader.expanded_field;\r\n
\t\t\t\t//check for arrow keys\r\n
\t\t\t\tif(target) {\r\n
\t\t\t\t\tmind = $t.p._index[target.id];\r\n
\t\t\t\t\tif(event.keyCode === 37 || event.keyCode === 38 || event.keyCode === 39 || event.keyCode === 40){\r\n
\t\t\t\t\t\t// up key\r\n
\t\t\t\t\t\tif(event.keyCode === 38 ){\r\n
\t\t\t\t\t\t\tr = target.previousSibling;\r\n
\t\t\t\t\t\t\tid = "";\r\n
\t\t\t\t\t\t\tif(r) {\r\n
\t\t\t\t\t\t\t\tif($(r).is(":hidden")) {\r\n
\t\t\t\t\t\t\t\t\twhile(r) {\r\n
\t\t\t\t\t\t\t\t\t\tr = r.previousSibling;\r\n
\t\t\t\t\t\t\t\t\t\tif(!$(r).is(":hidden") \046\046 $(r).hasClass(\'jqgrow\')) {id = r.id;break;}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\tid = r.id;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'setSelection\', id, true, event);\r\n
\t\t\t\t\t\t\tevent.preventDefault();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t//if key is down arrow\r\n
\t\t\t\t\t\tif(event.keyCode === 40){\r\n
\t\t\t\t\t\t\tr = target.nextSibling;\r\n
\t\t\t\t\t\t\tid ="";\r\n
\t\t\t\t\t\t\tif(r) {\r\n
\t\t\t\t\t\t\t\tif($(r).is(":hidden")) {\r\n
\t\t\t\t\t\t\t\t\twhile(r) {\r\n
\t\t\t\t\t\t\t\t\t\tr = r.nextSibling;\r\n
\t\t\t\t\t\t\t\t\t\tif(!$(r).is(":hidden") \046\046 $(r).hasClass(\'jqgrow\') ) {id = r.id;break;}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\tid = r.id;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'setSelection\', id, true, event);\r\n
\t\t\t\t\t\t\tevent.preventDefault();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t// left\r\n
\t\t\t\t\t\tif(event.keyCode === 37 ){\r\n
\t\t\t\t\t\t\tif($t.p.treeGrid \046\046 $t.p.data[mind][expanded]) {\r\n
\t\t\t\t\t\t\t\t$(target).find("div.treeclick").trigger(\'click\');\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t$($t).triggerHandler("jqGridKeyLeft", [$t.p.selrow]);\r\n
\t\t\t\t\t\t\tif($.isFunction(o.onLeftKey)) {\r\n
\t\t\t\t\t\t\t\to.onLeftKey.call($t, $t.p.selrow);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t// right\r\n
\t\t\t\t\t\tif(event.keyCode === 39 ){\r\n
\t\t\t\t\t\t\tif($t.p.treeGrid \046\046 !$t.p.data[mind][expanded]) {\r\n
\t\t\t\t\t\t\t\t$(target).find("div.treeclick").trigger(\'click\');\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t$($t).triggerHandler("jqGridKeyRight", [$t.p.selrow]);\r\n
\t\t\t\t\t\t\tif($.isFunction(o.onRightKey)) {\r\n
\t\t\t\t\t\t\t\to.onRightKey.call($t, $t.p.selrow);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t//check if enter was pressed on a grid or treegrid node\r\n
\t\t\t\t\telse if( event.keyCode === 13 ){\r\n
\t\t\t\t\t\t$($t).triggerHandler("jqGridKeyEnter", [$t.p.selrow]);\r\n
\t\t\t\t\t\tif($.isFunction(o.onEnter)) {\r\n
\t\t\t\t\t\t\to.onEnter.call($t, $t.p.selrow);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else if(event.keyCode === 32) {\r\n
\t\t\t\t\t\t$($t).triggerHandler("jqGridKeySpace", [$t.p.selrow]);\r\n
\t\t\t\t\t\tif($.isFunction(o.onSpace)) {\r\n
\t\t\t\t\t\t\to.onSpace.call($t, $t.p.selrow);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t});\r\n
\t},\r\n
\tunbindKeys : function(){\r\n
\t\treturn this.each(function(){\r\n
\t\t\t$(this).unbind(\'keydown\');\r\n
\t\t});\r\n
\t},\r\n
\tgetLocalRow : function (rowid) {\r\n
\t\tvar ret = false, ind;\r\n
\t\tthis.each(function(){\r\n
\t\t\tif(typeof(rowid) !== "undefined") {\r\n
\t\t\t\tind = this.p._index[rowid];\r\n
\t\t\t\tif(ind \076= 0 ) {\r\n
\t\t\t\t\tret = this.p.data[ind];\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn ret;\r\n
\t}\r\n
});\r\n
})(jQuery);\r\n
(function($){\r\n
/**\r\n
 * jqGrid extension for custom methods\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/ \r\n
 * \r\n
 * Wildraid wildraid@mail.ru\r\n
 * Oleg Kiriljuk oleg.kiriljuk@ok-soft-gmbh.com\r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
**/\r\n
/*global jQuery, $ */\r\n
"use strict";\r\n
$.jgrid.extend({\r\n
\tgetColProp : function(colname){\r\n
\t\tvar ret ={}, $t = this[0];\r\n
\t\tif ( !$t.grid ) { return false; }\r\n
\t\tvar cM = $t.p.colModel;\r\n
\t\tfor ( var i =0;i\074cM.length;i++ ) {\r\n
\t\t\tif ( cM[i].name == colname ) {\r\n
\t\t\t\tret = cM[i];\r\n
\t\t\t\tbreak;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn ret;\r\n
\t},\r\n
\tsetColProp : function(colname, obj){\r\n
\t\t//do not set width will not work\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif ( this.grid ) {\r\n
\t\t\t\tif ( obj ) {\r\n
\t\t\t\t\tvar cM = this.p.colModel;\r\n
\t\t\t\t\tfor ( var i =0;i\074cM.length;i++ ) {\r\n
\t\t\t\t\t\tif ( cM[i].name == colname ) {\r\n
\t\t\t\t\t\t\t$.extend(this.p.colModel[i],obj);\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tsortGrid : function(colname,reload, sor){\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t=this,idx=-1;\r\n
\t\t\tif ( !$t.grid ) { return;}\r\n
\t\t\tif ( !colname ) { colname = $t.p.sortname; }\r\n
\t\t\tfor ( var i=0;i\074$t.p.colModel.length;i++ ) {\r\n
\t\t\t\tif ( $t.p.colModel[i].index == colname || $t.p.colModel[i].name==colname ) {\r\n
\t\t\t\t\tidx = i;\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif ( idx!=-1 ){\r\n
\t\t\t\tvar sort = $t.p.colModel[idx].sortable;\r\n
\t\t\t\tif ( typeof sort !== \'boolean\' ) { sort =  true; }\r\n
\t\t\t\tif ( typeof reload !==\'boolean\' ) { reload = false; }\r\n
\t\t\t\tif ( sort ) { $t.sortData("jqgh_"+$t.p.id+"_" + colname, idx, reload, sor); }\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tclearBeforeUnload : function () {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar grid = this.grid;\r\n
\t\t\tgrid.emptyRows.call(this, true, true); // this work quick enough and reduce the size of memory leaks if we have someone\r\n
\r\n
\t\t\t//$(document).unbind("mouseup"); // TODO add namespace\r\n
\t\t\t$(grid.hDiv).unbind("mousemove"); // TODO add namespace\r\n
\t\t\t$(this).unbind();\r\n
\r\n
\t\t\tgrid.dragEnd = null;\r\n
\t\t\tgrid.dragMove = null;\r\n
\t\t\tgrid.dragStart = null;\r\n
\t\t\tgrid.emptyRows = null;\r\n
\t\t\tgrid.populate = null;\r\n
\t\t\tgrid.populateVisible = null;\r\n
\t\t\tgrid.scrollGrid = null;\r\n
\t\t\tgrid.selectionPreserver = null;\r\n
\r\n
\t\t\tgrid.bDiv = null;\r\n
\t\t\tgrid.cDiv = null;\r\n
\t\t\tgrid.hDiv = null;\r\n
\t\t\tgrid.cols = null;\r\n
\t\t\tvar i, l = grid.headers.length;\r\n
\t\t\tfor (i = 0; i \074 l; i++) {\r\n
\t\t\t\tgrid.headers[i].el = null;\r\n
\t\t\t}\r\n
\r\n
\t\t\tthis.formatCol = null;\r\n
\t\t\tthis.sortData = null;\r\n
\t\t\tthis.updatepager = null;\r\n
\t\t\tthis.refreshIndex = null;\r\n
\t\t\tthis.setHeadCheckBox = null;\r\n
\t\t\tthis.constructTr = null;\r\n
\t\t\tthis.formatter = null;\r\n
\t\t\tthis.addXmlData = null;\r\n
\t\t\tthis.addJSONData = null;\r\n
\t\t});\r\n
\t},\r\n
\tGridDestroy : function () {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif ( this.grid ) { \r\n
\t\t\t\tif ( this.p.pager ) { // if not part of grid\r\n
\t\t\t\t\t$(this.p.pager).remove();\r\n
\t\t\t\t}\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\t$(this).jqGrid(\'clearBeforeUnload\');\r\n
\t\t\t\t\t$("#gbox_"+$.jgrid.jqID(this.id)).remove();\r\n
\t\t\t\t} catch (_) {}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tGridUnload : function(){\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif ( !this.grid ) {return;}\r\n
\t\t\tvar defgrid = {id: $(this).attr(\'id\'),cl: $(this).attr(\'class\')};\r\n
\t\t\tif (this.p.pager) {\r\n
\t\t\t\t$(this.p.pager).empty().removeClass("ui-state-default ui-jqgrid-pager corner-bottom");\r\n
\t\t\t}\r\n
\t\t\tvar newtable = document.createElement(\'table\');\r\n
\t\t\t$(newtable).attr({id:defgrid.id});\r\n
\t\t\tnewtable.className = defgrid.cl;\r\n
\t\t\tvar gid = $.jgrid.jqID(this.id);\r\n
\t\t\t$(newtable).removeClass("ui-jqgrid-btable");\r\n
\t\t\tif( $(this.p.pager).parents("#gbox_"+gid).length === 1 ) {\r\n
\t\t\t\t$(newtable).insertBefore("#gbox_"+gid).show();\r\n
\t\t\t\t$(this.p.pager).insertBefore("#gbox_"+gid);\r\n
\t\t\t} else {\r\n
\t\t\t\t$(newtable).insertBefore("#gbox_"+gid).show();\r\n
\t\t\t}\r\n
\t\t\t$(this).jqGrid(\'clearBeforeUnload\');\r\n
\t\t\t$("#gbox_"+gid).remove();\r\n
\t\t});\r\n
\t},\r\n
    setGridState : function(state) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif ( !this.grid ) {return;}\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(state == \'hidden\'){\r\n
\t\t\t\t$(".ui-jqgrid-bdiv, .ui-jqgrid-hdiv","#gview_"+$.jgrid.jqID($t.p.id)).slideUp("fast");\r\n
\t\t\t\tif($t.p.pager) {$($t.p.pager).slideUp("fast");}\r\n
\t\t\t\tif($t.p.toppager) {$($t.p.toppager).slideUp("fast");}\r\n
\t\t\t\tif($t.p.toolbar[0]===true) {\r\n
\t\t\t\t\tif( $t.p.toolbar[1]==\'both\') {\r\n
\t\t\t\t\t\t$($t.grid.ubDiv).slideUp("fast");\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$($t.grid.uDiv).slideUp("fast");\r\n
\t\t\t\t}\r\n
\t\t\t\tif($t.p.footerrow) { $(".ui-jqgrid-sdiv","#gbox_"+$.jgrid.jqID($t.p.id)).slideUp("fast"); }\r\n
\t\t\t\t$(".ui-jqgrid-titlebar-close span",$t.grid.cDiv).removeClass("ui-icon-circle-triangle-n").addClass("ui-icon-circle-triangle-s");\r\n
\t\t\t\t$t.p.gridstate = \'hidden\';\r\n
\t\t\t} else if(state==\'visible\') {\r\n
\t\t\t\t$(".ui-jqgrid-hdiv, .ui-jqgrid-bdiv","#gview_"+$.jgrid.jqID($t.p.id)).slideDown("fast");\r\n
\t\t\t\tif($t.p.pager) {$($t.p.pager).slideDown("fast");}\r\n
\t\t\t\tif($t.p.toppager) {$($t.p.toppager).slideDown("fast");}\r\n
\t\t\t\tif($t.p.toolbar[0]===true) {\r\n
\t\t\t\t\tif( $t.p.toolbar[1]==\'both\') {\r\n
\t\t\t\t\t\t$($t.grid.ubDiv).slideDown("fast");\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$($t.grid.uDiv).slideDown("fast");\r\n
\t\t\t\t}\r\n
\t\t\t\tif($t.p.footerrow) { $(".ui-jqgrid-sdiv","#gbox_"+$.jgrid.jqID($t.p.id)).slideDown("fast"); }\r\n
\t\t\t\t$(".ui-jqgrid-titlebar-close span",$t.grid.cDiv).removeClass("ui-icon-circle-triangle-s").addClass("ui-icon-circle-triangle-n");\r\n
\t\t\t\t$t.p.gridstate = \'visible\';\r\n
\t\t\t}\r\n
\r\n
\t\t});\r\n
\t},\r\n
\tfilterToolbar : function(p){\r\n
\t\tp = $.extend({\r\n
\t\t\tautosearch: true,\r\n
\t\t\tsearchOnEnter : true,\r\n
\t\t\tbeforeSearch: null,\r\n
\t\t\tafterSearch: null,\r\n
\t\t\tbeforeClear: null,\r\n
\t\t\tafterClear: null,\r\n
\t\t\tsearchurl : \'\',\r\n
\t\t\tstringResult: false,\r\n
\t\t\tgroupOp: \'AND\',\r\n
\t\t\tdefaultSearch : "bw"\r\n
\t\t},p  || {});\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(this.ftoolbar) { return; }\r\n
\t\t\tvar triggerToolbar = function() {\r\n
\t\t\t\tvar sdata={}, j=0, v, nm, sopt={},so;\r\n
\t\t\t\t$.each($t.p.colModel,function(){\r\n
\t\t\t\t\tnm = this.index || this.name;\r\n
\t\t\t\t\tso  = (this.searchoptions \046\046 this.searchoptions.sopt) ? this.searchoptions.sopt[0] : this.stype==\'select\'?  \'eq\' : p.defaultSearch;\r\n
\t\t\t\t\tv = $("#gs_"+$.jgrid.jqID(this.name), (this.frozen===true \046\046 $t.p.frozenColumns === true) ?  $t.grid.fhDiv : $t.grid.hDiv).val();\r\n
\t\t\t\t\tif(v) {\r\n
\t\t\t\t\t\tsdata[nm] = v;\r\n
\t\t\t\t\t\tsopt[nm] = so;\r\n
\t\t\t\t\t\tj++;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\tdelete $t.p.postData[nm];\r\n
\t\t\t\t\t\t} catch (z) {}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tvar sd =  j\0760 ? true : false;\r\n
\t\t\t\tif(p.stringResult === true || $t.p.datatype == "local") {\r\n
\t\t\t\t\tvar ruleGroup = "{\\"groupOp\\":\\"" + p.groupOp + "\\",\\"rules\\":[";\r\n
\t\t\t\t\tvar gi=0;\r\n
\t\t\t\t\t$.each(sdata,function(i,n){\r\n
\t\t\t\t\t\tif (gi \076 0) {ruleGroup += ",";}\r\n
\t\t\t\t\t\truleGroup += "{\\"field\\":\\"" + i + "\\",";\r\n
\t\t\t\t\t\truleGroup += "\\"op\\":\\"" + sopt[i] + "\\",";\r\n
\t\t\t\t\t\tn+="";\r\n
\t\t\t\t\t\truleGroup += "\\"data\\":\\"" + n.replace(/\\\\/g,\'\\\\\\\\\').replace(/\\"/g,\'\\\\"\') + "\\"}";\r\n
\t\t\t\t\t\tgi++;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\truleGroup += "]}";\r\n
\t\t\t\t\t$.extend($t.p.postData,{filters:ruleGroup});\r\n
\t\t\t\t\t$.each([\'searchField\', \'searchString\', \'searchOper\'], function(i, n){\r\n
\t\t\t\t\t\tif($t.p.postData.hasOwnProperty(n)) { delete $t.p.postData[n];}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$.extend($t.p.postData,sdata);\r\n
\t\t\t\t}\r\n
\t\t\t\tvar saveurl;\r\n
\t\t\t\tif($t.p.searchurl) {\r\n
\t\t\t\t\tsaveurl = $t.p.url;\r\n
\t\t\t\t\t$($t).jqGrid("setGridParam",{url:$t.p.searchurl});\r\n
\t\t\t\t}\r\n
\t\t\t\tvar bsr = $($t).triggerHandler("jqGridToolbarBeforeSearch") === \'stop\' ? true : false;\r\n
\t\t\t\tif(!bsr \046\046 $.isFunction(p.beforeSearch)){bsr = p.beforeSearch.call($t);}\r\n
\t\t\t\tif(!bsr) { $($t).jqGrid("setGridParam",{search:sd}).trigger("reloadGrid",[{page:1}]); }\r\n
\t\t\t\tif(saveurl) {$($t).jqGrid("setGridParam",{url:saveurl});}\r\n
\t\t\t\t$($t).triggerHandler("jqGridToolbarAfterSearch");\r\n
\t\t\t\tif($.isFunction(p.afterSearch)){p.afterSearch.call($t);}\r\n
\t\t\t};\r\n
\t\t\tvar clearToolbar = function(trigger){\r\n
\t\t\t\tvar sdata={}, j=0, nm;\r\n
\t\t\t\ttrigger = (typeof trigger != \'boolean\') ? true : trigger;\r\n
\t\t\t\t$.each($t.p.colModel,function(){\r\n
\t\t\t\t\tvar v;\r\n
\t\t\t\t\tif(this.searchoptions \046\046 this.searchoptions.defaultValue !== undefined) { v = this.searchoptions.defaultValue; }\r\n
\t\t\t\t\tnm = this.index || this.name;\r\n
\t\t\t\t\tswitch (this.stype) {\r\n
\t\t\t\t\t\tcase \'select\' :\r\n
\t\t\t\t\t\t\t$("#gs_"+$.jgrid.jqID(this.name)+" option",(this.frozen===true \046\046 $t.p.frozenColumns === true) ?  $t.grid.fhDiv : $t.grid.hDiv).each(function (i){\r\n
\t\t\t\t\t\t\t\tif(i===0) { this.selected = true; }\r\n
\t\t\t\t\t\t\t\tif ($(this).val() == v) {\r\n
\t\t\t\t\t\t\t\t\tthis.selected = true;\r\n
\t\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\tif ( v !== undefined ) {\r\n
\t\t\t\t\t\t\t\t// post the key and not the text\r\n
\t\t\t\t\t\t\t\tsdata[nm] = v;\r\n
\t\t\t\t\t\t\t\tj++;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\tdelete $t.p.postData[nm];\r\n
\t\t\t\t\t\t\t\t} catch(e) {}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase \'text\':\r\n
\t\t\t\t\t\t\t$("#gs_"+$.jgrid.jqID(this.name),(this.frozen===true \046\046 $t.p.frozenColumns === true) ?  $t.grid.fhDiv : $t.grid.hDiv).val(v);\r\n
\t\t\t\t\t\t\tif(v !== undefined) {\r\n
\t\t\t\t\t\t\t\tsdata[nm] = v;\r\n
\t\t\t\t\t\t\t\tj++;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\tdelete $t.p.postData[nm];\r\n
\t\t\t\t\t\t\t\t} catch (y){}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tvar sd =  j\0760 ? true : false;\r\n
\t\t\t\tif(p.stringResult === true || $t.p.datatype == "local") {\r\n
\t\t\t\t\tvar ruleGroup = "{\\"groupOp\\":\\"" + p.groupOp + "\\",\\"rules\\":[";\r\n
\t\t\t\t\tvar gi=0;\r\n
\t\t\t\t\t$.each(sdata,function(i,n){\r\n
\t\t\t\t\t\tif (gi \076 0) {ruleGroup += ",";}\r\n
\t\t\t\t\t\truleGroup += "{\\"field\\":\\"" + i + "\\",";\r\n
\t\t\t\t\t\truleGroup += "\\"op\\":\\"" + "eq" + "\\",";\r\n
\t\t\t\t\t\tn+="";\r\n
\t\t\t\t\t\truleGroup += "\\"data\\":\\"" + n.replace(/\\\\/g,\'\\\\\\\\\').replace(/\\"/g,\'\\\\"\') + "\\"}";\r\n
\t\t\t\t\t\tgi++;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\truleGroup += "]}";\r\n
\t\t\t\t\t$.extend($t.p.postData,{filters:ruleGroup});\r\n
\t\t\t\t\t$.each([\'searchField\', \'searchString\', \'searchOper\'], function(i, n){\r\n
\t\t\t\t\t\tif($t.p.postData.hasOwnProperty(n)) { delete $t.p.postData[n];}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$.extend($t.p.postData,sdata);\r\n
\t\t\t\t}\r\n
\t\t\t\tvar saveurl;\r\n
\t\t\t\tif($t.p.searchurl) {\r\n
\t\t\t\t\tsaveurl = $t.p.url;\r\n
\t\t\t\t\t$($t).jqGrid("setGridParam",{url:$t.p.searchurl});\r\n
\t\t\t\t}\r\n
\t\t\t\tvar bcv = $($t).triggerHandler("jqGridToolbarBeforeClear") === \'stop\' ? true : false;\r\n
\t\t\t\tif(!bcv \046\046 $.isFunction(p.beforeClear)){bcv = p.beforeClear.call($t);}\r\n
\t\t\t\tif(!bcv) {\r\n
\t\t\t\t\tif(trigger) {\r\n
\t\t\t\t\t\t$($t).jqGrid("setGridParam",{search:sd}).trigger("reloadGrid",[{page:1}]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(saveurl) {$($t).jqGrid("setGridParam",{url:saveurl});}\r\n
\t\t\t\t$($t).triggerHandler("jqGridToolbarAfterClear");\r\n
\t\t\t\tif($.isFunction(p.afterClear)){p.afterClear();}\r\n
\t\t\t};\r\n
\t\t\tvar toggleToolbar = function(){\r\n
\t\t\t\tvar trow = $("tr.ui-search-toolbar",$t.grid.hDiv),\r\n
\t\t\t\ttrow2 = $t.p.frozenColumns === true ?  $("tr.ui-search-toolbar",$t.grid.fhDiv) : false;\r\n
\t\t\t\tif(trow.css("display")==\'none\') { \r\n
\t\t\t\t\ttrow.show(); \r\n
\t\t\t\t\tif(trow2) {\r\n
\t\t\t\t\t\ttrow2.show();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else { \r\n
\t\t\t\t\ttrow.hide(); \r\n
\t\t\t\t\tif(trow2) {\r\n
\t\t\t\t\t\ttrow2.hide();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t};\r\n
\t\t\t// create the row\r\n
\t\t\tfunction bindEvents(selector, events) {\r\n
\t\t\t\tvar jElem = $(selector);\r\n
\t\t\t\tif (jElem[0]) {\r\n
\t\t\t\t\tjQuery.each(events, function() {\r\n
\t\t\t\t\t\tif (this.data !== undefined) {\r\n
\t\t\t\t\t\t\tjElem.bind(this.type, this.data, this.fn);\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tjElem.bind(this.type, this.fn);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tvar tr = $("\074tr class=\'ui-search-toolbar\' role=\'rowheader\'\076\074/tr\076");\r\n
\t\t\tvar timeoutHnd;\r\n
\t\t\t$.each($t.p.colModel,function(){\r\n
\t\t\t\tvar cm=this, thd , th, soptions,surl,self;\r\n
\t\t\t\tth = $("\074th role=\'columnheader\' class=\'ui-state-default ui-th-column ui-th-"+$t.p.direction+"\'\076\074/th\076");\r\n
\t\t\t\tthd = $("\074div style=\'width:100%;position:relative;height:100%;padding-right:0.3em;\'\076\074/div\076");\r\n
\t\t\t\tif(this.hidden===true) { $(th).css("display","none");}\r\n
\t\t\t\tthis.search = this.search === false ? false : true;\r\n
\t\t\t\tif(typeof this.stype == \'undefined\' ) {this.stype=\'text\';}\r\n
\t\t\t\tsoptions = $.extend({},this.searchoptions || {});\r\n
\t\t\t\tif(this.search){\r\n
\t\t\t\t\tswitch (this.stype)\r\n
\t\t\t\t\t{\r\n
\t\t\t\t\tcase "select":\r\n
\t\t\t\t\t\tsurl = this.surl || soptions.dataUrl;\r\n
\t\t\t\t\t\tif(surl) {\r\n
\t\t\t\t\t\t\t// data returned should have already constructed html select\r\n
\t\t\t\t\t\t\t// primitive jQuery load\r\n
\t\t\t\t\t\t\tself = thd;\r\n
\t\t\t\t\t\t\t$.ajax($.extend({\r\n
\t\t\t\t\t\t\t\turl: surl,\r\n
\t\t\t\t\t\t\t\tdataType: "html",\r\n
\t\t\t\t\t\t\t\tsuccess: function(res) {\r\n
\t\t\t\t\t\t\t\t\tif(soptions.buildSelect !== undefined) {\r\n
\t\t\t\t\t\t\t\t\t\tvar d = soptions.buildSelect(res);\r\n
\t\t\t\t\t\t\t\t\t\tif (d) { $(self).append(d); }\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t$(self).append(res);\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\tif(soptions.defaultValue !== undefined) { $("select",self).val(soptions.defaultValue); }\r\n
\t\t\t\t\t\t\t\t\t$("select",self).attr({name:cm.index || cm.name, id: "gs_"+cm.name});\r\n
\t\t\t\t\t\t\t\t\tif(soptions.attr) {$("select",self).attr(soptions.attr);}\r\n
\t\t\t\t\t\t\t\t\t$("select",self).css({width: "100%"});\r\n
\t\t\t\t\t\t\t\t\t// preserve autoserch\r\n
\t\t\t\t\t\t\t\t\tif(soptions.dataInit !== undefined) { soptions.dataInit($("select",self)[0]); }\r\n
\t\t\t\t\t\t\t\t\tif(soptions.dataEvents !== undefined) { bindEvents($("select",self)[0],soptions.dataEvents); }\r\n
\t\t\t\t\t\t\t\t\tif(p.autosearch===true){\r\n
\t\t\t\t\t\t\t\t\t\t$("select",self).change(function(){\r\n
\t\t\t\t\t\t\t\t\t\t\ttriggerToolbar();\r\n
\t\t\t\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\tres=null;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}, $.jgrid.ajaxOptions, $t.p.ajaxSelectOptions || {} ));\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tvar oSv, sep, delim;\r\n
\t\t\t\t\t\t\tif(cm.searchoptions) {\r\n
\t\t\t\t\t\t\t\toSv = cm.searchoptions.value === undefined ? "" : cm.searchoptions.value;\r\n
\t\t\t\t\t\t\t\tsep = cm.searchoptions.separator === undefined ? ":" : cm.searchoptions.separator;\r\n
\t\t\t\t\t\t\t\tdelim = cm.searchoptions.delimiter === undefined ? ";" : cm.searchoptions.delimiter;\r\n
\t\t\t\t\t\t\t} else if(cm.editoptions) {\r\n
\t\t\t\t\t\t\t\toSv = cm.editoptions.value === undefined ? "" : cm.editoptions.value;\r\n
\t\t\t\t\t\t\t\tsep = cm.editoptions.separator === undefined ? ":" : cm.editoptions.separator;\r\n
\t\t\t\t\t\t\t\tdelim = cm.editoptions.delimiter === undefined ? ";" : cm.editoptions.delimiter;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif (oSv) {\t\r\n
\t\t\t\t\t\t\t\tvar elem = document.createElement("select");\r\n
\t\t\t\t\t\t\t\telem.style.width = "100%";\r\n
\t\t\t\t\t\t\t\t$(elem).attr({name:cm.index || cm.name, id: "gs_"+cm.name});\r\n
\t\t\t\t\t\t\t\tvar so, sv, ov;\r\n
\t\t\t\t\t\t\t\tif(typeof oSv === "string") {\r\n
\t\t\t\t\t\t\t\t\tso = oSv.split(delim);\r\n
\t\t\t\t\t\t\t\t\tfor(var k=0; k\074so.length;k++){\r\n
\t\t\t\t\t\t\t\t\t\tsv = so[k].split(sep);\r\n
\t\t\t\t\t\t\t\t\t\tov = document.createElement("option");\r\n
\t\t\t\t\t\t\t\t\t\tov.value = sv[0]; ov.innerHTML = sv[1];\r\n
\t\t\t\t\t\t\t\t\t\telem.appendChild(ov);\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t} else if(typeof oSv === "object" ) {\r\n
\t\t\t\t\t\t\t\t\tfor ( var key in oSv) {\r\n
\t\t\t\t\t\t\t\t\t\tif(oSv.hasOwnProperty(key)) {\r\n
\t\t\t\t\t\t\t\t\t\t\tov = document.createElement("option");\r\n
\t\t\t\t\t\t\t\t\t\t\tov.value = key; ov.innerHTML = oSv[key];\r\n
\t\t\t\t\t\t\t\t\t\t\telem.appendChild(ov);\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif(soptions.defaultValue !== undefined) { $(elem).val(soptions.defaultValue); }\r\n
\t\t\t\t\t\t\t\tif(soptions.attr) {$(elem).attr(soptions.attr);}\r\n
\t\t\t\t\t\t\t\tif(soptions.dataInit !== undefined) { soptions.dataInit(elem); }\r\n
\t\t\t\t\t\t\t\tif(soptions.dataEvents !== undefined) { bindEvents(elem, soptions.dataEvents); }\r\n
\t\t\t\t\t\t\t\t$(thd).append(elem);\r\n
\t\t\t\t\t\t\t\tif(p.autosearch===true){\r\n
\t\t\t\t\t\t\t\t\t$(elem).change(function(){\r\n
\t\t\t\t\t\t\t\t\t\ttriggerToolbar();\r\n
\t\t\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'text\':\r\n
\t\t\t\t\t\tvar df = soptions.defaultValue !== undefined ? soptions.defaultValue: "";\r\n
\t\t\t\t\t\t$(thd).append("\074input type=\'text\' style=\'width:95%;padding:0px;\' name=\'"+(cm.index || cm.name)+"\' id=\'gs_"+cm.name+"\' value=\'"+df+"\'/\076");\r\n
\t\t\t\t\t\tif(soptions.attr) {$("input",thd).attr(soptions.attr);}\r\n
\t\t\t\t\t\tif(soptions.dataInit !== undefined) { soptions.dataInit($("input",thd)[0]); }\r\n
\t\t\t\t\t\tif(soptions.dataEvents !== undefined) { bindEvents($("input",thd)[0], soptions.dataEvents); }\r\n
\t\t\t\t\t\tif(p.autosearch===true){\r\n
\t\t\t\t\t\t\tif(p.searchOnEnter) {\r\n
\t\t\t\t\t\t\t\t$("input",thd).keypress(function(e){\r\n
\t\t\t\t\t\t\t\t\tvar key = e.charCode ? e.charCode : e.keyCode ? e.keyCode : 0;\r\n
\t\t\t\t\t\t\t\t\tif(key == 13){\r\n
\t\t\t\t\t\t\t\t\t\ttriggerToolbar();\r\n
\t\t\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\treturn this;\r\n
\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$("input",thd).keydown(function(e){\r\n
\t\t\t\t\t\t\t\t\tvar key = e.which;\r\n
\t\t\t\t\t\t\t\t\tswitch (key) {\r\n
\t\t\t\t\t\t\t\t\t\tcase 13:\r\n
\t\t\t\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t\t\t\tcase 9 :\r\n
\t\t\t\t\t\t\t\t\t\tcase 16:\r\n
\t\t\t\t\t\t\t\t\t\tcase 37:\r\n
\t\t\t\t\t\t\t\t\t\tcase 38:\r\n
\t\t\t\t\t\t\t\t\t\tcase 39:\r\n
\t\t\t\t\t\t\t\t\t\tcase 40:\r\n
\t\t\t\t\t\t\t\t\t\tcase 27:\r\n
\t\t\t\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t\t\t\tdefault :\r\n
\t\t\t\t\t\t\t\t\t\t\tif(timeoutHnd) { clearTimeout(timeoutHnd); }\r\n
\t\t\t\t\t\t\t\t\t\t\ttimeoutHnd = setTimeout(function(){triggerToolbar();},500);\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\t$(th).append(thd);\r\n
\t\t\t\t$(tr).append(th);\r\n
\t\t\t});\r\n
\t\t\t$("table thead",$t.grid.hDiv).append(tr);\r\n
\t\t\tthis.ftoolbar = true;\r\n
\t\t\tthis.triggerToolbar = triggerToolbar;\r\n
\t\t\tthis.clearToolbar = clearToolbar;\r\n
\t\t\tthis.toggleToolbar = toggleToolbar;\r\n
\t\t});\r\n
\t},\r\n
\r\n
\tdestroyGroupHeader : function(nullHeader)\r\n
\t{\r\n
\t\tif(typeof(nullHeader) == \'undefined\') {\r\n
\t\t\tnullHeader = true;\r\n
\t\t}\r\n
\t\treturn this.each(function()\r\n
\t\t{\r\n
\t\t\tvar $t = this, $tr, i, l, headers, $th, $resizing, grid = $t.grid,\r\n
\t\t\tthead = $("table.ui-jqgrid-htable thead", grid.hDiv), cm = $t.p.colModel, hc;\r\n
\t\t\tif(!grid) { return; }\r\n
\r\n
\t\t\t$(this).unbind(\'.setGroupHeaders\');\r\n
\t\t\t$tr = $("\074tr\076", {role: "rowheader"}).addClass("ui-jqgrid-labels");\r\n
\t\t\theaders = grid.headers;\r\n
\t\t\tfor (i = 0, l = headers.length; i \074 l; i++) {\r\n
\t\t\t\thc = cm[i].hidden ? "none" : "";\r\n
\t\t\t\t$th = $(headers[i].el)\r\n
\t\t\t\t\t.width(headers[i].width)\r\n
\t\t\t\t\t.css(\'display\',hc);\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\t$th.removeAttr("rowSpan");\r\n
\t\t\t\t} catch (rs) {\r\n
\t\t\t\t\t//IE 6/7\r\n
\t\t\t\t\t$th.attr("rowSpan",1);\r\n
\t\t\t\t}\r\n
\t\t\t\t$tr.append($th);\r\n
\t\t\t\t$resizing = $th.children("span.ui-jqgrid-resize");\r\n
\t\t\t\tif ($resizing.length\0760) {// resizable column\r\n
\t\t\t\t\t$resizing[0].style.height = "";\r\n
\t\t\t\t}\r\n
\t\t\t\t$th.children("div")[0].style.top = "";\r\n
\t\t\t}\r\n
\t\t\t$(thead).children(\'tr.ui-jqgrid-labels\').remove();\r\n
\t\t\t$(thead).prepend($tr);\r\n
\r\n
\t\t\tif(nullHeader === true) {\r\n
\t\t\t\t$($t).jqGrid(\'setGridParam\',{ \'groupHeader\': null});\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\t\r\n
\tsetGroupHeaders : function ( o ) {\r\n
\t\to = $.extend({\r\n
\t\t\tuseColSpanStyle :  false,\r\n
\t\t\tgroupHeaders: []\r\n
\t\t},o  || {});\r\n
\t\treturn this.each(function(){\r\n
\t\t\tthis.p.groupHeader = o;\r\n
\t\t\tvar ts = this,\r\n
\t\t\ti, cmi, skip = 0, $tr, $colHeader, th, $th, thStyle,\r\n
\t\t\tiCol,\r\n
\t\t\tcghi,\r\n
\t\t\t//startColumnName,\r\n
\t\t\tnumberOfColumns,\r\n
\t\t\ttitleText,\r\n
\t\t\tcVisibleColumns,\r\n
\t\t\tcolModel = ts.p.colModel,\r\n
\t\t\tcml = colModel.length,\r\n
\t\t\tths = ts.grid.headers,\r\n
\t\t\t$htable = $("table.ui-jqgrid-htable", ts.grid.hDiv),\r\n
\t\t\t$trLabels = $htable.children("thead").children("tr.ui-jqgrid-labels:last").addClass("jqg-second-row-header"),\r\n
\t\t\t$thead = $htable.children("thead"),\r\n
\t\t\t$theadInTable,\r\n
\t\t\t$firstHeaderRow = $htable.find(".jqg-first-row-header");\r\n
\t\t\tif($firstHeaderRow[0] === undefined) {\r\n
\t\t\t\t$firstHeaderRow = $(\'\074tr\076\', {role: "row", "aria-hidden": "true"}).addClass("jqg-first-row-header").css("height", "auto");\r\n
\t\t\t} else {\r\n
\t\t\t\t$firstHeaderRow.empty();\r\n
\t\t\t}\r\n
\t\t\tvar $firstRow,\r\n
\t\t\tinColumnHeader = function (text, columnHeaders) {\r\n
\t\t\t\tvar i = 0, length = columnHeaders.length;\r\n
\t\t\t\tfor (; i \074 length; i++) {\r\n
\t\t\t\t\tif (columnHeaders[i].startColumnName === text) {\r\n
\t\t\t\t\t\treturn i;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\treturn -1;\r\n
\t\t\t};\r\n
\r\n
\t\t\t$(ts).prepend($thead);\r\n
\t\t\t$tr = $(\'\074tr\076\', {role: "rowheader"}).addClass("ui-jqgrid-labels jqg-third-row-header");\r\n
\t\t\tfor (i = 0; i \074 cml; i++) {\r\n
\t\t\t\tth = ths[i].el;\r\n
\t\t\t\t$th = $(th);\r\n
\t\t\t\tcmi = colModel[i];\r\n
\t\t\t\t// build the next cell for the first header row\r\n
\t\t\t\tthStyle = { height: \'0px\', width: ths[i].width + \'px\', display: (cmi.hidden ? \'none\' : \'\')};\r\n
\t\t\t\t$("\074th\076", {role: \'gridcell\'}).css(thStyle).addClass("ui-first-th-"+ts.p.direction).appendTo($firstHeaderRow);\r\n
\r\n
\t\t\t\tth.style.width = ""; // remove unneeded style\r\n
\t\t\t\tiCol = inColumnHeader(cmi.name, o.groupHeaders);\r\n
\t\t\t\tif (iCol \076= 0) {\r\n
\t\t\t\t\tcghi = o.groupHeaders[iCol];\r\n
\t\t\t\t\tnumberOfColumns = cghi.numberOfColumns;\r\n
\t\t\t\t\ttitleText = cghi.titleText;\r\n
\r\n
\t\t\t\t\t// caclulate the number of visible columns from the next numberOfColumns columns\r\n
\t\t\t\t\tfor (cVisibleColumns = 0, iCol = 0; iCol \074 numberOfColumns \046\046 (i + iCol \074 cml); iCol++) {\r\n
\t\t\t\t\t\tif (!colModel[i + iCol].hidden) {\r\n
\t\t\t\t\t\t\tcVisibleColumns++;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\t// The next numberOfColumns headers will be moved in the next row\r\n
\t\t\t\t\t// in the current row will be placed the new column header with the titleText.\r\n
\t\t\t\t\t// The text will be over the cVisibleColumns columns\r\n
\t\t\t\t\t$colHeader = $(\'\074th\076\').attr({role: "columnheader"})\r\n
\t\t\t\t\t\t.addClass("ui-state-default ui-th-column-header ui-th-"+ts.p.direction)\r\n
\t\t\t\t\t\t.css({\'height\':\'22px\', \'border-top\': \'0px none\'})\r\n
\t\t\t\t\t\t.html(titleText);\r\n
\t\t\t\t\tif(cVisibleColumns \076 0) {\r\n
\t\t\t\t\t\t$colHeader.attr("colspan", String(cVisibleColumns));\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (ts.p.headertitles) {\r\n
\t\t\t\t\t\t$colHeader.attr("title", $colHeader.text());\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t// hide if not a visible cols\r\n
\t\t\t\t\tif( cVisibleColumns === 0) {\r\n
\t\t\t\t\t\t$colHeader.hide();\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\t$th.before($colHeader); // insert new column header before the current\r\n
\t\t\t\t\t$tr.append(th);         // move the current header in the next row\r\n
\r\n
\t\t\t\t\t// set the coumter of headers which will be moved in the next row\r\n
\t\t\t\t\tskip = numberOfColumns - 1;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tif (skip === 0) {\r\n
\t\t\t\t\t\tif (o.useColSpanStyle) {\r\n
\t\t\t\t\t\t\t// expand the header height to two rows\r\n
\t\t\t\t\t\t\t$th.attr("rowspan", "2");\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$(\'\074th\076\', {role: "columnheader"})\r\n
\t\t\t\t\t\t\t\t.addClass("ui-state-default ui-th-column-header ui-th-"+ts.p.direction)\r\n
\t\t\t\t\t\t\t\t.css({"display": cmi.hidden ? \'none\' : \'\', \'border-top\': \'0px none\'})\r\n
\t\t\t\t\t\t\t\t.insertBefore($th);\r\n
\t\t\t\t\t\t\t$tr.append(th);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t// move the header to the next row\r\n
\t\t\t\t\t\t//$th.css({"padding-top": "2px", height: "19px"});\r\n
\t\t\t\t\t\t$tr.append(th);\r\n
\t\t\t\t\t\tskip--;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\t$theadInTable = $(ts).children("thead");\r\n
\t\t\t$theadInTable.prepend($firstHeaderRow);\r\n
\t\t\t$tr.insertAfter($trLabels);\r\n
\t\t\t$htable.append($theadInTable);\r\n
\r\n
\t\t\tif (o.useColSpanStyle) {\r\n
\t\t\t\t// Increase the height of resizing span of visible headers\r\n
\t\t\t\t$htable.find("span.ui-jqgrid-resize").each(function () {\r\n
\t\t\t\t\tvar $parent = $(this).parent();\r\n
\t\t\t\t\tif ($parent.is(":visible")) {\r\n
\t\t\t\t\t\tthis.style.cssText = \'height: \' + $parent.height() + \'px !important; cursor: col-resize;\';\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\r\n
\t\t\t\t// Set position of the sortable div (the main lable)\r\n
\t\t\t\t// with the column header text to the middle of the cell.\r\n
\t\t\t\t// One should not do this for hidden headers.\r\n
\t\t\t\t$htable.find("div.ui-jqgrid-sortable").each(function () {\r\n
\t\t\t\t\tvar $ts = $(this), $parent = $ts.parent();\r\n
\t\t\t\t\tif ($parent.is(":visible") \046\046 $parent.is(":has(span.ui-jqgrid-resize)")) {\r\n
\t\t\t\t\t\t$ts.css(\'top\', ($parent.height() - $ts.outerHeight()) / 2 + \'px\');\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\r\n
\t\t\t$firstRow = $theadInTable.find("tr.jqg-first-row-header");\r\n
\t\t\t$(ts).bind(\'jqGridResizeStop.setGroupHeaders\', function (e, nw, idx) {\r\n
\t\t\t\t$firstRow.find(\'th\').eq(idx).width(nw);\r\n
\t\t\t});\r\n
\t\t});\t\t\t\t\r\n
\t},\r\n
\tsetFrozenColumns : function () {\r\n
\t\treturn this.each(function() {\r\n
\t\t\tif ( !this.grid ) {return;}\r\n
\t\t\tvar $t = this, cm = $t.p.colModel,i=0, len = cm.length, maxfrozen = -1, frozen= false;\r\n
\t\t\t// TODO treeGrid and grouping  Support\r\n
\t\t\tif($t.p.subGrid === true || $t.p.treeGrid === true || $t.p.cellEdit === true || $t.p.sortable || $t.p.scroll || $t.p.grouping )\r\n
\t\t\t{\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t\tif($t.p.rownumbers) { i++; }\r\n
\t\t\tif($t.p.multiselect) { i++; }\r\n
\t\t\t\r\n
\t\t\t// get the max index of frozen col\r\n
\t\t\twhile(i\074len)\r\n
\t\t\t{\r\n
\t\t\t\t// from left, no breaking frozen\r\n
\t\t\t\tif(cm[i].frozen === true)\r\n
\t\t\t\t{\r\n
\t\t\t\t\tfrozen = true;\r\n
\t\t\t\t\tmaxfrozen = i;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t\ti++;\r\n
\t\t\t}\r\n
\t\t\tif( maxfrozen\076=0 \046\046 frozen) {\r\n
\t\t\t\tvar top = $t.p.caption ? $($t.grid.cDiv).outerHeight() : 0,\r\n
\t\t\t\thth = $(".ui-jqgrid-htable","#gview_"+$.jgrid.jqID($t.p.id)).height();\r\n
\t\t\t\t//headers\r\n
\t\t\t\tif($t.p.toppager) {\r\n
\t\t\t\t\ttop = top + $($t.grid.topDiv).outerHeight();\r\n
\t\t\t\t}\r\n
\t\t\t\tif($t.p.toolbar[0] === true) {\r\n
\t\t\t\t\tif($t.p.toolbar[1] != "bottom") {\r\n
\t\t\t\t\t\ttop = top + $($t.grid.uDiv).outerHeight();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\t$t.grid.fhDiv = $(\'\074div style="position:absolute;left:0px;top:\'+top+\'px;height:\'+hth+\'px;" class="frozen-div ui-state-default ui-jqgrid-hdiv"\076\074/div\076\');\r\n
\t\t\t\t$t.grid.fbDiv = $(\'\074div style="position:absolute;left:0px;top:\'+(parseInt(top,10)+parseInt(hth,10) + 1)+\'px;overflow-y:hidden" class="frozen-bdiv ui-jqgrid-bdiv"\076\074/div\076\');\r\n
\t\t\t\t$("#gview_"+$.jgrid.jqID($t.p.id)).append($t.grid.fhDiv);\r\n
\t\t\t\tvar htbl = $(".ui-jqgrid-htable","#gview_"+$.jgrid.jqID($t.p.id)).clone(true);\r\n
\t\t\t\t// groupheader support - only if useColSpanstyle is false\r\n
\t\t\t\tif($t.p.groupHeader) {\r\n
\t\t\t\t\t$("tr.jqg-first-row-header, tr.jqg-third-row-header", htbl).each(function(){\r\n
\t\t\t\t\t\t$("th:gt("+maxfrozen+")",this).remove();\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tvar swapfroz = -1, fdel = -1;\r\n
\t\t\t\t\t$("tr.jqg-second-row-header th", htbl).each(function(){\r\n
\t\t\t\t\t\tvar cs= parseInt($(this).attr("colspan"),10);\r\n
\t\t\t\t\t\tif(cs) {\r\n
\t\t\t\t\t\t\tswapfroz = swapfroz+cs;\r\n
\t\t\t\t\t\t\tfdel++;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(swapfroz === maxfrozen) {\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tif(swapfroz !== maxfrozen) {\r\n
\t\t\t\t\t\tfdel = maxfrozen;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$("tr.jqg-second-row-header", htbl).each(function(){\r\n
\t\t\t\t\t\t$("th:gt("+fdel+")",this).remove();\r\n
\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$("tr",htbl).each(function(){\r\n
\t\t\t\t\t\t$("th:gt("+maxfrozen+")",this).remove();\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\t$(htbl).width(1);\r\n
\t\t\t\t// resizing stuff\r\n
\t\t\t\t$($t.grid.fhDiv).append(htbl)\r\n
\t\t\t\t.mousemove(function (e) {\r\n
\t\t\t\t\tif($t.grid.resizing){ $t.grid.dragMove(e);return false; }\r\n
\t\t\t\t});\r\n
\t\t\t\t$($t).bind(\'jqGridResizeStop.setFrozenColumns\', function (e, w, index) {\r\n
\t\t\t\t\tvar rhth = $(".ui-jqgrid-htable",$t.grid.fhDiv);\r\n
\t\t\t\t\t$("th:eq("+index+")",rhth).width( w ); \r\n
\t\t\t\t\tvar btd = $(".ui-jqgrid-btable",$t.grid.fbDiv);\r\n
\t\t\t\t\t$("tr:first td:eq("+index+")",btd).width( w ); \r\n
\t\t\t\t});\r\n
\t\t\t\t// sorting stuff\r\n
\t\t\t\t$($t).bind(\'jqGridOnSortCol.setFrozenColumns\', function (index, idxcol) {\r\n
\r\n
\t\t\t\t\tvar previousSelectedTh = $("tr.ui-jqgrid-labels:last th:eq("+$t.p.lastsort+")",$t.grid.fhDiv), newSelectedTh = $("tr.ui-jqgrid-labels:last th:eq("+idxcol+")",$t.grid.fhDiv);\r\n
\r\n
\t\t\t\t\t$("span.ui-grid-ico-sort",previousSelectedTh).addClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t$(previousSelectedTh).attr("aria-selected","false");\r\n
\t\t\t\t\t$("span.ui-icon-"+$t.p.sortorder,newSelectedTh).removeClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t$(newSelectedTh).attr("aria-selected","true");\r\n
\t\t\t\t\tif(!$t.p.viewsortcols[0]) {\r\n
\t\t\t\t\t\tif($t.p.lastsort != idxcol) {\r\n
\t\t\t\t\t\t\t$("span.s-ico",previousSelectedTh).hide();\r\n
\t\t\t\t\t\t\t$("span.s-ico",newSelectedTh).show();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\t\r\n
\t\t\t\t// data stuff\r\n
\t\t\t\t//TODO support for setRowData\r\n
\t\t\t\t$("#gview_"+$.jgrid.jqID($t.p.id)).append($t.grid.fbDiv);\r\n
\t\t\t\tjQuery($t.grid.bDiv).scroll(function () {\r\n
\t\t\t\t\tjQuery($t.grid.fbDiv).scrollTop(jQuery(this).scrollTop());\r\n
\t\t\t\t});\r\n
\t\t\t\tif($t.p.hoverrows === true) {\r\n
\t\t\t\t\t$("#"+$.jgrid.jqID($t.p.id)).unbind(\'mouseover\').unbind(\'mouseout\');\r\n
\t\t\t\t}\r\n
\t\t\t\t$($t).bind(\'jqGridAfterGridComplete.setFrozenColumns\', function () {\r\n
\t\t\t\t\t$("#"+$.jgrid.jqID($t.p.id)+"_frozen").remove();\r\n
\t\t\t\t\tjQuery($t.grid.fbDiv).height( jQuery($t.grid.bDiv).height()-16);\r\n
\t\t\t\t\tvar btbl = $("#"+$.jgrid.jqID($t.p.id)).clone(true);\r\n
\t\t\t\t\t$("tr",btbl).each(function(){\r\n
\t\t\t\t\t\t$("td:gt("+maxfrozen+")",this).remove();\r\n
\t\t\t\t\t});\r\n
\r\n
\t\t\t\t\t$(btbl).width(1).attr("id",$t.p.id+"_frozen");\r\n
\t\t\t\t\t$($t.grid.fbDiv).append(btbl);\r\n
\t\t\t\t\tif($t.p.hoverrows === true) {\r\n
\t\t\t\t\t\t$("tr.jqgrow", btbl).hover(\r\n
\t\t\t\t\t\t\tfunction(){ $(this).addClass("ui-state-hover"); $("#"+$.jgrid.jqID(this.id), "#"+$.jgrid.jqID($t.p.id)).addClass("ui-state-hover"); },\r\n
\t\t\t\t\t\t\tfunction(){ $(this).removeClass("ui-state-hover"); $("#"+$.jgrid.jqID(this.id), "#"+$.jgrid.jqID($t.p.id)).removeClass("ui-state-hover"); }\r\n
\t\t\t\t\t\t);\r\n
\t\t\t\t\t\t$("tr.jqgrow", "#"+$.jgrid.jqID($t.p.id)).hover(\r\n
\t\t\t\t\t\t\tfunction(){ $(this).addClass("ui-state-hover"); $("#"+$.jgrid.jqID(this.id), "#"+$.jgrid.jqID($t.p.id)+"_frozen").addClass("ui-state-hover");},\r\n
\t\t\t\t\t\t\tfunction(){ $(this).removeClass("ui-state-hover"); $("#"+$.jgrid.jqID(this.id), "#"+$.jgrid.jqID($t.p.id)+"_frozen").removeClass("ui-state-hover"); }\r\n
\t\t\t\t\t\t);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tbtbl=null;\r\n
\t\t\t\t});\r\n
\t\t\t\t$t.p.frozenColumns = true;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tdestroyFrozenColumns :  function() {\r\n
\t\treturn this.each(function() {\r\n
\t\t\tif ( !this.grid ) {return;}\r\n
\t\t\tif(this.p.frozenColumns === true) {\r\n
\t\t\t\tvar $t = this;\r\n
\t\t\t\t$($t.grid.fhDiv).remove();\r\n
\t\t\t\t$($t.grid.fbDiv).remove();\r\n
\t\t\t\t$t.grid.fhDiv = null; $t.grid.fbDiv=null;\r\n
\t\t\t\t$(this).unbind(\'.setFrozenColumns\');\r\n
\t\t\t\tif($t.p.hoverrows === true) {\r\n
\t\t\t\t\tvar ptr;\r\n
\t\t\t\t\t$("#"+$.jgrid.jqID($t.p.id)).bind(\'mouseover\',function(e) {\r\n
\t\t\t\t\t\tptr = $(e.target).closest("tr.jqgrow");\r\n
\t\t\t\t\t\tif($(ptr).attr("class") !== "ui-subgrid") {\r\n
\t\t\t\t\t\t$(ptr).addClass("ui-state-hover");\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t}).bind(\'mouseout\',function(e) {\r\n
\t\t\t\t\t\tptr = $(e.target).closest("tr.jqgrow");\r\n
\t\t\t\t\t\t$(ptr).removeClass("ui-state-hover");\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\tthis.p.frozenColumns = false;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t}\r\n
});\r\n
})(jQuery);/*\r\n
 * jqModal - Minimalist Modaling with jQuery\r\n
 *   (http://dev.iceburg.net/jquery/jqmodal/)\r\n
 *\r\n
 * Copyright (c) 2007,2008 Brice Burgess \074bhb@iceburg.net\076\r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 *   http://www.opensource.org/licenses/mit-license.php\r\n
 *   http://www.gnu.org/licenses/gpl.html\r\n
 * \r\n
 * $Version: 07/06/2008 +r13\r\n
 */\r\n
(function($) {\r\n
$.fn.jqm=function(o){\r\n
var p={\r\n
overlay: 50,\r\n
closeoverlay : true,\r\n
overlayClass: \'jqmOverlay\',\r\n
closeClass: \'jqmClose\',\r\n
trigger: \'.jqModal\',\r\n
ajax: F,\r\n
ajaxText: \'\',\r\n
target: F,\r\n
modal: F,\r\n
toTop: F,\r\n
onShow: F,\r\n
onHide: F,\r\n
onLoad: F\r\n
};\r\n
return this.each(function(){if(this._jqm)return H[this._jqm].c=$.extend({},H[this._jqm].c,o);s++;this._jqm=s;\r\n
H[s]={c:$.extend(p,$.jqm.params,o),a:F,w:$(this).addClass(\'jqmID\'+s),s:s};\r\n
if(p.trigger)$(this).jqmAddTrigger(p.trigger);\r\n
});};\r\n
\r\n
$.fn.jqmAddClose=function(e){return hs(this,e,\'jqmHide\');};\r\n
$.fn.jqmAddTrigger=function(e){return hs(this,e,\'jqmShow\');};\r\n
$.fn.jqmShow=function(t){return this.each(function(){$.jqm.open(this._jqm,t);});};\r\n
$.fn.jqmHide=function(t){return this.each(function(){$.jqm.close(this._jqm,t)});};\r\n
\r\n
$.jqm = {\r\n
hash:{},\r\n
open:function(s,t){var h=H[s],c=h.c,cc=\'.\'+c.closeClass,z=(parseInt(h.w.css(\'z-index\')));z=(z\0760)?z:3000;var o=$(\'\074div\076\074/div\076\').css({height:\'100%\',width:\'100%\',position:\'fixed\',left:0,top:0,\'z-index\':z-1,opacity:c.overlay/100});if(h.a)return F;h.t=t;h.a=true;h.w.css(\'z-index\',z);\r\n
 if(c.modal) {if(!A[0])setTimeout(function(){L(\'bind\');},1);A.push(s);}\r\n
 else if(c.overlay \076 0) {if(c.closeoverlay) h.w.jqmAddClose(o);}\r\n
 else o=F;\r\n
\r\n
 h.o=(o)?o.addClass(c.overlayClass).prependTo(\'body\'):F;\r\n
 if(ie6){$(\'html,body\').css({height:\'100%\',width:\'100%\'});if(o){o=o.css({position:\'absolute\'})[0];for(var y in {Top:1,Left:1})o.style.setExpression(y.toLowerCase(),"(_=(document.documentElement.scroll"+y+" || document.body.scroll"+y+"))+\'px\'");}}\r\n
\r\n
 if(c.ajax) {var r=c.target||h.w,u=c.ajax;r=(typeof r == \'string\')?$(r,h.w):$(r);u=(u.substr(0,1) == \'@\')?$(t).attr(u.substring(1)):u;\r\n
  r.html(c.ajaxText).load(u,function(){if(c.onLoad)c.onLoad.call(this,h);if(cc)h.w.jqmAddClose($(cc,h.w));e(h);});}\r\n
 else if(cc)h.w.jqmAddClose($(cc,h.w));\r\n
\r\n
 if(c.toTop\046\046h.o)h.w.before(\'\074span id="jqmP\'+h.w[0]._jqm+\'"\076\074/span\076\').insertAfter(h.o);\t\r\n
 (c.onShow)?c.onShow(h):h.w.show();e(h);return F;\r\n
},\r\n
close:function(s){var h=H[s];if(!h.a)return F;h.a=F;\r\n
 if(A[0]){A.pop();if(!A[0])L(\'unbind\');}\r\n
 if(h.c.toTop\046\046h.o)$(\'#jqmP\'+h.w[0]._jqm).after(h.w).remove();\r\n
 if(h.c.onHide)h.c.onHide(h);else{h.w.hide();if(h.o)h.o.remove();} return F;\r\n
},\r\n
params:{}};\r\n
var s=0,H=$.jqm.hash,A=[],ie6=$.browser.msie\046\046($.browser.version == "6.0"),F=false,\r\n
e=function(h){var i=$(\'\074iframe src="javascript:false;document.write(\\\'\\\');" class="jqm"\076\074/iframe\076\').css({opacity:0});if(ie6)if(h.o)h.o.html(\'\074p style="width:100%;height:100%"/\076\').prepend(i);else if(!$(\'iframe.jqm\',h.w)[0])h.w.prepend(i); f(h);},\r\n
f=function(h){try{$(\':input:visible\',h.w)[0].focus();}catch(_){}},\r\n
L=function(t){$(document)[t]("keypress",m)[t]("keydown",m)[t]("mousedown",m);},\r\n
m=function(e){var h=H[A[A.length-1]],r=(!$(e.target).parents(\'.jqmID\'+h.s)[0]);if(r)f(h);return !r;},\r\n
hs=function(w,t,c){return w.each(function(){var s=this._jqm;$(t).each(function() {\r\n
 if(!this[c]){this[c]=[];$(this).click(function(){for(var i in {jqmShow:1,jqmHide:1})for(var s in this[i])if(H[this[i][s]])H[this[i][s]].w[i](this);return F;});}this[c].push(s);});});};\r\n
})(jQuery);/*\r\n
 * jqDnR - Minimalistic Drag\'n\'Resize for jQuery.\r\n
 *\r\n
 * Copyright (c) 2007 Brice Burgess \074bhb@iceburg.net\076, http://www.iceburg.net\r\n
 * Licensed under the MIT License:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * \r\n
 * $Version: 2007.08.19 +r2\r\n
 */\r\n
\r\n
(function($){\r\n
$.fn.jqDrag=function(h){return i(this,h,\'d\');};\r\n
$.fn.jqResize=function(h,ar){return i(this,h,\'r\',ar);};\r\n
$.jqDnR={\r\n
\tdnr:{},\r\n
\te:0,\r\n
\tdrag:function(v){\r\n
\t\tif(M.k == \'d\'){E.css({left:M.X+v.pageX-M.pX,top:M.Y+v.pageY-M.pY});}\r\n
\t\telse {\r\n
\t\t\tE.css({width:Math.max(v.pageX-M.pX+M.W,0),height:Math.max(v.pageY-M.pY+M.H,0)});\r\n
\t\t\tif(M1){E1.css({width:Math.max(v.pageX-M1.pX+M1.W,0),height:Math.max(v.pageY-M1.pY+M1.H,0)});}\r\n
\t\t}\r\n
\t\treturn false;\r\n
\t},\r\n
\tstop:function(){\r\n
\t\t//E.css(\'opacity\',M.o);\r\n
\t\t$(document).unbind(\'mousemove\',J.drag).unbind(\'mouseup\',J.stop);\r\n
\t}\r\n
};\r\n
var J=$.jqDnR,M=J.dnr,E=J.e,E1,M1,\r\n
i=function(e,h,k,aR){\r\n
\treturn e.each(function(){\r\n
\t\th=(h)?$(h,e):e;\r\n
\t\th.bind(\'mousedown\',{e:e,k:k},function(v){\r\n
\t\t\tvar d=v.data,p={};E=d.e;E1 = aR ? $(aR) : false;\r\n
\t\t\t// attempt utilization of dimensions plugin to fix IE issues\r\n
\t\t\tif(E.css(\'position\') != \'relative\'){try{E.position(p);}catch(e){}}\r\n
\t\t\tM={\r\n
\t\t\t\tX:p.left||f(\'left\')||0,\r\n
\t\t\t\tY:p.top||f(\'top\')||0,\r\n
\t\t\t\tW:f(\'width\')||E[0].scrollWidth||0,\r\n
\t\t\t\tH:f(\'height\')||E[0].scrollHeight||0,\r\n
\t\t\t\tpX:v.pageX,\r\n
\t\t\t\tpY:v.pageY,\r\n
\t\t\t\tk:d.k\r\n
\t\t\t\t//o:E.css(\'opacity\')\r\n
\t\t\t};\r\n
\t\t\t// also resize\r\n
\t\t\tif(E1 \046\046 d.k != \'d\'){\r\n
\t\t\t\tM1={\r\n
\t\t\t\t\tX:p.left||f1(\'left\')||0,\r\n
\t\t\t\t\tY:p.top||f1(\'top\')||0,\r\n
\t\t\t\t\tW:E1[0].offsetWidth||f1(\'width\')||0,\r\n
\t\t\t\t\tH:E1[0].offsetHeight||f1(\'height\')||0,\r\n
\t\t\t\t\tpX:v.pageX,\r\n
\t\t\t\t\tpY:v.pageY,\r\n
\t\t\t\t\tk:d.k\r\n
\t\t\t\t};\r\n
\t\t\t} else {M1 = false;}\t\t\t\r\n
\t\t\t//E.css({opacity:0.8});\r\n
\t\t\tif($("input.hasDatepicker",E[0])[0]) {\r\n
\t\t\ttry {$("input.hasDatepicker",E[0]).datepicker(\'hide\');}catch (dpe){}\r\n
\t\t\t}\r\n
\t\t\t$(document).mousemove($.jqDnR.drag).mouseup($.jqDnR.stop);\r\n
\t\t\treturn false;\r\n
\t\t});\r\n
\t});\r\n
},\r\n
f=function(k){return parseInt(E.css(k),10)||false;},\r\n
f1=function(k){return parseInt(E1.css(k),10)||false;};\r\n
})(jQuery);/*\r\n
\tThe below work is licensed under Creative Commons GNU LGPL License.\r\n
\r\n
\tOriginal work:\r\n
\r\n
\tLicense:     http://creativecommons.org/licenses/LGPL/2.1/\r\n
\tAuthor:      Stefan Goessner/2006\r\n
\tWeb:         http://goessner.net/ \r\n
\r\n
\tModifications made:\r\n
\r\n
\tVersion:     0.9-p5\r\n
\tDescription: Restructured code, JSLint validated (no strict whitespaces),\r\n
\t             added handling of empty arrays, empty strings, and int/floats values.\r\n
\tAuthor:      Michael Schøler/2008-01-29\r\n
\tWeb:         http://michael.hinnerup.net/blog/2008/01/26/converting-json-to-xml-and-xml-to-json/\r\n
\t\r\n
\tDescription: json2xml added support to convert functions as CDATA\r\n
\t             so it will be easy to write characters that cause some problems when convert\r\n
\tAuthor:      Tony Tomov\r\n
*/\r\n
\r\n
/*global alert */\r\n
var xmlJsonClass = {\r\n
\t// Param "xml": Element or document DOM node.\r\n
\t// Param "tab": Tab or indent string for pretty output formatting omit or use empty string "" to supress.\r\n
\t// Returns:     JSON string\r\n
\txml2json: function(xml, tab) {\r\n
\t\tif (xml.nodeType === 9) {\r\n
\t\t\t// document node\r\n
\t\t\txml = xml.documentElement;\r\n
\t\t}\r\n
\t\tvar nws = this.removeWhite(xml);\r\n
\t\tvar obj = this.toObj(nws);\r\n
\t\tvar json = this.toJson(obj, xml.nodeName, "\\t");\r\n
\t\treturn "{\\n" + tab + (tab ? json.replace(/\\t/g, tab) : json.replace(/\\t|\\n/g, "")) + "\\n}";\r\n
\t},\r\n
\r\n
\t// Param "o":   JavaScript object\r\n
\t// Param "tab": tab or indent string for pretty output formatting omit or use empty string "" to supress.\r\n
\t// Returns:     XML string\r\n
\tjson2xml: function(o, tab) {\r\n
\t\tvar toXml = function(v, name, ind) {\r\n
\t\t\tvar xml = "";\r\n
\t\t\tvar i, n;\r\n
\t\t\tif (v instanceof Array) {\r\n
\t\t\t\tif (v.length === 0) {\r\n
\t\t\t\t\txml += ind + "\074"+name+"\076__EMPTY_ARRAY_\074/"+name+"\076\\n";\r\n
\t\t\t\t}\r\n
\t\t\t\telse {\r\n
\t\t\t\t\tfor (i = 0, n = v.length; i \074 n; i += 1) {\r\n
\t\t\t\t\t\tvar sXml = ind + toXml(v[i], name, ind+"\\t") + "\\n";\r\n
\t\t\t\t\t\txml += sXml;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\telse if (typeof(v) === "object") {\r\n
\t\t\t\tvar hasChild = false;\r\n
\t\t\t\txml += ind + "\074" + name;\r\n
\t\t\t\tvar m;\r\n
\t\t\t\tfor (m in v) if (v.hasOwnProperty(m)) {\r\n
\t\t\t\t\tif (m.charAt(0) === "@") {\r\n
\t\t\t\t\t\txml += " " + m.substr(1) + "=\\"" + v[m].toString() + "\\"";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\thasChild = true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\txml += hasChild ? "\076" : "/\076";\r\n
\t\t\t\tif (hasChild) {\r\n
\t\t\t\t\tfor (m in v) if (v.hasOwnProperty(m)) {\r\n
\t\t\t\t\t\tif (m === "#text") {\r\n
\t\t\t\t\t\t\txml += v[m];\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\telse if (m === "#cdata") {\r\n
\t\t\t\t\t\t\txml += "\074![CDATA[" + v[m] + "]]\076";\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\telse if (m.charAt(0) !== "@") {\r\n
\t\t\t\t\t\t\txml += toXml(v[m], m, ind+"\\t");\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\txml += (xml.charAt(xml.length - 1) === "\\n" ? ind : "") + "\074/" + name + "\076";\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\telse if (typeof(v) === "function") {\r\n
\t\t\t\txml += ind + "\074" + name + "\076" + "\074![CDATA[" + v + "]]\076" + "\074/" + name + "\076";\r\n
\t\t\t}\r\n
\t\t\telse {\r\n
\t\t\t\tif (v === undefined ) { v = ""; }\r\n
\t\t\t\tif (v.toString() === "\\"\\"" || v.toString().length === 0) {\r\n
\t\t\t\t\txml += ind + "\074" + name + "\076__EMPTY_STRING_\074/" + name + "\076";\r\n
\t\t\t\t} \r\n
\t\t\t\telse {\r\n
\t\t\t\t\txml += ind + "\074" + name + "\076" + v.toString() + "\074/" + name + "\076";\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\treturn xml;\r\n
\t\t};\r\n
\t\tvar xml = "";\r\n
\t\tvar m;\r\n
\t\tfor (m in o) if (o.hasOwnProperty(m)) {\r\n
\t\t\txml += toXml(o[m], m, "");\r\n
\t\t}\r\n
\t\treturn tab ? xml.replace(/\\t/g, tab) : xml.replace(/\\t|\\n/g, "");\r\n
\t},\r\n
\t// Internal methods\r\n
\ttoObj: function(xml) {\r\n
\t\tvar o = {};\r\n
\t\tvar FuncTest = /function/i;\r\n
\t\tif (xml.nodeType === 1) {\r\n
\t\t\t// element node ..\r\n
\t\t\tif (xml.attributes.length) {\r\n
\t\t\t\t// element with attributes ..\r\n
\t\t\t\tvar i;\r\n
\t\t\t\tfor (i = 0; i \074 xml.attributes.length; i += 1) {\r\n
\t\t\t\t\to["@" + xml.attributes[i].nodeName] = (xml.attributes[i].nodeValue || "").toString();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif (xml.firstChild) {\r\n
\t\t\t\t// element has child nodes ..\r\n
\t\t\t\tvar textChild = 0, cdataChild = 0, hasElementChild = false;\r\n
\t\t\t\tvar n;\r\n
\t\t\t\tfor (n = xml.firstChild; n; n = n.nextSibling) {\r\n
\t\t\t\t\tif (n.nodeType === 1) {\r\n
\t\t\t\t\t\thasElementChild = true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse if (n.nodeType === 3 \046\046 n.nodeValue.match(/[^ \\f\\n\\r\\t\\v]/)) {\r\n
\t\t\t\t\t\t// non-whitespace text\r\n
\t\t\t\t\t\ttextChild += 1;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse if (n.nodeType === 4) {\r\n
\t\t\t\t\t\t// cdata section node\r\n
\t\t\t\t\t\tcdataChild += 1;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif (hasElementChild) {\r\n
\t\t\t\t\tif (textChild \074 2 \046\046 cdataChild \074 2) {\r\n
\t\t\t\t\t\t// structured element with evtl. a single text or/and cdata node ..\r\n
\t\t\t\t\t\tthis.removeWhite(xml);\r\n
\t\t\t\t\t\tfor (n = xml.firstChild; n; n = n.nextSibling) {\r\n
\t\t\t\t\t\t\tif (n.nodeType === 3) {\r\n
\t\t\t\t\t\t\t\t// text node\r\n
\t\t\t\t\t\t\t\to["#text"] = this.escape(n.nodeValue);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\telse if (n.nodeType === 4) {\r\n
\t\t\t\t\t\t\t\t// cdata node\r\n
\t\t\t\t\t\t\t\tif (FuncTest.test(n.nodeValue)) {\r\n
\t\t\t\t\t\t\t\t\to[n.nodeName] = [o[n.nodeName], n.nodeValue];\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\to["#cdata"] = this.escape(n.nodeValue);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\telse if (o[n.nodeName]) {\r\n
\t\t\t\t\t\t\t\t// multiple occurence of element ..\r\n
\t\t\t\t\t\t\t\tif (o[n.nodeName] instanceof Array) {\r\n
\t\t\t\t\t\t\t\t\to[n.nodeName][o[n.nodeName].length] = this.toObj(n);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\telse {\r\n
\t\t\t\t\t\t\t\t\to[n.nodeName] = [o[n.nodeName], this.toObj(n)];\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\telse {\r\n
\t\t\t\t\t\t\t\t// first occurence of element ..\r\n
\t\t\t\t\t\t\t\to[n.nodeName] = this.toObj(n);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\t// mixed content\r\n
\t\t\t\t\t\tif (!xml.attributes.length) {\r\n
\t\t\t\t\t\t\to = this.escape(this.innerXml(xml));\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\telse {\r\n
\t\t\t\t\t\t\to["#text"] = this.escape(this.innerXml(xml));\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\telse if (textChild) {\r\n
\t\t\t\t\t// pure text\r\n
\t\t\t\t\tif (!xml.attributes.length) {\r\n
\t\t\t\t\t\to = this.escape(this.innerXml(xml));\r\n
\t\t\t\t\t\tif (o === "__EMPTY_ARRAY_") {\r\n
\t\t\t\t\t\t\to = "[]";\r\n
\t\t\t\t\t\t} else if (o === "__EMPTY_STRING_") {\r\n
\t\t\t\t\t\t\to = "";\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\to["#text"] = this.escape(this.innerXml(xml));\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\telse if (cdataChild) {\r\n
\t\t\t\t\t// cdata\r\n
\t\t\t\t\tif (cdataChild \076 1) {\r\n
\t\t\t\t\t\to = this.escape(this.innerXml(xml));\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\tfor (n = xml.firstChild; n; n = n.nextSibling) {\r\n
\t\t\t\t\t\t\tif(FuncTest.test(xml.firstChild.nodeValue)) {\r\n
\t\t\t\t\t\t\t\to = xml.firstChild.nodeValue;\r\n
\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\to["#cdata"] = this.escape(n.nodeValue);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif (!xml.attributes.length \046\046 !xml.firstChild) {\r\n
\t\t\t\to = null;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\telse if (xml.nodeType === 9) {\r\n
\t\t\t// document.node\r\n
\t\t\to = this.toObj(xml.documentElement);\r\n
\t\t}\r\n
\t\telse {\r\n
\t\t\talert("unhandled node type: " + xml.nodeType);\r\n
\t\t}\r\n
\t\treturn o;\r\n
\t},\r\n
\ttoJson: function(o, name, ind, wellform) {\r\n
\t\tif(wellform === undefined) wellform = true;\r\n
\t\tvar json = name ? ("\\"" + name + "\\"") : "", tab = "\\t", newline = "\\n";\r\n
\t\tif(!wellform) {\r\n
\t\t\ttab= ""; newline= "";\r\n
\t\t}\r\n
\r\n
\t\tif (o === "[]") {\r\n
\t\t\tjson += (name ? ":[]" : "[]");\r\n
\t\t}\r\n
\t\telse if (o instanceof Array) {\r\n
\t\t\tvar n, i, ar=[];\r\n
\t\t\tfor (i = 0, n = o.length; i \074 n; i += 1) {\r\n
\t\t\t\tar[i] = this.toJson(o[i], "", ind + tab, wellform);\r\n
\t\t\t}\r\n
\t\t\tjson += (name ? ":[" : "[") + (ar.length \076 1 ? (newline + ind + tab + ar.join(","+newline + ind + tab) + newline + ind) : ar.join("")) + "]";\r\n
\t\t}\r\n
\t\telse if (o === null) {\r\n
\t\t\tjson += (name \046\046 ":") + "null";\r\n
\t\t}\r\n
\t\telse if (typeof(o) === "object") {\r\n
\t\t\tvar arr = [], m;\r\n
\t\t\tfor (m in o) {\r\n
\t\t\t\tif (o.hasOwnProperty(m)) {\r\n
\t\t\t\t\tarr[arr.length] = this.toJson(o[m], m, ind + tab, wellform);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\t\tjson += (name ? ":{" : "{") + (arr.length \076 1 ? (newline + ind + tab + arr.join(","+newline + ind + tab) + newline + ind) : arr.join("")) + "}";\r\n
\t\t}\r\n
\t\telse if (typeof(o) === "string") {\r\n
\t\t\t/*\r\n
\t\t\tvar objRegExp  = /(^-?\\d+\\.?\\d*$)/;\r\n
\t\t\tvar FuncTest = /function/i;\r\n
\t\t\tvar os = o.toString();\r\n
\t\t\tif (objRegExp.test(os) || FuncTest.test(os) || os==="false" || os==="true") {\r\n
\t\t\t\t// int or float\r\n
\t\t\t\tjson += (name \046\046 ":")  + "\\"" +os + "\\"";\r\n
\t\t\t} \r\n
\t\t\telse {\r\n
\t\t\t*/\r\n
\t\t\t\tjson += (name \046\046 ":") + "\\"" + o.replace(/\\\\/g,\'\\\\\\\\\').replace(/\\"/g,\'\\\\"\') + "\\"";\r\n
\t\t\t//}\r\n
\t\t\t}\r\n
\t\telse {\r\n
\t\t\tjson += (name \046\046 ":") +  o.toString();\r\n
\t\t}\r\n
\t\treturn json;\r\n
\t},\r\n
\tinnerXml: function(node) {\r\n
\t\tvar s = "";\r\n
\t\tif ("innerHTML" in node) {\r\n
\t\t\ts = node.innerHTML;\r\n
\t\t}\r\n
\t\telse {\r\n
\t\t\tvar asXml = function(n) {\r\n
\t\t\t\tvar s = "", i;\r\n
\t\t\t\tif (n.nodeType === 1) {\r\n
\t\t\t\t\ts += "\074" + n.nodeName;\r\n
\t\t\t\t\tfor (i = 0; i \074 n.attributes.length; i += 1) {\r\n
\t\t\t\t\t\ts += " " + n.attributes[i].nodeName + "=\\"" + (n.attributes[i].nodeValue || "").toString() + "\\"";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (n.firstChild) {\r\n
\t\t\t\t\t\ts += "\076";\r\n
\t\t\t\t\t\tfor (var c = n.firstChild; c; c = c.nextSibling) {\r\n
\t\t\t\t\t\t\ts += asXml(c);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ts += "\074/" + n.nodeName + "\076";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\ts += "/\076";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\telse if (n.nodeType === 3) {\r\n
\t\t\t\t\ts += n.nodeValue;\r\n
\t\t\t\t}\r\n
\t\t\t\telse if (n.nodeType === 4) {\r\n
\t\t\t\t\ts += "\074![CDATA[" + n.nodeValue + "]]\076";\r\n
\t\t\t\t}\r\n
\t\t\t\treturn s;\r\n
\t\t\t};\r\n
\t\t\tfor (var c = node.firstChild; c; c = c.nextSibling) {\r\n
\t\t\t\ts += asXml(c);\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn s;\r\n
\t},\r\n
\tescape: function(txt) {\r\n
\t\treturn txt.replace(/[\\\\]/g, "\\\\\\\\").replace(/[\\"]/g, \'\\\\"\').replace(/[\\n]/g, \'\\\\n\').replace(/[\\r]/g, \'\\\\r\');\r\n
\t},\r\n
\tremoveWhite: function(e) {\r\n
\t\te.normalize();\r\n
\t\tvar n;\r\n
\t\tfor (n = e.firstChild; n; ) {\r\n
\t\t\tif (n.nodeType === 3) {\r\n
\t\t\t\t// text node\r\n
\t\t\t\tif (!n.nodeValue.match(/[^ \\f\\n\\r\\t\\v]/)) {\r\n
\t\t\t\t\t// pure whitespace text node\r\n
\t\t\t\t\tvar nxt = n.nextSibling;\r\n
\t\t\t\t\te.removeChild(n);\r\n
\t\t\t\t\tn = nxt;\r\n
\t\t\t\t}\r\n
\t\t\t\telse {\r\n
\t\t\t\t\tn = n.nextSibling;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\telse if (n.nodeType === 1) {\r\n
\t\t\t\t// element node\r\n
\t\t\t\tthis.removeWhite(n);\r\n
\t\t\t\tn = n.nextSibling;\r\n
\t\t\t}\r\n
\t\t\telse {\r\n
\t\t\t\t// any other node\r\n
\t\t\t\tn = n.nextSibling;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn e;\r\n
\t}\r\n
};/*\r\n
**\r\n
 * formatter for values but most of the values if for jqGrid\r\n
 * Some of this was inspired and based on how YUI does the table datagrid but in jQuery fashion\r\n
 * we are trying to keep it as light as possible\r\n
 * Joshua Burnett josh@9ci.com\t\r\n
 * http://www.greenbill.com\r\n
 *\r\n
 * Changes from Tony Tomov tony@trirand.com\r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
 * \r\n
**/\r\n
\r\n
;(function($) {\r\n
"use strict";\t\r\n
\t$.fmatter = {};\r\n
\t//opts can be id:row id for the row, rowdata:the data for the row, colmodel:the column model for this column\r\n
\t//example {id:1234,}\r\n
\t$.extend($.fmatter,{\r\n
\t\tisBoolean : function(o) {\r\n
\t\t\treturn typeof o === \'boolean\';\r\n
\t\t},\r\n
\t\tisObject : function(o) {\r\n
\t\t\treturn (o \046\046 (typeof o === \'object\' || $.isFunction(o))) || false;\r\n
\t\t},\r\n
\t\tisString : function(o) {\r\n
\t\t\treturn typeof o === \'string\';\r\n
\t\t},\r\n
\t\tisNumber : function(o) {\r\n
\t\t\treturn typeof o === \'number\' \046\046 isFinite(o);\r\n
\t\t},\r\n
\t\tisNull : function(o) {\r\n
\t\t\treturn o === null;\r\n
\t\t},\r\n
\t\tisUndefined : function(o) {\r\n
\t\t\treturn typeof o === \'undefined\';\r\n
\t\t},\r\n
\t\tisValue : function (o) {\r\n
\t\t\treturn (this.isObject(o) || this.isString(o) || this.isNumber(o) || this.isBoolean(o));\r\n
\t\t},\r\n
\t\tisEmpty : function(o) {\r\n
\t\t\tif(!this.isString(o) \046\046 this.isValue(o)) {\r\n
\t\t\t\treturn false;\r\n
\t\t\t}else if (!this.isValue(o)){\r\n
\t\t\t\treturn true;\r\n
\t\t\t}\r\n
\t\t\to = $.trim(o).replace(/\\\046nbsp\\;/ig,\'\').replace(/\\\046#160\\;/ig,\'\');\r\n
\t\t\treturn o==="";\t\r\n
\t\t}\r\n
\t});\r\n
\t$.fn.fmatter = function(formatType, cellval, opts, rwd, act) {\r\n
\t\t// build main options before element iteration\r\n
\t\tvar v=cellval;\r\n
\t\topts = $.extend({}, $.jgrid.formatter, opts);\r\n
\r\n
\t\ttry {\r\n
\t\t\tv = $.fn.fmatter[formatType].call(this, cellval, opts, rwd, act);\r\n
\t\t} catch(fe){}\r\n
\t\treturn v;\r\n
\t};\r\n
\t$.fmatter.util = {\r\n
\t\t// Taken from YAHOO utils\r\n
\t\tNumberFormat : function(nData,opts) {\r\n
\t\t\tif(!$.fmatter.isNumber(nData)) {\r\n
\t\t\t\tnData *= 1;\r\n
\t\t\t}\r\n
\t\t\tif($.fmatter.isNumber(nData)) {\r\n
\t\t\t\tvar bNegative = (nData \074 0);\r\n
\t\t\t\tvar sOutput = nData + "";\r\n
\t\t\t\tvar sDecimalSeparator = (opts.decimalSeparator) ? opts.decimalSeparator : ".";\r\n
\t\t\t\tvar nDotIndex;\r\n
\t\t\t\tif($.fmatter.isNumber(opts.decimalPlaces)) {\r\n
\t\t\t\t\t// Round to the correct decimal place\r\n
\t\t\t\t\tvar nDecimalPlaces = opts.decimalPlaces;\r\n
\t\t\t\t\tvar nDecimal = Math.pow(10, nDecimalPlaces);\r\n
\t\t\t\t\tsOutput = Math.round(nData*nDecimal)/nDecimal + "";\r\n
\t\t\t\t\tnDotIndex = sOutput.lastIndexOf(".");\r\n
\t\t\t\t\tif(nDecimalPlaces \076 0) {\r\n
\t\t\t\t\t// Add the decimal separator\r\n
\t\t\t\t\t\tif(nDotIndex \074 0) {\r\n
\t\t\t\t\t\t\tsOutput += sDecimalSeparator;\r\n
\t\t\t\t\t\t\tnDotIndex = sOutput.length-1;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t// Replace the "."\r\n
\t\t\t\t\t\telse if(sDecimalSeparator !== "."){\r\n
\t\t\t\t\t\t\tsOutput = sOutput.replace(".",sDecimalSeparator);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t// Add missing zeros\r\n
\t\t\t\t\t\twhile((sOutput.length - 1 - nDotIndex) \074 nDecimalPlaces) {\r\n
\t\t\t\t\t\t\tsOutput += "0";\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(opts.thousandsSeparator) {\r\n
\t\t\t\t\tvar sThousandsSeparator = opts.thousandsSeparator;\r\n
\t\t\t\t\tnDotIndex = sOutput.lastIndexOf(sDecimalSeparator);\r\n
\t\t\t\t\tnDotIndex = (nDotIndex \076 -1) ? nDotIndex : sOutput.length;\r\n
\t\t\t\t\tvar sNewOutput = sOutput.substring(nDotIndex);\r\n
\t\t\t\t\tvar nCount = -1;\r\n
\t\t\t\t\tfor (var i=nDotIndex; i\0760; i--) {\r\n
\t\t\t\t\t\tnCount++;\r\n
\t\t\t\t\t\tif ((nCount%3 === 0) \046\046 (i !== nDotIndex) \046\046 (!bNegative || (i \076 1))) {\r\n
\t\t\t\t\t\t\tsNewOutput = sThousandsSeparator + sNewOutput;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tsNewOutput = sOutput.charAt(i-1) + sNewOutput;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tsOutput = sNewOutput;\r\n
\t\t\t\t}\r\n
\t\t\t\t// Prepend prefix\r\n
\t\t\t\tsOutput = (opts.prefix) ? opts.prefix + sOutput : sOutput;\r\n
\t\t\t\t// Append suffix\r\n
\t\t\t\tsOutput = (opts.suffix) ? sOutput + opts.suffix : sOutput;\r\n
\t\t\t\treturn sOutput;\r\n
\t\t\t\t\r\n
\t\t\t} else {\r\n
\t\t\t\treturn nData;\r\n
\t\t\t}\r\n
\t\t},\r\n
\t\t// Tony Tomov\r\n
\t\t// PHP implementation. Sorry not all options are supported.\r\n
\t\t// Feel free to add them if you want\r\n
\t\tDateFormat : function (format, date, newformat, opts)  {\r\n
\t\t\tvar\ttoken = /\\\\.|[dDjlNSwzWFmMntLoYyaABgGhHisueIOPTZcrU]/g,\r\n
\t\t\ttimezone = /\\b(?:[PMCEA][SDP]T|(?:Pacific|Mountain|Central|Eastern|Atlantic) (?:Standard|Daylight|Prevailing) Time|(?:GMT|UTC)(?:[-+]\\d{4})?)\\b/g,\r\n
\t\t\ttimezoneClip = /[^-+\\dA-Z]/g,\r\n
\t\t\tmsDateRegExp = new RegExp("^\\/Date\\\\((([-+])?[0-9]+)(([-+])([0-9]{2})([0-9]{2}))?\\\\)\\/$"),\r\n
\t\t\tmsMatch = ((typeof date === \'string\') ? date.match(msDateRegExp): null),\r\n
\t\t\tpad = function (value, length) {\r\n
\t\t\t\tvalue = String(value);\r\n
\t\t\t\tlength = parseInt(length,10) || 2;\r\n
\t\t\t\twhile (value.length \074 length)  { value = \'0\' + value; }\r\n
\t\t\t\treturn value;\r\n
\t\t\t},\r\n
\t\t\tts = {m : 1, d : 1, y : 1970, h : 0, i : 0, s : 0, u:0},\r\n
\t\t\ttimestamp=0, dM, k,hl,\r\n
\t\t\tdateFormat=["i18n"];\r\n
\t\t\t// Internationalization strings\r\n
\t\t\tdateFormat.i18n = {\r\n
\t\t\t\tdayNames: opts.dayNames,\r\n
\t\t\t\tmonthNames: opts.monthNames\r\n
\t\t\t};\r\n
\t\t\tif( format in opts.masks ) { format = opts.masks[format]; }\r\n
\t\t\tif( !isNaN( date - 0 ) \046\046 String(format).toLowerCase() == "u") {\r\n
\t\t\t\t//Unix timestamp\r\n
\t\t\t\ttimestamp = new Date( parseFloat(date)*1000 );\r\n
\t\t\t} else if(date.constructor === Date) {\r\n
\t\t\t\ttimestamp = date;\r\n
\t\t\t\t// Microsoft date format support\r\n
\t\t\t} else if( msMatch !== null ) {\r\n
\t\t\t\ttimestamp = new Date(parseInt(msMatch[1], 10));\r\n
\t\t\t\tif (msMatch[3]) {\r\n
\t\t\t\t\tvar offset = Number(msMatch[5]) * 60 + Number(msMatch[6]);\r\n
\t\t\t\t\toffset *= ((msMatch[4] == \'-\') ? 1 : -1);\r\n
\t\t\t\t\toffset -= timestamp.getTimezoneOffset();\r\n
\t\t\t\t\ttimestamp.setTime(Number(Number(timestamp) + (offset * 60 * 1000)));\r\n
\t\t\t\t}\r\n
\t\t\t} else {\r\n
\t\t\t\tdate = String(date).split(/[\\\\\\/:_;.,\\t\\T\\s-]/);\r\n
\t\t\t\tformat = format.split(/[\\\\\\/:_;.,\\t\\T\\s-]/);\r\n
\t\t\t\t// parsing for month names\r\n
\t\t\t\tfor(k=0,hl=format.length;k\074hl;k++){\r\n
\t\t\t\t\tif(format[k] == \'M\') {\r\n
\t\t\t\t\t\tdM = $.inArray(date[k],dateFormat.i18n.monthNames);\r\n
\t\t\t\t\t\tif(dM !== -1 \046\046 dM \074 12){date[k] = dM+1;}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(format[k] == \'F\') {\r\n
\t\t\t\t\t\tdM = $.inArray(date[k],dateFormat.i18n.monthNames);\r\n
\t\t\t\t\t\tif(dM !== -1 \046\046 dM \076 11){date[k] = dM+1-12;}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(date[k]) {\r\n
\t\t\t\t\t\tts[format[k].toLowerCase()] = parseInt(date[k],10);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ts.f) {ts.m = ts.f;}\r\n
\t\t\t\tif( ts.m === 0 \046\046 ts.y === 0 \046\046 ts.d === 0) {\r\n
\t\t\t\t\treturn "\046#160;" ;\r\n
\t\t\t\t}\r\n
\t\t\t\tts.m = parseInt(ts.m,10)-1;\r\n
\t\t\t\tvar ty = ts.y;\r\n
\t\t\t\tif (ty \076= 70 \046\046 ty \074= 99) {ts.y = 1900+ts.y;}\r\n
\t\t\t\telse if (ty \076=0 \046\046 ty \074=69) {ts.y= 2000+ts.y;}\r\n
\t\t\t\ttimestamp = new Date(ts.y, ts.m, ts.d, ts.h, ts.i, ts.s, ts.u);\r\n
\t\t\t}\r\n
\t\t\t\r\n
\t\t\tif( newformat in opts.masks )  {\r\n
\t\t\t\tnewformat = opts.masks[newformat];\r\n
\t\t\t} else if ( !newformat ) {\r\n
\t\t\t\tnewformat = \'Y-m-d\';\r\n
\t\t\t}\r\n
\t\t\tvar \r\n
\t\t\t\tG = timestamp.getHours(),\r\n
\t\t\t\ti = timestamp.getMinutes(),\r\n
\t\t\t\tj = timestamp.getDate(),\r\n
\t\t\t\tn = timestamp.getMonth() + 1,\r\n
\t\t\t\to = timestamp.getTimezoneOffset(),\r\n
\t\t\t\ts = timestamp.getSeconds(),\r\n
\t\t\t\tu = timestamp.getMilliseconds(),\r\n
\t\t\t\tw = timestamp.getDay(),\r\n
\t\t\t\tY = timestamp.getFullYear(),\r\n
\t\t\t\tN = (w + 6) % 7 + 1,\r\n
\t\t\t\tz = (new Date(Y, n - 1, j) - new Date(Y, 0, 1)) / 86400000,\r\n
\t\t\t\tflags = {\r\n
\t\t\t\t\t// Day\r\n
\t\t\t\t\td: pad(j),\r\n
\t\t\t\t\tD: dateFormat.i18n.dayNames[w],\r\n
\t\t\t\t\tj: j,\r\n
\t\t\t\t\tl: dateFormat.i18n.dayNames[w + 7],\r\n
\t\t\t\t\tN: N,\r\n
\t\t\t\t\tS: opts.S(j),\r\n
\t\t\t\t\t//j \074 11 || j \076 13 ? [\'st\', \'nd\', \'rd\', \'th\'][Math.min((j - 1) % 10, 3)] : \'th\',\r\n
\t\t\t\t\tw: w,\r\n
\t\t\t\t\tz: z,\r\n
\t\t\t\t\t// Week\r\n
\t\t\t\t\tW: N \074 5 ? Math.floor((z + N - 1) / 7) + 1 : Math.floor((z + N - 1) / 7) || ((new Date(Y - 1, 0, 1).getDay() + 6) % 7 \074 4 ? 53 : 52),\r\n
\t\t\t\t\t// Month\r\n
\t\t\t\t\tF: dateFormat.i18n.monthNames[n - 1 + 12],\r\n
\t\t\t\t\tm: pad(n),\r\n
\t\t\t\t\tM: dateFormat.i18n.monthNames[n - 1],\r\n
\t\t\t\t\tn: n,\r\n
\t\t\t\t\tt: \'?\',\r\n
\t\t\t\t\t// Year\r\n
\t\t\t\t\tL: \'?\',\r\n
\t\t\t\t\to: \'?\',\r\n
\t\t\t\t\tY: Y,\r\n
\t\t\t\t\ty: String(Y).substring(2),\r\n
\t\t\t\t\t// Time\r\n
\t\t\t\t\ta: G \074 12 ? opts.AmPm[0] : opts.AmPm[1],\r\n
\t\t\t\t\tA: G \074 12 ? opts.AmPm[2] : opts.AmPm[3],\r\n
\t\t\t\t\tB: \'?\',\r\n
\t\t\t\t\tg: G % 12 || 12,\r\n
\t\t\t\t\tG: G,\r\n
\t\t\t\t\th: pad(G % 12 || 12),\r\n
\t\t\t\t\tH: pad(G),\r\n
\t\t\t\t\ti: pad(i),\r\n
\t\t\t\t\ts: pad(s),\r\n
\t\t\t\t\tu: u,\r\n
\t\t\t\t\t// Timezone\r\n
\t\t\t\t\te: \'?\',\r\n
\t\t\t\t\tI: \'?\',\r\n
\t\t\t\t\tO: (o \076 0 ? "-" : "+") + pad(Math.floor(Math.abs(o) / 60) * 100 + Math.abs(o) % 60, 4),\r\n
\t\t\t\t\tP: \'?\',\r\n
\t\t\t\t\tT: (String(timestamp).match(timezone) || [""]).pop().replace(timezoneClip, ""),\r\n
\t\t\t\t\tZ: \'?\',\r\n
\t\t\t\t\t// Full Date/Time\r\n
\t\t\t\t\tc: \'?\',\r\n
\t\t\t\t\tr: \'?\',\r\n
\t\t\t\t\tU: Math.floor(timestamp / 1000)\r\n
\t\t\t\t};\t\r\n
\t\t\treturn newformat.replace(token, function ($0) {\r\n
\t\t\t\treturn $0 in flags ? flags[$0] : $0.substring(1);\r\n
\t\t\t});\t\t\t\r\n
\t\t}\r\n
\t};\r\n
\t$.fn.fmatter.defaultFormat = function(cellval, opts) {\r\n
\t\treturn ($.fmatter.isValue(cellval) \046\046 cellval!=="" ) ?  cellval : opts.defaultValue ? opts.defaultValue : "\046#160;";\r\n
\t};\r\n
\t$.fn.fmatter.email = function(cellval, opts) {\r\n
\t\tif(!$.fmatter.isEmpty(cellval)) {\r\n
\t\t\treturn "\074a href=\\"mailto:" + cellval + "\\"\076" + cellval + "\074/a\076";\r\n
\t\t}else {\r\n
\t\t\treturn $.fn.fmatter.defaultFormat(cellval,opts );\r\n
\t\t}\r\n
\t};\r\n
\t$.fn.fmatter.checkbox =function(cval, opts) {\r\n
\t\tvar op = $.extend({},opts.checkbox), ds;\r\n
\t\tif(opts.colModel !== undefined \046\046 !$.fmatter.isUndefined(opts.colModel.formatoptions)) {\r\n
\t\t\top = $.extend({},op,opts.colModel.formatoptions);\r\n
\t\t}\r\n
\t\tif(op.disabled===true) {ds = "disabled=\\"disabled\\"";} else {ds="";}\r\n
\t\tif($.fmatter.isEmpty(cval) || $.fmatter.isUndefined(cval) ) {cval = $.fn.fmatter.defaultFormat(cval,op);}\r\n
\t\tcval=cval+"";cval=cval.toLowerCase();\r\n
\t\tvar bchk = cval.search(/(false|0|no|off)/i)\0740 ? " checked=\'checked\' " : "";\r\n
\t\treturn "\074input type=\\"checkbox\\" " + bchk  + " value=\\""+ cval+"\\" offval=\\"no\\" "+ds+ "/\076";\r\n
\t};\r\n
\t$.fn.fmatter.link = function(cellval, opts) {\r\n
\t\tvar op = {target:opts.target};\r\n
\t\tvar target = "";\r\n
\t\tif(opts.colModel !== undefined \046\046 !$.fmatter.isUndefined(opts.colModel.formatoptions)) {\r\n
\t\t\top = $.extend({},op,opts.colModel.formatoptions);\r\n
\t\t}\r\n
\t\tif(op.target) {target = \'target=\' + op.targe</string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAQ=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="4" aka="AAAAAAAAAAQ=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string>t;}\r\n
\t\tif(!$.fmatter.isEmpty(cellval)) {\r\n
\t\t\treturn "\074a "+target+" href=\\"" + cellval + "\\"\076" + cellval + "\074/a\076";\r\n
\t\t}else {\r\n
\t\t\treturn $.fn.fmatter.defaultFormat(cellval,opts);\r\n
\t\t}\r\n
\t};\r\n
\t$.fn.fmatter.showlink = function(cellval, opts) {\r\n
\t\tvar op = {baseLinkUrl: opts.baseLinkUrl,showAction:opts.showAction, addParam: opts.addParam || "", target: opts.target, idName: opts.idName},\r\n
\t\ttarget = "", idUrl;\r\n
\t\tif(opts.colModel !== undefined \046\046 !$.fmatter.isUndefined(opts.colModel.formatoptions)) {\r\n
\t\t\top = $.extend({},op,opts.colModel.formatoptions);\r\n
\t\t}\r\n
\t\tif(op.target) {target = \'target=\' + op.target;}\r\n
\t\tidUrl = op.baseLinkUrl+op.showAction + \'?\'+ op.idName+\'=\'+opts.rowId+op.addParam;\r\n
\t\tif($.fmatter.isString(cellval) || $.fmatter.isNumber(cellval)) {\t//add this one even if its blank string\r\n
\t\t\treturn "\074a "+target+" href=\\"" + idUrl + "\\"\076" + cellval + "\074/a\076";\r\n
\t\t}else {\r\n
\t\t\treturn $.fn.fmatter.defaultFormat(cellval,opts);\r\n
\t\t}\r\n
\t};\r\n
\t$.fn.fmatter.integer = function(cellval, opts) {\r\n
\t\tvar op = $.extend({},opts.integer);\r\n
\t\tif(opts.colModel !== undefined \046\046 !$.fmatter.isUndefined(opts.colModel.formatoptions)) {\r\n
\t\t\top = $.extend({},op,opts.colModel.formatoptions);\r\n
\t\t}\r\n
\t\tif($.fmatter.isEmpty(cellval)) {\r\n
\t\t\treturn op.defaultValue;\r\n
\t\t}\r\n
\t\treturn $.fmatter.util.NumberFormat(cellval,op);\r\n
\t};\r\n
\t$.fn.fmatter.number = function (cellval, opts) {\r\n
\t\tvar op = $.extend({},opts.number);\r\n
\t\tif(opts.colModel !== undefined \046\046 !$.fmatter.isUndefined(opts.colModel.formatoptions)) {\r\n
\t\t\top = $.extend({},op,opts.colModel.formatoptions);\r\n
\t\t}\r\n
\t\tif($.fmatter.isEmpty(cellval)) {\r\n
\t\t\treturn op.defaultValue;\r\n
\t\t}\r\n
\t\treturn $.fmatter.util.NumberFormat(cellval,op);\r\n
\t};\r\n
\t$.fn.fmatter.currency = function (cellval, opts) {\r\n
\t\tvar op = $.extend({},opts.currency);\r\n
\t\tif(opts.colModel !== undefined \046\046 !$.fmatter.isUndefined(opts.colModel.formatoptions)) {\r\n
\t\t\top = $.extend({},op,opts.colModel.formatoptions);\r\n
\t\t}\r\n
\t\tif($.fmatter.isEmpty(cellval)) {\r\n
\t\t\treturn op.defaultValue;\r\n
\t\t}\r\n
\t\treturn $.fmatter.util.NumberFormat(cellval,op);\r\n
\t};\r\n
\t$.fn.fmatter.date = function (cellval, opts, rwd, act) {\r\n
\t\tvar op = $.extend({},opts.date);\r\n
\t\tif(opts.colModel !== undefined \046\046 !$.fmatter.isUndefined(opts.colModel.formatoptions)) {\r\n
\t\t\top = $.extend({},op,opts.colModel.formatoptions);\r\n
\t\t}\r\n
\t\tif(!op.reformatAfterEdit \046\046 act==\'edit\'){\r\n
\t\t\treturn $.fn.fmatter.defaultFormat(cellval, opts);\r\n
\t\t} else if(!$.fmatter.isEmpty(cellval)) {\r\n
\t\t\treturn  $.fmatter.util.DateFormat(op.srcformat,cellval,op.newformat,op);\r\n
\t\t} else {\r\n
\t\t\treturn $.fn.fmatter.defaultFormat(cellval, opts);\r\n
\t\t}\r\n
\t};\r\n
\t$.fn.fmatter.select = function (cellval,opts) {\r\n
\t\t// jqGrid specific\r\n
\t\tcellval = cellval + "";\r\n
\t\tvar oSelect = false, ret=[], sep, delim;\r\n
\t\tif(!$.fmatter.isUndefined(opts.colModel.formatoptions)){\r\n
\t\t\toSelect= opts.colModel.formatoptions.value;\r\n
\t\t\tsep = opts.colModel.formatoptions.separator === undefined ? ":" : opts.colModel.formatoptions.separator;\r\n
\t\t\tdelim = opts.colModel.formatoptions.delimiter === undefined ? ";" : opts.colModel.formatoptions.delimiter;\r\n
\t\t} else if(!$.fmatter.isUndefined(opts.colModel.editoptions)){\r\n
\t\t\toSelect= opts.colModel.editoptions.value;\r\n
\t\t\tsep = opts.colModel.editoptions.separator === undefined ? ":" : opts.colModel.editoptions.separator;\r\n
\t\t\tdelim = opts.colModel.editoptions.delimiter === undefined ? ";" : opts.colModel.editoptions.delimiter;\r\n
\t\t}\r\n
\t\tif (oSelect) {\r\n
\t\t\tvar\tmsl =  opts.colModel.editoptions.multiple === true ? true : false,\r\n
\t\t\tscell = [], sv;\r\n
\t\t\tif(msl) {scell = cellval.split(",");scell = $.map(scell,function(n){return $.trim(n);});}\r\n
\t\t\tif ($.fmatter.isString(oSelect)) {\r\n
\t\t\t\t// mybe here we can use some caching with care ????\r\n
\t\t\t\tvar so = oSelect.split(delim), j=0;\r\n
\t\t\t\tfor(var i=0; i\074so.length;i++){\r\n
\t\t\t\t\tsv = so[i].split(sep);\r\n
\t\t\t\t\tif(sv.length \076 2 ) {\r\n
\t\t\t\t\t\tsv[1] = $.map(sv,function(n,i){if(i\0760) {return n;}}).join(sep);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(msl) {\r\n
\t\t\t\t\t\tif($.inArray(sv[0],scell)\076-1) {\r\n
\t\t\t\t\t\t\tret[j] = sv[1];\r\n
\t\t\t\t\t\t\tj++;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else if($.trim(sv[0])==$.trim(cellval)) {\r\n
\t\t\t\t\t\tret[0] = sv[1];\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t} else if($.fmatter.isObject(oSelect)) {\r\n
\t\t\t\t// this is quicker\r\n
\t\t\t\tif(msl) {\r\n
\t\t\t\t\tret = $.map(scell, function(n){\r\n
\t\t\t\t\t\treturn oSelect[n];\r\n
\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tret[0] = oSelect[cellval] || "";\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tcellval = ret.join(", ");\r\n
\t\treturn  cellval === "" ? $.fn.fmatter.defaultFormat(cellval,opts) : cellval;\r\n
\t};\r\n
\t$.fn.fmatter.rowactions = function(rid,gid,act,pos) {\r\n
\t\tvar op ={\r\n
\t\t\tkeys:false,\r\n
\t\t\tonEdit : null, \r\n
\t\t\tonSuccess: null, \r\n
\t\t\tafterSave:null,\r\n
\t\t\tonError: null,\r\n
\t\t\tafterRestore: null,\r\n
\t\t\textraparam: {},\r\n
\t\t\turl: null,\r\n
\t\t\trestoreAfterError: true,\r\n
\t\t\tmtype: "POST",\r\n
\t\t\tdelOptions: {},\r\n
\t\t\teditOptions : {}\r\n
\t\t};\r\n
\t\trid = $.jgrid.jqID( rid );\r\n
\t\tgid = $.jgrid.jqID( gid );\r\n
\t\tvar cm = $(\'#\'+gid)[0].p.colModel[pos];\r\n
\t\tif(!$.fmatter.isUndefined(cm.formatoptions)) {\r\n
\t\t\top = $.extend(op,cm.formatoptions);\r\n
\t\t}\r\n
\t\tif( !$.fmatter.isUndefined($(\'#\'+gid)[0].p.editOptions) ) {\r\n
\t\t\top.editOptions = $(\'#\'+gid)[0].p.editOptions;\r\n
\t\t}\r\n
\t\tif( !$.fmatter.isUndefined($(\'#\'+gid)[0].p.delOptions) ) {\r\n
\t\t\top.delOptions = $(\'#\'+gid)[0].p.delOptions;\r\n
\t\t}\r\n
\t\tvar $t = $("#"+gid)[0];\r\n
\t\tvar saverow = function( rowid, res)\t{\r\n
\t\t\tif($.isFunction(op.afterSave)) { op.afterSave.call($t, rowid, res); }\r\n
\t\t\t$("tr#"+rid+" div.ui-inline-edit, "+"tr#"+rid+" div.ui-inline-del","#"+gid + ".ui-jqgrid-btable:first").show();\r\n
\t\t\t$("tr#"+rid+" div.ui-inline-save, "+"tr#"+rid+" div.ui-inline-cancel","#"+gid+ ".ui-jqgrid-btable:first").hide();\r\n
\t\t},\r\n
\t\trestorerow = function( rowid)\t{\r\n
\t\t\tif($.isFunction(op.afterRestore) ) { op.afterRestore.call($t, rowid); }\r\n
\t\t\t$("tr#"+rid+" div.ui-inline-edit, "+"tr#"+rid+" div.ui-inline-del","#"+gid+ ".ui-jqgrid-btable:first").show();\r\n
\t\t\t$("tr#"+rid+" div.ui-inline-save, "+"tr#"+rid+" div.ui-inline-cancel","#"+gid+ ".ui-jqgrid-btable:first").hide();\r\n
\t\t};\r\n
\t\tif( $("#"+rid,"#"+gid).hasClass("jqgrid-new-row") ){\r\n
\t\t\tvar opers = $t.p.prmNames,\r\n
\t\t\toper = opers.oper;\r\n
\t\t\top.extraparam[oper] = opers.addoper;\r\n
\t\t}\r\n
\t\tvar actop = {\r\n
\t\t\tkeys : op.keys,\r\n
\t\t\toneditfunc: op.onEdit,\r\n
\t\t\tsuccessfunc: op.onSuccess,\r\n
\t\t\turl: op.url,\r\n
\t\t\textraparam: op.extraparam,\r\n
\t\t\taftersavefunc: saverow,\r\n
\t\t\terrorfunc: op.onError,\r\n
\t\t\tafterrestorefunc: restorerow,\r\n
\t\t\trestoreAfterError: op.restoreAfterError,\r\n
\t\t\tmtype: op.mtype\r\n
\t\t};\r\n
\t\tswitch(act)\r\n
\t\t{\r\n
\t\t\tcase \'edit\':\r\n
\t\t\t\t$(\'#\'+gid).jqGrid(\'editRow\', rid, actop);\r\n
\t\t\t\t$("tr#"+rid+" div.ui-inline-edit, "+"tr#"+rid+" div.ui-inline-del","#"+gid+ ".ui-jqgrid-btable:first").hide();\r\n
\t\t\t\t$("tr#"+rid+" div.ui-inline-save, "+"tr#"+rid+" div.ui-inline-cancel","#"+gid+ ".ui-jqgrid-btable:first").show();\r\n
\t\t\t\t$($t).triggerHandler("jqGridAfterGridComplete");\r\n
\t\t\t\tbreak;\r\n
\t\t\tcase \'save\':\r\n
\t\t\t\tif ( $(\'#\'+gid).jqGrid(\'saveRow\', rid, actop) ) {\r\n
\t\t\t\t$("tr#"+rid+" div.ui-inline-edit, "+"tr#"+rid+" div.ui-inline-del","#"+gid+ ".ui-jqgrid-btable:first").show();\r\n
\t\t\t\t$("tr#"+rid+" div.ui-inline-save, "+"tr#"+rid+" div.ui-inline-cancel","#"+gid+ ".ui-jqgrid-btable:first").hide();\r\n
\t\t\t\t$($t).triggerHandler("jqGridAfterGridComplete");\r\n
\t\t\t\t}\r\n
\t\t\t\tbreak;\r\n
\t\t\tcase \'cancel\' :\r\n
\t\t\t\t$(\'#\'+gid).jqGrid(\'restoreRow\',rid, restorerow);\r\n
\t\t\t\t$("tr#"+rid+" div.ui-inline-edit, "+"tr#"+rid+" div.ui-inline-del","#"+gid+ ".ui-jqgrid-btable:first").show();\r\n
\t\t\t\t$("tr#"+rid+" div.ui-inline-save, "+"tr#"+rid+" div.ui-inline-cancel","#"+gid+ ".ui-jqgrid-btable:first").hide();\r\n
\t\t\t\t$($t).triggerHandler("jqGridAfterGridComplete");\r\n
\t\t\t\tbreak;\r\n
\t\t\tcase \'del\':\r\n
\t\t\t\t$(\'#\'+gid).jqGrid(\'delGridRow\',rid, op.delOptions);\r\n
\t\t\t\tbreak;\r\n
\t\t\tcase \'formedit\':\r\n
\t\t\t\t$(\'#\'+gid).jqGrid(\'setSelection\',rid);\r\n
\t\t\t\t$(\'#\'+gid).jqGrid(\'editGridRow\',rid, op.editOptions);\r\n
\t\t\t\tbreak;\r\n
\t\t}\r\n
\t};\r\n
\t$.fn.fmatter.actions = function(cellval,opts) {\r\n
\t\tvar op ={keys:false, editbutton:true, delbutton:true, editformbutton: false};\r\n
\t\tif(!$.fmatter.isUndefined(opts.colModel.formatoptions)) {\r\n
\t\t\top = $.extend(op,opts.colModel.formatoptions);\r\n
\t\t}\r\n
\t\tvar rowid = opts.rowId, str="",ocl;\r\n
\t\tif(typeof(rowid) ==\'undefined\' || $.fmatter.isEmpty(rowid)) {return "";}\r\n
\t\tif(op.editformbutton){\r\n
\t\t\tocl = "onclick=jQuery.fn.fmatter.rowactions(\'"+rowid+"\',\'"+opts.gid+"\',\'formedit\',"+opts.pos+"); onmouseover=jQuery(this).addClass(\'ui-state-hover\'); onmouseout=jQuery(this).removeClass(\'ui-state-hover\'); ";\r\n
\t\t\tstr =str+ "\074div title=\'"+$.jgrid.nav.edittitle+"\' style=\'float:left;cursor:pointer;\' class=\'ui-pg-div ui-inline-edit\' "+ocl+"\076\074span class=\'ui-icon ui-icon-pencil\'\076\074/span\076\074/div\076";\r\n
\t\t} else if(op.editbutton){\r\n
\t\t\tocl = "onclick=jQuery.fn.fmatter.rowactions(\'"+rowid+"\',\'"+opts.gid+"\',\'edit\',"+opts.pos+"); onmouseover=jQuery(this).addClass(\'ui-state-hover\'); onmouseout=jQuery(this).removeClass(\'ui-state-hover\') ";\r\n
\t\t\tstr =str+ "\074div title=\'"+$.jgrid.nav.edittitle+"\' style=\'float:left;cursor:pointer;\' class=\'ui-pg-div ui-inline-edit\' "+ocl+"\076\074span class=\'ui-icon ui-icon-pencil\'\076\074/span\076\074/div\076";\r\n
\t\t}\r\n
\t\tif(op.delbutton) {\r\n
\t\t\tocl = "onclick=jQuery.fn.fmatter.rowactions(\'"+rowid+"\',\'"+opts.gid+"\',\'del\',"+opts.pos+"); onmouseover=jQuery(this).addClass(\'ui-state-hover\'); onmouseout=jQuery(this).removeClass(\'ui-state-hover\'); ";\r\n
\t\t\tstr = str+"\074div title=\'"+$.jgrid.nav.deltitle+"\' style=\'float:left;margin-left:5px;\' class=\'ui-pg-div ui-inline-del\' "+ocl+"\076\074span class=\'ui-icon ui-icon-trash\'\076\074/span\076\074/div\076";\r\n
\t\t}\r\n
\t\tocl = "onclick=jQuery.fn.fmatter.rowactions(\'"+rowid+"\',\'"+opts.gid+"\',\'save\',"+opts.pos+"); onmouseover=jQuery(this).addClass(\'ui-state-hover\'); onmouseout=jQuery(this).removeClass(\'ui-state-hover\'); ";\r\n
\t\tstr = str+"\074div title=\'"+$.jgrid.edit.bSubmit+"\' style=\'float:left;display:none\' class=\'ui-pg-div ui-inline-save\' "+ocl+"\076\074span class=\'ui-icon ui-icon-disk\'\076\074/span\076\074/div\076";\r\n
\t\tocl = "onclick=jQuery.fn.fmatter.rowactions(\'"+rowid+"\',\'"+opts.gid+"\',\'cancel\',"+opts.pos+"); onmouseover=jQuery(this).addClass(\'ui-state-hover\'); onmouseout=jQuery(this).removeClass(\'ui-state-hover\'); ";\r\n
\t\tstr = str+"\074div title=\'"+$.jgrid.edit.bCancel+"\' style=\'float:left;display:none;margin-left:5px;\' class=\'ui-pg-div ui-inline-cancel\' "+ocl+"\076\074span class=\'ui-icon ui-icon-cancel\'\076\074/span\076\074/div\076";\r\n
\t\treturn "\074div style=\'margin-left:8px;\'\076" + str + "\074/div\076";\r\n
\t};\r\n
\t$.unformat = function (cellval,options,pos,cnt) {\r\n
\t\t// specific for jqGrid only\r\n
\t\tvar ret, formatType = options.colModel.formatter,\r\n
\t\top =options.colModel.formatoptions || {}, sep,\r\n
\t\tre = /([\\.\\*\\_\\\'\\(\\)\\{\\}\\+\\?\\\\])/g,\r\n
\t\tunformatFunc = options.colModel.unformat||($.fn.fmatter[formatType] \046\046 $.fn.fmatter[formatType].unformat);\r\n
\t\tif(typeof unformatFunc !== \'undefined\' \046\046 $.isFunction(unformatFunc) ) {\r\n
\t\t\tret = unformatFunc.call(this, $(cellval).text(), options, cellval);\r\n
\t\t} else if(!$.fmatter.isUndefined(formatType) \046\046 $.fmatter.isString(formatType) ) {\r\n
\t\t\tvar opts = $.jgrid.formatter || {}, stripTag;\r\n
\t\t\tswitch(formatType) {\r\n
\t\t\t\tcase \'integer\' :\r\n
\t\t\t\t\top = $.extend({},opts.integer,op);\r\n
\t\t\t\t\tsep = op.thousandsSeparator.replace(re,"\\\\$1");\r\n
\t\t\t\t\tstripTag = new RegExp(sep, "g");\r\n
\t\t\t\t\tret = $(cellval).text().replace(stripTag,\'\');\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'number\' :\r\n
\t\t\t\t\top = $.extend({},opts.number,op);\r\n
\t\t\t\t\tsep = op.thousandsSeparator.replace(re,"\\\\$1");\r\n
\t\t\t\t\tstripTag = new RegExp(sep, "g");\r\n
\t\t\t\t\tret = $(cellval).text().replace(stripTag,"").replace(op.decimalSeparator,\'.\');\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'currency\':\r\n
\t\t\t\t\top = $.extend({},opts.currency,op);\r\n
\t\t\t\t\tsep = op.thousandsSeparator.replace(re,"\\\\$1");\r\n
\t\t\t\t\tstripTag = new RegExp(sep, "g");\r\n
\t\t\t\t\tret = $(cellval).text();\r\n
\t\t\t\t\tif (op.prefix \046\046 op.prefix.length) {\r\n
\t\t\t\t\t\tret = ret.substr(op.prefix.length);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (op.suffix \046\046 op.suffix.length) {\r\n
\t\t\t\t\t\tret = ret.substr(0, ret.length - op.suffix.length);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tret = ret.replace(stripTag,\'\').replace(op.decimalSeparator,\'.\');\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'checkbox\':\r\n
\t\t\t\t\tvar cbv = (options.colModel.editoptions) ? options.colModel.editoptions.value.split(":") : ["Yes","No"];\r\n
\t\t\t\t\tret = $(\'input\',cellval).is(":checked") ? cbv[0] : cbv[1];\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'select\' :\r\n
\t\t\t\t\tret = $.unformat.select(cellval,options,pos,cnt);\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'actions\':\r\n
\t\t\t\t\treturn "";\r\n
\t\t\t\tdefault:\r\n
\t\t\t\t\tret= $(cellval).text();\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn ret !== undefined ? ret : cnt===true ? $(cellval).text() : $.jgrid.htmlDecode($(cellval).html());\r\n
\t};\r\n
\t$.unformat.select = function (cellval,options,pos,cnt) {\r\n
\t\t// Spacial case when we have local data and perform a sort\r\n
\t\t// cnt is set to true only in sortDataArray\r\n
\t\tvar ret = [];\r\n
\t\tvar cell = $(cellval).text();\r\n
\t\tif(cnt===true) {return cell;}\r\n
\t\tvar op = $.extend({}, !$.fmatter.isUndefined(options.colModel.formatoptions) ? options.colModel.formatoptions: options.colModel.editoptions),\r\n
\t\tsep = op.separator === undefined ? ":" : op.separator,\r\n
\t\tdelim = op.delimiter === undefined ? ";" : op.delimiter;\r\n
\t\t\r\n
\t\tif(op.value){\r\n
\t\t\tvar oSelect = op.value,\r\n
\t\t\tmsl =  op.multiple === true ? true : false,\r\n
\t\t\tscell = [], sv;\r\n
\t\t\tif(msl) {scell = cell.split(",");scell = $.map(scell,function(n){return $.trim(n);});}\r\n
\t\t\tif ($.fmatter.isString(oSelect)) {\r\n
\t\t\t\tvar so = oSelect.split(delim), j=0;\r\n
\t\t\t\tfor(var i=0; i\074so.length;i++){\r\n
\t\t\t\t\tsv = so[i].split(sep);\r\n
\t\t\t\t\tif(sv.length \076 2 ) {\r\n
\t\t\t\t\t\tsv[1] = $.map(sv,function(n,i){if(i\0760) {return n;}}).join(sep);\r\n
\t\t\t\t\t}\t\t\t\t\t\r\n
\t\t\t\t\tif(msl) {\r\n
\t\t\t\t\t\tif($.inArray(sv[1],scell)\076-1) {\r\n
\t\t\t\t\t\t\tret[j] = sv[0];\r\n
\t\t\t\t\t\t\tj++;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else if($.trim(sv[1])==$.trim(cell)) {\r\n
\t\t\t\t\t\tret[0] = sv[0];\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t} else if($.fmatter.isObject(oSelect) || $.isArray(oSelect) ){\r\n
\t\t\t\tif(!msl) {scell[0] =  cell;}\r\n
\t\t\t\tret = $.map(scell, function(n){\r\n
\t\t\t\t\tvar rv;\r\n
\t\t\t\t\t$.each(oSelect, function(i,val){\r\n
\t\t\t\t\t\tif (val == n) {\r\n
\t\t\t\t\t\t\trv = i;\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tif( typeof(rv) != \'undefined\' ) {return rv;}\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\treturn ret.join(", ");\r\n
\t\t} else {\r\n
\t\t\treturn cell || "";\r\n
\t\t}\r\n
\t};\r\n
\t$.unformat.date = function (cellval, opts) {\r\n
\t\tvar op = $.jgrid.formatter.date || {};\r\n
\t\tif(!$.fmatter.isUndefined(opts.formatoptions)) {\r\n
\t\t\top = $.extend({},op,opts.formatoptions);\r\n
\t\t}\t\t\r\n
\t\tif(!$.fmatter.isEmpty(cellval)) {\r\n
\t\t\treturn $.fmatter.util.DateFormat(op.newformat,cellval,op.srcformat,op);\r\n
\t\t} else {\r\n
\t\t\treturn $.fn.fmatter.defaultFormat(cellval, opts);\r\n
\t\t}\r\n
\t};\r\n
})(jQuery);\r\n
;(function($){\r\n
/*\r\n
 * jqGrid common function\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/ \r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
*/\r\n
/*global jQuery, $ */\r\n
\r\n
$.extend($.jgrid,{\r\n
// Modal functions\r\n
\tshowModal : function(h) {\r\n
\t\th.w.show();\r\n
\t},\r\n
\tcloseModal : function(h) {\r\n
\t\th.w.hide().attr("aria-hidden","true");\r\n
\t\tif(h.o) {h.o.remove();}\r\n
\t},\r\n
\thideModal : function (selector,o) {\r\n
\t\to = $.extend({jqm : true, gb :\'\'}, o || {});\r\n
\t\tif(o.onClose) {\r\n
\t\t\tvar oncret =  o.onClose(selector);\r\n
\t\t\tif (typeof oncret == \'boolean\'  \046\046 !oncret ) { return; }\r\n
\t\t}\r\n
\t\tif ($.fn.jqm \046\046 o.jqm === true) {\r\n
\t\t\t$(selector).attr("aria-hidden","true").jqmHide();\r\n
\t\t} else {\r\n
\t\t\tif(o.gb !== \'\') {\r\n
\t\t\t\ttry {$(".jqgrid-overlay:first",o.gb).hide();} catch (e){}\r\n
\t\t\t}\r\n
\t\t\t$(selector).hide().attr("aria-hidden","true");\r\n
\t\t}\r\n
\t},\r\n
//Helper functions\r\n
\tfindPos : function(obj) {\r\n
\t\tvar curleft = 0, curtop = 0;\r\n
\t\tif (obj.offsetParent) {\r\n
\t\t\tdo {\r\n
\t\t\t\tcurleft += obj.offsetLeft;\r\n
\t\t\t\tcurtop += obj.offsetTop;\r\n
\t\t\t} while (obj = obj.offsetParent);\r\n
\t\t\t//do not change obj == obj.offsetParent\r\n
\t\t}\r\n
\t\treturn [curleft,curtop];\r\n
\t},\r\n
\tcreateModal : function(aIDs, content, p, insertSelector, posSelector, appendsel, css) {\r\n
\t\tp = $.extend(true, $.jgrid.jqModal || {}, p);\r\n
\t\tvar mw  = document.createElement(\'div\'), rtlsup, self = this;\r\n
\t\tcss = $.extend({}, css || {});\r\n
\t\trtlsup = $(p.gbox).attr("dir") == "rtl" ? true : false;\r\n
\t\tmw.className= "ui-widget ui-widget-content ui-corner-all ui-jqdialog";\r\n
\t\tmw.id = aIDs.themodal;\r\n
\t\tvar mh = document.createElement(\'div\');\r\n
\t\tmh.className = "ui-jqdialog-titlebar ui-widget-header ui-corner-all ui-helper-clearfix";\r\n
\t\tmh.id = aIDs.modalhead;\r\n
\t\t$(mh).append("\074span class=\'ui-jqdialog-title\'\076"+p.caption+"\074/span\076");\r\n
\t\tvar ahr= $("\074a href=\'javascript:void(0)\' class=\'ui-jqdialog-titlebar-close ui-corner-all\'\076\074/a\076")\r\n
\t\t.hover(function(){ahr.addClass(\'ui-state-hover\');},\r\n
\t\t\t   function(){ahr.removeClass(\'ui-state-hover\');})\r\n
\t\t.append("\074span class=\'ui-icon ui-icon-closethick\'\076\074/span\076");\r\n
\t\t$(mh).append(ahr);\r\n
\t\tif(rtlsup) {\r\n
\t\t\tmw.dir = "rtl";\r\n
\t\t\t$(".ui-jqdialog-title",mh).css("float","right");\r\n
\t\t\t$(".ui-jqdialog-titlebar-close",mh).css("left",0.3+"em");\r\n
\t\t} else {\r\n
\t\t\tmw.dir = "ltr";\r\n
\t\t\t$(".ui-jqdialog-title",mh).css("float","left");\r\n
\t\t\t$(".ui-jqdialog-titlebar-close",mh).css("right",0.3+"em");\r\n
\t\t}\r\n
\t\tvar mc = document.createElement(\'div\');\r\n
\t\t$(mc).addClass("ui-jqdialog-content ui-widget-content").attr("id",aIDs.modalcontent);\r\n
\t\t$(mc).append(content);\r\n
\t\tmw.appendChild(mc);\r\n
\t\t$(mw).prepend(mh);\r\n
\t\tif(appendsel===true) { $(\'body\').append(mw); } //append as first child in body -for alert dialog\r\n
\t\telse if (typeof appendsel == "string")\r\n
\t\t\t$(appendsel).append(mw);\r\n
\t\telse {$(mw).insertBefore(insertSelector);}\r\n
\t\t$(mw).css(css);\r\n
\t\tif(typeof p.jqModal === \'undefined\') {p.jqModal = true;} // internal use\r\n
\t\tvar coord = {};\r\n
\t\tif ( $.fn.jqm \046\046 p.jqModal === true) {\r\n
\t\t\tif(p.left ===0 \046\046 p.top===0 \046\046 p.overlay) {\r\n
\t\t\t\tvar pos = [];\r\n
\t\t\t\tpos = $.jgrid.findPos(posSelector);\r\n
\t\t\t\tp.left = pos[0] + 4;\r\n
\t\t\t\tp.top = pos[1] + 4;\r\n
\t\t\t}\r\n
\t\t\tcoord.top = p.top+"px";\r\n
\t\t\tcoord.left = p.left;\r\n
\t\t} else if(p.left !==0 || p.top!==0) {\r\n
\t\t\tcoord.left = p.left;\r\n
\t\t\tcoord.top = p.top+"px";\r\n
\t\t}\r\n
\t\t$("a.ui-jqdialog-titlebar-close",mh).click(function(){\r\n
\t\t\tvar oncm = $("#"+$.jgrid.jqID(aIDs.themodal)).data("onClose") || p.onClose;\r\n
\t\t\tvar gboxclose = $("#"+$.jgrid.jqID(aIDs.themodal)).data("gbox") || p.gbox;\r\n
\t\t\tself.hideModal("#"+$.jgrid.jqID(aIDs.themodal),{gb:gboxclose,jqm:p.jqModal,onClose:oncm});\r\n
\t\t\treturn false;\r\n
\t\t});\r\n
\t\tif (p.width === 0 || !p.width) {p.width = 300;}\r\n
\t\tif(p.height === 0 || !p.height) {p.height =200;}\r\n
\t\tif(!p.zIndex) {\r\n
\t\t\tvar parentZ = $(insertSelector).parents("*[role=dialog]").filter(\':first\').css("z-index");\r\n
\t\t\tif(parentZ) {\r\n
\t\t\t\tp.zIndex = parseInt(parentZ,10)+2;\r\n
\t\t\t} else {\r\n
\t\t\t\tp.zIndex = 950;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tvar rtlt = 0;\r\n
\t\tif( rtlsup \046\046 coord.left \046\046 !appendsel) {\r\n
\t\t\trtlt = $(p.gbox).width()- (!isNaN(p.width) ? parseInt(p.width,10) :0) - 8; // to do\r\n
\t\t// just in case\r\n
\t\t\tcoord.left = parseInt(coord.left,10) + parseInt(rtlt,10);\r\n
\t\t}\r\n
\t\tif(coord.left) { coord.left += "px"; }\r\n
\t\t$(mw).css($.extend({\r\n
\t\t\twidth: isNaN(p.width) ? "auto": p.width+"px",\r\n
\t\t\theight:isNaN(p.height) ? "auto" : p.height + "px",\r\n
\t\t\tzIndex:p.zIndex,\r\n
\t\t\toverflow: \'hidden\'\r\n
\t\t},coord))\r\n
\t\t.attr({tabIndex: "-1","role":"dialog","aria-labelledby":aIDs.modalhead,"aria-hidden":"true"});\r\n
\t\tif(typeof p.drag == \'undefined\') { p.drag=true;}\r\n
\t\tif(typeof p.resize == \'undefined\') {p.resize=true;}\r\n
\t\tif (p.drag) {\r\n
\t\t\t$(mh).css(\'cursor\',\'move\');\r\n
\t\t\tif($.fn.jqDrag) {\r\n
\t\t\t\t$(mw).jqDrag(mh);\r\n
\t\t\t} else {\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\t$(mw).draggable({handle: $("#"+$.jgrid.jqID(mh.id))});\r\n
\t\t\t\t} catch (e) {}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tif(p.resize) {\r\n
\t\t\tif($.fn.jqResize) {\r\n
\t\t\t\t$(mw).append("\074div class=\'jqResize ui-resizable-handle ui-resizable-se ui-icon ui-icon-gripsmall-diagonal-se ui-icon-grip-diagonal-se\'\076\074/div\076");\r\n
\t\t\t\t$("#"+$.jgrid.jqID(aIDs.themodal)).jqResize(".jqResize",aIDs.scrollelm ? "#"+$.jgrid.jqID(aIDs.scrollelm) : false);\r\n
\t\t\t} else {\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\t$(mw).resizable({handles: \'se, sw\',alsoResize: aIDs.scrollelm ? "#"+$.jgrid.jqID(aIDs.scrollelm) : false});\r\n
\t\t\t\t} catch (r) {}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tif(p.closeOnEscape === true){\r\n
\t\t\t$(mw).keydown( function( e ) {\r\n
\t\t\t\tif( e.which == 27 ) {\r\n
\t\t\t\t\tvar cone = $("#"+$.jgrid.jqID(aIDs.themodal)).data("onClose") || p.onClose;\r\n
\t\t\t\t\tself.hideModal(this,{gb:p.gbox,jqm:p.jqModal,onClose: cone});\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t}\r\n
\t},\r\n
\tviewModal : function (selector,o){\r\n
\t\to = $.extend({\r\n
\t\t\ttoTop: true,\r\n
\t\t\toverlay: 10,\r\n
\t\t\tmodal: false,\r\n
\t\t\toverlayClass : \'ui-widget-overlay\',\r\n
\t\t\tonShow: $.jgrid.showModal,\r\n
\t\t\tonHide: $.jgrid.closeModal,\r\n
\t\t\tgbox: \'\',\r\n
\t\t\tjqm : true,\r\n
\t\t\tjqM : true\r\n
\t\t}, o || {});\r\n
\t\tif ($.fn.jqm \046\046 o.jqm === true) {\r\n
\t\t\tif(o.jqM) { $(selector).attr("aria-hidden","false").jqm(o).jqmShow(); }\r\n
\t\t\telse {$(selector).attr("aria-hidden","false").jqmShow();}\r\n
\t\t} else {\r\n
\t\t\tif(o.gbox !== \'\') {\r\n
\t\t\t\t$(".jqgrid-overlay:first",o.gbox).show();\r\n
\t\t\t\t$(selector).data("gbox",o.gbox);\r\n
\t\t\t}\r\n
\t\t\t$(selector).show().attr("aria-hidden","false");\r\n
\t\t\ttry{$(\':input:visible\',selector)[0].focus();}catch(_){}\r\n
\t\t}\r\n
\t},\r\n
\r\n
\tinfo_dialog : function(caption, content,c_b, modalopt) {\r\n
\t\tvar mopt = {\r\n
\t\t\twidth:290,\r\n
\t\t\theight:\'auto\',\r\n
\t\t\tdataheight: \'auto\',\r\n
\t\t\tdrag: true,\r\n
\t\t\tresize: false,\r\n
\t\t\tcaption:"\074b\076"+caption+"\074/b\076",\r\n
\t\t\tleft:250,\r\n
\t\t\ttop:170,\r\n
\t\t\tzIndex : 1000,\r\n
\t\t\tjqModal : true,\r\n
\t\t\tmodal : false,\r\n
\t\t\tcloseOnEscape : true,\r\n
\t\t\talign: \'center\',\r\n
\t\t\tbuttonalign : \'center\',\r\n
\t\t\tbuttons : []\r\n
\t\t// {text:\'textbutt\', id:"buttid", onClick : function(){...}}\r\n
\t\t// if the id is not provided we set it like info_button_+ the index in the array - i.e info_button_0,info_button_1...\r\n
\t\t};\r\n
\t\t$.extend(mopt,modalopt || {});\r\n
\t\tvar jm = mopt.jqModal, self = this;\r\n
\t\tif($.fn.jqm \046\046 !jm) { jm = false; }\r\n
\t\t// in case there is no jqModal\r\n
\t\tvar buttstr ="";\r\n
\t\tif(mopt.buttons.length \076 0) {\r\n
\t\t\tfor(var i=0;i\074mopt.buttons.length;i++) {\r\n
\t\t\t\tif(typeof mopt.buttons[i].id == "undefined") { mopt.buttons[i].id = "info_button_"+i; }\r\n
\t\t\t\tbuttstr += "\074a href=\'javascript:void(0)\' id=\'"+mopt.buttons[i].id+"\' class=\'fm-button ui-state-default ui-corner-all\'\076"+mopt.buttons[i].text+"\074/a\076";\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tvar dh = isNaN(mopt.dataheight) ? mopt.dataheight : mopt.dataheight+"px",\r\n
\t\tcn = "text-align:"+mopt.align+";";\r\n
\t\tvar cnt = "\074div id=\'info_id\'\076";\r\n
\t\tcnt += "\074div id=\'infocnt\' style=\'margin:0px;padding-bottom:1em;width:100%;overflow:auto;position:relative;height:"+dh+";"+cn+"\'\076"+content+"\074/div\076";\r\n
\t\tcnt += c_b ? "\074div class=\'ui-widget-content ui-helper-clearfix\' style=\'text-align:"+mopt.buttonalign+";padding-bottom:0.8em;padding-top:0.5em;background-image: none;border-width: 1px 0 0 0;\'\076\074a href=\'javascript:void(0)\' id=\'closedialog\' class=\'fm-button ui-state-default ui-corner-all\'\076"+c_b+"\074/a\076"+buttstr+"\074/div\076" :\r\n
\t\t\tbuttstr !== ""  ? "\074div class=\'ui-widget-content ui-helper-clearfix\' style=\'text-align:"+mopt.buttonalign+";padding-bottom:0.8em;padding-top:0.5em;background-image: none;border-width: 1px 0 0 0;\'\076"+buttstr+"\074/div\076" : "";\r\n
\t\tcnt += "\074/div\076";\r\n
\r\n
\t\ttry {\r\n
\t\t\tif($("#info_dialog").attr("aria-hidden") == "false") {\r\n
\t\t\t\t$.jgrid.hideModal("#info_dialog",{jqm:jm});\r\n
\t\t\t}\r\n
\t\t\t$("#info_dialog").remove();\r\n
\t\t} catch (e){}\r\n
\t\t$.jgrid.createModal({\r\n
\t\t\tthemodal:\'info_dialog\',\r\n
\t\t\tmodalhead:\'info_head\',\r\n
\t\t\tmodalcontent:\'info_content\',\r\n
\t\t\tscrollelm: \'infocnt\'},\r\n
\t\t\tcnt,\r\n
\t\t\tmopt,\r\n
\t\t\t\'\',\'\',true\r\n
\t\t);\r\n
\t\t// attach onclick after inserting into the dom\r\n
\t\tif(buttstr) {\r\n
\t\t\t$.each(mopt.buttons,function(i){\r\n
\t\t\t\t$("#"+$.jgrid.jqID(this.id),"#info_id").bind(\'click\',function(){mopt.buttons[i].onClick.call($("#info_dialog")); return false;});\r\n
\t\t\t});\r\n
\t\t}\r\n
\t\t$("#closedialog", "#info_id").click(function(){\r\n
\t\t\tself.hideModal("#info_dialog",{jqm:jm});\r\n
\t\t\treturn false;\r\n
\t\t});\r\n
\t\t$(".fm-button","#info_dialog").hover(\r\n
\t\t\tfunction(){$(this).addClass(\'ui-state-hover\');},\r\n
\t\t\tfunction(){$(this).removeClass(\'ui-state-hover\');}\r\n
\t\t);\r\n
\t\tif($.isFunction(mopt.beforeOpen) ) { mopt.beforeOpen(); }\r\n
\t\t$.jgrid.viewModal("#info_dialog",{\r\n
\t\t\tonHide: function(h) {\r\n
\t\t\t\th.w.hide().remove();\r\n
\t\t\t\tif(h.o) { h.o.remove(); }\r\n
\t\t\t},\r\n
\t\t\tmodal :mopt.modal,\r\n
\t\t\tjqm:jm\r\n
\t\t});\r\n
\t\tif($.isFunction(mopt.afterOpen) ) { mopt.afterOpen(); }\r\n
\t\ttry{ $("#info_dialog").focus();} catch (m){}\r\n
\t},\r\n
// Form Functions\r\n
\tcreateEl : function(eltype,options,vl,autowidth, ajaxso) {\r\n
\t\tvar elem = "", $t = this;\r\n
\t\tfunction bindEv (el, opt) {\r\n
\t\t\tif($.isFunction(opt.dataInit)) {\r\n
\t\t\t\topt.dataInit.call($t,el);\r\n
\t\t\t}\r\n
\t\t\tif(opt.dataEvents) {\r\n
\t\t\t\t$.each(opt.dataEvents, function() {\r\n
\t\t\t\t\tif (this.data !== undefined) {\r\n
\t\t\t\t\t\t$(el).bind(this.type, this.data, this.fn);\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$(el).bind(this.type, this.fn);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\treturn opt;\r\n
\t\t}\r\n
\t\tfunction setAttributes(elm, atr, exl ) {\r\n
\t\t\tvar exclude = [\'dataInit\',\'dataEvents\',\'dataUrl\', \'buildSelect\',\'sopt\', \'searchhidden\', \'defaultValue\', \'attr\'];\r\n
\t\t\tif(typeof(exl) != "undefined" \046\046 $.isArray(exl)) {\r\n
\t\t\t\t$.merge(exclude, exl);\r\n
\t\t\t}\r\n
\t\t\t$.each(atr, function(key, value){\r\n
\t\t\t\tif($.inArray(key, exclude) === -1) {\r\n
\t\t\t\t\t$(elm).attr(key,value);\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\tif(!atr.hasOwnProperty(\'id\')) {\r\n
\t\t\t\t$(elm).attr(\'id\', $.jgrid.randId());\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tswitch (eltype)\r\n
\t\t{\r\n
\t\t\tcase "textarea" :\r\n
\t\t\t\telem = document.createElement("textarea");\r\n
\t\t\t\tif(autowidth) {\r\n
\t\t\t\t\tif(!options.cols) { $(elem).css({width:"98%"});}\r\n
\t\t\t\t} else if (!options.cols) { options.cols = 20; }\r\n
\t\t\t\tif(!options.rows) { options.rows = 2; }\r\n
\t\t\t\tif(vl==\'\046nbsp;\' || vl==\'\046#160;\' || (vl.length==1 \046\046 vl.charCodeAt(0)==160)) {vl="";}\r\n
\t\t\t\telem.value = vl;\r\n
\t\t\t\tsetAttributes(elem, options);\r\n
\t\t\t\toptions = bindEv(elem,options);\r\n
\t\t\t\t$(elem).attr({"role":"textbox","multiline":"true"});\r\n
\t\t\tbreak;\r\n
\t\t\tcase "checkbox" : //what code for simple checkbox\r\n
\t\t\t\telem = document.createElement("input");\r\n
\t\t\t\telem.type = "checkbox";\r\n
\t\t\t\tif( !options.value ) {\r\n
\t\t\t\t\tvar vl1 = vl.toLowerCase();\r\n
\t\t\t\t\tif(vl1.search(/(false|0|no|off|undefined)/i)\0740 \046\046 vl1!=="") {\r\n
\t\t\t\t\t\telem.checked=true;\r\n
\t\t\t\t\t\telem.defaultChecked=true;\r\n
\t\t\t\t\t\telem.value = vl;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\telem.value = "on";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$(elem).attr("offval","off");\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tvar cbval = options.value.split(":");\r\n
\t\t\t\t\tif(vl === cbval[0]) {\r\n
\t\t\t\t\t\telem.checked=true;\r\n
\t\t\t\t\t\telem.defaultChecked=true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\telem.value = cbval[0];\r\n
\t\t\t\t\t$(elem).attr("offval",cbval[1]);\r\n
\t\t\t\t}\r\n
\t\t\t\tsetAttributes(elem, options, [\'value\']);\r\n
\t\t\t\toptions = bindEv(elem,options);\r\n
\t\t\t\t$(elem).attr("role","checkbox");\r\n
\t\t\tbreak;\r\n
\t\t\tcase "select" :\r\n
\t\t\t\telem = document.createElement("select");\r\n
\t\t\t\telem.setAttribute("role","select");\r\n
\t\t\t\tvar msl, ovm = [];\r\n
\t\t\t\tif(options.multiple===true) {\r\n
\t\t\t\t\tmsl = true;\r\n
\t\t\t\t\telem.multiple="multiple";\r\n
\t\t\t\t\t$(elem).attr("aria-multiselectable","true");\r\n
\t\t\t\t} else { msl = false; }\r\n
\t\t\t\tif(typeof(options.dataUrl) != "undefined") {\r\n
\t\t\t\t\t$.ajax($.extend({\r\n
\t\t\t\t\t\turl: options.dataUrl,\r\n
\t\t\t\t\t\ttype : "GET",\r\n
\t\t\t\t\t\tdataType: "html",\r\n
\t\t\t\t\t\tcontext: {elem:elem, options:options, vl:vl},\r\n
\t\t\t\t\t\tsuccess: function(data){\r\n
\t\t\t\t\t\t\tvar a,\tovm = [], elem = this.elem, vl = this.vl,\r\n
\t\t\t\t\t\t\toptions = $.extend({},this.options),\r\n
\t\t\t\t\t\t\tmsl = options.multiple===true;\r\n
\t\t\t\t\t\t\tif($.isFunction(options.buildSelect)) {\r\n
\t\t\t\t\t\t\t\tvar b = options.buildSelect.call($t,data);\r\n
\t\t\t\t\t\t\t\ta = $(b).html();\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\ta = $(data).html();\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(a) {\r\n
\t\t\t\t\t\t\t\t$(elem).append(a);\r\n
\t\t\t\t\t\t\t\tsetAttributes(elem, options);\r\n
\t\t\t\t\t\t\t\toptions = bindEv(elem,options);\r\n
\t\t\t\t\t\t\t\tif(typeof options.size === \'undefined\') { options.size =  msl ? 3 : 1;}\r\n
\t\t\t\t\t\t\t\tif(msl) {\r\n
\t\t\t\t\t\t\t\t\tovm = vl.split(",");\r\n
\t\t\t\t\t\t\t\t\tovm = $.map(ovm,function(n){return $.trim(n);});\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\tovm[0] = $.trim(vl);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t//$(elem).attr(options);\r\n
\t\t\t\t\t\t\t\tsetTimeout(function(){\r\n
\t\t\t\t\t\t\t\t\t$("option",elem).each(function(i){\r\n
\t\t\t\t\t\t\t\t\t\t//if(i===0) { this.selected = ""; }\r\n
\t\t\t\t\t\t\t\t\t\t// fix IE8/IE7 problem with selecting of the first item on multiple=true\r\n
\t\t\t\t\t\t\t\t\t\tif (i === 0 \046\046 elem.multiple) { this.selected = false; }\r\n
\t\t\t\t\t\t\t\t\t\t$(this).attr("role","option");\r\n
\t\t\t\t\t\t\t\t\t\tif($.inArray($.trim($(this).text()),ovm) \076 -1 || $.inArray($.trim($(this).val()),ovm) \076 -1 ) {\r\n
\t\t\t\t\t\t\t\t\t\t\tthis.selected= "selected";\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\t},0);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t},ajaxso || {}));\r\n
\t\t\t\t} else if(options.value) {\r\n
\t\t\t\t\tvar i;\r\n
\t\t\t\t\tif(typeof options.size === \'undefined\') {\r\n
\t\t\t\t\t\toptions.size = msl ? 3 : 1;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(msl) {\r\n
\t\t\t\t\t\tovm = vl.split(",");\r\n
\t\t\t\t\t\tovm = $.map(ovm,function(n){return $.trim(n);});\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(typeof options.value === \'function\') { options.value = options.value(); }\r\n
\t\t\t\t\tvar so,sv, ov, \r\n
\t\t\t\t\tsep = options.separator === undefined ? ":" : options.separator,\r\n
\t\t\t\t\tdelim = options.delimiter === undefined ? ";" : options.delimiter;\r\n
\t\t\t\t\tif(typeof options.value === \'string\') {\r\n
\t\t\t\t\t\tso = options.value.split(delim);\r\n
\t\t\t\t\t\tfor(i=0; i\074so.length;i++){\r\n
\t\t\t\t\t\t\tsv = so[i].split(sep);\r\n
\t\t\t\t\t\t\tif(sv.length \076 2 ) {\r\n
\t\t\t\t\t\t\t\tsv[1] = $.map(sv,function(n,ii){if(ii\0760) { return n;} }).join(sep);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tov = document.createElement("option");\r\n
\t\t\t\t\t\t\tov.setAttribute("role","option");\r\n
\t\t\t\t\t\t\tov.value = sv[0]; ov.innerHTML = sv[1];\r\n
\t\t\t\t\t\t\telem.appendChild(ov);\r\n
\t\t\t\t\t\t\tif (!msl \046\046  ($.trim(sv[0]) == $.trim(vl) || $.trim(sv[1]) == $.trim(vl))) { ov.selected ="selected"; }\r\n
\t\t\t\t\t\t\tif (msl \046\046 ($.inArray($.trim(sv[1]), ovm)\076-1 || $.inArray($.trim(sv[0]), ovm)\076-1)) {ov.selected ="selected";}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else if (typeof options.value === \'object\') {\r\n
\t\t\t\t\t\tvar oSv = options.value;\r\n
\t\t\t\t\t\tfor ( var key in oSv) {\r\n
\t\t\t\t\t\t\tif (oSv.hasOwnProperty(key ) ){\r\n
\t\t\t\t\t\t\t\tov = document.createElement("option");\r\n
\t\t\t\t\t\t\t\tov.setAttribute("role","option");\r\n
\t\t\t\t\t\t\t\tov.value = key; ov.innerHTML = oSv[key];\r\n
\t\t\t\t\t\t\t\telem.appendChild(ov);\r\n
\t\t\t\t\t\t\t\tif (!msl \046\046  ( $.trim(key) == $.trim(vl) || $.trim(oSv[key]) == $.trim(vl)) ) { ov.selected ="selected"; }\r\n
\t\t\t\t\t\t\t\tif (msl \046\046 ($.inArray($.trim(oSv[key]),ovm)\076-1 || $.inArray($.trim(key),ovm)\076-1)) { ov.selected ="selected"; }\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tsetAttributes(elem, options, [\'value\']);\r\n
\t\t\t\t\toptions = bindEv(elem,options);\r\n
\t\t\t\t}\r\n
\t\t\tbreak;\r\n
\t\t\tcase "text" :\r\n
\t\t\tcase "password" :\r\n
\t\t\tcase "button" :\r\n
\t\t\t\tvar role;\r\n
\t\t\t\tif(eltype=="button") { role = "button"; }\r\n
\t\t\t\telse { role = "textbox"; }\r\n
\t\t\t\telem = document.createElement("input");\r\n
\t\t\t\telem.type = eltype;\r\n
\t\t\t\telem.value = vl;\r\n
\t\t\t\tsetAttributes(elem, options);\r\n
\t\t\t\toptions = bindEv(elem,options);\r\n
\t\t\t\tif(eltype != "button"){\r\n
\t\t\t\t\tif(autowidth) {\r\n
\t\t\t\t\t\tif(!options.size) { $(elem).css({width:"98%"}); }\r\n
\t\t\t\t\t} else if (!options.size) { options.size = 20; }\r\n
\t\t\t\t}\r\n
\t\t\t\t$(elem).attr("role",role);\r\n
\t\t\tbreak;\r\n
\t\t\tcase "image" :\r\n
\t\t\tcase "file" :\r\n
\t\t\t\telem = document.createElement("input");\r\n
\t\t\t\telem.type = eltype;\r\n
\t\t\t\tsetAttributes(elem, options);\r\n
\t\t\t\toptions = bindEv(elem,options);\r\n
\t\t\t\tbreak;\r\n
\t\t\tcase "custom" :\r\n
\t\t\t\telem = document.createElement("span");\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\tif($.isFunction(options.custom_element)) {\r\n
\t\t\t\t\t\tvar celm = options.custom_element.call($t,vl,options);\r\n
\t\t\t\t\t\tif(celm) {\r\n
\t\t\t\t\t\t\tcelm = $(celm).addClass("customelement").attr({id:options.id,name:options.name});\r\n
\t\t\t\t\t\t\t$(elem).empty().append(celm);\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tthrow "e2";\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tthrow "e1";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} catch (e) {\r\n
\t\t\t\t\tif (e=="e1") { $.jgrid.info_dialog($.jgrid.errors.errcap,"function \'custom_element\' "+$.jgrid.edit.msg.nodefined, $.jgrid.edit.bClose);}\r\n
\t\t\t\t\tif (e=="e2") { $.jgrid.info_dialog($.jgrid.errors.errcap,"function \'custom_element\' "+$.jgrid.edit.msg.novalue,$.jgrid.edit.bClose);}\r\n
\t\t\t\t\telse { $.jgrid.info_dialog($.jgrid.errors.errcap,typeof(e)==="string"?e:e.message,$.jgrid.edit.bClose); }\r\n
\t\t\t\t}\r\n
\t\t\tbreak;\r\n
\t\t}\r\n
\t\treturn elem;\r\n
\t},\r\n
// Date Validation Javascript\r\n
\tcheckDate : function (format, date) {\r\n
\t\tvar daysInFebruary = function(year){\r\n
\t\t// February has 29 days in any year evenly divisible by four,\r\n
\t\t// EXCEPT for centurial years which are not also divisible by 400.\r\n
\t\t\treturn (((year % 4 === 0) \046\046 ( year % 100 !== 0 || (year % 400 === 0))) ? 29 : 28 );\r\n
\t\t},\r\n
\t\tDaysArray = function(n) {\r\n
\t\t\tfor (var i = 1; i \074= n; i++) {\r\n
\t\t\t\tthis[i] = 31;\r\n
\t\t\t\tif (i==4 || i==6 || i==9 || i==11) {this[i] = 30;}\r\n
\t\t\t\tif (i==2) {this[i] = 29;}\r\n
\t\t\t}\r\n
\t\t\treturn this;\r\n
\t\t};\r\n
\r\n
\t\tvar tsp = {}, sep;\r\n
\t\tformat = format.toLowerCase();\r\n
\t\t//we search for /,-,. for the date separator\r\n
\t\tif(format.indexOf("/") != -1) {\r\n
\t\t\tsep = "/";\r\n
\t\t} else if(format.indexOf("-") != -1) {\r\n
\t\t\tsep = "-";\r\n
\t\t} else if(format.indexOf(".") != -1) {\r\n
\t\t\tsep = ".";\r\n
\t\t} else {\r\n
\t\t\tsep = "/";\r\n
\t\t}\r\n
\t\tformat = format.split(sep);\r\n
\t\tdate = date.split(sep);\r\n
\t\tif (date.length != 3) { return false; }\r\n
\t\tvar j=-1,yln, dln=-1, mln=-1;\r\n
\t\tfor(var i=0;i\074format.length;i++){\r\n
\t\t\tvar dv =  isNaN(date[i]) ? 0 : parseInt(date[i],10);\r\n
\t\t\ttsp[format[i]] = dv;\r\n
\t\t\tyln = format[i];\r\n
\t\t\tif(yln.indexOf("y") != -1) { j=i; }\r\n
\t\t\tif(yln.indexOf("m") != -1) { mln=i; }\r\n
\t\t\tif(yln.indexOf("d") != -1) { dln=i; }\r\n
\t\t}\r\n
\t\tif (format[j] == "y" || format[j] == "yyyy") {\r\n
\t\t\tyln=4;\r\n
\t\t} else if(format[j] =="yy"){\r\n
\t\t\tyln = 2;\r\n
\t\t} else {\r\n
\t\t\tyln = -1;\r\n
\t\t}\r\n
\t\tvar daysInMonth = DaysArray(12),\r\n
\t\tstrDate;\r\n
\t\tif (j === -1) {\r\n
\t\t\treturn false;\r\n
\t\t} else {\r\n
\t\t\tstrDate = tsp[format[j]].toString();\r\n
\t\t\tif(yln == 2 \046\046 strDate.length == 1) {yln = 1;}\r\n
\t\t\tif (strDate.length != yln || (tsp[format[j]]===0 \046\046 date[j]!="00")){\r\n
\t\t\t\treturn false;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tif(mln === -1) {\r\n
\t\t\treturn false;\r\n
\t\t} else {\r\n
\t\t\tstrDate = tsp[format[mln]].toString();\r\n
\t\t\tif (strDate.length\0741 || tsp[format[mln]]\0741 || tsp[format[mln]]\07612){\r\n
\t\t\t\treturn false;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tif(dln === -1) {\r\n
\t\t\treturn false;\r\n
\t\t} else {\r\n
\t\t\tstrDate = tsp[format[dln]].toString();\r\n
\t\t\tif (strDate.length\0741 || tsp[format[dln]]\0741 || tsp[format[dln]]\07631 || (tsp[format[mln]]==2 \046\046 tsp[format[dln]]\076daysInFebruary(tsp[format[j]])) || tsp[format[dln]] \076 daysInMonth[tsp[format[mln]]]){\r\n
\t\t\t\treturn false;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn true;\r\n
\t},\r\n
\tisEmpty : function(val)\r\n
\t{\r\n
\t\tif (val.match(/^\\s+$/) || val === "")\t{\r\n
\t\t\treturn true;\r\n
\t\t} else {\r\n
\t\t\treturn false;\r\n
\t\t}\r\n
\t},\r\n
\tcheckTime : function(time){\r\n
\t// checks only hh:ss (and optional am/pm)\r\n
\t\tvar re = /^(\\d{1,2}):(\\d{2})([ap]m)?$/,regs;\r\n
\t\tif(!$.jgrid.isEmpty(time))\r\n
\t\t{\r\n
\t\t\tregs = time.match(re);\r\n
\t\t\tif(regs) {\r\n
\t\t\t\tif(regs[3]) {\r\n
\t\t\t\t\tif(regs[1] \074 1 || regs[1] \076 12) { return false; }\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tif(regs[1] \076 23) { return false; }\r\n
\t\t\t\t}\r\n
\t\t\t\tif(regs[2] \076 59) {\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t}\r\n
\t\t\t} else {\r\n
\t\t\t\treturn false;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn true;\r\n
\t},\r\n
\tcheckValues : function(val, valref,g, customobject, nam) {\r\n
\t\tvar edtrul,i, nm, dft, len;\r\n
\t\tif(typeof(customobject) === "undefined") {\r\n
\t\t\tif(typeof(valref)==\'string\'){\r\n
\t\t\t\tfor( i =0, len=g.p.colModel.length;i\074len; i++){\r\n
\t\t\t\t\tif(g.p.colModel[i].name==valref) {\r\n
\t\t\t\t\t\tedtrul = g.p.colModel[i].editrules;\r\n
\t\t\t\t\t\tvalref = i;\r\n
\t\t\t\t\t\ttry { nm = g.p.colModel[i].formoptions.label; } catch (e) {}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t} else if(valref \076=0) {\r\n
\t\t\t\tedtrul = g.p.colModel[valref].editrules;\r\n
\t\t\t}\r\n
\t\t} else {\r\n
\t\t\tedtrul = customobject;\r\n
\t\t\tnm = nam===undefined ? "_" : nam;\r\n
\t\t}\r\n
\t\tif(edtrul) {\r\n
\t\t\tif(!nm) { nm = g.p.colNames[valref]; }\r\n
\t\t\tif(edtrul.required === true) {\r\n
\t\t\t\tif( $.jgrid.isEmpty(val) )  { return [false,nm+": "+$.jgrid.edit.msg.required,""]; }\r\n
\t\t\t}\r\n
\t\t\t// force required\r\n
\t\t\tvar rqfield = edtrul.required === false ? false : true;\r\n
\t\t\tif(edtrul.number === true) {\r\n
\t\t\t\tif( !(rqfield === false \046\046 $.jgrid.isEmpty(val)) ) {\r\n
\t\t\t\t\tif(isNaN(val)) { return [false,nm+": "+$.jgrid.edit.msg.number,""]; }\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(typeof edtrul.minValue != \'undefined\' \046\046 !isNaN(edtrul.minValue)) {\r\n
\t\t\t\tif (parseFloat(val) \074 parseFloat(edtrul.minValue) ) { return [false,nm+": "+$.jgrid.edit.msg.minValue+" "+edtrul.minValue,""];}\r\n
\t\t\t}\r\n
\t\t\tif(typeof edtrul.maxValue != \'undefined\' \046\046 !isNaN(edtrul.maxValue)) {\r\n
\t\t\t\tif (parseFloat(val) \076 parseFloat(edtrul.maxValue) ) { return [false,nm+": "+$.jgrid.edit.msg.maxValue+" "+edtrul.maxValue,""];}\r\n
\t\t\t}\r\n
\t\t\tvar filter;\r\n
\t\t\tif(edtrul.email === true) {\r\n
\t\t\t\tif( !(rqfield === false \046\046 $.jgrid.isEmpty(val)) ) {\r\n
\t\t\t\t// taken from $ Validate plugin\r\n
\t\t\t\t\tfilter = /^((([a-z]|\\d|[!#\\$%\046\'\\*\\+\\-\\/=\\?\\^_`{\\|}~]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])+(\\.([a-z]|\\d|[!#\\$%\046\'\\*\\+\\-\\/=\\?\\^_`{\\|}~]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])+)*)|((\\x22)((((\\x20|\\x09)*(\\x0d\\x0a))?(\\x20|\\x09)+)?(([\\x01-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f]|\\x21|[\\x23-\\x5b]|[\\x5d-\\x7e]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])|(\\\\([\\x01-\\x09\\x0b\\x0c\\x0d-\\x7f]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF]))))*(((\\x20|\\x09)*(\\x0d\\x0a))?(\\x20|\\x09)+)?(\\x22)))@((([a-z]|\\d|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])|(([a-z]|\\d|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])([a-z]|\\d|-|\\.|_|~|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])*([a-z]|\\d|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])))\\.)+(([a-z]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])|(([a-z]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])([a-z]|\\d|-|\\.|_|~|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])*([a-z]|[\\u00A0-\\uD7FF\\uF900-\\uFDCF\\uFDF0-\\uFFEF])))\\.?$/i;\r\n
\t\t\t\t\tif(!filter.test(val)) {return [false,nm+": "+$.jgrid.edit.msg.email,""];}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(edtrul.integer === true) {\r\n
\t\t\t\tif( !(rqfield === false \046\046 $.jgrid.isEmpty(val)) ) {\r\n
\t\t\t\t\tif(isNaN(val)) { return [false,nm+": "+$.jgrid.edit.msg.integer,""]; }\r\n
\t\t\t\t\tif ((val % 1 !== 0) || (val.indexOf(\'.\') != -1)) { return [false,nm+": "+$.jgrid.edit.msg.integer,""];}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(edtrul.date === true) {\r\n
\t\t\t\tif( !(rqfield === false \046\046 $.jgrid.isEmpty(val)) ) {\r\n
\t\t\t\t\tif(g.p.colModel[valref].formatoptions \046\046 g.p.colModel[valref].formatoptions.newformat) {\r\n
\t\t\t\t\t\tdft = g.p.colModel[valref].formatoptions.newformat;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tdft = g.p.colModel[valref].datefmt || "Y-m-d";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(!$.jgrid.checkDate (dft, val)) { return [false,nm+": "+$.jgrid.edit.msg.date+" - "+dft,""]; }\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(edtrul.time === true) {\r\n
\t\t\t\tif( !(rqfield === false \046\046 $.jgrid.isEmpty(val)) ) {\r\n
\t\t\t\t\tif(!$.jgrid.checkTime (val)) { return [false,nm+": "+$.jgrid.edit.msg.date+" - hh:mm (am/pm)",""]; }\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(edtrul.url === true) {\r\n
\t\t\t\tif( !(rqfield === false \046\046 $.jgrid.isEmpty(val)) ) {\r\n
\t\t\t\t\tfilter = /^(((https?)|(ftp)):\\/\\/([\\-\\w]+\\.)+\\w{2,3}(\\/[%\\-\\w]+(\\.\\w{2,})?)*(([\\w\\-\\.\\?\\\\\\/+@\046#;`~=%!]*)(\\.\\w{2,})?)*\\/?)/i;\r\n
\t\t\t\t\tif(!filter.test(val)) {return [false,nm+": "+$.jgrid.edit.msg.url,""];}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(edtrul.custom === true) {\r\n
\t\t\t\tif( !(rqfield === false \046\046 $.jgrid.isEmpty(val)) ) {\r\n
\t\t\t\t\tif($.isFunction(edtrul.custom_func)) {\r\n
\t\t\t\t\t\tvar ret = edtrul.custom_func.call(g,val,nm);\r\n
\t\t\t\t\t\tif($.isArray(ret)) {\r\n
\t\t\t\t\t\t\treturn ret;\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\treturn [false,$.jgrid.edit.msg.customarray,""];\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\treturn [false,$.jgrid.edit.msg.customfcheck,""];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn [true,"",""];\r\n
\t}\r\n
});\r\n
})(jQuery);/*\r\n
 * jqFilter  jQuery jqGrid filter addon.\r\n
 * Copyright (c) 2011, Tony Tomov, tony@trirand.com\r\n
 * Dual licensed under the MIT and GPL licenses\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
 * \r\n
 * The work is inspired from this Stefan Pirvu\r\n
 * http://www.codeproject.com/KB/scripting/json-filtering.aspx\r\n
 *\r\n
 * The filter uses JSON entities to hold filter rules and groups. Here is an example of a filter:\r\n
\r\n
{ "groupOp": "AND",\r\n
      "groups" : [ \r\n
        { "groupOp": "OR",\r\n
            "rules": [\r\n
                { "field": "name", "op": "eq", "data": "England" }, \r\n
                { "field": "id", "op": "le", "data": "5"}\r\n
             ]\r\n
        } \r\n
      ],\r\n
      "rules": [\r\n
        { "field": "name", "op": "eq", "data": "Romania" }, \r\n
        { "field": "id", "op": "le", "data": "1"}\r\n
      ]\r\n
}\r\n
*/\r\n
/*global jQuery, $, window, navigator */\r\n
\r\n
(function ($) {\r\n
\r\n
$.fn.jqFilter = function( arg ) {\r\n
\tif (typeof arg === \'string\') {\r\n
\t\t\r\n
\t\tvar fn = $.fn.jqFilter[arg];\r\n
\t\tif (!fn) {\r\n
\t\t\tthrow ("jqFilter - No such method: " + arg);\r\n
\t\t}\r\n
\t\tvar args = $.makeArray(arguments).slice(1);\r\n
\t\treturn fn.apply(this,args);\r\n
\t}\r\n
\r\n
\tvar p = $.extend(true,{\r\n
\t\tfilter: null,\r\n
\t\tcolumns: [],\r\n
\t\tonChange : null,\r\n
\t\tafterRedraw : null,\r\n
\t\tcheckValues : null,\r\n
\t\terror: false,\r\n
\t\terrmsg : "",\r\n
\t\terrorcheck : true,\r\n
\t\tshowQuery : true,\r\n
\t\tsopt : null,\r\n
\t\tops : [\r\n
\t\t\t{"name": "eq", "description": "equal", "operator":"="},\r\n
\t\t\t{"name": "ne", "description": "not equal", "operator":"\074\076"},\r\n
\t\t\t{"name": "lt", "description": "less", "operator":"\074"},\r\n
\t\t\t{"name": "le", "description": "less or equal","operator":"\074="},\r\n
\t\t\t{"name": "gt", "description": "greater", "operator":"\076"},\r\n
\t\t\t{"name": "ge", "description": "greater or equal", "operator":"\076="},\r\n
\t\t\t{"name": "bw", "description": "begins with", "operator":"LIKE"},\r\n
\t\t\t{"name": "bn", "description": "does not begin with", "operator":"NOT LIKE"},\r\n
\t\t\t{"name": "in", "description": "in", "operator":"IN"},\r\n
\t\t\t{"name": "ni", "description": "not in", "operator":"NOT IN"},\r\n
\t\t\t{"name": "ew", "description": "ends with", "operator":"LIKE"},\r\n
\t\t\t{"name": "en", "description": "does not end with", "operator":"NOT LIKE"},\r\n
\t\t\t{"name": "cn", "description": "contains", "operator":"LIKE"},\r\n
\t\t\t{"name": "nc", "description": "does not contain", "operator":"NOT LIKE"},\r\n
\t\t\t{"name": "nu", "description": "is null", "operator":"IS NULL"},\r\n
\t\t\t{"name": "nn", "description": "is not null", "operator":"IS NOT NULL"}\r\n
\t\t],\r\n
\t\tnumopts : [\'eq\',\'ne\', \'lt\', \'le\', \'gt\', \'ge\', \'nu\', \'nn\', \'in\', \'ni\'],\r\n
\t\tstropts : [\'eq\', \'ne\', \'bw\', \'bn\', \'ew\', \'en\', \'cn\', \'nc\', \'nu\', \'nn\', \'in\', \'ni\'],\r\n
\t\t_gridsopt : [], // grid translated strings, do not tuch\r\n
\t\tgroupOps : [{ op: "AND", text: "AND" },\t{ op: "OR",  text: "OR" }],\r\n
\t\tgroupButton : true,\r\n
\t\truleButtons : true,\r\n
\t\tdirection : "ltr"\r\n
\t}, $.jgrid.filter, arg || {});\r\n
\treturn this.each( function() {\r\n
\t\tif (this.filter) {return;}\r\n
\t\tthis.p = p;\r\n
\t\t// setup filter in case if they is not defined\r\n
\t\tif (this.p.filter === null || this.p.filter === undefined) {\r\n
\t\t\tthis.p.filter = {\r\n
\t\t\t\tgroupOp: this.p.groupOps[0].op,\r\n
\t\t\t\trules: [],\r\n
\t\t\t\tgroups: []\r\n
\t\t\t};\r\n
\t\t}\r\n
\t\tvar i, len = this.p.columns.length, cl,\r\n
\t\tisIE = /msie/i.test(navigator.userAgent) \046\046 !window.opera;\r\n
\r\n
\t\t// translating the options\r\n
\t\tif(this.p._gridsopt.length) {\r\n
\t\t\t// [\'eq\',\'ne\',\'lt\',\'le\',\'gt\',\'ge\',\'bw\',\'bn\',\'in\',\'ni\',\'ew\',\'en\',\'cn\',\'nc\']\r\n
\t\t\tfor(i=0;i\074this.p._gridsopt.length;i++) {\r\n
\t\t\t\tthis.p.ops[i].description = this.p._gridsopt[i];\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tthis.p.initFilter = $.extend(true,{},this.p.filter);\r\n
\r\n
\t\t// set default values for the columns if they are not set\r\n
\t\tif( !len ) {return;}\r\n
\t\tfor(i=0; i \074 len; i++) {\r\n
\t\t\tcl = this.p.columns[i];\r\n
\t\t\tif( cl.stype ) {\r\n
\t\t\t\t// grid compatibility\r\n
\t\t\t\tcl.inputtype = cl.stype;\r\n
\t\t\t} else if(!cl.inputtype) {\r\n
\t\t\t\tcl.inputtype = \'text\';\r\n
\t\t\t}\r\n
\t\t\tif( cl.sorttype ) {\r\n
\t\t\t\t// grid compatibility\r\n
\t\t\t\tcl.searchtype = cl.sorttype;\r\n
\t\t\t} else if (!cl.searchtype) {\r\n
\t\t\t\tcl.searchtype = \'string\';\r\n
\t\t\t}\r\n
\t\t\tif(cl.hidden === undefined) {\r\n
\t\t\t\t// jqGrid compatibility\r\n
\t\t\t\tcl.hidden = false;\r\n
\t\t\t}\r\n
\t\t\tif(!cl.label) {\r\n
\t\t\t\tcl.label = cl.name;\r\n
\t\t\t}\r\n
\t\t\tif(cl.index) {\r\n
\t\t\t\tcl.name = cl.index;\r\n
\t\t\t}\r\n
\t\t\tif(!cl.hasOwnProperty(\'searchoptions\')) {\r\n
\t\t\t\tcl.searchoptions = {};\r\n
\t\t\t}\r\n
\t\t\tif(!cl.hasOwnProperty(\'searchrules\')) {\r\n
\t\t\t\tcl.searchrules = {};\r\n
\t\t\t}\r\n
\r\n
\t\t}\r\n
\t\tif(this.p.showQuery) {\r\n
\t\t\t$(this).append("\074table class=\'queryresult ui-widget ui-widget-content\' style=\'display:block;max-width:440px;border:0px none;\' dir=\'"+this.p.direction+"\'\076\074tbody\076\074tr\076\074td class=\'query\'\076\074/td\076\074/tr\076\074/tbody\076\074/table\076");\r\n
\t\t}\r\n
\t\t/*\r\n
\t\t *Perform checking.\r\n
\t\t *\r\n
\t\t*/\r\n
\t\tvar checkData = function(val, colModelItem) {\r\n
\t\t\tvar ret = [true,""];\r\n
\t\t\tif($.isFunction(colModelItem.searchrules)) {\r\n
\t\t\t\tret = colModelItem.searchrules(val, colModelItem);\r\n
\t\t\t} else if($.jgrid \046\046 $.jgrid.checkValues) {\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\tret = $.jgrid.checkValues(val, -1, null, colModelItem.searchrules, colModelItem.label);\r\n
\t\t\t\t} catch (e) {}\r\n
\t\t\t}\r\n
\t\t\tif(ret \046\046 ret.length \046\046 ret[0] === false) {\r\n
\t\t\t\tp.error = !ret[0];\r\n
\t\t\t\tp.errmsg = ret[1];\r\n
\t\t\t}\r\n
\t\t};\r\n
\t\t/* moving to common\r\n
\t\trandId = function() {\r\n
\t\t\treturn Math.floor(Math.random()*10000).toString();\r\n
\t\t};\r\n
\t\t*/\r\n
\r\n
\t\tthis.onchange = function (  ){\r\n
\t\t\t// clear any error \r\n
\t\t\tthis.p.error = false;\r\n
\t\t\tthis.p.errmsg="";\r\n
\t\t\treturn $.isFunction(this.p.onChange) ? this.p.onChange.call( this, this.p ) : false;\r\n
\t\t};\r\n
\t\t/*\r\n
\t\t * Redraw the filter every time when new field is added/deleted\r\n
\t\t * and field is  changed\r\n
\t\t */\r\n
\t\tthis.reDraw = function() {\r\n
\t\t\t$("table.group:first",this).remove();\r\n
\t\t\tvar t = this.createTableForGroup(p.filter, null);\r\n
\t\t\t$(this).append(t);\r\n
\t\t\tif($.isFunction(this.p.afterRedraw) ) {\r\n
\t\t\t\tthis.p.afterRedraw.call(this, this.p);\r\n
\t\t\t}\r\n
\t\t};\r\n
\t\t/*\r\n
\t\t * Creates a grouping data for the filter\r\n
\t\t * @param group - object\r\n
\t\t * @param parentgroup - object\r\n
\t\t */\r\n
\t\tthis.createTableForGroup = function(group, parentgroup) {\r\n
\t\t\tvar that = this,  i;\r\n
\t\t\t// this table will hold all the group (tables) and rules (rows)\r\n
\t\t\tvar table = $("\074table class=\'group ui-widget ui-widget-content\' style=\'border:0px none;\'\076\074tbody\076\074/tbody\076\074/table\076"),\r\n
\t\t\t// create error message row\r\n
\t\t\talign = "left";\r\n
\t\t\tif(this.p.direction == "rtl") {\r\n
\t\t\t\talign = "right";\r\n
\t\t\t\ttable.attr("dir","rtl");\r\n
\t\t\t}\r\n
\t\t\tif(parentgroup === null) {\r\n
\t\t\t\ttable.append("\074tr class=\'error\' style=\'display:none;\'\076\074th colspan=\'5\' class=\'ui-state-error\' align=\'"+align+"\'\076\074/th\076\074/tr\076");\r\n
\t\t\t}\r\n
\r\n
\t\t\tvar tr = $("\074tr\076\074/tr\076");\r\n
\t\t\ttable.append(tr);\r\n
\t\t\t// this header will hold the group operator type and group action buttons for\r\n
\t\t\t// creating subgroup "+ {}", creating rule "+" or deleting the group "-"\r\n
\t\t\tvar th = $("\074th colspan=\'5\' align=\'"+align+"\'\076\074/th\076");\r\n
\t\t\ttr.append(th);\r\n
\r\n
\t\t\tif(this.p.ruleButtons === true) {\r\n
\t\t\t// dropdown for: choosing group operator type\r\n
\t\t\tvar groupOpSelect = $("\074select class=\'opsel\'\076\074/select\076");\r\n
\t\t\tth.append(groupOpSelect);\r\n
\t\t\t// populate dropdown with all posible group operators: or, and\r\n
\t\t\tvar str= "", selected;\r\n
\t\t\tfor (i = 0; i \074 p.groupOps.length; i++) {\r\n
\t\t\t\tselected =  group.groupOp === that.p.groupOps[i].op ? " selected=\'selected\'" :"";\r\n
\t\t\t\tstr += "\074option value=\'"+that.p.groupOps[i].op+"\'" + selected+"\076"+that.p.groupOps[i].text+"\074/option\076";\r\n
\t\t\t}\r\n
\r\n
\t\t\tgroupOpSelect\r\n
\t\t\t.append(str)\r\n
\t\t\t.bind(\'change\',function() {\r\n
\t\t\t\tgroup.groupOp = $(groupOpSelect).val();\r\n
\t\t\t\tthat.onchange(); // signals that the filter has changed\r\n
\t\t\t});\r\n
\t\t\t}\r\n
\t\t\t// button for adding a new subgroup\r\n
\t\t\tvar inputAddSubgroup ="\074span\076\074/span\076";\r\n
\t\t\tif(this.p.groupButton) {\r\n
\t\t\t\tinputAddSubgroup = $("\074input type=\'button\' value=\'+ {}\' title=\'Add subgroup\' class=\'add-group\'/\076");\r\n
\t\t\t\tinputAddSubgroup.bind(\'click\',function() {\r\n
\t\t\t\t\tif (group.groups === undefined ) {\r\n
\t\t\t\t\t\tgroup.groups = [];\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tgroup.groups.push({\r\n
\t\t\t\t\t\tgroupOp: p.groupOps[0].op,\r\n
\t\t\t\t\t\trules: [],\r\n
\t\t\t\t\t\tgroups: []\r\n
\t\t\t\t\t}); // adding a new group\r\n
\r\n
\t\t\t\t\tthat.reDraw(); // the html has changed, force reDraw\r\n
\r\n
\t\t\t\t\tthat.onchange(); // signals that the filter has changed\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tth.append(inputAddSubgroup);\r\n
\t\t\tif(this.p.ruleButtons === true) {\r\n
\t\t\t// button for adding a new rule\r\n
\t\t\tvar inputAddRule = $("\074input type=\'button\' value=\'+\' title=\'Add rule\' class=\'add-rule ui-add\'/\076"), cm;\r\n
\t\t\tinputAddRule.bind(\'click\',function() {\r\n
\t\t\t\t//if(!group) { group = {};}\r\n
\t\t\t\tif (group.rules === undefined) {\r\n
\t\t\t\t\tgroup.rules = [];\r\n
\t\t\t\t}\r\n
\t\t\t\tfor (i = 0; i \074 that.p.columns.length; i++) {\r\n
\t\t\t\t// but show only serchable and serchhidden = true fields\r\n
\t\t\t\t\tvar searchable = (typeof that.p.columns[i].search === \'undefined\') ?  true: that.p.columns[i].search ,\r\n
\t\t\t\t\thidden = (that.p.columns[i].hidden === true),\r\n
\t\t\t\t\tignoreHiding = (that.p.columns[i].searchoptions.searchhidden === true);\r\n
\t\t\t\t\tif ((ignoreHiding \046\046 searchable) || (searchable \046\046 !hidden)) {\r\n
\t\t\t\t\t\tcm = that.p.columns[i];\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\t\r\n
\t\t\t\tvar opr;\r\n
\t\t\t\tif( cm.searchoptions.sopt ) {opr = cm.searchoptions.sopt;}\r\n
\t\t\t\telse if(that.p.sopt) { opr= that.p.sopt; }\r\n
\t\t\t\telse if  (cm.searchtype === \'string\') {opr = that.p.stropts;}\r\n
\t\t\t\telse {opr = that.p.numopts;}\r\n
\r\n
\t\t\t\tgroup.rules.push({\r\n
\t\t\t\t\tfield: cm.name,\r\n
\t\t\t\t\top: opr[0],\r\n
\t\t\t\t\tdata: ""\r\n
\t\t\t\t}); // adding a new rule\r\n
\r\n
\t\t\t\tthat.reDraw(); // the html has changed, force reDraw\r\n
\t\t\t\t// for the moment no change have been made to the rule, so\r\n
\t\t\t\t// this will not trigger onchange event\r\n
\t\t\t\treturn false;\r\n
\t\t\t});\r\n
\t\t\tth.append(inputAddRule);\r\n
\t\t\t}\r\n
\r\n
\t\t\t// button for delete the group\r\n
\t\t\tif (parentgroup !== null) { // ignore the first group\r\n
\t\t\t\tvar inputDeleteGroup = $("\074input type=\'button\' value=\'-\' title=\'Delete group\' class=\'delete-group\'/\076");\r\n
\t\t\t\tth.append(inputDeleteGroup);\r\n
\t\t\t\tinputDeleteGroup.bind(\'click\',function() {\r\n
\t\t\t\t// remove group from parent\r\n
\t\t\t\t\tfor (i = 0; i \074 parentgroup.groups.length; i++) {\r\n
\t\t\t\t\t\tif (parentgroup.groups[i] === group) {\r\n
\t\t\t\t\t\t\tparentgroup.groups.splice(i, 1);\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tthat.reDraw(); // the html has changed, force reDraw\r\n
\r\n
\t\t\t\t\tthat.onchange(); // signals that the filter has changed\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\r\n
\t\t\t// append subgroup rows\r\n
\t\t\tif (group.groups !== undefined) {\r\n
\t\t\t\tfor (i = 0; i \074 group.groups.length; i++) {\r\n
\t\t\t\t\tvar trHolderForSubgroup = $("\074tr\076\074/tr\076");\r\n
\t\t\t\t\ttable.append(trHolderForSubgroup);\r\n
\r\n
\t\t\t\t\tvar tdFirstHolderForSubgroup = $("\074td class=\'first\'\076\074/td\076");\r\n
\t\t\t\t\ttrHolderForSubgroup.append(tdFirstHolderForSubgroup);\r\n
\r\n
\t\t\t\t\tvar tdMainHolderForSubgroup = $("\074td colspan=\'4\'\076\074/td\076");\r\n
\t\t\t\t\ttdMainHolderForSubgroup.append(this.createTableForGroup(group.groups[i], group));\r\n
\t\t\t\t\ttrHolderForSubgroup.append(tdMainHolderForSubgroup);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(group.groupOp === undefined) {\r\n
\t\t\t\tgroup.groupOp = that.p.groupOps[0].op;\r\n
\t\t\t}\r\n
\r\n
\t\t\t// append rules rows\r\n
\t\t\tif (group.rules !== undefined) {\r\n
\t\t\t\tfor (i = 0; i \074 group.rules.length; i++) {\r\n
\t\t\t\t\ttable.append(\r\n
                       this.createTableRowForRule(group.rules[i], group)\r\n
\t\t\t\t\t);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\treturn table;\r\n
\t\t};\r\n
\t\t/*\r\n
\t\t * Create the rule data for the filter\r\n
\t\t */\r\n
\t\tthis.createTableRowForRule = function(rule, group ) {\r\n
\t\t\t// save current entity in a variable so that it could\r\n
\t\t\t// be referenced in anonimous method calls\r\n
\r\n
\t\t\tvar that=this, tr = $("\074tr\076\074/tr\076"),\r\n
\t\t\t//document.createElement("tr"),\r\n
\r\n
\t\t\t// first column used for padding\r\n
\t\t\t//tdFirstHolderForRule = document.createElement("td"),\r\n
\t\t\ti, op, trpar, cm, str="", selected;\r\n
\t\t\t//tdFirstHolderForRule.setAttribute("class", "first");\r\n
\t\t\ttr.append("\074td class=\'first\'\076\074/td\076");\r\n
\r\n
\r\n
\t\t\t// create field container\r\n
\t\t\tvar ruleFieldTd = $("\074td class=\'columns\'\076\074/td\076");\r\n
\t\t\ttr.append(ruleFieldTd);\r\n
\r\n
\r\n
\t\t\t// dropdown for: choosing field\r\n
\t\t\tvar ruleFieldSelect = $("\074select\076\074/select\076"), ina, aoprs = [];\r\n
\t\t\truleFieldTd.append(ruleFieldSelect);\r\n
\t\t\truleFieldSelect.bind(\'change\',function() {\r\n
\t\t\t\trule.field = $(ruleFieldSelect).val();\r\n
\r\n
\t\t\t\ttrpar = $(this).parents("tr:first");\r\n
\t\t\t\tfor (i=0;i\074that.p.columns.length;i++) {\r\n
\t\t\t\t\tif(that.p.columns[i].name ===  rule.field) {\r\n
\t\t\t\t\t\tcm = that.p.columns[i];\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(!cm) {return;}\r\n
\t\t\t\tcm.searchoptions.id = $.jgrid.randId();\r\n
\t\t\t\tif(isIE \046\046 cm.inputtype === "text") {\r\n
\t\t\t\t\tif(!cm.searchoptions.size) {\r\n
\t\t\t\t\t\tcm.searchoptions.size = 10;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tvar elm = $.jgrid.createEl(cm.inputtype,cm.searchoptions, "", true, that.p.ajaxSelectOptions, true);\r\n
\t\t\t\t$(elm).addClass("input-elm");\r\n
\t\t\t\t//that.createElement(rule, "");\r\n
\r\n
\t\t\t\tif( cm.searchoptions.sopt ) {op = cm.searchoptions.sopt;}\r\n
\t\t\t\telse if(that.p.sopt) { op= that.p.sopt; }\r\n
\t\t\t\telse if  (cm.searchtype === \'string\') {op = that.p.stropts;}\r\n
\t\t\t\telse {op = that.p.numopts;}\r\n
\t\t\t\t// operators\r\n
\t\t\t\tvar s ="", so = 0;\r\n
\t\t\t\taoprs = [];\r\n
\t\t\t\t$.each(that.p.ops, function() { aoprs.push(this.name) });\r\n
\t\t\t\tfor ( i = 0 ; i \074 op.length; i++) {\r\n
\t\t\t\t\tina = $.inArray(op[i],aoprs);\r\n
\t\t\t\t\tif(ina !== -1) {\r\n
\t\t\t\t\t\tif(so===0) {\r\n
\t\t\t\t\t\t\trule.op = that.p.ops[ina].name;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ts += "\074option value=\'"+that.p.ops[ina].name+"\'\076"+that.p.ops[ina].description+"\074/option\076";\r\n
\t\t\t\t\t\tso++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\t$(".selectopts",trpar).empty().append( s );\r\n
\t\t\t\t$(".selectopts",trpar)[0].selectedIndex = 0;\r\n
\t\t\t\tif( $.browser.msie \046\046 $.browser.version \074 9) {\r\n
\t\t\t\t\tvar sw = parseInt($("select.selectopts",trpar)[0].offsetWidth) + 1;\r\n
\t\t\t\t\t$(".selectopts",trpar).width( sw );\r\n
\t\t\t\t\t$(".selectopts",trpar).css("width","auto");\r\n
\t\t\t\t}\r\n
\t\t\t\t// data\r\n
\t\t\t\t$(".data",trpar).empty().append( elm );\r\n
\t\t\t\t$(".input-elm",trpar).bind(\'change\',function( e ) {\r\n
\t\t\t\t\tvar tmo = $(this).hasClass("ui-autocomplete-input") ? 200 :0;\r\n
\t\t\t\t\tsetTimeout(function(){\r\n
\t\t\t\t\t\tvar elem = e.target;\r\n
\t\t\t\t\t\trule.data = elem.nodeName.toUpperCase() === "SPAN" \046\046 cm.searchoptions \046\046 $.isFunction(cm.searchoptions.custom_value) ?\r\n
\t\t\t\t\t\t\tcm.searchoptions.custom_value($(elem).children(".customelement:first"), \'get\') : elem.value;\r\n
\t\t\t\t\t\tthat.onchange(); // signals that the filter has changed\r\n
\t\t\t\t\t}, tmo);\r\n
\t\t\t\t});\r\n
\t\t\t\tsetTimeout(function(){ //IE, Opera, Chrome\r\n
\t\t\t\trule.data = $(elm).val();\r\n
\t\t\t\tthat.onchange();  // signals that the filter has changed\r\n
\t\t\t\t}, 0);\r\n
\t\t\t});\r\n
\r\n
\t\t\t// populate drop down with user provided column definitions\r\n
\t\t\tvar j=0;\r\n
\t\t\tfor (i = 0; i \074 that.p.columns.length; i++) {\r\n
\t\t\t\t// but show only serchable and serchhidden = true fields\r\n
\t\t        var searchable = (typeof that.p.columns[i].search === \'undefined\') ?  true: that.p.columns[i].search ,\r\n
\t\t        hidden = (that.p.columns[i].hidden === true),\r\n
\t\t\t\tignoreHiding = (that.p.columns[i].searchoptions.searchhidden === true);\r\n
\t\t\t\tif ((ignoreHiding \046\046 searchable) || (searchable \046\046 !hidden)) {\r\n
\t\t\t\t\tselected = "";\r\n
\t\t\t\t\tif(rule.field === that.p.columns[i].name) {\r\n
\t\t\t\t\t\tselected = " selected=\'selected\'";\r\n
\t\t\t\t\t\tj=i;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tstr += "\074option value=\'"+that.p.columns[i].name+"\'" +selected+"\076"+that.p.columns[i].label+"\074/option\076";\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\truleFieldSelect.append( str );\r\n
\r\n
\r\n
\t\t\t// create operator container\r\n
\t\t\tvar ruleOperatorTd = $("\074td class=\'operators\'\076\074/td\076");\r\n
\t\t\ttr.append(ruleOperatorTd);\r\n
\t\t\tcm = p.columns[j];\r\n
\t\t\t// create it here so it can be referentiated in the onchange event\r\n
\t\t\t//var RD = that.createElement(rule, rule.data);\r\n
\t\t\tcm.searchoptions.id = $.jgrid.randId();\r\n
\t\t\tif(isIE \046\046 cm.inputtype === "text") {\r\n
\t\t\t\tif(!cm.searchoptions.size) {\r\n
\t\t\t\t\tcm.searchoptions.size = 10;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tvar ruleDataInput = $.jgrid.createEl(cm.inputtype,cm.searchoptions, rule.data, true, that.p.ajaxSelectOptions, true);\r\n
\r\n
\t\t\t// dropdown for: choosing operator\r\n
\t\t\tvar ruleOperatorSelect = $("\074select class=\'selectopts\'\076\074/select\076");\r\n
\t\t\truleOperatorTd.append(ruleOperatorSelect);\r\n
\t\t\truleOperatorSelect.bind(\'change\',function() {\r\n
\t\t\t\trule.op = $(ruleOperatorSelect).val();\r\n
\t\t\t\ttrpar = $(this).parents("tr:first");\r\n
\t\t\t\tvar rd = $(".input-elm",trpar)[0];\r\n
\t\t\t\tif (rule.op === "nu" || rule.op === "nn") { // disable for operator "is null" and "is not null"\r\n
\t\t\t\t\trule.data = "";\r\n
\t\t\t\t\trd.value = "";\r\n
\t\t\t\t\trd.setAttribute("readonly", "true");\r\n
\t\t\t\t\trd.setAttribute("disabled", "true");\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\trd.removeAttribute("readonly");\r\n
\t\t\t\t\trd.removeAttribute("disabled");\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthat.onchange();  // signals that the filter has changed\r\n
\t\t\t});\r\n
\r\n
\t\t\t// populate drop down with all available operators\r\n
\t\t\tif( cm.searchoptions.sopt ) {op = cm.searchoptions.sopt;}\r\n
\t\t\telse if(that.p.sopt) { op= that.p.sopt; }\r\n
\t\t\telse if  (cm.searchtype === \'string\') {op = p.stropts;}\r\n
\t\t\telse {op = that.p.numopts;}\r\n
\t\t\tstr="";\r\n
\t\t\t$.each(that.p.ops, function() { aoprs.push(this.name) });\r\n
\t\t\tfor ( i = 0; i \074 op.length; i++) {\r\n
\t\t\t\tina = $.inArray(op[i],aoprs);\r\n
\t\t\t\tif(ina !== -1) {\r\n
\t\t\t\t\tselected = rule.op === that.p.ops[ina].name ? " selected=\'selected\'" : "";\r\n
\t\t\t\t\tstr += "\074option value=\'"+that.p.ops[ina].name+"\'"+selected+"\076"+that.p.ops[ina].description+"\074/option\076";\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\truleOperatorSelect.append( str );\r\n
\t\t\t// create data container\r\n
\t\t\tvar ruleDataTd = $("\074td class=\'data\'\076\074/td\076");\r\n
\t\t\ttr.append(ruleDataTd);\r\n
\r\n
\t\t\t// textbox for: data\r\n
\t\t\t// is created previously\r\n
\t\t\t//ruleDataInput.setAttribute("type", "text");\r\n
\t\t\truleDataTd.append(ruleDataInput);\r\n
\r\n
\t\t\t$(ruleDataInput)\r\n
\t\t\t.addClass("input-elm")\r\n
\t\t\t.bind(\'change\', function() {\r\n
\t\t\t\trule.data = cm.inputtype === \'custom\' ? cm.searchoptions.custom_value($(this).children(".customelement:first"),\'get\') : $(this).val();\r\n
\t\t\t\tthat.onchange(); // signals that the filter has changed\r\n
\t\t\t});\r\n
\r\n
\t\t\t// create action container\r\n
\t\t\tvar ruleDeleteTd = $("\074td\076\074/td\076");\r\n
\t\t\ttr.append(ruleDeleteTd);\r\n
\r\n
\t\t\t// create button for: delete rule\r\n
\t\t\tif(this.p.ruleButtons === true) {\r\n
\t\t\tvar ruleDeleteInput = $("\074input type=\'button\' value=\'-\' title=\'Delete rule\' class=\'delete-rule ui-del\'/\076");\r\n
\t\t\truleDeleteTd.append(ruleDeleteInput);\r\n
\t\t\t//$(ruleDeleteInput).html("").height(20).width(30).button({icons: {  primary: "ui-icon-minus", text:false}});\r\n
\t\t\truleDeleteInput.bind(\'click\',function() {\r\n
\t\t\t\t// remove rule from group\r\n
\t\t\t\tfor (i = 0; i \074 group.rules.length; i++) {\r\n
\t\t\t\t\tif (group.rules[i] === rule) {\r\n
\t\t\t\t\t\tgroup.rules.splice(i, 1);\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tthat.reDraw(); // the html has changed, force reDraw\r\n
\r\n
\t\t\t\tthat.onchange(); // signals that the filter has changed\r\n
\t\t\t\treturn false;\r\n
\t\t\t});\r\n
\t\t\t}\r\n
\t\t\treturn tr;\r\n
\t\t};\r\n
\r\n
\t\tthis.getStringForGroup = function(group) {\r\n
\t\t\tvar s = "(", index;\r\n
\t\t\tif (group.groups !== undefined) {\r\n
\t\t\t\tfor (index = 0; index \074 group.groups.length; index++) {\r\n
\t\t\t\t\tif (s.length \076 1) {\r\n
\t\t\t\t\t\ts += " " + group.groupOp + " ";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\ttry {\r\n
\t\t\t\t\t\ts += this.getStringForGroup(group.groups[index]);\r\n
\t\t\t\t\t} catch (eg) {alert(eg);}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tif (group.rules !== undefined) {\r\n
\t\t\t\ttry{\r\n
\t\t\t\t\tfor (index = 0; index \074 group.rules.length; index++) {\r\n
\t\t\t\t\t\tif (s.length \076 1) {\r\n
\t\t\t\t\t\t\ts += " " + group.groupOp + " ";\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ts += this.getStringForRule(group.rules[index]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} catch (e) {alert(e);}\r\n
\t\t\t}\r\n
\r\n
\t\t\ts += ")";\r\n
\r\n
\t\t\tif (s === "()") {\r\n
\t\t\t\treturn ""; // ignore groups that don\'t have rules\r\n
\t\t\t} else {\r\n
\t\t\t\treturn s;\r\n
\t\t\t}\r\n
\t\t};\r\n
\t\tthis.getStringForRule = function(rule) {\r\n
\t\t\tvar opUF = "",opC="", i, cm, ret, val,\r\n
\t\t\tnumtypes = [\'int\', \'integer\', \'float\', \'number\', \'currency\']; // jqGrid\r\n
\t\t\tfor (i = 0; i \074 this.p.ops.length; i++) {\r\n
\t\t\t\tif (this.p.ops[i].name === rule.op) {\r\n
\t\t\t\t\topUF = this.p.ops[i].operator;\r\n
\t\t\t\t\topC = this.p.ops[i].name;\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tfor (i=0; i\074this.p.columns.length; i++) {\r\n
\t\t\t\tif(this.p.columns[i].name === rule.field) {\r\n
\t\t\t\t\tcm = this.p.columns[i];\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tval = rule.data;\r\n
\t\t\tif(opC === \'bw\' || opC === \'bn\') { val = val+"%"; }\r\n
\t\t\tif(opC === \'ew\' || opC === \'en\') { val = "%"+val; }\r\n
\t\t\tif(opC === \'cn\' || opC === \'nc\') { val = "%"+val+"%"; }\r\n
\t\t\tif(opC === \'in\' || opC === \'ni\') { val = " ("+val+")"; }\r\n
\t\t\tif(p.errorcheck) { checkData(rule.data, cm); }\r\n
\t\t\tif($.inArray(cm.searchtype, numtypes) !== -1 || opC === \'nn\' || opC === \'nu\') { ret = rule.field + " " + opUF + " " + val; }\r\n
\t\t\telse { ret = rule.field + " " + opUF + " \\"" + val + "\\""; }\r\n
\t\t\treturn ret;\r\n
\t\t};\r\n
\t\tthis.resetFilter = function () {\r\n
\t\t\tthis.p.filter = $.extend(true,{},this.p.initFilter);\r\n
\t\t\tthis.reDraw();\r\n
\t\t\tthis.onchange();\r\n
\t\t};\r\n
\t\tthis.hideError = function() {\r\n
\t\t\t$("th.ui-state-error", this).html("");\r\n
\t\t\t$("tr.error", this).hide();\r\n
\t\t};\r\n
\t\tthis.showError = function() {\r\n
\t\t\t$("th.ui-state-error", this).html(this.p.errmsg);\r\n
\t\t\t$("tr.error", this).show();\r\n
\t\t};\r\n
\t\tthis.toUserFriendlyString = function() {\r\n
\t\t\treturn this.getStringForGroup(p.filter);\r\n
\t\t};\r\n
\t\tthis.toString = function() {\r\n
\t\t\t// this will obtain a string that can be used to match an item.\r\n
\t\t\tvar that = this;\r\n
\t\t\tfunction getStringRule(rule) {\r\n
\t\t\t\tif(that.p.errorcheck) {\r\n
\t\t\t\t\tvar i, cm;\r\n
\t\t\t\t\tfor (i=0; i\074that.p.columns.length; i++) {\r\n
\t\t\t\t\t\tif(that.p.columns[i].name === rule.field) {\r\n
\t\t\t\t\t\t\tcm = that.p.columns[i];\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(cm) {checkData(rule.data, cm);}\r\n
\t\t\t\t}\r\n
\t\t\t\treturn rule.op + "(item." + rule.field + ",\'" + rule.data + "\')";\r\n
\t\t\t}\r\n
\r\n
\t\t\tfunction getStringForGroup(group) {\r\n
\t\t\t\tvar s = "(", index;\r\n
\r\n
\t\t\t\tif (group.groups !== undefined) {\r\n
\t\t\t\t\tfor (index = 0; index \074 group.groups.length; index++) {\r\n
\t\t\t\t\t\tif (s.length \076 1) {\r\n
\t\t\t\t\t\t\tif (group.groupOp === "OR") {\r\n
\t\t\t\t\t\t\t\ts += " || ";\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\telse {\r\n
\t\t\t\t\t\t\t\ts += " \046\046 ";\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ts += getStringForGroup(group.groups[index]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tif (group.rules !== undefined) {\r\n
\t\t\t\t\tfor (index = 0; index \074 group.rules.length; index++) {\r\n
\t\t\t\t\t\tif (s.length \076 1) {\r\n
\t\t\t\t\t\t\tif (group.groupOp === "OR") {\r\n
\t\t\t\t\t\t\t\ts += " || ";\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\telse  {\r\n
\t\t\t\t\t\t\t\ts += " \046\046 ";\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ts += getStringRule(group.rules[index]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\ts += ")";\r\n
\r\n
\t\t\t\tif (s === "()") {\r\n
\t\t\t\t\treturn ""; // ignore groups that don\'t have rules\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\treturn s;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\treturn getStringForGroup(this.p.filter);\r\n
\t\t};\r\n
\r\n
\t\t// Here we init the filter\r\n
\t\tthis.reDraw();\r\n
\r\n
\t\tif(this.p.showQuery) {\r\n
\t\t\tthis.onchange();\r\n
\t\t}\r\n
\t\t// mark is as created so that it will not be created twice on this element\r\n
\t\tthis.filter = true;\r\n
\t});\r\n
};\r\n
$.extend($.fn.jqFilter,{\r\n
\t/*\r\n
\t * Return SQL like string. Can be used directly\r\n
\t */\r\n
\ttoSQLString : function()\r\n
\t{\r\n
\t\tvar s ="";\r\n
\t\tthis.each(function(){\r\n
\t\t\ts = this.toUserFriendlyString();\r\n
\t\t});\r\n
\t\treturn s;\r\n
\t},\r\n
\t/*\r\n
\t * Return filter data as object.\r\n
\t */\r\n
\tfilterData : function()\r\n
\t{\r\n
\t\tvar s;\r\n
\t\tthis.each(function(){\r\n
\t\t\ts = this.p.filter;\r\n
\t\t});\r\n
\t\treturn s;\r\n
\r\n
\t},\r\n
\tgetParameter : function (param) {\r\n
\t\tif(param !== undefined) {\r\n
\t\t\tif (this.p.hasOwnProperty(param) ) {\r\n
\t\t\t\treturn this.p[param];\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn this.p;\r\n
\t},\r\n
\tresetFilter: function() {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tthis.resetFilter();\r\n
\t\t});\r\n
\t},\r\n
\taddFilter: function (pfilter) {\r\n
\t\tif (typeof pfilter === "string") {\r\n
\t\t\tpfilter = jQuery.jgrid.parse( pfilter );\r\n
\t}\r\n
\t\tthis.each(function(){\r\n
\t\t\tthis.p.filter = pfilter;\r\n
\t\t\tthis.reDraw();\r\n
\t\t\tthis.onchange();\r\n
\t\t});\r\n
\t}\r\n
\r\n
});\r\n
})(jQuery);\r\n
\r\n
(function($){\r\n
/**\r\n
 * jqGrid extension for form editing Grid Data\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/\r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
**/\r\n
"use strict";\r\n
/*global xmlJsonClass, jQuery, $  */\r\n
var rp_ge = {};\r\n
$.jgrid.extend({\r\n
\tsearchGrid : function (p) {\r\n
\t\tp = $.extend({\r\n
\t\t\trecreateFilter: false,\r\n
\t\t\tdrag: true,\r\n
\t\t\tsField:\'searchField\',\r\n
\t\t\tsValue:\'searchString\',\r\n
\t\t\tsOper: \'searchOper\',\r\n
\t\t\tsFilter: \'filters\',\r\n
\t\t\tloadDefaults: true, // this options activates loading of default filters from grid\'s postData for Multipe Search only.\r\n
\t\t\tbeforeShowSearch: null,\r\n
\t\t\tafterShowSearch : null,\r\n
\t\t\tonInitializeSearch: null,\r\n
\t\t\tafterRedraw : null,\r\n
\t\t\tafterChange: null,\r\n
\t\t\tcloseAfterSearch : false,\r\n
\t\t\tcloseAfterReset: false,\r\n
\t\t\tcloseOnEscape : false,\r\n
\t\t\tsearchOnEnter : false,\r\n
\t\t\tmultipleSearch : false,\r\n
\t\t\tmultipleGroup : false,\r\n
\t\t\t//cloneSearchRowOnAdd: true,\r\n
\t\t\ttop : 0,\r\n
\t\t\tleft: 0,\r\n
\t\t\tjqModal : true,\r\n
\t\t\tmodal: false,\r\n
\t\t\tresize : true,\r\n
\t\t\twidth: 450,\r\n
\t\t\theight: \'auto\',\r\n
\t\t\tdataheight: \'auto\',\r\n
\t\t\tshowQuery: false,\r\n
\t\t\terrorcheck : true,\r\n
\t\t\t// translation\r\n
\t\t\t// if you want to change or remove the order change it in sopt\r\n
\t\t\t// [\'eq\',\'ne\',\'lt\',\'le\',\'gt\',\'ge\',\'bw\',\'bn\',\'in\',\'ni\',\'ew\',\'en\',\'cn\',\'nc\'],\r\n
\t\t\tsopt: null,\r\n
\t\t\tstringResult: undefined,\r\n
\t\t\tonClose : null,\r\n
\t\t\tonSearch : null,\r\n
\t\t\tonReset : null,\r\n
\t\t\ttoTop : true,\r\n
\t\t\toverlay : 30,\r\n
\t\t\tcolumns : [],\r\n
\t\t\ttmplNames : null,\r\n
\t\t\ttmplFilters : null,\r\n
\t\t\t// translations - later in lang file\r\n
\t\t\ttmplLabel : \' Template: \',\r\n
\t\t\tshowOnLoad: false,\r\n
\t\t\tlayer: null\r\n
\t\t}, $.jgrid.search, p || {});\r\n
\t\treturn this.each(function() {\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid) {return;}\r\n
\t\t\tvar fid = "fbox_"+$t.p.id,\r\n
\t\t\tshowFrm = true,\r\n
\t\t\tIDs = {themodal:\'searchmod\'+fid,modalhead:\'searchhd\'+fid,modalcontent:\'searchcnt\'+fid, scrollelm : fid},\r\n
\t\t\tdefaultFilters  = $t.p.postData[p.sFilter];\r\n
\t\t\tif(typeof(defaultFilters) === "string") {\r\n
\t\t\t\tdefaultFilters = $.jgrid.parse( defaultFilters );\r\n
\t\t\t}\r\n
\t\t\tif(p.recreateFilter === true) {\r\n
\t\t\t\t$("#"+$.jgrid.jqID(IDs.themodal)).remove();\r\n
\t\t\t}\r\n
\t\t\tfunction showFilter(_filter) {\r\n
\t\t\t\tshowFrm = $($t).triggerHandler("jqGridFilterBeforeShow", [_filter]);\r\n
\t\t\t\tif(typeof(showFrm) === "undefined") {\r\n
\t\t\t\t\tshowFrm = true;\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm \046\046 $.isFunction(p.beforeShowSearch)) {\r\n
\t\t\t\t\tshowFrm = p.beforeShowSearch.call($t,_filter);\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm) {\r\n
\t\t\t\t\t$.jgrid.viewModal("#"+$.jgrid.jqID(IDs.themodal),{gbox:"#gbox_"+$.jgrid.jqID(fid),jqm:p.jqModal, modal:p.modal, overlay: p.overlay, toTop: p.toTop});\r\n
\t\t\t\t\t$($t).triggerHandler("jqGridFilterAfterShow", [_filter]);\r\n
\t\t\t\t\tif($.isFunction(p.afterShowSearch)) {\r\n
\t\t\t\t\t\tp.afterShowSearch.call($t, _filter);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif ( $("#"+$.jgrid.jqID(IDs.themodal))[0] !== undefined ) {\r\n
\t\t\t\tshowFilter($("#fbox_"+$.jgrid.jqID(+$t.p.id)));\r\n
\t\t\t} else {\r\n
\t\t\t\tvar fil = $("\074div\076\074div id=\'"+fid+"\' class=\'searchFilter\' style=\'overflow:auto\'\076\074/div\076\074/div\076").insertBefore("#gview_"+$.jgrid.jqID($t.p.id)),\r\n
\t\t\t\talign = "left", butleft =""; \r\n
\t\t\t\tif($t.p.direction == "rtl") {\r\n
\t\t\t\t\talign = "right";\r\n
\t\t\t\t\tbutleft = " style=\'text-align:left\'";\r\n
\t\t\t\t\tfil.attr("dir","rtl");\r\n
\t\t\t\t}\r\n
\t\t\t\tvar columns = $.extend([],$t.p.colModel),\r\n
\t\t\t\tbS  ="\074a href=\'javascript:void(0)\' id=\'"+fid+"_search\' class=\'fm-button ui-state-default ui-corner-all fm-button-icon-right ui-reset\'\076\074span class=\'ui-icon ui-icon-search\'\076\074/span\076"+p.Find+"\074/a\076",\r\n
\t\t\t\tbC  ="\074a href=\'javascript:void(0)\' id=\'"+fid+"_reset\' class=\'fm-button ui-state-default ui-corner-all fm-button-icon-left ui-search\'\076\074span class=\'ui-icon ui-icon-arrowreturnthick-1-w\'\076\074/span\076"+p.Reset+"\074/a\076",\r\n
\t\t\t\tbQ = "", tmpl="", colnm, found = false, bt, cmi=-1;\r\n
\t\t\t\tif(p.showQuery) {\r\n
\t\t\t\t\tbQ ="</string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAU=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="5" aka="AAAAAAAAAAU=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

<a href=\'javascript:void(0)\' id=\'"+fid+"_query\' class=\'fm-button ui-state-default ui-corner-all fm-button-icon-left\'><span class=\'ui-icon ui-icon-comment\'></span>Query</a>";\r\n
\t\t\t\t}\r\n
\t\t\t\tif(!p.columns.length) {\r\n
\t\t\t\t\t$.each(columns, function(i,n){\r\n
\t\t\t\t\t\tif(!n.label) {\r\n
\t\t\t\t\t\t\tn.label = $t.p.colNames[i];\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t// find first searchable column and set it if no default filter\r\n
\t\t\t\t\t\tif(!found) {\r\n
\t\t\t\t\t\t\tvar searchable = (typeof n.search === \'undefined\') ?  true: n.search ,\r\n
\t\t\t\t\t\t\thidden = (n.hidden === true),\r\n
\t\t\t\t\t\t\tignoreHiding = (n.searchoptions && n.searchoptions.searchhidden === true);\r\n
\t\t\t\t\t\t\tif ((ignoreHiding && searchable) || (searchable && !hidden)) {\r\n
\t\t\t\t\t\t\t\tfound = true;\r\n
\t\t\t\t\t\t\t\tcolnm = n.index || n.name;\r\n
\t\t\t\t\t\t\t\tcmi =i;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tcolumns = p.columns;\r\n
\t\t\t\t}\r\n
\t\t\t\t// old behaviour\r\n
\t\t\t\tif( (!defaultFilters && colnm) || p.multipleSearch === false  ) {\r\n
\t\t\t\t\tvar cmop = "eq";\r\n
\t\t\t\t\tif(cmi >=0 && columns[cmi].searchoptions && columns[cmi].searchoptions.sopt) {\r\n
\t\t\t\t\t\tcmop = columns[cmi].searchoptions.sopt[0];\r\n
\t\t\t\t\t} else if(p.sopt && p.sopt.length) {\r\n
\t\t\t\t\t\tcmop = p.sopt[0];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tdefaultFilters = {"groupOp": "AND",rules:[{"field":colnm,"op":cmop,"data":""}]};\r\n
\t\t\t\t}\r\n
\t\t\t\tfound = false;\r\n
\t\t\t\tif(p.tmplNames && p.tmplNames.length) {\r\n
\t\t\t\t\tfound = true;\r\n
\t\t\t\t\ttmpl = p.tmplLabel;\r\n
\t\t\t\t\ttmpl += "<select class=\'ui-template\'>";\r\n
\t\t\t\t\ttmpl += "<option value=\'default\'>Default</option>";\r\n
\t\t\t\t\t$.each(p.tmplNames, function(i,n){\r\n
\t\t\t\t\t\ttmpl += "<option value=\'"+i+"\'>"+n+"</option>";\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\ttmpl += "</select>";\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tbt = "<table class=\'EditTable\' style=\'border:0px none;margin-top:5px\' id=\'"+fid+"_2\'><tbody><tr><td colspan=\'2\'><hr class=\'ui-widget-content\' style=\'margin:1px\'/></td></tr><tr><td class=\'EditButton\' style=\'text-align:"+align+"\'>"+bC+tmpl+"</td><td class=\'EditButton\' "+butleft+">"+bQ+bS+"</td></tr></tbody></table>";\r\n
\t\t\t\tfid = $.jgrid.jqID( fid);\r\n
\t\t\t\t$("#"+fid).jqFilter({\r\n
\t\t\t\t\tcolumns : columns,\r\n
\t\t\t\t\tfilter: p.loadDefaults ? defaultFilters : null,\r\n
\t\t\t\t\tshowQuery: p.showQuery,\r\n
\t\t\t\t\terrorcheck : p.errorcheck,\r\n
\t\t\t\t\tsopt: p.sopt,\r\n
\t\t\t\t\tgroupButton : p.multipleGroup,\r\n
\t\t\t\t\truleButtons : p.multipleSearch,\r\n
\t\t\t\t\tafterRedraw : p.afterRedraw,\r\n
\t\t\t\t\t_gridsopt : $.jgrid.search.odata,\r\n
\t\t\t\t\tajaxSelectOptions: $t.p.ajaxSelectOptions,\r\n
\t\t\t\t\tgroupOps: p.groupOps,\r\n
\t\t\t\t\tonChange : function() {\r\n
\t\t\t\t\t\tif(this.p.showQuery) {\r\n
\t\t\t\t\t\t\t$(\'.query\',this).html(this.toUserFriendlyString());\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif ($.isFunction(p.afterChange)) {\r\n
\t\t\t\t\t\t\tp.afterChange.call($t, $("#"+fid), p);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t},\r\n
\t\t\t\t\tdirection : $t.p.direction\r\n
\t\t\t\t});\r\n
\t\t\t\tfil.append( bt );\r\n
\t\t\t\tif(found && p.tmplFilters && p.tmplFilters.length) {\r\n
\t\t\t\t\t$(".ui-template", fil).bind(\'change\', function(){\r\n
\t\t\t\t\t\tvar curtempl = $(this).val();\r\n
\t\t\t\t\t\tif(curtempl=="default") {\r\n
\t\t\t\t\t\t\t$("#"+fid).jqFilter(\'addFilter\', defaultFilters);\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$("#"+fid).jqFilter(\'addFilter\', p.tmplFilters[parseInt(curtempl,10)]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\tif(p.multipleGroup === true) {p.multipleSearch = true;}\r\n
\t\t\t\t$($t).triggerHandler("jqGridFilterInitialize", [$("#"+fid)]);\r\n
\t\t\t\tif($.isFunction(p.onInitializeSearch) ) {\r\n
\t\t\t\t\tp.onInitializeSearch.call($t, $("#"+fid));\r\n
\t\t\t\t}\r\n
\t\t\t\tp.gbox = "#gbox_"+fid;\r\n
\t\t\t\tif (p.layer) {\r\n
\t\t\t\t\t$.jgrid.createModal(IDs ,fil,p,"#gview_"+$.jgrid.jqID($t.p.id),$("#gbox_"+$.jgrid.jqID($t.p.id))[0], "#"+$.jgrid.jqID(p.layer), {position: "relative"});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$.jgrid.createModal(IDs ,fil,p,"#gview_"+$.jgrid.jqID($t.p.id),$("#gbox_"+$.jgrid.jqID($t.p.id))[0]);\r\n
\t\t\t\t}\r\n
\t\t\t\tif (p.searchOnEnter || p.closeOnEscape) {\r\n
\t\t\t\t\t$("#"+$.jgrid.jqID(IDs.themodal)).keydown(function (e) {\r\n
\t\t\t\t\t\tvar $target = $(e.target);\r\n
\t\t\t\t\t\tif (p.searchOnEnter && e.which === 13 && // 13 === $.ui.keyCode.ENTER\r\n
\t\t\t\t\t\t\t\t!$target.hasClass(\'add-group\') && !$target.hasClass(\'add-rule\') &&\r\n
\t\t\t\t\t\t\t\t!$target.hasClass(\'delete-group\') && !$target.hasClass(\'delete-rule\') &&\r\n
\t\t\t\t\t\t\t\t(!$target.hasClass("fm-button") || !$target.is("[id$=_query]"))) {\r\n
\t\t\t\t\t\t\t$("#"+fid+"_search").focus().click();\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif (p.closeOnEscape && e.which === 27) { // 27 === $.ui.keyCode.ESCAPE\r\n
\t\t\t\t\t\t\t$("#"+$.jgrid.jqID(IDs.modalhead)).find(".ui-jqdialog-titlebar-close").focus().click();\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\tif(bQ) {\r\n
\t\t\t\t\t$("#"+fid+"_query").bind(\'click\', function(){\r\n
\t\t\t\t\t\t$(".queryresult", fil).toggle();\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\tif (p.stringResult===undefined) {\r\n
\t\t\t\t\t// to provide backward compatibility, inferring stringResult value from multipleSearch\r\n
\t\t\t\t\tp.stringResult = p.multipleSearch;\r\n
\t\t\t\t}\r\n
\t\t\t\t$("#"+fid+"_search").bind(\'click\', function(){\r\n
\t\t\t\t\tvar fl = $("#"+fid),\r\n
\t\t\t\t\tsdata={}, res ,\r\n
\t\t\t\t\tfilters = fl.jqFilter(\'filterData\');\r\n
\t\t\t\t\tif(p.errorcheck) {\r\n
\t\t\t\t\t\tfl[0].hideError();\r\n
\t\t\t\t\t\tif(!p.showQuery) {fl.jqFilter(\'toSQLString\');}\r\n
\t\t\t\t\t\tif(fl[0].p.error) {\r\n
\t\t\t\t\t\t\tfl[0].showError();\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tif(p.stringResult) {\r\n
\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t// xmlJsonClass or JSON.stringify\r\n
\t\t\t\t\t\t\tres = xmlJsonClass.toJson(filters, \'\', \'\', false);\r\n
\t\t\t\t\t\t} catch (e) {\r\n
\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\tres = JSON.stringify(filters);\r\n
\t\t\t\t\t\t\t} catch (e2) { }\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(typeof(res)==="string") {\r\n
\t\t\t\t\t\t\tsdata[p.sFilter] = res;\r\n
\t\t\t\t\t\t\t$.each([p.sField,p.sValue, p.sOper], function() {sdata[this] = "";});\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tif(p.multipleSearch) {\r\n
\t\t\t\t\t\t\tsdata[p.sFilter] = filters;\r\n
\t\t\t\t\t\t\t$.each([p.sField,p.sValue, p.sOper], function() {sdata[this] = "";});\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tsdata[p.sField] = filters.rules[0].field;\r\n
\t\t\t\t\t\t\tsdata[p.sValue] = filters.rules[0].data;\r\n
\t\t\t\t\t\t\tsdata[p.sOper] = filters.rules[0].op;\r\n
\t\t\t\t\t\t\tsdata[p.sFilter] = "";\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$t.p.search = true;\r\n
\t\t\t\t\t$.extend($t.p.postData,sdata);\r\n
\t\t\t\t\t$($t).triggerHandler("jqGridFilterSearch");\r\n
\t\t\t\t\tif($.isFunction(p.onSearch) ) {\r\n
\t\t\t\t\t\tp.onSearch.call($t);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$($t).trigger("reloadGrid",[{page:1}]);\r\n
\t\t\t\t\tif(p.closeAfterSearch) {\r\n
\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID($t.p.id),jqm:p.jqModal,onClose: p.onClose});\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#"+fid+"_reset").bind(\'click\', function(){\r\n
\t\t\t\t\tvar sdata={},\r\n
\t\t\t\t\tfl = $("#"+fid);\r\n
\t\t\t\t\t$t.p.search = false;\r\n
\t\t\t\t\tif(p.multipleSearch===false) {\r\n
\t\t\t\t\t\tsdata[p.sField] = sdata[p.sValue] = sdata[p.sOper] = "";\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tsdata[p.sFilter] = "";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tfl[0].resetFilter();\r\n
\t\t\t\t\tif(found) {\r\n
\t\t\t\t\t\t$(".ui-template", fil).val("default");\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$.extend($t.p.postData,sdata);\r\n
\t\t\t\t\t$($t).triggerHandler("jqGridFilterReset");\r\n
\t\t\t\t\tif($.isFunction(p.onReset) ) {\r\n
\t\t\t\t\t\tp.onReset.call($t);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$($t).trigger("reloadGrid",[{page:1}]);\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\tshowFilter($("#"+fid));\r\n
\t\t\t\t$(".fm-button:not(.ui-state-disabled)",fil).hover(\r\n
\t\t\t\t\tfunction(){$(this).addClass(\'ui-state-hover\');},\r\n
\t\t\t\t\tfunction(){$(this).removeClass(\'ui-state-hover\');}\r\n
\t\t\t\t);\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\teditGridRow : function(rowid, p){\r\n
\t\tp = $.extend({\r\n
\t\t\ttop : 0,\r\n
\t\t\tleft: 0,\r\n
\t\t\twidth: 300,\r\n
\t\t\theight: \'auto\',\r\n
\t\t\tdataheight: \'auto\',\r\n
\t\t\tmodal: false,\r\n
\t\t\toverlay : 30,\r\n
\t\t\tdrag: true,\r\n
\t\t\tresize: true,\r\n
\t\t\turl: null,\r\n
\t\t\tmtype : "POST",\r\n
\t\t\tclearAfterAdd :true,\r\n
\t\t\tcloseAfterEdit : false,\r\n
\t\t\treloadAfterSubmit : true,\r\n
\t\t\tonInitializeForm: null,\r\n
\t\t\tbeforeInitData: null,\r\n
\t\t\tbeforeShowForm: null,\r\n
\t\t\tafterShowForm: null,\r\n
\t\t\tbeforeSubmit: null,\r\n
\t\t\tafterSubmit: null,\r\n
\t\t\tonclickSubmit: null,\r\n
\t\t\tafterComplete: null,\r\n
\t\t\tonclickPgButtons : null,\r\n
\t\t\tafterclickPgButtons: null,\r\n
\t\t\teditData : {},\r\n
\t\t\trecreateForm : false,\r\n
\t\t\tjqModal : true,\r\n
\t\t\tcloseOnEscape : false,\r\n
\t\t\taddedrow : "first",\r\n
\t\t\ttopinfo : \'\',\r\n
\t\t\tbottominfo: \'\',\r\n
\t\t\tsaveicon : [],\r\n
\t\t\tcloseicon : [],\r\n
\t\t\tsavekey: [false,13],\r\n
\t\t\tnavkeys: [false,38,40],\r\n
\t\t\tcheckOnSubmit : false,\r\n
\t\t\tcheckOnUpdate : false,\r\n
\t\t\t_savedData : {},\r\n
\t\t\tprocessing : false,\r\n
\t\t\tonClose : null,\r\n
\t\t\tajaxEditOptions : {},\r\n
\t\t\tserializeEditData : null,\r\n
\t\t\tviewPagerButtons : true\r\n
\t\t}, $.jgrid.edit, p || {});\r\n
\t\trp_ge[$(this)[0].p.id] = p;\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif (!$t.grid || !rowid) {return;}\r\n
\t\t\tvar gID = $t.p.id,\r\n
\t\t\tfrmgr = "FrmGrid_"+gID, frmtborg = "TblGrid_"+gID, frmtb = "#"+$.jgrid.jqID(frmtborg), \r\n
\t\t\tIDs = {themodal:\'editmod\'+gID,modalhead:\'edithd\'+gID,modalcontent:\'editcnt\'+gID, scrollelm : frmgr},\r\n
\t\t\tonBeforeShow = $.isFunction(rp_ge[$t.p.id].beforeShowForm) ? rp_ge[$t.p.id].beforeShowForm : false,\r\n
\t\t\tonAfterShow = $.isFunction(rp_ge[$t.p.id].afterShowForm) ? rp_ge[$t.p.id].afterShowForm : false,\r\n
\t\t\tonBeforeInit = $.isFunction(rp_ge[$t.p.id].beforeInitData) ? rp_ge[$t.p.id].beforeInitData : false,\r\n
\t\t\tonInitializeForm = $.isFunction(rp_ge[$t.p.id].onInitializeForm) ? rp_ge[$t.p.id].onInitializeForm : false,\r\n
\t\t\tshowFrm = true,\r\n
\t\t\tmaxCols = 1, maxRows=0,\tpostdata, extpost, newData, diff, frmoper;\r\n
\t\t\tfrmgr = $.jgrid.jqID(frmgr);\r\n
\t\t\tif (rowid === "new") {\r\n
\t\t\t\trowid = "_empty";\r\n
\t\t\t\tfrmoper = "add";\r\n
\t\t\t\tp.caption=rp_ge[$t.p.id].addCaption;\r\n
\t\t\t} else {\r\n
\t\t\t\tp.caption=rp_ge[$t.p.id].editCaption;\r\n
\t\t\t\tfrmoper = "edit";\r\n
\t\t\t}\r\n
\t\t\tif(p.recreateForm===true && $("#"+$.jgrid.jqID(IDs.themodal))[0] !== undefined) {\r\n
\t\t\t\t$("#"+$.jgrid.jqID(IDs.themodal)).remove();\r\n
\t\t\t}\r\n
\t\t\tvar closeovrl = true;\r\n
\t\t\tif(p.checkOnUpdate && p.jqModal && !p.modal) {\r\n
\t\t\t\tcloseovrl = false;\r\n
\t\t\t}\r\n
\t\t\tfunction getFormData(){\r\n
\t\t\t\t$(frmtb+" > tbody > tr > td > .FormElement").each(function() {\r\n
\t\t\t\t\tvar celm = $(".customelement", this);\r\n
\t\t\t\t\tif (celm.length) {\r\n
\t\t\t\t\t\tvar  elem = celm[0], nm = $(elem).attr(\'name\');\r\n
\t\t\t\t\t\t$.each($t.p.colModel, function(){\r\n
\t\t\t\t\t\t\tif(this.name === nm && this.editoptions && $.isFunction(this.editoptions.custom_value)) {\r\n
\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\tpostdata[nm] = this.editoptions.custom_value.call($t, $("#"+$.jgrid.jqID(nm),frmtb),\'get\');\r\n
\t\t\t\t\t\t\t\t\tif (postdata[nm] === undefined) {throw "e1";}\r\n
\t\t\t\t\t\t\t\t} catch (e) {\r\n
\t\t\t\t\t\t\t\t\tif (e==="e1") {$.jgrid.info_dialog(jQuery.jgrid.errors.errcap,"function \'custom_value\' "+$.jgrid.edit.msg.novalue,jQuery.jgrid.edit.bClose);}\r\n
\t\t\t\t\t\t\t\t\telse {$.jgrid.info_dialog(jQuery.jgrid.errors.errcap,e.message,jQuery.jgrid.edit.bClose);}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\treturn true;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\tswitch ($(this).get(0).type) {\r\n
\t\t\t\t\t\tcase "checkbox":\r\n
\t\t\t\t\t\t\tif($(this).is(":checked")) {\r\n
\t\t\t\t\t\t\t\tpostdata[this.name]= $(this).val();\r\n
\t\t\t\t\t\t\t}else {\r\n
\t\t\t\t\t\t\t\tvar ofv = $(this).attr("offval");\r\n
\t\t\t\t\t\t\t\tpostdata[this.name]= ofv;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase "select-one":\r\n
\t\t\t\t\t\t\tpostdata[this.name]= $("option:selected",this).val();\r\n
\t\t\t\t\t\t\textpost[this.name]= $("option:selected",this).text();\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase "select-multiple":\r\n
\t\t\t\t\t\t\tpostdata[this.name]= $(this).val();\r\n
\t\t\t\t\t\t\tif(postdata[this.name]) {postdata[this.name] = postdata[this.name].join(",");}\r\n
\t\t\t\t\t\t\telse {postdata[this.name] ="";}\r\n
\t\t\t\t\t\t\tvar selectedText = [];\r\n
\t\t\t\t\t\t\t$("option:selected",this).each(\r\n
\t\t\t\t\t\t\t\tfunction(i,selected){\r\n
\t\t\t\t\t\t\t\t\tselectedText[i] = $(selected).text();\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t);\r\n
\t\t\t\t\t\t\textpost[this.name]= selectedText.join(",");\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase "password":\r\n
\t\t\t\t\t\tcase "text":\r\n
\t\t\t\t\t\tcase "textarea":\r\n
\t\t\t\t\t\tcase "button":\r\n
\t\t\t\t\t\t\tpostdata[this.name] = $(this).val();\r\n
\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif($t.p.autoencode) {postdata[this.name] = $.jgrid.htmlEncode(postdata[this.name]);}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\treturn true;\r\n
\t\t\t}\r\n
\t\t\tfunction createData(rowid,obj,tb,maxcols){\r\n
\t\t\t\tvar nm, hc,trdata, cnt=0,tmp, dc,elc, retpos=[], ind=false,\r\n
\t\t\t\ttdtmpl = "<td class=\'CaptionTD\'>&#160;</td><td class=\'DataTD\'>&#160;</td>", tmpl="", i; //*2\r\n
\t\t\t\tfor (i =1; i<=maxcols;i++) {\r\n
\t\t\t\t\ttmpl += tdtmpl;\r\n
\t\t\t\t}\r\n
\t\t\t\tif(rowid != \'_empty\') {\r\n
\t\t\t\t\tind = $(obj).jqGrid("getInd",rowid);\r\n
\t\t\t\t}\r\n
\t\t\t\t$(obj.p.colModel).each( function(i) {\r\n
\t\t\t\t\tnm = this.name;\r\n
\t\t\t\t\t// hidden fields are included in the form\r\n
\t\t\t\t\tif(this.editrules && this.editrules.edithidden === true) {\r\n
\t\t\t\t\t\thc = false;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\thc = this.hidden === true ? true : false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tdc = hc ? "style=\'display:none\'" : "";\r\n
\t\t\t\t\tif ( nm !== \'cb\' && nm !== \'subgrid\' && this.editable===true && nm !== \'rn\') {\r\n
\t\t\t\t\t\tif(ind === false) {\r\n
\t\t\t\t\t\t\ttmp = "";\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tif(nm == obj.p.ExpandColumn && obj.p.treeGrid === true) {\r\n
\t\t\t\t\t\t\t\ttmp = $("td:eq("+i+")",obj.rows[ind]).text();\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\ttmp =  $.unformat.call(obj, $("td:eq("+i+")",obj.rows[ind]),{rowId:rowid, colModel:this},i);\r\n
\t\t\t\t\t\t\t\t} catch (_) {\r\n
\t\t\t\t\t\t\t\t\ttmp =  (this.edittype && this.edittype == "textarea") ? $("td:eq("+i+")",obj.rows[ind]).text() : $("td:eq("+i+")",obj.rows[ind]).html();\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif(!tmp || tmp == "&nbsp;" || tmp == "&#160;" || (tmp.length==1 && tmp.charCodeAt(0)==160) ) {tmp=\'\';}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tvar opt = $.extend({}, this.editoptions || {} ,{id:nm,name:nm}),\r\n
\t\t\t\t\t\tfrmopt = $.extend({}, {elmprefix:\'\',elmsuffix:\'\',rowabove:false,rowcontent:\'\'}, this.formoptions || {}),\r\n
\t\t\t\t\t\trp = parseInt(frmopt.rowpos,10) || cnt+1,\r\n
\t\t\t\t\t\tcp = parseInt((parseInt(frmopt.colpos,10) || 1)*2,10);\r\n
\t\t\t\t\t\tif(rowid == "_empty" && opt.defaultValue ) {\r\n
\t\t\t\t\t\t\ttmp = $.isFunction(opt.defaultValue) ? opt.defaultValue.call($t) : opt.defaultValue;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(!this.edittype) {this.edittype = "text";}\r\n
\t\t\t\t\t\tif($t.p.autoencode) {tmp = $.jgrid.htmlDecode(tmp);}\r\n
\t\t\t\t\t\telc = $.jgrid.createEl.call($t,this.edittype,opt,tmp,false,$.extend({},$.jgrid.ajaxOptions,obj.p.ajaxSelectOptions || {}));\r\n
\t\t\t\t\t\tif(tmp === "" && this.edittype == "checkbox") {tmp = $(elc).attr("offval");}\r\n
\t\t\t\t\t\tif(tmp === "" && this.edittype == "select") {tmp = $("option:eq(0)",elc).text();}\r\n
\t\t\t\t\t\tif(rp_ge[$t.p.id].checkOnSubmit || rp_ge[$t.p.id].checkOnUpdate) {rp_ge[$t.p.id]._savedData[nm] = tmp;}\r\n
\t\t\t\t\t\t$(elc).addClass("FormElement");\r\n
\t\t\t\t\t\tif(this.edittype == \'text\' || this.edittype == \'textarea\') {\r\n
\t\t\t\t\t\t\t$(elc).addClass("ui-widget-content ui-corner-all");\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ttrdata = $(tb).find("tr[rowpos="+rp+"]");\r\n
\t\t\t\t\t\tif(frmopt.rowabove) {\r\n
\t\t\t\t\t\t\tvar newdata = $("<tr><td class=\'contentinfo\' colspan=\'"+(maxcols*2)+"\'>"+frmopt.rowcontent+"</td></tr>");\r\n
\t\t\t\t\t\t\t$(tb).append(newdata);\r\n
\t\t\t\t\t\t\tnewdata[0].rp = rp;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif ( trdata.length===0 ) {\r\n
\t\t\t\t\t\t\ttrdata = $("<tr "+dc+" rowpos=\'"+rp+"\'></tr>").addClass("FormData").attr("id","tr_"+nm);\r\n
\t\t\t\t\t\t\t$(trdata).append(tmpl);\r\n
\t\t\t\t\t\t\t$(tb).append(trdata);\r\n
\t\t\t\t\t\t\ttrdata[0].rp = rp;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t$("td:eq("+(cp-2)+")",trdata[0]).html( typeof frmopt.label === \'undefined\' ? obj.p.colNames[i]: frmopt.label);\r\n
\t\t\t\t\t\t$("td:eq("+(cp-1)+")",trdata[0]).append(frmopt.elmprefix).append(elc).append(frmopt.elmsuffix);\r\n
\t\t\t\t\t\tretpos[cnt] = i;\r\n
\t\t\t\t\t\tcnt++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tif( cnt > 0) {\r\n
\t\t\t\t\tvar idrow = $("<tr class=\'FormData\' style=\'display:none\'><td class=\'CaptionTD\'></td><td colspan=\'"+ (maxcols*2-1)+"\' class=\'DataTD\'><input class=\'FormElement\' id=\'id_g\' type=\'text\' name=\'"+obj.p.id+"_id\' value=\'"+rowid+"\'/></td></tr>");\r\n
\t\t\t\t\tidrow[0].rp = cnt+999;\r\n
\t\t\t\t\t$(tb).append(idrow);\r\n
\t\t\t\t\tif(rp_ge[$t.p.id].checkOnSubmit || rp_ge[$t.p.id].checkOnUpdate) {rp_ge[$t.p.id]._savedData[obj.p.id+"_id"] = rowid;}\r\n
\t\t\t\t}\r\n
\t\t\t\treturn retpos;\r\n
\t\t\t}\r\n
\t\t\tfunction fillData(rowid,obj,fmid){\r\n
\t\t\t\tvar nm,cnt=0,tmp, fld,opt,vl,vlc;\r\n
\t\t\t\tif(rp_ge[$t.p.id].checkOnSubmit || rp_ge[$t.p.id].checkOnUpdate) {rp_ge[$t.p.id]._savedData = {};rp_ge[$t.p.id]._savedData[obj.p.id+"_id"]=rowid;}\r\n
\t\t\t\tvar cm = obj.p.colModel;\r\n
\t\t\t\tif(rowid == \'_empty\') {\r\n
\t\t\t\t\t$(cm).each(function(){\r\n
\t\t\t\t\t\tnm = this.name;\r\n
\t\t\t\t\t\topt = $.extend({}, this.editoptions || {} );\r\n
\t\t\t\t\t\tfld = $("#"+$.jgrid.jqID(nm),"#"+fmid);\r\n
\t\t\t\t\t\tif(fld && fld.length && fld[0] !== null) {\r\n
\t\t\t\t\t\t\tvl = "";\r\n
\t\t\t\t\t\t\tif(opt.defaultValue ) {\r\n
\t\t\t\t\t\t\t\tvl = $.isFunction(opt.defaultValue) ? opt.defaultValue.call($t) : opt.defaultValue;\r\n
\t\t\t\t\t\t\t\tif(fld[0].type==\'checkbox\') {\r\n
\t\t\t\t\t\t\t\t\tvlc = vl.toLowerCase();\r\n
\t\t\t\t\t\t\t\t\tif(vlc.search(/(false|0|no|off|undefined)/i)<0 && vlc!=="") {\r\n
\t\t\t\t\t\t\t\t\t\tfld[0].checked = true;\r\n
\t\t\t\t\t\t\t\t\t\tfld[0].defaultChecked = true;\r\n
\t\t\t\t\t\t\t\t\t\tfld[0].value = vl;\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\tfld[0].checked = false;\r\n
\t\t\t\t\t\t\t\t\t\tfld[0].defaultChecked = false;\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t} else {fld.val(vl);}\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tif( fld[0].type==\'checkbox\' ) {\r\n
\t\t\t\t\t\t\t\t\tfld[0].checked = false;\r\n
\t\t\t\t\t\t\t\t\tfld[0].defaultChecked = false;\r\n
\t\t\t\t\t\t\t\t\tvl = $(fld).attr("offval");\r\n
\t\t\t\t\t\t\t\t} else if (fld[0].type && fld[0].type.substr(0,6)==\'select\') {\r\n
\t\t\t\t\t\t\t\t\tfld[0].selectedIndex = 0;\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\tfld.val(vl);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(rp_ge[$t.p.id].checkOnSubmit===true || rp_ge[$t.p.id].checkOnUpdate) {rp_ge[$t.p.id]._savedData[nm] = vl;}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\t$("#id_g","#"+fmid).val(rowid);\r\n
\t\t\t\t\treturn;\r\n
\t\t\t\t}\r\n
\t\t\t\tvar tre = $(obj).jqGrid("getInd",rowid,true);\r\n
\t\t\t\tif(!tre) {return;}\r\n
\t\t\t\t$(\'td[role="gridcell"]\',tre).each( function(i) {\r\n
\t\t\t\t\tnm = cm[i].name;\r\n
\t\t\t\t\t// hidden fields are included in the form\r\n
\t\t\t\t\tif ( nm !== \'cb\' && nm !== \'subgrid\' && nm !== \'rn\' && cm[i].editable===true) {\r\n
\t\t\t\t\t\tif(nm == obj.p.ExpandColumn && obj.p.treeGrid === true) {\r\n
\t\t\t\t\t\t\ttmp = $(this).text();\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\ttmp =  $.unformat.call(obj, $(this),{rowId:rowid, colModel:cm[i]},i);\r\n
\t\t\t\t\t\t\t} catch (_) {\r\n
\t\t\t\t\t\t\t\ttmp = cm[i].edittype=="textarea" ? $(this).text() : $(this).html();\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif($t.p.autoencode) {tmp = $.jgrid.htmlDecode(tmp);}\r\n
\t\t\t\t\t\tif(rp_ge[$t.p.id].checkOnSubmit===true || rp_ge[$t.p.id].checkOnUpdate) {rp_ge[$t.p.id]._savedData[nm] = tmp;}\r\n
\t\t\t\t\t\tnm = $.jgrid.jqID(nm);\r\n
\t\t\t\t\t\tswitch (cm[i].edittype) {\r\n
\t\t\t\t\t\t\tcase "password":\r\n
\t\t\t\t\t\t\tcase "text":\r\n
\t\t\t\t\t\t\tcase "button" :\r\n
\t\t\t\t\t\t\tcase "image":\r\n
\t\t\t\t\t\t\tcase "textarea":\r\n
\t\t\t\t\t\t\t\tif(tmp == "&nbsp;" || tmp == "&#160;" || (tmp.length==1 && tmp.charCodeAt(0)==160) ) {tmp=\'\';}\r\n
\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid).val(tmp);\r\n
\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\tcase "select":\r\n
\t\t\t\t\t\t\t\tvar opv = tmp.split(",");\r\n
\t\t\t\t\t\t\t\topv = $.map(opv,function(n){return $.trim(n);});\r\n
\t\t\t\t\t\t\t\t$("#"+nm+" option","#"+fmid).each(function(){\r\n
\t\t\t\t\t\t\t\t\tif (!cm[i].editoptions.multiple && ($.trim(tmp) == $.trim($(this).text()) || opv[0] == $.trim($(this).text()) || opv[0] == $.trim($(this).val())) ){\r\n
\t\t\t\t\t\t\t\t\t\tthis.selected= true;\r\n
\t\t\t\t\t\t\t\t\t} else if (cm[i].editoptions.multiple){\r\n
\t\t\t\t\t\t\t\t\t\tif(  $.inArray($.trim($(this).text()), opv ) > -1 || $.inArray($.trim($(this).val()), opv ) > -1  ){\r\n
\t\t\t\t\t\t\t\t\t\t\tthis.selected = true;\r\n
\t\t\t\t\t\t\t\t\t\t}else{\r\n
\t\t\t\t\t\t\t\t\t\t\tthis.selected = false;\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\tthis.selected = false;\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\tcase "checkbox":\r\n
\t\t\t\t\t\t\t\ttmp = tmp+"";\r\n
\t\t\t\t\t\t\t\tif(cm[i].editoptions && cm[i].editoptions.value) {\r\n
\t\t\t\t\t\t\t\t\tvar cb = cm[i].editoptions.value.split(":");\r\n
\t\t\t\t\t\t\t\t\tif(cb[0] == tmp) {\r\n
\t\t\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid)[$t.p.useProp ? \'prop\': \'attr\']("checked",true);\r\n
\t\t\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid)[$t.p.useProp ? \'prop\': \'attr\']("defaultChecked",true); //ie\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid)[$t.p.useProp ? \'prop\': \'attr\']("checked", false);\r\n
\t\t\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid)[$t.p.useProp ? \'prop\': \'attr\']("defaultChecked", false); //ie\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\ttmp = tmp.toLowerCase();\r\n
\t\t\t\t\t\t\t\t\tif(tmp.search(/(false|0|no|off|undefined)/i)<0 && tmp!=="") {\r\n
\t\t\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid)[$t.p.useProp ? \'prop\': \'attr\']("checked",true);\r\n
\t\t\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid)[$t.p.useProp ? \'prop\': \'attr\']("defaultChecked",true); //ie\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid)[$t.p.useProp ? \'prop\': \'attr\']("checked", false);\r\n
\t\t\t\t\t\t\t\t\t\t$("#"+nm,"#"+fmid)[$t.p.useProp ? \'prop\': \'attr\']("defaultChecked", false); //ie\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\tcase \'custom\' :\r\n
\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\tif(cm[i].editoptions && $.isFunction(cm[i].editoptions.custom_value)) {\r\n
\t\t\t\t\t\t\t\t\t\tcm[i].editoptions.custom_value.call($t, $("#"+nm,"#"+fmid),\'set\',tmp);\r\n
\t\t\t\t\t\t\t\t\t} else {throw "e1";}\r\n
\t\t\t\t\t\t\t\t} catch (e) {\r\n
\t\t\t\t\t\t\t\t\tif (e=="e1") {$.jgrid.info_dialog(jQuery.jgrid.errors.errcap,"function \'custom_value\' "+$.jgrid.edit.msg.nodefined,jQuery.jgrid.edit.bClose);}\r\n
\t\t\t\t\t\t\t\t\telse {$.jgrid.info_dialog(jQuery.jgrid.errors.errcap,e.message,jQuery.jgrid.edit.bClose);}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tcnt++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tif(cnt>0) {$("#id_g",frmtb).val(rowid);}\r\n
\t\t\t}\r\n
\t\t\tfunction setNulls() {\r\n
\t\t\t\t$.each($t.p.colModel, function(i,n){\r\n
\t\t\t\t\tif(n.editoptions && n.editoptions.NullIfEmpty === true) {\r\n
\t\t\t\t\t\tif(postdata.hasOwnProperty(n.name) && postdata[n.name] === "") {\r\n
\t\t\t\t\t\t\tpostdata[n.name] = \'null\';\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tfunction postIt() {\r\n
\t\t\t\tvar copydata, ret=[true,"",""], onCS = {}, opers = $t.p.prmNames, idname, oper, key, selr, i;\r\n
\t\t\t\t\r\n
\t\t\t\tvar retvals = $($t).triggerHandler("jqGridAddEditBeforeCheckValues", [$("#"+frmgr), frmoper]);\r\n
\t\t\t\tif(retvals && typeof(retvals) === \'object\') {postdata = retvals;}\r\n
\t\t\t\t\r\n
\t\t\t\tif($.isFunction(rp_ge[$t.p.id].beforeCheckValues)) {\r\n
\t\t\t\t\tretvals = rp_ge[$t.p.id].beforeCheckValues.call($t, postdata,$("#"+frmgr),postdata[$t.p.id+"_id"] == "_empty" ? opers.addoper : opers.editoper);\r\n
\t\t\t\t\tif(retvals && typeof(retvals) === \'object\') {postdata = retvals;}\r\n
\t\t\t\t}\r\n
\t\t\t\tfor( key in postdata ){\r\n
\t\t\t\t\tif(postdata.hasOwnProperty(key)) {\r\n
\t\t\t\t\t\tret = $.jgrid.checkValues.call($t,postdata[key],key,$t);\r\n
\t\t\t\t\t\tif(ret[0] === false) {break;}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tsetNulls();\r\n
\t\t\t\tif(ret[0]) {\r\n
\t\t\t\t\tonCS = $($t).triggerHandler("jqGridAddEditClickSubmit", [rp_ge[$t.p.id], postdata, frmoper]);\r\n
\t\t\t\t\tif( onCS === undefined && $.isFunction( rp_ge[$t.p.id].onclickSubmit)) { \r\n
\t\t\t\t\t\tonCS = rp_ge[$t.p.id].onclickSubmit.call($t, rp_ge[$t.p.id], postdata) || {}; \r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tret = $($t).triggerHandler("jqGridAddEditBeforeSubmit", [postdata, $("#"+frmgr), frmoper]);\r\n
\t\t\t\t\tif(ret === undefined) {\r\n
\t\t\t\t\t\tret = [true,"",""];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif( ret[0] && $.isFunction(rp_ge[$t.p.id].beforeSubmit))  {\r\n
\t\t\t\t\t\tret = rp_ge[$t.p.id].beforeSubmit.call($t,postdata,$("#"+frmgr));\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\r\n
\t\t\t\tif(ret[0] && !rp_ge[$t.p.id].processing) {\r\n
\t\t\t\t\trp_ge[$t.p.id].processing = true;\r\n
\t\t\t\t\t$("#sData", frmtb+"_2").addClass(\'ui-state-active\');\r\n
\t\t\t\t\toper = opers.oper;\r\n
\t\t\t\t\tidname = opers.id;\r\n
\t\t\t\t\t// we add to pos data array the action - the name is oper\r\n
\t\t\t\t\tpostdata[oper] = ($.trim(postdata[$t.p.id+"_id"]) == "_empty") ? opers.addoper : opers.editoper;\r\n
\t\t\t\t\tif(postdata[oper] != opers.addoper) {\r\n
\t\t\t\t\t\tpostdata[idname] = postdata[$t.p.id+"_id"];\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t// check to see if we have allredy this field in the form and if yes lieve it\r\n
\t\t\t\t\t\tif( postdata[idname] === undefined ) {postdata[idname] = postdata[$t.p.id+"_id"];}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tdelete postdata[$t.p.id+"_id"];\r\n
\t\t\t\t\tpostdata = $.extend(postdata,rp_ge[$t.p.id].editData,onCS);\r\n
\t\t\t\t\tif($t.p.treeGrid === true)  {\r\n
\t\t\t\t\t\tif(postdata[oper] == opers.addoper) {\r\n
\t\t\t\t\t\tselr = $($t).jqGrid("getGridParam", \'selrow\');\r\n
\t\t\t\t\t\t\tvar tr_par_id = $t.p.treeGridModel == \'adjacency\' ? $t.p.treeReader.parent_id_field : \'parent_id\';\r\n
\t\t\t\t\t\t\tpostdata[tr_par_id] = selr;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tfor(i in $t.p.treeReader){\r\n
\t\t\t\t\t\t\tif($t.p.treeReader.hasOwnProperty(i)) {\r\n
\t\t\t\t\t\t\t\tvar itm = $t.p.treeReader[i];\r\n
\t\t\t\t\t\t\t\tif(postdata.hasOwnProperty(itm)) {\r\n
\t\t\t\t\t\t\t\t\tif(postdata[oper] == opers.addoper && i === \'parent_id_field\') {continue;}\r\n
\t\t\t\t\t\t\t\t\tdelete postdata[itm];\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t\r\n
\t\t\t\t\tpostdata[idname] = $.jgrid.stripPref($t.p.idPrefix, postdata[idname]);\r\n
\t\t\t\t\tvar ajaxOptions = $.extend({\r\n
\t\t\t\t\t\turl: rp_ge[$t.p.id].url ? rp_ge[$t.p.id].url : $($t).jqGrid(\'getGridParam\',\'editurl\'),\r\n
\t\t\t\t\t\ttype: rp_ge[$t.p.id].mtype,\r\n
\t\t\t\t\t\tdata: $.isFunction(rp_ge[$t.p.id].serializeEditData) ? rp_ge[$t.p.id].serializeEditData.call($t,postdata) :  postdata,\r\n
\t\t\t\t\t\tcomplete:function(data,Status){\r\n
\t\t\t\t\t\t\tpostdata[idname] = $t.p.idPrefix + postdata[idname];\r\n
\t\t\t\t\t\t\tif(Status != "success") {\r\n
\t\t\t\t\t\t\t\tret[0] = false;\r\n
\t\t\t\t\t\t\t\tret[1] = $($t).triggerHandler("jqGridAddEditErrorTextFormat", [data, frmoper]);\r\n
\t\t\t\t\t\t\t\tif ($.isFunction(rp_ge[$t.p.id].errorTextFormat)) {\r\n
\t\t\t\t\t\t\t\t\tret[1] = rp_ge[$t.p.id].errorTextFormat.call($t, data);\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\tret[1] = Status + " Status: \'" + data.statusText + "\'. Error code: " + data.status;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t// data is posted successful\r\n
\t\t\t\t\t\t\t\t// execute aftersubmit with the returned data from server\r\n
\t\t\t\t\t\t\t\tret = $($t).triggerHandler("jqGridAddEditAfterSubmit", [data, postdata, frmoper]);\r\n
\t\t\t\t\t\t\t\tif(ret === undefined) {\r\n
\t\t\t\t\t\t\t\t\tret = [true,"",""];\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif( ret[0] && $.isFunction(rp_ge[$t.p.id].afterSubmit) ) {\r\n
\t\t\t\t\t\t\t\t\tret = rp_ge[$t.p.id].afterSubmit.call($t, data,postdata);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(ret[0] === false) {\r\n
\t\t\t\t\t\t\t\t$("#FormError>td",frmtb).html(ret[1]);\r\n
\t\t\t\t\t\t\t\t$("#FormError",frmtb).show();\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t// remove some values if formattaer select or checkbox\r\n
\t\t\t\t\t\t\t\t$.each($t.p.colModel, function(){\r\n
\t\t\t\t\t\t\t\t\tif(extpost[this.name] && this.formatter && this.formatter==\'select\') {\r\n
\t\t\t\t\t\t\t\t\t\ttry {delete extpost[this.name];} catch (e) {}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\tpostdata = $.extend(postdata,extpost);\r\n
\t\t\t\t\t\t\t\tif($t.p.autoencode) {\r\n
\t\t\t\t\t\t\t\t\t$.each(postdata,function(n,v){\r\n
\t\t\t\t\t\t\t\t\t\tpostdata[n] = $.jgrid.htmlDecode(v);\r\n
\t\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t//rp_ge[$t.p.id].reloadAfterSubmit = rp_ge[$t.p.id].reloadAfterSubmit && $t.p.datatype != "local";\r\n
\t\t\t\t\t\t\t\t// the action is add\r\n
\t\t\t\t\t\t\t\tif(postdata[oper] == opers.addoper ) {\r\n
\t\t\t\t\t\t\t\t\t//id processing\r\n
\t\t\t\t\t\t\t\t\t// user not set the id ret[2]\r\n
\t\t\t\t\t\t\t\t\tif(!ret[2]) {ret[2] = $.jgrid.randId();}\r\n
\t\t\t\t\t\t\t\t\tpostdata[idname] = ret[2];\r\n
\t\t\t\t\t\t\t\t\tif(rp_ge[$t.p.id].closeAfterAdd) {\r\n
\t\t\t\t\t\t\t\t\t\tif(rp_ge[$t.p.id].reloadAfterSubmit) {$($t).trigger("reloadGrid");}\r\n
\t\t\t\t\t\t\t\t\t\telse {\r\n
\t\t\t\t\t\t\t\t\t\t\tif($t.p.treeGrid === true){\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("addChildNode",ret[2],selr,postdata );\r\n
\t\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("addRowData",ret[2],postdata,p.addedrow);\r\n
\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("setSelection",ret[2]);\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal,onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\t\t\t\t\t} else if (rp_ge[$t.p.id].clearAfterAdd) {\r\n
\t\t\t\t\t\t\t\t\t\tif(rp_ge[$t.p.id].reloadAfterSubmit) {$($t).trigger("reloadGrid");}\r\n
\t\t\t\t\t\t\t\t\t\telse {\r\n
\t\t\t\t\t\t\t\t\t\t\tif($t.p.treeGrid === true){\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("addChildNode",ret[2],selr,postdata );\r\n
\t\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("addRowData",ret[2],postdata,p.addedrow);\r\n
\t\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\tfillData("_empty",$t,frmgr);\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\tif(rp_ge[$t.p.id].reloadAfterSubmit) {$($t).trigger("reloadGrid");}\r\n
\t\t\t\t\t\t\t\t\t\telse {\r\n
\t\t\t\t\t\t\t\t\t\t\tif($t.p.treeGrid === true){\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("addChildNode",ret[2],selr,postdata );\r\n
\t\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("addRowData",ret[2],postdata,p.addedrow);\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t// the action is update\r\n
\t\t\t\t\t\t\t\t\tif(rp_ge[$t.p.id].reloadAfterSubmit) {\r\n
\t\t\t\t\t\t\t\t\t\t$($t).trigger("reloadGrid");\r\n
\t\t\t\t\t\t\t\t\t\tif( !rp_ge[$t.p.id].closeAfterEdit ) {setTimeout(function(){$($t).jqGrid("setSelection",postdata[idname]);},1000);}\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\tif($t.p.treeGrid === true) {\r\n
\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("setTreeRow", postdata[idname],postdata);\r\n
\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("setRowData", postdata[idname],postdata);\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\tif(rp_ge[$t.p.id].closeAfterEdit) {$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal,onClose: rp_ge[$t.p.id].onClose});}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif($.isFunction(rp_ge[$t.p.id].afterComplete)) {\r\n
\t\t\t\t\t\t\t\t\tcopydata = data;\r\n
\t\t\t\t\t\t\t\t\tsetTimeout(function(){\r\n
\t\t\t\t\t\t\t\t\t\t$($t).triggerHandler("jqGridAddEditAfterComplete", [copydata, postdata, $("#"+frmgr), frmoper]);\r\n
\t\t\t\t\t\t\t\t\t\trp_ge[$t.p.id].afterComplete.call($t, copydata, postdata, $("#"+frmgr));\r\n
\t\t\t\t\t\t\t\t\t\tcopydata=null;\r\n
\t\t\t\t\t\t\t\t\t},500);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(rp_ge[$t.p.id].checkOnSubmit || rp_ge[$t.p.id].checkOnUpdate) {\r\n
\t\t\t\t\t\t\t\t$("#"+frmgr).data("disabled",false);\r\n
\t\t\t\t\t\t\t\tif(rp_ge[$t.p.id]._savedData[$t.p.id+"_id"] !="_empty"){\r\n
\t\t\t\t\t\t\t\t\tfor(var key in rp_ge[$t.p.id]._savedData) {\r\n
\t\t\t\t\t\t\t\t\t\tif(postdata[key]) {\r\n
\t\t\t\t\t\t\t\t\t\t\trp_ge[$t.p.id]._savedData[key] = postdata[key];\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\trp_ge[$t.p.id].processing=false;\r\n
\t\t\t\t\t\t\t$("#sData", frmtb+"_2").removeClass(\'ui-state-active\');\r\n
\t\t\t\t\t\t\ttry{$(\':input:visible\',"#"+frmgr)[0].focus();} catch (e){}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}, $.jgrid.ajaxOptions, rp_ge[$t.p.id].ajaxEditOptions );\r\n
\r\n
\t\t\t\t\tif (!ajaxOptions.url && !rp_ge[$t.p.id].useDataProxy) {\r\n
\t\t\t\t\t\tif ($.isFunction($t.p.dataProxy)) {\r\n
\t\t\t\t\t\t\trp_ge[$t.p.id].useDataProxy = true;\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tret[0]=false;ret[1] += " "+$.jgrid.errors.nourl;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (ret[0]) {\r\n
\t\t\t\t\t\tif (rp_ge[$t.p.id].useDataProxy) {\r\n
\t\t\t\t\t\t\tvar dpret = $t.p.dataProxy.call($t, ajaxOptions, "set_"+$t.p.id); \r\n
\t\t\t\t\t\t\tif(typeof(dpret) == "undefined") {\r\n
\t\t\t\t\t\t\t\tdpret = [true, ""];\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(dpret[0] === false ) {\r\n
\t\t\t\t\t\t\t\tret[0] = false;\r\n
\t\t\t\t\t\t\t\tret[1] = dpret[1] || "Error deleting the selected row!" ;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tif(ajaxOptions.data.oper == opers.addoper && rp_ge[$t.p.id].closeAfterAdd ) {\r\n
\t\t\t\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif(ajaxOptions.data.oper == opers.editoper && rp_ge[$t.p.id].closeAfterEdit ) {\r\n
\t\t\t\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$.ajax(ajaxOptions); \r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ret[0] === false) {\r\n
\t\t\t\t\t$("#FormError>td",frmtb).html(ret[1]);\r\n
\t\t\t\t\t$("#FormError",frmtb).show();\r\n
\t\t\t\t\t// return;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tfunction compareData(nObj, oObj ) {\r\n
\t\t\t\tvar ret = false,key;\r\n
\t\t\t\tfor (key in nObj) {\r\n
\t\t\t\t\tif(nObj[key] != oObj[key]) {\r\n
\t\t\t\t\t\tret = true;\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\treturn ret;\r\n
\t\t\t}\r\n
\t\t\tfunction checkUpdates () {\r\n
\t\t\t\tvar stat = true;\r\n
\t\t\t\t$("#FormError",frmtb).hide();\r\n
\t\t\t\tif(rp_ge[$t.p.id].checkOnUpdate) {\r\n
\t\t\t\t\tpostdata = {};extpost={};\r\n
\t\t\t\t\tgetFormData();\r\n
\t\t\t\t\tnewData = $.extend({},postdata,extpost);\r\n
\t\t\t\t\tdiff = compareData(newData,rp_ge[$t.p.id]._savedData);\r\n
\t\t\t\t\tif(diff) {\r\n
\t\t\t\t\t\t$("#"+frmgr).data("disabled",true);\r\n
\t\t\t\t\t\t$(".confirm","#"+IDs.themodal).show();\r\n
\t\t\t\t\t\tstat = false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\treturn stat;\r\n
\t\t\t}\r\n
\t\t\tfunction restoreInline()\r\n
\t\t\t{\r\n
\t\t\t\tif (rowid !== "_empty" && typeof($t.p.savedRow) !== "undefined" && $t.p.savedRow.length > 0 && $.isFunction($.fn.jqGrid.restoreRow)) {\r\n
\t\t\t\t\tfor (var i=0;i<$t.p.savedRow.length;i++) {\r\n
\t\t\t\t\t\tif ($t.p.savedRow[i].id == rowid) {\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'restoreRow\',rowid);\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tfunction updateNav(cr,totr){\r\n
\t\t\t\tif (cr===0) {$("#pData",frmtb+"_2").addClass(\'ui-state-disabled\');} else {$("#pData",frmtb+"_2").removeClass(\'ui-state-disabled\');}\r\n
\t\t\t\tif (cr==totr) {$("#nData",frmtb+"_2").addClass(\'ui-state-disabled\');} else {$("#nData",frmtb+"_2").removeClass(\'ui-state-disabled\');}\r\n
\t\t\t}\r\n
\t\t\tfunction getCurrPos() {\r\n
\t\t\t\tvar rowsInGrid = $($t).jqGrid("getDataIDs"),\r\n
\t\t\t\tselrow = $("#id_g",frmtb).val(),\r\n
\t\t\t\tpos = $.inArray(selrow,rowsInGrid);\r\n
\t\t\t\treturn [pos,rowsInGrid];\r\n
\t\t\t}\r\n
\r\n
\t\t\tif ( $("#"+$.jgrid.jqID(IDs.themodal))[0] !== undefined ) {\r\n
\t\t\t\tshowFrm = $($t).triggerHandler("jqGridAddEditBeforeInitData", [$("#"+$.jgrid.jqID(frmgr)), frmoper]);\r\n
\t\t\t\tif(typeof(showFrm) == "undefined") {\r\n
\t\t\t\t\tshowFrm = true;\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm && onBeforeInit) {\r\n
\t\t\t\t\tshowFrm = onBeforeInit.call($t,$("#"+frmgr));\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm === false) {return;}\r\n
\t\t\t\trestoreInline();\r\n
\t\t\t\t$(".ui-jqdialog-title","#"+$.jgrid.jqID(IDs.modalhead)).html(p.caption);\r\n
\t\t\t\t$("#FormError",frmtb).hide();\r\n
\t\t\t\tif(rp_ge[$t.p.id].topinfo) {\r\n
\t\t\t\t\t$(".topinfo",frmtb).html(rp_ge[$t.p.id].topinfo);\r\n
\t\t\t\t\t$(".tinfo",frmtb).show();\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$(".tinfo",frmtb).hide();\r\n
\t\t\t\t}\r\n
\t\t\t\tif(rp_ge[$t.p.id].bottominfo) {\r\n
\t\t\t\t\t$(".bottominfo",frmtb+"_2").html(rp_ge[$t.p.id].bottominfo);\r\n
\t\t\t\t\t$(".binfo",frmtb+"_2").show();\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$(".binfo",frmtb+"_2").hide();\r\n
\t\t\t\t}\r\n
\t\t\t\t// filldata\r\n
\t\t\t\tfillData(rowid,$t,frmgr);\r\n
\t\t\t\t///\r\n
\t\t\t\tif(rowid=="_empty" || !rp_ge[$t.p.id].viewPagerButtons) {\r\n
\t\t\t\t\t$("#pData, #nData",frmtb+"_2").hide();\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$("#pData, #nData",frmtb+"_2").show();\r\n
\t\t\t\t}\r\n
\t\t\t\tif(rp_ge[$t.p.id].processing===true) {\r\n
\t\t\t\t\trp_ge[$t.p.id].processing=false;\r\n
\t\t\t\t\t$("#sData", frmtb+"_2").removeClass(\'ui-state-active\');\r\n
\t\t\t\t}\r\n
\t\t\t\tif($("#"+frmgr).data("disabled")===true) {\r\n
\t\t\t\t\t$(".confirm","#"+$.jgrid.jqID(IDs.themodal)).hide();\r\n
\t\t\t\t\t$("#"+frmgr).data("disabled",false);\r\n
\t\t\t\t}\r\n
\t\t\t\t$($t).triggerHandler("jqGridAddEditBeforeShowForm", [$("#"+frmgr), frmoper]);\r\n
\t\t\t\tif(onBeforeShow) { onBeforeShow.call($t, $("#"+frmgr)); }\r\n
\t\t\t\t$("#"+$.jgrid.jqID(IDs.themodal)).data("onClose",rp_ge[$t.p.id].onClose);\r\n
\t\t\t\t$.jgrid.viewModal("#"+$.jgrid.jqID(IDs.themodal),{gbox:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, jqM: false, overlay: p.overlay, modal:p.modal});\r\n
\t\t\t\tif(!closeovrl) {\r\n
\t\t\t\t\t$(".jqmOverlay").click(function(){\r\n
\t\t\t\t\t\tif(!checkUpdates()) {return false;}\r\n
\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\t$($t).triggerHandler("jqGridAddEditAfterShowForm", [$("#"+frmgr), frmoper]);\r\n
\t\t\t\tif(onAfterShow) { onAfterShow.call($t, $("#"+frmgr)); }\r\n
\t\t\t} else {\r\n
\t\t\t\tvar dh = isNaN(p.dataheight) ? p.dataheight : p.dataheight+"px",\r\n
\t\t\t\tfrm = $("<form name=\'FormPost\' id=\'"+frmgr+"\' class=\'FormGrid\' onSubmit=\'return false;\' style=\'width:100%;overflow:auto;position:relative;height:"+dh+";\'></form>").data("disabled",false),\r\n
\t\t\t\ttbl = $("<table id=\'"+frmtborg+"\' class=\'EditTable\' cellspacing=\'0\' cellpadding=\'0\' border=\'0\'><tbody></tbody></table>");\r\n
\t\t\t\tshowFrm = $($t).triggerHandler("jqGridAddEditBeforeInitData", [$("#"+frmgr), frmoper]);\r\n
\t\t\t\tif(typeof(showFrm) == "undefined") {\r\n
\t\t\t\t\tshowFrm = true;\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm && onBeforeInit) {\r\n
\t\t\t\t\tshowFrm = onBeforeInit.call($t,$("#"+frmgr));\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm === false) {return;}\r\n
\t\t\t\trestoreInline();\r\n
\t\t\t\t$($t.p.colModel).each( function() {\r\n
\t\t\t\t\tvar fmto = this.formoptions;\r\n
\t\t\t\t\tmaxCols = Math.max(maxCols, fmto ? fmto.colpos || 0 : 0 );\r\n
\t\t\t\t\tmaxRows = Math.max(maxRows, fmto ? fmto.rowpos || 0 : 0 );\r\n
\t\t\t\t});\r\n
\t\t\t\t$(frm).append(tbl);\r\n
\t\t\t\tvar flr = $("<tr id=\'FormError\' style=\'display:none\'><td class=\'ui-state-error\' colspan=\'"+(maxCols*2)+"\'></td></tr>");\r\n
\t\t\t\tflr[0].rp = 0;\r\n
\t\t\t\t$(tbl).append(flr);\r\n
\t\t\t\t//topinfo\r\n
\t\t\t\tflr = $("<tr style=\'display:none\' class=\'tinfo\'><td class=\'topinfo\' colspan=\'"+(maxCols*2)+"\'>"+rp_ge[$t.p.id].topinfo+"</td></tr>");\r\n
\t\t\t\tflr[0].rp = 0;\r\n
\t\t\t\t$(tbl).append(flr);\r\n
\t\t\t\t// set the id.\r\n
\t\t\t\t// use carefull only to change here colproperties.\r\n
\t\t\t\t// create data\r\n
\t\t\t\tvar rtlb = $t.p.direction == "rtl" ? true :false,\r\n
\t\t\t\tbp = rtlb ? "nData" : "pData",\r\n
\t\t\t\tbn = rtlb ? "pData" : "nData";\r\n
\t\t\t\tcreateData(rowid,$t,tbl,maxCols);\r\n
\t\t\t\t// buttons at footer\r\n
\t\t\t\tvar bP = "<a href=\'javascript:void(0)\' id=\'"+bp+"\' class=\'fm-button ui-state-default ui-corner-left\'><span class=\'ui-icon ui-icon-triangle-1-w\'></span></a>",\r\n
\t\t\t\tbN = "<a href=\'javascript:void(0)\' id=\'"+bn+"\' class=\'fm-button ui-state-default ui-corner-right\'><span class=\'ui-icon ui-icon-triangle-1-e\'></span></a>",\r\n
\t\t\t\tbS  ="<a href=\'javascript:void(0)\' id=\'sData\' class=\'fm-button ui-state-default ui-corner-all\'>"+p.bSubmit+"</a>",\r\n
\t\t\t\tbC  ="<a href=\'javascript:void(0)\' id=\'cData\' class=\'fm-button ui-state-default ui-corner-all\'>"+p.bCancel+"</a>";\r\n
\t\t\t\tvar bt = "<table border=\'0\' cellspacing=\'0\' cellpadding=\'0\' class=\'EditTable\' id=\'"+frmtborg+"_2\'><tbody><tr><td colspan=\'2\'><hr class=\'ui-widget-content\' style=\'margin:1px\'/></td></tr><tr id=\'Act_Buttons\'><td class=\'navButton\'>"+(rtlb ? bN+bP : bP+bN)+"</td><td class=\'EditButton\'>"+bS+bC+"</td></tr>";\r\n
\t\t\t\tbt += "<tr style=\'display:none\' class=\'binfo\'><td class=\'bottominfo\' colspan=\'2\'>"+rp_ge[$t.p.id].bottominfo+"</td></tr>";\r\n
\t\t\t\tbt += "</tbody></table>";\r\n
\t\t\t\tif(maxRows >  0) {\r\n
\t\t\t\t\tvar sd=[];\r\n
\t\t\t\t\t$.each($(tbl)[0].rows,function(i,r){\r\n
\t\t\t\t\t\tsd[i] = r;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tsd.sort(function(a,b){\r\n
\t\t\t\t\t\tif(a.rp > b.rp) {return 1;}\r\n
\t\t\t\t\t\tif(a.rp < b.rp) {return -1;}\r\n
\t\t\t\t\t\treturn 0;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\t$.each(sd, function(index, row) {\r\n
\t\t\t\t\t\t$(\'tbody\',tbl).append(row);\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\tp.gbox = "#gbox_"+$.jgrid.jqID(gID);\r\n
\t\t\t\tvar cle = false;\r\n
\t\t\t\tif(p.closeOnEscape===true){\r\n
\t\t\t\t\tp.closeOnEscape = false;\r\n
\t\t\t\t\tcle = true;\r\n
\t\t\t\t}\r\n
\t\t\t\tvar tms = $("<span></span>").append(frm).append(bt);\r\n
\t\t\t\t$.jgrid.createModal(IDs,tms,p,"#gview_"+$.jgrid.jqID($t.p.id),$("#gbox_"+$.jgrid.jqID($t.p.id))[0]);\r\n
\t\t\t\tif(rtlb) {\r\n
\t\t\t\t\t$("#pData, #nData",frmtb+"_2").css("float","right");\r\n
\t\t\t\t\t$(".EditButton",frmtb+"_2").css("text-align","left");\r\n
\t\t\t\t}\r\n
\t\t\t\tif(rp_ge[$t.p.id].topinfo) {$(".tinfo",frmtb).show();}\r\n
\t\t\t\tif(rp_ge[$t.p.id].bottominfo) {$(".binfo",frmtb+"_2").show();}\r\n
\t\t\t\ttms = null;bt=null;\r\n
\t\t\t\t$("#"+$.jgrid.jqID(IDs.themodal)).keydown( function( e ) {\r\n
\t\t\t\t\tvar wkey = e.target;\r\n
\t\t\t\t\tif ($("#"+frmgr).data("disabled")===true ) {return false;}//??\r\n
\t\t\t\t\tif(rp_ge[$t.p.id].savekey[0] === true && e.which == rp_ge[$t.p.id].savekey[1]) { // save\r\n
\t\t\t\t\t\tif(wkey.tagName != "TEXTAREA") {\r\n
\t\t\t\t\t\t\t$("#sData", frmtb+"_2").trigger("click");\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(e.which === 27) {\r\n
\t\t\t\t\t\tif(!checkUpdates()) {return false;}\r\n
\t\t\t\t\t\tif(cle)\t{$.jgrid.hideModal(this,{gb:p.gbox,jqm:p.jqModal, onClose: rp_ge[$t.p.id].onClose});}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(rp_ge[$t.p.id].navkeys[0]===true) {\r\n
\t\t\t\t\t\tif($("#id_g",frmtb).val() == "_empty") {return true;}\r\n
\t\t\t\t\t\tif(e.which == rp_ge[$t.p.id].navkeys[1]){ //up\r\n
\t\t\t\t\t\t\t$("#pData", frmtb+"_2").trigger("click");\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(e.which == rp_ge[$t.p.id].navkeys[2]){ //down\r\n
\t\t\t\t\t\t\t$("#nData", frmtb+"_2").trigger("click");\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tif(p.checkOnUpdate) {\r\n
\t\t\t\t\t$("a.ui-jqdialog-titlebar-close span","#"+$.jgrid.jqID(IDs.themodal)).removeClass("jqmClose");\r\n
\t\t\t\t\t$("a.ui-jqdialog-titlebar-close","#"+$.jgrid.jqID(IDs.themodal)).unbind("click")\r\n
\t\t\t\t\t.click(function(){\r\n
\t\t\t\t\t\tif(!checkUpdates()) {return false;}\r\n
\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal,onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\tp.saveicon = $.extend([true,"left","ui-icon-disk"],p.saveicon);\r\n
\t\t\t\tp.closeicon = $.extend([true,"left","ui-icon-close"],p.closeicon);\r\n
\t\t\t\t// beforeinitdata after creation of the form\r\n
\t\t\t\tif(p.saveicon[0]===true) {\r\n
\t\t\t\t\t$("#sData",frmtb+"_2").addClass(p.saveicon[1] == "right" ? \'fm-button-icon-right\' : \'fm-button-icon-left\')\r\n
\t\t\t\t\t.append("<span class=\'ui-icon "+p.saveicon[2]+"\'></span>");\r\n
\t\t\t\t}\r\n
\t\t\t\tif(p.closeicon[0]===true) {\r\n
\t\t\t\t\t$("#cData",frmtb+"_2").addClass(p.closeicon[1] == "right" ? \'fm-button-icon-right\' : \'fm-button-icon-left\')\r\n
\t\t\t\t\t.append("<span class=\'ui-icon "+p.closeicon[2]+"\'></span>");\r\n
\t\t\t\t}\r\n
\t\t\t\tif(rp_ge[$t.p.id].checkOnSubmit || rp_ge[$t.p.id].checkOnUpdate) {\r\n
\t\t\t\t\tbS  ="<a href=\'javascript:void(0)\' id=\'sNew\' class=\'fm-button ui-state-default ui-corner-all\' style=\'z-index:1002\'>"+p.bYes+"</a>";\r\n
\t\t\t\t\tbN  ="<a href=\'javascript:void(0)\' id=\'nNew\' class=\'fm-button ui-state-default ui-corner-all\' style=\'z-index:1002\'>"+p.bNo+"</a>";\r\n
\t\t\t\t\tbC  ="<a href=\'javascript:void(0)\' id=\'cNew\' class=\'fm-button ui-state-default ui-corner-all\' style=\'z-index:1002\'>"+p.bExit+"</a>";\r\n
\t\t\t\t\tvar ii, zI = p.zIndex  || 999;zI ++;\r\n
\t\t\t\t\tif ($.browser.msie && $.browser.version ==6) {\r\n
\t\t\t\t\t\tii = \'<iframe style="display:block;position:absolute;z-index:-1;filter:Alpha(Opacity=\\\'0\\\');" src="javascript:false;"></iframe>\';\r\n
\t\t\t\t\t} else {ii="";}\r\n
\t\t\t\t\t$("<div class=\'ui-widget-overlay jqgrid-overlay confirm\' style=\'z-index:"+zI+";display:none;\'>&#160;"+ii+"</div><div class=\'confirm ui-widget-content ui-jqconfirm\' style=\'z-index:"+(zI+1)+"\'>"+p.saveData+"<br/><br/>"+bS+bN+bC+"</div>").insertAfter("#"+frmgr);\r\n
\t\t\t\t\t$("#sNew","#"+$.jgrid.jqID(IDs.themodal)).click(function(){\r\n
\t\t\t\t\t\tpostIt();\r\n
\t\t\t\t\t\t$("#"+frmgr).data("disabled",false);\r\n
\t\t\t\t\t\t$(".confirm","#"+$.jgrid.jqID(IDs.themodal)).hide();\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\t$("#nNew","#"+$.jgrid.jqID(IDs.themodal)).click(function(){\r\n
\t\t\t\t\t\t$(".confirm","#"+$.jgrid.jqID(IDs.themodal)).hide();\r\n
\t\t\t\t\t\t$("#"+frmgr).data("disabled",false);\r\n
\t\t\t\t\t\tsetTimeout(function(){$(":input","#"+frmgr)[0].focus();},0);\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\t$("#cNew","#"+$.jgrid.jqID(IDs.themodal)).click(function(){\r\n
\t\t\t\t\t\t$(".confirm","#"+$.jgrid.jqID(IDs.themodal)).hide();\r\n
\t\t\t\t\t\t$("#"+frmgr).data("disabled",false);\r\n
\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal,onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\t// here initform - only once\r\n
\t\t\t\t$($t).triggerHandler("jqGridAddEditInitializeForm", [$("#"+frmgr), frmoper]);\r\n
\t\t\t\tif(onInitializeForm) {onInitializeForm.call($t,$("#"+frmgr));}\r\n
\t\t\t\tif(rowid=="_empty" || !rp_ge[$t.p.id].viewPagerButtons) {$("#pData,#nData",frmtb+"_2").hide();} else {$("#pData,#nData",frmtb+"_2").show();}\r\n
\t\t\t\t$($t).triggerHandler("jqGridAddEditBeforeShowForm", [$("#"+frmgr), frmoper]);\r\n
\t\t\t\tif(onBeforeShow) { onBeforeShow.call($t, $("#"+frmgr));}\r\n
\t\t\t\t$("#"+$.jgrid.jqID(IDs.themodal)).data("onClose",rp_ge[$t.p.id].onClose);\r\n
\t\t\t\t$.jgrid.viewModal("#"+$.jgrid.jqID(IDs.themodal),{gbox:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, overlay: p.overlay,modal:p.modal});\r\n
\t\t\t\tif(!closeovrl) {\r\n
\t\t\t\t\t$(".jqmOverlay").click(function(){\r\n
\t\t\t\t\t\tif(!checkUpdates()) {return false;}\r\n
\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\t$($t).triggerHandler("jqGridAddEditAfterShowForm", [$("#"+frmgr), frmoper]);\r\n
\t\t\t\tif(onAfterShow) { onAfterShow.call($t, $("#"+frmgr)); }\r\n
\t\t\t\t$(".fm-button","#"+$.jgrid.jqID(IDs.themodal)).hover(\r\n
\t\t\t\t\tfunction(){$(this).addClass(\'ui-state-hover\');},\r\n
\t\t\t\t\tfunction(){$(this).removeClass(\'ui-state-hover\');}\r\n
\t\t\t\t);\r\n
\t\t\t\t$("#sData", frmtb+"_2").click(function(){\r\n
\t\t\t\t\tpostdata = {};extpost={};\r\n
\t\t\t\t\t$("#FormError",frmtb).hide();\r\n
\t\t\t\t\t// all depend on ret array\r\n
\t\t\t\t\t//ret[0] - succes\r\n
\t\t\t\t\t//ret[1] - msg if not succes\r\n
\t\t\t\t\t//ret[2] - the id  that will be set if reload after submit false\r\n
\t\t\t\t\tgetFormData();\r\n
\t\t\t\t\tif(postdata[$t.p.id+"_id"] == "_empty")\t{postIt();}\r\n
\t\t\t\t\telse if(p.checkOnSubmit===true ) {\r\n
\t\t\t\t\t\tnewData = $.extend({},postdata,extpost);\r\n
\t\t\t\t\t\tdiff = compareData(newData,rp_ge[$t.p.id]._savedData);\r\n
\t\t\t\t\t\tif(diff) {\r\n
\t\t\t\t\t\t\t$("#"+frmgr).data("disabled",true);\r\n
\t\t\t\t\t\t\t$(".confirm","#"+$.jgrid.jqID(IDs.themodal)).show();\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tpostIt();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tpostIt();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#cData", frmtb+"_2").click(function(){\r\n
\t\t\t\t\tif(!checkUpdates()) {return false;}\r\n
\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal,onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#nData", frmtb+"_2").click(function(){\r\n
\t\t\t\t\tif(!checkUpdates()) {return false;}\r\n
\t\t\t\t\t$("#FormError",frmtb).hide();\r\n
\t\t\t\t\tvar npos = getCurrPos();\r\n
\t\t\t\t\tnpos[0] = parseInt(npos[0],10);\r\n
\t\t\t\t\tif(npos[0] != -1 && npos[1][npos[0]+1]) {\r\n
\t\t\t\t\t\t$($t).triggerHandler("jqGridAddEditClickPgButtons", [\'next\',$("#"+frmgr),npos[1][npos[0]]]);\r\n
\t\t\t\t\t\tvar nposret = true;\r\n
\t\t\t\t\t\tif($.isFunction(p.onclickPgButtons)) {\r\n
\t\t\t\t\t\t\tnposret = p.onclickPgButtons.call($t, \'next\',$("#"+frmgr),npos[1][npos[0]]);\r\n
\t\t\t\t\t\t\tif( nposret !== undefined && nposret === false ) {return false;}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif( $("#"+$.jgrid.jqID(npos[1][npos[0]+1])).hasClass(\'ui-state-disabled\')) {return false;}\r\n
\t\t\t\t\t\tfillData(npos[1][npos[0]+1],$t,frmgr);\r\n
\t\t\t\t\t\t$($t).jqGrid("setSelection",npos[1][npos[0]+1]);\r\n
\t\t\t\t\t\t$($t).triggerHandler("jqGridAddEditAfterClickPgButtons", [\'next\',$("#"+frmgr),npos[1][npos[0]]]);\r\n
\t\t\t\t\t\tif($.isFunction(p.afterclickPgButtons)) {\r\n
\t\t\t\t\t\t\tp.afterclickPgButtons.call($t, \'next\',$("#"+frmgr),npos[1][npos[0]+1]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tupdateNav(npos[0]+1,npos[1].length-1);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#pData", frmtb+"_2").click(function(){\r\n
\t\t\t\t\tif(!checkUpdates()) {return false;}\r\n
\t\t\t\t\t$("#FormError",frmtb).hide();\r\n
\t\t\t\t\tvar ppos = getCurrPos();\r\n
\t\t\t\t\tif(ppos[0] != -1 && ppos[1][ppos[0]-1]) {\r\n
\t\t\t\t\t\t$($t).triggerHandler("jqGridAddEditClickPgButtons", [\'prev\',$("#"+frmgr),ppos[1][ppos[0]]]);\r\n
\t\t\t\t\t\tvar pposret = true;\r\n
\t\t\t\t\t\tif($.isFunction(p.onclickPgButtons)) {\r\n
\t\t\t\t\t\t\tpposret = p.onclickPgButtons.call($t, \'prev\',$("#"+frmgr),ppos[1][ppos[0]]);\r\n
\t\t\t\t\t\t\tif( pposret !== undefined && pposret === false ) {return false;}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif( $("#"+$.jgrid.jqID(ppos[1][ppos[0]-1])).hasClass(\'ui-state-disabled\')) {return false;}\r\n
\t\t\t\t\t\tfillData(ppos[1][ppos[0]-1],$t,frmgr);\r\n
\t\t\t\t\t\t$($t).jqGrid("setSelection",ppos[1][ppos[0]-1]);\r\n
\t\t\t\t\t\t$($t).triggerHandler("jqGridAddEditAfterClickPgButtons", [\'prev\',$("#"+frmgr),ppos[1][ppos[0]]]);\r\n
\t\t\t\t\t\tif($.isFunction(p.afterclickPgButtons)) {\r\n
\t\t\t\t\t\t\tp.afterclickPgButtons.call($t, \'prev\',$("#"+frmgr),ppos[1][ppos[0]-1]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tupdateNav(ppos[0]-1,ppos[1].length-1);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tvar posInit =getCurrPos();\r\n
\t\t\tupdateNav(posInit[0],posInit[1].length-1);\r\n
\r\n
\t\t});\r\n
\t},\r\n
\tviewGridRow : function(rowid, p){\r\n
\t\tp = $.extend({\r\n
\t\t\ttop : 0,\r\n
\t\t\tleft: 0,\r\n
\t\t\twidth: 0,\r\n
\t\t\theight: \'auto\',\r\n
\t\t\tdataheight: \'auto\',\r\n
\t\t\tmodal: false,\r\n
\t\t\toverlay: 30,\r\n
\t\t\tdrag: true,\r\n
\t\t\tresize: true,\r\n
\t\t\tjqModal: true,\r\n
\t\t\tcloseOnEscape : false,\r\n
\t\t\tlabelswidth: \'30%\',\r\n
\t\t\tcloseicon: [],\r\n
\t\t\tnavkeys: [false,38,40],\r\n
\t\t\tonClose: null,\r\n
\t\t\tbeforeShowForm : null,\r\n
\t\t\tbeforeInitData : null,\r\n
\t\t\tviewPagerButtons : true\r\n
\t\t}, $.jgrid.view, p || {});\r\n
\t\trp_ge[$(this)[0].p.id] = p;\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif (!$t.grid || !rowid) {return;}\r\n
\t\t\tvar gID = $t.p.id,\r\n
\t\t\tfrmgr = "ViewGrid_"+$.jgrid.jqID( gID  ), frmtb = "ViewTbl_" + $.jgrid.jqID( gID ),\r\n
\t\t\tfrmgr_id = "ViewGrid_"+gID, frmtb_id = "ViewTbl_"+gID,\r\n
\t\t\tIDs = {themodal:\'viewmod\'+gID,modalhead:\'viewhd\'+gID,modalcontent:\'viewcnt\'+gID, scrollelm : frmgr},\r\n
\t\t\tonBeforeInit = $.isFunction(rp_ge[$t.p.id].beforeInitData) ? rp_ge[$t.p.id].beforeInitData : false,\r\n
\t\t\tshowFrm = true,\r\n
\t\t\tmaxCols = 1, maxRows=0;\r\n
\t\t\tfunction focusaref(){ //Sfari 3 issues\r\n
\t\t\t\tif(rp_ge[$t.p.id].closeOnEscape===true || rp_ge[$t.p.id].navkeys[0]===true) {\r\n
\t\t\t\t\tsetTimeout(function(){$(".ui-jqdialog-titlebar-close","#"+$.jgrid.jqID(IDs.modalhead)).focus();},0);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tfunction createData(rowid,obj,tb,maxcols){\r\n
\t\t\t\tvar nm, hc,trdata, cnt=0,tmp, dc, retpos=[], ind=false,\r\n
\t\t\t\ttdtmpl = "<td class=\'CaptionTD form-view-label ui-widget-content\' width=\'"+p.labelswidth+"\'>&#160;</td><td class=\'DataTD form-view-data ui-helper-reset ui-widget-content\'>&#160;</td>", tmpl="",\r\n
\t\t\t\ttdtmpl2 = "<td class=\'CaptionTD form-view-label ui-widget-content\'>&#160;</td><td class=\'DataTD form-view-data ui-widget-content\'>&#160;</td>",\r\n
\t\t\t\tfmtnum = [\'integer\',\'number\',\'currency\'],max1 =0, max2=0 ,maxw,setme, viewfld;\r\n
\t\t\t\tfor (var i =1;i<=maxcols;i++) {\r\n
\t\t\t\t\ttmpl += i == 1 ? tdtmpl : tdtmpl2;\r\n
\t\t\t\t}\r\n
\t\t\t\t// find max number align rigth with property formatter\r\n
\t\t\t\t$(obj.p.colModel).each( function() {\r\n
\t\t\t\t\tif(this.editrules && this.editrules.edithidden === true) {\r\n
\t\t\t\t\t\thc = false;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\thc = this.hidden === true ? true : false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(!hc && this.align===\'right\') {\r\n
\t\t\t\t\t\tif(this.formatter && $.inArray(this.formatter,fmtnum) !== -1 ) {\r\n
\t\t\t\t\t\t\tmax1 = Math.max(max1,parseInt(this.width,10));\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tmax2 = Math.max(max2,parseInt(this.width,10));\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tmaxw  = max1 !==0 ? max1 : max2 !==0 ? max2 : 0;\r\n
\t\t\t\tind = $(obj).jqGrid("getInd",rowid);\r\n
\t\t\t\t$(obj.p.colModel).each( function(i) {\r\n
\t\t\t\t\tnm = this.name;\r\n
\t\t\t\t\tsetme = false;\r\n
\t\t\t\t\t// hidden fields are included in the form\r\n
\t\t\t\t\tif(this.editrules && this.editrules.edithidden === true) {\r\n
\t\t\t\t\t\thc = false;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\thc = this.hidden === true ? true : false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tdc = hc ? "style=\'display:none\'" : "";\r\n
\t\t\t\t\tviewfld = (typeof this.viewable != \'boolean\') ? true : this.viewable;\r\n
\t\t\t\t\tif ( nm !== \'cb\' && nm !== \'subgrid\' && nm !== \'rn\' && viewfld) {\r\n
\t\t\t\t\t\tif(ind === false) {\r\n
\t\t\t\t\t\t\ttmp = "";\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tif(nm == obj.p.ExpandColumn && obj.p.treeGrid === true) {\r\n
\t\t\t\t\t\t\t\ttmp = $("td:eq("+i+")",obj.rows[ind]).text();\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\ttmp = $("td:eq("+i+")",obj.rows[ind]).html();\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tsetme = this.align === \'right\' && maxw !==0 ? true : false;\r\n
\t\t\t\t\t\tvar frmopt = $.extend({},{rowabove:false,rowcontent:\'\'}, this.formoptions || {}),\r\n
\t\t\t\t\t\trp = parseInt(frmopt.rowpos,10) || cnt+1,\r\n
\t\t\t\t\t\tcp = parseInt((parseInt(frmopt.colpos,10) || 1)*2,10);\r\n
\t\t\t\t\t\tif(frmopt.rowabove) {\r\n
\t\t\t\t\t\t\tvar newdata = $("<tr><td class=\'contentinfo\' colspan=\'"+(maxcols*2)+"\'>"+frmopt.rowcontent+"</td></tr>");\r\n
\t\t\t\t\t\t\t$(tb).append(newdata);\r\n
\t\t\t\t\t\t\tnewdata[0].rp = rp;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ttrdata = $(tb).find("tr[rowpos="+rp+"]");\r\n
\t\t\t\t\t\tif ( trdata.length===0 ) {\r\n
\t\t\t\t\t\t\ttrdata = $("<tr "+dc+" rowpos=\'"+rp+"\'></tr>").addClass("FormData").attr("id","trv_"+nm);\r\n
\t\t\t\t\t\t\t$(trdata).append(tmpl);\r\n
\t\t\t\t\t\t\t$(tb).append(trdata);\r\n
\t\t\t\t\t\t\ttrdata[0].rp = rp;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t$("td:eq("+(cp-2)+")",trdata[0]).html(\'<b>\'+ (typeof frmopt.label === \'undefined\' ? obj.p.colNames[i]: frmopt.label)+\'</b>\');\r\n
\t\t\t\t\t\t$("td:eq("+(cp-1)+")",trdata[0]).append("<span>"+tmp+"</span>").attr("id","v_"+nm);\r\n
\t\t\t\t\t\tif(setme){\r\n
\t\t\t\t\t\t\t$("td:eq("+(cp-1)+") span",trdata[0]).css({\'text-align\':\'right\',width:maxw+"px"});\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tretpos[cnt] = i;\r\n
\t\t\t\t\t\tcnt++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tif( cnt > 0) {\r\n
\t\t\t\t\tvar idrow = $("<tr class=\'FormData\' style=\'display:none\'><td class=\'CaptionTD\'></td><td colspan=\'"+ (maxcols*2-1)+"\' class=\'DataTD\'><input class=\'FormElement\' id=\'id_g\' type=\'text\' name=\'id\' value=\'"+rowid+"\'/></td></tr>");\r\n
\t\t\t\t\tidrow[0].rp = cnt+99;\r\n
\t\t\t\t\t$(tb).append(idrow);\r\n
\t\t\t\t}\r\n
\t\t\t\treturn retpos;\r\n
\t\t\t}\r\n
\t\t\tfunction fillData(rowid,obj){\r\n
\t\t\t\tvar nm, hc,cnt=0,tmp, opt,trv;\r\n
\t\t\t\ttrv = $(obj).jqGrid("getInd",rowid,true);\r\n
\t\t\t\tif(!trv) {return;}\r\n
\t\t\t\t$(\'td\',trv).each( function(i) {\r\n
\t\t\t\t\tnm = obj.p.colModel[i].name;\r\n
\t\t\t\t\t// hidden fields are included in the form\r\n
\t\t\t\t\tif(obj.p.colModel[i].editrules && obj.p.colModel[i].editrules.edithidden === true) {\r\n
\t\t\t\t\t\thc = false;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\thc = obj.p.colModel[i].hidden === true ? true : false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif ( nm !== \'cb\' && nm !== \'subgrid\' && nm !== \'rn\') {\r\n
\t\t\t\t\t\tif(nm == obj.p.ExpandColumn && obj.p.treeGrid === true) {\r\n
\t\t\t\t\t\t\ttmp = $(this).text();\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\ttmp = $(this).html();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\topt = $.extend({},obj.p.colModel[i].editoptions || {});\r\n
\t\t\t\t\t\tnm = $.jgrid.jqID("v_"+nm);\r\n
\t\t\t\t\t\t$("#"+nm+" span","#"+frmtb).html(tmp);\r\n
\t\t\t\t\t\tif (hc) {$("#"+nm,"#"+frmtb).parents("tr:first").hide();}\r\n
\t\t\t\t\t\tcnt++;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tif(cnt>0) {$("#id_g","#"+frmtb).val(rowid);}\r\n
\t\t\t}\r\n
\t\t\tfunction updateNav(cr,totr){\r\n
\t\t\t\tif (cr===0) {$("#pData","#"+frmtb+"_2").addClass(\'ui-state-disabled\');} else {$("#pData","#"+frmtb+"_2").removeClass(\'ui-state-disabled\');}\r\n
\t\t\t\tif (cr==totr) {$("#nData","#"+frmtb+"_2").addClass(\'ui-state-disabled\');} else {$("#nData","#"+frmtb+"_2").removeClass(\'ui-state-disabled\');}\r\n
\t\t\t}\r\n
\t\t\tfunction getCurrPos() {\r\n
\t\t\t\tvar rowsInGrid = $($t).jqGrid("getDataIDs"),\r\n
\t\t\t\tselrow = $("#id_g","#"+frmtb).val(),\r\n
\t\t\t\tpos = $.inArray(selrow,rowsInGrid);\r\n
\t\t\t\treturn [pos,rowsInGrid];\r\n
\t\t\t}\r\n
\r\n
\t\t\tif ( $("#"+$.jgrid.jqID(IDs.themodal))[0] !== undefined ) {\r\n
\t\t\t\tif(onBeforeInit) {\r\n
\t\t\t\t\tshowFrm = onBeforeInit.call($t,$("#"+frmgr));\r\n
\t\t\t\t\tif(typeof(showFrm) == "undefined") {\r\n
\t\t\t\t\t\tshowFrm = true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm === false) {return;}\r\n
\t\t\t\t$(".ui-jqdialog-title","#"+$.jgrid.jqID(IDs.modalhead)).html(p.caption);\r\n
\t\t\t\t$("#FormError","#"+frmtb).hide();\r\n
\t\t\t\tfillData(rowid,$t);\r\n
\t\t\t\tif($.isFunction(rp_ge[$t.p.id].beforeShowForm)) {rp_ge[$t.p.id].beforeShowForm.call($t,$("#"+frmgr));}\r\n
\t\t\t\t$.jgrid.viewModal("#"+$.jgrid.jqID(IDs.themodal),{gbox:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, jqM: false, overlay: p.overlay, modal:p.modal});\r\n
\t\t\t\tfocusaref();\r\n
\t\t\t} else {\r\n
\t\t\t\tvar dh = isNaN(p.dataheight) ? p.dataheight : p.dataheight+"px";\r\n
\t\t\t\tvar frm = $("<form name=\'FormPost\' id=\'"+frmgr_id+"\' class=\'FormGrid\' style=\'width:100%;overflow:auto;position:relative;height:"+dh+";\'></form>"),\r\n
\t\t\t\ttbl =$("<table id=\'"+frmtb_id+"\' class=\'EditTable\' cellspacing=\'1\' cellpadding=\'2\' border=\'0\' style=\'table-layout:fixed\'><tbody></tbody></table>");\r\n
\t\t\t\tif(onBeforeInit) {\r\n
\t\t\t\t\tshowFrm = onBeforeInit.call($t,$("#"+frmgr));\r\n
\t\t\t\t\tif(typeof(showFrm) == "undefined") {\r\n
\t\t\t\t\t\tshowFrm = true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm === false) {return;}\r\n
\t\t\t\t$($t.p.colModel).each( function() {\r\n
\t\t\t\t\tvar fmto = this.formoptions;\r\n
\t\t\t\t\tmaxCols = Math.max(maxCols, fmto ? fmto.colpos || 0 : 0 );\r\n
\t\t\t\t\tmaxRows = Math.max(maxRows, fmto ? fmto.rowpos || 0 : 0 );\r\n
\t\t\t\t});\r\n
\t\t\t\t// set the id.\r\n
\t\t\t\t$(frm).append(tbl);\r\n
\t\t\t\tcreateData(rowid, $t, tbl, maxCols);\r\n
\t\t\t\tvar rtlb = $t.p.direction == "rtl" ? true :false,\r\n
\t\t\t\tbp = rtlb ? "nData" : "pData",\r\n
\t\t\t\tbn = rtlb ? "pData" : "nData",\r\n
\r\n
\t\t\t\t// buttons at footer\r\n
\t\t\t\tbP = "<a href=\'javascript:void(0)\' id=\'"+bp+"\' class=\'fm-button ui-state-default ui-corner-left\'><span class=\'ui-icon ui-icon-triangle-1-w\'></span></a>",\r\n
\t\t\t\tbN = "<a href=\'javascript:void(0)\' id=\'"+bn+"\' class=\'fm-button ui-state-default ui-corner-right\'><span class=\'ui-icon ui-icon-triangle-1-e\'></span></a>",\r\n
\t\t\t\tbC  ="<a href=\'javascript:void(0)\' id=\'cData\' class=\'fm-button ui-state-default ui-corner-all\'>"+p.bClose+"</a>";\r\n
\t\t\t\tif(maxRows >  0) {\r\n
\t\t\t\t\tvar sd=[];\r\n
\t\t\t\t\t$.each($(tbl)[0].rows,function(i,r){\r\n
\t\t\t\t\t\tsd[i] = r;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tsd.sort(function(a,b){\r\n
\t\t\t\t\t\tif(a.rp > b.rp) {return 1;}\r\n
\t\t\t\t\t\tif(a.rp < b.rp) {return -1;}\r\n
\t\t\t\t\t\treturn 0;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\t$.each(sd, function(index, row) {\r\n
\t\t\t\t\t\t$(\'tbody\',tbl).append(row);\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\tp.gbox = "#gbox_"+$.jgrid.jqID(gID);\r\n
\t\t\t\tvar bt = $("<span></span>").append(frm).append("<table border=\'0\' class=\'EditTable\' id=\'"+frmtb+"_2\'><tbody><tr id=\'Act_Buttons\'><td class=\'navButton\' width=\'"+p.labelswidth+"\'>"+(rtlb ? bN+bP : bP+bN)+"</td><td class=\'EditButton\'>"+bC+"</td></tr></tbody></table>");\r\n
\t\t\t\t$.jgrid.createModal(IDs,bt,p,"#gview_"+$.jgrid.jqID($t.p.id),$("#gview_"+$.jgrid.jqID($t.p.id))[0]);\r\n
\t\t\t\tif(rtlb) {\r\n
\t\t\t\t\t$("#pData, #nData","#"+frmtb+"_2").css("float","right");\r\n
\t\t\t\t\t$(".EditButton","#"+frmtb+"_2").css("text-align","left");\r\n
\t\t\t\t}\r\n
\t\t\t\tif(!p.viewPagerButtons) {$("#pData, #nData","#"+frmtb+"_2").hide();}\r\n
\t\t\t\tbt = null;\r\n
\t\t\t\t$("#"+IDs.themodal).keydown( function( e ) {\r\n
\t\t\t\t\tif(e.which === 27) {\r\n
\t\t\t\t\t\tif(rp_ge[$t.p.id].closeOnEscape) {$.jgrid.hideModal(this,{gb:p.gbox,jqm:p.jqModal, onClose: p.onClose});}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(p.navkeys[0]===true) {\r\n
\t\t\t\t\t\tif(e.which === p.navkeys[1]){ //up\r\n
\t\t\t\t\t\t\t$("#pData", "#"+frmtb+"_2").trigger("click");\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(e.which === p.navkeys[2]){ //down\r\n
\t\t\t\t\t\t\t$("#nData", "#"+frmtb+"_2").trigger("click");\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tp.closeicon = $.extend([true,"left","ui-icon-close"],p.closeicon);\r\n
\t\t\t\tif(p.closeicon[0]===true) {\r\n
\t\t\t\t\t$("#cData","#"+frmtb+"_2").addClass(p.closeicon[1] == "right" ? \'fm-button-icon-right\' : \'fm-button-icon-left\')\r\n
\t\t\t\t\t.append("<span class=\'ui-icon "+p.closeicon[2]+"\'></span>");\r\n
\t\t\t\t}\r\n
\t\t\t\tif($.isFunction(p.beforeShowForm)) {p.beforeShowForm.call($t,$("#"+frmgr));}\r\n
\t\t\t\t$.jgrid.viewModal("#"+$.jgrid.jqID(IDs.themodal),{gbox:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, modal:p.modal});\r\n
\t\t\t\t$(".fm-button:not(.ui-state-disabled)","#"+frmtb+"_2").hover(\r\n
\t\t\t\t\tfunction(){$(this).addClass(\'ui-state-hover\');},\r\n
\t\t\t\t\tfunction(){$(this).removeClass(\'ui-state-hover\');}\r\n
\t\t\t\t);\r\n
\t\t\t\tfocusaref();\r\n
\t\t\t\t$("#cData", "#"+frmtb+"_2").click(function(){\r\n
\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, onClose: p.onClose});\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#nData", "#"+frmtb+"_2").click(function(){\r\n
\t\t\t\t\t$("#FormError","#"+frmtb).hide();\r\n
\t\t\t\t\tvar npos = getCurrPos();\r\n
\t\t\t\t\tnpos[0] = parseInt(npos[0],10);\r\n
\t\t\t\t\tif(npos[0] != -1 && npos[1][npos[0]+1]) {\r\n
\t\t\t\t\t\tif($.isFunction(p.onclickPgButtons)) {\r\n
\t\t\t\t\t\t\tp.onclickPgButtons.call($t,\'next\',$("#"+frmgr),npos[1][npos[0]]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tfillData(npos[1][npos[0]+1],$t);\r\n
\t\t\t\t\t\t$($t).jqGrid("setSelection",npos[1][npos[0]+1]);\r\n
\t\t\t\t\t\tif($.isFunction(p.afterclickPgButtons)) {\r\n
\t\t\t\t\t\t\tp.afterclickPgButtons.call($t,\'next\',$("#"+frmgr),npos[1][npos[0]+1]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tupdateNav(npos[0]+1,npos[1].length-1);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tfocusaref();\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#pData", "#"+frmtb+"_2").click(function(){\r\n
\t\t\t\t\t$("#FormError","#"+frmtb).hide();\r\n
\t\t\t\t\tvar ppos = getCurrPos();\r\n
\t\t\t\t\tif(ppos[0] != -1 && ppos[1][ppos[0]-1]) {\r\n
\t\t\t\t\t\tif($.isFunction(p.onclickPgButtons)) {\r\n
\t\t\t\t\t\t\tp.onclickPgButtons.call($t,\'prev\',$("#"+frmgr),ppos[1][ppos[0]]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tfillData(ppos[1][ppos[0]-1],$t);\r\n
\t\t\t\t\t\t$($t).jqGrid("setSelection",ppos[1][ppos[0]-1]);\r\n
\t\t\t\t\t\tif($.isFunction(p.afterclickPgButtons)) {\r\n
\t\t\t\t\t\t\tp.afterclickPgButtons.call($t,\'prev\',$("#"+frmgr),ppos[1][ppos[0]-1]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tupdateNav(ppos[0]-1,ppos[1].length-1);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tfocusaref();\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tvar posInit =getCurrPos();\r\n
\t\t\tupdateNav(posInit[0],posInit[1].length-1);\r\n
\t\t});\r\n
\t},\r\n
\tdelGridRow : function(rowids,p) {\r\n
\t\tp = $.extend({\r\n
\t\t\ttop : 0,\r\n
\t\t\tleft: 0,\r\n
\t\t\twidth: 240,\r\n
\t\t\theight: \'auto\',\r\n
\t\t\tdataheight : \'auto\',\r\n
\t\t\tmodal: false,\r\n
\t\t\toverlay: 30,\r\n
\t\t\tdrag: true,\r\n
\t\t\tresize: true,\r\n
\t\t\turl : \'\',\r\n
\t\t\tmtype : "POST",\r\n
\t\t\treloadAfterSubmit: true,\r\n
\t\t\tbeforeShowForm: null,\r\n
\t\t\tbeforeInitData : null,\r\n
\t\t\tafterShowForm: null,\r\n
\t\t\tbeforeSubmit: null,\r\n
\t\t\tonclickSubmit: null,\r\n
\t\t\tafterSubmit: null,\r\n
\t\t\tjqModal : true,\r\n
\t\t\tcloseOnEscape : false,\r\n
\t\t\tdelData: {},\r\n
\t\t\tdelicon : [],\r\n
\t\t\tcancelicon : [],\r\n
\t\t\tonClose : null,\r\n
\t\t\tajaxDelOptions : {},\r\n
\t\t\tprocessing : false,\r\n
\t\t\tserializeDelData : null,\r\n
\t\t\tuseDataProxy : false\r\n
\t\t}, $.jgrid.del, p ||{});\r\n
\t\trp_ge[$(this)[0].p.id] = p;\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif (!$t.grid ) {return;}\r\n
\t\t\tif(!rowids) {return;}\r\n
\t\t\tvar onBeforeShow = $.isFunction( rp_ge[$t.p.id].beforeShowForm  ),\r\n
\t\t\tonAfterShow = $.isFunction( rp_ge[$t.p.id].afterShowForm ),\r\n
\t\t\tonBeforeInit = $.isFunction(rp_ge[$t.p.id].beforeInitData) ? rp_ge[$t.p.id].beforeInitData : false,\r\n
\t\t\tgID = $t.p.id, onCS = {},\r\n
\t\t\tshowFrm = true,\r\n
\t\t\tdtbl = "DelTbl_"+$.jgrid.jqID(gID),postd, idname, opers, oper,\r\n
\t\t\tdtbl_id = "DelTbl_" + gID,\r\n
\t\t\tIDs = {themodal:\'delmod\'+gID,modalhead:\'delhd\'+gID,modalcontent:\'delcnt\'+gID, scrollelm: dtbl};\r\n
\t\t\tif (jQuery.isArray(rowids)) {rowids = rowids.join();}\r\n
\t\t\tif ( $("#"+$.jgrid.jqID(IDs.themodal))[0] !== undefined ) {\r\n
\t\t\t\tif(onBeforeInit) {\r\n
\t\t\t\t\tshowFrm = onBeforeInit.call($t,$("#"+dtbl));\r\n
\t\t\t\t\tif(typeof(showFrm) == "undefined") {\r\n
\t\t\t\t\t\tshowFrm = true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm === false) {return;}\r\n
\t\t\t\t$("#DelData>td","#"+dtbl).text(rowids);\r\n
\t\t\t\t$("#DelError","#"+dtbl).hide();\r\n
\t\t\t\tif( rp_ge[$t.p.id].processing === true) {\r\n
\t\t\t\t\trp_ge[$t.p.id].processing=false;\r\n
\t\t\t\t\t$("#dData", "#"+dtbl).removeClass(\'ui-state-active\');\r\n
\t\t\t\t}\r\n
\t\t\t\tif(onBeforeShow) {rp_ge[$t.p.id].beforeShowForm.call($t,$("#"+dtbl));}\r\n
\t\t\t\t$.jgrid.viewModal("#"+$.jgrid.jqID(IDs.themodal),{gbox:"#gbox_"+$.jgrid.jqID(gID),jqm:rp_ge[$t.p.id].jqModal,jqM: false, overlay: rp_ge[$t.p.id].overlay, modal:rp_ge[$t.p.id].modal});\r\n
\t\t\t\tif(onAfterShow) {rp_ge[$t.p.id].afterShowForm.call($t,$("#"+dtbl));}\r\n
\t\t\t} else {\r\n
\t\t\t\tvar dh = isNaN(rp_ge[$t.p.id].dataheight) ? rp_ge[$t.p.id].dataheight : rp_ge[$t.p.id].dataheight+"px";\r\n
\t\t\t\tvar tbl = "<div id=\'"+dtbl_id+"\' class=\'formdata\' style=\'width:100%;overflow:auto;position:relative;height:"+dh+";\'>";\r\n
\t\t\t\ttbl += "<table class=\'DelTable\'><tbody>";\r\n
\t\t\t\t// error data\r\n
\t\t\t\ttbl += "<tr id=\'DelError\' style=\'display:none\'><td class=\'ui-state-error\'></td></tr>";\r\n
\t\t\t\ttbl += "<tr id=\'DelData\' style=\'display:none\'><td >"+rowids+"</td></tr>";\r\n
\t\t\t\ttbl += "<tr><td class=\\"delmsg\\" style=\\"white-space:pre;\\">"+rp_ge[$t.p.id].msg+"</td></tr><tr><td >&#160;</td></tr>";\r\n
\t\t\t\t// buttons at footer\r\n
\t\t\t\ttbl += "</tbody></table></div>";\r\n
\t\t\t\tvar bS  = "<a href=\'javascript:void(0)\' id=\'dData\' class=\'fm-button ui-state-default ui-corner-all\'>"+p.bSubmit+"</a>",\r\n
\t\t\t\tbC  = "<a href=\'javascript:void(0)\' id=\'eData\' class=\'fm-button ui-state-default ui-corner-all\'>"+p.bCancel+"</a>";\r\n
\t\t\t\ttbl += "<table cellspacing=\'0\' cellpadding=\'0\' border=\'0\' class=\'EditTable\' id=\'"+dtbl+"_2\'><tbody><tr><td><hr class=\'ui-widget-content\' style=\'margin:1px\'/></td></tr><tr><td class=\'DelButton EditButton\'>"+bS+"&#160;"+bC+"</td></tr></tbody></table>";\r\n
\t\t\t\tp.gbox = "#gbox_"+$.jgrid.jqID(gID);\r\n
\t\t\t\t$.jgrid.createModal(IDs,tbl,p,"#gview_"+$.jgrid.jqID($t.p.id),$("#gview_"+$.jgrid.jqID($t.p.id))[0]);\r\n
\r\n
\t\t\t\tif(onBeforeInit) {\r\n
\t\t\t\t\tshowFrm = onBeforeInit.call($t,$("#"+dtbl));\r\n
\t\t\t\t\tif(typeof(showFrm) == "undefined") {\r\n
\t\t\t\t\t\tshowFrm = true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(showFrm === false) {return;}\r\n
\r\n
\t\t\t\t$(".fm-button","#"+dtbl+"_2").hover(\r\n
\t\t\t\t\tfunction(){$(this).addClass(\'ui-state-hover\');},\r\n
\t\t\t\t\tfunction(){$(this).removeClass(\'ui-state-hover\');}\r\n
\t\t\t\t);\r\n
\t\t\t\tp.delicon = $.extend([true,"left","ui-icon-scissors"],rp_ge[$t.p.id].delicon);\r\n
\t\t\t\tp.cancelicon = $.extend([true,"left","ui-icon-cancel"],rp_ge[$t.p.id].cancelicon);\r\n
\t\t\t\tif(p.delicon[0]===true) {\r\n
\t\t\t\t\t$("#dData","#"+dtbl+"_2").addClass(p.delicon[1] == "right" ? \'fm-button-icon-right\' : \'fm-button-icon-left\')\r\n
\t\t\t\t\t.append("<span class=\'ui-icon "+p.delicon[2]+"\'></span>");\r\n
\t\t\t\t}\r\n
\t\t\t\tif(p.cancelicon[0]===true) {\r\n
\t\t\t\t\t$("#eData","#"+dtbl+"_2").addClass(p.cancelicon[1] == "right" ? \'fm-button-icon-right\' : \'fm-button-icon-left\')\r\n
\t\t\t\t\t.append("<span class=\'ui-icon "+p.cancelicon[2]+"\'></span>");\r\n
\t\t\t\t}\r\n
\t\t\t\t$("#dData","#"+dtbl+"_2").click(function(){\r\n
\t\t\t\t\tvar ret=[true,""];onCS = {};\r\n
\t\t\t\t\tvar postdata = $("#DelData>td","#"+dtbl).text(); //the pair is name=val1,val2,...\r\n
\t\t\t\t\tif( $.isFunction( rp_ge[$t.p.id].onclickSubmit ) ) {onCS = rp_ge[$t.p.id].onclickSubmit.call($t,rp_ge[$t.p.id], postdata) || {};}\r\n
\t\t\t\t\tif( $.isFunction( rp_ge[$t.p.id].beforeSubmit ) ) {ret = rp_ge[$t.p.id].beforeSubmit.call($t,postdata);}\r\n
\t\t\t\t\tif(ret[0] && !rp_ge[$t.p.id].processing) {\r\n
\t\t\t\t\t\trp_ge[$t.p.id].processing = true;\r\n
\t\t\t\t\t\topers = $t.p.prmNames;\r\n
\t\t\t\t\t\tpostd = $.extend({},rp_ge[$t.p.id].delData, onCS);\r\n
\t\t\t\t\t\toper = opers.oper;\r\n
\t\t\t\t\t\tpostd[oper] = opers.deloper;\r\n
\t\t\t\t\t\tidname = opers.id;\r\n
\t\t\t\t\t\tpostdata = String(postdata).split(",");\r\n
\t\t\t\t\t\tif(!postdata.length) { return false; }\r\n
\t\t\t\t\t\tfor( var pk in postdata) {\r\n
\t\t\t\t\t\t\tif(postdata.hasOwnProperty(pk)) {\r\n
\t\t\t\t\t\t\t\tpostdata[pk] = $.jgrid.stripPref($t.p.idPrefix, postdata[pk]);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tpostd[idname] = postdata.join();\r\n
\t\t\t\t\t\t$(this).addClass(\'ui-state-active\');\r\n
\t\t\t\t\t\tvar ajaxOptions = $.extend({\r\n
\t\t\t\t\t\t\turl: rp_ge[$t.p.id].url ? rp_ge[$t.p.id].url : $($t).jqGrid(\'getGridParam\',\'editurl\'),\r\n
\t\t\t\t\t\t\ttype: rp_ge[$t.p.id].mtype,\r\n
\t\t\t\t\t\t\tdata: $.isFunction(rp_ge[$t.p.id].serializeDelData) ? rp_ge[$t.p.id].serializeDelData.call($t,postd) : postd,\r\n
\t\t\t\t\t\t\tcomplete:function(data,Status){\r\n
\t\t\t\t\t\t\t\tif(Status != "success") {\r\n
\t\t\t\t\t\t\t\t\tret[0] = false;\r\n
\t\t\t\t\t\t\t\t\tif ($.isFunction(rp_ge[$t.p.id].errorTextFormat)) {\r\n
\t\t\t\t\t\t\t\t\t\tret[1] = rp_ge[$t.p.id].errorTextFormat.call($t,data);\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\tret[1] = Status + " Status: \'" + data.statusText + "\'. Error code: " + data.status;\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t// data is posted successful\r\n
\t\t\t\t\t\t\t\t\t// execute aftersubmit with the returned data from server\r\n
\t\t\t\t\t\t\t\t\tif( $.isFunction( rp_ge[$t.p.id].afterSubmit ) ) {\r\n
\t\t\t\t\t\t\t\t\t\tret = rp_ge[$t.p.id].afterSubmit.call($t,data,postd);\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif(ret[0] === false) {\r\n
\t\t\t\t\t\t\t\t\t$("#DelError>td","#"+dtbl).html(ret[1]);\r\n
\t\t\t\t\t\t\t\t\t$("#DelError","#"+dtbl).show();\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\tif(rp_ge[$t.p.id].reloadAfterSubmit && $t.p.datatype != "local") {\r\n
\t\t\t\t\t\t\t\t\t\t$($t).trigger("reloadGrid");\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\tif($t.p.treeGrid===true){\r\n
\t\t\t\t\t\t\t\t\t\t\t\ttry {$($t).jqGrid("delTreeNode",$t.p.idPrefix+postdata[0]);} catch(e){}\r\n
\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\tfor(var i=0;i<postdata.length;i++) {\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("delRowData",$t.p.idPrefix+ postdata[i]);\r\n
\t\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t$t.p.selrow = null;\r\n
\t\t\t\t\t\t\t\t\t\t$t.p.selarrrow = [];\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\tif($.isFunction(rp_ge[$t.p.id].afterComplete)) {\r\n
\t\t\t\t\t\t\t\t\t\tsetTimeout(function(){rp_ge[$t.p.id].afterComplete.call($t,data,postdata);},500);\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\trp_ge[$t.p.id].processing=false;\r\n
\t\t\t\t\t\t\t\t$("#dData", "#"+dtbl+"_2").removeClass(\'ui-state-active\');\r\n
\t\t\t\t\t\t\t\tif(ret[0]) {$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, onClose: rp_ge[$t.p.id].onClose});}\r\n
\t\t\t\t\t\t\t}\r\n
\t

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAY=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="6" aka="AAAAAAAAAAY=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

\t\t\t\t\t}, $.jgrid.ajaxOptions, rp_ge[$t.p.id].ajaxDelOptions);\r\n
\r\n
\r\n
\t\t\t\t\t\tif (!ajaxOptions.url && !rp_ge[$t.p.id].useDataProxy) {\r\n
\t\t\t\t\t\t\tif ($.isFunction($t.p.dataProxy)) {\r\n
\t\t\t\t\t\t\t\trp_ge[$t.p.id].useDataProxy = true;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tret[0]=false;ret[1] += " "+$.jgrid.errors.nourl;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif (ret[0]) {\r\n
\t\t\t\t\t\t\tif (rp_ge[$t.p.id].useDataProxy) {\r\n
\t\t\t\t\t\t\t\tvar dpret = $t.p.dataProxy.call($t, ajaxOptions, "del_"+$t.p.id); \r\n
\t\t\t\t\t\t\t\tif(typeof(dpret) == "undefined") {\r\n
\t\t\t\t\t\t\t\t\tdpret = [true, ""];\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif(dpret[0] === false ) {\r\n
\t\t\t\t\t\t\t\t\tret[0] = false;\r\n
\t\t\t\t\t\t\t\t\tret[1] = dpret[1] || "Error deleting the selected row!" ;\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:p.jqModal, onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\telse {$.ajax(ajaxOptions);}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tif(ret[0] === false) {\r\n
\t\t\t\t\t\t$("#DelError>td","#"+dtbl).html(ret[1]);\r\n
\t\t\t\t\t\t$("#DelError","#"+dtbl).show();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#eData", "#"+dtbl+"_2").click(function(){\r\n
\t\t\t\t\t$.jgrid.hideModal("#"+$.jgrid.jqID(IDs.themodal),{gb:"#gbox_"+$.jgrid.jqID(gID),jqm:rp_ge[$t.p.id].jqModal, onClose: rp_ge[$t.p.id].onClose});\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t\tif(onBeforeShow) {rp_ge[$t.p.id].beforeShowForm.call($t,$("#"+dtbl));}\r\n
\t\t\t\t$.jgrid.viewModal("#"+$.jgrid.jqID(IDs.themodal),{gbox:"#gbox_"+$.jgrid.jqID(gID),jqm:rp_ge[$t.p.id].jqModal, overlay: rp_ge[$t.p.id].overlay, modal:rp_ge[$t.p.id].modal});\r\n
\t\t\t\tif(onAfterShow) {rp_ge[$t.p.id].afterShowForm.call($t,$("#"+dtbl));}\r\n
\t\t\t}\r\n
\t\t\tif(rp_ge[$t.p.id].closeOnEscape===true) {\r\n
\t\t\t\tsetTimeout(function(){$(".ui-jqdialog-titlebar-close","#"+$.jgrid.jqID(IDs.modalhead)).focus();},0);\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tnavGrid : function (elem, o, pEdit,pAdd,pDel,pSearch, pView) {\r\n
\t\to = $.extend({\r\n
\t\t\tedit: true,\r\n
\t\t\tediticon: "ui-icon-pencil",\r\n
\t\t\tadd: true,\r\n
\t\t\taddicon:"ui-icon-plus",\r\n
\t\t\tdel: true,\r\n
\t\t\tdelicon:"ui-icon-trash",\r\n
\t\t\tsearch: true,\r\n
\t\t\tsearchicon:"ui-icon-search",\r\n
\t\t\trefresh: true,\r\n
\t\t\trefreshicon:"ui-icon-refresh",\r\n
\t\t\trefreshstate: \'firstpage\',\r\n
\t\t\tview: false,\r\n
\t\t\tviewicon : "ui-icon-document",\r\n
\t\t\tposition : "left",\r\n
\t\t\tcloseOnEscape : true,\r\n
\t\t\tbeforeRefresh : null,\r\n
\t\t\tafterRefresh : null,\r\n
\t\t\tcloneToTop : false,\r\n
\t\t\talertwidth : 200,\r\n
\t\t\talertheight : \'auto\',\r\n
\t\t\talerttop: null,\r\n
\t\t\talertleft: null,\r\n
\t\t\talertzIndex : null\r\n
\t\t}, $.jgrid.nav, o ||{});\r\n
\t\treturn this.each(function() {\r\n
\t\t\tif(this.nav) {return;}\r\n
\t\t\tvar alertIDs = {themodal:\'alertmod\',modalhead:\'alerthd\',modalcontent:\'alertcnt\'},\r\n
\t\t\t$t = this, twd, tdw;\r\n
\t\t\tif(!$t.grid || typeof elem != \'string\') {return;}\r\n
\t\t\tif ($("#"+alertIDs.themodal)[0] === undefined) {\r\n
\t\t\t\tif(!o.alerttop && !o.alertleft) {\r\n
\t\t\t\t\tif (typeof window.innerWidth != \'undefined\') {\r\n
\t\t\t\t\t\to.alertleft = window.innerWidth;\r\n
\t\t\t\t\t\to.alerttop = window.innerHeight;\r\n
\t\t\t\t\t} else if (typeof document.documentElement != \'undefined\' && typeof document.documentElement.clientWidth != \'undefined\' && document.documentElement.clientWidth !== 0) {\r\n
\t\t\t\t\t\to.alertleft = document.documentElement.clientWidth;\r\n
\t\t\t\t\t\to.alerttop = document.documentElement.clientHeight;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\to.alertleft=1024;\r\n
\t\t\t\t\t\to.alerttop=768;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\to.alertleft = o.alertleft/2 - parseInt(o.alertwidth,10)/2;\r\n
\t\t\t\t\to.alerttop = o.alerttop/2-25;\r\n
\t\t\t\t}\r\n
\t\t\t\t$.jgrid.createModal(alertIDs,"<div>"+o.alerttext+"</div><span tabindex=\'0\'><span tabindex=\'-1\' id=\'jqg_alrt\'></span></span>",{gbox:"#gbox_"+$.jgrid.jqID($t.p.id),jqModal:true,drag:true,resize:true,caption:o.alertcap,top:o.alerttop,left:o.alertleft,width:o.alertwidth,height: o.alertheight,closeOnEscape:o.closeOnEscape, zIndex: o.alertzIndex},"","",true);\r\n
\t\t\t}\r\n
\t\t\tvar clone = 1;\r\n
\t\t\tif(o.cloneToTop && $t.p.toppager) {clone = 2;}\r\n
\t\t\tfor(var i = 0; i<clone; i++) {\r\n
\t\t\t\tvar tbd,\r\n
\t\t\t\tnavtbl = $("<table cellspacing=\'0\' cellpadding=\'0\' border=\'0\' class=\'ui-pg-table navtable\' style=\'float:left;table-layout:auto;\'><tbody><tr></tr></tbody></table>"),\r\n
\t\t\t\tsep = "<td class=\'ui-pg-button ui-state-disabled\' style=\'width:4px;\'><span class=\'ui-separator\'></span></td>",\r\n
\t\t\t\tpgid, elemids;\r\n
\t\t\t\tif(i===0) {\r\n
\t\t\t\t\tpgid = elem;\r\n
\t\t\t\t\telemids = $t.p.id;\r\n
\t\t\t\t\tif(pgid == $t.p.toppager) {\r\n
\t\t\t\t\t\telemids += "_top";\r\n
\t\t\t\t\t\tclone = 1;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tpgid = $t.p.toppager;\r\n
\t\t\t\t\telemids = $t.p.id+"_top";\r\n
\t\t\t\t}\r\n
\t\t\t\tif($t.p.direction == "rtl") {$(navtbl).attr("dir","rtl").css("float","right");}\r\n
\t\t\t\tif (o.add) {\r\n
\t\t\t\t\tpAdd = pAdd || {};\r\n
\t\t\t\t\ttbd = $("<td class=\'ui-pg-button ui-corner-all\'></td>");\r\n
\t\t\t\t\t$(tbd).append("<div class=\'ui-pg-div\'><span class=\'ui-icon "+o.addicon+"\'></span>"+o.addtext+"</div>");\r\n
\t\t\t\t\t$("tr",navtbl).append(tbd);\r\n
\t\t\t\t\t$(tbd,navtbl)\r\n
\t\t\t\t\t.attr({"title":o.addtitle || "",id : pAdd.id || "add_"+elemids})\r\n
\t\t\t\t\t.click(function(){\r\n
\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\tif ($.isFunction( o.addfunc )) {\r\n
\t\t\t\t\t\t\t\to.addfunc.call($t);\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid("editGridRow","new",pAdd);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}).hover(\r\n
\t\t\t\t\t\tfunction () {\r\n
\t\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\t\t$(this).addClass("ui-state-hover");\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t},\r\n
\t\t\t\t\t\tfunction () {$(this).removeClass("ui-state-hover");}\r\n
\t\t\t\t\t);\r\n
\t\t\t\t\ttbd = null;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (o.edit) {\r\n
\t\t\t\t\ttbd = $("<td class=\'ui-pg-button ui-corner-all\'></td>");\r\n
\t\t\t\t\tpEdit = pEdit || {};\r\n
\t\t\t\t\t$(tbd).append("<div class=\'ui-pg-div\'><span class=\'ui-icon "+o.editicon+"\'></span>"+o.edittext+"</div>");\r\n
\t\t\t\t\t$("tr",navtbl).append(tbd);\r\n
\t\t\t\t\t$(tbd,navtbl)\r\n
\t\t\t\t\t.attr({"title":o.edittitle || "",id: pEdit.id || "edit_"+elemids})\r\n
\t\t\t\t\t.click(function(){\r\n
\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\tvar sr = $t.p.selrow;\r\n
\t\t\t\t\t\t\tif (sr) {\r\n
\t\t\t\t\t\t\t\tif($.isFunction( o.editfunc ) ) {\r\n
\t\t\t\t\t\t\t\t\to.editfunc.call($t, sr);\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("editGridRow",sr,pEdit);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$.jgrid.viewModal("#"+alertIDs.themodal,{gbox:"#gbox_"+$.jgrid.jqID($t.p.id),jqm:true});\r\n
\t\t\t\t\t\t\t\t$("#jqg_alrt").focus();\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}).hover(\r\n
\t\t\t\t\t\tfunction () {\r\n
\t\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\t\t$(this).addClass("ui-state-hover");\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t},\r\n
\t\t\t\t\t\tfunction () {$(this).removeClass("ui-state-hover");}\r\n
\t\t\t\t\t);\r\n
\t\t\t\t\ttbd = null;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (o.view) {\r\n
\t\t\t\t\ttbd = $("<td class=\'ui-pg-button ui-corner-all\'></td>");\r\n
\t\t\t\t\tpView = pView || {};\r\n
\t\t\t\t\t$(tbd).append("<div class=\'ui-pg-div\'><span class=\'ui-icon "+o.viewicon+"\'></span>"+o.viewtext+"</div>");\r\n
\t\t\t\t\t$("tr",navtbl).append(tbd);\r\n
\t\t\t\t\t$(tbd,navtbl)\r\n
\t\t\t\t\t.attr({"title":o.viewtitle || "",id: pView.id || "view_"+elemids})\r\n
\t\t\t\t\t.click(function(){\r\n
\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\tvar sr = $t.p.selrow;\r\n
\t\t\t\t\t\t\tif (sr) {\r\n
\t\t\t\t\t\t\t\tif($.isFunction( o.viewfunc ) ) {\r\n
\t\t\t\t\t\t\t\t\to.viewfunc.call($t, sr);\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("viewGridRow",sr,pView);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$.jgrid.viewModal("#"+alertIDs.themodal,{gbox:"#gbox_"+$.jgrid.jqID($t.p.id),jqm:true});\r\n
\t\t\t\t\t\t\t\t$("#jqg_alrt").focus();\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}).hover(\r\n
\t\t\t\t\t\tfunction () {\r\n
\t\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\t\t$(this).addClass("ui-state-hover");\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t},\r\n
\t\t\t\t\t\tfunction () {$(this).removeClass("ui-state-hover");}\r\n
\t\t\t\t\t);\r\n
\t\t\t\t\ttbd = null;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (o.del) {\r\n
\t\t\t\t\ttbd = $("<td class=\'ui-pg-button ui-corner-all\'></td>");\r\n
\t\t\t\t\tpDel = pDel || {};\r\n
\t\t\t\t\t$(tbd).append("<div class=\'ui-pg-div\'><span class=\'ui-icon "+o.delicon+"\'></span>"+o.deltext+"</div>");\r\n
\t\t\t\t\t$("tr",navtbl).append(tbd);\r\n
\t\t\t\t\t$(tbd,navtbl)\r\n
\t\t\t\t\t.attr({"title":o.deltitle || "",id: pDel.id || "del_"+elemids})\r\n
\t\t\t\t\t.click(function(){\r\n
\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\tvar dr;\r\n
\t\t\t\t\t\t\tif($t.p.multiselect) {\r\n
\t\t\t\t\t\t\t\tdr = $t.p.selarrrow;\r\n
\t\t\t\t\t\t\t\tif(dr.length===0) {dr = null;}\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tdr = $t.p.selrow;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(dr){\r\n
\t\t\t\t\t\t\t\tif($.isFunction( o.delfunc )){\r\n
\t\t\t\t\t\t\t\t\to.delfunc.call($t, dr);\r\n
\t\t\t\t\t\t\t\t}else{\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("delGridRow",dr,pDel);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t} else  {\r\n
\t\t\t\t\t\t\t\t$.jgrid.viewModal("#"+alertIDs.themodal,{gbox:"#gbox_"+$.jgrid.jqID($t.p.id),jqm:true});$("#jqg_alrt").focus();\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}).hover(\r\n
\t\t\t\t\t\tfunction () {\r\n
\t\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\t\t$(this).addClass("ui-state-hover");\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t},\r\n
\t\t\t\t\t\tfunction () {$(this).removeClass("ui-state-hover");}\r\n
\t\t\t\t\t);\r\n
\t\t\t\t\ttbd = null;\r\n
\t\t\t\t}\r\n
\t\t\t\tif(o.add || o.edit || o.del || o.view) {$("tr",navtbl).append(sep);}\r\n
\t\t\t\tif (o.search) {\r\n
\t\t\t\t\ttbd = $("<td class=\'ui-pg-button ui-corner-all\'></td>");\r\n
\t\t\t\t\tpSearch = pSearch || {};\r\n
\t\t\t\t\t$(tbd).append("<div class=\'ui-pg-div\'><span class=\'ui-icon "+o.searchicon+"\'></span>"+o.searchtext+"</div>");\r\n
\t\t\t\t\t$("tr",navtbl).append(tbd);\r\n
\t\t\t\t\t$(tbd,navtbl)\r\n
\t\t\t\t\t.attr({"title":o.searchtitle  || "",id:pSearch.id || "search_"+elemids})\r\n
\t\t\t\t\t.click(function(){\r\n
\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\tif($.isFunction( o.searchfunc )) {\r\n
\t\t\t\t\t\t\t\to.searchfunc.call($t, pSearch);\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid("searchGrid",pSearch);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}).hover(\r\n
\t\t\t\t\t\tfunction () {\r\n
\t\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\t\t$(this).addClass("ui-state-hover");\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t},\r\n
\t\t\t\t\t\tfunction () {$(this).removeClass("ui-state-hover");}\r\n
\t\t\t\t\t);\r\n
\t\t\t\t\tif (pSearch.showOnLoad && pSearch.showOnLoad === true) {\r\n
\t\t\t\t\t\t$(tbd,navtbl).click();\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\ttbd = null;\r\n
\t\t\t\t}\r\n
\t\t\t\tif (o.refresh) {\r\n
\t\t\t\t\ttbd = $("<td class=\'ui-pg-button ui-corner-all\'></td>");\r\n
\t\t\t\t\t$(tbd).append("<div class=\'ui-pg-div\'><span class=\'ui-icon "+o.refreshicon+"\'></span>"+o.refreshtext+"</div>");\r\n
\t\t\t\t\t$("tr",navtbl).append(tbd);\r\n
\t\t\t\t\t$(tbd,navtbl)\r\n
\t\t\t\t\t.attr({"title":o.refreshtitle  || "",id: "refresh_"+elemids})\r\n
\t\t\t\t\t.click(function(){\r\n
\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\tif($.isFunction(o.beforeRefresh)) {o.beforeRefresh.call($t);}\r\n
\t\t\t\t\t\t\t$t.p.search = false;\r\n
\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\tvar gID = $t.p.id;\r\n
\t\t\t\t\t\t\t\t$t.p.postData.filters ="";\r\n
\t\t\t\t\t\t\t\t$("#fbox_"+$.jgrid.jqID(gID)).jqFilter(\'resetFilter\');\r\n
\t\t\t\t\t\t\t\tif($.isFunction($t.clearToolbar)) {$t.clearToolbar.call($t,false);}\r\n
\t\t\t\t\t\t\t} catch (e) {}\r\n
\t\t\t\t\t\t\tswitch (o.refreshstate) {\r\n
\t\t\t\t\t\t\t\tcase \'firstpage\':\r\n
\t\t\t\t\t\t\t\t\t$($t).trigger("reloadGrid", [{page:1}]);\r\n
\t\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t\tcase \'current\':\r\n
\t\t\t\t\t\t\t\t\t$($t).trigger("reloadGrid", [{current:true}]);\r\n
\t\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif($.isFunction(o.afterRefresh)) {o.afterRefresh.call($t);}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}).hover(\r\n
\t\t\t\t\t\tfunction () {\r\n
\t\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\t\t$(this).addClass("ui-state-hover");\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t},\r\n
\t\t\t\t\t\tfunction () {$(this).removeClass("ui-state-hover");}\r\n
\t\t\t\t\t);\r\n
\t\t\t\t\ttbd = null;\r\n
\t\t\t\t}\r\n
\t\t\t\ttdw = $(".ui-jqgrid").css("font-size") || "11px";\r\n
\t\t\t\t$(\'body\').append("<div id=\'testpg2\' class=\'ui-jqgrid ui-widget ui-widget-content\' style=\'font-size:"+tdw+";visibility:hidden;\' ></div>");\r\n
\t\t\t\ttwd = $(navtbl).clone().appendTo("#testpg2").width();\r\n
\t\t\t\t$("#testpg2").remove();\r\n
\t\t\t\t$(pgid+"_"+o.position,pgid).append(navtbl);\r\n
\t\t\t\tif($t.p._nvtd) {\r\n
\t\t\t\t\tif(twd > $t.p._nvtd[0] ) {\r\n
\t\t\t\t\t\t$(pgid+"_"+o.position,pgid).width(twd);\r\n
\t\t\t\t\t\t$t.p._nvtd[0] = twd;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$t.p._nvtd[1] = twd;\r\n
\t\t\t\t}\r\n
\t\t\t\ttdw =null;twd=null;navtbl =null;\r\n
\t\t\t\tthis.nav = true;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tnavButtonAdd : function (elem, p) {\r\n
\t\tp = $.extend({\r\n
\t\t\tcaption : "newButton",\r\n
\t\t\ttitle: \'\',\r\n
\t\t\tbuttonicon : \'ui-icon-newwin\',\r\n
\t\t\tonClickButton: null,\r\n
\t\t\tposition : "last",\r\n
\t\t\tcursor : \'pointer\'\r\n
\t\t}, p ||{});\r\n
\t\treturn this.each(function() {\r\n
\t\t\tif( !this.grid)  {return;}\r\n
\t\t\tif( typeof elem === "string" && elem.indexOf("#") !== 0) {elem = "#"+$.jgrid.jqID(elem);}\r\n
\t\t\tvar findnav = $(".navtable",elem)[0], $t = this;\r\n
\t\t\tif (findnav) {\r\n
\t\t\t\tif( p.id && $("#"+$.jgrid.jqID(p.id), findnav)[0] !== undefined )  {return;}\r\n
\t\t\t\tvar tbd = $("<td></td>");\r\n
\t\t\t\tif(p.buttonicon.toString().toUpperCase() == "NONE") {\r\n
                    $(tbd).addClass(\'ui-pg-button ui-corner-all\').append("<div class=\'ui-pg-div\'>"+p.caption+"</div>");\r\n
\t\t\t\t} else\t{\r\n
\t\t\t\t\t$(tbd).addClass(\'ui-pg-button ui-corner-all\').append("<div class=\'ui-pg-div\'><span class=\'ui-icon "+p.buttonicon+"\'></span>"+p.caption+"</div>");\r\n
\t\t\t\t}\r\n
\t\t\t\tif(p.id) {$(tbd).attr("id",p.id);}\r\n
\t\t\t\tif(p.position==\'first\'){\r\n
\t\t\t\t\tif(findnav.rows[0].cells.length ===0 ) {\r\n
\t\t\t\t\t\t$("tr",findnav).append(tbd);\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$("tr td:eq(0)",findnav).before(tbd);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$("tr",findnav).append(tbd);\r\n
\t\t\t\t}\r\n
\t\t\t\t$(tbd,findnav)\r\n
\t\t\t\t.attr("title",p.title  || "")\r\n
\t\t\t\t.click(function(e){\r\n
\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\tif ($.isFunction(p.onClickButton) ) {p.onClickButton.call($t,e);}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t})\r\n
\t\t\t\t.hover(\r\n
\t\t\t\t\tfunction () {\r\n
\t\t\t\t\t\tif (!$(this).hasClass(\'ui-state-disabled\')) {\r\n
\t\t\t\t\t\t\t$(this).addClass(\'ui-state-hover\');\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t},\r\n
\t\t\t\t\tfunction () {$(this).removeClass("ui-state-hover");}\r\n
\t\t\t\t);\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tnavSeparatorAdd:function (elem,p) {\r\n
\t\tp = $.extend({\r\n
\t\t\tsepclass : "ui-separator",\r\n
\t\t\tsepcontent: \'\'\r\n
\t\t}, p ||{});\r\n
\t\treturn this.each(function() {\r\n
\t\t\tif( !this.grid)  {return;}\r\n
\t\t\tif( typeof elem === "string" && elem.indexOf("#") !== 0) {elem = "#"+$.jgrid.jqID(elem);}\r\n
\t\t\tvar findnav = $(".navtable",elem)[0];\r\n
\t\t\tif(findnav) {\r\n
\t\t\t\tvar sep = "<td class=\'ui-pg-button ui-state-disabled\' style=\'width:4px;\'><span class=\'"+p.sepclass+"\'></span>"+p.sepcontent+"</td>";\r\n
\t\t\t\t$("tr",findnav).append(sep);\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tGridToForm : function( rowid, formid ) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif (!$t.grid) {return;}\r\n
\t\t\tvar rowdata = $($t).jqGrid("getRowData",rowid);\r\n
\t\t\tif (rowdata) {\r\n
\t\t\t\tfor(var i in rowdata) {\r\n
\t\t\t\t\tif ( $("[name="+$.jgrid.jqID(i)+"]",formid).is("input:radio") || $("[name="+$.jgrid.jqID(i)+"]",formid).is("input:checkbox"))  {\r\n
\t\t\t\t\t\t$("[name="+$.jgrid.jqID(i)+"]",formid).each( function() {\r\n
\t\t\t\t\t\t\tif( $(this).val() == rowdata[i] ) {\r\n
\t\t\t\t\t\t\t\t$(this)[$t.p.useProp ? \'prop\': \'attr\']("checked",true);\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$(this)[$t.p.useProp ? \'prop\': \'attr\']("checked", false);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t// this is very slow on big table and form.\r\n
\t\t\t\t\t\t$("[name="+$.jgrid.jqID(i)+"]",formid).val(rowdata[i]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tFormToGrid : function(rowid, formid, mode, position){\r\n
\t\treturn this.each(function() {\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid) {return;}\r\n
\t\t\tif(!mode) {mode = \'set\';}\r\n
\t\t\tif(!position) {position = \'first\';}\r\n
\t\t\tvar fields = $(formid).serializeArray();\r\n
\t\t\tvar griddata = {};\r\n
\t\t\t$.each(fields, function(i, field){\r\n
\t\t\t\tgriddata[field.name] = field.value;\r\n
\t\t\t});\r\n
\t\t\tif(mode==\'add\') {$($t).jqGrid("addRowData",rowid,griddata, position);}\r\n
\t\t\telse if(mode==\'set\') {$($t).jqGrid("setRowData",rowid,griddata);}\r\n
\t\t});\r\n
\t}\r\n
});\r\n
})(jQuery);\r\n
;(function($){\r\n
/**\r\n
 * jqGrid extension for manipulating Grid Data\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/ \r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
**/ \r\n
//jsHint options\r\n
/*global alert, $, jQuery */\r\n
"use strict";\r\n
$.jgrid.inlineEdit = $.jgrid.inlineEdit || {};\r\n
$.jgrid.extend({\r\n
//Editing\r\n
\teditRow : function(rowid,keys,oneditfunc,successfunc, url, extraparam, aftersavefunc,errorfunc, afterrestorefunc) {\r\n
\t\t// Compatible mode old versions\r\n
\t\tvar o={}, args = $.makeArray(arguments).slice(1);\r\n
\r\n
\t\tif( $.type(args[0]) === "object" ) {\r\n
\t\t\to = args[0];\r\n
\t\t} else {\r\n
\t\t\tif (typeof keys !== "undefined") { o.keys = keys; }\r\n
\t\t\tif ($.isFunction(oneditfunc)) { o.oneditfunc = oneditfunc; }\r\n
\t\t\tif ($.isFunction(successfunc)) { o.successfunc = successfunc; }\r\n
\t\t\tif (typeof url !== "undefined") { o.url = url; }\r\n
\t\t\tif (typeof extraparam !== "undefined") { o.extraparam = extraparam; }\r\n
\t\t\tif ($.isFunction(aftersavefunc)) { o.aftersavefunc = aftersavefunc; }\r\n
\t\t\tif ($.isFunction(errorfunc)) { o.errorfunc = errorfunc; }\r\n
\t\t\tif ($.isFunction(afterrestorefunc)) { o.afterrestorefunc = afterrestorefunc; }\r\n
\t\t\t// last two not as param, but as object (sorry)\r\n
\t\t\t//if (typeof restoreAfterError !== "undefined") { o.restoreAfterError = restoreAfterError; }\r\n
\t\t\t//if (typeof mtype !== "undefined") { o.mtype = mtype || "POST"; }\t\t\t\r\n
\t\t}\r\n
\t\to = $.extend(true, {\r\n
\t\t\tkeys : false,\r\n
\t\t\toneditfunc: null,\r\n
\t\t\tsuccessfunc: null,\r\n
\t\t\turl: null,\r\n
\t\t\textraparam: {},\r\n
\t\t\taftersavefunc: null,\r\n
\t\t\terrorfunc: null,\r\n
\t\t\tafterrestorefunc: null,\r\n
\t\t\trestoreAfterError: true,\r\n
\t\t\tmtype: "POST"\r\n
\t\t}, $.jgrid.inlineEdit, o );\r\n
\r\n
\t\t// End compatible\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this, nm, tmp, editable, cnt=0, focus=null, svr={}, ind,cm;\r\n
\t\t\tif (!$t.grid ) { return; }\r\n
\t\t\tind = $($t).jqGrid("getInd",rowid,true);\r\n
\t\t\tif( ind === false ) {return;}\r\n
\t\t\teditable = $(ind).attr("editable") || "0";\r\n
\t\t\tif (editable == "0" && !$(ind).hasClass("not-editable-row")) {\r\n
\t\t\t\tcm = $t.p.colModel;\r\n
\t\t\t\t$(\'td[role="gridcell"]\',ind).each( function(i) {\r\n
\t\t\t\t\tnm = cm[i].name;\r\n
\t\t\t\t\tvar treeg = $t.p.treeGrid===true && nm == $t.p.ExpandColumn;\r\n
\t\t\t\t\tif(treeg) { tmp = $("span:first",this).html();}\r\n
\t\t\t\t\telse {\r\n
\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\ttmp = $.unformat.call($t,this,{rowId:rowid, colModel:cm[i]},i);\r\n
\t\t\t\t\t\t} catch (_) {\r\n
\t\t\t\t\t\t\ttmp =  ( cm[i].edittype && cm[i].edittype == \'textarea\' ) ? $(this).text() : $(this).html();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif ( nm != \'cb\' && nm != \'subgrid\' && nm != \'rn\') {\r\n
\t\t\t\t\t\tif($t.p.autoencode) { tmp = $.jgrid.htmlDecode(tmp); }\r\n
\t\t\t\t\t\tsvr[nm]=tmp;\r\n
\t\t\t\t\t\tif(cm[i].editable===true) {\r\n
\t\t\t\t\t\t\tif(focus===null) { focus = i; }\r\n
\t\t\t\t\t\t\tif (treeg) { $("span:first",this).html(""); }\r\n
\t\t\t\t\t\t\telse { $(this).html(""); }\r\n
\t\t\t\t\t\t\tvar opt = $.extend({},cm[i].editoptions || {},{id:rowid+"_"+nm,name:nm});\r\n
\t\t\t\t\t\t\tif(!cm[i].edittype) { cm[i].edittype = "text"; }\r\n
\t\t\t\t\t\t\tif(tmp == "&nbsp;" || tmp == "&#160;" || (tmp.length==1 && tmp.charCodeAt(0)==160) ) {tmp=\'\';}\r\n
\t\t\t\t\t\t\tvar elc = $.jgrid.createEl.call($t,cm[i].edittype,opt,tmp,true,$.extend({},$.jgrid.ajaxOptions,$t.p.ajaxSelectOptions || {}));\r\n
\t\t\t\t\t\t\t$(elc).addClass("editable");\r\n
\t\t\t\t\t\t\tif(treeg) { $("span:first",this).append(elc); }\r\n
\t\t\t\t\t\t\telse { $(this).append(elc); }\r\n
\t\t\t\t\t\t\t//Again IE\r\n
\t\t\t\t\t\t\tif(cm[i].edittype == "select" && typeof(cm[i].editoptions)!=="undefined" && cm[i].editoptions.multiple===true  && typeof(cm[i].editoptions.dataUrl)==="undefined" && $.browser.msie) {\r\n
\t\t\t\t\t\t\t\t$(elc).width($(elc).width());\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tcnt++;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\tif(cnt > 0) {\r\n
\t\t\t\t\tsvr.id = rowid; $t.p.savedRow.push(svr);\r\n
\t\t\t\t\t$(ind).attr("editable","1");\r\n
\t\t\t\t\t$("td:eq("+focus+") input",ind).focus();\r\n
\t\t\t\t\tif(o.keys===true) {\r\n
\t\t\t\t\t\t$(ind).bind("keydown",function(e) {\r\n
\t\t\t\t\t\t\tif (e.keyCode === 27) {\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid("restoreRow",rowid, o.afterrestorefunc);\r\n
\t\t\t\t\t\t\t\tif($t.p._inlinenav) {\r\n
\t\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\t\t$($t).jqGrid(\'showAddEditButtons\');\r\n
\t\t\t\t\t\t\t\t\t} catch (eer1) {}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif (e.keyCode === 13) {\r\n
\t\t\t\t\t\t\t\tvar ta = e.target;\r\n
\t\t\t\t\t\t\t\tif(ta.tagName == \'TEXTAREA\') { return true; }\r\n
\t\t\t\t\t\t\t\tif( $($t).jqGrid("saveRow", rowid, o ) ) {\r\n
\t\t\t\t\t\t\t\t\tif($t.p._inlinenav) {\r\n
\t\t\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid(\'showAddEditButtons\');\r\n
\t\t\t\t\t\t\t\t\t\t} catch (eer2) {}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$($t).triggerHandler("jqGridInlineEditRow", [rowid, o]);\r\n
\t\t\t\t\tif( $.isFunction(o.oneditfunc)) { o.oneditfunc.call($t, rowid); }\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tsaveRow : function(rowid, successfunc, url, extraparam, aftersavefunc,errorfunc, afterrestorefunc) {\r\n
\t\t// Compatible mode old versions\r\n
\t\tvar args = $.makeArray(arguments).slice(1), o = {};\r\n
\r\n
\t\tif( $.type(args[0]) === "object" ) {\r\n
\t\t\to = args[0];\r\n
\t\t} else {\r\n
\t\t\tif ($.isFunction(successfunc)) { o.successfunc = successfunc; }\r\n
\t\t\tif (typeof url !== "undefined") { o.url = url; }\r\n
\t\t\tif (typeof extraparam !== "undefined") { o.extraparam = extraparam; }\r\n
\t\t\tif ($.isFunction(aftersavefunc)) { o.aftersavefunc = aftersavefunc; }\r\n
\t\t\tif ($.isFunction(errorfunc)) { o.errorfunc = errorfunc; }\r\n
\t\t\tif ($.isFunction(afterrestorefunc)) { o.afterrestorefunc = afterrestorefunc; }\r\n
\t\t}\r\n
\t\to = $.extend(true, {\r\n
\t\t\tsuccessfunc: null,\r\n
\t\t\turl: null,\r\n
\t\t\textraparam: {},\r\n
\t\t\taftersavefunc: null,\r\n
\t\t\terrorfunc: null,\r\n
\t\t\tafterrestorefunc: null,\r\n
\t\t\trestoreAfterError: true,\r\n
\t\t\tmtype: "POST"\r\n
\t\t}, $.jgrid.inlineEdit, o );\r\n
\t\t// End compatible\r\n
\r\n
\t\tvar success = false;\r\n
\t\tvar $t = this[0], nm, tmp={}, tmp2={}, tmp3= {}, editable, fr, cv, ind;\r\n
\t\tif (!$t.grid ) { return success; }\r\n
\t\tind = $($t).jqGrid("getInd",rowid,true);\r\n
\t\tif(ind === false) {return success;}\r\n
\t\teditable = $(ind).attr("editable");\r\n
\t\to.url = o.url ? o.url : $t.p.editurl;\r\n
\t\tif (editable==="1") {\r\n
\t\t\tvar cm;\r\n
\t\t\t$(\'td[role="gridcell"]\',ind).each(function(i) {\r\n
\t\t\t\tcm = $t.p.colModel[i];\r\n
\t\t\t\tnm = cm.name;\r\n
\t\t\t\tif ( nm != \'cb\' && nm != \'subgrid\' && cm.editable===true && nm != \'rn\' && !$(this).hasClass(\'not-editable-cell\')) {\r\n
\t\t\t\t\tswitch (cm.edittype) {\r\n
\t\t\t\t\t\tcase "checkbox":\r\n
\t\t\t\t\t\t\tvar cbv = ["Yes","No"];\r\n
\t\t\t\t\t\t\tif(cm.editoptions ) {\r\n
\t\t\t\t\t\t\t\tcbv = cm.editoptions.value.split(":");\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\ttmp[nm]=  $("input",this).is(":checked") ? cbv[0] : cbv[1]; \r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase \'text\':\r\n
\t\t\t\t\t\tcase \'password\':\r\n
\t\t\t\t\t\tcase \'textarea\':\r\n
\t\t\t\t\t\tcase "button" :\r\n
\t\t\t\t\t\t\ttmp[nm]=$("input, textarea",this).val();\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase \'select\':\r\n
\t\t\t\t\t\t\tif(!cm.editoptions.multiple) {\r\n
\t\t\t\t\t\t\t\ttmp[nm] = $("select option:selected",this).val();\r\n
\t\t\t\t\t\t\t\ttmp2[nm] = $("select option:selected", this).text();\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tvar sel = $("select",this), selectedText = [];\r\n
\t\t\t\t\t\t\t\ttmp[nm] = $(sel).val();\r\n
\t\t\t\t\t\t\t\tif(tmp[nm]) { tmp[nm]= tmp[nm].join(","); } else { tmp[nm] =""; }\r\n
\t\t\t\t\t\t\t\t$("select option:selected",this).each(\r\n
\t\t\t\t\t\t\t\t\tfunction(i,selected){\r\n
\t\t\t\t\t\t\t\t\t\tselectedText[i] = $(selected).text();\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t);\r\n
\t\t\t\t\t\t\t\ttmp2[nm] = selectedText.join(",");\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(cm.formatter && cm.formatter == \'select\') { tmp2={}; }\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\tcase \'custom\' :\r\n
\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\tif(cm.editoptions && $.isFunction(cm.editoptions.custom_value)) {\r\n
\t\t\t\t\t\t\t\t\ttmp[nm] = cm.editoptions.custom_value.call($t, $(".customelement",this),\'get\');\r\n
\t\t\t\t\t\t\t\t\tif (tmp[nm] === undefined) { throw "e2"; }\r\n
\t\t\t\t\t\t\t\t} else { throw "e1"; }\r\n
\t\t\t\t\t\t\t} catch (e) {\r\n
\t\t\t\t\t\t\t\tif (e=="e1") { $.jgrid.info_dialog($.jgrid.errors.errcap,"function \'custom_value\' "+$.jgrid.edit.msg.nodefined,$.jgrid.edit.bClose); }\r\n
\t\t\t\t\t\t\t\tif (e=="e2") { $.jgrid.info_dialog($.jgrid.errors.errcap,"function \'custom_value\' "+$.jgrid.edit.msg.novalue,$.jgrid.edit.bClose); }\r\n
\t\t\t\t\t\t\t\telse { $.jgrid.info_dialog($.jgrid.errors.errcap,e.message,$.jgrid.edit.bClose); }\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tcv = $.jgrid.checkValues(tmp[nm],i,$t);\r\n
\t\t\t\t\tif(cv[0] === false) {\r\n
\t\t\t\t\t\tcv[1] = tmp[nm] + " " + cv[1];\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif($t.p.autoencode) { tmp[nm] = $.jgrid.htmlEncode(tmp[nm]); }\r\n
\t\t\t\t\tif(o.url !== \'clientArray\' && cm.editoptions && cm.editoptions.NullIfEmpty === true) {\r\n
\t\t\t\t\t\tif(tmp[nm] === "") {\r\n
\t\t\t\t\t\t\ttmp3[nm] = \'null\';\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\tif (cv[0] === false){\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\tvar positions = $.jgrid.findPos($("#"+$.jgrid.jqID(rowid), $t.grid.bDiv)[0]);\r\n
\t\t\t\t\t$.jgrid.info_dialog($.jgrid.errors.errcap,cv[1],$.jgrid.edit.bClose,{left:positions[0],top:positions[1]});\r\n
\t\t\t\t} catch (e) {\r\n
\t\t\t\t\talert(cv[1]);\r\n
\t\t\t\t}\r\n
\t\t\t\treturn success;\r\n
\t\t\t}\r\n
\t\t\tvar idname, opers, oper;\r\n
\t\t\topers = $t.p.prmNames;\r\n
\t\t\toper = opers.oper;\r\n
\t\t\tidname = opers.id;\r\n
\t\t\tif(tmp) {\r\n
\t\t\t\ttmp[oper] = opers.editoper;\r\n
\t\t\t\ttmp[idname] = rowid;\r\n
\t\t\t\tif(typeof($t.p.inlineData) == \'undefined\') { $t.p.inlineData ={}; }\r\n
\t\t\t\ttmp = $.extend({},tmp,$t.p.inlineData,o.extraparam);\r\n
\t\t\t}\r\n
\t\t\tif (o.url == \'clientArray\') {\r\n
\t\t\t\ttmp = $.extend({},tmp, tmp2);\r\n
\t\t\t\tif($t.p.autoencode) {\r\n
\t\t\t\t\t$.each(tmp,function(n,v){\r\n
\t\t\t\t\t\ttmp[n] = $.jgrid.htmlDecode(v);\r\n
\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\tvar resp = $($t).jqGrid("setRowData",rowid,tmp);\r\n
\t\t\t\t$(ind).attr("editable","0");\r\n
\t\t\t\tfor( var k=0;k<$t.p.savedRow.length;k++) {\r\n
\t\t\t\t\tif( $t.p.savedRow[k].id == rowid) {fr = k; break;}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(fr >= 0) { $t.p.savedRow.splice(fr,1); }\r\n
\t\t\t\t$($t).triggerHandler("jqGridInlineAfterSaveRow", [rowid, resp, tmp, o]);\r\n
\t\t\t\tif( $.isFunction(o.aftersavefunc) ) { o.aftersavefunc.call($t, rowid,resp, o); }\r\n
\t\t\t\tsuccess = true;\r\n
\t\t\t\t$(ind).unbind("keydown");\r\n
\t\t\t} else {\r\n
\t\t\t\t$("#lui_"+$.jgrid.jqID($t.p.id)).show();\r\n
\t\t\t\ttmp3 = $.extend({},tmp,tmp3);\r\n
\t\t\t\ttmp3[idname] = $.jgrid.stripPref($t.p.idPrefix, tmp3[idname]);\r\n
\t\t\t\t$.ajax($.extend({\r\n
\t\t\t\t\turl:o.url,\r\n
\t\t\t\t\tdata: $.isFunction($t.p.serializeRowData) ? $t.p.serializeRowData.call($t, tmp3) : tmp3,\r\n
\t\t\t\t\ttype: o.mtype,\r\n
\t\t\t\t\tasync : false, //?!?\r\n
\t\t\t\t\tcomplete: function(res,stat){\r\n
\t\t\t\t\t\t$("#lui_"+$.jgrid.jqID($t.p.id)).hide();\r\n
\t\t\t\t\t\tif (stat === "success"){\r\n
\t\t\t\t\t\t\tvar ret = true, sucret;\r\n
\t\t\t\t\t\t\tsucret = $($t).triggerHandler("jqGridInlineSuccessSaveRow", [res, rowid, o]);\r\n
\t\t\t\t\t\t\tif (!$.isArray(sucret)) {sucret = [true, tmp];}\r\n
\t\t\t\t\t\t\tif (sucret[0] && $.isFunction(o.successfunc)) {sucret = o.successfunc.call($t, res);}\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t\tif($.isArray(sucret)) {\r\n
\t\t\t\t\t\t\t\t// expect array - status, data, rowid\r\n
\t\t\t\t\t\t\t\tret = sucret[0];\r\n
\t\t\t\t\t\t\t\ttmp = sucret[1] ? sucret[1] : tmp;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tret = sucret;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif (ret===true) {\r\n
\t\t\t\t\t\t\t\tif($t.p.autoencode) {\r\n
\t\t\t\t\t\t\t\t\t$.each(tmp,function(n,v){\r\n
\t\t\t\t\t\t\t\t\t\ttmp[n] = $.jgrid.htmlDecode(v);\r\n
\t\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\ttmp = $.extend({},tmp, tmp2);\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid("setRowData",rowid,tmp);\r\n
\t\t\t\t\t\t\t\t$(ind).attr("editable","0");\r\n
\t\t\t\t\t\t\t\tfor( var k=0;k<$t.p.savedRow.length;k++) {\r\n
\t\t\t\t\t\t\t\t\tif( $t.p.savedRow[k].id == rowid) {fr = k; break;}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif(fr >= 0) { $t.p.savedRow.splice(fr,1); }\r\n
\t\t\t\t\t\t\t\t$($t).triggerHandler("jqGridInlineAfterSaveRow", [rowid, res, tmp, o]);\r\n
\t\t\t\t\t\t\t\tif( $.isFunction(o.aftersavefunc) ) { o.aftersavefunc.call($t, rowid,res); }\r\n
\t\t\t\t\t\t\t\tsuccess = true;\r\n
\t\t\t\t\t\t\t\t$(ind).unbind("keydown");\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$($t).triggerHandler("jqGridInlineErrorSaveRow", [rowid, res, stat, null, o]);\r\n
\t\t\t\t\t\t\t\tif($.isFunction(o.errorfunc) ) {\r\n
\t\t\t\t\t\t\t\t\to.errorfunc.call($t, rowid, res, stat, null);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tif(o.restoreAfterError === true) {\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("restoreRow",rowid, o.afterrestorefunc);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t},\r\n
\t\t\t\t\terror:function(res,stat,err){\r\n
\t\t\t\t\t\t$("#lui_"+$.jgrid.jqID($t.p.id)).hide();\r\n
\t\t\t\t\t\t$($t).triggerHandler("jqGridInlineErrorSaveRow", [rowid, res, stat, err, o]);\r\n
\t\t\t\t\t\tif($.isFunction(o.errorfunc) ) {\r\n
\t\t\t\t\t\t\to.errorfunc.call($t, rowid, res, stat, err);\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tvar rT = res.responseText || res.statusText;\r\n
\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t$.jgrid.info_dialog($.jgrid.errors.errcap,\'<div class="ui-state-error">\'+ rT +\'</div>\', $.jgrid.edit.bClose,{buttonalign:\'right\'});\r\n
\t\t\t\t\t\t\t} catch(e) {\r\n
\t\t\t\t\t\t\t\talert(rT);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(o.restoreAfterError === true) {\r\n
\t\t\t\t\t\t\t$($t).jqGrid("restoreRow",rowid, o.afterrestorefunc);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}, $.jgrid.ajaxOptions, $t.p.ajaxRowOptions || {}));\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\treturn success;\r\n
\t},\r\n
\trestoreRow : function(rowid, afterrestorefunc) {\r\n
\t\t// Compatible mode old versions\r\n
\t\tvar args = $.makeArray(arguments).slice(1), o={};\r\n
\r\n
\t\tif( $.type(args[0]) === "object" ) {\r\n
\t\t\to = args[0];\r\n
\t\t} else {\r\n
\t\t\tif ($.isFunction(afterrestorefunc)) { o.afterrestorefunc = afterrestorefunc; }\r\n
\t\t}\r\n
\t\to = $.extend(true, $.jgrid.inlineEdit, o );\r\n
\r\n
\t\t// End compatible\r\n
\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t= this, fr, ind, ares={};\r\n
\t\t\tif (!$t.grid ) { return; }\r\n
\t\t\tind = $($t).jqGrid("getInd",rowid,true);\r\n
\t\t\tif(ind === false) {return;}\r\n
\t\t\tfor( var k=0;k<$t.p.savedRow.length;k++) {\r\n
\t\t\t\tif( $t.p.savedRow[k].id == rowid) {fr = k; break;}\r\n
\t\t\t}\r\n
\t\t\tif(fr >= 0) {\r\n
\t\t\t\tif($.isFunction($.fn.datepicker)) {\r\n
\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t$("input.hasDatepicker","#"+$.jgrid.jqID(ind.id)).datepicker(\'hide\');\r\n
\t\t\t\t\t} catch (e) {}\r\n
\t\t\t\t}\r\n
\t\t\t\t$.each($t.p.colModel, function(){\r\n
\t\t\t\t\tif(this.editable === true && this.name in $t.p.savedRow[fr] ) {\r\n
\t\t\t\t\t\tares[this.name] = $t.p.savedRow[fr][this.name];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\t$($t).jqGrid("setRowData",rowid,ares);\r\n
\t\t\t\t$(ind).attr("editable","0").unbind("keydown");\r\n
\t\t\t\t$t.p.savedRow.splice(fr,1);\r\n
\t\t\t\tif($("#"+$.jgrid.jqID(rowid), "#"+$.jgrid.jqID($t.p.id)).hasClass("jqgrid-new-row")){\r\n
\t\t\t\t\tsetTimeout(function(){$($t).jqGrid("delRowData",rowid);},0);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\t$($t).triggerHandler("jqGridInlineAfterRestoreRow", [rowid]);\r\n
\t\t\tif ($.isFunction(o.afterrestorefunc))\r\n
\t\t\t{\r\n
\t\t\t\to.afterrestorefunc.call($t, rowid);\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\taddRow : function ( p ) {\r\n
\t\tp = $.extend(true, {\r\n
\t\t\trowID : "new_row",\r\n
\t\t\tinitdata : {},\r\n
\t\t\tposition :"first",\r\n
\t\t\tuseDefValues : true,\r\n
\t\t\tuseFormatter : false,\r\n
\t\t\taddRowParams : {extraparam:{}}\r\n
\t\t},p  || {});\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif (!this.grid ) { return; }\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(p.useDefValues === true) {\r\n
\t\t\t\t$($t.p.colModel).each(function(){\r\n
\t\t\t\t\tif( this.editoptions && this.editoptions.defaultValue ) {\r\n
\t\t\t\t\t\tvar opt = this.editoptions.defaultValue,\r\n
\t\t\t\t\t\ttmp = $.isFunction(opt) ? opt.call($t) : opt;\r\n
\t\t\t\t\t\tp.initdata[this.name] = tmp;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\t$($t).jqGrid(\'addRowData\', p.rowID, p.initdata, p.position);\r\n
\t\t\tp.rowID = $t.p.idPrefix + p.rowID;\r\n
\t\t\t$("#"+$.jgrid.jqID(p.rowID), "#"+$.jgrid.jqID($t.p.id)).addClass("jqgrid-new-row");\r\n
\t\t\tif(p.useFormatter) {\r\n
\t\t\t\t$("#"+$.jgrid.jqID(p.rowID)+" .ui-inline-edit", "#"+$.jgrid.jqID($t.p.id)).click();\r\n
\t\t\t} else {\r\n
\t\t\t\tvar opers = $t.p.prmNames,\r\n
\t\t\t\toper = opers.oper;\r\n
\t\t\t\tp.addRowParams.extraparam[oper] = opers.addoper;\r\n
\t\t\t\t$($t).jqGrid(\'editRow\', p.rowID, p.addRowParams);\r\n
\t\t\t\t$($t).jqGrid(\'setSelection\', p.rowID);\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tinlineNav : function (elem, o) {\r\n
\t\to = $.extend({\r\n
\t\t\tedit: true,\r\n
\t\t\tediticon: "ui-icon-pencil",\r\n
\t\t\tadd: true,\r\n
\t\t\taddicon:"ui-icon-plus",\r\n
\t\t\tsave: true,\r\n
\t\t\tsaveicon:"ui-icon-disk",\r\n
\t\t\tcancel: true,\r\n
\t\t\tcancelicon:"ui-icon-cancel",\r\n
\t\t\taddParams : {useFormatter : false,rowID : "new_row"},\r\n
\t\t\teditParams : {},\r\n
\t\t\trestoreAfterSelect : true\r\n
\t\t}, $.jgrid.nav, o ||{});\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif (!this.grid ) { return; }\r\n
\t\t\tvar $t = this, onSelect, gID = $.jgrid.jqID($t.p.id);\r\n
\t\t\t$t.p._inlinenav = true;\r\n
\t\t\t// detect the formatactions column\r\n
\t\t\tif(o.addParams.useFormatter === true) {\r\n
\t\t\t\tvar cm = $t.p.colModel,i;\r\n
\t\t\t\tfor (i = 0; i<cm.length; i++) {\r\n
\t\t\t\t\tif(cm[i].formatter && cm[i].formatter === "actions" ) {\r\n
\t\t\t\t\t\tif(cm[i].formatoptions) {\r\n
\t\t\t\t\t\t\tvar defaults =  {\r\n
\t\t\t\t\t\t\t\tkeys:false,\r\n
\t\t\t\t\t\t\t\tonEdit : null,\r\n
\t\t\t\t\t\t\t\tonSuccess: null,\r\n
\t\t\t\t\t\t\t\tafterSave:null,\r\n
\t\t\t\t\t\t\t\tonError: null,\r\n
\t\t\t\t\t\t\t\tafterRestore: null,\r\n
\t\t\t\t\t\t\t\textraparam: {},\r\n
\t\t\t\t\t\t\t\turl: null\r\n
\t\t\t\t\t\t\t},\r\n
\t\t\t\t\t\t\tap = $.extend( defaults, cm[i].formatoptions );\r\n
\t\t\t\t\t\t\to.addParams.addRowParams = {\r\n
\t\t\t\t\t\t\t\t"keys" : ap.keys,\r\n
\t\t\t\t\t\t\t\t"oneditfunc" : ap.onEdit,\r\n
\t\t\t\t\t\t\t\t"successfunc" : ap.onSuccess,\r\n
\t\t\t\t\t\t\t\t"url" : ap.url,\r\n
\t\t\t\t\t\t\t\t"extraparam" : ap.extraparam,\r\n
\t\t\t\t\t\t\t\t"aftersavefunc" : ap.afterSavef,\r\n
\t\t\t\t\t\t\t\t"errorfunc": ap.onError,\r\n
\t\t\t\t\t\t\t\t"afterrestorefunc" : ap.afterRestore\r\n
\t\t\t\t\t\t\t};\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(o.add) {\r\n
\t\t\t\t$($t).jqGrid(\'navButtonAdd\', elem,{\r\n
\t\t\t\t\tcaption : o.addtext,\r\n
\t\t\t\t\ttitle : o.addtitle,\r\n
\t\t\t\t\tbuttonicon : o.addicon,\r\n
\t\t\t\t\tid : $t.p.id+"_iladd",\r\n
\t\t\t\t\tonClickButton : function () {\r\n
\t\t\t\t\t\t$($t).jqGrid(\'addRow\', o.addParams);\r\n
\t\t\t\t\t\tif(!o.addParams.useFormatter) {\r\n
\t\t\t\t\t\t\t$("#"+gID+"_ilsave").removeClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\t\t$("#"+gID+"_ilcancel").removeClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\t\t$("#"+gID+"_iladd").addClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\t\t$("#"+gID+"_iledit").addClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tif(o.edit) {\r\n
\t\t\t\t$($t).jqGrid(\'navButtonAdd\', elem,{\r\n
\t\t\t\t\tcaption : o.edittext,\r\n
\t\t\t\t\ttitle : o.edittitle,\r\n
\t\t\t\t\tbuttonicon : o.editicon,\r\n
\t\t\t\t\tid : $t.p.id+"_iledit",\r\n
\t\t\t\t\tonClickButton : function () {\r\n
\t\t\t\t\t\tvar sr = $($t).jqGrid(\'getGridParam\',\'selrow\');\r\n
\t\t\t\t\t\tif(sr) {\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'editRow\', sr, o.editParams);\r\n
\t\t\t\t\t\t\t$("#"+gID+"_ilsave").removeClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\t\t$("#"+gID+"_ilcancel").removeClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\t\t$("#"+gID+"_iladd").addClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\t\t$("#"+gID+"_iledit").addClass(\'ui-state-disabled\');\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$.jgrid.viewModal("#alertmod",{gbox:"#gbox_"+gID,jqm:true});$("#jqg_alrt").focus();\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tif(o.save) {\r\n
\t\t\t\t$($t).jqGrid(\'navButtonAdd\', elem,{\r\n
\t\t\t\t\tcaption : o.savetext || \'\',\r\n
\t\t\t\t\ttitle : o.savetitle || \'Save row\',\r\n
\t\t\t\t\tbuttonicon : o.saveicon,\r\n
\t\t\t\t\tid : $t.p.id+"_ilsave",\r\n
\t\t\t\t\tonClickButton : function () {\r\n
\t\t\t\t\t\tvar sr = $t.p.savedRow[0].id;\r\n
\t\t\t\t\t\tif(sr) {\r\n
\t\t\t\t\t\t\tvar opers = $t.p.prmNames,\r\n
\t\t\t\t\t\t\toper = opers.oper;\r\n
\t\t\t\t\t\t\tif(!o.editParams.extraparam) {\r\n
\t\t\t\t\t\t\t\to.editParams.extraparam = {};\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif($("#"+$.jgrid.jqID(sr), "#"+gID ).hasClass("jqgrid-new-row")) {\r\n
\t\t\t\t\t\t\t\to.editParams.extraparam[oper] = opers.addoper;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\to.editParams.extraparam[oper] = opers.editoper;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif( $($t).jqGrid(\'saveRow\', sr, o.editParams) ) {\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid(\'showAddEditButtons\');\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$.jgrid.viewModal("#alertmod",{gbox:"#gbox_"+gID,jqm:true});$("#jqg_alrt").focus();\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#"+gID+"_ilsave").addClass(\'ui-state-disabled\');\r\n
\t\t\t}\r\n
\t\t\tif(o.cancel) {\r\n
\t\t\t\t$($t).jqGrid(\'navButtonAdd\', elem,{\r\n
\t\t\t\t\tcaption : o.canceltext || \'\',\r\n
\t\t\t\t\ttitle : o.canceltitle || \'Cancel row editing\',\r\n
\t\t\t\t\tbuttonicon : o.cancelicon,\r\n
\t\t\t\t\tid : $t.p.id+"_ilcancel",\r\n
\t\t\t\t\tonClickButton : function () {\r\n
\t\t\t\t\t\tvar sr = $t.p.savedRow[0].id;\r\n
\t\t\t\t\t\tif(sr) {\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'restoreRow\', sr, o.editParams);\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'showAddEditButtons\');\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$.jgrid.viewModal("#alertmod",{gbox:"#gbox_"+gID,jqm:true});$("#jqg_alrt").focus();\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t});\r\n
\t\t\t\t$("#"+gID+"_ilcancel").addClass(\'ui-state-disabled\');\r\n
\t\t\t}\r\n
\t\t\tif(o.restoreAfterSelect === true) {\r\n
\t\t\t\tif($.isFunction($t.p.beforeSelectRow)) {\r\n
\t\t\t\t\tonSelect = $t.p.beforeSelectRow;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tonSelect =  false;\r\n
\t\t\t\t}\r\n
\t\t\t\t$t.p.beforeSelectRow = function(id, stat) {\r\n
\t\t\t\t\tvar ret = true;\r\n
\t\t\t\t\tif($t.p.savedRow.length > 0 && $t.p._inlinenav===true && ( id !== $t.p.selrow && $t.p.selrow !==null) ) {\r\n
\t\t\t\t\t\tif($t.p.selrow == o.addParams.rowID ) {\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'delRowData\', $t.p.selrow);\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'restoreRow\', $t.p.selrow, o.editParams);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t$($t).jqGrid(\'showAddEditButtons\');\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(onSelect) {\r\n
\t\t\t\t\t\tret = onSelect.call($t, id, stat);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn ret;\r\n
\t\t\t\t};\r\n
\t\t\t}\r\n
\r\n
\t\t});\r\n
\t},\r\n
\tshowAddEditButtons : function()  {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif (!this.grid ) { return; }\r\n
\t\t\tvar gID = $.jgrid.jqID(this.p.id);\r\n
\t\t\t$("#"+gID+"_ilsave").addClass(\'ui-state-disabled\');\r\n
\t\t\t$("#"+gID+"_ilcancel").addClass(\'ui-state-disabled\');\r\n
\t\t\t$("#"+gID+"_iladd").removeClass(\'ui-state-disabled\');\r\n
\t\t\t$("#"+gID+"_iledit").removeClass(\'ui-state-disabled\');\r\n
\t\t});\r\n
\t}\r\n
//end inline edit\r\n
});\r\n
})(jQuery);\r\n
;(function($){\r\n
/*\r\n
**\r\n
 * jqGrid extension for cellediting Grid Data\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/ \r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
**/ \r\n
/**\r\n
 * all events and options here are aded anonynous and not in the base grid\r\n
 * since the array is to big. Here is the order of execution.\r\n
 * From this point we use jQuery isFunction\r\n
 * formatCell\r\n
 * beforeEditCell,\r\n
 * onSelectCell (used only for noneditable cels)\r\n
 * afterEditCell,\r\n
 * beforeSaveCell, (called before validation of values if any)\r\n
 * beforeSubmitCell (if cellsubmit remote (ajax))\r\n
 * afterSubmitCell(if cellsubmit remote (ajax)),\r\n
 * afterSaveCell,\r\n
 * errorCell,\r\n
 * serializeCellData - new\r\n
 * Options\r\n
 * cellsubmit (remote,clientArray) (added in grid options)\r\n
 * cellurl\r\n
 * ajaxCellOptions\r\n
* */\r\n
"use strict";\r\n
$.jgrid.extend({\r\n
\teditCell : function (iRow,iCol, ed){\r\n
\t\treturn this.each(function (){\r\n
\t\t\tvar $t = this, nm, tmp,cc, cm;\r\n
\t\t\tif (!$t.grid || $t.p.cellEdit !== true) {return;}\r\n
\t\t\tiCol = parseInt(iCol,10);\r\n
\t\t\t// select the row that can be used for other methods\r\n
\t\t\t$t.p.selrow = $t.rows[iRow].id;\r\n
\t\t\tif (!$t.p.knv) {$($t).jqGrid("GridNav");}\r\n
\t\t\t// check to see if we have already edited cell\r\n
\t\t\tif ($t.p.savedRow.length>0) {\r\n
\t\t\t\t// prevent second click on that field and enable selects\r\n
\t\t\t\tif (ed===true ) {\r\n
\t\t\t\t\tif(iRow == $t.p.iRow && iCol == $t.p.iCol){\r\n
\t\t\t\t\t\treturn;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\t// save the cell\r\n
\t\t\t\t$($t).jqGrid("saveCell",$t.p.savedRow[0].id,$t.p.savedRow[0].ic);\r\n
\t\t\t} else {\r\n
\t\t\t\twindow.setTimeout(function () { $("#"+$.jgrid.jqID($t.p.knv)).attr("tabindex","-1").focus();},0);\r\n
\t\t\t}\r\n
\t\t\tcm = $t.p.colModel[iCol];\r\n
\t\t\tnm = cm.name;\r\n
\t\t\tif (nm==\'subgrid\' || nm==\'cb\' || nm==\'rn\') {return;}\r\n
\t\t\tcc = $("td:eq("+iCol+")",$t.rows[iRow]);\r\n
\t\t\tif (cm.editable===true && ed===true && !cc.hasClass("not-editable-cell")) {\r\n
\t\t\t\tif(parseInt($t.p.iCol,10)>=0  && parseInt($t.p.iRow,10)>=0) {\r\n
\t\t\t\t\t$("td:eq("+$t.p.iCol+")",$t.rows[$t.p.iRow]).removeClass("edit-cell ui-state-highlight");\r\n
\t\t\t\t\t$($t.rows[$t.p.iRow]).removeClass("selected-row ui-state-hover");\r\n
\t\t\t\t}\r\n
\t\t\t\t$(cc).addClass("edit-cell ui-state-highlight");\r\n
\t\t\t\t$($t.rows[iRow]).addClass("selected-row ui-state-hover");\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\ttmp =  $.unformat.call($t,cc,{rowId: $t.rows[iRow].id, colModel:cm},iCol);\r\n
\t\t\t\t} catch (_) {\r\n
\t\t\t\t\ttmp = ( cm.edittype && cm.edittype == \'textarea\' ) ? $(cc).text() : $(cc).html();\r\n
\t\t\t\t}\r\n
\t\t\t\tif($t.p.autoencode) { tmp = $.jgrid.htmlDecode(tmp); }\r\n
\t\t\t\tif (!cm.edittype) {cm.edittype = "text";}\r\n
\t\t\t\t$t.p.savedRow.push({id:iRow,ic:iCol,name:nm,v:tmp});\r\n
\t\t\t\tif(tmp === "&nbsp;" || tmp === "&#160;" || (tmp.length===1 && tmp.charCodeAt(0)===160) ) {tmp=\'\';}\r\n
\t\t\t\tif($.isFunction($t.p.formatCell)) {\r\n
\t\t\t\t\tvar tmp2 = $t.p.formatCell.call($t, $t.rows[iRow].id,nm,tmp,iRow,iCol);\r\n
\t\t\t\t\tif(tmp2 !== undefined ) {tmp = tmp2;}\r\n
\t\t\t\t}\r\n
\t\t\t\tvar opt = $.extend({}, cm.editoptions || {} ,{id:iRow+"_"+nm,name:nm});\r\n
\t\t\t\tvar elc = $.jgrid.createEl.call($t,cm.edittype,opt,tmp,true,$.extend({},$.jgrid.ajaxOptions,$t.p.ajaxSelectOptions || {}));\r\n
\t\t\t\t$($t).triggerHandler("jqGridBeforeEditCell", [$t.rows[iRow].id, nm, tmp, iRow, iCol]);\r\n
\t\t\t\tif ($.isFunction($t.p.beforeEditCell)) {\r\n
\t\t\t\t\t$t.p.beforeEditCell.call($t, $t.rows[iRow].id,nm,tmp,iRow,iCol);\r\n
\t\t\t\t}\r\n
\t\t\t\t$(cc).html("").append(elc).attr("tabindex","0");\r\n
\t\t\t\twindow.setTimeout(function () { $(elc).focus();},0);\r\n
\t\t\t\t$("input, select, textarea",cc).bind("keydown",function(e) {\r\n
\t\t\t\t\tif (e.keyCode === 27) {\r\n
\t\t\t\t\t\tif($("input.hasDatepicker",cc).length >0) {\r\n
\t\t\t\t\t\t\tif( $(".ui-datepicker").is(":hidden") )  { $($t).jqGrid("restoreCell",iRow,iCol); }\r\n
\t\t\t\t\t\t\telse { $("input.hasDatepicker",cc).datepicker(\'hide\'); }\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$($t).jqGrid("restoreCell",iRow,iCol);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} //ESC\r\n
\t\t\t\t\tif (e.keyCode === 13) {\r\n
\t\t\t\t\t\t$($t).jqGrid("saveCell",iRow,iCol);\r\n
\t\t\t\t\t\t// Prevent default action\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t} //Enter\r\n
\t\t\t\t\tif (e.keyCode === 9)  {\r\n
\t\t\t\t\t\tif(!$t.grid.hDiv.loading ) {\r\n
\t\t\t\t\t\t\tif (e.shiftKey) {$($t).jqGrid("prevCell",iRow,iCol);} //Shift TAb\r\n
\t\t\t\t\t\t\telse {$($t).jqGrid("nextCell",iRow,iCol);} //Tab\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\te.stopPropagation();\r\n
\t\t\t\t});\r\n
\t\t\t\t$($t).triggerHandler("jqGridAfterEditCell", [$t.rows[iRow].id, nm, tmp, iRow, iCol]);\r\n
\t\t\t\tif ($.isFunction($t.p.afterEditCell)) {\r\n
\t\t\t\t\t$t.p.afterEditCell.call($t, $t.rows[iRow].id,nm,tmp,iRow,iCol);\r\n
\t\t\t\t}\r\n
\t\t\t} else {\r\n
\t\t\t\tif (parseInt($t.p.iCol,10)>=0  && parseInt($t.p.iRow,10)>=0) {\r\n
\t\t\t\t\t$("td:eq("+$t.p.iCol+")",$t.rows[$t.p.iRow]).removeClass("edit-cell ui-state-highlight");\r\n
\t\t\t\t\t$($t.rows[$t.p.iRow]).removeClass("selected-row ui-state-hover");\r\n
\t\t\t\t}\r\n
\t\t\t\tcc.addClass("edit-cell ui-state-highlight");\r\n
\t\t\t\t$($t.rows[iRow]).addClass("selected-row ui-state-hover");\r\n
\t\t\t\ttmp = cc.html().replace(/\\&#160\\;/ig,\'\');\r\n
\t\t\t\t$($t).triggerHandler("jqGridSelectCell", [$t.rows[iRow].id, nm, tmp, iRow, iCol]);\r\n
\t\t\t\tif ($.isFunction($t.p.onSelectCell)) {\r\n
\t\t\t\t\t$t.p.onSelectCell.call($t, $t.rows[iRow].id,nm,tmp,iRow,iCol);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\t$t.p.iCol = iCol; $t.p.iRow = iRow;\r\n
\t\t});\r\n
\t},\r\n
\tsaveCell : function (iRow, iCol){\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t= this, fr;\r\n
\t\t\tif (!$t.grid || $t.p.cellEdit !== true) {return;}\r\n
\t\t\tif ( $t.p.savedRow.length >= 1) {fr = 0;} else {fr=null;} \r\n
\t\t\tif(fr !== null) {\r\n
\t\t\t\tvar cc = $("td:eq("+iCol+")",$t.rows[iRow]),v,v2,\r\n
\t\t\t\tcm = $t.p.colModel[iCol], nm = cm.name, nmjq = $.jgrid.jqID(nm) ;\r\n
\t\t\t\tswitch (cm.edittype) {\r\n
\t\t\t\t\tcase "select":\r\n
\t\t\t\t\t\tif(!cm.editoptions.multiple) {\r\n
\t\t\t\t\t\t\tv = $("#"+iRow+"_"+nmjq+" option:selected",$t.rows[iRow]).val();\r\n
\t\t\t\t\t\t\tv2 = $("#"+iRow+"_"+nmjq+" option:selected",$t.rows[iRow]).text();\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tvar sel = $("#"+iRow+"_"+nmjq,$t.rows[iRow]), selectedText = [];\r\n
\t\t\t\t\t\t\tv = $(sel).val();\r\n
\t\t\t\t\t\t\tif(v) { v.join(",");} else { v=""; }\r\n
\t\t\t\t\t\t\t$("option:selected",sel).each(\r\n
\t\t\t\t\t\t\t\tfunction(i,selected){\r\n
\t\t\t\t\t\t\t\t\tselectedText[i] = $(selected).text();\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t);\r\n
\t\t\t\t\t\t\tv2 = selectedText.join(",");\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(cm.formatter) { v2 = v; }\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase "checkbox":\r\n
\t\t\t\t\t\tvar cbv  = ["Yes","No"];\r\n
\t\t\t\t\t\tif(cm.editoptions){\r\n
\t\t\t\t\t\t\tcbv = cm.editoptions.value.split(":");\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tv = $("#"+iRow+"_"+nmjq,$t.rows[iRow]).is(":checked") ? cbv[0] : cbv[1];\r\n
\t\t\t\t\t\tv2=v;\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase "password":\r\n
\t\t\t\t\tcase "text":\r\n
\t\t\t\t\tcase "textarea":\r\n
\t\t\t\t\tcase "button" :\r\n
\t\t\t\t\t\tv = $("#"+iRow+"_"+nmjq,$t.rows[iRow]).val();\r\n
\t\t\t\t\t\tv2=v;\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase \'custom\' :\r\n
\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\tif(cm.editoptions && $.isFunction(cm.editoptions.custom_value)) {\r\n
\t\t\t\t\t\t\t\tv = cm.editoptions.custom_value.call($t, $(".customelement",cc),\'get\');\r\n
\t\t\t\t\t\t\t\tif (v===undefined) { throw "e2";} else { v2=v; }\r\n
\t\t\t\t\t\t\t} else { throw "e1"; }\r\n
\t\t\t\t\t\t} catch (e) {\r\n
\t\t\t\t\t\t\tif (e=="e1") { $.jgrid.info_dialog(jQuery.jgrid.errors.errcap,"function \'custom_value\' "+$.jgrid.edit.msg.nodefined,jQuery.jgrid.edit.bClose); }\r\n
\t\t\t\t\t\t\tif (e=="e2") { $.jgrid.info_dialog(jQuery.jgrid.errors.errcap,"function \'custom_value\' "+$.jgrid.edit.msg.novalue,jQuery.jgrid.edit.bClose); }\r\n
\t\t\t\t\t\t\telse {$.jgrid.info_dialog(jQuery.jgrid.errors.errcap,e.message,jQuery.jgrid.edit.bClose); }\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t\t// The common approach is if nothing changed do not do anything\r\n
\t\t\t\tif (v2 !== $t.p.savedRow[fr].v){\r\n
\t\t\t\t\tvar vvv = $($t).triggerHandler("jqGridBeforeSaveCell", [$t.rows[iRow].id, nm, v, iRow, iCol]);\r\n
\t\t\t\t\tif (vvv) {v = vvv; v2=vvv;}\r\n
\t\t\t\t\tif ($.isFunction($t.p.beforeSaveCell)) {\r\n
\t\t\t\t\t\tvar vv = $t.p.beforeSaveCell.call($t, $t.rows[iRow].id,nm, v, iRow,iCol);\r\n
\t\t\t\t\t\tif (vv) {v = vv; v2=vv;}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tvar cv = $.jgrid.checkValues(v,iCol,$t);\r\n
\t\t\t\t\tif(cv[0] === true) {\r\n
\t\t\t\t\t\tvar addpost = $($t).triggerHandler("jqGridBeforeSubmitCell", [$t.rows[iRow].id, nm, v, iRow, iCol]) || {};\r\n
\t\t\t\t\t\tif ($.isFunction($t.p.beforeSubmitCell)) {\r\n
\t\t\t\t\t\t\taddpost = $t.p.beforeSubmitCell.call($t, $t.rows[iRow].id,nm, v, iRow,iCol);\r\n
\t\t\t\t\t\t\tif (!addpost) {addpost={};}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif( $("input.hasDatepicker",cc).length >0) { $("input.hasDatepicker",cc).datepicker(\'hide\'); }\r\n
\t\t\t\t\t\tif ($t.p.cellsubmit == \'remote\') {\r\n
\t\t\t\t\t\t\tif ($t.p.cellurl) {\r\n
\t\t\t\t\t\t\t\tvar postdata = {};\r\n
\t\t\t\t\t\t\t\tif($t.p.autoencode) { v = $.jgrid.htmlEncode(v); }\r\n
\t\t\t\t\t\t\t\tpostdata[nm] = v;\r\n
\t\t\t\t\t\t\t\tvar idname,oper, opers;\r\n
\t\t\t\t\t\t\t\topers = $t.p.prmNames;\r\n
\t\t\t\t\t\t\t\tidname = opers.id;\r\n
\t\t\t\t\t\t\t\toper = opers.oper;\r\n
\t\t\t\t\t\t\t\tpostdata[idname] = $.jgrid.stripPref($t.p.idPrefix, $t.rows[iRow].id);\r\n
\t\t\t\t\t\t\t\tpostdata[oper] = opers.editoper;\r\n
\t\t\t\t\t\t\t\tpostdata = $.extend(addpost,postdata);\r\n
\t\t\t\t\t\t\t\t$("#lui_"+$.jgrid.jqID($t.p.id)).show();\r\n
\t\t\t\t\t\t\t\t$t.grid.hDiv.loading = true;\r\n
\t\t\t\t\t\t\t\t$.ajax( $.extend( {\r\n
\t\t\t\t\t\t\t\t\turl: $t.p.cellurl,\r\n
\t\t\t\t\t\t\t\t\tdata :$.isFunction($t.p.serializeCellData) ? $t.p.serializeCellData.call($t, postdata) : postdata,\r\n
\t\t\t\t\t\t\t\t\ttype: "POST",\r\n
\t\t\t\t\t\t\t\t\tcomplete: function (result, stat) {\r\n
\t\t\t\t\t\t\t\t\t\t$("#lui_"+$t.p.id).hide();\r\n
\t\t\t\t\t\t\t\t\t\t$t.grid.hDiv.loading = false;\r\n
\t\t\t\t\t\t\t\t\t\tif (stat == \'success\') {\r\n
\t\t\t\t\t\t\t\t\t\t\tvar ret = $($t).triggerHandler("jqGridAfterSubmitCell", [$t, result, postdata.id, nm, v, iRow, iCol]) || [true, \'\'];\r\n
\t\t\t\t\t\t\t\t\t\t\tif (ret[0] === true && $.isFunction($t.p.afterSubmitCell)) {\r\n
\t\t\t\t\t\t\t\t\t\t\t\tret = $t.p.afterSubmitCell.call($t, result,postdata.id,nm,v,iRow,iCol);\r\n
\t\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t\tif(ret[0] === true){\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$(cc).empty();\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("setCell",$t.rows[iRow].id, iCol, v2, false, false, true);\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$(cc).addClass("dirty-cell");\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t.rows[iRow]).addClass("edited");\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).triggerHandler("jqGridAfterSaveCell", [$t.rows[iRow].id, nm, v, iRow, iCol]);\r\n
\t\t\t\t\t\t\t\t\t\t\t\tif ($.isFunction($t.p.afterSaveCell)) {\r\n
\t\t\t\t\t\t\t\t\t\t\t\t\t$t.p.afterSaveCell.call($t, $t.rows[iRow].id,nm, v, iRow,iCol);\r\n
\t\t\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$t.p.savedRow.splice(0,1);\r\n
\t\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$.jgrid.info_dialog($.jgrid.errors.errcap,ret[1],$.jgrid.edit.bClose);\r\n
\t\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("restoreCell",iRow,iCol);\r\n
\t\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t},\r\n
\t\t\t\t\t\t\t\t\terror:function(res,stat,err) {\r\n
\t\t\t\t\t\t\t\t\t\t$("#lui_"+$.jgrid.jqID($t.p.id)).hide();\r\n
\t\t\t\t\t\t\t\t\t\t$t.grid.hDiv.loading = false;\r\n
\t\t\t\t\t\t\t\t\t\t$($t).triggerHandler("jqGridErrorCell", [res, stat, err]);\r\n
\t\t\t\t\t\t\t\t\t\tif ($.isFunction($t.p.errorCell)) {\r\n
\t\t\t\t\t\t\t\t\t\t\t$t.p.errorCell.call($t, res,stat,err);\r\n
\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("restoreCell",iRow,iCol);\r\n
\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\t$.jgrid.info_dialog($.jgrid.errors.errcap,res.status+" : "+res.statusText+"<br/>"+stat,$.jgrid.edit.bClose);\r\n
\t\t\t\t\t\t\t\t\t\t\t$($t).jqGrid("restoreCell",iRow,iCol);\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}, $.jgrid.ajaxOptions, $t.p.ajaxCellOptions || {}));\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\t$.jgrid.info_dialog($.jgrid.errors.errcap,$.jgrid.errors.nourl,$.jgrid.edit.bClose);\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("restoreCell",iRow,iCol);\r\n
\t\t\t\t\t\t\t\t} catch (e) {}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif ($t.p.cellsubmit == \'clientArray\') {\r\n
\t\t\t\t\t\t\t$(cc).empty();\r\n
\t\t\t\t\t\t\t$($t).jqGrid("setCell",$t.rows[iRow].id,iCol, v2, false, false, true);\r\n
\t\t\t\t\t\t\t$(cc).addClass("dirty-cell");\r\n
\t\t\t\t\t\t\t$($t.rows[iRow]).addClass("edited");\r\n
\t\t\t\t\t\t\t$($t).triggerHandler("jqGridAfterSaveCell", [$t.rows[iRow].id, nm, v, iRow, iCol]);\r\n
\t\t\t\t\t\t\tif ($.isFunction($t.p.afterSaveCell)) {\r\n
\t\t\t\t\t\t\t\t$t.p.afterSaveCell.call($t, $t.rows[iRow].id,nm, v, iRow,iCol);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t$t.p.savedRow.splice(0,1);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\twindow.setTimeout(function(){$.jgrid.info_dialog($.jgrid.errors.errcap,v+" "+cv[1],$.jgrid.edit.bClose);},100);\r\n
\t\t\t\t\t\t\t$($t).jqGrid("restoreCell",iRow,iCol);\r\n
\t\t\t\t\t\t} catch (e) {}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$($t).jqGrid("restoreCell",iRow,iCol);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif ($.browser.opera) {\r\n
\t\t\t\t$("#"+$.jgrid.jqID($t.p.knv)).attr("tabindex","-1").focus();\r\n
\t\t\t} else {\r\n
\t\t\t\twindow.setTimeout(function () { $("#"+$.jgrid.jqID($t.p.knv)).attr("tabindex","-1").focus();},0);\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\trestoreCell : function(iRow, iCol) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t= this, fr;\r\n
\t\t\tif (!$t.grid || $t.p.cellEdit !== true ) {return;}\r\n
\t\t\tif ( $t.p.savedRow.length >= 1) {fr = 0;} else {fr=null;}\r\n
\t\t\tif(fr !== null) {\r\n
\t\t\t\tvar cc = $("td:eq("+iCol+")",$t.rows[iRow]);\r\n
\t\t\t\t// datepicker fix\r\n
\t\t\t\tif($.isFunction($.fn.datepicker)) {\r\n
\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t$("input.hasDatepicker",cc).datepicker(\'hide\');\r\n
\t\t\t\t\t} catch (e) {}\r\n
\t\t\t\t}\r\n
\t\t\t\t$(cc).empty().attr("tabindex","-1");\r\n
\t\t\t\t$($t).jqGrid("setCell",$t.rows[iRow].id, iCol, $t.p.savedRow[fr].v, false, false, true);\r\n
\t\t\t\t$($t).triggerHandler("jqGridAfterRestoreCell", [$t.rows[iRow].id, $t.p.savedRow[fr].v, iRow, iCol]);\r\n
\t\t\t\tif ($.isFunction($t.p.afterRestoreCell)) {\r\n
\t\t\t\t\t$t.p.afterRestoreCell.call($t, $t.rows[iRow].id, $t.p.savedRow[fr].v, iRow, iCol);\r\n
\t\t\t\t}\t\t\t\t\r\n
\t\t\t\t$t.p.savedRow.splice(0,1);\r\n
\t\t\t}\r\n
\t\t\twindow.setTimeout(function () { $("#"+$t.p.knv).attr("tabindex","-1").focus();},0);\r\n
\t\t});\r\n
\t},\r\n
\tnextCell : function (iRow,iCol) {\r\n
\t\treturn this.each(function (){\r\n
\t\t\tvar $t = this, nCol=false;\r\n
\t\t\tif (!$t.grid || $t.p.cellEdit !== true) {return;}\r\n
\t\t\t// try to find next editable cell\r\n
\t\t\tfor (var i=iCol+1; i<$t.p.colModel.length; i++) {\r\n
\t\t\t\tif ( $t.p.colModel[i].editable ===true) {\r\n
\t\t\t\t\tnCol = i; break;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(nCol !== false) {\r\n
\t\t\t\t$($t).jqGrid("editCell",iRow,nCol,true);\r\n
\t\t\t} else {\r\n
\t\t\t\tif ($t.p.savedRow.length >0) {\r\n
\t\t\t\t\t$($t).jqGrid("saveCell",iRow,iCol);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tprevCell : function (iRow,iCol) {\r\n
\t\treturn this.each(function (){\r\n
\t\t\tvar $t = this, nCol=false;\r\n
\t\t\tif (!$t.grid || $t.p.cellEdit !== true) {return;}\r\n
\t\t\t// try to find next editable cell\r\n
\t\t\tfor (var i=iCol-1; i>=0; i--) {\r\n
\t\t\t\tif ( $t.p.colModel[i].editable ===true) {\r\n
\t\t\t\t\tnCol = i; break;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(nCol !== false) {\r\n
\t\t\t\t$($t).jqGrid("editCell",iRow,nCol,true);\r\n
\t\t\t} else {\r\n
\t\t\t\tif ($t.p.savedRow.length >0) {\r\n
\t\t\t\t\t$($t).jqGrid("saveCell",iRow,iCol);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tGridNav : function() {\r\n
\t\treturn this.each(function () {\r\n
\t\t\tvar  $t = this;\r\n
\t\t\tif (!$t.grid || $t.p.cellEdit !== true ) {return;}\r\n
\t\t\t// trick to process keydown on non input elements\r\n
\t\t\t$t.p.knv = $t.p.id + "_kn";\r\n
\t\t\tvar selection = $("<div style=\'position:absolute;top:-1000000px;width:1px;height:1px;\' tabindex=\'0\'><div tabindex=\'-1\' style=\'width:1px;height:1px;\' id=\'"+$t.p.knv+"\'></div></div>"),\r\n
\t\t\ti, kdir;\r\n
\t\t\tfunction scrollGrid(iR, iC, tp){\r\n
\t\t\t\tif (tp.substr(0,1)==\'v\') {\r\n
\t\t\t\t\tvar ch = $($t.grid.bDiv)[0].clientHeight,\r\n
\t\t\t\t\tst = $($t.grid.bDiv)[0].scrollTop,\r\n
\t\t\t\t\tnROT = $t.rows[iR].offsetTop+$t.rows[iR].clientHeight,\r\n
\t\t\t\t\tpROT = $t.rows[iR].offsetTop;\r\n
\t\t\t\t\tif(tp == \'vd\') {\r\n
\t\t\t\t\t\tif(nROT >= ch) {\r\n
\t\t\t\t\t\t\t$($t.grid.bDiv)[0].scrollTop = $($t.grid.bDiv)[0].scrollTop + $t.rows[iR].clientHeight;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(tp == \'vu\'){\r\n
\t\t\t\t\t\tif (pROT < st ) {\r\n
\t\t\t\t\t\t\t$($t.grid.bDiv)[0].scrollTop = $($t.grid.bDiv)[0].scrollTop - $t.rows[iR].clientHeight;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(tp==\'h\') {\r\n
\t\t\t\t\tvar cw = $($t.grid.bDiv)[0].clientWidth,\r\n
\t\t\t\t\tsl = $($t.grid.bDiv)[0].scrollLeft,\r\n
\t\t\t\t\tnCOL = $t.rows[iR].cells[iC].offsetLeft+$t.rows[iR].cells[iC].clientWidth,\r\n
\t\t\t\t\tpCOL = $t.rows[iR].cells[iC].offsetLeft;\r\n
\t\t\t\t\tif(nCOL >= cw+parseInt(sl,10)) {\r\n
\t\t\t\t\t\t$($t.grid.bDiv)[0].scrollLeft = $($t.grid.bDiv)[0].scrollLeft + $t.rows[iR].cells[iC].clientWidth;\r\n
\t\t\t\t\t} else if (pCOL < sl) {\r\n
\t\t\t\t\t\t$($t.grid.bDiv)[0].scrollLeft = $($t.grid.bDiv)[0].scrollLeft - $t.rows[iR].cells[iC].clientWidth;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tfunction findNextVisible(iC,act){\r\n
\t\t\t\tvar ind, i;\r\n
\t\t\t\tif(act == \'lft\') {\r\n
\t\t\t\t\tind = iC+1;\r\n
\t\t\t\t\tfor (i=iC;i>=0;i--){\r\n
\t\t\t\t\t\tif ($t.p.colModel[i].hidden !== true) {\r\n
\t\t\t\t\t\t\tind = i;\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(act == \'rgt\') {\r\n
\t\t\t\t\tind = iC-1;\r\n
\t\t\t\t\tfor (i=iC; i<$t.p.colModel.length;i++){\r\n
\t\t\t\t\t\tif ($t.p.colModel[i].hidden !== true) {\r\n
\t\t\t\t\t\t\tind = i;\r\n
\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t}\t\t\t\t\t\t\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\treturn ind;\r\n
\t\t\t}\r\n
\r\n
\t\t\t$(selection).insertBefore($t.grid.cDiv);\r\n
\t\t\t$("#"+$t.p.knv)\r\n
\t\t\t.focus()\r\n
\t\t\t.keydown(function (e){\r\n
\t\t\t\tkdir = e.keyCode;\r\n
\t\t\t\tif($t.p.direction == "rtl") {\r\n
\t\t\t\t\tif(kdir===37) { kdir = 39;}\r\n
\t\t\t\t\telse if (kdir===39) { kdir = 37; }\r\n
\t\t\t\t}\r\n
\t\t\t\tswitch (kdir) {\r\n
\t\t\t\t\tcase 38:\r\n
\t\t\t\t\t\tif ($t.p.iRow-1 >0 ) {\r\n
\t\t\t\t\t\t\tscrollGrid($t.p.iRow-1,$t.p.iCol,\'vu\');\r\n
\t\t\t\t\t\t\t$($t).jqGrid("editCell",$t.p.iRow-1,$t.p.iCol,false);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase 40 :\r\n
\t\t\t\t\t\tif ($t.p.iRow+1 <=  $t.rows.length-1) {\r\n
\t\t\t\t\t\t\tscrollGrid($t.p.iRow+1,$t.p.iCol,\'vd\');\r\n
\t\t\t\t\t\t\t$($t).jqGrid("editCell",$t.p.iRow+1,$t.p.iCol,false);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase 37 :\r\n
\t\t\t\t\t\tif ($t.p.iCol -1 >=  0) {\r\n
\t\t\t\t\t\t\ti = findNextVisible($t.p.iCol-1,\'lft\');\r\n
\t\t\t\t\t\t\tscrollGrid($t.p.iRow, i,\'h\');\r\n
\t\t\t\t\t\t\t$($t).jqGrid("editCell",$t.p.iRow, i,false);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase 39 :\r\n
\t\t\t\t\t\tif ($t.p.iCol +1 <=  $t.p.colModel.length-1) {\r\n
\t\t\t\t\t\t\ti = findNextVisible($t.p.iCol+1,\'rgt\');\r\n
\t\t\t\t\t\t\tscrollGrid($t.p.iRow,i,\'h\');\r\n
\t\t\t\t\t\t\t$($t).jqGrid("editCell",$t.p.iRow,i,false);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t\tcase 13:\r\n
\t\t\t\t\t\tif (parseInt($t.p.iCol,10)>=0 && parseInt($t.p.iRow,10)>=0) {\r\n
\t\t\t\t\t\t\t$($t).jqGrid("editCell",$t.p.iRow,$t.p.iCol,true);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t\tdefault :\r\n
\t\t\t\t\t\treturn true;\r\n
\t\t\t\t}\r\n
\t\t\t\treturn false;\r\n
\t\t\t});\r\n
\t\t});\r\n
\t},\r\n
\tgetChangedCells : function (mthd) {\r\n
\t\tvar ret=[];\r\n
\t\tif (!mthd) {mthd=\'all\';}\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t= this,nm;\r\n
\t\t\tif (!$t.grid || $t.p.cellEdit !== true ) {return;}\r\n
\t\t\t$($t.rows).each(function(j){\r\n
\t\t\t\tvar res = {};\r\n
\t\t\t\tif ($(this).hasClass("edited")) {\r\n
\t\t\t\t\t$(\'td\',this).each( function(i) {\r\n
\t\t\t\t\t\tnm = $t.p.colModel[i].name;\r\n
\t\t\t\t\t\tif ( nm !== \'cb\' && nm !== \'subgrid\') {\r\n
\t\t\t\t\t\t\tif (mthd==\'dirty\') {\r\n
\t\t\t\t\t\t\t\tif ($(this).hasClass(\'dirty-cell\')) {\r\n
\t\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\t\tres[nm] = $.unformat.call($t,this,{rowId:$t.rows[j].id, colModel:$t.p.colModel[i]},i);\r\n
\t\t\t\t\t\t\t\t\t} catch (e){\r\n
\t\t\t\t\t\t\t\t\t\tres[nm] = $.jgrid.htmlDecode($(this).html());\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\tres[nm] = $.unformat.call($t,this,{rowId:$t.rows[j].id,colModel:$t.p.colModel[i]},i);\r\n
\t\t\t\t\t\t\t\t} catch (e) {\r\n
\t\t\t\t\t\t\t\t\tres[nm] = $.jgrid.htmlDecode($(this).html());\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tres.id = this.id;\r\n
\t\t\t\t\tret.push(res);\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t});\r\n
\t\treturn ret;\r\n
\t}\r\n
/// end  cell editing\r\n
});\r\n
})(jQuery);\r\n
;(function($){\r\n
/**\r\n
 * jqGrid extension for SubGrid Data\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/ \r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
**/\r\n
"use strict";\r\n
$.jgrid.extend({\r\n
setSubGrid : function () {\r\n
\treturn this.each(function (){\r\n
\t\tvar $t = this, cm,\r\n
\t\tsuboptions = {\r\n
\t\t\tplusicon : "ui-icon-plus",\r\n
\t\t\tminusicon : "ui-icon-minus",\r\n
\t\t\topenicon: "ui-icon-carat-1-sw",\r\n
\t\t\texpandOnLoad:  false,\r\n
\t\t\tdelayOnLoad : 50,\r\n
\t\t\tselectOnExpand : false,\r\n
\t\t\treloadOnExpand : true\r\n
\t\t};\r\n
\t\t$t.p.subGridOptions = $.extend(suboptions, $t.p.subGridOptions || {});\r\n
\t\t$t.p.colNames.unshift("");\r\n
\t\t$t.p.colModel.unshift({name:\'subgrid\',width: $.browser.safari ?  $t.p.subGridWidth+$t.p.cellLayout : $t.p.subGridWidth,sortable: false,resizable:false,hidedlg:true,search:false,fixed:true});\r\n
\t\tcm = $t.p.subGridModel;\r\n
\t\tif(cm[0]) {\r\n
\t\t\tcm[0].align = $.extend([],cm[0].align || []);\r\n
\t\t\tfor(var i=0;i<cm[0].name.length;i++) { cm[0].align[i] = cm[0].align[i] || \'left\';}\r\n
\t\t}\r\n
\t});\r\n
},\r\n
addSubGridCell :function (pos,iRow) {\r\n
\tvar prp=\'\',ic,sid;\r\n
\tthis.each(function(){\r\n
\t\tprp = this.formatCol(pos,iRow);\r\n
\t\tsid= this.p.id;\r\n
\t\tic = this.p.subGridOptions.plusicon;\r\n
\t});\r\n
\treturn "<td role=\\"gridcell\\" aria-describedby=\\""+sid+"_subgrid\\" class=\\"ui-sgcollapsed sgcollapsed\\" "+prp+"><a href=\'javascript:void(0);\'><span class=\'ui-icon "+ic+"\'></span></a></td>";\r\n
},\r\n
addSubGrid : function( pos, sind ) {\r\n
\treturn this.each(function(){\r\n
\t\tvar ts = this;\r\n
\t\tif (!ts.grid ) { return; }\r\n
\t\t//-------------------------\r\n
\t\tvar subGridCell = function(trdiv,cell,pos)\r\n
\t\t{\r\n
\t\t\tvar tddiv = $("<td align=\'"+ts.p.subGridModel[0].align[pos]+"\'></td>").html(cell);\r\n
\t\t\t$(trdiv).append(tddiv);\r\n
\t\t};\r\n
\t\tvar subGridXml = function(sjxml, sbid){\r\n
\t\t\tvar tddiv, i,  sgmap,\r\n
\t\t\tdummy = $("<table cellspacing=\'0\' cellpadding=\'0\' border=\'0\'><tbody></tbody></table>"),\r\n
\t\t\ttrdiv = $("<tr></tr>");\r\n
\t\t\tfor (i = 0; i<ts.p.subGridModel[0].name.length; i++) {\r\n
\t\t\t\ttddiv = $("<th class=\'ui-state-default ui-th-subgrid ui-th-column ui-th-"+ts.p.direction+"\'></th>");\r\n
\t\t\t\t$(tddiv).html(ts.p.subGridModel[0].name[i]);\r\n
\t\t\t\t$(tddiv).width( ts.p.subGridModel[0].width[i]);\r\n
\t\t\t\t$(trdiv).append(tddiv);\r\n
\t\t\t}\r\n
\t\t\t$(dummy).append(trdiv);\r\n
\t\t\tif (sjxml){\r\n
\t\t\t\tsgmap = ts.p.xmlReader.subgrid;\r\n
\t\t\t\t$(sgmap.root+" "+sgmap.row, sjxml).each( function(){\r\n
\t\t\t\t\ttrdiv = $("<tr class=\'ui-widget-content ui-subtblcell\'></tr>");\r\n
\t\t\t\t\tif(sgmap.repeatitems === true) {\r\n
\t\t\t\t\t\t$(sgmap.cell,this).each( function(i) {\r\n
\t\t\t\t\t\t\tsubGridCell(trdiv, $(this).text() || \'&#160;\',i);\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tvar f = ts.p.subGridModel[0].mapping || ts.p.subGridModel[0].name;\r\n
\t\t\t\t\t\tif (f) {\r\n
\t\t\t\t\t\t\tfor (i=0;i<f.length;i++) {\r\n
\t\t\t\t\t\t\t\tsubGridCell(trdiv, $(f[i],this).text() || \'&#160;\',i);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$(dummy).append(trdiv);\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\tvar pID = $("table:first",ts.grid.bDiv).attr("id")+"_";\r\n
\t\t\t$("#"+$.jgrid.jqID(pID+sbid)).append(dummy);\r\n
\t\t\tts.grid.hDiv.loading = false;\r\n
\t\t\t$("#load_"+$.jgrid.jqID(ts.p.id)).hide();\r\n
\t\t\treturn false;\r\n
\t\t};\r\n
\t\tvar subGridJson = function(sjxml, sbid){\r\n
\t\t\tvar tddiv,result,i,cur, sgmap,j,\r\n
\t\t\tdummy = $("<table cellspacing=\'0\' cellpadding=\'0\' border=\'0\'><tbody></tbody></table>"),\r\n
\t\t\ttrdiv = $("<tr></tr>");\r\n
\t\t\tfor (i = 0; i<ts.p.subGridModel[0].name.length; i++) {\r\n
\t\t\t\ttddiv = $("<th class=\'ui-state-default ui-th-subgrid ui-th-column ui-th-"+ts.p.direction+"\'></th>");\r\n
\t\t\t\t$(tddiv).html(ts.p.subGridModel[0].name[i]);\r\n
\t\t\t\t$(tddiv).width( ts.p.subGridModel[0].width[i]);\r\n
\t\t\t\t$(trdiv).append(tddiv);\r\n
\t\t\t}\r\n
\t\t\t$(dummy).append(trdiv);\r\n
\t\t\tif (sjxml){\r\n
\t\t\t\tsgmap = ts.p.jsonReader.subgrid;\r\n
\t\t\t\tresult = $.jgrid.getAccessor(sjxml, sgmap.root);\r\n
\t\t\t\tif ( typeof result !== \'undefined\' ) {\r\n
\t\t\t\t\tfor (i=0;i<result.length;i++) {\r\n
\t\t\t\t\t\tcur = result[i];\r\n
\t\t\t\t\t\ttrdiv = $("<tr class=\'ui-widget-content ui-subtblcell\'></tr>");\r\n
\t\t\t\t\t\tif(sgmap.repeatitems === true) {\r\n
\t\t\t\t\t\t\tif(sgmap.cell) { cur=cur[sgmap.cell]; }\r\n
\t\t\t\t\t\t\tfor (j=0;j<cur.length;j++) {\r\n
\t\t\t\t\t\t\t\tsubGridCell(trdiv, cur[j] || \'&#160;\',j);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tvar f = ts.p.subGridModel[0].mapping || ts.p.subGridModel[0].name;\r\n
\t\t\t\t\t\t\tif(f.length) {\r\n
\t\t\t\t\t\t\t\tfor (j=0;j<f.length;j++) {\r\n
\t\t\t\t\t\t\t\t\tsubGridCell(trdiv, cur[f[j]] || \'&#160;\',j);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t$(dummy).append(trdiv);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tvar pID = $("table:first",ts.grid.bDiv).attr("id")+"_";\r\n
\t\t\t$("#"+$.jgrid.jqID(pID+sbid)).append(dummy);\r\n
\t\t\tts.grid.hDiv.loading = false;\r\n
\t\t\t$("#load_"+$.jgrid.jqID(ts.p.id)).hide();\r\n
\t\t\treturn false;\r\n
\t\t};\r\n
\t\tvar populatesubgrid = function( rd )\r\n
\t\t{\r\n
\t\t\tvar sid,dp, i, j;\r\n
\t\t\tsid = $(rd).attr("id");\r\n
\t\t\tdp = {nd_: (new Date().getTime())};\r\n
\t\t\tdp[ts.p.prmNames.subgridid]=sid;\r\n
\t\t\tif(!ts.p.subGridModel[0]) { return false; }\r\n
\t\t\tif(ts.p.subGridModel[0].params) {\r\n
\t\t\t\tfor(j=0; j < ts.p.subGridModel[0].params.length; j++) {\r\n
\t\t\t\t\tfor(i=0; i<ts.p.colModel.length; i++) {\r\n
\t\t\t\t\t\tif(ts.p.colModel[i].name === ts.p.subGridModel[0].params[j]) {\r\n
\t\t\t\t\t\t\tdp[ts.p.colModel[i].name]= $("td:eq("+i+")",rd).text().replace(/\\&#160\\;/ig,\'\');\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif(!ts.grid.hDiv.loading) {\r\n
\t\t\t\tts.grid.hDiv.loading = true;\r\n
\t\t\t\t$("#load_"+$.jgrid.jqID(ts.p.id)).show();\r\n
\t\t\t\tif(!ts.p.subgridtype) { ts.p.subgridtype = ts.p.datatype; }\r\n
\t\t\t\tif($.isFunction(ts.p.subgridtype)) {\r\n
\t\t\t\t\tts.p.subgridtype.call(ts, dp);\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tts.p.subgridtype = ts.p.subgridtype.toLowerCase();\r\n
\t\t\t\t}\r\n
\t\t\t\tswitch(ts.p.subgridtype) {\r\n
\t\t\t\t\tcase "xml":\r\n
\t\t\t\t\tcase "json":\r\n
\t\t\t\t\t$.ajax($.extend({\r\n
\t\t\t\t\t\ttype:ts.p.mtype,\r\n
\t\t\t\t\t\turl: ts.p.subGridUrl,\r\n
\t\t\t\t\t\tdataType:ts.p.subgridtype,\r\n
\t\t\t\t\t\tdata: $.isFunction(ts.p.serializeSubGridData)? ts.p.serializeSubGridData.call(ts, dp) : dp,\r\n
\t\t\t\t\t\tcomplete: function(sxml) {\r\n
\t\t\t\t\t\t\tif(ts.p.subgridtype === "xml") {\r\n
\t\t\t\t\t\t\t\tsubGridXml(sxml.responseXML, sid);\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tsubGridJson($.jgrid.parse(sxml.responseText),sid);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tsxml=null;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}, $.jgrid.ajaxOptions, ts.p.ajaxSubgridOptions || {}));\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\treturn false;\r\n
\t\t};\r\n
\t\tvar _id, pID,atd, nhc=0, bfsc, r;\r\n
\t\t$.each(ts.p.colModel,function(){\r\n
\t\t\tif(this.hidden === true || this.name === \'rn\' || this.name === \'cb\') {\r\n
\t\t\t\tnhc++;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\tvar len = ts.rows.length, i=1;\r\n
\t\tif( sind !== undefined && sind > 0) {\r\n
\t\t\ti = sind;\r\n
\t\t\tlen = sind+1;\r\n
\t\t}\r\n
\t\twhile(i < len) {\r\n
\t\t\tif($(ts.rows[i]).hasClass(\'jqgrow\')) {\r\n
\t\t\t\t$(ts.rows[i].cells[pos]).bind(\'click\', function() {\r\n
\t\t\t\t\tvar tr = $(this).parent("tr")[0];\r\n
\t\t\t\t\tr = tr.nextSibling;\r\n
\t\t\t\t\tif($(this).hasClass("sgcollapsed")) {\r\n
\t\t\t\t\t\tpID = ts.p.id;\r\n
\t\t\t\t\t\t_id = tr.id;\r\n
\t\t\t\t\t\tif(ts.p.subGridOptions.reloadOnExpand === true || ( ts.p.subGridOptions.reloadOnExpand === false && !$(r).hasClass(\'ui-subgrid\') ) ) {\r\n
\t\t\t\t\t\t\tatd = pos >=1 ? "<td colspan=\'"+pos+"\'>&#160;</td>":"";\r\n
\t\t\t\t\t\t\tbfsc = $(ts).triggerHandler("jqGridSubGridBeforeExpand", [pID + "_" + _id, _id]);\r\n
\t\t\t\t\t\t\tbfsc = (bfsc === false || bfsc === \'stop\') ? false : true;\r\n
\t\t\t\t\t\t\tif(bfsc && $.isFunction(ts.p.subGridBeforeExpand)) {\r\n
\t\t\t\t\t\t\t\tbfsc = ts.p.subGridBeforeExpand.call(ts, pID+"_"+_id,_id);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\tif(bfsc === false) {return false;}\r\n
\t\t\t\t\t\t\t$(tr).after( "<tr role=\'row\' class=\'ui-subgrid\'>"+atd+"<td class=\'ui-widget-content subgrid-cell\'><span class=\'ui-icon "+ts.p.subGridOptions.openicon+"\'></span></td><td colspan=\'"+parseInt(ts.p.colNames.length-1-nhc,10)+"\' class=\'ui-widget-content subgrid-data\'><div id="+pID+"_"+_id+" class=\'tablediv\'></div></td></tr>" );\r\n
\t\t\t\t\t\t\t$(ts).triggerHandler("jqGridSubGridRowExpanded", [pID + "_" + _id, _id]);\r\n
\t\t\t\t\t\t\tif( $.isFunction(ts.p.subGridRowExpanded)) {\r\n
\t\t\t\t\t\t\t\tts.p.subGridRowExpanded.call(ts, pID+"_"+ _id,_id);\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tpopulatesubgrid(tr);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t$(r).show();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t$(this).html("<a href=\'javascript:void(0);\'><span class=\'ui-icon "+ts.p.subGridOptions.minusicon+"\'></span></a>").removeClass("sgcollapsed").addClass("sgexpanded");\r\n
\t\t\t\t\t\tif(ts.p.subGridOptions.selectOnExpand) {\r\n
\t\t\t\t\t\t\t$(ts).jqGrid(\'setSelection\',_id);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t} else if($(this).hasClass("sgexpanded")) {\r\n
\t\t\t\t\t\tbfsc = $(ts).triggerHandler("jqGridSubGridRowColapsed", [pID + "_" + _id, _id]);\r\n
\t\t\t\t\t\tbfsc = (bfsc === false || bfsc === \'stop\') ? false : true;\r\n
\t\t\t\t\t\tif( bfsc &&  $.isFunction(ts.p.subGridRowColapsed)) {\r\n
\t\t\t\t\t\t\t_id = tr.id;\r\n
\t\t\t\t\t\t\tbfsc = ts.p.subGridRowColapsed.call(ts, pID+"_"+_id,_id );\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(bfsc===false) {return false;}\r\n
\t\t\t\t\t\tif(ts.p.subGridOptions.reloadOnExpand === true) {\r\n
\t\t\t\t\t\t\t$(r).remove(".ui-subgrid");\r\n
\t\t\t\t\t\t} else if($(r).hasClass(\'ui-subgrid\')) { // incase of dynamic deleting\r\n
\t\t\t\t\t\t\t$(r).hide();\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t$(this).html("<a href=\'javascript:void(0);\'><span class=\'ui-icon "+ts.p.subGridOptions.plusicon+"\'></span></a>").removeClass("sgexpanded").addClass("sgcollapsed");\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn false;\r\n
\t\t\t\t});\r\n
\t\t\t}\r\n
\t\t\ti++;\r\n
\t\t}\r\n
\t\tif(ts.p.subGridOptions.expandOnLoad === true) {\r\n
\t\t\t$(ts.rows).filter(\'.jqgrow\').each(function(index,row){\r\n
\t\t\t\t$(row.cells[0]).click();\r\n
\t\t\t});\r\n
\t\t}\r\n
\t\tts.subGridXml = function(xml,sid) {subGridXml(xml,sid);};\r\n
\t\tts.subGridJson = function(json,sid) {subGridJson(json,sid);};\r\n
\t});\r\n
},\r\n
expandSubGridRow : function(rowid) {\r\n
\treturn this.each(function () {\r\n
\t\tvar $t = this;\r\n
\t\tif(!$t.grid && !rowid) {return;}\r\n
\t\tif($t.p.subGrid===true) {\r\n
\t\t\tvar rc = $(this).jqGrid("getInd",rowid,true);\r\n
\t\t\tif(rc) {\r\n
\t\t\t\tvar sgc = $("td.sgcollapsed",rc)[0];\r\n
\t\t\t\tif(sgc) {\r\n
\t\t\t\t\t$(sgc).trigger("click");\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t});\r\n
},\r\n
collapseSubGridRow : function(rowid) {\r\n
\treturn this.each(function () {\r\n
\t\tvar $t = this;\r\n
\t\tif(!$t.grid && !rowid) {return;}\r\n
\t\tif($t.p.subGrid===true) {\r\n
\t\t\tvar rc = $(this).jqGrid("getInd",rowid,true);\r\n
\t\t\tif(rc) {\r\n
\t\t\t\tvar sgc = $("td.sgexpanded",rc)[0];\r\n
\t\t\t\tif(sgc) {\r\n
\t\t\t\t\t$(sgc).trigger("click");\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t});\r\n
},\r\n
toggleSubGridRow : function(rowid) {\r\n
\treturn this.each(function () {\r\n
\t\tvar $t = this;\r\n
\t\tif(!$t.grid && !rowid) {return;}\r\n
\t\tif($t.p.subGrid===true) {\r\n
\t\t\tvar rc = $(this).jqGrid("getInd",rowid,true);\r\n
\t\t\tif(rc) {\r\n
\t\t\t\tvar sgc = $("td.sgcollapsed",rc)[0];\r\n
\t\t\t\tif(sgc) {\r\n
\t\t\t\t\t$(sgc).trigger("click");\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tsgc = $("td.sgexpanded",rc)[0];\r\n
\t\t\t\t\tif(sgc) {\r\n
\t\t\t\t\t\t$(sgc).trigger("click");\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
\t});\r\n
}\r\n
});\r\n
})(jQuery);\r\n
/**\r\n
 * jqGrid extension - Tree Grid\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/\r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl.html\r\n
**/\r\n
\r\n
/*global document, jQuery, $ */\r\n
(function($) {\r\n
"use strict";\r\n
$.jgrid.extend({\r\n
\tsetTreeNode : function(i, len){\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif( !$t.grid || !$t.p.treeGrid ) {return;}\r\n
\t\t\tvar expCol = $t.p.expColInd,\r\n
\t\t\texpanded = $t.p.treeReader.expanded_field,\r\n
\t\t\tisLeaf = $t.p.treeReader.leaf_field,\r\n
\t\t\tlevel = $t.p.treeReader.level_field,\r\n
\t\t\ticon = $t.p.treeReader.icon_field,\r\n
\t\t\tloaded = $t.p.treeReader.loaded,  lft, rgt, curLevel, ident,lftpos, twrap,\r\n
\t\t\tldat, lf;\r\n
\t\t\twhile(i<len) {\r\n
\t\t\t\tvar ind = $t.rows[i].id, dind = $t.p._index[ind], expan;\r\n
\t\t\t\tldat = $t.p.data[dind];\r\n
\t\t\t\t//$t.rows[i].level = ldat[level];\r\n
\t\t\t\tif($t.p.treeGridModel == \'nested\') {\r\n
\t\t\t\t\tif(!ldat[isLeaf]) {\r\n
\t\t\t\t\tlft = parseInt(ldat[$t.p.treeReader.left_field],10);\r\n
\t\t\t\t\trgt = parseInt(ldat[$t.p.treeReader.right_field],10);\r\n
\t\t\t\t\t// NS Model\r\n
\t\t\t\t\t\tldat[isLeaf] = (rgt === lft+1) ? \'

]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <persistent> <string encoding="base64">AAAAAAAAAAc=</string> </persistent>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
  <record id="7" aka="AAAAAAAAAAc=">
    <pickle>
      <global name="Pdata" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

true\' : \'false\';\r\n
\t\t\t\t\t\t$t.rows[i].cells[$t.p._treeleafpos].innerHTML = ldat[isLeaf];\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\t//else {\r\n
\t\t\t\t\t//row.parent_id = rd[$t.p.treeReader.parent_id_field];\r\n
\t\t\t\t//}\r\n
\t\t\t\tcurLevel = parseInt(ldat[level],10);\r\n
\t\t\t\tif($t.p.tree_root_level === 0) {\r\n
\t\t\t\t\tident = curLevel+1;\r\n
\t\t\t\t\tlftpos = curLevel;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tident = curLevel;\r\n
\t\t\t\t\tlftpos = curLevel -1;\r\n
\t\t\t\t}\r\n
\t\t\t\ttwrap = "<div class=\'tree-wrap tree-wrap-"+$t.p.direction+"\' style=\'width:"+(ident*18)+"px;\'>";\r\n
\t\t\t\ttwrap += "<div style=\'"+($t.p.direction=="rtl" ? "right:" : "left:")+(lftpos*18)+"px;\' class=\'ui-icon ";\r\n
\r\n
\r\n
\t\t\t\tif(ldat[loaded] !== undefined) {\r\n
\t\t\t\t\tif(ldat[loaded]=="true" || ldat[loaded]===true) {\r\n
\t\t\t\t\t\tldat[loaded] = true;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tldat[loaded] = false;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif(ldat[isLeaf] == "true" || ldat[isLeaf] === true) {\r\n
\t\t\t\t\ttwrap += ((ldat[icon] !== undefined && ldat[icon] !== "") ? ldat[icon] : $t.p.treeIcons.leaf)+" tree-leaf treeclick";\r\n
\t\t\t\t\tldat[isLeaf] = true;\r\n
\t\t\t\t\tlf="leaf";\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tldat[isLeaf] = false;\r\n
\t\t\t\t\tlf="";\r\n
\t\t\t\t}\r\n
\t\t\t\tldat[expanded] = ((ldat[expanded] == "true" || ldat[expanded] === true) ? true : false) && ldat[loaded];\r\n
\t\t\t\tif(ldat[expanded] === false) {\r\n
\t\t\t\t\ttwrap += ((ldat[isLeaf] === true) ? "\'" : $t.p.treeIcons.plus+" tree-plus treeclick\'");\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\ttwrap += ((ldat[isLeaf] === true) ? "\'" : $t.p.treeIcons.minus+" tree-minus treeclick\'");\r\n
\t\t\t\t}\r\n
\t\t\t\t\r\n
\t\t\t\ttwrap += "></div></div>";\r\n
\t\t\t\t$($t.rows[i].cells[expCol]).wrapInner("<span class=\'cell-wrapper"+lf+"\'></span>").prepend(twrap);\r\n
\r\n
\t\t\t\tif(curLevel !== parseInt($t.p.tree_root_level,10)) {\r\n
\t\t\t\t\tvar pn = $($t).jqGrid(\'getNodeParent\',ldat);\r\n
\t\t\t\t\texpan = pn && pn.hasOwnProperty(expanded) ? pn[expanded] : true;\r\n
\t\t\t\t\tif( !expan ){\r\n
\t\t\t\t\t\t$($t.rows[i]).css("display","none");\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\t$($t.rows[i].cells[expCol])\r\n
\t\t\t\t\t.find("div.treeclick")\r\n
\t\t\t\t\t.bind("click",function(e){\r\n
\t\t\t\t\t\tvar target = e.target || e.srcElement,\r\n
\t\t\t\t\t\tind2 =$(target,$t.rows).closest("tr.jqgrow")[0].id,\r\n
\t\t\t\t\t\tpos = $t.p._index[ind2];\r\n
\t\t\t\t\t\tif(!$t.p.data[pos][isLeaf]){\r\n
\t\t\t\t\t\t\tif($t.p.data[pos][expanded]){\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid("collapseRow",$t.p.data[pos]);\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid("collapseNode",$t.p.data[pos]);\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid("expandRow",$t.p.data[pos]);\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid("expandNode",$t.p.data[pos]);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t});\r\n
\t\t\t\tif($t.p.ExpandColClick === true) {\r\n
\t\t\t\t\t$($t.rows[i].cells[expCol])\r\n
\t\t\t\t\t\t.find("span.cell-wrapper")\r\n
\t\t\t\t\t\t.css("cursor","pointer")\r\n
\t\t\t\t\t\t.bind("click",function(e) {\r\n
\t\t\t\t\t\t\tvar target = e.target || e.srcElement,\r\n
\t\t\t\t\t\t\tind2 =$(target,$t.rows).closest("tr.jqgrow")[0].id,\r\n
\t\t\t\t\t\t\tpos = $t.p._index[ind2];\r\n
\t\t\t\t\t\t\tif(!$t.p.data[pos][isLeaf]){\r\n
\t\t\t\t\t\t\t\tif($t.p.data[pos][expanded]){\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("collapseRow",$t.p.data[pos]);\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("collapseNode",$t.p.data[pos]);\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("expandRow",$t.p.data[pos]);\r\n
\t\t\t\t\t\t\t\t\t$($t).jqGrid("expandNode",$t.p.data[pos]);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t$($t).jqGrid("setSelection",ind2);\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t}\r\n
\t\t\t\ti++;\r\n
\t\t\t}\r\n
\r\n
\t\t});\r\n
\t},\r\n
\tsetTreeGrid : function() {\r\n
\t\treturn this.each(function (){\r\n
\t\t\tvar $t = this, i=0, pico, ecol = false, nm, key, dupcols=[];\r\n
\t\t\tif(!$t.p.treeGrid) {return;}\r\n
\t\t\tif(!$t.p.treedatatype ) {$.extend($t.p,{treedatatype: $t.p.datatype});}\r\n
\t\t\t$t.p.subGrid = false;$t.p.altRows =false;\r\n
\t\t\t$t.p.pgbuttons = false;$t.p.pginput = false;\r\n
\t\t\t$t.p.gridview =  true;\r\n
\t\t\tif($t.p.rowTotal === null ) { $t.p.rowNum = 10000; }\r\n
\t\t\t$t.p.multiselect = false;$t.p.rowList = [];\r\n
\t\t\t$t.p.expColInd = 0;\r\n
\t\t\tpico = \'ui-icon-triangle-1-\' + ($t.p.direction=="rtl" ? \'w\' : \'e\');\r\n
\t\t\t$t.p.treeIcons = $.extend({plus:pico,minus:\'ui-icon-triangle-1-s\',leaf:\'ui-icon-radio-off\'},$t.p.treeIcons || {});\r\n
\t\t\tif($t.p.treeGridModel == \'nested\') {\r\n
\t\t\t\t$t.p.treeReader = $.extend({\r\n
\t\t\t\t\tlevel_field: "level",\r\n
\t\t\t\t\tleft_field:"lft",\r\n
\t\t\t\t\tright_field: "rgt",\r\n
\t\t\t\t\tleaf_field: "isLeaf",\r\n
\t\t\t\t\texpanded_field: "expanded",\r\n
\t\t\t\t\tloaded: "loaded",\r\n
\t\t\t\t\ticon_field: "icon"\r\n
\t\t\t\t},$t.p.treeReader);\r\n
\t\t\t} else if($t.p.treeGridModel == \'adjacency\') {\r\n
\t\t\t\t$t.p.treeReader = $.extend({\r\n
\t\t\t\t\t\tlevel_field: "level",\r\n
\t\t\t\t\t\tparent_id_field: "parent",\r\n
\t\t\t\t\t\tleaf_field: "isLeaf",\r\n
\t\t\t\t\t\texpanded_field: "expanded",\r\n
\t\t\t\t\t\tloaded: "loaded",\r\n
\t\t\t\t\t\ticon_field: "icon"\r\n
\t\t\t\t},$t.p.treeReader );\r\n
\t\t\t}\r\n
\t\t\tfor ( key in $t.p.colModel){\r\n
\t\t\t\tif($t.p.colModel.hasOwnProperty(key)) {\r\n
\t\t\t\t\tnm = $t.p.colModel[key].name;\r\n
\t\t\t\t\tif( nm == $t.p.ExpandColumn && !ecol ) {\r\n
\t\t\t\t\t\tecol = true;\r\n
\t\t\t\t\t\t$t.p.expColInd = i;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\ti++;\r\n
\t\t\t\t\t//\r\n
\t\t\t\t\tfor(var tkey in $t.p.treeReader) {\r\n
\t\t\t\t\t\tif($t.p.treeReader[tkey] == nm) {\r\n
\t\t\t\t\t\t\tdupcols.push(nm);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\t$.each($t.p.treeReader,function(j,n){\r\n
\t\t\t\tif(n && $.inArray(n, dupcols) === -1){\r\n
\t\t\t\t\tif(j===\'leaf_field\') { $t.p._treeleafpos= i; }\r\n
\t\t\t\ti++;\r\n
\t\t\t\t\t$t.p.colNames.push(n);\r\n
\t\t\t\t\t$t.p.colModel.push({name:n,width:1,hidden:true,sortable:false,resizable:false,hidedlg:true,editable:true,search:false});\r\n
\t\t\t\t}\r\n
\t\t\t});\t\t\t\r\n
\t\t});\r\n
\t},\r\n
\texpandRow: function (record){\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tvar childern = $($t).jqGrid("getNodeChildren",record),\r\n
\t\t\t//if ($($t).jqGrid("isVisibleNode",record)) {\r\n
\t\t\texpanded = $t.p.treeReader.expanded_field,\r\n
\t\t\trows = $t.rows;\r\n
\t\t\t$(childern).each(function(){\r\n
\t\t\t\tvar id  = $.jgrid.getAccessor(this,$t.p.localReader.id);\r\n
\t\t\t\t$(rows.namedItem(id)).css("display","");\r\n
\t\t\t\tif(this[expanded]) {\r\n
\t\t\t\t\t$($t).jqGrid("expandRow",this);\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\t//}\r\n
\t\t});\r\n
\t},\r\n
\tcollapseRow : function (record) {\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tvar childern = $($t).jqGrid("getNodeChildren",record),\r\n
\t\t\texpanded = $t.p.treeReader.expanded_field,\r\n
\t\t\trows = $t.rows;\r\n
\t\t\t$(childern).each(function(){\r\n
\t\t\t\tvar id  = $.jgrid.getAccessor(this,$t.p.localReader.id);\r\n
\t\t\t\t$(rows.namedItem(id)).css("display","none");\r\n
\t\t\t\tif(this[expanded]){\r\n
\t\t\t\t\t$($t).jqGrid("collapseRow",this);\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t});\r\n
\t},\r\n
\t// NS ,adjacency models\r\n
\tgetRootNodes : function() {\r\n
\t\tvar result = [];\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tswitch ($t.p.treeGridModel) {\r\n
\t\t\t\tcase \'nested\' :\r\n
\t\t\t\t\tvar level = $t.p.treeReader.level_field;\r\n
\t\t\t\t\t$($t.p.data).each(function(){\r\n
\t\t\t\t\t\tif(parseInt(this[level],10) === parseInt($t.p.tree_root_level,10)) {\r\n
\t\t\t\t\t\t\tresult.push(this);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'adjacency\' :\r\n
\t\t\t\t\tvar parent_id = $t.p.treeReader.parent_id_field;\r\n
\t\t\t\t\t$($t.p.data).each(function(){\r\n
\t\t\t\t\t\tif(this[parent_id] === null || String(this[parent_id]).toLowerCase() == "null") {\r\n
\t\t\t\t\t\t\tresult.push(this);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn result;\r\n
\t},\r\n
\tgetNodeDepth : function(rc) {\r\n
\t\tvar ret = null;\r\n
\t\tthis.each(function(){\r\n
\t\t\tif(!this.grid || !this.p.treeGrid) {return;}\r\n
\t\t\tvar $t = this;\r\n
\t\t\tswitch ($t.p.treeGridModel) {\r\n
\t\t\t\tcase \'nested\' :\r\n
\t\t\t\t\tvar level = $t.p.treeReader.level_field;\r\n
\t\t\t\t\tret = parseInt(rc[level],10) - parseInt($t.p.tree_root_level,10);\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'adjacency\' :\r\n
\t\t\t\t\tret = $($t).jqGrid("getNodeAncestors",rc).length;\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn ret;\r\n
\t},\r\n
\tgetNodeParent : function(rc) {\r\n
\t\tvar result = null;\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tswitch ($t.p.treeGridModel) {\r\n
\t\t\t\tcase \'nested\' :\r\n
\t\t\t\t\tvar lftc = $t.p.treeReader.left_field,\r\n
\t\t\t\t\trgtc = $t.p.treeReader.right_field,\r\n
\t\t\t\t\tlevelc = $t.p.treeReader.level_field,\r\n
\t\t\t\t\tlft = parseInt(rc[lftc],10), rgt = parseInt(rc[rgtc],10), level = parseInt(rc[levelc],10);\r\n
\t\t\t\t\t$(this.p.data).each(function(){\r\n
\t\t\t\t\t\tif(parseInt(this[levelc],10) === level-1 && parseInt(this[lftc],10) < lft && parseInt(this[rgtc],10) > rgt) {\r\n
\t\t\t\t\t\t\tresult = this;\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'adjacency\' :\r\n
\t\t\t\t\tvar parent_id = $t.p.treeReader.parent_id_field,\r\n
\t\t\t\t\tdtid = $t.p.localReader.id;\r\n
\t\t\t\t\t$(this.p.data).each(function(){\r\n
\t\t\t\t\t\tif(this[dtid] == rc[parent_id] ) {\r\n
\t\t\t\t\t\t\tresult = this;\r\n
\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn result;\r\n
\t},\r\n
\tgetNodeChildren : function(rc) {\r\n
\t\tvar result = [];\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tswitch ($t.p.treeGridModel) {\r\n
\t\t\t\tcase \'nested\' :\r\n
\t\t\t\t\tvar lftc = $t.p.treeReader.left_field,\r\n
\t\t\t\t\trgtc = $t.p.treeReader.right_field,\r\n
\t\t\t\t\tlevelc = $t.p.treeReader.level_field,\r\n
\t\t\t\t\tlft = parseInt(rc[lftc],10), rgt = parseInt(rc[rgtc],10), level = parseInt(rc[levelc],10);\r\n
\t\t\t\t\t$(this.p.data).each(function(){\r\n
\t\t\t\t\t\tif(parseInt(this[levelc],10) === level+1 && parseInt(this[lftc],10) > lft && parseInt(this[rgtc],10) < rgt) {\r\n
\t\t\t\t\t\t\tresult.push(this);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'adjacency\' :\r\n
\t\t\t\t\tvar parent_id = $t.p.treeReader.parent_id_field,\r\n
\t\t\t\t\tdtid = $t.p.localReader.id;\r\n
\t\t\t\t\t$(this.p.data).each(function(){\r\n
\t\t\t\t\t\tif(this[parent_id] == rc[dtid]) {\r\n
\t\t\t\t\t\t\tresult.push(this);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn result;\r\n
\t},\r\n
\tgetFullTreeNode : function(rc) {\r\n
\t\tvar result = [];\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this, len;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tswitch ($t.p.treeGridModel) {\r\n
\t\t\t\tcase \'nested\' :\r\n
\t\t\t\t\tvar lftc = $t.p.treeReader.left_field,\r\n
\t\t\t\t\trgtc = $t.p.treeReader.right_field,\r\n
\t\t\t\t\tlevelc = $t.p.treeReader.level_field,\r\n
\t\t\t\t\tlft = parseInt(rc[lftc],10), rgt = parseInt(rc[rgtc],10), level = parseInt(rc[levelc],10);\r\n
\t\t\t\t\t$(this.p.data).each(function(){\r\n
\t\t\t\t\t\tif(parseInt(this[levelc],10) >= level && parseInt(this[lftc],10) >= lft && parseInt(this[lftc],10) <= rgt) {\r\n
\t\t\t\t\t\t\tresult.push(this);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\tcase \'adjacency\' :\r\n
\t\t\t\t\tif(rc) {\r\n
\t\t\t\t\tresult.push(rc);\r\n
\t\t\t\t\tvar parent_id = $t.p.treeReader.parent_id_field,\r\n
\t\t\t\t\tdtid = $t.p.localReader.id;\r\n
\t\t\t\t\t$(this.p.data).each(function(i){\r\n
\t\t\t\t\t\tlen = result.length;\r\n
\t\t\t\t\t\tfor (i = 0; i < len; i++) {\r\n
\t\t\t\t\t\t\tif (result[i][dtid] == this[parent_id]) {\r\n
\t\t\t\t\t\t\t\tresult.push(this);\r\n
\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn result;\r\n
\t},\t\r\n
\t// End NS, adjacency Model\r\n
\tgetNodeAncestors : function(rc) {\r\n
\t\tvar ancestors = [];\r\n
\t\tthis.each(function(){\r\n
\t\t\tif(!this.grid || !this.p.treeGrid) {return;}\r\n
\t\t\tvar parent = $(this).jqGrid("getNodeParent",rc);\r\n
\t\t\twhile (parent) {\r\n
\t\t\t\tancestors.push(parent);\r\n
\t\t\t\tparent = $(this).jqGrid("getNodeParent",parent);\t\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn ancestors;\r\n
\t},\r\n
\tisVisibleNode : function(rc) {\r\n
\t\tvar result = true;\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tvar ancestors = $($t).jqGrid("getNodeAncestors",rc),\r\n
\t\t\texpanded = $t.p.treeReader.expanded_field;\r\n
\t\t\t$(ancestors).each(function(){\r\n
\t\t\t\tresult = result && this[expanded];\r\n
\t\t\t\tif(!result) {return false;}\r\n
\t\t\t});\r\n
\t\t});\r\n
\t\treturn result;\r\n
\t},\r\n
\tisNodeLoaded : function(rc) {\r\n
\t\tvar result;\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tvar isLeaf = $t.p.treeReader.leaf_field;\r\n
\t\t\tif(rc !== undefined ) {\r\n
\t\t\t\tif(rc.loaded !== undefined) {\r\n
\t\t\t\t\tresult = rc.loaded;\r\n
\t\t\t\t} else if( rc[isLeaf] || $($t).jqGrid("getNodeChildren",rc).length > 0){\r\n
\t\t\t\t\tresult = true;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tresult = false;\r\n
\t\t\t\t}\r\n
\t\t\t} else {\r\n
\t\t\t\tresult = false;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\treturn result;\r\n
\t},\r\n
\texpandNode : function(rc) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif(!this.grid || !this.p.treeGrid) {return;}\r\n
\t\t\tvar expanded = this.p.treeReader.expanded_field,\r\n
\t\t\tparent = this.p.treeReader.parent_id_field,\r\n
\t\t\tloaded = this.p.treeReader.loaded,\r\n
\t\t\tlevel = this.p.treeReader.level_field,\r\n
\t\t\tlft = this.p.treeReader.left_field,\r\n
\t\t\trgt = this.p.treeReader.right_field;\r\n
\r\n
\t\t\tif(!rc[expanded]) {\r\n
\t\t\t\tvar id = $.jgrid.getAccessor(rc,this.p.localReader.id);\r\n
\t\t\t\tvar rc1 = $("#"+$.jgrid.jqID(id),this.grid.bDiv)[0];\r\n
\t\t\t\tvar position = this.p._index[id];\r\n
\t\t\t\tif( $(this).jqGrid("isNodeLoaded",this.p.data[position]) ) {\r\n
\t\t\t\t\trc[expanded] = true;\r\n
\t\t\t\t\t$("div.treeclick",rc1).removeClass(this.p.treeIcons.plus+" tree-plus").addClass(this.p.treeIcons.minus+" tree-minus");\r\n
\t\t\t\t} else if (!this.grid.hDiv.loading) {\r\n
\t\t\t\t\trc[expanded] = true;\r\n
\t\t\t\t\t$("div.treeclick",rc1).removeClass(this.p.treeIcons.plus+" tree-plus").addClass(this.p.treeIcons.minus+" tree-minus");\r\n
\t\t\t\t\tthis.p.treeANode = rc1.rowIndex;\r\n
\t\t\t\t\tthis.p.datatype = this.p.treedatatype;\r\n
\t\t\t\t\tif(this.p.treeGridModel == \'nested\') {\r\n
\t\t\t\t\t\t$(this).jqGrid("setGridParam",{postData:{nodeid:id,n_left:rc[lft],n_right:rc[rgt],n_level:rc[level]}});\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$(this).jqGrid("setGridParam",{postData:{nodeid:id,parentid:rc[parent],n_level:rc[level]}} );\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t$(this).trigger("reloadGrid");\r\n
\t\t\t\t\trc[loaded] = true;\r\n
\t\t\t\t\tif(this.p.treeGridModel == \'nested\') {\r\n
\t\t\t\t\t\t$(this).jqGrid("setGridParam",{postData:{nodeid:\'\',n_left:\'\',n_right:\'\',n_level:\'\'}});\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t$(this).jqGrid("setGridParam",{postData:{nodeid:\'\',parentid:\'\',n_level:\'\'}}); \r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tcollapseNode : function(rc) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif(!this.grid || !this.p.treeGrid) {return;}\r\n
\t\t\tvar expanded = this.p.treeReader.expanded_field;\r\n
\t\t\tif(rc[expanded]) {\r\n
\t\t\t\trc[expanded] = false;\r\n
\t\t\t\tvar id = $.jgrid.getAccessor(rc,this.p.localReader.id);\r\n
\t\t\t\tvar rc1 = $("#"+$.jgrid.jqID(id),this.grid.bDiv)[0];\r\n
\t\t\t\t$("div.treeclick",rc1).removeClass(this.p.treeIcons.minus+" tree-minus").addClass(this.p.treeIcons.plus+" tree-plus");\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tSortTree : function( sortname, newDir, st, datefmt) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif(!this.grid || !this.p.treeGrid) {return;}\r\n
\t\t\tvar i, len,\r\n
\t\t\trec, records = [], $t = this, query, roots,\r\n
\t\t\trt = $(this).jqGrid("getRootNodes");\r\n
\t\t\t// Sorting roots\r\n
\t\t\tquery = $.jgrid.from(rt);\r\n
\t\t\tquery.orderBy(sortname,newDir,st, datefmt);\r\n
\t\t\troots = query.select();\r\n
\r\n
\t\t\t// Sorting children\r\n
\t\t\tfor (i = 0, len = roots.length; i < len; i++) {\r\n
\t\t\t\trec = roots[i];\r\n
\t\t\t\trecords.push(rec);\r\n
\t\t\t\t$(this).jqGrid("collectChildrenSortTree",records, rec, sortname, newDir,st, datefmt);\r\n
\t\t\t}\r\n
\t\t\t$.each(records, function(index) {\r\n
\t\t\t\tvar id  = $.jgrid.getAccessor(this,$t.p.localReader.id);\r\n
\t\t\t\t$(\'#\'+$.jgrid.jqID($t.p.id)+ \' tbody tr:eq(\'+index+\')\').after($(\'tr#\'+$.jgrid.jqID(id),$t.grid.bDiv));\r\n
\t\t\t});\r\n
\t\t\tquery = null;roots=null;records=null;\r\n
\t\t});\r\n
\t},\r\n
\tcollectChildrenSortTree : function(records, rec, sortname, newDir,st, datefmt) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tif(!this.grid || !this.p.treeGrid) {return;}\r\n
\t\t\tvar i, len,\r\n
\t\t\tchild, ch, query, children;\r\n
\t\t\tch = $(this).jqGrid("getNodeChildren",rec);\r\n
\t\t\tquery = $.jgrid.from(ch);\r\n
\t\t\tquery.orderBy(sortname, newDir, st, datefmt);\r\n
\t\t\tchildren = query.select();\r\n
\t\t\tfor (i = 0, len = children.length; i < len; i++) {\r\n
\t\t\t\tchild = children[i];\r\n
\t\t\t\trecords.push(child);\r\n
\t\t\t\t$(this).jqGrid("collectChildrenSortTree",records, child, sortname, newDir, st, datefmt); \r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\t// experimental \r\n
\tsetTreeRow : function(rowid, data) {\r\n
\t\tvar success=false;\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar t = this;\r\n
\t\t\tif(!t.grid || !t.p.treeGrid) {return;}\r\n
\t\t\tsuccess = $(t).jqGrid("setRowData",rowid,data);\r\n
\t\t});\r\n
\t\treturn success;\r\n
\t},\r\n
\tdelTreeNode : function (rowid) {\r\n
\t\treturn this.each(function () {\r\n
\t\t\tvar $t = this, rid = $t.p.localReader.id,\r\n
\t\t\tleft = $t.p.treeReader.left_field,\r\n
\t\t\tright = $t.p.treeReader.right_field, myright, width, res, key;\r\n
\t\t\tif(!$t.grid || !$t.p.treeGrid) {return;}\r\n
\t\t\tvar rc = $t.p._index[rowid];\r\n
\t\t\tif (rc !== undefined) {\r\n
\t\t\t\t// nested\r\n
\t\t\t\tmyright = parseInt($t.p.data[rc][right],10);\r\n
\t\t\t\twidth = myright -  parseInt($t.p.data[rc][left],10) + 1;\r\n
\t\t\t\tvar dr = $($t).jqGrid("getFullTreeNode",$t.p.data[rc]);\r\n
\t\t\t\tif(dr.length>0){\r\n
\t\t\t\t\tfor (var i=0;i<dr.length;i++){\r\n
\t\t\t\t\t\t$($t).jqGrid("delRowData",dr[i][rid]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tif( $t.p.treeGridModel === "nested") {\r\n
\t\t\t\t\t// ToDo - update grid data\r\n
\t\t\t\t\tres = $.jgrid.from($t.p.data)\r\n
\t\t\t\t\t\t.greater(left,myright,{stype:\'integer\'})\r\n
\t\t\t\t\t\t.select();\r\n
\t\t\t\t\tif(res.length) {\r\n
\t\t\t\t\t\tfor( key in res) {\r\n
\t\t\t\t\t\t\tif(res.hasOwnProperty(key)) {\r\n
\t\t\t\t\t\t\t\tres[key][left] = parseInt(res[key][left],10) - width ;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tres = $.jgrid.from($t.p.data)\r\n
\t\t\t\t\t\t.greater(right,myright,{stype:\'integer\'})\r\n
\t\t\t\t\t\t.select();\r\n
\t\t\t\t\tif(res.length) {\r\n
\t\t\t\t\t\tfor( key in res) {\r\n
\t\t\t\t\t\t\tif(res.hasOwnProperty(key)) {\r\n
\t\t\t\t\t\t\t\tres[key][right] = parseInt(res[key][right],10) - width ;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\taddChildNode : function( nodeid, parentid, data ) {\r\n
\t\t//return this.each(function(){\r\n
\t\tvar $t = this[0];\r\n
\t\tif(data) {\r\n
\t\t\t// we suppose tha the id is autoincremet and\r\n
\t\t\tvar expanded = $t.p.treeReader.expanded_field,\r\n
\t\t\tisLeaf = $t.p.treeReader.leaf_field,\r\n
\t\t\tlevel = $t.p.treeReader.level_field,\r\n
\t\t\t//icon = $t.p.treeReader.icon_field,\r\n
\t\t\tparent = $t.p.treeReader.parent_id_field,\r\n
\t\t\tleft = $t.p.treeReader.left_field,\r\n
\t\t\tright = $t.p.treeReader.right_field,\r\n
\t\t\tloaded = $t.p.treeReader.loaded,\r\n
\t\t\tmethod, parentindex, parentdata, parentlevel, i, len, max=0, rowind = parentid, leaf, maxright;\r\n
\r\n
\t\t\tif ( typeof nodeid === \'undefined\' || nodeid === null ) {\r\n
\t\t\t\ti = $t.p.data.length-1;\r\n
\t\t\t\tif(\ti>= 0 ) {\r\n
\t\t\t\t\twhile(i>=0){max = Math.max(max, parseInt($t.p.data[i][$t.p.localReader.id],10)); i--;}\r\n
\t\t\t\t}\r\n
\t\t\t\tnodeid = max+1;\r\n
\t\t\t}\r\n
\t\t\tvar prow = $($t).jqGrid(\'getInd\', parentid);\r\n
\t\t\t\tleaf = false;\r\n
\t\t\t\t// if not a parent we assume root\r\n
\t\t\t\tif ( parentid === undefined  || parentid === null || parentid==="") {\r\n
\t\t\t\t\tparentid = null;\r\n
\t\t\t\t\trowind = null;\r\n
\t\t\t\t\tmethod = \'last\';\r\n
\t\t\t\t\tparentlevel = $t.p.tree_root_level;\r\n
\t\t\t\t\ti = $t.p.data.length+1;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tmethod = \'after\';\r\n
\t\t\t\t\tparentindex = $t.p._index[parentid];\r\n
\t\t\t\t\tparentdata = $t.p.data[parentindex];\r\n
\t\t\t\t\tparentid = parentdata[$t.p.localReader.id];\r\n
\t\t\t\t\tparentlevel = parseInt(parentdata[level],10)+1;\r\n
\t\t\t\t\tvar childs = $($t).jqGrid(\'getFullTreeNode\', parentdata);\r\n
\t\t\t\t\t// if there are child nodes get the last index of it\r\n
\t\t\t\t\tif(childs.length) {\r\n
\t\t\t\t\t\ti = childs[childs.length-1][$t.p.localReader.id];\r\n
\t\t\t\t\t\trowind = i;\r\n
\t\t\t\t\t\ti = $($t).jqGrid(\'getInd\',rowind)+1;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\ti = $($t).jqGrid(\'getInd\', parentid)+1;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\t// if the node is leaf\r\n
\t\t\t\t\tif(parentdata[isLeaf]) {\r\n
\t\t\t\t\t\tleaf = true;\r\n
\t\t\t\t\t\tparentdata[expanded] = true;\r\n
\t\t\t\t\t\t//var prow = $($t).jqGrid(\'getInd\', parentid);\r\n
\t\t\t\t\t\t$($t.rows[prow])\r\n
\t\t\t\t\t\t\t.find("span.cell-wrapperleaf").removeClass("cell-wrapperleaf").addClass("cell-wrapper")\r\n
\t\t\t\t\t\t\t.end()\r\n
\t\t\t\t\t\t\t.find("div.tree-leaf").removeClass($t.p.treeIcons.leaf+" tree-leaf").addClass($t.p.treeIcons.minus+" tree-minus");\r\n
\t\t\t\t\t\t$t.p.data[parentindex][isLeaf] = false;\r\n
\t\t\t\t\t\tparentdata[loaded] = true;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tlen = i+1;\r\n
\r\n
\t\t\tdata[expanded] = false;\r\n
\t\t\tdata[loaded] = true;\r\n
\t\t\tdata[level] = parentlevel;\r\n
\t\t\tdata[isLeaf] = true;\r\n
\t\t\tif( $t.p.treeGridModel === "adjacency") {\r\n
\t\t\t\tdata[parent] = parentid;\r\n
\t\t\t}\r\n
\t\t\tif( $t.p.treeGridModel === "nested") {\r\n
\t\t\t\t// this method requiere more attention\r\n
\t\t\t\tvar query, res, key;\r\n
\t\t\t\t//maxright = parseInt(maxright,10);\r\n
\t\t\t\t// ToDo - update grid data\r\n
\t\t\t\tif(parentid !== null) {\r\n
\t\t\t\t\tmaxright = parseInt(parentdata[right],10);\r\n
\t\t\t\t\tquery = $.jgrid.from($t.p.data);\r\n
\t\t\t\t\tquery = query.greaterOrEquals(right,maxright,{stype:\'integer\'});\r\n
\t\t\t\t\tres = query.select();\r\n
\t\t\t\t\tif(res.length) {\r\n
\t\t\t\t\t\tfor( key in res) {\r\n
\t\t\t\t\t\t\tif(res.hasOwnProperty(key)) {\r\n
\t\t\t\t\t\t\t\tres[key][left] = res[key][left] > maxright ? parseInt(res[key][left],10) +2 : res[key][left];\r\n
\t\t\t\t\t\t\t\tres[key][right] = res[key][right] >= maxright ? parseInt(res[key][right],10) +2 : res[key][right];\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tdata[left] = maxright;\r\n
\t\t\t\t\tdata[right]= maxright+1;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tmaxright = parseInt( $($t).jqGrid(\'getCol\', right, false, \'max\'), 10);\r\n
\t\t\t\t\tres = $.jgrid.from($t.p.data)\r\n
\t\t\t\t\t\t.greater(left,maxright,{stype:\'integer\'})\r\n
\t\t\t\t\t\t.select();\r\n
\t\t\t\t\tif(res.length) {\r\n
\t\t\t\t\t\tfor( key in res) {\r\n
\t\t\t\t\t\t\tif(res.hasOwnProperty(key)) {\r\n
\t\t\t\t\t\t\t\tres[key][left] = parseInt(res[key][left],10) +2 ;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tres = $.jgrid.from($t.p.data)\r\n
\t\t\t\t\t\t.greater(right,maxright,{stype:\'integer\'})\r\n
\t\t\t\t\t\t.select();\r\n
\t\t\t\t\tif(res.length) {\r\n
\t\t\t\t\t\tfor( key in res) {\r\n
\t\t\t\t\t\t\tif(res.hasOwnProperty(key)) {\r\n
\t\t\t\t\t\t\t\tres[key][right] = parseInt(res[key][right],10) +2 ;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tdata[left] = maxright+1;\r\n
\t\t\t\t\tdata[right] = maxright + 2;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tif( parentid === null || $($t).jqGrid("isNodeLoaded",parentdata) || leaf ) {\r\n
\t\t\t\t\t$($t).jqGrid(\'addRowData\', nodeid, data, method, rowind);\r\n
\t\t\t\t\t$($t).jqGrid(\'setTreeNode\', i, len);\r\n
\t\t\t}\r\n
\t\t\tif(parentdata && !parentdata[expanded]) {\r\n
\t\t\t\t$($t.rows[prow])\r\n
\t\t\t\t\t.find("div.treeclick")\r\n
\t\t\t\t\t.click();\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\t//});\r\n
\t}\r\n
});\r\n
})(jQuery);\r\n
// Grouping module\r\n
;(function($){\r\n
"use strict";\r\n
$.extend($.jgrid,{\r\n
\ttemplate : function(format){ //jqgformat\r\n
\t\tvar args = $.makeArray(arguments).slice(1), j = 1;\r\n
\t\tif(format===undefined) { format = ""; }\r\n
\t\treturn format.replace(/\\{([\\w\\-]+)(?:\\:([\\w\\.]*)(?:\\((.*?)?\\))?)?\\}/g, function(m,i){\r\n
\t\t\tif(!isNaN(parseInt(i,10))) {\r\n
\t\t\t\tj++;\r\n
\t\t\t\treturn args[parseInt(i,10)];\r\n
\t\t\t} else {\r\n
\t\t\t\tvar nmarr = args[ j ],\r\n
\t\t\t\tk = nmarr.length;\r\n
\t\t\t\twhile(k--) {\r\n
\t\t\t\t\tif(i===nmarr[k].nm) {\r\n
\t\t\t\t\t\treturn nmarr[k].v;\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\tj++;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t}\r\n
});\r\n
$.jgrid.extend({\r\n
\tgroupingSetup : function () {\r\n
\t\treturn this.each(function (){\r\n
\t\t\tvar $t = this,\r\n
\t\t\tgrp = $t.p.groupingView;\r\n
\t\t\tif(grp !== null && ( (typeof grp === \'object\') || $.isFunction(grp) ) ) {\r\n
\t\t\t\tif(!grp.groupField.length) {\r\n
\t\t\t\t\t$t.p.grouping = false;\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tif ( typeof(grp.visibiltyOnNextGrouping) === \'undefined\') {\r\n
\t\t\t\t\t\tgrp.visibiltyOnNextGrouping = [];\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t\tgrp.lastvalues=[];\r\n
\t\t\t\t\tgrp.groups =[];\r\n
\t\t\t\t\tgrp.counters =[];\r\n
\t\t\t\t\tfor(var i=0;i<grp.groupField.length;i++) {\r\n
\t\t\t\t\t\tif(!grp.groupOrder[i]) {\r\n
\t\t\t\t\t\t\tgrp.groupOrder[i] = \'asc\';\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(!grp.groupText[i]) {\r\n
\t\t\t\t\t\t\tgrp.groupText[i] = \'{0}\';\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif( typeof(grp.groupColumnShow[i]) !== \'boolean\') {\r\n
\t\t\t\t\t\t\tgrp.groupColumnShow[i] = true;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif( typeof(grp.groupSummary[i]) !== \'boolean\') {\r\n
\t\t\t\t\t\t\tgrp.groupSummary[i] = false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(grp.groupColumnShow[i] === true) {\r\n
\t\t\t\t\t\t\tgrp.visibiltyOnNextGrouping[i] = true;\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'showCol\',grp.groupField[i]);\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tgrp.visibiltyOnNextGrouping[i] = $("#"+$.jgrid.jqID($t.p.id+"_"+grp.groupField[i])).is(":visible");\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'hideCol\',grp.groupField[i]);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tgrp.summary =[];\r\n
\t\t\t\t\tvar cm = $t.p.colModel;\r\n
\t\t\t\t\tfor(var j=0, cml = cm.length; j < cml; j++) {\r\n
\t\t\t\t\t\tif(cm[j].summaryType) {\r\n
\t\t\t\t\t\t\tgrp.summary.push({nm:cm[j].name,st:cm[j].summaryType, v: \'\', sr: cm[j].summaryRound, srt: cm[j].summaryRoundType || \'round\'});\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t} else {\r\n
\t\t\t\t$t.p.grouping = false;\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tgroupingPrepare : function (rData, gdata, record, irow) {\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar grp = this.p.groupingView, $t= this;\r\n
\t\t\tvar grlen = grp.groupField.length, \r\n
\t\t\tfieldName,\r\n
\t\t\tv,\r\n
\t\t\tchanged = 0;\r\n
\t\t\tfor(var i=0;i<grlen;i++) {\r\n
\t\t\t\tfieldName = grp.groupField[i];\r\n
\t\t\t\tv = record[fieldName];\r\n
\t\t\t\tif( v !== undefined ) {\r\n
\t\t\t\t\tif(irow === 0 ) {\r\n
\t\t\t\t\t\t// First record always starts a new group\r\n
\t\t\t\t\t\tgrp.groups.push({idx:i,dataIndex:fieldName,value:v, startRow: irow, cnt:1, summary : [] } );\r\n
\t\t\t\t\t\tgrp.lastvalues[i] = v;\r\n
\t\t\t\t\t\tgrp.counters[i] = {cnt:1, pos:grp.groups.length-1, summary: $.extend(true,[],grp.summary)};\r\n
\t\t\t\t\t\t$.each(grp.counters[i].summary,function() {\r\n
\t\t\t\t\t\t\tif ($.isFunction(this.st)) {\r\n
\t\t\t\t\t\t\t\tthis.v = this.st.call($t, this.v, this.nm, record);\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tthis.v = $($t).jqGrid(\'groupingCalculations.handler\',this.st, this.v, this.nm, this.sr, this.srt, record);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t\tgrp.groups[grp.counters[i].pos].summary = grp.counters[i].summary;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tif( (typeof(v) !== "object" && (grp.lastvalues[i] !== v) ) ) {\r\n
\t\t\t\t\t\t\t// This record is not in same group as previous one\r\n
\t\t\t\t\t\t\tgrp.groups.push({idx:i,dataIndex:fieldName,value:v, startRow: irow, cnt:1, summary : [] } );\r\n
\t\t\t\t\t\t\tgrp.lastvalues[i] = v;\r\n
\t\t\t\t\t\t\tchanged = 1;\r\n
\t\t\t\t\t\t\tgrp.counters[i] = {cnt:1, pos:grp.groups.length-1, summary: $.extend(true,[],grp.summary)};\r\n
\t\t\t\t\t\t\t$.each(grp.counters[i].summary,function() {\r\n
\t\t\t\t\t\t\t\tif ($.isFunction(this.st)) {\r\n
\t\t\t\t\t\t\t\t\tthis.v = this.st.call($t, this.v, this.nm, record);\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\tthis.v = $($t).jqGrid(\'groupingCalculations.handler\',this.st, this.v, this.nm, this.sr, this.srt, record);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\tgrp.groups[grp.counters[i].pos].summary = grp.counters[i].summary;\r\n
\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\tif (changed === 1) {\r\n
\t\t\t\t\t\t\t\t// This group has changed because an earlier group changed.\r\n
\t\t\t\t\t\t\t\tgrp.groups.push({idx:i,dataIndex:fieldName,value:v, startRow: irow, cnt:1, summary : [] } );\r\n
\t\t\t\t\t\t\t\tgrp.lastvalues[i] = v;\r\n
\t\t\t\t\t\t\t\tgrp.counters[i] = {cnt:1, pos:grp.groups.length-1, summary: $.extend(true,[],grp.summary)};\r\n
\t\t\t\t\t\t\t\t$.each(grp.counters[i].summary,function() {\r\n
\t\t\t\t\t\t\t\t\tif ($.isFunction(this.st)) {\r\n
\t\t\t\t\t\t\t\t\t\tthis.v = this.st.call($t, this.v, this.nm, record);\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\tthis.v = $($t).jqGrid(\'groupingCalculations.handler\',this.st, this.v, this.nm, this.sr, this.srt, record);\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\tgrp.groups[grp.counters[i].pos].summary = grp.counters[i].summary;\r\n
\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\tgrp.counters[i].cnt += 1;\r\n
\t\t\t\t\t\t\t\tgrp.groups[grp.counters[i].pos].cnt = grp.counters[i].cnt;\r\n
\t\t\t\t\t\t\t\t$.each(grp.counters[i].summary,function() {\r\n
\t\t\t\t\t\t\t\t\tif ($.isFunction(this.st)) {\r\n
\t\t\t\t\t\t\t\t\t\tthis.v = this.st.call($t, this.v, this.nm, record);\r\n
\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\tthis.v = $($t).jqGrid(\'groupingCalculations.handler\',this.st, this.v, this.nm, this.sr, this.srt, record);\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\tgrp.groups[grp.counters[i].pos].summary = grp.counters[i].summary;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tgdata.push( rData );\r\n
\t\t});\r\n
\t\treturn gdata;\r\n
\t},\r\n
\tgroupingToggle : function(hid){\r\n
\t\tthis.each(function(){\r\n
\t\t\tvar $t = this,\r\n
\t\t\tgrp = $t.p.groupingView,\r\n
\t\t\tstrpos = hid.split(\'_\'),\r\n
\t\t\t//uid = hid.substring(0,strpos+1),\r\n
\t\t\tnum = parseInt(strpos[strpos.length-2], 10);\r\n
\t\t\tstrpos.splice(strpos.length-2,2);\r\n
\t\t\tvar uid = strpos.join("_"),\r\n
\t\t\tminus = grp.minusicon,\r\n
\t\t\tplus = grp.plusicon,\r\n
\t\t\ttar = $("#"+$.jgrid.jqID(hid)),\r\n
\t\t\tr = tar.length ? tar[0].nextSibling : null,\r\n
\t\t\ttarspan = $("#"+$.jgrid.jqID(hid)+" span."+"tree-wrap-"+$t.p.direction),\r\n
\t\t\tcollapsed = false, tspan;\r\n
\t\t\tif( tarspan.hasClass(minus) ) {\r\n
\t\t\t\tif(grp.showSummaryOnHide) {\r\n
\t\t\t\t\tif(r){\r\n
\t\t\t\t\t\twhile(r) {\r\n
\t\t\t\t\t\t\tif($(r).hasClass(\'jqfoot\') ) {\r\n
\t\t\t\t\t\t\t\tvar lv = parseInt($(r).attr("jqfootlevel"),10);\r\n
\t\t\t\t\t\t\t\tif(  lv <= num) {\r\n
\t\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t$(r).hide();\r\n
\t\t\t\t\t\t\tr = r.nextSibling;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else  {\r\n
\t\t\t\t\tif(r){\r\n
\t\t\t\t\t\twhile(r) {\r\n
\t\t\t\t\t\t\tif( $(r).hasClass(uid+"_"+String(num) ) || $(r).hasClass(uid+"_"+String(num-1))) { break; }\r\n
\t\t\t\t\t\t\t$(r).hide();\r\n
\t\t\t\t\t\t\tr = r.nextSibling;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\ttarspan.removeClass(minus).addClass(plus);\r\n
\t\t\t\tcollapsed = true;\r\n
\t\t\t} else {\r\n
\t\t\t\tif(r){\r\n
\t\t\t\t\twhile(r) {\r\n
\t\t\t\t\t\tif($(r).hasClass(uid+"_"+String(num)) || $(r).hasClass(uid+"_"+String(num-1)) ) { break; }\r\n
\t\t\t\t\t\t$(r).show();\r\n
\t\t\t\t\t\ttspan = $(r).find("span."+"tree-wrap-"+$t.p.direction);\r\n
\t\t\t\t\t\tif( tspan && $(tspan).hasClass(plus) ) {\r\n
\t\t\t\t\t\t\t$(tspan).removeClass(plus).addClass(minus);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tr = r.nextSibling;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\ttarspan.removeClass(plus).addClass(minus);\r\n
\t\t\t}\r\n
\t\t\t$($t).triggerHandler("jqGridGroupingClickGroup", [hid , collapsed]);\r\n
\t\t\tif( $.isFunction($t.p.onClickGroup)) { $t.p.onClickGroup.call($t, hid , collapsed); }\r\n
\r\n
\t\t});\r\n
\t\treturn false;\r\n
\t},\r\n
\tgroupingRender : function (grdata, colspans ) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this,\r\n
\t\t\tgrp = $t.p.groupingView,\r\n
\t\t\tstr = "", icon = "", hid, clid, pmrtl = grp.groupCollapse ? grp.plusicon : grp.minusicon, gv, cp=[], ii, len =grp.groupField.length;\r\n
\t\t\tpmrtl += " tree-wrap-"+$t.p.direction; \r\n
\t\t\tii = 0;\r\n
\t\t\t$.each($t.p.colModel, function (i,n){\r\n
\t\t\t\tfor(var ii=0;ii<len;ii++) {\r\n
\t\t\t\t\tif(grp.groupField[ii] === n.name ) {\r\n
\t\t\t\t\t\tcp[ii] = i;\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\tvar toEnd = 0;\r\n
\t\t\tfunction findGroupIdx( ind , offset, grp) {\r\n
\t\t\t\tif(offset===0) {\r\n
\t\t\t\t\treturn grp[ind];\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tvar id = grp[ind].idx;\r\n
\t\t\t\t\tif(id===0) { return grp[ind]; }\r\n
\t\t\t\t\tfor(var i=ind;i >= 0; i--) {\r\n
\t\t\t\t\t\tif(grp[i].idx === id-offset) {\r\n
\t\t\t\t\t\t\treturn grp[i];\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\tvar sumreverse = $.makeArray(grp.groupSummary);\r\n
\t\t\tsumreverse.reverse();\r\n
\t\t\t$.each(grp.groups,function(i,n){\r\n
\t\t\t\ttoEnd++;\r\n
\t\t\t\tclid = $t.p.id+"ghead_"+n.idx;\r\n
\t\t\t\thid = clid+"_"+i;\r\n
\t\t\t\ticon = "<span style=\'cursor:pointer;\' class=\'ui-icon "+pmrtl+"\' onclick=\\"jQuery(\'#"+$.jgrid.jqID($t.p.id)+"\').jqGrid(\'groupingToggle\',\'"+hid+"\');return false;\\"></span>";\r\n
\t\t\t\ttry {\r\n
\t\t\t\t\tgv = $t.formatter(hid, n.value, cp[n.idx], n.value );\r\n
\t\t\t\t} catch (egv) {\r\n
\t\t\t\t\tgv = n.value;\r\n
\t\t\t\t}\r\n
\t\t\t\tstr += "<tr id=\\""+hid+"\\" role=\\"row\\" class= \\"ui-widget-content jqgroup ui-row-"+$t.p.direction+" "+clid+"\\"><td style=\\"padding-left:"+(n.idx * 12) + "px;"+"\\" colspan=\\""+colspans+"\\">"+icon+$.jgrid.template(grp.groupText[n.idx], gv, n.cnt, n.summary)+"</td></tr>";\r\n
\t\t\t\tvar leaf = len-1 === n.idx; \r\n
\t\t\t\tif( leaf ) {\r\n
\t\t\t\t\tvar gg = grp.groups[i+1];\r\n
\t\t\t\t\tvar end = gg !== undefined ?  grp.groups[i+1].startRow : grdata.length;\r\n
\t\t\t\t\tfor(var kk=n.startRow;kk<end;kk++) {\r\n
\t\t\t\t\t\tstr += grdata[kk].join(\'\');\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tvar jj;\r\n
\t\t\t\t\tif (gg !== undefined) {\r\n
\t\t\t\t\t\tfor (jj = 0; jj < grp.groupField.length; jj++) {\r\n
\t\t\t\t\t\t\tif (gg.dataIndex === grp.groupField[jj]) {\r\n
\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\ttoEnd = grp.groupField.length - jj;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tfor (var ik = 0; ik < toEnd; ik++) {\r\n
\t\t\t\t\t\tif(!sumreverse[ik]) { continue; }\r\n
\t\t\t\t\t\tvar hhdr = "";\r\n
\t\t\t\t\t\tif(grp.groupCollapse && !grp.showSummaryOnHide) {\r\n
\t\t\t\t\t\t\thhdr = " style=\\"display:none;\\"";\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tstr += "<tr"+hhdr+" jqfootlevel=\\""+(n.idx-ik)+"\\" role=\\"row\\" class=\\"ui-widget-content jqfoot ui-row-"+$t.p.direction+"\\">";\r\n
\t\t\t\t\t\tvar fdata = findGroupIdx(i, ik, grp.groups),\r\n
\t\t\t\t\t\tcm = $t.p.colModel,\r\n
\t\t\t\t\t\tvv, grlen = fdata.cnt;\r\n
\t\t\t\t\t\tfor(var k=0; k<colspans;k++) {\r\n
\t\t\t\t\t\t\tvar tmpdata = "<td "+$t.formatCol(k,1,\'\')+">&#160;</td>",\r\n
\t\t\t\t\t\t\ttplfld = "{0}";\r\n
\t\t\t\t\t\t\t$.each(fdata.summary,function(){\r\n
\t\t\t\t\t\t\t\tif(this.nm === cm[k].name) {\r\n
\t\t\t\t\t\t\t\t\tif(cm[k].summaryTpl)  {\r\n
\t\t\t\t\t\t\t\t\t\ttplfld = cm[k].summaryTpl;\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\tif(typeof(this.st) === \'string\' && this.st.toLowerCase() === \'avg\') {\r\n
\t\t\t\t\t\t\t\t\t\tif(this.v && grlen > 0) {\r\n
\t\t\t\t\t\t\t\t\t\t\tthis.v = (this.v/grlen);\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t\t\tvv = $t.formatter(\'\', this.v, k, this);\r\n
\t\t\t\t\t\t\t\t\t} catch (ef) {\r\n
\t\t\t\t\t\t\t\t\t\tvv = this.v;\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\ttmpdata= "<td "+$t.formatCol(k,1,\'\')+">"+$.jgrid.format(tplfld,vv)+ "</td>";\r\n
\t\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\tstr += tmpdata;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tstr += "</tr>";\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\ttoEnd = jj;\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\t$("#"+$.jgrid.jqID($t.p.id)+" tbody:first").append(str);\r\n
\t\t\t// free up memory\r\n
\t\t\tstr = null;\r\n
\t\t});\r\n
\t},\r\n
\tgroupingGroupBy : function (name, options ) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(typeof(name) === "string") {\r\n
\t\t\t\tname = [name];\r\n
\t\t\t}\r\n
\t\t\tvar grp = $t.p.groupingView;\r\n
\t\t\t$t.p.grouping = true;\r\n
\r\n
\t\t\t//Set default, in case visibilityOnNextGrouping is undefined \r\n
\t\t\tif (typeof grp.visibiltyOnNextGrouping === "undefined") {\r\n
\t\t\t\tgrp.visibiltyOnNextGrouping = [];\r\n
\t\t\t}\r\n
\t\t\tvar i;\r\n
\t\t\t// show previous hidden groups if they are hidden and weren\'t removed yet\r\n
\t\t\tfor(i=0;i<grp.groupField.length;i++) {\r\n
\t\t\t\tif(!grp.groupColumnShow[i] && grp.visibiltyOnNextGrouping[i]) {\r\n
\t\t\t\t$($t).jqGrid(\'showCol\',grp.groupField[i]);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t\t// set visibility status of current group columns on next grouping\r\n
\t\t\tfor(i=0;i<name.length;i++) {\r\n
\t\t\t\tgrp.visibiltyOnNextGrouping[i] = $("#"+$.jgrid.jqID($t.p.id)+"_"+$.jgrid.jqID(name[i])).is(":visible");\r\n
\t\t\t}\r\n
\t\t\t$t.p.groupingView = $.extend($t.p.groupingView, options || {});\r\n
\t\t\tgrp.groupField = name;\r\n
\t\t\t$($t).trigger("reloadGrid");\r\n
\t\t});\r\n
\t},\r\n
\tgroupingRemove : function (current) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(typeof(current) === \'undefined\') {\r\n
\t\t\t\tcurrent = true;\r\n
\t\t\t}\r\n
\t\t\t$t.p.grouping = false;\r\n
\t\t\tif(current===true) {\r\n
\t\t\t\tvar grp = $t.p.groupingView;\r\n
\t\t\t\t// show previous hidden groups if they are hidden and weren\'t removed yet\r\n
\t\t\t\tfor(var i=0;i<grp.groupField.length;i++) {\r\n
\t\t\t\tif (!grp.groupColumnShow[i] && grp.visibiltyOnNextGrouping[i]) {\r\n
\t\t\t\t\t\t$($t).jqGrid(\'showCol\', grp.groupField);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t\t$("tr.jqgroup, tr.jqfoot","#"+$.jgrid.jqID($t.p.id)+" tbody:first").remove();\r\n
\t\t\t\t$("tr.jqgrow:hidden","#"+$.jgrid.jqID($t.p.id)+" tbody:first").show();\r\n
\t\t\t} else {\r\n
\t\t\t\t$($t).trigger("reloadGrid");\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tgroupingCalculations : {\r\n
\t\thandler: function(fn, v, field, round, roundType, rc) {\r\n
\t\t\tvar funcs = {\r\n
\t\t\t\tsum: function() {\r\n
\t\t\t\t\treturn parseFloat(v||0) + parseFloat((rc[field]||0));\r\n
\t\t\t\t},\r\n
\r\n
\t\t\t\tmin: function() {\r\n
\t\t\t\t\tif(v==="") {\r\n
\t\t\t\t\t\treturn parseFloat(rc[field]||0);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn Math.min(parseFloat(v),parseFloat(rc[field]||0));\r\n
\t\t\t\t},\r\n
\r\n
\t\t\t\tmax: function() {\r\n
\t\t\t\t\tif(v==="") {\r\n
\t\t\t\t\t\treturn parseFloat(rc[field]||0);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\treturn Math.max(parseFloat(v),parseFloat(rc[field]||0));\r\n
\t\t\t\t},\r\n
\r\n
\t\t\t\tcount: function() {\r\n
\t\t\t\t\tif(v==="") {v=0;}\r\n
\t\t\t\t\tif(rc.hasOwnProperty(field)) {\r\n
\t\t\t\t\t\treturn v+1;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\treturn 0;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t},\r\n
\r\n
\t\t\t\tavg: function() {\r\n
\t\t\t\t\t// the same as sum, but at end we divide it\r\n
\t\t\t\t\t// so use sum instead of duplicating the code (?)\r\n
\t\t\t\t\treturn funcs.sum();\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\tif(!funcs[fn]) {\r\n
\t\t\t\tthrow ("jqGrid Grouping No such method: " + fn);\r\n
\t\t\t}\r\n
\t\t\tvar res = funcs[fn]();\r\n
\r\n
\t\t\tif (round != null) {\r\n
\t\t\t\tif (roundType == \'fixed\')\r\n
\t\t\t\t\tres = res.toFixed(round);\r\n
\t\t\t\telse {\r\n
\t\t\t\t\tvar mul = Math.pow(10, round);\r\n
\r\n
\t\t\t\t\tres = Math.round(res * mul) / mul;\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\r\n
\t\t\treturn res;\r\n
\t\t}\t\r\n
\t}\r\n
});\r\n
})(jQuery);\r\n
;(function($){\r\n
/*\r\n
 * jqGrid extension for constructing Grid Data from external file\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/ \r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
**/ \r\n
//jsHint options\r\n
/*global jQuery, $, alert, xmlJsonClass */\r\n
\r\n
"use strict";\r\n
    $.jgrid.extend({\r\n
        jqGridImport : function(o) {\r\n
            o = $.extend({\r\n
                imptype : "xml", // xml, json, xmlstring, jsonstring\r\n
                impstring: "",\r\n
                impurl: "",\r\n
                mtype: "GET",\r\n
                impData : {},\r\n
                xmlGrid :{\r\n
                    config : "roots>grid",\r\n
                    data: "roots>rows"\r\n
                },\r\n
                jsonGrid :{\r\n
                    config : "grid",\r\n
                    data: "data"\r\n
                },\r\n
                ajaxOptions :{}\r\n
            }, o || {});\r\n
            return this.each(function(){\r\n
                var $t = this;\r\n
                var xmlConvert = function (xml,o) {\r\n
                    var cnfg = $(o.xmlGrid.config,xml)[0];\r\n
                    var xmldata = $(o.xmlGrid.data,xml)[0], jstr, jstr1;\r\n
                    if(xmlJsonClass.xml2json && $.jgrid.parse) {\r\n
                        jstr = xmlJsonClass.xml2json(cnfg," ");\r\n
                        jstr = $.jgrid.parse(jstr);\r\n
                        for(var key in jstr) {\r\n
                            if(jstr.hasOwnProperty(key)) {\r\n
                                jstr1=jstr[key];\r\n
                            }\r\n
                        }\r\n
                        if(xmldata) {\r\n
                        // save the datatype\r\n
                            var svdatatype = jstr.grid.datatype;\r\n
                            jstr.grid.datatype = \'xmlstring\';\r\n
                            jstr.grid.datastr = xml;\r\n
                            $($t).jqGrid( jstr1 ).jqGrid("setGridParam",{datatype:svdatatype});\r\n
                        } else {\r\n
                            $($t).jqGrid( jstr1 );\r\n
                        }\r\n
                        jstr = null;jstr1=null;\r\n
                    } else {\r\n
                        alert("xml2json or parse are not present");\r\n
                    }\r\n
                };\r\n
                var jsonConvert = function (jsonstr,o){\r\n
                    if (jsonstr && typeof jsonstr == \'string\') {\r\n
\t\t\t\t\t\tvar _jsonparse = false;\r\n
\t\t\t\t\t\tif($.jgrid.useJSON) {\r\n
\t\t\t\t\t\t\t$.jgrid.useJSON = false;\r\n
\t\t\t\t\t\t\t_jsonparse = true;\r\n
\t\t\t\t\t\t}\r\n
                        var json = $.jgrid.parse(jsonstr);\r\n
\t\t\t\t\t\tif(_jsonparse) { $.jgrid.useJSON = true; }\r\n
                        var gprm = json[o.jsonGrid.config];\r\n
                        var jdata = json[o.jsonGrid.data];\r\n
                        if(jdata) {\r\n
                            var svdatatype = gprm.datatype;\r\n
                            gprm.datatype = \'jsonstring\';\r\n
                            gprm.datastr = jdata;\r\n
                            $($t).jqGrid( gprm ).jqGrid("setGridParam",{datatype:svdatatype});\r\n
                        } else {\r\n
                            $($t).jqGrid( gprm );\r\n
                        }\r\n
                    }\r\n
                };\r\n
                switch (o.imptype){\r\n
                    case \'xml\':\r\n
                        $.ajax($.extend({\r\n
                            url:o.impurl,\r\n
                            type:o.mtype,\r\n
                            data: o.impData,\r\n
                            dataType:"xml",\r\n
                            complete: function(xml,stat) {\r\n
                                if(stat == \'success\') {\r\n
                                    xmlConvert(xml.responseXML,o);\r\n
                                    $($t).triggerHandler("jqGridImportComplete", [xml, o]);\r\n
                                    if($.isFunction(o.importComplete)) {\r\n
                                        o.importComplete(xml);\r\n
                                    }\r\n
                                }\r\n
                                xml=null;\r\n
                            }\r\n
                        }, o.ajaxOptions));\r\n
                        break;\r\n
                    case \'xmlstring\' :\r\n
                        // we need to make just the conversion and use the same code as xml\r\n
                        if(o.impstring && typeof o.impstring == \'string\') {\r\n
                            var xmld = $.jgrid.stringToDoc(o.impstring);\r\n
                            if(xmld) {\r\n
                                xmlConvert(xmld,o);\r\n
                                $($t).triggerHandler("jqGridImportComplete", [xmld, o]);\r\n
                                if($.isFunction(o.importComplete)) {\r\n
                                    o.importComplete(xmld);\r\n
                                }\r\n
                                o.impstring = null;\r\n
                            }\r\n
                            xmld = null;\r\n
                        }\r\n
                        break;\r\n
                    case \'json\':\r\n
                        $.ajax($.extend({\r\n
                            url:o.impurl,\r\n
                            type:o.mtype,\r\n
                            data: o.impData,\r\n
                            dataType:"json",\r\n
                            complete: function(json) {\r\n
                                try {\r\n
                                    jsonConvert(json.responseText,o );\r\n
                                    $($t).triggerHandler("jqGridImportComplete", [json, o]);\r\n
                                    if($.isFunction(o.importComplete)) {\r\n
                                        o.importComplete(json);\r\n
                                    }\r\n
                                } catch (ee){}\r\n
                                json=null;\r\n
                            }\r\n
                        }, o.ajaxOptions ));\r\n
                        break;\r\n
                    case \'jsonstring\' :\r\n
                        if(o.impstring && typeof o.impstring == \'string\') {\r\n
                            jsonConvert(o.impstring,o );\r\n
                            $($t).triggerHandler("jqGridImportComplete", [o.impstring, o]);\r\n
                            if($.isFunction(o.importComplete)) {\r\n
                                o.importComplete(o.impstring);\r\n
                            }\r\n
                            o.impstring = null;\r\n
                        }\r\n
                        break;\r\n
                }\r\n
            });\r\n
        },\r\n
        jqGridExport : function(o) {\r\n
            o = $.extend({\r\n
                exptype : "xmlstring",\r\n
                root: "grid",\r\n
                ident: "\\t"\r\n
            }, o || {});\r\n
            var ret = null;\r\n
            this.each(function () {\r\n
                if(!this.grid) { return;}\r\n
                var gprm = $.extend(true, {},$(this).jqGrid("getGridParam"));\r\n
                // we need to check for:\r\n
                // 1.multiselect, 2.subgrid  3. treegrid and remove the unneded columns from colNames\r\n
                if(gprm.rownumbers) {\r\n
                    gprm.colNames.splice(0,1);\r\n
                    gprm.colModel.splice(0,1);\r\n
                }\r\n
                if(gprm.multiselect) {\r\n
                    gprm.colNames.splice(0,1);\r\n
                    gprm.colModel.splice(0,1);\r\n
                }\r\n
                if(gprm.subGrid) {\r\n
                    gprm.colNames.splice(0,1);\r\n
                    gprm.colModel.splice(0,1);\r\n
                }\r\n
                gprm.knv = null;\r\n
                if(gprm.treeGrid) {\r\n
                    for (var key in gprm.treeReader) {\r\n
                        if(gprm.treeReader.hasOwnProperty(key)) {\r\n
                            gprm.colNames.splice(gprm.colNames.length-1);\r\n
                            gprm.colModel.splice(gprm.colModel.length-1);\r\n
                        }\r\n
                    }\r\n
                }\r\n
                switch (o.exptype) {\r\n
                    case \'xmlstring\' :\r\n
                        ret = "<"+o.root+">"+xmlJsonClass.json2xml(gprm,o.ident)+"</"+o.root+">";\r\n
                        break;\r\n
                    case \'jsonstring\' :\r\n
                        ret = "{"+ xmlJsonClass.toJson(gprm,o.root,o.ident,false)+"}";\r\n
                        if(gprm.postData.filters !== undefined) {\r\n
                            ret=ret.replace(/filters":"/,\'filters":\');\r\n
                            ret=ret.replace(/}]}"/,\'}]}\');\r\n
                        }\r\n
                        break;\r\n
                }\r\n
            });\r\n
            return ret;\r\n
        },\r\n
        excelExport : function(o) {\r\n
            o = $.extend({\r\n
                exptype : "remote",\r\n
                url : null,\r\n
                oper: "oper",\r\n
                tag: "excel",\r\n
                exportOptions : {}\r\n
            }, o || {});\r\n
            return this.each(function(){\r\n
                if(!this.grid) { return;}\r\n
                var url;\r\n
                if(o.exptype == "remote") {\r\n
                    var pdata = $.extend({},this.p.postData);\r\n
                    pdata[o.oper] = o.tag;\r\n
                    var params = jQuery.param(pdata);\r\n
                    if(o.url.indexOf("?") != -1) { url = o.url+"&"+params; }\r\n
                    else { url = o.url+"?"+params; }\r\n
                    window.location = url;\r\n
                }\r\n
            });\r\n
        }\r\n
    });\r\n
})(jQuery);;(function($){\r\n
/*\r\n
**\r\n
 * jqGrid addons using jQuery UI \r\n
 * Author: Mark Williams\r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl-2.0.html\r\n
 * depends on jQuery UI \r\n
**/\r\n
if ($.browser.msie && $.browser.version==8) {\r\n
\t$.expr[":"].hidden = function(elem) {\r\n
\t\treturn elem.offsetWidth === 0 || elem.offsetHeight === 0 ||\r\n
\t\t\telem.style.display == "none";\r\n
\t};\r\n
}\r\n
// requiere load multiselect before grid\r\n
$.jgrid._multiselect = false;\r\n
if($.ui) {\r\n
\tif ($.ui.multiselect ) {\r\n
\t\tif($.ui.multiselect.prototype._setSelected) {\r\n
\t\t\tvar setSelected = $.ui.multiselect.prototype._setSelected;\r\n
\t\t    $.ui.multiselect.prototype._setSelected = function(item,selected) {\r\n
\t\t        var ret = setSelected.call(this,item,selected);\r\n
\t\t        if (selected && this.selectedList) {\r\n
\t\t            var elt = this.element;\r\n
\t\t\t\t    this.selectedList.find(\'li\').each(function() {\r\n
\t\t\t\t\t    if ($(this).data(\'optionLink\')) {\r\n
\t\t\t\t\t\t    $(this).data(\'optionLink\').remove().appendTo(elt);\r\n
\t\t\t\t\t    }\r\n
\t\t\t\t    });\r\n
\t\t        }\r\n
\t\t        return ret;\r\n
\t\t\t};\r\n
\t\t}\r\n
\t\tif($.ui.multiselect.prototype.destroy) {\r\n
\t\t\t$.ui.multiselect.prototype.destroy = function() {\r\n
\t\t\t\tthis.element.show();\r\n
\t\t\t\tthis.container.remove();\r\n
\t\t\t\tif ($.Widget === undefined) {\r\n
\t\t\t\t\t$.widget.prototype.destroy.apply(this, arguments);\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$.Widget.prototype.destroy.apply(this, arguments);\r\n
\t            }\r\n
\t\t\t};\r\n
\t\t}\r\n
\t\t$.jgrid._multiselect = true;\r\n
\t}\r\n
}\r\n
        \r\n
$.jgrid.extend({\r\n
\tsortableColumns : function (tblrow)\r\n
\t{\r\n
\t\treturn this.each(function (){\r\n
\t\t\tvar ts = this, tid= $.jgrid.jqID( ts.p.id );\r\n
\t\t\tfunction start() {ts.p.disableClick = true;}\r\n
\t\t\tvar sortable_opts = {\r\n
\t\t\t\t"tolerance" : "pointer",\r\n
\t\t\t\t"axis" : "x",\r\n
\t\t\t\t"scrollSensitivity": "1",\r\n
\t\t\t\t"items": \'>th:not(:has(#jqgh_\'+tid+\'_cb\'+\',#jqgh_\'+tid+\'_rn\'+\',#jqgh_\'+tid+\'_subgrid),:hidden)\',\r\n
\t\t\t\t"placeholder": {\r\n
\t\t\t\t\telement: function(item) {\r\n
\t\t\t\t\t\tvar el = $(document.createElement(item[0].nodeName))\r\n
\t\t\t\t\t\t.addClass(item[0].className+" ui-sortable-placeholder ui-state-highlight")\r\n
\t\t\t\t\t\t.removeClass("ui-sortable-helper")[0];\r\n
\t\t\t\t\t\treturn el;\r\n
\t\t\t\t\t},\r\n
\t\t\t\t\tupdate: function(self, p) {\r\n
\t\t\t\t\t\tp.height(self.currentItem.innerHeight() - parseInt(self.currentItem.css(\'paddingTop\')||0, 10) - parseInt(self.currentItem.css(\'paddingBottom\')||0, 10));\r\n
\t\t\t\t\t\tp.width(self.currentItem.innerWidth() - parseInt(self.currentItem.css(\'paddingLeft\')||0, 10) - parseInt(self.currentItem.css(\'paddingRight\')||0, 10));\r\n
\t\t\t\t\t}\r\n
\t\t\t\t},\r\n
\t\t\t\t"update": function(event, ui) {\r\n
\t\t\t\t\tvar p = $(ui.item).parent(),\r\n
\t\t\t\t\tth = $(">th", p),\r\n
\t\t\t\t\tcolModel = ts.p.colModel,\r\n
\t\t\t\t\tcmMap = {}, tid= ts.p.id+"_";\r\n
\t\t\t\t\t$.each(colModel, function(i) { cmMap[this.name]=i; });\r\n
\t\t\t\t\tvar permutation = [];\r\n
\t\t\t\t\tth.each(function() {\r\n
\t\t\t\t\t\tvar id = $(">div", this).get(0).id.replace(/^jqgh_/, "").replace(tid,"");\r\n
\t\t\t\t\t\t\tif (id in cmMap) {\r\n
\t\t\t\t\t\t\t\tpermutation.push(cmMap[id]);\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\r\n
\t\t\t\t\t$(ts).jqGrid("remapColumns",permutation, true, true);\r\n
\t\t\t\t\tif ($.isFunction(ts.p.sortable.update)) {\r\n
\t\t\t\t\t\tts.p.sortable.update(permutation);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tsetTimeout(function(){ts.p.disableClick=false;}, 50);\r\n
\t\t\t\t}\r\n
\t\t\t};\r\n
\t\t\tif (ts.p.sortable.options) {\r\n
\t\t\t\t$.extend(sortable_opts, ts.p.sortable.options);\r\n
\t\t\t} else if ($.isFunction(ts.p.sortable)) {\r\n
\t\t\t\tts.p.sortable = { "update" : ts.p.sortable };\r\n
\t\t\t}\r\n
\t\t\tif (sortable_opts.start) {\r\n
\t\t\t\tvar s = sortable_opts.start;\r\n
\t\t\t\tsortable_opts.start = function(e,ui) {\r\n
\t\t\t\t\tstart();\r\n
\t\t\t\t\ts.call(this,e,ui);\r\n
\t\t\t\t};\r\n
\t\t\t} else {\r\n
\t\t\t\tsortable_opts.start = start;\r\n
\t\t\t}\r\n
\t\t\tif (ts.p.sortable.exclude) {\r\n
\t\t\t\tsortable_opts.items += ":not("+ts.p.sortable.exclude+")";\r\n
\t\t\t}\r\n
\t\t\ttblrow.sortable(sortable_opts).data("sortable").floating = true;\r\n
\t\t});\r\n
\t},\r\n
    columnChooser : function(opts) {\r\n
        var self = this;\r\n
\t\tif($("#colchooser_"+$.jgrid.jqID(self[0].p.id)).length ) { return; }\r\n
        var selector = $(\'<div id="colchooser_\'+self[0].p.id+\'" style="position:relative;overflow:hidden"><div><select multiple="multiple"></select></div></div>\');\r\n
        var select = $(\'select\', selector);\r\n
\t\t\r\n
\t\tfunction insert(perm,i,v) {\r\n
\t\t\tif(i>=0){\r\n
\t\t\t\tvar a = perm.slice();\r\n
\t\t\t\tvar b = a.splice(i,Math.max(perm.length-i,i));\r\n
\t\t\t\tif(i>perm.length) { i = perm.length; }\r\n
\t\t\t\ta[i] = v;\r\n
\t\t\t\treturn a.concat(b);\r\n
\t\t\t}\r\n
\t\t}\r\n
        opts = $.extend({\r\n
            "width" : 420,\r\n
            "height" : 240,\r\n
            "classname" : null,\r\n
            "done" : function(perm) { if (perm) { self.jqGrid("remapColumns", perm, true); } },\r\n
            /* msel is either the name of a ui widget class that\r\n
               extends a multiselect, or a function that supports\r\n
               creating a multiselect object (with no argument,\r\n
               or when passed an object), and destroying it (when\r\n
               passed the string "destroy"). */\r\n
            "msel" : "multiselect",\r\n
            /* "msel_opts" : {}, */\r\n
\r\n
            /* dlog is either the name of a ui widget class that \r\n
               behaves in a dialog-like way, or a function, that\r\n
               supports creating a dialog (when passed dlog_opts)\r\n
               or destroying a dialog (when passed the string\r\n
               "destroy")\r\n
               */\r\n
            "dlog" : "dialog",\r\n
\t\t\t"dialog_opts" : {\r\n
\t\t\t\t"minWidth": 470\r\n
\t\t\t},\r\n
            /* dlog_opts is either an option object to be passed \r\n
               to "dlog", or (more likely) a function that creates\r\n
               the options object.\r\n
               The default produces a suitable options object for\r\n
               ui.dialog */\r\n
            "dlog_opts" : function(opts) {\r\n
                var buttons = {};\r\n
                buttons[opts.bSubmit] = function() {\r\n
                    opts.apply_perm();\r\n
                    opts.cleanup(false);\r\n
                };\r\n
                buttons[opts.bCancel] = function() {\r\n
                    opts.cleanup(true);\r\n
                };\r\n
                return $.extend(true, {\r\n
                    "buttons": buttons,\r\n
                    "close": function() {\r\n
                        opts.cleanup(true);\r\n
                    },\r\n
\t\t\t\t\t"modal" : opts.modal ? opts.modal : false,\r\n
\t\t\t\t\t"resizable": opts.resizable ? opts.resizable : true,\r\n
                    "width": opts.width+20\r\n
                }, opts.dialog_opts || {});\r\n
            },\r\n
            /* Function to get the permutation array, and pass it to the\r\n
               "done" function */\r\n
            "apply_perm" : function() {\r\n
                $(\'option\',select).each(function() {\r\n
                    if (this.selected) {\r\n
                        self.jqGrid("showCol", colModel[this.value].name);\r\n
                    } else {\r\n
                        self.jqGrid("hideCol", colModel[this.value].name);\r\n
                    }\r\n
                });\r\n
                \r\n
                var perm = [];\r\n
\t\t\t\t//fixedCols.slice(0);\r\n
                $(\'option:selected\',select).each(function() { perm.push(parseInt(this.value,10)); });\r\n
                $.each(perm, function() { delete colMap[colModel[parseInt(this,10)].name]; });\r\n
                $.each(colMap, function() {\r\n
\t\t\t\t\tvar ti = parseInt(this,10);\r\n
\t\t\t\t\tperm = insert(perm,ti,ti);\r\n
\t\t\t\t});\r\n
                if (opts.done) {\r\n
                    opts.done.call(self, perm);\r\n
                }\r\n
            },\r\n
            /* Function to cleanup the dialog, and select. Also calls the\r\n
               done function with no permutation (to indicate that the\r\n
               columnChooser was aborted */\r\n
            "cleanup" : function(calldone) {\r\n
                call(opts.dlog, selector, \'destroy\');\r\n
                call(opts.msel, select, \'destroy\');\r\n
                selector.remove();\r\n
                if (calldone && opts.done) {\r\n
                    opts.done.call(self);\r\n
                }\r\n
            },\r\n
\t\t\t"msel_opts" : {}\r\n
        }, $.jgrid.col, opts || {});\r\n
\t\tif($.ui) {\r\n
\t\t\tif ($.ui.multiselect ) {\r\n
\t\t\t\tif(opts.msel == "multiselect") {\r\n
\t\t\t\t\tif(!$.jgrid._multiselect) {\r\n
\t\t\t\t\t\t// should be in language file\r\n
\t\t\t\t\t\talert("Multiselect plugin loaded after jqGrid. Please load the plugin before the jqGrid!");\r\n
\t\t\t\t\t\treturn;\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\topts.msel_opts = $.extend($.ui.multiselect.defaults,opts.msel_opts);\r\n
\t\t\t\t}\r\n
\t\t\t}\r\n
\t\t}\r\n
        if (opts.caption) {\r\n
            selector.attr("title", opts.caption);\r\n
        }\r\n
        if (opts.classname) {\r\n
            selector.addClass(opts.classname);\r\n
            select.addClass(opts.classname);\r\n
        }\r\n
        if (opts.width) {\r\n
            $(">div",selector).css({"width": opts.width,"margin":"0 auto"});\r\n
            select.css("width", opts.width);\r\n
        }\r\n
        if (opts.height) {\r\n
            $(">div",selector).css("height", opts.height);\r\n
            select.css("height", opts.height - 10);\r\n
        }\r\n
        var colModel = self.jqGrid("getGridParam", "colModel");\r\n
        var colNames = self.jqGrid("getGridParam", "colNames");\r\n
        var colMap = {}, fixedCols = [];\r\n
\r\n
        select.empty();\r\n
        $.each(colModel, function(i) {\r\n
            colMap[this.name] = i;\r\n
            if (this.hidedlg) {\r\n
                if (!this.hidden) {\r\n
                    fixedCols.push(i);\r\n
                }\r\n
                return;\r\n
            }\r\n
\r\n
            select.append("<option value=\'"+i+"\' "+\r\n
                          (this.hidden?"":"selected=\'selected\'")+">"+jQuery.jgrid.stripHtml(colNames[i])+"</option>");\r\n
        });\r\n
        function call(fn, obj) {\r\n
            if (!fn) { return; }\r\n
            if (typeof fn == \'string\') {\r\n
                if ($.fn[fn]) {\r\n
                    $.fn[fn].apply(obj, $.makeArray(arguments).slice(2));\r\n
                }\r\n
            } else if ($.isFunction(fn)) {\r\n
                fn.apply(obj, $.makeArray(arguments).slice(2));\r\n
            }\r\n
        }\r\n
\r\n
        var dopts = $.isFunction(opts.dlog_opts) ? opts.dlog_opts.call(self, opts) : opts.dlog_opts;\r\n
        call(opts.dlog, selector, dopts);\r\n
        var mopts = $.isFunction(opts.msel_opts) ? opts.msel_opts.call(self, opts) : opts.msel_opts;\r\n
        call(opts.msel, select, mopts);\r\n
    },\r\n
\tsortableRows : function (opts) {\r\n
\t\t// Can accept all sortable options and events\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this;\r\n
\t\t\tif(!$t.grid) { return; }\r\n
\t\t\t// Currently we disable a treeGrid sortable\r\n
\t\t\tif($t.p.treeGrid) { return; }\r\n
\t\t\tif($.fn.sortable) {\r\n
\t\t\t\topts = $.extend({\r\n
\t\t\t\t\t"cursor":"move",\r\n
\t\t\t\t\t"axis" : "y",\r\n
\t\t\t\t\t"items": ".jqgrow"\r\n
\t\t\t\t\t},\r\n
\t\t\t\topts || {});\r\n
\t\t\t\tif(opts.start && $.isFunction(opts.start)) {\r\n
\t\t\t\t\topts._start_ = opts.start;\r\n
\t\t\t\t\tdelete opts.start;\r\n
\t\t\t\t} else {opts._start_=false;}\r\n
\t\t\t\tif(opts.update && $.isFunction(opts.update)) {\r\n
\t\t\t\t\topts._update_ = opts.update;\r\n
\t\t\t\t\tdelete opts.update;\r\n
\t\t\t\t} else {opts._update_ = false;}\r\n
\t\t\t\topts.start = function(ev,ui) {\r\n
\t\t\t\t\t$(ui.item).css("border-width","0px");\r\n
\t\t\t\t\t$("td",ui.item).each(function(i){\r\n
\t\t\t\t\t\tthis.style.width = $t.grid.cols[i].style.width;\r\n
\t\t\t\t\t});\r\n
\t\t\t\t\tif($t.p.subGrid) {\r\n
\t\t\t\t\t\tvar subgid = $(ui.item).attr("id");\r\n
\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'collapseSubGridRow\',subgid);\r\n
\t\t\t\t\t\t} catch (e) {}\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(opts._start_) {\r\n
\t\t\t\t\t\topts._start_.apply(this,[ev,ui]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t};\r\n
\t\t\t\topts.update = function (ev,ui) {\r\n
\t\t\t\t\t$(ui.item).css("border-width","");\r\n
\t\t\t\t\tif($t.p.rownumbers === true) {\r\n
\t\t\t\t\t\t$("td.jqgrid-rownum",$t.rows).each(function( i ){\r\n
\t\t\t\t\t\t\t$(this).html( i+1+(parseInt($t.p.page,10)-1)*parseInt($t.p.rowNum,10) );\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif(opts._update_) {\r\n
\t\t\t\t\t\topts._update_.apply(this,[ev,ui]);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t};\r\n
\t\t\t\t$("tbody:first",$t).sortable(opts);\r\n
\t\t\t\t$("tbody:first",$t).disableSelection();\r\n
\t\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tgridDnD : function(opts) {\r\n
\t\treturn this.each(function(){\r\n
\t\tvar $t = this;\r\n
\t\tif(!$t.grid) { return; }\r\n
\t\t// Currently we disable a treeGrid drag and drop\r\n
\t\tif($t.p.treeGrid) { return; }\r\n
\t\tif(!$.fn.draggable || !$.fn.droppable) { return; }\r\n
\t\tfunction updateDnD ()\r\n
\t\t{\r\n
\t\t\tvar datadnd = $.data($t,"dnd");\r\n
\t\t    $("tr.jqgrow:not(.ui-draggable)",$t).draggable($.isFunction(datadnd.drag) ? datadnd.drag.call($($t),datadnd) : datadnd.drag);\r\n
\t\t}\r\n
\t\tvar appender = "<table id=\'jqgrid_dnd\' class=\'ui-jqgrid-dnd\'></table>";\r\n
\t\tif($("#jqgrid_dnd")[0] === undefined) {\r\n
\t\t\t$(\'body\').append(appender);\r\n
\t\t}\r\n
\r\n
\t\tif(typeof opts == \'string\' && opts == \'updateDnD\' && $t.p.jqgdnd===true) {\r\n
\t\t\tupdateDnD();\r\n
\t\t\treturn;\r\n
\t\t}\r\n
\t\topts = $.extend({\r\n
\t\t\t"drag" : function (opts) {\r\n
\t\t\t\treturn $.extend({\r\n
\t\t\t\t\tstart : function (ev, ui) {\r\n
\t\t\t\t\t\t// if we are in subgrid mode try to collapse the node\r\n
\t\t\t\t\t\tif($t.p.subGrid) {\r\n
\t\t\t\t\t\t\tvar subgid = $(ui.helper).attr("id");\r\n
\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\t$($t).jqGrid(\'collapseSubGridRow\',subgid);\r\n
\t\t\t\t\t\t\t} catch (e) {}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t// hack\r\n
\t\t\t\t\t\t// drag and drop does not insert tr in table, when the table has no rows\r\n
\t\t\t\t\t\t// we try to insert new empty row on the target(s)\r\n
\t\t\t\t\t\tfor (var i=0;i<$.data($t,"dnd").connectWith.length;i++){\r\n
\t\t\t\t\t\t\tif($($.data($t,"dnd").connectWith[i]).jqGrid(\'getGridParam\',\'reccount\') == "0" ){\r\n
\t\t\t\t\t\t\t\t$($.data($t,"dnd").connectWith[i]).jqGrid(\'addRowData\',\'jqg_empty_row\',{});\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tui.helper.addClass("ui-state-highlight");\r\n
\t\t\t\t\t\t$("td",ui.helper).each(function(i) {\r\n
\t\t\t\t\t\t\tthis.style.width = $t.grid.headers[i].width+"px";\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t\tif(opts.onstart && $.isFunction(opts.onstart) ) { opts.onstart.call($($t),ev,ui); }\r\n
\t\t\t\t\t},\r\n
\t\t\t\t\tstop :function(ev,ui) {\r\n
\t\t\t\t\t\tif(ui.helper.dropped && !opts.dragcopy) {\r\n
\t\t\t\t\t\t\tvar ids = $(ui.helper).attr("id");\r\n
\t\t\t\t\t\t\tif(ids === undefined) { ids = $(this).attr("id"); }\r\n
\t\t\t\t\t\t\t$($t).jqGrid(\'delRowData\',ids );\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t// if we have a empty row inserted from start event try to delete it\r\n
\t\t\t\t\t\tfor (var i=0;i<$.data($t,"dnd").connectWith.length;i++){\r\n
\t\t\t\t\t\t\t$($.data($t,"dnd").connectWith[i]).jqGrid(\'delRowData\',\'jqg_empty_row\');\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(opts.onstop && $.isFunction(opts.onstop) ) { opts.onstop.call($($t),ev,ui); }\r\n
\t\t\t\t\t}\r\n
\t\t\t\t},opts.drag_opts || {});\r\n
\t\t\t},\r\n
\t\t\t"drop" : function (opts) {\r\n
\t\t\t\treturn $.extend({\r\n
\t\t\t\t\taccept: function(d) {\r\n
\t\t\t\t\t\tif (!$(d).hasClass(\'jqgrow\')) { return d;}\r\n
\t\t\t\t\t\tvar tid = $(d).closest("table.ui-jqgrid-btable");\r\n
\t\t\t\t\t\tif(tid.length > 0 && $.data(tid[0],"dnd") !== undefined) {\r\n
\t\t\t\t\t\t    var cn = $.data(tid[0],"dnd").connectWith;\r\n
\t\t\t\t\t\t    return $.inArray(\'#\'+$.jgrid.jqID(this.id),cn) != -1 ? true : false;\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t},\r\n
\t\t\t\t\tdrop: function(ev, ui) {\r\n
\t\t\t\t\t\tif (!$(ui.draggable).hasClass(\'jqgrow\')) { return; }\r\n
\t\t\t\t\t\tvar accept = $(ui.draggable).attr("id");\r\n
\t\t\t\t\t\tvar getdata = ui.draggable.parent().parent().jqGrid(\'getRowData\',accept);\r\n
\t\t\t\t\t\tif(!opts.dropbyname) {\r\n
\t\t\t\t\t\t\tvar j =0, tmpdata = {}, nm;\r\n
\t\t\t\t\t\t\tvar dropmodel = $("#"+$.jgrid.jqID(this.id)).jqGrid(\'getGridParam\',\'colModel\');\r\n
\t\t\t\t\t\t\ttry {\r\n
\t\t\t\t\t\t\t\tfor (var key in getdata) {\r\n
\t\t\t\t\t\t\t\t\tnm = dropmodel[j].name;\r\n
\t\t\t\t\t\t\t\t\tif( !(nm == \'cb\' || nm ==\'rn\' || nm == \'subgrid\' )) {\r\n
\t\t\t\t\t\t\t\t\t\tif(getdata.hasOwnProperty(key) && dropmodel[j]) {\r\n
\t\t\t\t\t\t\t\t\t\t\ttmpdata[nm] = getdata[key];\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\tj++;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tgetdata = tmpdata;\r\n
\t\t\t\t\t\t\t} catch (e) {}\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tui.helper.dropped = true;\r\n
\t\t\t\t\t\tif(opts.beforedrop && $.isFunction(opts.beforedrop) ) {\r\n
\t\t\t\t\t\t\t//parameters to this callback - event, element, data to be inserted, sender, reciever\r\n
\t\t\t\t\t\t\t// should return object which will be inserted into the reciever\r\n
\t\t\t\t\t\t\tvar datatoinsert = opts.beforedrop.call(this,ev,ui,getdata,$(\'#\'+$.jgrid.jqID($t.p.id)),$(this));\r\n
\t\t\t\t\t\t\tif (typeof datatoinsert != "undefined" && datatoinsert !== null && typeof datatoinsert == "object") { getdata = datatoinsert; }\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(ui.helper.dropped) {\r\n
\t\t\t\t\t\t\tvar grid;\r\n
\t\t\t\t\t\t\tif(opts.autoid) {\r\n
\t\t\t\t\t\t\t\tif($.isFunction(opts.autoid)) {\r\n
\t\t\t\t\t\t\t\t\tgrid = opts.autoid.call(this,getdata);\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\tgrid = Math.ceil(Math.random()*1000);\r\n
\t\t\t\t\t\t\t\t\tgrid = opts.autoidprefix+grid;\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t// NULL is interpreted as undefined while null as object\r\n
\t\t\t\t\t\t\t$("#"+$.jgrid.jqID(this.id)).jqGrid(\'addRowData\',grid,getdata,opts.droppos);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t\tif(opts.ondrop && $.isFunction(opts.ondrop) ) { opts.ondrop.call(this,ev,ui, getdata); }\r\n
\t\t\t\t\t}}, opts.drop_opts || {});\r\n
\t\t\t},\r\n
\t\t\t"onstart" : null,\r\n
\t\t\t"onstop" : null,\r\n
\t\t\t"beforedrop": null,\r\n
\t\t\t"ondrop" : null,\r\n
\t\t\t"drop_opts" : {\r\n
\t\t\t\t"activeClass": "ui-state-active",\r\n
\t\t\t\t"hoverClass": "ui-state-hover"\r\n
\t\t\t},\r\n
\t\t\t"drag_opts" : {\r\n
\t\t\t\t"revert": "invalid",\r\n
\t\t\t\t"helper": "clone",\r\n
\t\t\t\t"cursor": "move",\r\n
\t\t\t\t"appendTo" : "#jqgrid_dnd",\r\n
\t\t\t\t"zIndex": 5000\r\n
\t\t\t},\r\n
\t\t\t"dragcopy": false,\r\n
\t\t\t"dropbyname" : false,\r\n
\t\t\t"droppos" : "first",\r\n
\t\t\t"autoid" : true,\r\n
\t\t\t"autoidprefix" : "dnd_"\r\n
\t\t}, opts || {});\r\n
\t\t\r\n
\t\tif(!opts.connectWith) { return; }\r\n
\t\topts.connectWith = opts.connectWith.split(",");\r\n
\t\topts.connectWith = $.map(opts.connectWith,function(n){return $.trim(n);});\r\n
\t\t$.data($t,"dnd",opts);\r\n
\t\t\r\n
\t\tif($t.p.reccount != "0" && !$t.p.jqgdnd) {\r\n
\t\t\tupdateDnD();\r\n
\t\t}\r\n
\t\t$t.p.jqgdnd = true;\r\n
\t\tfor (var i=0;i<opts.connectWith.length;i++){\r\n
\t\t\tvar cn =opts.connectWith[i];\r\n
\t\t\t$(cn).droppable($.isFunction(opts.drop) ? opts.drop.call($($t),opts) : opts.drop);\r\n
\t\t}\r\n
\t\t});\r\n
\t},\r\n
\tgridResize : function(opts) {\r\n
\t\treturn this.each(function(){\r\n
\t\t\tvar $t = this, gID = $.jgrid.jqID($t.p.id);\r\n
\t\t\tif(!$t.grid || !$.fn.resizable) { return; }\r\n
\t\t\topts = $.extend({}, opts || {});\r\n
\t\t\tif(opts.alsoResize ) {\r\n
\t\t\t\topts._alsoResize_ = opts.alsoResize;\r\n
\t\t\t\tdelete opts.alsoResize;\r\n
\t\t\t} else {\r\n
\t\t\t\topts._alsoResize_ = false;\r\n
\t\t\t}\r\n
\t\t\tif(opts.stop && $.isFunction(opts.stop)) {\r\n
\t\t\t\topts._stop_ = opts.stop;\r\n
\t\t\t\tdelete opts.stop;\r\n
\t\t\t} else {\r\n
\t\t\t\topts._stop_ = false;\r\n
\t\t\t}\r\n
\t\t\topts.stop = function (ev, ui) {\r\n
\t\t\t\t$($t).jqGrid(\'setGridParam\',{height:$("#gview_"+gID+" .ui-jqgrid-bdiv").height()});\r\n
\t\t\t\t$($t).jqGrid(\'setGridWidth\',ui.size.width,opts.shrinkToFit);\r\n
\t\t\t\tif(opts._stop_) { opts._stop_.call($t,ev,ui); }\r\n
\t\t\t};\r\n
\t\t\tif(opts._alsoResize_) {\r\n
\t\t\t\tvar optstest = "{\\\'#gview_"+gID+" .ui-jqgrid-bdiv\\\':true,\'" +opts._alsoResize_+"\':true}";\r\n
\t\t\t\topts.alsoResize = eval(\'(\'+optstest+\')\'); // the only way that I found to do this\r\n
\t\t\t} else {\r\n
\t\t\t\topts.alsoResize = $(".ui-jqgrid-bdiv","#gview_"+gID);\r\n
\t\t\t}\r\n
\t\t\tdelete opts._alsoResize_;\r\n
\t\t\t$("#gbox_"+gID).resizable(opts);\r\n
\t\t});\r\n
\t}\r\n
});\r\n
})(jQuery);\r\n
/*\r\n
 Transform a table to a jqGrid.\r\n
 Peter Romianowski <peter.romianowski@optivo.de> \r\n
 If the first column of the table contains checkboxes or\r\n
 radiobuttons then the jqGrid is made selectable.\r\n
*/\r\n
// Addition - selector can be a class or id\r\n
function tableToGrid(selector, options) {\r\n
jQuery(selector).each(function() {\r\n
\tif(this.grid) {return;} //Adedd from Tony Tomov\r\n
\t// This is a small "hack" to make the width of the jqGrid 100%\r\n
\tjQuery(this).width("99%");\r\n
\tvar w = jQuery(this).width();\r\n
\r\n
\t// Text whether we have single or multi select\r\n
\tvar inputCheckbox = jQuery(\'tr td:first-child input[type=checkbox]:first\', jQuery(this));\r\n
\tvar inputRadio = jQuery(\'tr td:first-child input[type=radio]:first\', jQuery(this));\r\n
\tvar selectMultiple = inputCheckbox.length > 0;\r\n
\tvar selectSingle = !selectMultiple && inputRadio.length > 0;\r\n
\tvar selectable = selectMultiple || selectSingle;\r\n
\t//var inputName = inputCheckbox.attr("name") || inputRadio.attr("name");\r\n
\r\n
\t// Build up the columnModel and the data\r\n
\tvar colModel = [];\r\n
\tvar colNames = [];\r\n
\tjQuery(\'th\', jQuery(this)).each(function() {\r\n
\t\tif (colModel.length === 0 && selectable) {\r\n
\t\t\tcolModel.push({\r\n
\t\t\t\tname: \'__selection__\',\r\n
\t\t\t\tindex: \'__selection__\',\r\n
\t\t\t\twidth: 0,\r\n
\t\t\t\thidden: true\r\n
\t\t\t});\r\n
\t\t\tcolNames.push(\'__selection__\');\r\n
\t\t} else {\r\n
\t\t\tcolModel.push({\r\n
\t\t\t\tname: jQuery(this).attr("id") || jQuery.trim(jQuery.jgrid.stripHtml(jQuery(this).html())).split(\' \').join(\'_\'),\r\n
\t\t\t\tindex: jQuery(this).attr("id") || jQuery.trim(jQuery.jgrid.stripHtml(jQuery(this).html())).split(\' \').join(\'_\'),\r\n
\t\t\t\twidth: jQuery(this).width() || 150\r\n
\t\t\t});\r\n
\t\t\tcolNames.push(jQuery(this).html());\r\n
\t\t}\r\n
\t});\r\n
\tvar data = [];\r\n
\tvar rowIds = [];\r\n
\tvar rowChecked = [];\r\n
\tjQuery(\'tbody > tr\', jQuery(this)).each(function() {\r\n
\t\tvar row = {};\r\n
\t\tvar rowPos = 0;\r\n
\t\tjQuery(\'td\', jQuery(this)).each(function() {\r\n
\t\t\tif (rowPos === 0 && selectable) {\r\n
\t\t\t\tvar input = jQuery(\'input\', jQuery(this));\r\n
\t\t\t\tvar rowId = input.attr("value");\r\n
\t\t\t\trowIds.push(rowId || data.length);\r\n
\t\t\t\tif (input.is(":checked")) {\r\n
\t\t\t\t\trowChecked.push(rowId);\r\n
\t\t\t\t}\r\n
\t\t\t\trow[colModel[rowPos].name] = input.attr("value");\r\n
\t\t\t} else {\r\n
\t\t\t\trow[colModel[rowPos].name] = jQuery(this).html();\r\n
\t\t\t}\r\n
\t\t\trowPos++;\r\n
\t\t});\r\n
\t\tif(rowPos >0) { data.push(row); }\r\n
\t});\r\n
\r\n
\t// Clear the original HTML table\r\n
\tjQuery(this).empty();\r\n
\r\n
\t// Mark it as jqGrid\r\n
\tjQuery(this).addClass("scroll");\r\n
\r\n
\tjQuery(this).jqGrid(jQuery.extend({\r\n
\t\tdatatype: "local",\r\n
\t\twidth: w,\r\n
\t\tcolNames: colNames,\r\n
\t\tcolModel: colModel,\r\n
\t\tmultiselect: selectMultiple\r\n
\t\t//inputName: inputName,\r\n
\t\t//inputValueCol: imputName != null ? "__selection__" : null\r\n
\t}, options || {}));\r\n
\r\n
\t// Add data\r\n
\tvar a;\r\n
\tfor (a = 0; a < data.length; a++) {\r\n
\t\tvar id = null;\r\n
\t\tif (rowIds.length > 0) {\r\n
\t\t\tid = rowIds[a];\r\n
\t\t\tif (id && id.replace) {\r\n
\t\t\t\t// We have to do this since the value of a checkbox\r\n
\t\t\t\t// or radio button can be anything \r\n
\t\t\t\tid = encodeURIComponent(id).replace(/[.\\-%]/g, "_");\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tif (id === null) {\r\n
\t\t\tid = a + 1;\r\n
\t\t}\r\n
\t\tjQuery(this).jqGrid("addRowData",id, data[a]);\r\n
\t}\r\n
\r\n
\t// Set the selection\r\n
\tfor (a = 0; a < rowChecked.length; a++) {\r\n
\t\tjQuery(this).jqGrid("setSelection",rowChecked[a]);\r\n
\t}\r\n
});\r\n
};\r\n


]]></string> </value>
        </item>
        <item>
            <key> <string>next</string> </key>
            <value>
              <none/>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
