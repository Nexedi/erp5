"""
Jump from Organisation to its related objects (but only if used as
source* or destination* categories) of the same portal type and
displayed using the module view

XXX: move this code to erp5_core if needed elsewhere?
"""
portal = context.getPortalObject()

# XXX: Seems there is no other better way to get the Arrow
#      destination/section categories...
base_category_list = []
for arrow_property in portal.portal_property_sheets.Arrow.contentValues():
  if arrow_property.getPortalType() != 'Category Property':
    continue

  arrow_property_title = arrow_property.getTitle()
  if (arrow_property_title.startswith('source') or
      arrow_property_title.startswith('destination')):
    base_category_list.append(arrow_property_title)

related_object_list = context.getRelatedValueList(
  checked_permission='View',
  base_category_list=base_category_list,
  portal_type=portal_type)

if not related_object_list:
  message = portal.Base_translateString('No ${portal_type} related.',
                                        mapping={'portal_type': portal_type})

  return context.Base_redirect(keep_items=dict(portal_status_message=message))

elif len(related_object_list) == 1:
  related_object = related_object_list[0]
  message = portal.Base_translateString(
    '${this_portal_type} related to ${that_portal_type}: ${that_title}.',
    mapping={"this_portal_type": related_object.getTranslatedPortalType(),
             "that_portal_type": context.getTranslatedPortalType(),
             "that_title": context.getTitleOrId()})

  return related_object.Base_redirect(
    keep_items=dict(reset=1,
                    portal_status_message=message))

else:
  # XXX: Use POST rather than GET because of GET URL length limitation?
  return portal.getDefaultModule(portal_type).Base_redirect(
    keep_items={'reset': 1,
                'uid': [obj.getUid() for obj in related_object_list]})
