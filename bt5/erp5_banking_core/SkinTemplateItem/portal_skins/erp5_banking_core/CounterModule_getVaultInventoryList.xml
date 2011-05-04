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
            <value> <string>def sortCurrencyCashList(currency_cash_list):\n
  """Sort a list of currency cash objects\n
  """\n
  def sortLines(a, b):\n
    """This method helps sorting supported by Python\'s standard function.\n
    """\n
    # First, compare the portal types.\n
    result = cmp(a.resource_portal_type, b.resource_portal_type)\n
    if result != 0:\n
      return result\n
\n
    # Second, compare the base prices (such as 1000 and 2000 Francs CFA).\n
    result = cmp(a.base_price, b.base_price)\n
    if result != 0:\n
      return result\n
\n
    # Last, compare the variations (such as the years 1994 and 2003).\n
    result = cmp(a.cash_status_title, b.cash_status_title)\n
    if result != 0:\n
      return result\n
\n
    result = cmp(getattr(a,\'date\',None),getattr(b,\'date\',None))\n
    return result\n
\n
  currency_cash_list.sort(sortLines)\n
  return currency_cash_list\n
\n
returned_value = context.CounterModule_getVaultTransactionList(**kw)\n
returned_value = sortCurrencyCashList(returned_value)\n
\n
\n
return returned_value\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CounterModule_getVaultInventoryList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
