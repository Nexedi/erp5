"""
 This script is part of ERP5 Web

 ERP5 Web is a business template of ERP5 which provides a way
 to create web sites which can display selected
 ERP5 contents through multiple custom web layouts.

 The default implementation searches for
 documents which are in the user language if any
 and which reference is equal to the name parameter.

 Other implementations are possible: ex. display the last
 version in the closest language rather than
 the latest version in the user language.

 NOTE:
 - the portal parameter was introduced to
   fix acquisition issues within the _aq_dynamic
   lookup from WebSection class.
"""
from Products.ZSQLCatalog.SQLCatalog import SimpleQuery, ComplexQuery
if portal is None: portal = context.getPortalObject()

# The list of portal types here should be large enough to include
# all portal_types defined in the various sections so that
# href tags which point to a document by reference can still work.
valid_portal_type_list = portal.getPortalDocumentTypeList()

# Find the applicable language
if language is None:
  language = portal.Localizer.get_selected_language()

if validation_state is None:
  validation_state = ('released', 'released_alive', 'published', 'published_alive',
                      'shared', 'shared_alive', 'public', 'validated')

if effective_date is None:
  if now is None:
    now = DateTime()
  effective_date = ComplexQuery(
    SimpleQuery(effective_date=None),
    SimpleQuery(effective_date=now, comparison_operator='<='),
    logical_operator='or',
  )

# Note: In sorts, NULL is considered lesser than non-NULL. So in descending
# sort, NULLs will be listed after non-NULLs, which is perfect for
# effective_date, which defines the date at which content becomes effective.
# None (NULL) effective date hence means "effective since infinite in te past".
base_sort = (('effective_date', 'descending'), )

# Portal Type and validation state should be handled by predicate
# By default
document_list = context.searchResults(
  reference=name,
  effective_date=effective_date,
  portal_type=valid_portal_type_list,
  language=(language, ''),
  sort_on=(('language', 'descending'), ) + base_sort,
  limit=1,
  **kw)

if len(document_list) == 0:
  # Default returns None
  document = None
else:
  # Try to get the first page on the list
  document = document_list[0]
  document = document.getObject()

# return the web page
return document
