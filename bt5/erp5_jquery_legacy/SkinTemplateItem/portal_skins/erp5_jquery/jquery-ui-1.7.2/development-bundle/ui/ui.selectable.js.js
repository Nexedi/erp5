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
            <value> <string>ts65545394.61</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ui.selectable.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Selectable 1.7.2\n
 *\n
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Selectables\n
 *\n
 * Depends:\n
 *\tui.core.js\n
 */\n
(function($) {\n
\n
$.widget("ui.selectable", $.extend({}, $.ui.mouse, {\n
\n
\t_init: function() {\n
\t\tvar self = this;\n
\n
\t\tthis.element.addClass("ui-selectable");\n
\n
\t\tthis.dragged = false;\n
\n
\t\t// cache selectee children based on filter\n
\t\tvar selectees;\n
\t\tthis.refresh = function() {\n
\t\t\tselectees = $(self.options.filter, self.element[0]);\n
\t\t\tselectees.each(function() {\n
\t\t\t\tvar $this = $(this);\n
\t\t\t\tvar pos = $this.offset();\n
\t\t\t\t$.data(this, "selectable-item", {\n
\t\t\t\t\telement: this,\n
\t\t\t\t\t$element: $this,\n
\t\t\t\t\tleft: pos.left,\n
\t\t\t\t\ttop: pos.top,\n
\t\t\t\t\tright: pos.left + $this.outerWidth(),\n
\t\t\t\t\tbottom: pos.top + $this.outerHeight(),\n
\t\t\t\t\tstartselected: false,\n
\t\t\t\t\tselected: $this.hasClass(\'ui-selected\'),\n
\t\t\t\t\tselecting: $this.hasClass(\'ui-selecting\'),\n
\t\t\t\t\tunselecting: $this.hasClass(\'ui-unselecting\')\n
\t\t\t\t});\n
\t\t\t});\n
\t\t};\n
\t\tthis.refresh();\n
\n
\t\tthis.selectees = selectees.addClass("ui-selectee");\n
\n
\t\tthis._mouseInit();\n
\n
\t\tthis.helper = $(document.createElement(\'div\'))\n
\t\t\t.css({border:\'1px dotted black\'})\n
\t\t\t.addClass("ui-selectable-helper");\n
\t},\n
\n
\tdestroy: function() {\n
\t\tthis.element\n
\t\t\t.removeClass("ui-selectable ui-selectable-disabled")\n
\t\t\t.removeData("selectable")\n
\t\t\t.unbind(".selectable");\n
\t\tthis._mouseDestroy();\n
\t},\n
\n
\t_mouseStart: function(event) {\n
\t\tvar self = this;\n
\n
\t\tthis.opos = [event.pageX, event.pageY];\n
\n
\t\tif (this.options.disabled)\n
\t\t\treturn;\n
\n
\t\tvar options = this.options;\n
\n
\t\tthis.selectees = $(options.filter, this.element[0]);\n
\n
\t\tthis._trigger("start", event);\n
\n
\t\t$(options.appendTo).append(this.helper);\n
\t\t// position helper (lasso)\n
\t\tthis.helper.css({\n
\t\t\t"z-index": 100,\n
\t\t\t"position": "absolute",\n
\t\t\t"left": event.clientX,\n
\t\t\t"top": event.clientY,\n
\t\t\t"width": 0,\n
\t\t\t"height": 0\n
\t\t});\n
\n
\t\tif (options.autoRefresh) {\n
\t\t\tthis.refresh();\n
\t\t}\n
\n
\t\tthis.selectees.filter(\'.ui-selected\').each(function() {\n
\t\t\tvar selectee = $.data(this, "selectable-item");\n
\t\t\tselectee.startselected = true;\n
\t\t\tif (!event.metaKey) {\n
\t\t\t\tselectee.$element.removeClass(\'ui-selected\');\n
\t\t\t\tselectee.selected = false;\n
\t\t\t\tselectee.$element.addClass(\'ui-unselecting\');\n
\t\t\t\tselectee.unselecting = true;\n
\t\t\t\t// selectable UNSELECTING callback\n
\t\t\t\tself._trigger("unselecting", event, {\n
\t\t\t\t\tunselecting: selectee.element\n
\t\t\t\t});\n
\t\t\t}\n
\t\t});\n
\n
\t\t$(event.target).parents().andSelf().each(function() {\n
\t\t\tvar selectee = $.data(this, "selectable-item");\n
\t\t\tif (selectee) {\n
\t\t\t\tselectee.$element.removeClass("ui-unselecting").addClass(\'ui-selecting\');\n
\t\t\t\tselectee.unselecting = false;\n
\t\t\t\tselectee.selecting = true;\n
\t\t\t\tselectee.selected = true;\n
\t\t\t\t// selectable SELECTING callback\n
\t\t\t\tself._trigger("selecting", event, {\n
\t\t\t\t\tselecting: selectee.element\n
\t\t\t\t});\n
\t\t\t\treturn false;\n
\t\t\t}\n
\t\t});\n
\n
\t},\n
\n
\t_mouseDrag: function(event) {\n
\t\tvar self = this;\n
\t\tthis.dragged = true;\n
\n
\t\tif (this.options.disabled)\n
\t\t\treturn;\n
\n
\t\tvar options = this.options;\n
\n
\t\tvar x1 = this.opos[0], y1 = this.opos[1], x2 = event.pageX, y2 = event.pageY;\n
\t\tif (x1 > x2) { var tmp = x2; x2 = x1; x1 = tmp; }\n
\t\tif (y1 > y2) { var tmp = y2; y2 = y1; y1 = tmp; }\n
\t\tthis.helper.css({left: x1, top: y1, width: x2-x1, height: y2-y1});\n
\n
\t\tthis.selectees.each(function() {\n
\t\t\tvar selectee = $.data(this, "selectable-item");\n
\t\t\t//prevent helper from being selected if appendTo: selectable\n
\t\t\tif (!selectee || selectee.element == self.element[0])\n
\t\t\t\treturn;\n
\t\t\tvar hit = false;\n
\t\t\tif (options.tolerance == \'touch\') {\n
\t\t\t\thit = ( !(selectee.left > x2 || selectee.right < x1 || selectee.top > y2 || selectee.bottom < y1) );\n
\t\t\t} else if (options.tolerance == \'fit\') {\n
\t\t\t\thit = (selectee.left > x1 && selectee.right < x2 && selectee.top > y1 && selectee.bottom < y2);\n
\t\t\t}\n
\n
\t\t\tif (hit) {\n
\t\t\t\t// SELECT\n
\t\t\t\tif (selectee.selected) {\n
\t\t\t\t\tselectee.$element.removeClass(\'ui-selected\');\n
\t\t\t\t\tselectee.selected = false;\n
\t\t\t\t}\n
\t\t\t\tif (selectee.unselecting) {\n
\t\t\t\t\tselectee.$element.removeClass(\'ui-unselecting\');\n
\t\t\t\t\tselectee.unselecting = false;\n
\t\t\t\t}\n
\t\t\t\tif (!selectee.selecting) {\n
\t\t\t\t\tselectee.$element.addClass(\'ui-selecting\');\n
\t\t\t\t\tselectee.selecting = true;\n
\t\t\t\t\t// selectable SELECTING callback\n
\t\t\t\t\tself._trigger("selecting", event, {\n
\t\t\t\t\t\tselecting: selectee.element\n
\t\t\t\t\t});\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\t// UNSELECT\n
\t\t\t\tif (selectee.selecting) {\n
\t\t\t\t\tif (event.metaKey && selectee.startselected) {\n
\t\t\t\t\t\tselectee.$element.removeClass(\'ui-selecting\');\n
\t\t\t\t\t\tselectee.selecting = false;\n
\t\t\t\t\t\tselectee.$element.addClass(\'ui-selected\');\n
\t\t\t\t\t\tselectee.selected = true;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tselectee.$element.removeClass(\'ui-selecting\');\n
\t\t\t\t\t\tselectee.selecting = false;\n
\t\t\t\t\t\tif (selectee.startselected) {\n
\t\t\t\t\t\t\tselectee.$element.addClass(\'ui-unselecting\');\n
\t\t\t\t\t\t\tselectee.unselecting = true;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\t// selectable UNSELECTING callback\n
\t\t\t\t\t\tself._trigger("unselecting", event, {\n
\t\t\t\t\t\t\tunselecting: selectee.element\n
\t\t\t\t\t\t});\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tif (selectee.selected) {\n
\t\t\t\t\tif (!event.metaKey && !selectee.startselected) {\n
\t\t\t\t\t\tselectee.$element.removeClass(\'ui-selected\');\n
\t\t\t\t\t\tselectee.selected = false;\n
\n
\t\t\t\t\t\tselectee.$element.addClass(\'ui-unselecting\');\n
\t\t\t\t\t\tselectee.unselecting = true;\n
\t\t\t\t\t\t// selectable UNSELECTING callback\n
\t\t\t\t\t\tself._trigger("unselecting", event, {\n
\t\t\t\t\t\t\tunselecting: selectee.element\n
\t\t\t\t\t\t});\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\n
\t\treturn false;\n
\t},\n
\n
\t_mouseStop: function(event) {\n
\t\tvar self = this;\n
\n
\t\tthis.dragged = false;\n
\n
\t\tvar options = this.options;\n
\n
\t\t$(\'.ui-unselecting\', this.element[0]).each(function() {\n
\t\t\tvar selectee = $.data(this, "selectable-item");\n
\t\t\tselectee.$element.removeClass(\'ui-unselecting\');\n
\t\t\tselectee.unselecting = false;\n
\t\t\tselectee.startselected = false;\n
\t\t\tself._trigger("unselected", event, {\n
\t\t\t\tunselected: selectee.element\n
\t\t\t});\n
\t\t});\n
\t\t$(\'.ui-selecting\', this.element[0]).each(function() {\n
\t\t\tvar selectee = $.data(this, "selectable-item");\n
\t\t\tselectee.$element.removeClass(\'ui-selecting\').addClass(\'ui-selected\');\n
\t\t\tselectee.selecting = false;\n
\t\t\tselectee.selected = true;\n
\t\t\tselectee.startselected = true;\n
\t\t\tself._trigger("selected", event, {\n
\t\t\t\tselected: selectee.element\n
\t\t\t});\n
\t\t});\n
\t\tthis._trigger("stop", event);\n
\n
\t\tthis.helper.remove();\n
\n
\t\treturn false;\n
\t}\n
\n
}));\n
\n
$.extend($.ui.selectable, {\n
\tversion: "1.7.2",\n
\tdefaults: {\n
\t\tappendTo: \'body\',\n
\t\tautoRefresh: true,\n
\t\tcancel: ":input,option",\n
\t\tdelay: 0,\n
\t\tdistance: 0,\n
\t\tfilter: \'*\',\n
\t\ttolerance: \'touch\'\n
\t}\n
});\n
\n
})(jQuery);\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <long>6546</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
