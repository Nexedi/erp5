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
            <value> <string>ts58176408.54</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>grid.locale-en.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

;(function($){\r\n
/**\r\n
 * jqGrid English Translation\r\n
 * Tony Tomov tony@trirand.com\r\n
 * http://trirand.com/blog/ \r\n
 * Dual licensed under the MIT and GPL licenses:\r\n
 * http://www.opensource.org/licenses/mit-license.php\r\n
 * http://www.gnu.org/licenses/gpl.html\r\n
**/\r\n
$.jgrid = $.jgrid || {};\r\n
$.extend($.jgrid,{\r\n
\tdefaults : {\r\n
\t\trecordtext: "View {0} - {1} of {2}",\r\n
\t\temptyrecords: "No records to view",\r\n
\t\tloadtext: "Loading...",\r\n
\t\tpgtext : "Page {0} of {1}"\r\n
\t},\r\n
\tsearch : {\r\n
\t\tcaption: "Search...",\r\n
\t\tFind: "Find",\r\n
\t\tReset: "Reset",\r\n
\t\todata : [\'equal\', \'not equal\', \'less\', \'less or equal\',\'greater\',\'greater or equal\', \'begins with\',\'does not begin with\',\'is in\',\'is not in\',\'ends with\',\'does not end with\',\'contains\',\'does not contain\'],\r\n
\t\tgroupOps: [\t{ op: "AND", text: "all" },\t{ op: "OR",  text: "any" }\t],\r\n
\t\tmatchText: " match",\r\n
\t\trulesText: " rules"\r\n
\t},\r\n
\tedit : {\r\n
\t\taddCaption: "Add Record",\r\n
\t\teditCaption: "Edit Record",\r\n
\t\tbSubmit: "Submit",\r\n
\t\tbCancel: "Cancel",\r\n
\t\tbClose: "Close",\r\n
\t\tsaveData: "Data has been changed! Save changes?",\r\n
\t\tbYes : "Yes",\r\n
\t\tbNo : "No",\r\n
\t\tbExit : "Cancel",\r\n
\t\tmsg: {\r\n
\t\t\trequired:"Field is required",\r\n
\t\t\tnumber:"Please, enter valid number",\r\n
\t\t\tminValue:"value must be greater than or equal to ",\r\n
\t\t\tmaxValue:"value must be less than or equal to",\r\n
\t\t\temail: "is not a valid e-mail",\r\n
\t\t\tinteger: "Please, enter valid integer value",\r\n
\t\t\tdate: "Please, enter valid date value",\r\n
\t\t\turl: "is not a valid URL. Prefix required (\'http://\' or \'https://\')",\r\n
\t\t\tnodefined : " is not defined!",\r\n
\t\t\tnovalue : " return value is required!",\r\n
\t\t\tcustomarray : "Custom function should return array!",\r\n
\t\t\tcustomfcheck : "Custom function should be present in case of custom checking!"\r\n
\t\t\t\r\n
\t\t}\r\n
\t},\r\n
\tview : {\r\n
\t\tcaption: "View Record",\r\n
\t\tbClose: "Close"\r\n
\t},\r\n
\tdel : {\r\n
\t\tcaption: "Delete",\r\n
\t\tmsg: "Delete selected record(s)?",\r\n
\t\tbSubmit: "Delete",\r\n
\t\tbCancel: "Cancel"\r\n
\t},\r\n
\tnav : {\r\n
\t\tedittext: "",\r\n
\t\tedittitle: "Edit selected row",\r\n
\t\taddtext:"",\r\n
\t\taddtitle: "Add new row",\r\n
\t\tdeltext: "",\r\n
\t\tdeltitle: "Delete selected row",\r\n
\t\tsearchtext: "",\r\n
\t\tsearchtitle: "Find records",\r\n
\t\trefreshtext: "",\r\n
\t\trefreshtitle: "Reload Grid",\r\n
\t\talertcap: "Warning",\r\n
\t\talerttext: "Please, select row",\r\n
\t\tviewtext: "",\r\n
\t\tviewtitle: "View selected row"\r\n
\t},\r\n
\tcol : {\r\n
\t\tcaption: "Select columns",\r\n
\t\tbSubmit: "Ok",\r\n
\t\tbCancel: "Cancel"\r\n
\t},\r\n
\terrors : {\r\n
\t\terrcap : "Error",\r\n
\t\tnourl : "No url is set",\r\n
\t\tnorecords: "No records to process",\r\n
\t\tmodel : "Length of colNames <> colModel!"\r\n
\t},\r\n
\tformatter : {\r\n
\t\tinteger : {thousandsSeparator: ",", defaultValue: \'0\'},\r\n
\t\tnumber : {decimalSeparator:".", thousandsSeparator: ",", decimalPlaces: 2, defaultValue: \'0.00\'},\r\n
\t\tcurrency : {decimalSeparator:".", thousandsSeparator: ",", decimalPlaces: 2, prefix: "", suffix:"", defaultValue: \'0.00\'},\r\n
\t\tdate : {\r\n
\t\t\tdayNames:   [\r\n
\t\t\t\t"Sun", "Mon", "Tue", "Wed", "Thr", "Fri", "Sat",\r\n
\t\t\t\t"Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"\r\n
\t\t\t],\r\n
\t\t\tmonthNames: [\r\n
\t\t\t\t"Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec",\r\n
\t\t\t\t"January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"\r\n
\t\t\t],\r\n
\t\t\tAmPm : ["am","pm","AM","PM"],\r\n
\t\t\tS: function (j) {return j < 11 || j > 13 ? [\'st\', \'nd\', \'rd\', \'th\'][Math.min((j - 1) % 10, 3)] : \'th\';},\r\n
\t\t\tsrcformat: \'Y-m-d\',\r\n
\t\t\tnewformat: \'n/j/Y\',\r\n
\t\t\tmasks : {\r\n
\t\t\t\t// see http://php.net/manual/en/function.date.php for PHP format used in jqGrid\r\n
\t\t\t\t// and see http://docs.jquery.com/UI/Datepicker/formatDate\r\n
\t\t\t\t// and https://github.com/jquery/globalize#dates for alternative formats used frequently\r\n
\t\t\t\t// one can find on https://github.com/jquery/globalize/tree/master/lib/cultures many\r\n
\t\t\t\t// information about date, time, numbers and currency formats used in different countries\r\n
\t\t\t\t// one should just convert the information in PHP format\r\n
\t\t\t\tISO8601Long:"Y-m-d H:i:s",\r\n
\t\t\t\tISO8601Short:"Y-m-d",\r\n
\t\t\t\t// short date:\r\n
\t\t\t\t//    n - Numeric representation of a month, without leading zeros\r\n
\t\t\t\t//    j - Day of the month without leading zeros\r\n
\t\t\t\t//    Y - A full numeric representation of a year, 4 digits\r\n
\t\t\t\t// example: 3/1/2012 which means 1 March 2012\r\n
\t\t\t\tShortDate: "n/j/Y", // in jQuery UI Datepicker: "M/d/yyyy"\r\n
\t\t\t\t// long date:\r\n
\t\t\t\t//    l - A full textual representation of the day of the week\r\n
\t\t\t\t//    F - A full textual representation of a month\r\n
\t\t\t\t//    d - Day of the month, 2 digits with leading zeros\r\n
\t\t\t\t//    Y - A full numeric representation of a year, 4 digits\r\n
\t\t\t\tLongDate: "l, F d, Y", // in jQuery UI Datepicker: "dddd, MMMM dd, yyyy"\r\n
\t\t\t\t// long date with long time:\r\n
\t\t\t\t//    l - A full textual representation of the day of the week\r\n
\t\t\t\t//    F - A full textual representation of a month\r\n
\t\t\t\t//    d - Day of the month, 2 digits with leading zeros\r\n
\t\t\t\t//    Y - A full numeric representation of a year, 4 digits\r\n
\t\t\t\t//    g - 12-hour format of an hour without leading zeros\r\n
\t\t\t\t//    i - Minutes with leading zeros\r\n
\t\t\t\t//    s - Seconds, with leading zeros\r\n
\t\t\t\t//    A - Uppercase Ante meridiem and Post meridiem (AM or PM)\r\n
\t\t\t\tFullDateTime: "l, F d, Y g:i:s A", // in jQuery UI Datepicker: "dddd, MMMM dd, yyyy h:mm:ss tt"\r\n
\t\t\t\t// month day:\r\n
\t\t\t\t//    F - A full textual representation of a month\r\n
\t\t\t\t//    d - Day of the month, 2 digits with leading zeros\r\n
\t\t\t\tMonthDay: "F d", // in jQuery UI Datepicker: "MMMM dd"\r\n
\t\t\t\t// short time (without seconds)\r\n
\t\t\t\t//    g - 12-hour format of an hour without leading zeros\r\n
\t\t\t\t//    i - Minutes with leading zeros\r\n
\t\t\t\t//    A - Uppercase Ante meridiem and Post meridiem (AM or PM)\r\n
\t\t\t\tShortTime: "g:i A", // in jQuery UI Datepicker: "h:mm tt"\r\n
\t\t\t\t// long time (with seconds)\r\n
\t\t\t\t//    g - 12-hour format of an hour without leading zeros\r\n
\t\t\t\t//    i - Minutes with leading zeros\r\n
\t\t\t\t//    s - Seconds, with leading zeros\r\n
\t\t\t\t//    A - Uppercase Ante meridiem and Post meridiem (AM or PM)\r\n
\t\t\t\tLongTime: "g:i:s A", // in jQuery UI Datepicker: "h:mm:ss tt"\r\n
\t\t\t\tSortableDateTime: "Y-m-d\\\\TH:i:s",\r\n
\t\t\t\tUniversalSortableDateTime: "Y-m-d H:i:sO",\r\n
\t\t\t\t// month with year\r\n
\t\t\t\t//    Y - A full numeric representation of a year, 4 digits\r\n
\t\t\t\t//    F - A full textual representation of a month\r\n
\t\t\t\tYearMonth: "F, Y" // in jQuery UI Datepicker: "MMMM, yyyy"\r\n
\t\t\t},\r\n
\t\t\treformatAfterEdit : false\r\n
\t\t},\r\n
\t\tbaseLinkUrl: \'\',\r\n
\t\tshowAction: \'\',\r\n
\t\ttarget: \'\',\r\n
\t\tcheckbox : {disabled:true},\r\n
\t\tidName : \'id\'\r\n
\t}\r\n
});\r\n
})(jQuery);\r\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6531</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>grid.locale-en.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
