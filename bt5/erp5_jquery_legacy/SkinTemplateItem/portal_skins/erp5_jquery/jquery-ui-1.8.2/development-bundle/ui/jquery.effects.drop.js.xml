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
            <value> <string>ts77895655.25</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.effects.drop.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Effects Drop 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Effects/Drop\n
 *\n
 * Depends:\n
 *\tjquery.effects.core.js\n
 */\n
(function($) {\n
\n
$.effects.drop = function(o) {\n
\n
\treturn this.queue(function() {\n
\n
\t\t// Create element\n
\t\tvar el = $(this), props = [\'position\',\'top\',\'left\',\'opacity\'];\n
\n
\t\t// Set options\n
\t\tvar mode = $.effects.setMode(el, o.options.mode || \'hide\'); // Set Mode\n
\t\tvar direction = o.options.direction || \'left\'; // Default Direction\n
\n
\t\t// Adjust\n
\t\t$.effects.save(el, props); el.show(); // Save & Show\n
\t\t$.effects.createWrapper(el); // Create Wrapper\n
\t\tvar ref = (direction == \'up\' || direction == \'down\') ? \'top\' : \'left\';\n
\t\tvar motion = (direction == \'up\' || direction == \'left\') ? \'pos\' : \'neg\';\n
\t\tvar distance = o.options.distance || (ref == \'top\' ? el.outerHeight({margin:true}) / 2 : el.outerWidth({margin:true}) / 2);\n
\t\tif (mode == \'show\') el.css(\'opacity\', 0).css(ref, motion == \'pos\' ? -distance : distance); // Shift\n
\n
\t\t// Animation\n
\t\tvar animation = {opacity: mode == \'show\' ? 1 : 0};\n
\t\tanimation[ref] = (mode == \'show\' ? (motion == \'pos\' ? \'+=\' : \'-=\') : (motion == \'pos\' ? \'-=\' : \'+=\')) + distance;\n
\n
\t\t// Animate\n
\t\tel.animate(animation, { queue: false, duration: o.duration, easing: o.options.easing, complete: function() {\n
\t\t\tif(mode == \'hide\') el.hide(); // Hide\n
\t\t\t$.effects.restore(el, props); $.effects.removeWrapper(el); // Restore\n
\t\t\tif(o.callback) o.callback.apply(this, arguments); // Callback\n
\t\t\tel.dequeue();\n
\t\t}});\n
\n
\t});\n
\n
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
            <value> <int>1635</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
