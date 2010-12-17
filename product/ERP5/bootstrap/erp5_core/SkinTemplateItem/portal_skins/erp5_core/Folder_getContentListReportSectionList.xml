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
            <value> <string>from Products.ERP5Form.Report import ReportSection\n
from Products.ERP5Type.Message import Message\n
\n
form = context\n
request = context.REQUEST\n
report_section_list = []\n
portal = context.getPortalObject()\n
selection_name = request.get(\'selection_name\', None)\n
stool = portal.portal_selections\n
\n
def getFormIdFromAction(action):\n
  return action[\'url\'].split(\'/\')[-1].split(\'?\')[0]\n
\n
def getReportSectionForObject(doc):\n
  """ Get all possible report section for object. """\n
  doc = doc.getObject()\n
  actions = portal.portal_actions.listFilteredActionsFor(doc)\n
  # use the default view\n
  action = actions[\'object_view\'][0]\n
  # unless a print action exists\n
  if actions.get(\'object_print\'):\n
    # we ignore the default print action.\n
    valid_print_dialog_list = [ai for ai in actions[\'object_print\']\n
            if getFormIdFromAction(ai) != \'Base_viewPrintDialog\']\n
    if valid_print_dialog_list:\n
      action = valid_print_dialog_list[0]\n
    \n
  form_id = getFormIdFromAction(action)\n
  return ReportSection(path=doc.getPath(), form_id=form_id, title=doc.getTitleOrId())\n
\n
if selection_name is not None:\n
  # get all documents in the selection\n
  checked_uid_list = stool.getSelectionCheckedUidsFor(selection_name)\n
  if checked_uid_list:\n
    getObject = portal.portal_catalog.getObject\n
    for uid in checked_uid_list:\n
      report_section_list.append(getReportSectionForObject(getObject(uid)))\n
  else:\n
    for doc in stool.callSelectionFor(selection_name, context=context):\n
      report_section_list.append(getReportSectionForObject(doc))\n
\n
return report_section_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Folder_getContentListReportSectionList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
