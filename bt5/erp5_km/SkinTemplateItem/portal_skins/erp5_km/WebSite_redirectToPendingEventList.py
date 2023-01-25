"""
  TODO:
    - Rename Event to Task everywhere
"""


context.getWebSiteValue().Base_redirect(form_id='WebSite_viewPendingEventList',
                keep_items=dict(reset=1,
                                search_section_path=context.getRelativeUrl()))
