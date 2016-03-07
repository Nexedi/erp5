from Products.ERP5Type.Message import translateString
bug_line = context.newContent(portal_type='Bug Line',
  title = title, text_content=text_content)
bug_line.start()

if batch_mode:
  return bug_line
else:
  return context.Base_redirect(form_id, keep_items=dict(
        portal_status_message=translateString('Bug Line sent.')))
