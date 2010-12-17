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
This script is called when a file is uploaded to an object via ERP5 standard interface.\n
It does the following:\n
\n
- determines portal types appropriate for the file type uploaded, and checks if the context portal type\n
  is one of those (this is not a complete check, but all we can do at this stage)\n
- checks if context already has some data (we do not allow re-upload of files)\n
Otherwise it just uploads the file, bumps up revision number and calls metadata discovery script.\n
\n
"""\n
\n
translateString = context.Base_translateString\n
request = context.REQUEST\n
current_type = context.getPortalType()\n
file_name = file.filename\n
\n
# we check for appropriate file type (by extension)\n
# ContributionTool_getCandidateTypeListByExtension script returns a tuple of\n
# one or more possible portal types for given extension\n
# we accept or suggest appropriate portal type\n
ext = file_name[file_name.rfind(\'.\')+1:]\n
candidate_type_list = context.ContributionTool_getCandidateTypeListByExtension(ext)\n
if candidate_type_list == () and current_type != \'File\':\n
  portal_status_message = translateString("Sorry, this is not one of ${portal_type}. This file should be uploaded into a file document.", \n
                                    mapping = dict(portal_type = str(candidate_type_list)))\n
  return context.Base_redirect(dialog_id, keep_items = dict(portal_status_message=portal_status_message,cancel_url = kw[\'cancel_url\']), **kw)\n
if candidate_type_list and current_type not in candidate_type_list:\n
  portal_status_message = translateString("Sorry, this is a ${portal_type}. This file should be uploaded into a ${appropriate_type} document.",\n
                                mapping = dict(portal_type = current_type, appropriate_type = str(candidate_type_list)))\n
  return context.Base_redirect(dialog_id, keep_items = dict(portal_status_message =portal_status_message, cancel_url = kw[\'cancel_url\']), **kw)\n
\n
context.edit(file=file)\n
context.activate().Document_convertToBaseFormatAndDiscoverMetadata(file_name=file_name)\n
\n
msg = translateString(\'File uploaded.\')\n
\n
# Return to view mode\n
return context.Base_redirect(form_id, keep_items = {\'portal_status_message\' : msg},  **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>dialog_id=None,form_id=None,file=None,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Document_uploadFile</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
