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
            <value> <string>from Products.ERP5Type.Message import translateString\n
\n
if id and id != context.getId():\n
  container = context.getParentValue()\n
\n
  # rename old one, if existing\n
  if id in container.objectIds():\n
    getattr(container, id).setId(container.generateNewId())\n
\n
  context.setId(id)\n
  return context.Base_redirect(form_id,\n
          keep_items=dict(selection_name=selection_name,\n
                          selection_index=selection_index,\n
                          portal_status_message=translateString("Function changed.")),)\n
\n
return context.Base_redirect(form_id,\n
          keep_items=dict(selection_name=selection_name,\n
                          selection_index=selection_index,\n
                          cancel_url=cancel_url,\n
                          portal_status_message=translateString("Cancelled.")),)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>id, selection_name=\'\', selection_index=\'0\', form_id=\'view\', cancel_url=\'\', **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_changeId</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
