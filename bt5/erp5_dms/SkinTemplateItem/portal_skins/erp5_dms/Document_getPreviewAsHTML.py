from Products.PythonScripts.standard import html_quote
portal = context.getPortalObject()
translateString = portal.Base_translateString

result = ''
error_message = None
if context.getSize() > (portal.portal_preferences.getPreferredDocumentPreviewMaxAllowedSize() or 5 * 1024 * 1024):
  error_message = translateString("Document is too large to be previewed")
else:
  try:
    result = context.asStrippedHTML()
    if result:
      return result
    if not context.hasBaseData():
      error_message = context.Base_translateString("This document is not converted yet.")
  except Exception as e:
    from erp5.component.module.Log import log
    log("asStrippedHTML", str(e))
    error_message = "%s %s" % (translateString("Preview Error:"),
                              str(e))

if error_message is not None:
  return '<div class="error">%s</div>' % html_quote(error_message)

return result
