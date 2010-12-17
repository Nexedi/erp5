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
            <value> <string>actions_to_add = [\n
  {\'name\' : \'Immobilisation Periods\',\n
   \'id\':     \'immobilisation_periods\',\n
   \'action\' : \'Item_viewImmobilisationPeriods\',\n
   \'condition\': \'\',\n
   \'permission\': (\'View\',),\n
   \'category\': \'object_view\',\n
   \'visible\':1\n
  },\n
  {\'name\' : \'Jump to Related Amortisation Transactions\',\n
   \'id\':     \'jump_amortisation_transaction\',\n
   \'action\' : \'Item_jumpToAmortisationTransaction\',\n
   \'condition\': \'\',\n
   \'permission\': (\'View\',),\n
   \'category\': \'object_jump\',\n
   \'visible\':1\n
  },\n
]\n
\n
\n
print \'Adding Immobilisation Item Actions to Portal Type %s :\' % context.getId()\n
action_list = context.listActions()\n
for action_to_add in actions_to_add:\n
  print "- Adding Action \'%s (%s)\'... " % (action_to_add[\'id\'],action_to_add[\'name\']),\n
  found = 0\n
  for action in action_list:\n
    if getattr(action, \'id\', None) == action_to_add[\'id\']:\n
      print \'already exists\'\n
      found = 1\n
  if not found:\n
    context.addAction(**action_to_add)\n
    print "OK"\n
\n
print\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PortalType_Item_addImmobilisationActions</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
