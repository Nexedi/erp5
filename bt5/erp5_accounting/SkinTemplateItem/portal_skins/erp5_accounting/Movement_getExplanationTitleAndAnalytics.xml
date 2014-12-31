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
            <value> <string>request = container.REQUEST\n
movement = brain.getObject()\n
\n
explanation = movement.getExplanationValue()\n
\n
if movement.hasTitle():\n
  title = movement.getTitle()\n
else:\n
  title = explanation.getTitle()\n
\n
analytic_property_list = [explanation.getReference()]\n
\n
for property_name, property_title in request[\'analytic_column_list\']:\n
  # XXX it would be a little better to reuse editable field\n
  if property_name == \'project\':\n
    analytic_property_list.append(brain.Movement_getProjectTitle())\n
  elif property_name == \'function\':\n
    analytic_property_list.append(brain.Movement_getFunctionTitle())\n
  elif property_name == \'funding\':\n
    analytic_property_list.append(brain.Movement_getFundingTitle())\n
  else:\n
    analytic_property_list.append(movement.getProperty(property_name))\n
\n
return "%s\\n%s" % (title, \', \'.join([x for x in analytic_property_list if x]))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>brain, selection=None, **kwd</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Movement_getExplanationTitleAndAnalytics</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
