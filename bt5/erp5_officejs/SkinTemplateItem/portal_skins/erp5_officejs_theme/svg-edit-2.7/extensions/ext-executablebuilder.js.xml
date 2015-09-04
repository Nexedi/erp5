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
            <value> <string>ext-executablebuilder.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string encoding="cdata"><![CDATA[

/*globals svgEditor*/\n
/*\n
Depends on Firefox add-on and executables from https://github.com/brettz9/webappfind\n
\n
Todos:\n
1. See WebAppFind Readme for SVG-related todos\n
*/\n
(function () {\'use strict\';\n
\n
var pathID,\n
    saveMessage = \'webapp-save\',\n
    readMessage = \'webapp-read\',\n
    excludedMessages = [readMessage, saveMessage];\n
\n
window.addEventListener(\'message\', function(e) {\n
    if (e.origin !== window.location.origin || // PRIVACY AND SECURITY! (for viewing and saving, respectively)\n
        (!Array.isArray(e.data) || excludedMessages.indexOf(e.data[0]) > -1) // Validate format and avoid our post below\n
    ) {\n
        return;\n
    }\n
    var svgString,\n
        messageType = e.data[0];\n
    switch (messageType) {\n
        case \'webapp-view\':\n
            // Populate the contents\n
            pathID = e.data[1];\n
            \n
            svgString = e.data[2];\n
            svgEditor.loadFromString(svgString);\n
            \n
            /*if ($(\'#tool_save_file\')) {\n
                $(\'#tool_save_file\').disabled = false;\n
            }*/\n
            break;\n
        case \'webapp-save-end\':\n
            alert(\'save complete for pathID \' + e.data[1] + \'!\');\n
            break;\n
        default:\n
            throw \'Unexpected mode\';\n
    }\n
}, false);\n
\n
window.postMessage([readMessage], window.location.origin !== \'null\' ? window.location.origin : \'*\'); // Avoid "null" string error for file: protocol (even though file protocol not currently supported by add-on)\n
\n
svgEditor.addExtension(\'WebAppFind\', function() {\n
\n
    return {\n
        name: \'WebAppFind\',\n
        svgicons: svgEditor.curConfig.extPath + \'executablebuilder-icocreator.svg\',\n
        buttons: [{\n
            id: \'webappfind_ico_export\', // \n
            type: \'app_menu\',\n
            title: \'Export ICO Image back to Disk\',\n
            position: 4, // Before 0-based index position 4 (after the regular "Save Image (S)")\n
            events: {\n
                click: function () {\n
                    if (!pathID) { // Not ready yet as haven\'t received first payload\n
                        return;\n
                    }\n
                    window.postMessage([saveMessage, pathID, svgEditor.canvas.getSvgString()], window.location.origin);\n
                }\n
            }\n
        }]\n
    };\n
});\n
\n
}());\n


]]></string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>2257</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
