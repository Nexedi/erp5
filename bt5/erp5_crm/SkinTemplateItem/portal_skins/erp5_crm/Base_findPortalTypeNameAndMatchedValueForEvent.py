miss = (None, None)

if not value:
  return miss

# length of portal type name must be less than 100.
value_first_lowered = value[:100].lower()

if not ':' in value_first_lowered:
  return miss

Base_translateString = context.Base_translateString
language_list = context.Localizer.get_supported_languages()
translated_portal_type_list = []

def addCandidateTypeName(name, portal_type):
  translated_portal_type_list.append((name, portal_type))
  if ' ' in name:
    alternative = name.split(' ')[0]
    translated_portal_type_list.append((alternative, portal_type))

for type_name in context.getPortalEventTypeList():
  addCandidateTypeName(type_name, type_name)
  for language in language_list:
    translated = Base_translateString(type_name, lang=language)
    if translated != type_name:
      addCandidateTypeName(translated, type_name)

for translated, type_name in translated_portal_type_list:
  prefix = '%s:' % translated.lower()
  if value_first_lowered.startswith(prefix):
    return type_name, translated

return miss
