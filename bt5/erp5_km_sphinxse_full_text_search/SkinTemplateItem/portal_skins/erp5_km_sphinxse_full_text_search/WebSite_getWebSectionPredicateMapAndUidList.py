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
            <value> <string>"""\n
  Examine Web Site\'s Web Sections and return mapping between sections\' uid and respective\n
  category used in sections\' predicate.\n
  This script is used in "No ZODB" approach to get fast search results (including list of \n
  sections a object belongs to).\n
"""\n
from Products.ERP5Type.Cache import CachingMethod\n
\n
website = context.getWebSiteValue()\n
\n
def getWebSectionList(section):\n
  result = [{\'uid\': section.getUid(),\n
             \'relative_url\': section.getRelativeUrl(),\n
             \'membership_base_category_list\': section.getMembershipCriterionBaseCategoryList(),\n
             \'multi_membership_base_category_list\': section.getMultimembershipCriterionBaseCategoryList(),\n
             \'membership_category_list\': section.getMembershipCriterionCategoryList()}]\n
  for section in section.contentValues(portal_type=\'Web Section\'):\n
    result.extend(getWebSectionList(section))\n
  return result\n
\n
def getWebSectionPredicateValueList():\n
  category_map = {}\n
  base_category_uid_list = []\n
  portal_categories = context.portal_categories\n
  for section in getWebSectionList(website):\n
    # calc category_path : section map \n
    for category in section[\'membership_category_list\']:\n
      # remove leading \'follow_up\' from category\n
      if category.startswith(\'follow_up/\'):\n
        category = category.replace(\'follow_up/\', \'\', 1)\n
      if not category_map.has_key(category):\n
        category_map[category] = []\n
      category_map[category].append({\'uid\': section[\'uid\'], \'relative_url\':section[\'relative_url\']})\n
    # get base_categories we care for\n
    section_category_list = section[\'membership_base_category_list\']+section[\'multi_membership_base_category_list\']\n
    for category_id in section_category_list:\n
      category = getattr(portal_categories, category_id, None)\n
      if category is not None and category.getUid() not in base_category_uid_list:\n
        base_category_uid_list.append(category.getUid())\n
  return category_map, base_category_uid_list\n
\n
getWebSectionPredicateValueList = CachingMethod(getWebSectionPredicateValueList,\n
                                      id = \'WebSite_getWebSectionPredicateMapAndUidList\',\n
                                      cache_factory = \'erp5_content_medium\')\n
return getWebSectionPredicateValueList()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSite_getWebSectionPredicateMapAndUidList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
