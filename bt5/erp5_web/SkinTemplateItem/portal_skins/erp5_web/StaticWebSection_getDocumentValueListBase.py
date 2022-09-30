"""
 This script is part of ERP5 Web

 ERP5 Web is a business template of ERP5 which provides a way
 to create web sites which can display selected
 ERP5 contents through multiple custom web layouts.

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
  portal = container.getPortalObject()
  kw = portal.portal_catalog.getSQLCatalog().getCannonicalArgumentDict(kw)

  # First find the Web Section or Web Site we belong to
  current_section = context.getWebSectionValue()

  if all_versions is None:
    all_versions = context.getLayoutProperty('layout_all_versions', default=False)
  if all_languages is None:
    all_languages = context.getLayoutProperty('layout_all_languages', default=False)

  # Build the list of parameters
  if not language:
    language = portal.Localizer.get_selected_language()

  if validation_state is None:
    # XXX hardcoded validation state list.
    # Use predicate or layout property instead
    validation_state = ('released', 'released_alive', 'published',
                        'published_alive', 'shared', 'shared_alive',
                        'public', 'validated')
  kw['validation_state'] = validation_state

  if 'order_by_list' not in kw:
    # XXX Do not sort by default, as it increases query time
    kw['order_by_list'] = [('int_index', 'DESC'), ('reference', 'DESC')]

  if effective_date is None:
    if now is None:
      now = DateTime()
    effective_date = ComplexQuery(
      SimpleQuery(effective_date=None),
      SimpleQuery(effective_date=now, comparison_operator='<='),
      logical_operator='or',
    )
  kw['effective_date'] = effective_date

  if not all_versions:
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
    #raise ValueError("%s" % current_section.WebSection_zGetDocumentValueList(language=language,
    #                                                        all_languages=all_languages,
    #                                                        src__=1,
    #                                                        kw=kw))
    return current_section.WebSection_zGetDocumentValueList(language=language,
                                                            all_languages=all_languages,
                                                            src__=src__,
                                                            kw=kw)
  else:
    if not all_languages:
      kw['language'] = language
    return current_section.searchResults(src__=src__, **kw)

except Unauthorized:
  return []
