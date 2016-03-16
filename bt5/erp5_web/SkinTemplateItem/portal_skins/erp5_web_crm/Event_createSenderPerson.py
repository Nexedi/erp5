portal = context.getPortalObject()
portal_type = 'Person'
module = portal.getDefaultModule(portal_type)

sender_list = [entity.getRelativeUrl() for entity\
               in context.Base_getEntityListFromFromHeader(default_email_text or '')]

if sender_list:
  context.setSourceList(sender_list)
  message = portal.Base_translateString('Sender found from ${person_module_translated_title}.',
                                        mapping={'person_module_translated_title': module.getTranslatedTitle()})
  return context.Base_redirect(form_id=kw.get('form_id', 'view'),
                               keep_items={'portal_status_message': message})


person = module.newContent(portal_type=portal_type,
                           default_email_text=default_email_text,
                           default_telephone_text=default_telephone_text,
                           first_name=first_name,
                           last_name=last_name)

context.setSourceValue(person)

message = portal.Base_translateString('Sender Person Created.')
return context.Base_redirect(form_id=kw.get('form_id', 'view'),
                             keep_items={'portal_status_message': message})
