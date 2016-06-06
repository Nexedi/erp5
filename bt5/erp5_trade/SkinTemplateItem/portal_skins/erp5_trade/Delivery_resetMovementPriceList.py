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
            <value> <string># This script sets zero to the prices of all movements, so that\n
# prices will be recalculated.\n
\n
portal = context.getPortalObject()\n
# We do not want to reset all kinds of movements (e.g. Accounting Movements).\n
portal_type_list = portal.getPortalInvoiceMovementTypeList() \\\n
  + portal.getPortalOrderMovementTypeList() \\\n
  + portal.getPortalDeliveryMovementTypeList()\n
for movement in context.getMovementList(portal_type=portal_type_list):\n
  movement.edit(price=None, base_unit_price=None)\n
\n
if not batch_mode:\n
  message = context.Base_translateString(\'Prices reset.\')\n
  return context.Base_redirect(form_id,\n
          keep_items=dict(portal_status_message=message))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', batch_mode=0, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_resetMovementPriceList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
