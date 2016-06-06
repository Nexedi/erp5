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

from Products.ERP5Type.Message import Message\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
\n
inventory = state_change[\'object\']\n
\n
# Make sure the start_date is defined\n
start_date = inventory.getStartDate()\n
if start_date is None:\n
  text = "Sorry, you must define the inventory date"\n
  message = Message(domain=\'ui\', message=text)\n
  raise ValidationFailed, message\n
\n
# Make sure the node is defined\n
node = inventory.getDestination()\n
if node is None:\n
  text = "Sorry, you must define the inventory warehouse"\n
  message = Message(domain=\'ui\', message=text)\n
  raise ValidationFailed, message\n
\n
\n
# use of the constraint\n
error_list = inventory.checkConsistency()\n
if len(error_list) > 0:\n
  raise ValidationFailed, (error_list[0].getTranslatedMessage(),)\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>validateConsistency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
