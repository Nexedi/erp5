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
            <value> <string>anonymous_http_cache</string> </value>
        </item>
        <item>
            <key> <string>_EtagSupport__etag</string> </key>
            <value> <string>ts52850585.04</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-helloworld.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string>/*\n
 * ext-helloworld.js\n
 *\n
 * Licensed under the Apache License, Version 2\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
 \n
/* \n
  This is a very basic SVG-Edit extension. It adds a "Hello World" button in\n
  the left panel. Clicking on the button, and then the canvas will show the\n
  user the point on the canvas that was clicked on.\n
*/\n
 \n
methodDraw.addExtension("Hello World", function() {\n
\n
    return {\n
      name: "Hello World",\n
      // For more notes on how to make an icon file, see the source of\n
      // the hellorworld-icon.xml\n
      svgicons: "extensions/helloworld-icon.xml",\n
      \n
      // Multiple buttons can be added in this array\n
      buttons: [{\n
        // Must match the icon ID in helloworld-icon.xml\n
        id: "hello_world", \n
        \n
        // This indicates that the button will be added to the "mode"\n
        // button panel on the left side\n
        type: "mode", \n
        \n
        // Tooltip text\n
        title: "Say \'Hello World\'", \n
        \n
        // Events\n
        events: {\n
          \'click\': function() {\n
            // The action taken when the button is clicked on.\n
            // For "mode" buttons, any other button will \n
            // automatically be de-pressed.\n
            svgCanvas.setMode("hello_world");\n
          }\n
        }\n
      }],\n
      // This is triggered when the main mouse button is pressed down \n
      // on the editor canvas (not the tool panels)\n
      mouseDown: function() {\n
        // Check the mode on mousedown\n
        if(svgCanvas.getMode() == "hello_world") {\n
        \n
          // The returned object must include "started" with \n
          // a value of true in order for mouseUp to be triggered\n
          return {started: true};\n
        }\n
      },\n
      \n
      // This is triggered from anywhere, but "started" must have been set\n
      // to true (see above). Note that "opts" is an object with event info\n
      mouseUp: function(opts) {\n
        // Check the mode on mouseup\n
        if(svgCanvas.getMode() == "hello_world") {\n
          var zoom = svgCanvas.getZoom();\n
          \n
          // Get the actual coordinate by dividing by the zoom value\n
          var x = opts.mouse_x / zoom;\n
          var y = opts.mouse_y / zoom;\n
          \n
          var text = "Hello World!\\n\\nYou clicked here: " \n
            + x + ", " + y;\n
            \n
          // Show the text using the custom alert function\n
          $.alert(text);\n
        }\n
      }\n
    };\n
});\n
\n
</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2417</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
