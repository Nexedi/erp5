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
\n
portal = context.getPortalObject()\n
resource = portal.restrictedTraverse(resource_relative_url)\n
\n
base_contribution_uid_dict = {}\n
for base_contribution in base_contribution_list:\n
  base_contribution_uid_dict[base_contribution]= (\n
        portal.portal_categories.restrictedTraverse(\n
          base_contribution).getUid())\n
\n
\n
total_price = 0\n
total_quantity = 0\n
\n
line_list = []\n
\n
inventory_kw = dict(strict_base_contribution_uid=base_contribution_uid_dict.values(),\n
          section_category=context.getGroup(base=1),\n
          portal_type=portal_type,\n
          simulation_state=(\'stopped\', \'delivered\'),\n
          resource_uid=resource.getUid(),\n
          mirror_date=dict(query=context.getStopDate(), range=\'ngt\'),\n
          only_accountable=False,\n
          parent_portal_type=delivery_portal_type)\n
if context.getValidationState() == \'validated\':\n
  inventory_kw[\'default_aggregate_uid\'] = context.getUid()\n
else:\n
  aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()\n
  inventory_kw[\'where_expression\'] = SQLQuery(\'(SELECT COUNT(uid) from category where \'\n
          \'base_category_uid=%s and uid=stock.uid) = 0\' % aggregate_base_category_uid)\n
\n
for brain in context.portal_simulation.getMovementHistoryList(**inventory_kw):\n
  movement = brain.getObject()\n
  transaction = movement.getParentValue()\n
  is_source = movement.getSource() == brain.node_relative_url\n
\n
  quantity = (brain.total_quantity or 0) * sign or 0\n
  price = (brain.total_price or 0) * sign or 0\n
  \n
  total_quantity += quantity\n
  total_price += price\n
\n
  line_list.append(transaction.asContext(uid=\'new_\',\n
                          title=movement.hasTitle() and\n
                                movement.getTitle() or\n
                                transaction.getTitle(),\n
                          reference=transaction.getReference(),\n
                          specific_reference=is_source and\n
                                              transaction.getSourceReference() or\n
                                              transaction.getDestinationReference(),\n
                          third_party_name=is_source and\n
                                           movement.getDestinationSectionTitle() or\n
                                           movement.getSourceSectionTitle(),\n
                          date=brain.date,\n
                          total_quantity=quantity,\n
                          total_price=price))\n
\n
container.REQUEST.set(\'TaxReturn_getDetailReportSectionStat\',\n
               dict(total_price=total_price, total_quantity=total_quantity))\n
return line_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>section_title, base_contribution_list, resource_relative_url, portal_type, delivery_portal_type, journal, sign, total_price, selection_name, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaxReturn_getDetailReportSectionLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
