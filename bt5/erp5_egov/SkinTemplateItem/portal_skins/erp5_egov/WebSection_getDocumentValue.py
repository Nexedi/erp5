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
if portal is None: portal = context.getPortalObject()
portal_catalog = portal.portal_catalog
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

# Search the catalog for all documents matching the reference
# this will only return documents which are accessible by the user
web_page_list = portal_catalog(reference=name,
                               portal_type=valid_portal_type_list,
                               validation_state=validation_state,
                               language=language,
                               sort_on=[('version', 'descending')],
                               group_by=('reference',),
                               limit=1,
                               **kw)

if len(web_page_list) == 0 and language != 'en':
  # Search again with English as a fallback.
  web_page_list = portal_catalog(reference=name,
                                 portal_type=valid_portal_type_list,
                                 validation_state=validation_state,
                                 language='en',
                                 sort_on=[('version', 'descending')],
                                 group_by=('reference',),
                                 limit=1,
                                 **kw)

if len(web_page_list) == 0:
  # Search again without the language
  web_page_list = portal_catalog(reference=name,
                                 portal_type=valid_portal_type_list,
                                 validation_state=validation_state,
                                 sort_on=[('version', 'descending')],
                                 group_by=('reference',),
                                 limit=1,
                                 **kw)

if len(web_page_list) == 0:
  name_without_web_site = '-'.join(name.split('-')[:-1])
  if name_without_web_site:
    # Search again without the website
    web_page_list = portal_catalog(reference=name_without_web_site,
                                   portal_type=valid_portal_type_list,
                                   validation_state=validation_state,
                                   sort_on=[('version', 'descending')],
                                   group_by=('reference',),
                                   limit=1,
                                   **kw)

if len(web_page_list) == 0:
  name_without_portal_type = '-'.join(name.split('-')[1:])
  if name_without_portal_type:
    # Search again without the portal_type
    web_page_list = portal_catalog(reference=name_without_portal_type,
                                   portal_type=valid_portal_type_list,
                                   validation_state=validation_state,
                                   sort_on=[('version', 'descending')],
                                   group_by=('reference',),
                                   limit=1,
                                   **kw)

if len(web_page_list) == 0:
  name_without_portal_type_and_web_site = '-'.join(name.split('-')[1:-1])
  if name_without_portal_type_and_web_site:
    # Search again without the portal_type and web_site
    web_page_list = portal_catalog(reference=name_without_portal_type_and_web_site,
                                   portal_type=valid_portal_type_list,
                                   validation_state=validation_state,
                                   sort_on=[('version', 'descending')],
                                   group_by=('reference',),
                                   limit=1,
                                   **kw)

if len(web_page_list) == 0:
  name_without_web_site_and_view = '-'.join(name.split('-')[:-2])
  if name_without_web_site_and_view:
    # Search again without the portal_type and view
    web_page_list = portal_catalog(reference=name_without_web_site_and_view,
                                   portal_type=valid_portal_type_list,
                                   validation_state=validation_state,
                                   sort_on=[('version', 'descending')],
                                   group_by=('reference',),
                                   limit=1,
                                   **kw)

if len(web_page_list) == 0:
  state = ''
  name_list = name.split('-')
  if len(name_list)>1:
    state = name_list[1]
  if state:
    state = '%' + state + '%'
    # Search only with state
    web_page_list = portal_catalog(reference=state,
                                   portal_type=valid_portal_type_list,
                                   validation_state=validation_state,
                                   sort_on=[('version', 'descending')],
                                   group_by=('reference',),
                                   limit=1,
                                   **kw)

if len(web_page_list) == 0:
  # Default returns None
  web_page = None
else:
  # Try to get the first page on the list
  web_page = web_page_list[0]
  web_page = web_page.getObject()

# return the web page
return web_page
