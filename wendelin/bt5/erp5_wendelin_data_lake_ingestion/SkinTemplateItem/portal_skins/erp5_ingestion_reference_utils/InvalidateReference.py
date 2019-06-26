portal = context.getPortalObject()

INVALID_SUFFIX = portal.getIngestionReferenceDictionary()["invalid_suffix"]

try:
  if not document.getReference().endswith(INVALID_SUFFIX):
    document.setReference(document.getReference() + INVALID_SUFFIX)
except Exception as e:
  context.logEntry("[ERROR] Error invalidating object: %s" % str(e))
