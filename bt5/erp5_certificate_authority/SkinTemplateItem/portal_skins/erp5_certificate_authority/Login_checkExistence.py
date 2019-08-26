portal_type = context.getPortalType()


# Define backward compatibility for do not duplicate Certificate and ERP5 Login
if portal_type in ("ERP5 Login", "Certificate Login"):
  portal_type = ("ERP5 Login", "Certificate Login")

return context.getPortalObject().Base_checkLoginExistence(
  portal_type=portal_type,
  reference=context.getReference(),
  ignore_uid=context.getUid(),
  ignore_user_uid=context.getParentValue().getUid(),
)
