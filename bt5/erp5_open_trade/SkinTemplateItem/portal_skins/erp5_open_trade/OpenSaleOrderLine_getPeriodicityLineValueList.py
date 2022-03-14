resource_uid = context.getResourceUid()

# XXX Currently sale trade condition is hardcoded by specialise category and
# cannot switch it by a period of time.

def iterate(trade_condition, trade_condition_list):
  if trade_condition is None:
    return
  elif trade_condition in trade_condition_list:
    return
  else:
    trade_condition_list.append(trade_condition)
    for next_trade_condition in trade_condition.getSpecialiseValueList():
      iterate(next_trade_condition, trade_condition_list)

sale_trade_condition_list = []
iterate(context.getSpecialiseValue(), sale_trade_condition_list)

for sale_trade_condition in sale_trade_condition_list:
  for periodicity_line in sale_trade_condition.objectValues(portal_type='Periodicity Line'):
    if periodicity_line.getResourceUid()==resource_uid:
      return [periodicity_line]

raise RuntimeError('Cannot find an appropriate Periodicity Line for the movement: %s' % context.getRelativeUrl())
