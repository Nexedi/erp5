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
            <value> <string>ts77895655.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>jquery.effects.scale.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/x-javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\n
 * jQuery UI Effects Scale 1.8.2\n
 *\n
 * Copyright (c) 2010 AUTHORS.txt (http://jqueryui.com/about)\n
 * Dual licensed under the MIT (MIT-LICENSE.txt)\n
 * and GPL (GPL-LICENSE.txt) licenses.\n
 *\n
 * http://docs.jquery.com/UI/Effects/Scale\n
 *\n
 * Depends:\n
 *\tjquery.effects.core.js\n
 */\n
(function($) {\n
\n
$.effects.puff = function(o) {\n
\treturn this.queue(function() {\n
\t\tvar elem = $(this),\n
\t\t\tmode = $.effects.setMode(elem, o.options.mode || \'hide\'),\n
\t\t\tpercent = parseInt(o.options.percent, 10) || 150,\n
\t\t\tfactor = percent / 100,\n
\t\t\toriginal = { height: elem.height(), width: elem.width() };\n
\n
\t\t$.extend(o.options, {\n
\t\t\tfade: true,\n
\t\t\tmode: mode,\n
\t\t\tpercent: mode == \'hide\' ? percent : 100,\n
\t\t\tfrom: mode == \'hide\'\n
\t\t\t\t? original\n
\t\t\t\t: {\n
\t\t\t\t\theight: original.height * factor,\n
\t\t\t\t\twidth: original.width * factor\n
\t\t\t\t}\n
\t\t});\n
\n
\t\telem.effect(\'scale\', o.options, o.duration, o.callback);\n
\t\telem.dequeue();\n
\t});\n
};\n
\n
$.effects.scale = function(o) {\n
\n
\treturn this.queue(function() {\n
\n
\t\t// Create element\n
\t\tvar el = $(this);\n
\n
\t\t// Set options\n
\t\tvar options = $.extend(true, {}, o.options);\n
\t\tvar mode = $.effects.setMode(el, o.options.mode || \'effect\'); // Set Mode\n
\t\tvar percent = parseInt(o.options.percent,10) || (parseInt(o.options.percent,10) == 0 ? 0 : (mode == \'hide\' ? 0 : 100)); // Set default scaling percent\n
\t\tvar direction = o.options.direction || \'both\'; // Set default axis\n
\t\tvar origin = o.options.origin; // The origin of the scaling\n
\t\tif (mode != \'effect\') { // Set default origin and restore for show/hide\n
\t\t\toptions.origin = origin || [\'middle\',\'center\'];\n
\t\t\toptions.restore = true;\n
\t\t}\n
\t\tvar original = {height: el.height(), width: el.width()}; // Save original\n
\t\tel.from = o.options.from || (mode == \'show\' ? {height: 0, width: 0} : original); // Default from state\n
\n
\t\t// Adjust\n
\t\tvar factor = { // Set scaling factor\n
\t\t\ty: direction != \'horizontal\' ? (percent / 100) : 1,\n
\t\t\tx: direction != \'vertical\' ? (percent / 100) : 1\n
\t\t};\n
\t\tel.to = {height: original.height * factor.y, width: original.width * factor.x}; // Set to state\n
\n
\t\tif (o.options.fade) { // Fade option to support puff\n
\t\t\tif (mode == \'show\') {el.from.opacity = 0; el.to.opacity = 1;};\n
\t\t\tif (mode == \'hide\') {el.from.opacity = 1; el.to.opacity = 0;};\n
\t\t};\n
\n
\t\t// Animation\n
\t\toptions.from = el.from; options.to = el.to; options.mode = mode;\n
\n
\t\t// Animate\n
\t\tel.effect(\'size\', options, o.duration, o.callback);\n
\t\tel.dequeue();\n
\t});\n
\n
};\n
\n
$.effects.size = function(o) {\n
\n
\treturn this.queue(function() {\n
\n
\t\t// Create element\n
\t\tvar el = $(this), props = [\'position\',\'top\',\'left\',\'width\',\'height\',\'overflow\',\'opacity\'];\n
\t\tvar props1 = [\'position\',\'top\',\'left\',\'overflow\',\'opacity\']; // Always restore\n
\t\tvar props2 = [\'width\',\'height\',\'overflow\']; // Copy for children\n
\t\tvar cProps = [\'fontSize\'];\n
\t\tvar vProps = [\'borderTopWidth\', \'borderBottomWidth\', \'paddingTop\', \'paddingBottom\'];\n
\t\tvar hProps = [\'borderLeftWidth\', \'borderRightWidth\', \'paddingLeft\', \'paddingRight\'];\n
\n
\t\t// Set options\n
\t\tvar mode = $.effects.setMode(el, o.options.mode || \'effect\'); // Set Mode\n
\t\tvar restore = o.options.restore || false; // Default restore\n
\t\tvar scale = o.options.scale || \'both\'; // Default scale mode\n
\t\tvar origin = o.options.origin; // The origin of the sizing\n
\t\tvar original = {height: el.height(), width: el.width()}; // Save original\n
\t\tel.from = o.options.from || original; // Default from state\n
\t\tel.to = o.options.to || original; // Default to state\n
\t\t// Adjust\n
\t\tif (origin) { // Calculate baseline shifts\n
\t\t\tvar baseline = $.effects.getBaseline(origin, original);\n
\t\t\tel.from.top = (original.height - el.from.height) * baseline.y;\n
\t\t\tel.from.left = (original.width - el.from.width) * baseline.x;\n
\t\t\tel.to.top = (original.height - el.to.height) * baseline.y;\n
\t\t\tel.to.left = (original.width - el.to.width) * baseline.x;\n
\t\t};\n
\t\tvar factor = { // Set scaling factor\n
\t\t\tfrom: {y: el.from.height / original.height, x: el.from.width / original.width},\n
\t\t\tto: {y: el.to.height / original.height, x: el.to.width / original.width}\n
\t\t};\n
\t\tif (scale == \'box\' || scale == \'both\') { // Scale the css box\n
\t\t\tif (factor.from.y != factor.to.y) { // Vertical props scaling\n
\t\t\t\tprops = props.concat(vProps);\n
\t\t\t\tel.from = $.effects.setTransition(el, vProps, factor.from.y, el.from);\n
\t\t\t\tel.to = $.effects.setTransition(el, vProps, factor.to.y, el.to);\n
\t\t\t};\n
\t\t\tif (factor.from.x != factor.to.x) { // Horizontal props scaling\n
\t\t\t\tprops = props.concat(hProps);\n
\t\t\t\tel.from = $.effects.setTransition(el, hProps, factor.from.x, el.from);\n
\t\t\t\tel.to = $.effects.setTransition(el, hProps, factor.to.x, el.to);\n
\t\t\t};\n
\t\t};\n
\t\tif (scale == \'content\' || scale == \'both\') { // Scale the content\n
\t\t\tif (factor.from.y != factor.to.y) { // Vertical props scaling\n
\t\t\t\tprops = props.concat(cProps);\n
\t\t\t\tel.from = $.effects.setTransition(el, cProps, factor.from.y, el.from);\n
\t\t\t\tel.to = $.effects.setTransition(el, cProps, factor.to.y, el.to);\n
\t\t\t};\n
\t\t};\n
\t\t$.effects.save(el, restore ? props : props1); el.show(); // Save & Show\n
\t\t$.effects.createWrapper(el); // Create Wrapper\n
\t\tel.css(\'overflow\',\'hidden\').css(el.from); // Shift\n
\n
\t\t// Animate\n
\t\tif (scale == \'content\' || scale == \'both\') { // Scale the children\n
\t\t\tvProps = vProps.concat([\'marginTop\',\'marginBottom\']).concat(cProps); // Add margins/font-size\n
\t\t\thProps = hProps.concat([\'marginLeft\',\'marginRight\']); // Add margins\n
\t\t\tprops2 = props.concat(vProps).concat(hProps); // Concat\n
\t\t\tel.find("*[width]").each(function(){\n
\t\t\t\tchild = $(this);\n
\t\t\t\tif (restore) $.effects.save(child, props2);\n
\t\t\t\tvar c_original = {height: child.height(), width: child.width()}; // Save original\n
\t\t\t\tchild.from = {height: c_original.height * factor.from.y, width: c_original.width * factor.from.x};\n
\t\t\t\tchild.to = {height: c_original.height * factor.to.y, width: c_original.width * factor.to.x};\n
\t\t\t\tif (factor.from.y != factor.to.y) { // Vertical props scaling\n
\t\t\t\t\tchild.from = $.effects.setTransition(child, vProps, factor.from.y, child.from);\n
\t\t\t\t\tchild.to = $.effects.setTransition(child, vProps, factor.to.y, child.to);\n
\t\t\t\t};\n
\t\t\t\tif (factor.from.x != factor.to.x) { // Horizontal props scaling\n
\t\t\t\t\tchild.from = $.effects.setTransition(child, hProps, factor.from.x, child.from);\n
\t\t\t\t\tchild.to = $.effects.setTransition(child, hProps, factor.to.x, child.to);\n
\t\t\t\t};\n
\t\t\t\tchild.css(child.from); // Shift children\n
\t\t\t\tchild.animate(child.to, o.duration, o.options.easing, function(){\n
\t\t\t\t\tif (restore) $.effects.restore(child, props2); // Restore children\n
\t\t\t\t}); // Animate children\n
\t\t\t});\n
\t\t};\n
\n
\t\t// Animate\n
\t\tel.animate(el.to, { queue: false, duration: o.duration, easing: o.options.easing, complete: function() {\n
\t\t\tif (el.to.opacity === 0) {\n
\t\t\t\tel.css(\'opacity\', el.from.opacity);\n
\t\t\t}\n
\t\t\tif(mode == \'hide\') el.hide(); // Hide\n
\t\t\t$.effects.restore(el, restore ? props : props1); $.effects.removeWrapper(el); // Restore\n
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
            <value> <int>6903</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
