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
            <value> <string>ts40515059.47</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-mathjax.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals MathJax, svgEditor, svgCanvas, $*/\n
/*jslint es5: true, todo: true, vars: true*/\n
/*\n
 * ext-mathjax.js\n
 *\n
 * Licensed under the Apache License\n
 *\n
 * Copyright(c) 2013 Jo Segaert\n
 *\n
 */\n
\n
svgEditor.addExtension("mathjax", function() {\'use strict\';\n
  // Configuration of the MathJax extention.\n
\n
  // This will be added to the head tag before MathJax is loaded.\n
  var /*mathjaxConfiguration = \'<script type="text/x-mathjax-config">\\\n
        MathJax.Hub.Config({\\\n
          extensions: ["tex2jax.js"],\\\n
\t\t\t    jax: ["input/TeX","output/SVG"],\\\n
          showProcessingMessages: true,\\\n
          showMathMenu: false,\\\n
          showMathMenuMSIE: false,\\\n
          errorSettings: {\\\n
            message: ["[Math Processing Error]"],\\\n
            style: {color: "#CC0000", "font-style":"italic"}\\\n
          },\\\n
          elements: [],\\\n
            tex2jax: {\\\n
            ignoreClass: "tex2jax_ignore2", processClass: "tex2jax_process2",\\\n
          },\\\n
          TeX: {\\\n
            extensions: ["AMSmath.js","AMSsymbols.js","noErrors.js","noUndefined.js"]\\\n
          },\\\n
          "SVG": {\\\n
          }\\\n
      });\\\n
      </script>\',*/\n
    // mathjaxSrc = \'http://cdn.mathjax.org/mathjax/latest/MathJax.js\',\n
    mathjaxSrcSecure = \'https://c328740.ssl.cf1.rackcdn.com/mathjax/latest/MathJax.js?config=TeX-AMS-MML_SVG.js\',\n
    math,\n
    locationX,\n
    locationY,\n
    mathjaxLoaded = false,\n
    uiStrings = svgEditor.uiStrings;\n
\n
  // TODO: Implement language support. Move these uiStrings to the locale files and the code to the langReady callback.\n
  $.extend(uiStrings, {\n
    mathjax: {\n
      embed_svg: \'Save as mathematics\',\n
      embed_mathml: \'Save as figure\',\n
      svg_save_warning: \'The math will be transformed into a figure is manipulatable like everything else. You will not be able to manipulate the TeX-code anymore. \',\n
      mathml_save_warning: \'Advised. The math will be saved as a figure.\',\n
      title: \'Mathematics code editor\'\n
    }\n
  });\n
\n
\n
  function saveMath() {\n
    var code = $(\'#mathjax_code_textarea\').val();\n
    // displaystyle to force MathJax NOT to use the inline style. Because it is\n
    // less fancy!\n
    MathJax.Hub.queue.Push([\'Text\', math, \'\\\\displaystyle{\' + code + \'}\']);\n
\n
    /*\n
     * The MathJax library doesn\'t want to bloat your webpage so it creates \n
     * every symbol (glymph) you need only once. These are saved in a <svg> on  \n
     * the top of your html document, just under the body tag. Each glymph has\n
     * its unique id and is saved as a <path> in the <defs> tag of the <svg>\n
     * \n
     * Then when the symbols are needed in the rest of your html document they\n
     * are refferd to by a <use> tag.\n
     * Because of bug 1076 we can\'t just grab the defs tag on the top and add it \n
     * to your formula\'s <svg> and copy the lot. So we have to replace each \n
     * <use> tag by it\'s <path>.\n
     */\n
    MathJax.Hub.queue.Push(\n
      function() {\n
        var mathjaxMath = $(\'.MathJax_SVG\');\n
        var svg = $(mathjaxMath.html());\n
        svg.find(\'use\').each(function() {\n
          var x, y, id, transform;\n
\n
          // TODO: find a less pragmatic and more elegant solution to this.\n
          if ($(this).attr(\'href\')) {\n
            id = $(this).attr(\'href\').slice(1); // Works in Chrome.\n
          } else {\n
            id = $(this).attr(\'xlink:href\').slice(1); // Works in Firefox.\n
          }\n
\n
          var glymph = $(\'#\' + id).clone().removeAttr(\'id\');\n
          x = $(this).attr(\'x\');\n
          y = $(this).attr(\'y\');\n
          transform = $(this).attr(\'transform\');\n
          if (transform && ( x || y )) {\n
            glymph.attr(\'transform\', transform + \' translate(\' + x + \',\' + y + \')\');\n
          }\n
          else if (transform) {\n
            glymph.attr(\'transform\', transform);\n
          }\n
          else if (x || y) {\n
            glymph.attr(\'transform\', \'translate(\' + x + \',\' + y + \')\');\n
          }\n
          $(this).replaceWith(glymph);\n
        });\n
        // Remove the style tag because it interferes with SVG-Edit.\n
        svg.removeAttr(\'style\');\n
        svg.attr(\'xmlns\', \'http://www.w3.org/2000/svg\');\n
        svgCanvas.importSvgString($(\'<div>\').append(svg.clone()).html(), true);\n
        svgCanvas.ungroupSelectedElement();\n
        // TODO: To undo the adding of the Formula you now have to undo twice.\n
        // This should only be once!\n
        svgCanvas.moveSelectedElements(locationX, locationY, true);\n
      }\n
    );\n
  }\n
\n
  return {\n
    name: "MatJax",\n
    svgicons: svgEditor.curConfig.extPath + "mathjax-icons.xml",\n
    buttons: [{\n
        id: "tool_mathjax",\n
        type: "mode",\n
        title: "Add Mathematics",\n
        events: {\n
          \'click\': function() {\n
            // Only load Mathjax when needed, we don\'t want to strain Svg-Edit any more. \n
            // From this point on it is very probable that it will be needed, so load it.\n
            if (mathjaxLoaded === false) {\n
\n
              $(\'<div id="mathjax">\\\n
                <!-- Here is where MathJax creates the math -->\\\n
                  <div id="mathjax_creator" class="tex2jax_process" style="display:none">\\\n
                    $${}$$\\\n
                  </div>\\\n
                  <div id="mathjax_overlay"></div>\\\n
                  <div id="mathjax_container">\\\n
                    <div id="tool_mathjax_back" class="toolbar_button">\\\n
                      <button id="tool_mathjax_save">OK</button>\\\n
                      <button id="tool_mathjax_cancel">Cancel</button>\\\n
                    </div>\\\n
                    <fieldset>\\\n
                      <legend id="mathjax_legend">Mathematics Editor</legend>\\\n
                      <label>\\\n
                        <span id="mathjax_explication">Please type your mathematics in \\\n
                        <a href="http://en.wikipedia.org/wiki/Help:Displaying_a_formula" target="_blank">TeX</a> code.</span></label>\\\n
                      <textarea id="mathjax_code_textarea" spellcheck="false"></textarea>\\\n
                    </fieldset>\\\n
                  </div>\\\n
                </div>\'\n
                ).insertAfter(\'#svg_prefs\').hide();\n
\n
              // Make the MathEditor draggable.\n
              $(\'#mathjax_container\').draggable({cancel: \'button,fieldset\', containment: \'window\'});\n
\n
              // Add functionality and picture to cancel button.\n
              $(\'#tool_mathjax_cancel\').prepend($.getSvgIcon(\'cancel\', true))\n
                .on("click touched", function() {\n
                $(\'#mathjax\').hide();\n
              });\n
\n
              // Add functionality and picture to the save button.\n
              $(\'#tool_mathjax_save\').prepend($.getSvgIcon(\'ok\', true))\n
                .on("click touched", function() {\n
                saveMath();\n
                $(\'#mathjax\').hide();\n
              });\n
\n
              // MathJax preprocessing has to ignore most of the page.\n
              $(\'body\').addClass(\'tex2jax_ignore\');\n
\n
              // Now get (and run) the MathJax Library.\n
              $.getScript(mathjaxSrcSecure)\n
                .done(function(script, textStatus) {\n
\n
                // When MathJax is loaded get the div where the math will be rendered.\n
                MathJax.Hub.queue.Push(function() {\n
                  math = MathJax.Hub.getAllJax(\'#mathjax_creator\')[0];\n
                  console.log(math);\n
                  mathjaxLoaded = true;\n
                  console.log(\'MathJax Loaded\');\n
                });\n
\n
              })\n
                // If it fails.\n
                .fail(function() {\n
                console.log("Failed loadeing MathJax.");\n
                $.alert("Failed loading MathJax. You will not be able to change the mathematics.");\n
              });\n
            }\n
            // Set the mode.\n
            svgCanvas.setMode("mathjax");\n
          }\n
        }\n
      }],\n
    \n
    mouseDown: function() {\n
      if (svgCanvas.getMode() === "mathjax") {\n
        return {started: true};\n
      }\n
    },\n
    mouseUp: function(opts) {\n
      if (svgCanvas.getMode() === "mathjax") {\n
        // Get the coordinates from your mouse.\n
        var zoom = svgCanvas.getZoom();\n
        // Get the actual coordinate by dividing by the zoom value\n
        locationX = opts.mouse_x / zoom;\n
        locationY = opts.mouse_y / zoom;\n
\n
        $(\'#mathjax\').show();\n
        return {started: false}; // Otherwise the last selected object dissapears.\n
      }\n
    },\n
    callback: function() {\n
      $(\'<style>\').text(\'\\\n
\t\t\t\t#mathjax fieldset{\\\n
\t\t\t\t\tpadding: 5px;\\\n
\t\t\t\t\tmargin: 5px;\\\n
\t\t\t\t\tborder: 1px solid #DDD;\\\n
\t\t\t\t}\\\n
\t\t\t\t#mathjax label{\\\n
\t\t\t\t\tdisplay: block;\\\n
\t\t\t\t\tmargin: .5em;\\\n
\t\t\t\t}\\\n
\t\t\t\t#mathjax legend {\\\n
\t\t\t\t\tmax-width:195px;\\\n
\t\t\t\t}\\\n
\t\t\t\t#mathjax_overlay {\\\n
\t\t\t\t\tposition: absolute;\\\n
\t\t\t\t\ttop: 0;\\\n
\t\t\t\t\tleft: 0;\\\n
\t\t\t\t\tright: 0;\\\n
\t\t\t\t\tbottom: 0;\\\n
\t\t\t\t\tbackground-color: black;\\\n
\t\t\t\t\topacity: 0.6;\\\n
\t\t\t\t\tz-index: 20000;\\\n
\t\t\t\t}\\\n
\t\t\t\t\\\n
\t\t\t\t#mathjax_container {\\\n
\t\t\t\t\tposition: absolute;\\\n
\t\t\t\t\ttop: 50px;\\\n
\t\t\t\t\tpadding: 10px;\\\n
\t\t\t\t\tbackground-color: #B0B0B0;\\\n
\t\t\t\t\tborder: 1px outset #777;\\\n
\t\t\t\t\topacity: 1.0;\\\n
\t\t\t\t\tfont-family: Verdana, Helvetica, sans-serif;\\\n
\t\t\t\t\tfont-size: .8em;\\\n
\t\t\t\t\tz-index: 20001;\\\n
\t\t\t\t}\\\n
\t\t\t\t\\\n
\t\t\t\t#tool_mathjax_back {\\\n
\t\t\t\t\tmargin-left: 1em;\\\n
\t\t\t\t\toverflow: auto;\\\n
\t\t\t\t}\\\n
\t\t\t\t\\\n
\t\t\t\t#mathjax_legend{\\\n
\t\t\t\t\tfont-weight: bold;\\\n
\t\t\t\t\tfont-size:1.1em;\\\n
\t\t\t\t}\\\n
\t\t\t\t\\\n
\t\t\t\t#mathjax_code_textarea {\\\\n\\\n
          margin: 5px .7em;\\\n
\t\t\t\t\toverflow: hidden;\\\n
          width: 416px;\\\n
\t\t\t\t\tdisplay: block;\\\n
\t\t\t\t\theight: 100px;\\\n
\t\t\t\t}\\\n
\t\t\t\').appendTo(\'head\');\n
\n
      // Add the MathJax configuration.\n
      //$(mathjaxConfiguration).appendTo(\'head\');\n
    }\n
  };\n
});\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>9534</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
