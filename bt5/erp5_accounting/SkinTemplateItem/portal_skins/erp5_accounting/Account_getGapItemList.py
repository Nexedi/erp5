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
            <value> <string>"""Return a list of possible GAP categories for a given account.\n
\n
if only_preferred_gap parameter is true, this will return only GAP\n
categories from the GAP set in preferences, otherwise it will return\n
categories from all available GAP.\n
"""\n
\n
portal = context.getPortalObject()\n
\n
display_cache = {}\n
def display(x):\n
  if x not in display_cache:\n
    gap_id = x.getReference()\n
    if gap_id:\n
      display_cache[x] = \'%s - %s\' % (gap_id,\n
                  x.getShortTitle() or x.getTitle())\n
    else:\n
      display_cache[x] = x.getIndentedTitle()\n
\n
  return display_cache[x]\n
\n
def getGapItemList(only_preferred_gap, gap_root=None):\n
  ctool = portal.portal_categories\n
  if only_preferred_gap:\n
    if gap_root:\n
      return ctool.resolveCategory(gap_root).getCategoryChildItemList(\n
        base=False, is_self_excluded=True, display_method=display,\n
        local_sort_id=(\'int_index\', \'reference\', \'id\'))\n
\n
  result = []\n
  for country in ctool.gap.contentValues():\n
    for gap_root in country.contentValues():\n
      result.extend(gap_root.getCategoryChildItemList(\n
        base=False, is_self_excluded=True, display_method=display,\n
        local_sort_id=(\'int_index\', \'reference\', \'id\')))\n
  return result\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
getGapItemList = CachingMethod(getGapItemList, id=\'Account_getGapItemList\', cache_factory=\'erp5_content_long\')\n
return getGapItemList(only_preferred_gap=only_preferred_gap,\n
                gap_root=portal.portal_preferences.getPreferredAccountingTransactionGap())\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>only_preferred_gap=1</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Account_getGapItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
