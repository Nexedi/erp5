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
            <value> <string># retrieve a date from object and return the new id\n
if obj is None:\n
  obj = context\n
date = None\n
# first try stop date\n
if getattr(obj, \'getStopDate\', None) is not None:\n
  date = obj.getStopDate()\n
if date is None:\n
  # if none, try creation date\n
  workflow_item_list = context.Base_getWorkflowHistoryItemList(\'edit_workflow\', display=0)\n
  workflow_item_list.reverse()\n
  for workflow_item in workflow_item_list:\n
    if workflow_item.getProperty(\'action\') == "edit":\n
      date = workflow_item.getProperty(\'time\')\n
      break\n
if date is None:\n
  # else use current date\n
  from DateTime import DateTime\n
  date = DateTime()\n
\n
date = date.Date().replace(\'/\', \'\')\n
old_id = obj.getId()\n
return "%s-%s" %(date, old_id)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>obj=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_generateIdFromStopDate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
