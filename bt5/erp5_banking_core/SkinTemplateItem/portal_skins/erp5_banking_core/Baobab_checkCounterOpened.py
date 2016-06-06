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
if simulation_state_list is None:\n
  simulation_state_list = [\'open\']\n
\n
site = context.Baobab_getVaultSite(counter)\n
counter_list = [x.getObject() for x in context.portal_catalog(portal_type="Counter", \n
         simulation_state = simulation_state_list, default_site_uid = site.getUid())]\n
if same_type(counter, \'a\'):\n
  counter_relative_url = counter\n
else:\n
  counter_relative_url = counter.getRelativeUrl()\n
found = 0\n
#if "guichet" in counter_relative_url:\n
for counter_ob in counter_list:\n
  if "site/%s" %counter_ob.getSite() in counter_relative_url or counter_relative_url in "site/%s" %counter_ob.getSite():\n
    found = 1\n
if found == 0:\n
  msg = Message(domain = "ui", message="Counter is not opened")\n
  raise ValidationFailed, (msg,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>counter, simulation_state_list=None, site=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_checkCounterOpened</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
