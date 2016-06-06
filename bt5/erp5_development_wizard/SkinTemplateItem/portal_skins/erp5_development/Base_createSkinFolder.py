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
            <value> <string>portal_skins = context.getPortalObject().portal_skins\n
skin_folder = portal_skins.manage_addProduct[\'OFSP\'].manage_addFolder(skin_folder_id)\n
\n
# Add the new skin folder at the top of portal_skins.\n
for skin_name, selection in portal_skins.getSkinPaths():\n
  new_selection = (\'%s,\' % skin_folder_id + selection).replace(",,",",")\n
  portal_skins.manage_skinLayers(skinpath = (new_selection,) , \n
                                 skinname = skin_name, \n
                                 add_skin = 1)\n
\n
return getattr(portal_skins, skin_folder_id)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>skin_folder_id</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Base_createSkinFolder</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
