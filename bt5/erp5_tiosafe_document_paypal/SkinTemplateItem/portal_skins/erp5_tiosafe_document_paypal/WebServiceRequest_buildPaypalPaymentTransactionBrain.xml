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
            <value> <string>brain_list = []\n
transaction_dict = {}\n
transaction_dict[\'title\'] = parameter_dict[\'title\']\n
transaction_dict[\'id\'] = parameter_dict[\'id\']\n
transaction_dict[\'reference\'] = parameter_dict[\'id\']\n
transaction_dict[\'start_date\'] = parameter_dict[\'start_date\']\n
#transaction_dict[\'stop_date\'] = parameter_dict[\'stop_date\']\n
\n
brain_list = [brain(context=context,\n
\t      object_type=context.getDestinationObjectType(),\n
              **transaction_dict),]\n
\n
\n
return brain_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>parameter_dict, brain</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebServiceRequest_buildPaypalPaymentTransactionBrain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
