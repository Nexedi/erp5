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
            <value> <string>from Products.ERP5Type.Message import translateString\n
tag = \'PaymentTransactionGroup_selectPaymentTransactionList\'\n
\n
context.serialize()\n
\n
if context.getPortalObject().portal_activities.countMessageWithTag(tag,):\n
  return context.Base_redirect(form_id, keep_items=dict(portal_status_message=translateString(\n
    "Some payments are still beeing processed in the background, please retry later")))\n
\n
context.activate(tag=tag).PaymentTransactionGroup_selectPaymentTransactionLineListActive(\n
  limit=limit,\n
  start_date_range_min=start_date_range_min,\n
  start_date_range_max=start_date_range_max,\n
  sign=sign,\n
  tag=tag)\n
\n
return context.Base_redirect(form_id,\n
  keep_items=dict(portal_status_message=translateString(\'Payment selection in progress.\')))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id=\'view\', limit=None, start_date_range_min=None, start_date_range_max=None, sign=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaymentTransactionGroup_selectPaymentTransactionLineList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
