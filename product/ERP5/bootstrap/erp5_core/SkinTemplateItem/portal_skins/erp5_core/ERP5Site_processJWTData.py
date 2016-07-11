origin = context.Base_getRequestHeader("Origin")
if origin:
  if not data:
    data = {}
  return origin in data.get('cors', ()) if data else False
return True
