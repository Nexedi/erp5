import re
import json

portal = context.getPortalObject()

Base_translateString = context.Base_translateString
#(data-i18n)=["']{{((?:.(?!["']?(?:\S+)=|[>"']))+.)}}["']
attribute_filter_re = re.compile(r"""(data-i18n)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?""")

translate_word = []

for web_page in portal.web_page_module.searchFolder(portal_type='Web Page',
                                                    reference=context.Base_getListFileFromAppcache(only_html=1)):
  data = attribute_filter_re.findall(web_page.getTextContent())
  for attribute in data:
    a = re.sub(r'[{|}]', "", attribute[1])
    a = re.sub(r'\[.*?\]', "", a)
    if a:
      translate_word.append(a)

translate_word =  list(set(translate_word))


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

if batch_mode:
  return 'done'
return context.Base_redirect('view', keep_items=dict(portal_status_message=Base_translateString("Translation Data Create")))
