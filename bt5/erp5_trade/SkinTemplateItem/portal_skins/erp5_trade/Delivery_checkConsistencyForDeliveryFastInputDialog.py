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
            <value> <string>"""This script check that values fit fast input requirements.\n
If validation succeeds, then form_dialog is returned.\n
Otherwise a message is displayed to the user.\n
"""\n
portal = context.getPortalObject()\n
# Retrieve lines portal type\n
line_portal_type_list = [x for x in context.getTypeInfo().getTypeAllowedContentTypeList() \\\n
                         if x in portal.getPortalMovementTypeList()]\n
line_portal_type = line_portal_type_list[0]\n
\n
use_list = []\n
# Check if the section and use preference are defined\n
if line_portal_type in context.getPortalSaleTypeList():\n
  section_uid = context.getSourceSectionUid()\n
  use_list = portal.portal_preferences.getPreferredSaleUseList()\n
elif line_portal_type in portal.getPortalPurchaseTypeList():\n
  section_uid = context.getDestinationSectionUid()\n
  use_list = portal.portal_preferences.getPreferredPurchaseUseList()\n
elif line_portal_type in portal.getPortalInternalTypeList() + portal.getPortalInventoryMovementTypeList():\n
  section_uid = ""\n
  use_list = portal.portal_preferences.getPreferredPurchaseUseList() + \\\n
             portal.portal_preferences.getPreferredSaleUseList()\n
else:\n
  from Products.ERP5Type.Message import translateString\n
  return context.Base_redirect(\'view\', keep_items=dict(\n
    portal_status_message=translateString(\'Type of document not known to retrieve section.\')))\n
\n
if len(use_list) == 0:\n
  from Products.ERP5Type.Message import translateString\n
  return context.Base_redirect(\'view\', keep_items=dict(\n
    portal_status_message=translateString(\'Use preference must be defined.\')))\n
  \n
if section_uid is None:\n
  from Products.ERP5Type.Message import translateString\n
  return context.Base_redirect(\'view\', keep_items=dict(\n
    portal_status_message=translateString(\'Section must be defined.\')))\n
\n
\n
return context.Delivery_viewDeliveryFastInputDialog(*args, **kw)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>*args, **kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>Delivery_checkConsistencyForDeliveryFastInputDialog</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
