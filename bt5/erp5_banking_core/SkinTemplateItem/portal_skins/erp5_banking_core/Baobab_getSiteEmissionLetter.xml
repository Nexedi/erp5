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
            <value> <string># Rerturns the emission letter corresponding to a particular site\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
def getSiteEmissionLetter(site=None):\n
  portal = context.getPortalObject()\n
  site_object = portal.portal_categories.restrictedTraverse(site)\n
  lower_letter = site_object.getCodification()[0].lower()\n
  if lower_letter == \'z\':\n
    lower_letter = \'k\'\n
  return lower_letter\n
\n
getSiteEmissionLetter = CachingMethod(getSiteEmissionLetter,\n
                             id = \'Baobab_getSiteEmissionLetter\',\n
                             cache_factory = \'erp5_ui_long\')\n
\n
if not same_type(site, \'a\'):\n
  site = site.getRelativeUrl()\n
\n
return getSiteEmissionLetter(site=site)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>site=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_getSiteEmissionLetter</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
