default_user_login = context.portal_catalog.getResultValue(
  portal_type='ERP5 Login',
  validation_state="validated",
  reference=1)
if default_user_login:
  default_user_login.invalidate()
  default_user_login.getParentValue().invalidate()
context.Zuite_waitForActivities()
return "Done"
