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
            <value> <string>"""\n
This scripts returns all documents related to a worklist\n
by creating a big Complex Query from each worklist\n
definition.\n
\n
Romain: this script could be a site killer, as it remove all optimisations done for worklist calculation (like sql_cache).\n
 XXX TODO: Use WorkflowTool_listActions instead, which uses optimisation and cache the results\n
      OR remove, and uses gadget instead\n
"""\n
\n
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery\n
\n
portal = context.getPortalObject()\n
action_list = portal.portal_actions.listFilteredActionsFor(context)\n
global_action_list = action_list[\'global\']\n
ordered_global_action_list = portal.getOrderedGlobalActionList(global_action_list)\n
\n
# Initialise query\n
query_list = []\n
\n
# Assemble query \n
for action in ordered_global_action_list:\n
  workflow_id = action.get(\'workflow_id\', None)\n
  worklist_id = action.get(\'worklist_id\', None)\n
  if workflow_id is not None and worklist_id is not None:\n
    # get worklist defined local roles\n
    local_roles = context.Base_getWorkflowWorklistInfo(workflow_id, worklist_id)\n
    query_dict = context.WebSite_getWorklistSettingsFor(action)\n
    if query_dict:\n
      sub_query_list = []\n
      for k, v in query_dict.items():\n
        sub_query_list.append(Query(**{k: v}))\n
      complex_query = ComplexQuery(*sub_query_list, **dict(operator="AND"))\n
      # add to query filtering by local roles as defined in worklist\n
      complex_query = portal.portal_catalog.getSecurityQuery(query=complex_query, local_roles=local_roles)\n
      query_list.append(complex_query)\n
\n
# Return empty list if nothing defined\n
if not query_list:\n
  if kw.get(\'_count\', 0):\n
    return [[0]]\n
  else:\n
    return []\n
\n
# Invoke catalog\n
query = ComplexQuery(*query_list, **dict(operator="OR"))\n
#query = portal.portal_catalog.getSecurityQuery(query)\n
#result_list = portal.portal_catalog(query=query,\n
#                                    sort_on=\'modification_date\',\n
#                                    sort_order=\'reverse\')\n
kw[\'query\'] = query\n
kw[\'sort_order\'] = \'reverse\'\n
\n
if kw.get(\'_count\', 0):\n
  del kw[\'_count\']\n
  return portal.portal_catalog.countResults(**kw)\n
\n
return portal.portal_catalog(**kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*a, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_getPendingEventInfoList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
