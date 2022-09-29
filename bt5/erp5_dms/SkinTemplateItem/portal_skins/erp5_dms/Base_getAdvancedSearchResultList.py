"""
  The main search script. Receives one big string - a searchabletext, in
  the search syntax, parses the string using external method Base_parseSearchString,
  then does the following:
    - processes arguments for searching by any category
    - selects search mode
    - adds creation and modification date clauses
    - searches
    - if requested, filters result so that only the user's docs are returned
    - if requested, filters result to return only the newest versions
"""
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
portal = context.getPortalObject()

query_kw = {}
date_format = '%Y-%m-%d'

if searchabletext is None:
  # searchabletext can be supplied in request (fallback)
  searchabletext = context.REQUEST.get('searchabletext')

if searchabletext is None:
  # or in selection
  selection_id = 'search_advanced_dialog_selection'
  selection_object = portal.portal_selections.getSelectionParamsFor(selection_id)
  if selection_object:
    searchabletext = selection_object.get('searchabletext')

if searchabletext is None:
  raise ValueError("No search string specified.")

parsed_search_string = context.Base_parseSearchString(searchabletext)

# if no portal type specified, take all
portal_type = parsed_search_string.get('portal_type', None)
if portal_type is None or not len(portal_type):
  query_kw['portal_type'] = portal.getPortalDocumentTypeList()
else:
  # safe to add passed portal_type,
  # as multiple values exists split them by ','
  query_kw['portal_type'] = portal_type.split(',')

# ZSQLCatalog wants table.key to avoid ambiguity
parsed_searchabletext = parsed_search_string.get('searchabletext', None)
if parsed_searchabletext is not None:
  query_kw['full_text.SearchableText'] =  parsed_searchabletext

for key in ('reference', 'version', 'language',):
  value = parsed_search_string.get(key, None)
  if value is not None:
    query_kw[key] = value

query_list = []
creation_from = parsed_search_string.get('creation_from', None)
creation_to = parsed_search_string.get('creation_to', None)
modification_from = parsed_search_string.get('modification_from', None)
modification_to = parsed_search_string.get('modification_to', None)
if creation_from:
  query_list.append(SimpleQuery(creation_date=creation_from.strftime('>=' + date_format)))
if creation_to:
  query_list.append(SimpleQuery(creation_date=creation_to.strftime('<=' + date_format)))
if modification_from:
  query_list.append(SimpleQuery(modification_date=modification_from.strftime('>=' + date_format)))
if modification_to:
  query_list.append(SimpleQuery(modification_date=modification_to.strftime('<=' + date_format)))
if query_list:
  query_kw['query'] = ComplexQuery(query_list, logical_operator='and')

if parsed_search_string.get('mine', None) is not None:
  # user wants only his documents
  query_kw['owner'] = portal.portal_membership.getAuthenticatedMember().getId()

# add contributor title
contributor_title = parsed_search_string.get('contributor_title', None)
if contributor_title is not None:
  query_kw['contributor_title'] = contributor_title

if parsed_search_string.get('newest', None) is not None:
  #...and now we check for only the newest versions
  # but we need to preserve order
  query_kw['group_by'] = ('reference',)
  result = [doc.getLatestVersionValue() \
              for doc in context.portal_catalog(**query_kw)]
else:
  result = portal.portal_catalog(**query_kw)

return result
