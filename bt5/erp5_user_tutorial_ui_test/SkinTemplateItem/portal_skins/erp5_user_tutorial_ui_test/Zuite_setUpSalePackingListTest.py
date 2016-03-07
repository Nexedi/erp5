
portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()

# check if there is already the euro curency on the instance
currency = context.portal_catalog.getResultValue(portal_type='Currency',
                                                 title=howto_dict['sale_howto_currency_title'])

# add default sale order trade condition
sale_order_trade_condition = context.portal_catalog.getResultValue(portal_type='Sale Trade Condition',
                                                                  reference='STC-General')

# Get the documents created by setUpSaleOrder
product = context.portal_catalog.getResultValue(portal_type='Product',
                                             title=howto_dict['sale_howto_product_title'])

my_organisation = context.portal_catalog.getResultValue(portal_type='Organisation',
                                                        title=howto_dict['sale_howto_organisation_title'])

organisation = context.portal_catalog.getResultValue(portal_type='Organisation',
                                                     title=howto_dict['sale_howto_organisation2_title'])

person = context.portal_catalog.getResultValue(portal_type='Person',
                                         title=howto_dict['sale_howto_person_title'])


sale_order = portal.sale_order_module.newContent(
                                   portal_type='Sale Order',                                   title='ZUITE-TEST-SALEORDER-PRODUCT-001',                                   specialise=sale_order_trade_condition.getRelativeUrl(),
                                   destination_section=organisation.getRelativeUrl(),
                                   destination=organisation.getRelativeUrl(),
                                   source_section=my_organisation.getRelativeUrl(),
                                   source=my_organisation.getRelativeUrl(),
                                   source_decision=my_organisation.getRelativeUrl(),
                                   destination_decision=organisation.getRelativeUrl(),
                                   destination_administration=person.getRelativeUrl(),
                                   source_administration=my_organisation.getRelativeUrl(),
                                   delivery_mode='delivery_mode/air',
                                   order='order/normal',
                                   start_date=DateTime().earliestTime(),
                                   stop_date=DateTime().earliestTime()+1,
)
sale_order.setPriceCurrency(currency.getRelativeUrl())
sale_order.setIncoterm('incoterm/cpt')

sale_order.newContent(portal_type='Sale Order Line',
                      resource=product.getRelativeUrl(), price=1.0, quantity=100000.0)
sale_order.confirm()
# Clear cache
portal.portal_caches.clearAllCache()

return "Init Ok"
