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
            <value> <string>"""\n
This script notify the user that the form has been submitted\n
"""\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
\n
\n
translateString = context.Base_translateString\n
portal_catalog = context.portal_catalog\n
\n
form = state_change[\'object\']\n
\n
# Build the message and translate it\n
msg = []\n
subject = translateString("Your application has been submitted successfully under the reference") + " : " + form.getId()\n
msg.append(subject)\n
msg.append(translateString("An Agent will review your application shortly. You will be notified by email whenever your application will start being processed. To further track your application, connect and login any time to the following site"))\n
msg.append(context.getWebSiteValue().getAbsoluteUrl())\n
msg.append(translateString("And use the login") + " : " + form.getReference())\n
msg.append(translateString("and the password") + " : " + form.getPassword())\n
\n
msg = "\\n".join(msg)\n
\n
# We can now notify the accoutant through the notification tool\n
context.portal_notifications.sendMessage(recipient=form.getReference(), \n
    subject=subject, message=msg, portal_type_list=(\'Subscription Form\'),\n
    store_as_event=True)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>state_change</string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Assignor</string>
                <string>Manager</string>
                <string>Owner</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>sendNotificationByMail</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
