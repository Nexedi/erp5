password_confirm = request.get('field_your_password_confirm', None)
if editor.encode('ascii', 'ignore') != editor:
  return False
return password_confirm == editor
