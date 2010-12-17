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
            <value> <string># Example code:\n
\n
def getCompactTitle(category):\n
  title_list = []\n
  while category.getPortalType() == \'Category\':\n
    if category.getCodification() or category.getShortTitle():\n
      compact_title = category.getTranslatedShortTitle() or category.getReference() or category.getTranslatedTitle()\n
      title_list.append(compact_title)\n
    category = category.getParentValue()\n
  if title_list:\n
    title_list = title_list[:-1]\n
    title_list.reverse()\n
  return \'/\'.join(title_list)\n
\n
def compareTitle(a, b):\n
  return cmp(a[1], b[1])\n
\n
def getCompactChildItemList(context):\n
  result = context.getCategoryChildItemList(display_method=getCompactTitle)\n
  result.sort(compareTitle)\n
  return result\n
\n
from Products.ERP5Type.Cache import CachingMethod\n
cached_getCompactChildItemList = CachingMethod(getCompactChildItemList, id=\'getCompactChildItemList\')\n
return cached_getCompactChildItemList(context)\n
</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Category_getCompactChildItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
