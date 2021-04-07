from Products.ERP5Type.Message import translateString
document = state_change_info['object']
portal = state_change_info.getPortal()

error_message_list = []
language_item_list = portal.Base_getContentTranslationLanguageValueAndLabelList()

for property_name in document.getTypeInfo().getContentTranslationDomainPropertyNameList():
  original_message = document.getProperty(property_name)
  for language, language_label in language_item_list:
    try:
      translation_original_text = document.getPropertyTranslationOriginalText(property_name, language)
    except KeyError:
      translation_original_text = None
    if translation_original_text is not None and translation_original_text!=original_message:
      error_message = translateString(
        'property ${property_name} of ${language} is outdated', mapping={'property_name':property_name, 'language':language_label})
      error_message_list.append(error_message)


content_translation_state = portal.portal_workflow.getInfoFor(document, 'content_translation_state')


if error_message_list:
  if content_translation_state!='outdated':
    document.invalidateContentTranslation(error_message=error_message_list)
else:
  if content_translation_state!='latest':
    document.validateContentTranslation()
