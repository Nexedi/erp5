portal = context.getPortalObject()
Base_translateString = portal.Base_translateString

redirect_context = context
catalog_list = context.Base_getRelatedDocumentList(limit=2)

if len(catalog_list) == 0:
  message = Base_translateString('No Document Related')

elif len(catalog_list) == 1:
  redirect_context = catalog_list[0].getObject()
  if target_form_id is not None:
    form_id = target_form_id
  message = Base_translateString(
    # first, try to get a full translated message with portal types
    "%s related to %s." % (redirect_context.getPortalType(), context.getPortalType()),
     # if not found, fallback to generic translation
    default=Base_translateString('${this_portal_type} related to ${that_portal_type} : ${that_title}.',
      mapping={"this_portal_type": redirect_context.getTranslatedPortalType(),
               "that_portal_type": context.getTranslatedPortalType(),
               "that_title": context.getTitleOrId() }),)

else:
  form_id = relation_form_id
  message = Base_translateString(
    # first, try to get a full translated message with portal types
    "Documents related to %s." % context.getPortalType(),
     # if not found, fallback to generic translation
    default=Base_translateString('Documents related to ${that_portal_type} : ${that_title}.',
      mapping={"that_portal_type": context.getTranslatedPortalType(),
               "that_title": context.getTitleOrId() }),)

query_params = dict(portal_status_message=message)
return redirect_context.Base_redirect(
         form_id, keep_items=query_params)
