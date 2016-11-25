from Products.ZSQLCatalog.SQLCatalog import Query, SimpleQuery, AndQuery
portal = context.getPortalObject()

# This scriptable key supports content_translation if the table is present
catalog = portal.portal_catalog.getSQLCatalog()
if 'content_translation' in getattr(catalog, 'sql_search_tables', []):
  if [x for x in getattr(catalog, 'sql_catalog_search_keys', []) if 'Mroonga' in x]:
    return AndQuery(SimpleQuery(**{'content_translation.translated_text': value, 'comparison_operator': 'mroonga_boolean'}),
                    Query(**{'content_translation.property_name': 'title'}))
  else:
    return AndQuery(SimpleQuery(**{'content_translation.translated_text': value, 'comparison_operator': 'match_boolean'}),
                    Query(**{'content_translation.property_name': 'title'}))

# Otherwise it simply use title
return Query(title=value)
