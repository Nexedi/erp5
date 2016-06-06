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
            <value> <string>request = context.REQUEST\n
\n
project_line_portal_type = \'Project Line\'\n
\n
domain_list = []\n
\n
here = context.REQUEST[\'here\']\n
\n
\n
\n
if depth == 0:\n
  category_list = here.searchFolder(portal_type=project_line_portal_type, sort_on=((\'int_index\', \'ASC\')))\n
  \n
else:\n
  category_list = []\n
  parent_category_list = parent.getMembershipCriterionCategoryList()\n
  for parent_category in parent_category_list:\n
    parent_category = \'/\'.join(parent_category.split(\'/\')[1:])\n
    category_list.extend([x for x in context.restrictedTraverse(parent_category).searchFolder(portal_type=project_line_portal_type, sort_on=((\'int_index\', \'ASC\')))])\n
\n
i = 0\n
for category in category_list:\n
  domain = parent.generateTempDomain(id = \'%s_%s\' % (depth, i))\n
  domain.edit(title = category.getTitle(),\n
              membership_criterion_base_category = (\'source_project\', ), \n
              membership_criterion_category = (\'source_project/\' + category.getRelativeUrl(),),\n
              domain_generator_method_id = script.id,\n
              uid = category.getUid())\n
  i += 1\n
                \n
  domain_list.append(domain)\n
\n
return domain_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>depth, parent, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Project_generateProjectDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
