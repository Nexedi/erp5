portal = context.getPortalObject()
howto_dict = context.Zuite_getHowToInfo()

# check if there is already the euro curency on the instance

invoice = context.portal_catalog.getResultValue(
                                   portal_type='Sale Invoice Transaction',
                                   title='ZUITE-TEST-SALEORDER-PRODUCT-001',)
if portal.portal_workflow.isTransitionPossible(invoice, "start"):
  invoice.start()
if not start_only:
  invoice.stop()
  invoice.deliver()
# Clear cache
portal.portal_caches.clearAllCache()

return "Init Ok"
