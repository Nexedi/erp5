if context.getParentValue().getParentValue().getPortalType() not in context.getPortalResourceTypeList() \
     and getattr(context, 'getValidationState', lambda: "")() in ('invalidated', 'deleted', 'draft'):
  # If this supply cell is contained in a supply or trade condition that is not validated, it does not apply.
  return None

base_category_tuple = ('resource', 'price_currency')

if context.getSourceSection():
  base_category_tuple += ('source_section',)
if context.getDestinationSection():
  base_category_tuple += ('destination_section',)
if context.getSource():
  base_category_tuple += ('source',)
if context.getDestination():
  base_category_tuple += ('destination',)

if context.hasProductLine():
  category_list = context.getCategoryList() + [
    pl.getRelativeUrl() for pl in context.getProductLineValue().getCategoryChildValueList()]
  context = context.asContext(categories=category_list)
  base_category_tuple += ('product_line', )

if context.getParentValue().getParentValue().getPortalType() in (
    ## XXX There is no portal type group for trade conditions.
    'Sale Trade Condition',
    'Purchase Trade Condition',
    'Internal Trade Condition'):
  # Supply Lines from trade conditions are set as specialise to this trade condition,
  # so that we can apply a predicate on movements later. Supply Lines from trade condition
  # only apply on movements using these trade conditions.
  category_list = context.getCategoryList() + ['specialise/%s' % context.getParentValue().getParentValue().getRelativeUrl()]
  context = context.asContext(categories=category_list)
  base_category_tuple += ('specialise', )


#backwards compatibility
mapped_value_property_list = context.getMappedValuePropertyList()
for mapped_property in ('priced_quantity', 'quantity_unit'):
  if not mapped_property in mapped_value_property_list:
    mapped_value_property_list.append(mapped_property)
    context.setMappedValuePropertyList(mapped_value_property_list)

# XXX: An hack that the context cell may not have the start_date_range_min/max properties.
# But they don't acquire it parent the properties.
# Correctly, the cell must acquire the properties.
if (context.getStartDateRangeMin() == None and
    context.getStartDateRangeMax() == None):
  supply_line = context.getParentValue()
  context = context.asContext(start_date_range_min=supply_line.getStartDateRangeMin(),
                              start_date_range_max=supply_line.getStartDateRangeMax())

return context.generatePredicate(membership_criterion_base_category_list = base_category_tuple,
                                                 criterion_property_list = ('start_date',))
