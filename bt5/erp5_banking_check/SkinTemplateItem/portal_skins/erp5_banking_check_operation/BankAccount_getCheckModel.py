PORTAL_TYPE_TO_CHECK_MODEL_REFERENCE = {
  'Person': 'CCOP',
  'Organisation': 'CCCO',
}

entity_portal_type = context.getParentValue().getPortalType()
reference = PORTAL_TYPE_TO_CHECK_MODEL_REFERENCE[entity_portal_type]
check_resource = context.getPortalObject().Base_getCheckModelByReference(
  reference=reference,
  unique_per_account=unique_per_account,
)
return check_resource
