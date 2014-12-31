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
            <value> <string>portal = context.getPortalObject()\n
\n
accounting_currency_reference_cache = container.REQUEST.get(\'%s.cache\' % script.id, {})\n
def getAccountingCurrencyReference(section_relative_url):\n
  try:\n
    return accounting_currency_reference_cache[section_relative_url]\n
  except KeyError:\n
    reference = \'\'\n
    if section_relative_url:\n
      section = portal.restrictedTraverse(section_relative_url, None)\n
      if section is not None:\n
        reference = section.getProperty(\'price_currency_reference\')\n
    accounting_currency_reference_cache[section_relative_url] = reference\n
    return reference\n
    \n
return getAccountingCurrencyReference(brain.section_relative_url)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>brain, *args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Movement_getSectionPriceCurrency</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
