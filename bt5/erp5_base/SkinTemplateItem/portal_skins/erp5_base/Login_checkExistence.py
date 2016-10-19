return context.getPortalObject().Base_checkLoginExistence(
  portal_type=context.getPortalType(),
  reference=context.getReference(),
  ignore_uid=context.getUid(),
  ignore_user_uid=context.getParentValue().getUid(),
)
