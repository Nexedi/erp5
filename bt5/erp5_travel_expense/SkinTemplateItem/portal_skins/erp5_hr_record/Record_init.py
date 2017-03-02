# Without this, getContentType() returns a method
# and it causes a problem when record is cloned.
context.setContentType(None)

context.setSourceValue(context.getPortalObject().portal_membership.getAuthenticatedMember().getUserValue())
context.Event_init()
