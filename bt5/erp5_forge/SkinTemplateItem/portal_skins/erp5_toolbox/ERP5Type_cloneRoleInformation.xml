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
            <value> <string>"""Obsolete compatibility script.\n
"""\n
from Products.ERP5Type.Log import log\n
log("Obsolete script, please use BaseType_copyRoleList instead")\n
\n
print \'cloning role information from\'\n
print from_type\n
if to_type_list == ():\n
  to_type_list = (to_type,)\n
\n
print "to", to_type_list\n
\n
context.portal_types[from_type].BaseType_copyRoleList(remove_existing_roles=True,\n
                                                      portal_type_list=to_type_list)\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>from_type, to_type_list=(), to_type=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Type_cloneRoleInformation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
