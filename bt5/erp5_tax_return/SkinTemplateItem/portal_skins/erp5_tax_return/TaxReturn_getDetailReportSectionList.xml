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
            <value> <string>from Products.ERP5Form.Report import ReportSection\n
\n
portal = context.getPortalObject()\n
report_section_list = []\n
\n
inventory_kw = dict(\n
        section_category=context.getGroup(base=1),\n
        portal_type=\'Invoice Line\',\n
        simulation_state=(\'stopped\', \'delivered\'),\n
        mirror_date=dict(query=context.getStopDate(), range=\'ngt\'),\n
        only_accountable=False,)\n
\n
if context.getValidationState() == \'validated\':\n
  inventory_kw[\'default_aggregate_uid\'] = context.getUid()\n
else:\n
  aggregate_base_category_uid = portal.portal_categories.aggregate.getUid()\n
  inventory_kw[\'where_expression\'] = \'(SELECT COUNT(uid) from category where \'\\\n
          \'base_category_uid=%s and uid=stock.uid) = 0\' % aggregate_base_category_uid\n
\n
for section_info in context.TaxReturn_getSectionInformationList():\n
  section_title = section_info[\'section_title\']\n
  common_selection_params = section_info[\'selection_params\']\n
  base_amount_relative_url_list=common_selection_params[\'base_amount_relative_url_list\']\n
  \n
  base_amount_uid_list = []\n
  for base_amount_relative_url in base_amount_relative_url_list:\n
    base_amount_uid_list.append(\n
          portal.portal_categories.restrictedTraverse(\n
            base_amount_relative_url).getUid())\n
\n
  selection_params = dict(\n
                        section_title=section_title,\n
                        base_amount_relative_url_list=base_amount_relative_url_list,\n
                        sign=common_selection_params[\'sign\'],\n
                        total_price=common_selection_params[\'total_price\'], )\n
    \n
  for journal, journal_name in common_selection_params[\'journal_list\']:\n
    # get all resources that have been used with this inventory parameters\n
    resource_list = [brain.resource_relative_url for brain in\n
                      portal.portal_simulation.getInventoryList(\n
                            group_by_node=0,\n
                            group_by_section=0,\n
                            group_by_resource=1,\n
                            parent_portal_type=journal,\n
                            strict_base_contribution_uid=base_amount_uid_list,\n
                            **inventory_kw)]\n
\n
    for resource_relative_url in resource_list:\n
      resource = portal.restrictedTraverse(resource_relative_url)\n
      selection_params[\'journal\'] = journal\n
      selection_params[\'resource_relative_url\'] = resource.getRelativeUrl()\n
      selection_params[\'section_title\'] = \'%s (%s/%s)\' % (section_title,\n
                                                          journal_name,\n
                                                          resource.getTranslatedTitle())\n
      report_section_list.append(ReportSection(\n
        path=context.getPhysicalPath(),\n
        form_id=\'TaxReturn_viewDetailReportSection\',\n
        selection_name=\'tax_return_detail_report_section_selection\',\n
        selection_params=selection_params.copy()))\n
  \n
return report_section_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaxReturn_getDetailReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
