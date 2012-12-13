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
            <value> <string>ts55407025.98</string> </value>
        </item>
        <item>
            <key> <string>__name__</string> </key>
            <value> <string>UnsavedChanges.js</string> </value>
        </item>
        <item>
            <key> <string>content_type</string> </key>
            <value> <string>application/javascript</string> </value>
        </item>
        <item>
            <key> <string>data</string> </key>
            <value> <string>function UnsavedChanges(editor) {\n
    // Keep a copy of the editor to perform any necessary functions\n
    var editor = editor;\n
\n
    // Private variable for storing the unmodified contents.  This is necessary\n
    // because whenDocReady needs a closure to reference this object.\n
    var defaultValue;\n
\n
    // Variable to allow the protector to be bypassed in the case of submit.\n
    var bypass = false;\n
\n
    var protector = function(event) {\n
        if (bypass) {\n
            return;\n
        }\n
\n
        if (defaultValue != (editor.getEditorContent ? editor.getEditorContent() : editor.outwardHtml(editor.getHTML()))) {\n
            // This needs to use _lc for multiple languages\n
            var dirty_prompt = Xinha._lc(\'You have unsaved changes in the editor\', \'UnsavedChanges\');\n
            event.returnValue = dirty_prompt;\n
            return dirty_prompt;\n
        }\n
    }\n
\n
    this.onBeforeSubmit = function() {\n
        bypass = true;\n
    }\n
\n
    // Setup to be called when the plugin is loaded.\n
    // We need a copy of the initial content for detection to work properly, so\n
    // we will setup a callback for when the document is ready to store an\n
    // unmodified copy of the content.\n
    this.onGenerate = function() {\n
        editor.whenDocReady(function () {\n
            // Copy the original, unmodified contents to check for changes\n
            defaultValue = defaultValue || (editor.getEditorContent ? editor.getEditorContent() : editor.outwardHtml(editor.getHTML()));\n
\n
            // Set up the blocker\n
            Xinha._addEvent(window, \'beforeunload\', protector);\n
        });\n
    }\n
\n
}\n
\n
// An object containing metadata for this plugin\n
UnsavedChanges._pluginInfo = {\n
    name:\'UnsavedChanges\',\n
    version:\'3.7\',\n
    developer:\'Douglas Mayle\',\n
    developer_url:\'http://douglas.mayle.org\',\n
    c_owner:\'Douglas Mayle\',\n
    sponsor:\'The Open Planning Project\',\n
    sponsor_url:\'http://topp.openplans.org\',\n
    license:\'LGPL\'\n
}\n
</string> </value>
        </item>
        <item>
            <key> <string>precondition</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>size</string> </key>
            <value> <int>1941</int> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
