"""
  A script which actually creates and returns the query object.
"""

query_module = context.getPortalObject().query_module
query = query_module.newContent(description=description,
                                title=context.getPortalType(),
                                agent_value=context)
query.updateLocalRolesOnSecurityGroups()
query.post()
return query
