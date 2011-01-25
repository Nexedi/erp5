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
            <value> <string>ts95872666.28</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>Common.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

try { document.execCommand("BackgroundImageCache", false, true); } catch (e) { }\r\n
var popUpWin;\r\n
function PopUpCenterWindow(URLStr, width, height, newWin, scrollbars) {\r\n
    var popUpWin = 0;\r\n
    if (typeof (newWin) == "undefined") {\r\n
        newWin = false;\r\n
    }\r\n
    if (typeof (scrollbars) == "undefined") {\r\n
        scrollbars = 0;\r\n
    }\r\n
    if (typeof (width) == "undefined") {\r\n
        width = 800;\r\n
    }\r\n
    if (typeof (height) == "undefined") {\r\n
        height = 600;\r\n
    }\r\n
    var left = 0;\r\n
    var top = 0;\r\n
    if (screen.width >= width) {\r\n
        left = Math.floor((screen.width - width) / 2);\r\n
    }\r\n
    if (screen.height >= height) {\r\n
        top = Math.floor((screen.height - height) / 2);\r\n
    }\r\n
    if (newWin) {\r\n
        open(URLStr, \'\', \'toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=\' + scrollbars + \',resizable=yes,copyhistory=yes,width=\' + width + \',height=\' + height + \',left=\' + left + \', top=\' + top + \',screenX=\' + left + \',screenY=\' + top + \'\');\r\n
        return;\r\n
    }\r\n
\r\n
    if (popUpWin) {\r\n
        if (!popUpWin.closed) popUpWin.close();\r\n
    }\r\n
    popUpWin = open(URLStr, \'popUpWin\', \'toolbar=no,location=no,directories=no,status=no,menubar=no,scrollbars=\' + scrollbars + \',resizable=yes,copyhistory=yes,width=\' + width + \',height=\' + height + \',left=\' + left + \', top=\' + top + \',screenX=\' + left + \',screenY=\' + top + \'\');\r\n
    popUpWin.focus();\r\n
}\r\n
\r\n
function OpenModelWindow(url, option) {\r\n
    var fun;\r\n
    try {\r\n
        if (parent != null && parent.$ != null && parent.$.ShowIfrmDailog != undefined) {\r\n
            fun = parent.$.ShowIfrmDailog\r\n
        }\r\n
        else {\r\n
            fun = $.ShowIfrmDailog;\r\n
        }\r\n
    }\r\n
    catch (e) {\r\n
        fun = $.ShowIfrmDailog;\r\n
    }\r\n
    fun(url, option);\r\n
}\r\n
function CloseModelWindow(callback, dooptioncallback) {\r\n
    parent.$.closeIfrm(callback, dooptioncallback);\r\n
}\r\n
\r\n
\r\n
function StrFormat(temp, dataarry) {\r\n
    return temp.replace(/\\{([\\d]+)\\}/g, function(s1, s2) { var s = dataarry[s2]; if (typeof (s) != "undefined") { if (s instanceof (Date)) { return s.getTimezoneOffset() } else { return encodeURIComponent(s) } } else { return "" } });\r\n
}\r\n
function StrFormatNoEncode(temp, dataarry) {\r\n
    return temp.replace(/\\{([\\d]+)\\}/g, function(s1, s2) { var s = dataarry[s2]; if (typeof (s) != "undefined") { if (s instanceof (Date)) { return s.getTimezoneOffset() } else { return (s); } } else { return ""; } });\r\n
}\r\n
function getiev() {\r\n
    var userAgent = window.navigator.userAgent.toLowerCase();\r\n
    $.browser.msie8 = $.browser.msie && /msie 8\\.0/i.test(userAgent);\r\n
    $.browser.msie7 = $.browser.msie && /msie 7\\.0/i.test(userAgent);\r\n
    $.browser.msie6 = !$.browser.msie8 && !$.browser.msie7 && $.browser.msie && /msie 6\\.0/i.test(userAgent);\r\n
    var v;\r\n
    if ($.browser.msie8) {\r\n
        v = 8;\r\n
    }\r\n
    else if ($.browser.msie7) {\r\n
        v = 7;\r\n
    }\r\n
    else if ($.browser.msie6) {\r\n
        v = 6;\r\n
    }\r\n
    else { v = -1; }\r\n
    return v;\r\n
}\r\n
$(document).ready(function() {\r\n
    var v = getiev()\r\n
    if (v > 0) {\r\n
        $(document.body).addClass("ie ie" + v);\r\n
    }\r\n
\r\n
});\r\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>3139</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Common.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
