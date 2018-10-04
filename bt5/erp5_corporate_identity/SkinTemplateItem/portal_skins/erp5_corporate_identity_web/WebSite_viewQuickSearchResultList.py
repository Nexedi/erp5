'''=============================================================================
                                Website Search
============================================================================='''
if field_your_search_form_id is None:
  field_your_search_form_id = 'WebSite_viewSearchResultList'
  if context is context.getWebSiteValue():
    field_your_search_form_id = context.getWebSiteValue()["browse"].absolute_url()

return context.ERP5Site_viewQuickSearchResultList(
  field_your_search_text=field_your_search_text,
  field_your_search_portal_type=field_your_search_portal_type,
  all_languages=all_languages,
  list_style=list_style,
  field_your_search_form_id=field_your_search_form_id,
)
