web_site = context.getWebSiteValue()
search_area_web_section_id = web_site.getLayoutProperty('search_area_web_section_id',
                                                        default=None)
if search_area_web_section_id:
  search_section = web_site[search_area_web_section_id]
else:
  search_section = web_site

search_section.Base_redirect(form_id='ERP5Site_viewSearchResult',
                keep_items=dict(reset=1, portal_type=list(context.getPortalDocumentTypeList()),
                                search_section_path=context.getRelativeUrl()))
