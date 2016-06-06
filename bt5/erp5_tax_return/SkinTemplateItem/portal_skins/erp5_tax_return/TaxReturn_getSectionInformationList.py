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
            <value> <string>""" Return a list of sections from the tax type definition.\n
\n
XXX this script is overkill, we could directly iterate on tax return line instead.\n
"""\n
\n
tax_type_definition = context.portal_types[context.getPortalType()]\n
\n
section_list = []\n
for tax_return_line in tax_type_definition.contentValues(\n
      portal_type=\'Tax Return Line\',\n
      sort_on=(\'float_index\',),):\n
  section_list.append(  \n
    dict(section_title=tax_return_line.getTitle(),\n
         selection_params=dict(\n
           base_contribution_list=tax_return_line.getBaseContributionList(base=1),\n
           portal_type=tax_return_line.getPropertyList(\'line_portal_type\'),\n
           delivery_portal_type=tax_return_line.getPropertyList(\'delivery_portal_type\'),\n
           column_list=[item for item in enumerate(tax_return_line.getBaseContributionTranslatedTitleList())],\n
           multiplier=tax_return_line.getProperty(\'multiplier\'),\n
           total_price=tax_return_line.getProperty(\'asset_price\'),\n
           only_accountable=tax_return_line.getProperty(\'only_accountable\'),\n
           journal_list=None,\n
         )))\n
\n
return section_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaxReturn_getSectionInformationList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
