from Products.ERP5Type.Core.Workflow import ValidationFailed
from Products.ERP5Type.Message import Message

context = state_change['object']
translate = context.Base_translateString
portal = context.getPortalObject()

if state_change.kwargs.get('create_sale_order'):
  if context.getFollowUpValue() is not None:
    error = translate("Coult not validate. There is already a Follow-Up Sale Order.")
    raise ValidationFailed(Message('erp5_ui', error))
  sale_order_value = portal.sale_order_module.newContent(
    portal_type="Sale Order",
    destination_reference=context.getReference(),
    version=context.getVersion())
  context.setFollowUpValue(sale_order_value)
  if sale_order_value is not None:
    if sale_order_value.getSimulationState() == "draft":
      sale_order_value.SaleOrder_checkCxmlOrderRequestConsistency(fixit=True, order_request_value=context)
      sale_order_value.SaleOrder_cxmlInit()
else:
  sale_order_value = context.getFollowUpValue()
  if sale_order_value is None:
    error = translate("Could not validate. A Follow-Up Sale Order must be assigned or created.")
    raise ValidationFailed(Message('erp5_ui', error))
  else:
    # if Follow-Up Sale Order is already attached to another Order Request, clone it
    order_request_list = sale_order_value.getFollowUpRelatedValueList(portal_type="Cxml Order Request")
    for previous_order_request in order_request_list:
      if previous_order_request != context:
        # we found another order request, so we continue with cloning and setting versions
        # only allow cloning from here if destination reference on sale order is correct
        if sale_order_value.getDestinationReference() != context.getReference():
          error = translate("Cannot FollowUp to Sale Order %s because it is related to another Order Request and the OrderID does not match." %sale_order.getTitle())
          raise ValidationFailed(Message('erp5_ui', error))
        clone_order = sale_order_value.Order_cloneAndUpdateVersion()
        previous_order_request.setFollowUpValue(clone_order)
        if portal.portal_workflow.isTransitionPossible(sale_order_value, 'update'):
          sale_order_value.update()
        break
    else:
      # we did not find another order request, so no need to clone
      # we can set destination reference automatically if it is empty
      if not sale_order_value.getDestinationReference():
        sale_order_value.setDestinationReference(context.getReference())
      elif sale_order_value.getDestinationReference() != context.getReference():
        error = translate("Could not validate. The OrderID of the Follow-Up Sale Order does not match." %sale_order.getTitle())
        raise ValidationFailed(Message('erp5_ui', error))
    sale_order_value.setVersion(context.getVersion())

# Attach PDF to Sale Order
for pdf in context.getFollowUpRelatedValueList(portal_type="PDF", checked_permission="Modify portal content"):
  pdf.setFollowUpValueList(pdf.getFollowUpValueList() + [sale_order_value])

context.validate()
