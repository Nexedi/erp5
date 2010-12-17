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
  Puts all the arguments from advanced search dialog form together as \n
  a parseable search string. Set it in the selection so it can be used\n
  in search form.\n
"""\n
portal = context.getPortalObject()\n
searchabletext = context.Base_assembleSearchString()\n
\n
selection_id = \'search_advanced_dialog_selection\'\n
selection_object = portal.portal_selections.getSelectionParamsFor(selection_id, {})\n
if selection_object:\n
  # update\n
  selection_object[\'searchabletext\'] = searchabletext\n
else:\n
  selection_object = {\'searchabletext\': searchabletext}\n
\n
selection_object[\'list_style\'] = \'search\'\n
portal.portal_selections.setSelectionParamsFor(selection_id, \\\n
                                               selection_object)\n
return context.Base_viewAdvancedSearchResultList()\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*a,**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_processAdvancedSearch</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
