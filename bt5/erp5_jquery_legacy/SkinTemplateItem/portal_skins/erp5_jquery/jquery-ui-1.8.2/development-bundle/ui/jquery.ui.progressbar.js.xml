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
            <value> <string>ts77895656.1</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.progressbar.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Progressbar 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Progressbar\n
 *\n
 * Depends:\n
 *   jquery.ui.core.js\n
 *   jquery.ui.widget.js\n
 */\n
(function( $ ) {\n
\n
$.widget( "ui.progressbar", {\n
\toptions: {\n
\t\tvalue: 0\n
\t},\n
\t_create: function() {\n
\t\tthis.element\n
\t\t\t.addClass( "ui-progressbar ui-widget ui-widget-content ui-corner-all" )\n
\t\t\t.attr({\n
\t\t\t\trole: "progressbar",\n
\t\t\t\t"aria-valuemin": this._valueMin(),\n
\t\t\t\t"aria-valuemax": this._valueMax(),\n
\t\t\t\t"aria-valuenow": this._value()\n
\t\t\t});\n
\n
\t\tthis.valueDiv = $( "<div class=\'ui-progressbar-value ui-widget-header ui-corner-left\'></div>" )\n
\t\t\t.appendTo( this.element );\n
\n
\t\tthis._refreshValue();\n
\t},\n
\n
\tdestroy: function() {\n
\t\tthis.element\n
\t\t\t.removeClass( "ui-progressbar ui-widget ui-widget-content ui-corner-all" )\n
\t\t\t.removeAttr( "role" )\n
\t\t\t.removeAttr( "aria-valuemin" )\n
\t\t\t.removeAttr( "aria-valuemax" )\n
\t\t\t.removeAttr( "aria-valuenow" );\n
\n
\t\tthis.valueDiv.remove();\n
\n
\t\t$.Widget.prototype.destroy.apply( this, arguments );\n
\t},\n
\n
\tvalue: function( newValue ) {\n
\t\tif ( newValue === undefined ) {\n
\t\t\treturn this._value();\n
\t\t}\n
\n
\t\tthis._setOption( "value", newValue );\n
\t\treturn this;\n
\t},\n
\n
\t_setOption: function( key, value ) {\n
\t\tswitch ( key ) {\n
\t\t\tcase "value":\n
\t\t\t\tthis.options.value = value;\n
\t\t\t\tthis._refreshValue();\n
\t\t\t\tthis._trigger( "change" );\n
\t\t\t\tbreak;\n
\t\t}\n
\n
\t\t$.Widget.prototype._setOption.apply( this, arguments );\n
\t},\n
\n
\t_value: function() {\n
\t\tvar val = this.options.value;\n
\t\t// normalize invalid value\n
\t\tif ( typeof val !== "number" ) {\n
\t\t\tval = 0;\n
\t\t}\n
\t\tif ( val < this._valueMin() ) {\n
\t\t\tval = this._valueMin();\n
\t\t}\n
\t\tif ( val > this._valueMax() ) {\n
\t\t\tval = this._valueMax();\n
\t\t}\n
\n
\t\treturn val;\n
\t},\n
\n
\t_valueMin: function() {\n
\t\treturn 0;\n
\t},\n
\n
\t_valueMax: function() {\n
\t\treturn 100;\n
\t},\n
\n
\t_refreshValue: function() {\n
\t\tvar value = this.value();\n
\t\tthis.valueDiv\n
\t\t\t[ value === this._valueMax() ? "addClass" : "removeClass"]( "ui-corner-right" )\n
\t\t\t.width( value + "%" );\n
\t\tthis.element.attr( "aria-valuenow", value );\n
\t}\n
});\n
\n
$.extend( $.ui.progressbar, {\n
\tversion: "1.8.2"\n
});\n
\n
})( jQuery );\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2204</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
