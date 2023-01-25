from Products.ERP5Type.Utils import convertToUpperCase
portal = context.getPortalObject()
portal_type_property_mapping = portal.ERP5Site_getPortalTypeContentTranslationMapping()

result = []

def upperCase(text):
  return convertToUpperCase(text.replace('-', '_'))

localizer = portal.Localizer
content_language_list = localizer.get_languages()

for document in document_list:
  portal_type = document.getPortalType()
  if portal_type not in portal_type_property_mapping:
    continue

  uid = document.getUid()
  for property_name in portal_type_property_mapping[portal_type]:
    temporary_result = []

    original_text = None
    original_method = getattr(document, 'get%s' % upperCase(property_name), None)
    if original_method is not None:
      original_text = original_method()

    property_translation_domain = document.getProperty('%s_translation_domain' % property_name)
    for content_language in content_language_list:
      method_name = 'get%s' % (upperCase('%s_translated_%s' %
                                         (content_language, property_name)),)
      translated_text = None
      method = getattr(document, method_name, None)
      if method is not None and property_translation_domain == 'content':
        translated_text = method()
      elif property_translation_domain == 'content_translation':
        translation_method = getattr(document, 'get%s' % upperCase('translated_%s' % property_name), None)
        if original_text is not None and translation_method is not None:
          temporary_translated_text = translation_method(language=content_language)
          if original_text != temporary_translated_text:
            translated_text = temporary_translated_text
      elif original_text:
        temporary_translated_text = (localizer.translate(
            domain=property_translation_domain,
            msgid=original_text,
            lang=content_language
        ) or original_text).encode('utf-8')
        if original_text != temporary_translated_text:
          translated_text = temporary_translated_text

      temporary_result.append({'uid': uid,
                               'property_name': property_name,
                               'content_language': content_language,
                               'translated_text': translated_text,
                               })
    # also add original content
    temporary_result.append({'uid': uid,
                             'property_name': property_name,
                             'content_language': '',
                             'translated_text': original_text,
                             })
    result.extend(temporary_result)
return result
