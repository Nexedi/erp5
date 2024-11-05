topmost_url_document = context.Base_getURLTopmostDocumentValue()
if not topmost_url_document.getOriginalDocument().isURLAncestorOf(cancel_url):
  return context.ERP5Site_redirect(topmost_url_document.absolute_url(),
    keep_items={'portal_status_message': 'Redirection to an external site prevented.'},
    **kw)

if '?selection_name=' in cancel_url or '&selection_name=' in cancel_url:
  # if selection_name is already present in the cancel URL, we do not
  # use erp5_xhtml_style script that would add it again.
  return context.REQUEST.RESPONSE.redirect(cancel_url)
return context.ERP5Site_redirect(cancel_url, **kw)
