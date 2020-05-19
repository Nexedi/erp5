portal = context.getPortalObject()

INVALID_SUFFIX = portal.ERP5Site_getIngestionReferenceDictionary()["invalid_suffix"]

return document.getReference().endswith(INVALID_SUFFIX)
