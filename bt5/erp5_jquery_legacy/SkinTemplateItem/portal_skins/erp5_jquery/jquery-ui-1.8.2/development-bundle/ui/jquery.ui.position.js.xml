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
            <value> <string>ts77895656.06</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.ui.position.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Position 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Position\n
 */\n
(function( $ ) {\n
\n
$.ui = $.ui || {};\n
\n
var horizontalPositions = /left|center|right/,\n
\thorizontalDefault = "center",\n
\tverticalPositions = /top|center|bottom/,\n
\tverticalDefault = "center",\n
\t_position = $.fn.position,\n
\t_offset = $.fn.offset;\n
\n
$.fn.position = function( options ) {\n
\tif ( !options || !options.of ) {\n
\t\treturn _position.apply( this, arguments );\n
\t}\n
\n
\t// make a copy, we don\'t want to modify arguments\n
\toptions = $.extend( {}, options );\n
\n
\tvar target = $( options.of ),\n
\t\tcollision = ( options.collision || "flip" ).split( " " ),\n
\t\toffset = options.offset ? options.offset.split( " " ) : [ 0, 0 ],\n
\t\ttargetWidth,\n
\t\ttargetHeight,\n
\t\tbasePosition;\n
\n
\tif ( options.of.nodeType === 9 ) {\n
\t\ttargetWidth = target.width();\n
\t\ttargetHeight = target.height();\n
\t\tbasePosition = { top: 0, left: 0 };\n
\t} else if ( options.of.scrollTo && options.of.document ) {\n
\t\ttargetWidth = target.width();\n
\t\ttargetHeight = target.height();\n
\t\tbasePosition = { top: target.scrollTop(), left: target.scrollLeft() };\n
\t} else if ( options.of.preventDefault ) {\n
\t\t// force left top to allow flipping\n
\t\toptions.at = "left top";\n
\t\ttargetWidth = targetHeight = 0;\n
\t\tbasePosition = { top: options.of.pageY, left: options.of.pageX };\n
\t} else {\n
\t\ttargetWidth = target.outerWidth();\n
\t\ttargetHeight = target.outerHeight();\n
\t\tbasePosition = target.offset();\n
\t}\n
\n
\t// force my and at to have valid horizontal and veritcal positions\n
\t// if a value is missing or invalid, it will be converted to center \n
\t$.each( [ "my", "at" ], function() {\n
\t\tvar pos = ( options[this] || "" ).split( " " );\n
\t\tif ( pos.length === 1) {\n
\t\t\tpos = horizontalPositions.test( pos[0] ) ?\n
\t\t\t\tpos.concat( [verticalDefault] ) :\n
\t\t\t\tverticalPositions.test( pos[0] ) ?\n
\t\t\t\t\t[ horizontalDefault ].concat( pos ) :\n
\t\t\t\t\t[ horizontalDefault, verticalDefault ];\n
\t\t}\n
\t\tpos[ 0 ] = horizontalPositions.test( pos[0] ) ? pos[ 0 ] : horizontalDefault;\n
\t\tpos[ 1 ] = verticalPositions.test( pos[1] ) ? pos[ 1 ] : verticalDefault;\n
\t\toptions[ this ] = pos;\n
\t});\n
\n
\t// normalize collision option\n
\tif ( collision.length === 1 ) {\n
\t\tcollision[ 1 ] = collision[ 0 ];\n
\t}\n
\n
\t// normalize offset option\n
\toffset[ 0 ] = parseInt( offset[0], 10 ) || 0;\n
\tif ( offset.length === 1 ) {\n
\t\toffset[ 1 ] = offset[ 0 ];\n
\t}\n
\toffset[ 1 ] = parseInt( offset[1], 10 ) || 0;\n
\n
\tif ( options.at[0] === "right" ) {\n
\t\tbasePosition.left += targetWidth;\n
\t} else if (options.at[0] === horizontalDefault ) {\n
\t\tbasePosition.left += targetWidth / 2;\n
\t}\n
\n
\tif ( options.at[1] === "bottom" ) {\n
\t\tbasePosition.top += targetHeight;\n
\t} else if ( options.at[1] === verticalDefault ) {\n
\t\tbasePosition.top += targetHeight / 2;\n
\t}\n
\n
\tbasePosition.left += offset[ 0 ];\n
\tbasePosition.top += offset[ 1 ];\n
\n
\treturn this.each(function() {\n
\t\tvar elem = $( this ),\n
\t\t\telemWidth = elem.outerWidth(),\n
\t\t\telemHeight = elem.outerHeight(),\n
\t\t\tposition = $.extend( {}, basePosition );\n
\n
\t\tif ( options.my[0] === "right" ) {\n
\t\t\tposition.left -= elemWidth;\n
\t\t} else if ( options.my[0] === horizontalDefault ) {\n
\t\t\tposition.left -= elemWidth / 2;\n
\t\t}\n
\n
\t\tif ( options.my[1] === "bottom" ) {\n
\t\t\tposition.top -= elemHeight;\n
\t\t} else if ( options.my[1] === verticalDefault ) {\n
\t\t\tposition.top -= elemHeight / 2;\n
\t\t}\n
\n
\t\t// prevent fractions (see #5280)\n
\t\tposition.left = parseInt( position.left );\n
\t\tposition.top = parseInt( position.top );\n
\n
\t\t$.each( [ "left", "top" ], function( i, dir ) {\n
\t\t\tif ( $.ui.position[ collision[i] ] ) {\n
\t\t\t\t$.ui.position[ collision[i] ][ dir ]( position, {\n
\t\t\t\t\ttargetWidth: targetWidth,\n
\t\t\t\t\ttargetHeight: targetHeight,\n
\t\t\t\t\telemWidth: elemWidth,\n
\t\t\t\t\telemHeight: elemHeight,\n
\t\t\t\t\toffset: offset,\n
\t\t\t\t\tmy: options.my,\n
\t\t\t\t\tat: options.at\n
\t\t\t\t});\n
\t\t\t}\n
\t\t});\n
\n
\t\tif ( $.fn.bgiframe ) {\n
\t\t\telem.bgiframe();\n
\t\t}\n
\t\telem.offset( $.extend( position, { using: options.using } ) );\n
\t});\n
};\n
\n
$.ui.position = {\n
\tfit: {\n
\t\tleft: function( position, data ) {\n
\t\t\tvar win = $( window ),\n
\t\t\t\tover = position.left + data.elemWidth - win.width() - win.scrollLeft();\n
\t\t\tposition.left = over > 0 ? position.left - over : Math.max( 0, position.left );\n
\t\t},\n
\t\ttop: function( position, data ) {\n
\t\t\tvar win = $( window ),\n
\t\t\t\tover = position.top + data.elemHeight - win.height() - win.scrollTop();\n
\t\t\tposition.top = over > 0 ? position.top - over : Math.max( 0, position.top );\n
\t\t}\n
\t},\n
\n
\tflip: {\n
\t\tleft: function( position, data ) {\n
\t\t\tif ( data.at[0] === "center" ) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tvar win = $( window ),\n
\t\t\t\tover = position.left + data.elemWidth - win.width() - win.scrollLeft(),\n
\t\t\t\tmyOffset = data.my[ 0 ] === "left" ?\n
\t\t\t\t\t-data.elemWidth :\n
\t\t\t\t\tdata.my[ 0 ] === "right" ?\n
\t\t\t\t\t\tdata.elemWidth :\n
\t\t\t\t\t\t0,\n
\t\t\t\toffset = -2 * data.offset[ 0 ];\n
\t\t\tposition.left += position.left < 0 ?\n
\t\t\t\tmyOffset + data.targetWidth + offset :\n
\t\t\t\tover > 0 ?\n
\t\t\t\t\tmyOffset - data.targetWidth + offset :\n
\t\t\t\t\t0;\n
\t\t},\n
\t\ttop: function( position, data ) {\n
\t\t\tif ( data.at[1] === "center" ) {\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\tvar win = $( window ),\n
\t\t\t\tover = position.top + data.elemHeight - win.height() - win.scrollTop(),\n
\t\t\t\tmyOffset = data.my[ 1 ] === "top" ?\n
\t\t\t\t\t-data.elemHeight :\n
\t\t\t\t\tdata.my[ 1 ] === "bottom" ?\n
\t\t\t\t\t\tdata.elemHeight :\n
\t\t\t\t\t\t0,\n
\t\t\t\tatOffset = data.at[ 1 ] === "top" ?\n
\t\t\t\t\tdata.targetHeight :\n
\t\t\t\t\t-data.targetHeight,\n
\t\t\t\toffset = -2 * data.offset[ 1 ];\n
\t\t\tposition.top += position.top < 0 ?\n
\t\t\t\tmyOffset + data.targetHeight + offset :\n
\t\t\t\tover > 0 ?\n
\t\t\t\t\tmyOffset + atOffset + offset :\n
\t\t\t\t\t0;\n
\t\t}\n
\t}\n
};\n
\n
// offset setter from jQuery 1.4\n
if ( !$.offset.setOffset ) {\n
\t$.offset.setOffset = function( elem, options ) {\n
\t\t// set position first, in-case top/left are set even on static elem\n
\t\tif ( /static/.test( $.curCSS( elem, "position" ) ) ) {\n
\t\t\telem.style.position = "relative";\n
\t\t}\n
\t\tvar curElem   = $( elem ),\n
\t\t\tcurOffset = curElem.offset(),\n
\t\t\tcurTop    = parseInt( $.curCSS( elem, "top",  true ), 10 ) || 0,\n
\t\t\tcurLeft   = parseInt( $.curCSS( elem, "left", true ), 10)  || 0,\n
\t\t\tprops     = {\n
\t\t\t\ttop:  (options.top  - curOffset.top)  + curTop,\n
\t\t\t\tleft: (options.left - curOffset.left) + curLeft\n
\t\t\t};\n
\t\t\n
\t\tif ( \'using\' in options ) {\n
\t\t\toptions.using.call( elem, props );\n
\t\t} else {\n
\t\t\tcurElem.css( props );\n
\t\t}\n
\t};\n
\n
\t$.fn.offset = function( options ) {\n
\t\tvar elem = this[ 0 ];\n
\t\tif ( !elem || !elem.ownerDocument ) { return null; }\n
\t\tif ( options ) { \n
\t\t\treturn this.each(function() {\n
\t\t\t\t$.offset.setOffset( this, options );\n
\t\t\t});\n
\t\t}\n
\t\treturn _offset.call( this );\n
\t};\n
}\n
\n
}( jQuery ));\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6588</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
