"""
================================================================================
Return parameters to correctly display the RenderJS gadget
================================================================================
"""
# parameters
# ------------------------------------------------------------------------------
# context_url:                   relative url of the context calling this script

from Products.ERP5Type.Log import log
portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

reference = str(context.getReference()) + "-Home.Page"
home_page = portal_catalog.getResultValue(
              portal_type = 'Web Page',
              reference = reference,
              validation_state = "published_alive")

if home_page:
  content = home_page.getTextContent()
else:
  content = ""

if home_page:
  home_page_jio_key = home_page.getRelativeUrl()
else:
  home_page_jio_key = ""

return [('project_title', context.getTitle()), ('jio_key', context.getRelativeUrl()), ('home_page_jio_key', home_page_jio_key), ('home_page_content', content)]
