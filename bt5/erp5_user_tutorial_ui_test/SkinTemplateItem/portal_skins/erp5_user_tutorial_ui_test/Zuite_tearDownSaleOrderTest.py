portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()

# remove the currency if it was created by us before
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['sale_howto_currency_title'],
                                                 local_roles = 'Owner')
if currency is not None:
  context.currency_module.deleteContent(currency.getId())

# remove the product of the test if existing
product_list = context.Zuite_checkPortalCatalog(portal_type='Product', max_count=1,
                                                       title=howto_dict['sale_howto_product_title'])
if product_list is not None:
  portal.product_module.deleteContent(product_list[0].getId())

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

# remove the third organisation of the test if existing
organisation_list3 = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                             title=howto_dict['sale_howto_organisation3_title'])
if organisation_list3 is not None:
  portal.organisation_module.deleteContent(organisation_list3[0].getId())

# remove the organisation of the test if existing
person_list = context.Zuite_checkPortalCatalog(portal_type='Person', max_count=1,
                                                      title=howto_dict['sale_howto_person_title'])
if person_list is not None:
  portal.person_module.deleteContent(person_list[0].getId())

# remove related sale packing list and sale order
sale_packing_list_list = context.Zuite_checkPortalCatalog(portal_type='Sale Packing List',
                                                                 title=howto_dict['sale_howto_product_title'])
if sale_packing_list_list is not None:
  for sale_packing_list in sale_packing_list_list:
    portal.sale_packing_list_module.deleteContent(sale_packing_list.getId())

sale_order_list = context.Zuite_checkPortalCatalog(portal_type='Sale Order', max_count=1,
                                                          title=howto_dict['sale_howto_product_title'])
if sale_order_list is not None:
  for applied_rule in sale_order_list[0].getCausalityRelatedValueList(portal_type='Applied Rule'):
    applied_rule.getParentValue().deleteContent(applied_rule.getId())
  portal.sale_order_module.deleteContent(sale_order_list[0].getId())

sale_invoice_transaction_list = context.Zuite_checkPortalCatalog(portal_type='Sale Invoice Transaction',
                                                                       title=howto_dict['sale_howto_product_title'])
if sale_invoice_transaction_list is not None:
  for sale_invoice_transaction in sale_invoice_transaction_list:
    portal.accounting_module.deleteContent(sale_invoice_transaction.getId())

payment_transaction_list = context.Zuite_checkPortalCatalog(portal_type='Payment Transaction', max_count=1,
                                                                  title=howto_dict['sale_howto_payment_title'])
if payment_transaction_list is not None:
  for applied_rule in payment_transaction_list[0].getCausalityRelatedValueList(portal_type='Applied Rule'):
    applied_rule.getParentValue().deleteContent(applied_rule.getId())
  portal.accounting_module.deleteContent(payment_transaction_list[0].getId())

# remove created accounting periods
accounting_period_list = context.Zuite_checkPortalCatalog(portal_type='Accounting Period', max_count=1,
                                                            title=howto_dict['optional_new_accounting_period_title'])
if accounting_period_list is not None:
  accounting_period_list[0].getParentValue().deleteContent(accounting_period_list[0].getId())


pref = getattr(context.portal_preferences, howto_dict['howto_preference_id'], None)
if pref is not None:
  context.portal_preferences.deleteContent(howto_dict['howto_preference_id'])

portal.portal_caches.clearAllCache()

return "Clean Ok"
