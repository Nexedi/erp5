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
            <value> <string># get all operations related to ths site\n
# as source\n
if simulation_state is None:\n
  simulation_state = [\'confirmed\']\n
kwd_source = {\'default_source_uid\' : site_uid,\'simulation_state\' : simulation_state}\n
kwd_destination = {\'default_destination_uid\' : site_uid,\'simulation_state\' : simulation_state}\n
kwd_site = {\'default_site_uid\' : site_uid,\'simulation_state\' : simulation_state}\n
if date is not None:\n
  kwd_source[\'delivery.start_date\']=date\n
  kwd_destination[\'delivery.start_date\']=date\n
  kwd_site[\'delivery.start_date\']=date\n
if portal_type is not None:\n
  kwd_source[\'portal_type\'] = portal_type\n
  kwd_destination[\'portal_type\'] = portal_type\n
  kwd_site[\'portal_type\'] = portal_type\n
# as destination\n
operation_list = list(context.portal_catalog(**kwd_source)) + \\\n
                 list(context.portal_catalog(**kwd_destination)) + \\\n
                      list(context.portal_catalog(**kwd_site))\n
operation_list_object = [x.getObject() for x in operation_list]\n
\n
return operation_list_object\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>site_uid=None, date=None, simulation_state=None,portal_type=None</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Baobab_getRemainingOperationList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
