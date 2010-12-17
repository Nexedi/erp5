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
            <value> <string>"""Guess the path of categories, taking as input a mapping {base_category:\n
category}, where category can be the relative_url, the title or the reference\n
of the category\n
"""\n
\n
from Products.ZSQLCatalog.SQLCatalog import Query, ComplexQuery\n
portal = context.getPortalObject()\n
result_dict = {}\n
\n
for base_category_name, category in category_dict.items():\n
  category_object = \\\n
    context.getPortalObject().portal_categories[base_category_name]\n
  \n
  category_value = category_object.restrictedTraverse(category, None)\n
  if category_value is None:\n
    query = ComplexQuery(\n
                ComplexQuery(Query(title=category,\n
                               key=\'ExactMatch\'),\n
                         Query(reference=category,\n
                               key=\'ExactMatch\'),\n
                         operator=\'OR\'),\n
                ComplexQuery(Query(relative_url=\'%s/%%\' % base_category_name)))\n
    category_value = portal.portal_catalog.getResultValue(query=query)\n
\n
  if category_value is not None:\n
    # remove base category from relative_url\n
    result_dict[base_category_name] = \\\n
      category_value.getRelativeUrl().split(\'/\', 1)[1]\n
\n
return result_dict\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>category_dict</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getCategoriesFullPath</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
