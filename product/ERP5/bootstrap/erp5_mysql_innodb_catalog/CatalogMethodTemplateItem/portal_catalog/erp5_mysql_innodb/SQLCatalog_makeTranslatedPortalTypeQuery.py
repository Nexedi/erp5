from collections import defaultdict
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
operator_value_dict, logical_operator, _ = search_key.processSearchValue(
  search_value=search_value,
  default_logical_operator=logical_operator,
  comparison_operator=comparison_operator,
)
original_message_dict = defaultdict(set)
for row in context.SQLCatalog_zSearchTranslation(
  language=context.getPortalObject().Localizer.get_selected_language(),
  message_context='portal_type',
  translated_message=sum(operator_value_dict.itervalues(), []),
):
  original_message_dict[row.translated_message].add(row.portal_type)
query_list = []
append = query_list.append
for comparison_operator, translated_message_list in operator_value_dict.iteritems():
  for translated_message in translated_message_list:
    portal_type_set = original_message_dict.get(translated_message)
    if portal_type_set:
      append(
        SimpleQuery(
          group=group,
          comparison_operator=comparison_operator,
          portal_type=list(portal_type_set),
        ),
      )
if len(query_list) == 1:
  return query_list[0]
if query_list:
  return ComplexQuery(query_list, logical_operator=logical_operator)
# No translation, match nothing.
return SimpleQuery(uid=-1)
