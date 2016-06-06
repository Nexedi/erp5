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
            <value> <string>batch_size = 100\n
priority = 1\n
\n
activate_kw = dict(tag=tag, priority=priority)\n
\n
aggregate = context.getRelativeUrl()\n
\n
payment_relative_url_list = [brain.relative_url for brain\n
  in context.PaymentTransactionGroup_getGroupablePaymentTransactionLineList(\n
      limit=limit,\n
      start_date_range_min=start_date_range_min,\n
      start_date_range_max=start_date_range_max,\n
      sign=sign,)]\n
\n
object_list_len = len(payment_relative_url_list)\n
activate = context.getPortalObject().portal_activities.activate\n
for i in xrange(0, object_list_len, batch_size):\n
  current_path_list = payment_relative_url_list[i:i+batch_size]\n
  activate(activity=\'SQLQueue\', activate_kw=activate_kw,).callMethodOnObjectList(\n
      current_path_list,\n
      \'PaymentTransactionLine_setAggregate\',\n
      aggregate=aggregate,\n
      activate_kw=activate_kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>limit=None, start_date_range_min=None, start_date_range_max=None, sign=None, tag=\'\'</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PaymentTransactionGroup_selectPaymentTransactionLineListActive</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
