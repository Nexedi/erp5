catalog = context.portal_catalog
glossary_module = context

for i in catalog(portal_type='Glossary Term',
                 validation_state='validated',
                 language_id='en'):

  english_term = i.getObject()

  reference = english_term.getReference()
  business_field = english_term.getBusinessField()

  if catalog.getResultValue(portal_type='Glossary Term',
                            causality_uid=english_term.getUid(),
                            reference=reference,
                            business_field_title=business_field,
                            language_id=language) is not None:
    continue

  glossary_module.newContent(portal_type='Glossary Term',
                                        reference=reference,
                                        business_field=business_field,
                                        language=language,
                                        title=english_term.getTitle(),
                                        description=english_term.getDescription(),
                                        comment=english_term.getComment(),
                                        causality=english_term.getRelativeUrl()
                                        )

portal_status_message = context.Base_translateString('Terms created.')
context.Base_redirect(keep_items={'portal_status_message':portal_status_message})
