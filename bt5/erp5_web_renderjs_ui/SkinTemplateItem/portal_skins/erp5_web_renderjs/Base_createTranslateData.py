import json

portal = context.getPortalObject()
Base_translateString = context.Base_translateString
translate_word = context.WebSite_getTranslatableMessageList()

language_list = context.getAvailableLanguageSet()

content = """
/*globals window*/\n
/*jslint indent: 2, nomen: true, maxlen: 80*/\n
(function (window) {\n
  "use strict";\n
"""

tmp = {}

for language in language_list:
  tmp[language] = {}
  for word in translate_word:
    tmp[language][word] = Base_translateString(word, lang = language)



content += "  window.translation_data = " + json.dumps(tmp, indent=3, ensure_ascii=False, separators=(',', ': '))
content += ";\n}(window));"
#return json.dumps(tmp, indent=3, ensure_ascii=False, separators=(',', ': '))
translation_data_file=context.web_page_module.searchFolder(portal_type='Web Script',reference=translation_data_file)[0]
translation_data_file.edit(text_content = content)

# Edit web section modification date
context.edit()

if batch_mode:
  return 'done'
return context.Base_redirect('view', keep_items=dict(portal_status_message=Base_translateString("Translation Data Create")))
