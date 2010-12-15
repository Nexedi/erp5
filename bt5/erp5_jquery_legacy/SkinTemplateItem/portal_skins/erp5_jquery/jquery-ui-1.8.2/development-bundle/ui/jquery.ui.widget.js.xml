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
            <value> <string>ts77895656.36</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.widget.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
 * jQuery UI Widget 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Widget\n
 */\n
(function( $ ) {\n
\n
var _remove = $.fn.remove;\n
\n
$.fn.remove = function( selector, keepData ) {\n
\treturn this.each(function() {\n
\t\tif ( !keepData ) {\n
\t\t\tif ( !selector || $.filter( selector, [ this ] ).length ) {\n
\t\t\t\t$( "*", this ).add( this ).each(function() {\n
\t\t\t\t\t$( this ).triggerHandler( "remove" );\n
\t\t\t\t});\n
\t\t\t}\n
\t\t}\n
\t\treturn _remove.call( $(this), selector, keepData );\n
\t});\n
};\n
\n
$.widget = function( name, base, prototype ) {\n
\tvar namespace = name.split( "." )[ 0 ],\n
\t\tfullName;\n
\tname = name.split( "." )[ 1 ];\n
\tfullName = namespace + "-" + name;\n
\n
\tif ( !prototype ) {\n
\t\tprototype = base;\n
\t\tbase = $.Widget;\n
\t}\n
\n
\t// create selector for plugin\n
\t$.expr[ ":" ][ fullName ] = function( elem ) {\n
\t\treturn !!$.data( elem, name );\n
\t};\n
\n
\t$[ namespace ] = $[ namespace ] || {};\n
\t$[ namespace ][ name ] = function( options, element ) {\n
\t\t// allow instantiation without initializing for simple inheritance\n
\t\tif ( arguments.length ) {\n
\t\t\tthis._createWidget( options, element );\n
\t\t}\n
\t};\n
\n
\tvar basePrototype = new base();\n
\t// we need to make the options hash a property directly on the new instance\n
\t// otherwise we\'ll modify the options hash on the prototype that we\'re\n
\t// inheriting from\n
//\t$.each( basePrototype, function( key, val ) {\n
//\t\tif ( $.isPlainObject(val) ) {\n
//\t\t\tbasePrototype[ key ] = $.extend( {}, val );\n
//\t\t}\n
//\t});\n
\tbasePrototype.options = $.extend( {}, basePrototype.options );\n
\t$[ namespace ][ name ].prototype = $.extend( true, basePrototype, {\n
\t\tnamespace: namespace,\n
\t\twidgetName: name,\n
\t\twidgetEventPrefix: $[ namespace ][ name ].prototype.widgetEventPrefix || name,\n
\t\twidgetBaseClass: fullName\n
\t}, prototype );\n
\n
\t$.widget.bridge( name, $[ namespace ][ name ] );\n
};\n
\n
$.widget.bridge = function( name, object ) {\n
\t$.fn[ name ] = function( options ) {\n
\t\tvar isMethodCall = typeof options === "string",\n
\t\t\targs = Array.prototype.slice.call( arguments, 1 ),\n
\t\t\treturnValue = this;\n
\n
\t\t// allow multiple hashes to be passed on init\n
\t\toptions = !isMethodCall && args.length ?\n
\t\t\t$.extend.apply( null, [ true, options ].concat(args) ) :\n
\t\t\toptions;\n
\n
\t\t// prevent calls to internal methods\n
\t\tif ( isMethodCall && options.substring( 0, 1 ) === "_" ) {\n
\t\t\treturn returnValue;\n
\t\t}\n
\n
\t\tif ( isMethodCall ) {\n
\t\t\tthis.each(function() {\n
\t\t\t\tvar instance = $.data( this, name ),\n
\t\t\t\t\tmethodValue = instance && $.isFunction( instance[options] ) ?\n
\t\t\t\t\t\tinstance[ options ].apply( instance, args ) :\n
\t\t\t\t\t\tinstance;\n
\t\t\t\tif ( methodValue !== instance && methodValue !== undefined ) {\n
\t\t\t\t\treturnValue = methodValue;\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\t\t\t});\n
\t\t} else {\n
\t\t\tthis.each(function() {\n
\t\t\t\tvar instance = $.data( this, name );\n
\t\t\t\tif ( instance ) {\n
\t\t\t\t\tif ( options ) {\n
\t\t\t\t\t\tinstance.option( options );\n
\t\t\t\t\t}\n
\t\t\t\t\tinstance._init();\n
\t\t\t\t} else {\n
\t\t\t\t\t$.data( this, name, new object( options, this ) );\n
\t\t\t\t}\n
\t\t\t});\n
\t\t}\n
\n
\t\treturn returnValue;\n
\t};\n
};\n
\n
$.Widget = function( options, element ) {\n
\t// allow instantiation without initializing for simple inheritance\n
\tif ( arguments.length ) {\n
\t\tthis._createWidget( options, element );\n
\t}\n
};\n
\n
$.Widget.prototype = {\n
\twidgetName: "widget",\n
\twidgetEventPrefix: "",\n
\toptions: {\n
\t\tdisabled: false\n
\t},\n
\t_createWidget: function( options, element ) {\n
\t\t// $.widget.bridge stores the plugin instance, but we do it anyway\n
\t\t// so that it\'s stored even before the _create function runs\n
\t\tthis.element = $( element ).data( this.widgetName, this );\n
\t\tthis.options = $.extend( true, {},\n
\t\t\tthis.options,\n
\t\t\t$.metadata && $.metadata.get( element )[ this.widgetName ],\n
\t\t\toptions );\n
\n
\t\tvar self = this;\n
\t\tthis.element.bind( "remove." + this.widgetName, function() {\n
\t\t\tself.destroy();\n
\t\t});\n
\n
\t\tthis._create();\n
\t\tthis._init();\n
\t},\n
\t_create: function() {},\n
\t_init: function() {},\n
\n
\tdestroy: function() {\n
\t\tthis.element\n
\t\t\t.unbind( "." + this.widgetName )\n
\t\t\t.removeData( this.widgetName );\n
\t\tthis.widget()\n
\t\t\t.unbind( "." + this.widgetName )\n
\t\t\t.removeAttr( "aria-disabled" )\n
\t\t\t.removeClass(\n
\t\t\t\tthis.widgetBaseClass + "-disabled " +\n
\t\t\t\t"ui-state-disabled" );\n
\t},\n
\n
\twidget: function() {\n
\t\treturn this.element;\n
\t},\n
\n
\toption: function( key, value ) {\n
\t\tvar options = key,\n
\t\t\tself = this;\n
\n
\t\tif ( arguments.length === 0 ) {\n
\t\t\t// don\'t return a reference to the internal hash\n
\t\t\treturn $.extend( {}, self.options );\n
\t\t}\n
\n
\t\tif  (typeof key === "string" ) {\n
\t\t\tif ( value === undefined ) {\n
\t\t\t\treturn this.options[ key ];\n
\t\t\t}\n
\t\t\toptions = {};\n
\t\t\toptions[ key ] = value;\n
\t\t}\n
\n
\t\t$.each( options, function( key, value ) {\n
\t\t\tself._setOption( key, value );\n
\t\t});\n
\n
\t\treturn self;\n
\t},\n
\t_setOption: function( key, value ) {\n
\t\tthis.options[ key ] = value;\n
\n
\t\tif ( key === "disabled" ) {\n
\t\t\tthis.widget()\n
\t\t\t\t[ value ? "addClass" : "removeClass"](\n
\t\t\t\t\tthis.widgetBaseClass + "-disabled" + " " +\n
\t\t\t\t\t"ui-state-disabled" )\n
\t\t\t\t.attr( "aria-disabled", value );\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\n
\tenable: function() {\n
\t\treturn this._setOption( "disabled", false );\n
\t},\n
\tdisable: function() {\n
\t\treturn this._setOption( "disabled", true );\n
\t},\n
\n
\t_trigger: function( type, event, data ) {\n
\t\tvar callback = this.options[ type ];\n
\n
\t\tevent = $.Event( event );\n
\t\tevent.type = ( type === this.widgetEventPrefix ?\n
\t\t\ttype :\n
\t\t\tthis.widgetEventPrefix + type ).toLowerCase();\n
\t\tdata = data || {};\n
\n
\t\t// copy original event properties over to the new event\n
\t\t// this would happen if we could call $.event.fix instead of $.Event\n
\t\t// but we don\'t have a way to force an event to be fixed multiple times\n
\t\tif ( event.originalEvent ) {\n
\t\t\tfor ( var i = $.event.props.length, prop; i; ) {\n
\t\t\t\tprop = $.event.props[ --i ];\n
\t\t\t\tevent[ prop ] = event.originalEvent[ prop ];\n
\t\t\t}\n
\t\t}\n
\n
\t\tthis.element.trigger( event, data );\n
\n
\t\treturn !( $.isFunction(callback) &&\n
\t\t\tcallback.call( this.element[0], event, data ) === false ||\n
\t\t\tevent.isDefaultPrevented() );\n
\t}\n
};\n
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
            <value> <int>5983</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
