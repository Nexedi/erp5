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
            <value> <string>dms_module = getattr(context, \'document_module\', None)\n
attachment_info_list =  context.getAttachmentInformationList()\n
Base_translateString = context.Base_translateString\n
if dms_module is not None:\n
  for uid in uids:\n
    # Maybe select Line can be improved later\n
    line = [ l for l in listbox if l[\'listbox_key\'].split(\'/\')[-1] ==  uid][0]\n
    # index is numeric and comes with uid \n
    attachment_index = int(uid.split(\'index_\')[-1])\n
    attachment_info = [i for i in attachment_info_list if i[\'index\'] == attachment_index][0]\n
    file = context.getAttachmentData(index=attachment_index)\n
    document = dms_module.newContent(follow_up=context.getFollowUp(),\n
                                     portal_type = line[\'content_type\'],\n
                                     description = line[\'description\'],\n
                                     version = line[\'version\'],\n
                                     short_title = line[\'short_title\'],\n
                                     language = line[\'language\'],\n
                                     reference= line[\'reference\'],\n
                                     title = line[\'title\'])\n
    document.edit(source_reference=attachment_info[\'file_name\'], file=file)\n
\n
if len(uids) == 1:\n
  message = Base_translateString(\'${portal_type} created successfully.\',\n
                                 mapping={\'portal_type\':document.getTranslatedPortalType()})\n
  return document.Base_redirect(keep_items=dict(portal_status_message=message))\n
\n
message = Base_translateString(\'${count} documents created successfully.\',\n
                               mapping={\'count\':len(uids)})\n
\n
return context.Base_redirect(keep_items=dict(portal_status_message=message))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>uids=[], listbox=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_createDocumentFromAttachment</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
