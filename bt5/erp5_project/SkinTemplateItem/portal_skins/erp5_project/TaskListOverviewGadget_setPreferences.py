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
            <value> <string>gadget_selection = context.Base_getListboxGadgetSelectionName\\\n
(context.REQUEST.get(\'box_relative_url\', \'\'))\n
\n
gadget_preference_dict = context.restrictedTraverse(context.\\\n
REQUEST.get(\'box_relative_url\', \'\')).KnowledgeBox_getDefaultPreferencesDict()\n
\n
\n
preference_destination_decision_title = (str(gadget_preference_dict.\\\n
get(\'listbox_destination_decision_title\', None) or \'\'))\n
\n
preference_source_project_title = (str(gadget_preference_dict.\\\n
get(\'listbox_source_project_title\', None) or \'\'))\n
\n
\n
context.portal_selections.setSelectionParamsFor(gadget_selection,\\\n
{\'source_project_title\': preference_source_project_title,\\\n
\'destination_decision_title\': preference_destination_decision_title})\n
\n
\n
return gadget_selection\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TaskListOverviewGadget_setPreferences</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
