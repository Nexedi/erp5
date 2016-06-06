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
            <value> <string># use \'id\' for embedded document, and use \'reference\' for non-embedded document.\n
# XXX the condition should be changed when we introduce Embedded Image / File portal type.\n
if brain.getValidationState() == \'embedded\':\n
  reference = brain.getId()\n
else:\n
  reference = brain.getReference()\n
format = context.getPortalObject().portal_preferences.getPreferredImageFormat()\n
return unicode("javascript:SelectFile(\'%s?format=%s\')" % (reference.replace("\'", "\\\\\'"), format), \'utf-8\')\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>brain, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>FCKeditor_getSetReferenceUrl</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
