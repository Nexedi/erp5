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
            <value> <string># check that every operation assigned to the counter are delivered\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
# XXX maybe raise other exception as otherwise the transition will passed even if\n
# check fail\n
\n
transaction = state_change[\'object\']\n
site = transaction.Baobab_getVaultSite(vault=transaction.getSiteValue())\n
\n
# get the current counter date\n
kwd = {\'portal_type\' : \'Counter Date\', \'simulation_state\' : \'open\', \'site_uid\' : site.getUid()}\n
date_list = [x.getObject() for x in context.portal_catalog(**kwd)]\n
current_date = None\n
if len(date_list) == 0:\n
  msg = Message(domain = \'ui\', message = \'No Counter Date found for this counter\')\n
  raise ValidationFailed, (msg,)\n
else:\n
  current_date = date_list[0].getStartDate()\n
\n
# We should not reject automatically\n
# I (seb) do not recommand this\n
#site_uid = transaction.getSiteUid()\n
\n
#operation_list_object = transaction.Baobab_getRemainingOperationList(site_uid=site_uid, date=current_date, simulation_state=[\'confirmed\',])\n
\n
#for operation in operation_list_object:\n
#  operation.reject()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, *args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>cancelRemainingOperation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
