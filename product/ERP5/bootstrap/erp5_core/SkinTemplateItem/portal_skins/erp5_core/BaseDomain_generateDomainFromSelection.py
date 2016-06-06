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
            <value> <string>"""This script generates a domain from selected objects in a module.\n
\n
It\'s not supposed to be used directly, but wrapped in another script that will pass those parameters:\n
 * script_id: the ID of the wrapper script (subdomains will be regenerated with this script);\n
 * selection_name: the selection name used by the listbox;\n
 * membership_criterion_base_category: base categories that will be set on generated domains.\n
"""\n
\n
if depth != 0:\n
  return []\n
\n
domain_list = []\n
portal = context.getPortalObject()\n
category_list = portal.portal_selections.getSelectionCheckedValueList(selection_name)\n
if not category_list:\n
  category_list = portal.portal_selections.callSelectionFor(selection_name)\n
\n
for category in category_list:\n
  domain = parent.generateTempDomain(id=category.getId())\n
  domain.edit(title=category.getTitle(),\n
              membership_criterion_base_category=membership_criterion_base_category,\n
              membership_criterion_category=(category.getRelativeUrl(),),\n
              domain_generator_method_id=script_id,\n
              uid=category.getUid())\n
                \n
  domain_list.append(domain)\n
\n
return domain_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>script_id, selection_name, membership_criterion_base_category, depth, parent, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BaseDomain_generateDomainFromSelection</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
