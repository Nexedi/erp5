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
            <value> <string>from Products.ZSQLCatalog.SQLCatalog import SQLQuery\n
portal = context.getPortalObject()\n
\n
line_list = []\n
\n
tax_type_definition = context.portal_types[context.getPortalType()]\n
\n
for tax_return_line in tax_type_definition.contentValues(\n
      portal_type=\'Tax Return Line\',\n
      sort_on=(\'float_index\',),):\n
        \n
  if tax_return_line.getProperty(\'total_price\'):\n
    method = portal.portal_simulation.getInventoryAssetPrice\n
  else:\n
    method = portal.portal_simulation.getInventory\n
  \n
  inventory_kw = dict(\n
          section_category=context.getGroup(base=1),\n
          strict_base_contribution_uid=tax_return_line.getBaseContributionUidList(),\n
          portal_type=tax_return_line.getPropertyList(\'line_portal_type\'),\n
          parent_portal_type=tax_return_line.getPropertyList(\'delivery_portal_type\'),\n
          simulation_state=(\'stopped\', \'delivered\'),\n
          mirror_date=dict(query=context.getStopDate(), range=\'ngt\'),\n
          only_accountable=tax_return_line.getProperty(\'only_accountable\'),\n
          )\n
  \n
  if context.getValidationState() == \'validated\':\n
    inventory_kw[\'default_aggregate_uid\'] = context.getUid()\n
  else:\n
    aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()\n
    # TODO include context portal type\n
    inventory_kw[\'where_expression\'] = SQLQuery(\'(SELECT COUNT(uid) from category where \'\n
            \'base_category_uid=%s and uid=stock.uid) = 0\' % aggregate_base_category_uid)\n
            \n
  line_list.append(\n
      tax_return_line.asContext(\n
        getListItemUrl=lambda *args: None, # XXX we could leave the link for developer\n
        quantity=tax_return_line.getProperty(\'multiplier\') * method(**inventory_kw)))\n
                   \n
return line_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaxReturn_getLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
