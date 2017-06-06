method_path = context.str_object_path + '/' + context.method_id
try:
  method_value = context.getPortalObject().restrictedTraverse(method_path)
except Exception:
  return
if getattr(method_value, 'manage_main', None) is not None:
  return method_path + '/manage_main'
