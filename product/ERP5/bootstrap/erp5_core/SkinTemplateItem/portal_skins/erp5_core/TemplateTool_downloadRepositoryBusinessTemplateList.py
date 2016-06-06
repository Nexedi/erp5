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
            <value> <string>REQUEST = container.REQUEST\n
RESPONSE = REQUEST.RESPONSE\n
\n
selection_name = kw[\'list_selection_name\']\n
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)\n
\n
ret_url = \'/\'.join([context.absolute_url(), REQUEST.get(\'form_id\', \'view\')])\n
\n
if len(uids) == 0:\n
  RESPONSE.redirect("%s?portal_status_message=No+Business+Template+Specified" % ret_url)\n
  return\n
\n
id_list = []\n
for uid in uids:\n
  repository, id = context.decodeRepositoryBusinessTemplateUid(uid)\n
  bt = context.download(\'/\'.join([repository, id]))\n
  id_list.append(bt.getId())\n
\n
RESPONSE.redirect("%s?portal_status_message=Business+Templates+Downloaded+As:+%s" % (ret_url, \',+\'.join(id_list)))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TemplateTool_downloadRepositoryBusinessTemplateList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
