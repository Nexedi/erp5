"""
Script to convert the prices used in the transaction to the
currency of the source section
"""
portal = context.getPortalObject()
precision = context.getSourceSectionValue().getPriceCurrencyValue().getQuantityPrecision()
line_list = context.contentValues(
      portal_type=portal.getPortalAccountingMovementTypeList())


for line in line_list:
  section = line.getSourceSectionValue()
  if section != context.getSourceSectionValue():
    continue
  currency = line.getResourceValue()
  if not exchange_rate:
    exchange_rate = currency.getPrice(context=line.asContext(
                          categories=[line.getResource(base=True),
                                      section.getPriceCurrency(base=True)],
                      start_date=line.getStartDate()))
  # redirect to previous page without doing the conversion
  if exchange_rate is None:
    return context.Base_redirect(
        form_id,
        keep_items=dict(
            portal_status_message=context.Base_translateString('No exchange ratio found.'),
            portal_status_level='error',
        ))

  # update the corresponding price and round it according to the precision of
  # the converted currency
  line.setSourceTotalAssetPrice(
       round(exchange_rate * (-line.getQuantity()), precision))

msg = context.Base_translateString('Price converted.')

return context.Base_redirect(form_id,
                             keep_items=dict(portal_status_message=msg))
