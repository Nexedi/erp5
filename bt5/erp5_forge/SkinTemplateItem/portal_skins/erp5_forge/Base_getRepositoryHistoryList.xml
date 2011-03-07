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
            <value> <string encoding="cdata"><![CDATA[

from Products.ERP5VCS.SubversionClient import SubversionSSLTrustError\n
from Products.ERP5Type.Document import newTempBase\n
\n
portal = context.getPortalObject()\n
\n
# For now we will work only under portal_skins\n
folder_id = context.getParentValue().getId() # replace aq_parent by getParentValue\n
                                      # once portal_skins is erp5 object\n
\n
history_list = []\n
business_template = None\n
for bt in portal.portal_templates.searchFolder(installation_state=\'installed\'):\n
  # if installation_state not in catalog, we have to check manually\n
  if bt.getInstallationState() != \'installed\':\n
    continue\n
  if folder_id in bt.getTemplateSkinIdList():\n
    business_template = bt.getObject()\n
\n
if business_template is not None:\n
  repository_path = \'%s/SkinTemplateItem/portal_skins/%s/%s.xml\' % (\n
    business_template.getTitle(), folder_id, context.getId())\n
\n
  vcs_tool = business_template.getVcsTool()\n
  log_list = vcs_tool.log(repository_path, business_template)\n
  for log_dict in log_list:\n
    log_dict[\'message\'] = log_dict[\'message\'].replace(\'\\n\', \'<br/>\')\n
    temp_object = newTempBase(folder=context, id=\'1\', **log_dict)\n
    history_list.append(temp_object)\n
\n
return history_list\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getRepositoryHistoryList</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Base_getRepositoryHistoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
