portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()

# check if there is already the euro curency on the instance

sale_packing_list = context.portal_catalog.getResultValue(
                                   portal_type='Sale Packing List',
                                   title='ZUITE-TEST-SALEORDER-PRODUCT-001',)
sale_packing_list.start()
sale_packing_list.deliver()
# Clear cache
portal.portal_caches.clearAllCache()

return "Init Ok"
