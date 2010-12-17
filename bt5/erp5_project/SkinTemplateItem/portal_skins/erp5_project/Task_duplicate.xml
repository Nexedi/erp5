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
            <value> <string>from Products.ERP5Type.DateUtils import addToDate\n
\n
task_portal_type = \'Task\'\n
task_module = context.getDefaultModule(task_portal_type)\n
\n
cb_data = task_module.manage_copyObjects([context.getId()])\n
copied, = task_module.manage_pasteObjects(cb_data)\n
pasted_task = task_module[copied[\'new_id\']]\n
\n
# Get task dates\n
start_date = pasted_task.getStartDate()\n
stop_date = pasted_task.getStopDate()\n
duration = int(stop_date) - int(start_date)\n
second_to_add = int(next_date) - int(start_date)\n
\n
for line in pasted_task.getMovementList():\n
  # Get task line dates\n
  if line.hasStartDate():\n
    line_start_date = line.getStartDate()\n
  else:\n
    line_start_date = start_date\n
\n
  if line.hasStopDate():\n
    line_stop_date = line.getStopDate()\n
  else:\n
    line_stop_date = stop_date\n
\n
  line_duration = int(line_stop_date) - int(line_start_date)\n
  # Line dates are different from task dates\n
  next_line_start_date = addToDate(line_start_date, second=second_to_add)\n
  line.edit(\n
    start_date=next_line_start_date,\n
    stop_date=addToDate(next_line_start_date, second=line_duration),\n
  )\n
\n
pasted_task.edit(\n
  start_date=next_date,\n
  stop_date=addToDate(next_date, second=duration),\n
)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>next_date</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Task_duplicate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
