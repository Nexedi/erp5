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
  Send an email after accept a credential request\n
  Proxy: Assignee, Assignor, Member -- allow to send notification by mail.\n
"""\n
\n
portal = context.getPortalObject()\n
recipient = context.getDestinationDecisionValue(portal_type="Person")\n
\n
#Define the type of notification\n
notification_type = "without-password"\n
if password:\n
  notification_type = "with-password"\n
\n
#Get message from catalog\n
notification_reference = \'crendential_request-confirmation-%s\' % notification_type\n
notification_message = portal.portal_notifications.getDocumentValue(reference=notification_reference, \n
                                                                    language=recipient.getLanguage())\n
if notification_message is None:\n
  raise ValueError, \'Unable to found Notification Message with reference "%s".\' % notification_reference\n
\n
#Set notification mapping\n
notification_mapping_dict = {\'login_name\': login}\n
if password:\n
  notification_mapping_dict.update(\n
                            {\'login_password\' : password})\n
\n
#Preserve HTML else convert to text\n
if notification_message.getContentType() == "text/html":\n
  mail_text = notification_message.asEntireHTML(\n
    substitution_method_parameter_dict={\'mapping_dict\':notification_mapping_dict})\n
else:\n
  mail_text = notification_message.asText(\n
    substitution_method_parameter_dict={\'mapping_dict\':notification_mapping_dict})\n
\n
#Send email\n
portal.portal_notifications.sendMessage(\n
  sender=None,\n
  recipient=recipient,\n
  subject=notification_message.getTitle(),\n
  message=mail_text,\n
  message_text_format=notification_message.getContentType(),\n
  notifier_list=(portal.portal_preferences.getPreferredLoginAndPasswordNotifier(),),\n
  store_as_event= portal.portal_preferences.isPreferredStoreEvents(),\n
  event_keyword_argument_dict={\'follow_up\':context.getRelativeUrl()},\n
  )\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>login,password</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CredentialRequest_sendAcceptedNotification</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
