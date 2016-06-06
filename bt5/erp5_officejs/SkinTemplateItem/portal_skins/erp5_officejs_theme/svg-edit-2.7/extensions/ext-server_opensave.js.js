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
            <value> <string>ext-server_opensave.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor, svgedit, svgCanvas, canvg, $*/\n
/*jslint eqeq: true*/\n
/*\n
 * ext-server_opensave.js\n
 *\n
 * Licensed under the MIT License\n
 *\n
 * Copyright(c) 2010 Alexis Deveria\n
 *\n
 */\n
\n
svgEditor.addExtension("server_opensave", {\n
\tcallback: function() {\n
\t\t\'use strict\';\n
\t\tfunction getFileNameFromTitle () {\n
\t\t\tvar title = svgCanvas.getDocumentTitle();\n
\t\t\t// We convert (to underscore) only those disallowed Win7 file name characters\n
\t\t\treturn $.trim(title).replace(/[\\/\\\\:*?"<>|]/g, \'_\');\n
\t\t}\n
\t\tfunction xhtmlEscape(str) {\n
\t\t\treturn str.replace(/&(?!amp;)/g, \'&amp;\').replace(/"/g, \'&quot;\').replace(/</g, \'&lt;\'); // < is actually disallowed above anyways\n
\t\t}\n
\t\tfunction clientDownloadSupport (filename, suffix, uri) {\n
\t\t\tvar a,\n
\t\t\t\tsupport = $(\'<a>\')[0].download === \'\';\n
\t\t\tif (support) {\n
\t\t\t\ta = $(\'<a>hidden</a>\').attr({download: (filename || \'image\') + suffix, href: uri}).css(\'display\', \'none\').appendTo(\'body\');\n
\t\t\t\ta[0].click();\n
\t\t\t\treturn true;\n
\t\t\t}\n
\t\t}\n
\t\tvar open_svg_action, import_svg_action, import_img_action,\n
\t\t\topen_svg_form, import_svg_form, import_img_form,\n
\t\t\tsave_svg_action = svgEditor.curConfig.extPath + \'filesave.php\',\n
\t\t\tsave_img_action = svgEditor.curConfig.extPath + \'filesave.php\',\n
\t\t\t// Create upload target (hidden iframe)\n
\t\t\tcancelled = false;\n
\t\n
\t\t$(\'<iframe name="output_frame" src="#"/>\').hide().appendTo(\'body\');\n
\t\tsvgEditor.setCustomHandlers({\n
\t\t\tsave: function(win, data) {\n
\t\t\t\tvar svg = \'<?xml version="1.0" encoding="UTF-8"?>\\n\' + data, // Firefox doesn\'t seem to know it is UTF-8 (no matter whether we use or skip the clientDownload code) despite the Content-Disposition header containing UTF-8, but adding the encoding works\n
\t\t\t\t\tfilename = getFileNameFromTitle();\n
\n
\t\t\t\tif (clientDownloadSupport(filename, \'.svg\', \'data:image/svg+xml;charset=UTF-8;base64,\' + svgedit.utilities.encode64(svg))) {\n
\t\t\t\t\treturn;\n
\t\t\t\t}\n
\n
\t\t\t\t$(\'<form>\').attr({\n
\t\t\t\t\tmethod: \'post\',\n
\t\t\t\t\taction: save_svg_action,\n
\t\t\t\t\ttarget: \'output_frame\'\n
\t\t\t\t}).append(\'<input type="hidden" name="output_svg" value="\' + xhtmlEscape(svg) + \'">\')\n
\t\t\t\t\t.append(\'<input type="hidden" name="filename" value="\' + xhtmlEscape(filename) + \'">\')\n
\t\t\t\t\t.appendTo(\'body\')\n
\t\t\t\t\t.submit().remove();\n
\t\t\t},\n
\t\t\texportImage: function(win, data) {\n
\t\t\t\tvar c,\n
\t\t\t\t\tissues = data.issues,\n
\t\t\t\t\tmimeType = data.mimeType,\n
\t\t\t\t\tquality = data.quality;\n
\t\t\t\t\n
\t\t\t\tif(!$(\'#export_canvas\').length) {\n
\t\t\t\t\t$(\'<canvas>\', {id: \'export_canvas\'}).hide().appendTo(\'body\');\n
\t\t\t\t}\n
\t\t\t\tc = $(\'#export_canvas\')[0];\n
\t\t\t\t\n
\t\t\t\tc.width = svgCanvas.contentW;\n
\t\t\t\tc.height = svgCanvas.contentH;\n
\t\t\t\tcanvg(c, data.svg, {renderCallback: function() {\n
\t\t\t\t\tvar pre, filename, suffix,\n
\t\t\t\t\t\tdatauri = quality ? c.toDataURL(mimeType, quality) : c.toDataURL(mimeType),\n
\t\t\t\t\t\t// uiStrings = svgEditor.uiStrings,\n
\t\t\t\t\t\tnote = \'\';\n
\t\t\t\t\t\n
\t\t\t\t\t// Check if there are issues\n
\t\t\t\t\tif (issues.length) {\n
\t\t\t\t\t\tpre = "\\n \\u2022 ";\n
\t\t\t\t\t\tnote += ("\\n\\n" + pre + issues.join(pre));\n
\t\t\t\t\t} \n
\t\t\t\t\t\n
\t\t\t\t\tif(note.length) {\n
\t\t\t\t\t\talert(note);\n
\t\t\t\t\t}\n
\t\t\t\t\t\n
\t\t\t\t\tfilename = getFileNameFromTitle();\n
\t\t\t\t\tsuffix = \'.\' + data.type.toLowerCase();\n
\t\t\t\t\t\n
\t\t\t\t\tif (clientDownloadSupport(filename, suffix, datauri)) {\n
\t\t\t\t\t\treturn;\n
\t\t\t\t\t}\n
\n
\t\t\t\t\t$(\'<form>\').attr({\n
\t\t\t\t\t\tmethod: \'post\',\n
\t\t\t\t\t\taction: save_img_action,\n
\t\t\t\t\t\ttarget: \'output_frame\'\n
\t\t\t\t\t}).append(\'<input type="hidden" name="output_img" value="\' + datauri + \'">\')\n
\t\t\t\t\t\t.append(\'<input type="hidden" name="mime" value="\' + mimeType + \'">\')\n
\t\t\t\t\t\t.append(\'<input type="hidden" name="filename" value="\' + xhtmlEscape(filename) + \'">\')\n
\t\t\t\t\t\t.appendTo(\'body\')\n
\t\t\t\t\t\t.submit().remove();\n
\t\t\t\t}});\n
\t\n
\t\t\t\t\n
\t\t\t}\n
\t\t});\n
\n
\t\t// Do nothing if client support is found\n
\t\tif (window.FileReader) {return;}\n
\t\t\n
\t\t// Change these to appropriate script file\n
\t\topen_svg_action = svgEditor.curConfig.extPath + \'fileopen.php?type=load_svg\';\n
\t\timport_svg_action = svgEditor.curConfig.extPath + \'fileopen.php?type=import_svg\';\n
\t\timport_img_action = svgEditor.curConfig.extPath + \'fileopen.php?type=import_img\';\n
\t\t\n
\t\t// Set up function for PHP uploader to use\n
\t\tsvgEditor.processFile = function(str64, type) {\n
\t\t\tvar xmlstr;\n
\t\t\tif (cancelled) {\n
\t\t\t\tcancelled = false;\n
\t\t\t\treturn;\n
\t\t\t}\n
\t\t\n
\t\t\t$(\'#dialog_box\').hide();\n
\n
\t\t\tif (type !== \'import_img\') {\n
\t\t\t\txmlstr = svgedit.utilities.decode64(str64);\n
\t\t\t}\n
\t\t\t\n
\t\t\tswitch (type) {\n
\t\t\t\tcase \'load_svg\':\n
\t\t\t\t\tsvgCanvas.clear();\n
\t\t\t\t\tsvgCanvas.setSvgString(xmlstr);\n
\t\t\t\t\tsvgEditor.updateCanvas();\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase \'import_svg\':\n
\t\t\t\t\tsvgCanvas.importSvgString(xmlstr);\n
\t\t\t\t\tsvgEditor.updateCanvas();\t\t\t\t\t\n
\t\t\t\t\tbreak;\n
\t\t\t\tcase \'import_img\':\n
\t\t\t\t\tsvgCanvas.setGoodImage(str64);\n
\t\t\t\t\tbreak;\n
\t\t\t}\n
\t\t};\n
\t\n
\t\t// Create upload form\n
\t\topen_svg_form = $(\'<form>\');\n
\t\topen_svg_form.attr({\n
\t\t\tenctype: \'multipart/form-data\',\n
\t\t\tmethod: \'post\',\n
\t\t\taction: open_svg_action,\n
\t\t\ttarget: \'output_frame\'\n
\t\t});\n
\t\t\n
\t\t// Create import form\n
\t\timport_svg_form = open_svg_form.clone().attr(\'action\', import_svg_action);\n
\n
\t\t// Create image form\n
\t\timport_img_form = open_svg_form.clone().attr(\'action\', import_img_action);\n
\t\t\n
\t\t// It appears necessary to rebuild this input every time a file is \n
\t\t// selected so the same file can be picked and the change event can fire.\n
\t\tfunction rebuildInput(form) {\n
\t\t\tform.empty();\n
\t\t\tvar inp = $(\'<input type="file" name="svg_file">\').appendTo(form);\n
\t\t\t\n
\t\t\t\n
\t\t\tfunction submit() {\n
\t\t\t\t// This submits the form, which returns the file data using svgEditor.processFile()\n
\t\t\t\tform.submit();\n
\t\t\t\t\n
\t\t\t\trebuildInput(form);\n
\t\t\t\t$.process_cancel("Uploading...", function() {\n
\t\t\t\t\tcancelled = true;\n
\t\t\t\t\t$(\'#dialog_box\').hide();\n
\t\t\t\t});\n
\t\t\t}\n
\t\t\t\n
\t\t\tif(form[0] == open_svg_form[0]) {\n
\t\t\t\tinp.change(function() {\n
\t\t\t\t\t// This takes care of the "are you sure" dialog box\n
\t\t\t\t\tsvgEditor.openPrep(function(ok) {\n
\t\t\t\t\t\tif(!ok) {\n
\t\t\t\t\t\t\trebuildInput(form);\n
\t\t\t\t\t\t\treturn;\n
\t\t\t\t\t\t}\n
\t\t\t\t\t\tsubmit();\n
\t\t\t\t\t});\n
\t\t\t\t});\n
\t\t\t} else {\n
\t\t\t\tinp.change(function() {\n
\t\t\t\t\t// This submits the form, which returns the file data using svgEditor.processFile()\n
\t\t\t\t\tsubmit();\n
\t\t\t\t});\n
\t\t\t}\n
\t\t}\n
\t\t\n
\t\t// Create the input elements\n
\t\trebuildInput(open_svg_form);\n
\t\trebuildInput(import_svg_form);\n
\t\trebuildInput(import_img_form);\n
\n
\t\t// Add forms to buttons\n
\t\t$("#tool_open").show().prepend(open_svg_form);\n
\t\t$("#tool_import").show().prepend(import_svg_form);\n
\t\t$("#tool_image").prepend(import_img_form);\n
\t}\n
});\n
\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>6289</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
