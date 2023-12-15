Base_translateString = context.getPortalObject().Base_translateString
language_tuple_list = [
  (Base_translateString('French'), 'fr'),
  (Base_translateString('English'), 'en'),
  (Base_translateString('German'), 'de'),
  (Base_translateString('Dutch'), 'nl'),
]

if is_source_language:
  return [('Auto-detect', 'auto')] + language_tuple_list
else:
  return language_tuple_list
