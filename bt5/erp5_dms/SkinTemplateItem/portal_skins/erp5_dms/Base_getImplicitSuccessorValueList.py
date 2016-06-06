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
  Called by document.getImplicitSuccessorValueList\n
  Gets a list of dicts containing reference and/or version and/or language\n
  and maybe some more things.\n
  Returns a list of objects.\n
\n
  dummy simple implementation - if no version, then return the newest in the chosen language\n
  or in any language if not specified\n
"""\n
my_reference = context.getReference()\n
temporary_dict = {}\n
for dic in reference_list:\n
  reference = dic.get(\'reference\')\n
  if reference is not None and reference!=my_reference:\n
    temporary_dict[reference] = None\n
\n
if not temporary_dict:\n
  return ()\n
\n
# For the present, we only use reference.\n
# Result document will be the latest version with appropriate language by user setting.)\n
return context.Base_zGetImplicitSuccessorValueList(reference_list=temporary_dict.keys())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference_list</string> </value>
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
            <value> <string>Base_getImplicitSuccessorValueList</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Get referenced by us objects</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
