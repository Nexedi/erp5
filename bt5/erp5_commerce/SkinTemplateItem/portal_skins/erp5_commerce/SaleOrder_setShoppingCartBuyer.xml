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
            <value> <string>"""Set connected user as shopping cart customer"""\n
if REQUEST is not None:\n
  raise RuntimeError, "You can not call this script from the URL"\n
\n
shopping_cart = context.SaleOrder_getShoppingCart()\n
\n
if person is None:\n
  person = shopping_cart.SaleOrder_getShoppingCartCustomer()\n
\n
shopping_cart.edit(destination_decision_value=person)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>person=None, REQUEST=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SaleOrder_setShoppingCartBuyer</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string>Set shopping cart customer object</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
