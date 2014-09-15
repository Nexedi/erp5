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
            <value> <string>if REQUEST is not None:\n
  raise\n
\n
portal = context.getPortalObject()\n
aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()\n
\n
tag = \'tax_return_set_aggregate_%s\' % context.getRelativeUrl()\n
\n
for section_info in context.TaxReturn_getSectionInformationList():\n
  selection_params = section_info[\'selection_params\']\n
\n
  base_amount_uid_list = []\n
  for base_amount_relative_url in \\\n
          selection_params[\'base_amount_relative_url_list\']:\n
    base_amount_uid_list.append(\n
          portal.portal_categories.restrictedTraverse(\n
            base_amount_relative_url).getUid())\n
\n
  # TODO: use section info instead of hardcoding portal types etc\n
  inventory_kw = dict(\n
        strict_base_contribution_uid=base_amount_uid_list,\n
        section_category=context.getGroup(base=1),\n
        portal_type=\'Invoice Line\',\n
        simulation_state=(\'stopped\', \'delivered\'),\n
        only_accountable=False,\n
        mirror_date=dict(query=context.getStopDate(), range=\'ngt\'),\n
        where_expression=\'(SELECT COUNT(uid) from category where \'\\\n
           \'base_category_uid=%s and uid=stock.uid) = 0\' % aggregate_base_category_uid,\n
        parent_portal_type=[journal[0] for journal in\n
                              selection_params[\'journal_list\']])\n
\n
  # TODO: distribute this\n
  for movement in portal.portal_simulation.getMovementHistoryList(**inventory_kw):\n
    movement.getObject().edit(activate_kw=dict(tag=tag),\n
                              aggregate_value=context)\n
\n
context.activate(after_tag=tag).getTitle()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaxReturn_setAggregateList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
