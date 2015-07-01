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
            <value> <string>ts25433708.96</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>erp5_datepicker_ui.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string>//\n
//\n
(function($) {\n
  var setDate = function(dateText, inst) {\n
      var date = $.datepicker.parseDate($(this).datepicker(\'option\', \'dateFormat\'), dateText);\n
      var date_map = {\n
        year: date.getFullYear(),\n
        month: date.getMonth() + 1,\n
        day: date.getDate()\n
      };\n
      $(\'input\', this.parentNode).each(function() {\n
        var name = jQuery(this).attr(\'name\');\n
        if (name !== undefined) {\n
          var word_list = name.split(\'_\');\n
          var last_word = word_list[word_list.length - 1];\n
          var value = date_map[last_word];\n
          if (value == null) {\n
            value = \'\';\n
          }\n
          this.value = value.toString();\n
        }\n
      });\n
  };\n
\n
  $.fn.erp5DatePicker = function() {\n
    this.each(function() {\n
      var input = $(\'input\', this);\n
      var size = input.size();\n
      input.each(function(index) {\n
          $(this).datepicker({\n
            onSelect: setDate\n
          });\n
         });\n
      });\n
    };\n
  })(jQuery);\n
$(document).ready(function(){\n
  $(\'div.date_field div.input\').erp5DatePicker();\n
});\n
</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1069</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
