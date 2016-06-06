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
object = state_change[\'object\']\n
\n
# Check that the destination is not empty\n
destination = object.getDestination()\n
if destination is None:\n
  message = Message(domain="ui",message="Please select a destination")\n
  raise ValidationFailed, (message,)\n
\n
# Check that the destination is not empty\n
description = object.getDescription()\n
if description in (None, \'\'):\n
  message = Message(domain="ui",message="Please set a description")\n
  raise ValidationFailed, (message,)\n
\n
# Check that there is a least one line\n
if len(object.objectValues())==0:\n
  message = Message(domain="ui",message="Please enter some check or checkbooks")\n
  raise ValidationFailed, (message,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CheckbookReception_validateData</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
