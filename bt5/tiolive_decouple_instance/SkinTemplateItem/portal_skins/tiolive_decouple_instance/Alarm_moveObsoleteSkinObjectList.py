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
 Decoupling the instance we need to move the Form used to create person\n
 and also the script used.\n
\n
 Those objects are customized into portal_skins/express_customization\n
 and must be moved to tiolive_decouple_obsolete.\n
\n
 The folder tiolive_decouple_obsolete is created only when it is required\n
 and it is not present into portal skins selection.\n
"""\n
from Products.ERP5Type.Log import log\n
portal = context.getPortalObject()\n
obsolete_object_list = [\'Person_createUser\',\n
                        \'Person_viewCreateUserActionDialog\']\n
\n
express_customisation_folder = getattr(portal.portal_skins, "express_customisation", None)\n
if express_customisation_folder is None:\n
  express_customisation_folder = getattr(portal.portal_skins, "express_customisation_user_synchronization", None)\n
  if express_customisation_folder is None:\n
    return True\n
\n
obsolete_skin_folder_id = "tiolive_decouple_obsolete"\n
obsolete_skin_folder = getattr(portal.portal_skins, obsolete_skin_folder_id, None)\n
if obsolete_skin_folder is None:\n
  portal.portal_skins.manage_addFolder(id=obsolete_skin_folder_id)\n
\n
try:\n
  object_list = express_customisation_folder.manage_cutObjects(obsolete_object_list)\n
  portal.portal_skins[obsolete_skin_folder_id].manage_pasteObjects(object_list)\n
except AttributeError:\n
  log(\'FAILED to move %s to %s skin folder. Please check is the objects are already into %s.\' % \\\n
                          (obsolete_object_list, obsolete_skin_folder_id, obsolete_skin_folder_id))\n
  return False\n
\n
return True\n
</string> </value>
        </item>
        <item>
            <key> <string>_code</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>_proxy_roles</string> </key>
            <value>
              <tuple>
                <string>Manager</string>
              </tuple>
            </value>
        </item>
        <item>
            <key> <string>errors</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
        <item>
            <key> <string>func_code</string> </key>
            <value>
              <object>
                <klass>
                  <global name="FuncCode" module="Shared.DC.Scripts.Signature"/>
                </klass>
                <tuple/>
                <state>
                  <dictionary>
                    <item>
                        <key> <string>co_argcount</string> </key>
                        <value> <int>0</int> </value>
                    </item>
                    <item>
                        <key> <string>co_varnames</string> </key>
                        <value>
                          <tuple>
                            <string>Products.ERP5Type.Log</string>
                            <string>log</string>
                            <string>_getattr_</string>
                            <string>context</string>
                            <string>portal</string>
                            <string>obsolete_object_list</string>
                            <string>getattr</string>
                            <string>None</string>
                            <string>express_customisation_folder</string>
                            <string>True</string>
                            <string>obsolete_skin_folder_id</string>
                            <string>obsolete_skin_folder</string>
                            <string>object_list</string>
                            <string>_getitem_</string>
                            <string>AttributeError</string>
                            <string>False</string>
                          </tuple>
                        </value>
                    </item>
                  </dictionary>
                </state>
              </object>
            </value>
        </item>
        <item>
            <key> <string>func_defaults</string> </key>
            <value>
              <none/>
            </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Alarm_moveObsoleteSkinObjectList</string> </value>
        </item>
        <item>
            <key> <string>warnings</string> </key>
            <value>
              <tuple/>
            </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
