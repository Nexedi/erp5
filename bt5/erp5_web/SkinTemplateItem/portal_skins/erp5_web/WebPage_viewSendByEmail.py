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
            <value> <string>for email in email_recipient_list:\n
  context.MailHost.send("From: %s\\nTo: %s\\nContent-Type: text/plain;\\n  charset=\\"utf-8\\"\\n\\n\\n%s" % (email_sender,email,email_text),\n
                        mto=email, mfrom=email_sender,\n
                        subject=email_title, encode=\'8bit\')\n
\n
return "Done"\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>email_title, email_sender, email_text, email_recipient_list, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebPage_viewSendByEmail</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
