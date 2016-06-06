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
            <value> <string>project = context\n
reference_list = []\n
\n
# return reference if defined:\n
reference = project.getReference()\n
if reference: return reference\n
\n
# Set marker for milestone\n
project_item_type = project.getPortalType()\n
\n
# browse projects parents until base found\n
# assemble list of default reference items\n
while project.getPortalType() in ( "Project Line", "Project Milestone"):\n
  reference = project.getReference()\n
  reference_list.append(reference or str(project.getProperty(\'int_index\', \'\') or \'\') or project.getId())\n
  project = project.getParentValue()\n
  # Quick exit if some parent project defines a reference\n
  if reference:\n
    reference_list.reverse()\n
    return \'-\'.join(reference_list)\n
\n
# Add M for milestone\n
if project_item_type == "Project Milestone":\n
  reference_list.append(\'M\')\n
\n
# Append default reference (P)\n
reference_list.append(reference or \'P\')\n
reference_list.reverse()\n
return \'-\'.join(reference_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Project_getDefaultReference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
