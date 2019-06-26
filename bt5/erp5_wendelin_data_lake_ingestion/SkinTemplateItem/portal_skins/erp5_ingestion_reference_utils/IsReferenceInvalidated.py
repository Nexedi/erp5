portal = context.getPortalObject()

INVALID_SUFFIX = portal.getIngestionReferenceDictionary()["invalid_suffix"]

return document.getReference().endswith(INVALID_SUFFIX)
