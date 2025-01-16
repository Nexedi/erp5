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

return context.getCausalityValue(portal_type='Manufacturing Execution').Base_redirect('view', keep_items={"portal_status_message":context.Base_translateString("Result is posted")})
