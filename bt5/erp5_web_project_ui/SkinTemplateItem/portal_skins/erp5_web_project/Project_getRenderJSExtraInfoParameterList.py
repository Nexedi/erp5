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
              reference = reference)

if home_page:
  content = home_page.getTextContent()
else:
  content = ""

return [('project_title', context.getTitle()), ('jio_key', context.getRelativeUrl()), ('home_page_content', content)]
