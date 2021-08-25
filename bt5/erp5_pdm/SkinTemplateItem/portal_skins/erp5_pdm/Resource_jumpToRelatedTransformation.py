portal = context.getPortalObject()
translateString = portal.Base_translateString
transformation_value_list = context.getRelatedValueList(checked_permission='View',
                                                        portal_type=('Transformation',
                                                                     'Transformation Transformed Resource'))
if len(transformation_value_list) == 0:
  return context.Base_redirect(form_id,
                               keep_items=dict(portal_status_message=translateString('No Transformation related.')))
elif len(transformation_value_list) == 1:
  related_object = transformation_value_list[0]
  if related_object.getPortalType() == 'Transformation Transformed Resource':
    related_object = related_object.getParentValue()

  return related_object.Base_redirect(keep_items=dict(
      reset=1,
      portal_status_message=portal.Base_translateString(
      # first, try to get a full translated message with portal types
      "%s related to %s." % (related_object.getPortalType(), context.getPortalType()),
       # if not found, fallback to generic translation
      default=translateString('${this_portal_type} related to ${that_portal_type} : ${that_title}.',
        mapping={"this_portal_type": related_object.getTranslatedPortalType(),
                 "that_portal_type": context.getTranslatedPortalType(),
                 "that_title": context.getTitleOrId()}))))

else:
  transformation_uid_list = []
  for value in transformation_value_list:
    if value.getPortalType() == 'Transformation Transformed Resource':
      uid = value.getParentUid()
    else:
      uid = value.getUid()

    transformation_uid_list.append(uid)

  module = portal.getDefaultModule('Transformation')
  message = translateString(
      # first, try to get a full translated message with portal types
      "Documents related to %s." % context.getPortalType(),
        # if not found, fallback to generic translation
      default=translateString('Documents related to ${that_portal_type} : ${that_title}.',
        mapping={"that_portal_type": context.getTranslatedPortalType(),
                  "that_title": context.getTitleOrId() }),)
  return module.Base_redirect('view',
                              keep_items=dict(reset=1,
                                              portal_status_message=message,
                                              ignore_hide_rows=1,
                                              uid=transformation_uid_list))
