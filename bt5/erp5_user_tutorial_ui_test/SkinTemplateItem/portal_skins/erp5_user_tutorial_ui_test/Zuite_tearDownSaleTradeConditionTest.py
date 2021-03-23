portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()

# remove the currency if it was created by us before
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['sale_howto_currency_title'],
                                                 local_roles = 'Owner')
if currency is not None:
  context.currency_module.deleteContent(currency.getId())

# remove the organisation of the test if existing
organisation_list = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                            title=howto_dict['sale_howto_organisation_title'])
if organisation_list is not None:
  portal.organisation_module.deleteContent(organisation_list[0].getId())

# remove the second organisation of the test if existing
organisation_list2 = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                            title=howto_dict['sale_howto_organisation2_title'])
if organisation_list2 is not None:
  portal.organisation_module.deleteContent(organisation_list2[0].getId())

# remove the organisation of the test if existing
person_list = context.Zuite_checkPortalCatalog(portal_type='Person', max_count=1,
                                                      title=howto_dict['sale_howto_person_title'])
if person_list is not None:
  portal.person_module.deleteContent(person_list[0].getId())

# remove related sale packing list and sale order
sale_order_list = context.Zuite_checkPortalCatalog(portal_type='Sale Order', max_count=1,
                                                          title=howto_dict['sale_howto_product_title'])
if sale_order_list is not None:
  for applied_rule in sale_order_list[0].getCausalityRelatedValueList(portal_type='Applied Rule'):
    applied_rule.getParentValue().deleteContent(applied_rule.getId())
  portal.sale_order_module.deleteContent(sale_order_list[0].getId())

# remove related sale packing list and sale order
sale_trade_condition_list = context.Zuite_checkPortalCatalog(portal_type='Sale Trade Condition', max_count=1,
                                                          title=howto_dict['sale_howto_trade_condition_title'])
if sale_trade_condition_list is not None:
  portal.sale_trade_condition_module.deleteContent(sale_trade_condition_list[0].getId())

# remove sale order created in the test
sale_order_in_test_list = context.Zuite_checkPortalCatalog(portal_type='Sale Order', max_count=1,
                                                          title=howto_dict['sale_howto_sale_order_title'])
if sale_order_in_test_list is not None:
  portal.sale_order_module.deleteContent(sale_order_in_test_list[0].getId())

pref = getattr(context.portal_preferences, howto_dict['howto_preference_id'], None)
if pref is not None:
  context.portal_preferences.deleteContent(howto_dict['howto_preference_id'])

portal.portal_caches.clearAllCache()

return "Clean Ok"
