if not data:
  data = {}

origin = context.Base_getRequestHeader("Origin")
if origin:
  if 'cors' in data and origin in data.get('cors', []):
    return True
  return False
return True
