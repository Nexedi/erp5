"""
  Launch the resolution process and display
  a message to the user.
"""
translateString = context.Base_translateString
context.solve()
return context.Base_redirect(form_id,
  keep_items = dict(portal_status_message = translateString("Alarm solving started.",)))
