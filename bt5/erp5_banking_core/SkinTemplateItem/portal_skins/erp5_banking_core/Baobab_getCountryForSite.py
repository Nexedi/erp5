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
            <value> <string>from Products.ERP5Type.Cache import CachingMethod\n
\n
if not isinstance(site, str):\n
  site = site.getRelativeUrl()\n
\n
\n
def getCountry(site):\n
  site = context.portal_categories.restrictedTraverse(site)\n
  orga_id = "site_%3s" %(site.getCodification()[:3])\n
  organisation = context.organisation_module[orga_id]\n
  country = organisation.getDefaultRegionTitle()\n
  if country is None:\n
    raise ValueError, "No Region found for site %s / %s defined by organisation %s" %(site.getPath(), site.getCodification(), organisation.getPath())\n
  return country\n
\n
\n
getCountry = CachingMethod(getCountry, id=\'Baobab_getCountryForSite\', cache_factory=\'erp5_ui_long\')\n
\n
return getCountry(site)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>site=None</string> </value>
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
            <value> <string>Baobab_getCountryForSite</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
