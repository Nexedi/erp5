"""
  Puts all the arguments from advanced search dialog form together as
  a parse-able search string.
"""
kw['reset'] = 1
kw['language'] = ''
kw['list_style'] = 'search'
kw['search_text'] = context.Base_assembleSearchString()

return context.Base_redirect('WebSite_viewSearchResultList', keep_items=kw)
