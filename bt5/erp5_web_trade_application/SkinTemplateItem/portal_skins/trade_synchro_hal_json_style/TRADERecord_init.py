# Without this, getContentType() returns a method
# and it causes a problem when record is cloned.
context.setContentType(None)

context.setContributorValue(context.ERP5Site_getAuthenticatedMemberPersonValue())
