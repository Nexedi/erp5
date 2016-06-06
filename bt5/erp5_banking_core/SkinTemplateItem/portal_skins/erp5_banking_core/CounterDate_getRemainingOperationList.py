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
            <value> <string>if site is None:\n
  site = context.getSiteValue()\n
site_uid = site.getUid()\n
site_url = site.getRelativeUrl()\n
operation_list = []\n
exception_portal_type_list = [\'Foreign Check\', \'External Banking Operation\', \'Account Transfer\', \'Check Deposit\',\n
                              \'Checkbook Reception\', \'Accounting Cancellation\', \'Stop Payment\']\n
if site_uid is not None:\n
  not_closed_state_list = (\'ordered\',\'planned\',\'confirmed\',\'started\',\'stopped\', \'ready\', \'deposited\', \'received\', \'finished\')\n
  portal_type_list = [x for x in context.getPortalDeliveryTypeList()\n
                      if x not in exception_portal_type_list]\n
  document_list = context.Baobab_getRemainingOperationList(\n
                        site_uid=site_uid,\n
                        simulation_state=not_closed_state_list,\n
                        portal_type=portal_type_list)\n
  append = operation_list.append\n
  for document in document_list:\n
    # Stop Payment and Cash Movement in started state must not block counter day closing.\n
    # Mutilated Banknotes in planned state or in finished state with siege as source must nogt block either.\n
    if document not in operation_list:\n
      portal_type = document.getPortalType()\n
      simulation_state = document.getSimulationState()\n
      if (portal_type in (\'Stop Payment\', ) and simulation_state == \'started\')  \\\n
              or (portal_type == \'Mutilated Banknote\' and \n
                   simulation_state != \'finished\' \\\n
                 ) \\\n
              or (portal_type == \'Check Payment\' and \n
                   simulation_state in (\'planned\', \'ordered\') \\\n
                 ) \\\n
              or (portal_type == \'Monetary Destruction\' and simulation_state in (\'stopped\', \'started\')) \\\n
              or (portal_type == \'Paper Money Payment\' and simulation_state != \'ready\') \\\n
              or (portal_type == \'Paper Money Deposit\' and simulation_state == \'stopped\'):\n
         continue\n
      if portal_type in (\'Cash Movement\', \'Cash Movement New Not Emitted\'):\n
         if not (\n
                ((simulation_state in (\'confirmed\') and site_url in document.getSource("")) \n
                  or \n
                (simulation_state in (\'stopped\') and site_url in document.getDestination("")))\n
             ):\n
          continue\n
      if portal_type in (\'Money Deposit\',) and simulation_state not in (\'confirmed\',):\n
        continue\n
      append(document)\n
\n
def operation_sort(a,b):\n
  result = cmp(a.getPortalType(),b.getPortalType())\n
  if result==0:\n
    result = cmp(a.getSourceReference(),b.getSourceReference())\n
  return result\n
\n
operation_list.sort(operation_sort)\n
\n
return operation_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>site=None,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CounterDate_getRemainingOperationList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
