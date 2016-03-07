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
portal_catalog = container.portal_catalog

# First find the Web Section or Web Site we belong to
current_section = context.getWebSectionValue()

# Build the list of parameters
if not kw.has_key('validation_state'):
  kw['validation_state'] = ['draft', 'submitted', 'shared',
                            'released', 'published', 'restricted']
if not kw.has_key('sort_on'):
  kw['sort_on'] = [('int_index', 'descending')]
if not kw.has_key('group_by'):
  kw['group_by'] = ('reference',)

# Remove sort on validation and groupd_by
kw.pop('validation_state')
kw.pop('group_by')

# Return the list of matching documents for the given states
return current_section.searchResults(**kw)
