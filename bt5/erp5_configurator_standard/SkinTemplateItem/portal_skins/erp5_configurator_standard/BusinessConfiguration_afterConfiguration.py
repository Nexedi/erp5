""" This script will be called to apply the customization. """
from erp5.component.module.Log import log

portal = context.getPortalObject()
portal_preferences = portal.portal_preferences
business_template = context.getSpecialiseValue()

if business_template is not None:
  # update role settings for modules which exists already
  for portal_type in business_template.getTemplatePortalTypeRoleList():
    module_list = portal.contentValues(
                    filter=dict(portal_type=portal_type))
    for module in module_list:
      module.updateLocalRolesOnSecurityGroups()
      print("Updated Role Mappings for: %s(%s) " % (module.getTitle(), module.getPortalType()))

  # validate and open all objects
  for path in business_template.getTemplatePathList():
    obj = portal.restrictedTraverse(path, None)
    if obj is not None and hasattr(obj, 'getPortalType'):
      # XXX This hardcoded list is a bit inconvinient.

      if obj.getPortalType() not in ('Category', 'Base Category',):
        obj.updateLocalRolesOnSecurityGroups()
        print("Updated Role Mappings for: ", path, obj.getPortalType())

      if obj.getPortalType() in ('Person', 'Organisation'):
        for period in obj.contentValues(filter={'portal_type':'Accounting Period'}):
          period.updateLocalRolesOnSecurityGroups()
          print("\tOpen (Accounting Period): ", period.getRelativeUrl())

        for assignment in obj.contentValues(filter={'portal_type':'Assignment'}):
          assignment.updateLocalRolesOnSecurityGroups()
          print("\tOpen (assignment): ", assignment.getRelativeUrl())

  for solver_type in context.portal_solvers.objectValues():
    solver_type.updateLocalRolesOnSecurityGroups()

  for gadget in context.portal_gadgets.objectValues():
    if gadget.getValidationState() == 'invisible':
      gadget.visible()
      gadget.public()



# update security settings for default preference # XXX why ???
default_configurator_preference = getattr(portal_preferences,
                                          'default_configurator_preference', None)
if default_configurator_preference is not None:
  default_configurator_preference.updateLocalRolesOnSecurityGroups()

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

# activate all available languages to allow user can select them in the ERP5JS UI
osoe_runner_website = getattr(portal.web_site_module, "osoe_runner", None)
if osoe_runner_website is not None:
  available_language_list = list(portal.Localizer.get_supported_languages())
  osoe_runner_website.edit(available_language_set = available_language_list)

print("Indexing translations")
portal.ERP5Site_updateTranslationTable()

# clear cache so user security is recalculated
portal.portal_caches.clearAllCache()
print("Clear cache.")

log("%s" % printed)
