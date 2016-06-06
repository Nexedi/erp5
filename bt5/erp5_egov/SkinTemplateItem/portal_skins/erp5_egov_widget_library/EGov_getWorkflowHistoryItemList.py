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
            <value> <string>request = context.REQUEST\n
from Products.ERP5Type.Document import newTempBase\n
from Products.ERP5Type.Document import newTempMappedValue\n
from AccessControl import getSecurityManager\n
\n
u=getSecurityManager().getUser()\n
connected_person = context.portal_catalog.getResultValue(portal_type=\'Person\', reference=u)\n
try:\n
  my_group = connected_person.Person_getPrimaryGroup()\n
except AttributeError:\n
  my_group = None\n
\n
\n
#workflow_id = "egov_universal_workflow"\n
\n
my_group = context.getTypeInfo().getOrganisationDirectionService()\n
\n
marker = []\n
result = []\n
i = 1\n
\n
portal_object = context.getPortalObject()\n
portal_workflow = portal_object.portal_workflow\n
workflow_id_list = [x for x, y in context.getWorkflowStateItemList()]\n
\n
\n
if not workflow_id in workflow_id_list:\n
  return []\n
# Get history\n
# XXX Compatibility\n
for history_name in [\'history\', \'building_history\', \'installation_history\']:\n
  workflow_item_list = portal_workflow.getInfoFor(ob=context, \n
                                          name=\'history\', wf_id=workflow_id)\n
  if workflow_item_list != []:\n
    break\n
\n
wf_states = portal_workflow[workflow_id].states\n
wf_transitions = portal_workflow[workflow_id].transitions\n
\n
next_serial = None\n
previous_obj = None\n
\n
for workflow_item in workflow_item_list:\n
  same_action = 0\n
  # XXX removing str method generate a strange bug\n
  o = newTempBase(portal_object, str(i))\n
  i += 1\n
  for key, value in workflow_item.items():\n
    # XXX Compatibility\n
    for compatibility_name in [\'building_\', \'installation_\']:\n
      if key.startswith(compatibility_name):\n
        # Display the workflow state in the state columns\n
        key = key[len(compatibility_name):]\n
    if key.endswith(\'state\'): \n
      key = \'state\'\n
      if display:\n
        value = wf_states.get(value, marker) and wf_states[value].title\n
      else:\n
        value = wf_states.get(value, marker) and wf_states[value].id\n
    if key == \'action\':\n
      action_name = value\n
      if value != \'\' and value is not None:\n
        if value == "\'edit\'":\n
          value = "edit"\n
        if display:\n
          value = wf_transitions.get(value, marker) and (wf_transitions[value].title or wf_transitions[value].actbox_name) or value\n
        else:\n
          value = wf_transitions.get(value, marker) and (wf_transitions[value].id or wf_transitions[value].actbox_name) or value\n
    if display:\n
      if key == \'error_message\' and same_type(value, \'\'):\n
        value = context.Localizer.erp5_ui.gettext(value)\n
      elif key == \'error_message\' and same_type(value, []):\n
        value = \'. \'.join([\'%s\' % x for x in value])\n
      elif key == \'error_message\':\n
        value = \'%s\' % value\n
      elif same_type(value, \'\') and key in ( \'action\', \'state\' ): \n
        value = context.Localizer.erp5_ui.gettext(value)\n
    if value is marker:\n
      value = \'Does not exist\'\n
    o.setProperty(key, value)\n
  \n
  if getattr(previous_obj, \'state\', None) is not None:\n
    if previous_obj.state ==  o.state:\n
      same_action = 1\n
\n
\n
  # record current serial as "next serial" for the previous revision\n
  if next_serial is not None:\n
    previous_obj.setProperty(\'next_serial\', o.serial)\n
  next_serial = getattr(o, \'serial\', None)\n
  previous_obj = o\n
  person = context.portal_catalog.getResultValue(portal_type=\'Person\', reference=o.actor)\n
  try:\n
    group = person.Person_getPrimaryGroup()\n
  except AttributeError:\n
    group = None\n
\n
  if not same_action:\n
    if group and my_group : \n
      if group.startswith(my_group) or action_name in [\'pending\', \'submit_draft\']:\n
        result.append(o)\n
    elif action_name in [\'pending\', \'submit_draft\']:\n
      result.append(o)\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>workflow_id, display=1, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Anonymous</string>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Associate</string>
                <string>Auditor</string>
                <string>Authenticated</string>
                <string>Author</string>
                <string>Manager</string>
                <string>Member</string>
                <string>Owner</string>
                <string>Reviewer</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EGov_getWorkflowHistoryItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
