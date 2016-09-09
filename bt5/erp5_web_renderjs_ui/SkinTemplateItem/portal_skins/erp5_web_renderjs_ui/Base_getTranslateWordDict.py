import re
import json

#(data-i18n)=["']{{((?:.(?!["']?(?:\S+)=|[>"']))+.)}}["']
attribute_filter_re = re.compile(r"""(data-i18n)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?""")

tmp_re = re.compile(r"""/[{}]/g, """"")


translate_word = []

for tmp in context.web_page_module.searchFolder(portal_type= 'Web Page'):
  if tmp.getId().startswith(base):
    data = attribute_filter_re.findall(tmp.getTextContent())
    for attribute in data:
      a = re.sub(r'[{|}]', "", attribute[1])
      a = re.sub(r'\[.*?\]', "", a)
      if a:
        translate_word.append(a)

translate_word =  list(set(translate_word))

language_list = context.Localizer.get_supported_languages()
language_list = context.web_site_module.restrictedTraverse(web_site).getAvailableLanguageSet()

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
    tmp[language][word] = context.Base_translateString(word, lang = language)



content += "  window.translation_data = " + json.dumps(tmp, indent=3, ensure_ascii=False, separators=(',', ': '))
content += ";\n}(window));"
#return json.dumps(tmp, indent=3, ensure_ascii=False, separators=(',', ': '))
translation_data =  context.web_page_module.restrictedTraverse(url)
translation_data.edit(text_content = content)
return "done"
