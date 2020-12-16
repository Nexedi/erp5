"""Returns the `text_content` that should be set on the translation data script for this RJS website.
"""
import re
import json

portal = context.getPortalObject()
Base_translateString = context.Base_translateString

# Collect all translatable messages from web pages referenced by this web sites.
# The convention is to use data-i18n tags in HTML, like:
#   <span data-18n="The message">The message</span>
# or in comments, like this:
#   <!-- data-i18n="The message" -->
attribute_filter_re = re.compile(r"""(data-i18n)=["']?((?:.(?!["']?\s+(?:\S+)=|[>"']))+.)["']?""")
translatable_message_set = set([])
for web_page in portal.web_page_module.searchFolder(portal_type='Web Page',
                                                    reference=context.Base_getTranslationSourceFileList(only_html=1)):
  data = attribute_filter_re.findall(web_page.getTextContent())
  for attribute in data:
    a = re.sub(r'[{|}]', "", attribute[1])
    a = re.sub(r'\[.*?\]', "", a)
    if a:
      translatable_message_set.add(a)

tmp = {}
for language in context.getAvailableLanguageSet():
  tmp[language] = {}
  for word in translatable_message_set:
    tmp[language][word] = Base_translateString(word, lang = language)

return """/**
 * This translation data is generated automatically and updated with upgrader in post-upgarde.
 * Do not edit manually, but use "Update Translation Data" action on web site to update from
 * Localizer and from data-i18n tags on web pages.
 */
/*globals window*/
/*jslint indent: 2, nomen: true */

(function (window) {
  "use strict";
  // @ts-ignore
  window.translation_data = %s;
}(window));
""" % ("\n  ".join(
        json.dumps(
            tmp,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            separators=(',', ': ')).splitlines()))
