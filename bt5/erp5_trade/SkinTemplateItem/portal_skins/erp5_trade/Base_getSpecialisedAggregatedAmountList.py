specialise = context.getSpecialiseValue(portal_type=('Purchase Trade Condition',
                                                     'Sale Trade Condition',
                                                     'Internal Trade Condition',))

if specialise is not None:
  rounding = kwargs.get('rounding', False)
  return specialise.getAggregatedAmountList(context, rounding=rounding)

return []
