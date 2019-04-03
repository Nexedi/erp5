"""
 This script returns a list of document values (ie. objects or brains)
 which are considered as part of this section. It can be
 a list of web pages (usual case), a list of products
 (online catalog), a list of tenders (e-government), etc.

 The default implementation provided here consists in
 listing documents which meet the predicate defined
 by the section (ex. which are part of a given publication_section)
 and which are in "published" state and of a "Web Page" portal_type.

 It should be noted that document selection should be implemented
 as much as possible using the Domain API.

 This script can be changed to meet other requirements. For example
 one may want to display a list of products in a section. In this case,
 this script must return a list of documents of type "Product"
 with a "validated" state and in the appropriate product family.

 This script is intended to be overriden by creating a new script
 within the Web Section or Web Site instance. It can be also
 customised per portal type within portal_skins. Customisation
 thourgh local scripts is recommended to host multiple sites
 on the same ERP5Site instance.

 The API uses **kw so that it is possible to extend the behaviour of
 the default script with advanced features (ex. group by reference,
 by version, only select a specific publication state, etc.).

 Here are some suggestions which can either be implemented using
 SQL (group_by, order_by) or using additional python scripting
 if this is compatible with data size.

 SUGGESTIONS:

 - Prevent showing duplicate references

 - Add documents associated to this section through 'aggregate'.

 - Display only the latest version and the appropriate language.
"""
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
from zExceptions import Unauthorized

try:
  portal = context.getPortalObject()
  kw = context.getCannonicalArgumentDict(kw)
  if search_context is None:
    search_context = portal

  # Build the list of parameters
  if not language:
    language = portal.Localizer.get_selected_language()

  if not kw.get('portal_type'):
    kw['portal_type'] = portal.getPortalDocumentTypeList()

  if not kw.get('validation_state'):
    # XXX hardcoded validation state list.
    # Use predicate or layout property instead
    kw['validation_state'] = ('released', 'released_alive', 'published',
                              'published_alive', 'shared', 'shared_alive',
                              'public', 'validated')

  if 'order_by_list' not in kw:
    # XXX Do not sort by default, as it increases query time
    kw['order_by_list'] = [('int_index', 'DESC'), ('reference', 'DESC')]

  if 'effective_date' not in kw:
    if now is None:
      now = DateTime()
    kw['effective_date'] = ComplexQuery(
      SimpleQuery(effective_date=None),
      SimpleQuery(effective_date=now, comparison_operator='<='),
      logical_operator='or',
    )

  if all_languages:
    strict_language = False
  if all_versions:
    if all_languages or not strict_language:
      result = search_context.searchResults(src__=src__, **kw)
    else:
      result = search_context.searchResults(src__=src__, language=language, **kw)
  else:
    group_by_list = set(kw.get('group_by_list', []))
    if all_languages:
      kw['group_by_list'] = list(group_by_list.union(('reference', 'language')))
    else:
      kw['group_by_list'] = list(group_by_list.union(('reference',)))

    # Extend select_dict by order_by_list and group_by_list columns.
    extra_column_set = {i[0] for i in kw.get('order_by_list', ())}.union(
      kw.get('group_by_list', ()))
    kw.setdefault('select_dict', {}).update(
      (x.replace('.', '_') + '__ext__', x)
      for x in extra_column_set if not x.endswith('__score__'))
    result = context.SQLCatalog_zGetDocumentValueList(search_context=search_context,
                                                    language=language,
                                                    strict_language=strict_language,
                                                    all_languages=all_languages,
                                                    src__=src__,
                                                    kw=kw)

  test_func = getattr(search_context, 'test', None)
  if test_func is None:
    return result
  else:
    result = [x.getObject() for x in result]
    return [x for x in result if test_func(x)]
except Unauthorized:
  return []
