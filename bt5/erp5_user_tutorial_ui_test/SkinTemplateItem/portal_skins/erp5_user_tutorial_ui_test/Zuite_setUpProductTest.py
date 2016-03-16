if clean:
  context.Zuite_tearDownProductTest()

howto_dict = context.Zuite_getHowToInfo()
portal = context.getPortalObject()
isTransitionPossible = portal.portal_workflow.isTransitionPossible

system_preference = portal.portal_preferences.getActiveSystemPreference()
base_category_list = system_preference.getPreferredProductIndividualVariationBaseCategoryList()
if 'variation' not in base_category_list:
  base_category_list.append('variation')
  system_preference.setPreferredProductIndividualVariationBaseCategoryList(base_category_list)

# check if there is already the euro curency on the instance
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['product_howto_currency_title'])
if currency is None:
  currency = portal.currency_module.newContent(portal_type='Currency',
                                               title=howto_dict['product_howto_currency_title'],
                                               reference=howto_dict['product_howto_currency_tag'],
                                               id=howto_dict['product_howto_currency_tag'],
                                               base_unit_quantity=0.01)

if isTransitionPossible(currency, 'validate'):
  currency.validate()


organisation = portal.organisation_module.newContent(
                 portal_type='Organisation',
                 title=howto_dict['product_howto_organisation_title'],
                 corporate_name=howto_dict['product_howto_organisation_title'])
organisation.validate()

portal.portal_caches.clearAllCache()

return "Init Ok"
