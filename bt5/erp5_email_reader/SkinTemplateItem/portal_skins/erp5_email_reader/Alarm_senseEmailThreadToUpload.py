for email in context.portal_catalog(portal_type="Email Thread", validation_state="outgoing"):
  email.getObject().activate(activity='SQLDict').upload()
