module = context.getDefaultModule(portal_type=portal_type)
return getattr(module, id, None)
