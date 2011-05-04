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
            <value> <string>request = container.REQUEST\n
kw.update(request.form)\n
\n
portal = context.getPortalObject()\n
\n
# Base_updateListboxSelection cannot be found.\n
Base_updateListboxSelection = getattr(context, \'Base_updateListboxSelection\', None)\n
if Base_updateListboxSelection is not None:\n
  Base_updateListboxSelection()\n
\n
action_context = portal.restrictedTraverse(request.get(\'object_path\', \'?\'), context)\n
\n
new_print_action_list = context.Base_fixDialogActions(\n
     context.Base_filterDuplicateActions(\n
     portal.portal_actions.listFilteredActionsFor(action_context)), \'object_report\')\n
\n
if new_print_action_list:\n
  return context.ERP5Site_redirect(new_print_action_list[0][\'url\'],\n
                                                           keep_items={\'form_id\': form_id,\n
                                                           \'cancel_url\': cancel_url,\n
                                                           \'object_path\': request.get(\'object_path\', context.getPath()),\n
                                                           \'dialog_category\': \'object_report\'}, **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>form_id, cancel_url, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_doReport</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
