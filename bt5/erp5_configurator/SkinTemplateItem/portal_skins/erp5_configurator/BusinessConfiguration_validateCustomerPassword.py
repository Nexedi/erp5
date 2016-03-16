password_confirm = request.get('field_your_password_confirm', None)
try:
  if editor.encode('ascii', 'ignore') != editor:
    return 0
except:
  return 0
return password_confirm == editor
