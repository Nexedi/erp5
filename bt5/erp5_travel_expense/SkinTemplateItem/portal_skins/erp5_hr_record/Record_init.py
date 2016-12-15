# Without this, getContentType() returns a method
# and it causes a problem when record is cloned.
context.setContentType(None)

context.setSourceValue(context.ERP5Site_getAuthenticatedMemberPersonValue())
context.Event_init()
