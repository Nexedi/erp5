section = context.getSourceSection()
if section:
  return context.AccountModule_getBankAccountItemList(
        organisation=section,
        base_category='source_payment')
return [('', '')]
