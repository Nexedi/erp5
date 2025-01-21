from DateTime import DateTime

incompleted_list = context.Base_getIncompletedOperationList()

if incompleted_list:
  return context.Base_redirect('view',keep_items={
    "portal_status_message":context.Base_translateString("Remained Controls are not finished"),
    "portal_status_level": "error"
  })

user_value = context.portal_membership.getAuthenticatedMember().getUserValue()

now = DateTime()

context.edit(
  effective_date = now,
  destination_decision_value = user_value
)
me_line = context.getAggregateRelatedValue(portal_type='Manufacturing Execution Line')
me_line.edit(
  start_date = now,
  stop_date = now)

context.post()
delivery = context.getCausalityValue(portal_type='Manufacturing Execution')
if delivery.getSimulationState() == 'stopped':
  delivery.edit(effective_date = now)
  delivery.deliver(comment='ACOM: is validated %s' % context.getRelativeUrl())

  PPL = delivery.Delivery_setReadyECOM()
  msg = context.Base_translateString("ACOM is validated and ECOM is set to ready")
  return PPL.Base_redirect('view', keep_items={"portal_status_message":msg})


return delivery.Base_redirect('view', keep_items={"portal_status_message":context.Base_translateString("ACOM is validated")})
