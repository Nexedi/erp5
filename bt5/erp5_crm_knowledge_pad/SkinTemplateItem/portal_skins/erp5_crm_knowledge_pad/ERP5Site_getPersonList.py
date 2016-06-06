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
            <value> <string>MARKER = (\'\', None,)\n
portal = context.getPortalObject()\n
portal_categories = portal.portal_categories\n
\n
kw.update({\'validation_state\' :[\'validated\']})\n
\n
box_relative_url = context.REQUEST.get(\'box_relative_url\')\n
box = context.restrictedTraverse(box_relative_url)\n
preferences = box.KnowledgeBox_getDefaultPreferencesDict()\n
\n
for key in (\'role\', \'function\', \'site\'):\n
  value = preferences.get(\'preferred_%s\' %key)\n
  context.log(\'%s=%s\' %(key, value))\n
  if value not in MARKER:\n
    kw[\'%s_uid\' %key] = portal_categories.restrictedTraverse(\'%s/%s\' %(key, value)).getUid()\n
\n
return portal.portal_catalog(**kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getPersonList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
