portal = context.getPortalObject()
portal_catalog = portal.portal_catalog

data_set = portal.data_set_module.get(reference)
if data_set is not None:
  version = int(data_set.getVersion()) + 1
  data_set.setVersion("%03d" % (version,))
else:
  context.logEntry("Fail to increase dataset version. No dataset found for reference '%s'" % (reference))
