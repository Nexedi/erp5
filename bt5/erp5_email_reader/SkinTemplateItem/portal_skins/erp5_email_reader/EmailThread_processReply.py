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
            <value> <string>email_reader = context.getParentValue()\n
title = context.getReplySubject()\n
text_content = context.getReplyBody()\n
\n
id_group = "%s-sent" % email_reader.getRelativeUrl()\n
new_id = context.portal_ids.generateNewId(id_group=id_group)\n
new_id = "OUTBOX-%s" % new_id\n
\n
# Prepare new message\n
new_message = email_reader.newContent(portal_type="Email Thread", id=new_id, title=title, text_content=text_content, text_format="text/plain")\n
new_message.setRecipient(context.getReplyTo())\n
# set In-Reply-To field\n
new_message.setDestinationReference(context.getSourceReference())\n
\n
# Reply to old one\n
context.reply()\n
\n
# And display\n
return new_message.Base_redirect()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EmailThread_processReply</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
