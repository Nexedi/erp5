context = state_change['object']

base_id = 'path'
kwd = {'base_id': base_id}


context.updateCellRange(script_id='CurrencyExchangeLine_asCellRange', base_id=base_id)
cell_range_key_list = context.getCellRangeKeyList(base_id = base_id)
resource_list = ['resource/%s' % context.getParentValue().getRelativeUrl()]
price_currency_list = [context.getPriceCurrency(base=True)]
membership_list = resource_list + price_currency_list
context.setMembershipCriterionBaseCategoryList([x.split('/')[0] for x in membership_list])
context.setMembershipCriterionCategoryList(membership_list)
context.setResourceValue(context.getParentValue())
context.setMappedValuePropertyList(('base_price','discount'))
if cell_range_key_list != [[None, None]] :
  for k in cell_range_key_list:
    category_list = [k_item for k_item in k if k]
    c = context.newCell(*k, **kwd)
    c.edit(mapped_value_property_list = ('base_price','discount'),
           force_update = 1,
           membership_criterion_base_category_list = [x.split('/')[0] for x in category_list],
           membership_criterion_category_list = category_list,
           category_list = category_list,
    )
    c.setCriterion('stop_date', min=context.getStartDate(), max=context.getStopDate())
    if c.getBasePrice() is None and context.getBasePrice() is not None:
      c.setBasePrice(context.getBasePrice())
    # set an int index for display
    currency_exchange_type_value_list = c.getValueList('currency_exchange_type')
    if currency_exchange_type_value_list:
      c.setIntIndex(currency_exchange_type_value_list[0].getIntIndex())
