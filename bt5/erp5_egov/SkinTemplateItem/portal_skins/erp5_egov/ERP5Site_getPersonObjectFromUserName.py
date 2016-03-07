module = context.getDefaultModule(portal_type='Person')
result = module.searchFolder(reference=user_name)

if len(result) == 1:
  return result[0]

return None
