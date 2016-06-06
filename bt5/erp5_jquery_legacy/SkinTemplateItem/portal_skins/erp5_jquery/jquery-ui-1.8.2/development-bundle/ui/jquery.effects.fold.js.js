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
            <value> <string>ts77895655.34</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.effects.fold.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Effects Fold 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Effects/Fold\n
 *\n
 * Depends:\n
 *\tjquery.effects.core.js\n
 */\n
(function($) {\n
\n
$.effects.fold = function(o) {\n
\n
\treturn this.queue(function() {\n
\n
\t\t// Create element\n
\t\tvar el = $(this), props = [\'position\',\'top\',\'left\'];\n
\n
\t\t// Set options\n
\t\tvar mode = $.effects.setMode(el, o.options.mode || \'hide\'); // Set Mode\n
\t\tvar size = o.options.size || 15; // Default fold size\n
\t\tvar horizFirst = !(!o.options.horizFirst); // Ensure a boolean value\n
\t\tvar duration = o.duration ? o.duration / 2 : $.fx.speeds._default / 2;\n
\n
\t\t// Adjust\n
\t\t$.effects.save(el, props); el.show(); // Save & Show\n
\t\tvar wrapper = $.effects.createWrapper(el).css({overflow:\'hidden\'}); // Create Wrapper\n
\t\tvar widthFirst = ((mode == \'show\') != horizFirst);\n
\t\tvar ref = widthFirst ? [\'width\', \'height\'] : [\'height\', \'width\'];\n
\t\tvar distance = widthFirst ? [wrapper.width(), wrapper.height()] : [wrapper.height(), wrapper.width()];\n
\t\tvar percent = /([0-9]+)%/.exec(size);\n
\t\tif(percent) size = parseInt(percent[1],10) / 100 * distance[mode == \'hide\' ? 0 : 1];\n
\t\tif(mode == \'show\') wrapper.css(horizFirst ? {height: 0, width: size} : {height: size, width: 0}); // Shift\n
\n
\t\t// Animation\n
\t\tvar animation1 = {}, animation2 = {};\n
\t\tanimation1[ref[0]] = mode == \'show\' ? distance[0] : size;\n
\t\tanimation2[ref[1]] = mode == \'show\' ? distance[1] : 0;\n
\n
\t\t// Animate\n
\t\twrapper.animate(animation1, duration, o.options.easing)\n
\t\t.animate(animation2, duration, o.options.easing, function() {\n
\t\t\tif(mode == \'hide\') el.hide(); // Hide\n
\t\t\t$.effects.restore(el, props); $.effects.removeWrapper(el); // Restore\n
\t\t\tif(o.callback) o.callback.apply(el[0], arguments); // Callback\n
\t\t\tel.dequeue();\n
\t\t});\n
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
            <value> <int>1879</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
