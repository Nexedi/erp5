"""Valid line field input as email list"""
#We stop the hook if we get an error else no error
def hasError(email):
  email_parts = email.split('@')
  if len(email_parts) != 2:
    return True

  suffix_parts = email_parts[1].split('.')
  if len(suffix_parts) < 2:
    return True

  if len(email_parts[0]) == 0:
    return True

  if len(suffix_parts[0]) == 0 or len(suffix_parts[1]) == 0 :
    return True

  return False

for email in value:
  if hasError(email):
    break
else:
  return True


return False
