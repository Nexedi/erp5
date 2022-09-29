translateString = context.Base_translateString

text_content = context.getTextContent()
error_list = context.TestPage_validateContent(text_content)

if len(error_list) > 0:
  portal_status_message = " ".join(error_list)
else:
  portal_status_message = translateString("No error was found.")

return context.Base_redirect(context.REQUEST.get("form_id", ""),
                             keep_items=dict(portal_status_message=portal_status_message))
