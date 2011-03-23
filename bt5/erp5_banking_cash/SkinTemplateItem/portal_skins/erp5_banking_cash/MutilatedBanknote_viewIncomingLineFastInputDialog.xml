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
            <value> <string>cash_detail_dict = {\'line_portal_type\'           : \'Incoming Mutilated Banknote Line\'\n
                    , \'operation_currency\'       :  context.Baobab_getPortalReferenceCurrencyID()\n
                    , \'cash_status_list\'         : [\'mutilated\',]\n
                    , \'emission_letter_list\'     : [\'not_defined\',]\n
                    , \'variation_list\'           :  context.Baobab_getResourceVintageList(banknote=1)\n
                    , \'currency_cash_portal_type\': \'Banknote\'\n
                    , \'read_only\'                : False\n
                    , \'column_base_category\'     : \'variation\'\n
                    }\n
\n
return context.CashDelivery_generateCashDetailInputDialog(listbox = None\n
                                                          , cash_detail_dict = cash_detail_dict\n
                                                          , destination = context.getObject().absolute_url()\n
)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>MutilatedBanknote_viewIncomingLineFastInputDialog</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
