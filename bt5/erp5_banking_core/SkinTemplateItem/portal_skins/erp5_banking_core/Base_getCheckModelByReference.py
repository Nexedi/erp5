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

from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
if reference is None:\n
  msg = Message(domain=\'ui\', message="Check not defined.")\n
  raise ValidationFailed, (msg,)\n
model_list = [x\n
  for x in context.checkbook_model_module.objectValues()\n
  if x.getReference() == reference\n
  and x.isUniquePerAccount() == unique_per_account\n
]\n
model_list_len = len(model_list)\n
if model_list_len == 0:\n
  msg = Message(domain=\'ui\', message="Check not defined.")\n
  raise ValidationFailed, (msg,)\n
if model_list_len > 1:\n
  msg = Message(domain=\'ui\', message="Two many check models with this reference.")\n
  raise ValidationFailed, (msg,)\n
return model_list[0]\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>reference=None, unique_per_account=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getCheckModelByReference</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
