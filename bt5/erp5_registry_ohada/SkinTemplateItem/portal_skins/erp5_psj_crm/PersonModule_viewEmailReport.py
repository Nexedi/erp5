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
            <value> <string>uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)\n
if len(uids) == 0:\n
#   uids = map(lambda x:x.uid, context.portal_selections.callSelectionFor(selection_name))\n
  uids = [x.uid for x in context.portal_selections.callSelectionFor(selection_name)]\n
object_list =  list(context.portal_catalog(parent_uid=uids, portal_type = "Email"))\n
for o in object_list:\n
  o_value = o.getObject()\n
  if o is not None:\n
    print o_value.getUrlString()\n
\n
return printed\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>PersonModule_viewEmailReport</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
