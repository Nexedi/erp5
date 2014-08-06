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

\'\'\'Lookup source account & destination account from applicable paths and copy\n
them on this movement.\n
\'\'\'\n
movement = state_change[\'object\']\n
searchPredicateList = movement.getPortalObject().portal_domains.searchPredicateList\n
\n
resource = movement.getResourceValue()\n
if resource is not None:\n
  if not movement.getDestinationAccount():\n
    for predicate in searchPredicateList(\n
                      context=movement, portal_type=\'Purchase Supply Line\'):\n
      if predicate.getDestinationAccount():\n
        movement.setDestinationAccount(predicate.getDestinationAccount())\n
        break\n
  if not movement.getSourceAccount():\n
    for predicate in searchPredicateList(\n
                      context=movement, portal_type=\'Sale Supply Line\'):\n
      if predicate.getSourceAccount():\n
        movement.setSourceAccount(predicate.getSourceAccount())\n
        break\n
else:\n
  movement.setSourceAccount(None)\n
  movement.setDestinationAccount(None)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
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
            <value> <string>Movement_copyAccountFromPath</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
