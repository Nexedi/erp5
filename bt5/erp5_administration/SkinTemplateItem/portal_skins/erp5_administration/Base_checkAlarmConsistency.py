from Products.ERP5Type.Constraint import PropertyTypeValidity
from Products.CMFActivity.ActiveResult import ActiveResult

portal = context.getPortalObject()
constraint_message_list = []

if context.providesIConstraint():
  # it is not possible to checkConsistency of Constraint itself, as method
  # of this name implement consistency checking on object
  return constraint_message_list

# this constraint is created as a temp object under portal_trash, because
# portal_trash has no restriction on allowed content types.
missing_category_document = portal.portal_trash.newContent(
  portal_type='Missing Category Document Constraint',
  id='missing_category_document_constraint',
  temp_object=True)
property_type_validity = PropertyTypeValidity(id='type_check', description='Type Validity Check')

if fixit:
  constraint_message_list.extend(context.fixConsistency())
  constraint_message_list.extend(property_type_validity.fixConsistency(context))
  constraint_message_list.extend(missing_category_document.fixConsistency(context))
else:
  constraint_message_list.extend(context.checkConsistency(fixit=fixit))
  constraint_message_list.extend(property_type_validity.checkConsistency(context, fixit=fixit))
  constraint_message_list.extend(missing_category_document.checkConsistency(context, fixit=fixit))

if constraint_message_list:
  portal.restrictedTraverse(active_process).postResult(ActiveResult(severity=100,
                      constraint_message_list=constraint_message_list))
