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

"""\n
  This script is called during the metadata discovery process\n
  for each document which has been ingested through the email interface\n
  by portal contributions. It tries to analyse the text content \n
  to define the different event parameters.\n
\n
  This version provides only early support.\n
"""\n
\n
def getPersonList(information_text):\n
  result = []\n
  for recipient in information_text.split(\',\'):\n
    if "<" in recipient:\n
      recipient = recipient[recipient.find(\'<\') + 1:]\n
      recipient = recipient[:recipient.find(\'>\')]\n
    if recipient:\n
      email = context.portal_catalog.getResultValue(url_string=recipient, portal_type="Email")\n
      if email is not None:\n
        result.append(email.getParentValue().getRelativeUrl())\n
  return result\n
\n
content_information = context.getContentInformation()\n
sender_list = getPersonList(content_information.get(\'From\', \'\'))\n
\n
# Build references\n
reference_search_list = []\n
text_search_list = []\n
for text, prop_dict in context.getSearchableReferenceList():\n
  if text: text_search_list.append(text)\n
  if prop_dict.has_key(\'reference\'): reference_search_list.append(prop_dict[\'reference\'])\n
\n
# Search reference ticket or project\n
follow_up_type_list = context.getPortalProjectTypeList() + context.getPortalTicketTypeList()\n
follow_up = context.portal_catalog.getResultValue(reference=reference_search_list, portal_type=follow_up_type_list)\n
if follow_up is None:\n
  follow_up = context.portal_catalog.getResultValue(reference=text_search_list, portal_type=follow_up_type_list)\n
\n
# Build dict.\n
result = {}\n
if sender_list: result[\'source_list\'] = sender_list\n
if follow_up is not None: result[\'follow_up\'] = follow_up.getRelativeUrl()\n
\n
return result\n


]]></string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DocumentIngestionMessage_getPropertyDictFromContent</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
