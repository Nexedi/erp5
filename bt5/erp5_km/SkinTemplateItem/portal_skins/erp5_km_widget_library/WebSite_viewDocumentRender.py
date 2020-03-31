"""
Returns a document by its reference in a gadget.
"""
portal = context.getPortalObject()

if box_relative_url:
  box = portal.restrictedTraverse(box_relative_url)
preferences = box.KnowledgeBox_getDefaultPreferencesDict()
reference=preferences.get('preferred_document_reference', None)
if reference is not None:
  web_page_list = context.getDocumentValueList(reference=reference, all_languages=True,
                                         portal_type='Web Page')
  if len(web_page_list):
    return '<div class="web-page-renderer">%s</div>' %web_page_list[0].getObject().asStrippedHTML()

return 'No document'
