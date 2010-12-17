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
            <value> <string>"""\n
  Returns the HTML content which must be displayed by the Editor Field.\n
\n
  Unlike other fields (which should never try to generate HTML), Editor\n
  Field expects to be provided valid HTML. It is therefore the responsibility\n
  of the Default value script to provide this valid HTML.\n
"""\n
# Define default editable value\n
if editable is None:\n
  editable = context.Event_isTextContentEditable()\n
\n
# If content is editable, nothing to do\n
if editable:\n
  return context.getTextContent()\n
\n
# If not, convert it to stripped HTML (read-only)\n
return context.asStrippedHTML()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>editable=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_getEditorFieldTextContent</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
