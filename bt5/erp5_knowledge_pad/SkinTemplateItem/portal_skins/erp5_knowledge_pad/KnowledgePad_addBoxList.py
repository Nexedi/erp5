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
            <value> <string>translate = context.Base_translateString\n
uids = kw.get(\'uids\', [])\n
cancel_url = kw.get(\'cancel_url\', None)\n
active_pad_relative_url = kw.get(\'active_pad_relative_url\', None)\n
knowledge_pad = context.restrictedTraverse(active_pad_relative_url)\n
not_added_gadgets_mesage = None\n
\n
selection_name = context.REQUEST.get(\'list_selection_name\', None)\n
if selection_name is not None:\n
  # maybe user already selected them in a previous page in a listbox selection\n
  portal_selection = context.portal_selections\n
  params = portal_selection.getSelectionParamsFor(selection_name, {})\n
  uids.extend(params.get(\'uids\', []))\n
\n
if len(uids):\n
  for uid in uids:\n
    gadget = context.portal_catalog(uid=uid)[0]\n
    multiple_instances_allowed = getattr(gadget,\'multiple_instances_allowed\', 0)\n
    # check if exists already such box specialising this gadget\n
    if multiple_instances_allowed or not knowledge_pad.searchFolder(portal_type = \'Knowledge Box\', \n
                                      validation_state = "!=deleted",\n
                                      specialise_uid = uid):\n
      # add as user has not added this gadget already\n
      knowledge_box = knowledge_pad.newContent(portal_type = \'Knowledge Box\')\n
      knowledge_box.setSpecialiseValue(gadget)\n
      knowledge_box.visible()\n
    else:\n
      not_added_gadgets_mesage = "You already have such gadgets."\n
  msg = \'Gadget added.\'\n
else:\n
  msg = \'Nothing to add.\'\n
\n
if not_added_gadgets_mesage is not None:\n
  msg = not_added_gadgets_mesage\n
\n
translated_msg = context.Base_translateString(msg)\n
if cancel_url is not None:\n
  cancel_url = \'%s?portal_status_message=%s\' %(cancel_url,translated_msg)\n
  context.REQUEST.RESPONSE.redirect(cancel_url)\n
else:\n
  context.Base_redirect(\'view\',\n
                        keep_items= {\'portal_status_message\':\n
                                     translated_msg})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>KnowledgePad_addBoxList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
