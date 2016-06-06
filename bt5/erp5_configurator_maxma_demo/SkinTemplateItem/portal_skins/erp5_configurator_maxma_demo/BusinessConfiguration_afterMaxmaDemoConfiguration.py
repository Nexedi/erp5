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
            <value> <string>""" This script will be called to apply the customization. """\n
from AccessControl import getSecurityManager\n
from Products.ERP5Type.Log import log\n
\n
portal = context.getPortalObject()\n
bt = portal.portal_templates.getInstalledBusinessTemplate("erp5_demo_maxma_sample")\n
isTransitionPossible = portal.portal_workflow.isTransitionPossible\n
\n
for obj in portal.portal_catalog(path=["%%/%s" % i.replace("**", "%") for i in bt.getTemplatePathList()]):\n
  obj.activate().updateLocalRolesOnSecurityGroups()\n
\n
for document in portal.portal_catalog(portal_type=bt.getTemplatePortalTypeRoleList()):\n
  document.updateLocalRolesOnSecurityGroups()\n
\n
conversion_server_hostname = portal.portal_preferences.getPreferredOoodocServerAddress()\n
conversion_server_port = portal.portal_preferences.getPreferredOoodocServerPortNumber()\n
for preference_id in ["default_configurator_preference", "default_configurator_system_preference"]:\n
  preference = getattr(portal.portal_preferences, preference_id)\n
  if preference.getPortalType() == "System Preference":\n
    preference.setPreferredOoodocServerPortNumber(conversion_server_port)\n
    preference.setPreferredOoodocServerAddress(conversion_server_hostname)\n
\n
  if isTransitionPossible(preference, "enable"):\n
    preference.enable()\n
  preference.updateLocalRolesOnSecurityGroups()\n
\n
for gadget in portal.portal_gadgets.objectValues():\n
  if gadget.getValidationState() == \'invisible\':\n
    gadget.visible()\n
    gadget.public()\n
\n
# set manually in \'Module Properties\' respective business_application category\n
# XXX This should be part of Configuration Item probably, but as access_tab is\n
# going to be deprecated, make sure it still requires set business application\n
# info modules.\n
module_business_application_map = {\'base\': (\'currency_module\',\n
                                            \'organisation_module\',\n
                                            \'person_module\',),\n
                                   \'accounting\': (\'accounting_module\',\n
                                                  \'account_module\',),\n
                                   \'crm\': (\'campaign_module\',\n
                                           \'event_module\',\n
                                           \'meeting_module\',\n
                                           \'sale_opportunity_module\',\n
                                           \'support_request_module\',),\n
                                   \'dms\': (\'document_module\',\n
                                           \'image_module\',\n
                                           \'document_ingestion_module\',\n
                                           \'web_page_module\',),\n
                                   \'trade\': (\'internal_packing_list_module\',\n
                                             \'inventory_module\',\n
                                             \'purchase_order_module\',\n
                                             \'purchase_packing_list_module\',\n
                                             \'purchase_trade_condition_module\',\n
                                             \'returned_sale_packing_list_module\',\n
                                             \'sale_order_module\',\n
                                             \'sale_packing_list_module\',\n
                                             \'sale_trade_condition_module\'),\n
                                   \'pdm\': (\'component_module\',\n
                                           \'product_module\',\n
                                           \'purchase_supply_module\',\n
                                           \'sale_supply_module\',\n
                                           \'service_module\',\n
                                           \'transformation_module\',),\n
                                   }\n
\n
for business_application_category_id, module_ids in module_business_application_map.items():\n
  for module_id in module_ids:\n
    module = getattr(portal, module_id, None)\n
    if module is not None:\n
      module.edit(business_application = business_application_category_id)\n
\n
print "Indexing translations"\n
portal.ERP5Site_updateTranslationTable()\n
\n
# clear cache so user security is recalculated\n
portal.portal_caches.clearAllCache()\n
print "Clear cache."\n
\n
log("%s" % printed)\n
</string> </value>
        </item>
        <item>
            <key> <string>_params</string> </key>
            <value> <string>**kw</string> </value>
        </item>
        <item>
            <key> <string>id</string> </key>
            <value> <string>BusinessConfiguration_afterMaxmaDemoConfiguration</string> </value>
        </item>
      </dictionary>
    </pickle>
  </record>
</ZopeData>
