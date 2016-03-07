result = []
for property_name in context.getTypeInfo().getContentTranslationDomainPropertyNameList():
  original_text = context.getProperty(property_name)
  if original_text:
    result.append((property_name, original_text))
return result
