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
  This script is invoked at the end of ingestion process.\n
  The default behaviour is to receive messages so that they\n
  are marked as \'New\' and appear in the worklist.\n
"""\n
\n
group_list = context.getGroupList()\n
function_list = context.getFunctionList()\n
site_list = context.getSiteList()\n
classification = context.getClassification()\n
publication_section_list = context.getPublicationSectionList()\n
owner = context.getSourceValue()\n
\n
# Documents ingested by unknown person\n
# can not be processed further\n
if owner is None:\n
  return\n
user_login = owner.getReference()\n
if not user_login:\n
  return\n
\n
# Build metadata dict\n
metadata = {}\n
if group_list: metadata[\'group_list\'] = group_list\n
if function_list: metadata[\'function_list\'] = function_list\n
if site_list: metadata[\'site_list\'] = site_list \n
if classification: metadata[\'classification\'] = classification \n
if publication_section_list: metadata[\'publication_section_list\'] = publication_section_list\n
\n
contribution_tool = context.getPortalObject().portal_contributions\n
\n
# Ingest attachments\n
for attachment_item in context.getAttachmentInformationList():\n
  # We do not care about files without name\n
  filename = attachment_item.get(\'filename\')\n
  # We do not take into account the message itself\n
  # XXX - this implementation is not acceptable in\n
  # the long term. Better approach to defining the\n
  # body of a message is required\n
  if filename and not filename.startswith(\'part\'):\n
    index = attachment_item[\'index\']\n
    data = context.getAttachmentData(index)\n
    # XXX - too bad we are not using content_type here\n
    d = contribution_tool.newContent(data=data, filename=filename, user_login=user_login, **metadata)\n
    context.setAggregateList(context.getAggregateList() + [d.getRelativeUrl()])\n
\n
context.receive()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>DocumentIngestionMessage_finishIngestion</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
