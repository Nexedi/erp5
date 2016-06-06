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
            <value> <string>request = context.REQUEST\n
currency_id = context.getPriceCurrencyId()\n
vault = context.getDestination()\n
\n
redirect_url = None\n
if currency_id in (None, \'\'):\n
  redirect_url = \'%s/%s?%s\' % ( context.absolute_url()\n
                              , \'view\'\n
                              , \'portal_status_message=Please+specify+a+currency.\'\n
                              )\n
if vault in (None, \'\'):\n
  redirect_url = \'%s/%s?%s\' % ( context.absolute_url()\n
                              , \'view\'\n
                              , \'portal_status_message=Please+specify+a+destination+vault.\'\n
                              )\n
if redirect_url is not None:\n
  return request.RESPONSE.redirect(redirect_url)\n
\n
\n
if currency_id == context.Baobab_getPortalReferenceCurrencyID():\n
  letter_list      = None\n
  variation_list   = context.Baobab_getResourceVintageList(coin=1, banknote=1)\n
  cash_status_list = None\n
else:\n
  letter_list      = [\'not_defined\']\n
  variation_list   = [\'not_defined\']\n
  cash_status_list = [\'not_defined\']\n
\n
cash_detail_dict = {\'line_portal_type\'           : \'Cash Inventory Line\'\n
                    , \'operation_currency\'       : context.getPriceCurrencyId()\n
                    , \'cash_status_list\'         : cash_status_list\n
                    , \'emission_letter_list\'     : letter_list\n
                    , \'variation_list\'           : variation_list\n
                    , \'currency_cash_portal_type\': None\n
                    , \'read_only\'                : False\n
                    , \'column_base_category\'     : \'variation\'\n
                    , \'use_inventory\'            : False\n
                    }\n
\n
return context.CashDelivery_generateCashDetailInputDialog( listbox              = None\n
                                         , cash_detail_dict = cash_detail_dict\n
                                         , destination          = context.getObject().absolute_url())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CashInventory_viewLineFastInputDialog</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
