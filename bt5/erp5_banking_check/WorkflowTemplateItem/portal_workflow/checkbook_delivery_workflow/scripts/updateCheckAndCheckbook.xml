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

# XXX: this script is not used any more, since checks are already\n
# generated when checks & checkbooks are received.\n
\n
# We will need to create all checks for all checkbooks\n
# Then all of them should be set as confirmed\n
transaction = state_change[\'object\']\n
\n
line_list = transaction.getMovementList()\n
\n
for line in line_list:\n
  aggregate_list = line.getAggregateValueList()\n
  for aggregate in aggregate_list:\n
    if aggregate.getPortalType()==\'Checkbook\':\n
      aggregate.setStartDate(transaction.getStartDate())\n
      aggregate.confirm()\n
      for check in aggregate.objectValues(portal_type=\'Check\'):\n
        check.confirm()\n
        check.setStartDate(transaction.getStartDate())\n
    elif aggregate.getPortalType()==\'Check\':\n
      aggregate.setStartDate(transaction.getStartDate())\n
      aggregate.confirm()\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>updateCheckAndCheckbook</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
