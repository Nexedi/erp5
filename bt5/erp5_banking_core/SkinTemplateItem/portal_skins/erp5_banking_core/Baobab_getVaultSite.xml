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
            <value> <string>from Products.ERP5Type.Message import Message\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
site = vault\n
if same_type(site, \'\'):\n
  if site.startswith(\'site/\'):\n
    site = site[len(\'site/\'):]\n
  site = context.restrictedTraverse(\'portal_categories/site/%s\' %(site,))\n
\n
while True:\n
  if not hasattr(site, \'getVaultTypeList\'):\n
    context.log(\'no getVaultTypeList on :\', site.getRelativeUrl())\n
    msg = Message(domain = \'ui\', message = \'The site value is misconfigured; report this to system administrators.\')\n
    raise ValidationFailed, (msg,)\n
  if \'site\' in site.getVaultTypeList():\n
    break\n
  site = site.getParentValue()\n
return site\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>vault</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_getVaultSite</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
