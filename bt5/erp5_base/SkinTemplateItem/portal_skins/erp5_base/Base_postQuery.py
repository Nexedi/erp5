translateString = context.Base_translateString
ptype = context.getPortalType()

if not description:
  return context.Base_redirect(dialog_id,
              keep_items = dict(portal_status_message = translateString("Question can not be empty.",), cancel_url = cancel_url))

query = context.Base_newQuery(description=description)
query_id = query.getId()
return context.Base_redirect(form_id,
              keep_items = dict(portal_status_message = translateString("A Query about the current ${portal_type} was posted with ID ${query_id}.", mapping = dict(query_id=query_id, portal_type=ptype)),
              cancel_url = cancel_url))
