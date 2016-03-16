"""
Public interface to the API method "convertToBase" which produces ODF version
of the document data, also discovering and setting metadata.
"""
translateString = context.Base_translateString
msg = context.convertToBaseFormat()
return context.Base_redirect(form_id,
              keep_items = dict(portal_status_message = translateString(msg)))
