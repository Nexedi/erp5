"""
 Cache and return a given Web Page as stripped HTML
 Use reference and language as cache keys

 TODO: remove same script in KM (XXX)
"""

def getInlinePage(reference, language):
  if reference:
    page = context.getDocumentValue(reference)
    if page is not None:
      return page.asStrippedHTML()
  return None

from Products.ERP5Type.Cache import CachingMethod
web_site_url = context.getWebSectionValue().absolute_url()
getInlinePage = CachingMethod(getInlinePage,
                 id=('WebSection_getInlinePageRenderer', web_site_url))
language = context.Localizer.get_selected_language()
return getInlinePage(reference, language)
