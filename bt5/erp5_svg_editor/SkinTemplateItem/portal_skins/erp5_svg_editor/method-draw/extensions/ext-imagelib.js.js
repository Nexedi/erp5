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
            <value> <string>ts52850574.26</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>ext-imagelib.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*\r\n
 * ext-imagelib.js\r\n
 *\r\n
 * Licensed under the Apache License, Version 2\r\n
 *\r\n
 * Copyright(c) 2010 Alexis Deveria\r\n
 *\r\n
 */\r\n
\r\n
methodDraw.addExtension("imagelib", function() {\r\n
\r\n
  var uiStrings = methodDraw.uiStrings;\r\n
  \r\n
  $.extend(uiStrings, {\r\n
    imagelib: {\r\n
      select_lib: \'Select an image library\',\r\n
      show_list: \'Show library list\',\r\n
      import_single: \'Import single\',\r\n
      import_multi: \'Import multiple\',\r\n
      open: \'Open as new document\'\r\n
    }\r\n
  });\r\n
\r\n
  var img_libs = [{\r\n
      name: \'Demo library (local)\',\r\n
      url: \'extensions/imagelib/index.html\',\r\n
      description: \'Demonstration library for SVG-edit on this server\'\r\n
    }, \r\n
    {\r\n
      name: \'IAN Symbol Libraries\',\r\n
      url: \'http://ian.umces.edu/symbols/catalog/svgedit/album_chooser.php\',\r\n
      description: \'Free library of illustrations\'\r\n
    }\r\n
  ];\r\n
  \r\n
  var xlinkns = "http://www.w3.org/1999/xlink";\r\n
\r\n
  function closeBrowser() {\r\n
    $(\'#imgbrowse_holder\').hide();\r\n
  }\r\n
  \r\n
  function importImage(url) {\r\n
    var newImage = svgCanvas.addSvgElementFromJson({\r\n
      "element": "image",\r\n
      "attr": {\r\n
        "x": 0,\r\n
        "y": 0,\r\n
        "width": 0,\r\n
        "height": 0,\r\n
        "id": svgCanvas.getNextId(),\r\n
        "style": "pointer-events:inherit"\r\n
      }\r\n
    });\r\n
    svgCanvas.clearSelection();\r\n
    svgCanvas.addToSelection([newImage]);\r\n
    svgCanvas.setImageURL(url);\r\n
  }\r\n
\r\n
  var mode = \'s\';\r\n
  var multi_arr = [];\r\n
  var cur_meta;\r\n
  var tranfer_stopped = false;\r\n
  var pending = {};\r\n
  \r\n
   window.addEventListener("message", function(evt) {\r\n
    // Receive postMessage data\r\n
    var response = evt.data;\r\n
    \r\n
    if(!response) {\r\n
      // Do nothing\r\n
      return;\r\n
    }\r\n
    \r\n
    var char1 = response.charAt(0);\r\n
    \r\n
    var svg_str;\r\n
    var img_str;\r\n
    \r\n
    if(char1 != "{" && tranfer_stopped) {\r\n
      tranfer_stopped = false;\r\n
      return;\r\n
    }\r\n
    \r\n
    if(char1 == \'|\') {\r\n
      var secondpos = response.indexOf(\'|\', 1);\r\n
      var id = response.substr(1, secondpos-1);\r\n
      response = response.substr(secondpos+1);\r\n
      char1 = response.charAt(0);\r\n
\r\n
    }\r\n
    \r\n
    \r\n
    // Hide possible transfer dialog box\r\n
    $(\'#dialog_box\').hide();\r\n
    \r\n
    switch (char1) {\r\n
      case \'{\':\r\n
        // Metadata\r\n
        tranfer_stopped = false;\r\n
        var cur_meta = JSON.parse(response);\r\n
        \r\n
        pending[cur_meta.id] = cur_meta;\r\n
        \r\n
        var name = (cur_meta.name || \'file\');\r\n
        \r\n
        var message = uiStrings.notification.retrieving.replace(\'%s\', name);\r\n
        \r\n
        if(mode != \'m\') {\r\n
          $.process_cancel(message, function() {\r\n
            tranfer_stopped = true;\r\n
            // Should a message be sent back to the frame?\r\n
            \r\n
            $(\'#dialog_box\').hide();\r\n
          });\r\n
        } else {\r\n
          var entry = $(\'<div>\' + message + \'</div>\').data(\'id\', cur_meta.id);\r\n
          preview.append(entry);\r\n
          cur_meta.entry = entry;\r\n
        }\r\n
        \r\n
        return;\r\n
      case \'<\':\r\n
        svg_str = true;\r\n
        break;\r\n
      case \'d\':\r\n
        if(response.indexOf(\'data:image/svg+xml\') === 0) {\r\n
          var pre = \'data:image/svg+xml;base64,\';\r\n
          var src = response.substring(pre.length);\r\n
          response = svgCanvas.Utils.decode64(src);\r\n
          svg_str = true;\r\n
          break;\r\n
        } else if(response.indexOf(\'data:image/\') === 0) {\r\n
          img_str = true;\r\n
          break;\r\n
        }\r\n
        // Else fall through\r\n
      default:\r\n
        // TODO: See if there\'s a way to base64 encode the binary data stream\r\n
//        var str = \'data:;base64,\' + svgCanvas.Utils.encode64(response, true);\r\n
      \r\n
        // Assume it\'s raw image data\r\n
//        importImage(str);\r\n
      \r\n
        // Don\'t give warning as postMessage may have been used by something else\r\n
        if(mode !== \'m\') {\r\n
          closeBrowser();\r\n
        } else {\r\n
          pending[id].entry.remove();\r\n
        }\r\n
//        $.alert(\'Unexpected data was returned: \' + response, function() {\r\n
//          if(mode !== \'m\') {\r\n
//            closeBrowser();\r\n
//          } else {\r\n
//            pending[id].entry.remove();\r\n
//          }\r\n
//        });\r\n
        return;\r\n
    }\r\n
    \r\n
    switch (mode) {\r\n
      case \'s\':\r\n
        // Import one\r\n
        if(svg_str) {\r\n
          svgCanvas.importSvgString(response);\r\n
        } else if(img_str) {\r\n
          importImage(response);\r\n
        }\r\n
        closeBrowser();\r\n
        break;\r\n
      case \'m\':\r\n
        // Import multiple\r\n
        multi_arr.push([(svg_str ? \'svg\' : \'img\'), response]);\r\n
        var cur_meta = pending[id];\r\n
        if(svg_str) {\r\n
          if(cur_meta && cur_meta.name) {\r\n
            var title = cur_meta.name;\r\n
          }  else {\r\n
            // Try to find a title\r\n
            var xml = new DOMParser().parseFromString(response, \'text/xml\').documentElement;\r\n
            var title = $(xml).children(\'title\').first().text() || \'(SVG #\' + response.length + \')\';\r\n
          }\r\n
          if(cur_meta) {\r\n
            preview.children().each(function() {\r\n
              if($(this).data(\'id\') == id) {\r\n
                if(cur_meta.preview_url) {\r\n
                  $(this).html(\'<img src="\' + cur_meta.preview_url + \'">\' + title);\r\n
                } else {\r\n
                  $(this).text(title);\r\n
                }\r\n
                submit.removeAttr(\'disabled\');\r\n
              }\r\n
            });\r\n
          } else {\r\n
            preview.append(\'<div>\'+title+\'</div>\');\r\n
            submit.removeAttr(\'disabled\');\r\n
          }\r\n
        } else {\r\n
          if(cur_meta && cur_meta.preview_url) {\r\n
            var title = cur_meta.name || \'\';\r\n
          }\r\n
          if(cur_meta && cur_meta.preview_url) {\r\n
            var entry = \'<img src="\' + cur_meta.preview_url + \'">\' + title;\r\n
          } else {\r\n
            var entry = \'<img src="\' + response + \'">\';\r\n
          }\r\n
        \r\n
          if(cur_meta) {\r\n
            preview.children().each(function() {\r\n
              if($(this).data(\'id\') == id) {\r\n
                $(this).html(entry);\r\n
                submit.removeAttr(\'disabled\');\r\n
              }\r\n
            });\r\n
          } else {\r\n
            preview.append($(\'<div>\').append(entry));\r\n
            submit.removeAttr(\'disabled\');\r\n
          }\r\n
\r\n
        }\r\n
        break;\r\n
      case \'o\':\r\n
        // Open\r\n
        if(!svg_str) break;\r\n
        methodDraw.openPrep(function(ok) {\r\n
          if(!ok) return;\r\n
          svgCanvas.clear();\r\n
          svgCanvas.setSvgString(response);\r\n
          // updateCanvas();\r\n
        });\r\n
        closeBrowser();\r\n
        break;\r\n
    }\r\n
  }, true);\r\n
  \r\n
  var preview, submit;\r\n
\r\n
  function toggleMulti(show) {\r\n
  \r\n
    $(\'#lib_framewrap, #imglib_opts\').css({right: (show ? 200 : 10)});\r\n
    if(!preview) {\r\n
      preview = $(\'<div id=imglib_preview>\').css({\r\n
        position: \'absolute\',\r\n
        top: 45,\r\n
        right: 10,\r\n
        width: 180,\r\n
        bottom: 45,\r\n
        background: \'#fff\',\r\n
        overflow: \'auto\'\r\n
      }).insertAfter(\'#lib_framewrap\');\r\n
      \r\n
      submit = $(\'<button disabled>Import selected</button>\').appendTo(\'#imgbrowse\').click(function() {\r\n
        $.each(multi_arr, function(i) {\r\n
          var type = this[0];\r\n
          var data = this[1];\r\n
          if(type == \'svg\') {\r\n
            svgCanvas.importSvgString(data);\r\n
          } else {\r\n
            importImage(data);\r\n
          }\r\n
          svgCanvas.moveSelectedElements(i*20, i*20, false);\r\n
        });\r\n
        preview.empty();\r\n
        multi_arr = [];\r\n
        $(\'#imgbrowse_holder\').hide();\r\n
      }).css({\r\n
        position: \'absolute\',\r\n
        bottom: 10,\r\n
        right: -10\r\n
      });\r\n
\r\n
    }\r\n
    \r\n
    preview.toggle(show);\r\n
    submit.toggle(show);\r\n
  }\r\n
\r\n
  function showBrowser() {\r\n
\r\n
    var browser = $(\'#imgbrowse\');\r\n
    if(!browser.length) {\r\n
      $(\'<div id=imgbrowse_holder><div id=imgbrowse class=toolbar_button>\\\r\n
      </div></div>\').insertAfter(\'#svg_docprops\');\r\n
      browser = $(\'#imgbrowse\');\r\n
\r\n
      var all_libs = uiStrings.imagelib.select_lib;\r\n
\r\n
      var lib_opts = $(\'<ul id=imglib_opts>\').appendTo(browser);\r\n
      var frame = $(\'<iframe/>\').prependTo(browser).hide().wrap(\'<div id=lib_framewrap>\');\r\n
      \r\n
      var header = $(\'<h1>\').prependTo(browser).text(all_libs).css({\r\n
        position: \'absolute\',\r\n
        top: 0,\r\n
        left: 0,\r\n
        width: \'100%\'\r\n
      });\r\n
      \r\n
      var cancel = $(\'<button>\' + uiStrings.common.cancel + \'</button>\').appendTo(browser).click(function() {\r\n
        $(\'#imgbrowse_holder\').hide();\r\n
      }).css({\r\n
        position: \'absolute\',\r\n
        top: 5,\r\n
        right: -10\r\n
      });\r\n
      \r\n
      var leftBlock = $(\'<span>\').css({position:\'absolute\',top:5,left:10}).appendTo(browser);\r\n
      \r\n
      var back = $(\'<button hidden>\' + uiStrings.imagelib.show_list + \'</button>\').appendTo(leftBlock).click(function() {\r\n
        frame.attr(\'src\', \'about:blank\').hide();\r\n
        lib_opts.show();\r\n
        header.text(all_libs);\r\n
        back.hide();\r\n
      }).css({\r\n
        \'margin-right\': 5\r\n
      }).hide();\r\n
      \r\n
      var type = $(\'<select><option value=s>\' + \r\n
      uiStrings.imagelib.import_single + \'</option><option value=m>\' +\r\n
      uiStrings.imagelib.import_multi + \'</option><option value=o>\' +\r\n
      uiStrings.imagelib.open + \'</option></select>\').appendTo(leftBlock).change(function() {\r\n
        mode = $(this).val();\r\n
        switch (mode) {\r\n
          case \'s\':\r\n
          case \'o\':\r\n
            toggleMulti(false);\r\n
            break;\r\n
          \r\n
          case \'m\':\r\n
            // Import multiple\r\n
            toggleMulti(true);\r\n
        }\r\n
      }).css({\r\n
        \'margin-top\': 10\r\n
      });\r\n
      \r\n
      cancel.prepend($.getSvgIcon(\'cancel\', true));\r\n
      back.prepend($.getSvgIcon(\'tool_imagelib\', true));\r\n
      \r\n
      $.each(img_libs, function(i, opts) {\r\n
        $(\'<li>\').appendTo(lib_opts).text(opts.name).click(function() {\r\n
          frame.attr(\'src\', opts.url).show();\r\n
          header.text(opts.name);\r\n
          lib_opts.hide();\r\n
          back.show();\r\n
        }).append(\'<span>\' + opts.description + \'</span>\');\r\n
      });\r\n
      \r\n
    } else {\r\n
      $(\'#imgbrowse_holder\').show();\r\n
    }\r\n
  }\r\n
  \r\n
  return {\r\n
    buttons: [{\r\n
      id: "tool_imagelib",\r\n
      type: "menu", // _flyout\r\n
      position: 4,\r\n
      panel: "file_menu",\r\n
      title: "Image library",\r\n
      events: {\r\n
        "mouseup": showBrowser\r\n
      }\r\n
    }],\r\n
    callback: function() {\r\n
    \r\n
      $(\'<style>\').text(\'\\\r\n
        #imgbrowse_holder {\\\r\n
          position: absolute;\\\r\n
          top: 0;\\\r\n
          left: 0;\\\r\n
          width: 100%;\\\r\n
          height: 100%;\\\r\n
          background-color: rgba(0, 0, 0, .5);\\\r\n
          z-index: 5;\\\r\n
        }\\\r\n
        \\\r\n
        #imgbrowse {\\\r\n
          position: absolute;\\\r\n
          top: 25px;\\\r\n
          left: 25px;\\\r\n
          right: 25px;\\\r\n
          bottom: 25px;\\\r\n
          min-width: 300px;\\\r\n
          min-height: 200px;\\\r\n
          background: #B0B0B0;\\\r\n
          border: 1px outset #777;\\\r\n
        }\\\r\n
        #imgbrowse h1 {\\\r\n
          font-size: 20px;\\\r\n
          margin: .4em;\\\r\n
          text-align: center;\\\r\n
        }\\\r\n
        #lib_framewrap,\\\r\n
        #imgbrowse > ul {\\\r\n
          position: absolute;\\\r\n
          top: 45px;\\\r\n
          left: 10px;\\\r\n
          right: 10px;\\\r\n
          bottom: 10px;\\\r\n
          background: white;\\\r\n
          margin: 0;\\\r\n
          padding: 0;\\\r\n
        }\\\r\n
        #imgbrowse > ul {\\\r\n
          overflow: auto;\\\r\n
        }\\\r\n
        #imgbrowse > div {\\\r\n
          border: 1px solid #666;\\\r\n
        }\\\r\n
        #imglib_preview > div {\\\r\n
          padding: 5px;\\\r\n
          font-size: 12px;\\\r\n
        }\\\r\n
        #imglib_preview img {\\\r\n
          display: block;\\\r\n
          margin: 0 auto;\\\r\n
          max-height: 100px;\\\r\n
        }\\\r\n
        #imgbrowse li {\\\r\n
          list-style: none;\\\r\n
          padding: .5em;\\\r\n
          background: #E8E8E8;\\\r\n
          border-bottom: 1px solid #B0B0B0;\\\r\n
          line-height: 1.2em;\\\r\n
          font-style: sans-serif;\\\r\n
          }\\\r\n
        #imgbrowse li > span {\\\r\n
          color: #666;\\\r\n
          font-size: 15px;\\\r\n
          display: block;\\\r\n
          }\\\r\n
        #imgbrowse li:hover {\\\r\n
          background: #FFC;\\\r\n
          cursor: pointer;\\\r\n
          }\\\r\n
        #imgbrowse iframe {\\\r\n
          width: 100%;\\\r\n
          height: 100%;\\\r\n
          border: 0;\\\r\n
        }\\\r\n
      \').appendTo(\'head\');\r\n
    }\r\n
  }\r\n
});\r\n
\r\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>12434</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
