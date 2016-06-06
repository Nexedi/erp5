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
            <value> <string>ext-imagelib.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals $, svgEditor, svgedit, svgCanvas, DOMParser*/\r\n
/*jslint vars: true, eqeq: true, es5: true, todo: true */\r\n
/*\r\n
 * ext-imagelib.js\r\n
 *\r\n
 * Licensed under the MIT License\r\n
 *\r\n
 * Copyright(c) 2010 Alexis Deveria\r\n
 *\r\n
 */\r\n
\r\n
svgEditor.addExtension("imagelib", function() {\'use strict\';\r\n
\r\n
\tvar uiStrings = svgEditor.uiStrings;\r\n
\r\n
\t$.extend(uiStrings, {\r\n
\t\timagelib: {\r\n
\t\t\tselect_lib: \'Select an image library\',\r\n
\t\t\tshow_list: \'Show library list\',\r\n
\t\t\timport_single: \'Import single\',\r\n
\t\t\timport_multi: \'Import multiple\',\r\n
\t\t\topen: \'Open as new document\'\r\n
\t\t}\r\n
\t});\r\n
\r\n
\tvar img_libs = [{\r\n
\t\t\tname: \'Demo library (local)\',\r\n
\t\t\turl: svgEditor.curConfig.extPath + \'imagelib/index.html\',\r\n
\t\t\tdescription: \'Demonstration library for SVG-edit on this server\'\r\n
\t\t},\r\n
\t\t{\r\n
\t\t\tname: \'IAN Symbol Libraries\',\r\n
\t\t\turl: \'http://ian.umces.edu/symbols/catalog/svgedit/album_chooser.php\',\r\n
\t\t\tdescription: \'Free library of illustrations\'\r\n
\t\t}\r\n
\t];\r\n
\r\n
\tfunction closeBrowser() {\r\n
\t\t$(\'#imgbrowse_holder\').hide();\r\n
\t}\r\n
\r\n
\tfunction importImage(url) {\r\n
\t\tvar newImage = svgCanvas.addSvgElementFromJson({\r\n
\t\t\t"element": "image",\r\n
\t\t\t"attr": {\r\n
\t\t\t\t"x": 0,\r\n
\t\t\t\t"y": 0,\r\n
\t\t\t\t"width": 0,\r\n
\t\t\t\t"height": 0,\r\n
\t\t\t\t"id": svgCanvas.getNextId(),\r\n
\t\t\t\t"style": "pointer-events:inherit"\r\n
\t\t\t}\r\n
\t\t});\r\n
\t\tsvgCanvas.clearSelection();\r\n
\t\tsvgCanvas.addToSelection([newImage]);\r\n
\t\tsvgCanvas.setImageURL(url);\r\n
\t}\r\n
\r\n
\tvar mode = \'s\';\r\n
\tvar multi_arr = [];\r\n
\tvar cur_meta;\r\n
\tvar tranfer_stopped = false;\r\n
\tvar pending = {};\r\n
\tvar preview, submit;\r\n
\r\n
\twindow.addEventListener("message", function(evt) {\r\n
\t\t// Receive postMessage data\r\n
\t\tvar response = evt.data;\r\n
\t\t\r\n
\t\tif (!response || typeof response !== "string") { // Todo: Should namespace postMessage API for this extension and filter out here\r\n
\t\t\t// Do nothing\r\n
\t\t\treturn;\r\n
\t\t}\r\n
\t\ttry { // This block can be removed if embedAPI moves away from a string to an object (if IE9 support not needed)\r\n
\t\t\tvar res = JSON.parse(response);\r\n
\t\t\tif (res.namespace) { // Part of embedAPI communications\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t}\r\n
\t\tcatch (e) {}\r\n
\t\t\r\n
\t\tvar char1 = response.charAt(0);\r\n
\t\tvar id;\r\n
\t\tvar svg_str;\r\n
\t\tvar img_str;\r\n
\t\t\r\n
\t\tif (char1 != "{" && tranfer_stopped) {\r\n
\t\t\ttranfer_stopped = false;\r\n
\t\t\treturn;\r\n
\t\t}\r\n
\t\t\r\n
\t\tif (char1 == \'|\') {\r\n
\t\t\tvar secondpos = response.indexOf(\'|\', 1);\r\n
\t\t\tid = response.substr(1, secondpos-1);\r\n
\t\t\tresponse = response.substr(secondpos+1);\r\n
\t\t\tchar1 = response.charAt(0);\r\n
\t\t}\r\n
\t\t\r\n
\t\t\r\n
\t\t// Hide possible transfer dialog box\r\n
\t\t$(\'#dialog_box\').hide();\r\n
\t\tvar entry, cur_meta;\r\n
\t\tswitch (char1) {\r\n
\t\t\tcase \'{\':\r\n
\t\t\t\t// Metadata\r\n
\t\t\t\ttranfer_stopped = false;\r\n
\t\t\t\tcur_meta = JSON.parse(response);\r\n
\t\t\t\t\r\n
\t\t\t\tpending[cur_meta.id] = cur_meta;\r\n
\t\t\t\t\r\n
\t\t\t\tvar name = (cur_meta.name || \'file\');\r\n
\t\t\t\t\r\n
\t\t\t\tvar message = uiStrings.notification.retrieving.replace(\'%s\', name);\r\n
\t\t\t\t\r\n
\t\t\t\tif (mode != \'m\') {\r\n
\t\t\t\t\t$.process_cancel(message, function() {\r\n
\t\t\t\t\t\ttranfer_stopped = true;\r\n
\t\t\t\t\t\t// Should a message be sent back to the frame?\r\n
\t\t\t\t\t\t\r\n
\t\t\t\t\t\t$(\'#dialog_box\').hide();\r\n
\t\t\t\t\t});\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tentry = $(\'<div>\' + message + \'</div>\').data(\'id\', cur_meta.id);\r\n
\t\t\t\t\tpreview.append(entry);\r\n
\t\t\t\t\tcur_meta.entry = entry;\r\n
\t\t\t\t}\r\n
\t\t\t\t\r\n
\t\t\t\treturn;\r\n
\t\t\tcase \'<\':\r\n
\t\t\t\tsvg_str = true;\r\n
\t\t\t\tbreak;\r\n
\t\t\tcase \'d\':\r\n
\t\t\t\tif (response.indexOf(\'data:image/svg+xml\') === 0) {\r\n
\t\t\t\t\tvar pre = \'data:image/svg+xml;base64,\';\r\n
\t\t\t\t\tvar src = response.substring(pre.length);\r\n
\t\t\t\t\tresponse = svgedit.utilities.decode64(src);\r\n
\t\t\t\t\tsvg_str = true;\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t} else if (response.indexOf(\'data:image/\') === 0) {\r\n
\t\t\t\t\timg_str = true;\r\n
\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t\t// Else fall through\r\n
\t\t\tdefault:\r\n
\t\t\t\t// TODO: See if there\'s a way to base64 encode the binary data stream\r\n
//\t\t\t\tvar str = \'data:;base64,\' + svgedit.utilities.encode64(response, true);\r\n
\t\t\t\r\n
\t\t\t\t// Assume it\'s raw image data\r\n
//\t\t\t\timportImage(str);\r\n
\t\t\t\r\n
\t\t\t\t// Don\'t give warning as postMessage may have been used by something else\r\n
\t\t\t\tif (mode !== \'m\') {\r\n
\t\t\t\t\tcloseBrowser();\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tpending[id].entry.remove();\r\n
\t\t\t\t}\r\n
//\t\t\t\t$.alert(\'Unexpected data was returned: \' + response, function() {\r\n
//\t\t\t\t\tif (mode !== \'m\') {\r\n
//\t\t\t\t\t\tcloseBrowser();\r\n
//\t\t\t\t\t} else {\r\n
//\t\t\t\t\t\tpending[id].entry.remove();\r\n
//\t\t\t\t\t}\r\n
//\t\t\t\t});\r\n
\t\t\t\treturn;\r\n
\t\t}\r\n
\t\t\r\n
\t\tswitch (mode) {\r\n
\t\t\tcase \'s\':\r\n
\t\t\t\t// Import one\r\n
\t\t\t\tif (svg_str) {\r\n
\t\t\t\t\tsvgCanvas.importSvgString(response);\r\n
\t\t\t\t} else if (img_str) {\r\n
\t\t\t\t\timportImage(response);\r\n
\t\t\t\t}\r\n
\t\t\t\tcloseBrowser();\r\n
\t\t\t\tbreak;\r\n
\t\t\tcase \'m\':\r\n
\t\t\t\t// Import multiple\r\n
\t\t\t\tmulti_arr.push([(svg_str ? \'svg\' : \'img\'), response]);\r\n
\t\t\t\tvar title;\r\n
\t\t\t\tcur_meta = pending[id];\r\n
\t\t\t\tif (svg_str) {\r\n
\t\t\t\t\tif (cur_meta && cur_meta.name) {\r\n
\t\t\t\t\t\ttitle = cur_meta.name;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t// Try to find a title\r\n
\t\t\t\t\t\tvar xml = new DOMParser().parseFromString(response, \'text/xml\').documentElement;\r\n
\t\t\t\t\t\ttitle = $(xml).children(\'title\').first().text() || \'(SVG #\' + response.length + \')\';\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (cur_meta) {\r\n
\t\t\t\t\t\tpreview.children().each(function() {\r\n
\t\t\t\t\t\t\tif ($(this).data(\'id\') == id) {\r\n
\t\t\t\t\t\t\t\tif (cur_meta.preview_url) {\r\n
\t\t\t\t\t\t\t\t\t$(this).html(\'<img src="\' + cur_meta.preview_url + \'">\' + title);\r\n
\t\t\t\t\t\t\t\t} else {\r\n
\t\t\t\t\t\t\t\t\t$(this).text(title);\r\n
\t\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t\t\tsubmit.removeAttr(\'disabled\');\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tpreview.append(\'<div>\'+title+\'</div>\');\r\n
\t\t\t\t\t\tsubmit.removeAttr(\'disabled\');\r\n
\t\t\t\t\t}\r\n
\t\t\t\t} else {\r\n
\t\t\t\t\tif (cur_meta && cur_meta.preview_url) {\r\n
\t\t\t\t\t\ttitle = cur_meta.name || \'\';\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tif (cur_meta && cur_meta.preview_url) {\r\n
\t\t\t\t\t\tentry = \'<img src="\' + cur_meta.preview_url + \'">\' + title;\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tentry = \'<img src="\' + response + \'">\';\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\r\n
\t\t\t\t\tif (cur_meta) {\r\n
\t\t\t\t\t\tpreview.children().each(function() {\r\n
\t\t\t\t\t\t\tif ($(this).data(\'id\') == id) {\r\n
\t\t\t\t\t\t\t\t$(this).html(entry);\r\n
\t\t\t\t\t\t\t\tsubmit.removeAttr(\'disabled\');\r\n
\t\t\t\t\t\t\t}\r\n
\t\t\t\t\t\t});\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\tpreview.append($(\'<div>\').append(entry));\r\n
\t\t\t\t\t\tsubmit.removeAttr(\'disabled\');\r\n
\t\t\t\t\t}\r\n
\r\n
\t\t\t\t}\r\n
\t\t\t\tbreak;\r\n
\t\t\tcase \'o\':\r\n
\t\t\t\t// Open\r\n
\t\t\t\tif (!svg_str) {break;}\r\n
\t\t\t\tsvgEditor.openPrep(function(ok) {\r\n
\t\t\t\t\tif (!ok) {return;}\r\n
\t\t\t\t\tsvgCanvas.clear();\r\n
\t\t\t\t\tsvgCanvas.setSvgString(response);\r\n
\t\t\t\t\t// updateCanvas();\r\n
\t\t\t\t});\r\n
\t\t\t\tcloseBrowser();\r\n
\t\t\t\tbreak;\r\n
\t\t}\r\n
\t}, true);\r\n
\r\n
\tfunction toggleMulti(show) {\r\n
\t\r\n
\t\t$(\'#lib_framewrap, #imglib_opts\').css({right: (show ? 200 : 10)});\r\n
\t\tif (!preview) {\r\n
\t\t\tpreview = $(\'<div id=imglib_preview>\').css({\r\n
\t\t\t\tposition: \'absolute\',\r\n
\t\t\t\ttop: 45,\r\n
\t\t\t\tright: 10,\r\n
\t\t\t\twidth: 180,\r\n
\t\t\t\tbottom: 45,\r\n
\t\t\t\tbackground: \'#fff\',\r\n
\t\t\t\toverflow: \'auto\'\r\n
\t\t\t}).insertAfter(\'#lib_framewrap\');\r\n
\t\t\t\r\n
\t\t\tsubmit = $(\'<button disabled>Import selected</button>\')\r\n
\t\t\t\t.appendTo(\'#imgbrowse\')\r\n
\t\t\t\t.on("click touchend", function() {\r\n
\t\t\t\t$.each(multi_arr, function(i) {\r\n
\t\t\t\t\tvar type = this[0];\r\n
\t\t\t\t\tvar data = this[1];\r\n
\t\t\t\t\tif (type == \'svg\') {\r\n
\t\t\t\t\t\tsvgCanvas.importSvgString(data);\r\n
\t\t\t\t\t} else {\r\n
\t\t\t\t\t\timportImage(data);\r\n
\t\t\t\t\t}\r\n
\t\t\t\t\tsvgCanvas.moveSelectedElements(i*20, i*20, false);\r\n
\t\t\t\t});\r\n
\t\t\t\tpreview.empty();\r\n
\t\t\t\tmulti_arr = [];\r\n
\t\t\t\t$(\'#imgbrowse_holder\').hide();\r\n
\t\t\t}).css({\r\n
\t\t\t\tposition: \'absolute\',\r\n
\t\t\t\tbottom: 10,\r\n
\t\t\t\tright: -10\r\n
\t\t\t});\r\n
\r\n
\t\t}\r\n
\t\t\r\n
\t\tpreview.toggle(show);\r\n
\t\tsubmit.toggle(show);\r\n
\t}\r\n
\r\n
\tfunction showBrowser() {\r\n
\r\n
\t\tvar browser = $(\'#imgbrowse\');\r\n
\t\tif (!browser.length) {\r\n
\t\t\t$(\'<div id=imgbrowse_holder><div id=imgbrowse class=toolbar_button>\\\r\n
\t\t\t</div></div>\').insertAfter(\'#svg_docprops\');\r\n
\t\t\tbrowser = $(\'#imgbrowse\');\r\n
\r\n
\t\t\tvar all_libs = uiStrings.imagelib.select_lib;\r\n
\r\n
\t\t\tvar lib_opts = $(\'<ul id=imglib_opts>\').appendTo(browser);\r\n
\t\t\tvar frame = $(\'<iframe/>\').prependTo(browser).hide().wrap(\'<div id=lib_framewrap>\');\r\n
\t\t\t\r\n
\t\t\tvar header = $(\'<h1>\').prependTo(browser).text(all_libs).css({\r\n
\t\t\t\tposition: \'absolute\',\r\n
\t\t\t\ttop: 0,\r\n
\t\t\t\tleft: 0,\r\n
\t\t\t\twidth: \'100%\'\r\n
\t\t\t});\r\n
\t\t\t\r\n
\t\t\tvar cancel = $(\'<button>\' + uiStrings.common.cancel + \'</button>\')\r\n
\t\t\t\t.appendTo(browser)\r\n
\t\t\t\t.on("click touchend", function() {\r\n
\t\t\t\t$(\'#imgbrowse_holder\').hide();\r\n
\t\t\t}).css({\r\n
\t\t\t\tposition: \'absolute\',\r\n
\t\t\t\ttop: 5,\r\n
\t\t\t\tright: -10\r\n
\t\t\t});\r\n
\t\t\t\r\n
\t\t\tvar leftBlock = $(\'<span>\').css({position:\'absolute\',top:5,left:10}).appendTo(browser);\r\n
\t\t\t\r\n
\t\t\tvar back = $(\'<button hidden>\' + uiStrings.imagelib.show_list + \'</button>\')\r\n
\t\t\t\t.appendTo(leftBlock)\r\n
\t\t\t\t.on("click touchend", function() {\r\n
\t\t\t\tframe.attr(\'src\', \'about:blank\').hide();\r\n
\t\t\t\tlib_opts.show();\r\n
\t\t\t\theader.text(all_libs);\r\n
\t\t\t\tback.hide();\r\n
\t\t\t}).css({\r\n
\t\t\t\t\'margin-right\': 5\r\n
\t\t\t}).hide();\r\n
\t\t\t\r\n
\t\t\tvar type = $(\'<select><option value=s>\' + \r\n
\t\t\tuiStrings.imagelib.import_single + \'</option><option value=m>\' +\r\n
\t\t\tuiStrings.imagelib.import_multi + \'</option><option value=o>\' +\r\n
\t\t\tuiStrings.imagelib.open + \'</option></select>\').appendTo(leftBlock).change(function() {\r\n
\t\t\t\tmode = $(this).val();\r\n
\t\t\t\tswitch (mode) {\r\n
\t\t\t\t\tcase \'s\':\r\n
\t\t\t\t\tcase \'o\':\r\n
\t\t\t\t\t\ttoggleMulti(false);\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t\t\r\n
\t\t\t\t\tcase \'m\':\r\n
\t\t\t\t\t\t// Import multiple\r\n
\t\t\t\t\t\ttoggleMulti(true);\r\n
\t\t\t\t\t\tbreak;\r\n
\t\t\t\t}\r\n
\t\t\t}).css({\r\n
\t\t\t\t\'margin-top\': 10\r\n
\t\t\t});\r\n
\t\t\t\r\n
\t\t\tcancel.prepend($.getSvgIcon(\'cancel\', true));\r\n
\t\t\tback.prepend($.getSvgIcon(\'tool_imagelib\', true));\r\n
\t\t\t\r\n
\t\t\t$.each(img_libs, function(i, opts) {\r\n
\t\t\t\t$(\'<li>\')\r\n
\t\t\t\t\t.appendTo(lib_opts)\r\n
\t\t\t\t\t.text(opts.name)\r\n
\t\t\t\t\t.on("click touchend", function() {\r\n
\t\t\t\t\tframe.attr(\'src\', opts.url).show();\r\n
\t\t\t\t\theader.text(opts.name);\r\n
\t\t\t\t\tlib_opts.hide();\r\n
\t\t\t\t\tback.show();\r\n
\t\t\t\t}).append(\'<span>\' + opts.description + \'</span>\');\r\n
\t\t\t});\r\n
\t\t\t\r\n
\t\t} else {\r\n
\t\t\t$(\'#imgbrowse_holder\').show();\r\n
\t\t}\r\n
\t}\r\n
\t\r\n
\treturn {\r\n
\t\tsvgicons: svgEditor.curConfig.extPath + "ext-imagelib.xml",\r\n
\t\tbuttons: [{\r\n
\t\t\tid: "tool_imagelib",\r\n
\t\t\ttype: "app_menu", // _flyout\r\n
\t\t\tposition: 4,\r\n
\t\t\ttitle: "Image library",\r\n
\t\t\tevents: {\r\n
\t\t\t\t"mouseup": showBrowser\r\n
\t\t\t}\r\n
\t\t}],\r\n
\t\tcallback: function() {\r\n
\t\t\r\n
\t\t\t$(\'<style>\').text(\'\\\r\n
\t\t\t\t#imgbrowse_holder {\\\r\n
\t\t\t\t\tposition: absolute;\\\r\n
\t\t\t\t\ttop: 0;\\\r\n
\t\t\t\t\tleft: 0;\\\r\n
\t\t\t\t\twidth: 100%;\\\r\n
\t\t\t\t\theight: 100%;\\\r\n
\t\t\t\t\tbackground-color: rgba(0, 0, 0, .5);\\\r\n
\t\t\t\t\tz-index: 5;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\t\\\r\n
\t\t\t\t#imgbrowse {\\\r\n
\t\t\t\t\tposition: absolute;\\\r\n
\t\t\t\t\ttop: 25px;\\\r\n
\t\t\t\t\tleft: 25px;\\\r\n
\t\t\t\t\tright: 25px;\\\r\n
\t\t\t\t\tbottom: 25px;\\\r\n
\t\t\t\t\tmin-width: 300px;\\\r\n
\t\t\t\t\tmin-height: 200px;\\\r\n
\t\t\t\t\tbackground: #B0B0B0;\\\r\n
\t\t\t\t\tborder: 1px outset #777;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\t#imgbrowse h1 {\\\r\n
\t\t\t\t\tfont-size: 20px;\\\r\n
\t\t\t\t\tmargin: .4em;\\\r\n
\t\t\t\t\ttext-align: center;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\t#lib_framewrap,\\\r\n
\t\t\t\t#imgbrowse > ul {\\\r\n
\t\t\t\t\tposition: absolute;\\\r\n
\t\t\t\t\ttop: 45px;\\\r\n
\t\t\t\t\tleft: 10px;\\\r\n
\t\t\t\t\tright: 10px;\\\r\n
\t\t\t\t\tbottom: 10px;\\\r\n
\t\t\t\t\tbackground: white;\\\r\n
\t\t\t\t\tmargin: 0;\\\r\n
\t\t\t\t\tpadding: 0;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\t#imgbrowse > ul {\\\r\n
\t\t\t\t\toverflow: auto;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\t#imgbrowse > div {\\\r\n
\t\t\t\t\tborder: 1px solid #666;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\t#imglib_preview > div {\\\r\n
\t\t\t\t\tpadding: 5px;\\\r\n
\t\t\t\t\tfont-size: 12px;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\t#imglib_preview img {\\\r\n
\t\t\t\t\tdisplay: block;\\\r\n
\t\t\t\t\tmargin: 0 auto;\\\r\n
\t\t\t\t\tmax-height: 100px;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\t#imgbrowse li {\\\r\n
\t\t\t\t\tlist-style: none;\\\r\n
\t\t\t\t\tpadding: .5em;\\\r\n
\t\t\t\t\tbackground: #E8E8E8;\\\r\n
\t\t\t\t\tborder-bottom: 1px solid #B0B0B0;\\\r\n
\t\t\t\t\tline-height: 1.2em;\\\r\n
\t\t\t\t\tfont-style: sans-serif;\\\r\n
\t\t\t\t\t}\\\r\n
\t\t\t\t#imgbrowse li > span {\\\r\n
\t\t\t\t\tcolor: #666;\\\r\n
\t\t\t\t\tfont-size: 15px;\\\r\n
\t\t\t\t\tdisplay: block;\\\r\n
\t\t\t\t\t}\\\r\n
\t\t\t\t#imgbrowse li:hover {\\\r\n
\t\t\t\t\tbackground: #FFC;\\\r\n
\t\t\t\t\tcursor: pointer;\\\r\n
\t\t\t\t\t}\\\r\n
\t\t\t\t#imgbrowse iframe {\\\r\n
\t\t\t\t\twidth: 100%;\\\r\n
\t\t\t\t\theight: 100%;\\\r\n
\t\t\t\t\tborder: 0;\\\r\n
\t\t\t\t}\\\r\n
\t\t\t\').appendTo(\'head\');\r\n
\t\t}\r\n
\t};\r\n
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
            <value> <int>11477</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
