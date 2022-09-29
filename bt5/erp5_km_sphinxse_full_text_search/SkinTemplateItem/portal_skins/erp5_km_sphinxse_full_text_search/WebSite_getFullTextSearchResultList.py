"""
  Return the result list of all documents found by specified agruments.
  Include an optimisation for 'search' mode which returns all documents info like
  (reference, state, web sections ...) without getting a ZODB object (i.e. get everything from
  MySQL - "No ZODB" approach).
"""
from Products.ERP5Type.Document import newTempBase

request = context.REQUEST
portal = context.getPortalObject()
web_site = context.getWebSiteValue()

selection = kw.get('selection', {})
list_style = kw.get('list_style', \
                    selection.get('list_style', request.get('list_style', 'table')))

search_text = kw['search_text']
parsed_dict = context.Base_parseSearchString(search_text)
search_string = parsed_dict['searchabletext']

# extend query
if all_versions is None:
    all_versions = context.getLayoutProperty('layout_all_versions', default=False)
if all_languages is None:
  all_languages = context.getLayoutProperty('layout_all_languages', default=False)

# Build the list of parameters
if not language:
  language = portal.Localizer.get_selected_language()

if not all_languages:
  kw['language'] = language

if validation_state is None:
  # XXX hardcoded validation state list.
  # Use predicate or layout property instead
  validation_state = ('released', 'released_alive', 'published',
                      'published_alive', 'shared', 'shared_alive',
                      'public', 'validated')
kw['validation_state'] = validation_state

if 'sort_on' not in kw:
  # XXX Do not sort by default, as it increases query time
  kw['sort_on'] = [('int_index', 'DESC'), ('reference', 'DESC')]

if list_style != 'search':
  return context.portal_catalog(**kw)
else:
  # search mode requires optimization, use catalog to get more data from it
  result_list = []
  result_set_dict_list = []
  repeating_uid_category_map = {}
  portal_types = portal.portal_types

  # get Web Site predicate info
  category_section_map, base_category_uid_list = web_site.WebSite_getWebSectionPredicateMapAndUidList()

  # XXX: using catalog API instead of script should be researched as a more maintainable alternative
  found_result_list = web_site.WebSite_zGetAdvancedSearchResultList(
                          base_category_uid_list = base_category_uid_list,
                          search_string = search_string,
                          is_full_text_search_on = 1,
                          use_text_excerpts = 1,
                          kw = kw)
  for line in found_result_list:
    uid = line['uid']
    if uid not in repeating_uid_category_map.keys():
      # first time
      repeating_uid_category_map[uid] = []
    category_relative_url = line['category_relative_url']
    if category_relative_url is not None:
      # exactly matches, document("group/nexedi") belongs to section("group/nexedi")
      sections = category_section_map.get(category_relative_url, [])
      if not len(sections):
        # try to find by similarity if no exact match so if document belongs to 'group/nexedi/hq'
        # and we have a section 'group/nexedi' it will belong to this section
        for key,value in category_section_map.items():
          if category_relative_url.startswith(key):
            sections.extend(value)
      repeating_uid_category_map[uid].extend(sections)
    # turn into a relative URL
    path = line['path'].replace('/%s/' %portal.getId(), '')
    result_set_dict_list.append({'uid': uid,
                                'object_portal_type': line['portal_type'],
                                'object_icon': portal_types[line['portal_type']].getIcon(),
                                'path': path,
                                'title': line['title'],
                                'text': getattr(line, 'text', ''),
                                'modification_date': line['modification_date'],
                                'reference': line['reference'],
                                'category_relative_url': line['category_relative_url'],
                                'owner': line['owner'],
                                'version': line['version'],
                                'language': line['language'],
                                'web_site': web_site.getRelativeUrl()})

  # one document can belong to n categories, we need show only one doc
  # and all sections it belongs to
  found_uids = []
  for line in result_set_dict_list:
    uid = line['uid']
    if uid not in found_uids:
      found_uids.append(uid)
      # show only unique sections
      unique_sections = {}
      sections = repeating_uid_category_map[uid]
      for section in sections:
        unique_sections[section['uid']] = section['relative_url']
      line['section_list'] = unique_sections.values()
      result_list.append(line)
  return [newTempBase(portal, x['title'], **x) for x in result_list]
