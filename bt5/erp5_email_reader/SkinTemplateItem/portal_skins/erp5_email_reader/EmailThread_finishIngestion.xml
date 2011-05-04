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
            <value> <string encoding="cdata"><![CDATA[

# New mail must be received\n
if context.getValidationState() == \'draft\':\n
  context.receive()\n
\n
# We assign the mailbox\n
# (this should be moved to metadata discovery)\n
id = context.getId()\n
mailbox = id.split(\'-\')[0]\n
subject_list = mailbox.split(\'.\')\n
if not subject_list:\n
  subject_list = [\'INBOX\']\n
context.setSubjectList(subject_list)\n
\n
# Let us check if this is Junk\n
bogosity = context.getContentInformation().get(\'X-Bogosity\', \'No\')\n
if bogosity.startswith(\'Yes\') or bogosity.startswith(\'Spam\') or \'Junk\' in subject_list or \'Spam\' in subject_list:\n
  context.spam()\n
\n
# Let us check if this is sent by us\n
if context.getSender() and context.getSender().find(\'jp@nexedi.com\') >= 0 and context.getValidationState() == \'new\':\n
  if context.getRecipient() and context.getRecipient().find(\'jp@nexedi.com\') >= 0:\n
    pass\n
  else:\n
    context.markAsSent()\n
if context.getSender() and context.getSender().find(\'jp@tiolive.com\') >= 0 and context.getValidationState() == \'new\':\n
  if context.getRecipient() and context.getRecipient().find(\'jp@tiolive.com\') >= 0:\n
    pass\n
  else:\n
    context.markAsSent()\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>EmailThread_finishIngestion</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
