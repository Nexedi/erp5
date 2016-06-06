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
            <value> <string># prevent lose of checked itens at listbox after click to print\n
# Do what Base_updateListboxSelection does, overwriting listbox_uid\n
\n
import ipdb\n
ipdb.set_trace()\n
\n
selection_name = context.REQUEST.get(\'list_selection_name\', None)\n
listbox_uid = context.REQUEST.get(\'knowledge_pad_module_ung_knowledge_pad_ung_docs_listbox_content_listbox_uid\', None)\n
uids = context.REQUEST.get(\'uids\', None)\n
context.portal_selections.updateSelectionCheckedUidList(listbox_uid = listbox_uid,\n
                                                        uids=uids,\n
                                                        selection_name=selection_name,\n
                                                        REQUEST=context.REQUEST)\n
\n
gadget_form_id = context.REQUEST.get(\'gadget_form_id\', \'erp5_web_ung_content_layout\')\n
keep_items=dict(\n
    form_id=gadget_form_id,\n
    selection_name=selection_name)\n
\n
\n
#return context.ERP5Site_redirect(\'Folder_viewWorkflowActionDialog\', keep_items=keep_items, **kw)\n
#return context, context.REQUEST, context.REQUEST.form, context.REQUEST.get(\'list_selection_name\', None), kw\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>WebSection_changeStateHelperUpdatePortalSelections</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
