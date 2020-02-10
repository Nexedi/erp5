portal = context.getPortalObject()

portal.portal_catalog.searchAndActivate(
  portal_type=["Active Process",],
  method_id='ActiveProcess_removeItselfFromActivityTool',
  reference="document_scanner_js",
  # Active Process don't have creation date set
  indexation_timestamp="< %s" % (DateTime()-4).earliestTime(),
)
