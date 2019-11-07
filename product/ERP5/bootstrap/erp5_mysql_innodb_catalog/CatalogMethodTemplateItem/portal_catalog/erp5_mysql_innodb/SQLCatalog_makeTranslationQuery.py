from collections import defaultdict
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
operator_value_dict, logical_operator, _ = search_key.processSearchValue(
  search_value=search_value,
  default_logical_operator=logical_operator,
  comparison_operator=comparison_operator,
)
original_message_dict = defaultdict(lambda: defaultdict(set))
for row in context.SQLCatalog_zSearchTranslation(
  language=context.getPortalObject().Localizer.get_selected_language(),
  message_context=message_context,
  translated_message=sum(operator_value_dict.itervalues(), []),
):
  original_message_dict[row.translated_message][row.original_message].add(row.portal_type)
query_list = []
append = query_list.append
for comparison_operator, translated_message_list in operator_value_dict.iteritems():
  for translated_message in translated_message_list:
    # XXX: what should be done for translated_message which were not found ?
    # Strictly, a "=" comparison should fail, which only matters with an "and" logical operator or when lone condition.
    # Conversely, a "!=" comparaison should succeed, which only matters with an "or" logical operator or when lone condition.
    for original_message, portal_type_set in original_message_dict[translated_message].iteritems():
      append(
        ComplexQuery(
          SimpleQuery(
            group=group,
            comparison_operator=comparison_operator,
            **{column_id: original_message}
          ),
          SimpleQuery(
            group=group,
            portal_type=list(portal_type_set),
          ),
          logical_operator='and',
        ),
      )
if len(query_list) == 1:
  return query_list[0]
if query_list:
  return ComplexQuery(query_list, logical_operator=logical_operator)
# No translation, match nothing.
return SimpleQuery(uid=-1)
