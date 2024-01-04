""" This script will be called to apply the customization. """
from AccessControl import getSecurityManager
from erp5.component.module.Log import log

portal = context.getPortalObject()
bt = portal.portal_templates.getInstalledBusinessTemplate("erp5_demo_maxma_sample")
isTransitionPossible = portal.portal_workflow.isTransitionPossible

for obj in portal.portal_catalog(path=["%%/%s" % i.replace("**", "%") for i in bt.getTemplatePathList()]):
  obj.activate().updateLocalRolesOnSecurityGroups()

for document in portal.portal_catalog(portal_type=bt.getTemplatePortalTypeRoleList()):
  document.updateLocalRolesOnSecurityGroups()

conversion_server_url = portal.portal_preferences.getPreferredDocumentConversionServerUrl()
for preference_id in ["default_configurator_preference", "default_configurator_system_preference"]:
  preference = getattr(portal.portal_preferences, preference_id)
  if preference.getPortalType() == "System Preference":
    preference.setPreferredDocumentConversionServerUrl(conversion_server_url)

  if isTransitionPossible(preference, "enable"):
    preference.enable()
  preference.updateLocalRolesOnSecurityGroups()

for gadget in portal.portal_gadgets.objectValues():
  if gadget.getValidationState() == 'invisible':
    gadget.visible()
    gadget.public()

# set manually in 'Module Properties' respective business_application category
# XXX This should be part of Configuration Item probably, but as access_tab is
# going to be deprecated, make sure it still requires set business application
# info modules.
module_business_application_map = {'base': ('currency_module',
                                            'organisation_module',
                                            'person_module',),
                                   'accounting': ('accounting_module',
                                                  'account_module',),
                                   'crm': ('campaign_module',
                                           'event_module',
                                           'meeting_module',
                                           'sale_opportunity_module',
                                           'support_request_module',),
                                   'dms': ('document_module',
                                           'image_module',
                                           'document_ingestion_module',
                                           'web_page_module',),
                                   'trade': ('internal_packing_list_module',
                                             'inventory_module',
                                             'purchase_order_module',
                                             'purchase_packing_list_module',
                                             'purchase_trade_condition_module',
                                             'returned_sale_packing_list_module',
                                             'sale_order_module',
                                             'sale_packing_list_module',
                                             'sale_trade_condition_module'),
                                   'pdm': ('component_module',
                                           'product_module',
                                           'purchase_supply_module',
                                           'sale_supply_module',
                                           'service_module',
                                           'transformation_module',),
                                   }

for business_application_category_id, module_ids in module_business_application_map.items():
  for module_id in module_ids:
    module = getattr(portal, module_id, None)
    if module is not None:
      module.edit(business_application = business_application_category_id)

print("Indexing translations")
portal.ERP5Site_updateTranslationTable()

# clear cache so user security is recalculated
portal.portal_caches.clearAllCache()
print("Clear cache.")

log("%s" % printed)
