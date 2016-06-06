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
            <value> <string>"""Convert the amounts used in the accounting transaction to the currency of the destination section\n
"""\n
portal = context.getPortalObject()\n
precision = context.getDestinationSectionValue().getPriceCurrencyValue().getQuantityPrecision()\n
line_list = context.contentValues(\n
      portal_type=portal.getPortalAccountingMovementTypeList())\n
\n
for line in line_list:\n
  section = line.getDestinationSectionValue()\n
  if section != context.getDestinationSectionValue():\n
    continue\n
  currency = line.getResourceValue()\n
  if not exchange_rate:\n
    exchange_rate = currency.getPrice(context=line.asContext(\n
                          categories=[line.getResource(base=True),\n
                                      section.getPriceCurrency(base=True)],\n
                          start_date=line.getStopDate()))\n
\n
  # redirect to previous page without doing the conversion\n
  if exchange_rate is None:\n
    return context.Base_redirect(form_id,\n
                                  keep_items=dict(\n
                portal_status_message=context.Base_translateString(\'No exchange ratio found.\')))\n
\n
  # update the corresponding price and round it according to the precision of\n
  # the converted currency\n
  line.setDestinationTotalAssetPrice(\n
       round(exchange_rate * (line.getQuantity()), precision))\n
\n
msg = context.Base_translateString(\'Price converted.\')\n
\n
return context.Base_redirect(form_id,\n
                             keep_items=dict(portal_status_message=msg))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>exchange_rate=None, form_id=\'view\'</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransaction_convertDestinationPrice</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
