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
category_list = []\n
if depth == 0:\n
  category_list = [x for x in context.portal_catalog(portal_type=\'Project\',\n
                                                     validation_state=\'validated\')]\n
else:\n
  parent_object = context.restrictedTraverse(parent.parent_url)\n
  category_list = parent_object.contentValues(portal_type=\'Project Line\', sort_on=\'int_index\')\n
\n
for category in category_list:\n
  domain = parent.generateTempDomain(id=\'sub%s\' % category.getId())\n
  \n
  membership_criterion_category = []\n
  sub_category_list = [category]\n
  while sub_category_list:\n
    sub_category = sub_category_list.pop()\n
    membership_criterion_category.append(\'source_project/%s/\' % sub_category.getRelativeUrl())\n
    sub_category_list.extend(sub_category.contentValues(portal_type=\'Project Line\'))\n
\n
  domain.edit(title = category.getTitle(),\n
              membership_criterion_base_category = (\'source_project\', ),\n
              membership_criterion_category = membership_criterion_category,\n
              domain_generator_method_id = script.id,\n
              parent_url=category.getRelativeUrl(),\n
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
            <value> <string>Base_generateValidatedProjectDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
