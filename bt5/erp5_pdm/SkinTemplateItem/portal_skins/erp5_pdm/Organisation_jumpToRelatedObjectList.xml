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
Jump from Organisation to its related objects (but only if used as\n
source* or destination* categories) of the same portal type and\n
displayed using the module view\n
\n
XXX: move this code to erp5_core if needed elsewhere?\n
"""\n
portal = context.getPortalObject()\n
\n
# XXX: Seems there is no other better way to get the Arrow\n
#      destination/section categories...\n
base_category_list = []\n
for arrow_property in portal.portal_property_sheets.Arrow.contentValues():\n
  if arrow_property.getPortalType() != \'Category Property\':\n
    continue\n
\n
  arrow_property_title = arrow_property.getTitle()\n
  if (arrow_property_title.startswith(\'source\') or\n
      arrow_property_title.startswith(\'destination\')):\n
    base_category_list.append(arrow_property_title)\n
\n
related_object_list = context.getRelatedValueList(\n
  checked_permission=\'View\',\n
  base_category_list=base_category_list,\n
  portal_type=portal_type)\n
\n
if not related_object_list:\n
  message = portal.Base_translateString(\'No ${portal_type} related.\',\n
                                        mapping={\'portal_type\': portal_type})\n
\n
  return context.Base_redirect(keep_items=dict(portal_status_message=message))\n
\n
elif len(related_object_list) == 1:\n
  related_object = related_object_list[0]\n
  message = portal.Base_translateString(\n
    \'${this_portal_type} related to ${that_portal_type}: ${that_title}.\',\n
    mapping={"this_portal_type": related_object.getTranslatedPortalType(),\n
             "that_portal_type": context.getTranslatedPortalType(),\n
             "that_title": context.getTitleOrId()})\n
\n
  return related_object.Base_redirect(\n
    keep_items=dict(reset=1,\n
                    portal_status_message=message))\n
\n
else:\n
  # XXX: Use POST rather than GET because of GET URL length limitation?\n
  return portal.getDefaultModule(portal_type).Base_redirect(\n
    keep_items={\'reset\': 1,\n
                \'uid\': [obj.getUid() for obj in related_object_list]})\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>portal_type</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Organisation_jumpToRelatedObjectList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
