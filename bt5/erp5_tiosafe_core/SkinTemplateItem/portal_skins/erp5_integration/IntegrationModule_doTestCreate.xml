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
            <value> <string>selection_name = kw[\'list_selection_name\']\n
from Products.PythonScripts.standard import url_quote\n
\n
uids = context.portal_selections.getSelectionCheckedUidsFor(selection_name)\n
\n
if len(uids) == 0:\n
  return context.REQUEST.RESPONSE.redirect(\n
           \'%s/%s?\'\n
           \'portal_status_message=%s\' % ( context.absolute_url(), kw[\'dialog_id\'],\n
                               url_quote(\'No Object Selected.\')))\n
\n
\n
conduit_id = context.getDestinationSectionValue().getConduitModuleId()\n
\n
for uid in uids:\n
  context.callAddNodeOnConduit(context, conduit_id, uid)\n
\n
\n
return context.REQUEST.RESPONSE.redirect(\n
           \'%s/%s?\'\n
           \'portal_status_message=%s\' % ( context.absolute_url(), kw[\'dialog_id\'],\n
                               url_quote(\'Request sent.\')))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>IntegrationModule_doTestCreate</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
