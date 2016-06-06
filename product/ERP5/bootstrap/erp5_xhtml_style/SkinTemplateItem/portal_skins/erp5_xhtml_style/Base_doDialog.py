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
            <value> <string># prevent lose checked itens at listbox after click to print\n
# For backward compatibility, do nothing if\n
# Base_updateListboxSelection cannot be found.\n
Base_updateListboxSelection = getattr(context, \'Base_updateListboxSelection\', None)\n
if Base_updateListboxSelection is not None:\n
  Base_updateListboxSelection()\n
\n
kw.update(context.REQUEST.form)\n
keep_items=dict(\n
    dialog_category=dialog_category,\n
    form_id=form_id,\n
    cancel_url=cancel_url,\n
    object_path=object_path)\n
\n
return context.ERP5Site_redirect(select_dialog.split()[0], keep_items=keep_items, **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>select_dialog, dialog_category, form_id, cancel_url, object_path, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_doDialog</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
