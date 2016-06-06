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
            <value> <string># check that accounting date is opened for the site in which is the counter\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
transaction = state_change[\'object\']\n
site = transaction.getSiteValue()\n
\n
while True:\n
  if not hasattr(site, \'getVaultTypeList\'):\n
    msg = Message(domain = \'ui\', message = \'The site value is misconfigured; report this to system administrators.\')\n
    raise ValidationFailed, (msg,)\n
  if \'site\' in site.getVaultTypeList():\n
    break\n
  site = site.getParentValue()\n
\n
kwd = {\'portal_type\' : \'Counter Date\', \'simulation_state\' : \'open\', \'site_uid\' : site.getUid()}\n
date_list = [x.getObject() for x in context.portal_catalog(**kwd)]\n
\n
if len(date_list) == 0:\n
  msg = Message(domain=\'ui\', message="Counter date is not opened.")\n
  raise ValidationFailed, (msg,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change, *args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>checkDateOpened</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
