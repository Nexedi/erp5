"""Jump to the invoice(s) related to this order
"""
portal = context.getPortalObject()
translateString = portal.Base_translateString
packing_list_list = context.getCausalityRelatedValueList(
                                          portal_type=packing_list_type,
                                          checked_permission='View')
related_invoice_uid_list = []
if packing_list_list:
  if len(packing_list_list) == 1:
    related_invoice_list = packing_list_list[0].getCausalityRelatedValueList(
                                portal_type=invoice_type,
                                checked_permission='View')
    related_invoice_uid_list = [o.getUid() for o in related_invoice_list]
    if len(related_invoice_list) == 1:
      related_object = related_invoice_list[0]
      message = translateString(
      # first, try to get a full translated message with portal types
      "%s related to %s." % (related_object.getPortalType(), context.getPortalType()),
       # if not found, fallback to generic translation
      default=translateString('${this_portal_type} related to ${that_portal_type} : ${that_title}.',
        mapping={"this_portal_type": related_object.getTranslatedPortalType(),
                 "that_portal_type": context.getTranslatedPortalType(),
                 "that_title": context.getTitleOrId() }))
      return related_object.Base_redirect('view',
                              keep_items=dict(portal_status_message=message))
  else:
    for packing_list in packing_list_list:
      related_invoice_uid_list.extend(
          [invoice.getUid() for invoice in packing_list.getCausalityRelatedValueList(
                                          portal_type=invoice_type,
                                          checked_permission='View')])

if related_invoice_uid_list:
  invoice_module = portal.getDefaultModule(invoice_type)
  return invoice_module.Base_redirect('view',
              keep_items=dict(reset=1,
                              uid=related_invoice_uid_list))

return context.Base_redirect(form_id, keep_items=dict(
    portal_status_message=translateString(
    'No %s Related' % invoice_type,
    default=translateString('No ${portal_type} related.',
                             mapping={'portal_type': translateString(invoice_type)}))))
