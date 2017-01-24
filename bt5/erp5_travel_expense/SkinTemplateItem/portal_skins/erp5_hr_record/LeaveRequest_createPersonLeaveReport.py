portal = context.getPortalObject()

record = portal.record_module.newContent(
  portal_type="Leave Report Record",
  source=context.getDestination(),
  follow_up=context.getDestination(),
  )

record.stop()
record.Record_archivePreviousVersions()
