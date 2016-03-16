"""External Validator for BIC on bank account
"""
if not editor:
  return True

if len(editor) not in (8, 11):
  return False

if not editor[:5].isalpha():
  return False

if not editor[5:].isalnum():
  return False

return True
