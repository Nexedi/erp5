kw = {'reset':1,
      'search_text':field_your_search_text,
      'your_search_text':field_your_search_text,
      'all_languages':all_languages,
      'ignore_hide_rows': 1,
      'list_style':list_style}

if field_your_search_portal_type:
  if field_your_search_portal_type == 'all':
    kw.update({'portal_type':list(context.getPortalDocumentTypeList())})
  else:
    kw.update({'portal_type':field_your_search_portal_type})

web_section = context.getWebSectionValue()
if web_section is not None and \
    not bool(context.REQUEST.get('ignore_layout', False)):
  search_context = web_section
  if list_style is None:
    kw.update({'list_style':'search'})
else:
  search_context = context.getPortalObject()

if field_your_search_text in ('', None):
  # no search criteria specified, refuse to conduct any search and
  # show a message to user
  kw['portal_status_message'] = 'Please specify search criteria.'
  return search_context.Base_redirect('view', keep_items=kw)

return search_context.Base_redirect(field_your_search_form_id, keep_items=kw)
