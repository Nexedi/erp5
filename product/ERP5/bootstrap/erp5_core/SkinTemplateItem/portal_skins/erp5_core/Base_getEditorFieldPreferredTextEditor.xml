<?xml version="1.0"?>
<ZopeData>
  <record id="1" aka="AAAAAAAAAAE=">
    <pickle>
      <global name="PythonScript" module="Products.PythonScripts.PythonScript"/>
    </pickle>
    <pickle>
      <dictionary>
        <item>
            <key> <string>Script_magic</string> </key>
            <value> <int>3</int> </value>
        </item>
        <item>
            <key> <string>_bind_names</string> </key>
            <value>
              <object>
                <klass>
                  <global name="NameAssignments" module="Shared.DC.Scripts.Bindings"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>_asgns</string> </key>
                        <value>
                          <dictionary>
                            <item>
                                <key> <string>name_container</string> </key>
                                <value> <string>container</string> </value>
                            </item>
                            <item>
                                <key> <string>name_context</string> </key>
                                <value> <string>context</string> </value>
                            </item>
                            <item>
                                <key> <string>name_m_self</string> </key>
                                <value> <string>script</string> </value>
                            </item>
                            <item>
                                <key> <string>name_subpath</string> </key>
                                <value> <string>traverse_subpath</string> </value>
                            </item>
                          </dictionary>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>_body</string> </key>
            <value> <string>"""Returns the preferred text editor and tries to take into account a default\n
content type if any.\n
The content type can also be passed, for example to use the editor in a dialog\n
that will create a document of this target content type.\n
"""\n
if not content_type:\n
  # By default, everthing related to EditorField is HTML\n
  content_type = \'text/html\'\n
  \n
  # If this document has a content type we use this information\n
  if getattr(context, \'getContentType\', None) is not None:\n
    content_type = context.getContentType() or \'text/html\'\n
\n
# If this is HTML, use preferred HTML editor or fallback to Textarea\n
if content_type == \'text/html\':\n
  return context.portal_preferences.getPreferredTextEditor() or \'text_area\'\n
\n
# Else use preferred source code editor or fallback to Textarea\n
return context.portal_preferences.getPreferredSourceCodeEditor() or \'text_area\'\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>content_type=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getEditorFieldPreferredTextEditor</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
