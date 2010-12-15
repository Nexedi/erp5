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
            <value> <string>ts77895656.24</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.slider.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Slider 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Slider\n
 *\n
 * Depends:\n
 *\tjquery.ui.core.js\n
 *\tjquery.ui.mouse.js\n
 *\tjquery.ui.widget.js\n
 */\n
\n
(function( $ ) {\n
\n
// number of pages in a slider\n
// (how many times can you page up/down to go through the whole range)\n
var numPages = 5;\n
\n
$.widget( "ui.slider", $.ui.mouse, {\n
\n
\twidgetEventPrefix: "slide",\n
\n
\toptions: {\n
\t\tanimate: false,\n
\t\tdistance: 0,\n
\t\tmax: 100,\n
\t\tmin: 0,\n
\t\torientation: "horizontal",\n
\t\trange: false,\n
\t\tstep: 1,\n
\t\tvalue: 0,\n
\t\tvalues: null\n
\t},\n
\n
\t_create: function() {\n
\t\tvar self = this,\n
\t\t\to = this.options;\n
\n
\t\tthis._keySliding = false;\n
\t\tthis._mouseSliding = false;\n
\t\tthis._animateOff = true;\n
\t\tthis._handleIndex = null;\n
\t\tthis._detectOrientation();\n
\t\tthis._mouseInit();\n
\n
\t\tthis.element\n
\t\t\t.addClass( "ui-slider" +\n
\t\t\t\t" ui-slider-" + this.orientation +\n
\t\t\t\t" ui-widget" +\n
\t\t\t\t" ui-widget-content" +\n
\t\t\t\t" ui-corner-all" );\n
\t\t\n
\t\tif ( o.disabled ) {\n
\t\t\tthis.element.addClass( "ui-slider-disabled ui-disabled" );\n
\t\t}\n
\n
\t\tthis.range = $([]);\n
\n
\t\tif ( o.range ) {\n
\t\t\tif ( o.range === true ) {\n
\t\t\t\tthis.range = $( "<div></div>" );\n
\t\t\t\tif ( !o.values ) {\n
\t\t\t\t\to.values = [ this._valueMin(), this._valueMin() ];\n
\t\t\t\t}\n
\t\t\t\tif ( o.values.length && o.values.length !== 2 ) {\n
\t\t\t\t\to.values = [ o.values[0], o.values[0] ];\n
\t\t\t\t}\n
\t\t\t} else {\n
\t\t\t\tthis.range = $( "<div></div>" );\n
\t\t\t}\n
\n
\t\t\tthis.range\n
\t\t\t\t.appendTo( this.element )\n
\t\t\t\t.addClass( "ui-slider-range" );\n
\n
\t\t\tif ( o.range === "min" || o.range === "max" ) {\n
\t\t\t\tthis.range.addClass( "ui-slider-range-" + o.range );\n
\t\t\t}\n
\n
\t\t\t// note: this isn\'t the most fittingly semantic framework class for this element,\n
\t\t\t// but worked best visually with a variety of themes\n
\t\t\tthis.range.addClass( "ui-widget-header" );\n
\t\t}\n
\n
\t\tif ( $( ".ui-slider-handle", this.element ).length === 0 ) {\n
\t\t\t$( "<a href=\'#\'></a>" )\n
\t\t\t\t.appendTo( this.element )\n
\t\t\t\t.addClass( "ui-slider-handle" );\n
\t\t}\n
\n
\t\tif ( o.values && o.values.length ) {\n
\t\t\twhile ( $(".ui-slider-handle", this.element).length < o.values.length ) {\n
\t\t\t\t$( "<a href=\'#\'></a>" )\n
\t\t\t\t\t.appendTo( this.element )\n
\t\t\t\t\t.addClass( "ui-slider-handle" );\n
\t\t\t}\n
\t\t}\n
\n
\t\tthis.handles = $( ".ui-slider-handle", this.element )\n
\t\t\t.addClass( "ui-state-default" +\n
\t\t\t\t" ui-corner-all" );\n
\n
\t\tthis.handle = this.handles.eq( 0 );\n
\n
\t\tthis.handles.add( this.range ).filter( "a" )\n
\t\t\t.click(function( event ) {\n
\t\t\t\tevent.preventDefault();\n
\t\t\t})\n
\t\t\t.hover(function() {\n
\t\t\t\tif ( !o.disabled ) {\n
\t\t\t\t\t$( this ).addClass( "ui-state-hover" );\n
\t\t\t\t}\n
\t\t\t}, function() {\n
\t\t\t\t$( this ).removeClass( "ui-state-hover" );\n
\t\t\t})\n
\t\t\t.focus(function() {\n
\t\t\t\tif ( !o.disabled ) {\n
\t\t\t\t\t$( ".ui-slider .ui-state-focus" ).removeClass( "ui-state-focus" );\n
\t\t\t\t\t$( this ).addClass( "ui-state-focus" );\n
\t\t\t\t} else {\n
\t\t\t\t\t$( this ).blur();\n
\t\t\t\t}\n
\t\t\t})\n
\t\t\t.blur(function() {\n
\t\t\t\t$( this ).removeClass( "ui-state-focus" );\n
\t\t\t});\n
\n
\t\tthis.handles.each(function( i ) {\n
\t\t\t$( this ).data( "index.ui-slider-handle", i );\n
\t\t});\n
\n
\t\tthis.handles\n
\t\t\t.keydown(function( event ) {\n
\t\t\t\tvar ret = true,\n
\t\t\t\t\tindex = $( this ).data( "index.ui-slider-handle" ),\n
\t\t\t\t\tallowed,\n
\t\t\t\t\tcurVal,\n
\t\t\t\t\tnewVal,\n
\t\t\t\t\tstep;\n
\t\n
\t\t\t\tif ( self.options.disabled ) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\t\n
\t\t\t\tswitch ( event.keyCode ) {\n
\t\t\t\t\tcase $.ui.keyCode.HOME:\n
\t\t\t\t\tcase $.ui.keyCode.END:\n
\t\t\t\t\tcase $.ui.keyCode.PAGE_UP:\n
\t\t\t\t\tcase $.ui.keyCode.PAGE_DOWN:\n
\t\t\t\t\tcase $.ui.keyCode.UP:\n
\t\t\t\t\tcase $.ui.keyCode.RIGHT:\n
\t\t\t\t\tcase $.ui.keyCode.DOWN:\n
\t\t\t\t\tcase $.ui.keyCode.LEFT:\n
\t\t\t\t\t\tret = false;\n
\t\t\t\t\t\tif ( !self._keySliding ) {\n
\t\t\t\t\t\t\tself._keySliding = true;\n
\t\t\t\t\t\t\t$( this ).addClass( "ui-state-active" );\n
\t\t\t\t\t\t\tallowed = self._start( event, index );\n
\t\t\t\t\t\t\tif ( allowed === false ) {\n
\t\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t\t}\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\n
\t\t\t\tstep = self.options.step;\n
\t\t\t\tif ( self.options.values && self.options.values.length ) {\n
\t\t\t\t\tcurVal = newVal = self.values( index );\n
\t\t\t\t} else {\n
\t\t\t\t\tcurVal = newVal = self.value();\n
\t\t\t\t}\n
\t\n
\t\t\t\tswitch ( event.keyCode ) {\n
\t\t\t\t\tcase $.ui.keyCode.HOME:\n
\t\t\t\t\t\tnewVal = self._valueMin();\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase $.ui.keyCode.END:\n
\t\t\t\t\t\tnewVal = self._valueMax();\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase $.ui.keyCode.PAGE_UP:\n
\t\t\t\t\t\tnewVal = self._trimAlignValue( curVal + ( (self._valueMax() - self._valueMin()) / numPages ) );\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase $.ui.keyCode.PAGE_DOWN:\n
\t\t\t\t\t\tnewVal = self._trimAlignValue( curVal - ( (self._valueMax() - self._valueMin()) / numPages ) );\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase $.ui.keyCode.UP:\n
\t\t\t\t\tcase $.ui.keyCode.RIGHT:\n
\t\t\t\t\t\tif ( curVal === self._valueMax() ) {\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tnewVal = self._trimAlignValue( curVal + step );\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t\tcase $.ui.keyCode.DOWN:\n
\t\t\t\t\tcase $.ui.keyCode.LEFT:\n
\t\t\t\t\t\tif ( curVal === self._valueMin() ) {\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tnewVal = self._trimAlignValue( curVal - step );\n
\t\t\t\t\t\tbreak;\n
\t\t\t\t}\n
\t\n
\t\t\t\tself._slide( event, index, newVal );\n
\t\n
\t\t\t\treturn ret;\n
\t\n
\t\t\t})\n
\t\t\t.keyup(function( event ) {\n
\t\t\t\tvar index = $( this ).data( "index.ui-slider-handle" );\n
\t\n
\t\t\t\tif ( self._keySliding ) {\n
\t\t\t\t\tself._keySliding = false;\n
\t\t\t\t\tself._stop( event, index );\n
\t\t\t\t\tself._change( event, index );\n
\t\t\t\t\t$( this ).removeClass( "ui-state-active" );\n
\t\t\t\t}\n
\t\n
\t\t\t});\n
\n
\t\tthis._refreshValue();\n
\n
\t\tthis._animateOff = false;\n
\t},\n
\n
\tdestroy: function() {\n
\t\tthis.handles.remove();\n
\t\tthis.range.remove();\n
\n
\t\tthis.element\n
\t\t\t.removeClass( "ui-slider" +\n
\t\t\t\t" ui-slider-horizontal" +\n
\t\t\t\t" ui-slider-vertical" +\n
\t\t\t\t" ui-slider-disabled" +\n
\t\t\t\t" ui-widget" +\n
\t\t\t\t" ui-widget-content" +\n
\t\t\t\t" ui-corner-all" )\n
\t\t\t.removeData( "slider" )\n
\t\t\t.unbind( ".slider" );\n
\n
\t\tthis._mouseDestroy();\n
\n
\t\treturn this;\n
\t},\n
\n
\t_mouseCapture: function( event ) {\n
\t\tvar o = this.options,\n
\t\t\tposition,\n
\t\t\tnormValue,\n
\t\t\tdistance,\n
\t\t\tclosestHandle,\n
\t\t\tself,\n
\t\t\tindex,\n
\t\t\tallowed,\n
\t\t\toffset,\n
\t\t\tmouseOverHandle;\n
\n
\t\tif ( o.disabled ) {\n
\t\t\treturn false;\n
\t\t}\n
\n
\t\tthis.elementSize = {\n
\t\t\twidth: this.element.outerWidth(),\n
\t\t\theight: this.element.outerHeight()\n
\t\t};\n
\t\tthis.elementOffset = this.element.offset();\n
\n
\t\tposition = { x: event.pageX, y: event.pageY };\n
\t\tnormValue = this._normValueFromMouse( position );\n
\t\tdistance = this._valueMax() - this._valueMin() + 1;\n
\t\tself = this;\n
\t\tthis.handles.each(function( i ) {\n
\t\t\tvar thisDistance = Math.abs( normValue - self.values(i) );\n
\t\t\tif ( distance > thisDistance ) {\n
\t\t\t\tdistance = thisDistance;\n
\t\t\t\tclosestHandle = $( this );\n
\t\t\t\tindex = i;\n
\t\t\t}\n
\t\t});\n
\n
\t\t// workaround for bug #3736 (if both handles of a range are at 0,\n
\t\t// the first is always used as the one with least distance,\n
\t\t// and moving it is obviously prevented by preventing negative ranges)\n
\t\tif( o.range === true && this.values(1) === o.min ) {\n
\t\t\tindex += 1;\n
\t\t\tclosestHandle = $( this.handles[index] );\n
\t\t}\n
\n
\t\tallowed = this._start( event, index );\n
\t\tif ( allowed === false ) {\n
\t\t\treturn false;\n
\t\t}\n
\t\tthis._mouseSliding = true;\n
\n
\t\tself._handleIndex = index;\n
\n
\t\tclosestHandle\n
\t\t\t.addClass( "ui-state-active" )\n
\t\t\t.focus();\n
\t\t\n
\t\toffset = closestHandle.offset();\n
\t\tmouseOverHandle = !$( event.target ).parents().andSelf().is( ".ui-slider-handle" );\n
\t\tthis._clickOffset = mouseOverHandle ? { left: 0, top: 0 } : {\n
\t\t\tleft: event.pageX - offset.left - ( closestHandle.width() / 2 ),\n
\t\t\ttop: event.pageY - offset.top -\n
\t\t\t\t( closestHandle.height() / 2 ) -\n
\t\t\t\t( parseInt( closestHandle.css("borderTopWidth"), 10 ) || 0 ) -\n
\t\t\t\t( parseInt( closestHandle.css("borderBottomWidth"), 10 ) || 0) +\n
\t\t\t\t( parseInt( closestHandle.css("marginTop"), 10 ) || 0)\n
\t\t};\n
\n
\t\tnormValue = this._normValueFromMouse( position );\n
\t\tthis._slide( event, index, normValue );\n
\t\tthis._animateOff = true;\n
\t\treturn true;\n
\t},\n
\n
\t_mouseStart: function( event ) {\n
\t\treturn true;\n
\t},\n
\n
\t_mouseDrag: function( event ) {\n
\t\tvar position = { x: event.pageX, y: event.pageY },\n
\t\t\tnormValue = this._normValueFromMouse( position );\n
\t\t\n
\t\tthis._slide( event, this._handleIndex, normValue );\n
\n
\t\treturn false;\n
\t},\n
\n
\t_mouseStop: function( event ) {\n
\t\tthis.handles.removeClass( "ui-state-active" );\n
\t\tthis._mouseSliding = false;\n
\n
\t\tthis._stop( event, this._handleIndex );\n
\t\tthis._change( event, this._handleIndex );\n
\n
\t\tthis._handleIndex = null;\n
\t\tthis._clickOffset = null;\n
\t\tthis._animateOff = false;\n
\n
\t\treturn false;\n
\t},\n
\t\n
\t_detectOrientation: function() {\n
\t\tthis.orientation = ( this.options.orientation === "vertical" ) ? "vertical" : "horizontal";\n
\t},\n
\n
\t_normValueFromMouse: function( position ) {\n
\t\tvar pixelTotal,\n
\t\t\tpixelMouse,\n
\t\t\tpercentMouse,\n
\t\t\tvalueTotal,\n
\t\t\tvalueMouse;\n
\n
\t\tif ( this.orientation === "horizontal" ) {\n
\t\t\tpixelTotal = this.elementSize.width;\n
\t\t\tpixelMouse = position.x - this.elementOffset.left - ( this._clickOffset ? this._clickOffset.left : 0 );\n
\t\t} else {\n
\t\t\tpixelTotal = this.elementSize.height;\n
\t\t\tpixelMouse = position.y - this.elementOffset.top - ( this._clickOffset ? this._clickOffset.top : 0 );\n
\t\t}\n
\n
\t\tpercentMouse = ( pixelMouse / pixelTotal );\n
\t\tif ( percentMouse > 1 ) {\n
\t\t\tpercentMouse = 1;\n
\t\t}\n
\t\tif ( percentMouse < 0 ) {\n
\t\t\tpercentMouse = 0;\n
\t\t}\n
\t\tif ( this.orientation === "vertical" ) {\n
\t\t\tpercentMouse = 1 - percentMouse;\n
\t\t}\n
\n
\t\tvalueTotal = this._valueMax() - this._valueMin();\n
\t\tvalueMouse = this._valueMin() + percentMouse * valueTotal;\n
\n
\t\treturn this._trimAlignValue( valueMouse );\n
\t},\n
\n
\t_start: function( event, index ) {\n
\t\tvar uiHash = {\n
\t\t\thandle: this.handles[ index ],\n
\t\t\tvalue: this.value()\n
\t\t};\n
\t\tif ( this.options.values && this.options.values.length ) {\n
\t\t\tuiHash.value = this.values( index );\n
\t\t\tuiHash.values = this.values();\n
\t\t}\n
\t\treturn this._trigger( "start", event, uiHash );\n
\t},\n
\n
\t_slide: function( event, index, newVal ) {\n
\t\tvar otherVal,\n
\t\t\tnewValues,\n
\t\t\tallowed;\n
\n
\t\tif ( this.options.values && this.options.values.length ) {\n
\t\t\totherVal = this.values( index ? 0 : 1 );\n
\n
\t\t\tif ( ( this.options.values.length === 2 && this.options.range === true ) && \n
\t\t\t\t\t( ( index === 0 && newVal > otherVal) || ( index === 1 && newVal < otherVal ) )\n
\t\t\t\t) {\n
\t\t\t\tnewVal = otherVal;\n
\t\t\t}\n
\n
\t\t\tif ( newVal !== this.values( index ) ) {\n
\t\t\t\tnewValues = this.values();\n
\t\t\t\tnewValues[ index ] = newVal;\n
\t\t\t\t// A slide can be canceled by returning false from the slide callback\n
\t\t\t\tallowed = this._trigger( "slide", event, {\n
\t\t\t\t\thandle: this.handles[ index ],\n
\t\t\t\t\tvalue: newVal,\n
\t\t\t\t\tvalues: newValues\n
\t\t\t\t} );\n
\t\t\t\totherVal = this.values( index ? 0 : 1 );\n
\t\t\t\tif ( allowed !== false ) {\n
\t\t\t\t\tthis.values( index, newVal, true );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t} else {\n
\t\t\tif ( newVal !== this.value() ) {\n
\t\t\t\t// A slide can be canceled by returning false from the slide callback\n
\t\t\t\tallowed = this._trigger( "slide", event, {\n
\t\t\t\t\thandle: this.handles[ index ],\n
\t\t\t\t\tvalue: newVal\n
\t\t\t\t} );\n
\t\t\t\tif ( allowed !== false ) {\n
\t\t\t\t\tthis.value( newVal );\n
\t\t\t\t}\n
\t\t\t}\n
\t\t}\n
\t},\n
\n
\t_stop: function( event, index ) {\n
\t\tvar uiHash = {\n
\t\t\thandle: this.handles[ index ],\n
\t\t\tvalue: this.value()\n
\t\t};\n
\t\tif ( this.options.values && this.options.values.length ) {\n
\t\t\tuiHash.value = this.values( index );\n
\t\t\tuiHash.values = this.values();\n
\t\t}\n
\n
\t\tthis._trigger( "stop", event, uiHash );\n
\t},\n
\n
\t_change: function( event, index ) {\n
\t\tif ( !this._keySliding && !this._mouseSliding ) {\n
\t\t\tvar uiHash = {\n
\t\t\t\thandle: this.handles[ index ],\n
\t\t\t\tvalue: this.value()\n
\t\t\t};\n
\t\t\tif ( this.options.values && this.options.values.length ) {\n
\t\t\t\tuiHash.value = this.values( index );\n
\t\t\t\tuiHash.values = this.values();\n
\t\t\t}\n
\n
\t\t\tthis._trigger( "change", event, uiHash );\n
\t\t}\n
\t},\n
\n
\tvalue: function( newValue ) {\n
\t\tif ( arguments.length ) {\n
\t\t\tthis.options.value = this._trimAlignValue( newValue );\n
\t\t\tthis._refreshValue();\n
\t\t\tthis._change( null, 0 );\n
\t\t}\n
\n
\t\treturn this._value();\n
\t},\n
\n
\tvalues: function( index, newValue ) {\n
\t\tvar vals,\n
\t\t\tnewValues,\n
\t\t\ti;\n
\n
\t\tif ( arguments.length > 1 ) {\n
\t\t\tthis.options.values[ index ] = this._trimAlignValue( newValue );\n
\t\t\tthis._refreshValue();\n
\t\t\tthis._change( null, index );\n
\t\t}\n
\n
\t\tif ( arguments.length ) {\n
\t\t\tif ( $.isArray( arguments[ 0 ] ) ) {\n
\t\t\t\tvals = this.options.values;\n
\t\t\t\tnewValues = arguments[ 0 ];\n
\t\t\t\tfor ( i = 0; i < vals.length; i += 1 ) {\n
\t\t\t\t\tvals[ i ] = this._trimAlignValue( newValues[ i ] );\n
\t\t\t\t\tthis._change( null, i );\n
\t\t\t\t}\n
\t\t\t\tthis._refreshValue();\n
\t\t\t} else {\n
\t\t\t\tif ( this.options.values && this.options.values.length ) {\n
\t\t\t\t\treturn this._values( index );\n
\t\t\t\t} else {\n
\t\t\t\t\treturn this.value();\n
\t\t\t\t}\n
\t\t\t}\n
\t\t} else {\n
\t\t\treturn this._values();\n
\t\t}\n
\t},\n
\n
\t_setOption: function( key, value ) {\n
\t\tvar i,\n
\t\t\tvalsLength = 0;\n
\n
\t\tif ( $.isArray( this.options.values ) ) {\n
\t\t\tvalsLength = this.options.values.length;\n
\t\t}\n
\n
\t\t$.Widget.prototype._setOption.apply( this, arguments );\n
\n
\t\tswitch ( key ) {\n
\t\t\tcase "disabled":\n
\t\t\t\tif ( value ) {\n
\t\t\t\t\tthis.handles.filter( ".ui-state-focus" ).blur();\n
\t\t\t\t\tthis.handles.removeClass( "ui-state-hover" );\n
\t\t\t\t\tthis.handles.attr( "disabled", "disabled" );\n
\t\t\t\t\tthis.element.addClass( "ui-disabled" );\n
\t\t\t\t} else {\n
\t\t\t\t\tthis.handles.removeAttr( "disabled" );\n
\t\t\t\t\tthis.element.removeClass( "ui-disabled" );\n
\t\t\t\t}\n
\t\t\t\tbreak;\n
\t\t\tcase "orientation":\n
\t\t\t\tthis._detectOrientation();\n
\t\t\t\tthis.element\n
\t\t\t\t\t.removeClass( "ui-slider-horizontal ui-slider-vertical" )\n
\t\t\t\t\t.addClass( "ui-slider-" + this.orientation );\n
\t\t\t\tthis._refreshValue();\n
\t\t\t\tbreak;\n
\t\t\tcase "value":\n
\t\t\t\tthis._animateOff = true;\n
\t\t\t\tthis._refreshValue();\n
\t\t\t\tthis._change( null, 0 );\n
\t\t\t\tthis._animateOff = false;\n
\t\t\t\tbreak;\n
\t\t\tcase "values":\n
\t\t\t\tthis._animateOff = true;\n
\t\t\t\tthis._refreshValue();\n
\t\t\t\tfor ( i = 0; i < valsLength; i += 1 ) {\n
\t\t\t\t\tthis._change( null, i );\n
\t\t\t\t}\n
\t\t\t\tthis._animateOff = false;\n
\t\t\t\tbreak;\n
\t\t}\n
\t},\n
\n
\t//internal value getter\n
\t// _value() returns value trimmed by min and max, aligned by step\n
\t_value: function() {\n
\t\tvar val = this.options.value;\n
\t\tval = this._trimAlignValue( val );\n
\n
\t\treturn val;\n
\t},\n
\n
\t//internal values getter\n
\t// _values() returns array of values trimmed by min and max, aligned by step\n
\t// _values( index ) returns single value trimmed by min and max, aligned by step\n
\t_values: function( index ) {\n
\t\tvar val,\n
\t\t\tvals,\n
\t\t\ti;\n
\n
\t\tif ( arguments.length ) {\n
\t\t\tval = this.options.values[ index ];\n
\t\t\tval = this._trimAlignValue( val );\n
\n
\t\t\treturn val;\n
\t\t} else {\n
\t\t\t// .slice() creates a copy of the array\n
\t\t\t// this copy gets trimmed by min and max and then returned\n
\t\t\tvals = this.options.values.slice();\n
\t\t\tfor ( i = 0; i < vals.length; i+= 1) {\n
\t\t\t\tvals[ i ] = this._trimAlignValue( vals[ i ] );\n
\t\t\t}\n
\n
\t\t\treturn vals;\n
\t\t}\n
\t},\n
\t\n
\t// returns the step-aligned value that val is closest to, between (inclusive) min and max\n
\t_trimAlignValue: function( val ) {\n
\t\tif ( val < this._valueMin() ) {\n
\t\t\treturn this._valueMin();\n
\t\t}\n
\t\tif ( val > this._valueMax() ) {\n
\t\t\treturn this._valueMax();\n
\t\t}\n
\t\tvar step = ( this.options.step > 0 ) ? this.options.step : 1,\n
\t\t\tvalModStep = val % step,\n
\t\t\talignValue = val - valModStep;\n
\n
\t\tif ( Math.abs(valModStep) * 2 >= step ) {\n
\t\t\talignValue += ( valModStep > 0 ) ? step : ( -step );\n
\t\t}\n
\n
\t\t// Since JavaScript has problems with large floats, round\n
\t\t// the final value to 5 digits after the decimal point (see #4124)\n
\t\treturn parseFloat( alignValue.toFixed(5) );\n
\t},\n
\n
\t_valueMin: function() {\n
\t\treturn this.options.min;\n
\t},\n
\n
\t_valueMax: function() {\n
\t\treturn this.options.max;\n
\t},\n
\t\n
\t_refreshValue: function() {\n
\t\tvar oRange = this.options.range,\n
\t\t\to = this.options,\n
\t\t\tself = this,\n
\t\t\tanimate = ( !this._animateOff ) ? o.animate : false,\n
\t\t\tvalPercent,\n
\t\t\t_set = {},\n
\t\t\tlastValPercent,\n
\t\t\tvalue,\n
\t\t\tvalueMin,\n
\t\t\tvalueMax;\n
\n
\t\tif ( this.options.values && this.options.values.length ) {\n
\t\t\tthis.handles.each(function( i, j ) {\n
\t\t\t\tvalPercent = ( self.values(i) - self._valueMin() ) / ( self._valueMax() - self._valueMin() ) * 100;\n
\t\t\t\t_set[ self.orientation === "horizontal" ? "left" : "bottom" ] = valPercent + "%";\n
\t\t\t\t$( this ).stop( 1, 1 )[ animate ? "animate" : "css" ]( _set, o.animate );\n
\t\t\t\tif ( self.options.range === true ) {\n
\t\t\t\t\tif ( self.orientation === "horizontal" ) {\n
\t\t\t\t\t\tif ( i === 0 ) {\n
\t\t\t\t\t\t\tself.range.stop( 1, 1 )[ animate ? "animate" : "css" ]( { left: valPercent + "%" }, o.animate );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif ( i === 1 ) {\n
\t\t\t\t\t\t\tself.range[ animate ? "animate" : "css" ]( { width: ( valPercent - lastValPercent ) + "%" }, { queue: false, duration: o.animate } );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t} else {\n
\t\t\t\t\t\tif ( i === 0 ) {\n
\t\t\t\t\t\t\tself.range.stop( 1, 1 )[ animate ? "animate" : "css" ]( { bottom: ( valPercent ) + "%" }, o.animate );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tif ( i === 1 ) {\n
\t\t\t\t\t\t\tself.range[ animate ? "animate" : "css" ]( { height: ( valPercent - lastValPercent ) + "%" }, { queue: false, duration: o.animate } );\n
\t\t\t\t\t\t}\n
\t\t\t\t\t}\n
\t\t\t\t}\n
\t\t\t\tlastValPercent = valPercent;\n
\t\t\t});\n
\t\t} else {\n
\t\t\tvalue = this.value();\n
\t\t\tvalueMin = this._valueMin();\n
\t\t\tvalueMax = this._valueMax();\n
\t\t\tvalPercent = ( valueMax !== valueMin ) ?\n
\t\t\t\t\t( value - valueMin ) / ( valueMax - valueMin ) * 100 :\n
\t\t\t\t\t0;\n
\t\t\t_set[ self.orientation === "horizontal" ? "left" : "bottom" ] = valPercent + "%";\n
\t\t\tthis.handle.stop( 1, 1 )[ animate ? "animate" : "css" ]( _set, o.animate );\n
\n
\t\t\tif ( oRange === "min" && this.orientation === "horizontal" ) {\n
\t\t\t\tthis.range.stop( 1, 1 )[ animate ? "animate" : "css" ]( { width: valPercent + "%" }, o.animate );\n
\t\t\t}\n
\t\t\tif ( oRange === "max" && this.orientation === "horizontal" ) {\n
\t\t\t\tthis.range[ animate ? "animate" : "css" ]( { width: ( 100 - valPercent ) + "%" }, { queue: false, duration: o.animate } );\n
\t\t\t}\n
\t\t\tif ( oRange === "min" && this.orientation === "vertical" ) {\n
\t\t\t\tthis.range.stop( 1, 1 )[ animate ? "animate" : "css" ]( { height: valPercent + "%" }, o.animate );\n
\t\t\t}\n
\t\t\tif ( oRange === "max" && this.orientation === "vertical" ) {\n
\t\t\t\tthis.range[ animate ? "animate" : "css" ]( { height: ( 100 - valPercent ) + "%" }, { queue: false, duration: o.animate } );\n
\t\t\t}\n
\t\t}\n
\t}\n
\n
});\n
\n
$.extend( $.ui.slider, {\n
\tversion: "1.8.2"\n
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
            <value> <int>17710</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
