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
            <value> <string>from Products.ERP5Type.Document import newTempDomain\n
portal = context.getPortalObject()\n
portal_type_list = portal.getPortalEventTypeList()\n
portal_types = portal.portal_types\n
translateString = portal.Base_translateString\n
domain_list = []\n
\n
domain_list_append = domain_list.append\n
\n
if depth == 0:\n
  for uid, portal_type in enumerate(portal_type_list):\n
    domain = parent.generateTempDomain(id=\'%s_%s\' % (depth, uid))\n
    domain.edit(title=translateString(portal_types[portal_type].getId()),\n
                domain_generator_method_id=script.id,\n
                uid=uid)\n
    domain.setCriterion(property=\'causality_portal_type\', identity=portal_type)\n
    domain.setCriterionPropertyList([\'causality_portal_type\'])\n
    domain_list_append(domain)\n
\n
return domain_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>depth, parent</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_generateCausalityEventPortalTypeDomain</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
