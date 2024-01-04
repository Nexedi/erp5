# This script set language property according to existing language category.
for i in context.getPortalObject().glossary_module.objectValues():
  lang_list = [x.split('/')[1] for x in i.categories if x.startswith('language/')]
  if len(lang_list):
    lang = lang_list[0]
    i.setLanguage(lang)
    i.setCategoryList([x for x in i.categories if not x.startswith('language/')])
    print(i.getPath(), lang)
print('Migration finished.')
return printed
