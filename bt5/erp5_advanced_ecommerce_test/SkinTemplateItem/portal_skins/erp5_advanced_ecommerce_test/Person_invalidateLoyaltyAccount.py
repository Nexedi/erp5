default_user_login = context.portal_catalog.getResultValue(
  portal_type='ERP5 Login',
  validation_state="validated",
  reference=1)
if default_user_login:
  default_user = default_user_login.getParentValue()
  default_user.manage_delObjects(ids=[x.getId() for x in default_user.contentValues(portal_type='Loyalty Account')])
  for loyalty in default_user.Base_getRelatedObjectList(portal_type='Loyalty Transaction'):
    for loyalty_line in loyalty.contentValues(portal_type='Loyalty Transaction Line'):
      loyalty_line.edit(quantity=0)
return "Done"
