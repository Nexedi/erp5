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
            <value> <string>from Products.ERP5Type.Cache import CachingMethod\n
\n
def getCurrencyList(exclude_reference_currency=0):\n
  currency_value_list = context.currency_module.objectValues()\n
  if exclude_reference_currency:\n
    reference_id = context.Baobab_getPortalReferenceCurrencyID()\n
    currency_value_list = [x for x in currency_value_list if x.getId() != reference_id]\n
  currency_list = [(\'%s - %s\' % (x.getReference(), x.getTitle()), x.getRelativeUrl())\n
    for x in currency_value_list]\n
\n
  currency_list.insert(0, (\'\',\'\'))\n
  return currency_list\n
\n
getCurrencyList = CachingMethod(getCurrencyList, id = \'CurrencyExchange_getCurrencyList\', \n
                                cache_factory = "erp5_ui_medium")\n
return getCurrencyList(exclude_reference_currency=exclude_reference_currency)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>exclude_reference_currency=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CurrencyExchange_getCurrencyList</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
