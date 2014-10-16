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
from Products.PythonScripts.standard import Object\n
from ZTUtils import make_query\n
portal = context.getPortalObject()\n
\n
line_list = []\n
\n
if total_price:\n
  method = context.portal_simulation.getInventoryAssetPrice\n
else:\n
  method = context.portal_simulation.getInventory\n
\n
def URLGetter(section_title,\n
              base_contribution,\n
              resource_relative_url,\n
              multiplier,\n
              total_price):\n
  def getListItemUrl(alias, index, selection_name):\n
    if alias == \'resource_title\':\n
      return \'%s/view\' % portal.restrictedTraverse(\n
                                resource_relative_url).absolute_url()\n
    return \'TaxReturn_viewDetailReportSection?%s\' % make_query(\n
                              section_title=section_title,\n
                              base_contribution_list=[base_contribution],\n
                              resource_relative_url=resource_relative_url,\n
                              multiplier=multiplier,\n
                              portal_type=list(portal_type),\n
                              delivery_portal_type=list(delivery_portal_type),\n
                              journal=alias, # XXX\n
                              total_price=total_price,)\n
  return getListItemUrl\n
\n
total = {}\n
\n
base_contribution_uid_dict = {}\n
for base_contribution in base_contribution_list:\n
  base_contribution_uid_dict[base_contribution]= (\n
        portal.portal_categories.restrictedTraverse(\n
          base_contribution).getUid())\n
\n
inventory_kw = dict(\n
        section_category=context.getGroup(base=1),\n
        strict_base_contribution_uid=base_contribution_uid_dict.values(),\n
        portal_type=portal_type,\n
        parent_portal_type=delivery_portal_type,\n
        simulation_state=(\'stopped\', \'delivered\'),\n
        mirror_date=dict(query=context.getStopDate(), range=\'ngt\'),\n
        only_accountable=only_accountable,\n
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
\n
# get all resources that have been used with this inventory parameters\n
resource_list = [brain.resource_relative_url for brain in\n
                  portal.portal_simulation.getInventoryList(\n
                        group_by_node=0,\n
                        group_by_section=0,\n
                        group_by_resource=1,\n
                        **inventory_kw)]\n
\n
for resource_relative_url in resource_list:\n
  resource = portal.restrictedTraverse(resource_relative_url)\n
  inventory_kw[\'resource_uid\'] = resource.getUid(),\n
\n
  line_dict = dict(uid=\'new_\',\n
                   resource_title=resource.getTranslatedTitle(),)\n
\n
  for idx, base_contribution in enumerate(base_contribution_list):\n
    idx = str(idx)\n
    inventory_kw[\'strict_base_contribution_uid\'] = base_contribution_uid_dict[base_contribution]\n
    amount = multiplier * method(**inventory_kw) or 0\n
\n
    line_dict[idx] = amount\n
    line_dict[\'getListItemUrl\'] = URLGetter(\n
        section_title=section_title,\n
        resource_relative_url=resource.getRelativeUrl(),\n
        base_contribution=base_contribution,\n
        multiplier=multiplier,\n
        total_price=total_price,)\n
\n
    total[idx] = total.get(idx, 0) + amount\n
\n
  line_list.append(Object(**line_dict))\n
\n
line_list.sort(key=lambda line: line.resource_title)\n
\n
container.REQUEST.set(\'TaxReturn_getSummaryReportSectionStat\', total)\n
return line_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>section_title, base_contribution_list, portal_type, delivery_portal_type, journal_list, multiplier, total_price, only_accountable, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaxReturn_getSummaryReportSectionLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
