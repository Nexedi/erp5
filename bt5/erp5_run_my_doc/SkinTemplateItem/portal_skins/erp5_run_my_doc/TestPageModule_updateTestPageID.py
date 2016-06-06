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
This script is intended to be run before exporting business template of test pages\n
It will change ID of all published/shared/released test page so that it can be exported easily\n
"""\n
portal = context.getPortalObject()\n
\n
test_pages = portal.test_page_module.searchFolder(validation_state=\n
  (\'published\', \'published_alive\',\'released\', \'released_alive\',\n
   \'shared\', \'shared_alive\',))\n
print len(test_pages)\n
new_page_list = []\n
for page in test_pages:\n
  print "changing ID of %s to %s of document in state %s" %(page.getRelativeUrl(), page.getReference(), page.getValidationState())\n
  if not dry_run:\n
    page.setId(page.getReference())\n
    print "\\tpage changed"\n
  new_page_list.append(page.getReference())\n
\n
print "finished"\n
\n
print "For business template Path"\n
for p in new_page_list:\n
  print "test_page_module/"+p\n
  print "test_page_module/"+p+"/**"\n
\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>dry_run=True</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>TestPageModule_updateTestPageID</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
