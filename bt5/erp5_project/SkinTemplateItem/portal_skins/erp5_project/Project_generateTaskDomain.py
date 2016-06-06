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
domain_list = []\n
object_path = request.get(\'object_path\')\n
if object_path is None:\n
  object_path = context.REQUEST.get(\'URL1\').split(\'/\')[-1]\n
\n
search_path = \'project_module/%s/%%\'\n
\n
if depth == 0:\n
  category_list = []\n
  for line in context.portal_catalog(path=search_path ):\n
     category_list.extend([ i for i in line.getObject().getSourceProjectRelatedValueList() if i not in category_list])\n
\n
else:\n
  return domain_list\n
\n
for category in category_list:\n
  domain = parent.generateTempDomain(id = \'sub\' + category.getId() )\n
  domain.edit(title = category.getTitle(),\n
              membership_criterion_base_category = (\'source_project_related\', ), \n
              membership_criterion_category = (category.getRelativeUrl(),),\n
              domain_generator_method_id = script.id,\n
              uid = category.getUid())\n
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
            <value> <string>Project_generateTaskDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
