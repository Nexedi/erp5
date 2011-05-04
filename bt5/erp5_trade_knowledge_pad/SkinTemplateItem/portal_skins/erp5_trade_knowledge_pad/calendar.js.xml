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
            <value> <string>ts94421826.17</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>calendar.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/**\n
 * jCalendar 0.5\n
 *\n
 * Some code based on jQuery Date Picker (http://kelvinluck.com/assets/jquery/datePicker/)\n
 *\n
 * Copyright (c) 2007 Theodore Serbinski (http://tedserbinski.com)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 */\n
jQuery.jcalendar = function() {\n
\tvar months = [\'January\', \'February\', \'March\', \'April\', \'May\', \'June\', \'July\', \'August\', \'September\', \'October\', \'November\', \'December\'];\n
\tvar days = [\'S\', \'M\', \'Tu\', \'W\', \'Th\', \'F\', \'S\'];\n
\tvar navLinks = {p:\'Prev\', n:\'Next\', t:\'Today\'};\n
\tvar _firstDayOfWeek;\n
\tvar _firstDate;\n
\tvar _lastDate;\n
\tvar _selectedDate;\n
\n
\tvar _drawCalendar = function(dateIn, a, day, month, year) {\n
\t  var today = new Date();\n
\t  var d;\n
\n
\t\tif (dateIn == undefined) {\n
\t\t\t// start from this month.\n
\t\t\td = new Date(today.getFullYear(), today.getMonth(), 1);\n
\t\t\tyear.val(today.getFullYear());\n
\t\t\tmonth.val(today.getMonth()+1);\n
\t\t\tday.val(today.getDate());\n
\t\t}\n
\t\telse {\n
\t\t\t// start from the passed in date\n
\t\t\td = dateIn;\n
\t\t  d.setDate(1);\n
\t\t}\n
\n
\t\t// check that date is within allowed limits\n
\t\tif ((d.getMonth() < _firstDate.getMonth() && d.getFullYear() == _firstDate.getFullYear()) || d.getFullYear() < _firstDate.getFullYear()) {\n
\t\t\td = new Date(_firstDate.getFullYear(), _firstDate.getMonth(), 1);\n
\t\t}\n
\t\telse if ((d.getMonth() > _lastDate.getMonth() && d.getFullYear() == _lastDate.getFullYear()) || d.getFullYear() > _lastDate.getFullYear()) {\n
\t\t\td = new Date(_lastDate.getFullYear(), _lastDate.getMonth(), 1);\n
\t\t}\n
\n
\t\tvar firstMonth = true;\n
\t\tvar firstDate = _firstDate.getDate();\n
\n
\t\t// create prev and next links\n
\t\tif (!(d.getMonth() == _firstDate.getMonth() && d.getFullYear() == _firstDate.getFullYear())) {\n
\t\t\t// not in first display month so show a previous link\n
\t\t\tfirstMonth = false;\n
\t\t\tvar lastMonth = d.getMonth() == 0 ? new Date(d.getFullYear()-1, 11, 1) : new Date(d.getFullYear(), d.getMonth()-1, 1);\n
\t\t\tvar prevLink = jQuery(\'<a href="" class="link-prev">&lsaquo; \'+ navLinks.p +\'</a>\').click(function() {\n
\t\t\t\tjQuery.jcalendar.changeMonth(lastMonth, this, day, month, year);\n
\t\t\t\treturn false;\n
\t\t\t});\n
\t\t}\n
\n
\t\tvar finalMonth = true;\n
\t\tvar lastDate = _lastDate.getDate();\n
\n
\t\tif (!(d.getMonth() == _lastDate.getMonth() && d.getFullYear() == _lastDate.getFullYear())) {\n
\t\t\t// in the last month - no next link\n
\t\t\tfinalMonth = false;\n
\t\t\tvar nextMonth = new Date(d.getFullYear(), d.getMonth()+1, 1);\n
\t\t\tvar nextLink = jQuery(\'<a href="" class="link-next">\'+ navLinks.n +\' &rsaquo;</a>\').click(function() {\n
\t\t\t\tjQuery.jcalendar.changeMonth(nextMonth, this, day, month, year);\n
\t\t\t\treturn false;\n
\t\t\t});\n
\t\t}\n
\n
\t\tvar todayLink = jQuery(\'<a href="" class="link-today">\'+ navLinks.t +\'</a>\').click(function() {\n
\t\t\tday.val(today.getDate());\n
\t\t\tjQuery.jcalendar.changeMonth(today, this, day, month, year);\n
\t\t\treturn false;\n
\t\t});\n
\n
    // update the year and month select boxes\n
  \tyear.val(d.getFullYear());\n
  \tmonth.val(d.getMonth()+1);\n
\n
\t\tvar headRow = jQuery("<tr></tr>");\n
\t\tfor (var i=_firstDayOfWeek; i<_firstDayOfWeek+7; i++) {\n
\t\t\tvar weekday = i%7;\n
\t\t\tvar wordday = days[weekday];\n
\t\t\theadRow.append(\'<th scope="col" abbr="\'+ wordday +\'" title="\'+ wordday +\'" class="\'+ (weekday == 0 || weekday == 6 ? \'weekend\' : \'weekday\') +\'">\'+ wordday +\'</th>\');\n
\t\t}\n
\t\theadRow = jQuery("<thead></thead>").append(headRow);\n
\n
\t\tvar tBody = jQuery("<tbody></tbody>");\n
\t\tvar lastDay = (new Date(d.getFullYear(), d.getMonth()+1, 0)).getDate();\n
\t\tvar curDay = _firstDayOfWeek - d.getDay();\n
\t\tif (curDay > 0) curDay -= 7;\n
\n
\t\tvar todayDate = today.getDate();\n
\t\tvar thisMonth = d.getMonth() == today.getMonth() && d.getFullYear() == today.getFullYear();\n
\n
    // render calendar\n
\t\tdo {\n
 \t\t  var thisRow = jQuery("<tr></tr>");\n
  \t\tfor (var i=0; i<7; i++) {\n
  \t\t\tvar weekday = (_firstDayOfWeek + i) % 7;\n
  \t\t\tvar atts = {\'class\':(weekday == 0 || weekday == 6 ? \'weekend \' : \'weekday \')};\n
\n
  \t\t\tif (curDay < 0 || curDay >= lastDay) {\n
  \t\t\t\tdayStr = \' \';\n
  \t\t\t}\n
  \t\t\telse if (firstMonth && curDay < firstDate-1) {\n
  \t\t\t\tdayStr = curDay+1;\n
  \t\t\t\tatts[\'class\'] += \'inactive\';\n
  \t\t\t}\n
  \t\t\telse if (finalMonth && curDay > lastDate-1) {\n
  \t\t\t\tdayStr = curDay+1;\n
  \t\t\t\tatts[\'class\'] += \'inactive\';\n
  \t\t\t}\n
  \t\t\telse {\n
  \t\t\t\td.setDate(curDay+1);\n
\n
  \t\t\t\t// attach a click handler to every day to select it if clicked\n
  \t\t\t\t// we use the rel attribute to keep track of the day that is being clicked\n
  \t\t\t\tdayStr = jQuery(\'<a href="" rel="\'+ d +\'">\'+ (curDay+1) +\'</a>\').click(function(e) {\n
            if (_selectedDate) {\n
               _selectedDate.removeClass(\'selected\');\n
            }\n
      \t\t\t_selectedDate = jQuery(this);\n
      \t\t\t_selectedDate.addClass(\'selected\');\n
            day.val(new Date(_selectedDate.attr(\'rel\')).getDate());\n
  \t\t\t\t\treturn false;\n
  \t\t\t\t});\n
\n
  \t\t\t\t// highlight the current selected day\n
  \t\t\t\tif (day.val() == d.getDate()) {\n
  \t\t\t\t  _selectedDate = dayStr;\n
  \t\t\t\t  _selectedDate.addClass(\'selected\');\n
  \t\t\t\t}\n
  \t\t\t}\n
\n
  \t\t\tif (thisMonth && curDay+1 == todayDate) {\n
  \t\t\t\tatts[\'class\'] += \'today\';\n
  \t\t\t}\n
  \t\t\tthisRow.append(jQuery("<td></td>").attr(atts).append(dayStr));\n
  \t\t\tcurDay++;\n
      }\n
\n
\t\t\ttBody.append(thisRow);\n
\t\t} while (curDay < lastDay);\n
\n
\t\tjQuery(\'div.jcalendar\').html(\'<table cellspacing="1"></table><div class="jcalendar-links"></div>\');\n
\t\tjQuery(\'div.jcalendar table\').append(headRow, tBody);\n
\t\tjQuery(\'div.jcalendar > div.jcalendar-links\').append(prevLink, todayLink, nextLink);\n
\t};\n
\n
\treturn {\n
\t\tshow: function(a, day, month, year) {\n
 \t\t\t_firstDate = a._startDate;\n
\t\t\t_lastDate = a._endDate;\n
\t\t\t_firstDayOfWeek = a._firstDayOfWeek;\n
\n
\t\t\t// pass in the selected form date if one was set\n
\t\t\tvar selected;\n
\t\t\tif (year.val() > 0 && month.val() > 0 && day.val() > 0) {\n
\t\t\t  selected = new Date(year.val(), month.val()-1, day.val());\n
\t\t\t}\n
\t\t\telse {\n
\t\t\t  selected = null;\n
\t\t\t}\n
\t\t\t_drawCalendar(selected, a, day, month, year);\n
\t\t},\n
\t\tchangeMonth: function(d, e, day, month, year) {\n
\t\t\t_drawCalendar(d, e, day, month, year);\n
\t\t},\n
\t\t/**\n
\t\t* Function: setLanguageStrings\n
\t\t*\n
\t\t* Allows you to localise the calendar by passing in relevant text for the english strings in the plugin.\n
\t\t*\n
\t\t* Arguments:\n
\t\t* days\t\t-\tArray, e.g. [\'Sunday\', \'Monday\', \'Tuesday\', \'Wednesday\', \'Thursday\', \'Friday\', \'Saturday\']\n
\t\t* months\t-\tArray, e.g. [\'January\', \'Febuary\', \'March\', \'April\', \'May\', \'June\', \'July\', \'August\', \'September\', \'October\', \'November\', \'December\'];\n
\t\t* navLinks\t-\tObject, e.g. {p:\'Prev\', n:\'Next\', c:\'Close\', b:\'Choose date\'}\n
\t\t**/\n
\t\tsetLanguageStrings: function(aDays, aMonths, aNavLinks) {\n
\t\t\tdays = aDays;\n
\t\t\tmonths = aMonths;\n
\t\t\tnavLinks = aNavLinks;\n
\t\t},\n
\t\t/**\n
\t\t* Function: setDateWindow\n
\t\t*\n
\t\t* Used internally to set the start and end dates for a given date select\n
\t\t*\n
\t\t* Arguments:\n
\t\t* i\t\t\t-\tThe id of the INPUT element this date window is for\n
\t\t* w\t\t\t-\tThe date window - an object containing startDate and endDate properties\n
\t\t*\t\t\t\te.g. {startDate:\'24-11-1981\', endDate:\'25-12-2012}\n
\t\t**/\n
\t\tsetDateWindow: function(i, w, year) {\n
\t\t\tif (w == undefined) w = {};\n
\t\t\tif (w.startDate == undefined) {\n
\t\t\t\t// set the minimum browseable date equal to January of the min year in the select box\n
\t\t\t\t// don\'t get the first option because that is an empty year\n
\n
\t\t\t\t// note we can\'t do this: year.find(\'option:eq(1)\').val()\n
\t\t\t\t// it doesn\'t work in 1.0 since find() is destructive\n
\t\t\t\t// so we copy the object to a new var\n
\t\t\t\ti._startDate = new Date($(year).find(\'option:eq(1)\').val(), 0, 1);\n
\t\t\t}\n
\t\t\telse {\n
  \t\t\tdateParts = w.startDate.split(\'-\');\n
  \t\t\ti._startDate = new Date(dateParts[2], Number(dateParts[1])-1, Number(dateParts[0]));\n
\t\t\t}\n
\t\t\tif (w.endDate == undefined) {\n
\t\t\t  // set the maximum browseable date equal to December of the max year in the select box\n
\n
\t\t\t  // note we can\'t do this: year.find(\'option:last\').val()\n
\t\t\t\t// it doesn\'t work in 1.0 since find() is destructive\n
\t\t\t\t// so we copy the object to a new var\n
\t\t\t\ti._endDate = new Date($(year).find(\'option:last\').val(), 11, 1);\n
\t\t\t}\n
\t\t\telse {\n
  \t\t\tdateParts = w.endDate.split(\'-\');\n
  \t\t\ti._endDate = new Date(dateParts[2], Number(dateParts[1])-1, Number(dateParts[0]));\n
\t\t\t}\n
\t\t\ti._firstDayOfWeek = w.firstDayOfWeek == undefined ? 0 : w.firstDayOfWeek;\n
\t\t}\n
\t};\n
}();\n
\n
jQuery.fn.jcalendar = function(a) {\n
\tthis.each(function() {\n
    var day = $(this).find(\'select.jcalendar-select-day\');\n
    var month = $(this).find(\'select.jcalendar-select-month\');\n
    var year = $(this).find(\'select.jcalendar-select-year\');\n
    $(\'div.jcalendar-selects\').after(\'<div class="jcalendar"></div>\');\n
\t\tjQuery.jcalendar.setDateWindow(this, a, year);\n
\t\tjQuery.jcalendar.show(this, day, month, year);\n
\n
\t\tday.change(function() {\n
\t\t  // only if a valid day is selected\n
\t\t  if (this.value > 0) {\n
\t\t    d = new Date(year.val(), month.val()-1, this.value);\n
  \t    jQuery.jcalendar.changeMonth(d, a, day, month, year);\n
  \t  }\n
\t\t});\n
\n
\t\tmonth.change(function() {\n
\t\t  // only if a valid month is selected\n
\t\t  if (this.value > 0) {\n
\t\t    d = new Date(year.val(), this.value-1, 1);\n
  \t    jQuery.jcalendar.changeMonth(d, a, day, month, year);\n
  \t  }\n
\t\t});\n
\n
\t\tyear.change(function() {\n
\t\t  // only if a valid year is selected\n
\t\t  if (this.value > 0) {\n
  \t\t  d = new Date(this.value, month.val()-1, 1);\n
    \t  jQuery.jcalendar.changeMonth(d, a, day, month, year);\n
    \t}\n
\t\t});\n
\n
\t});\n
\treturn this;\n
};\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9221</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>calendar.js</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
