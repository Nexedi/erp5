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
            <value> <string>from Products.ZSQLCatalog.SQLCatalog import SimpleQuery\n
\n
portal = context.getPortalObject()\n
\n
reference_list = [x.reference for x in\n
                  portal.portal_catalog(SimpleQuery(reference=None,\n
                                                    comparison_operator="is not"),\n
                                        select_list=[\'reference\'],\n
                                        portal_type="Person", title=value)]\n
\n
return SimpleQuery(owner=reference_list or value or -1)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>value</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>SQLCatalog_makeOwnerTitleSearchQuery</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
