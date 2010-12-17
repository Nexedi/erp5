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
            <value> <string>translateString = context.Base_translateString\n
request = context.REQUEST\n
ptype = context.getPortalType()\n
\n
if not description:\n
  return context.Base_redirect(dialog_id,\n
              keep_items = dict(portal_status_message = translateString("Question can not be empty.",), cancel_url = cancel_url))\n
\n
query = context.Base_newQuery(description=description)\n
query_id = query.getId()\n
return context.Base_redirect(form_id,\n
              keep_items = dict(portal_status_message = translateString("A Query about the current ${portal_type} was posted with ID ${query_id}.", mapping = dict(query_id=query_id, portal_type=ptype)),\n
              cancel_url = cancel_url))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>dialog_id=None,form_id=None,description=None,cancel_url=\'\'</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_postQuery</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
