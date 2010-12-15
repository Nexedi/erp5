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
            <value> <string>ts65545385.48</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.bgiframe.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/* Copyright (c) 2006 Brandon Aaron (http://brandonaaron.net)\n
 * Dual licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) \n
 * and GPL (http://www.opensource.org/licenses/gpl-license.php) licenses.\n
 *\n
 * $LastChangedDate: 2007-07-21 18:44:59 -0500 (Sat, 21 Jul 2007) $\n
 * $Rev: 2446 $\n
 *\n
 * Version 2.1.1\n
 */\n
\n
(function($){\n
\n
/**\n
 * The bgiframe is chainable and applies the iframe hack to get \n
 * around zIndex issues in IE6. It will only apply itself in IE6 \n
 * and adds a class to the iframe called \'bgiframe\'. The iframe\n
 * is appeneded as the first child of the matched element(s) \n
 * with a tabIndex and zIndex of -1.\n
 * \n
 * By default the plugin will take borders, sized with pixel units,\n
 * into account. If a different unit is used for the border\'s width,\n
 * then you will need to use the top and left settings as explained below.\n
 *\n
 * NOTICE: This plugin has been reported to cause perfromance problems\n
 * when used on elements that change properties (like width, height and\n
 * opacity) a lot in IE6. Most of these problems have been caused by \n
 * the expressions used to calculate the elements width, height and \n
 * borders. Some have reported it is due to the opacity filter. All \n
 * these settings can be changed if needed as explained below.\n
 *\n
 * @example $(\'div\').bgiframe();\n
 * @before <div><p>Paragraph</p></div>\n
 * @result <div><iframe class="bgiframe".../><p>Paragraph</p></div>\n
 *\n
 * @param Map settings Optional settings to configure the iframe.\n
 * @option String|Number top The iframe must be offset to the top\n
 * \t\tby the width of the top border. This should be a negative \n
 *      number representing the border-top-width. If a number is \n
 * \t\tis used here, pixels will be assumed. Otherwise, be sure\n
 *\t\tto specify a unit. An expression could also be used. \n
 * \t\tBy default the value is "auto" which will use an expression \n
 * \t\tto get the border-top-width if it is in pixels.\n
 * @option String|Number left The iframe must be offset to the left\n
 * \t\tby the width of the left border. This should be a negative \n
 *      number representing the border-left-width. If a number is \n
 * \t\tis used here, pixels will be assumed. Otherwise, be sure\n
 *\t\tto specify a unit. An expression could also be used. \n
 * \t\tBy default the value is "auto" which will use an expression \n
 * \t\tto get the border-left-width if it is in pixels.\n
 * @option String|Number width This is the width of the iframe. If\n
 *\t\ta number is used here, pixels will be assume. Otherwise, be sure\n
 * \t\tto specify a unit. An experssion could also be used.\n
 *\t\tBy default the value is "auto" which will use an experssion\n
 * \t\tto get the offsetWidth.\n
 * @option String|Number height This is the height of the iframe. If\n
 *\t\ta number is used here, pixels will be assume. Otherwise, be sure\n
 * \t\tto specify a unit. An experssion could also be used.\n
 *\t\tBy default the value is "auto" which will use an experssion\n
 * \t\tto get the offsetHeight.\n
 * @option Boolean opacity This is a boolean representing whether or not\n
 * \t\tto use opacity. If set to true, the opacity of 0 is applied. If\n
 *\t\tset to false, the opacity filter is not applied. Default: true.\n
 * @option String src This setting is provided so that one could change \n
 *\t\tthe src of the iframe to whatever they need.\n
 *\t\tDefault: "javascript:false;"\n
 *\n
 * @name bgiframe\n
 * @type jQuery\n
 * @cat Plugins/bgiframe\n
 * @author Brandon Aaron (brandon.aaron@gmail.com || http://brandonaaron.net)\n
 */\n
$.fn.bgIframe = $.fn.bgiframe = function(s) {\n
\t// This is only for IE6\n
\tif ( $.browser.msie && /6.0/.test(navigator.userAgent) ) {\n
\t\ts = $.extend({\n
\t\t\ttop     : \'auto\', // auto == .currentStyle.borderTopWidth\n
\t\t\tleft    : \'auto\', // auto == .currentStyle.borderLeftWidth\n
\t\t\twidth   : \'auto\', // auto == offsetWidth\n
\t\t\theight  : \'auto\', // auto == offsetHeight\n
\t\t\topacity : true,\n
\t\t\tsrc     : \'javascript:false;\'\n
\t\t}, s || {});\n
\t\tvar prop = function(n){return n&&n.constructor==Number?n+\'px\':n;},\n
\t\t    html = \'<iframe class="bgiframe"frameborder="0"tabindex="-1"src="\'+s.src+\'"\'+\n
\t\t               \'style="display:block;position:absolute;z-index:-1;\'+\n
\t\t\t               (s.opacity !== false?\'filter:Alpha(Opacity=\\\'0\\\');\':\'\')+\n
\t\t\t\t\t       \'top:\'+(s.top==\'auto\'?\'expression(((parseInt(this.parentNode.currentStyle.borderTopWidth)||0)*-1)+\\\'px\\\')\':prop(s.top))+\';\'+\n
\t\t\t\t\t       \'left:\'+(s.left==\'auto\'?\'expression(((parseInt(this.parentNode.currentStyle.borderLeftWidth)||0)*-1)+\\\'px\\\')\':prop(s.left))+\';\'+\n
\t\t\t\t\t       \'width:\'+(s.width==\'auto\'?\'expression(this.parentNode.offsetWidth+\\\'px\\\')\':prop(s.width))+\';\'+\n
\t\t\t\t\t       \'height:\'+(s.height==\'auto\'?\'expression(this.parentNode.offsetHeight+\\\'px\\\')\':prop(s.height))+\';\'+\n
\t\t\t\t\t\'"/>\';\n
\t\treturn this.each(function() {\n
\t\t\tif ( $(\'> iframe.bgiframe\', this).length == 0 )\n
\t\t\t\tthis.insertBefore( document.createElement(html), this.firstChild );\n
\t\t});\n
\t}\n
\treturn this;\n
};\n
\n
})(jQuery);

]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <long>4879</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
