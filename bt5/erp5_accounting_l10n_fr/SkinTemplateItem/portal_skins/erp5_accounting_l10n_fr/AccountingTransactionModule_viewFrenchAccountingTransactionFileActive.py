portal = context.getPortalObject()
at_date = at_date.latestTime()

section_uid_list = portal.Base_getSectionUidListForSectionCategory(
  section_category, section_category_strict)

from_date = portal.Base_getAccountingPeriodStartDateForSectionCategory(
  section_category, at_date)

# XXX we need proxy role for that
active_process = portal.portal_activities.newActiveProcess()

priority = 4

for portal_type in portal.getPortalAccountingTransactionTypeList():
  # XXX we need proxy role for that
  this_portal_type_active_process = portal.portal_activities.newActiveProcess()
  context.AccountingTransactionModule_viewFrenchAccountingTransactionFileForPortalType(
    portal_type,
    section_uid_list,
    from_date,
    at_date,
    simulation_state,
    ledger,
    active_process.getRelativeUrl(),
    this_portal_type_active_process.getRelativeUrl(),
    tag,
    aggregate_tag,
    priority)

context.activate(after_tag=(tag, aggregate_tag)).AccountingTransactionModule_aggregateFrenchAccountingTransactionFile(
  at_date,
  active_process.getRelativeUrl(),
  user_name=user_name)
