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
            <value> <string>"""\n
Deployment script for crating initial accounts upon gap/pl/default structure\n
Warning: Before using this script as zope, edit account_workflow and give Manager permission to validate_action\n
"""\n
\n
#This script will REMOVE any existing accounts!!!\n
#comment following if you are sure\n
print \'Nothing done!\'\n
return printed\n
\n
\n
\n
gap_root = context.getPortalObject().portal_categories.gap.pl.default\n
account_module = context.getPortalObject().account_module\n
account_module.manage_delObjects(ids=[a.getId() for a in account_module.contentValues()])\n
\n
\n
for category in gap_root.getCategoryMemberValueList():\n
  category = category.getObject()\n
  if len(category.contentValues())==0:\n
    #jest lisciem\n
    acc = account_module.newContent(title=\'%s %s\' % (category.getId(),category.getTitle()),\\\n
                             gap_value = category)\n
    acc.validate()\n
    print \'acc created\'\n
\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountModule_createAccountFromGap</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
