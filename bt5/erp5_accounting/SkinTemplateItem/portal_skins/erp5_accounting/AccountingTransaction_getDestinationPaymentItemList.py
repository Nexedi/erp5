section = context.getDestinationSection()
if section:
  return context.AccountModule_getBankAccountItemList(
        organisation=section,
        base_category='destination_payment')
return [('', '')]
