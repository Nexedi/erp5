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
            <value> <string>context_obj = context.getObject()\n
\n
module_type   = \'Task Module\'\n
document_type = \'Task\'\n
source_project_type = [ \'Project Line\' , \'Project\']\n
\n
task_module = context.getDefaultModule(module_type)\n
\n
if context_obj.getPortalType() not in source_project_type:\n
 return context.REQUEST.RESPONSE.redirect(context.absolute_url() + \'?portal_status_message=Error:+bad+context.\')\n
\n
# this list contain all task items\n
task_items = []\n
\n
# get the user information\n
for task in listbox:\n
  if task.has_key(\'listbox_key\'):\n
    task_id = int(task[\'listbox_key\'])\n
    task_dict = {}\n
    task_dict[\'id\'] = task_id\n
    task_dict[\'title\'] = task[\'task_title\']\n
    task_dict[\'reference\'] = task[\'task_reference\']\n
    task_dict[\'description\'] = task[\'task_description\']\n
    task_dict[\'start_date\'] = task[\'task_start_date\']\n
    task_dict[\'stop_date\'] = task[\'task_stop_date\']\n
    task_dict[\'requirement\'] = task[\'task_requirement\']\n
    task_dict[\'source\'] = task[\'task_source\'] or source\n
    task_dict[\'source_section\'] = source_section\n
    task_dict[\'resource\'] = task[\'task_line_resource\'] or resource\n
    task_dict[\'quantity\'] = task[\'task_line_quantity\']\n
    task_dict[\'quantity_unit\'] = task[\'task_line_quantity_unit\'] or task_line_quantity_unit\n
    task_dict[\'source_section\'] = source_section\n
    task_dict[\'destination_decision\'] = destination_decision\n
    task_dict[\'destination_section\'] = destination_section\n
    task_dict[\'destination\'] = destination\n
    task_items.append(task_dict)\n
\n
# sort the requirements list by id to have the same order of the user\n
task_items.sort(key=lambda x: x[\'id\'])\n
\n
\n
\n
for item in task_items:\n
   \n
   if item[\'title\'] != \'\':\n
      task = task_module.newContent( portal_type = document_type\n
                                     , title = item[\'title\']\n
                                     , reference = item[\'reference\']\n
                                     , description = item[\'description\']\n
                                     , start_date = item[\'start_date\']\n
                                     , stop_date = item[\'stop_date\']\n
                                     , source = item[\'source\']\n
                                     , source_section = item[\'source_section\']\n
                                     , resource = item[\'resource\']\n
                                     , task_line_quantity = item[\'quantity\']\n
                                     , task_line_quantity_unit = item[\'quantity_unit\']\n
                                     , source_section = item[\'source_section\']\n
                                     , destination_decision = item[\'destination_decision\']\n
                                     , destination_section = item[\'destination_section\']\n
                                     , destination = item[\'destination\']\n
                                     )\n
      \n
      if item[\'reference\'] == \'\':\n
        task.setReference(\'T-\' + str(task.getId()))\n
      \n
      if item[\'requirement\'] is not None:\n
          if isinstance(item[\'requirement\'],str):\n
              task.setTaskLineRequirement(item[\'requirement\'])\n
          else:\n
              task.setTaskLineRequirementList(item[\'requirement\'])\n
      task.setSourceProjectValue(context_obj)\n
\n
# return to the project\n
return context.REQUEST.RESPONSE.redirect(context.absolute_url() + \'?portal_status_message=Tasks+added+at+Task+Module.\')\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>source, source_section, destination_decision, destination_section, destination, task_line_quantity_unit, resource, listbox=[],**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ProjectLine_generateTasks</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
