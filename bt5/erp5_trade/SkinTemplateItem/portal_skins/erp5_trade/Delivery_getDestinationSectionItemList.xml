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
            <value> <string>from Products.ERP5Type.Log import log\n
log(\'Deprecated: use Base_getPreferredSectionItemList instead.\')\n
\n
section_cat = context.portal_preferences.getPreferredSectionCategory()\n
if section_cat in (None, \'\') : \n
  section_cat = context.getPortalDefaultSectionCategory()\n
\n
section_cat_obj = None\n
result = []\n
\n
if section_cat is not None:\n
  # get the organisations belonging to this group\n
  section_cat_obj = context.portal_categories.resolveCategory(section_cat)\n
\n
if section_cat_obj is not None:\n
  result = section_cat_obj.getGroupRelatedValueList(portal_type=\'Organisation\',\n
                                                    checked_permission=\'View\')\n
  result = [r for r in result\n
            if r.getProperty(\'validation_state\') not in (\'invalidated\', \'deleted\')]\n
\n
current_destination_section = context.getDestinationSectionValue()\n
if current_destination_section is not None and current_destination_section not in result:\n
  result.append(current_destination_section)\n
\n
# convert to ListField format\n
return [(\'\', \'\')] + [(i.getTitle(), i.getRelativeUrl()) for i in result]\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string></string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_getDestinationSectionItemList</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
