portal = context.getPortalObject()

INVALID_SUFFIX = portal.getIngestionReferenceDictionary()["invalid_suffix"]

try:
  if document.getReference().endswith(INVALID_SUFFIX):
    document.setReference(document.getReference().replace(INVALID_SUFFIX, ""))
except Exception as e:
  context.logEntry("[ERROR] Error revalidating object: %s" % str(e))
