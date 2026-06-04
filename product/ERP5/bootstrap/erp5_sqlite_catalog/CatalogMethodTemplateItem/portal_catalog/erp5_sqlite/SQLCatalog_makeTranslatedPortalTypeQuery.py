from Products.ZSQLCatalog.SQLCatalog import SimpleQuery
operator_value_dict, logical_operator, _ = search_key.processSearchValue(
  detect_like=True,
  search_value=search_value,
  default_logical_operator=logical_operator,
  comparison_operator=comparison_operator,
)
row_list = context.SQLCatalog_zSearchTranslation(
  language=context.getPortalObject().Localizer.get_selected_language(),
  message_context='portal_type',
  logical_operator=logical_operator,
  translated_message_dict=operator_value_dict,
)
if row_list:
  return SimpleQuery(
    group=group,
    portal_type=list({x.portal_type for x in row_list}),
  )
# No translation, match nothing.
return SimpleQuery(uid=-1)
