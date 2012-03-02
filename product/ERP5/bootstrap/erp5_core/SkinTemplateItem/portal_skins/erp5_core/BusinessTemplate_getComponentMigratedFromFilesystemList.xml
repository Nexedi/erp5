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
            <value> <string>template_document_id_list = context.getTemplateDocumentIdList()\n
template_extension_id_list = context.getTemplateExtensionIdList()\n
template_test_id_list = context.getTemplateTestIdList()\n
if not (template_document_id_list or template_extension_id_list or template_test_id_list):\n
  return []\n
\n
component_tool = context.getPortalObject().portal_components\n
\n
from Products.ERP5Type.Document import newTempBase\n
def addLineListByType(id_list, destination_portal_type, line_list):\n
  for component_id in id_list:\n
    if getattr(component_tool, component_id, None) is not None:\n
      continue\n
\n
    line = newTempBase(context,\n
                       \'tmp_migrate_%s_%s\' % (destination_portal_type, component_id),\n
                       uid=component_id,\n
                       name=component_id,\n
                       destination_portal_type=destination_portal_type)\n
\n
    line_list.append(line)\n
\n
line_list = []\n
addLineListByType(template_document_id_list, \'Document Component\', line_list)\n
addLineListByType(template_extension_id_list, \'Extension Component\', line_list)\n
addLineListByType(template_test_id_list, \'Test Component\', line_list)\n
return line_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kwargs</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessTemplate_getComponentMigratedFromFilesystemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
