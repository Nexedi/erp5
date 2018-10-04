"""
================================================================================
Render page content for pages in this web section as book
================================================================================
"""
context.REQUEST.set("content_form_id", "WebPage_viewAsBook")

web_section = context.getWebSectionValue()
web_section_default_renderer = getattr(context, web_section.getApplicableLayout())

return web_section_default_renderer()
