currency = context.Baobab_getPortalReferenceCurrencyID()
try:
  currency_object = context.restrictedTraverse('currency_module/%s' %(currency,))
  context.setResourceValue(currency_object)
except KeyError:
  context.log("MonetaryReception_init", "Cannot set resource value for object %s" %(context,))
  pass
