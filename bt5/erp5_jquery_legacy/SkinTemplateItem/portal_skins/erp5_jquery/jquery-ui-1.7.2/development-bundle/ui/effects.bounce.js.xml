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
            <value> <string>ts65545393.52</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>effects.bounce.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Effects Bounce 1.7.2\n
 *\n
 * Copyright (c) 2009 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Effects/Bounce\n
 *\n
 * Depends:\n
 *\teffects.core.js\n
 */\n
(function($) {\n
\n
$.effects.bounce = function(o) {\n
\n
\treturn this.queue(function() {\n
\n
\t\t// Create element\n
\t\tvar el = $(this), props = [\'position\',\'top\',\'left\'];\n
\n
\t\t// Set options\n
\t\tvar mode = $.effects.setMode(el, o.options.mode || \'effect\'); // Set Mode\n
\t\tvar direction = o.options.direction || \'up\'; // Default direction\n
\t\tvar distance = o.options.distance || 20; // Default distance\n
\t\tvar times = o.options.times || 5; // Default # of times\n
\t\tvar speed = o.duration || 250; // Default speed per bounce\n
\t\tif (/show|hide/.test(mode)) props.push(\'opacity\'); // Avoid touching opacity to prevent clearType and PNG issues in IE\n
\n
\t\t// Adjust\n
\t\t$.effects.save(el, props); el.show(); // Save & Show\n
\t\t$.effects.createWrapper(el); // Create Wrapper\n
\t\tvar ref = (direction == \'up\' || direction == \'down\') ? \'top\' : \'left\';\n
\t\tvar motion = (direction == \'up\' || direction == \'left\') ? \'pos\' : \'neg\';\n
\t\tvar distance = o.options.distance || (ref == \'top\' ? el.outerHeight({margin:true}) / 3 : el.outerWidth({margin:true}) / 3);\n
\t\tif (mode == \'show\') el.css(\'opacity\', 0).css(ref, motion == \'pos\' ? -distance : distance); // Shift\n
\t\tif (mode == \'hide\') distance = distance / (times * 2);\n
\t\tif (mode != \'hide\') times--;\n
\n
\t\t// Animate\n
\t\tif (mode == \'show\') { // Show Bounce\n
\t\t\tvar animation = {opacity: 1};\n
\t\t\tanimation[ref] = (motion == \'pos\' ? \'+=\' : \'-=\') + distance;\n
\t\t\tel.animate(animation, speed / 2, o.options.easing);\n
\t\t\tdistance = distance / 2;\n
\t\t\ttimes--;\n
\t\t};\n
\t\tfor (var i = 0; i < times; i++) { // Bounces\n
\t\t\tvar animation1 = {}, animation2 = {};\n
\t\t\tanimation1[ref] = (motion == \'pos\' ? \'-=\' : \'+=\') + distance;\n
\t\t\tanimation2[ref] = (motion == \'pos\' ? \'+=\' : \'-=\') + distance;\n
\t\t\tel.animate(animation1, speed / 2, o.options.easing).animate(animation2, speed / 2, o.options.easing);\n
\t\t\tdistance = (mode == \'hide\') ? distance * 2 : distance / 2;\n
\t\t};\n
\t\tif (mode == \'hide\') { // Last Bounce\n
\t\t\tvar animation = {opacity: 0};\n
\t\t\tanimation[ref] = (motion == \'pos\' ? \'-=\' : \'+=\')  + distance;\n
\t\t\tel.animate(animation, speed / 2, o.options.easing, function(){\n
\t\t\t\tel.hide(); // Hide\n
\t\t\t\t$.effects.restore(el, props); $.effects.removeWrapper(el); // Restore\n
\t\t\t\tif(o.callback) o.callback.apply(this, arguments); // Callback\n
\t\t\t});\n
\t\t} else {\n
\t\t\tvar animation1 = {}, animation2 = {};\n
\t\t\tanimation1[ref] = (motion == \'pos\' ? \'-=\' : \'+=\') + distance;\n
\t\t\tanimation2[ref] = (motion == \'pos\' ? \'+=\' : \'-=\') + distance;\n
\t\t\tel.animate(animation1, speed / 2, o.options.easing).animate(animation2, speed / 2, o.options.easing, function(){\n
\t\t\t\t$.effects.restore(el, props); $.effects.removeWrapper(el); // Restore\n
\t\t\t\tif(o.callback) o.callback.apply(this, arguments); // Callback\n
\t\t\t});\n
\t\t};\n
\t\tel.queue(\'fx\', function() { el.dequeue(); });\n
\t\tel.dequeue();\n
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
            <value> <long>3028</long> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
