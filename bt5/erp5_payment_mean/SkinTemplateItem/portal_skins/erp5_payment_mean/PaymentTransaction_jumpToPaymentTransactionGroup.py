translateString = context.Base_translateString
portal_type = 'Payment Transaction Group'

for line in context.getMovementList(
        portal_type=context.getPortalAccountingMovementTypeList()):

  related_object = line.getAggregateValue(portal_type=portal_type)

  if related_object is not None:
    return related_object.Base_redirect('view', keep_items=dict(
      portal_status_message=translateString(
      # first, try to get a full translated message with portal types
      "%s related to %s." % (related_object.getPortalType(), context.getPortalType()),
       # if not found, fallback to generic translation
      default=translateString('${this_portal_type} related to ${that_portal_type} : ${that_title}.',
        mapping={"this_portal_type": related_object.getTranslatedPortalType(),
                 "that_portal_type": context.getTranslatedPortalType(),
                 "that_title": context.getTitleOrId()}))))

return context.Base_redirect('view', keep_items=dict(
    portal_status_message=translateString(
    'No %s Related' % portal_type,
    default=translateString('No ${portal_type} related.',
                             mapping={'portal_type': translateString(portal_type)}))))
