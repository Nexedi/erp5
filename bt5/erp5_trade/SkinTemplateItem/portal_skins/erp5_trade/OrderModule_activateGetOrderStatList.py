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
            <value> <string>from Products.ZSQLCatalog.SQLCatalog import Query\n
\n
portal = context.getPortalObject()\n
category_tool = portal.portal_categories\n
\n
request = container.REQUEST\n
from_date = request.get(\'from_date\', None)\n
to_date = request.get(\'at_date\', None)\n
aggregation_level = request.get(\'aggregation_level\', None)\n
report_group_by = request.get(\'group_by\', None)\n
# get all category\n
incoterm = request.get(\'incoterm\', None)\n
section_category = request.get(\'section_category\', None)\n
order = request.get(\'order\', None)\n
delivery_mode = request.get(\'delivery_mode\', None)\n
\n
catalog_params = {}\n
line_params = {"portal_type" : line_portal_type}\n
# get all organisations for the selected section category\n
if section_category:\n
  group_uid = category_tool.getCategoryValue(section_category).getUid()\n
  organisation_uid_list = [x.uid for x in portal.portal_catalog(\n
                                            portal_type="Organisation",\n
                                            default_group_uid=group_uid)]\n
  if report_type == "sale":\n
    catalog_params[\'default_source_section_uid\'] = organisation_uid_list or -1\n
    line_params["mirror_section_uid"] = organisation_uid_list or -1\n
  elif report_type:\n
    catalog_params[\'default_destination_section_uid\'] = organisation_uid_list or -1\n
    line_params["section_uid"] = organisation_uid_list or -1\n
else:\n
  raise ValueError("Section category must be defined for report")\n
# add category params if defined\n
if incoterm not in (\'\', None):\n
  incoterm_uid = category_tool.incoterm.restrictedTraverse(incoterm).getUid()\n
  catalog_params[\'default_incoterm_uid\'] = incoterm_uid\n
if order not in (\'\', None):\n
  order_uid = category_tool.order.restrictedTraverse(order).getUid()\n
  catalog_params[\'default_order_uid\'] = order_uid\n
if delivery_mode not in (\'\', None):\n
  delivery_mode_uid = category_tool.delivery_mode.restrictedTraverse(delivery_mode).getUid()\n
  catalog_params[\'default_delivery_mode_uid\'] = delivery_mode_uid\n
\n
# compute sql params, we group and order by date and portal type\n
if aggregation_level == "year":\n
  date_format = "%Y"\n
elif aggregation_level == "month":\n
  date_format = "%Y-%m"\n
elif aggregation_level == "week":\n
  date_format = "%Y-%U"\n
elif aggregation_level == "day":\n
  date_format = "%Y-%m-%d"\n
\n
params = {"delivery.start_date":(from_date, to_date)}\n
query=None\n
if from_date is not None and to_date is not None:\n
  params = {"delivery.start_date":(from_date, to_date)}\n
  query = Query(range="minngt", **params)\n
elif from_date is not None:\n
  params = {"delivery.start_date":from_date}\n
  query = Query(range="min", **params)\n
elif to_date is not None:\n
  params = {"delivery.start_date":to_date}\n
  query = Query(range="ngt", **params)\n
\n
select_params = {"select_list" : [\'source_section_title\', \'destination_section_title\', \n
  \'delivery.start_date\']}\n
\n
# sort_on_list = [ (\'delivery.destination_section_uid\', \'ASC\'), (\'delivery.start_date\',\'ASC\')]\n
\n
active_process_value = portal.portal_activities.newContent(\n
  portal_type=\'Active Process\',)\n
catalog_params.update(select_params)\n
portal.portal_catalog.activate(tag=tag).searchAndActivate(\n
  method_id="OrderModule_processOrderStat",\n
  method_kw = {\'active_process\' : active_process_value.getPath(), \n
                \'line_params\' : line_params, \n
                \'date_format\' : date_format,\n
                \'report_type\' : report_type,\n
                \'report_group_by\' : report_group_by},\n
  select_method_id = \'OrderModule_filterOrderStatResul\',\n
  activate_kw = {\'priority\' : 7,\n
    \'tag\' : tag,\n
    },\n
  # All SQL Params\n
  query=query,\n
  portal_type=doc_portal_type,\n
  simulation_state=simulation_state,\n
  packet_size=1000,\n
  **catalog_params\n
  )\n
  \n
return active_process_value\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>tag, period_list, report_type, doc_portal_type, line_portal_type, simulation_state,**kw</string> </value>
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
            <value> <string>OrderModule_activateGetOrderStatList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
