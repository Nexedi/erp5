from ZTUtils import LazyFilter
from Products.CMFCore.permissions import AccessContentsInformation


portal = context.getPortalObject()

def getCurrencyItemList(include_empty=1, validation_state=validation_state):
  result = []
  if include_empty :
    result = [('', ''),]
  currency_module = portal.restrictedTraverse(
                             'currency_module',
                             portal.restrictedTraverse('currency', None))

  if currency_module is not None:
    for currency in LazyFilter(currency_module.contentValues(), skip=AccessContentsInformation):
      if currency.getProperty('validation_state', 'validated') in validation_state:
        # for currency, we intentionaly use reference (EUR) not title (Euros).
        result.append((currency.getReference() or currency.getTitleOrId(),
                       currency.getRelativeUrl()))

  result.sort(key=lambda x: x[0])
  return result

from Products.ERP5Type.Cache import CachingMethod
getCurrencyItemList = CachingMethod(
                          getCurrencyItemList,
                          id='CurrencyModule_getCurrencyItemList',
                          cache_factory = 'erp5_ui_short')

return getCurrencyItemList(include_empty=include_empty,
                           validation_state=validation_state)
