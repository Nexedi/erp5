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
            <value> <string>ts77895655.71</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.autocomplete.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Autocomplete 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Autocomplete\n
 *\n
 * Depends:\n
 *\tjquery.ui.core.js\n
 *\tjquery.ui.widget.js\n
 *\tjquery.ui.position.js\n
 */\n
(function( $ ) {\n
\n
$.widget( "ui.autocomplete", {\n
\toptions: {\n
\t\tminLength: 1,\n
\t\tdelay: 300\n
\t},\n
\t_create: function() {\n
\t\tvar self = this,\n
\t\t\tdoc = this.element[ 0 ].ownerDocument;\n
\t\tthis.element\n
\t\t\t.addClass( "ui-autocomplete-input" )\n
\t\t\t.attr( "autocomplete", "off" )\n
\t\t\t// TODO verify these actually work as intended\n
\t\t\t.attr({\n
\t\t\t\trole: "textbox",\n
\t\t\t\t"aria-autocomplete": "list",\n
\t\t\t\t"aria-haspopup": "true"\n
\t\t\t})\n
\t\t\t.bind( "keydown.autocomplete", function( event ) {\n
\t\t\t\tvar keyCode = $.ui.keyCode;\n
\t\t\t\tswitch( event.keyCode ) {\n
\t\t\t\tcase keyCode.PAGE_UP:\n
\t\t\t\t\tself._move( "previousPage", event );\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase keyCode.PAGE_DOWN:\n
\t\t\t\t\tself._move( "nextPage", event );\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase keyCode.UP:\n
\t\t\t\t\tself._move( "previous", event );\n
\t\t\t\t\t// prevent moving cursor to beginning of text field in some browsers\n
\t\t\t\t\tevent.preventDefault();\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase keyCode.DOWN:\n
\t\t\t\t\tself._move( "next", event );\n
\t\t\t\t\t// prevent moving cursor to end of text field in some browsers\n
\t\t\t\t\tevent.preventDefault();\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase keyCode.ENTER:\n
\t\t\t\tcase keyCode.NUMPAD_ENTER:\n
\t\t\t\t\t// when menu is open or has focus\n
\t\t\t\t\tif ( self.menu.active ) {\n
\t\t\t\t\t\tevent.preventDefault();\n
\t\t\t\t\t}\n
\t\t\t\t\t//passthrough - ENTER and TAB both select the current element\n
\t\t\t\tcase keyCode.TAB:\n
\t\t\t\t\tif ( !self.menu.active ) {\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\t\t\t\t\tself.menu.select( event );\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase keyCode.ESCAPE:\n
\t\t\t\t\tself.element.val( self.term );\n
\t\t\t\t\tself.close( event );\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase keyCode.LEFT:\n
\t\t\t\tcase keyCode.RIGHT:\n
\t\t\t\tcase keyCode.SHIFT:\n
\t\t\t\tcase keyCode.CONTROL:\n
\t\t\t\tcase keyCode.ALT:\n
\t\t\t\tcase keyCode.COMMAND:\n
\t\t\t\tcase keyCode.COMMAND_RIGHT:\n
\t\t\t\tcase keyCode.INSERT:\n
\t\t\t\tcase keyCode.CAPS_LOCK:\n
\t\t\t\tcase keyCode.END:\n
\t\t\t\tcase keyCode.HOME:\n
\t\t\t\t\t// ignore metakeys (shift, ctrl, alt)\n
\t\t\t\t\tbreak;\n
\t\t\t\tdefault:\n
\t\t\t\t\t// keypress is triggered before the input value is changed\n
\t\t\t\t\tclearTimeout( self.searching );\n
\t\t\t\t\tself.searching = setTimeout(function() {\n
\t\t\t\t\t\tself.search( null, event );\n
\t\t\t\t\t}, self.options.delay );\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t})\n
\t\t\t.bind( "focus.autocomplete", function() {\n
\t\t\t\tself.selectedItem = null;\n
\t\t\t\tself.previous = self.element.val();\n
\t\t\t})\n
\t\t\t.bind( "blur.autocomplete", function( event ) {\n
\t\t\t\tclearTimeout( self.searching );\n
\t\t\t\t// clicks on the menu (or a button to trigger a search) will cause a blur event\n
\t\t\t\tself.closing = setTimeout(function() {\n
\t\t\t\t\tself.close( event );\n
\t\t\t\t\tself._change( event );\n
\t\t\t\t}, 150 );\n
\t\t\t});\n
\t\tthis._initSource();\n
\t\tthis.response = function() {\n
\t\t\treturn self._response.apply( self, arguments );\n
\t\t};\n
\t\tthis.menu = $( "<ul></ul>" )\n
\t\t\t.addClass( "ui-autocomplete" )\n
\t\t\t.appendTo( "body", doc )\n
\t\t\t// prevent the close-on-blur in case of a "slow" click on the menu (long mousedown)\n
\t\t\t.mousedown(function() {\n
\t\t\t\t// use another timeout to make sure the blur-event-handler on the input was already triggered\n
\t\t\t\tsetTimeout(function() {\n
\t\t\t\t\tclearTimeout( self.closing );\n
\t\t\t\t}, 13);\n
\t\t\t})\n
\t\t\t.menu({\n
\t\t\t\tfocus: function( event, ui ) {\n
\t\t\t\t\tvar item = ui.item.data( "item.autocomplete" );\n
\t\t\t\t\tif ( false !== self._trigger( "focus", null, { item: item } ) ) {\n
\t\t\t\t\t\t// use value to match what will end up in the input, if it was a key event\n
\t\t\t\t\t\tif ( /^key/.test(event.originalEvent.type) ) {\n
\t\t\t\t\t\t\tself.element.val( item.value );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t},\n
\t\t\t\tselected: function( event, ui ) {\n
\t\t\t\t\tvar item = ui.item.data( "item.autocomplete" );\n
\t\t\t\t\tif ( false !== self._trigger( "select", event, { item: item } ) ) {\n
\t\t\t\t\t\tself.element.val( item.value );\n
\t\t\t\t\t}\n
\t\t\t\t\tself.close( event );\n
\t\t\t\t\t// only trigger when focus was lost (click on menu)\n
\t\t\t\t\tvar previous = self.previous;\n
\t\t\t\t\tif ( self.element[0] !== doc.activeElement ) {\n
\t\t\t\t\t\tself.element.focus();\n
\t\t\t\t\t\tself.previous = previous;\n
\t\t\t\t\t}\n
\t\t\t\t\tself.selectedItem = item;\n
\t\t\t\t},\n
\t\t\t\tblur: function( event, ui ) {\n
\t\t\t\t\tif ( self.menu.element.is(":visible") ) {\n
\t\t\t\t\t\tself.element.val( self.term );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t})\n
\t\t\t.zIndex( this.element.zIndex() + 1 )\n
\t\t\t// workaround for jQuery bug #5781 http://dev.jquery.com/ticket/5781\n
\t\t\t.css({ top: 0, left: 0 })\n
\t\t\t.hide()\n
\t\t\t.data( "menu" );\n
\t\tif ( $.fn.bgiframe ) {\n
\t\t\t this.menu.element.bgiframe();\n
\t\t}\n
\t},\n
\n
\tdestroy: function() {\n
\t\tthis.element\n
\t\t\t.removeClass( "ui-autocomplete-input" )\n
\t\t\t.removeAttr( "autocomplete" )\n
\t\t\t.removeAttr( "role" )\n
\t\t\t.removeAttr( "aria-autocomplete" )\n
\t\t\t.removeAttr( "aria-haspopup" );\n
\t\tthis.menu.element.remove();\n
\t\t$.Widget.prototype.destroy.call( this );\n
\t},\n
\n
\t_setOption: function( key ) {\n
\t\t$.Widget.prototype._setOption.apply( this, arguments );\n
\t\tif ( key === "source" ) {\n
\t\t\tthis._initSource();\n
\t\t}\n
\t},\n
\n
\t_initSource: function() {\n
\t\tvar array,\n
\t\t\turl;\n
\t\tif ( $.isArray(this.options.source) ) {\n
\t\t\tarray = this.options.source;\n
\t\t\tthis.source = function( request, response ) {\n
\t\t\t\tresponse( $.ui.autocomplete.filter(array, request.term) );\n
\t\t\t};\n
\t\t} else if ( typeof this.options.source === "string" ) {\n
\t\t\turl = this.options.source;\n
\t\t\tthis.source = function( request, response ) {\n
\t\t\t\t$.getJSON( url, request, response );\n
\t\t\t};\n
\t\t} else {\n
\t\t\tthis.source = this.options.source;\n
\t\t}\n
\t},\n
\n
\tsearch: function( value, event ) {\n
\t\tvalue = value != null ? value : this.element.val();\n
\t\tif ( value.length < this.options.minLength ) {\n
\t\t\treturn this.close( event );\n
\t\t}\n
\n
\t\tclearTimeout( this.closing );\n
\t\tif ( this._trigger("search") === false ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\treturn this._search( value );\n
\t},\n
\n
\t_search: function( value ) {\n
\t\tthis.term = this.element\n
\t\t\t.addClass( "ui-autocomplete-loading" )\n
\t\t\t// always save the actual value, not the one passed as an argument\n
\t\t\t.val();\n
\n
\t\tthis.source( { term: value }, this.response );\n
\t},\n
\n
\t_response: function( content ) {\n
\t\tif ( content.length ) {\n
\t\t\tcontent = this._normalize( content );\n
\t\t\tthis._suggest( content );\n
\t\t\tthis._trigger( "open" );\n
\t\t} else {\n
\t\t\tthis.close();\n
\t\t}\n
\t\tthis.element.removeClass( "ui-autocomplete-loading" );\n
\t},\n
\n
\tclose: function( event ) {\n
\t\tclearTimeout( this.closing );\n
\t\tif ( this.menu.element.is(":visible") ) {\n
\t\t\tthis._trigger( "close", event );\n
\t\t\tthis.menu.element.hide();\n
\t\t\tthis.menu.deactivate();\n
\t\t}\n
\t},\n
\t\n
\t_change: function( event ) {\n
\t\tif ( this.previous !== this.element.val() ) {\n
\t\t\tthis._trigger( "change", event, { item: this.selectedItem } );\n
\t\t}\n
\t},\n
\n
\t_normalize: function( items ) {\n
\t\t// assume all items have the right format when the first item is complete\n
\t\tif ( items.length && items[0].label && items[0].value ) {\n
\t\t\treturn items;\n
\t\t}\n
\t\treturn $.map( items, function(item) {\n
\t\t\tif ( typeof item === "string" ) {\n
\t\t\t\treturn {\n
\t\t\t\t\tlabel: item,\n
\t\t\t\t\tvalue: item\n
\t\t\t\t};\n
\t\t\t}\n
\t\t\treturn $.extend({\n
\t\t\t\tlabel: item.label || item.value,\n
\t\t\t\tvalue: item.value || item.label\n
\t\t\t}, item );\n
\t\t});\n
\t},\n
\n
\t_suggest: function( items ) {\n
\t\tvar ul = this.menu.element\n
\t\t\t\t.empty()\n
\t\t\t\t.zIndex( this.element.zIndex() + 1 ),\n
\t\t\tmenuWidth,\n
\t\t\ttextWidth;\n
\t\tthis._renderMenu( ul, items );\n
\t\t// TODO refresh should check if the active item is still in the dom, removing the need for a manual deactivate\n
\t\tthis.menu.deactivate();\n
\t\tthis.menu.refresh();\n
\t\tthis.menu.element.show().position({\n
\t\t\tmy: "left top",\n
\t\t\tat: "left bottom",\n
\t\t\tof: this.element,\n
\t\t\tcollision: "none"\n
\t\t});\n
\n
\t\tmenuWidth = ul.width( "" ).width();\n
\t\ttextWidth = this.element.width();\n
\t\tul.width( Math.max( menuWidth, textWidth ) );\n
\t},\n
\t\n
\t_renderMenu: function( ul, items ) {\n
\t\tvar self = this;\n
\t\t$.each( items, function( index, item ) {\n
\t\t\tself._renderItem( ul, item );\n
\t\t});\n
\t},\n
\n
\t_renderItem: function( ul, item) {\n
\t\treturn $( "<li></li>" )\n
\t\t\t.data( "item.autocomplete", item )\n
\t\t\t.append( "<a>" + item.label + "</a>" )\n
\t\t\t.appendTo( ul );\n
\t},\n
\n
\t_move: function( direction, event ) {\n
\t\tif ( !this.menu.element.is(":visible") ) {\n
\t\t\tthis.search( null, event );\n
\t\t\treturn;\n
\t\t}\n
\t\tif ( this.menu.first() && /^previous/.test(direction) ||\n
\t\t\t\tthis.menu.last() && /^next/.test(direction) ) {\n
\t\t\tthis.element.val( this.term );\n
\t\t\tthis.menu.deactivate();\n
\t\t\treturn;\n
\t\t}\n
\t\tthis.menu[ direction ]( event );\n
\t},\n
\n
\twidget: function() {\n
\t\treturn this.menu.element;\n
\t}\n
});\n
\n
$.extend( $.ui.autocomplete, {\n
\tescapeRegex: function( value ) {\n
\t\treturn value.replace( /([\\^\\$\\(\\)\\[\\]\\{\\}\\*\\.\\+\\?\\|\\\\])/gi, "\\\\$1" );\n
\t},\n
\tfilter: function(array, term) {\n
\t\tvar matcher = new RegExp( $.ui.autocomplete.escapeRegex(term), "i" );\n
\t\treturn $.grep( array, function(value) {\n
\t\t\treturn matcher.test( value.label || value.value || value );\n
\t\t});\n
\t}\n
});\n
\n
}( jQuery ));\n
\n
/*\n
 * jQuery UI Menu (not officially released)\n
 * \n
 * This widget isn\'t yet finished and the API is subject to change. We plan to finish\n
 * it for the next release. You\'re welcome to give it a try anyway and give us feedback,\n
 * as long as you\'re okay with migrating your code later on. We can help with that, too.\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Menu\n
 *\n
 * Depends:\n
 *\tjquery.ui.core.js\n
 *  jquery.ui.widget.js\n
 */\n
(function($) {\n
\n
$.widget("ui.menu", {\n
\t_create: function() {\n
\t\tvar self = this;\n
\t\tthis.element\n
\t\t\t.addClass("ui-menu ui-widget ui-widget-content ui-corner-all")\n
\t\t\t.attr({\n
\t\t\t\trole: "listbox",\n
\t\t\t\t"aria-activedescendant": "ui-active-menuitem"\n
\t\t\t})\n
\t\t\t.click(function( event ) {\n
\t\t\t\tif ( !$( event.target ).closest( ".ui-menu-item a" ).length ) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\t\t\t// temporary\n
\t\t\t\tevent.preventDefault();\n
\t\t\t\tself.select( event );\n
\t\t\t});\n
\t\tthis.refresh();\n
\t},\n
\t\n
\trefresh: function() {\n
\t\tvar self = this;\n
\n
\t\t// don\'t refresh list items that are already adapted\n
\t\tvar items = this.element.children("li:not(.ui-menu-item):has(a)")\n
\t\t\t.addClass("ui-menu-item")\n
\t\t\t.attr("role", "menuitem");\n
\t\t\n
\t\titems.children("a")\n
\t\t\t.addClass("ui-corner-all")\n
\t\t\t.attr("tabindex", -1)\n
\t\t\t// mouseenter doesn\'t work with event delegation\n
\t\t\t.mouseenter(function( event ) {\n
\t\t\t\tself.activate( event, $(this).parent() );\n
\t\t\t})\n
\t\t\t.mouseleave(function() {\n
\t\t\t\tself.deactivate();\n
\t\t\t});\n
\t},\n
\n
\tactivate: function( event, item ) {\n
\t\tthis.deactivate();\n
\t\tif (this.hasScroll()) {\n
\t\t\tvar offset = item.offset().top - this.element.offset().top,\n
\t\t\t\tscroll = this.element.attr("scrollTop"),\n
\t\t\t\telementHeight = this.element.height();\n
\t\t\tif (offset < 0) {\n
\t\t\t\tthis.element.attr("scrollTop", scroll + offset);\n
\t\t\t} else if (offset > elementHeight) {\n
\t\t\t\tthis.element.attr("scrollTop", scroll + offset - elementHeight + item.height());\n
\t\t\t}\n
\t\t}\n
\t\tthis.active = item.eq(0)\n
\t\t\t.children("a")\n
\t\t\t\t.addClass("ui-state-hover")\n
\t\t\t\t.attr("id", "ui-active-menuitem")\n
\t\t\t.end();\n
\t\tthis._trigger("focus", event, { item: item });\n
\t},\n
\n
\tdeactivate: function() {\n
\t\tif (!this.active) { return; }\n
\n
\t\tthis.active.children("a")\n
\t\t\t.removeClass("ui-state-hover")\n
\t\t\t.removeAttr("id");\n
\t\tthis._trigger("blur");\n
\t\tthis.active = null;\n
\t},\n
\n
\tnext: function(event) {\n
\t\tthis.move("next", ".ui-menu-item:first", event);\n
\t},\n
\n
\tprevious: function(event) {\n
\t\tthis.move("prev", ".ui-menu-item:last", event);\n
\t},\n
\n
\tfirst: function() {\n
\t\treturn this.active && !this.active.prev().length;\n
\t},\n
\n
\tlast: function() {\n
\t\treturn this.active && !this.active.next().length;\n
\t},\n
\n
\tmove: function(direction, edge, event) {\n
\t\tif (!this.active) {\n
\t\t\tthis.activate(event, this.element.children(edge));\n
\t\t\treturn;\n
\t\t}\n
\t\tvar next = this.active[direction + "All"](".ui-menu-item").eq(0);\n
\t\tif (next.length) {\n
\t\t\tthis.activate(event, next);\n
\t\t} else {\n
\t\t\tthis.activate(event, this.element.children(edge));\n
\t\t}\n
\t},\n
\n
\t// TODO merge with previousPage\n
\tnextPage: function(event) {\n
\t\tif (this.hasScroll()) {\n
\t\t\t// TODO merge with no-scroll-else\n
\t\t\tif (!this.active || this.last()) {\n
\t\t\t\tthis.activate(event, this.element.children(":first"));\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tvar base = this.active.offset().top,\n
\t\t\t\theight = this.element.height(),\n
\t\t\t\tresult = this.element.children("li").filter(function() {\n
\t\t\t\t\tvar close = $(this).offset().top - base - height + $(this).height();\n
\t\t\t\t\t// TODO improve approximation\n
\t\t\t\t\treturn close < 10 && close > -10;\n
\t\t\t\t});\n
\n
\t\t\t// TODO try to catch this earlier when scrollTop indicates the last page anyway\n
\t\t\tif (!result.length) {\n
\t\t\t\tresult = this.element.children(":last");\n
\t\t\t}\n
\t\t\tthis.activate(event, result);\n
\t\t} else {\n
\t\t\tthis.activate(event, this.element.children(!this.active || this.last() ? ":first" : ":last"));\n
\t\t}\n
\t},\n
\n
\t// TODO merge with nextPage\n
\tpreviousPage: function(event) {\n
\t\tif (this.hasScroll()) {\n
\t\t\t// TODO merge with no-scroll-else\n
\t\t\tif (!this.active || this.first()) {\n
\t\t\t\tthis.activate(event, this.element.children(":last"));\n
\t\t\t\treturn;\n
\t\t\t}\n
\n
\t\t\tvar base = this.active.offset().top,\n
\t\t\t\theight = this.element.height();\n
\t\t\t\tresult = this.element.children("li").filter(function() {\n
\t\t\t\t\tvar close = $(this).offset().top - base + height - $(this).height();\n
\t\t\t\t\t// TODO improve approximation\n
\t\t\t\t\treturn close < 10 && close > -10;\n
\t\t\t\t});\n
\n
\t\t\t// TODO try to catch this earlier when scrollTop indicates the last page anyway\n
\t\t\tif (!result.length) {\n
\t\t\t\tresult = this.element.children(":first");\n
\t\t\t}\n
\t\t\tthis.activate(event, result);\n
\t\t} else {\n
\t\t\tthis.activate(event, this.element.children(!this.active || this.first() ? ":last" : ":first"));\n
\t\t}\n
\t},\n
\n
\thasScroll: function() {\n
\t\treturn this.element.height() < this.element.attr("scrollHeight");\n
\t},\n
\n
\tselect: function( event ) {\n
\t\tthis._trigger("selected", event, { item: this.active });\n
\t}\n
});\n
\n
}(jQuery));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>13627</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
