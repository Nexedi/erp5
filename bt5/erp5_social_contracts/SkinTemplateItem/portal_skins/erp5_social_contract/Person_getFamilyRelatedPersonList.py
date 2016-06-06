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
            <value> <string>from Products.ERP5Type.Utils import convertToUpperCase\n
related_person_list = []\n
known_person_uid = {}\n
\n
for base_category in [\'natural_parent\', \'legal_parent\', \'insurance_coverage\'] :\n
  relation_title = context.getPortalObject().portal_categories[base_category].getTranslatedTitle()\n
  relation_method = getattr(context, "get%sRelatedValueList" % convertToUpperCase(base_category))\n
  for person in relation_method( portal_type = \'Person\' ) :\n
    if person.getUid() not in known_person_uid :\n
      known_person_uid[person.getUid()] = 1\n
      related_person_list.append(person.asContext(relation_title = relation_title))\n
\n
return related_person_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Person_getFamilyRelatedPersonList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
