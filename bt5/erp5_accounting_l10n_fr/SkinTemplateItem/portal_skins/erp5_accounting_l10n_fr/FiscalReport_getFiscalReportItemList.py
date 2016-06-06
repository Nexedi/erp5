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
            <value> <string>from Products.CMFCore.utils import getToolByName\n
\n
tool = getToolByName(context, \'portal_skins\')\n
skin_folders = tool.objectValues()\n
\n
fiscal_report_list = []\n
\n
for folder in skin_folders:\n
  folder_id = folder.id\n
  if folder_id.startswith(\'erp5_accounting_l10n_\') or folder_id.startswith(\'custom\'):\n
    # Assume all PDFForm in the folder are Fiscal Reports\n
    for object in folder.objectValues():\n
      if object.meta_type == \'ERP5 PDF Form\':\n
        fiscal_report_list.append((object.title, object.getId()))\n
\n
# Sort by title\n
fiscal_report_list.sort(lambda x,y: cmp(x[0], y[0]))\n
\n
return fiscal_report_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>FiscalReport_getFiscalReportItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
