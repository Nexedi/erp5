from Products.DCWorkflow.DCWorkflow import ValidationFailed
from Products.ERP5Type.Message import Message

delivery = state_change['object']

cell_list = delivery.getMovementList()

# We must check that we have a quantity of 100
# for each kind of banknote
resource_dict = {}
for cell in cell_list:
  resource = cell.getResource()
  resource_dict[resource] = resource_dict.get(resource, 0.0) + cell.getQuantity()

for resource, total_quantity in resource_dict.items():
  if round(total_quantity,3) != 1.0:
    portal = delivery.getPortalObject()
    resource_value = portal.restrictedTraverse(resource)
    message = Message(domain='ui', message="Sorry, you must have a quantity of 1 for : $resource_title",
                      mapping={'resource_title': resource_value.getTranslatedTitle()})
    raise ValidationFailed(message)
