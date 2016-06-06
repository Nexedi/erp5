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
  This script is called during the metadata discovery process\n
  for each event which has been ingested through the email interface\n
  by portal contributions. It tries to analyse the text content \n
  to define the different event parameters.\n
\n
  This version provides only early support.\n
\n
  TODO:\n
  - support forwarded messages\n
  - support incoming / outgoing messages (in releation with \n
    Event_finishIngestion)\n
"""\n
\n
getResultValue = context.getPortalObject().portal_catalog.getResultValue\n
Base_getEntityListFromFromHeader = context.Base_getEntityListFromFromHeader\n
def getEntityList(text):\n
  return [entity.getRelativeUrl()\n
          for entity in Base_getEntityListFromFromHeader(text)]\n
\n
content_information = context.getContentInformation()\n
sender_list = context.getSourceList() or getEntityList(content_information.get(\'From\', \'\'))\n
to_list = context.getDestinationList() or getEntityList(content_information.get(\'To\', \'\'))\n
cc_list = getEntityList(content_information.get(\'CC\', \'\'))\n
\n
# Build references\n
reference_search_list = []\n
text_search_list = []\n
for text, prop_dict in context.getSearchableReferenceList():\n
  if text:\n
    text_search_list.append(text)\n
  if prop_dict.has_key(\'reference\'):\n
    reference_search_list.append(prop_dict[\'reference\'])\n
\n
# Search reference ticket or project\n
follow_up_type_list = context.getPortalProjectTypeList() + context.getPortalTicketTypeList()\n
follow_up = None\n
if reference_search_list:\n
  follow_up = getResultValue(reference=reference_search_list, portal_type=follow_up_type_list)\n
if follow_up is None and text_search_list:\n
  follow_up = getResultValue(reference=text_search_list, portal_type=follow_up_type_list)\n
\n
# Find portal type\n
subject = content_information.get(\'Subject\', \'\')\n
body = context.asText()\n
portal_type = None\n
for text in (subject, body):\n
  portal_type, matched_value = context.Base_findPortalTypeNameAndMatchedValueForEvent(text)\n
  if portal_type is not None:\n
    break\n
\n
# Build dict.\n
result = {}\n
if sender_list:\n
  result[\'source_list\'] = sender_list\n
if to_list or cc_list:\n
  result[\'destination_list\'] = to_list + cc_list\n
if follow_up is not None:\n
  result[\'follow_up\'] = follow_up.getRelativeUrl()\n
if portal_type is not None:\n
  result[\'portal_type\'] = portal_type\n
\n
return result\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Event_getPropertyDictFromContent</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
