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
            <value> <string>ts74199327.37</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery-1.4.2.js</string> </value>
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
            <value> <int>163907</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
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

/*!\n
 * jQuery JavaScript Library v1.4.2\n
 * http://jquery.com/\n
 *\n
 * Copyright 2010, John Resig\n
 * Dual licensed under the MIT or GPL Version 2 licenses.\n
 * http://jquery.org/license\n
 *\n
 * Includes Sizzle.js\n
 * http://sizzlejs.com/\n
 * Copyright 2010, The Dojo Foundation\n
 * Released under the MIT, BSD, and GPL Licenses.\n
 *\n
 * Date: Sat Feb 13 22:33:48 2010 -0500\n
 */\n
(function( window, undefined ) {\n
\n
// Define a local copy of jQuery\n
var jQuery = function( selector, context ) {\n
\t\t// The jQuery object is actually just the init constructor \'enhanced\'\n
\t\treturn new jQuery.fn.init( selector, context );\n
\t},\n
\n
\t// Map over jQuery in case of overwrite\n
\t_jQuery = window.jQuery,\n
\n
\t// Map over the $ in case of overwrite\n
\t_$ = window.$,\n
\n
\t// Use the correct document accordingly with window argument (sandbox)\n
\tdocument = window.document,\n
\n
\t// A central reference to the root jQuery(document)\n
\trootjQuery,\n
\n
\t// A simple way to check for HTML strings or ID strings\n
\t// (both of which we optimize for)\n
\tquickExpr = /^[^<]*(<[\\w\\W]+>)[^>]*$|^#([\\w-]+)$/,\n
\n
\t// Is it a simple selector\n
\tisSimple = /^.[^:#\\[\\.,]*$/,\n
\n
\t// Check if a string has a non-whitespace character in it\n
\trnotwhite = /\\S/,\n
\n
\t// Used for trimming whitespace\n
\trtrim = /^(\\s|\\u00A0)+|(\\s|\\u00A0)+$/g,\n
\n
\t// Match a standalone tag\n
\trsingleTag = /^<(\\w+)\\s*\\/?>(?:<\\/\\1>)?$/,\n
\n
\t// Keep a UserAgent string for use with jQuery.browser\n
\tuserAgent = navigator.userAgent,\n
\n
\t// For matching the engine and version of the browser\n
\tbrowserMatch,\n
\t\n
\t// Has the ready events already been bound?\n
\treadyBound = false,\n
\t\n
\t// The functions to execute on DOM ready\n
\treadyList = [],\n
\n
\t// The ready event handler\n
\tDOMContentLoaded,\n
\n
\t// Save a reference to some core methods\n
\ttoString = Object.prototype.toString,\n
\thasOwnProperty = Object.prototype.hasOwnProperty,\n
\tpush = Array.prototype.push,\n
\tslice = Array.prototype.slice,\n
\tindexOf = Array.prototype.indexOf;\n
\n
jQuery.fn = jQuery.prototype = {\n
\tinit: function( selector, context ) {\n
\t\tvar match, elem, ret, doc;\n
\n
\t\t// Handle $(""), $(null), or $(undefined)\n
\t\tif ( !selector ) {\n
\t\t\treturn this;\n
\t\t}\n
\n
\t\t// Handle $(DOMElement)\n
\t\tif ( selector.nodeType ) {\n
\t\t\tthis.context = this[0] = selector;\n
\t\t\tthis.length = 1;\n
\t\t\treturn this;\n
\t\t}\n
\t\t\n
\t\t// The body element only exists once, optimize finding it\n
\t\tif ( selector === "body" && !context ) {\n
\t\t\tthis.context = document;\n
\t\t\tthis[0] = document.body;\n
\t\t\tthis.selector = "body";\n
\t\t\tthis.length = 1;\n
\t\t\treturn this;\n
\t\t}\n
\n
\t\t// Handle HTML strings\n
\t\tif ( typeof selector === "string" ) {\n
\t\t\t// Are we dealing with HTML string or an ID?\n
\t\t\tmatch = quickExpr.exec( selector );\n
\n
\t\t\t// Verify a match, and that no context was specified for #id\n
\t\t\tif ( match && (match[1] || !context) ) {\n
\n
\t\t\t\t// HANDLE: $(html) -> $(array)\n
\t\t\t\tif ( match[1] ) {\n
\t\t\t\t\tdoc = (context ? context.ownerDocument || context : document);\n
\n
\t\t\t\t\t// If a single string is passed in and it\'s a single tag\n
\t\t\t\t\t// just do a createElement and skip the rest\n
\t\t\t\t\tret = rsingleTag.exec( selector );\n
\n
\t\t\t\t\tif ( ret ) {\n
\t\t\t\t\t\tif ( jQuery.isPlainObject( context ) ) {\n
\t\t\t\t\t\t\tselector = [ document.createElement( ret[1] ) ];\n
\t\t\t\t\t\t\tjQuery.fn.attr.call( selector, context, true );\n
\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tselector = [ doc.createElement( ret[1] ) ];\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tret = buildFragment( [ match[1] ], [ doc ] );\n
\t\t\t\t\t\tselector = (ret.cacheable ? ret.fragment.cloneNode(true) : ret.fragment).childNodes;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\treturn jQuery.merge( this, selector );\n
\t\t\t\t\t\n
\t\t\t\t// HANDLE: $("#id")\n
\t\t\t\t} else {\n
\t\t\t\t\telem = document.getElementById( match[2] );\n
\n
\t\t\t\t\tif ( elem ) {\n
\t\t\t\t\t\t// Handle the case where IE and Opera return items\n
\t\t\t\t\t\t// by name instead of ID\n
\t\t\t\t\t\tif ( elem.id !== match[2] ) {\n
\t\t\t\t\t\t\treturn rootjQuery.find( selector );\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// Otherwise, we inject the element directly into the jQuery object\n
\t\t\t\t\t\tthis.length = 1;\n
\t\t\t\t\t\tthis[0] = elem;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tthis.context = document;\n
\t\t\t\t\tthis.selector = selector;\n
\t\t\t\t\treturn this;\n
\t\t\t\t}\n
\n
\t\t\t// HANDLE: $("TAG")\n
\t\t\t} else if ( !context && /^\\w+$/.test( selector ) ) {\n
\t\t\t\tthis.selector = selector;\n
\t\t\t\tthis.context = document;\n
\t\t\t\tselector = document.getElementsByTagName( selector );\n
\t\t\t\treturn jQuery.merge( this, selector );\n
\n
\t\t\t// HANDLE: $(expr, $(...))\n
\t\t\t} else if ( !context || context.jquery ) {\n
\t\t\t\treturn (context || rootjQuery).find( selector );\n
\n
\t\t\t// HANDLE: $(expr, context)\n
\t\t\t// (which is just equivalent to: $(context).find(expr)\n
\t\t\t} else {\n
\t\t\t\treturn jQuery( context ).find( selector );\n
\t\t\t}\n
\n
\t\t// HANDLE: $(function)\n
\t\t// Shortcut for document ready\n
\t\t} else if ( jQuery.isFunction( selector ) ) {\n
\t\t\treturn rootjQuery.ready( selector );\n
\t\t}\n
\n
\t\tif (selector.selector !== undefined) {\n
\t\t\tthis.selector = selector.selector;\n
\t\t\tthis.context = selector.context;\n
\t\t}\n
\n
\t\treturn jQuery.makeArray( selector, this );\n
\t},\n
\n
\t// Start with an empty selector\n
\tselector: "",\n
\n
\t// The current version of jQuery being used\n
\tjquery: "1.4.2",\n
\n
\t// The default length of a jQuery object is 0\n
\tlength: 0,\n
\n
\t// The number of elements contained in the matched element set\n
\tsize: function() {\n
\t\treturn this.length;\n
\t},\n
\n
\ttoArray: function() {\n
\t\treturn slice.call( this, 0 );\n
\t},\n
\n
\t// Get the Nth element in the matched element set OR\n
\t// Get the whole matched element set as a clean array\n
\tget: function( num ) {\n
\t\treturn num == null ?\n
\n
\t\t\t// Return a \'clean\' array\n
\t\t\tthis.toArray() :\n
\n
\t\t\t// Return just the object\n
\t\t\t( num < 0 ? this.slice(num)[ 0 ] : this[ num ] );\n
\t},\n
\n
\t// Take an array of elements and push it onto the stack\n
\t// (returning the new matched element set)\n
\tpushStack: function( elems, name, selector ) {\n
\t\t// Build a new jQuery matched element set\n
\t\tvar ret = jQuery();\n
\n
\t\tif ( jQuery.isArray( elems ) ) {\n
\t\t\tpush.apply( ret, elems );\n
\t\t\n
\t\t} else {\n
\t\t\tjQuery.merge( ret, elems );\n
\t\t}\n
\n
\t\t// Add the old object onto the stack (as a reference)\n
\t\tret.prevObject = this;\n
\n
\t\tret.context = this.context;\n
\n
\t\tif ( name === "find" ) {\n
\t\t\tret.selector = this.selector + (this.selector ? " " : "") + selector;\n
\t\t} else if ( name ) {\n
\t\t\tret.selector = this.selector + "." + name + "(" + selector + ")";\n
\t\t}\n
\n
\t\t// Return the newly-formed element set\n
\t\treturn ret;\n
\t},\n
\n
\t// Execute a callback for every element in the matched set.\n
\t// (You can seed the arguments with an array of args, but this is\n
\t// only used internally.)\n
\teach: function( callback, args ) {\n
\t\treturn jQuery.each( this, callback, args );\n
\t},\n
\t\n
\tready: function( fn ) {\n
\t\t// Attach the listeners\n
\t\tjQuery.bindReady();\n
\n
\t\t// If the DOM is already ready\n
\t\tif ( jQuery.isReady ) {\n
\t\t\t// Execute the function immediately\n
\t\t\tfn.call( document, jQuery );\n
\n
\t\t// Otherwise, remember the function for later\n
\t\t} else if ( readyList ) {\n
\t\t\t// Add the function to the wait list\n
\t\t\treadyList.push( fn );\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\t\n
\teq: function( i ) {\n
\t\treturn i === -1 ?\n
\t\t\tthis.slice( i ) :\n
\t\t\tthis.slice( i, +i + 1 );\n
\t},\n
\n
\tfirst: function() {\n
\t\treturn this.eq( 0 );\n
\t},\n
\n
\tlast: function() {\n
\t\treturn this.eq( -1 );\n
\t},\n
\n
\tslice: function() {\n
\t\treturn this.pushStack( slice.apply( this, arguments ),\n
\t\t\t"slice", slice.call(arguments).join(",") );\n
\t},\n
\n
\tmap: function( callback ) {\n
\t\treturn this.pushStack( jQuery.map(this, function( elem, i ) {\n
\t\t\treturn callback.call( elem, i, elem );\n
\t\t}));\n
\t},\n
\t\n
\tend: function() {\n
\t\treturn this.prevObject || jQuery(null);\n
\t},\n
\n
\t// For internal use only.\n
\t// Behaves like an Array\'s method, not like a jQuery method.\n
\tpush: push,\n
\tsort: [].sort,\n
\tsplice: [].splice\n
};\n
\n
// Give the init function the jQuery prototype for later instantiation\n
jQuery.fn.init.prototype = jQuery.fn;\n
\n
jQuery.extend = jQuery.fn.extend = function() {\n
\t// copy reference to target object\n
\tvar target = arguments[0] || {}, i = 1, length = arguments.length, deep = false, options, name, src, copy;\n
\n
\t// Handle a deep copy situation\n
\tif ( typeof target === "boolean" ) {\n
\t\tdeep = target;\n
\t\ttarget = arguments[1] || {};\n
\t\t// skip the boolean and the target\n
\t\ti = 2;\n
\t}\n
\n
\t// Handle case when target is a string or something (possible in deep copy)\n
\tif ( typeof target !== "object" && !jQuery.isFunction(target) ) {\n
\t\ttarget = {};\n
\t}\n
\n
\t// extend jQuery itself if only one argument is passed\n
\tif ( length === i ) {\n
\t\ttarget = this;\n
\t\t--i;\n
\t}\n
\n
\tfor ( ; i < length; i++ ) {\n
\t\t// Only deal with non-null/undefined values\n
\t\tif ( (options = arguments[ i ]) != null ) {\n
\t\t\t// Extend the base object\n
\t\t\tfor ( name in options ) {\n
\t\t\t\tsrc = target[ name ];\n
\t\t\t\tcopy = options[ name ];\n
\n
\t\t\t\t// Prevent never-ending loop\n
\t\t\t\tif ( target === copy ) {\n
\t\t\t\t\tcontinue;\n
\t\t\t\t}\n
\n
\t\t\t\t// Recurse if we\'re merging object literal values or arrays\n
\t\t\t\tif ( deep && copy && ( jQuery.isPlainObject(copy) || jQuery.isArray(copy) ) ) {\n
\t\t\t\t\tvar clone = src && ( jQuery.isPlainObject(src) || jQuery.isArray(src) ) ? src\n
\t\t\t\t\t\t: jQuery.isArray(copy) ? [] : {};\n
\n
\t\t\t\t\t// Never move original objects, clone them\n
\t\t\t\t\ttarget[ name ] = jQuery.extend( deep, clone, copy );\n
\n
\t\t\t\t// Don\'t bring in undefined values\n
\t\t\t\t} else if ( copy !== undefined ) {\n
\t\t\t\t\ttarget[ name ] = copy;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\t// Return the modified object\n
\treturn target;\n
};\n
\n
jQuery.extend({\n
\tnoConflict: function( deep ) {\n
\t\twindow.$ = _$;\n
\n
\t\tif ( deep ) {\n
\t\t\twindow.jQuery = _jQuery;\n
\t\t}\n
\n
\t\treturn jQuery;\n
\t},\n
\t\n
\t// Is the DOM ready to be used? Set to true once it occurs.\n
\tisReady: false,\n
\t\n
\t// Handle when the DOM is ready\n
\tready: function() {\n
\t\t// Make sure that the DOM is not already loaded\n
\t\tif ( !jQuery.isReady ) {\n
\t\t\t// Make sure body exists, at least, in case IE gets a little overzealous (ticket #5443).\n
\t\t\tif ( !document.body ) {\n
\t\t\t\treturn setTimeout( jQuery.ready, 13 );\n
\t\t\t}\n
\n
\t\t\t// Remember that the DOM is ready\n
\t\t\tjQuery.isReady = true;\n
\n
\t\t\t// If there are functions bound, to execute\n
\t\t\tif ( readyList ) {\n
\t\t\t\t// Execute all of them\n
\t\t\t\tvar fn, i = 0;\n
\t\t\t\twhile ( (fn = readyList[ i++ ]) ) {\n
\t\t\t\t\tfn.call( document, jQuery );\n
\t\t\t\t}\n
\n
\t\t\t\t// Reset the list of functions\n
\t\t\t\treadyList = null;\n
\t\t\t}\n
\n
\t\t\t// Trigger any bound ready events\n
\t\t\tif ( jQuery.fn.triggerHandler ) {\n
\t\t\t\tjQuery( document ).triggerHandler( "ready" );\n
\t\t\t}\n
\t\t}\n
\t},\n
\t\n
\tbindReady: function() {\n
\t\tif ( readyBound ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\treadyBound = true;\n
\n
\t\t// Catch cases where $(document).ready() is called after the\n
\t\t// browser event has already occurred.\n
\t\tif ( document.readyState === "complete" ) {\n
\t\t\treturn jQuery.ready();\n
\t\t}\n
\n
\t\t// Mozilla, Opera and webkit nightlies currently support this event\n
\t\tif ( document.addEventListener ) {\n
\t\t\t// Use the handy event callback\n
\t\t\tdocument.addEventListener( "DOMContentLoaded", DOMContentLoaded, false );\n
\t\t\t\n
\t\t\t// A fallback to window.onload, that will always work\n
\t\t\twindow.addEventListener( "load", jQuery.ready, false );\n
\n
\t\t// If IE event model is used\n
\t\t} else if ( document.attachEvent ) {\n
\t\t\t// ensure firing before onload,\n
\t\t\t// maybe late but safe also for iframes\n
\t\t\tdocument.attachEvent("onreadystatechange", DOMContentLoaded);\n
\t\t\t\n
\t\t\t// A fallback to window.onload, that will always work\n
\t\t\twindow.attachEvent( "onload", jQuery.ready );\n
\n
\t\t\t// If IE and not a frame\n
\t\t\t// continually check to see if the document is ready\n
\t\t\tvar toplevel = false;\n
\n
\t\t\ttry {\n
\t\t\t\ttoplevel = window.frameElement == null;\n
\t\t\t} catch(e) {}\n
\n
\t\t\tif ( document.documentElement.doScroll && toplevel ) {\n
\t\t\t\tdoScrollCheck();\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\t// See test/unit/core.js for details concerning isFunction.\n
\t// Since version 1.3, DOM methods and functions like alert\n
\t// aren\'t supported. They return false on IE (#2968).\n
\tisFunction: function( obj ) {\n
\t\treturn toString.call(obj) === "[object Function]";\n
\t},\n
\n
\tisArray: function( obj ) {\n
\t\treturn toString.call(obj) === "[object Array]";\n
\t},\n
\n
\tisPlainObject: function( obj ) {\n
\t\t// Must be an Object.\n
\t\t// Because of IE, we also have to check the presence of the constructor property.\n
\t\t// Make sure that DOM nodes and window objects don\'t pass through, as well\n
\t\tif ( !obj || toString.call(obj) !== "[object Object]" || obj.nodeType || obj.setInterval ) {\n
\t\t\treturn false;\n
\t\t}\n
\t\t\n
\t\t// Not own constructor property must be Object\n
\t\tif ( obj.constructor\n
\t\t\t&& !hasOwnProperty.call(obj, "constructor")\n
\t\t\t&& !hasOwnProperty.call(obj.constructor.prototype, "isPrototypeOf") ) {\n
\t\t\treturn false;\n
\t\t}\n
\t\t\n
\t\t// Own properties are enumerated firstly, so to speed up,\n
\t\t// if last one is own, then all properties are own.\n
\t\n
\t\tvar key;\n
\t\tfor ( key in obj ) {}\n
\t\t\n
\t\treturn key === undefined || hasOwnProperty.call( obj, key );\n
\t},\n
\n
\tisEmptyObject: function( obj ) {\n
\t\tfor ( var name in obj ) {\n
\t\t\treturn false;\n
\t\t}\n
\t\treturn true;\n
\t},\n
\t\n
\terror: function( msg ) {\n
\t\tthrow msg;\n
\t},\n
\t\n
\tparseJSON: function( data ) {\n
\t\tif ( typeof data !== "string" || !data ) {\n
\t\t\treturn null;\n
\t\t}\n
\n
\t\t// Make sure leading/trailing whitespace is removed (IE can\'t handle it)\n
\t\tdata = jQuery.trim( data );\n
\t\t\n
\t\t// Make sure the incoming data is actual JSON\n
\t\t// Logic borrowed from http://json.org/json2.js\n
\t\tif ( /^[\\],:{}\\s]*$/.test(data.replace(/\\\\(?:["\\\\\\/bfnrt]|u[0-9a-fA-F]{4})/g, "@")\n
\t\t\t.replace(/"[^"\\\\\\n\\r]*"|true|false|null|-?\\d+(?:\\.\\d*)?(?:[eE][+\\-]?\\d+)?/g, "]")\n
\t\t\t.replace(/(?:^|:|,)(?:\\s*\\[)+/g, "")) ) {\n
\n
\t\t\t// Try to use the native JSON parser first\n
\t\t\treturn window.JSON && window.JSON.parse ?\n
\t\t\t\twindow.JSON.parse( data ) :\n
\t\t\t\t(new Function("return " + data))();\n
\n
\t\t} else {\n
\t\t\tjQuery.error( "Invalid JSON: " + data );\n
\t\t}\n
\t},\n
\n
\tnoop: function() {},\n
\n
\t// Evalulates a script in a global context\n
\tglobalEval: function( data ) {\n
\t\tif ( data && rnotwhite.test(data) ) {\n
\t\t\t// Inspired by code by Andrea Giammarchi\n
\t\t\t// http://webreflection.blogspot.com/2007/08/global-scope-evaluation-and-dom.html\n
\t\t\tvar head = document.getElementsByTagName("head")[0] || document.documentElement,\n
\t\t\t\tscript = document.createElement("script");\n
\n
\t\t\tscript.type = "text/javascript";\n
\n
\t\t\tif ( jQuery.support.scriptEval ) {\n
\t\t\t\tscript.appendChild( document.createTextNode( data ) );\n
\t\t\t} else {\n
\t\t\t\tscript.text = data;\n
\t\t\t}\n
\n
\t\t\t// Use insertBefore instead of appendChild to circumvent an IE6 bug.\n
\t\t\t// This arises when a base node is used (#2709).\n
\t\t\thead.insertBefore( script, head.firstChild );\n
\t\t\thead.removeChild( script );\n
\t\t}\n
\t},\n
\n
\tnodeName: function( elem, name ) {\n
\t\treturn elem.nodeName && elem.nodeName.toUpperCase() === name.toUpperCase();\n
\t},\n
\n
\t// args is for internal usage only\n
\teach: function( object, callback, args ) {\n
\t\tvar name, i = 0,\n
\t\t\tlength = object.length,\n
\t\t\tisObj = length === undefined || jQuery.isFunction(object);\n
\n
\t\tif ( args ) {\n
\t\t\tif ( isObj ) {\n
\t\t\t\tfor ( name in object ) {\n
\t\t\t\t\tif ( callback.apply( object[ name ], args ) === false ) {\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tfor ( ; i < length; ) {\n
\t\t\t\t\tif ( callback.apply( object[ i++ ], args ) === false ) {\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t// A special, fast, case for the most common use of each\n
\t\t} else {\n
\t\t\tif ( isObj ) {\n
\t\t\t\tfor ( name in object ) {\n
\t\t\t\t\tif ( callback.call( object[ name ], name, object[ name ] ) === false ) {\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tfor ( var value = object[0];\n
\t\t\t\t\ti < length && callback.call( value, i, value ) !== false; value = object[++i] ) {}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn object;\n
\t},\n
\n
\ttrim: function( text ) {\n
\t\treturn (text || "").replace( rtrim, "" );\n
\t},\n
\n
\t// results is for internal usage only\n
\tmakeArray: function( array, results ) {\n
\t\tvar ret = results || [];\n
\n
\t\tif ( array != null ) {\n
\t\t\t// The window, strings (and functions) also have \'length\'\n
\t\t\t// The extra typeof function check is to prevent crashes\n
\t\t\t// in Safari 2 (See: #3039)\n
\t\t\tif ( array.length == null || typeof array === "string" || jQuery.isFunction(array) || (typeof array !== "function" && array.setInterval) ) {\n
\t\t\t\tpush.call( ret, array );\n
\t\t\t} else {\n
\t\t\t\tjQuery.merge( ret, array );\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn ret;\n
\t},\n
\n
\tinArray: function( elem, array ) {\n
\t\tif ( array.indexOf ) {\n
\t\t\treturn array.indexOf( elem );\n
\t\t}\n
\n
\t\tfor ( var i = 0, length = array.length; i < length; i++ ) {\n
\t\t\tif ( array[ i ] === elem ) {\n
\t\t\t\treturn i;\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn -1;\n
\t},\n
\n
\tmerge: function( first, second ) {\n
\t\tvar i = first.length, j = 0;\n
\n
\t\tif ( typeof second.length === "number" ) {\n
\t\t\tfor ( var l = second.length; j < l; j++ ) {\n
\t\t\t\tfirst[ i++ ] = second[ j ];\n
\t\t\t}\n
\t\t\n
\t\t} else {\n
\t\t\twhile ( second[j] !== undefined ) {\n
\t\t\t\tfirst[ i++ ] = second[ j++ ];\n
\t\t\t}\n
\t\t}\n
\n
\t\tfirst.length = i;\n
\n
\t\treturn first;\n
\t},\n
\n
\tgrep: function( elems, callback, inv ) {\n
\t\tvar ret = [];\n
\n
\t\t// Go through the array, only saving the items\n
\t\t// that pass the validator function\n
\t\tfor ( var i = 0, length = elems.length; i < length; i++ ) {\n
\t\t\tif ( !inv !== !callback( elems[ i ], i ) ) {\n
\t\t\t\tret.push( elems[ i ] );\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn ret;\n
\t},\n
\n
\t// arg is for internal usage only\n
\tmap: function( elems, callback, arg ) {\n
\t\tvar ret = [], value;\n
\n
\t\t// Go through the array, translating each of the items to their\n
\t\t// new value (or values).\n
\t\tfor ( var i = 0, length = elems.length; i < length; i++ ) {\n
\t\t\tvalue = callback( elems[ i ], i, arg );\n
\n
\t\t\tif ( value != null ) {\n
\t\t\t\tret[ ret.length ] = value;\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn ret.concat.apply( [], ret );\n
\t},\n
\n
\t// A global GUID counter for objects\n
\tguid: 1,\n
\n
\tproxy: function( fn, proxy, thisObject ) {\n
\t\tif ( arguments.length === 2 ) {\n
\t\t\tif ( typeof proxy === "string" ) {\n
\t\t\t\tthisObject = fn;\n
\t\t\t\tfn = thisObject[ proxy ];\n
\t\t\t\tproxy = undefined;\n
\n
\t\t\t} else if ( proxy && !jQuery.isFunction( proxy ) ) {\n
\t\t\t\tthisObject = proxy;\n
\t\t\t\tproxy = undefined;\n
\t\t\t}\n
\t\t}\n
\n
\t\tif ( !proxy && fn ) {\n
\t\t\tproxy = function() {\n
\t\t\t\treturn fn.apply( thisObject || this, arguments );\n
\t\t\t};\n
\t\t}\n
\n
\t\t// Set the guid of unique handler to the same of original handler, so it can be removed\n
\t\tif ( fn ) {\n
\t\t\tproxy.guid = fn.guid = fn.guid || proxy.guid || jQuery.guid++;\n
\t\t}\n
\n
\t\t// So proxy can be declared as an argument\n
\t\treturn proxy;\n
\t},\n
\n
\t// Use of jQuery.browser is frowned upon.\n
\t// More details: http://docs.jquery.com/Utilities/jQuery.browser\n
\tuaMatch: function( ua ) {\n
\t\tua = ua.toLowerCase();\n
\n
\t\tvar match = /(webkit)[ \\/]([\\w.]+)/.exec( ua ) ||\n
\t\t\t/(opera)(?:.*version)?[ \\/]([\\w.]+)/.exec( ua ) ||\n
\t\t\t/(msie) ([\\w.]+)/.exec( ua ) ||\n
\t\t\t!/compatible/.test( ua ) && /(mozilla)(?:.*? rv:([\\w.]+))?/.exec( ua ) ||\n
\t\t  \t[];\n
\n
\t\treturn { browser: match[1] || "", version: match[2] || "0" };\n
\t},\n
\n
\tbrowser: {}\n
});\n
\n
browserMatch = jQuery.uaMatch( userAgent );\n
if ( browserMatch.browser ) {\n
\tjQuery.browser[ browserMatch.browser ] = true;\n
\tjQuery.browser.version = browserMatch.version;\n
}\n
\n
// Deprecated, use jQuery.browser.webkit instead\n
if ( jQuery.browser.webkit ) {\n
\tjQuery.browser.safari = true;\n
}\n
\n
if ( indexOf ) {\n
\tjQuery.inArray = function( elem, array ) {\n
\t\treturn indexOf.call( array, elem );\n
\t};\n
}\n
\n
// All jQuery objects should point back to these\n
rootjQuery = jQuery(document);\n
\n
// Cleanup functions for the document ready method\n
if ( document.addEventListener ) {\n
\tDOMContentLoaded = function() {\n
\t\tdocument.removeEventListener( "DOMContentLoaded", DOMContentLoaded, false );\n
\t\tjQuery.ready();\n
\t};\n
\n
} else if ( document.attachEvent ) {\n
\tDOMContentLoaded = function() {\n
\t\t// Make sure body exists, at least, in case IE gets a little overzealous (ticket #5443).\n
\t\tif ( document.readyState === "complete" ) {\n
\t\t\tdocument.detachEvent( "onreadystatechange", DOMContentLoaded );\n
\t\t\tjQuery.ready();\n
\t\t}\n
\t};\n
}\n
\n
// The DOM ready check for Internet Explorer\n
function doScrollCheck() {\n
\tif ( jQuery.isReady ) {\n
\t\treturn;\n
\t}\n
\n
\ttry {\n
\t\t// If IE is used, use the trick by Diego Perini\n
\t\t// http://javascript.nwbox.com/IEContentLoaded/\n
\t\tdocument.documentElement.doScroll("left");\n
\t} catch( error ) {\n
\t\tsetTimeout( doScrollCheck, 1 );\n
\t\treturn;\n
\t}\n
\n
\t// and execute any waiting functions\n
\tjQuery.ready();\n
}\n
\n
function evalScript( i, elem ) {\n
\tif ( elem.src ) {\n
\t\tjQuery.ajax({\n
\t\t\turl: elem.src,\n
\t\t\tasync: false,\n
\t\t\tdataType: "script"\n
\t\t});\n
\t} else {\n
\t\tjQuery.globalEval( elem.text || elem.textContent || elem.innerHTML || "" );\n
\t}\n
\n
\tif ( elem.parentNode ) {\n
\t\telem.parentNode.removeChild( elem );\n
\t}\n
}\n
\n
// Mutifunctional method to get and set values to a collection\n
// The value/s can be optionally by executed if its a function\n
function access( elems, key, value, exec, fn, pass ) {\n
\tvar length = elems.length;\n
\t\n
\t// Setting many attributes\n
\tif ( typeof key === "object" ) {\n
\t\tfor ( var k in key ) {\n
\t\t\taccess( elems, k, key[k], exec, fn, value );\n
\t\t}\n
\t\treturn elems;\n
\t}\n
\t\n
\t// Setting one attribute\n
\tif ( value !== undefined ) {\n
\t\t// Optionally, function values get executed if exec is true\n
\t\texec = !pass && exec && jQuery.isFunction(value);\n
\t\t\n
\t\tfor ( var i = 0; i < length; i++ ) {\n
\t\t\tfn( elems[i], key, exec ? value.call( elems[i], i, fn( elems[i], key ) ) : value, pass );\n
\t\t}\n
\t\t\n
\t\treturn elems;\n
\t}\n
\t\n
\t// Getting an attribute\n
\treturn length ? fn( elems[0], key ) : undefined;\n
}\n
\n
function now() {\n
\treturn (new Date).getTime();\n
}\n
(function() {\n
\n
\tjQuery.support = {};\n
\n
\tvar root = document.documentElement,\n
\t\tscript = document.createElement("script"),\n
\t\tdiv = document.createElement("div"),\n
\t\tid = "script" + now();\n
\n
\tdiv.style.display = "none";\n
\tdiv.innerHTML = "   <link/><table></table><a href=\'/a\' style=\'color:red;float:left;opacity:.55;\'>a</a><input type=\'checkbox\'/>";\n
\n
\tvar all = div.getElementsByTagName("*"),\n
\t\ta = div.getElementsByTagName("a")[0];\n
\n
\t// Can\'t get basic test support\n
\tif ( !all || !all.length || !a ) {\n
\t\treturn;\n
\t}\n
\n
\tjQuery.support = {\n
\t\t// IE strips leading whitespace when .innerHTML is used\n
\t\tleadingWhitespace: div.firstChild.nodeType === 3,\n
\n
\t\t// Make sure that tbody elements aren\'t automatically inserted\n
\t\t// IE will insert them into empty tables\n
\t\ttbody: !div.getElementsByTagName("tbody").length,\n
\n
\t\t// Make sure that link elements get serialized correctly by innerHTML\n
\t\t// This requires a wrapper element in IE\n
\t\thtmlSerialize: !!div.getElementsByTagName("link").length,\n
\n
\t\t// Get the style information from getAttribute\n
\t\t// (IE uses .cssText insted)\n
\t\tstyle: /red/.test( a.getAttribute("style") ),\n
\n
\t\t// Make sure that URLs aren\'t manipulated\n
\t\t// (IE normalizes it by default)\n
\t\threfNormalized: a.getAttribute("href") === "/a",\n
\n
\t\t// Make sure that element opacity exists\n
\t\t// (IE uses filter instead)\n
\t\t// Use a regex to work around a WebKit issue. See #5145\n
\t\topacity: /^0.55$/.test( a.style.opacity ),\n
\n
\t\t// Verify style float existence\n
\t\t// (IE uses styleFloat instead of cssFloat)\n
\t\tcssFloat: !!a.style.cssFloat,\n
\n
\t\t// Make sure that if no value is specified for a checkbox\n
\t\t// that it defaults to "on".\n
\t\t// (WebKit defaults to "" instead)\n
\t\tcheckOn: div.getElementsByTagName("input")[0].value === "on",\n
\n
\t\t// Make sure that a selected-by-default option has a working selected property.\n
\t\t// (WebKit defaults to false instead of true, IE too, if it\'s in an optgroup)\n
\t\toptSelected: document.createElement("select").appendChild( document.createElement("option") ).selected,\n
\n
\t\tparentNode: div.removeChild( div.appendChild( document.createElement("div") ) ).parentNode === null,\n
\n
\t\t// Will be defined later\n
\t\tdeleteExpando: true,\n
\t\tcheckClone: false,\n
\t\tscriptEval: false,\n
\t\tnoCloneEvent: true,\n
\t\tboxModel: null\n
\t};\n
\n
\tscript.type = "text/javascript";\n
\ttry {\n
\t\tscript.appendChild( document.createTextNode( "window." + id + "=1;" ) );\n
\t} catch(e) {}\n
\n
\troot.insertBefore( script, root.firstChild );\n
\n
\t// Make sure that the execution of code works by injecting a script\n
\t// tag with appendChild/createTextNode\n
\t// (IE doesn\'t support this, fails, and uses .text instead)\n
\tif ( window[ id ] ) {\n
\t\tjQuery.support.scriptEval = true;\n
\t\tdelete window[ id ];\n
\t}\n
\n
\t// Test to see if it\'s possible to delete an expando from an element\n
\t// Fails in Internet Explorer\n
\ttry {\n
\t\tdelete script.test;\n
\t\n
\t} catch(e) {\n
\t\tjQuery.support.deleteExpando = false;\n
\t}\n
\n
\troot.removeChild( script );\n
\n
\tif ( div.attachEvent && div.fireEvent ) {\n
\t\tdiv.attachEvent("onclick", function click() {\n
\t\t\t// Cloning a node shouldn\'t copy over any\n
\t\t\t// bound event handlers (IE does this)\n
\t\t\tjQuery.support.noCloneEvent = false;\n
\t\t\tdiv.detachEvent("onclick", click);\n
\t\t});\n
\t\tdiv.cloneNode(true).fireEvent("onclick");\n
\t}\n
\n
\tdiv = document.createElement("div");\n
\tdiv.innerHTML = "<input type=\'radio\' name=\'radiotest\' checked=\'checked\'/>";\n
\n
\tvar fragment = document.createDocumentFragment();\n
\tfragment.appendChild( div.firstChild );\n
\n
\t// WebKit doesn\'t clone checked state correctly in fragments\n
\tjQuery.support.checkClone = fragment.cloneNode(true).cloneNode(true).lastChild.checked;\n
\n
\t// Figure out if the W3C box model works as expected\n
\t// document.body must exist before we can do this\n
\tjQuery(function() {\n
\t\tvar div = document.createElement("div");\n
\t\tdiv.style.width = div.style.paddingLeft = "1px";\n
\n
\t\tdocument.body.appendChild( div );\n
\t\tjQuery.boxModel = jQuery.support.boxModel = div.offsetWidth === 2;\n
\t\tdocument.body.removeChild( div ).style.display = \'none\';\n
\n
\t\tdiv = null;\n
\t});\n
\n
\t// Technique from Juriy Zaytsev\n
\t// http://thinkweb2.com/projects/prototype/detecting-event-support-without-browser-sniffing/\n
\tvar eventSupported = function( eventName ) { \n
\t\tvar el = document.createElement("div"); \n
\t\teventName = "on" + eventName; \n
\n
\t\tvar isSupported = (eventName in el); \n
\t\tif ( !isSupported ) { \n
\t\t\tel.setAttribute(eventName, "return;"); \n
\t\t\tisSupported = typeof el[eventName] === "function"; \n
\t\t} \n
\t\tel = null; \n
\n
\t\treturn isSupported; \n
\t};\n
\t\n
\tjQuery.support.submitBubbles = eventSupported("submit");\n
\tjQuery.support.changeBubbles = eventSupported("change");\n
\n
\t// release memory in IE\n
\troot = script = div = all = a = null;\n
})();\n
\n
jQuery.props = {\n
\t"for": "htmlFor",\n
\t"class": "className",\n
\treadonly: "readOnly",\n
\tmaxlength: "maxLength",\n
\tcellspacing: "cellSpacing",\n
\trowspan: "rowSpan",\n
\tcolspan: "colSpan",\n
\ttabindex: "tabIndex",\n
\tusemap: "useMap",\n
\tframeborder: "frameBorder"\n
};\n
var expando = "jQuery" + now(), uuid = 0, windowData = {};\n
\n
jQuery.extend({\n
\tcache: {},\n
\t\n
\texpando:expando,\n
\n
\t// The following elements throw uncatchable exceptions if you\n
\t// attempt to add expando properties to them.\n
\tnoData: {\n
\t\t"embed": true,\n
\t\t"object": true,\n
\t\t"applet": true\n
\t},\n
\n
\tdata: function( elem, name, data ) {\n
\t\tif ( elem.nodeName && jQuery.noData[elem.nodeName.toLowerCase()] ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\telem = elem == window ?\n
\t\t\twindowData :\n
\t\t\telem;\n
\n
\t\tvar id = elem[ expando ], cache = jQuery.cache, thisCache;\n
\n
\t\tif ( !id && typeof name === "string" && data === undefined ) {\n
\t\t\treturn null;\n
\t\t}\n
\n
\t\t// Compute a unique ID for the element\n
\t\tif ( !id ) { \n
\t\t\tid = ++uuid;\n
\t\t}\n
\n
\t\t// Avoid generating a new cache unless none exists and we\n
\t\t// want to manipulate it.\n
\t\tif ( typeof name === "object" ) {\n
\t\t\telem[ expando ] = id;\n
\t\t\tthisCache = cache[ id ] = jQuery.extend(true, {}, name);\n
\n
\t\t} else if ( !cache[ id ] ) {\n
\t\t\telem[ expando ] = id;\n
\t\t\tcache[ id ] = {};\n
\t\t}\n
\n
\t\tthisCache = cache[ id ];\n
\n
\t\t// Prevent overriding the named cache with undefined values\n
\t\tif ( data !== undefined ) {\n
\t\t\tthisCache[ name ] = data;\n
\t\t}\n
\n
\t\treturn typeof name === "string" ? thisCache[ name ] : thisCache;\n
\t},\n
\n
\tremoveData: function( elem, name ) {\n
\t\tif ( elem.nodeName && jQuery.noData[elem.nodeName.toLowerCase()] ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\telem = elem == window ?\n
\t\t\twindowData :\n
\t\t\telem;\n
\n
\t\tvar id = elem[ expando ], cache = jQuery.cache, thisCache = cache[ id ];\n
\n
\t\t// If we want to remove a specific section of the element\'s data\n
\t\tif ( name ) {\n
\t\t\tif ( thisCache ) {\n
\t\t\t\t// Remove the section of cache data\n
\t\t\t\tdelete thisCache[ name ];\n
\n
\t\t\t\t// If we\'ve removed all the data, remove the element\'s cache\n
\t\t\t\tif ( jQuery.isEmptyObject(thisCache) ) {\n
\t\t\t\t\tjQuery.removeData( elem );\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t// Otherwise, we want to remove all of the element\'s data\n
\t\t} else {\n
\t\t\tif ( jQuery.support.deleteExpando ) {\n
\t\t\t\tdelete elem[ jQuery.expando ];\n
\n
\t\t\t} else if ( elem.removeAttribute ) {\n
\t\t\t\telem.removeAttribute( jQuery.expando );\n
\t\t\t}\n
\n
\t\t\t// Completely remove the data cache\n
\t\t\tdelete cache[ id ];\n
\t\t}\n
\t}\n
});\n
\n
jQuery.fn.extend({\n
\tdata: function( key, value ) {\n
\t\tif ( typeof key === "undefined" && this.length ) {\n
\t\t\treturn jQuery.data( this[0] );\n
\n
\t\t} else if ( typeof key === "object" ) {\n
\t\t\treturn this.each(function() {\n
\t\t\t\tjQuery.data( this, key );\n
\t\t\t});\n
\t\t}\n
\n
\t\tvar parts = key.split(".");\n
\t\tparts[1] = parts[1] ? "." + parts[1] : "";\n
\n
\t\tif ( value === undefined ) {\n
\t\t\tvar data = this.triggerHandler("getData" + parts[1] + "!", [parts[0]]);\n
\n
\t\t\tif ( data === undefined && this.length ) {\n
\t\t\t\tdata = jQuery.data( this[0], key );\n
\t\t\t}\n
\t\t\treturn data === undefined && parts[1] ?\n
\t\t\t\tthis.data( parts[0] ) :\n
\t\t\t\tdata;\n
\t\t} else {\n
\t\t\treturn this.trigger("setData" + parts[1] + "!", [parts[0], value]).each(function() {\n
\t\t\t\tjQuery.data( this, key, value );\n
\t\t\t});\n
\t\t}\n
\t},\n
\n
\tremoveData: function( key ) {\n
\t\treturn this.each(function() {\n
\t\t\tjQuery.removeData( this, key );\n
\t\t});\n
\t}\n
});\n
jQuery.extend({\n
\tqueue: function( elem, type, data ) {\n
\t\tif ( !elem ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\ttype = (type || "fx") + "queue";\n
\t\tvar q = jQuery.data( elem, type );\n
\n
\t\t// Speed up dequeue by getting out quickly if this is just a lookup\n
\t\tif ( !data ) {\n
\t\t\treturn q || [];\n
\t\t}\n
\n
\t\tif ( !q || jQuery.isArray(data) ) {\n
\t\t\tq = jQuery.data( elem, type, jQuery.makeArray(data) );\n
\n
\t\t} else {\n
\t\t\tq.push( data );\n
\t\t}\n
\n
\t\treturn q;\n
\t},\n
\n
\tdequeue: function( elem, type ) {\n
\t\ttype = type || "fx";\n
\n
\t\tvar queue = jQuery.queue( elem, type ), fn = queue.shift();\n
\n
\t\t// If the fx queue is dequeued, always remove the progress sentinel\n
\t\tif ( fn === "inprogress" ) {\n
\t\t\tfn = queue.shift();\n
\t\t}\n
\n
\t\tif ( fn ) {\n
\t\t\t// Add a progress sentinel to prevent the fx queue from being\n
\t\t\t// automatically dequeued\n
\t\t\tif ( type === "fx" ) {\n
\t\t\t\tqueue.unshift("inprogress");\n
\t\t\t}\n
\n
\t\t\tfn.call(elem, function() {\n
\t\t\t\tjQuery.dequeue(elem, type);\n
\t\t\t});\n
\t\t}\n
\t}\n
});\n
\n
jQuery.fn.extend({\n
\tqueue: function( type, data ) {\n
\t\tif ( typeof type !== "string" ) {\n
\t\t\tdata = type;\n
\t\t\ttype = "fx";\n
\t\t}\n
\n
\t\tif ( data === undefined ) {\n
\t\t\treturn jQuery.queue( this[0], type );\n
\t\t}\n
\t\treturn this.each(function( i, elem ) {\n
\t\t\tvar queue = jQuery.queue( this, type, data );\n
\n
\t\t\tif ( type === "fx" && queue[0] !== "inprogress" ) {\n
\t\t\t\tjQuery.dequeue( this, type );\n
\t\t\t}\n
\t\t});\n
\t},\n
\tdequeue: function( type ) {\n
\t\treturn this.each(function() {\n
\t\t\tjQuery.dequeue( this, type );\n
\t\t});\n
\t},\n
\n
\t// Based off of the plugin by Clint Helfers, with permission.\n
\t// http://blindsignals.com/index.php/2009/07/jquery-delay/\n
\tdelay: function( time, type ) {\n
\t\ttime = jQuery.fx ? jQuery.fx.speeds[time] || time : time;\n
\t\ttype = type || "fx";\n
\n
\t\treturn this.queue( type, function() {\n
\t\t\tvar elem = this;\n
\t\t\tsetTimeout(function() {\n
\t\t\t\tjQuery.dequeue( elem, type );\n
\t\t\t}, time );\n
\t\t});\n
\t},\n
\n
\tclearQueue: function( type ) {\n
\t\treturn this.queue( type || "fx", [] );\n
\t}\n
});\n
var rclass = /[\\n\\t]/g,\n
\trspace = /\\s+/,\n
\trreturn = /\\r/g,\n
\trspecialurl = /href|src|style/,\n
\trtype = /(button|input)/i,\n
\trfocusable = /(button|input|object|select|textarea)/i,\n
\trclickable = /^(a|area)$/i,\n
\trradiocheck = /radio|checkbox/;\n
\n
jQuery.fn.extend({\n
\tattr: function( name, value ) {\n
\t\treturn access( this, name, value, true, jQuery.attr );\n
\t},\n
\n
\tremoveAttr: function( name, fn ) {\n
\t\treturn this.each(function(){\n
\t\t\tjQuery.attr( this, name, "" );\n
\t\t\tif ( this.nodeType === 1 ) {\n
\t\t\t\tthis.removeAttribute( name );\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\taddClass: function( value ) {\n
\t\tif ( jQuery.isFunction(value) ) {\n
\t\t\treturn this.each(function(i) {\n
\t\t\t\tvar self = jQuery(this);\n
\t\t\t\tself.addClass( value.call(this, i, self.attr("class")) );\n
\t\t\t});\n
\t\t}\n
\n
\t\tif ( value && typeof value === "string" ) {\n
\t\t\tvar classNames = (value || "").split( rspace );\n
\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\t\tvar elem = this[i];\n
\n
\t\t\t\tif ( elem.nodeType === 1 ) {\n
\t\t\t\t\tif ( !elem.className ) {\n
\t\t\t\t\t\telem.className = value;\n
\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tvar className = " " + elem.className + " ", setClass = elem.className;\n
\t\t\t\t\t\tfor ( var c = 0, cl = classNames.length; c < cl; c++ ) {\n
\t\t\t\t\t\t\tif ( className.indexOf( " " + classNames[c] + " " ) < 0 ) {\n
\t\t\t\t\t\t\t\tsetClass += " " + classNames[c];\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telem.className = jQuery.trim( setClass );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\n
\tremoveClass: function( value ) {\n
\t\tif ( jQuery.isFunction(value) ) {\n
\t\t\treturn this.each(function(i) {\n
\t\t\t\tvar self = jQuery(this);\n
\t\t\t\tself.removeClass( value.call(this, i, self.attr("class")) );\n
\t\t\t});\n
\t\t}\n
\n
\t\tif ( (value && typeof value === "string") || value === undefined ) {\n
\t\t\tvar classNames = (value || "").split(rspace);\n
\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\t\tvar elem = this[i];\n
\n
\t\t\t\tif ( elem.nodeType === 1 && elem.className ) {\n
\t\t\t\t\tif ( value ) {\n
\t\t\t\t\t\tvar className = (" " + elem.className + " ").replace(rclass, " ");\n
\t\t\t\t\t\tfor ( var c = 0, cl = classNames.length; c < cl; c++ ) {\n
\t\t\t\t\t\t\tclassName = className.replace(" " + classNames[c] + " ", " ");\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\telem.className = jQuery.trim( className );\n
\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\telem.className = "";\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\n
\ttoggleClass: function( value, stateVal ) {\n
\t\tvar type = typeof value, isBool = typeof stateVal === "boolean";\n
\n
\t\tif ( jQuery.isFunction( value ) ) {\n
\t\t\treturn this.each(function(i) {\n
\t\t\t\tvar self = jQuery(this);\n
\t\t\t\tself.toggleClass( value.call(this, i, self.attr("class"), stateVal), stateVal );\n
\t\t\t});\n
\t\t}\n
\n
\t\treturn this.each(function() {\n
\t\t\tif ( type === "string" ) {\n
\t\t\t\t// toggle individual class names\n
\t\t\t\tvar className, i = 0, self = jQuery(this),\n
\t\t\t\t\tstate = stateVal,\n
\t\t\t\t\tclassNames = value.split( rspace );\n
\n
\t\t\t\twhile ( (className = classNames[ i++ ]) ) {\n
\t\t\t\t\t// check each className given, space seperated list\n
\t\t\t\t\tstate = isBool ? state : !self.hasClass( className );\n
\t\t\t\t\tself[ state ? "addClass" : "removeClass" ]( className );\n
\t\t\t\t}\n
\n
\t\t\t} else if ( type === "undefined" || type === "boolean" ) {\n
\t\t\t\tif ( this.className ) {\n
\t\t\t\t\t// store className if set\n
\t\t\t\t\tjQuery.data( this, "__className__", this.className );\n
\t\t\t\t}\n
\n
\t\t\t\t// toggle whole className\n
\t\t\t\tthis.className = this.className || value === false ? "" : jQuery.data( this, "__className__" ) || "";\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\thasClass: function( selector ) {\n
\t\tvar className = " " + selector + " ";\n
\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\tif ( (" " + this[i].className + " ").replace(rclass, " ").indexOf( className ) > -1 ) {\n
\t\t\t\treturn true;\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn false;\n
\t},\n
\n
\tval: function( value ) {\n
\t\tif ( value === undefined ) {\n
\t\t\tvar elem = this[0];\n
\n
\t\t\tif ( elem ) {\n
\t\t\t\tif ( jQuery.nodeName( elem, "option" ) ) {\n
\t\t\t\t\treturn (elem.attributes.value || {}).specified ? elem.value : elem.text;\n
\t\t\t\t}\n
\n
\t\t\t\t// We need to handle select boxes special\n
\t\t\t\tif ( jQuery.nodeName( elem, "select" ) ) {\n
\t\t\t\t\tvar index = elem.selectedIndex,\n
\t\t\t\t\t\tvalues = [],\n
\t\t\t\t\t\toptions = elem.options,\n
\t\t\t\t\t\tone = elem.type === "select-one";\n
\n
\t\t\t\t\t// Nothing was selected\n
\t\t\t\t\tif ( index < 0 ) {\n
\t\t\t\t\t\treturn null;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t// Loop through all the selected options\n
\t\t\t\t\tfor ( var i = one ? index : 0, max = one ? index + 1 : options.length; i < max; i++ ) {\n
\t\t\t\t\t\tvar option = options[ i ];\n
\n
\t\t\t\t\t\tif ( option.selected ) {\n
\t\t\t\t\t\t\t// Get the specifc value for the option\n
\t\t\t\t\t\t\tvalue = jQuery(option).val();\n
\n
\t\t\t\t\t\t\t// We don\'t need an array for one selects\n
\t\t\t\t\t\t\tif ( one ) {\n
\t\t\t\t\t\t\t\treturn value;\n
\t\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t\t// Multi-Selects return an array\n
\t\t\t\t\t\t\tvalues.push( value );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t\treturn values;\n
\t\t\t\t}\n
\n
\t\t\t\t// Handle the case where in Webkit "" is returned instead of "on" if a value isn\'t specified\n
\t\t\t\tif ( rradiocheck.test( elem.type ) && !jQuery.support.checkOn ) {\n
\t\t\t\t\treturn elem.getAttribute("value") === null ? "on" : elem.value;\n
\t\t\t\t}\n
\t\t\t\t\n
\n
\t\t\t\t// Everything else, we just grab the value\n
\t\t\t\treturn (elem.value || "").replace(rreturn, "");\n
\n
\t\t\t}\n
\n
\t\t\treturn undefined;\n
\t\t}\n
\n
\t\tvar isFunction = jQuery.isFunction(value);\n
\n
\t\treturn this.each(function(i) {\n
\t\t\tvar self = jQuery(this), val = value;\n
\n
\t\t\tif ( this.nodeType !== 1 ) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\n
\t\t\tif ( isFunction ) {\n
\t\t\t\tval = value.call(this, i, self.val());\n
\t\t\t}\n
\n
\t\t\t// Typecast each time if the value is a Function and the appended\n
\t\t\t// value is therefore different each time.\n
\t\t\tif ( typeof val === "number" ) {\n
\t\t\t\tval += "";\n
\t\t\t}\n
\n
\t\t\tif ( jQuery.isArray(val) && rradiocheck.test( this.type ) ) {\n
\t\t\t\tthis.checked = jQuery.inArray( self.val(), val ) >= 0;\n
\n
\t\t\t} else if ( jQuery.nodeName( this, "select" ) ) {\n
\t\t\t\tvar values = jQuery.makeArray(val);\n
\n
\t\t\t\tjQuery( "option", this ).each(function() {\n
\t\t\t\t\tthis.selected = jQuery.inArray( jQuery(this).val(), values ) >= 0;\n
\t\t\t\t});\n
\n
\t\t\t\tif ( !values.length ) {\n
\t\t\t\t\tthis.selectedIndex = -1;\n
\t\t\t\t}\n
\n
\t\t\t} else {\n
\t\t\t\tthis.value = val;\n
\t\t\t}\n
\t\t});\n
\t}\n
});\n
\n
jQuery.extend({\n
\tattrFn: {\n
\t\tval: true,\n
\t\tcss: true,\n
\t\thtml: true,\n
\t\ttext: true,\n
\t\tdata: true,\n
\t\twidth: true,\n
\t\theight: true,\n
\t\toffset: true\n
\t},\n
\t\t\n
\tattr: function( elem, name, value, pass ) {\n
\t\t// don\'t set attributes on text and comment nodes\n
\t\tif ( !elem || elem.nodeType === 3 || elem.nodeType === 8 ) {\n
\t\t\treturn undefined;\n
\t\t}\n
\n
\t\tif ( pass && name in jQuery.attrFn ) {\n
\t\t\treturn jQuery(elem)[name](value);\n
\t\t}\n
\n
\t\tvar notxml = elem.nodeType !== 1 || !jQuery.isXMLDoc( elem ),\n
\t\t\t// Whether we are setting (or getting)\n
\t\t\tset = value !== undefined;\n
\n
\t\t// Try to normalize/fix the name\n
\t\tname = notxml && jQuery.props[ name ] || name;\n
\n
\t\t// Only do all the following if this is a node (faster for style)\n
\t\tif ( elem.nodeType === 1 ) {\n
\t\t\t// These attributes require special treatment\n
\t\t\tvar special = rspecialurl.test( name );\n
\n
\t\t\t// Safari mis-reports the default selected property of an option\n
\t\t\t// Accessing the parent\'s selectedIndex property fixes it\n
\t\t\tif ( name === "selected" && !jQuery.support.optSelected ) {\n
\t\t\t\tvar parent = elem.parentNode;\n
\t\t\t\tif ( parent ) {\n
\t\t\t\t\tparent.selectedIndex;\n
\t\n
\t\t\t\t\t// Make sure that it also works with optgroups, see #5701\n
\t\t\t\t\tif ( parent.parentNode ) {\n
\t\t\t\t\t\tparent.parentNode.selectedIndex;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// If applicable, access the attribute via the DOM 0 way\n
\t\t\tif ( name in elem && notxml && !special ) {\n
\t\t\t\tif ( set ) {\n
\t\t\t\t\t// We can\'t allow the type property to be changed (since it causes problems in IE)\n
\t\t\t\t\tif ( name === "type" && rtype.test( elem.nodeName ) && elem.parentNode ) {\n
\t\t\t\t\t\tjQuery.error( "type property can\'t be changed" );\n
\t\t\t\t\t}\n
\n
\t\t\t\t\telem[ name ] = value;\n
\t\t\t\t}\n
\n
\t\t\t\t// browsers index elements by id/name on forms, give priority to attributes.\n
\t\t\t\tif ( jQuery.nodeName( elem, "form" ) && elem.getAttributeNode(name) ) {\n
\t\t\t\t\treturn elem.getAttributeNode( name ).nodeValue;\n
\t\t\t\t}\n
\n
\t\t\t\t// elem.tabIndex doesn\'t always return the correct value when it hasn\'t been explicitly set\n
\t\t\t\t// http://fluidproject.org/blog/2008/01/09/getting-setting-and-removing-tabindex-values-with-javascript/\n
\t\t\t\tif ( name === "tabIndex" ) {\n
\t\t\t\t\tvar attributeNode = elem.getAttributeNode( "tabIndex" );\n
\n
\t\t\t\t\treturn attributeNode && attributeNode.specified ?\n
\t\t\t\t\t\tattributeNode.value :\n
\t\t\t\t\t\trfocusable.test( elem.nodeName ) || rclickable.test( elem.nodeName ) && elem.href ?\n
\t\t\t\t\t\t\t0 :\n
\t\t\t\t\t\t\tundefined;\n
\t\t\t\t}\n
\n
\t\t\t\treturn elem[ name ];\n
\t\t\t}\n
\n
\t\t\tif ( !jQuery.support.style && notxml && name === "style" ) {\n
\t\t\t\tif ( set ) {\n
\t\t\t\t\telem.style.cssText = "" + value;\n
\t\t\t\t}\n
\n
\t\t\t\treturn elem.style.cssText;\n
\t\t\t}\n
\n
\t\t\tif ( set ) {\n
\t\t\t\t// convert the value to a string (all browsers do this but IE) see #1070\n
\t\t\t\telem.setAttribute( name, "" + value );\n
\t\t\t}\n
\n
\t\t\tvar attr = !jQuery.support.hrefNormalized && notxml && special ?\n
\t\t\t\t\t// Some attributes require a special call on IE\n
\t\t\t\t\telem.getAttribute( name, 2 ) :\n
\t\t\t\t\telem.getAttribute( name );\n
\n
\t\t\t// Non-existent attributes return null, we normalize to undefined\n
\t\t\treturn attr === null ? undefined : attr;\n
\t\t}\n
\n
\t\t// elem is actually elem.style ... set the style\n
\t\t// Using attr for specific style information is now deprecated. Use style instead.\n
\t\treturn jQuery.style( elem, name, value );\n
\t}\n
});\n
var rnamespaces = /\\.(.*)$/,\n
\tfcleanup = function( nm ) {\n
\t\treturn nm.replace(/[^\\w\\s\\.\\|`]/g, function( ch ) {\n
\t\t\treturn "\\\\" + ch;\n
\t\t});\n
\t};\n
\n
/*\n
 * A number of helper functions used for managing events.\n
 * Many of the ideas behind this code originated from\n
 * Dean Edwards\' addEvent library.\n
 */\n
jQuery.event = {\n
\n
\t// Bind an event to an element\n
\t// Original by Dean Edwards\n
\tadd: function( elem, types, handler, data ) {\n
\t\tif ( elem.nodeType === 3 || elem.nodeType === 8 ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t// For whatever reason, IE has trouble passing the window object\n
\t\t// around, causing it to be cloned in the process\n
\t\tif ( elem.setInterval && ( elem !== window && !elem.frameElement ) ) {\n
\t\t\telem = window;\n
\t\t}\n
\n
\t\tvar handleObjIn, handleObj;\n
\n
\t\tif ( handler.handler ) {\n
\t\t\thandleObjIn = handler;\n
\t\t\thandler = handleObjIn.handler;\n
\t\t}\n
\n
\t\t// Make sure that the function being executed has a unique ID\n
\t\tif ( !handler.guid ) {\n
\t\t\thandler.guid = jQuery.guid++;\n
\t\t}\n
\n
\t\t// Init the element\'s event structure\n
\t\tvar elemData = jQuery.data( elem );\n
\n
\t\t// If no elemData is found then we must be trying to bind to one of the\n
\t\t// banned noData elements\n
\t\tif ( !elemData ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tvar events = elemData.events = elemData.events || {},\n
\t\t\teventHandle = elemData.handle, eventHandle;\n
\n
\t\tif ( !eventHandle ) {\n
\t\t\telemData.handle = eventHandle = function() {\n
\t\t\t\t// Handle the second event of a trigger and when\n
\t\t\t\t// an event is called after a page has unloaded\n
\t\t\t\treturn typeof jQuery !== "undefined" && !jQuery.event.triggered ?\n
\t\t\t\t\tjQuery.event.handle.apply( eventHandle.elem, arguments ) :\n
\t\t\t\t\tundefined;\n
\t\t\t};\n
\t\t}\n
\n
\t\t// Add elem as a property of the handle function\n
\t\t// This is to prevent a memory leak with non-native events in IE.\n
\t\teventHandle.elem = elem;\n
\n
\t\t// Handle multiple events separated by a space\n
\t\t// jQuery(...).bind("mouseover mouseout", fn);\n
\t\ttypes = types.split(" ");\n
\n
\t\tvar type, i = 0, namespaces;\n
\n
\t\twhile ( (type = types[ i++ ]) ) {\n
\t\t\thandleObj = handleObjIn ?\n
\t\t\t\tjQuery.extend({}, handleObjIn) :\n
\t\t\t\t{ handler: handler, data: data };\n
\n
\t\t\t// Namespaced event handlers\n
\t\t\tif ( type.indexOf(".") > -1 ) {\n
\t\t\t\tnamespaces = type.split(".");\n
\t\t\t\ttype = namespaces.shift();\n
\t\t\t\thandleObj.namespace = namespaces.slice(0).sort().join(".");\n
\n
\t\t\t} else {\n
\t\t\t\tnamespaces = [];\n
\t\t\t\thandleObj.namespace = "";\n
\t\t\t}\n
\n
\t\t\thandleObj.type = type;\n
\t\t\thandleObj.guid = handler.guid;\n
\n
\t\t\t// Get the current list of functions bound to this event\n
\t\t\tvar handlers = events[ type ],\n
\t\t\t\tspecial = jQuery.event.special[ type ] || {};\n
\n
\t\t\t// Init the event handler queue\n
\t\t\tif ( !handlers ) {\n
\t\t\t\thandlers = events[ type ] = [];\n
\n
\t\t\t\t// Check for a special event handler\n
\t\t\t\t// Only use addEventListener/attachEvent if the special\n
\t\t\t\t// events handler returns false\n
\t\t\t\tif ( !special.setup || special.setup.call( elem, data, namespaces, eventHandle ) === false ) {\n
\t\t\t\t\t// Bind the global event handler to the element\n
\t\t\t\t\tif ( elem.addEventListener ) {\n
\t\t\t\t\t\telem.addEventListener( type, eventHandle, false );\n
\n
\t\t\t\t\t} else if ( elem.attachEvent ) {\n
\t\t\t\t\t\telem.attachEvent( "on" + type, eventHandle );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\tif ( special.add ) { \n
\t\t\t\tspecial.add.call( elem, handleObj ); \n
\n
\t\t\t\tif ( !handleObj.handler.guid ) {\n
\t\t\t\t\thandleObj.handler.guid = handler.guid;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// Add the function to the element\'s handler list\n
\t\t\thandlers.push( handleObj );\n
\n
\t\t\t// Keep track of which events have been used, for global triggering\n
\t\t\tjQuery.event.global[ type ] = true;\n
\t\t}\n
\n
\t\t// Nullify elem to prevent memory leaks in IE\n
\t\telem = null;\n
\t},\n
\n
\tglobal: {},\n
\n
\t// Detach an event or set of events from an element\n
\tremove: function( elem, types, handler, pos ) {\n
\t\t// don\'t do events on text and comment nodes\n
\t\tif ( elem.nodeType === 3 || elem.nodeType === 8 ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tvar ret, type, fn, i = 0, all, namespaces, namespace, special, eventType, handleObj, origType,\n
\t\t\telemData = jQuery.data( elem ),\n
\t\t\tevents = elemData && elemData.events;\n
\n
\t\tif ( !elemData || !events ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t// types is actually an event object here\n
\t\tif ( types && types.type ) {\n
\t\t\thandler = types.handler;\n
\t\t\ttypes = types.type;\n
\t\t}\n
\n
\t\t// Unbind all events for the element\n
\t\tif ( !types || typeof types === "string" && types.charAt(0) === "." ) {\n
\t\t\ttypes = types || "";\n
\n
\t\t\tfor ( type in events ) {\n
\t\t\t\tjQuery.event.remove( elem, type + types );\n
\t\t\t}\n
\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t// Handle multiple events separated by a space\n
\t\t// jQuery(...).unbind("mouseover mouseout", fn);\n
\t\ttypes = types.split(" ");\n
\n
\t\twhile ( (type = types[ i++ ]) ) {\n
\t\t\torigType = type;\n
\t\t\thandleObj = null;\n
\t\t\tall = type.indexOf(".") < 0;\n
\t\t\tnamespaces = [];\n
\n
\t\t\tif ( !all ) {\n
\t\t\t\t// Namespaced event handlers\n
\t\t\t\tnamespaces = type.split(".");\n
\t\t\t\ttype = namespaces.shift();\n
\n
\t\t\t\tnamespace = new RegExp("(^|\\\\.)" + \n
\t\t\t\t\tjQuery.map( namespaces.slice(0).sort(), fcleanup ).join("\\\\.(?:.*\\\\.)?") + "(\\\\.|$)")\n
\t\t\t}\n
\n
\t\t\teventType = events[ type ];\n
\n
\t\t\tif ( !eventType ) {\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\n
\t\t\tif ( !handler ) {\n
\t\t\t\tfor ( var j = 0; j < eventType.length; j++ ) {\n
\t\t\t\t\thandleObj = eventType[ j ];\n
\n
\t\t\t\t\tif ( all || namespace.test( handleObj.namespace ) ) {\n
\t\t\t\t\t\tjQuery.event.remove( elem, origType, handleObj.handler, j );\n
\t\t\t\t\t\teventType.splice( j--, 1 );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\n
\t\t\tspecial = jQuery.event.special[ type ] || {};\n
\n
\t\t\tfor ( var j = pos || 0; j < eventType.length; j++ ) {\n
\t\t\t\thandleObj = eventType[ j ];\n
\n
\t\t\t\tif ( handler.guid === handleObj.guid ) {\n
\t\t\t\t\t// remove the given handler for the given type\n
\t\t\t\t\tif ( all || namespace.test( handleObj.namespace ) ) {\n
\t\t\t\t\t\tif ( pos == null ) {\n
\t\t\t\t\t\t\teventType.splice( j--, 1 );\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tif ( special.remove ) {\n
\t\t\t\t\t\t\tspecial.remove.call( elem, handleObj );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif ( pos != null ) {\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// remove generic event handler if no more handlers exist\n
\t\t\tif ( eventType.length === 0 || pos != null && eventType.length === 1 ) {\n
\t\t\t\tif ( !special.teardown || special.teardown.call( elem, namespaces ) === false ) {\n
\t\t\t\t\tremoveEvent( elem, type, elemData.handle );\n
\t\t\t\t}\n
\n
\t\t\t\tret = null;\n
\t\t\t\tdelete events[ type ];\n
\t\t\t}\n
\t\t}\n
\n
\t\t// Remove the expando if it\'s no longer used\n
\t\tif ( jQuery.isEmptyObject( events ) ) {\n
\t\t\tvar handle = elemData.handle;\n
\t\t\tif ( handle ) {\n
\t\t\t\thandle.elem = null;\n
\t\t\t}\n
\n
\t\t\tdelete elemData.events;\n
\t\t\tdelete elemData.handle;\n
\n
\t\t\tif ( jQuery.isEmptyObject( elemData ) ) {\n
\t\t\t\tjQuery.removeData( elem );\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\t// bubbling is internal\n
\ttrigger: function( event, data, elem /*, bubbling */ ) {\n
\t\t// Event object or event type\n
\t\tvar type = event.type || event,\n
\t\t\tbubbling = arguments[3];\n
\n
\t\tif ( !bubbling ) {\n
\t\t\tevent = typeof event === "object" ?\n
\t\t\t\t// jQuery.Event object\n
\t\t\t\tevent[expando] ? event :\n
\t\t\t\t// Object literal\n
\t\t\t\tjQuery.extend( jQuery.Event(type), event ) :\n
\t\t\t\t// Just the event type (string)\n
\t\t\t\tjQuery.Event(type);\n
\n
\t\t\tif ( type.indexOf("!") >= 0 ) {\n
\t\t\t\tevent.type = type = type.slice(0, -1);\n
\t\t\t\tevent.exclusive = true;\n
\t\t\t}\n
\n
\t\t\t// Handle a global trigger\n
\t\t\tif ( !elem ) {\n
\t\t\t\t// Don\'t bubble custom events when global (to avoid too much overhead)\n
\t\t\t\tevent.stopPropagation();\n
\n
\t\t\t\t// Only trigger if we\'ve ever bound an event for it\n
\t\t\t\tif ( jQuery.event.global[ type ] ) {\n
\t\t\t\t\tjQuery.each( jQuery.cache, function() {\n
\t\t\t\t\t\tif ( this.events && this.events[type] ) {\n
\t\t\t\t\t\t\tjQuery.event.trigger( event, data, this.handle.elem );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t});\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// Handle triggering a single element\n
\n
\t\t\t// don\'t do events on text and comment nodes\n
\t\t\tif ( !elem || elem.nodeType === 3 || elem.nodeType === 8 ) {\n
\t\t\t\treturn undefined;\n
\t\t\t}\n
\n
\t\t\t// Clean up in case it is reused\n
\t\t\tevent.result = undefined;\n
\t\t\tevent.target = elem;\n
\n
\t\t\t// Clone the incoming data, if any\n
\t\t\tdata = jQuery.makeArray( data );\n
\t\t\tdata.unshift( event );\n
\t\t}\n
\n
\t\tevent.currentTarget = elem;\n
\n
\t\t// Trigger the event, it is assumed that "handle" is a function\n
\t\tvar handle = jQuery.data( elem, "handle" );\n
\t\tif ( handle ) {\n
\t\t\thandle.apply( elem, data );\n
\t\t}\n
\n
\t\tvar parent = elem.parentNode || elem.ownerDocument;\n
\n
\t\t// Trigger an inline bound script\n
\t\ttry {\n
\t\t\tif ( !(elem && elem.nodeName && jQuery.noData[elem.nodeName.toLowerCase()]) ) {\n
\t\t\t\tif ( elem[ "on" + type ] && elem[ "on" + type ].apply( elem, data ) === false ) {\n
\t\t\t\t\tevent.result = false;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t// prevent IE from throwing an error for some elements with some event types, see #3533\n
\t\t} catch (e) {}\n
\n
\t\tif ( !event.isPropagationStopped() && parent ) {\n
\t\t\tjQuery.event.trigger( event, data, parent, true );\n
\n
\t\t} else if ( !event.isDefaultPrevented() ) {\n
\t\t\tvar target = event.target, old,\n
\t\t\t\tisClick = jQuery.nodeName(target, "a") && type === "click",\n
\t\t\t\tspecial = jQuery.event.special[ type ] || {};\n
\n
\t\t\tif ( (!special._default || special._default.call( elem, event ) === false) && \n
\t\t\t\t!isClick && !(target && target.nodeName && jQuery.noData[target.nodeName.toLowerCase()]) ) {\n
\n
\t\t\t\ttry {\n
\t\t\t\t\tif ( target[ type ] ) {\n
\t\t\t\t\t\t// Make sure that we don\'t accidentally re-trigger the onFOO events\n
\t\t\t\t\t\told = target[ "on" + type ];\n
\n
\t\t\t\t\t\tif ( old ) {\n
\t\t\t\t\t\t\ttarget[ "on" + type ] = null;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\tjQuery.event.triggered = true;\n
\t\t\t\t\t\ttarget[ type ]();\n
\t\t\t\t\t}\n
\n
\t\t\t\t// prevent IE from throwing an error for some elements with some event types, see #3533\n
\t\t\t\t} catch (e) {}\n
\n
\t\t\t\tif ( old ) {\n
\t\t\t\t\ttarget[ "on" + type ] = old;\n
\t\t\t\t}\n
\n
\t\t\t\tjQuery.event.triggered = false;\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\thandle: function( event ) {\n
\t\tvar all, handlers, namespaces, namespace, events;\n
\n
\t\tevent = arguments[0] = jQuery.event.fix( event || window.event );\n
\t\tevent.currentTarget = this;\n
\n
\t\t// Namespaced event handlers\n
\t\tall = event.type.indexOf(".") < 0 && !event.exclusive;\n
\n
\t\tif ( !all ) {\n
\t\t\tnamespaces = event.type.split(".");\n
\t\t\tevent.type = namespaces.shift();\n
\t\t\tnamespace = new RegExp("(^|\\\\.)" + namespaces.slice(0).sort().join("\\\\.(?:.*\\\\.)?") + "(\\\\.|$)");\n
\t\t}\n
\n
\t\tvar events = jQuery.data(this, "events"), handlers = events[ event.type ];\n
\n
\t\tif ( events && handlers ) {\n
\t\t\t// Clone the handlers to prevent manipulation\n
\t\t\thandlers = handlers.slice(0);\n
\n
\t\t\tfor ( var j = 0, l = handlers.length; j < l; j++ ) {\n
\t\t\t\tvar handleObj = handlers[ j ];\n
\n
\t\t\t\t// Filter the functions by class\n
\t\t\t\tif ( all || namespace.test( handleObj.namespace ) ) {\n
\t\t\t\t\t// Pass in a reference to the handler function itself\n
\t\t\t\t\t// So that we can later remove it\n
\t\t\t\t\tevent.handler = handleObj.handler;\n
\t\t\t\t\tevent.data = handleObj.data;\n
\t\t\t\t\tevent.handleObj = handleObj;\n
\t\n
\t\t\t\t\tvar ret = handleObj.handler.apply( this, arguments );\n
\n
\t\t\t\t\tif ( ret !== undefined ) {\n
\t\t\t\t\t\tevent.result = ret;\n
\t\t\t\t\t\tif ( ret === false ) {\n
\t\t\t\t\t\t\tevent.preventDefault();\n
\t\t\t\t\t\t\tevent.stopPropagation();\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif ( event.isImmediatePropagationStopped() ) {\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn event.result;\n
\t},\n
\n
\tprops: "altKey attrChange attrName bubbles button cancelable charCode clientX clientY ctrlKey currentTarget data detail eventPhase fromElement handler keyCode layerX layerY metaKey newValue offsetX offsetY originalTarget pageX pageY prevValue relatedNode relatedTarget screenX screenY shiftKey srcElement target toElement view wheelDelta which".split(" "),\n
\n
\tfix: function( event ) {\n
\t\tif ( event[ expando ] ) {\n
\t\t\treturn event;\n
\t\t}\n
\n
\t\t// store a copy of the original event object\n
\t\t// and "clone" to set read-only properties\n
\t\tvar originalEvent = event;\n
\t\tevent = jQuery.Event( originalEvent );\n
\n
\t\tfor ( var i = this.props.length, prop; i; ) {\n
\t\t\tprop = this.props[ --i ];\n
\t\t\tevent[ prop ] = originalEvent[ prop ];\n
\t\t}\n
\n
\t\t// Fix target property, if necessary\n
\t\tif ( !event.target ) {\n
\t\t\tevent.target = event.srcElement || document; // Fixes #1925 where srcElement might not be defined either\n
\t\t}\n
\n
\t\t// check if target is a textnode (safari)\n
\t\tif ( event.target.nodeType === 3 ) {\n
\t\t\tevent.target = event.target.parentNode;\n
\t\t}\n
\n
\t\t// Add relatedTarget, if necessary\n
\t\tif ( !event.relatedTarget && event.fromElement ) {\n
\t\t\tevent.relatedTarget = event.fromElement === event.target ? event.toElement : event.fromElement;\n
\t\t}\n
\n
\t\t// Calculate pageX/Y if missing and clientX/Y available\n
\t\tif ( event.pageX == null && event.clientX != null ) {\n
\t\t\tvar doc = document.documentElement, body = document.body;\n
\t\t\tevent.pageX = event.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc && doc.clientLeft || body && body.clientLeft || 0);\n
\t\t\tevent.pageY = event.clientY + (doc && doc.scrollTop  || body && body.scrollTop  || 0) - (doc && doc.clientTop  || body && body.clientTop  || 0);\n
\t\t}\n
\n
\t\t// Add which for key events\n
\t\tif ( !event.which && ((event.charCode || event.charCode === 0) ? event.charCode : event.keyCode) ) {\n
\t\t\tevent.which = event.charCode || event.keyCode;\n
\t\t}\n
\n
\t\t// Add metaKey to non-Mac browsers (use ctrl for PC\'s and Meta for Macs)\n
\t\tif ( !event.metaKey && event.ctrlKey ) {\n
\t\t\tevent.metaKey = event.ctrlKey;\n
\t\t}\n
\n
\t\t// Add which for click: 1 === left; 2 === middle; 3 === right\n
\t\t// Note: button is not normalized, so don\'t use it\n
\t\tif ( !event.which && event.button !== undefined ) {\n
\t\t\tevent.which = (event.button & 1 ? 1 : ( event.button & 2 ? 3 : ( event.button & 4 ? 2 : 0 ) ));\n
\t\t}\n
\n
\t\treturn event;\n
\t},\n
\n
\t// Deprecated, use jQuery.guid instead\n
\tguid: 1E8,\n
\n
\t// Deprecated, use jQuery.proxy instead\n
\tproxy: jQuery.proxy,\n
\n
\tspecial: {\n
\t\tready: {\n
\t\t\t// Make sure the ready event is setup\n
\t\t\tsetup: jQuery.bindReady,\n
\t\t\tteardown: jQuery.noop\n
\t\t},\n
\n
\t\tlive: {\n
\t\t\tadd: function( handleObj ) {\n
\t\t\t\tjQuery.event.add( this, handleObj.origType, jQuery.extend({}, handleObj, {handler: liveHandler}) ); \n
\t\t\t},\n
\n
\t\t\tremove: function( handleObj ) {\n
\t\t\t\tvar remove = true,\n
\t\t\t\t\ttype = handleObj.origType.replace(rnamespaces, "");\n
\t\t\t\t\n
\t\t\t\tjQuery.each( jQuery.data(this, "events").live || [], function() {\n
\t\t\t\t\tif ( type === this.origType.replace(rnamespaces, "") ) {\n
\t\t\t\t\t\tremove = false;\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\n
\t\t\t\tif ( remove ) {\n
\t\t\t\t\tjQuery.event.remove( this, handleObj.origType, liveHandler );\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t},\n
\n
\t\tbeforeunload: {\n
\t\t\tsetup: function( data, namespaces, eventHandle ) {\n
\t\t\t\t// We only want to do this special case on windows\n
\t\t\t\tif ( this.setInterval ) {\n
\t\t\t\t\tthis.onbeforeunload = eventHandle;\n
\t\t\t\t}\n
\n
\t\t\t\treturn false;\n
\t\t\t},\n
\t\t\tteardown: function( namespaces, eventHandle ) {\n
\t\t\t\tif ( this.onbeforeunload === eventHandle ) {\n
\t\t\t\t\tthis.onbeforeunload = null;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
};\n
\n
var removeEvent = document.removeEventListener ?\n
\tfunction( elem, type, handle ) {\n
\t\telem.removeEventListener( type, handle, false );\n
\t} : \n
\tfunction( elem, type, handle ) {\n
\t\telem.detachEvent( "on" + type, handle );\n
\t};\n
\n
jQuery.Event = function( src ) {\n
\t// Allow instantiation without the \'new\' keyword\n
\tif ( !this.preventDefault ) {\n
\t\treturn new jQuery.Event( src );\n
\t}\n
\n
\t// Event object\n
\tif ( src && src.type ) {\n
\t\tthis.originalEvent = src;\n
\t\tthis.type = src.type;\n
\t// Event type\n
\t} else {\n
\t\tthis.type = src;\n
\t}\n
\n
\t// timeStamp is buggy for some events on Firefox(#3843)\n
\t// So we won\'t rely on the native value\n
\tthis.timeStamp = now();\n
\n
\t// Mark it as fixed\n
\tthis[ expando ] = true;\n
};\n
\n
function returnFalse() {\n
\treturn false;\n
}\n
function returnTrue() {\n
\treturn true;\n
}\n
\n
// jQuery.Event is based on DOM3 Events as specified by the ECMAScript Language Binding\n
// http://www.w3.org/TR/2003/WD-DOM-Level-3-Events-20030331/ecma-script-binding.html\n
jQuery.Event.prototype = {\n
\tpreventDefault: function() {\n
\t\tthis.isDefaultPrevented = returnTrue;\n
\n
\t\tvar e = this.originalEvent;\n
\t\tif ( !e ) {\n
\t\t\treturn;\n
\t\t}\n
\t\t\n
\t\t// if preventDefault exists run it on the original event\n
\t\tif ( e.preventDefault ) {\n
\t\t\te.preventDefault();\n
\t\t}\n
\t\t// otherwise set the returnValue property of the original event to false (IE)\n
\t\te.returnValue = false;\n
\t},\n
\tstopPropagation: function() {\n
\t\tthis.isPropagationStopped = returnTrue;\n
\n
\t\tvar e = this.originalEvent;\n
\t\tif ( !e ) {\n
\t\t\treturn;\n
\t\t}\n
\t\t// if stopPropagation exists run it on the original event\n
\t\tif ( e.stopPropagation ) {\n
\t\t\te.stopPropagation();\n
\t\t}\n
\t\t// otherwise set the cancelBubble property of the original event to true (IE)\n
\t\te.cancelBubble = true;\n
\t},\n
\tstopImmediatePropagation: function() {\n
\t\tthis.isImmediatePropagationStopped = returnTrue;\n
\t\tthis.stopPropagation();\n
\t},\n
\tisDefaultPrevented: returnFalse,\n
\tisPropagationStopped: returnFalse,\n
\tisImmediatePropagationStopped: returnFalse\n
};\n
\n
// Checks if an event happened on an element within another element\n
// Used in jQuery.event.special.mouseenter and mouseleave handlers\n
var withinElement = function( event ) {\n
\t// Check if mouse(over|out) are still within the same parent element\n
\tvar parent = event.relatedTarget;\n
\n
\t// Firefox sometimes assigns relatedTarget a XUL element\n
\t// which we cannot access the parentNode property of\n
\ttry {\n
\t\t// Traverse up the tree\n
\t\twhile ( parent && parent !== this ) {\n
\t\t\tparent = parent.parentNode;\n
\t\t}\n
\n
\t\tif ( parent !== this ) {\n
\t\t\t// set the correct event type\n
\t\t\tevent.type = event.data;\n
\n
\t\t\t// handle event if we actually just moused on to a non sub-element\n
\t\t\tjQuery.event.handle.apply( this, arguments );\n
\t\t}\n
\n
\t// assuming we\'ve left the element since we most likely mousedover a xul element\n
\t} catch(e) { }\n
},\n
\n
// In case of event delegation, we only need to rename the event.type,\n
// liveHandler will take care of the rest.\n
delegate = function( event ) {\n
\tevent.type = event.data;\n
\tjQuery.event.handle.apply( this, arguments );\n
};\n
\n
// Create mouseenter and mouseleave events\n
jQuery.each({\n
\tmouseenter: "mouseover",\n
\tmouseleave: "mouseout"\n
}, function( orig, fix ) {\n
\tjQuery.event.special[ orig ] = {\n
\t\tsetup: function( data ) {\n
\t\t\tjQuery.event.add( this, fix, data && data.selector ? delegate : withinElement, orig );\n
\t\t},\n
\t\tteardown: function( data ) {\n
\t\t\tjQuery.event.remove( this, fix, data && data.selector ? delegate : withinElement );\n
\t\t}\n
\t};\n
});\n
\n
// submit delegation\n
if ( !jQuery.support.submitBubbles ) {\n
\n
\tjQuery.event.special.submit = {\n
\t\tsetup: function( data, namespaces ) {\n
\t\t\tif ( this.nodeName.toLowerCase() !== "form" ) {\n
\t\t\t\tjQuery.event.add(this, "click.specialSubmit", function( e ) {\n
\t\t\t\t\tvar elem = e.target, type = elem.type;\n
\n
\t\t\t\t\tif ( (type === "submit" || type === "image") && jQuery( elem ).closest("form").length ) {\n
\t\t\t\t\t\treturn trigger( "submit", this, arguments );\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t \n
\t\t\t\tjQuery.event.add(this, "keypress.specialSubmit", function( e ) {\n
\t\t\t\t\tvar elem = e.target, type = elem.type;\n
\n
\t\t\t\t\tif ( (type === "text" || type === "password") && jQuery( elem ).closest("form").length && e.keyCode === 13 ) {\n
\t\t\t\t\t\treturn trigger( "submit", this, arguments );\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\n
\t\t\t} else {\n
\t\t\t\treturn false;\n
\t\t\t}\n
\t\t},\n
\n
\t\tteardown: function( namespaces ) {\n
\t\t\tjQuery.event.remove( this, ".specialSubmit" );\n
\t\t}\n
\t};\n
\n
}\n
\n
// change delegation, happens here so we have bind.\n
if ( !jQuery.support.changeBubbles ) {\n
\n
\tvar formElems = /textarea|input|select/i,\n
\n
\tchangeFilters,\n
\n
\tgetVal = function( elem ) {\n
\t\tvar type = elem.type, val = elem.value;\n
\n
\t\tif ( type === "radio" || type === "checkbox" ) {\n
\t\t\tval = elem.checked;\n
\n
\t\t} else if ( type === "select-multiple" ) {\n
\t\t\tval = elem.selectedIndex > -1 ?\n
\t\t\t\tjQuery.map( elem.options, function( elem ) {\n
\t\t\t\t\treturn elem.selected;\n
\t\t\t\t}).join("-") :\n
\t\t\t\t"";\n
\n
\t\t} else if ( elem.nodeName.toLowerCase() === "select" ) {\n
\t\t\tval = elem.selectedIndex;\n
\t\t}\n
\n
\t\treturn val;\n
\t},\n
\n
\ttestChange = function testChange( e ) {\n
\t\tvar elem = e.target, data, val;\n
\n
\t\tif ( !formElems.test( elem.nodeName ) || elem.readOnly ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tdata = jQuery.data( elem, "_change_data" );\n
\t\tval = getVal(elem);\n
\n
\t\t// the current data will be also retrieved by beforeactivate\n
\t\tif ( e.type !== "focusout" || elem.type !== "radio" ) {\n
\t\t\tjQuery.data( elem, "_change_data", val );\n
\t\t}\n
\t\t\n
\t\tif ( data === undefined || val === data ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tif ( data != null || val ) {\n
\t\t\te.type = "change";\n
\t\t\treturn jQuery.event.trigger( e, arguments[1], elem );\n
\t\t}\n
\t};\n
\n
\tjQuery.event.special.change = {\n
\t\tfilters: {\n
\t\t\tfocusout: testChange, \n
\n
\t\t\tclick: function( e ) {\n
\t\t\t\tvar elem = e.target, type = elem.type;\n
\n
\t\t\t\tif ( type === "radio" || type === "checkbox" || elem.nodeName.toLowerCase() === "select" ) {\n
\t\t\t\t\treturn testChange.call( this, e );\n
\t\t\t\t}\n
\t\t\t},\n
\n
\t\t\t// Change has to be called before submit\n
\t\t\t// Keydown will be called before keypress, which is used in submit-event delegation\n
\t\t\tkeydown: function( e ) {\n
\t\t\t\tvar elem = e.target, type = elem.type;\n
\n
\t\t\t\tif ( (e.keyCode === 13 && elem.nodeName.toLowerCase() !== "textarea") ||\n
\t\t\t\t\t(e.keyCode === 32 && (type === "checkbox" || type === "radio")) ||\n
\t\t\t\t\ttype === "select-multiple" ) {\n
\t\t\t\t\treturn testChange.call( this, e );\n
\t\t\t\t}\n
\t\t\t},\n
\n
\t\t\t// Beforeactivate happens also before the previous element is blurred\n
\t\t\t// with this event you can\'t trigger a change event, but you can store\n
\t\t\t// information/focus[in] is not needed anymore\n
\t\t\tbeforeactivate: function( e ) {\n
\t\t\t\tvar elem = e.target;\n
\t\t\t\tjQuery.data( elem, "_change_data", getVal(elem) );\n
\t\t\t}\n
\t\t},\n
\n
\t\tsetup: function( data, namespaces ) {\n
\t\t\tif ( this.type === "file" ) {\n
\t\t\t\treturn false;\n
\t\t\t}\n
\n
\t\t\tfor ( var type in changeFilters ) {\n
\t\t\t\tjQuery.event.add( this, type + ".specialChange", changeFilters[type] );\n
\t\t\t}\n
\n
\t\t\treturn formElems.test( this.nodeName );\n
\t\t},\n
\n
\t\tteardown: function( namespaces ) {\n
\t\t\tjQuery.event.remove( this, ".specialChange" );\n
\n
\t\t\treturn formElems.test( this.nodeName );\n
\t\t}\n
\t};\n
\n
\tchangeFilters = jQuery.event.special.change.filters;\n
}\n
\n
function trigger( type, elem, args ) {\n
\targs[0].type = type;\n
\treturn jQuery.event.handle.apply( elem, args );\n
}\n
\n
// Create "bubbling" focus and blur events\n
if ( document.addEventListener ) {\n
\tjQuery.each({ focus: "focusin", blur: "focusout" }, function( orig, fix ) {\n
\t\tjQuery.event.special[ fix ] = {\n
\t\t\tsetup: function() {\n
\t\t\t\tthis.addEventListener( orig, handler, true );\n
\t\t\t}, \n
\t\t\tteardown: function() { \n
\t\t\t\tthis.removeEventListener( orig, handler, true );\n
\t\t\t}\n
\t\t};\n
\n
\t\tfunction handler( e ) { \n
\t\t\te = jQuery.event.fix( e );\n
\t\t\te.type = fix;\n
\t\t\treturn jQuery.event.handle.call( this, e );\n
\t\t}\n
\t});\n
}\n
\n
jQuery.each(["bind", "one"], function( i, name ) {\n
\tjQuery.fn[ name ] = function( type, data, fn ) {\n
\t\t// Handle object literals\n
\t\tif ( typeof type === "object" ) {\n
\t\t\tfor ( var key in type ) {\n
\t\t\t\tthis[ name ](key, data, type[key], fn);\n
\t\t\t}\n
\t\t\treturn this;\n
\t\t}\n
\t\t\n
\t\tif ( jQuery.isFunction( data ) ) {\n
\t\t\tfn = data;\n
\t\t\tdata = undefined;\n
\t\t}\n
\n
\t\tvar handler = name === "one" ? jQuery.proxy( fn, function( event ) {\n
\t\t\tjQuery( this ).unbind( event, handler );\n
\t\t\treturn fn.apply( this, arguments );\n
\t\t}) : fn;\n
\n
\t\tif ( type === "unload" && name !== "one" ) {\n
\t\t\tthis.one( type, data, fn );\n
\n
\t\t} else {\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\t\tjQuery.event.add( this[i], type, handler, data );\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn this;\n
\t};\n
});\n
\n
jQuery.fn.extend({\n
\tunbind: function( type, fn ) {\n
\t\t// Handle object literals\n
\t\tif ( typeof type === "object" && !type.preventDefault ) {\n
\t\t\tfor ( var key in type ) {\n
\t\t\t\tthis.unbind(key, type[key]);\n
\t\t\t}\n
\n
\t\t} else {\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\t\tjQuery.event.remove( this[i], type, fn );\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\t\n
\tdelegate: function( selector, types, data, fn ) {\n
\t\treturn this.live( types, data, fn, selector );\n
\t},\n
\t\n
\tundelegate: function( selector, types, fn ) {\n
\t\tif ( arguments.length === 0 ) {\n
\t\t\t\treturn this.unbind( "live" );\n
\t\t\n
\t\t} else {\n
\t\t\treturn this.die( types, null, fn, selector );\n
\t\t}\n
\t},\n
\t\n
\ttrigger: function( type, data ) {\n
\t\treturn this.each(function() {\n
\t\t\tjQuery.event.trigger( type, data, this );\n
\t\t});\n
\t},\n
\n
\ttriggerHandler: function( type, data ) {\n
\t\tif ( this[0] ) {\n
\t\t\tvar event = jQuery.Event( type );\n
\t\t\tevent.preventDefault();\n
\t\t\tevent.stopPropagation();\n
\t\t\tjQuery.event.trigger( event, data, this[0] );\n
\t\t\treturn event.result;\n
\t\t}\n
\t},\n
\n
\ttoggle: function( fn ) {\n
\t\t// Save reference to arguments for access in closure\n
\t\tvar args = arguments, i = 1;\n
\n
\t\t// link all the functions, so any of them can unbind this click handler\n
\t\twhile ( i < args.length ) {\n
\t\t\tjQuery.proxy( fn, args[ i++ ] );\n
\t\t}\n
\n
\t\treturn this.click( jQuery.proxy( fn, function( event ) {\n
\t\t\t// Figure out which function to execute\n
\t\t\tvar lastToggle = ( jQuery.data( this, "lastToggle" + fn.guid ) || 0 ) % i;\n
\t\t\tjQuery.data( this, "lastToggle" + fn.guid, lastToggle + 1 );\n
\n
\t\t\t// Make sure that clicks stop\n
\t\t\tevent.preventDefault();\n
\n
\t\t\t// and execute the function\n
\t\t\treturn args[ lastToggle ].apply( this, arguments ) || false;\n
\t\t}));\n
\t},\n
\n
\thover: function( fnOver, fnOut ) {\n
\t\treturn this.mouseenter( fnOver ).mouseleave( fnOut || fnOver );\n
\t}\n
});\n
\n
var liveMap = {\n
\tfocus: "focusin",\n
\tblur: "focusout",\n
\tmouseenter: "mouseover",\n
\tmouseleave: "mouseout"\n
};\n
\n
jQuery.each(["live", "die"], function( i, name ) {\n
\tjQuery.fn[ name ] = function( types, data, fn, origSelector /* Internal Use Only */ ) {\n
\t\tvar type, i = 0, match, namespaces, preType,\n
\t\t\tselector = origSelector || this.selector,\n
\t\t\tcontext = origSelector ? this : jQuery( this.context );\n
\n
\t\tif ( jQuery.isFunction( data ) ) {\n
\t\t\tfn = data;\n
\t\t\tdata = undefined;\n
\t\t}\n
\n
\t\ttypes = (types || "").split(" ");\n
\n
\t\twhile ( (type = types[ i++ ]) != null ) {\n
\t\t\tmatch = rnamespaces.exec( type );\n
\t\t\tnamespaces = "";\n
\n
\t\t\tif ( match )  {\n
\t\t\t\tnamespaces = match[0];\n
\t\t\t\ttype = type.replace( rnamespaces, "" );\n
\t\t\t}\n
\n
\t\t\tif ( type === "hover" ) {\n
\t\t\t\ttypes.push( "mouseenter" + namespaces, "mouseleave" + namespaces );\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\n
\t\t\tpreType = type;\n
\n
\t\t\tif ( type === "focus" || type === "blur" ) {\n
\t\t\t\ttypes.push( liveMap[ type ] + namespaces );\n
\t\t\t\ttype = type + namespaces;\n
\n
\t\t\t} else {\n
\t\t\t\ttype = (liveMap[ type ] || type) + namespaces;\n
\t\t\t}\n
\n
\t\t\tif ( name === "live" ) {\n
\t\t\t\t// bind live handler\n
\t\t\t\tcontext.each(function(){\n
\t\t\t\t\tjQuery.event.add( this, liveConvert( type, selector ),\n
\t\t\t\t\t\t{ data: data, selector: selector, handler: fn, origType: type, origHandler: fn, preType: preType } );\n
\t\t\t\t});\n
\n
\t\t\t} else {\n
\t\t\t\t// unbind live handler\n
\t\t\t\tcontext.unbind( liveConvert( type, selector ), fn );\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\treturn this;\n
\t}\n
});\n
\n
function liveHandler( event ) {\n
\tvar stop, elems = [], selectors = [], args = arguments,\n
\t\trelated, match, handleObj, elem, j, i, l, data,\n
\t\tevents = jQuery.data( this, "events" );\n
\n
\t// Make sure we avoid non-left-click bubbling in Firefox (#3861)\n
\tif ( event.liveFired === this || !events || !events.live || event.button && event.type === "click" ) {\n
\t\treturn;\n
\t}\n
\n
\tevent.liveFired = this;\n
\n
\tvar live = events.live.slice(0);\n
\n
\tfor ( j = 0; j < live.length; j++ ) {\n
\t\thandleObj = live[j];\n
\n
\t\tif ( handleObj.origType.replace( rnamespaces, "" ) === event.type ) {\n
\t\t\tselectors.push( handleObj.selector );\n
\n
\t\t} else {\n
\t\t\tlive.splice( j--, 1 );\n
\t\t}\n
\t}\n
\n
\tmatch = jQuery( event.target ).closest( selectors, event.currentTarget );\n
\n
\tfor ( i = 0, l = match.length; i < l; i++ ) {\n
\t\tfor ( j = 0; j < live.length; j++ ) {\n
\t\t\thandleObj = live[j];\n
\n
\t\t\tif ( match[i].selector === handleObj.selector ) {\n
\t\t\t\telem = match[i].elem;\n
\t\t\t\trelated = null;\n
\n
\t\t\t\t// Those two events require additional checking\n
\t\t\t\tif ( handleObj.preType === "mouseenter" || handleObj.preType === "mouseleave" ) {\n
\t\t\t\t\trelated = jQuery( event.relatedTarget ).closest( handleObj.selector )[0];\n
\t\t\t\t}\n
\n
\t\t\t\tif ( !related || related !== elem ) {\n
\t\t\t\t\telems.push({ elem: elem, handleObj: handleObj });\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\tfor ( i = 0, l = elems.length; i < l; i++ ) {\n
\t\tmatch = elems[i];\n
\t\tevent.currentTarget = match.elem;\n
\t\tevent.data = match.handleObj.data;\n
\t\tevent.handleObj = match.handleObj;\n
\n
\t\tif ( match.handleObj.origHandler.apply( match.elem, args ) === false ) {\n
\t\t\tstop = false;\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\n
\treturn stop;\n
}\n
\n
function liveConvert( type, selector ) {\n
\treturn "live." + (type && type !== "*" ? type + "." : "") + selector.replace(/\\./g, "`").replace(/ /g, "&");\n
}\n
\n
jQuery.each( ("blur focus focusin focusout load resize scroll unload click dblclick " +\n
\t"mousedown mouseup mousemove mouseover mouseout mouseenter mouseleave " +\n
\t"change select submit keydown keypress keyup error").split(" "), function( i, name ) {\n
\n
\t// Handle event binding\n
\tjQuery.fn[ name ] = function( fn ) {\n
\t\treturn fn ? this.bind( name, fn ) : this.trigger( name );\n
\t};\n
\n
\tif ( jQuery.attrFn ) {\n
\t\tjQuery.attrFn[ name ] = true;\n
\t}\n
});\n
\n
// Prevent memory leaks in IE\n
// Window isn\'t included so as not to unbind existing unload events\n
// More info:\n
//  - http://isaacschlueter.com/2006/10/msie-memory-leaks/\n
if ( window.attachEvent && !window.addEventListener ) {\n
\twindow.attachEvent("onunload", function() {\n
\t\tfor ( var id in jQuery.cache ) {\n
\t\t\tif ( jQuery.cache[ id ].handle ) {\n
\t\t\t\t// Try/Catch is to handle iframes being unloaded, see #4280\n
\t\t\t\ttry {\n
\t\t\t\t\tjQuery.event.remove( jQuery.cache[ id ].handle.elem );\n
\t\t\t\t} catch(e) {}\n
\t\t\t}\n
\t\t}\n
\t});\n
}\n
/*!\n
 * Sizzle CSS Selector Engine - v1.0\n
 *  Copyright 2009, The Dojo Foundation\n
 *  Released under the MIT, BSD, and GPL Licenses.\n
 *  More information: http://sizzlejs.com/\n
 */\n
(function(){\n
\n
var chunker = /((?:\\((?:\\([^()]+\\)|[^()]+)+\\)|\\[(?:\\[[^[\\]]*\\]|[\'"][^\'"]*[\'"]|[^[\\]\'"]+)+\\]|\\\\.|[^ >+~,(\\[\\\\]+)+|[>+~])(\\s*,\\s*)?((?:.|\\r|\\n)*)/g,\n
\tdone = 0,\n
\ttoString = Object.prototype.toString,\n
\thasDuplicate = false,\n
\tbaseHasDuplicate = true;\n
\n
// Here we check if the JavaScript engine is using some sort of\n
// optimization where it does not always call our comparision\n
// function. If that is the case, discard the hasDuplicate value.\n
//   Thus far that includes Google Chrome.\n
[0, 0].sort(function(){\n
\tbaseHasDuplicate = false;\n
\treturn 0;\n
});\n
\n
var Sizzle = function(selector, context, results, seed) {\n
\tresults = results || [];\n
\tvar origContext = context = context || document;\n
\n
\tif ( context.nodeType !== 1 && context.nodeType !== 9 ) {\n
\t\treturn [];\n
\t}\n
\t\n
\tif ( !selector || typeof selector !== "string" ) {\n
\t\treturn results;\n
\t}\n
\n
\tvar parts = [], m, set, checkSet, extra, prune = true, contextXML = isXML(context),\n
\t\tsoFar = selector;\n
\t\n
\t// Reset the position of the chunker regexp (start from head)\n
\twhile ( (chunker.exec(""), m = chunker.exec(soFar)) !== null ) {\n
\t\tsoFar = m[3];\n
\t\t\n
\t\tparts.push( m[1] );\n
\t\t\n
\t\tif ( m[2] ) {\n
\t\t\textra = m[3];\n
\t\t\tbreak;\n
\t\t}\n
\t}\n
\n
\tif ( parts.length > 1 && origPOS.exec( selector ) ) {\n
\t\tif ( parts.length === 2 && Expr.relative[ parts[0] ] ) {\n
\t\t\tset = posProcess( parts[0] + parts[1], context );\n
\t\t} else {\n
\t\t\tset = Expr.relative[ parts[0] ] ?\n
\t\t\t\t[ context ] :\n
\t\t\t\tSizzle( parts.shift(), context );\n
\n
\t\t\twhile ( parts.length ) {\n
\t\t\t\tselector = parts.shift();\n
\n
\t\t\t\tif ( Expr.relative[ selector ] ) {\n
\t\t\t\t\tselector += parts.shift();\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tset = posProcess( selector, set );\n
\t\t\t}\n
\t\t}\n
\t} else {\n
\t\t// Take a shortcut and set the context if the root selector is an ID\n
\t\t// (but not if it\'ll be faster if the inner selector is an ID)\n
\t\tif ( !seed && parts.length > 1 && context.nodeType === 9 && !contextXML &&\n
\t\t\t\tExpr.match.ID.test(parts[0]) && !Expr.match.ID.test(parts[parts.length - 1]) ) {\n
\t\t\tvar ret = Sizzle.find( parts.shift(), context, contextXML );\n
\t\t\tcontext = ret.expr ? Sizzle.filter( ret.expr, ret.set )[0] : ret.set[0];\n
\t\t}\n
\n
\t\tif ( context ) {\n
\t\t\tvar ret = seed ?\n
\t\t\t\t{ expr: parts.pop(), set: makeArray(seed) } :\n
\t\t\t\tSizzle.find( parts.pop(), parts.length === 1 && (parts[0] === "~" || parts[0] === "+") && context.parentNode ? context.parentNode : context, contextXML );\n
\t\t\tset = ret.expr ? Sizzle.filter( ret.expr, ret.set ) : ret.set;\n
\n
\t\t\tif ( parts.length > 0 ) {\n
\t\t\t\tcheckSet = makeArray(set);\n
\t\t\t} else {\n
\t\t\t\tprune = false;\n
\t\t\t}\n
\n
\t\t\twhile ( parts.length ) {\n
\t\t\t\tvar cur = parts.pop(), pop = cur;\n
\n
\t\t\t\tif ( !Expr.relative[ cur ] ) {\n
\t\t\t\t\tcur = "";\n
\t\t\t\t} else {\n
\t\t\t\t\tpop = parts.pop();\n
\t\t\t\t}\n
\n
\t\t\t\tif ( pop == null ) {\n
\t\t\t\t\tpop = context;\n
\t\t\t\t}\n
\n
\t\t\t\tExpr.relative[ cur ]( checkSet, pop, contextXML );\n
\t\t\t}\n
\t\t} else {\n
\t\t\tcheckSet = parts = [];\n
\t\t}\n
\t}\n
\n
\tif ( !checkSet ) {\n
\t\tcheckSet = set;\n
\t}\n
\n
\tif ( !checkSet ) {\n
\t\tSizzle.error( cur || selector );\n
\t}\n
\n
\tif ( toString.call(checkSet) === "[object Array]" ) {\n
\t\tif ( !prune ) {\n
\t\t\tresults.push.apply( results, checkSet );\n
\t\t} else if ( context && context.nodeType === 1 ) {\n
\t\t\tfor ( var i = 0; checkSet[i] != null; i++ ) {\n
\t\t\t\tif ( checkSet[i] && (checkSet[i] === true || checkSet[i].nodeType === 1 && contains(context, checkSet[i])) ) {\n
\t\t\t\t\tresults.push( set[i] );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t} else {\n
\t\t\tfor ( var i = 0; checkSet[i] != null; i++ ) {\n
\t\t\t\tif ( checkSet[i] && checkSet[i].nodeType === 1 ) {\n
\t\t\t\t\tresults.push( set[i] );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t} else {\n
\t\tmakeArray( checkSet, results );\n
\t}\n
\n
\tif ( extra ) {\n
\t\tSizzle( extra, origContext, results, seed );\n
\t\tSizzle.uniqueSort( results );\n
\t}\n
\n
\treturn results;\n
};\n
\n
Sizzle.uniqueSort = function(results){\n
\tif ( sortOrder ) {\n
\t\thasDuplicate = baseHasDuplicate;\n
\t\tresults.sort(sortOrder);\n
\n
\t\tif ( hasDuplicate ) {\n
\t\t\tfor ( var i = 1; i < results.length; i++ ) {\n
\t\t\t\tif ( results[i] === results[i-1] ) {\n
\t\t\t\t\tresults.splice(i--, 1);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\treturn results;\n
};\n
\n
Sizzle.matches = function(expr, set){\n
\treturn Sizzle(expr, null, null, set);\n
};\n
\n
Sizzle.find = function(expr, context, isXML){\n
\tvar set, match;\n
\n
\tif ( !expr ) {\n
\t\treturn [];\n
\t}\n
\n
\tfor ( var i = 0, l = Expr.order.length; i < l; i++ ) {\n
\t\tvar type = Expr.order[i], match;\n
\t\t\n
\t\tif ( (match = Expr.leftMatch[ type ].exec( expr )) ) {\n
\t\t\tvar left = match[1];\n
\t\t\tmatch.splice(1,1);\n
\n
\t\t\tif ( left.substr( left.length - 1 ) !== "\\\\" ) {\n
\t\t\t\tmatch[1] = (match[1] || "").replace(/\\\\/g, "");\n
\t\t\t\tset = Expr.find[ type ]( match, context, isXML );\n
\t\t\t\tif ( set != null ) {\n
\t\t\t\t\texpr = expr.replace( Expr.match[ type ], "" );\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\tif ( !set ) {\n
\t\tset = context.getElementsByTagName("*");\n
\t}\n
\n
\treturn {set: set, expr: expr};\n
};\n
\n
Sizzle.filter = function(expr, set, inplace, not){\n
\tvar old = expr, result = [], curLoop = set, match, anyFound,\n
\t\tisXMLFilter = set && set[0] && isXML(set[0]);\n
\n
\twhile ( expr && set.length ) {\n
\t\tfor ( var type in Expr.filter ) {\n
\t\t\tif ( (match = Expr.leftMatch[ type ].exec( expr )) != null && match[2] ) {\n
\t\t\t\tvar filter = Expr.filter[ type ], found, item, left = match[1];\n
\t\t\t\tanyFound = false;\n
\n
\t\t\t\tmatch.splice(1,1);\n
\n
\t\t\t\tif ( left.substr( left.length - 1 ) === "\\\\" ) {\n
\t\t\t\t\tcontinue;\n
\t\t\t\t}\n
\n
\t\t\t\tif ( curLoop === result ) {\n
\t\t\t\t\tresult = [];\n
\t\t\t\t}\n
\n
\t\t\t\tif ( Expr.preFilter[ type ] ) {\n
\t\t\t\t\tmatch = Expr.preFilter[ type ]( match, curLoop, inplace, result, not, isXMLFilter );\n
\n
\t\t\t\t\tif ( !match ) {\n
\t\t\t\t\t\tanyFound = found = true;\n
\t\t\t\t\t} else if ( match === true ) {\n
\t\t\t\t\t\tcontinue;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tif ( match ) {\n
\t\t\t\t\tfor ( var i = 0; (item = curLoop[i]) != null; i++ ) {\n
\t\t\t\t\t\tif ( item ) {\n
\t\t\t\t\t\t\tfound = filter( item, match, i, curLoop );\n
\t\t\t\t\t\t\tvar pass = not ^ !!found;\n
\n
\t\t\t\t\t\t\tif ( inplace && found != null ) {\n
\t\t\t\t\t\t\t\tif ( pass ) {\n
\t\t\t\t\t\t\t\t\tanyFound = true;\n
\t\t\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\t\t\tcurLoop[i] = false;\n
\t\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\t} else if ( pass ) {\n
\t\t\t\t\t\t\t\tresult.push( item );\n
\t\t\t\t\t\t\t\tanyFound = true;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tif ( found !== undefined ) {\n
\t\t\t\t\tif ( !inplace ) {\n
\t\t\t\t\t\tcurLoop = result;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\texpr = expr.replace( Expr.match[ type ], "" );\n
\n
\t\t\t\t\tif ( !anyFound ) {\n
\t\t\t\t\t\treturn [];\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\t// Improper expression\n
\t\tif ( expr === old ) {\n
\t\t\tif ( anyFound == null ) {\n
\t\t\t\tSizzle.error( expr );\n
\t\t\t} else {\n
\t\t\t\tbreak;\n
\t\t\t}\n
\t\t}\n
\n
\t\told = expr;\n
\t}\n
\n
\treturn curLoop;\n
};\n
\n
Sizzle.error = function( msg ) {\n
\tthrow "Syntax error, unrecognized expression: " + msg;\n
};\n
\n
var Expr = Sizzle.selectors = {\n
\torder: [ "ID", "NAME", "TAG" ],\n
\tmatch: {\n
\t\tID: /#((?:[\\w\\u00c0-\\uFFFF-]|\\\\.)+)/,\n
\t\tCLASS: /\\.((?:[\\w\\u00c0-\\uFFFF-]|\\\\.)+)/,\n
\t\tNAME: /\\[name=[\'"]*((?:[\\w\\u00c0-\\uFFFF-]|\\\\.)+)[\'"]*\\]/,\n
\t\tATTR: /\\[\\s*((?:[\\w\\u00c0-\\uFFFF-]|\\\\.)+)\\s*(?:(\\S?=)\\s*([\'"]*)(.*?)\\3|)\\s*\\]/,\n
\t\tTAG: /^((?:[\\w\\u00c0-\\uFFFF\\*-]|\\\\.)+)/,\n
\t\tCHILD: /:(only|nth|last|first)-child(?:\\((even|odd|[\\dn+-]*)\\))?/,\n
\t\tPOS: /:(nth|eq|gt|lt|first|last|even|odd)(?:\\((\\d*)\\))?(?=[^-]|$)/,\n
\t\tPSEUDO: /:((?:[\\w\\u00c0-\\uFFFF-]|\\\\.)+)(?:\\(([\'"]?)((?:\\([^\\)]+\\)|[^\\(\\)]*)+)\\2\\))?/\n
\t},\n
\tleftMatch: {},\n
\tattrMap: {\n
\t\t"class": "className",\n
\t\t"for": "htmlFor"\n
\t},\n
\tattrHandle: {\n
\t\thref: function(elem){\n
\t\t\treturn elem.getAttribute("href");\n
\t\t}\n
\t},\n
\trelative: {\n
\t\t"+": function(checkSet, part){\n
\t\t\tvar isPartStr = typeof part === "string",\n
\t\t\t\tisTag = isPartStr && !/\\W/.test(part),\n
\t\t\t\tisPartStrNotTag = isPartStr && !isTag;\n
\n
\t\t\tif ( isTag ) {\n
\t\t\t\tpart = part.toLowerCase();\n
\t\t\t}\n
\n
\t\t\tfor ( var i = 0, l = checkSet.length, elem; i < l; i++ ) {\n
\t\t\t\tif ( (elem = checkSet[i]) ) {\n
\t\t\t\t\twhile ( (elem = elem.previousSibling) && elem.nodeType !== 1 ) {}\n
\n
\t\t\t\t\tcheckSet[i] = isPartStrNotTag || elem && elem.nodeName.toLowerCase() === part ?\n
\t\t\t\t\t\telem || false :\n
\t\t\t\t\t\telem === part;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tif ( isPartStrNotTag ) {\n
\t\t\t\tSizzle.filter( part, checkSet, true );\n
\t\t\t}\n
\t\t},\n
\t\t">": function(checkSet, part){\n
\t\t\tvar isPartStr = typeof part === "string";\n
\n
\t\t\tif ( isPartStr && !/\\W/.test(part) ) {\n
\t\t\t\tpart = part.toLowerCase();\n
\n
\t\t\t\tfor ( var i = 0, l = checkSet.length; i < l; i++ ) {\n
\t\t\t\t\tvar elem = checkSet[i];\n
\t\t\t\t\tif ( elem ) {\n
\t\t\t\t\t\tvar parent = elem.parentNode;\n
\t\t\t\t\t\tcheckSet[i] = parent.nodeName.toLowerCase() === part ? parent : false;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tfor ( var i = 0, l = checkSet.length; i < l; i++ ) {\n
\t\t\t\t\tvar elem = checkSet[i];\n
\t\t\t\t\tif ( elem ) {\n
\t\t\t\t\t\tcheckSet[i] = isPartStr ?\n
\t\t\t\t\t\t\telem.parentNode :\n
\t\t\t\t\t\t\telem.parentNode === part;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tif ( isPartStr ) {\n
\t\t\t\t\tSizzle.filter( part, checkSet, true );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\t"": function(checkSet, part, isXML){\n
\t\t\tvar doneName = done++, checkFn = dirCheck;\n
\n
\t\t\tif ( typeof part === "string" && !/\\W/.test(part) ) {\n
\t\t\t\tvar nodeCheck = part = part.toLowerCase();\n
\t\t\t\tcheckFn = dirNodeCheck;\n
\t\t\t}\n
\n
\t\t\tcheckFn("parentNode", part, doneName, checkSet, nodeCheck, isXML);\n
\t\t},\n
\t\t"~": function(checkSet, part, isXML){\n
\t\t\tvar doneName = done++, checkFn = dirCheck;\n
\n
\t\t\tif ( typeof part === "string" && !/\\W/.test(part) ) {\n
\t\t\t\tvar nodeCheck = part = part.toLowerCase();\n
\t\t\t\tcheckFn = dirNodeCheck;\n
\t\t\t}\n
\n
\t\t\tcheckFn("previousSibling", part, doneName, checkSet, nodeCheck, isXML);\n
\t\t}\n
\t},\n
\tfind: {\n
\t\tID: function(match, context, isXML){\n
\t\t\tif ( typeof context.getElementById !== "undefined" && !isXML ) {\n
\t\t\t\tvar m = context.getElementById(match[1]);\n
\t\t\t\treturn m ? [m] : [];\n
\t\t\t}\n
\t\t},\n
\t\tNAME: function(match, context){\n
\t\t\tif ( typeof context.getElementsByName !== "undefined" ) {\n
\t\t\t\tvar ret = [], results = context.getElementsByName(match[1]);\n
\n
\t\t\t\tfor ( var i = 0, l = results.length; i < l; i++ ) {\n
\t\t\t\t\tif ( results[i].getAttribute("name") === match[1] ) {\n
\t\t\t\t\t\tret.push( results[i] );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\treturn ret.length === 0 ? null : ret;\n
\t\t\t}\n
\t\t},\n
\t\tTAG: function(match, context){\n
\t\t\treturn context.getElementsByTagName(match[1]);\n
\t\t}\n
\t},\n
\tpreFilter: {\n
\t\tCLASS: function(match, curLoop, inplace, result, not, isXML){\n
\t\t\tmatch = " " + match[1].replace(/\\\\/g, "") + " ";\n
\n
\t\t\tif ( isXML ) {\n
\t\t\t\treturn match;\n
\t\t\t}\n
\n
\t\t\tfor ( var i = 0, elem; (elem = curLoop[i]) != null; i++ ) {\n
\t\t\t\tif ( elem ) {\n
\t\t\t\t\tif ( not ^ (elem.className && (" " + elem.className + " ").replace(/[\\t\\n]/g, " ").indexOf(match) >= 0) ) {\n
\t\t\t\t\t\tif ( !inplace ) {\n
\t\t\t\t\t\t\tresult.push( elem );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t} else if ( inplace ) {\n
\t\t\t\t\t\tcurLoop[i] = false;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\treturn false;\n
\t\t},\n
\t\tID: function(match){\n
\t\t\treturn match[1].replace(/\\\\/g, "");\n
\t\t},\n
\t\tTAG: function(match, curLoop){\n
\t\t\treturn match[1].toLowerCase();\n
\t\t},\n
\t\tCHILD: function(match){\n
\t\t\tif ( match[1] === "nth" ) {\n
\t\t\t\t// parse equations like \'even\', \'odd\', \'5\', \'2n\', \'3n+2\', \'4n-1\', \'-n+6\'\n
\t\t\t\tvar test = /(-?)(\\d*)n((?:\\+|-)?\\d*)/.exec(\n
\t\t\t\t\tmatch[2] === "even" && "2n" || match[2] === "odd" && "2n+1" ||\n
\t\t\t\t\t!/\\D/.test( match[2] ) && "0n+" + match[2] || match[2]);\n
\n
\t\t\t\t// calculate the numbers (first)n+(last) including if they are negative\n
\t\t\t\tmatch[2] = (test[1] + (test[2] || 1)) - 0;\n
\t\t\t\tmatch[3] = test[3] - 0;\n
\t\t\t}\n
\n
\t\t\t// TODO: Move to normal caching system\n
\t\t\tmatch[0] = done++;\n
\n
\t\t\treturn match;\n
\t\t},\n
\t\tATTR: function(match, curLoop, inplace, result, not, isXML){\n
\t\t\tvar name = match[1].replace(/\\\\/g, "");\n
\t\t\t\n
\t\t\tif ( !isXML && Expr.attrMap[name] ) {\n
\t\t\t\tmatch[1] = Expr.attrMap[name];\n
\t\t\t}\n
\n
\t\t\tif ( match[2] === "~=" ) {\n
\t\t\t\tmatch[4] = " " + match[4] + " ";\n
\t\t\t}\n
\n
\t\t\treturn match;\n
\t\t},\n
\t\tPSEUDO: function(match, curLoop, inplace, result, not){\n
\t\t\tif ( match[1] === "not" ) {\n
\t\t\t\t// If we\'re dealing with a complex expression, or a simple one\n
\t\t\t\tif ( ( chunker.exec(match[3]) || "" ).length > 1 || /^\\w/.test(match[3]) ) {\n
\t\t\t\t\tmatch[3] = Sizzle(match[3], null, null, curLoop);\n
\t\t\t\t} else {\n
\t\t\t\t\tvar ret = Sizzle.filter(match[3], curLoop, inplace, true ^ not);\n
\t\t\t\t\tif ( !inplace ) {\n
\t\t\t\t\t\tresult.push.apply( result, ret );\n
\t\t\t\t\t}\n
\t\t\t\t\treturn false;\n
\t\t\t\t}\n
\t\t\t} else if ( Expr.match.POS.test( match[0] ) || Expr.match.CHILD.test( match[0] ) ) {\n
\t\t\t\treturn true;\n
\t\t\t}\n
\t\t\t\n
\t\t\treturn match;\n
\t\t},\n
\t\tPOS: function(match){\n
\t\t\tmatch.unshift( true );\n
\t\t\treturn match;\n
\t\t}\n
\t},\n
\tfilters: {\n
\t\tenabled: function(elem){\n
\t\t\treturn elem.disabled === false && elem.type !== "hidden";\n
\t\t},\n
\t\tdisabled: function(elem){\n
\t\t\treturn elem.disabled === true;\n
\t\t},\n
\t\tchecked: function(elem){\n
\t\t\treturn elem.checked === true;\n
\t\t},\n
\t\tselected: function(elem){\n
\t\t\t// Accessing this property makes selected-by-default\n
\t\t\t// options in Safari work properly\n
\t\t\telem.parentNode.selectedIndex;\n
\t\t\treturn elem.selected === true;\n
\t\t},\n
\t\tparent: function(elem){\n
\t\t\treturn !!elem.firstChild;\n
\t\t},\n
\t\tempty: function(elem){\n
\t\t\treturn !elem.firstChild;\n
\t\t},\n
\t\thas: function(elem, i, match){\n
\t\t\treturn !!Sizzle( match[3], elem ).length;\n
\t\t},\n
\t\theader: function(elem){\n
\t\t\treturn /h\\d/i.test( elem.nodeName );\n
\t\t},\n
\t\ttext: function(elem){\n
\t\t\treturn "text" === elem.type;\n
\t\t},\n
\t\tradio: function(elem){\n
\t\t\treturn "radio" === elem.type;\n
\t\t},\n
\t\tcheckbox: function(elem){\n
\t\t\treturn "checkbox" === elem.type;\n
\t\t},\n
\t\tfile: function(elem){\n
\t\t\treturn "file" === elem.type;\n
\t\t},\n
\t\tpassword: function(elem){\n
\t\t\treturn "password" === elem.type;\n
\t\t},\n
\t\tsubmit: function(elem){\n
\t\t\treturn "submit" === elem.type;\n
\t\t},\n
\t\timage: function(elem){\n
\t\t\treturn "image" === elem.type;\n
\t\t},\n
\t\treset: function(elem){\n
\t\t\treturn "reset" === elem.type;\n
\t\t},\n
\t\tbutton: function(elem){\n
\t\t\treturn "button" === elem.type || elem.nodeName.toLowerCase() === "button";\n
\t\t},\n
\t\tinput: function(elem){\n
\t\t\treturn /input|select|textarea|button/i.test(elem.nodeName);\n
\t\t}\n
\t},\n
\tsetFilters: {\n
\t\tfirst: function(elem, i){\n
\t\t\treturn i === 0;\n
\t\t},\n
\t\tlast: function(elem, i, match, array){\n
\t\t\treturn i === array.length - 1;\n
\t\t},\n
\t\teven: function(elem, i){\n
\t\t\treturn i % 2 === 0;\n
\t\t},\n
\t\todd: function(elem, i){\n
\t\t\treturn i % 2 === 1;\n
\t\t},\n
\t\tlt: function(elem, i, match){\n
\t\t\treturn i < match[3] - 0;\n
\t\t},\n
\t\tgt: function(elem, i, match){\n
\t\t\treturn i > match[3] - 0;\n
\t\t},\n
\t\tnth: function(elem, i, match){\n
\t\t\treturn match[3] - 0 === i;\n
\t\t},\n
\t\teq: function(elem, i, match){\n
\t\t\treturn match[3] - 0 === i;\n
\t\t}\n
\t},\n
\tfilter: {\n
\t\tPSEUDO: function(elem, match, i, array){\n
\t\t\tvar name = match[1], filter = Expr.filters[ name ];\n
\n
\t\t\tif ( filter ) {\n
\t\t\t\treturn filter( elem, i, match, array );\n
\t\t\t} else if ( name === "contains" ) {\n
\t\t\t\treturn (elem.textContent || elem.innerText || getText([ elem ]) || "").indexOf(match[3]) >= 0;\n
\t\t\t} else if ( name === "not" ) {\n
\t\t\t\tvar not = match[3];\n
\n
\t\t\t\tfor ( var i = 0, l = not.length; i < l; i++ ) {\n
\t\t\t\t\tif ( not[i] === elem ) {\n
\t\t\t\t\t\treturn false;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\treturn true;\n
\t\t\t} else {\n
\t\t\t\tSizzle.error( "Syntax error, unrecognized expression: " + name );\n
\t\t\t}\n
\t\t},\n
\t\tCHILD: function(elem, match){\n
\t\t\tvar type = match[1], node = elem;\n
\t\t\tswitch (type) {\n
\t\t\t\tcase \'only\':\n
\t\t\t\tcase \'first\':\n
\t\t\t\t\twhile ( (node = node.previousSibling) )\t {\n
\t\t\t\t\t\tif ( node.nodeType === 1 ) { \n
\t\t\t\t\t\t\treturn false; \n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tif ( type === "first" ) { \n
\t\t\t\t\t\treturn true; \n
\t\t\t\t\t}\n
\t\t\t\t\tnode = elem;\n
\t\t\t\tcase \'last\':\n
\t\t\t\t\twhile ( (node = node.nextSibling) )\t {\n
\t\t\t\t\t\tif ( node.nodeType === 1 ) { \n
\t\t\t\t\t\t\treturn false; \n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\treturn true;\n
\t\t\t\tcase \'nth\':\n
\t\t\t\t\tvar first = match[2], last = match[3];\n
\n
\t\t\t\t\tif ( first === 1 && last === 0 ) {\n
\t\t\t\t\t\treturn true;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tvar doneName = match[0],\n
\t\t\t\t\t\tparent = elem.parentNode;\n
\t\n
\t\t\t\t\tif ( parent && (parent.sizcache !== doneName || !elem.nodeIndex) ) {\n
\t\t\t\t\t\tvar count = 0;\n
\t\t\t\t\t\tfor ( node = parent.firstChild; node; node = node.nextSibling ) {\n
\t\t\t\t\t\t\tif ( node.nodeType === 1 ) {\n
\t\t\t\t\t\t\t\tnode.nodeIndex = ++count;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t} \n
\t\t\t\t\t\tparent.sizcache = doneName;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tvar diff = elem.nodeIndex - last;\n
\t\t\t\t\tif ( first === 0 ) {\n
\t\t\t\t\t\treturn diff === 0;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\treturn ( diff % first === 0 && diff / first >= 0 );\n
\t\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\tID: function(elem, match){\n
\t\t\treturn elem.nodeType === 1 && elem.getAttribute("id") === match;\n
\t\t},\n
\t\tTAG: function(elem, match){\n
\t\t\treturn (match === "*" && elem.nodeType === 1) || elem.nodeName.toLowerCase() === match;\n
\t\t},\n
\t\tCLASS: function(elem, match){\n
\t\t\treturn (" " + (elem.className || elem.getAttribute("class")) + " ")\n
\t\t\t\t.indexOf( match ) > -1;\n
\t\t},\n
\t\tATTR: function(elem, match){\n
\t\t\tvar name = match[1],\n
\t\t\t\tresult = Expr.attrHandle[ name ] ?\n
\t\t\t\t\tExpr.attrHandle[ name ]( elem ) :\n
\t\t\t\t\telem[ name ] != null ?\n
\t\t\t\t\t\telem[ name ] :\n
\t\t\t\t\t\telem.getAttribute( name ),\n
\t\t\t\tvalue = result + "",\n
\t\t\t\ttype = match[2],\n
\t\t\t\tcheck = match[4];\n
\n
\t\t\treturn result == null ?\n
\t\t\t\ttype === "!=" :\n
\t\t\t\ttype === "=" ?\n
\t\t\t\tvalue === check :\n
\t\t\t\ttype === "*=" ?\n
\t\t\t\tvalue.indexOf(check) >= 0 :\n
\t\t\t\ttype === "~=" ?\n
\t\t\t\t(" " + value + " ").indexOf(check) >= 0 :\n
\t\t\t\t!check ?\n
\t\t\t\tvalue && result !== false :\n
\t\t\t\ttype === "!=" ?\n
\t\t\t\tvalue !== check :\n
\t\t\t\ttype === "^=" ?\n
\t\t\t\tvalue.indexOf(check) === 0 :\n
\t\t\t\ttype === "$=" ?\n
\t\t\t\tvalue.substr(value.length - check.length) === check :\n
\t\t\t\ttype === "|=" ?\n
\t\t\t\tvalue === check || value.substr(0, check.length + 1) === check + "-" :\n
\t\t\t\tfalse;\n
\t\t},\n
\t\tPOS: function(elem, match, i, array){\n
\t\t\tvar name = match[2], filter = Expr.setFilters[ name ];\n
\n
\t\t\tif ( filter ) {\n
\t\t\t\treturn filter( elem, i, match, array );\n
\t\t\t}\n
\t\t}\n
\t}\n
};\n
\n
var origPOS = Expr.match.POS;\n
\n
for ( var type in Expr.match ) {\n
\tExpr.match[ type ] = new RegExp( Expr.match[ type ].source + /(?![^\\[]*\\])(?![^\\(]*\\))/.source );\n
\tExpr.leftMatch[ type ] = new RegExp( /(^(?:.|\\r|\\n)*?)/.source + Expr.match[ type ].source.replace(/\\\\(\\d+)/g, function(all, num){\n
\t\treturn "\\\\" + (num - 0 + 1);\n
\t}));\n
}\n
\n
var makeArray = function(array, results) {\n
\tarray = Array.prototype.slice.call( array, 0 );\n
\n
\tif ( results ) {\n
\t\tresults.push.apply( results, array );\n
\t\treturn results;\n
\t}\n
\t\n
\treturn array;\n
};\n
\n
// Perform a simple check to determine if the browser is capable of\n
// converting a NodeList to an array using builtin methods.\n
// Also verifies that the returned array holds DOM nodes\n
// (which is not the case in the Blackberry browser)\n
try {\n
\tArray.prototype.slice.call( document.documentElement.childNodes, 0 )[0].nodeType;\n
\n
// Provide a fallback method if it does not work\n
} catch(e){\n
\tmakeArray = function(array, results) {\n
\t\tvar ret = results || [];\n
\n
\t\tif ( toString.call(array) === "[object Array]" ) {\n
\t\t\tArray.prototype.push.apply( ret, array );\n
\t\t} else {\n
\t\t\tif ( typeof array.length === "number" ) {\n
\t\t\t\tfor ( var i = 0, l = array.length; i < l; i++ ) {\n
\t\t\t\t\tret.push( array[i] );\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tfor ( var i = 0; array[i]; i++ ) {\n
\t\t\t\t\tret.push( array[i] );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn ret;\n
\t};\n
}\n
\n
var sortOrder;\n
\n
if ( document.documentElement.compareDocumentPosition ) {\n
\tsortOrder = function( a, b ) {\n
\t\tif ( !a.compareDocumentPosition || !b.compareDocumentPosition ) {\n
\t\t\tif ( a == b ) {\n
\t\t\t\thasDuplicate = true;\n
\t\t\t}\n
\t\t\treturn a.compareDocumentPosition ? -1 : 1;\n
\t\t}\n
\n
\t\tvar ret = a.compareDocumentPosition(b) & 4 ? -1 : a === b ? 0 : 1;\n
\t\tif ( ret === 0 ) {\n
\t\t\thasDuplicate = true;\n
\t\t}\n
\t\treturn ret;\n
\t};\n
} else if ( "sourceIndex" in document.documentElement ) {\n
\tsortOrder = function( a, b ) {\n
\t\tif ( !a.sourceIndex || !b.sourceIndex ) {\n
\t\t\tif ( a == b ) {\n
\t\t\t\thasDuplicate = true;\n
\t\t\t}\n
\t\t\treturn a.sourceIndex ? -1 : 1;\n
\t\t}\n
\n
\t\tvar ret = a.sourceIndex - b.sourceIndex;\n
\t\tif ( ret === 0 ) {\n
\t\t\thasDuplicate = true;\n
\t\t}\n
\t\treturn ret;\n
\t};\n
} else if ( document.createRange ) {\n
\tsortOrder = function( a, b ) {\n
\t\tif ( !a.ownerDocument || !b.ownerDocument ) {\n
\t\t\tif ( a == b ) {\n
\t\t\t\thasDuplicate = true;\n
\t\t\t}\n
\t\t\treturn a.ownerDocument ? -1 : 1;\n
\t\t}\n
\n
\t\tvar aRange = a.ownerDocument.createRange(), bRange = b.ownerDocument.createRange();\n
\t\taRange.setStart(a, 0);\n
\t\taRange.setEnd(a, 0);\n
\t\tbRange.setStart(b, 0);\n
\t\tbRange.setEnd(b, 0);\n
\t\tvar ret = aRange.compareBoundaryPoints(Range.START_TO_END, bRange);\n
\t\tif ( ret === 0 ) {\n
\t\t\thasDuplicate = true;\n
\t\t}\n
\t\treturn ret;\n
\t};\n
}\n
\n
// Utility function for retreiving the text value of an array of DOM nodes\n
function getText( elems ) {\n
\tvar ret = "", elem;\n
\n
\tfor ( var i = 0; elems[i]; i++ ) {\n
\t\telem = elems[i];\n
\n
\t\t// Get the text from text nodes and CDATA nodes\n
\t\tif ( elem.nodeType === 3 || elem.nodeType === 4 ) {\n
\t\t\tret += elem.nodeValue;\n
\n
\t\t// Traverse everything else, except comment nodes\n
\t\t} else if ( elem.nodeType !== 8 ) {\n
\t\t\tret += getText( elem.childNodes );\n
\t\t}\n
\t}\n
\n
\treturn ret;\n
}\n
\n
// Check to see if the browser returns elements by name when\n
// querying by getElementById (and provide a workaround)\n
(function(){\n
\t// We\'re going to inject a fake input element with a specified name\n
\tvar form = document.createElement("div"),\n
\t\tid = "script" + (new Date).getTime();\n
\tform.innerHTML = "<a name=\'" + id + "\'/>";\n
\n
\t// Inject it into the root element, check its status, and remove it quickly\n
\tvar root = document.documentElement;\n
\troot.insertBefore( form, root.firstChild );\n
\n
\t// The workaround has to do additional checks after a getElementById\n
\t// Which slows things down for other browsers (hence the branching)\n
\tif ( document.getElementById( id ) ) {\n
\t\tExpr.find.ID = function(match, context, isXML){\n
\t\t\tif ( typeof context.getElementById !== "undefined" && !isXML ) {\n
\t\t\t\tvar m = context.getElementById(match[1]);\n
\t\t\t\treturn m ? m.id === match[1] || typeof m.getAttributeNode !== "undefined" && m.getAttributeNode("id").nodeValue === match[1] ? [m] : undefined : [];\n
\t\t\t}\n
\t\t};\n
\n
\t\tExpr.filter.ID = function(elem, match){\n
\t\t\tvar node = typeof elem.getAttributeNode !== "undefined" && elem.getAttributeNode("id");\n
\t\t\treturn elem.nodeType === 1 && node && node.nodeValue === match;\n
\t\t};\n
\t}\n
\n
\troot.removeChild( form );\n
\troot = form = null; // release memory in IE\n
})();\n
\n
(function(){\n
\t// Check to see if the browser returns only elements\n
\t// when doing getElementsByTagName("*")\n
\n
\t// Create a fake element\n
\tvar div = document.createElement("div");\n
\tdiv.appendChild( document.createComment("") );\n
\n
\t// Make sure no comments are found\n
\tif ( div.getElementsByTagName("*").length > 0 ) {\n
\t\tExpr.find.TAG = function(match, context){\n
\t\t\tvar results = context.getElementsByTagName(match[1]);\n
\n
\t\t\t// Filter out possible comments\n
\t\t\tif ( match[1] === "*" ) {\n
\t\t\t\tvar tmp = [];\n
\n
\t\t\t\tfor ( var i = 0; results[i]; i++ ) {\n
\t\t\t\t\tif ( results[i].nodeType === 1 ) {\n
\t\t\t\t\t\ttmp.push( results[i] );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tresults = tmp;\n
\t\t\t}\n
\n
\t\t\treturn results;\n
\t\t};\n
\t}\n
\n
\t// Check to see if an attribute returns normalized href attributes\n
\tdiv.innerHTML = "<a href=\'#\'></a>";\n
\tif ( div.firstChild && typeof div.firstChild.getAttribute !== "undefined" &&\n
\t\t\tdiv.firstChild.getAttribute("href") !== "#" ) {\n
\t\tExpr.attrHandle.href = function(elem){\n
\t\t\treturn elem.getAttribute("href", 2);\n
\t\t};\n
\t}\n
\n
\tdiv = null; // release memory in IE\n
})();\n
\n
if ( document.querySelectorAll ) {\n
\t(function(){\n
\t\tvar oldSizzle = Sizzle, div = document.createElement("div");\n
\t\tdiv.innerHTML = "<p class=\'TEST\'></p>";\n
\n
\t\t// Safari can\'t handle uppercase or unicode characters when\n
\t\t// in quirks mode.\n
\t\tif ( div.querySelectorAll && div.querySelectorAll(".TEST").length === 0 ) {\n
\t\t\treturn;\n
\t\t}\n
\t\n
\t\tSizzle = function(query, context, extra, seed){\n
\t\t\tcontext = context || document;\n
\n
\t\t\t// Only use querySelectorAll on non-XML documents\n
\t\t\t// (ID selectors don\'t work in non-HTML documents)\n
\t\t\tif ( !seed && context.nodeType === 9 && !isXML(context) ) {\n
\t\t\t\ttry {\n
\t\t\t\t\treturn makeArray( context.querySelectorAll(query), extra );\n
\t\t\t\t} catch(e){}\n
\t\t\t}\n
\t\t\n
\t\t\treturn oldSizzle(query, context, extra, seed);\n
\t\t};\n
\n
\t\tfor ( var prop in oldSizzle ) {\n
\t\t\tSizzle[ prop ] = oldSizzle[ prop ];\n
\t\t}\n
\n
\t\tdiv = null; // release memory in IE\n
\t})();\n
}\n
\n
(function(){\n
\tvar div = document.createElement("div");\n
\n
\tdiv.innerHTML = "<div class=\'test e\'></div><div class=\'test\'></div>";\n
\n
\t// Opera can\'t find a second classname (in 9.6)\n
\t// Also, make sure that getElementsByClassName actually exists\n
\tif ( !div.getElementsByClassName || div.getElementsByClassName("e").length === 0 ) {\n
\t\treturn;\n
\t}\n
\n
\t// Safari caches class attributes, doesn\'t catch changes (in 3.2)\n
\tdiv.lastChild.className = "e";\n
\n
\tif ( div.getElementsByClassName("e").length === 1 ) {\n
\t\treturn;\n
\t}\n
\t\n
\tExpr.order.splice(1, 0, "CLASS");\n
\tExpr.find.CLASS = function(match, context, isXML) {\n
\t\tif ( typeof context.getElementsByClassName !== "undefined" && !isXML ) {\n
\t\t\treturn context.getElementsByClassName(match[1]);\n
\t\t}\n
\t};\n
\n
\tdiv = null; // release memory in IE\n
})();\n
\n
function dirNodeCheck( dir, cur, doneName, checkSet, nodeCheck, isXML ) {\n
\tfor ( var i = 0, l = checkSet.length; i < l; i++ ) {\n
\t\tvar elem = checkSet[i];\n
\t\tif ( elem ) {\n
\t\t\telem = elem[dir];\n
\t\t\tvar match = false;\n
\n
\t\t\twhile ( elem ) {\n
\t\t\t\tif ( elem.sizcache === doneName ) {\n
\t\t\t\t\tmatch = checkSet[elem.sizset];\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\n
\t\t\t\tif ( elem.nodeType === 1 && !isXML ){\n
\t\t\t\t\telem.sizcache = doneName;\n
\t\t\t\t\telem.sizset = i;\n
\t\t\t\t}\n
\n
\t\t\t\tif ( elem.nodeName.toLowerCase() === cur ) {\n
\t\t\t\t\tmatch = elem;\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\n
\t\t\t\telem = elem[dir];\n
\t\t\t}\n
\n
\t\t\tcheckSet[i] = match;\n
\t\t}\n
\t}\n
}\n
\n
function dirCheck( dir, cur, doneName, checkSet, nodeCheck, isXML ) {\n
\tfor ( var i = 0, l = checkSet.length; i < l; i++ ) {\n
\t\tvar elem = checkSet[i];\n
\t\tif ( elem ) {\n
\t\t\telem = elem[dir];\n
\t\t\tvar match = false;\n
\n
\t\t\twhile ( elem ) {\n
\t\t\t\tif ( elem.sizcache === doneName ) {\n
\t\t\t\t\tmatch = checkSet[elem.sizset];\n
\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\n
\t\t\t\tif ( elem.nodeType === 1 ) {\n
\t\t\t\t\tif ( !isXML ) {\n
\t\t\t\t\t\telem.sizcache = doneName;\n
\t\t\t\t\t\telem.sizset = i;\n
\t\t\t\t\t}\n
\t\t\t\t\tif ( typeof cur !== "string" ) {\n
\t\t\t\t\t\tif ( elem === cur ) {\n
\t\t\t\t\t\t\tmatch = true;\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t} else if ( Sizzle.filter( cur, [elem] ).length > 0 ) {\n
\t\t\t\t\t\tmatch = elem;\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\telem = elem[dir];\n
\t\t\t}\n
\n
\t\t\tcheckSet[i] = match;\n
\t\t}\n
\t}\n
}\n
\n
var contains = document.compareDocumentPosition ? function(a, b){\n
\treturn !!(a.compareDocumentPosition(b) & 16);\n
} : function(a, b){\n
\treturn a !== b && (a.contains ? a.contains(b) : true);\n
};\n
\n
var isXML = function(elem){\n
\t// documentElement is verified for cases where it doesn\'t yet exist\n
\t// (such as loading iframes in IE - #4833) \n
\tvar documentElement = (elem ? elem.ownerDocument || elem : 0).documentElement;\n
\treturn documentElement ? documentElement.nodeName !== "HTML" : false;\n
};\n
\n
var posProcess = function(selector, context){\n
\tvar tmpSet = [], later = "", match,\n
\t\troot = context.nodeType ? [context] : context;\n
\n
\t// Position selectors must be done after the filter\n
\t// And so must :not(positional) so we move all PSEUDOs to the end\n
\twhile ( (match = Expr.match.PSEUDO.exec( selector )) ) {\n
\t\tlater += match[0];\n
\t\tselector = selector.replace( Expr.match.PSEUDO, "" );\n
\t}\n
\n
\tselector = Expr.relative[selector] ? selector + "*" : selector;\n
\n
\tfor ( var i = 0, l = root.length; i < l; i++ ) {\n
\t\tSizzle( selector, root[i], tmpSet );\n
\t}\n
\n
\treturn Sizzle.filter( later, tmpSet );\n
};\n
\n
// EXPOSE\n
jQuery.find = Sizzle;\n
jQuery.expr = Sizzle.selectors;\n
jQuery.expr[":"] = jQuery.expr.filters;\n
jQuery.unique = Sizzle.uniqueSort;\n
jQuery.text = getText;\n
jQuery.isXMLDoc = isXML;\n
jQuery.contains = contains;\n
\n
return;\n
\n
window.Sizzle = Sizzle;\n
\n
})();\n
var runtil = /Until$/,\n
\trparentsprev = /^(?:parents|prevUntil|prevAll)/,\n
\t// Note: This RegExp should be improved, or likely pulled from Sizzle\n
\trmultiselector = /,/,\n
\tslice = Array.prototype.slice;\n
\n
// Implement the identical functionality for filter and not\n
var winnow = function( elements, qualifier, keep ) {\n
\tif ( jQuery.isFunction( qualifier ) ) {\n
\t\treturn jQuery.grep(elements, function( elem, i ) {\n
\t\t\treturn !!qualifier.call( elem, i, elem ) === keep;\n
\t\t});\n
\n
\t} else if ( qualifier.nodeType ) {\n
\t\treturn jQuery.grep(elements, function( elem, i ) {\n
\t\t\treturn (elem === qualifier) === keep;\n
\t\t});\n
\n
\t} else if ( typeof qualifier === "string" ) {\n
\t\tvar filtered = jQuery.grep(elements, function( elem ) {\n
\t\t\treturn elem.nodeType === 1;\n
\t\t});\n
\n
\t\tif ( isSimple.test( qualifier ) ) {\n
\t\t\treturn jQuery.filter(qualifier, filtered, !keep);\n
\t\t} else {\n
\t\t\tqualifier = jQuery.filter( qualifier, filtered );\n
\t\t}\n
\t}\n
\n
\treturn jQuery.grep(elements, function( elem, i ) {\n
\t\treturn (jQuery.inArray( elem, qualifier ) >= 0) === keep;\n
\t});\n
};\n
\n
jQuery.fn.extend({\n
\tfind: function( selector ) {\n
\t\tvar ret = this.pushStack( "", "find", selector ), length = 0;\n
\n
\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\tlength = ret.length;\n
\t\t\tjQuery.find( selector, this[i], ret );\n
\n
\t\t\tif ( i > 0 ) {\n
\t\t\t\t// Make sure that the results are unique\n
\t\t\t\tfor ( var n = length; n < ret.length; n++ ) {\n
\t\t\t\t\tfor ( var r = 0; r < length; r++ ) {\n
\t\t\t\t\t\tif ( ret[r] === ret[n] ) {\n
\t\t\t\t\t\t\tret.splice(n--, 1);\n
\t\t\t\t\t\t\tbreak;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn ret;\n
\t},\n
\n
\thas: function( target ) {\n
\t\tvar targets = jQuery( target );\n
\t\treturn this.filter(function() {\n
\t\t\tfor ( var i = 0, l = targets.length; i < l; i++ ) {\n
\t\t\t\tif ( jQuery.contains( this, targets[i] ) ) {\n
\t\t\t\t\treturn true;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\tnot: function( selector ) {\n
\t\treturn this.pushStack( winnow(this, selector, false), "not", selector);\n
\t},\n
\n
\tfilter: function( selector ) {\n
\t\treturn this.pushStack( winnow(this, selector, true), "filter", selector );\n
\t},\n
\t\n
\tis: function( selector ) {\n
\t\treturn !!selector && jQuery.filter( selector, this ).length > 0;\n
\t},\n
\n
\tclosest: function( selectors, context ) {\n
\t\tif ( jQuery.isArray( selectors ) ) {\n
\t\t\tvar ret = [], cur = this[0], match, matches = {}, selector;\n
\n
\t\t\tif ( cur && selectors.length ) {\n
\t\t\t\tfor ( var i = 0, l = selectors.length; i < l; i++ ) {\n
\t\t\t\t\tselector = selectors[i];\n
\n
\t\t\t\t\tif ( !matches[selector] ) {\n
\t\t\t\t\t\tmatches[selector] = jQuery.expr.match.POS.test( selector ) ? \n
\t\t\t\t\t\t\tjQuery( selector, context || this.context ) :\n
\t\t\t\t\t\t\tselector;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\twhile ( cur && cur.ownerDocument && cur !== context ) {\n
\t\t\t\t\tfor ( selector in matches ) {\n
\t\t\t\t\t\tmatch = matches[selector];\n
\n
\t\t\t\t\t\tif ( match.jquery ? match.index(cur) > -1 : jQuery(cur).is(match) ) {\n
\t\t\t\t\t\t\tret.push({ selector: selector, elem: cur });\n
\t\t\t\t\t\t\tdelete matches[selector];\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t\tcur = cur.parentNode;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\treturn ret;\n
\t\t}\n
\n
\t\tvar pos = jQuery.expr.match.POS.test( selectors ) ? \n
\t\t\tjQuery( selectors, context || this.context ) : null;\n
\n
\t\treturn this.map(function( i, cur ) {\n
\t\t\twhile ( cur && cur.ownerDocument && cur !== context ) {\n
\t\t\t\tif ( pos ? pos.index(cur) > -1 : jQuery(cur).is(selectors) ) {\n
\t\t\t\t\treturn cur;\n
\t\t\t\t}\n
\t\t\t\tcur = cur.parentNode;\n
\t\t\t}\n
\t\t\treturn null;\n
\t\t});\n
\t},\n
\t\n
\t// Determine the position of an element within\n
\t// the matched set of elements\n
\tindex: function( elem ) {\n
\t\tif ( !elem || typeof elem === "string" ) {\n
\t\t\treturn jQuery.inArray( this[0],\n
\t\t\t\t// If it receives a string, the selector is used\n
\t\t\t\t// If it receives nothing, the siblings are used\n
\t\t\t\telem ? jQ

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
            <value> <string encoding="cdata"><![CDATA[

uery( elem ) : this.parent().children() );\n
\t\t}\n
\t\t// Locate the position of the desired element\n
\t\treturn jQuery.inArray(\n
\t\t\t// If it receives a jQuery object, the first element is used\n
\t\t\telem.jquery ? elem[0] : elem, this );\n
\t},\n
\n
\tadd: function( selector, context ) {\n
\t\tvar set = typeof selector === "string" ?\n
\t\t\t\tjQuery( selector, context || this.context ) :\n
\t\t\t\tjQuery.makeArray( selector ),\n
\t\t\tall = jQuery.merge( this.get(), set );\n
\n
\t\treturn this.pushStack( isDisconnected( set[0] ) || isDisconnected( all[0] ) ?\n
\t\t\tall :\n
\t\t\tjQuery.unique( all ) );\n
\t},\n
\n
\tandSelf: function() {\n
\t\treturn this.add( this.prevObject );\n
\t}\n
});\n
\n
// A painfully simple check to see if an element is disconnected\n
// from a document (should be improved, where feasible).\n
function isDisconnected( node ) {\n
\treturn !node || !node.parentNode || node.parentNode.nodeType === 11;\n
}\n
\n
jQuery.each({\n
\tparent: function( elem ) {\n
\t\tvar parent = elem.parentNode;\n
\t\treturn parent && parent.nodeType !== 11 ? parent : null;\n
\t},\n
\tparents: function( elem ) {\n
\t\treturn jQuery.dir( elem, "parentNode" );\n
\t},\n
\tparentsUntil: function( elem, i, until ) {\n
\t\treturn jQuery.dir( elem, "parentNode", until );\n
\t},\n
\tnext: function( elem ) {\n
\t\treturn jQuery.nth( elem, 2, "nextSibling" );\n
\t},\n
\tprev: function( elem ) {\n
\t\treturn jQuery.nth( elem, 2, "previousSibling" );\n
\t},\n
\tnextAll: function( elem ) {\n
\t\treturn jQuery.dir( elem, "nextSibling" );\n
\t},\n
\tprevAll: function( elem ) {\n
\t\treturn jQuery.dir( elem, "previousSibling" );\n
\t},\n
\tnextUntil: function( elem, i, until ) {\n
\t\treturn jQuery.dir( elem, "nextSibling", until );\n
\t},\n
\tprevUntil: function( elem, i, until ) {\n
\t\treturn jQuery.dir( elem, "previousSibling", until );\n
\t},\n
\tsiblings: function( elem ) {\n
\t\treturn jQuery.sibling( elem.parentNode.firstChild, elem );\n
\t},\n
\tchildren: function( elem ) {\n
\t\treturn jQuery.sibling( elem.firstChild );\n
\t},\n
\tcontents: function( elem ) {\n
\t\treturn jQuery.nodeName( elem, "iframe" ) ?\n
\t\t\telem.contentDocument || elem.contentWindow.document :\n
\t\t\tjQuery.makeArray( elem.childNodes );\n
\t}\n
}, function( name, fn ) {\n
\tjQuery.fn[ name ] = function( until, selector ) {\n
\t\tvar ret = jQuery.map( this, fn, until );\n
\t\t\n
\t\tif ( !runtil.test( name ) ) {\n
\t\t\tselector = until;\n
\t\t}\n
\n
\t\tif ( selector && typeof selector === "string" ) {\n
\t\t\tret = jQuery.filter( selector, ret );\n
\t\t}\n
\n
\t\tret = this.length > 1 ? jQuery.unique( ret ) : ret;\n
\n
\t\tif ( (this.length > 1 || rmultiselector.test( selector )) && rparentsprev.test( name ) ) {\n
\t\t\tret = ret.reverse();\n
\t\t}\n
\n
\t\treturn this.pushStack( ret, name, slice.call(arguments).join(",") );\n
\t};\n
});\n
\n
jQuery.extend({\n
\tfilter: function( expr, elems, not ) {\n
\t\tif ( not ) {\n
\t\t\texpr = ":not(" + expr + ")";\n
\t\t}\n
\n
\t\treturn jQuery.find.matches(expr, elems);\n
\t},\n
\t\n
\tdir: function( elem, dir, until ) {\n
\t\tvar matched = [], cur = elem[dir];\n
\t\twhile ( cur && cur.nodeType !== 9 && (until === undefined || cur.nodeType !== 1 || !jQuery( cur ).is( until )) ) {\n
\t\t\tif ( cur.nodeType === 1 ) {\n
\t\t\t\tmatched.push( cur );\n
\t\t\t}\n
\t\t\tcur = cur[dir];\n
\t\t}\n
\t\treturn matched;\n
\t},\n
\n
\tnth: function( cur, result, dir, elem ) {\n
\t\tresult = result || 1;\n
\t\tvar num = 0;\n
\n
\t\tfor ( ; cur; cur = cur[dir] ) {\n
\t\t\tif ( cur.nodeType === 1 && ++num === result ) {\n
\t\t\t\tbreak;\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn cur;\n
\t},\n
\n
\tsibling: function( n, elem ) {\n
\t\tvar r = [];\n
\n
\t\tfor ( ; n; n = n.nextSibling ) {\n
\t\t\tif ( n.nodeType === 1 && n !== elem ) {\n
\t\t\t\tr.push( n );\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn r;\n
\t}\n
});\n
var rinlinejQuery = / jQuery\\d+="(?:\\d+|null)"/g,\n
\trleadingWhitespace = /^\\s+/,\n
\trxhtmlTag = /(<([\\w:]+)[^>]*?)\\/>/g,\n
\trselfClosing = /^(?:area|br|col|embed|hr|img|input|link|meta|param)$/i,\n
\trtagName = /<([\\w:]+)/,\n
\trtbody = /<tbody/i,\n
\trhtml = /<|&#?\\w+;/,\n
\trnocache = /<script|<object|<embed|<option|<style/i,\n
\trchecked = /checked\\s*(?:[^=]|=\\s*.checked.)/i,  // checked="checked" or checked (html5)\n
\tfcloseTag = function( all, front, tag ) {\n
\t\treturn rselfClosing.test( tag ) ?\n
\t\t\tall :\n
\t\t\tfront + "></" + tag + ">";\n
\t},\n
\twrapMap = {\n
\t\toption: [ 1, "<select multiple=\'multiple\'>", "</select>" ],\n
\t\tlegend: [ 1, "<fieldset>", "</fieldset>" ],\n
\t\tthead: [ 1, "<table>", "</table>" ],\n
\t\ttr: [ 2, "<table><tbody>", "</tbody></table>" ],\n
\t\ttd: [ 3, "<table><tbody><tr>", "</tr></tbody></table>" ],\n
\t\tcol: [ 2, "<table><tbody></tbody><colgroup>", "</colgroup></table>" ],\n
\t\tarea: [ 1, "<map>", "</map>" ],\n
\t\t_default: [ 0, "", "" ]\n
\t};\n
\n
wrapMap.optgroup = wrapMap.option;\n
wrapMap.tbody = wrapMap.tfoot = wrapMap.colgroup = wrapMap.caption = wrapMap.thead;\n
wrapMap.th = wrapMap.td;\n
\n
// IE can\'t serialize <link> and <script> tags normally\n
if ( !jQuery.support.htmlSerialize ) {\n
\twrapMap._default = [ 1, "div<div>", "</div>" ];\n
}\n
\n
jQuery.fn.extend({\n
\ttext: function( text ) {\n
\t\tif ( jQuery.isFunction(text) ) {\n
\t\t\treturn this.each(function(i) {\n
\t\t\t\tvar self = jQuery(this);\n
\t\t\t\tself.text( text.call(this, i, self.text()) );\n
\t\t\t});\n
\t\t}\n
\n
\t\tif ( typeof text !== "object" && text !== undefined ) {\n
\t\t\treturn this.empty().append( (this[0] && this[0].ownerDocument || document).createTextNode( text ) );\n
\t\t}\n
\n
\t\treturn jQuery.text( this );\n
\t},\n
\n
\twrapAll: function( html ) {\n
\t\tif ( jQuery.isFunction( html ) ) {\n
\t\t\treturn this.each(function(i) {\n
\t\t\t\tjQuery(this).wrapAll( html.call(this, i) );\n
\t\t\t});\n
\t\t}\n
\n
\t\tif ( this[0] ) {\n
\t\t\t// The elements to wrap the target around\n
\t\t\tvar wrap = jQuery( html, this[0].ownerDocument ).eq(0).clone(true);\n
\n
\t\t\tif ( this[0].parentNode ) {\n
\t\t\t\twrap.insertBefore( this[0] );\n
\t\t\t}\n
\n
\t\t\twrap.map(function() {\n
\t\t\t\tvar elem = this;\n
\n
\t\t\t\twhile ( elem.firstChild && elem.firstChild.nodeType === 1 ) {\n
\t\t\t\t\telem = elem.firstChild;\n
\t\t\t\t}\n
\n
\t\t\t\treturn elem;\n
\t\t\t}).append(this);\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\n
\twrapInner: function( html ) {\n
\t\tif ( jQuery.isFunction( html ) ) {\n
\t\t\treturn this.each(function(i) {\n
\t\t\t\tjQuery(this).wrapInner( html.call(this, i) );\n
\t\t\t});\n
\t\t}\n
\n
\t\treturn this.each(function() {\n
\t\t\tvar self = jQuery( this ), contents = self.contents();\n
\n
\t\t\tif ( contents.length ) {\n
\t\t\t\tcontents.wrapAll( html );\n
\n
\t\t\t} else {\n
\t\t\t\tself.append( html );\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\twrap: function( html ) {\n
\t\treturn this.each(function() {\n
\t\t\tjQuery( this ).wrapAll( html );\n
\t\t});\n
\t},\n
\n
\tunwrap: function() {\n
\t\treturn this.parent().each(function() {\n
\t\t\tif ( !jQuery.nodeName( this, "body" ) ) {\n
\t\t\t\tjQuery( this ).replaceWith( this.childNodes );\n
\t\t\t}\n
\t\t}).end();\n
\t},\n
\n
\tappend: function() {\n
\t\treturn this.domManip(arguments, true, function( elem ) {\n
\t\t\tif ( this.nodeType === 1 ) {\n
\t\t\t\tthis.appendChild( elem );\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\tprepend: function() {\n
\t\treturn this.domManip(arguments, true, function( elem ) {\n
\t\t\tif ( this.nodeType === 1 ) {\n
\t\t\t\tthis.insertBefore( elem, this.firstChild );\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\tbefore: function() {\n
\t\tif ( this[0] && this[0].parentNode ) {\n
\t\t\treturn this.domManip(arguments, false, function( elem ) {\n
\t\t\t\tthis.parentNode.insertBefore( elem, this );\n
\t\t\t});\n
\t\t} else if ( arguments.length ) {\n
\t\t\tvar set = jQuery(arguments[0]);\n
\t\t\tset.push.apply( set, this.toArray() );\n
\t\t\treturn this.pushStack( set, "before", arguments );\n
\t\t}\n
\t},\n
\n
\tafter: function() {\n
\t\tif ( this[0] && this[0].parentNode ) {\n
\t\t\treturn this.domManip(arguments, false, function( elem ) {\n
\t\t\t\tthis.parentNode.insertBefore( elem, this.nextSibling );\n
\t\t\t});\n
\t\t} else if ( arguments.length ) {\n
\t\t\tvar set = this.pushStack( this, "after", arguments );\n
\t\t\tset.push.apply( set, jQuery(arguments[0]).toArray() );\n
\t\t\treturn set;\n
\t\t}\n
\t},\n
\t\n
\t// keepData is for internal use only--do not document\n
\tremove: function( selector, keepData ) {\n
\t\tfor ( var i = 0, elem; (elem = this[i]) != null; i++ ) {\n
\t\t\tif ( !selector || jQuery.filter( selector, [ elem ] ).length ) {\n
\t\t\t\tif ( !keepData && elem.nodeType === 1 ) {\n
\t\t\t\t\tjQuery.cleanData( elem.getElementsByTagName("*") );\n
\t\t\t\t\tjQuery.cleanData( [ elem ] );\n
\t\t\t\t}\n
\n
\t\t\t\tif ( elem.parentNode ) {\n
\t\t\t\t\t elem.parentNode.removeChild( elem );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\treturn this;\n
\t},\n
\n
\tempty: function() {\n
\t\tfor ( var i = 0, elem; (elem = this[i]) != null; i++ ) {\n
\t\t\t// Remove element nodes and prevent memory leaks\n
\t\t\tif ( elem.nodeType === 1 ) {\n
\t\t\t\tjQuery.cleanData( elem.getElementsByTagName("*") );\n
\t\t\t}\n
\n
\t\t\t// Remove any remaining nodes\n
\t\t\twhile ( elem.firstChild ) {\n
\t\t\t\telem.removeChild( elem.firstChild );\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\treturn this;\n
\t},\n
\n
\tclone: function( events ) {\n
\t\t// Do the clone\n
\t\tvar ret = this.map(function() {\n
\t\t\tif ( !jQuery.support.noCloneEvent && !jQuery.isXMLDoc(this) ) {\n
\t\t\t\t// IE copies events bound via attachEvent when\n
\t\t\t\t// using cloneNode. Calling detachEvent on the\n
\t\t\t\t// clone will also remove the events from the orignal\n
\t\t\t\t// In order to get around this, we use innerHTML.\n
\t\t\t\t// Unfortunately, this means some modifications to\n
\t\t\t\t// attributes in IE that are actually only stored\n
\t\t\t\t// as properties will not be copied (such as the\n
\t\t\t\t// the name attribute on an input).\n
\t\t\t\tvar html = this.outerHTML, ownerDocument = this.ownerDocument;\n
\t\t\t\tif ( !html ) {\n
\t\t\t\t\tvar div = ownerDocument.createElement("div");\n
\t\t\t\t\tdiv.appendChild( this.cloneNode(true) );\n
\t\t\t\t\thtml = div.innerHTML;\n
\t\t\t\t}\n
\n
\t\t\t\treturn jQuery.clean([html.replace(rinlinejQuery, "")\n
\t\t\t\t\t// Handle the case in IE 8 where action=/test/> self-closes a tag\n
\t\t\t\t\t.replace(/=([^="\'>\\s]+\\/)>/g, \'="$1">\')\n
\t\t\t\t\t.replace(rleadingWhitespace, "")], ownerDocument)[0];\n
\t\t\t} else {\n
\t\t\t\treturn this.cloneNode(true);\n
\t\t\t}\n
\t\t});\n
\n
\t\t// Copy the events from the original to the clone\n
\t\tif ( events === true ) {\n
\t\t\tcloneCopyEvent( this, ret );\n
\t\t\tcloneCopyEvent( this.find("*"), ret.find("*") );\n
\t\t}\n
\n
\t\t// Return the cloned set\n
\t\treturn ret;\n
\t},\n
\n
\thtml: function( value ) {\n
\t\tif ( value === undefined ) {\n
\t\t\treturn this[0] && this[0].nodeType === 1 ?\n
\t\t\t\tthis[0].innerHTML.replace(rinlinejQuery, "") :\n
\t\t\t\tnull;\n
\n
\t\t// See if we can take a shortcut and just use innerHTML\n
\t\t} else if ( typeof value === "string" && !rnocache.test( value ) &&\n
\t\t\t(jQuery.support.leadingWhitespace || !rleadingWhitespace.test( value )) &&\n
\t\t\t!wrapMap[ (rtagName.exec( value ) || ["", ""])[1].toLowerCase() ] ) {\n
\n
\t\t\tvalue = value.replace(rxhtmlTag, fcloseTag);\n
\n
\t\t\ttry {\n
\t\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\t\t\t// Remove element nodes and prevent memory leaks\n
\t\t\t\t\tif ( this[i].nodeType === 1 ) {\n
\t\t\t\t\t\tjQuery.cleanData( this[i].getElementsByTagName("*") );\n
\t\t\t\t\t\tthis[i].innerHTML = value;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t// If using innerHTML throws an exception, use the fallback method\n
\t\t\t} catch(e) {\n
\t\t\t\tthis.empty().append( value );\n
\t\t\t}\n
\n
\t\t} else if ( jQuery.isFunction( value ) ) {\n
\t\t\tthis.each(function(i){\n
\t\t\t\tvar self = jQuery(this), old = self.html();\n
\t\t\t\tself.empty().append(function(){\n
\t\t\t\t\treturn value.call( this, i, old );\n
\t\t\t\t});\n
\t\t\t});\n
\n
\t\t} else {\n
\t\t\tthis.empty().append( value );\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\n
\treplaceWith: function( value ) {\n
\t\tif ( this[0] && this[0].parentNode ) {\n
\t\t\t// Make sure that the elements are removed from the DOM before they are inserted\n
\t\t\t// this can help fix replacing a parent with child elements\n
\t\t\tif ( jQuery.isFunction( value ) ) {\n
\t\t\t\treturn this.each(function(i) {\n
\t\t\t\t\tvar self = jQuery(this), old = self.html();\n
\t\t\t\t\tself.replaceWith( value.call( this, i, old ) );\n
\t\t\t\t});\n
\t\t\t}\n
\n
\t\t\tif ( typeof value !== "string" ) {\n
\t\t\t\tvalue = jQuery(value).detach();\n
\t\t\t}\n
\n
\t\t\treturn this.each(function() {\n
\t\t\t\tvar next = this.nextSibling, parent = this.parentNode;\n
\n
\t\t\t\tjQuery(this).remove();\n
\n
\t\t\t\tif ( next ) {\n
\t\t\t\t\tjQuery(next).before( value );\n
\t\t\t\t} else {\n
\t\t\t\t\tjQuery(parent).append( value );\n
\t\t\t\t}\n
\t\t\t});\n
\t\t} else {\n
\t\t\treturn this.pushStack( jQuery(jQuery.isFunction(value) ? value() : value), "replaceWith", value );\n
\t\t}\n
\t},\n
\n
\tdetach: function( selector ) {\n
\t\treturn this.remove( selector, true );\n
\t},\n
\n
\tdomManip: function( args, table, callback ) {\n
\t\tvar results, first, value = args[0], scripts = [], fragment, parent;\n
\n
\t\t// We can\'t cloneNode fragments that contain checked, in WebKit\n
\t\tif ( !jQuery.support.checkClone && arguments.length === 3 && typeof value === "string" && rchecked.test( value ) ) {\n
\t\t\treturn this.each(function() {\n
\t\t\t\tjQuery(this).domManip( args, table, callback, true );\n
\t\t\t});\n
\t\t}\n
\n
\t\tif ( jQuery.isFunction(value) ) {\n
\t\t\treturn this.each(function(i) {\n
\t\t\t\tvar self = jQuery(this);\n
\t\t\t\targs[0] = value.call(this, i, table ? self.html() : undefined);\n
\t\t\t\tself.domManip( args, table, callback );\n
\t\t\t});\n
\t\t}\n
\n
\t\tif ( this[0] ) {\n
\t\t\tparent = value && value.parentNode;\n
\n
\t\t\t// If we\'re in a fragment, just use that instead of building a new one\n
\t\t\tif ( jQuery.support.parentNode && parent && parent.nodeType === 11 && parent.childNodes.length === this.length ) {\n
\t\t\t\tresults = { fragment: parent };\n
\n
\t\t\t} else {\n
\t\t\t\tresults = buildFragment( args, this, scripts );\n
\t\t\t}\n
\t\t\t\n
\t\t\tfragment = results.fragment;\n
\t\t\t\n
\t\t\tif ( fragment.childNodes.length === 1 ) {\n
\t\t\t\tfirst = fragment = fragment.firstChild;\n
\t\t\t} else {\n
\t\t\t\tfirst = fragment.firstChild;\n
\t\t\t}\n
\n
\t\t\tif ( first ) {\n
\t\t\t\ttable = table && jQuery.nodeName( first, "tr" );\n
\n
\t\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\t\t\tcallback.call(\n
\t\t\t\t\t\ttable ?\n
\t\t\t\t\t\t\troot(this[i], first) :\n
\t\t\t\t\t\t\tthis[i],\n
\t\t\t\t\t\ti > 0 || results.cacheable || this.length > 1  ?\n
\t\t\t\t\t\t\tfragment.cloneNode(true) :\n
\t\t\t\t\t\t\tfragment\n
\t\t\t\t\t);\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tif ( scripts.length ) {\n
\t\t\t\tjQuery.each( scripts, evalScript );\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn this;\n
\n
\t\tfunction root( elem, cur ) {\n
\t\t\treturn jQuery.nodeName(elem, "table") ?\n
\t\t\t\t(elem.getElementsByTagName("tbody")[0] ||\n
\t\t\t\telem.appendChild(elem.ownerDocument.createElement("tbody"))) :\n
\t\t\t\telem;\n
\t\t}\n
\t}\n
});\n
\n
function cloneCopyEvent(orig, ret) {\n
\tvar i = 0;\n
\n
\tret.each(function() {\n
\t\tif ( this.nodeName !== (orig[i] && orig[i].nodeName) ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\tvar oldData = jQuery.data( orig[i++] ), curData = jQuery.data( this, oldData ), events = oldData && oldData.events;\n
\n
\t\tif ( events ) {\n
\t\t\tdelete curData.handle;\n
\t\t\tcurData.events = {};\n
\n
\t\t\tfor ( var type in events ) {\n
\t\t\t\tfor ( var handler in events[ type ] ) {\n
\t\t\t\t\tjQuery.event.add( this, type, events[ type ][ handler ], events[ type ][ handler ].data );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t});\n
}\n
\n
function buildFragment( args, nodes, scripts ) {\n
\tvar fragment, cacheable, cacheresults,\n
\t\tdoc = (nodes && nodes[0] ? nodes[0].ownerDocument || nodes[0] : document);\n
\n
\t// Only cache "small" (1/2 KB) strings that are associated with the main document\n
\t// Cloning options loses the selected state, so don\'t cache them\n
\t// IE 6 doesn\'t like it when you put <object> or <embed> elements in a fragment\n
\t// Also, WebKit does not clone \'checked\' attributes on cloneNode, so don\'t cache\n
\tif ( args.length === 1 && typeof args[0] === "string" && args[0].length < 512 && doc === document &&\n
\t\t!rnocache.test( args[0] ) && (jQuery.support.checkClone || !rchecked.test( args[0] )) ) {\n
\n
\t\tcacheable = true;\n
\t\tcacheresults = jQuery.fragments[ args[0] ];\n
\t\tif ( cacheresults ) {\n
\t\t\tif ( cacheresults !== 1 ) {\n
\t\t\t\tfragment = cacheresults;\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
\tif ( !fragment ) {\n
\t\tfragment = doc.createDocumentFragment();\n
\t\tjQuery.clean( args, doc, fragment, scripts );\n
\t}\n
\n
\tif ( cacheable ) {\n
\t\tjQuery.fragments[ args[0] ] = cacheresults ? fragment : 1;\n
\t}\n
\n
\treturn { fragment: fragment, cacheable: cacheable };\n
}\n
\n
jQuery.fragments = {};\n
\n
jQuery.each({\n
\tappendTo: "append",\n
\tprependTo: "prepend",\n
\tinsertBefore: "before",\n
\tinsertAfter: "after",\n
\treplaceAll: "replaceWith"\n
}, function( name, original ) {\n
\tjQuery.fn[ name ] = function( selector ) {\n
\t\tvar ret = [], insert = jQuery( selector ),\n
\t\t\tparent = this.length === 1 && this[0].parentNode;\n
\t\t\n
\t\tif ( parent && parent.nodeType === 11 && parent.childNodes.length === 1 && insert.length === 1 ) {\n
\t\t\tinsert[ original ]( this[0] );\n
\t\t\treturn this;\n
\t\t\t\n
\t\t} else {\n
\t\t\tfor ( var i = 0, l = insert.length; i < l; i++ ) {\n
\t\t\t\tvar elems = (i > 0 ? this.clone(true) : this).get();\n
\t\t\t\tjQuery.fn[ original ].apply( jQuery(insert[i]), elems );\n
\t\t\t\tret = ret.concat( elems );\n
\t\t\t}\n
\t\t\n
\t\t\treturn this.pushStack( ret, name, insert.selector );\n
\t\t}\n
\t};\n
});\n
\n
jQuery.extend({\n
\tclean: function( elems, context, fragment, scripts ) {\n
\t\tcontext = context || document;\n
\n
\t\t// !context.createElement fails in IE with an error but returns typeof \'object\'\n
\t\tif ( typeof context.createElement === "undefined" ) {\n
\t\t\tcontext = context.ownerDocument || context[0] && context[0].ownerDocument || document;\n
\t\t}\n
\n
\t\tvar ret = [];\n
\n
\t\tfor ( var i = 0, elem; (elem = elems[i]) != null; i++ ) {\n
\t\t\tif ( typeof elem === "number" ) {\n
\t\t\t\telem += "";\n
\t\t\t}\n
\n
\t\t\tif ( !elem ) {\n
\t\t\t\tcontinue;\n
\t\t\t}\n
\n
\t\t\t// Convert html string into DOM nodes\n
\t\t\tif ( typeof elem === "string" && !rhtml.test( elem ) ) {\n
\t\t\t\telem = context.createTextNode( elem );\n
\n
\t\t\t} else if ( typeof elem === "string" ) {\n
\t\t\t\t// Fix "XHTML"-style tags in all browsers\n
\t\t\t\telem = elem.replace(rxhtmlTag, fcloseTag);\n
\n
\t\t\t\t// Trim whitespace, otherwise indexOf won\'t work as expected\n
\t\t\t\tvar tag = (rtagName.exec( elem ) || ["", ""])[1].toLowerCase(),\n
\t\t\t\t\twrap = wrapMap[ tag ] || wrapMap._default,\n
\t\t\t\t\tdepth = wrap[0],\n
\t\t\t\t\tdiv = context.createElement("div");\n
\n
\t\t\t\t// Go to html and back, then peel off extra wrappers\n
\t\t\t\tdiv.innerHTML = wrap[1] + elem + wrap[2];\n
\n
\t\t\t\t// Move to the right depth\n
\t\t\t\twhile ( depth-- ) {\n
\t\t\t\t\tdiv = div.lastChild;\n
\t\t\t\t}\n
\n
\t\t\t\t// Remove IE\'s autoinserted <tbody> from table fragments\n
\t\t\t\tif ( !jQuery.support.tbody ) {\n
\n
\t\t\t\t\t// String was a <table>, *may* have spurious <tbody>\n
\t\t\t\t\tvar hasBody = rtbody.test(elem),\n
\t\t\t\t\t\ttbody = tag === "table" && !hasBody ?\n
\t\t\t\t\t\t\tdiv.firstChild && div.firstChild.childNodes :\n
\n
\t\t\t\t\t\t\t// String was a bare <thead> or <tfoot>\n
\t\t\t\t\t\t\twrap[1] === "<table>" && !hasBody ?\n
\t\t\t\t\t\t\t\tdiv.childNodes :\n
\t\t\t\t\t\t\t\t[];\n
\n
\t\t\t\t\tfor ( var j = tbody.length - 1; j >= 0 ; --j ) {\n
\t\t\t\t\t\tif ( jQuery.nodeName( tbody[ j ], "tbody" ) && !tbody[ j ].childNodes.length ) {\n
\t\t\t\t\t\t\ttbody[ j ].parentNode.removeChild( tbody[ j ] );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t}\n
\n
\t\t\t\t// IE completely kills leading whitespace when innerHTML is used\n
\t\t\t\tif ( !jQuery.support.leadingWhitespace && rleadingWhitespace.test( elem ) ) {\n
\t\t\t\t\tdiv.insertBefore( context.createTextNode( rleadingWhitespace.exec(elem)[0] ), div.firstChild );\n
\t\t\t\t}\n
\n
\t\t\t\telem = div.childNodes;\n
\t\t\t}\n
\n
\t\t\tif ( elem.nodeType ) {\n
\t\t\t\tret.push( elem );\n
\t\t\t} else {\n
\t\t\t\tret = jQuery.merge( ret, elem );\n
\t\t\t}\n
\t\t}\n
\n
\t\tif ( fragment ) {\n
\t\t\tfor ( var i = 0; ret[i]; i++ ) {\n
\t\t\t\tif ( scripts && jQuery.nodeName( ret[i], "script" ) && (!ret[i].type || ret[i].type.toLowerCase() === "text/javascript") ) {\n
\t\t\t\t\tscripts.push( ret[i].parentNode ? ret[i].parentNode.removeChild( ret[i] ) : ret[i] );\n
\t\t\t\t\n
\t\t\t\t} else {\n
\t\t\t\t\tif ( ret[i].nodeType === 1 ) {\n
\t\t\t\t\t\tret.splice.apply( ret, [i + 1, 0].concat(jQuery.makeArray(ret[i].getElementsByTagName("script"))) );\n
\t\t\t\t\t}\n
\t\t\t\t\tfragment.appendChild( ret[i] );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn ret;\n
\t},\n
\t\n
\tcleanData: function( elems ) {\n
\t\tvar data, id, cache = jQuery.cache,\n
\t\t\tspecial = jQuery.event.special,\n
\t\t\tdeleteExpando = jQuery.support.deleteExpando;\n
\t\t\n
\t\tfor ( var i = 0, elem; (elem = elems[i]) != null; i++ ) {\n
\t\t\tid = elem[ jQuery.expando ];\n
\t\t\t\n
\t\t\tif ( id ) {\n
\t\t\t\tdata = cache[ id ];\n
\t\t\t\t\n
\t\t\t\tif ( data.events ) {\n
\t\t\t\t\tfor ( var type in data.events ) {\n
\t\t\t\t\t\tif ( special[ type ] ) {\n
\t\t\t\t\t\t\tjQuery.event.remove( elem, type );\n
\n
\t\t\t\t\t\t} else {\n
\t\t\t\t\t\t\tremoveEvent( elem, type, data.handle );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tif ( deleteExpando ) {\n
\t\t\t\t\tdelete elem[ jQuery.expando ];\n
\n
\t\t\t\t} else if ( elem.removeAttribute ) {\n
\t\t\t\t\telem.removeAttribute( jQuery.expando );\n
\t\t\t\t}\n
\t\t\t\t\n
\t\t\t\tdelete cache[ id ];\n
\t\t\t}\n
\t\t}\n
\t}\n
});\n
// exclude the following css properties to add px\n
var rexclude = /z-?index|font-?weight|opacity|zoom|line-?height/i,\n
\tralpha = /alpha\\([^)]*\\)/,\n
\tropacity = /opacity=([^)]*)/,\n
\trfloat = /float/i,\n
\trdashAlpha = /-([a-z])/ig,\n
\trupper = /([A-Z])/g,\n
\trnumpx = /^-?\\d+(?:px)?$/i,\n
\trnum = /^-?\\d/,\n
\n
\tcssShow = { position: "absolute", visibility: "hidden", display:"block" },\n
\tcssWidth = [ "Left", "Right" ],\n
\tcssHeight = [ "Top", "Bottom" ],\n
\n
\t// cache check for defaultView.getComputedStyle\n
\tgetComputedStyle = document.defaultView && document.defaultView.getComputedStyle,\n
\t// normalize float css property\n
\tstyleFloat = jQuery.support.cssFloat ? "cssFloat" : "styleFloat",\n
\tfcamelCase = function( all, letter ) {\n
\t\treturn letter.toUpperCase();\n
\t};\n
\n
jQuery.fn.css = function( name, value ) {\n
\treturn access( this, name, value, true, function( elem, name, value ) {\n
\t\tif ( value === undefined ) {\n
\t\t\treturn jQuery.curCSS( elem, name );\n
\t\t}\n
\t\t\n
\t\tif ( typeof value === "number" && !rexclude.test(name) ) {\n
\t\t\tvalue += "px";\n
\t\t}\n
\n
\t\tjQuery.style( elem, name, value );\n
\t});\n
};\n
\n
jQuery.extend({\n
\tstyle: function( elem, name, value ) {\n
\t\t// don\'t set styles on text and comment nodes\n
\t\tif ( !elem || elem.nodeType === 3 || elem.nodeType === 8 ) {\n
\t\t\treturn undefined;\n
\t\t}\n
\n
\t\t// ignore negative width and height values #1599\n
\t\tif ( (name === "width" || name === "height") && parseFloat(value) < 0 ) {\n
\t\t\tvalue = undefined;\n
\t\t}\n
\n
\t\tvar style = elem.style || elem, set = value !== undefined;\n
\n
\t\t// IE uses filters for opacity\n
\t\tif ( !jQuery.support.opacity && name === "opacity" ) {\n
\t\t\tif ( set ) {\n
\t\t\t\t// IE has trouble with opacity if it does not have layout\n
\t\t\t\t// Force it by setting the zoom level\n
\t\t\t\tstyle.zoom = 1;\n
\n
\t\t\t\t// Set the alpha filter to set the opacity\n
\t\t\t\tvar opacity = parseInt( value, 10 ) + "" === "NaN" ? "" : "alpha(opacity=" + value * 100 + ")";\n
\t\t\t\tvar filter = style.filter || jQuery.curCSS( elem, "filter" ) || "";\n
\t\t\t\tstyle.filter = ralpha.test(filter) ? filter.replace(ralpha, opacity) : opacity;\n
\t\t\t}\n
\n
\t\t\treturn style.filter && style.filter.indexOf("opacity=") >= 0 ?\n
\t\t\t\t(parseFloat( ropacity.exec(style.filter)[1] ) / 100) + "":\n
\t\t\t\t"";\n
\t\t}\n
\n
\t\t// Make sure we\'re using the right name for getting the float value\n
\t\tif ( rfloat.test( name ) ) {\n
\t\t\tname = styleFloat;\n
\t\t}\n
\n
\t\tname = name.replace(rdashAlpha, fcamelCase);\n
\n
\t\tif ( set ) {\n
\t\t\tstyle[ name ] = value;\n
\t\t}\n
\n
\t\treturn style[ name ];\n
\t},\n
\n
\tcss: function( elem, name, force, extra ) {\n
\t\tif ( name === "width" || name === "height" ) {\n
\t\t\tvar val, props = cssShow, which = name === "width" ? cssWidth : cssHeight;\n
\n
\t\t\tfunction getWH() {\n
\t\t\t\tval = name === "width" ? elem.offsetWidth : elem.offsetHeight;\n
\n
\t\t\t\tif ( extra === "border" ) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\n
\t\t\t\tjQuery.each( which, function() {\n
\t\t\t\t\tif ( !extra ) {\n
\t\t\t\t\t\tval -= parseFloat(jQuery.curCSS( elem, "padding" + this, true)) || 0;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tif ( extra === "margin" ) {\n
\t\t\t\t\t\tval += parseFloat(jQuery.curCSS( elem, "margin" + this, true)) || 0;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tval -= parseFloat(jQuery.curCSS( elem, "border" + this + "Width", true)) || 0;\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t}\n
\n
\t\t\tif ( elem.offsetWidth !== 0 ) {\n
\t\t\t\tgetWH();\n
\t\t\t} else {\n
\t\t\t\tjQuery.swap( elem, props, getWH );\n
\t\t\t}\n
\n
\t\t\treturn Math.max(0, Math.round(val));\n
\t\t}\n
\n
\t\treturn jQuery.curCSS( elem, name, force );\n
\t},\n
\n
\tcurCSS: function( elem, name, force ) {\n
\t\tvar ret, style = elem.style, filter;\n
\n
\t\t// IE uses filters for opacity\n
\t\tif ( !jQuery.support.opacity && name === "opacity" && elem.currentStyle ) {\n
\t\t\tret = ropacity.test(elem.currentStyle.filter || "") ?\n
\t\t\t\t(parseFloat(RegExp.$1) / 100) + "" :\n
\t\t\t\t"";\n
\n
\t\t\treturn ret === "" ?\n
\t\t\t\t"1" :\n
\t\t\t\tret;\n
\t\t}\n
\n
\t\t// Make sure we\'re using the right name for getting the float value\n
\t\tif ( rfloat.test( name ) ) {\n
\t\t\tname = styleFloat;\n
\t\t}\n
\n
\t\tif ( !force && style && style[ name ] ) {\n
\t\t\tret = style[ name ];\n
\n
\t\t} else if ( getComputedStyle ) {\n
\n
\t\t\t// Only "float" is needed here\n
\t\t\tif ( rfloat.test( name ) ) {\n
\t\t\t\tname = "float";\n
\t\t\t}\n
\n
\t\t\tname = name.replace( rupper, "-$1" ).toLowerCase();\n
\n
\t\t\tvar defaultView = elem.ownerDocument.defaultView;\n
\n
\t\t\tif ( !defaultView ) {\n
\t\t\t\treturn null;\n
\t\t\t}\n
\n
\t\t\tvar computedStyle = defaultView.getComputedStyle( elem, null );\n
\n
\t\t\tif ( computedStyle ) {\n
\t\t\t\tret = computedStyle.getPropertyValue( name );\n
\t\t\t}\n
\n
\t\t\t// We should always get a number back from opacity\n
\t\t\tif ( name === "opacity" && ret === "" ) {\n
\t\t\t\tret = "1";\n
\t\t\t}\n
\n
\t\t} else if ( elem.currentStyle ) {\n
\t\t\tvar camelCase = name.replace(rdashAlpha, fcamelCase);\n
\n
\t\t\tret = elem.currentStyle[ name ] || elem.currentStyle[ camelCase ];\n
\n
\t\t\t// From the awesome hack by Dean Edwards\n
\t\t\t// http://erik.eae.net/archives/2007/07/27/18.54.15/#comment-102291\n
\n
\t\t\t// If we\'re not dealing with a regular pixel number\n
\t\t\t// but a number that has a weird ending, we need to convert it to pixels\n
\t\t\tif ( !rnumpx.test( ret ) && rnum.test( ret ) ) {\n
\t\t\t\t// Remember the original values\n
\t\t\t\tvar left = style.left, rsLeft = elem.runtimeStyle.left;\n
\n
\t\t\t\t// Put in the new values to get a computed value out\n
\t\t\t\telem.runtimeStyle.left = elem.currentStyle.left;\n
\t\t\t\tstyle.left = camelCase === "fontSize" ? "1em" : (ret || 0);\n
\t\t\t\tret = style.pixelLeft + "px";\n
\n
\t\t\t\t// Revert the changed values\n
\t\t\t\tstyle.left = left;\n
\t\t\t\telem.runtimeStyle.left = rsLeft;\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn ret;\n
\t},\n
\n
\t// A method for quickly swapping in/out CSS properties to get correct calculations\n
\tswap: function( elem, options, callback ) {\n
\t\tvar old = {};\n
\n
\t\t// Remember the old values, and insert the new ones\n
\t\tfor ( var name in options ) {\n
\t\t\told[ name ] = elem.style[ name ];\n
\t\t\telem.style[ name ] = options[ name ];\n
\t\t}\n
\n
\t\tcallback.call( elem );\n
\n
\t\t// Revert the old values\n
\t\tfor ( var name in options ) {\n
\t\t\telem.style[ name ] = old[ name ];\n
\t\t}\n
\t}\n
});\n
\n
if ( jQuery.expr && jQuery.expr.filters ) {\n
\tjQuery.expr.filters.hidden = function( elem ) {\n
\t\tvar width = elem.offsetWidth, height = elem.offsetHeight,\n
\t\t\tskip = elem.nodeName.toLowerCase() === "tr";\n
\n
\t\treturn width === 0 && height === 0 && !skip ?\n
\t\t\ttrue :\n
\t\t\twidth > 0 && height > 0 && !skip ?\n
\t\t\t\tfalse :\n
\t\t\t\tjQuery.curCSS(elem, "display") === "none";\n
\t};\n
\n
\tjQuery.expr.filters.visible = function( elem ) {\n
\t\treturn !jQuery.expr.filters.hidden( elem );\n
\t};\n
}\n
var jsc = now(),\n
\trscript = /<script(.|\\s)*?\\/script>/gi,\n
\trselectTextarea = /select|textarea/i,\n
\trinput = /color|date|datetime|email|hidden|month|number|password|range|search|tel|text|time|url|week/i,\n
\tjsre = /=\\?(&|$)/,\n
\trquery = /\\?/,\n
\trts = /(\\?|&)_=.*?(&|$)/,\n
\trurl = /^(\\w+:)?\\/\\/([^\\/?#]+)/,\n
\tr20 = /%20/g,\n
\n
\t// Keep a copy of the old load method\n
\t_load = jQuery.fn.load;\n
\n
jQuery.fn.extend({\n
\tload: function( url, params, callback ) {\n
\t\tif ( typeof url !== "string" ) {\n
\t\t\treturn _load.call( this, url );\n
\n
\t\t// Don\'t do a request if no elements are being requested\n
\t\t} else if ( !this.length ) {\n
\t\t\treturn this;\n
\t\t}\n
\n
\t\tvar off = url.indexOf(" ");\n
\t\tif ( off >= 0 ) {\n
\t\t\tvar selector = url.slice(off, url.length);\n
\t\t\turl = url.slice(0, off);\n
\t\t}\n
\n
\t\t// Default to a GET request\n
\t\tvar type = "GET";\n
\n
\t\t// If the second parameter was provided\n
\t\tif ( params ) {\n
\t\t\t// If it\'s a function\n
\t\t\tif ( jQuery.isFunction( params ) ) {\n
\t\t\t\t// We assume that it\'s the callback\n
\t\t\t\tcallback = params;\n
\t\t\t\tparams = null;\n
\n
\t\t\t// Otherwise, build a param string\n
\t\t\t} else if ( typeof params === "object" ) {\n
\t\t\t\tparams = jQuery.param( params, jQuery.ajaxSettings.traditional );\n
\t\t\t\ttype = "POST";\n
\t\t\t}\n
\t\t}\n
\n
\t\tvar self = this;\n
\n
\t\t// Request the remote document\n
\t\tjQuery.ajax({\n
\t\t\turl: url,\n
\t\t\ttype: type,\n
\t\t\tdataType: "html",\n
\t\t\tdata: params,\n
\t\t\tcomplete: function( res, status ) {\n
\t\t\t\t// If successful, inject the HTML into all the matched elements\n
\t\t\t\tif ( status === "success" || status === "notmodified" ) {\n
\t\t\t\t\t// See if a selector was specified\n
\t\t\t\t\tself.html( selector ?\n
\t\t\t\t\t\t// Create a dummy div to hold the results\n
\t\t\t\t\t\tjQuery("<div />")\n
\t\t\t\t\t\t\t// inject the contents of the document in, removing the scripts\n
\t\t\t\t\t\t\t// to avoid any \'Permission Denied\' errors in IE\n
\t\t\t\t\t\t\t.append(res.responseText.replace(rscript, ""))\n
\n
\t\t\t\t\t\t\t// Locate the specified elements\n
\t\t\t\t\t\t\t.find(selector) :\n
\n
\t\t\t\t\t\t// If not, just inject the full result\n
\t\t\t\t\t\tres.responseText );\n
\t\t\t\t}\n
\n
\t\t\t\tif ( callback ) {\n
\t\t\t\t\tself.each( callback, [res.responseText, status, res] );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\n
\t\treturn this;\n
\t},\n
\n
\tserialize: function() {\n
\t\treturn jQuery.param(this.serializeArray());\n
\t},\n
\tserializeArray: function() {\n
\t\treturn this.map(function() {\n
\t\t\treturn this.elements ? jQuery.makeArray(this.elements) : this;\n
\t\t})\n
\t\t.filter(function() {\n
\t\t\treturn this.name && !this.disabled &&\n
\t\t\t\t(this.checked || rselectTextarea.test(this.nodeName) ||\n
\t\t\t\t\trinput.test(this.type));\n
\t\t})\n
\t\t.map(function( i, elem ) {\n
\t\t\tvar val = jQuery(this).val();\n
\n
\t\t\treturn val == null ?\n
\t\t\t\tnull :\n
\t\t\t\tjQuery.isArray(val) ?\n
\t\t\t\t\tjQuery.map( val, function( val, i ) {\n
\t\t\t\t\t\treturn { name: elem.name, value: val };\n
\t\t\t\t\t}) :\n
\t\t\t\t\t{ name: elem.name, value: val };\n
\t\t}).get();\n
\t}\n
});\n
\n
// Attach a bunch of functions for handling common AJAX events\n
jQuery.each( "ajaxStart ajaxStop ajaxComplete ajaxError ajaxSuccess ajaxSend".split(" "), function( i, o ) {\n
\tjQuery.fn[o] = function( f ) {\n
\t\treturn this.bind(o, f);\n
\t};\n
});\n
\n
jQuery.extend({\n
\n
\tget: function( url, data, callback, type ) {\n
\t\t// shift arguments if data argument was omited\n
\t\tif ( jQuery.isFunction( data ) ) {\n
\t\t\ttype = type || callback;\n
\t\t\tcallback = data;\n
\t\t\tdata = null;\n
\t\t}\n
\n
\t\treturn jQuery.ajax({\n
\t\t\ttype: "GET",\n
\t\t\turl: url,\n
\t\t\tdata: data,\n
\t\t\tsuccess: callback,\n
\t\t\tdataType: type\n
\t\t});\n
\t},\n
\n
\tgetScript: function( url, callback ) {\n
\t\treturn jQuery.get(url, null, callback, "script");\n
\t},\n
\n
\tgetJSON: function( url, data, callback ) {\n
\t\treturn jQuery.get(url, data, callback, "json");\n
\t},\n
\n
\tpost: function( url, data, callback, type ) {\n
\t\t// shift arguments if data argument was omited\n
\t\tif ( jQuery.isFunction( data ) ) {\n
\t\t\ttype = type || callback;\n
\t\t\tcallback = data;\n
\t\t\tdata = {};\n
\t\t}\n
\n
\t\treturn jQuery.ajax({\n
\t\t\ttype: "POST",\n
\t\t\turl: url,\n
\t\t\tdata: data,\n
\t\t\tsuccess: callback,\n
\t\t\tdataType: type\n
\t\t});\n
\t},\n
\n
\tajaxSetup: function( settings ) {\n
\t\tjQuery.extend( jQuery.ajaxSettings, settings );\n
\t},\n
\n
\tajaxSettings: {\n
\t\turl: location.href,\n
\t\tglobal: true,\n
\t\ttype: "GET",\n
\t\tcontentType: "application/x-www-form-urlencoded",\n
\t\tprocessData: true,\n
\t\tasync: true,\n
\t\t/*\n
\t\ttimeout: 0,\n
\t\tdata: null,\n
\t\tusername: null,\n
\t\tpassword: null,\n
\t\ttraditional: false,\n
\t\t*/\n
\t\t// Create the request object; Microsoft failed to properly\n
\t\t// implement the XMLHttpRequest in IE7 (can\'t request local files),\n
\t\t// so we use the ActiveXObject when it is available\n
\t\t// This function can be overriden by calling jQuery.ajaxSetup\n
\t\txhr: window.XMLHttpRequest && (window.location.protocol !== "file:" || !window.ActiveXObject) ?\n
\t\t\tfunction() {\n
\t\t\t\treturn new window.XMLHttpRequest();\n
\t\t\t} :\n
\t\t\tfunction() {\n
\t\t\t\ttry {\n
\t\t\t\t\treturn new window.ActiveXObject("Microsoft.XMLHTTP");\n
\t\t\t\t} catch(e) {}\n
\t\t\t},\n
\t\taccepts: {\n
\t\t\txml: "application/xml, text/xml",\n
\t\t\thtml: "text/html",\n
\t\t\tscript: "text/javascript, application/javascript",\n
\t\t\tjson: "application/json, text/javascript",\n
\t\t\ttext: "text/plain",\n
\t\t\t_default: "*/*"\n
\t\t}\n
\t},\n
\n
\t// Last-Modified header cache for next request\n
\tlastModified: {},\n
\tetag: {},\n
\n
\tajax: function( origSettings ) {\n
\t\tvar s = jQuery.extend(true, {}, jQuery.ajaxSettings, origSettings);\n
\t\t\n
\t\tvar jsonp, status, data,\n
\t\t\tcallbackContext = origSettings && origSettings.context || s,\n
\t\t\ttype = s.type.toUpperCase();\n
\n
\t\t// convert data if not already a string\n
\t\tif ( s.data && s.processData && typeof s.data !== "string" ) {\n
\t\t\ts.data = jQuery.param( s.data, s.traditional );\n
\t\t}\n
\n
\t\t// Handle JSONP Parameter Callbacks\n
\t\tif ( s.dataType === "jsonp" ) {\n
\t\t\tif ( type === "GET" ) {\n
\t\t\t\tif ( !jsre.test( s.url ) ) {\n
\t\t\t\t\ts.url += (rquery.test( s.url ) ? "&" : "?") + (s.jsonp || "callback") + "=?";\n
\t\t\t\t}\n
\t\t\t} else if ( !s.data || !jsre.test(s.data) ) {\n
\t\t\t\ts.data = (s.data ? s.data + "&" : "") + (s.jsonp || "callback") + "=?";\n
\t\t\t}\n
\t\t\ts.dataType = "json";\n
\t\t}\n
\n
\t\t// Build temporary JSONP function\n
\t\tif ( s.dataType === "json" && (s.data && jsre.test(s.data) || jsre.test(s.url)) ) {\n
\t\t\tjsonp = s.jsonpCallback || ("jsonp" + jsc++);\n
\n
\t\t\t// Replace the =? sequence both in the query string and the data\n
\t\t\tif ( s.data ) {\n
\t\t\t\ts.data = (s.data + "").replace(jsre, "=" + jsonp + "$1");\n
\t\t\t}\n
\n
\t\t\ts.url = s.url.replace(jsre, "=" + jsonp + "$1");\n
\n
\t\t\t// We need to make sure\n
\t\t\t// that a JSONP style response is executed properly\n
\t\t\ts.dataType = "script";\n
\n
\t\t\t// Handle JSONP-style loading\n
\t\t\twindow[ jsonp ] = window[ jsonp ] || function( tmp ) {\n
\t\t\t\tdata = tmp;\n
\t\t\t\tsuccess();\n
\t\t\t\tcomplete();\n
\t\t\t\t// Garbage collect\n
\t\t\t\twindow[ jsonp ] = undefined;\n
\n
\t\t\t\ttry {\n
\t\t\t\t\tdelete window[ jsonp ];\n
\t\t\t\t} catch(e) {}\n
\n
\t\t\t\tif ( head ) {\n
\t\t\t\t\thead.removeChild( script );\n
\t\t\t\t}\n
\t\t\t};\n
\t\t}\n
\n
\t\tif ( s.dataType === "script" && s.cache === null ) {\n
\t\t\ts.cache = false;\n
\t\t}\n
\n
\t\tif ( s.cache === false && type === "GET" ) {\n
\t\t\tvar ts = now();\n
\n
\t\t\t// try replacing _= if it is there\n
\t\t\tvar ret = s.url.replace(rts, "$1_=" + ts + "$2");\n
\n
\t\t\t// if nothing was replaced, add timestamp to the end\n
\t\t\ts.url = ret + ((ret === s.url) ? (rquery.test(s.url) ? "&" : "?") + "_=" + ts : "");\n
\t\t}\n
\n
\t\t// If data is available, append data to url for get requests\n
\t\tif ( s.data && type === "GET" ) {\n
\t\t\ts.url += (rquery.test(s.url) ? "&" : "?") + s.data;\n
\t\t}\n
\n
\t\t// Watch for a new set of requests\n
\t\tif ( s.global && ! jQuery.active++ ) {\n
\t\t\tjQuery.event.trigger( "ajaxStart" );\n
\t\t}\n
\n
\t\t// Matches an absolute URL, and saves the domain\n
\t\tvar parts = rurl.exec( s.url ),\n
\t\t\tremote = parts && (parts[1] && parts[1] !== location.protocol || parts[2] !== location.host);\n
\n
\t\t// If we\'re requesting a remote document\n
\t\t// and trying to load JSON or Script with a GET\n
\t\tif ( s.dataType === "script" && type === "GET" && remote ) {\n
\t\t\tvar head = document.getElementsByTagName("head")[0] || document.documentElement;\n
\t\t\tvar script = document.createElement("script");\n
\t\t\tscript.src = s.url;\n
\t\t\tif ( s.scriptCharset ) {\n
\t\t\t\tscript.charset = s.scriptCharset;\n
\t\t\t}\n
\n
\t\t\t// Handle Script loading\n
\t\t\tif ( !jsonp ) {\n
\t\t\t\tvar done = false;\n
\n
\t\t\t\t// Attach handlers for all browsers\n
\t\t\t\tscript.onload = script.onreadystatechange = function() {\n
\t\t\t\t\tif ( !done && (!this.readyState ||\n
\t\t\t\t\t\t\tthis.readyState === "loaded" || this.readyState === "complete") ) {\n
\t\t\t\t\t\tdone = true;\n
\t\t\t\t\t\tsuccess();\n
\t\t\t\t\t\tcomplete();\n
\n
\t\t\t\t\t\t// Handle memory leak in IE\n
\t\t\t\t\t\tscript.onload = script.onreadystatechange = null;\n
\t\t\t\t\t\tif ( head && script.parentNode ) {\n
\t\t\t\t\t\t\thead.removeChild( script );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\t\t\t}\n
\n
\t\t\t// Use insertBefore instead of appendChild  to circumvent an IE6 bug.\n
\t\t\t// This arises when a base node is used (#2709 and #4378).\n
\t\t\thead.insertBefore( script, head.firstChild );\n
\n
\t\t\t// We handle everything using the script element injection\n
\t\t\treturn undefined;\n
\t\t}\n
\n
\t\tvar requestDone = false;\n
\n
\t\t// Create the request object\n
\t\tvar xhr = s.xhr();\n
\n
\t\tif ( !xhr ) {\n
\t\t\treturn;\n
\t\t}\n
\n
\t\t// Open the socket\n
\t\t// Passing null username, generates a login popup on Opera (#2865)\n
\t\tif ( s.username ) {\n
\t\t\txhr.open(type, s.url, s.async, s.username, s.password);\n
\t\t} else {\n
\t\t\txhr.open(type, s.url, s.async);\n
\t\t}\n
\n
\t\t// Need an extra try/catch for cross domain requests in Firefox 3\n
\t\ttry {\n
\t\t\t// Set the correct header, if data is being sent\n
\t\t\tif ( s.data || origSettings && origSettings.contentType ) {\n
\t\t\t\txhr.setRequestHeader("Content-Type", s.contentType);\n
\t\t\t}\n
\n
\t\t\t// Set the If-Modified-Since and/or If-None-Match header, if in ifModified mode.\n
\t\t\tif ( s.ifModified ) {\n
\t\t\t\tif ( jQuery.lastModified[s.url] ) {\n
\t\t\t\t\txhr.setRequestHeader("If-Modified-Since", jQuery.lastModified[s.url]);\n
\t\t\t\t}\n
\n
\t\t\t\tif ( jQuery.etag[s.url] ) {\n
\t\t\t\t\txhr.setRequestHeader("If-None-Match", jQuery.etag[s.url]);\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// Set header so the called script knows that it\'s an XMLHttpRequest\n
\t\t\t// Only send the header if it\'s not a remote XHR\n
\t\t\tif ( !remote ) {\n
\t\t\t\txhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");\n
\t\t\t}\n
\n
\t\t\t// Set the Accepts header for the server, depending on the dataType\n
\t\t\txhr.setRequestHeader("Accept", s.dataType && s.accepts[ s.dataType ] ?\n
\t\t\t\ts.accepts[ s.dataType ] + ", */*" :\n
\t\t\t\ts.accepts._default );\n
\t\t} catch(e) {}\n
\n
\t\t// Allow custom headers/mimetypes and early abort\n
\t\tif ( s.beforeSend && s.beforeSend.call(callbackContext, xhr, s) === false ) {\n
\t\t\t// Handle the global AJAX counter\n
\t\t\tif ( s.global && ! --jQuery.active ) {\n
\t\t\t\tjQuery.event.trigger( "ajaxStop" );\n
\t\t\t}\n
\n
\t\t\t// close opended socket\n
\t\t\txhr.abort();\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\tif ( s.global ) {\n
\t\t\ttrigger("ajaxSend", [xhr, s]);\n
\t\t}\n
\n
\t\t// Wait for a response to come back\n
\t\tvar onreadystatechange = xhr.onreadystatechange = function( isTimeout ) {\n
\t\t\t// The request was aborted\n
\t\t\tif ( !xhr || xhr.readyState === 0 || isTimeout === "abort" ) {\n
\t\t\t\t// Opera doesn\'t call onreadystatechange before this point\n
\t\t\t\t// so we simulate the call\n
\t\t\t\tif ( !requestDone ) {\n
\t\t\t\t\tcomplete();\n
\t\t\t\t}\n
\n
\t\t\t\trequestDone = true;\n
\t\t\t\tif ( xhr ) {\n
\t\t\t\t\txhr.onreadystatechange = jQuery.noop;\n
\t\t\t\t}\n
\n
\t\t\t// The transfer is complete and the data is available, or the request timed out\n
\t\t\t} else if ( !requestDone && xhr && (xhr.readyState === 4 || isTimeout === "timeout") ) {\n
\t\t\t\trequestDone = true;\n
\t\t\t\txhr.onreadystatechange = jQuery.noop;\n
\n
\t\t\t\tstatus = isTimeout === "timeout" ?\n
\t\t\t\t\t"timeout" :\n
\t\t\t\t\t!jQuery.httpSuccess( xhr ) ?\n
\t\t\t\t\t\t"error" :\n
\t\t\t\t\t\ts.ifModified && jQuery.httpNotModified( xhr, s.url ) ?\n
\t\t\t\t\t\t\t"notmodified" :\n
\t\t\t\t\t\t\t"success";\n
\n
\t\t\t\tvar errMsg;\n
\n
\t\t\t\tif ( status === "success" ) {\n
\t\t\t\t\t// Watch for, and catch, XML document parse errors\n
\t\t\t\t\ttry {\n
\t\t\t\t\t\t// process the data (runs the xml through httpData regardless of callback)\n
\t\t\t\t\t\tdata = jQuery.httpData( xhr, s.dataType, s );\n
\t\t\t\t\t} catch(err) {\n
\t\t\t\t\t\tstatus = "parsererror";\n
\t\t\t\t\t\terrMsg = err;\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\t// Make sure that the request was successful or notmodified\n
\t\t\t\tif ( status === "success" || status === "notmodified" ) {\n
\t\t\t\t\t// JSONP handles its own success callback\n
\t\t\t\t\tif ( !jsonp ) {\n
\t\t\t\t\t\tsuccess();\n
\t\t\t\t\t}\n
\t\t\t\t} else {\n
\t\t\t\t\tjQuery.handleError(s, xhr, status, errMsg);\n
\t\t\t\t}\n
\n
\t\t\t\t// Fire the complete handlers\n
\t\t\t\tcomplete();\n
\n
\t\t\t\tif ( isTimeout === "timeout" ) {\n
\t\t\t\t\txhr.abort();\n
\t\t\t\t}\n
\n
\t\t\t\t// Stop memory leaks\n
\t\t\t\tif ( s.async ) {\n
\t\t\t\t\txhr = null;\n
\t\t\t\t}\n
\t\t\t}\n
\t\t};\n
\n
\t\t// Override the abort handler, if we can (IE doesn\'t allow it, but that\'s OK)\n
\t\t// Opera doesn\'t fire onreadystatechange at all on abort\n
\t\ttry {\n
\t\t\tvar oldAbort = xhr.abort;\n
\t\t\txhr.abort = function() {\n
\t\t\t\tif ( xhr ) {\n
\t\t\t\t\toldAbort.call( xhr );\n
\t\t\t\t}\n
\n
\t\t\t\tonreadystatechange( "abort" );\n
\t\t\t};\n
\t\t} catch(e) { }\n
\n
\t\t// Timeout checker\n
\t\tif ( s.async && s.timeout > 0 ) {\n
\t\t\tsetTimeout(function() {\n
\t\t\t\t// Check to see if the request is still happening\n
\t\t\t\tif ( xhr && !requestDone ) {\n
\t\t\t\t\tonreadystatechange( "timeout" );\n
\t\t\t\t}\n
\t\t\t}, s.timeout);\n
\t\t}\n
\n
\t\t// Send the data\n
\t\ttry {\n
\t\t\txhr.send( type === "POST" || type === "PUT" || type === "DELETE" ? s.data : null );\n
\t\t} catch(e) {\n
\t\t\tjQuery.handleError(s, xhr, null, e);\n
\t\t\t// Fire the complete handlers\n
\t\t\tcomplete();\n
\t\t}\n
\n
\t\t// firefox 1.5 doesn\'t fire statechange for sync requests\n
\t\tif ( !s.async ) {\n
\t\t\tonreadystatechange();\n
\t\t}\n
\n
\t\tfunction success() {\n
\t\t\t// If a local callback was specified, fire it and pass it the data\n
\t\t\tif ( s.success ) {\n
\t\t\t\ts.success.call( callbackContext, data, status, xhr );\n
\t\t\t}\n
\n
\t\t\t// Fire the global callback\n
\t\t\tif ( s.global ) {\n
\t\t\t\ttrigger( "ajaxSuccess", [xhr, s] );\n
\t\t\t}\n
\t\t}\n
\n
\t\tfunction complete() {\n
\t\t\t// Process result\n
\t\t\tif ( s.complete ) {\n
\t\t\t\ts.complete.call( callbackContext, xhr, status);\n
\t\t\t}\n
\n
\t\t\t// The request was completed\n
\t\t\tif ( s.global ) {\n
\t\t\t\ttrigger( "ajaxComplete", [xhr, s] );\n
\t\t\t}\n
\n
\t\t\t// Handle the global AJAX counter\n
\t\t\tif ( s.global && ! --jQuery.active ) {\n
\t\t\t\tjQuery.event.trigger( "ajaxStop" );\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\tfunction trigger(type, args) {\n
\t\t\t(s.context ? jQuery(s.context) : jQuery.event).trigger(type, args);\n
\t\t}\n
\n
\t\t// return XMLHttpRequest to allow aborting the request etc.\n
\t\treturn xhr;\n
\t},\n
\n
\thandleError: function( s, xhr, status, e ) {\n
\t\t// If a local callback was specified, fire it\n
\t\tif ( s.error ) {\n
\t\t\ts.error.call( s.context || s, xhr, status, e );\n
\t\t}\n
\n
\t\t// Fire the global callback\n
\t\tif ( s.global ) {\n
\t\t\t(s.context ? jQuery(s.context) : jQuery.event).trigger( "ajaxError", [xhr, s, e] );\n
\t\t}\n
\t},\n
\n
\t// Counter for holding the number of active queries\n
\tactive: 0,\n
\n
\t// Determines if an XMLHttpRequest was successful or not\n
\thttpSuccess: function( xhr ) {\n
\t\ttry {\n
\t\t\t// IE error sometimes returns 1223 when it should be 204 so treat it as success, see #1450\n
\t\t\treturn !xhr.status && location.protocol === "file:" ||\n
\t\t\t\t// Opera returns 0 when status is 304\n
\t\t\t\t( xhr.status >= 200 && xhr.status < 300 ) ||\n
\t\t\t\txhr.status === 304 || xhr.status === 1223 || (jQuery.browser.opera && xhr.status === 0);\n
\t\t} catch(e) {}\n
\n
\t\treturn false;\n
\t},\n
\n
\t// Determines if an XMLHttpRequest returns NotModified\n
\thttpNotModified: function( xhr, url ) {\n
\t\tvar lastModified = xhr.getResponseHeader("Last-Modified"),\n
\t\t\tetag = xhr.getResponseHeader("Etag");\n
\n
\t\tif ( lastModified ) {\n
\t\t\tjQuery.lastModified[url] = lastModified;\n
\t\t}\n
\n
\t\tif ( etag ) {\n
\t\t\tjQuery.etag[url] = etag;\n
\t\t}\n
\n
\t\t// Opera returns 0 when status is 304\n
\t\treturn xhr.status === 304 || (jQuery.browser.opera && xhr.status === 0);\n
\t},\n
\n
\thttpData: function( xhr, type, s ) {\n
\t\tvar ct = xhr.getResponseHeader("content-type") || "",\n
\t\t\txml = type === "xml" || !type && ct.indexOf("xml") >= 0,\n
\t\t\tdata = xml ? xhr.responseXML : xhr.responseText;\n
\n
\t\tif ( xml && data.documentElement.nodeName === "parsererror" ) {\n
\t\t\tjQuery.error( "parsererror" );\n
\t\t}\n
\n
\t\t// Allow a pre-filtering function to sanitize the response\n
\t\t// s is checked to keep backwards compatibility\n
\t\tif ( s && s.dataFilter ) {\n
\t\t\tdata = s.dataFilter( data, type );\n
\t\t}\n
\n
\t\t// The filter can actually parse the response\n
\t\tif ( typeof data === "string" ) {\n
\t\t\t// Get the JavaScript object, if JSON is used.\n
\t\t\tif ( type === "json" || !type && ct.indexOf("json") >= 0 ) {\n
\t\t\t\tdata = jQuery.parseJSON( data );\n
\n
\t\t\t// If the type is "script", eval it in global context\n
\t\t\t} else if ( type === "script" || !type && ct.indexOf("javascript") >= 0 ) {\n
\t\t\t\tjQuery.globalEval( data );\n
\t\t\t}\n
\t\t}\n
\n
\t\treturn data;\n
\t},\n
\n
\t// Serialize an array of form elements or a set of\n
\t// key/values into a query string\n
\tparam: function( a, traditional ) {\n
\t\tvar s = [];\n
\t\t\n
\t\t// Set traditional to true for jQuery <= 1.3.2 behavior.\n
\t\tif ( traditional === undefined ) {\n
\t\t\ttraditional = jQuery.ajaxSettings.traditional;\n
\t\t}\n
\t\t\n
\t\t// If an array was passed in, assume that it is an array of form elements.\n
\t\tif ( jQuery.isArray(a) || a.jquery ) {\n
\t\t\t// Serialize the form elements\n
\t\t\tjQuery.each( a, function() {\n
\t\t\t\tadd( this.name, this.value );\n
\t\t\t});\n
\t\t\t\n
\t\t} else {\n
\t\t\t// If traditional, encode the "old" way (the way 1.3.2 or older\n
\t\t\t// did it), otherwise encode params recursively.\n
\t\t\tfor ( var prefix in a ) {\n
\t\t\t\tbuildParams( prefix, a[prefix] );\n
\t\t\t}\n
\t\t}\n
\n
\t\t// Return the resulting serialization\n
\t\treturn s.join("&").replace(r20, "+");\n
\n
\t\tfunction buildParams( prefix, obj ) {\n
\t\t\tif ( jQuery.isArray(obj) ) {\n
\t\t\t\t// Serialize array item.\n
\t\t\t\tjQuery.each( obj, function( i, v ) {\n
\t\t\t\t\tif ( traditional || /\\[\\]$/.test( prefix ) ) {\n
\t\t\t\t\t\t// Treat each array item as a scalar.\n
\t\t\t\t\t\tadd( prefix, v );\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\t// If array item is non-scalar (array or object), encode its\n
\t\t\t\t\t\t// numeric index to resolve deserialization ambiguity issues.\n
\t\t\t\t\t\t// Note that rack (as of 1.0.0) can\'t currently deserialize\n
\t\t\t\t\t\t// nested arrays properly, and attempting to do so may cause\n
\t\t\t\t\t\t// a server error. Possible fixes are to modify rack\'s\n
\t\t\t\t\t\t// deserialization algorithm or to provide an option or flag\n
\t\t\t\t\t\t// to force array serialization to be shallow.\n
\t\t\t\t\t\tbuildParams( prefix + "[" + ( typeof v === "object" || jQuery.isArray(v) ? i : "" ) + "]", v );\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t\t\t\n
\t\t\t} else if ( !traditional && obj != null && typeof obj === "object" ) {\n
\t\t\t\t// Serialize object item.\n
\t\t\t\tjQuery.each( obj, function( k, v ) {\n
\t\t\t\t\tbuildParams( prefix + "[" + k + "]", v );\n
\t\t\t\t});\n
\t\t\t\t\t\n
\t\t\t} else {\n
\t\t\t\t// Serialize scalar item.\n
\t\t\t\tadd( prefix, obj );\n
\t\t\t}\n
\t\t}\n
\n
\t\tfunction add( key, value ) {\n
\t\t\t// If value is a function, invoke it and return its value\n
\t\t\tvalue = jQuery.isFunction(value) ? value() : value;\n
\t\t\ts[ s.length ] = encodeURIComponent(key) + "=" + encodeURIComponent(value);\n
\t\t}\n
\t}\n
});\n
var elemdisplay = {},\n
\trfxtypes = /toggle|show|hide/,\n
\trfxnum = /^([+-]=)?([\\d+-.]+)(.*)$/,\n
\ttimerId,\n
\tfxAttrs = [\n
\t\t// height animations\n
\t\t[ "height", "marginTop", "marginBottom", "paddingTop", "paddingBottom" ],\n
\t\t// width animations\n
\t\t[ "width", "marginLeft", "marginRight", "paddingLeft", "paddingRight" ],\n
\t\t// opacity animations\n
\t\t[ "opacity" ]\n
\t];\n
\n
jQuery.fn.extend({\n
\tshow: function( speed, callback ) {\n
\t\tif ( speed || speed === 0) {\n
\t\t\treturn this.animate( genFx("show", 3), speed, callback);\n
\n
\t\t} else {\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\t\tvar old = jQuery.data(this[i], "olddisplay");\n
\n
\t\t\t\tthis[i].style.display = old || "";\n
\n
\t\t\t\tif ( jQuery.css(this[i], "display") === "none" ) {\n
\t\t\t\t\tvar nodeName = this[i].nodeName, display;\n
\n
\t\t\t\t\tif ( elemdisplay[ nodeName ] ) {\n
\t\t\t\t\t\tdisplay = elemdisplay[ nodeName ];\n
\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tvar elem = jQuery("<" + nodeName + " />").appendTo("body");\n
\n
\t\t\t\t\t\tdisplay = elem.css("display");\n
\n
\t\t\t\t\t\tif ( display === "none" ) {\n
\t\t\t\t\t\t\tdisplay = "block";\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\telem.remove();\n
\n
\t\t\t\t\t\telemdisplay[ nodeName ] = display;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\tjQuery.data(this[i], "olddisplay", display);\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// Set the display of the elements in a second loop\n
\t\t\t// to avoid the constant reflow\n
\t\t\tfor ( var j = 0, k = this.length; j < k; j++ ) {\n
\t\t\t\tthis[j].style.display = jQuery.data(this[j], "olddisplay") || "";\n
\t\t\t}\n
\n
\t\t\treturn this;\n
\t\t}\n
\t},\n
\n
\thide: function( speed, callback ) {\n
\t\tif ( speed || speed === 0 ) {\n
\t\t\treturn this.animate( genFx("hide", 3), speed, callback);\n
\n
\t\t} else {\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ) {\n
\t\t\t\tvar old = jQuery.data(this[i], "olddisplay");\n
\t\t\t\tif ( !old && old !== "none" ) {\n
\t\t\t\t\tjQuery.data(this[i], "olddisplay", jQuery.css(this[i], "display"));\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// Set the display of the elements in a second loop\n
\t\t\t// to avoid the constant reflow\n
\t\t\tfor ( var j = 0, k = this.length; j < k; j++ ) {\n
\t\t\t\tthis[j].style.display = "none";\n
\t\t\t}\n
\n
\t\t\treturn this;\n
\t\t}\n
\t},\n
\n
\t// Save the old toggle function\n
\t_toggle: jQuery.fn.toggle,\n
\n
\ttoggle: function( fn, fn2 ) {\n
\t\tvar bool = typeof fn === "boolean";\n
\n
\t\tif ( jQuery.isFunction(fn) && jQuery.isFunction(fn2) ) {\n
\t\t\tthis._toggle.apply( this, arguments );\n
\n
\t\t} else if ( fn == null || bool ) {\n
\t\t\tthis.each(function() {\n
\t\t\t\tvar state = bool ? fn : jQuery(this).is(":hidden");\n
\t\t\t\tjQuery(this)[ state ? "show" : "hide" ]();\n
\t\t\t});\n
\n
\t\t} else {\n
\t\t\tthis.animate(genFx("toggle", 3), fn, fn2);\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\n
\tfadeTo: function( speed, to, callback ) {\n
\t\treturn this.filter(":hidden").css("opacity", 0).show().end()\n
\t\t\t\t\t.animate({opacity: to}, speed, callback);\n
\t},\n
\n
\tanimate: function( prop, speed, easing, callback ) {\n
\t\tvar optall = jQuery.speed(speed, easing, callback);\n
\n
\t\tif ( jQuery.isEmptyObject( prop ) ) {\n
\t\t\treturn this.each( optall.complete );\n
\t\t}\n
\n
\t\treturn this[ optall.queue === false ? "each" : "queue" ](function() {\n
\t\t\tvar opt = jQuery.extend({}, optall), p,\n
\t\t\t\thidden = this.nodeType === 1 && jQuery(this).is(":hidden"),\n
\t\t\t\tself = this;\n
\n
\t\t\tfor ( p in prop ) {\n
\t\t\t\tvar name = p.replace(rdashAlpha, fcamelCase);\n
\n
\t\t\t\tif ( p !== name ) {\n
\t\t\t\t\tprop[ name ] = prop[ p ];\n
\t\t\t\t\tdelete prop[ p ];\n
\t\t\t\t\tp = name;\n
\t\t\t\t}\n
\n
\t\t\t\tif ( prop[p] === "hide" && hidden || prop[p] === "show" && !hidden ) {\n
\t\t\t\t\treturn opt.complete.call(this);\n
\t\t\t\t}\n
\n
\t\t\t\tif ( ( p === "height" || p === "width" ) && this.style ) {\n
\t\t\t\t\t// Store display property\n
\t\t\t\t\topt.display = jQuery.css(this, "display");\n
\n
\t\t\t\t\t// Make sure that nothing sneaks out\n
\t\t\t\t\topt.overflow = this.style.overflow;\n
\t\t\t\t}\n
\n
\t\t\t\tif ( jQuery.isArray( prop[p] ) ) {\n
\t\t\t\t\t// Create (if needed) and add to specialEasing\n
\t\t\t\t\t(opt.specialEasing = opt.specialEasing || {})[p] = prop[p][1];\n
\t\t\t\t\tprop[p] = prop[p][0];\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tif ( opt.overflow != null ) {\n
\t\t\t\tthis.style.overflow = "hidden";\n
\t\t\t}\n
\n
\t\t\topt.curAnim = jQuery.extend({}, prop);\n
\n
\t\t\tjQuery.each( prop, function( name, val ) {\n
\t\t\t\tvar e = new jQuery.fx( self, opt, name );\n
\n
\t\t\t\tif ( rfxtypes.test(val) ) {\n
\t\t\t\t\te[ val === "toggle" ? hidden ? "show" : "hide" : val ]( prop );\n
\n
\t\t\t\t} else {\n
\t\t\t\t\tvar parts = rfxnum.exec(val),\n
\t\t\t\t\t\tstart = e.cur(true) || 0;\n
\n
\t\t\t\t\tif ( parts ) {\n
\t\t\t\t\t\tvar end = parseFloat( parts[2] ),\n
\t\t\t\t\t\t\tunit = parts[3] || "px";\n
\n
\t\t\t\t\t\t// We need to compute starting value\n
\t\t\t\t\t\tif ( unit !== "px" ) {\n
\t\t\t\t\t\t\tself.style[ name ] = (end || 1) + unit;\n
\t\t\t\t\t\t\tstart = ((end || 1) / e.cur(true)) * start;\n
\t\t\t\t\t\t\tself.style[ name ] = start + unit;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// If a +=/-= token was provided, we\'re doing a relative animation\n
\t\t\t\t\t\tif ( parts[1] ) {\n
\t\t\t\t\t\t\tend = ((parts[1] === "-=" ? -1 : 1) * end) + start;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\te.custom( start, end, unit );\n
\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\te.custom( start, val, "" );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\t// For JS strict compliance\n
\t\t\treturn true;\n
\t\t});\n
\t},\n
\n
\tstop: function( clearQueue, gotoEnd ) {\n
\t\tvar timers = jQuery.timers;\n
\n
\t\tif ( clearQueue ) {\n
\t\t\tthis.queue([]);\n
\t\t}\n
\n
\t\tthis.each(function() {\n
\t\t\t// go in reverse order so anything added to the queue during the loop is ignored\n
\t\t\tfor ( var i = timers.length - 1; i >= 0; i-- ) {\n
\t\t\t\tif ( timers[i].elem === this ) {\n
\t\t\t\t\tif (gotoEnd) {\n
\t\t\t\t\t\t// force the next step to be the last\n
\t\t\t\t\t\ttimers[i](true);\n
\t\t\t\t\t}\n
\n
\t\t\t\t\ttimers.splice(i, 1);\n
\t\t\t\t}\n
\t\t\t}\n
\t\t});\n
\n
\t\t// start the next in the queue if the last step wasn\'t forced\n
\t\tif ( !gotoEnd ) {\n
\t\t\tthis.dequeue();\n
\t\t}\n
\n
\t\treturn this;\n
\t}\n
\n
});\n
\n
// Generate shortcuts for custom animations\n
jQuery.each({\n
\tslideDown: genFx("show", 1),\n
\tslideUp: genFx("hide", 1),\n
\tslideToggle: genFx("toggle", 1),\n
\tfadeIn: { opacity: "show" },\n
\tfadeOut: { opacity: "hide" }\n
}, function( name, props ) {\n
\tjQuery.fn[ name ] = function( speed, callback ) {\n
\t\treturn this.animate( props, speed, callback );\n
\t};\n
});\n
\n
jQuery.extend({\n
\tspeed: function( speed, easing, fn ) {\n
\t\tvar opt = speed && typeof speed === "object" ? speed : {\n
\t\t\tcomplete: fn || !fn && easing ||\n
\t\t\t\tjQuery.isFunction( speed ) && speed,\n
\t\t\tduration: speed,\n
\t\t\teasing: fn && easing || easing && !jQuery.isFunction(easing) && easing\n
\t\t};\n
\n
\t\topt.duration = jQuery.fx.off ? 0 : typeof opt.duration === "number" ? opt.duration :\n
\t\t\tjQuery.fx.speeds[opt.duration] || jQuery.fx.speeds._default;\n
\n
\t\t// Queueing\n
\t\topt.old = opt.complete;\n
\t\topt.complete = function() {\n
\t\t\tif ( opt.queue !== false ) {\n
\t\t\t\tjQuery(this).dequeue();\n
\t\t\t}\n
\t\t\tif ( jQuery.isFunction( opt.old ) ) {\n
\t\t\t\topt.old.call( this );\n
\t\t\t}\n
\t\t};\n
\n
\t\treturn opt;\n
\t},\n
\n
\teasing: {\n
\t\tlinear: function( p, n, firstNum, diff ) {\n
\t\t\treturn firstNum + diff * p;\n
\t\t},\n
\t\tswing: function( p, n, firstNum, diff ) {\n
\t\t\treturn ((-Math.cos(p*Math.PI)/2) + 0.5) * diff + firstNum;\n
\t\t}\n
\t},\n
\n
\ttimers: [],\n
\n
\tfx: function( elem, options, prop ) {\n
\t\tthis.options = options;\n
\t\tthis.elem = elem;\n
\t\tthis.prop = prop;\n
\n
\t\tif ( !options.orig ) {\n
\t\t\toptions.orig = {};\n
\t\t}\n
\t}\n
\n
});\n
\n
jQuery.fx.prototype = {\n
\t// Simple function for setting a style value\n
\tupdate: function() {\n
\t\tif ( this.options.step ) {\n
\t\t\tthis.options.step.call( this.elem, this.now, this );\n
\t\t}\n
\n
\t\t(jQuery.fx.step[this.prop] || jQuery.fx.step._default)( this );\n
\n
\t\t// Set display property to block for height/width animations\n
\t\tif ( ( this.prop === "height" || this.prop === "width" ) && this.elem.style ) {\n
\t\t\tthis.elem.style.display = "block";\n
\t\t}\n
\t},\n
\n
\t// Get the current size\n
\tcur: function( force ) {\n
\t\tif ( this.elem[this.prop] != null && (!this.elem.style || this.elem.style[this.prop] == null) ) {\n
\t\t\treturn this.elem[ this.prop ];\n
\t\t}\n
\n
\t\tvar r = parseFloat(jQuery.css(this.elem, this.prop, force));\n
\t\treturn r && r > -10000 ? r : parseFloat(jQuery.curCSS(this.elem, this.prop)) || 0;\n
\t},\n
\n
\t// Start an animation from one number to another\n
\tcustom: function( from, to, unit ) {\n
\t\tthis.startTime = now();\n
\t\tthis.start = from;\n
\t\tthis.end = to;\n
\t\tthis.unit = unit || this.unit || "px";\n
\t\tthis.now = this.start;\n
\t\tthis.pos = this.state = 0;\n
\n
\t\tvar self = this;\n
\t\tfunction t( gotoEnd ) {\n
\t\t\treturn self.step(gotoEnd);\n
\t\t}\n
\n
\t\tt.elem = this.elem;\n
\n
\t\tif ( t() && jQuery.timers.push(t) && !timerId ) {\n
\t\t\ttimerId = setInterval(jQuery.fx.tick, 13);\n
\t\t}\n
\t},\n
\n
\t// Simple \'show\' function\n
\tshow: function() {\n
\t\t// Remember where we started, so that we can go back to it later\n
\t\tthis.options.orig[this.prop] = jQuery.style( this.elem, this.prop );\n
\t\tthis.options.show = true;\n
\n
\t\t// Begin the animation\n
\t\t// Make sure that we start at a small width/height to avoid any\n
\t\t// flash of content\n
\t\tthis.custom(this.prop === "width" || this.prop === "height" ? 1 : 0, this.cur());\n
\n
\t\t// Start by showing the element\n
\t\tjQuery( this.elem ).show();\n
\t},\n
\n
\t// Simple \'hide\' function\n
\thide: function() {\n
\t\t// Remember where we started, so that we can go back to it later\n
\t\tthis.options.orig[this.prop] = jQuery.style( this.elem, this.prop );\n
\t\tthis.options.hide = true;\n
\n
\t\t// Begin the animation\n
\t\tthis.custom(this.cur(), 0);\n
\t},\n
\n
\t// Each step of an animation\n
\tstep: function( gotoEnd ) {\n
\t\tvar t = now(), done = true;\n
\n
\t\tif ( gotoEnd || t >= this.options.duration + this.startTime ) {\n
\t\t\tthis.now = this.end;\n
\t\t\tthis.pos = this.state = 1;\n
\t\t\tthis.update();\n
\n
\t\t\tthis.options.curAnim[ this.prop ] = true;\n
\n
\t\t\tfor ( var i in this.options.curAnim ) {\n
\t\t\t\tif ( this.options.curAnim[i] !== true ) {\n
\t\t\t\t\tdone = false;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tif ( done ) {\n
\t\t\t\tif ( this.options.display != null ) {\n
\t\t\t\t\t// Reset the overflow\n
\t\t\t\t\tthis.elem.style.overflow = this.options.overflow;\n
\n
\t\t\t\t\t// Reset the display\n
\t\t\t\t\tvar old = jQuery.data(this.elem, "olddisplay");\n
\t\t\t\t\tthis.elem.style.display = old ? old : this.options.display;\n
\n
\t\t\t\t\tif ( jQuery.css(this.elem, "display") === "none" ) {\n
\t\t\t\t\t\tthis.elem.style.display = "block";\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\t// Hide the element if the "hide" operation was done\n
\t\t\t\tif ( this.options.hide ) {\n
\t\t\t\t\tjQuery(this.elem).hide();\n
\t\t\t\t}\n
\n
\t\t\t\t// Reset the properties, if the item has been hidden or shown\n
\t\t\t\tif ( this.options.hide || this.options.show ) {\n
\t\t\t\t\tfor ( var p in this.options.curAnim ) {\n
\t\t\t\t\t\tjQuery.style(this.elem, p, this.options.orig[p]);\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\t// Execute the complete function\n
\t\t\t\tthis.options.complete.call( this.elem );\n
\t\t\t}\n
\n
\t\t\treturn false;\n
\n
\t\t} else {\n
\t\t\tvar n = t - this.startTime;\n
\t\t\tthis.state = n / this.options.duration;\n
\n
\t\t\t// Perform the easing function, defaults to swing\n
\t\t\tvar specialEasing = this.options.specialEasing && this.options.specialEasing[this.prop];\n
\t\t\tvar defaultEasing = this.options.easing || (jQuery.easing.swing ? "swing" : "linear");\n
\t\t\tthis.pos = jQuery.easing[specialEasing || defaultEasing](this.state, n, 0, 1, this.options.duration);\n
\t\t\tthis.now = this.start + ((this.end - this.start) * this.pos);\n
\n
\t\t\t// Perform the next step of the animation\n
\t\t\tthis.update();\n
\t\t}\n
\n
\t\treturn true;\n
\t}\n
};\n
\n
jQuery.extend( jQuery.fx, {\n
\ttick: function() {\n
\t\tvar timers = jQuery.timers;\n
\n
\t\tfor ( var i = 0; i < timers.length; i++ ) {\n
\t\t\tif ( !timers[i]() ) {\n
\t\t\t\ttimers.splice(i--, 1);\n
\t\t\t}\n
\t\t}\n
\n
\t\tif ( !timers.length ) {\n
\t\t\tjQuery.fx.stop();\n
\t\t}\n
\t},\n
\t\t\n
\tstop: function() {\n
\t\tclearInterval( timerId );\n
\t\ttimerId = null;\n
\t},\n
\t\n
\tspeeds: {\n
\t\tslow: 600,\n
 \t\tfast: 200,\n
 \t\t// Default speed\n
 \t\t_default: 400\n
\t},\n
\n
\tstep: {\n
\t\topacity: function( fx ) {\n
\t\t\tjQuery.style(fx.elem, "opacity", fx.now);\n
\t\t},\n
\n
\t\t_default: function( fx ) {\n
\t\t\tif ( fx.elem.style && fx.elem.style[ fx.prop ] != null ) {\n
\t\t\t\tfx.elem.style[ fx.prop ] = (fx.prop === "width" || fx.prop === "height" ? Math.max(0, fx.now) : fx.now) + fx.unit;\n
\t\t\t} else {\n
\t\t\t\tfx.elem[ fx.prop ] = fx.now;\n
\t\t\t}\n
\t\t}\n
\t}\n
});\n
\n
if ( jQuery.expr && jQuery.expr.filters ) {\n
\tjQuery.expr.filters.animated = function( elem ) {\n
\t\treturn jQuery.grep(jQuery.timers, function( fn ) {\n
\t\t\treturn elem === fn.elem;\n
\t\t}).length;\n
\t};\n
}\n
\n
function genFx( type, num ) {\n
\tvar obj = {};\n
\n
\tjQuery.each( fxAttrs.concat.apply([], fxAttrs.slice(0,num)), function() {\n
\t\tobj[ this ] = type;\n
\t});\n
\n
\treturn obj;\n
}\n
if ( "getBoundingClientRect" in document.documentElement ) {\n
\tjQuery.fn.offset = function( options ) {\n
\t\tvar elem = this[0];\n
\n
\t\tif ( options ) { \n
\t\t\treturn this.each(function( i ) {\n
\t\t\t\tjQuery.offset.setOffset( this, options, i );\n
\t\t\t});\n
\t\t}\n
\n
\t\tif ( !elem || !elem.ownerDocument ) {\n
\t\t\treturn null;\n
\t\t}\n
\n
\t\tif ( elem === elem.ownerDocument.body ) {\n
\t\t\treturn jQuery.offset.bodyOffset( elem );\n
\t\t}\n
\n
\t\tvar box = elem.getBoundingClientRect(), doc = elem.ownerDocument, body = doc.body, docElem = doc.documentElement,\n
\t\t\tclientTop = docElem.clientTop || body.clientTop || 0, clientLeft = docElem.clientLeft || body.clientLeft || 0,\n
\t\t\ttop  = box.top  + (self.pageYOffset || jQuery.support.boxModel && docElem.scrollTop  || body.scrollTop ) - clientTop,\n
\t\t\tleft = box.left + (self.pageXOffset || jQuery.support.boxModel && docElem.scrollLeft || body.scrollLeft) - clientLeft;\n
\n
\t\treturn { top: top, left: left };\n
\t};\n
\n
} else {\n
\tjQuery.fn.offset = function( options ) {\n
\t\tvar elem = this[0];\n
\n
\t\tif ( options ) { \n
\t\t\treturn this.each(function( i ) {\n
\t\t\t\tjQuery.offset.setOffset( this, options, i );\n
\t\t\t});\n
\t\t}\n
\n
\t\tif ( !elem || !elem.ownerDocument ) {\n
\t\t\treturn null;\n
\t\t}\n
\n
\t\tif ( elem === elem.ownerDocument.body ) {\n
\t\t\treturn jQuery.offset.bodyOffset( elem );\n
\t\t}\n
\n
\t\tjQuery.offset.initialize();\n
\n
\t\tvar offsetParent = elem.offsetParent, prevOffsetParent = elem,\n
\t\t\tdoc = elem.ownerDocument, computedStyle, docElem = doc.documentElement,\n
\t\t\tbody = doc.body, defaultView = doc.defaultView,\n
\t\t\tprevComputedStyle = defaultView ? defaultView.getComputedStyle( elem, null ) : elem.currentStyle,\n
\t\t\ttop = elem.offsetTop, left = elem.offsetLeft;\n
\n
\t\twhile ( (elem = elem.parentNode) && elem !== body && elem !== docElem ) {\n
\t\t\tif ( jQuery.offset.supportsFixedPosition && prevComputedStyle.position === "fixed" ) {\n
\t\t\t\tbreak;\n
\t\t\t}\n
\n
\t\t\tcomputedStyle = defaultView ? defaultView.getComputedStyle(elem, null) : elem.currentStyle;\n
\t\t\ttop  -= elem.scrollTop;\n
\t\t\tleft -= elem.scrollLeft;\n
\n
\t\t\tif ( elem === offsetParent ) {\n
\t\t\t\ttop  += elem.offsetTop;\n
\t\t\t\tleft += elem.offsetLeft;\n
\n
\t\t\t\tif ( jQuery.offset.doesNotAddBorder && !(jQuery.offset.doesAddBorderForTableAndCells && /^t(able|d|h)$/i.test(elem.nodeName)) ) {\n
\t\t\t\t\ttop  += parseFloat( computedStyle.borderTopWidth  ) || 0;\n
\t\t\t\t\tleft += parseFloat( computedStyle.borderLeftWidth ) || 0;\n
\t\t\t\t}\n
\n
\t\t\t\tprevOffsetParent = offsetParent, offsetParent = elem.offsetParent;\n
\t\t\t}\n
\n
\t\t\tif ( jQuery.offset.subtractsBorderForOverflowNotVisible && computedStyle.overflow !== "visible" ) {\n
\t\t\t\ttop  += parseFloat( computedStyle.borderTopWidth  ) || 0;\n
\t\t\t\tleft += parseFloat( computedStyle.borderLeftWidth ) || 0;\n
\t\t\t}\n
\n
\t\t\tprevComputedStyle = computedStyle;\n
\t\t}\n
\n
\t\tif ( prevComputedStyle.position === "relative" || prevComputedStyle.position === "static" ) {\n
\t\t\ttop  += body.offsetTop;\n
\t\t\tleft += body.offsetLeft;\n
\t\t}\n
\n
\t\tif ( jQuery.offset.supportsFixedPosition && prevComputedStyle.position === "fixed" ) {\n
\t\t\ttop  += Math.max( docElem.scrollTop, body.scrollTop );\n
\t\t\tleft += Math.max( docElem.scrollLeft, body.scrollLeft );\n
\t\t}\n
\n
\t\treturn { top: top, left: left };\n
\t};\n
}\n
\n
jQuery.offset = {\n
\tinitialize: function() {\n
\t\tvar body = document.body, container = document.createElement("div"), innerDiv, checkDiv, table, td, bodyMarginTop = parseFloat( jQuery.curCSS(body, "marginTop", true) ) || 0,\n
\t\t\thtml = "<div style=\'position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;\'><div></div></div><table style=\'position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;\' cellpadding=\'0\' cellspacing=\'0\'><tr><td></td></tr></table>";\n
\n
\t\tjQuery.extend( container.style, { position: "absolute", top: 0, left: 0, margin: 0, border: 0, width: "1px", height: "1px", visibility: "hidden" } );\n
\n
\t\tcontainer.innerHTML = html;\n
\t\tbody.insertBefore( container, body.firstChild );\n
\t\tinnerDiv = container.firstChild;\n
\t\tcheckDiv = innerDiv.firstChild;\n
\t\ttd = innerDiv.nextSibling.firstChild.firstChild;\n
\n
\t\tthis.doesNotAddBorder = (checkDiv.offsetTop !== 5);\n
\t\tthis.doesAddBorderForTableAndCells = (td.offsetTop === 5);\n
\n
\t\tcheckDiv.style.position = "fixed", checkDiv.style.top = "20px";\n
\t\t// safari subtracts parent border width here which is 5px\n
\t\tthis.supportsFixedPosition = (checkDiv.offsetTop === 20 || checkDiv.offsetTop === 15);\n
\t\tcheckDiv.style.position = checkDiv.style.top = "";\n
\n
\t\tinnerDiv.style.overflow = "hidden", innerDiv.style.position = "relative";\n
\t\tthis.subtractsBorderForOverflowNotVisible = (checkDiv.offsetTop === -5);\n
\n
\t\tthis.doesNotIncludeMarginInBodyOffset = (body.offsetTop !== bodyMarginTop);\n
\n
\t\tbody.removeChild( container );\n
\t\tbody = container = innerDiv = checkDiv = table = td = null;\n
\t\tjQuery.offset.initialize = jQuery.noop;\n
\t},\n
\n
\tbodyOffset: function( body ) {\n
\t\tvar top = body.offsetTop, left = body.offsetLeft;\n
\n
\t\tjQuery.offset.initialize();\n
\n
\t\tif ( jQuery.offset.doesNotIncludeMarginInBodyOffset ) {\n
\t\t\ttop  += parseFloat( jQuery.curCSS(body, "marginTop",  true) ) || 0;\n
\t\t\tleft += parseFloat( jQuery.curCSS(body, "marginLeft", true) ) || 0;\n
\t\t}\n
\n
\t\treturn { top: top, left: left };\n
\t},\n
\t\n
\tsetOffset: function( elem, options, i ) {\n
\t\t// set position first, in-case top/left are set even on static elem\n
\t\tif ( /static/.test( jQuery.curCSS( elem, "position" ) ) ) {\n
\t\t\telem.style.position = "relative";\n
\t\t}\n
\t\tvar curElem   = jQuery( elem ),\n
\t\t\tcurOffset = curElem.offset(),\n
\t\t\tcurTop    = parseInt( jQuery.curCSS( elem, "top",  true ), 10 ) || 0,\n
\t\t\tcurLeft   = parseInt( jQuery.curCSS( elem, "left", true ), 10 ) || 0;\n
\n
\t\tif ( jQuery.isFunction( options ) ) {\n
\t\t\toptions = options.call( elem, i, curOffset );\n
\t\t}\n
\n
\t\tvar props = {\n
\t\t\ttop:  (options.top  - curOffset.top)  + curTop,\n
\t\t\tleft: (options.left - curOffset.left) + curLeft\n
\t\t};\n
\t\t\n
\t\tif ( "using" in options ) {\n
\t\t\toptions.using.call( elem, props );\n
\t\t} else {\n
\t\t\tcurElem.css( props );\n
\t\t}\n
\t}\n
};\n
\n
\n
jQuery.fn.extend({\n
\tposition: function() {\n
\t\tif ( !this[0] ) {\n
\t\t\treturn null;\n
\t\t}\n
\n
\t\tvar elem = this[0],\n
\n
\t\t// Get *real* offsetParent\n
\t\toffsetParent = this.offsetParent(),\n
\n
\t\t// Get correct offsets\n
\t\toffset       = this.offset(),\n
\t\tparentOffset = /^body|html$/i.test(offsetParent[0].nodeName) ? { top: 0, left: 0 } : offsetParent.offset();\n
\n
\t\t// Subtract element margins\n
\t\t// note: when an element has margin: auto the offsetLeft and marginLeft\n
\t\t// are the same in Safari causing offset.left to incorrectly be 0\n
\t\toffset.top  -= parseFloat( jQuery.curCSS(elem, "marginTop",  true) ) || 0;\n
\t\toffset.left -= parseFloat( jQuery.curCSS(elem, "marginLeft", true) ) || 0;\n
\n
\t\t// Add offsetParent borders\n
\t\tparentOffset.top  += parseFloat( jQuery.curCSS(offsetParent[0], "borderTopWidth",  true) ) || 0;\n
\t\tparentOffset.left += parseFloat( jQuery.curCSS(offsetParent[0], "borderLeftWidth", true) ) || 0;\n
\n
\t\t// Subtract the two offsets\n
\t\treturn {\n
\t\t\ttop:  offset.top  - parentOffset.top,\n
\t\t\tleft: offset.left - parentOffset.left\n
\t\t};\n
\t},\n
\n
\toffsetParent: function() {\n
\t\treturn this.map(function() {\n
\t\t\tvar offsetParent = this.offsetParent || document.body;\n
\t\t\twhile ( offsetParent && (!/^body|html$/i.test(offsetParent.nodeName) && jQuery.css(offsetParent, "position") === "static") ) {\n
\t\t\t\toffsetParent = offsetParent.offsetParent;\n
\t\t\t}\n
\t\t\treturn offsetParent;\n
\t\t});\n
\t}\n
});\n
\n
\n
// Create scrollLeft and scrollTop methods\n
jQuery.each( ["Left", "Top"], function( i, name ) {\n
\tvar method = "scroll" + name;\n
\n
\tjQuery.fn[ method ] = function(val) {\n
\t\tvar elem = this[0], win;\n
\t\t\n
\t\tif ( !elem ) {\n
\t\t\treturn null;\n
\t\t}\n
\n
\t\tif ( val !== undefined ) {\n
\t\t\t// Set the scroll offset\n
\t\t\treturn this.each(function() {\n
\t\t\t\twin = getWindow( this );\n
\n
\t\t\t\tif ( win ) {\n
\t\t\t\t\twin.scrollTo(\n
\t\t\t\t\t\t!i ? val : jQuery(win).scrollLeft(),\n
\t\t\t\t\t\t i ? val : jQuery(win).scrollTop()\n
\t\t\t\t\t);\n
\n
\t\t\t\t} else {\n
\t\t\t\t\tthis[ method ] = val;\n
\t\t\t\t}\n
\t\t\t});\n
\t\t} else {\n
\t\t\twin = getWindow( elem );\n
\n
\t\t\t// Return the scroll offset\n
\t\t\treturn win ? ("pageXOffset" in win) ? win[ i ? "pageYOffset" : "pageXOffset" ] :\n
\t\t\t\tjQuery.support.boxModel && win.document.documentElement[ method ] ||\n
\t\t\t\t\twin.document.body[ method ] :\n
\t\t\t\telem[ method ];\n
\t\t}\n
\t};\n
});\n
\n
function getWindow( elem ) {\n
\treturn ("scrollTo" in elem && elem.document) ?\n
\t\telem :\n
\t\telem.nodeType === 9 ?\n
\t\t\telem.defaultView || elem.parentWindow :\n
\t\t\tfalse;\n
}\n
// Create innerHeight, innerWidth, outerHeight and outerWidth methods\n
jQuery.each([ "Height", "Width" ], function( i, name ) {\n
\n
\tvar type = name.toLowerCase();\n
\n
\t// innerHeight and innerWidth\n
\tjQuery.fn["inner" + name] = function() {\n
\t\treturn this[0] ?\n
\t\t\tjQuery.css( this[0], type, false, "padding" ) :\n
\t\t\tnull;\n
\t};\n
\n
\t// outerHeight and outerWidth\n
\tjQuery.fn["outer" + name] = function( margin ) {\n
\t\treturn this[0] ?\n
\t\t\tjQuery.css( this[0], type, false, margin ? "margin" : "border" ) :\n
\t\t\tnull;\n
\t};\n
\n
\tjQuery.fn[ type ] = function( size ) {\n
\t\t// Get window width or height\n
\t\tvar elem = this[0];\n
\t\tif ( !elem ) {\n
\t\t\treturn size == null ? null : this;\n
\t\t}\n
\t\t\n
\t\tif ( jQuery.isFunction( size ) ) {\n
\t\t\treturn this.each(function( i ) {\n
\t\t\t\tvar self = jQuery( this );\n
\t\t\t\tself[ type ]( size.call( this, i, self[ type ]() ) );\n
\t\t\t});\n
\t\t}\n
\n
\t\treturn ("scrollTo" in elem && elem.document) ? // does it walk and quack like a window?\n
\t\t\t// Everyone else use document.documentElement or document.body depending on Quirks vs Standards mode\n
\t\t\telem.document.compatMode === "CSS1Compat" && elem.document.documentElement[ "client" + name ] ||\n
\t\t\telem.document.body[ "client" + name ] :\n
\n
\t\t\t// Get document width or height\n
\t\t\t(elem.nodeType === 9) ? // is it a document\n
\t\t\t\t// Either scroll[Width/Height] or offset[Width/Height], whichever is greater\n
\t\t\t\tMath.max(\n
\t\t\t\t\telem.documentElement["client" + name],\n
\t\t\t\t\telem.body["scroll" + name], elem.documentElement["scroll" + name],\n
\t\t\t\t\telem.body["offset" + name], elem.documentElement["offset" + name]\n
\t\t\t\t) :\n
\n
\t\t\t\t// Get or set width or height on the element\n
\t\t\t\tsize === undefined ?\n
\t\t\t\t\t// Get width or height on the element\n
\t\t\t\t\tjQuery.css( elem, type ) :\n
\n
\t\t\t\t\t// Set the width or height on the element (default to pixels if value is unitless)\n
\t\t\t\t\tthis.css( type, typeof size === "string" ? size : size + "px" );\n
\t};\n
\n
});\n
// Expose jQuery to the global object\n
window.jQuery = window.$ = jQuery;\n
\n
})(window);\n


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
