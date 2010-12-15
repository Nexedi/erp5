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
            <value> <string>ts77895655.43</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.effects.pulsate.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Effects Pulsate 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Effects/Pulsate\n
 *\n
 * Depends:\n
 *\tjquery.effects.core.js\n
 */\n
(function($) {\n
\n
$.effects.pulsate = function(o) {\n
\treturn this.queue(function() {\n
\t\tvar elem = $(this),\n
\t\t\tmode = $.effects.setMode(elem, o.options.mode || \'show\');\n
\t\t\ttimes = ((o.options.times || 5) * 2) - 1;\n
\t\t\tduration = o.duration ? o.duration / 2 : $.fx.speeds._default / 2,\n
\t\t\tisVisible = elem.is(\':visible\'),\n
\t\t\tanimateTo = 0;\n
\n
\t\tif (!isVisible) {\n
\t\t\telem.css(\'opacity\', 0).show();\n
\t\t\tanimateTo = 1;\n
\t\t}\n
\n
\t\tif ((mode == \'hide\' && isVisible) || (mode == \'show\' && !isVisible)) {\n
\t\t\ttimes--;\n
\t\t}\n
\n
\t\tfor (var i = 0; i < times; i++) {\n
\t\t\telem.animate({ opacity: animateTo }, duration, o.options.easing);\n
\t\t\tanimateTo = (animateTo + 1) % 2;\n
\t\t}\n
\n
\t\telem.animate({ opacity: animateTo }, duration, o.options.easing, function() {\n
\t\t\tif (animateTo == 0) {\n
\t\t\t\telem.hide();\n
\t\t\t}\n
\t\t\t(o.callback && o.callback.apply(this, arguments));\n
\t\t});\n
\n
\t\telem\n
\t\t\t.queue(\'fx\', function() { elem.dequeue(); })\n
\t\t\t.dequeue();\n
\t});\n
};\n
\n
})(jQuery);\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1211</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
