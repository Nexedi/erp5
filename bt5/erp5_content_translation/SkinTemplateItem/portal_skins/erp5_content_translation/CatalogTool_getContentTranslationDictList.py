from Products.ERP5Type.Utils import convertToUpperCase
portal = context.getPortalObject()
portal_type_property_mapping = portal.ERP5Site_getPortalTypeContentTranslationMapping()

result = []

def upperCase(text):
  return convertToUpperCase(text.replace('-', '_'))

content_language_list = context.Localizer.get_languages()

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

    for content_language in content_language_list:
      method_name = 'get%s' % (upperCase('%s_translated_%s' %
                                         (content_language, property_name)),)
      translated_text = None
      method = getattr(document, method_name, None)
      if method is not None and document.getProperty('%s_translation_domain' % property_name) == 'content':
        translated_text = method()
      else:
        translation_method = getattr(document, 'get%s' % upperCase('translated_%s' % property_name), None)
        if original_text is not None and translation_method is not None:
          temporary_translated_text = translation_method(language=content_language)
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
