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
            <value> <string>ext-xdomain-messaging.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/**\r\n
* Should not be needed for same domain control (just call via child frame),\r\n
*  but an API common for cross-domain and same domain use can be found\r\n
*  in embedapi.js with a demo at embedapi.html\r\n
*/\r\n
/*globals svgEditor, svgCanvas*/\r\n
svgEditor.addExtension(\'xdomain-messaging\', function() {\'use strict\';\r\n
\ttry {\r\n
\t\twindow.addEventListener(\'message\', function(e) {\r\n
\t\t\t// We accept and post strings for the sake of IE9 support\r\n
\t\t\tif (typeof e.data !== \'string\' || e.data.charAt() === \'|\') {\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t\tvar cbid, name, args, message, allowedOrigins, data = JSON.parse(e.data);\r\n
\t\t\tif (!data || typeof data !== \'object\' || data.namespace !== \'svgCanvas\') {\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t\t// The default is not to allow any origins, including even the same domain or if run on a file:// URL\r\n
\t\t\t//  See config-sample.js for an example of how to configure\r\n
\t\t\tallowedOrigins = svgEditor.curConfig.allowedOrigins;\r\n
\t\t\tif (allowedOrigins.indexOf(\'*\') === -1 && allowedOrigins.indexOf(e.origin) === -1) {\r\n
\t\t\t\treturn;\r\n
\t\t\t}\r\n
\t\t\tcbid = data.id;\r\n
\t\t\tname = data.name;\r\n
\t\t\targs = data.args;\r\n
\t\t\tmessage = {\r\n
\t\t\t\tnamespace: \'svg-edit\',\r\n
\t\t\t\tid: cbid\r\n
\t\t\t};\r\n
\t\t\ttry {\r\n
\t\t\t\tmessage.result = svgCanvas[name].apply(svgCanvas, args);\r\n
\t\t\t} catch (err) {\r\n
\t\t\t\tmessage.error = err.message;\r\n
\t\t\t}\r\n
\t\t\te.source.postMessage(JSON.stringify(message), \'*\');\r\n
\t\t}, false);\r\n
\t}\r\n
\tcatch (err) {\r\n
\t\tconsole.log(\'Error with xdomain message listener: \' + err);\r\n
\t}\r\n
});\r\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1451</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
