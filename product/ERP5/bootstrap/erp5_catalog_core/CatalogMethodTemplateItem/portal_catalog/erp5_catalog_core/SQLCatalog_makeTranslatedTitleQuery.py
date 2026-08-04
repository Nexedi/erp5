from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery, AndQuery, ComplexQuery
portal = context.getPortalObject()

# To make `translated_title` behave like `title`, we support the LIKE operator.
# If user made a search with %, we treat it as a LIKE.
operator_value_dict, logical_operator, _ = search_key.processSearchValue(
    detect_like=True,
    search_value=search_value,
    default_logical_operator=logical_operator,
    comparison_operator=comparison_operator,
)

if 'like' in operator_value_dict:
  return AndQuery(
    ComplexQuery(
      [
          SimpleQuery(
              **{
                    'content_translation.translated_text': search_term,
                    'comparison_operator': 'like'
              }) for search_term in operator_value_dict['like']
          ],
          logical_operator=logical_operator,
      ),
      Query(**{'content_translation.property_name': 'title'}),
  )

# This scriptable key supports content_translation if the table is present
catalog = portal.portal_catalog.getSQLCatalog()
if 'content_translation' in catalog.getSqlSearchTablesList():
  if [x for x in catalog.getSqlCatalogSearchKeysList() if 'Mroonga' in x]:
    return AndQuery(SimpleQuery(**{'content_translation.translated_text': search_value, 'comparison_operator': 'mroonga_boolean'}),
                    Query(**{'content_translation.property_name': 'title'}))
  else:
    return AndQuery(SimpleQuery(**{'content_translation.translated_text': search_value, 'comparison_operator': 'match_boolean'}),
                    Query(**{'content_translation.property_name': 'title'}))

# Otherwise it simply use title
return Query(title=search_value)
