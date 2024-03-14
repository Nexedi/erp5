from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import Message

context = state_change['object']
translate = context.Base_translateString

# Only allow to set Follow-Up Sale Order if its destination refereference is our OrderID
# or if it is not yet Follow-Up to another Order Request
sale_order = context.getFollowUpValue(portal_type="Sale Order")
if sale_order is None:
  return
if sale_order.getDestinationReference() == context.getReference():
  return
order_request_list = sale_order.getFollowUpRelatedValueList(portal_type="Cxml Order Request")
for previous_order_request in order_request_list:
  if previous_order_request != context:
    # we found another order request, so we raise
    error = translate("Cannot FollowUp to Sale Order %s because it is related to another Order Request and the OrderID does not match." %sale_order.getTitle())
    raise ValidationFailed(Message('erp5_ui', error))
