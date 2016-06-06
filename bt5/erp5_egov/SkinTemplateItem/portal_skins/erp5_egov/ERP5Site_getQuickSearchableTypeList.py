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
            <value> <string>from AccessControl import getSecurityManager\n
user=getSecurityManager().getUser()\n
\n
portal_types = context.getPortalObject().portal_types\n
validated_type_list = portal_types.searchFolder(portal_type=\'EGov Type\', validation_state = \'validated\')\n
access_permission= \'Access contents information\'\n
view_permission = \'View\'\n
\n
portal_type_list = ()\n
for ptype_title in [\'Person\', \'Organisation\']:\n
  default_module = context.getDefaultModule(ptype_title)\n
  if user.has_permission(access_permission,default_module) or user.has_permission(view_permission,default_module):\n
    portal_type_list += (ptype_title,)\n
  \n
for ptype in validated_type_list:\n
  default_module = context.getDefaultModule(ptype.getTitle())\n
  if user.has_permission(access_permission,default_module) or user.has_permission(view_permission,default_module):\n
    portal_type_list += (ptype.getTitle(),)\n
\n
return portal_type_list\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>ERP5Site_getQuickSearchableTypeList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
