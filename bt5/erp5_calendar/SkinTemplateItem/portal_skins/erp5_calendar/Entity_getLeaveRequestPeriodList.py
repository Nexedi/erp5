kw = {}
kw["node_uid"]=context.getUid()
kw["portal_type"]="Leave Request Period"
#raise ValueError("%s" % kw)
return context.getPortalObject().portal_simulation.getInventoryList(**kw)
