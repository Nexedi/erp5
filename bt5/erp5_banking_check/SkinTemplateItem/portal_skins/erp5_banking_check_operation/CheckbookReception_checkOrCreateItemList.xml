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
            <value> <string># It was decided that it is possible to receive in an agency only\n
# checks and checkbooks for accounts managed by that agency. Moreover\n
# we have decided that we will not allow many checkbook reception at\n
# a time inside an agency, like this we can create many activities with\n
# the tag "CheckbookReception_[Agency Code or Url]" in order to make sure\n
# we will not do duplicate (of course we check that there is not already\n
# a check or checkbook with this references.\n
\n
from Products.DCWorkflow.DCWorkflow import ValidationFailed\n
from Products.ERP5Type.Message import Message\n
\n
destination_id = context.getDestinationId()\n
if destination_id is None:\n
  msg = Message(domain=\'ui\', message=\'Sorry, you must define the site\')\n
  raise ValidationFailed, (msg, )\n
\n
# serialize destination vault to only have one operation at a time\n
destination_value = context.getDestinationValue()\n
destination_value.serialize()\n
line_list = context.objectValues(portal_type=\'Checkbook Reception Line\')\n
\n
for line in line_list:\n
  if not line.getResourceValue().isUniquePerAccount():\n
    checkbook_reception_tag = "CheckbookReception_global"\n
    msg = Message(domain=\'ui\', message=\'Sorry, there is already a pending checkbook reception\')\n
    break\n
else:\n
  msg = Message(domain=\'ui\', message=\'Sorry, there is already a checkbook reception newly validated\')\n
  checkbook_reception_tag = "CheckbookReception_%s" % destination_id\n
if context.portal_activities.countMessageWithTag(checkbook_reception_tag) != 0:\n
  raise ValidationFailed, (msg, )\n
\n
if check == 1:\n
  encountered_check_identifiers_dict = {}\n
  for line in line_list:\n
    encountered_check_identifiers_dict = line.CheckbookReceptionLine_checkOrCreateItemList(check=1, \n
         encountered_check_identifiers_dict=encountered_check_identifiers_dict)\n
\n
if create==1:\n
  for line in line_list:\n
    line.activate(priority=4, tag=checkbook_reception_tag).\\\n
        CheckbookReceptionLine_checkOrCreateItemList(create=1, tag=checkbook_reception_tag, confirm_check=confirm_check)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>check=0, create=0, confirm_check=0</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>CheckbookReception_checkOrCreateItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
