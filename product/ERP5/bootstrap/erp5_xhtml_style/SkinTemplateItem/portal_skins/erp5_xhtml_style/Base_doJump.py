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
            <value> <string># prevent lose checked itens after click to print\n
# For backward compatibility, do nothing if\n
# Base_updateListboxSelection cannot be found.\n
Base_updateListboxSelection = getattr(context, \'Base_updateListboxSelection\', None)\n
if Base_updateListboxSelection is not None:\n
  Base_updateListboxSelection()\n
\n
if select_jump is None:\n
  select_jump = context.REQUEST.form["Base_doJump"]\n
\n
if select_jump == \'\':\n
  return\n
\n
request = container.REQUEST\n
return context.ERP5Site_redirect(select_jump,\n
     keep_items=dict(form_id=request.get(\'form_id\', \'view\')), **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>select_jump=None, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_doJump</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
