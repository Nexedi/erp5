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
            <value> <string>\'\'\'Returns the currency that is used for this section category.\n
Returns None if no currency defined or if mixed currency are used.\n
\'\'\'\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
def getCurrencyForSectionCategory(section_category, section_category_strict):\n
  portal = context.getPortalObject()\n
  currency_set = set()\n
  for section_uid in portal.Base_getSectionUidListForSectionCategory(\n
      section_category, section_category_strict):\n
    if section_uid != -1:\n
      section = portal.portal_catalog.getObject(section_uid)\n
      currency = section.getPriceCurrency()\n
      if currency:\n
        currency_set.add(currency)\n
  if len(currency_set) == 1:\n
    return currency_set.pop()\n
\n
getCurrencyForSectionCategory = CachingMethod(\n
              getCurrencyForSectionCategory,\n
              id=script.getId(), cache_factory=\'erp5_content_long\')\n
\n
return getCurrencyForSectionCategory(section_category, section_category_strict)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>section_category, section_category_strict</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getCurrencyForSectionCategory</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
