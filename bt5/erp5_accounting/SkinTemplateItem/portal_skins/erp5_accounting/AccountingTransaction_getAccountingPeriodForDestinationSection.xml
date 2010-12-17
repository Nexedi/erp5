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
            <value> <string encoding="cdata"><![CDATA[

"""Returns the accounting period for the destination section that should be applied for this\n
accounting transaction.\n
"""\n
\n
operation_date = context.getStopDate()\n
if not operation_date:\n
  return None\n
\n
section = context.getDestinationSectionValue(portal_type=\'Organisation\')\n
if section is not None:\n
  section = section.Organisation_getMappingRelatedOrganisation()\n
  for accounting_period in section.contentValues(\n
                          portal_type=\'Accounting Period\',\n
                          checked_permission=\'Access contents information\'):\n
    if accounting_period.getSimulationState() in (\n
              \'draft\', \'cancelled\', \'deleted\'):\n
      continue\n
    if accounting_period.getStartDate().earliestTime()\\\n
              <=  operation_date <= \\\n
       accounting_period.getStopDate().latestTime():\n
      return accounting_period\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransaction_getAccountingPeriodForDestinationSection</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
