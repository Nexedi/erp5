portal = context.getPortalObject()

portal.portal_catalog.searchAndActivate(
  portal_type=["Active Process",],
  method_id='ActiveProcess_removeItselfFromActivityTool',
  reference=context.Base_getDocumentScannerDefaultReference(),
  # Active Process don't have creation date set
  modification_date=(DateTime()-4).earliestTime(),
  comparison_operator="<"
)
