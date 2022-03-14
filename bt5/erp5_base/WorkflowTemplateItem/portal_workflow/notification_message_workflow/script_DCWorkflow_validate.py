"""
This script is invoked each time a new message is validated
The previous version is archived automatically.
"""
document = state_change['object']
reference = document.getReference()
if not reference:
  # If this object has no reference, we can not do anything
  return
portal = document.getPortalObject()
portal_catalog = portal.portal_catalog
search_kw = dict(reference=reference,
                 validation_state="validated",
                 uid='NOT %s' %document.getUid())
for old_document in portal_catalog(**search_kw):
  old_document = old_document.getObject()
  old_document.archive()
