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
            <value> <string>from Products.ERP5Type.Document import newTempBase\n
\n
request = context.REQUEST\n
portal = context.getPortalObject()\n
\n
# we can use current_web_document in case it\'s "embedded" into a Web Section\n
document = request.get(\'current_web_document\', context)\n
\n
event_document_list = []\n
event_list = document.Base_getWorkflowEventInfoList()\n
for event in event_list:\n
  event_document = newTempBase(context, \'Event Info\')\n
  event_document.edit(**{\'date\': event.time,\n
                         \'action\': event.action,\n
                         \'actor\': event.actor\n
                        })\n
  event_document_list.append(event_document)\n
\n
return event_document_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_getWorkflowEventInfoAsDocumentList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
