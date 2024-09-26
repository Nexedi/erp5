# Do not re-index security recursively if contained objects don't acquire roles
#
# After all, recursively re-indexing a module in a production system
# with lots of content could mean hours of non-usable overloaded system.
type_tool = context.getPortalObject().portal_types
for portal_type_name in context.getTypeInfo().getTypeAllowedContentTypeList():
  if getattr(type_tool, portal_type_name).getTypeAcquireLocalRole():
    reindex = context.recursiveReindexObject
    break
else:
  reindex = context.reindexObject

return reindex(*args, **kw)
