"""
  This script receives a request from advanced search form and
  puts together a search string in a search syntax, depending on
  parameters received.
  It is the reverse of Base_parseSearchString script.
"""
MARKER = ['', None]
BOOLEAN_MARKER = MARKER + [0]
request = context.REQUEST

# one can specify a direct search string,
# in this case simply returning it is expected
searchabletext = kw.get('searchabletext',
                        request.get('searchabletext', None))
if searchabletext not in MARKER:
  return searchabletext

# words to search in 'any of the words' form - left intact
searchabletext_any = kw.get('searchabletext_any',
                            request.get('searchabletext_any', ''))
search_string = searchabletext_any

# exact phrase to search for double-quoted
searchabletext_phrase = kw.get('searchabletext_phrase',
                               request.get('searchabletext_phrase', None))
if searchabletext_phrase not in MARKER:
  search_string += ' \"%s\"' %searchabletext_phrase

# search "with all of the words" - each word prefixed by "+"
searchabletext_all = kw.get('searchabletext_all',
                            request.get('searchabletext_all', None))
if searchabletext_all not in MARKER:
  search_string += '  %s' %' '.join('+%s' %word for word in searchabletext_all.split(' '))

# search without these words - every word prefixed by "-"
searchabletext_without = kw.get('searchabletext_without',
                                request.get('searchabletext_without', None))
if searchabletext_without not in MARKER:
  search_string += ' %s'  %' '.join('-%s' %word for word in searchabletext_without.split(' '))

# search limited to a certain date range - add "created:xxx"
created_within = kw.get('created_within', request.get('created_within', None))
if created_within not in MARKER:
  search_string += ' created:%s' %created_within

# only given portal_types - add "type:Type" or type:(Type1,Type2...)
portal_type_list = kw.get('search_portal_type',
                          request.get('search_portal_type'))
if portal_type_list == 'all':
  portal_type_list=None
if isinstance(portal_type_list, str):
  portal_type_list=[portal_type_list]
if portal_type_list:
  portal_type_string_list = []
  for portal_type in portal_type_list:
    if ' ' in portal_type:
      portal_type = '"%s"' %portal_type
    portal_type_string_list.append('portal_type:%s' %portal_type)
  portal_type_string = '(%s)' %' OR '.join(portal_type_string_list)
  if search_string not in MARKER:
    search_string += ' %s %s' %(logical_operator, portal_type_string)
  else:
    search_string += portal_type_string

# search by reference
reference = kw.get('reference', request.get('reference', None))
if reference not in MARKER:
  search_string += ' reference:%s' % reference

# search by version
version = kw.get('version', request.get('version'))
if version not in MARKER:
  search_string += ' version:%s' %version

# search by language
language=kw.get('language', request.get('language', None))
if language not in MARKER and language != '0':
  search_string += ' language:%s' % language

# category search
for category in ('group', 'site', 'function', 'publication_section', 'classification'):
  category_field_id = 'subfield_field_your_category_list_%s' %category
  category_value = kw.get(category_field_id, request.get(category_field_id, None))
  if category_value not in MARKER:
    search_string += ' %s:%s' % (category, category_value)

# contributor title search
for category in ('contributor_title',):
  category_value = kw.get(category, request.get(category, None))
  if category_value not in MARKER:
    search_string += ' %s:%s' %(category, category_value)

# only my docs
mine = kw.get('mine', request.get('mine', None))
if mine not in BOOLEAN_MARKER:
  search_string += ' mine:yes'

# only newest versions
newest =  kw.get('newest', request.get('newest', None))
if newest not in BOOLEAN_MARKER:
  search_string += ' newest:yes'

# search mode
search_mode = kw.get('search_mode', request.get('search_mode', None))
search_mode_map={'in_boolean_mode':'boolean',
                 'with_query_expansion':'expanded'}
if search_mode not in MARKER and search_mode in search_mode_map:
  search_string += ' mode:%s' % search_mode_map[search_mode]

return search_string
