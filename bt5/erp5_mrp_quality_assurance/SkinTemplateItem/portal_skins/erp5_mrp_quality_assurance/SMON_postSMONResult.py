from DateTime import DateTime

user_value = context.portal_membership.getAuthenticatedMember().getUserValue()

now = DateTime()

context.edit(
  effective_date = now,
  destination_decision_value = user_value
)
me_line = context.getAggregateRelatedValue(portal_type='Manufacturing Execution Line')
me_line.edit(
  start_date = now,
  stop_date = now
)
context.post()

delivery = context.getCausalityValue(portal_type='Manufacturing Execution')
if delivery.getSimulationState() == 'started':
  delivery.edit(stop_date = now)
  delivery.stop(comment='SMON: is validated %s' % context.getRelativeUrl())
return delivery.Base_redirect('view', keep_items={"portal_status_message":context.Base_translateString("SMON is validated")})
