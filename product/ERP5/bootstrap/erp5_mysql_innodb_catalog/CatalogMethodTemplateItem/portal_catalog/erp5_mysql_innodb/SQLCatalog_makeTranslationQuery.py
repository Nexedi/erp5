from collections import defaultdict
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
operator_value_dict, logical_operator, _ = search_key.processSearchValue(
  detect_like=True,
  search_value=search_value,
  default_logical_operator=logical_operator,
  comparison_operator=comparison_operator,
)
original_message_dict = defaultdict(set)
for row in context.SQLCatalog_zSearchTranslation(
  language=context.getPortalObject().Localizer.get_selected_language(),
  message_context=message_context,
  logical_operator=logical_operator,
  translated_message_dict=operator_value_dict,
):
  original_message_dict[row.original_message].add(row.portal_type)
query_list = [
  ComplexQuery(
    SimpleQuery(
      group=group,
      comparison_operator='=',
      **{column_id: original_message}
    ),
    SimpleQuery(
      group=group,
      portal_type=list(portal_type_set),
    ),
    logical_operator='and',
  )
  for original_message, portal_type_set in original_message_dict.iteritems()
]
if len(query_list) == 1:
  return query_list[0]
if query_list:
  return ComplexQuery(query_list, logical_operator='or')
# No translation, match nothing.
return SimpleQuery(uid=-1)
