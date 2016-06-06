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
            <value> <string>portal = context.getPortalObject()\n
translateString = portal.Base_translateString\n
transformation_value_list = context.getRelatedValueList(checked_permission=\'View\',\n
                                                        portal_type=(\'Transformation\',\n
                                                                     \'Transformation Transformed Resource\'))\n
if len(transformation_value_list) == 0:\n
  return context.Base_redirect(\'view\',\n
                               keep_items=dict(portal_status_message=translateString(\'No Transformation related.\')))\n
elif len(transformation_value_list) == 1:\n
  related_object = transformation_value_list[0]\n
  if related_object.getPortalType() == \'Transformation Transformed Resource\':\n
    related_object = related_object.getParentValue()\n
  return related_object.Base_redirect(\n
    \'view\',\n
    keep_items=dict(reset=1,\n
                    portal_status_message=translateString(\'${this_portal_type} related to ${that_portal_type} : ${that_title}.\',\n
                                                          mapping={"this_portal_type": related_object.getTranslatedPortalType(),\n
                                                                   "that_portal_type": context.getTranslatedPortalType(),\n
                                                                   "that_title": context.getTitleOrId()})))\n
else:\n
  transformation_uid_list = []\n
  for value in transformation_value_list:\n
    if value.getPortalType() == \'Transformation Transformed Resource\':\n
      uid = value.getParentUid()\n
    else:\n
      uid = value.getUid()\n
\n
    transformation_uid_list.append(uid)\n
\n
  module = portal.getDefaultModule(\'Transformation\')\n
  return module.Base_redirect(\'view\',\n
                              keep_items=dict(reset=1,\n
                                              uid=transformation_uid_list))\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Resource_jumpToRelatedTransformation</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
