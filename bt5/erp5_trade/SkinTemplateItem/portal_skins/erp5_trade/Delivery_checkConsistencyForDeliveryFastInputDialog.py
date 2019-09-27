"""This script check that values fit fast input requirements.
If validation succeeds, then form_dialog is returned.
Otherwise a message is displayed to the user.
"""
portal = context.getPortalObject()

delivery = context
if delivery.getPortalType() in portal.getPortalContainerTypeList():
  delivery = context.getExplanationValue()

# Retrieve lines portal type
line_portal_type_list = [x for x in delivery.getTypeInfo().getTypeAllowedContentTypeList() \
                         if x in portal.getPortalMovementTypeList()]
line_portal_type = line_portal_type_list[0]

use_list = []
# Check if the section and use preference are defined
if line_portal_type in portal.getPortalSaleTypeList():
  section_uid = delivery.getSourceSectionUid()
  use_list = portal.portal_preferences.getPreferredSaleUseList()
elif line_portal_type in portal.getPortalPurchaseTypeList():
  section_uid = delivery.getDestinationSectionUid()
  use_list = portal.portal_preferences.getPreferredPurchaseUseList()
elif line_portal_type in portal.getPortalInternalTypeList() + portal.getPortalInventoryMovementTypeList():
  section_uid = ""
  use_list = portal.portal_preferences.getPreferredPurchaseUseList() + \
             portal.portal_preferences.getPreferredSaleUseList()
else:
  from Products.ERP5Type.Message import translateString
  return context.Base_redirect('view', keep_items=dict(
    portal_status_message=translateString('Type of document not known to retrieve section.')))

if len(use_list) == 0:
  from Products.ERP5Type.Message import translateString
  return context.Base_redirect('view', keep_items=dict(
    portal_status_message=translateString('Use preference must be defined.')))
  
if section_uid is None:
  from Products.ERP5Type.Message import translateString
  return context.Base_redirect('view', keep_items=dict(
    portal_status_message=translateString('Section must be defined.')))

return context.Base_renderForm('Delivery_viewDeliveryFastInputDialog', *args, **kw)
