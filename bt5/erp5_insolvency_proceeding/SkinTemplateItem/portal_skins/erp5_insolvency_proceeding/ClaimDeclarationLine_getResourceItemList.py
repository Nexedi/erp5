portal = context.getPortalObject()

return [''] + [
  ("%s - %s" %(x.getReference(), x.getTitle()), x.getRelativeUrl()) for x in portal.service_module.searchFolder(
    default_use_uid=portal.portal_categories.use.debt_recovery.getUid(),
    sort_on=("catalog.reference", "ASC"),
    portal_type='Service',
    validation_state="validated"
  )
]
