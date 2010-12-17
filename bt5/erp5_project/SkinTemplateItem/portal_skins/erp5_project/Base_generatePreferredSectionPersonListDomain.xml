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
\n
if depth == 0:\n
  preferred_group = context.portal_preferences.getPreferredSectionCategory()\n
  if preferred_group:\n
\n
    person_sql_list = context.portal_catalog(\n
      portal_type=\'Person\', group_relative_url=preferred_group)\n
\n
    for person in person_sql_list:\n
      person = person.getObject()\n
      domain = parent.generateTempDomain(id=\'sub%s\' % person.getId())\n
      domain.edit(title = person.getTitle(),\n
                  membership_criterion_base_category = (\'source\', ), \n
                  membership_criterion_category = (\'source/%s\' % person.getRelativeUrl(),),\n
                  domain_generator_method_id = script.id,\n
                  uid = person.getUid())\n
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
            <value> <string>Base_generatePreferredSectionPersonListDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
