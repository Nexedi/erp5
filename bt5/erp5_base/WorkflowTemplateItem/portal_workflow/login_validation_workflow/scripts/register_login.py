obj = state_change['object']
obj.activate(tag='login:%s:%s' % (obj.getPortalType(), obj.getReference())).reindexObject()
