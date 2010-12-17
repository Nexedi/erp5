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
            <value> <string encoding="cdata"><![CDATA[

# Return first listbox in a form that is enabled and not hidden\n
# Christophe Dumez <christophe@nexedi.com>\n
# This script should be used to detect a listbox without having to name it "listbox"\n
\n
if form is None:\n
  form=context\n
\n
if form.meta_type != \'ERP5 Form\':\n
  return None\n
\n
# we start with \'bottom\' because most of the time\n
# the listbox is there.\n
for group in (\'bottom\', \'center\', \'left\', \'right\'):\n
  for field in form.get_fields_in_group(group):\n
     if field.meta_type == \'PlanningBox\' and not(field[\'hidden\']) and field[\'enabled\']:\n
       return field\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getPlanningBox</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
