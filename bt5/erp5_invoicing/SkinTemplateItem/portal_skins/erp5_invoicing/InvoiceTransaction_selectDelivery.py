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
            <value> <string>#\n
#  This method is used by the invoice_transaction_builder\n
# delivery builder to select the Invoice Transaction \n
# in which creating new Invoice Transaction Lines.\n
#\n
\n
deliveries_keys = {}\n
for movement in movement_list:\n
  ar = movement.getParentValue()\n
  line = None\n
\n
  # case of trade model movement\n
  if ar.getParentValue().getParentValue().getSpecialiseValue().getPortalType() == \'Trade Model Simulation Rule\':\n
    line = ar.getParentValue().getParentValue().getParentValue().getDeliveryValue()\n
\n
  # in case of invoice rule (ie. starting from Invoice)\n
  if line is None:\n
    line = ar.getParentValue().getOrderValue()\n
\n
  # in case of invoicing rule (ie. starting from Order)\n
  if line is None:\n
    line = movement.getParentValue().getParentValue().getDeliveryValue()\n
\n
  if line is not None:\n
    deliveries_keys[line.getExplanationValue()] = 1\n
\n
return filter(lambda x : x is not None, deliveries_keys.keys())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>movement_list, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>InvoiceTransaction_selectDelivery</string> </value>
        </item>
        <item>
            <key> <string>title</string> </key>
            <value> <string></string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
