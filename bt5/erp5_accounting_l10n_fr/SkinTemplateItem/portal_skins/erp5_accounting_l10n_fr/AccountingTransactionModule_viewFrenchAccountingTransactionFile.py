from Products.ERP5Type.Message import translateString
portal = context.getPortalObject()

if group_by in ('ledger', 'portal_type_ledger') and ledger is None:
  return context.Base_redirect('view', keep_items=dict(
              portal_status_message=translateString("At least one Ledger must be selected")))

# Only for ERP5Site_notifyReportComplete after aggregating all the Journals
person_value = portal.portal_membership.getAuthenticatedMember().getUserValue()
user_name = person_value.Person_getUserId() if person_value is not None else None

tag = 'AccountingTransactionModule_viewFrenchAccountingTransactionFile'
aggregate_tag = '%s:aggregate' % tag

if portal.portal_activities.countMessageWithTag(tag) or \
      portal.portal_activities.countMessageWithTag(aggregate_tag):
  return context.Base_redirect(form_id, keep_items=dict(
              portal_status_message=translateString("Report already in progress.")))

context.activate().AccountingTransactionModule_viewFrenchAccountingTransactionFileActive(
  section_category,
  section_category_strict,
  from_date,
  at_date,
  group_by,
  simulation_state,
  ledger,
  user_name=user_name,
  tag=tag,
  aggregate_tag=aggregate_tag,
  date_column=date_column,
  search_kw=search_kw)

return context.Base_redirect(form_id, keep_items=dict(
              portal_status_message=translateString("Report Started")))
