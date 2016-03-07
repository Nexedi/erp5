portal = context.getPortalObject()

howto_dict = context.Zuite_getHowToInfo()

# remove the currency if it was created by us before
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['product_howto_currency_title'],
                                                 local_roles = 'Owner')
if currency is not None:
  context.currency_module.deleteContent(currency.getId())

# remove the product of the test if existing
product_list = context.Zuite_checkPortalCatalog(portal_type='Product', max_count=1,
                                                title=context.Zuite_getHowToInfo()['product_howto_product_title'])
if product_list is not None:
  portal.product_module.deleteContent(product_list[0].getId())

# remove the organisation of the test if existing
organisation_list = context.Zuite_checkPortalCatalog(portal_type='Organisation', max_count=1,
                                                     title=context.Zuite_getHowToInfo()['product_howto_organisation_title'])
if organisation_list is not None:
  portal.organisation_module.deleteContent(organisation_list[0].getId())

return "Clean Ok"
