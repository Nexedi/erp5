<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="File" module="OFS.Image"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts44314535.46</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery-migrate.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
 * jQuery Migrate - v1.1.1 - 2013-02-16\n
 * https://github.com/jquery/jquery-migrate\n
 * Copyright 2005, 2013 jQuery Foundation, Inc. and other contributors; Licensed MIT\n
 */\n
(function( jQuery, window, undefined ) {\n
// See http://bugs.jquery.com/ticket/13335\n
// "use strict";\n
\n
\n
var warnedAbout = {};\n
\n
// List of warnings already given; public read only\n
jQuery.migrateWarnings = [];\n
\n
// Set to true to prevent console output; migrateWarnings still maintained\n
// jQuery.migrateMute = false;\n
\n
// Show a message on the console so devs know we\'re active\n
if ( !jQuery.migrateMute && window.console && console.log ) {\n
\tconsole.log("JQMIGRATE: Logging is active");\n
}\n
\n
// Set to false to disable traces that appear with warnings\n
if ( jQuery.migrateTrace === undefined ) {\n
\tjQuery.migrateTrace = true;\n
}\n
\n
// Forget any warnings we\'ve already given; public\n
jQuery.migrateReset = function() {\n
\twarnedAbout = {};\n
\tjQuery.migrateWarnings.length = 0;\n
};\n
\n
function migrateWarn( msg) {\n
\tif ( !warnedAbout[ msg ] ) {\n
\t\twarnedAbout[ msg ] = true;\n
\t\tjQuery.migrateWarnings.push( msg );\n
\t\tif ( window.console && console.warn && !jQuery.migrateMute ) {\n
\t\t\tconsole.warn( "JQMIGRATE: " + msg );\n
\t\t\tif ( jQuery.migrateTrace && console.trace ) {\n
\t\t\t\tconsole.trace();\n
\t\t\t}\n
\t\t}\n
\t}\n
}\n
\n
function migrateWarnProp( obj, prop, value, msg ) {\n
\tif ( Object.defineProperty ) {\n
\t\t// On ES5 browsers (non-oldIE), warn if the code tries to get prop;\n
\t\t// allow property to be overwritten in case some other plugin wants it\n
\t\ttry {\n
\t\t\tObject.defineProperty( obj, prop, {\n
\t\t\t\tconfigurable: true,\n
\t\t\t\tenumerable: true,\n
\t\t\t\tget: function() {\n
\t\t\t\t\tmigrateWarn( msg );\n
\t\t\t\t\treturn value;\n
\t\t\t\t},\n
\t\t\t\tset: function( newValue ) {\n
\t\t\t\t\tmigrateWarn( msg );\n
\t\t\t\t\tvalue = newValue;\n
\t\t\t\t}\n
\t\t\t});\n
\t\t\treturn;\n
\t\t} catch( err ) {\n
\t\t\t// IE8 is a dope about Object.defineProperty, can\'t warn there\n
\t\t}\n
\t}\n
\n
\t// Non-ES5 (or broken) browser; just set the property\n
\tjQuery._definePropertyBroken = true;\n
\tobj[ prop ] = value;\n
}\n
\n
if ( document.compatMode === "BackCompat" ) {\n
\t// jQuery has never supported or tested Quirks Mode\n
\tmigrateWarn( "jQuery is not compatible with Quirks Mode" );\n
}\n
\n
\n
var attrFn = jQuery( "<input/>", { size: 1 } ).attr("size") && jQuery.attrFn,\n
\toldAttr = jQuery.attr,\n
\tvalueAttrGet = jQuery.attrHooks.value && jQuery.attrHooks.value.get ||\n
\t\tfunction() { return null; },\n
\tvalueAttrSet = jQuery.attrHooks.value && jQuery.attrHooks.value.set ||\n
\t\tfunction() { return undefined; },\n
\trnoType = /^(?:input|button)$/i,\n
\trnoAttrNodeType = /^[238]$/,\n
\trboolean = /^(?:autofocus|autoplay|async|checked|controls|defer|disabled|hidden|loop|multiple|open|readonly|required|scoped|selected)$/i,\n
\truseDefault = /^(?:checked|selected)$/i;\n
\n
// jQuery.attrFn\n
migrateWarnProp( jQuery, "attrFn", attrFn || {}, "jQuery.attrFn is deprecated" );\n
\n
jQuery.attr = function( elem, name, value, pass ) {\n
\tvar lowerName = name.toLowerCase(),\n
\t\tnType = elem && elem.nodeType;\n
\n
\tif ( pass ) {\n
\t\t// Since pass is used internally, we only warn for new jQuery\n
\t\t// versions where there isn\'t a pass arg in the formal params\n
\t\tif ( oldAttr.length < 4 ) {\n
\t\t\tmigrateWarn("jQuery.fn.attr( props, pass ) is deprecated");\n
\t\t}\n
\t\tif ( elem && !rnoAttrNodeType.test( nType ) &&\n
\t\t\t(attrFn ? name in attrFn : jQuery.isFunction(jQuery.fn[name])) ) {\n
\t\t\treturn jQuery( elem )[ name ]( value );\n
\t\t}\n
\t}\n
\n
\t// Warn if user tries to set `type`, since it breaks on IE 6/7/8; by checking\n
\t// for disconnected elements we don\'t warn on $( "<button>", { type: "button" } ).\n
\tif ( name === "type" && value !== undefined && rnoType.test( elem.nodeName ) && elem.parentNode ) {\n
\t\tmigrateWarn("Can\'t change the \'type\' of an input or button in IE 6/7/8");\n
\t}\n
\n
\t// Restore boolHook for boolean property/attribute synchronization\n
\tif ( !jQuery.attrHooks[ lowerName ] && rboolean.test( lowerName ) ) {\n
\t\tjQuery.attrHooks[ lowerName ] = {\n
\t\t\tget: function( elem, name ) {\n
\t\t\t\t// Align boolean attributes with corresponding properties\n
\t\t\t\t// Fall back to attribute presence where some booleans are not supported\n
\t\t\t\tvar attrNode,\n
\t\t\t\t\tproperty = jQuery.prop( elem, name );\n
\t\t\t\treturn property === true || typeof property !== "boolean" &&\n
\t\t\t\t\t( attrNode = elem.getAttributeNode(name) ) && attrNode.nodeValue !== false ?\n
\n
\t\t\t\t\tname.toLowerCase() :\n
\t\t\t\t\tundefined;\n
\t\t\t},\n
\t\t\tset: function( elem, value, name ) {\n
\t\t\t\tvar propName;\n
\t\t\t\tif ( value === false ) {\n
\t\t\t\t\t// Remove boolean attributes when set to false\n
\t\t\t\t\tjQuery.removeAttr( elem, name );\n
\t\t\t\t} else {\n
\t\t\t\t\t// value is true since we know at this point it\'s type boolean and not false\n
\t\t\t\t\t// Set boolean attributes to the same name and set the DOM property\n
\t\t\t\t\tpropName = jQuery.propFix[ name ] || name;\n
\t\t\t\t\tif ( propName in elem ) {\n
\t\t\t\t\t\t// Only set the IDL specifically if it already exists on the element\n
\t\t\t\t\t\telem[ propName ] = true;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\telem.setAttribute( name, name.toLowerCase() );\n
\t\t\t\t}\n
\t\t\t\treturn name;\n
\t\t\t}\n
\t\t};\n
\n
\t\t// Warn only for attributes that can remain distinct from their properties post-1.9\n
\t\tif ( ruseDefault.test( lowerName ) ) {\n
\t\t\tmigrateWarn( "jQuery.fn.attr(\'" + lowerName + "\') may use property instead of attribute" );\n
\t\t}\n
\t}\n
\n
\treturn oldAttr.call( jQuery, elem, name, value );\n
};\n
\n
// attrHooks: value\n
jQuery.attrHooks.value = {\n
\tget: function( elem, name ) {\n
\t\tvar nodeName = ( elem.nodeName || "" ).toLowerCase();\n
\t\tif ( nodeName === "button" ) {\n
\t\t\treturn valueAttrGet.apply( this, arguments );\n
\t\t}\n
\t\tif ( nodeName !== "input" && nodeName !== "option" ) {\n
\t\t\tmigrateWarn("jQuery.fn.attr(\'value\') no longer gets properties");\n
\t\t}\n
\t\treturn name in elem ?\n
\t\t\telem.value :\n
\t\t\tnull;\n
\t},\n
\tset: function( elem, value ) {\n
\t\tvar nodeName = ( elem.nodeName || "" ).toLowerCase();\n
\t\tif ( nodeName === "button" ) {\n
\t\t\treturn valueAttrSet.apply( this, arguments );\n
\t\t}\n
\t\tif ( nodeName !== "input" && nodeName !== "option" ) {\n
\t\t\tmigrateWarn("jQuery.fn.attr(\'value\', val) no longer sets properties");\n
\t\t}\n
\t\t// Does not return so that setAttribute is also used\n
\t\telem.value = value;\n
\t}\n
};\n
\n
\n
var matched, browser,\n
\toldInit = jQuery.fn.init,\n
\toldParseJSON = jQuery.parseJSON,\n
\t// Note this does NOT include the #9521 XSS fix from 1.7!\n
\trquickExpr = /^(?:[^<]*(<[\\w\\W]+>)[^>]*|#([\\w\\-]*))$/;\n
\n
// $(html) "looks like html" rule change\n
jQuery.fn.init = function( selector, context, rootjQuery ) {\n
\tvar match;\n
\n
\tif ( selector && typeof selector === "string" && !jQuery.isPlainObject( context ) &&\n
\t\t\t(match = rquickExpr.exec( selector )) && match[1] ) {\n
\t\t// This is an HTML string according to the "old" rules; is it still?\n
\t\tif ( selector.charAt( 0 ) !== "<" ) {\n
\t\t\tmigrateWarn("$(html) HTML strings must start with \'<\' character");\n
\t\t}\n
\t\t// Now process using loose rules; let pre-1.8 play too\n
\t\tif ( context && context.context ) {\n
\t\t\t// jQuery object as context; parseHTML expects a DOM object\n
\t\t\tcontext = context.context;\n
\t\t}\n
\t\tif ( jQuery.parseHTML ) {\n
\t\t\treturn oldInit.call( this, jQuery.parseHTML( jQuery.trim(selector), context, true ),\n
\t\t\t\t\tcontext, rootjQuery );\n
\t\t}\n
\t}\n
\treturn oldInit.apply( this, arguments );\n
};\n
jQuery.fn.init.prototype = jQuery.fn;\n
\n
// Let $.parseJSON(falsy_value) return null\n
jQuery.parseJSON = function( json ) {\n
\tif ( !json && json !== null ) {\n
\t\tmigrateWarn("jQuery.parseJSON requires a valid JSON string");\n
\t\treturn null;\n
\t}\n
\treturn oldParseJSON.apply( this, arguments );\n
};\n
\n
jQuery.uaMatch = function( ua ) {\n
\tua = ua.toLowerCase();\n
\n
\tvar match = /(chrome)[ \\/]([\\w.]+)/.exec( ua ) ||\n
\t\t/(webkit)[ \\/]([\\w.]+)/.exec( ua ) ||\n
\t\t/(opera)(?:.*version|)[ \\/]([\\w.]+)/.exec( ua ) ||\n
\t\t/(msie) ([\\w.]+)/.exec( ua ) ||\n
\t\tua.indexOf("compatible") < 0 && /(mozilla)(?:.*? rv:([\\w.]+)|)/.exec( ua ) ||\n
\t\t[];\n
\n
\treturn {\n
\t\tbrowser: match[ 1 ] || "",\n
\t\tversion: match[ 2 ] || "0"\n
\t};\n
};\n
\n
// Don\'t clobber any existing jQuery.browser in case it\'s different\n
if ( !jQuery.browser ) {\n
\tmatched = jQuery.uaMatch( navigator.userAgent );\n
\tbrowser = {};\n
\n
\tif ( matched.browser ) {\n
\t\tbrowser[ matched.browser ] = true;\n
\t\tbrowser.version = matched.version;\n
\t}\n
\n
\t// Chrome is Webkit, but Webkit is also Safari.\n
\tif ( browser.chrome ) {\n
\t\tbrowser.webkit = true;\n
\t} else if ( browser.webkit ) {\n
\t\tbrowser.safari = true;\n
\t}\n
\n
\tjQuery.browser = browser;\n
}\n
\n
// Warn if the code tries to get jQuery.browser\n
migrateWarnProp( jQuery, "browser", jQuery.browser, "jQuery.browser is deprecated" );\n
\n
jQuery.sub = function() {\n
\tfunction jQuerySub( selector, context ) {\n
\t\treturn new jQuerySub.fn.init( selector, context );\n
\t}\n
\tjQuery.extend( true, jQuerySub, this );\n
\tjQuerySub.superclass = this;\n
\tjQuerySub.fn = jQuerySub.prototype = this();\n
\tjQuerySub.fn.constructor = jQuerySub;\n
\tjQuerySub.sub = this.sub;\n
\tjQuerySub.fn.init = function init( selector, context ) {\n
\t\tif ( context && context instanceof jQuery && !(context instanceof jQuerySub) ) {\n
\t\t\tcontext = jQuerySub( context );\n
\t\t}\n
\n
\t\treturn jQuery.fn.init.call( this, selector, context, rootjQuerySub );\n
\t};\n
\tjQuerySub.fn.init.prototype = jQuerySub.fn;\n
\tvar rootjQuerySub = jQuerySub(document);\n
\tmigrateWarn( "jQuery.sub() is deprecated" );\n
\treturn jQuerySub;\n
};\n
\n
\n
// Ensure that $.ajax gets the new parseJSON defined in core.js\n
jQuery.ajaxSetup({\n
\tconverters: {\n
\t\t"text json": jQuery.parseJSON\n
\t}\n
});\n
\n
\n
var oldFnData = jQuery.fn.data;\n
\n
jQuery.fn.data = function( name ) {\n
\tvar ret, evt,\n
\t\telem = this[0];\n
\n
\t// Handles 1.7 which has this behavior and 1.8 which doesn\'t\n
\tif ( elem && name === "events" && arguments.length === 1 ) {\n
\t\tret = jQuery.data( elem, name );\n
\t\tevt = jQuery._data( elem, name );\n
\t\tif ( ( ret === undefined || ret === evt ) && evt !== undefined ) {\n
\t\t\tmigrateWarn("Use of jQuery.fn.data(\'events\') is deprecated");\n
\t\t\treturn evt;\n
\t\t}\n
\t}\n
\treturn oldFnData.apply( this, arguments );\n
};\n
\n
\n
var rscriptType = /\\/(java|ecma)script/i,\n
\toldSelf = jQuery.fn.andSelf || jQuery.fn.addBack;\n
\n
jQuery.fn.andSelf = function() {\n
\tmigrateWarn("jQuery.fn.andSelf() replaced by jQuery.fn.addBack()");\n
\treturn oldSelf.apply( this, arguments );\n
};\n
\n
// Since jQuery.clean is used internally on older versions, we only shim if it\'s missing\n
if ( !jQuery.clean ) {\n
\tjQuery.clean = function( elems, context, fragment, scripts ) {\n
\t\t// Set context per 1.8 logic\n
\t\tcontext = context || document;\n
\t\tcontext = !context.nodeType && context[0] || context;\n
\t\tcontext = context.ownerDocument || context;\n
\n
\t\tmigrateWarn("jQuery.clean() is deprecated");\n
\n
\t\tvar i, elem, handleScript, jsTags,\n
\t\t\tret = [];\n
\n
\t\tjQuery.merge( ret, jQuery.buildFragment( elems, context ).childNodes );\n
\n
\t\t// Complex logic lifted directly from jQuery 1.8\n
\t\tif ( fragment ) {\n
\t\t\t// Special handling of each script element\n
\t\t\thandleScript = function( elem ) {\n
\t\t\t\t// Check if we consider it executable\n
\t\t\t\tif ( !elem.type || rscriptType.test( elem.type ) ) {\n
\t\t\t\t\t// Detach the script and store it in the scripts array (if provided) or the fragment\n
\t\t\t\t\t// Return truthy to indicate that it has been handled\n
\t\t\t\t\treturn scripts ?\n
\t\t\t\t\t\tscripts.push( elem.parentNode ? elem.parentNode.removeChild( elem ) : elem ) :\n
\t\t\t\t\t\tfragment.appendChild( elem );\n
\t\t\t\t}\n
\t\t\t};\n
\n
\t\t\tfor ( i = 0; (elem = ret[i]) != null; i++ ) {\n
\t\t\t\t// Check if we\'re done after handling an executable script\n
\t\t\t\tif ( !( jQuery.nodeName( elem, "script" ) && handleScript( elem ) ) ) {\n
\t\t\t\t\t// Append to fragment and handle embedded scripts\n
\t\t\t\t\tfragment.appendChild( elem );\n
\t\t\t\t\tif ( typeof elem.getElementsByTagName !== "undefined" ) {\n
\t\t\t\t\t\t// handleScript alters the DOM, so use jQuery.merge to ensure snapshot iteration\n
\t\t\t\t\t\tjsTags = jQuery.grep( jQuery.merge( [], elem.getElementsByTagName("script") ), handleScript );\n
\n
\t\t\t\t\t\t// Splice the scripts into ret after their former ancestor and advance our index beyond them\n
\t\t\t\t\t\tret.splice.apply( ret, [i + 1, 0].concat( jsTags ) );\n
\t\t\t\t\t\ti += jsTags.length;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn ret;\n
\t};\n
}\n
\n
var eventAdd = jQuery.event.add,\n
\teventRemove = jQuery.event.remove,\n
\teventTrigger = jQuery.event.trigger,\n
\toldToggle = jQuery.fn.toggle,\n
\toldLive = jQuery.fn.live,\n
\toldDie = jQuery.fn.die,\n
\tajaxEvents = "ajaxStart|ajaxStop|ajaxSend|ajaxComplete|ajaxError|ajaxSuccess",\n
\trajaxEvent = new RegExp( "\\\\b(?:" + ajaxEvents + ")\\\\b" ),\n
\trhoverHack = /(?:^|\\s)hover(\\.\\S+|)\\b/,\n
\thoverHack = function( events ) {\n
\t\tif ( typeof( events ) !== "string" || jQuery.event.special.hover ) {\n
\t\t\treturn events;\n
\t\t}\n
\t\tif ( rhoverHack.test( events ) ) {\n
\t\t\tmigrateWarn("\'hover\' pseudo-event is deprecated, use \'mouseenter mouseleave\'");\n
\t\t}\n
\t\treturn events && events.replace( rhoverHack, "mouseenter$1 mouseleave$1" );\n
\t};\n
\n
// Event props removed in 1.9, put them back if needed; no practical way to warn them\n
if ( jQuery.event.props && jQuery.event.props[ 0 ] !== "attrChange" ) {\n
\tjQuery.event.props.unshift( "attrChange", "attrName", "relatedNode", "srcElement" );\n
}\n
\n
// Undocumented jQuery.event.handle was "deprecated" in jQuery 1.7\n
if ( jQuery.event.dispatch ) {\n
\tmigrateWarnProp( jQuery.event, "handle", jQuery.event.dispatch, "jQuery.event.handle is undocumented and deprecated" );\n
}\n
\n
// Support for \'hover\' pseudo-event and ajax event warnings\n
jQuery.event.add = function( elem, types, handler, data, selector ){\n
\tif ( elem !== document && rajaxEvent.test( types ) ) {\n
\t\tmigrateWarn( "AJAX events should be attached to document: " + types );\n
\t}\n
\teventAdd.call( this, elem, hoverHack( types || "" ), handler, data, selector );\n
};\n
jQuery.event.remove = function( elem, types, handler, selector, mappedTypes ){\n
\teventRemove.call( this, elem, hoverHack( types ) || "", handler, selector, mappedTypes );\n
};\n
\n
jQuery.fn.error = function() {\n
\tvar args = Array.prototype.slice.call( arguments, 0);\n
\tmigrateWarn("jQuery.fn.error() is deprecated");\n
\targs.splice( 0, 0, "error" );\n
\tif ( arguments.length ) {\n
\t\treturn this.bind.apply( this, args );\n
\t}\n
\t// error event should not bubble to window, although it does pre-1.7\n
\tthis.triggerHandler.apply( this, args );\n
\treturn this;\n
};\n
\n
jQuery.fn.toggle = function( fn, fn2 ) {\n
\n
\t// Don\'t mess with animation or css toggles\n
\tif ( !jQuery.isFunction( fn ) || !jQuery.isFunction( fn2 ) ) {\n
\t\treturn oldToggle.apply( this, arguments );\n
\t}\n
\tmigrateWarn("jQuery.fn.toggle(handler, handler...) is deprecated");\n
\n
\t// Save reference to arguments for access in closure\n
\tvar args = arguments,\n
\t\tguid = fn.guid || jQuery.guid++,\n
\t\ti = 0,\n
\t\ttoggler = function( event ) {\n
\t\t\t// Figure out which function to execute\n
\t\t\tvar lastToggle = ( jQuery._data( this, "lastToggle" + fn.guid ) || 0 ) % i;\n
\t\t\tjQuery._data( this, "lastToggle" + fn.guid, lastToggle + 1 );\n
\n
\t\t\t// Make sure that clicks stop\n
\t\t\tevent.preventDefault();\n
\n
\t\t\t// and execute the function\n
\t\t\treturn args[ lastToggle ].apply( this, arguments ) || false;\n
\t\t};\n
\n
\t// link all the functions, so any of them can unbind this click handler\n
\ttoggler.guid = guid;\n
\twhile ( i < args.length ) {\n
\t\targs[ i++ ].guid = guid;\n
\t}\n
\n
\treturn this.click( toggler );\n
};\n
\n
jQuery.fn.live = function( types, data, fn ) {\n
\tmigrateWarn("jQuery.fn.live() is deprecated");\n
\tif ( oldLive ) {\n
\t\treturn oldLive.apply( this, arguments );\n
\t}\n
\tjQuery( this.context ).on( types, this.selector, data, fn );\n
\treturn this;\n
};\n
\n
jQuery.fn.die = function( types, fn ) {\n
\tmigrateWarn("jQuery.fn.die() is deprecated");\n
\tif ( oldDie ) {\n
\t\treturn oldDie.apply( this, arguments );\n
\t}\n
\tjQuery( this.context ).off( types, this.selector || "**", fn );\n
\treturn this;\n
};\n
\n
// Turn global events into document-triggered events\n
jQuery.event.trigger = function( event, data, elem, onlyHandlers  ){\n
\tif ( !elem && !rajaxEvent.test( event ) ) {\n
\t\tmigrateWarn( "Global events are undocumented and deprecated" );\n
\t}\n
\treturn eventTrigger.call( this,  event, data, elem || document, onlyHandlers  );\n
};\n
jQuery.each( ajaxEvents.split("|"),\n
\tfunction( _, name ) {\n
\t\tjQuery.event.special[ name ] = {\n
\t\t\tsetup: function() {\n
\t\t\t\tvar elem = this;\n
\n
\t\t\t\t// The document needs no shimming; must be !== for oldIE\n
\t\t\t\tif ( elem !== document ) {\n
\t\t\t\t\tjQuery.event.add( document, name + "." + jQuery.guid, function() {\n
\t\t\t\t\t\tjQuery.event.trigger( name, null, elem, true );\n
\t\t\t\t\t});\n
\t\t\t\t\tjQuery._data( this, name, jQuery.guid++ );\n
\t\t\t\t}\n
\t\t\t\treturn false;\n
\t\t\t},\n
\t\t\tteardown: function() {\n
\t\t\t\tif ( this !== document ) {\n
\t\t\t\t\tjQuery.event.remove( document, name + "." + jQuery._data( this, name ) );\n
\t\t\t\t}\n
\t\t\t\treturn false;\n
\t\t\t}\n
\t\t};\n
\t}\n
);\n
\n
\n
})( jQuery, window );\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>16178</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
