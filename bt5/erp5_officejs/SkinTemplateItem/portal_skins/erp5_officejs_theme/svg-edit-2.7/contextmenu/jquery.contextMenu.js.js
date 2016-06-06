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
            <value> <string>ts40515059.46</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.contextMenu.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

// jQuery Context Menu Plugin\r\n
//\r\n
// Version 1.01\r\n
//\r\n
// Cory S.N. LaViska\r\n
// A Beautiful Site (http://abeautifulsite.net/)\r\n
// Modified by Alexis Deveria\r\n
//\r\n
// More info: http://abeautifulsite.net/2008/09/jquery-context-menu-plugin/\r\n
//\r\n
// Terms of Use\r\n
//\r\n
// This plugin is dual-licensed under the GNU General Public License\r\n
//   and the MIT License and is copyright A Beautiful Site, LLC.\r\n
//\r\n
if(jQuery)( function() {\r\n
\tvar win = $(window);\r\n
\tvar doc = $(document);\r\n
\r\n
\t$.extend($.fn, {\r\n
\t\t\r\n
\t\tcontextMenu: function(o, callback) {\r\n
\t\t\t// Defaults\r\n
\t\t\tif( o.menu == undefined ) return false;\r\n
\t\t\tif( o.inSpeed == undefined ) o.inSpeed = 150;\r\n
\t\t\tif( o.outSpeed == undefined ) o.outSpeed = 75;\r\n
\t\t\t// 0 needs to be -1 for expected results (no fade)\r\n
\t\t\tif( o.inSpeed == 0 ) o.inSpeed = -1;\r\n
\t\t\tif( o.outSpeed == 0 ) o.outSpeed = -1;\r\n
\t\t\t// Loop each context menu\r\n
\t\t\t$(this).each( function() {\r\n
\t\t\t\tvar el = $(this);\r\n
\t\t\t\tvar offset = $(el).offset();\r\n
\t\t\t\r\n
\t\t\t\tvar menu = $(\'#\' + o.menu);\r\n
\r\n
\t\t\t\t// Add contextMenu class\r\n
\t\t\t\tmenu.addClass(\'contextMenu\');\r\n
\t\t\t\t// Simulate a true right click\r\n
\t\t\t\t$(this).bind( "mousedown", function(e) {\r\n
\t\t\t\t\tvar evt = e;\r\n
\t\t\t\t\t$(this).mouseup( function(e) {\r\n
\t\t\t\t\t\tvar srcElement = $(this);\r\n
\t\t\t\t\t\tsrcElement.unbind(\'mouseup\');\r\n
\t\t\t\t\t\tif( evt.button === 2 || o.allowLeft || (evt.ctrlKey && svgedit.browser.isMac()) ) {\r\n
\t\t\t\t\t\t\te.stopPropagation();\r\n
\t\t\t\t\t\t\t// Hide context menus that may be showing\r\n
\t\t\t\t\t\t\t$(".contextMenu").hide();\r\n
\t\t\t\t\t\t\t// Get this context menu\r\n
\t\t\t\t\t\t\r\n
\t\t\t\t\t\t\tif( el.hasClass(\'disabled\') ) return false;\r\n
\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t\t// Detect mouse position\r\n
\t\t\t\t\t\t\tvar d = {}, x = e.pageX, y = e.pageY;\r\n
\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t\tvar x_off = win.width() - menu.width(), \r\n
\t\t\t\t\t\t\t\ty_off = win.height() - menu.height();\r\n
\r\n
\t\t\t\t\t\t\tif(x > x_off - 15) x = x_off-15;\r\n
\t\t\t\t\t\t\tif(y > y_off - 30) y = y_off-30; // 30 is needed to prevent scrollbars in FF\r\n
\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t\t// Show the menu\r\n
\t\t\t\t\t\t\tdoc.unbind(\'click\');\r\n
\t\t\t\t\t\t\tmenu.css({ top: y, left: x }).fadeIn(o.inSpeed);\r\n
\t\t\t\t\t\t\t// Hover events\r\n
\t\t\t\t\t\t\tmenu.find(\'A\').mouseover( function() {\r\n
\t\t\t\t\t\t\t\tmenu.find(\'LI.hover\').removeClass(\'hover\');\r\n
\t\t\t\t\t\t\t\t$(this).parent().addClass(\'hover\');\r\n
\t\t\t\t\t\t\t}).mouseout( function() {\r\n
\t\t\t\t\t\t\t\tmenu.find(\'LI.hover\').removeClass(\'hover\');\r\n
\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t\t// Keyboard\r\n
\t\t\t\t\t\t\tdoc.keypress( function(e) {\r\n
\t\t\t\t\t\t\t\tswitch( e.keyCode ) {\r\n
\t\t\t\t\t\t\t\t\tcase 38: // up\r\n
\t\t\t\t\t\t\t\t\t\tif( !menu.find(\'LI.hover\').length ) {\r\n
\t\t\t\t\t\t\t\t\t\t\tmenu.find(\'LI:last\').addClass(\'hover\');\r\n
\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\tmenu.find(\'LI.hover\').removeClass(\'hover\').prevAll(\'LI:not(.disabled)\').eq(0).addClass(\'hover\');\r\n
\t\t\t\t\t\t\t\t\t\t\tif( !menu.find(\'LI.hover\').length ) menu.find(\'LI:last\').addClass(\'hover\');\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t\t\tcase 40: // down\r\n
\t\t\t\t\t\t\t\t\t\tif( menu.find(\'LI.hover\').length == 0 ) {\r\n
\t\t\t\t\t\t\t\t\t\t\tmenu.find(\'LI:first\').addClass(\'hover\');\r\n
\t\t\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t\t\tmenu.find(\'LI.hover\').removeClass(\'hover\').nextAll(\'LI:not(.disabled)\').eq(0).addClass(\'hover\');\r\n
\t\t\t\t\t\t\t\t\t\t\tif( !menu.find(\'LI.hover\').length ) menu.find(\'LI:first\').addClass(\'hover\');\r\n
\t\t\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t\t\tcase 13: // enter\r\n
\t\t\t\t\t\t\t\t\t\tmenu.find(\'LI.hover A\').trigger(\'click\');\r\n
\t\t\t\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\t\t\t\tcase 27: // esc\r\n
\t\t\t\t\t\t\t\t\t\tdoc.trigger(\'click\');\r\n
\t\t\t\t\t\t\t\t\tbreak\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t\t// When items are selected\r\n
\t\t\t\t\t\t\tmenu.find(\'A\').unbind(\'mouseup\');\r\n
\t\t\t\t\t\t\tmenu.find(\'LI:not(.disabled) A\').mouseup( function() {\r\n
\t\t\t\t\t\t\t\tdoc.unbind(\'click\').unbind(\'keypress\');\r\n
\t\t\t\t\t\t\t\t$(".contextMenu").hide();\r\n
\t\t\t\t\t\t\t\t// Callback\r\n
\t\t\t\t\t\t\t\tif( callback ) callback( $(this).attr(\'href\').substr(1), $(srcElement), {x: x - offset.left, y: y - offset.top, docX: x, docY: y} );\r\n
\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t\r\n
\t\t\t\t\t\t\t// Hide bindings\r\n
\t\t\t\t\t\t\tsetTimeout( function() { // Delay for Mozilla\r\n
\t\t\t\t\t\t\t\tdoc.click( function() {\r\n
\t\t\t\t\t\t\t\t\tdoc.unbind(\'click\').unbind(\'keypress\');\r\n
\t\t\t\t\t\t\t\t\tmenu.fadeOut(o.outSpeed);\r\n
\t\t\t\t\t\t\t\t\treturn false;\r\n
\t\t\t\t\t\t\t\t});\r\n
\t\t\t\t\t\t\t}, 0);\r\n
\t\t\t\t\t\t}\r\n
\t\t\t\t\t});\r\n
\t\t\t\t});\r\n
\t\t\t\t\r\n
\t\t\t\t// Disable text selection\r\n
\t\t\t\tif( $.browser.mozilla ) {\r\n
\t\t\t\t\t$(\'#\' + o.menu).each( function() { $(this).css({ \'MozUserSelect\' : \'none\' }); });\r\n
\t\t\t\t} else if( $.browser.msie ) {\r\n
\t\t\t\t\t$(\'#\' + o.menu).each( function() { $(this).bind(\'selectstart.disableTextSelect\', function() { return false; }); });\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\t$(\'#\' + o.menu).each(function() { $(this).bind(\'mousedown.disableTextSelect\', function() { return false; }); });\r\n
\t\t\t\t}\r\n
\t\t\t\t// Disable browser context menu (requires both selectors to work in IE/Safari + FF/Chrome)\r\n
\t\t\t\t$(el).add($(\'UL.contextMenu\')).bind(\'contextmenu\', function() { return false; });\r\n
\t\t\t\t\r\n
\t\t\t});\r\n
\t\t\treturn $(this);\r\n
\t\t},\r\n
\t\t\r\n
\t\t// Disable context menu items on the fly\r\n
\t\tdisableContextMenuItems: function(o) {\r\n
\t\t\tif( o == undefined ) {\r\n
\t\t\t\t// Disable all\r\n
\t\t\t\t$(this).find(\'LI\').addClass(\'disabled\');\r\n
\t\t\t\treturn( $(this) );\r\n
\t\t\t}\r\n
\t\t\t$(this).each( function() {\r\n
\t\t\t\tif( o != undefined ) {\r\n
\t\t\t\t\tvar d = o.split(\',\');\r\n
\t\t\t\t\tfor( var i = 0; i < d.length; i++ ) {\r\n
\t\t\t\t\t\t$(this).find(\'A[href="\' + d[i] + \'"]\').parent().addClass(\'disabled\');\r\n
\t\t\t\t\t\t\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\treturn( $(this) );\r\n
\t\t},\r\n
\t\t\r\n
\t\t// Enable context menu items on the fly\r\n
\t\tenableContextMenuItems: function(o) {\r\n
\t\t\tif( o == undefined ) {\r\n
\t\t\t\t// Enable all\r\n
\t\t\t\t$(this).find(\'LI.disabled\').removeClass(\'disabled\');\r\n
\t\t\t\treturn( $(this) );\r\n
\t\t\t}\r\n
\t\t\t$(this).each( function() {\r\n
\t\t\t\tif( o != undefined ) {\r\n
\t\t\t\t\tvar d = o.split(\',\');\r\n
\t\t\t\t\tfor( var i = 0; i < d.length; i++ ) {\r\n
\t\t\t\t\t\t$(this).find(\'A[href="\' + d[i] + \'"]\').parent().removeClass(\'disabled\');\r\n
\t\t\t\t\t\t\r\n
\t\t\t\t\t}\r\n
\t\t\t\t}\r\n
\t\t\t});\r\n
\t\t\treturn( $(this) );\r\n
\t\t},\r\n
\t\t\r\n
\t\t// Disable context menu(s)\r\n
\t\tdisableContextMenu: function() {\r\n
\t\t\t$(this).each( function() {\r\n
\t\t\t\t$(this).addClass(\'disabled\');\r\n
\t\t\t});\r\n
\t\t\treturn( $(this) );\r\n
\t\t},\r\n
\t\t\r\n
\t\t// Enable context menu(s)\r\n
\t\tenableContextMenu: function() {\r\n
\t\t\t$(this).each( function() {\r\n
\t\t\t\t$(this).removeClass(\'disabled\');\r\n
\t\t\t});\r\n
\t\t\treturn( $(this) );\r\n
\t\t},\r\n
\t\t\r\n
\t\t// Destroy context menu(s)\r\n
\t\tdestroyContextMenu: function() {\r\n
\t\t\t// Destroy specified context menus\r\n
\t\t\t$(this).each( function() {\r\n
\t\t\t\t// Disable action\r\n
\t\t\t\t$(this).unbind(\'mousedown\').unbind(\'mouseup\');\r\n
\t\t\t});\r\n
\t\t\treturn( $(this) );\r\n
\t\t}\r\n
\t\t\r\n
\t});\r\n
})(jQuery);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6314</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
