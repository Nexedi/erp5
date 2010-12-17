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
            <value> <string>domain_list = []\n
\n
if depth == 0:\n
  task_uid_list  = context.portal_selections.getSelectionUidList(context=context, selection_name=\'task_report_module_selection\')\n
  person_result = context.portal_catalog(portal_type=["Person",],\n
                                         source_related_uid=task_uid_list,\n
                                         select_expression=\'portal_type, relative_url, id, title\',\n
                                         sort_on = ((\'title\',\'ascending\'),))\n
  person_dict = {}\n
  person_list = []\n
  append = person_list.append\n
  for person in person_result:\n
    key = person.uid\n
    if key not in person_dict:\n
      person_dict[key] = None\n
      category_dict = {\'relative_url\':person.relative_url, \n
                       \'portal_type\': "Person",\n
                       \'id\':person.id,\n
                       \'title\':person.title,\n
                       \'uid\':person.uid}\n
      append(category_dict)\n
else:\n
  return domain_list\n
\n
for person in person_list:\n
  domain = parent.generateTempDomain(id = \'sub\' + person[\'id\'] )\n
  domain.edit(title = person[\'title\'],\n
              membership_criterion_base_category = (\'source\', ), \n
              membership_criterion_category = (person[\'relative_url\'],),\n
              domain_generator_method_id = script.id,\n
              uid = person[\'uid\'])\n
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
            <value> <string>TaskReportModule_generatePersonDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
