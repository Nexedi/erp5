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
            <value> <string>"""Return the notification messages that can be used as a template to create an event.\n
"""\n
reference_set = set() # If there are two messages with same reference, we only\n
                      # display one entry, because later code will use getDocumentValue\n
item_list = [(\'\', \'\')]\n
\n
portal = context.getPortalObject()\n
\n
preferred_use_list = portal.portal_preferences.getPreferredEventResponseUseList()\n
\n
for notification_message in portal.portal_catalog(\n
        validation_state=\'validated\', portal_type=\'Notification Message\'):\n
  notification_message = notification_message.getObject()\n
  reference = notification_message.getReference()\n
  if reference and reference not in reference_set:\n
    reference_set.add(reference)\n
    service = notification_message.getSpecialiseValue()\n
    if response_only and preferred_use_list:\n
      if service is not None:\n
        for preferred_use in preferred_use_list:\n
          if service.isMemberOf(\'use/%s\' % preferred_use):\n
            item_list.append(\n
              (\'%s - %s\' % (reference, notification_message.getTranslatedTitle()), reference))\n
    else:\n
      item_list.append(\n
        (\'%s - %s\' % (reference, notification_message.getTranslatedTitle()), reference))\n
\n
return sorted(item_list)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>response_only=False</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_getNotificationMessageItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
