dimension_list = ['contribution_share', 'product', 'region', 'product_line',
                  'destination_region', 'has_vat_number', 'movement']

for pred in context.objectValues(portal_type='Predicate'):
  if pred.getStringIndex() not in dimension_list:
    dimension_list.append(pred.getStringIndex())

if list_dimensions:
  return dimension_list

dimension_result_list = []

for dimension in dimension_list:
  if dimension is not None:
    predicate_list = [x for x in context.contentValues(portal_type='Predicate')
                       if x.getStringIndex() == dimension ]
    predicate_list.sort(key=lambda x: x.getProperty('int_index', 1))
    if len(predicate_list):
      dimension_result_list.append(predicate_list)

dimension_ids_list = []

if matrixbox:
  for dimension_result in dimension_result_list:
    dimension_ids_list.append(
              [(x.getObject().getId(),
                x.getObject().getTitle()) for x in dimension_result])
else :
  for dimension_result in dimension_result_list :
    dimension_ids_list.append(
          [x.getObject().getId() for x in dimension_result])

return dimension_ids_list
# vim: syntax=python
