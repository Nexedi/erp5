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
            <value> <string># Raise ValidationFailed if the counter date not opened for the given date and the given site\n
\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
\n
if date is None:\n
  # get current date\n
  from DateTime import DateTime\n
  date = DateTime()\n
\n
# Make sure we have a date with no hours\n
date = date.Date()\n
\n
if site is None:\n
  # get site from user assignment\n
  site_list = context.Baobab_getUserAssignedSiteList()\n
  if len(site_list) == 0:\n
    context.log(\'Baobab_checkCounterDateOpen\', \'No site found for the user\')\n
    return 0\n
  else:\n
    site = site_list[0]\n
\n
# get only the office, not need of vault\n
#context.log(\'Baobab_checkCounterDateOpen\', \'get site for vault %s\' %(site))\n
site = context.Baobab_getVaultSite(site)\n
\n
if context.portal_catalog.countResults(portal_type=\'Counter Date\', start_date=date, site_id=site.getId(), simulation_state="open")[0][0] == 0:\n
  msg = Message(domain = "ui", message="Transaction not in the good counter date")\n
  raise ValidationFailed, (msg,)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>site=None, date=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_checkCounterDateOpen</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
