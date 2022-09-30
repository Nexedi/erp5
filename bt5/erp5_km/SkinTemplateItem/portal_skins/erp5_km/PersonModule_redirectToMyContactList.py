web_site = context.getWebSiteValue()
search_area_web_section_id = web_site.getLayoutProperty('search_area_web_section_id',
                                                        default=None)
if search_area_web_section_id:
  search_section = web_site[search_area_web_section_id]
else:
  search_section = web_site

search_section.Base_redirect(form_id='PersonModule_viewMyContactList',
                keep_items=dict(reset=1,
                                search_section_path=context.getRelativeUrl()))
