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
contribution_registry = context.portal_contribution_registry\n
\n
base_list = []\n
for attachment in context.getAttachmentInformationList():\n
  # XXX this is for prevent get parts related to body or not related to\n
  # Attachments\n
  if attachment[\'uid\'] not in [\'part_1\', \'part_0\']:\n
    filename  = context.getTitle()\n
    if attachment.has_key("file_name"):\n
       filename=attachment["file_name"]\n
    pt = "File"\n
    temp_base_id = \'index_\'.join([attachment["uid"], str(attachment["index"])])\n
    base_list.append(newTempBase(context, id=temp_base_id,\n
                                              uid=temp_base_id,\n
                                              index= attachment["index"],\n
                                              file_name=filename,\n
                                              content_type=pt))\n
\n
return base_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_getAttachmentFastInputList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
