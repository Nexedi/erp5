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
            <value> <string>portal_type_dict = {"Web Page": ["Text", "web_page_template"],\n
                    "Web Table": ["Spreadsheet", "web_table_template"],\n
                    "Web Illustration": ["Drawing", "web_illustration_template"]}\n
\n
portal_type = context.REQUEST.form.get("portal_type")\n
document = context.Base_contribute(file=file, \n
                       url=None, \n
                       portal_type=portal_type_dict.get(portal_type)[0], \n
                       synchronous_metadata_discovery=None, \n
                       redirect_to_document=False, \n
                       attach_document_to_context=False, \n
                       use_context_for_container=False, \n
                       redirect_url=None, \n
                       cancel_url=None, \n
                       batch_mode=False,\n
                       max_repeat=0, \n
                       editable_mode=1,\n
                       follow_up_list=None, \n
)\n
\n
return context.ERP5Site_createNewWebDocument(template=portal_type_dict.get(portal_type)[1],\n
                                             selection_action=portal_type,\n
                                             document_path=document.getPath(),\n
                                             upload_document=1)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>file, **kw</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Assignee</string>
                <string>Assignor</string>
                <string>Auditor</string>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_uploadDocument</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
