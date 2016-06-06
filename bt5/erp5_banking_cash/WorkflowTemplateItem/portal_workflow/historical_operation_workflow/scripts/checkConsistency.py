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
            <value> <string>from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
delivery = state_change[\'object\']\n
\n
total_cash = delivery.getTotalPrice(fast=0,portal_type=(\'Cash Delivery Line\',\'Cash Delivery Cell\'))\n
\n
if len(delivery.objectValues(portal_type="Cash Delivery Line")) == 0:\n
  msg=Message(domain=\'ui\',message=\'No resource defined.\')\n
  raise ValidationFailed, (msg,)\n
\n
if total_cash != delivery.getSourceTotalAssetPrice():\n
  msg=Message(domain=\'ui\',message=\'Amount differs from cash total.\')\n
  raise ValidationFailed, (msg,)\n
\n
historical_operation_type = delivery.getHistoricalOperationTypeValue()\n
if historical_operation_type is None:\n
  msg=Message(domain=\'ui\',message=\'You must define an historical operation type.\')\n
  raise ValidationFailed, (msg,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>checkConsistency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
