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
            <value> <string>ts65545361.36</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery-1.3.2.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
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
            <value> <long>120619</long> </value>
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
      <tuple>
        <global name="Pdata" module="OFS.Image"/>
        <tuple/>
      </tuple>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*!\n
 * jQuery JavaScript Library v1.3.2\n
 * http://jquery.com/\n
 *\n
 * Copyright (c) 2009 John Resig\n
 * Dual licensed under the MIT and GPL licenses.\n
 * http://docs.jquery.com/License\n
 *\n
 * Date: 2009-02-19 17:34:21 -0500 (Thu, 19 Feb 2009)\n
 * Revision: 6246\n
 */\n
(function(){\n
\n
var \n
\t// Will speed up references to window, and allows munging its name.\n
\twindow = this,\n
\t// Will speed up references to undefined, and allows munging its name.\n
\tundefined,\n
\t// Map over jQuery in case of overwrite\n
\t_jQuery = window.jQuery,\n
\t// Map over the $ in case of overwrite\n
\t_$ = window.$,\n
\n
\tjQuery = window.jQuery = window.$ = function( selector, context ) {\n
\t\t// The jQuery object is actually just the init constructor \'enhanced\'\n
\t\treturn new jQuery.fn.init( selector, context );\n
\t},\n
\n
\t// A simple way to check for HTML strings or ID strings\n
\t// (both of which we optimize for)\n
\tquickExpr = /^[^<]*(<(.|\\s)+>)[^>]*$|^#([\\w-]+)$/,\n
\t// Is it a simple selector\n
\tisSimple = /^.[^:#\\[\\.,]*$/;\n
\n
jQuery.fn = jQuery.prototype = {\n
\tinit: function( selector, context ) {\n
\t\t// Make sure that a selection was provided\n
\t\tselector = selector || document;\n
\n
\t\t// Handle $(DOMElement)\n
\t\tif ( selector.nodeType ) {\n
\t\t\tthis[0] = selector;\n
\t\t\tthis.length = 1;\n
\t\t\tthis.context = selector;\n
\t\t\treturn this;\n
\t\t}\n
\t\t// Handle HTML strings\n
\t\tif ( typeof selector === "string" ) {\n
\t\t\t// Are we dealing with HTML string or an ID?\n
\t\t\tvar match = quickExpr.exec( selector );\n
\n
\t\t\t// Verify a match, and that no context was specified for #id\n
\t\t\tif ( match && (match[1] || !context) ) {\n
\n
\t\t\t\t// HANDLE: $(html) -> $(array)\n
\t\t\t\tif ( match[1] )\n
\t\t\t\t\tselector = jQuery.clean( [ match[1] ], context );\n
\n
\t\t\t\t// HANDLE: $("#id")\n
\t\t\t\telse {\n
\t\t\t\t\tvar elem = document.getElementById( match[3] );\n
\n
\t\t\t\t\t// Handle the case where IE and Opera return items\n
\t\t\t\t\t// by name instead of ID\n
\t\t\t\t\tif ( elem && elem.id != match[3] )\n
\t\t\t\t\t\treturn jQuery().find( selector );\n
\n
\t\t\t\t\t// Otherwise, we inject the element directly into the jQuery object\n
\t\t\t\t\tvar ret = jQuery( elem || [] );\n
\t\t\t\t\tret.context = document;\n
\t\t\t\t\tret.selector = selector;\n
\t\t\t\t\treturn ret;\n
\t\t\t\t}\n
\n
\t\t\t// HANDLE: $(expr, [context])\n
\t\t\t// (which is just equivalent to: $(content).find(expr)\n
\t\t\t} else\n
\t\t\t\treturn jQuery( context ).find( selector );\n
\n
\t\t// HANDLE: $(function)\n
\t\t// Shortcut for document ready\n
\t\t} else if ( jQuery.isFunction( selector ) )\n
\t\t\treturn jQuery( document ).ready( selector );\n
\n
\t\t// Make sure that old selector state is passed along\n
\t\tif ( selector.selector && selector.context ) {\n
\t\t\tthis.selector = selector.selector;\n
\t\t\tthis.context = selector.context;\n
\t\t}\n
\n
\t\treturn this.setArray(jQuery.isArray( selector ) ?\n
\t\t\tselector :\n
\t\t\tjQuery.makeArray(selector));\n
\t},\n
\n
\t// Start with an empty selector\n
\tselector: "",\n
\n
\t// The current version of jQuery being used\n
\tjquery: "1.3.2",\n
\n
\t// The number of elements contained in the matched element set\n
\tsize: function() {\n
\t\treturn this.length;\n
\t},\n
\n
\t// Get the Nth element in the matched element set OR\n
\t// Get the whole matched element set as a clean array\n
\tget: function( num ) {\n
\t\treturn num === undefined ?\n
\n
\t\t\t// Return a \'clean\' array\n
\t\t\tArray.prototype.slice.call( this ) :\n
\n
\t\t\t// Return just the object\n
\t\t\tthis[ num ];\n
\t},\n
\n
\t// Take an array of elements and push it onto the stack\n
\t// (returning the new matched element set)\n
\tpushStack: function( elems, name, selector ) {\n
\t\t// Build a new jQuery matched element set\n
\t\tvar ret = jQuery( elems );\n
\n
\t\t// Add the old object onto the stack (as a reference)\n
\t\tret.prevObject = this;\n
\n
\t\tret.context = this.context;\n
\n
\t\tif ( name === "find" )\n
\t\t\tret.selector = this.selector + (this.selector ? " " : "") + selector;\n
\t\telse if ( name )\n
\t\t\tret.selector = this.selector + "." + name + "(" + selector + ")";\n
\n
\t\t// Return the newly-formed element set\n
\t\treturn ret;\n
\t},\n
\n
\t// Force the current matched set of elements to become\n
\t// the specified array of elements (destroying the stack in the process)\n
\t// You should use pushStack() in order to do this, but maintain the stack\n
\tsetArray: function( elems ) {\n
\t\t// Resetting the length to 0, then using the native Array push\n
\t\t// is a super-fast way to populate an object with array-like properties\n
\t\tthis.length = 0;\n
\t\tArray.prototype.push.apply( this, elems );\n
\n
\t\treturn this;\n
\t},\n
\n
\t// Execute a callback for every element in the matched set.\n
\t// (You can seed the arguments with an array of args, but this is\n
\t// only used internally.)\n
\teach: function( callback, args ) {\n
\t\treturn jQuery.each( this, callback, args );\n
\t},\n
\n
\t// Determine the position of an element within\n
\t// the matched set of elements\n
\tindex: function( elem ) {\n
\t\t// Locate the position of the desired element\n
\t\treturn jQuery.inArray(\n
\t\t\t// If it receives a jQuery object, the first element is used\n
\t\t\telem && elem.jquery ? elem[0] : elem\n
\t\t, this );\n
\t},\n
\n
\tattr: function( name, value, type ) {\n
\t\tvar options = name;\n
\n
\t\t// Look for the case where we\'re accessing a style value\n
\t\tif ( typeof name === "string" )\n
\t\t\tif ( value === undefined )\n
\t\t\t\treturn this[0] && jQuery[ type || "attr" ]( this[0], name );\n
\n
\t\t\telse {\n
\t\t\t\toptions = {};\n
\t\t\t\toptions[ name ] = value;\n
\t\t\t}\n
\n
\t\t// Check to see if we\'re setting style values\n
\t\treturn this.each(function(i){\n
\t\t\t// Set all the styles\n
\t\t\tfor ( name in options )\n
\t\t\t\tjQuery.attr(\n
\t\t\t\t\ttype ?\n
\t\t\t\t\t\tthis.style :\n
\t\t\t\t\t\tthis,\n
\t\t\t\t\tname, jQuery.prop( this, options[ name ], type, i, name )\n
\t\t\t\t);\n
\t\t});\n
\t},\n
\n
\tcss: function( key, value ) {\n
\t\t// ignore negative width and height values\n
\t\tif ( (key == \'width\' || key == \'height\') && parseFloat(value) < 0 )\n
\t\t\tvalue = undefined;\n
\t\treturn this.attr( key, value, "curCSS" );\n
\t},\n
\n
\ttext: function( text ) {\n
\t\tif ( typeof text !== "object" && text != null )\n
\t\t\treturn this.empty().append( (this[0] && this[0].ownerDocument || document).createTextNode( text ) );\n
\n
\t\tvar ret = "";\n
\n
\t\tjQuery.each( text || this, function(){\n
\t\t\tjQuery.each( this.childNodes, function(){\n
\t\t\t\tif ( this.nodeType != 8 )\n
\t\t\t\t\tret += this.nodeType != 1 ?\n
\t\t\t\t\t\tthis.nodeValue :\n
\t\t\t\t\t\tjQuery.fn.text( [ this ] );\n
\t\t\t});\n
\t\t});\n
\n
\t\treturn ret;\n
\t},\n
\n
\twrapAll: function( html ) {\n
\t\tif ( this[0] ) {\n
\t\t\t// The elements to wrap the target around\n
\t\t\tvar wrap = jQuery( html, this[0].ownerDocument ).clone();\n
\n
\t\t\tif ( this[0].parentNode )\n
\t\t\t\twrap.insertBefore( this[0] );\n
\n
\t\t\twrap.map(function(){\n
\t\t\t\tvar elem = this;\n
\n
\t\t\t\twhile ( elem.firstChild )\n
\t\t\t\t\telem = elem.firstChild;\n
\n
\t\t\t\treturn elem;\n
\t\t\t}).append(this);\n
\t\t}\n
\n
\t\treturn this;\n
\t},\n
\n
\twrapInner: function( html ) {\n
\t\treturn this.each(function(){\n
\t\t\tjQuery( this ).contents().wrapAll( html );\n
\t\t});\n
\t},\n
\n
\twrap: function( html ) {\n
\t\treturn this.each(function(){\n
\t\t\tjQuery( this ).wrapAll( html );\n
\t\t});\n
\t},\n
\n
\tappend: function() {\n
\t\treturn this.domManip(arguments, true, function(elem){\n
\t\t\tif (this.nodeType == 1)\n
\t\t\t\tthis.appendChild( elem );\n
\t\t});\n
\t},\n
\n
\tprepend: function() {\n
\t\treturn this.domManip(arguments, true, function(elem){\n
\t\t\tif (this.nodeType == 1)\n
\t\t\t\tthis.insertBefore( elem, this.firstChild );\n
\t\t});\n
\t},\n
\n
\tbefore: function() {\n
\t\treturn this.domManip(arguments, false, function(elem){\n
\t\t\tthis.parentNode.insertBefore( elem, this );\n
\t\t});\n
\t},\n
\n
\tafter: function() {\n
\t\treturn this.domManip(arguments, false, function(elem){\n
\t\t\tthis.parentNode.insertBefore( elem, this.nextSibling );\n
\t\t});\n
\t},\n
\n
\tend: function() {\n
\t\treturn this.prevObject || jQuery( [] );\n
\t},\n
\n
\t// For internal use only.\n
\t// Behaves like an Array\'s method, not like a jQuery method.\n
\tpush: [].push,\n
\tsort: [].sort,\n
\tsplice: [].splice,\n
\n
\tfind: function( selector ) {\n
\t\tif ( this.length === 1 ) {\n
\t\t\tvar ret = this.pushStack( [], "find", selector );\n
\t\t\tret.length = 0;\n
\t\t\tjQuery.find( selector, this[0], ret );\n
\t\t\treturn ret;\n
\t\t} else {\n
\t\t\treturn this.pushStack( jQuery.unique(jQuery.map(this, function(elem){\n
\t\t\t\treturn jQuery.find( selector, elem );\n
\t\t\t})), "find", selector );\n
\t\t}\n
\t},\n
\n
\tclone: function( events ) {\n
\t\t// Do the clone\n
\t\tvar ret = this.map(function(){\n
\t\t\tif ( !jQuery.support.noCloneEvent && !jQuery.isXMLDoc(this) ) {\n
\t\t\t\t// IE copies events bound via attachEvent when\n
\t\t\t\t// using cloneNode. Calling detachEvent on the\n
\t\t\t\t// clone will also remove the events from the orignal\n
\t\t\t\t// In order to get around this, we use innerHTML.\n
\t\t\t\t// Unfortunately, this means some modifications to\n
\t\t\t\t// attributes in IE that are actually only stored\n
\t\t\t\t// as properties will not be copied (such as the\n
\t\t\t\t// the name attribute on an input).\n
\t\t\t\tvar html = this.outerHTML;\n
\t\t\t\tif ( !html ) {\n
\t\t\t\t\tvar div = this.ownerDocument.createElement("div");\n
\t\t\t\t\tdiv.appendChild( this.cloneNode(true) );\n
\t\t\t\t\thtml = div.innerHTML;\n
\t\t\t\t}\n
\n
\t\t\t\treturn jQuery.clean([html.replace(/ jQuery\\d+="(?:\\d+|null)"/g, "").replace(/^\\s*/, "")])[0];\n
\t\t\t} else\n
\t\t\t\treturn this.cloneNode(true);\n
\t\t});\n
\n
\t\t// Copy the events from the original to the clone\n
\t\tif ( events === true ) {\n
\t\t\tvar orig = this.find("*").andSelf(), i = 0;\n
\n
\t\t\tret.find("*").andSelf().each(function(){\n
\t\t\t\tif ( this.nodeName !== orig[i].nodeName )\n
\t\t\t\t\treturn;\n
\n
\t\t\t\tvar events = jQuery.data( orig[i], "events" );\n
\n
\t\t\t\tfor ( var type in events ) {\n
\t\t\t\t\tfor ( var handler in events[ type ] ) {\n
\t\t\t\t\t\tjQuery.event.add( this, type, events[ type ][ handler ], events[ type ][ handler ].data );\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\ti++;\n
\t\t\t});\n
\t\t}\n
\n
\t\t// Return the cloned set\n
\t\treturn ret;\n
\t},\n
\n
\tfilter: function( selector ) {\n
\t\treturn this.pushStack(\n
\t\t\tjQuery.isFunction( selector ) &&\n
\t\t\tjQuery.grep(this, function(elem, i){\n
\t\t\t\treturn selector.call( elem, i );\n
\t\t\t}) ||\n
\n
\t\t\tjQuery.multiFilter( selector, jQuery.grep(this, function(elem){\n
\t\t\t\treturn elem.nodeType === 1;\n
\t\t\t}) ), "filter", selector );\n
\t},\n
\n
\tclosest: function( selector ) {\n
\t\tvar pos = jQuery.expr.match.POS.test( selector ) ? jQuery(selector) : null,\n
\t\t\tcloser = 0;\n
\n
\t\treturn this.map(function(){\n
\t\t\tvar cur = this;\n
\t\t\twhile ( cur && cur.ownerDocument ) {\n
\t\t\t\tif ( pos ? pos.index(cur) > -1 : jQuery(cur).is(selector) ) {\n
\t\t\t\t\tjQuery.data(cur, "closest", closer);\n
\t\t\t\t\treturn cur;\n
\t\t\t\t}\n
\t\t\t\tcur = cur.parentNode;\n
\t\t\t\tcloser++;\n
\t\t\t}\n
\t\t});\n
\t},\n
\n
\tnot: function( selector ) {\n
\t\tif ( typeof selector === "string" )\n
\t\t\t// test special case where just one selector is passed in\n
\t\t\tif ( isSimple.test( selector ) )\n
\t\t\t\treturn this.pushStack( jQuery.multiFilter( selector, this, true ), "not", selector );\n
\t\t\telse\n
\t\t\t\tselector = jQuery.multiFilter( selector, this );\n
\n
\t\tvar isArrayLike = selector.length && selector[selector.length - 1] !== undefined && !selector.nodeType;\n
\t\treturn this.filter(function() {\n
\t\t\treturn isArrayLike ? jQuery.inArray( this, selector ) < 0 : this != selector;\n
\t\t});\n
\t},\n
\n
\tadd: function( selector ) {\n
\t\treturn this.pushStack( jQuery.unique( jQuery.merge(\n
\t\t\tthis.get(),\n
\t\t\ttypeof selector === "string" ?\n
\t\t\t\tjQuery( selector ) :\n
\t\t\t\tjQuery.makeArray( selector )\n
\t\t)));\n
\t},\n
\n
\tis: function( selector ) {\n
\t\treturn !!selector && jQuery.multiFilter( selector, this ).length > 0;\n
\t},\n
\n
\thasClass: function( selector ) {\n
\t\treturn !!selector && this.is( "." + selector );\n
\t},\n
\n
\tval: function( value ) {\n
\t\tif ( value === undefined ) {\t\t\t\n
\t\t\tvar elem = this[0];\n
\n
\t\t\tif ( elem ) {\n
\t\t\t\tif( jQuery.nodeName( elem, \'option\' ) )\n
\t\t\t\t\treturn (elem.attributes.value || {}).specified ? elem.value : elem.text;\n
\t\t\t\t\n
\t\t\t\t// We need to handle select boxes special\n
\t\t\t\tif ( jQuery.nodeName( elem, "select" ) ) {\n
\t\t\t\t\tvar index = elem.selectedIndex,\n
\t\t\t\t\t\tvalues = [],\n
\t\t\t\t\t\toptions = elem.options,\n
\t\t\t\t\t\tone = elem.type == "select-one";\n
\n
\t\t\t\t\t// Nothing was selected\n
\t\t\t\t\tif ( index < 0 )\n
\t\t\t\t\t\treturn null;\n
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
\t\t\t\t\t\t\tif ( one )\n
\t\t\t\t\t\t\t\treturn value;\n
\n
\t\t\t\t\t\t\t// Multi-Selects return an array\n
\t\t\t\t\t\t\tvalues.push( value );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\n
\t\t\t\t\treturn values;\t\t\t\t\n
\t\t\t\t}\n
\n
\t\t\t\t// Everything else, we just grab the value\n
\t\t\t\treturn (elem.value || "").replace(/\\r/g, "");\n
\n
\t\t\t}\n
\n
\t\t\treturn undefined;\n
\t\t}\n
\n
\t\tif ( typeof value === "number" )\n
\t\t\tvalue += \'\';\n
\n
\t\treturn this.each(function(){\n
\t\t\tif ( this.nodeType != 1 )\n
\t\t\t\treturn;\n
\n
\t\t\tif ( jQuery.isArray(value) && /radio|checkbox/.test( this.type ) )\n
\t\t\t\tthis.checked = (jQuery.inArray(this.value, value) >= 0 ||\n
\t\t\t\t\tjQuery.inArray(this.name, value) >= 0);\n
\n
\t\t\telse if ( jQuery.nodeName( this, "select" ) ) {\n
\t\t\t\tvar values = jQuery.makeArray(value);\n
\n
\t\t\t\tjQuery( "option", this ).each(function(){\n
\t\t\t\t\tthis.selected = (jQuery.inArray( this.value, values ) >= 0 ||\n
\t\t\t\t\t\tjQuery.inArray( this.text, values ) >= 0);\n
\t\t\t\t});\n
\n
\t\t\t\tif ( !values.length )\n
\t\t\t\t\tthis.selectedIndex = -1;\n
\n
\t\t\t} else\n
\t\t\t\tthis.value = value;\n
\t\t});\n
\t},\n
\n
\thtml: function( value ) {\n
\t\treturn value === undefined ?\n
\t\t\t(this[0] ?\n
\t\t\t\tthis[0].innerHTML.replace(/ jQuery\\d+="(?:\\d+|null)"/g, "") :\n
\t\t\t\tnull) :\n
\t\t\tthis.empty().append( value );\n
\t},\n
\n
\treplaceWith: function( value ) {\n
\t\treturn this.after( value ).remove();\n
\t},\n
\n
\teq: function( i ) {\n
\t\treturn this.slice( i, +i + 1 );\n
\t},\n
\n
\tslice: function() {\n
\t\treturn this.pushStack( Array.prototype.slice.apply( this, arguments ),\n
\t\t\t"slice", Array.prototype.slice.call(arguments).join(",") );\n
\t},\n
\n
\tmap: function( callback ) {\n
\t\treturn this.pushStack( jQuery.map(this, function(elem, i){\n
\t\t\treturn callback.call( elem, i, elem );\n
\t\t}));\n
\t},\n
\n
\tandSelf: function() {\n
\t\treturn this.add( this.prevObject );\n
\t},\n
\n
\tdomManip: function( args, table, callback ) {\n
\t\tif ( this[0] ) {\n
\t\t\tvar fragment = (this[0].ownerDocument || this[0]).createDocumentFragment(),\n
\t\t\t\tscripts = jQuery.clean( args, (this[0].ownerDocument || this[0]), fragment ),\n
\t\t\t\tfirst = fragment.firstChild;\n
\n
\t\t\tif ( first )\n
\t\t\t\tfor ( var i = 0, l = this.length; i < l; i++ )\n
\t\t\t\t\tcallback.call( root(this[i], first), this.length > 1 || i > 0 ?\n
\t\t\t\t\t\t\tfragment.cloneNode(true) : fragment );\n
\t\t\n
\t\t\tif ( scripts )\n
\t\t\t\tjQuery.each( scripts, evalScript );\n
\t\t}\n
\n
\t\treturn this;\n
\t\t\n
\t\tfunction root( elem, cur ) {\n
\t\t\treturn table && jQuery.nodeName(elem, "table") && jQuery.nodeName(cur, "tr") ?\n
\t\t\t\t(elem.getElementsByTagName("tbody")[0] ||\n
\t\t\t\telem.appendChild(elem.ownerDocument.createElement("tbody"))) :\n
\t\t\t\telem;\n
\t\t}\n
\t}\n
};\n
\n
// Give the init function the jQuery prototype for later instantiation\n
jQuery.fn.init.prototype = jQuery.fn;\n
\n
function evalScript( i, elem ) {\n
\tif ( elem.src )\n
\t\tjQuery.ajax({\n
\t\t\turl: elem.src,\n
\t\t\tasync: false,\n
\t\t\tdataType: "script"\n
\t\t});\n
\n
\telse\n
\t\tjQuery.globalEval( elem.text || elem.textContent || elem.innerHTML || "" );\n
\n
\tif ( elem.parentNode )\n
\t\telem.parentNode.removeChild( elem );\n
}\n
\n
function now(){\n
\treturn +new Date;\n
}\n
\n
jQuery.extend = jQuery.fn.extend = function() {\n
\t// copy reference to target object\n
\tvar target = arguments[0] || {}, i = 1, length = arguments.length, deep = false, options;\n
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
\tif ( typeof target !== "object" && !jQuery.isFunction(target) )\n
\t\ttarget = {};\n
\n
\t// extend jQuery itself if only one argument is passed\n
\tif ( length == i ) {\n
\t\ttarget = this;\n
\t\t--i;\n
\t}\n
\n
\tfor ( ; i < length; i++ )\n
\t\t// Only deal with non-null/undefined values\n
\t\tif ( (options = arguments[ i ]) != null )\n
\t\t\t// Extend the base object\n
\t\t\tfor ( var name in options ) {\n
\t\t\t\tvar src = target[ name ], copy = options[ name ];\n
\n
\t\t\t\t// Prevent never-ending loop\n
\t\t\t\tif ( target === copy )\n
\t\t\t\t\tcontinue;\n
\n
\t\t\t\t// Recurse if we\'re merging object values\n
\t\t\t\tif ( deep && copy && typeof copy === "object" && !copy.nodeType )\n
\t\t\t\t\ttarget[ name ] = jQuery.extend( deep, \n
\t\t\t\t\t\t// Never move original objects, clone them\n
\t\t\t\t\t\tsrc || ( copy.length != null ? [ ] : { } )\n
\t\t\t\t\t, copy );\n
\n
\t\t\t\t// Don\'t bring in undefined values\n
\t\t\t\telse if ( copy !== undefined )\n
\t\t\t\t\ttarget[ name ] = copy;\n
\n
\t\t\t}\n
\n
\t// Return the modified object\n
\treturn target;\n
};\n
\n
// exclude the following css properties to add px\n
var\texclude = /z-?index|font-?weight|opacity|zoom|line-?height/i,\n
\t// cache defaultView\n
\tdefaultView = document.defaultView || {},\n
\ttoString = Object.prototype.toString;\n
\n
jQuery.extend({\n
\tnoConflict: function( deep ) {\n
\t\twindow.$ = _$;\n
\n
\t\tif ( deep )\n
\t\t\twindow.jQuery = _jQuery;\n
\n
\t\treturn jQuery;\n
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
\t// check if an element is in a (or is an) XML document\n
\tisXMLDoc: function( elem ) {\n
\t\treturn elem.nodeType === 9 && elem.documentElement.nodeName !== "HTML" ||\n
\t\t\t!!elem.ownerDocument && jQuery.isXMLDoc( elem.ownerDocument );\n
\t},\n
\n
\t// Evalulates a script in a global context\n
\tglobalEval: function( data ) {\n
\t\tif ( data && /\\S/.test(data) ) {\n
\t\t\t// Inspired by code by Andrea Giammarchi\n
\t\t\t// http://webreflection.blogspot.com/2007/08/global-scope-evaluation-and-dom.html\n
\t\t\tvar head = document.getElementsByTagName("head")[0] || document.documentElement,\n
\t\t\t\tscript = document.createElement("script");\n
\n
\t\t\tscript.type = "text/javascript";\n
\t\t\tif ( jQuery.support.scriptEval )\n
\t\t\t\tscript.appendChild( document.createTextNode( data ) );\n
\t\t\telse\n
\t\t\t\tscript.text = data;\n
\n
\t\t\t// Use insertBefore instead of appendChild  to circumvent an IE6 bug.\n
\t\t\t// This arises when a base node is used (#2709).\n
\t\t\thead.insertBefore( script, head.firstChild );\n
\t\t\thead.removeChild( script );\n
\t\t}\n
\t},\n
\n
\tnodeName: function( elem, name ) {\n
\t\treturn elem.nodeName && elem.nodeName.toUpperCase() == name.toUpperCase();\n
\t},\n
\n
\t// args is for internal usage only\n
\teach: function( object, callback, args ) {\n
\t\tvar name, i = 0, length = object.length;\n
\n
\t\tif ( args ) {\n
\t\t\tif ( length === undefined ) {\n
\t\t\t\tfor ( name in object )\n
\t\t\t\t\tif ( callback.apply( object[ name ], args ) === false )\n
\t\t\t\t\t\tbreak;\n
\t\t\t} else\n
\t\t\t\tfor ( ; i < length; )\n
\t\t\t\t\tif ( callback.apply( object[ i++ ], args ) === false )\n
\t\t\t\t\t\tbreak;\n
\n
\t\t// A special, fast, case for the most common use of each\n
\t\t} else {\n
\t\t\tif ( length === undefined ) {\n
\t\t\t\tfor ( name in object )\n
\t\t\t\t\tif ( callback.call( object[ name ], name, object[ name ] ) === false )\n
\t\t\t\t\t\tbreak;\n
\t\t\t} else\n
\t\t\t\tfor ( var value = object[0];\n
\t\t\t\t\ti < length && callback.call( value, i, value ) !== false; value = object[++i] ){}\n
\t\t}\n
\n
\t\treturn object;\n
\t},\n
\n
\tprop: function( elem, value, type, i, name ) {\n
\t\t// Handle executable functions\n
\t\tif ( jQuery.isFunction( value ) )\n
\t\t\tvalue = value.call( elem, i );\n
\n
\t\t// Handle passing in a number to a CSS property\n
\t\treturn typeof value === "number" && type == "curCSS" && !exclude.test( name ) ?\n
\t\t\tvalue + "px" :\n
\t\t\tvalue;\n
\t},\n
\n
\tclassName: {\n
\t\t// internal only, use addClass("class")\n
\t\tadd: function( elem, classNames ) {\n
\t\t\tjQuery.each((classNames || "").split(/\\s+/), function(i, className){\n
\t\t\t\tif ( elem.nodeType == 1 && !jQuery.className.has( elem.className, className ) )\n
\t\t\t\t\telem.className += (elem.className ? " " : "") + className;\n
\t\t\t});\n
\t\t},\n
\n
\t\t// internal only, use removeClass("class")\n
\t\tremove: function( elem, classNames ) {\n
\t\t\tif (elem.nodeType == 1)\n
\t\t\t\telem.className = classNames !== undefined ?\n
\t\t\t\t\tjQuery.grep(elem.className.split(/\\s+/), function(className){\n
\t\t\t\t\t\treturn !jQuery.className.has( classNames, className );\n
\t\t\t\t\t}).join(" ") :\n
\t\t\t\t\t"";\n
\t\t},\n
\n
\t\t// internal only, use hasClass("class")\n
\t\thas: function( elem, className ) {\n
\t\t\treturn elem && jQuery.inArray( className, (elem.className || elem).toString().split(/\\s+/) ) > -1;\n
\t\t}\n
\t},\n
\n
\t// A method for quickly swapping in/out CSS properties to get correct calculations\n
\tswap: function( elem, options, callback ) {\n
\t\tvar old = {};\n
\t\t// Remember the old values, and insert the new ones\n
\t\tfor ( var name in options ) {\n
\t\t\told[ name ] = elem.style[ name ];\n
\t\t\telem.style[ name ] = options[ name ];\n
\t\t}\n
\n
\t\tcallback.call( elem );\n
\n
\t\t// Revert the old values\n
\t\tfor ( var name in options )\n
\t\t\telem.style[ name ] = old[ name ];\n
\t},\n
\n
\tcss: function( elem, name, force, extra ) {\n
\t\tif ( name == "width" || name == "height" ) {\n
\t\t\tvar val, props = { position: "absolute", visibility: "hidden", display:"block" }, which = name == "width" ? [ "Left", "Right" ] : [ "Top", "Bottom" ];\n
\n
\t\t\tfunction getWH() {\n
\t\t\t\tval = name == "width" ? elem.offsetWidth : elem.offsetHeight;\n
\n
\t\t\t\tif ( extra === "border" )\n
\t\t\t\t\treturn;\n
\n
\t\t\t\tjQuery.each( which, function() {\n
\t\t\t\t\tif ( !extra )\n
\t\t\t\t\t\tval -= parseFloat(jQuery.curCSS( elem, "padding" + this, true)) || 0;\n
\t\t\t\t\tif ( extra === "margin" )\n
\t\t\t\t\t\tval += parseFloat(jQuery.curCSS( elem, "margin" + this, true)) || 0;\n
\t\t\t\t\telse\n
\t\t\t\t\t\tval -= parseFloat(jQuery.curCSS( elem, "border" + this + "Width", true)) || 0;\n
\t\t\t\t});\n
\t\t\t}\n
\n
\t\t\tif ( elem.offsetWidth !== 0 )\n
\t\t\t\tgetWH();\n
\t\t\telse\n
\t\t\t\tjQuery.swap( elem, props, getWH );\n
\n
\t\t\treturn Math.max(0, Math.round(val));\n
\t\t}\n
\n
\t\treturn jQuery.curCSS( elem, name, force );\n
\t},\n
\n
\tcurCSS: function( elem, name, force ) {\n
\t\tvar ret, style = elem.style;\n
\n
\t\t// We need to handle opacity special in IE\n
\t\tif ( name == "opacity" && !jQuery.support.opacity ) {\n
\t\t\tret = jQuery.attr( style, "opacity" );\n
\n
\t\t\treturn ret == "" ?\n
\t\t\t\t"1" :\n
\t\t\t\tret;\n
\t\t}\n
\n
\t\t// Make sure we\'re using the right name for getting the float value\n
\t\tif ( name.match( /float/i ) )\n
\t\t\tname = styleFloat;\n
\n
\t\tif ( !force && style && style[ name ] )\n
\t\t\tret = style[ name ];\n
\n
\t\telse if ( defaultView.getComputedStyle ) {\n
\n
\t\t\t// Only "float" is needed here\n
\t\t\tif ( name.match( /float/i ) )\n
\t\t\t\tname = "float";\n
\n
\t\t\tname = name.replace( /([A-Z])/g, "-$1" ).toLowerCase();\n
\n
\t\t\tvar computedStyle = defaultView.getComputedStyle( elem, null );\n
\n
\t\t\tif ( computedStyle )\n
\t\t\t\tret = computedStyle.getPropertyValue( name );\n
\n
\t\t\t// We should always get a number back from opacity\n
\t\t\tif ( name == "opacity" && ret == "" )\n
\t\t\t\tret = "1";\n
\n
\t\t} else if ( elem.currentStyle ) {\n
\t\t\tvar camelCase = name.replace(/\\-(\\w)/g, function(all, letter){\n
\t\t\t\treturn letter.toUpperCase();\n
\t\t\t});\n
\n
\t\t\tret = elem.currentStyle[ name ] || elem.currentStyle[ camelCase ];\n
\n
\t\t\t// From the awesome hack by Dean Edwards\n
\t\t\t// http://erik.eae.net/archives/2007/07/27/18.54.15/#comment-102291\n
\n
\t\t\t// If we\'re not dealing with a regular pixel number\n
\t\t\t// but a number that has a weird ending, we need to convert it to pixels\n
\t\t\tif ( !/^\\d+(px)?$/i.test( ret ) && /^\\d/.test( ret ) ) {\n
\t\t\t\t// Remember the original values\n
\t\t\t\tvar left = style.left, rsLeft = elem.runtimeStyle.left;\n
\n
\t\t\t\t// Put in the new values to get a computed value out\n
\t\t\t\telem.runtimeStyle.left = elem.currentStyle.left;\n
\t\t\t\tstyle.left = ret || 0;\n
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
\tclean: function( elems, context, fragment ) {\n
\t\tcontext = context || document;\n
\n
\t\t// !context.createElement fails in IE with an error but returns typeof \'object\'\n
\t\tif ( typeof context.createElement === "undefined" )\n
\t\t\tcontext = context.ownerDocument || context[0] && context[0].ownerDocument || document;\n
\n
\t\t// If a single string is passed in and it\'s a single tag\n
\t\t// just do a createElement and skip the rest\n
\t\tif ( !fragment && elems.length === 1 && typeof elems[0] === "string" ) {\n
\t\t\tvar match = /^<(\\w+)\\s*\\/?>$/.exec(elems[0]);\n
\t\t\tif ( match )\n
\t\t\t\treturn [ context.createElement( match[1] ) ];\n
\t\t}\n
\n
\t\tvar ret = [], scripts = [], div = context.createElement("div");\n
\n
\t\tjQuery.each(elems, function(i, elem){\n
\t\t\tif ( typeof elem === "number" )\n
\t\t\t\telem += \'\';\n
\n
\t\t\tif ( !elem )\n
\t\t\t\treturn;\n
\n
\t\t\t// Convert html string into DOM nodes\n
\t\t\tif ( typeof elem === "string" ) {\n
\t\t\t\t// Fix "XHTML"-style tags in all browsers\n
\t\t\t\telem = elem.replace(/(<(\\w+)[^>]*?)\\/>/g, function(all, front, tag){\n
\t\t\t\t\treturn tag.match(/^(abbr|br|col|img|input|link|meta|param|hr|area|embed)$/i) ?\n
\t\t\t\t\t\tall :\n
\t\t\t\t\t\tfront + "></" + tag + ">";\n
\t\t\t\t});\n
\n
\t\t\t\t// Trim whitespace, otherwise indexOf won\'t work as expected\n
\t\t\t\tvar tags = elem.replace(/^\\s+/, "").substring(0, 10).toLowerCase();\n
\n
\t\t\t\tvar wrap =\n
\t\t\t\t\t// option or optgroup\n
\t\t\t\t\t!tags.indexOf("<opt") &&\n
\t\t\t\t\t[ 1, "<select multiple=\'multiple\'>", "</select>" ] ||\n
\n
\t\t\t\t\t!tags.indexOf("<leg") &&\n
\t\t\t\t\t[ 1, "<fieldset>", "</fieldset>" ] ||\n
\n
\t\t\t\t\ttags.match(/^<(thead|tbody|tfoot|colg|cap)/) &&\n
\t\t\t\t\t[ 1, "<table>", "</table>" ] ||\n
\n
\t\t\t\t\t!tags.indexOf("<tr") &&\n
\t\t\t\t\t[ 2, "<table><tbody>", "</tbody></table>" ] ||\n
\n
\t\t\t\t \t// <thead> matched above\n
\t\t\t\t\t(!tags.indexOf("<td") || !tags.indexOf("<th")) &&\n
\t\t\t\t\t[ 3, "<table><tbody><tr>", "</tr></tbody></table>" ] ||\n
\n
\t\t\t\t\t!tags.indexOf("<col") &&\n
\t\t\t\t\t[ 2, "<table><tbody></tbody><colgroup>", "</colgroup></table>" ] ||\n
\n
\t\t\t\t\t// IE can\'t serialize <link> and <script> tags normally\n
\t\t\t\t\t!jQuery.support.htmlSerialize &&\n
\t\t\t\t\t[ 1, "div<div>", "</div>" ] ||\n
\n
\t\t\t\t\t[ 0, "", "" ];\n
\n
\t\t\t\t// Go to html and back, then peel off extra wrappers\n
\t\t\t\tdiv.innerHTML = wrap[1] + elem + wrap[2];\n
\n
\t\t\t\t// Move to the right depth\n
\t\t\t\twhile ( wrap[0]-- )\n
\t\t\t\t\tdiv = div.lastChild;\n
\n
\t\t\t\t// Remove IE\'s autoinserted <tbody> from table fragments\n
\t\t\t\tif ( !jQuery.support.tbody ) {\n
\n
\t\t\t\t\t// String was a <table>, *may* have spurious <tbody>\n
\t\t\t\t\tvar hasBody = /<tbody/i.test(elem),\n
\t\t\t\t\t\ttbody = !tags.indexOf("<table") && !hasBody ?\n
\t\t\t\t\t\t\tdiv.firstChild && div.firstChild.childNodes :\n
\n
\t\t\t\t\t\t// String was a bare <thead> or <tfoot>\n
\t\t\t\t\t\twrap[1] == "<table>" && !hasBody ?\n
\t\t\t\t\t\t\tdiv.childNodes :\n
\t\t\t\t\t\t\t[];\n
\n
\t\t\t\t\tfor ( var j = tbody.length - 1; j >= 0 ; --j )\n
\t\t\t\t\t\tif ( jQuery.nodeName( tbody[ j ], "tbody" ) && !tbody[ j ].childNodes.length )\n
\t\t\t\t\t\t\ttbody[ j ].parentNode.removeChild( tbody[ j ] );\n
\n
\t\t\t\t\t}\n
\n
\t\t\t\t// IE completely kills leading whitespace when innerHTML is used\n
\t\t\t\tif ( !jQuery.support.leadingWhitespace && /^\\s/.test( elem ) )\n
\t\t\t\t\tdiv.insertBefore( context.createTextNode( elem.match(/^\\s*/)[0] ), div.firstChild );\n
\t\t\t\t\n
\t\t\t\telem = jQuery.makeArray( div.childNodes );\n
\t\t\t}\n
\n
\t\t\tif ( elem.nodeType )\n
\t\t\t\tret.push( elem );\n
\t\t\telse\n
\t\t\t\tret = jQuery.merge( ret, elem );\n
\n
\t\t});\n
\n
\t\tif ( fragment ) {\n
\t\t\tfor ( var i = 0; ret[i]; i++ ) {\n
\t\t\t\tif ( jQuery.nodeName( ret[i], "script" ) && (!ret[i].type || ret[i].type.toLowerCase() === "text/javascript") ) {\n
\t\t\t\t\tscripts.push( ret[i].parentNode ? ret[i].parentNode.removeChild( ret[i] ) : ret[i] );\n
\t\t\t\t} else {\n
\t\t\t\t\tif ( ret[i].nodeType === 1 )\n
\t\t\t\t\t\tret.splice.apply( ret, [i + 1, 0].concat(jQuery.makeArray(ret[i].getElementsByTagName("script"))) );\n
\t\t\t\t\tfragment.appendChild( ret[i] );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t\t\n
\t\t\treturn scripts;\n
\t\t}\n
\n
\t\treturn ret;\n
\t},\n
\n
\tattr: function( elem, name, value ) {\n
\t\t// don\'t set attributes on text and comment nodes\n
\t\tif (!elem || elem.nodeType == 3 || elem.nodeType == 8)\n
\t\t\treturn undefined;\n
\n
\t\tvar notxml = !jQuery.isXMLDoc( elem ),\n
\t\t\t// Whether we are setting (or getting)\n
\t\t\tset = value !== undefined;\n
\n
\t\t// Try to normalize/fix the name\n
\t\tname = notxml && jQuery.props[ name ] || name;\n
\n
\t\t// Only do all the following if this is a node (faster for style)\n
\t\t// IE elem.getAttribute passes even for style\n
\t\tif ( elem.tagName ) {\n
\n
\t\t\t// These attributes require special treatment\n
\t\t\tvar special = /href|src|style/.test( name );\n
\n
\t\t\t// Safari mis-reports the default selected property of a hidden option\n
\t\t\t// Accessing the parent\'s selectedIndex property fixes it\n
\t\t\tif ( name == "selected" && elem.parentNode )\n
\t\t\t\telem.parentNode.selectedIndex;\n
\n
\t\t\t// If applicable, access the attribute via the DOM 0 way\n
\t\t\tif ( name in elem && notxml && !special ) {\n
\t\t\t\tif ( set ){\n
\t\t\t\t\t// We can\'t allow the type property to be changed (since it causes problems in IE)\n
\t\t\t\t\tif ( name == "type" && jQuery.nodeName( elem, "input" ) && elem.parentNode )\n
\t\t\t\t\t\tthrow "type property can\'t be changed";\n
\n
\t\t\t\t\telem[ name ] = value;\n
\t\t\t\t}\n
\n
\t\t\t\t// browsers index elements by id/name on forms, give priority to attributes.\n
\t\t\t\tif( jQuery.nodeName( elem, "form" ) && elem.getAttributeNode(name) )\n
\t\t\t\t\treturn elem.getAttributeNode( name ).nodeValue;\n
\n
\t\t\t\t// elem.tabIndex doesn\'t always return the correct value when it hasn\'t been explicitly set\n
\t\t\t\t// http://fluidproject.org/blog/2008/01/09/getting-setting-and-removing-tabindex-values-with-javascript/\n
\t\t\t\tif ( name == "tabIndex" ) {\n
\t\t\t\t\tvar attributeNode = elem.getAttributeNode( "tabIndex" );\n
\t\t\t\t\treturn attributeNode && attributeNode.specified\n
\t\t\t\t\t\t? attributeNode.value\n
\t\t\t\t\t\t: elem.nodeName.match(/(button|input|object|select|textarea)/i)\n
\t\t\t\t\t\t\t? 0\n
\t\t\t\t\t\t\t: elem.nodeName.match(/^(a|area)$/i) && elem.href\n
\t\t\t\t\t\t\t\t? 0\n
\t\t\t\t\t\t\t\t: undefined;\n
\t\t\t\t}\n
\n
\t\t\t\treturn elem[ name ];\n
\t\t\t}\n
\n
\t\t\tif ( !jQuery.support.style && notxml &&  name == "style" )\n
\t\t\t\treturn jQuery.attr( elem.style, "cssText", value );\n
\n
\t\t\tif ( set )\n
\t\t\t\t// convert the value to a string (all browsers do this but IE) see #1070\n
\t\t\t\telem.setAttribute( name, "" + value );\n
\n
\t\t\tvar attr = !jQuery.support.hrefNormalized && notxml && special\n
\t\t\t\t\t// Some attributes require a special call on IE\n
\t\t\t\t\t? elem.getAttribute( name, 2 )\n
\t\t\t\t\t: elem.getAttribute( name );\n
\n
\t\t\t// Non-existent attributes return null, we normalize to undefined\n
\t\t\treturn attr === null ? undefined : attr;\n
\t\t}\n
\n
\t\t// elem is actually elem.style ... set the style\n
\n
\t\t// IE uses filters for opacity\n
\t\tif ( !jQuery.support.opacity && name == "opacity" ) {\n
\t\t\tif ( set ) {\n
\t\t\t\t// IE has trouble with opacity if it does not have layout\n
\t\t\t\t// Force it by setting the zoom level\n
\t\t\t\telem.zoom = 1;\n
\n
\t\t\t\t// Set the alpha filter to set the opacity\n
\t\t\t\telem.filter = (elem.filter || "").replace( /alpha\\([^)]*\\)/, "" ) +\n
\t\t\t\t\t(parseInt( value ) + \'\' == "NaN" ? "" : "alpha(opacity=" + value * 100 + ")");\n
\t\t\t}\n
\n
\t\t\treturn elem.filter && elem.filter.indexOf("opacity=") >= 0 ?\n
\t\t\t\t(parseFloat( elem.filter.match(/opacity=([^)]*)/)[1] ) / 100) + \'\':\n
\t\t\t\t"";\n
\t\t}\n
\n
\t\tname = name.replace(/-([a-z])/ig, function(all, letter){\n
\t\t\treturn letter.toUpperCase();\n
\t\t});\n
\n
\t\tif ( set )\n
\t\t\telem[ name ] = value;\n
\n
\t\treturn elem[ name ];\n
\t},\n
\n
\ttrim: function( text ) {\n
\t\treturn (text || "").replace( /^\\s+|\\s+$/g, "" );\n
\t},\n
\n
\tmakeArray: function( array ) {\n
\t\tvar ret = [];\n
\n
\t\tif( array != null ){\n
\t\t\tvar i = array.length;\n
\t\t\t// The window, strings (and functions) also have \'length\'\n
\t\t\tif( i == null || typeof array === "string" || jQuery.isFunction(array) || array.setInterval )\n
\t\t\t\tret[0] = array;\n
\t\t\telse\n
\t\t\t\twhile( i )\n
\t\t\t\t\tret[--i] = array[i];\n
\t\t}\n
\n
\t\treturn ret;\n
\t},\n
\n
\tinArray: function( elem, array ) {\n
\t\tfor ( var i = 0, length = array.length; i < length; i++ )\n
\t\t// Use === because on IE, window == document\n
\t\t\tif ( array[ i ] === elem )\n
\t\t\t\treturn i;\n
\n
\t\treturn -1;\n
\t},\n
\n
\tmerge: function( first, second ) {\n
\t\t// We have to loop this way because IE & Opera overwrite the length\n
\t\t// expando of getElementsByTagName\n
\t\tvar i = 0, elem, pos = first.length;\n
\t\t// Also, we need to make sure that the correct elements are being returned\n
\t\t// (IE returns comment nodes in a \'*\' query)\n
\t\tif ( !jQuery.support.getAll ) {\n
\t\t\twhile ( (elem = second[ i++ ]) != null )\n
\t\t\t\tif ( elem.nodeType != 8 )\n
\t\t\t\t\tfirst[ pos++ ] = elem;\n
\n
\t\t} else\n
\t\t\twhile ( (elem = second[ i++ ]) != null )\n
\t\t\t\tfirst[ pos++ ] = elem;\n
\n
\t\treturn first;\n
\t},\n
\n
\tunique: function( array ) {\n
\t\tvar ret = [], done = {};\n
\n
\t\ttry {\n
\n
\t\t\tfor ( var i = 0, length = array.length; i < length; i++ ) {\n
\t\t\t\tvar id = jQuery.data( array[ i ] );\n
\n
\t\t\t\tif ( !done[ id ] ) {\n
\t\t\t\t\tdone[ id ] = true;\n
\t\t\t\t\tret.push( array[ i ] );\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t} catch( e ) {\n
\t\t\tret = array;\n
\t\t}\n
\n
\t\treturn ret;\n
\t},\n
\n
\tgrep: function( elems, callback, inv ) {\n
\t\tvar ret = [];\n
\n
\t\t// Go through the array, only saving the items\n
\t\t// that pass the validator function\n
\t\tfor ( var i = 0, length = elems.length; i < length; i++ )\n
\t\t\tif ( !inv != !callback( elems[ i ], i ) )\n
\t\t\t\tret.push( elems[ i ] );\n
\n
\t\treturn ret;\n
\t},\n
\n
\tmap: function( elems, callback ) {\n
\t\tvar ret = [];\n
\n
\t\t// Go through the array, translating each of the items to their\n
\t\t// new value (or values).\n
\t\tfor ( var i = 0, length = elems.length; i < length; i++ ) {\n
\t\t\tvar value = callback( elems[ i ], i );\n
\n
\t\t\tif ( value != null )\n
\t\t\t\tret[ ret.length ] = value;\n
\t\t}\n
\n
\t\treturn ret.concat.apply( [], ret );\n
\t}\n
});\n
\n
// Use of jQuery.browser is deprecated.\n
// It\'s included for backwards compatibility and plugins,\n
// although they should work to migrate away.\n
\n
var userAgent = navigator.userAgent.toLowerCase();\n
\n
// Figure out what browser is being used\n
jQuery.browser = {\n
\tversion: (userAgent.match( /.+(?:rv|it|ra|ie)[\\/: ]([\\d.]+)/ ) || [0,\'0\'])[1],\n
\tsafari: /webkit/.test( userAgent ),\n
\topera: /opera/.test( userAgent ),\n
\tmsie: /msie/.test( userAgent ) && !/opera/.test( userAgent ),\n
\tmozilla: /mozilla/.test( userAgent ) && !/(compatible|webkit)/.test( userAgent )\n
};\n
\n
jQuery.each({\n
\tparent: function(elem){return elem.parentNode;},\n
\tparents: function(elem){return jQuery.dir(elem,"parentNode");},\n
\tnext: function(elem){return jQuery.nth(elem,2,"nextSibling");},\n
\tprev: function(elem){return jQuery.nth(elem,2,"previousSibling");},\n
\tnextAll: function(elem){return jQuery.dir(elem,"nextSibling");},\n
\tprevAll: function(elem){return jQuery.dir(elem,"previousSibling");},\n
\tsiblings: function(elem){return jQuery.sibling(elem.parentNode.firstChild,elem);},\n
\tchildren: function(elem){return jQuery.sibling(elem.firstChild);},\n
\tcontents: function(elem){return jQuery.nodeName(elem,"iframe")?elem.contentDocument||elem.contentWindow.document:jQuery.makeArray(elem.childNodes);}\n
}, function(name, fn){\n
\tjQuery.fn[ name ] = function( selector ) {\n
\t\tvar ret = jQuery.map( this, fn );\n
\n
\t\tif ( selector && typeof selector == "string" )\n
\t\t\tret = jQuery.multiFilter( selector, ret );\n
\n
\t\treturn this.pushStack( jQuery.unique( ret ), name, selector );\n
\t};\n
});\n
\n
jQuery.each({\n
\tappendTo: "append",\n
\tprependTo: "prepend",\n
\tinsertBefore: "before",\n
\tinsertAfter: "after",\n
\treplaceAll: "replaceWith"\n
}, function(name, original){\n
\tjQuery.fn[ name ] = function( selector ) {\n
\t\tvar ret = [], insert = jQuery( selector );\n
\n
\t\tfor ( var i = 0, l = insert.length; i < l; i++ ) {\n
\t\t\tvar elems = (i > 0 ? this.clone(true) : this).get();\n
\t\t\tjQuery.fn[ original ].apply( jQuery(insert[i]), elems );\n
\t\t\tret = ret.concat( elems );\n
\t\t}\n
\n
\t\treturn this.pushStack( ret, name, selector );\n
\t};\n
});\n
\n
jQuery.each({\n
\tremoveAttr: function( name ) {\n
\t\tjQuery.attr( this, name, "" );\n
\t\tif (this.nodeType == 1)\n
\t\t\tthis.removeAttribute( name );\n
\t},\n
\n
\taddClass: function( classNames ) {\n
\t\tjQuery.className.add( this, classNames );\n
\t},\n
\n
\tremoveClass: function( classNames ) {\n
\t\tjQuery.className.remove( this, classNames );\n
\t},\n
\n
\ttoggleClass: function( classNames, state ) {\n
\t\tif( typeof state !== "boolean" )\n
\t\t\tstate = !jQuery.className.has( this, classNames );\n
\t\tjQuery.className[ state ? "add" : "remove" ]( this, classNames );\n
\t},\n
\n
\tremove: function( selector ) {\n
\t\tif ( !selector || jQuery.filter( selector, [ this ] ).length ) {\n
\t\t\t// Prevent memory leaks\n
\t\t\tjQuery( "*", this ).add([this]).each(function(){\n
\t\t\t\tjQuery.event.remove(this);\n
\t\t\t\tjQuery.removeData(this);\n
\t\t\t});\n
\t\t\tif (this.parentNode)\n
\t\t\t\tthis.parentNode.removeChild( this );\n
\t\t}\n
\t},\n
\n
\tempty: function() {\n
\t\t// Remove element nodes and prevent memory leaks\n
\t\tjQuery(this).children().remove();\n
\n
\t\t// Remove any remaining nodes\n
\t\twhile ( this.firstChild )\n
\t\t\tthis.removeChild( this.firstChild );\n
\t}\n
}, function(name, fn){\n
\tjQuery.fn[ name ] = function(){\n
\t\treturn this.each( fn, arguments );\n
\t};\n
});\n
\n
// Helper function used by the dimensions and offset modules\n
function num(elem, prop) {\n
\treturn elem[0] && parseInt( jQuery.curCSS(elem[0], prop, true), 10 ) || 0;\n
}\n
var expando = "jQuery" + now(), uuid = 0, windowData = {};\n
\n
jQuery.extend({\n
\tcache: {},\n
\n
\tdata: function( elem, name, data ) {\n
\t\telem = elem == window ?\n
\t\t\twindowData :\n
\t\t\telem;\n
\n
\t\tvar id = elem[ expando ];\n
\n
\t\t// Compute a unique ID for the element\n
\t\tif ( !id )\n
\t\t\tid = elem[ expando ] = ++uuid;\n
\n
\t\t// Only generate the data cache if we\'re\n
\t\t// trying to access or manipulate it\n
\t\tif ( name && !jQuery.cache[ id ] )\n
\t\t\tjQuery.cache[ id ] = {};\n
\n
\t\t// Prevent overriding the named cache with undefined values\n
\t\tif ( data !== undefined )\n
\t\t\tjQuery.cache[ id ][ name ] = data;\n
\n
\t\t// Return the named cache data, or the ID for the element\n
\t\treturn name ?\n
\t\t\tjQuery.cache[ id ][ name ] :\n
\t\t\tid;\n
\t},\n
\n
\tremoveData: function( elem, name ) {\n
\t\telem = elem == window ?\n
\t\t\twindowData :\n
\t\t\telem;\n
\n
\t\tvar id = elem[ expando ];\n
\n
\t\t// If we want to remove a specific section of the element\'s data\n
\t\tif ( name ) {\n
\t\t\tif ( jQuery.cache[ id ] ) {\n
\t\t\t\t// Remove the section of cache data\n
\t\t\t\tdelete jQuery.cache[ id ][ name ];\n
\n
\t\t\t\t// If we\'ve removed all the data, remove the element\'s cache\n
\t\t\t\tname = "";\n
\n
\t\t\t\tfor ( name in jQuery.cache[ id ] )\n
\t\t\t\t\tbreak;\n
\n
\t\t\t\tif ( !name )\n
\t\t\t\t\tjQuery.removeData( elem );\n
\t\t\t}\n
\n
\t\t// Otherwise, we want to remove all of the element\'s data\n
\t\t} else {\n
\t\t\t// Clean up the element expando\n
\t\t\ttry {\n
\t\t\t\tdelete elem[ expando ];\n
\t\t\t} catch(e){\n
\t\t\t\t// IE has trouble directly removing the expando\n
\t\t\t\t// but it\'s ok with using removeAttribute\n
\t\t\t\tif ( elem.removeAttribute )\n
\t\t\t\t\telem.removeAttribute( expando );\n
\t\t\t}\n
\n
\t\t\t// Completely remove the data cache\n
\t\t\tdelete jQuery.cache[ id ];\n
\t\t}\n
\t},\n
\tqueue: function( elem, type, data ) {\n
\t\tif ( elem ){\n
\t\n
\t\t\ttype = (type || "fx") + "queue";\n
\t\n
\t\t\tvar q = jQuery.data( elem, type );\n
\t\n
\t\t\tif ( !q || jQuery.isArray(data) )\n
\t\t\t\tq = jQuery.data( elem, type, jQuery.makeArray(data) );\n
\t\t\telse if( data )\n
\t\t\t\tq.push( data );\n
\t\n
\t\t}\n
\t\treturn q;\n
\t},\n
\n
\tdequeue: function( elem, type ){\n
\t\tvar queue = jQuery.queue( elem, type ),\n
\t\t\tfn = queue.shift();\n
\t\t\n
\t\tif( !type || type === "fx" )\n
\t\t\tfn = queue[0];\n
\t\t\t\n
\t\tif( fn !== undefined )\n
\t\t\tfn.call(elem);\n
\t}\n
});\n
\n
jQuery.fn.extend({\n
\tdata: function( key, value ){\n
\t\tvar parts = key.split(".");\n
\t\tparts[1] = parts[1] ? "." + parts[1] : "";\n
\n
\t\tif ( value === undefined ) {\n
\t\t\tvar data = this.triggerHandler("getData" + parts[1] + "!", [parts[0]]);\n
\n
\t\t\tif ( data === undefined && this.length )\n
\t\t\t\tdata = jQuery.data( this[0], key );\n
\n
\t\t\treturn data === undefined && parts[1] ?\n
\t\t\t\tthis.data( parts[0] ) :\n
\t\t\t\tdata;\n
\t\t} else\n
\t\t\treturn this.trigger("setData" + parts[1] + "!", [parts[0], value]).each(function(){\n
\t\t\t\tjQuery.data( this, key, value );\n
\t\t\t});\n
\t},\n
\n
\tremoveData: function( key ){\n
\t\treturn this.each(function(){\n
\t\t\tjQuery.removeData( this, key );\n
\t\t});\n
\t},\n
\tqueue: function(type, data){\n
\t\tif ( typeof type !== "string" ) {\n
\t\t\tdata = type;\n
\t\t\ttype = "fx";\n
\t\t}\n
\n
\t\tif ( data === undefined )\n
\t\t\treturn jQuery.queue( this[0], type );\n
\n
\t\treturn this.each(function(){\n
\t\t\tvar queue = jQuery.queue( this, type, data );\n
\t\t\t\n
\t\t\t if( type == "fx" && queue.length == 1 )\n
\t\t\t\tqueue[0].call(this);\n
\t\t});\n
\t},\n
\tdequeue: function(type){\n
\t\treturn this.each(function(){\n
\t\t\tjQuery.dequeue( this, type );\n
\t\t});\n
\t}\n
});/*!\n
 * Sizzle CSS Selector Engine - v0.9.3\n
 *  Copyright 2009, The Dojo Foundation\n
 *  Released under the MIT, BSD, and GPL Licenses.\n
 *  More information: http://sizzlejs.com/\n
 */\n
(function(){\n
\n
var chunker = /((?:\\((?:\\([^()]+\\)|[^()]+)+\\)|\\[(?:\\[[^[\\]]*\\]|[\'"][^\'"]*[\'"]|[^[\\]\'"]+)+\\]|\\\\.|[^ >+~,(\\[\\\\]+)+|[>+~])(\\s*,\\s*)?/g,\n
\tdone = 0,\n
\ttoString = Object.prototype.toString;\n
\n
var Sizzle = function(selector, context, results, seed) {\n
\tresults = results || [];\n
\tcontext = context || document;\n
\n
\tif ( context.nodeType !== 1 && context.nodeType !== 9 )\n
\t\treturn [];\n
\t\n
\tif ( !selector || typeof selector !== "string" ) {\n
\t\treturn results;\n
\t}\n
\n
\tvar parts = [], m, set, checkSet, check, mode, extra, prune = true;\n
\t\n
\t// Reset the position of the chunker regexp (start from head)\n
\tchunker.lastIndex = 0;\n
\t\n
\twhile ( (m = chunker.exec(selector)) !== null ) {\n
\t\tparts.push( m[1] );\n
\t\t\n
\t\tif ( m[2] ) {\n
\t\t\textra = RegExp.rightContext;\n
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
\t\t\t\tif ( Expr.relative[ selector ] )\n
\t\t\t\t\tselector += parts.shift();\n
\n
\t\t\t\tset = posProcess( selector, set );\n
\t\t\t}\n
\t\t}\n
\t} else {\n
\t\tvar ret = seed ?\n
\t\t\t{ expr: parts.pop(), set: makeArray(seed) } :\n
\t\t\tSizzle.find( parts.pop(), parts.length === 1 && context.parentNode ? context.parentNode : context, isXML(context) );\n
\t\tset = Sizzle.filter( ret.expr, ret.set );\n
\n
\t\tif ( parts.length > 0 ) {\n
\t\t\tcheckSet = makeArray(set);\n
\t\t} else {\n
\t\t\tprune = false;\n
\t\t}\n
\n
\t\twhile ( parts.length ) {\n
\t\t\tvar cur = parts.pop(), pop = cur;\n
\n
\t\t\tif ( !Expr.relative[ cur ] ) {\n
\t\t\t\tcur = "";\n
\t\t\t} else {\n
\t\t\t\tpop = parts.pop();\n
\t\t\t}\n
\n
\t\t\tif ( pop == null ) {\n
\t\t\t\tpop = context;\n
\t\t\t}\n
\n
\t\t\tExpr.relative[ cur ]( checkSet, pop, isXML(context) );\n
\t\t}\n
\t}\n
\n
\tif ( !checkSet ) {\n
\t\tcheckSet = set;\n
\t}\n
\n
\tif ( !checkSet ) {\n
\t\tthrow "Syntax error, unrecognized expression: " + (cur || selector);\n
\t}\n
\n
\tif ( toString.call(checkSet) === "[object Array]" ) {\n
\t\tif ( !prune ) {\n
\t\t\tresults.push.apply( results, checkSet );\n
\t\t} else if ( context.nodeType === 1 ) {\n
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
\t\tSizzle( extra, context, results, seed );\n
\n
\t\tif ( sortOrder ) {\n
\t\t\thasDuplicate = false;\n
\t\t\tresults.sort(sortOrder);\n
\n
\t\t\tif ( hasDuplicate ) {\n
\t\t\t\tfor ( var i = 1; i < results.length; i++ ) {\n
\t\t\t\t\tif ( results[i] === results[i-1] ) {\n
\t\t\t\t\t\tresults.splice(i--, 1);\n
\t\t\t\t\t}\n
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
\t\tif ( (match = Expr.match[ type ].exec( expr )) ) {\n
\t\t\tvar left = RegExp.leftContext;\n
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
\t\t\tif ( (match = Expr.match[ type ].exec( expr )) != null ) {\n
\t\t\t\tvar filter = Expr.filter[ type ], found, item;\n
\t\t\t\tanyFound = false;\n
\n
\t\t\t\tif ( curLoop == result ) {\n
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
\t\tif ( expr == old ) {\n
\t\t\tif ( anyFound == null ) {\n
\t\t\t\tthrow "Syntax error, unrecognized expression: " + expr;\n
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
var Expr = Sizzle.selectors = {\n
\torder: [ "ID", "NAME", "TAG" ],\n
\tmatch: {\n
\t\tID: /#((?:[\\w\\u00c0-\\uFFFF_-]|\\\\.)+)/,\n
\t\tCLASS: /\\.((?:[\\w\\u00c0-\\uFFFF_-]|\\\\.)+)/,\n
\t\tNAME: /\\[name=[\'"]*((?:[\\w\\u00c0-\\uFFFF_-]|\\\\.)+)[\'"]*\\]/,\n
\t\tATTR: /\\[\\s*((?:[\\w\\u00c0-\\uFFFF_-]|\\\\.)+)\\s*(?:(\\S?=)\\s*([\'"]*)(.*?)\\3|)\\s*\\]/,\n
\t\tTAG: /^((?:[\\w\\u00c0-\\uFFFF\\*_-]|\\\\.)+)/,\n
\t\tCHILD: /:(only|nth|last|first)-child(?:\\((even|odd|[\\dn+-]*)\\))?/,\n
\t\tPOS: /:(nth|eq|gt|lt|first|last|even|odd)(?:\\((\\d*)\\))?(?=[^-]|$)/,\n
\t\tPSEUDO: /:((?:[\\w\\u00c0-\\uFFFF_-]|\\\\.)+)(?:\\(([\'"]*)((?:\\([^\\)]+\\)|[^\\2\\(\\)]*)+)\\2\\))?/\n
\t},\n
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
\t\t"+": function(checkSet, part, isXML){\n
\t\t\tvar isPartStr = typeof part === "string",\n
\t\t\t\tisTag = isPartStr && !/\\W/.test(part),\n
\t\t\t\tisPartStrNotTag = isPartStr && !isTag;\n
\n
\t\t\tif ( isTag && !isXML ) {\n
\t\t\t\tpart = part.toUpperCase();\n
\t\t\t}\n
\n
\t\t\tfor ( var i = 0, l = checkSet.length, elem; i < l; i++ ) {\n
\t\t\t\tif ( (elem = checkSet[i]) ) {\n
\t\t\t\t\twhile ( (elem = elem.previousSibling) && elem.nodeType !== 1 ) {}\n
\n
\t\t\t\t\tcheckSet[i] = isPartStrNotTag || elem && elem.nodeName === part ?\n
\t\t\t\t\t\telem || false :\n
\t\t\t\t\t\telem === part;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tif ( isPartStrNotTag ) {\n
\t\t\t\tSizzle.filter( part, checkSet, true );\n
\t\t\t}\n
\t\t},\n
\t\t">": function(checkSet, part, isXML){\n
\t\t\tvar isPartStr = typeof part === "string";\n
\n
\t\t\tif ( isPartStr && !/\\W/.test(part) ) {\n
\t\t\t\tpart = isXML ? part : part.toUpperCase();\n
\n
\t\t\t\tfor ( var i = 0, l = checkSet.length; i < l; i++ ) {\n
\t\t\t\t\tvar elem = checkSet[i];\n
\t\t\t\t\tif ( elem ) {\n
\t\t\t\t\t\tvar parent = elem.parentNode;\n
\t\t\t\t\t\tcheckSet[i] = parent.nodeName === part ? parent : false;\n
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
\t\t\tif ( !part.match(/\\W/) ) {\n
\t\t\t\tvar nodeCheck = part = isXML ? part : part.toUpperCase();\n
\t\t\t\tcheckFn = dirNodeCheck;\n
\t\t\t}\n
\n
\t\t\tcheckFn("parentNode", part, doneName, checkSet, nodeCheck, isXML);\n
\t\t},\n
\t\t"~": function(checkSet, part, isXML){\n
\t\t\tvar doneName = done++, checkFn = dirCheck;\n
\n
\t\t\tif ( typeof part === "string" && !part.match(/\\W/) ) {\n
\t\t\t\tvar nodeCheck = part = isXML ? part : part.toUpperCase();\n
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
\t\tNAME: function(match, context, isXML){\n
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
\t\t\t\t\tif ( not ^ (elem.className && (" " + elem.className + " ").indexOf(match) >= 0) ) {\n
\t\t\t\t\t\tif ( !inplace )\n
\t\t\t\t\t\t\tresult.push( elem );\n
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
\t\t\tfor ( var i = 0; curLoop[i] === false; i++ ){}\n
\t\t\treturn curLoop[i] && isXML(curLoop[i]) ? match[1] : match[1].toUpperCase();\n
\t\t},\n
\t\tCHILD: function(match){\n
\t\t\tif ( match[1] == "nth" ) {\n
\t\t\t\t// parse equations like \'even\', \'odd\', \'5\', \'2n\', \'3n+2\', \'4n-1\', \'-n+6\'\n
\t\t\t\tvar test = /(-?)(\\d*)n((?:\\+|-)?\\d*)/.exec(\n
\t\t\t\t\tmatch[2] == "even" && "2n" || match[2] == "odd" && "2n+1" ||\n
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
\t\t\t\tif ( match[3].match(chunker).length > 1 || /^\\w/.test(match[3]) ) {\n
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
\t\t\treturn "button" === elem.type || elem.nodeName.toUpperCase() === "BUTTON";\n
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
\t\t\treturn match[3] - 0 == i;\n
\t\t},\n
\t\teq: function(elem, i, match){\n
\t\t\treturn match[3] - 0 == i;\n
\t\t}\n
\t},\n
\tfilter: {\n
\t\tPSEUDO: function(elem, match, i, array){\n
\t\t\tvar name = match[1], filter = Expr.filters[ name ];\n
\n
\t\t\tif ( filter ) {\n
\t\t\t\treturn filter( elem, i, match, array );\n
\t\t\t} else if ( name === "contains" ) {\n
\t\t\t\treturn (elem.textContent || elem.innerText || "").indexOf(match[3]) >= 0;\n
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
\t\t\t}\n
\t\t},\n
\t\tCHILD: function(elem, match){\n
\t\t\tvar type = match[1], node = elem;\n
\t\t\tswitch (type) {\n
\t\t\t\tcase \'only\':\n
\t\t\t\tcase \'first\':\n
\t\t\t\t\twhile (node = node.previousSibling)  {\n
\t\t\t\t\t\tif ( node.nodeType === 1 ) return false;\n
\t\t\t\t\t}\n
\t\t\t\t\tif ( type == \'first\') return true;\n
\t\t\t\t\tnode = elem;\n
\t\t\t\tcase \'last\':\n
\t\t\t\t\twhile (node = node.nextSibling)  {\n
\t\t\t\t\t\tif ( node.nodeType === 1 ) return false;\n
\t\t\t\t\t}\n
\t\t\t\t\treturn true;\n
\t\t\t\tcase \'nth\':\n
\t\t\t\t\tvar first = match[2], last = match[3];\n
\n
\t\t\t\t\tif ( first == 1 && last == 0 ) {\n
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
\t\t\t\t\tif ( first == 0 ) {\n
\t\t\t\t\t\treturn diff == 0;\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\treturn ( diff % first == 0 && diff / first >= 0 );\n
\t\t\t\t\t}\n
\t\t\t}\n
\t\t},\n
\t\tID: function(elem, match){\n
\t\t\treturn elem.nodeType === 1 && elem.getAttribute("id") === match;\n
\t\t},\n
\t\tTAG: function(elem, match){\n
\t\t\treturn (match === "*" && elem.nodeType === 1) || elem.nodeName === match;\n
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
\t\t\t\tvalue != check :\n
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
\tExpr.match[ type ] = RegExp( Expr.match[ type ].source + /(?![^\\[]*\\])(?![^\\(]*\\))/.source );\n
}\n
\n
var makeArray = function(array, results) {\n
\tarray = Array.prototype.slice.call( array );\n
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
try {\n
\tArray.prototype.slice.call( document.documentElement.childNodes );\n
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
\t\tvar ret = a.compareDocumentPosition(b) & 4 ? -1 : a === b ? 0 : 1;\n
\t\tif ( ret === 0 ) {\n
\t\t\thasDuplicate = true;\n
\t\t}\n
\t\treturn ret;\n
\t};\n
} else if ( "sourceIndex" in document.documentElement ) {\n
\tsortOrder = function( a, b ) {\n
\t\tvar ret = a.sourceIndex - b.sourceIndex;\n
\t\tif ( ret === 0 ) {\n
\t\t\thasDuplicate = true;\n
\t\t}\n
\t\treturn ret;\n
\t};\n
} else if ( document.createRange ) {\n
\tsortOrder = function( a, b ) {\n
\t\tvar aRange = a.ownerDocument.createRange(), bRange = b.ownerDocument.createRange();\n
\t\taRange.selectNode(a);\n
\t\taRange.collapse(true);\n
\t\tbRange.selectNode(b);\n
\t\tbRange.collapse(true);\n
\t\tvar ret = aRange.compareBoundaryPoints(Range.START_TO_END, bRange);\n
\t\tif ( ret === 0 ) {\n
\t\t\thasDuplicate = true;\n
\t\t}\n
\t\treturn ret;\n
\t};\n
}\n
\n
// Check to see if the browser returns elements by name when\n
// querying by getElementById (and provide a workaround)\n
(function(){\n
\t// We\'re going to inject a fake input element with a specified name\n
\tvar form = document.createElement("form"),\n
\t\tid = "script" + (new Date).getTime();\n
\tform.innerHTML = "<input name=\'" + id + "\'/>";\n
\n
\t// Inject it into the root element, check its status, and remove it quickly\n
\tvar root = document.documentElement;\n
\troot.insertBefore( form, root.firstChild );\n
\n
\t// The workaround has to do additional checks after a getElementById\n
\t// Which slows things down for other browsers (hence the branching)\n
\tif ( !!document.getElementById( id ) ) {\n
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
})();\n
\n
if ( document.querySelectorAll ) (function(){\n
\tvar oldSizzle = Sizzle, div = document.createElement("div");\n
\tdiv.innerHTML = "<p class=\'TEST\'></p>";\n
\n
\t// Safari can\'t handle uppercase or unicode characters when\n
\t// in quirks mode.\n
\tif ( div.querySelectorAll && div.querySelectorAll(".TEST").length === 0 ) {\n
\t\treturn;\n
\t}\n
\t\n
\tSizzle = function(query, context, extra, seed){\n
\t\tcontext = context || document;\n
\n
\t\t// Only use querySelectorAll on non-XML documents\n
\t\t// (ID selectors don\'t work in non-HTML documents)\n
\t\tif ( !seed && context.nodeType === 9 && !isXML(context) ) {\n
\t\t\ttry {\n
\t\t\t\treturn makeArray( context.querySelectorAll(query), extra );\n
\t\t\t} catch(e){}\n
\t\t}\n
\t\t\n
\t\treturn oldSizzle(query, context, extra, seed);\n
\t};\n
\n
\tSizzle.find = oldSizzle.find;\n
\tSizzle.filter = oldSizzle.filter;\n
\tSizzle.selectors = oldSizzle.selectors;\n
\tSizzle.matches = oldSizzle.matches;\n
})();\n
\n
if ( document.getElementsByClassName && document.documentElement.getElementsByClassName ) (function(){\n
\tvar div = document.createElement("div");\n
\tdiv.innerHTML = "<div class=\'test e\'></div><div class=\'test\'></div>";\n
\n
\t// Opera can\'t find a second classname (in 9.6)\n
\tif ( div.getElementsByClassName("e").length === 0 )\n
\t\treturn;\n
\n
\t// Safari caches class attributes, doesn\'t catch changes (in 3.2)\n
\tdiv.lastChild.className = "e";\n
\n
\tif ( div.getElementsByClassName("e").length === 1 )\n
\t\treturn;\n
\n
\tExpr.order.splice(1, 0, "CLASS");\n
\tExpr.find.CLASS = function(match, context, isXML) {\n
\t\tif ( typeof context.getElementsByClassName !== "undefined" && !isXML ) {\n
\t\t\treturn context.getElementsByClassName(match[1]);\n
\t\t}\n
\t};\n
})();\n
\n
function dirNodeCheck( dir, cur, doneName, checkSet, nodeCheck, isXML ) {\n
\tvar sibDir = dir == "previousSibling" && !isXML;\n
\tfor ( var i = 0, l = checkSet.length; i < l; i++ ) {\n
\t\tvar elem = checkSet[i];\n
\t\tif ( elem ) {\n
\t\t\tif ( sibDir && elem.nodeType === 1 ){\n
\t\t\t\telem.sizcache = doneName;\n
\t\t\t\telem.sizset = i;\n
\t\t\t}\n
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
\t\t\t\tif ( elem.nodeName === cur ) {\n
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
\tvar sibDir = dir == "previousSibling" && !isXML;\n
\tfor ( var i = 0, l = checkSet.length; i < l; i++ ) {\n
\t\tvar elem = checkSet[i];\n
\t\tif ( elem ) {\n
\t\t\tif ( sibDir && elem.nodeType === 1 ) {\n
\t\t\t\telem.sizcache = doneName;\n
\t\t\t\telem.sizset = i;\n
\t\t\t}\n
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
var contains = document.compareDocumentPosition ?  function(a, b){\n
\treturn a.compareDocumentPosition(b) & 16;\n
} : function(a, b){\n
\treturn a !== b && (a.contains ? a.contains(b) : true);\n
};\n
\n
var isXML = function(elem){\n
\treturn elem.nodeType === 9 && elem.documentElement.nodeName !== "HTML" ||\n
\t\t!!elem.ownerDocument && isXML( elem.ownerDocument );\n
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
jQuery.filter = Sizzle.filter;\n
jQuery.expr = Sizzle.selectors;\n
jQuery.expr[":"] = jQuery.expr.filters;\n
\n
Sizzle.selectors.filters.hidden = function(elem){\n
\treturn elem.offsetWidth === 0 || elem.offsetHeight === 0;\n
};\n
\n
Sizzle.selectors.filters.visible = function(elem){\n
\treturn elem.offsetWidth > 0 || elem.offsetHeight > 0;\n
};\n
\n
Sizzle.selectors.filters.animated = function(elem){\n
\treturn jQuery.grep(jQuery.timers, function(fn){\n
\t\treturn elem === fn.elem;\n
\t}).length;\n
};\n
\n
jQuery.multiFilter = function( expr, elems, not ) {\n
\tif ( not ) {\n
\t\texpr = ":not(" + expr + ")";\n
\t}\n
\n
\treturn Sizzle.matches(expr, elems);\n
};\n
\n
jQuery.dir = function( elem, dir ){\n
\tvar matched = [], cur = elem[dir];\n
\twhile ( cur && cur != document ) {\n
\t\tif ( cur.nodeType == 1 )\n
\t\t\tmatched.push( cur );\n
\t\tcur = cur[dir];\n
\t}\n
\treturn matched;\n
};\n
\n
jQuery.nth = function(cur, result, dir, elem){\n
\tresult = result || 1;\n
\tvar num = 0;\n
\n
\tfor ( ; cur; cur = cur[dir] )\n
\t\tif ( cur.nodeType == 1 && ++num == result )\n
\t\t\tbreak;\n
\n
\treturn cur;\n
};\n
\n
jQuery.sibling = function(n, elem){\n
\tvar r = [];\n
\n
\tfor ( ; n; n = n.nextSibling ) {\n
\t\tif ( n.nodeType == 1 && n != elem )\n
\t\t\tr.push( n );\n
\t}\n
\n
\treturn r;\n
};\n
\n
return;\n
\n
window.Sizzle = Sizzle;\n
\n
})();\n
/*\n
 * A number of helper functions used for managing events.\n
 * Many of the ideas behind this code originated from\n
 * Dean Edwards\' addEvent library.\n
 */\n
jQuery.event = {\n
\n
\t// Bind an event to an element\n
\t// Original by Dean Edwards\n
\tadd: function(elem, types, handler, data) {\n
\t\tif ( elem.nodeType == 3 || elem.nodeType == 8 )\n
\t\t\treturn;\n
\n
\t\t// For whatever reason, IE has trouble passing the window object\n
\t\t// around, causing it to be cloned in the process\n
\t\tif ( elem.setInterval && elem != window )\n
\t\t\telem = window;\n
\n
\t\t// Make sure that the function being executed has a unique ID\n
\t\tif ( !handler.guid )\n
\t\t\thandler.guid = this.guid++;\n
\n
\t\t// if data is passed, bind to handler\n
\t\tif ( data !== undefined ) {\n
\t\t\t// Create temporary function pointer to original handler\n
\t\t\tvar fn = handler;\n
\n
\t\t\t// Create unique handler function, wrapped around original handler\n
\t\t\thandler = this.proxy( fn );\n
\n
\t\t\t// Store data in unique handler\n
\t\t\thandler.data = data;\n
\t\t}\n
\n
\t\t// Init the element\'s event structure\n
\t\tvar events = jQuery.data(elem, "events") || jQuery.data(elem, "events", {}),\n
\t\t\thandle = jQuery.data(elem, "handle") || jQuery.data(elem, "handle", function(){\n
\t\t\t\t// Handle the second event of a trigger and when\n
\t\t\t\t// an event is called after a page has unloaded\n
\t\t\t\treturn typeof jQuery !== "undefined" && !jQuery.event.triggered ?\n
\t\t\t\t\tjQuery.event.handle.apply(arguments.callee.elem, arguments) :\n
\t\t\t\t\tundefined;\n
\t\t\t});\n
\t\t// Add elem as a property of the handle function\n
\t\t// This is to prevent a memory leak with non-native\n
\t\t// event in IE.\n
\t\thandle.elem = elem;\n
\n
\t\t// Handle multiple events separated by a space\n
\t\t// jQuery(...).bind("mouseover mouseout", fn);\n
\t\tjQuery.each(types.split(/\\s+/), function(index, type) {\n
\t\t\t// Namespaced event handlers\n
\t\t\tvar namespaces = type.split(".");\n
\t\t\ttype = namespaces.shift();\n
\t\t\thandler.type = namespaces.slice().sort().join(".");\n
\n
\t\t\t// Get the current list of functions bound to this event\n
\t\t\tvar handlers = events[type];\n
\t\t\t\n
\t\t\tif ( jQuery.event.specialAll[type] )\n
\t\t\t\tjQuery.event.specialAll[type].setup.call(elem, data, namespaces);\n
\n
\t\t\t// Init the event handler queue\n
\t\t\tif (!handlers) {\n
\t\t\t\thandlers = events[type] = {};\n
\n
\t\t\t\t// Check for a special event handler\n
\t\t\t\t// Only use addEventListener/attachEvent if the special\n
\t\t\t\t// events handler returns false\n
\t\t\t\tif ( !jQuery.event.special[type] || jQuery.event.special[type].setup.call(elem, data, namespaces) === false ) {\n
\t\t\t\t\t// Bind the global event handler to the element\n
\t\t\t\t\tif (elem.addEventListener)\n
\t\t\t\t\t\telem.addEventListener(type, handle, false);\n
\t\t\t\t\telse if (elem.attachEvent)\n
\t\t\t\t\t\telem.attachEvent("on" + type, handle);\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// Add the function to the element\'s handler list\n
\t\t\thandlers[handler.guid] = handler;\n
\n
\t\t\t// Keep track of which events have been used, for global triggering\n
\t\t\tjQuery.event.global[type] = true;\n
\t\t});\n
\n
\t\t// Nullify elem to prevent memory leaks in IE\n
\t\telem = null;\n
\t},\n
\n
\tguid: 1,\n
\tglobal: {},\n
\n
\t// Detach an event or set of events from an element\n
\tremove: function(elem, types, handler) {\n
\t\t// don\'t do events on text and comment nodes\n
\t\tif ( elem.nodeType == 3 || elem.nodeType == 8 )\n
\t\t\treturn;\n
\n
\t\tvar events = jQuery.data(elem, "events"), ret, index;\n
\n
\t\tif ( events ) {\n
\t\t\t// Unbind all events for the element\n
\t\t\tif ( types === undefined || (typeof types === "string" && types.charAt(0) == ".") )\n
\t\t\t\tfor ( var type in events )\n
\t\t\t\t\tthis.remove( elem, type + (types || "") );\n
\t\t\telse {\n
\t\t\t\t// types is actually an event object here\n
\t\t\t\tif ( types.type ) {\n
\t\t\t\t\thandler = types.handler;\n
\t\t\t\t\ttypes = types.type;\n
\t\t\t\t}\n
\n
\t\t\t\t// Handle multiple events seperated by a space\n
\t\t\t\t// jQuery(...).unbind("mouseover mouseout", fn);\n
\t\t\t\tjQuery.each(types.split(/\\s+/), function(index, type){\n
\t\t\t\t\t// Namespaced event handlers\n
\t\t\t\t\tvar namespaces = type.split(".");\n
\t\t\t\t\ttype = namespaces.shift();\n
\t\t\t\t\tvar namespace = RegExp("(^|\\\\.)" + namespaces.slice().sort().join(".*\\\\.") + "(\\\\.|$)");\n
\n
\t\t\t\t\tif ( events[type] ) {\n
\t\t\t\t\t\t// remove the given handler for the given type\n
\t\t\t\t\t\tif ( handler )\n
\t\t\t\t\t\t\tdelete events[type][handler.guid];\n
\n
\t\t\t\t\t\t// remove all handlers for the given type\n
\t\t\t\t\t\telse\n
\t\t\t\t\t\t\tfor ( var handle in events[type] )\n
\t\t\t\t\t\t\t\t// Handle the removal of namespaced events\n
\t\t\t\t\t\t\t\tif ( namespace.test(events[type][handle].type) )\n
\t\t\t\t\t\t\t\t\tdelete events[type][handle];\n
\t\t\t\t\t\t\t\t\t\n
\t\t\t\t\t\tif ( jQuery.event.specialAll[type] )\n
\t\t\t\t\t\t\tjQuery.event.specialAll[type].teardown.call(elem, namespaces);\n
\n
\t\t\t\t\t\t// remove generic event handler if no more handlers exist\n
\t\t\t\t\t\tfor ( ret in events[type] ) break;\n
\t\t\t\t\t\tif ( !ret ) {\n
\t\t\t\t\t\t\tif ( !jQuery.event.special[type] || jQuery.event.special[type].teardown.call(elem, namespaces) === false ) {\n
\t\t\t\t\t\t\t\tif (elem.removeEventListener)\n
\t\t\t\t\t\t\t\t\telem.removeEventListener(type, jQuery.data(elem, "handle"), false);\n
\t\t\t\t\t\t\t\telse if (elem.detachEvent)\n
\t\t\t\t\t\t\t\t\telem.detachEvent("on" + type, jQuery.data(elem, "handle"));\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t\tret = null;\n
\t\t\t\t\t\t\tdelete events[type];\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t});\n
\t\t\t}\n
\n
\t\t\t// Remove the expando if it\'s no longer used\n
\t\t\tfor ( ret in events ) break;\n
\t\t\tif ( !ret ) {\n
\t\t\t\tvar handle = jQuery.data( elem, "handle" );\n
\t\t\t\tif ( handle ) handle.elem = null;\n
\t\t\t\tjQuery.removeData( elem, "events" );\n
\t\t\t\tjQuery.removeData( elem, "handle" );\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\t// bubbling is internal\n
\ttrigger: function( event, data, elem, bubbling ) {\n
\t\t// Event object or event type\n
\t\tvar type = event.type || event;\n
\n
\t\tif( !bubbling ){\n
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
\t\t\t\t// Only trigger if we\'ve ever bound an event for it\n
\t\t\t\tif ( this.global[type] )\n
\t\t\t\t\tjQuery.each( jQuery.cache, function(){\n
\t\t\t\t\t\tif ( this.events && this.events[type] )\n
\t\t\t\t\t\t\tjQuery.event.trigger( event, data, this.handle.elem );\n
\t\t\t\t\t});\n
\t\t\t}\n
\n
\t\t\t// Handle triggering a single element\n
\n
\t\t\t// don\'t do events on text and comment nodes\n
\t\t\tif ( !elem || elem.nodeType == 3 || elem.nodeType == 8 )\n
\t\t\t\treturn undefined;\n
\t\t\t\n
\t\t\t// Clean up in case it is reused\n
\t\t\tevent.result = undefined;\n
\t\t\tevent.target = elem;\n
\t\t\t\n
\t\t\t// Clone the incoming data, if any\n
\t\t\tdata = jQuery.makeArray(data);\n
\t\t\tdata.unshift( event );\n
\t\t}\n
\n
\t\tevent.currentTarget = elem;\n
\n
\t\t// Trigger the event, it is assumed that "handle" is a function\n
\t\tvar handle = jQuery.data(elem, "handle");\n
\t\tif ( handle )\n
\t\t\thandle.apply( elem, data );\n
\n
\t\t// Handle triggering native .onfoo handlers (and on links since we don\'t call .click() for links)\n
\t\tif ( (!elem[type] || (jQuery.nodeName(elem, \'a\') && type == "click")) && elem["on"+type] && elem["on"+type].apply( elem, data ) === false )\n
\t\t\tevent.result = false;\n
\n
\t\t// Trigger the native events (except for clicks on links)\n
\t\tif ( !bubbling && elem[type] && !event.isDefaultPrevented() && !(jQuery.nodeName(elem, \'a\') && type == "click") ) {\n
\t\t\tthis.triggered = true;\n
\t\t\ttry {\n
\t\t\t\telem[ type ]();\n
\t\t\t// prevent IE from throwing an error for some hidden elements\n
\t\t\t} catch (e) {}\n
\t\t}\n
\n
\t\tthis.triggered = false;\n
\n
\t\tif ( !event.isPropagationStopped() ) {\n
\t\t\tvar parent = elem.parentNode || elem.ownerDocument;\n
\t\t\tif ( parent )\n
\t\t\t\tjQuery.event.trigger(event, data, parent, true);\n
\t\t}\n
\t},\n
\n
\thandle: function(event) {\n
\t\t// returned undefined or false\n
\t\tvar all, handlers;\n
\n
\t\tevent = arguments[0] = jQuery.event.fix( event || window.event );\n
\t\tevent.currentTarget = this;\n
\t\t\n
\t\t// Namespaced event handlers\n
\t\tvar namespaces = event.type.split(".");\n
\t\tevent.type = namespaces.shift();\n
\n
\t\t// Cache this now, all = true means, any handler\n
\t\tall = !namespaces.length && !event.exclusive;\n
\t\t\n
\t\tvar namespace = RegExp("(^|\\\\.)" + namespaces.slice().sort().join(".*\\\\.") + "(\\\\.|$)");\n
\n
\t\thandlers = ( jQuery.data(this, "events") || {} )[event.type];\n
\n
\t\tfor ( var j in handlers ) {\n
\t\t\tvar handler = handlers[j];\n
\n
\t\t\t// Filter the functions by class\n
\t\t\tif ( all || namespace.test(handler.type) ) {\n
\t\t\t\t// Pass in a reference to the handler function itself\n
\t\t\t\t// So that we can later remove it\n
\t\t\t\tevent.handler = handler;\n
\t\t\t\tevent.data = handler.data;\n
\n
\t\t\t\tvar ret = handler.apply(this, arguments);\n
\n
\t\t\t\tif( ret !== undefined ){\n
\t\t\t\t\tevent.result = ret;\n
\t\t\t\t\tif ( ret === false ) {\n
\t\t\t\t\t\tevent.preventDefault();\n
\t\t\t\t\t\tevent.stopPropagation();\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\tif( event.isImmediatePropagationStopped() )\n
\t\t\t\t\tbreak;\n
\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\tprops: "altKey attrChange attrName bubbles button cancelable charCode clientX clientY ctrlKey currentTarget data detail eventPhase fromElement handler keyCode metaKey newValue originalTarget pageX pageY prevValue relatedNode relatedTarget screenX screenY shiftKey srcElement target toElement view wheelDelta which".split(" "),\n
\n
\tfix: function(event) {\n
\t\tif ( event[expando] )\n
\t\t\treturn event;\n
\n
\t\t// store a copy of the original event object\n
\t\t// and "clone" to set read-only properties\n
\t\tvar originalEvent = event;\n
\t\tevent = jQuery.Event( originalEvent );\n
\n
\t\tfor ( var i = this.props.length, prop; i; ){\n
\t\t\tprop = this.props[ --i ];\n
\t\t\tevent[ prop ] = originalEvent[ prop ];\n
\t\t}\n
\n
\t\t// Fix target property, if necessary\n
\t\tif ( !event.target )\n
\t\t\tevent.target = event.srcElement || document; // Fixes #1925 where srcElement might not be defined either\n
\n
\t\t// check if target is a textnode (safari)\n
\t\tif ( event.target.nodeType == 3 )\n
\t\t\tevent.target = event.target.parentNode;\n
\n
\t\t// Add relatedTarget, if necessary\n
\t\tif ( !event.relatedTarget && event.fromElement )\n
\t\t\tevent.relatedTarget = event.fromElement == event.target ? event.toElement : event.fromElement;\n
\n
\t\t// Calculate pageX/Y if missing and clientX/Y available\n
\t\tif ( event.pageX == null && event.clientX != null ) {\n
\t\t\tvar doc = document.documentElement, body = document.body;\n
\t\t\tevent.pageX = event.clientX + (doc && doc.scrollLeft || body && body.scrollLeft || 0) - (doc.clientLeft || 0);\n
\t\t\tevent.pageY = event.clientY + (doc && doc.scrollTop || body && body.scrollTop || 0) - (doc.clientTop || 0);\n
\t\t}\n
\n
\t\t// Add which for key events\n
\t\tif ( !event.which && ((event.charCode || event.charCode === 0) ? event.charCode : event.keyCode) )\n
\t\t\tevent.which = event.charCode || event.keyCode;\n
\n
\t\t// Add metaKey to non-Mac browsers (use ctrl for PC\'s and Meta for Macs)\n
\t\tif ( !event.metaKey && event.ctrlKey )\n
\t\t\tevent.metaKey = event.ctrlKey;\n
\n
\t\t// Add which for click: 1 == left; 2 == middle; 3 == right\n
\t\t// Note: button is not normalized, so don\'t use it\n
\t\tif ( !event.which && event.button )\n
\t\t\tevent.which = (event.button & 1 ? 1 : ( event.button & 2 ? 3 : ( event.button & 4 ? 2 : 0 ) ));\n
\n
\t\treturn event;\n
\t},\n
\n
\tproxy: function( fn, proxy ){\n
\t\tproxy = proxy || function(){ return fn.apply(this, arguments); };\n
\t\t// Set the guid of unique handler to the same of original handler, so it can be removed\n
\t\tproxy.guid = fn.guid = fn.guid || proxy.guid || this.guid++;\n
\t\t// So proxy can be declared as an argument\n
\t\treturn proxy;\n
\t},\n
\n
\tspecial: {\n
\t\tready: {\n
\t\t\t// Make sure the ready event is setup\n
\t\t\tsetup: bindReady,\n
\t\t\tteardown: function() {}\n
\t\t}\n
\t},\n
\t\n
\tspecialAll: {\n
\t\tlive: {\n
\t\t\tsetup: function( selector, namespaces ){\n
\t\t\t\tjQuery.event.add( this, namespaces[0], liveHandler );\n
\t\t\t},\n
\t\t\tteardown:  function( namespaces ){\n
\t\t\t\tif ( namespaces.length ) {\n
\t\t\t\t\tvar remove = 0, name = RegExp("(^|\\\\.)" + namespaces[0] + "(\\\\.|$)");\n
\t\t\t\t\t\n
\t\t\t\t\tjQuery.each( (jQuery.data(this, "events").live || {}), function(){\n
\t\t\t\t\t\tif ( name.test(this.type) )\n
\t\t\t\t\t\t\tremove++;\n
\t\t\t\t\t});\n
\t\t\t\t\t\n
\t\t\t\t\tif ( remove < 1 )\n
\t\t\t\t\t\tjQuery.event.remove( this, namespaces[0], liveHandler );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t}\n
};\n
\n
jQuery.Event = function( src ){\n
\t// Allow instantiation without the \'new\' keyword\n
\tif( !this.preventDefault )\n
\t\treturn new jQuery.Event(src);\n
\t\n
\t// Event object\n
\tif( src && src.type ){\n
\t\tthis.originalEvent = src;\n
\t\tthis.type = src.type;\n
\t// Event type\n
\t}else\n
\t\tthis.type = src;\n
\n
\t// timeStamp is buggy for some events on Firefox(#3843)\n
\t// So we won\'t rely on the native value\n
\tthis.timeStamp = now();\n
\t\n
\t// Mark it as fixed\n
\tthis[expando] = true;\n
};\n
\n
function returnFalse(){\n
\treturn false;\n
}\n
function returnTrue(){\n
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
\t\tif( !e )\n
\t\t\treturn;\n
\t\t// if preventDefault exists run it on the original event\n
\t\tif (e.preventDefault)\n
\t\t\te.preventDefault();\n
\t\t// otherwise set the returnValue property of the original event to false (IE)\n
\t\te.returnValue = false;\n
\t},\n
\tstopPropagation: function() {\n
\t\tthis.isPropagationStopped = returnTrue;\n
\n
\t\tvar e = this.originalEvent;\n
\t\tif( !e )\n
\t\t\treturn;\n
\t\t// if stopPropagation exists run it on the original event\n
\t\tif (e.stopPropagation)\n
\t\t\te.stopPropagation();\n
\t\t// otherwise set the cancelBubble property of the original event to true (IE)\n
\t\te.cancelBubble = true;\n
\t},\n
\tstopImmediatePropagation:function(){\n
\t\tthis.isImmediatePropagationStopped = returnTrue;\n
\t\tthis.stopPropagation();\n
\t},\n
\tisDefaultPrevented: returnFalse,\n
\tisPropagationStopped: returnFalse,\n
\tisImmediatePropagationStopped: returnFalse\n
};\n
// Checks if an event happened on an element within another element\n
// Used in jQuery.event.special.mouseenter and mouseleave handlers\n
var withinElement = function(event) {\n
\t// Check if mouse(over|out) are still within the same parent element\n
\tvar parent = event.relatedTarget;\n
\t// Traverse up the tree\n
\twhile ( parent && parent != this )\n
\t\ttry { parent = parent.parentNode; }\n
\t\tcatch(e) { parent = this; }\n
\t\n
\tif( parent != this ){\n
\t\t// set the correct event type\n
\t\tevent.type = event.data;\n
\t\t// handle event if we actually just moused on to a non sub-element\n
\t\tjQuery.event.handle.apply( this, arguments );\n
\t}\n
};\n
\t\n
jQuery.each({ \n
\tmouseover: \'mouseenter\', \n
\tmouseout: \'mouseleave\'\n
}, function( orig, fix ){\n
\tjQuery.event.special[ fix ] = {\n
\t\tsetup: function(){\n
\t\t\tjQuery.event.add( this, orig, withinElement, fix );\n
\t\t},\n
\t\tteardown: function(){\n
\t\t\tjQuery.event.remove( this, orig, withinElement );\n
\t\t}\n
\t};\t\t\t   \n
});\n
\n
jQuery.fn.extend({\n
\tbind: function( type, data, fn ) {\n
\t\treturn type == "unload" ? this.one(type, data, fn) : this.each(function(){\n
\t\t\tjQuery.event.add( this, type, fn || data, fn && data );\n
\t\t});\n
\t},\n
\n
\tone: function( type, data, fn ) {\n
\t\tvar one = jQuery.event.proxy( fn || data, function(event) {\n
\t\t\tjQuery(this).unbind(event, one);\n
\t\t\treturn (fn || data).apply( this, arguments );\n
\t\t});\n
\t\treturn this.each(function(){\n
\t\t\tjQuery.event.add( this, type, one, fn && data);\n
\t\t});\n
\t},\n
\n
\tunbind: function( type, fn ) {\n
\t\treturn this.each(function(){\n
\t\t\tjQuery.event.remove( this, type, fn );\n
\t\t});\n
\t},\n
\n
\ttrigger: function( type, data ) {\n
\t\treturn this.each(function(){\n
\t\t\tjQuery.event.trigger( type, data, this );\n
\t\t});\n
\t},\n
\n
\ttriggerHandler: function( type, data ) {\n
\t\tif( this[0] ){\n
\t\t\tvar event = jQuery.Event(type);\n
\t\t\tevent.preventDefault();\n
\t\t\tevent.stopPropagation();\n
\t\t\tjQuery.event.trigger( event, data, this[0] );\n
\t\t\treturn event.result;\n
\t\t}\t\t\n
\t},\n
\n
\ttoggle: function( fn ) {\n
\t\t// Save reference to arguments for access in closure\n
\t\tvar args = arguments, i = 1;\n
\n
\t\t// link all the functions, so any of them can unbind this click handler\n
\t\twhile( i < args.length )\n
\t\t\tjQuery.event.proxy( fn, args[i++] );\n
\n
\t\treturn this.click( jQuery.event.proxy( fn, function(event) {\n
\t\t\t// Figure out which function to execute\n
\t\t\tthis.lastToggle = ( this.lastToggle || 0 ) % i;\n
\n
\t\t\t// Make sure that clicks stop\n
\t\t\tevent.preventDefault();\n
\n
\t\t\t// and execute the function\n
\t\t\treturn args[ this.lastToggle++ ].apply( this, arguments ) || false;\n
\t\t}));\n
\t},\n
\n
\thover: function(fnOver, fnOut) {\n
\t\treturn this.mouseenter(fnOver).mouseleave(fnOut);\n
\t},\n
\n
\tready: function(fn) {\n
\t\t// Attach the listeners\n
\t\tbindReady();\n
\n
\t\t// If the DOM is already ready\n
\t\tif ( jQuery.isReady )\n
\t\t\t// Execute the function immediately\n
\t\t\tfn.call( document, jQuery );\n
\n
\t\t// Otherwise, remember the function for later\n
\t\telse\n
\t\t\t// Add the function to the wait list\n
\t\t\tjQuery.readyList.push( fn );\n
\n
\t\treturn this;\n
\t},\n
\t\n
\tlive: function( type, fn ){\n
\t\tvar proxy = jQuery.event.proxy( fn );\n
\t\tproxy.guid += this.selector + type;\n
\n
\t\tjQuery(document).bind( liveConvert(type, this.selector), this.selector, proxy );\n
\n
\t\treturn this;\n
\t},\n
\t\n
\tdie: function( type, fn ){\n
\t\tjQuery(document).unbind( liveConvert(type, this.selector), fn ? { guid: fn.guid + this.selector + type } : null );\n
\t\treturn this;\n
\t}\n
});\n
\n
function liveHandler( event ){\n
\tvar check = RegExp("(^|\\\\.)" + event.type + "(\\\\.|$)"),\n
\t\tstop = true,\n
\t\telems = [];\n
\n
\tjQuery.each(jQuery.data(this, "events").live || [], function(i, fn){\n
\t\tif ( check.test(fn.type) ) {\n
\t\t\tvar elem = jQuery(event.target).closest(fn.data)[0];\n
\t\t\tif ( elem )\n
\t\t\t\telems.push({ elem: elem, fn: fn });\n
\t\t}\n
\t});\n
\n
\telems.sort(function(a,b) {\n
\t\treturn jQuery.data(a.elem, "closest") - jQuery.data(b.elem, "closest");\n
\t});\n
\t\n
\tjQuery.each(elems, function(){\n
\t\tif ( this.fn.call(this.elem, event, this.fn.data) === false )\n
\t\t\treturn (stop = false);\n
\t});\n
\n
\treturn stop;\n
}\n
\n
function liveConvert(type, selector){\n
\treturn ["live", type, selector.replace(/\\./g, "`").replace(/ /g, "|")].join(".");\n
}\n
\n
jQuery.extend({\n
\tisReady: false,\n
\treadyList: [],\n
\t// Handle when the DOM is ready\n
\tready: function() {\n
\t\t// Make sure that the DOM is not already loaded\n
\t\tif ( !jQuery.isReady ) {\n
\t\t\t// Remember that the DOM is ready\n
\t\t\tjQuery.isReady = true;\n
\n
\t\t\t// If there are functions bound, to execute\n
\t\t\tif ( jQuery.readyList ) {\n
\t\t\t\t// Execute all of them\n
\t\t\t\tjQuery.each( jQuery.readyList, function(){\n
\t\t\t\t\tthis.call( document, jQuery );\n
\t\t\t\t});\n
\n
\t\t\t\t// Reset the list of functions\n
\t\t\t\tjQuery.readyList = null;\n
\t\t\t}\n
\n
\t\t\t// Trigger any bound ready events\n
\t\t\tjQuery(document).triggerHandler("ready");\n
\t\t}\n
\t}\n
});\n
\n
var readyBound = false;\n
\n
function bindReady(){\n
\tif ( readyBound ) return;\n
\treadyBound = true;\n
\n
\t// Mozilla, Opera and webkit nightlies currently support this event\n
\tif ( document.addEventListener ) {\n
\t\t// Use the handy event callback\n
\t\tdocument.addEventListener( "DOMContentLoaded", function(){\n
\t\t\tdocument.removeEventListener( "DOMContentLoaded", arguments.callee, false );\n
\t\t\tjQuery.ready();\n
\t\t}, false );\n
\n
\t// If IE event model is used\n
\t} else if ( document.attachEvent ) {\n
\t\t// ensure firing before onload,\n
\t\t// maybe late but safe also for iframes\n
\t\tdocument.attachEvent("onreadystatechange", function(){\n
\t\t\tif ( document.readyState === "complete" ) {\n
\t\t\t\tdocument.detachEvent( "onreadystatechange", arguments.callee );\n
\t\t\t\tjQuery.ready();\n
\t\t\t}\n
\t\t});\n
\n
\t\t// If IE and not an iframe\n
\t\t// continually check to see if the document is ready\n
\t\tif ( document.documentElement.doScroll && window == window.top ) (function(){\n
\t\t\tif ( jQuery.isReady ) return;\n
\n
\t\t\ttry {\n
\t\t\t\t// If IE is used, use the trick by Diego Perini\n
\t\t\t\t// http://javascript.nwbox.com/IEContentLoaded/\n
\t\t\t\tdocument.documentElement.doScroll("left");\n
\t\t\t} catch( error ) {\n
\t\t\t\tsetTimeout( arguments.callee, 0 );\n
\t\t\t\treturn;\n
\t\t\t}\n
\n
\t\t\t// and execute any waiting functions\n
\t\t\tjQuery.ready();\n
\t\t})();\n
\t}\n
\n
\t// A fallback to window.onload, that will always work\n
\tjQuery.event.add( window, "load", jQuery.ready );\n
}\n
\n
jQuery.each( ("blur,focus,load,resize,scroll,unload,click,dblclick," +\n
\t"mousedown,mouseup,mousemove,mouseover,mouseout,mouseenter,mouseleave," +\n
\t"change,select,submit,keydown,keypress,keyup,error").split(","), function(i, name){\n
\n
\t// Handle event binding\n
\tjQuery.fn[name] = function(fn){\n
\t\treturn fn ? this.bind(name, fn) : this.trigger(name);\n
\t};\n
});\n
\n
// Prevent memory leaks in IE\n
// And prevent errors on refresh with events like mouseover in other browsers\n
// Window isn\'t included so as not to unbind existing unload events\n
jQuery( window ).bind( \'unload\', function(){ \n
\tfor ( var id in jQuery.cache )\n
\t\t// Skip the window\n
\t\tif ( id != 1 && jQuery.cache[ id ].handle )\n
\t\t\tjQuery.event.remove( jQuery.cache[ id ].handle.elem );\n
}); \n
(function(){\n
\n
\tjQuery.support = {};\n
\n
\tvar root = document.documentElement,\n
\t\tscript = document.createElement("script"),\n
\t\tdiv = document.createElement("div"),\n
\t\tid = "script" + (new Date).getTime();\n
\n
\tdiv.style.display = "none";\n
\tdiv.innerHTML = \'   <link/><table></table><a href="/a" style="color:red;float:left;opacity:.5;">a</a><select><option>text</option></select><object><param/></object>\';\n
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
\t\tleadingWhitespace: div.firstChild.nodeType == 3,\n
\t\t\n
\t\t// Make sure that tbody elements aren\'t automatically inserted\n
\t\t// IE will insert them into empty tables\n
\t\ttbody: !div.getElementsByTagName("tbody").length,\n
\t\t\n
\t\t// Make sure that you can get all elements in an <object> element\n
\t\t// IE 7 always returns no results\n
\t\tobjectAll: !!div.getElementsByTagName("object")[0]\n
\t\t\t.getElementsByTagName("*").length,\n
\t\t\n
\t\t// Make sure that link elements get serialized correctly by innerHTML\n
\t\t// This requires a wrapper element in IE\n
\t\thtmlSerialize: !!div.getElementsByTagName("link").length,\n
\t\t\n
\t\t// Get the style information from getAttribute\n
\t\t// (IE uses .cssText insted)\n
\t\tstyle: /red/.test( a.getAttribute("style") ),\n
\t\t\n
\t\t// Make sure that URLs aren\'t manipulated\n
\t\t// (IE normalizes it by default)\n
\t\threfNormalized: a.getAttribute("href") === "/a",\n
\t\t\n
\t\t// Make sure that element opacity exists\n
\t\t// (IE uses filter instead)\n
\t\topacity: a.style.opacity === "0.5",\n
\t\t\n
\t\t// Verify style float existence\n
\t\t// (IE uses styleFloat instead of cssFloat)\n
\t\tcssFloat: !!a.style.cssFloat,\n
\n
\t\t// Will be defined later\n
\t\tscriptEval: false,\n
\t\tnoCloneEvent: true,\n
\t\tboxModel: null\n
\t};\n
\t\n
\tscript.type = "text/javascript";\n
\ttry {\n
\t\tscript.appendChild( document.createTextNode( "window." + id + "=1;" ) );\n
\t} catch(e){}\n
\n
\troot.insertBefore( script, root.firstChild );\n
\t\n
\t// Make sure that the execution of code works by injecting a script\n
\t// tag with appendChild/createTextNode\n
\t// (IE doesn\'t support this, fails, and uses .text instead)\n
\tif ( window[ id ] ) {\n
\t\tjQuery.support.scriptEval = true;\n
\t\tdelete window[ id ];\n
\t}\n
\n
\troot.removeChild( script );\n
\n
\tif ( div.attachEvent && div.fireEvent ) {\n
\t\tdiv.attachEvent("onclick", function(){\n
\t\t\t// Cloning a node shouldn\'t copy over any\n
\t\t\t// bound event handlers (IE does this)\n
\t\t\tjQuery.support.noCloneEvent = false;\n
\t\t\tdiv.detachEvent("onclick", arguments.callee);\n
\t\t});\n
\t\tdiv.cloneNode(true).fireEvent("onclick");\n
\t}\n
\n
\t// Figure out if the W3C box model works as expected\n
\t// document.body must exist before we can do this\n
\tjQuery(function(){\n
\t\tvar div = document.createElement("div");\n
\t\tdiv.style.width = div.style.paddingLeft = "1px";\n
\n
\t\tdocument.body.appendChild( div );\n
\t\tjQuery.boxModel = jQuery.support.boxModel = div.offsetWidth === 2;\n
\t\tdocument.body.removeChild( div ).style.display = \'none\';\n
\t});\n
})();\n
\n
var styleFloat = jQuery.support.cssFloat ? "cssFloat" : "styleFloat";\n
\n
jQuery.props = {\n
\t"for": "htmlFor",\n
\t"class": "className",\n
\t"float": styleFloat,\n
\tcssFloat: styleFloat,\n
\tstyleFloat: styleFloat,\n
\treadonly: "readOnly",\n
\tmaxlength: "maxLength",\n
\tcellspacing: "cellSpacing",\n
\trowspan: "rowSpan",\n
\ttabindex: "tabIndex"\n
};\n
jQuery.fn.extend({\n
\t// Keep a copy of the old load\n
\t_load: jQuery.fn.load,\n
\n
\tload: function( url, params, callback ) {\n
\t\tif ( typeof url !== "string" )\n
\t\t\treturn this._load( url );\n
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
\t\tif ( params )\n
\t\t\t// If it\'s a function\n
\t\t\tif ( jQuery.isFunction( params ) ) {\n
\t\t\t\t// We assume that it\'s the callback\n
\t\t\t\tcallback = params;\n
\t\t\t\tparams = null;\n
\n
\t\t\t// Otherwise, build a param string\n
\t\t\t} else if( typeof params === "object" ) {\n
\t\t\t\tparams = jQuery.param( params );\n
\t\t\t\ttype = "POST";\n
\t\t\t}\n
\n
\t\tvar self = this;\n
\n
\t\t// Request the remote document\n
\t\tjQuery.ajax({\n
\t\t\turl: url,\n
\t\t\ttype: type,\n
\t\t\tdataType: "html",\n
\t\t\tdata: params,\n
\t\t\tcomplete: function(res, status){\n
\t\t\t\t// If successful, inject the HTML into all the matched elements\n
\t\t\t\tif ( status == "success" || status == "notmodified" )\n
\t\t\t\t\t// See if a selector was specified\n
\t\t\t\t\tself.html( selector ?\n
\t\t\t\t\t\t// Create a dummy div to hold the results\n
\t\t\t\t\t\tjQuery("<div/>")\n
\t\t\t\t\t\t\t// inject the contents of the document in, removing the scripts\n
\t\t\t\t\t\t\t// to avoid any \'Permission Denied\' errors in IE\n
\t\t\t\t\t\t\t.append(res.responseText.replace(/<script(.|\\s)*?\\/script>/g, ""))\n
\n
\t\t\t\t\t\t\t// Locate the specified elements\n
\t\t\t\t\t\t\t.find(selector) :\n
\n
\t\t\t\t\t\t// If not, just inject the full result\n
\t\t\t\t\t\tres.responseText );\n
\n
\t\t\t\tif( callback )\n
\t\t\t\t\tself.each( callback, [res.responseText, status, res] );\n
\t\t\t}\n
\t\t});\n
\t\treturn this;\n
\t},\n
\n
\tserialize: function() {\n
\t\treturn jQuery.param(this.serializeArray());\n
\t},\n
\tserializeArray: function() {\n
\t\treturn this.map(function(){\n
\t\t\treturn this.elements ? jQuery.makeArray(this.elements) : this;\n
\t\t})\n
\t\t.filter(function(){\n
\t\t\treturn this.name && !this.disabled &&\n
\t\t\t\t(this.checked || /select|textarea/i.test(this.nodeName) ||\n
\t\t\t\t\t/text|hidden|password|search/i.test(this.type));\n
\t\t})\n
\t\t.map(function(i, elem){\n
\t\t\tvar val = jQuery(this).val();\n
\t\t\treturn val == null ? null :\n
\t\t\t\tjQuery.isArray(val) ?\n
\t\t\t\t\tjQuery.map( val, function(val, i){\n
\t\t\t\t\t\treturn {name: elem.name, value: val};\n
\t\t\t\t\t}) :\n
\t\t\t\t\t{name: elem.name, value: val};\n
\t\t}).get();\n
\t}\n
});\n
\n
// Attach a bunch of functions for handling common AJAX events\n
jQuery.each( "ajaxStart,ajaxStop,ajaxComplete,ajaxError,ajaxSuccess,ajaxSend".split(","), function(i,o){\n
\tjQuery.fn[o] = function(f){\n
\t\treturn this.bind(o, f);\n
\t};\n
});\n
\n
var jsc = now();\n
\n
jQuery.extend({\n
  \n
\tget: function( url, data, callback, type ) {\n
\t\t// shift arguments if data argument was ommited\n
\t\tif ( jQuery.isFunction( data ) ) {\n
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
\t\tif ( jQuery.isFunction( data ) ) {\n
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
\t\t*/\n
\t\t// Create the request object; Microsoft failed to properly\n
\t\t// implement the XMLHttpRequest in IE7, so we use the ActiveXObject when it is available\n
\t\t// This function can be overriden by calling jQuery.ajaxSetup\n
\t\txhr:function(){\n
\t\t\treturn window.ActiveXObject ? new ActiveXObject("Microsoft.XMLHTTP") : new XMLHttpRequest();\n
\t\t},\n
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
\n
\tajax: function( s ) {\n
\t\t// Extend the settings, but re-extend \'s\' so that it can be\n
\t\t// checked again later (in the test suite, specifically)\n
\t\ts = jQuery.extend(true, s, jQuery.extend(true, {}, jQuery.ajaxSettings, s));\n
\n
\t\tvar jsonp, jsre = /=\\?(&|$)/g, status, data,\n
\t\t\ttype = s.type.toUpperCase();\n
\n
\t\t// convert data if not already a string\n
\t\tif ( s.data && s.processData && typeof s.data !== "string" )\n
\t\t\ts.data = jQuery.param(s.data);\n
\n
\t\t// Handle JSONP Parameter Callbacks\n
\t\tif ( s.dataType == "jsonp" ) {\n
\t\t\tif ( type == "GET" ) {\n
\t\t\t\tif ( !s.url.match(jsre) )\n
\t\t\t\t\ts.url += (s.url.match(/\\?/) ? "&" : "?") + (s.jsonp || "callback") + "=?";\n
\t\t\t} else if ( !s.data || !s.data.match(jsre) )\n
\t\t\t\ts.data = (s.data ? s.data + "&" : "") + (s.jsonp || "callback") + "=?";\n
\t\t\ts.dataType = "json";\n
\t\t}\n
\n
\t\t// Build temporary JSONP function\n
\t\tif ( s.dataType == "json" && (s.data && s.data.match(jsre) || s.url.match(jsre)) ) {\n
\t\t\tjsonp = "jsonp" + jsc++;\n
\n
\t\t\t// Replace the =? sequence both in the query string and the data\n
\t\t\tif ( s.data )\n
\t\t\t\ts.data = (s.data + "").replace(jsre, "=" + jsonp + "$1");\n
\t\t\ts.url = s.url.replace(jsre, "=" + jsonp + "$1");\n
\n
\t\t\t// We need to make sure\n
\t\t\t// that a JSONP style response is executed properly\n
\t\t\ts.dataType = "script";\n
\n
\t\t\t// Handle JSONP-style loading\n
\t\t\twindow[ jsonp ] = function(tmp){\n
\t\t\t\tdata = tmp;\n
\t\t\t\tsuccess();\n
\t\t\t\tcomplete();\n
\t\t\t\t// Garbage collect\n
\t\t\t\twindow[ jsonp ] = undefined;\n
\t\t\t\ttry{ delete window[ jsonp ]; } catch(e){}\n
\t\t\t\tif ( head )\n
\t\t\t\t\thead.removeChild( script );\n
\t\t\t};\n
\t\t}\n
\n
\t\tif ( s.dataType == "script" && s.cache == null )\n
\t\t\ts.cache = false;\n
\n
\t\tif ( s.cache === false && type == "GET" ) {\n
\t\t\tvar ts = now();\n
\t\t\t// try replacing _= if it is there\n
\t\t\tvar ret = s.url.replace(/(\\?|&)_=.*?(&|$)/, "$1_=" + ts + "$2");\n
\t\t\t// if nothing was replaced, add timestamp to the end\n
\t\t\ts.url = ret + ((ret == s.url) ? (s.url.match(/\\?/) ? "&" : "?") + "_=" + ts : "");\n
\t\t}\n
\n
\t\t// If data is available, append data to url for get requests\n
\t\tif ( s.data && type == "GET" ) {\n
\t\t\ts.url += (s.url.match(/\\?/) ? "&" : "?") + s.data;\n
\n
\t\t\t// IE likes to send both get and post data, prevent this\n
\t\t\ts.data = null;\n
\t\t}\n
\n
\t\t// Watch for a new set of requests\n
\t\tif ( s.global && ! jQuery.active++ )\n
\t\t\tjQuery.event.trigger( "ajaxStart" );\n
\n
\t\t// Matches an absolute URL, and saves the domain\n
\t\tvar parts = /^(\\w+:)?\\/\\/([^\\/?#]+)/.exec( s.url );\n
\n
\t\t// If we\'re requesting a remote document\n
\t\t// and trying to load JSON or Script with a GET\n
\t\tif ( s.dataType == "script" && type == "GET" && parts\n
\t\t\t&& ( parts[1] && parts[1] != location.protocol || parts[2] != location.host )){\n
\n
\t\t\tvar head = document.getElementsByTagName("head")[0];\n
\t\t\tvar script = document.createElement("script");\n
\t\t\tscript.src = s.url;\n
\t\t\tif (s.scriptCharset)\n
\t\t\t\tscript.charset = s.scriptCharset;\n
\n
\t\t\t// Handle Script loading\n
\t\t\tif ( !jsonp ) {\n
\t\t\t\tvar done = false;\n
\n
\t\t\t\t// Attach handlers for all browsers\n
\t\t\t\tscript.onload = script.onreadystatechange = function(){\n
\t\t\t\t\tif ( !done && (!this.readyState ||\n
\t\t\t\t\t\t\tthis.readyState == "loaded" || this.readyState == "complete") ) {\n
\t\t\t\t\t\tdone = true;\n
\t\t\t\t\t\tsuccess();\n
\t\t\t\t\t\tcomplete();\n
\n
\t\t\t\t\t\t// Handle memory leak in IE\n
\t\t\t\t\t\tscript.onload = script.onreadystatechange = null;\n
\t\t\t\t\t\thead.removeChild( script );\n
\t\t\t\t\t}\n
\t\t\t\t};\n
\t\t\t}\n
\n
\t\t\thead.appendChild(script);\n
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
\t\t// Open the socket\n
\t\t// Passing null username, generates a login popup on Opera (#2865)\n
\t\tif( s.username )\n
\t\t\txhr.open(type, s.url, s.async, s.username, s.password);\n
\t\telse\n
\t\t\txhr.open(type, s.url, s.async);\n
\n
\t\t// Need an extra try/catch for cross domain requests in Firefox 3\n
\t\ttry {\n
\t\t\t// Set the correct header, if data is being sent\n
\t\t\tif ( s.data )\n
\t\t\t\txhr.setRequestHeader("Content-Type", s.contentType);\n
\n
\t\t\t// Set the If-Modified-Since header, if ifModified mode.\n
\t\t\tif ( s.ifModified )\n
\t\t\t\txhr.setRequestHeader("If-Modified-Since",\n
\t\t\t\t\tjQuery.lastModified[s.url] || "Thu, 01 Jan 1970 00:00:00 GMT" );\n
\n
\t\t\t// Set header so the called script knows that it\'s an XMLHttpRequest\n
\t\t\txhr.setRequestHeader("X-Requested-With", "XMLHttpRequest");\n
\n
\t\t\t// Set the Accepts header for the server, depending on the dataType\n
\t\t\txhr.setRequestHeader("Accept", s.dataType && s.accepts[ s.dataType ] ?\n
\t\t\t\ts.accepts[ s.dataType ] + ", */*" :\n
\t\t\t\ts.accepts._default );\n
\t\t} catch(e){}\n
\n
\t\t// Allow custom headers/mimetypes and early abort\n
\t\tif ( s.beforeSend && s.beforeSend(xhr, s) === false ) {\n
\t\t\t// Handle the global AJAX counter\n
\t\t\tif ( s.global && ! --jQuery.active )\n
\t\t\t\tjQuery.event.trigger( "ajaxStop" );\n
\t\t\t// close opended socket\n
\t\t\txhr.abort();\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\tif ( s.global )\n
\t\t\tjQuery.event.trigger("ajaxSend", [xhr, s]);\n
\n
\t\t// Wait for a response to come back\n
\t\tvar onreadystatechange = function(isTimeout){\n
\t\t\t// The request was aborted, clear the interval and decrement jQuery.active\n
\t\t\tif (xhr.readyState == 0) {\n
\t\t\t\tif (ival) {\n
\t\t\t\t\t// clear poll interval\n
\t\t\t\t\tclearInterval(ival);\n
\t\t\t\t\tival = null;\n
\t\t\t\t\t// Handle the global AJAX counter\n
\t\t\t\t\tif ( s.global && ! --jQuery.active )\n
\t\t\t\t\t\tjQuery.event.trigger( "ajaxStop" );\n
\t\t\t\t}\n
\t\t\t// The transfer is complete and the data is available, or the request timed out\n
\t\t\t} else if ( !requestDone && xhr && (xhr.readyState == 4 || isTimeout == "timeout") ) {\n
\t\t\t\trequestDone = true;\n
\n
\t\t\t\t// clear poll interval\n
\t\t\t\tif (ival) {\n
\t\t\t\t\tclearInterval(ival);\n
\t\t\t\t\tival = null;\n
\t\t\t\t}\n
\n
\t\t\t\tstatus = isTimeout == "timeout" ? "timeout" :\n
\t\t\t\t\t!jQuery.httpSuccess( xhr ) ? "error" :\n
\t\t\t\t\ts.ifModified && jQuery.httpNotModified( xhr, s.url ) ? "notmodified" :\n
\t\t\t\t\t"success";\n
\n
\t\t\t\tif ( status == "success" ) {\n
\t\t\t\t\t// Watch for, and catch, XML document parse errors\n
\t\t\t\t\ttry {\n
\t\t\t\t\t\t// process the data (runs the xml through httpData regardless of callback)\n
\t\t\t\t\t\tdata = jQuery.httpData( xhr, s.dataType, s );\n
\t\t\t\t\t} catch(e) {\n
\t\t\t\t\t\tstatus = "parsererror";\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\n
\t\t\t\t// Make sure that the request was successful or notmodified\n
\t\t\t\tif ( status == "success" ) {\n
\t\t\t\t\t// Cache Last-Modified header, if ifModified mode.\n
\t\t\t\t\tvar modRes;\n
\t\t\t\t\ttry {\n
\t\t\t\t\t\tmodRes = xhr.getResponseHeader("Last-Modified");\n
\t\t\t\t\t} catch(e) {} // swallow exception thrown by FF if header is not available\n
\n
\t\t\t\t\tif ( s.ifModified && modRes )\n
\t\t\t\t\t\tjQuery.lastModified[s.url] = modRes;\n
\n
\t\t\t\t\t// JSONP handles its own success callback\n
\t\t\t\t\tif ( !jsonp )\n
\t\t\t\t\t\tsuccess();\n
\t\t\t\t} else\n
\t\t\t\t\tjQuery.handleError(s, xhr, status);\n
\n
\t\t\t\t// Fire the complete handlers\n
\t\t\t\tcomplete();\n
\n
\t\t\t\tif ( isTimeout )\n
\t\t\t\t\txhr.abort();\n
\n
\t\t\t\t// Stop memory leaks\n
\t\t\t\tif ( s.async )\n
\t\t\t\t\txhr = null;\n
\t\t\t}\n
\t\t};\n
\n
\t\tif ( s.async ) {\n
\t\t\t// don\'t attach the handler to the request, just poll it instead\n
\t\t\tvar ival = setInterval(onreadystatechange, 13);\n
\n
\t\t\t// Timeout checker\n
\t\t\tif ( s.timeout > 0 )\n
\t\t\t\tsetTimeout(function(){\n
\t\t\t\t\t// Check to see if the request is still happening\n
\t\t\t\t\tif ( xhr && !requestDone )\n
\t\t\t\t\t\tonreadystatechange( "timeout" );\n
\t\t\t\t}, s.timeout);\n
\t\t}\n
\n
\t\t// Send the data\n
\t\ttry {\n
\t\t\txhr.send(s.data);\n
\t\t} catch(e) {\n
\t\t\tjQuery.handleError(s, xhr, null, e);\n
\t\t}\n
\n
\t\t// firefox 1.5 doesn\'t fire statechange for sync requests\n
\t\tif ( !s.async )\n
\t\t\tonreadystatechange();\n
\n
\t\tfunction success(){\n
\t\t\t// If a local callback was specified, fire it and pass it the data\n
\t\t\tif ( s.success )\n
\t\t\t\ts.success( data, status );\n
\n
\t\t\t// Fire the global callback\n
\t\t\tif ( s.global )\n
\t\t\t\tjQuery.event.trigger( "ajaxSuccess", [xhr, s] );\n
\t\t}\n
\n
\t\tfunction complete(){\n
\t\t\t// Process result\n
\t\t\tif ( s.complete )\n
\t\t\t\ts.complete(xhr, status);\n
\n
\t\t\t// The request was completed\n
\t\t\tif ( s.global )\n
\t\t\t\tjQuery.event.trigger( "ajaxComplete", [xhr, s] );\n
\n
\t\t\t// Handle the global AJAX counter\n
\t\t\tif ( s.global && ! --jQuery.active )\n
\t\t\t\tjQuery.event.trigger( "ajaxStop" );\n
\t\t}\n
\n
\t\t// return XMLHttpRequest to allow aborting the request etc.\n
\t\treturn xhr;\n
\t},\n
\n
\thandleError: function( s, xhr, status, e ) {\n
\t\t// If a local callback was specified, fire it\n
\t\tif ( s.error ) s.error( xhr, status, e );\n
\n
\t\t// Fire the global callback\n
\t\tif ( s.global )\n
\t\t\tjQuery.event.trigger( "ajaxError", [xhr, s, e] );\n
\t},\n
\n
\t// Counter for holding the number of active queries\n
\tactive: 0,\n
\n
\t// Determines if an XMLHttpRequest was successful or not\n
\thttpSuccess: function( xhr ) {\n
\t\ttry {\n
\t\t\t// IE error sometimes returns 1223 when it should be 204 so treat it as success, see #1450\n
\t\t\treturn !xhr.status && location.protocol == "file:" ||\n
\t\t\t\t( xhr.status >= 200 && xhr.status < 300 ) || xhr.status == 304 || xhr.status == 1223;\n
\t\t} catch(e){}\n
\t\treturn false;\n
\t},\n
\n
\t// Determines if an XMLHttpRequest returns NotModified\n
\thttpNotModified: function( xhr, url ) {\n
\t\ttry {\n
\t\t\tvar xhrRes = xhr.getResponseHeader("Last-Modified");\n
\n
\t\t\t// Firefox always returns 200. check Last-Modified date\n
\t\t\treturn xhr.status == 304 || xhrRes == jQuery.lastModified[url];\n
\t\t} catch(e){}\n
\t\treturn false;\n
\t},\n
\n
\thttpData: function( xhr, type, s ) {\n
\t\tvar ct = xhr.getResponseHeader("content-type"),\n
\t\t\txml = type == "xml" || !type && ct && ct.indexOf("xml") >= 0,\n
\t\t\tdata = xml ? xhr.responseXML : xhr.responseText;\n
\n
\t\tif ( xml && data.documentElement.tagName == "parsererror" )\n
\t\t\tthrow "parsererror";\n
\t\t\t\n
\t\t// Allow a pre-filtering function to sanitize the response\n
\t\t// s != null is checked to keep backwards compatibility\n
\t\tif( s && s.dataFilter )\n
\t\t\tdata = s.dataFilter( data, type );\n
\n
\t\t// The filter can actually parse the response\n
\t\tif( typeof data === "string" ){\n
\n
\t\t\t// If the type is "script", eval it in global context\n
\t\t\tif ( type == "script" )\n
\t\t\t\tjQuery.globalEval( data );\n
\n
\t\t\t// Get the JavaScript object, if JSON is used.\n
\t\t\tif ( type == "json" )\n
\t\t\t\tdata = window["eval"]("(" + data + ")");\n
\t\t}\n
\t\t\n
\t\treturn data;\n
\t},\n
\n
\t// Serialize an array of form elements or a set of\n
\t// key/values into a query string\n
\tparam: function( a ) {\n
\t\tvar s = [ ];\n
\n
\t\tfunction add( key, value ){\n
\t\t\ts[ s.length ] = encodeURIComponent(key) + \'=\' + encodeURIComponent(value);\n
\t\t};\n
\n
\t\t// If an array was passed in, assume that it is an array\n
\t\t// of form elements\n
\t\tif ( jQuery.isArray(a) || a.jquery )\n
\t\t\t// Serialize the form elements\n
\t\t\tjQuery.each( a, function(){\n
\t\t\t\tadd( this.name, this.value );\n
\t\t\t});\n
\n
\t\t// Otherwise, assume that it\'s an object of key/value pairs\n
\t\telse\n
\t\t\t// Serialize the key/values\n
\t\t\tfor ( var j in a )\n
\t\t\t\t// If the value is an array then the key names need to be repeated\n
\t\t\t\tif ( jQuery.isArray(a[j]) )\n
\t\t\t\t\tjQuery.each( a[j], function(){\n
\t\t\t\t\t\tadd( j, this );\n
\t\t\t\t\t});\n
\t\t\t\telse\n
\t\t\t\t\tadd( j, jQuery.isFunction(a[j]) ? a[j]() : a[j] );\n
\n
\t\t// Return the resulting serialization\n
\t\treturn s.join("&").replace(/%20/g, "+");\n
\t}\n
\n
});\n
var elemdisplay = {},\n
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
function genFx( type, num ){\n
\tvar obj = {};\n
\tjQuery.each( fxAttrs.concat.apply([], fxAttrs.slice(0,num)), function(){\n
\t\tobj[ this ] = type;\n
\t});\n
\treturn obj;\n
}\n
\n
jQuery.fn.extend({\n
\tshow: function(speed,callback){\n
\t\tif ( speed ) {\n
\t\t\treturn this.animate( genFx("show", 3), speed, callback);\n
\t\t} else {\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ){\n
\t\t\t\tvar old = jQuery.data(this[i], "olddisplay");\n
\t\t\t\t\n
\t\t\t\tthis[i].style.display = old || "";\n
\t\t\t\t\n
\t\t\t\tif ( jQuery.css(this[i], "display") === "none" ) {\n
\t\t\t\t\tvar tagName = this[i].tagName, display;\n
\t\t\t\t\t\n
\t\t\t\t\tif ( elemdisplay[ tagName ] ) {\n
\t\t\t\t\t\tdisplay = elemdisplay[ tagName ];\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tvar elem = jQuery("<" + tagName + " />").appendTo("body");\n
\t\t\t\t\t\t\n
\t\t\t\t\t\tdisplay = elem.css("display");\n
\t\t\t\t\t\tif ( display === "none" )\n
\t\t\t\t\t\t\tdisplay = "block";\n
\t\t\t\t\t\t\n
\t\t\t\t\t\telem.remove();\n
\t\t\t\t\t\t\n
\t\t\t\t\t\telemdisplay[ tagName ] = display;\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tjQuery.data(this[i], "olddisplay", display);\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\t// Set the display of the elements in a second loop\n
\t\t\t// to avoid the constant reflow\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ){\n
\t\t\t\tthis[i].style.display = jQuery.data(this[i], "olddisplay") || "";\n
\t\t\t}\n
\t\t\t\n
\t\t\treturn this;\n
\t\t}\n
\t},\n
\n
\thide: function(speed,callback){\n
\t\tif ( speed ) {\n
\t\t\treturn this.animate( genFx("hide", 3), speed, callback);\n
\t\t} else {\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ){\n
\t\t\t\tvar old = jQuery.data(this[i], "olddisplay");\n
\t\t\t\tif ( !old && old !== "none" )\n
\t\t\t\t\tjQuery.data(this[i], "olddisplay", jQuery.css(this[i], "display"));\n
\t\t\t}\n
\n
\t\t\t// Set the display of the elements in a second loop\n
\t\t\t// to avoid the constant reflow\n
\t\t\tfor ( var i = 0, l = this.length; i < l; i++ ){\n
\t\t\t\tthis[i].style.display = "none";\n
\t\t\t}\n
\n
\t\t\treturn this;\n
\t\t}\n
\t},\n
\n
\t// Save the old toggle function\n
\t_toggle: jQuery.fn.toggle,\n
\n
\ttoggle: function( fn, fn2 ){\n
\t\tvar bool = typeof fn === "boolean";\n
\n
\t\treturn jQuery.isFunction(fn) && jQuery.isFunction(fn2) ?\n
\t\t\tthis._toggle.apply( this, arguments ) :\n
\t\t\tfn == null || bool ?\n
\t\t\t\tthis.each(function(){\n
\t\t\t\t\tvar state = bool ? fn : jQuery(this).is(":hidden");\n
\t\t\t\t\tjQuery(this)[ state ? "show" : "hide" ]();\n
\t\t\t\t}) :\n
\t\t\t\tthis.animate(genFx("toggle", 3), fn, fn2);\n
\t},\n
\n
\tfadeTo: function(speed,to,callback){\n
\t\treturn this.animate({opacity: to}, speed, callback);\n
\t},\n
\n
\tanimate: function( prop, speed, easing, callback ) {\n
\t\tvar optall = jQuery.speed(speed, easing, callback);\n
\n
\t\treturn this[ optall.queue === false ? "each" : "queue" ](function(){\n
\t\t\n
\t\t\tvar opt = jQuery.extend({}, optall), p,\n
\t\t\t\thidden = this.nodeType == 1 && jQuery(this).is(":hidden"),\n
\t\t\t\tself = this;\n
\t\n
\t\t\tfor ( p in prop ) {\n
\t\t\t\tif ( prop[p] == "hide" && hidden || prop[p] == "show" && !hidden )\n
\t\t\t\t\treturn opt.complete.call(this);\n
\n
\t\t\t\tif ( ( p == "height" || p == "width" ) && this.style ) {\n
\t\t\t\t\t// Store display property\n
\t\t\t\t\topt.display = jQuery.css(this, "display");\n
\n
\t\t\t\t\t// Make sure that nothing sneaks out\n
\t\t\t\t\topt.overflow = this.style.overflow;\n
\t\t\t\t}\n
\t\t\t}\n
\n
\t\t\tif ( opt.overflow != null )\n
\t\t\t\tthis.style.overflow = "hidden";\n
\n
\t\t\topt.curAnim = jQuery.extend({}, prop);\n
\n
\t\t\tjQuery.each( prop, function(name, val){\n
\t\t\t\tvar e = new jQuery.fx( self, opt, name );\n
\n
\t\t\t\tif ( /toggle|show|hide/.test(val) )\n
\t\t\t\t\te[ val == "toggle" ? hidden ? "show" : "hide" : val ]( prop );\n
\t\t\t\telse {\n
\t\t\t\t\tvar parts = val.toString().match(/^([+-]=)?([\\d+-.]+)(.*)$/),\n
\t\t\t\t\t\tstart = e.cur(true) || 0;\n
\n
\t\t\t\t\tif ( parts ) {\n
\t\t\t\t\t\tvar end = parseFloat(parts[2]),\n
\t\t\t\t\t\t\tunit = parts[3] || "px";\n
\n
\t\t\t\t\t\t// We need to compute starting value\n
\t\t\t\t\t\tif ( unit != "px" ) {\n
\t\t\t\t\t\t\tself.style[ name ] = (end || 1) + unit;\n
\t\t\t\t\t\t\tstart = ((end || 1) / e.cur(true)) * start;\n
\t\t\t\t\t\t\tself.style[ name ] = start + unit;\n
\t\t\t\t\t\t}\n
\n
\t\t\t\t\t\t// If a +=/-= token was provided, we\'re doing a relative animation\n
\t\t\t\t\t\tif ( parts[1] )\n
\t\t\t\t\t\t\tend = ((parts[1] == "-=" ? -1 : 1) * end) + start;\n
\n
\t\t\t\t\t\te.custom( start, end, unit );\n
\t\t\t\t\t} else\n
\t\t\t\t\t\te.custom( start, val, "" );\n
\t\t\t\t}\n
\t\t\t});\n
\n
\t\t\t// For JS strict compliance\n
\t\t\treturn true;\n
\t\t});\n
\t},\n
\n
\tstop: function(clearQueue, gotoEnd){\n
\t\tvar timers = jQuery.timers;\n
\n
\t\tif (clearQueue)\n
\t\t\tthis.queue([]);\n
\n
\t\tthis.each(function(){\n
\t\t\t// go in reverse order so anything added to the queue during the loop is ignored\n
\t\t\tfor ( var i = timers.length - 1; i >= 0; i-- )\n
\t\t\t\tif ( timers[i].elem == this ) {\n
\t\t\t\t\tif (gotoEnd)\n
\t\t\t\t\t\t// force the next step to be the last\n
\t\t\t\t\t\ttimers[i](true);\n
\t\t\t\t\ttimers.splice(i, 1);\n
\t\t\t\t}\n
\t\t});\n
\n
\t\t// start the next in the queue if the last step wasn\'t forced\n
\t\tif (!gotoEnd)\n
\t\t\tthis.dequeue();\n
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
}, function( name, props ){\n
\tjQuery.fn[ name ] = function( speed, callback ){\n
\t\treturn this.animate( props, speed, callback );\n
\t};\n
});\n
\n
jQuery.extend({\n
\n
\tspeed: function(speed, easing, fn) {\n
\t\tvar opt = typeof speed === "object" ? speed : {\n
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
\t\topt.complete = function(){\n
\t\t\tif ( opt.queue !== false )\n
\t\t\t\tjQuery(this).dequeue();\n
\t\t\tif ( jQuery.isFunction( opt.old ) )\n
\t\t\t\topt.old.call( this );\n
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
\tfx: function( elem, options, prop ){\n
\t\tthis.options = options;\n
\t\tthis.elem = elem;\n
\t\tthis.prop = prop;\n
\n
\t\tif ( !options.orig )\n
\t\t\toptions.orig = {};\n
\t}\n
\n
});\n
\n
jQuery.fx.prototype = {\n
\n
\t// Simple function for setting a style value\n
\tupdate: function(){\n
\t\tif ( this.options.step )\n
\t\t\tthis.options.step.call( this.elem, this.now, this );\n
\n
\t\t(jQuery.fx.step[this.prop] || jQuery.fx.step._default)( this );\n
\n
\t\t// Set display property to block for height/width animations\n
\t\tif ( ( this.prop == "height" || this.prop == "width" ) && this.elem.style )\n
\t\t\tthis.elem.style.display = "block";\n
\t},\n
\n
\t// Get the current size\n
\tcur: function(force){\n
\t\tif ( this.elem[this.prop] != null && (!this.elem.style || this.elem.style[this.prop] == null) )\n
\t\t\treturn this.elem[ this.prop ];\n
\n
\t\tvar r = parseFloat(jQuery.css(this.elem, this.prop, force));\n
\t\treturn r && r > -10000 ? r : parseFloat(jQuery.curCSS(this.elem, this.prop)) || 0;\n
\t},\n
\n
\t// Start an animation from one number to another\n
\tcustom: function(from, to, unit){\n
\t\tthis.startTime = now();\n
\t\tthis.start = from;\n
\t\tthis.end = to;\n
\t\tthis.unit = unit || this.unit || "px";\n
\t\tthis.now = this.start;\n
\t\tthis.pos = this.state = 0;\n
\n
\t\tvar self = this;\n
\t\tfunction t(gotoEnd){\n
\t\t\treturn self.step(gotoEnd);\n
\t\t}\n
\n
\t\tt.elem = this.elem;\n
\n
\t\tif ( t() && jQuery.timers.push(t) && !timerId ) {\n
\t\t\ttimerId = setInterval(function(){\n
\t\t\t\tvar timers = jQuery.timers;\n
\n
\t\t\t\tfor ( var i = 0; i < timers.length; i++ )\n
\t\t\t\t\tif ( !timers[i]() )\n
\t\t\t\t\t\ttimers.splice(i--, 1);\n
\n
\t\t\t\tif ( !timers.length ) {\n
\t\t\t\t\tclearInterval( timerId );\n
\t\t\t\t\ttimerId = undefined;\n
\t\t\t\t}\n
\t\t\t}, 13);\n
\t\t}\n
\t},\n
\n
\t// Simple \'show\' function\n
\tshow: function(){\n
\t\t// Remember where we started, so that we can go back to it later\n
\t\tthis.options.orig[this.prop] = jQuery.attr( this.elem.style, this.prop );\n
\t\tthis.options.show = true;\n
\n
\t\t// Begin the animation\n
\t\t// Make sure that we start at a small width/height to avoid any\n
\t\t// flash of content\n
\t\tthis.custom(this.prop == "width" || this.prop == "height" ? 1 : 0, this.cur());\n
\n
\t\t// Start by showing the element\n
\t\tjQuery(this.elem).show();\n
\t},\n
\n
\t// Simple \'hide\' function\n
\thide: function(){\n
\t\t// Remember where we started, so that we can go back to it later\n
\t\tthis.options.orig[this.prop] = jQuery.attr( this.elem.style, this.prop );\n
\t\tthis.options.hide = true;\n
\n
\t\t// Begin the animation\n
\t\tthis.custom(this.cur(), 0);\n
\t},\n
\n
\t// Each step of an animation\n
\tstep: function(gotoEnd){\n
\t\tvar t = now();\n
\n
\t\tif ( gotoEnd || t >= this.options.duration + this.startTime ) {\n
\t\t\tthis.now = this.end;\n
\t\t\tthis.pos = this.state = 1;\n
\t\t\tthis.update();\n
\n
\t\t\tthis.options.curAnim[ this.prop ] = true;\n
\n
\t\t\tvar done = true;\n
\t\t\tfor ( var i in this.options.curAnim )\n
\t\t\t\tif ( this.options.curAnim[i] !== true )\n
\t\t\t\t\tdone = false;\n
\n
\t\t\tif ( done ) {\n
\t\t\t\tif ( this.options.display != null ) {\n
\t\t\t\t\t// Reset the overflow\n
\t\t\t\t\tthis.elem.style.overflow = this.options.overflow;\n
\n
\t\t\t\t\t// Reset the display\n
\t\t\t\t\tthis.elem.style.display = this.options.display;\n
\t\t\t\t\tif ( jQuery.css(this.elem, "display") == "none" )\n
\t\t\t\t\t\tthis.elem.style.display = "block";\n
\t\t\t\t}\n
\n
\t\t\t\t// Hide the element if the "hide" operation was done\n
\t\t\t\tif ( this.options.hide )\n
\t\t\t\t\tjQuery(this.elem).hide();\n
\n
\t\t\t\t// Reset the properties, if the item has been hidden or shown\n
\t\t\t\tif ( this.options.hide || this.options.show )\n
\t\t\t\t\tfor ( var p in this.options.curAnim )\n
\t\t\t\t\t\tjQuery.attr(this.elem.style, p, this.options.orig[p]);\n
\t\t\t\t\t\n
\t\t\t\t// Execute the complete function\n
\t\t\t\tthis.options.complete.call( this.elem );\n
\t\t\t}\n
\n
\t\t\treturn false;\n
\t\t} else {\n
\t\t\tvar n = t - this.startTime;\n
\t\t\tthis.state = n / this.options.duration;\n
\n
\t\t\t// Perform the easing function, defaults to swing\n
\t\t\tthis.pos = jQuery.easing[this.options.easing || (jQuery.easing.swing ? "swing" : "linear")](this.state, n, 0, 1, this.options.duration);\n
\t\t\tthis.now = this.start + ((this.end - this.start) * this.pos);\n
\n
\t\t\t// Perform the next step of the animation\n
\t\t\tthis.update();\n
\t\t}\n
\n
\t\treturn true;\n
\t}\n
\n
};\n
\n
jQuery.extend( jQuery.fx, {\n
\tspeeds:{\n
\t\tslow: 600,\n
 \t\tfast: 200,\n
 \t\t// Default speed\n
 \t\t_default: 400\n
\t},\n
\tstep: {\n
\n
\t\topacity: function(fx){\n
\t\t\tjQuery.attr(fx.elem.style, "opacity", fx.now);\n
\t\t},\n
\n
\t\t_default: function(fx){\n
\t\t\tif ( fx.elem.style && fx.elem.style[ fx.prop ] != null )\n
\t\t\t\tfx.elem.style[ fx.prop ] = fx.now + fx.unit;\n
\t\t\telse\n
\t\t\t\tfx.elem[ fx.prop ] = fx.now;\n
\t\t}\n
\t}\n
});\n
if ( document.documentElement["getBoundingClientRect"] )\n
\tjQuery.fn.offset = function() {\n
\t\tif ( !this[0] ) return { top: 0, left: 0 };\n
\t\tif ( this[0] === this[0].ownerDocument.body ) return jQuery.offset.bodyOffset( this[0] );\n
\t\tvar box  = this[0].getBoundingClientRect(), doc = this[0].ownerDocument, body = doc.body, docElem = doc.documentElement,\n
\t\t\tclientTop = docElem.clientTop || body.clientTop || 0, clientLeft = docElem.clientLeft || body.clientLeft || 0,\n
\t\t\ttop  = box.top  + (self.pageYOffset || jQuery.boxModel && docElem.scrollTop  || body.scrollTop ) - clientTop,\n
\t\t\tleft = box.left + (self.pageXOffset || jQuery.boxModel && docElem.scrollLeft || body.scrollLeft) - clientLeft;\n
\t\treturn { top: top, left: left };\n
\t};\n
else \n
\tjQuery.fn.offset = function() {\n
\t\tif ( !this[0] ) return { top: 0, left: 0 };\n
\t\tif ( this[0] === this[0].ownerDocument.body ) return jQuery.offset.bodyOffset( this[0] );\n
\t\tjQuery.offset.initialized || jQuery.offset.initialize();\n
\n
\t\tvar elem = this[0], offsetParent = elem.offsetParent, prevOffsetParent = elem,\n
\t\t\tdoc = elem.ownerDocument, computedStyle, docElem = doc.documentElement,\n
\t\t\tbody = doc.body, defaultView = doc.defaultView,\n
\t\t\tprevComputedStyle = defaultView.getComputedStyle(elem, null),\n
\t\t\ttop = elem.offsetTop, left = elem.offsetLeft;\n
\n
\t\twhile ( (elem = elem.parentNode) && elem !== body && elem !== docElem ) {\n
\t\t\tcomputedStyle = defaultView.getComputedStyle(elem, null);\n
\t\t\ttop -= elem.scrollTop, left -= elem.scrollLeft;\n
\t\t\tif ( elem === offsetParent ) {\n
\t\t\t\ttop += elem.offsetTop, left += elem.offsetLeft;\n
\t\t\t\tif ( jQuery.offset.doesNotAddBorder && !(jQuery.offset.doesAddBorderForTableAndCells && /^t(able|d|h)$/i.test(elem.tagName)) )\n
\t\t\t\t\ttop  += parseInt( computedStyle.borderTopWidth,  10) || 0,\n
\t\t\t\t\tleft += parseInt( computedStyle.borderLeftWidth, 10) || 0;\n
\t\t\t\tprevOffsetParent = offsetParent, offsetParent = elem.offsetParent;\n
\t\t\t}\n
\t\t\tif ( jQuery.offset.subtractsBorderForOverflowNotVisible && computedStyle.overflow !== "visible" )\n
\t\t\t\ttop  += parseInt( computedStyle.borderTopWidth,  10) || 0,\n
\t\t\t\tleft += parseInt( computedStyle.borderLeftWidth, 10) || 0;\n
\t\t\tprevComputedStyle = computedStyle;\n
\t\t}\n
\n
\t\tif ( prevComputedStyle.position === "relative" || prevComputedStyle.position === "static" )\n
\t\t\ttop  += body.offsetTop,\n
\t\t\tleft += body.offsetLeft;\n
\n
\t\tif ( prevComputedStyle.position === "fixed" )\n
\t\t\ttop  += Math.max(docElem.scrollTop, body.scrollTop),\n
\t\t\tleft += Math.max(docElem.scrollLeft, body.scrollLeft);\n
\n
\t\treturn { top: top, left: left };\n
\t};\n
\n
jQuery.offset = {\n
\tinitialize: function() {\n
\t\tif ( this.initialized ) return;\n
\t\tvar body = document.body, container = document.createElement(\'div\'), innerDiv, checkDiv, table, td, rules, prop, bodyMarginTop = body.style.marginTop,\n
\t\t\thtml = \'<div style="position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;"><div></div></div><table style="position:absolute;top:0;left:0;margin:0;border:5px solid #000;padding:0;width:1px;height:1px;" cellpadding="0" cellspacing="0"><tr><td></td></tr></table>\';\n
\n
\t\trules = { position: \'absolute\', top: 0, left: 0, margin: 0, border: 0, width: \'1px\', height: \'1px\', visibility: \'hidden\' };\n
\t\tfor ( prop in rules ) container.style[prop] = rules[prop];\n
\n
\t\tcontainer.innerHTML = html;\n
\t\tbody.insertBefore(container, body.firstChild);\n
\t\tinnerDiv = container.firstChild, checkDiv = innerDiv.firstChild, td = innerDiv.nextSibling.firstChild.firstChild;\n
\n
\t\tthis.doesNotAddBorder = (checkDiv.offsetTop !== 5);\n
\t\tthis.doesAddBorderForTableAndCells = (td.offsetTop === 5);\n
\n
\t\tinnerDiv.style.overflow = \'hidden\', innerDiv.style.position = \'relative\';\n
\t\tthis.subtractsBorderForOverflowNotVisible = (checkDiv.offsetTop === -5);\n
\n
\t\tbody.style.marginTop = \'1px\';\n
\t\tthis.doesNotIncludeMarginInBodyOffset = (body.offsetTop === 0);\n
\t\tbody.style.marginTop = bodyMarginTop;\n
\n
\t\tbody.removeChild(container);\n
\t\tthis.initialized = true;\n
\t},\n
\n
\tbodyOffset: function(body) {\n
\t\tjQuery.offset.initialized || jQuery.offset.initialize();\n
\t\tvar top = body.offsetTop, left = body.offsetLeft;\n
\t\tif ( jQuery.offset.doesNotIncludeMarginInBodyOffset )\n
\t\t\ttop  += parseInt( jQuery.curCSS(body, \'marginTop\',  true), 10 ) || 0,\n
\t\t\tleft += parseInt( jQuery.curCSS(body, \'marginLeft\', true), 10 ) || 0;\n
\t\treturn { top: top, left: left };\n
\t}\n
};\n
\n
\n
jQuery.fn.extend({\n
\tposition: function() {\n
\t\tvar left = 0, top = 0, results;\n
\n
\t\tif ( this[0] ) {\n
\t\t\t// Get *real* offsetParent\n
\t\t\tvar offsetParent = this.offsetParent(),\n
\n
\t\t\t// Get correct offsets\n
\t\t\toffset       = this.offset(),\n
\t\t\tparentOffset = /^body|html$/i.test(offsetParent[0].tagName) ? { top: 0, left: 0 } : offsetParent.offset();\n
\n
\t\t\t// Subtract element margins\n
\t\t\t// note: when an element has margin: auto the offsetLeft and marginLeft \n
\t\t\t// are the same in Safari causing offset.left to incorrectly be 0\n
\t\t\toffset.top  -= num( this, \'marginTop\'  );\n
\t\t\toffset.left -= num( this, \'marginLeft\' );\n
\n
\t\t\t// Add offsetParent borders\n
\t\t\tparentOffset.top  += num( offsetParent, \'borderTopWidth\'  );\n
\t\t\tparentOffset.left += num( offsetParent, \'borderLeftWidth\' );\n
\n
\t\t\t// Subtract the two offsets\n
\t\t\tresults = {\n
\t\t\t\ttop:  offset.top  - parentOffset.top,\n
\t\t\t\tleft: offset.left - parentOffset.left\n
\t\t\t};\n
\t\t}\n
\n
\t\treturn results;\n
\t},\n
\n
\toffsetParent: function() {\n
\t\tvar offsetParent = this[0].offsetParent || document.body;\n
\t\twhile ( offsetParent && (!/^body|html$/i.test(offsetParent.tagName) && jQuery.css(offsetParent, \'position\') == \'static\') )\n
\t\t\toffsetParent = offsetParent.offsetParent;\n
\t\treturn jQuery(offsetParent);\n
\t}\n
});\n
\n
\n
// Create scrollLeft and scrollTop methods\n
jQuery.each( [\'Left\', \'Top\'], function(i, name) {\n
\tvar method = \'scroll\' + name;\n
\t\n
\tjQuery.fn[ method ] = function(val) {\n
\t\tif (!this[0]) return null;\n
\n
\t\treturn val !== undefined ?\n
\n
\t\t\t// Set the scroll offset\n
\t\t\tthis.each(function() {\n
\t\t\t\tthis == window || this == document ?\n
\t\t\t\t\twindow.scrollTo(\n
\t\t\t\t\t\t!i ? val : jQuery(window).scrollLeft(),\n
\t\t\t\t\t\t i ? val : jQuery(window).scrollTop()\n
\t\t\t\t\t) :\n
\t\t\t\t\tthis[ method ] = val;\n
\t\t\t}) :\n
\n
\t\t\t// Return the scroll offset\n
\t\t\tthis[0] == window || this[0] == document ?\n
\t\t\t\tself[ i ? \'pageYOffset\' : \'pageXOffset\' ] ||\n
\t\t\t\t\tjQuery.boxModel && document.documentElement[ method ] ||\n
\t\t\t\t\tdocument.body[ method ] :\n
\t\t\t\tthis[0][ method ];\n
\t};\n
});\n
// Create innerHeight, innerWidth, outerHeight and outerWidth methods\n
jQuery.each([ "Height", "Width" ], function(i, name){\n
\n
\tvar tl = i ? "Left"  : "Top",  // top or left\n
\t\tbr = i ? "Right" : "Bottom", // bottom or right\n
\t\tlower = name.toLowerCase();\n
\n
\t// innerHeight and innerWidth\n
\tjQuery.fn["inner" + name] = function(){\n
\t\treturn this[0] ?\n
\t\t\tjQuery.css( this[0], lower, false, "padding" ) :\n
\t\t\tnull;\n
\t};\n
\n
\t// outerHeight and outerWidth\n
\tjQuery.fn["outer" + name] = function(margin) {\n
\t\treturn this[0] ?\n
\t\t\tjQuery.css( this[0], lower, false, margin ? "margin" : "border" ) :\n
\t\t\tnull;\n
\t};\n
\t\n
\tvar type = name.toLowerCase();\n
\n
\tjQuery.fn[ type ] = function( size ) {\n
\t\t// Get window width or height\n
\t\treturn this[0] == window ?\n
\t\t\t// Everyone else use document.documentElement or document.body depending on Quirks vs Standards mode\n
\t\t\tdocument.compatMode == "CSS1Compat" && document.documentElement[ "client" + name ] ||\n
\t\t\tdocument.body[ "client" + name ] :\n
\n
\t\t\t// Get document width or height\n
\t\t\tthis[0] == document ?\n
\t\t\t\t// Either scroll[Width/Height] or offset[Width/Height], whichever is greater\n
\t\t\t\tMath.max(\n
\t\t\t\t\tdocument.documentElement["client" + name],\n
\t\t\t\t\tdocument.body["scroll" + name], document.documentElement["scroll" + name],\n
\t\t\t\t\tdocument.body["offset" + name], document.documentElement["offset" + name]\n
\t\t\t\t) :\n
\n
\t\t\t\t// Get or set width or height on the element\n
\t\t\t\tsize === undefined ?\n
\t\t\t\t\t// Get width or height on the element\n
\t\t\t\t\t(this.length ? jQuery.css( this[0], type ) : null) :\n
\n
\t\t\t\t\t// Set the width or height on the element (default to pixels if value is unitless)\n
\t\t\t\t\tthis.css( type, typeof size === "string" ? size : size + "px" );\n
\t};\n
\n
});\n
})();\n


]]></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
