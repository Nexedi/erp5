assert context.getPortalType() == "Active Process", "It must be an Active Process"
assert context.getReference() == context.Base_getDocumentScannerDefaultReference(), "Unexpected reference"

context.getPortalObject().portal_activities.manage_delObjects(
  ids=[context.getId(),])
