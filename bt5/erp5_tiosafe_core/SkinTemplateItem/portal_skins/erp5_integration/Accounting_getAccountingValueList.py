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
  Find the list of objects to synchronize by calling the catalog.\n
\n
  Possibly look up a single object based on its ID, GID\n
"""\n
accounting_list = []\n
if not id:\n
  for accounting in context.accounting_module.objectValues():\n
    if accounting.getReference() and accounting.getStartDate() and accounting.getSimulationState() != \'deleted\':\n
      accounting_list.append(accounting)\n
  return accounting_list\n
accounting = getattr(context.accounting_module, id)\n
if accounting.getReference() and accounting.getStartDate() and accounting.getSimulationState() != \'deleted\':\n
  accounting_list.append(accounting)\n
return accounting_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>id="", gid=""</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Accounting_getAccountingValueList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
