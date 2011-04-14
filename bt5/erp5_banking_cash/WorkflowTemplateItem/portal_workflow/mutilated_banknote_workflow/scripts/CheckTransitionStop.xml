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
ob = state_change[\'object\']\n
\n
ob.Baobab_checkCounterDateOpen(site=ob.getSource(), date=ob.getStartDate())\n
\n
\n
\n
# check presence of banknote\n
if len(ob.objectValues()) == 0:\n
  msg = Message(domain = "ui", message="No mutilated banknotes defined.")\n
  raise ValidationFailed, (msg,)\n
\n
# check price defined\n
if ob.getSourceTotalAssetPrice() != ob.getTotalPrice(portal_type=\'Incoming Mutilated Banknote Line\', fast=0):\n
  msg = Message(domain = "ui", message="Amount differ between document and line.")\n
  raise ValidationFailed, (msg,)\n
\n
# check reporter defined\n
if ob.getDeponent() in (None, ""):\n
  msg = Message(domain = "ui", message="You must define a reporter.")\n
  raise ValidationFailed, (msg,)\n
\n
# check original site defined is hq\n
if "siege" in ob.getSource() and ob.getSourceTrade() is None:\n
  msg = Message(domain = "ui", message="You must define the original site.")\n
  raise ValidationFailed, (msg,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CheckTransitionStop</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
