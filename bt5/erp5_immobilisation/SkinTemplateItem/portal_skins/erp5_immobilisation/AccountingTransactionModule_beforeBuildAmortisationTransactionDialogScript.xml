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
            <value> <string>from ZTUtils import make_query\n
\n
my_selection_name=\'accounting_module_build_amortisation_selection\'\n
if selection_name == my_selection_name:\n
  # Update the selection by adding new selected objects to \n
  # the list of already selected objects\n
  selected_uids = context.portal_selections.updateSelectionCheckedUidList(selection_name,listbox_uid,uids)\n
\n
  # Then take the full list of selected objects\n
  # selection_method should be the same method as the one used in listbox,\n
  # most of the time it is context.portal_catalog or context.searchFolder\n
  object_list= [x.getObject() for x in context.portal_selections.getSelectionValueList(selection_name,selection_method=context.portal_catalog)]\n
  # object_list is the list of selected objects, or it is the full list of objects\n
  # if there is not any object selected\n
else:\n
  object_list = []\n
\n
item_uid_list = [x.getUid() for x in object_list]\n
\n
url_params = make_query(form_id=form_id, \n
                        cancel_url=cancel_url,\n
                        item_uid_list=item_uid_list)\n
redirect_url = \'%s/AccountingTransactionModule_buildAmortisationTransactionDialog?%s\' %\\\n
                          (context.absolute_url(), url_params)\n
context.REQUEST[ \'RESPONSE\' ].redirect(redirect_url)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>selection_name=None,uids=None,listbox_uid=(),form_id=None,cancel_url=\'\',**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>AccountingTransactionModule_beforeBuildAmortisationTransactionDialogScript</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
