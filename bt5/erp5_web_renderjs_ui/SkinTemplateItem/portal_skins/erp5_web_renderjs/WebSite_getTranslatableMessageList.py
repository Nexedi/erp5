"""Returns messages to be translated from this web site.
"""
import re

portal = context.getPortalObject()

#(data-i18n)=["']{{((?:.(?!["']?(?:\S+)=|[>"']))+.)}}["']
attribute_filter_re = re.compile(r"""(data-i18n)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?""")

translate_word = []

for web_page in portal.web_page_module.searchFolder(portal_type='Web Page',
                                                    reference=context.Base_getTranslationSourceFileList(only_html=1)):
  data = attribute_filter_re.findall(web_page.getTextContent())
  for attribute in data:
    a = re.sub(r'[{|}]', "", attribute[1])
    a = re.sub(r'\[.*?\]', "", a)
    if a:
      translate_word.append(a)

return list(set(translate_word))
