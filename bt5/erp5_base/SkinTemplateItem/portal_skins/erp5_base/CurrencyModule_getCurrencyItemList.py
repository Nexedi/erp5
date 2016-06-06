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
            <value> <string>from ZTUtils import LazyFilter\n
from Products.CMFCore.permissions import AccessContentsInformation\n
\n
\n
portal = context.getPortalObject()\n
\n
def getCurrencyItemList(include_empty=1, validation_state=validation_state):\n
  result = []\n
  if include_empty :\n
    result = [[\'\', \'\'],]\n
  currency_module = portal.restrictedTraverse(\n
                             \'currency_module\',\n
                             portal.restrictedTraverse(\'currency\', None))\n
\n
  if currency_module is not None:\n
    for currency in LazyFilter(currency_module.contentValues(), skip=AccessContentsInformation):\n
      if currency.getProperty(\'validation_state\', \'validated\') in validation_state:\n
        # for currency, we intentionaly use reference (EUR) not title (Euros).\n
        result.append((currency.getReference() or currency.getTitleOrId(),\n
                       currency.getRelativeUrl()))\n
  \n
  result.sort(key=lambda x: x[0])\n
  return result\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
getCurrencyItemList = CachingMethod(\n
                          getCurrencyItemList,\n
                          id=\'CurrencyModule_getCurrencyItemList\',\n
                          cache_factory = \'erp5_ui_short\')\n
                             \n
return getCurrencyItemList(include_empty=include_empty,\n
                           validation_state=validation_state)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>include_empty=1, validation_state=(\'validated\', \'draft\')</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CurrencyModule_getCurrencyItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
