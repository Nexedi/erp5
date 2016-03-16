"""
  Prepare a new query by combining an advanced search string
  with other options. We consider that parameters are received
  in absolute values (ie. not translated) and that they will
  be displayed translated. For this reason, we provide
  a translated portal type.
"""
#return context.Base_redirect('Base_viewSearchResultList',
#                             keep_items=dict(SearchableText=field_your_search_text, reset=1,
#                                              your_search_text=field_your_search_text))


translateString = context.Base_translateString
search_section = context
if new_advanced_search_portal_type:
  if new_advanced_search_portal_type == 'all':
    return search_section.Base_redirect('WebSite_viewAdvancedSearchResultList',
                                 keep_items = dict(reset = 1, 
                                                   advanced_search_text = new_advanced_search_text,
                                                   list_style= 'search',))
  if new_advanced_search_portal_type in context.ERP5Site_getQuickSearchableTypeList():
    #query = search_section.ERP5Site_getQuickSearchableParamDict(new_advanced_search_portal_type)
    portal_type = new_advanced_search_portal_type
    new_query = dict(reset = 1,
                     list_style = 'search',
                     advanced_search_text = new_advanced_search_text,
                     portal_type = portal_type)
    #new_query.update(query)
    return context.Base_redirect('WebSite_viewAdvancedSearchResultList',
                                 keep_items = new_query)
  else:
    translated_type = translateString(new_advanced_search_portal_type)
    return search_section.Base_redirect('WebSite_viewAdvancedSearchResultList',
                                        keep_items = dict(reset = 1,
                                                          advanced_search_text = new_advanced_search_text,
                                                          list_style= 'search',
                                                          translated_portal_type=translated_type))
else:
  return search_section.Base_redirect('WebSite_viewAdvancedSearchResultList',
                                      keep_items = dict(reset = 1,
                                                        list_style= 'search',
                                                        advanced_search_text = new_advanced_search_text))





translateString = context.Base_translateString
search_section = context

if new_advanced_search_portal_type:
  if new_advanced_search_portal_type == 'all':
    return search_section.Base_redirect('WebSite_viewAdvancedSearchResultList',
                                 keep_items = dict(reset = 1, 
                                                   advanced_search_text = new_advanced_search_text,
                                                   list_style= 'search',
                                                   portal_type=list(context.getPortalDocumentTypeList())))
  if new_advanced_search_portal_type in context.ERP5Site_getQuickSearchableTypeList():
    query = search_section.ERP5Site_getQuickSearchableParamDict(new_advanced_search_portal_type)
    new_query = dict(reset = 1,
                     list_style= 'search',
                     advanced_search_text = new_advanced_search_text)
    new_query.update(query)
    return context.Base_redirect('WebSite_viewAdvancedSearchResultList',
                                 keep_items = new_query)
  else:
    translated_type = translateString(new_advanced_search_portal_type)
    return search_section.Base_redirect('WebSite_viewAdvancedSearchResultList',
                                        keep_items = dict(reset = 1,
                                                          advanced_search_text = new_advanced_search_text,
                                                          list_style= 'search',
                                                          translated_portal_type=translated_type))
else:
  return search_section.Base_redirect('WebSite_viewAdvancedSearchResultList',
                                      keep_items = dict(reset = 1,
                                                        list_style= 'search',
                                                        advanced_search_text = new_advanced_search_text))
