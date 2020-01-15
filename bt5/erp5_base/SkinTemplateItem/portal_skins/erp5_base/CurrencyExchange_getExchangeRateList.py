# This script will calculate the exchange value for the current
# context. If to_currency is provided, then instead of using
# the context, it will generate a temp object.

# Handle the case where from_currency is to_currency
# Assumes that 2 currencies with the same ID, they are the same currency
if from_currency is not None and to_currency is not None and \
   [x for x in from_currency.split('/') if x.strip()][-1] == [x for x in to_currency.split('/') if x.strip()][-1]:
    return [1]

def sort_by_date(a, b):
  if a.getStartDateRangeMin() > b.getStartDateRangeMin() :
    return -1
  return 1

object = context

from Products.ERP5Type.Cache import CachingMethod

if to_currency is not None:
  # we have parameters, not a context, so we can use cache
  def calculateExchangeFromParameters(from_currency=None,
                                      to_currency=None,
                                      currency_exchange_type='sale',
                                      start_date=None,**kw):
    if start_date is None:
      from DateTime import DateTime
      start_date = DateTime()
    # Note: SupplyCell is the class of Currency Exchange Line portal type objects
    # But in reality, anything should do.
    temp_object = context.getPortalObject().newContent(temp_object=True,
      portal_type='Supply Cell', id='temp_object')
    temp_kw = {'category_list':['resource/%s' % from_currency,
                                'price_currency/%s' % to_currency],
               'start_date':start_date
              }
    if currency_exchange_type is not None:
      temp_kw['category_list'].append('currency_exchange_type/%s' % currency_exchange_type)
    temp_object.edit(**temp_kw)
    object = temp_object
    mapped_value = context.portal_domains.generateMappedValue(object, 
                                                      has_cell_content=0, 
                                                      validation_state='validated',
                                                      sort_method=sort_by_date)
    base_price = getattr(mapped_value, 'base_price', None)
    discount = getattr(mapped_value, 'discount', None)
    if base_price is None and discount is None:
      mapped_value = context.portal_domains.generateMappedValue(object, 
                                                      has_cell_content=1, 
                                                      validation_state='validated',
                                                      sort_method=sort_by_date)
      base_price = getattr(mapped_value, 'base_price', None)
      discount = getattr(mapped_value, 'discount', None)
    result = [base_price, discount]
    return result
  # The cache duration must not be too long, 300 is the maximum
  calculateExchangeFromParameters = CachingMethod(calculateExchangeFromParameters, 
                      id = 'calculateExchangeFromParameters', cache_factory = 'erp5_ui_short')
  result = calculateExchangeFromParameters(start_date=start_date,
                       currency_exchange_type=currency_exchange_type,
                       from_currency=from_currency,to_currency=to_currency)
else:
  if start_date is None:
    if getattr(context,'isDelivery',None):
      start_date = context.getStartDate()
  mapped_value = context.portal_domains.generateMappedValue(object, 
                                                   has_cell_content=0, 
                                                   validation_state='validated',
                                                   sort_method=sort_by_date)
  base_price = getattr(mapped_value, 'base_price', None)
  discount = getattr(mapped_value, 'discount', None)
  if base_price is None and discount is None:
    mapped_value = context.portal_domains.generateMappedValue(object, 
                                                   has_cell_content=1, 
                                                   validation_state='validated',
                                                   sort_method=sort_by_date)  
    base_price = getattr(mapped_value, 'base_price', None)
    discount = getattr(mapped_value, 'discount', None)
  result = [base_price, discount]
return result
