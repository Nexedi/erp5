"""Returns the `text_content` that should be set on the translation data script for this RJS website.
"""
import json

portal = context.getPortalObject()
Base_translateString = context.Base_translateString

# Collect all translatable messages from web pages referenced by this web sites.
# The convention is to use data-i18n tags in HTML, like:
#   <span data-18n="The message">The message</span>
# or in comments, like this:
#   <!-- data-i18n="The message" -->
translatable_message_set = set([])

# Web pages can be in web page module ...
web_page_reference_list = context.Base_getTranslationSourceFileList(only_html=1)
not_found_in_web_page_reference_set = set([])
for web_page_reference in web_page_reference_list:
  web_page = context.getDocumentValue(web_page_reference)
  if web_page is None:
    not_found_in_web_page_reference_set.add(web_page_reference)
  else:
    for message in portal.ERP5Site_extractTranslationMessageListFromHTML(web_page.getTextContent()):
      translatable_message_set.add(message)
# ... or in skin folders
for web_page_reference in not_found_in_web_page_reference_set:
  if not '/' in web_page_reference:
    web_page = context.restrictedTraverse(web_page_reference, None)
    if web_page is not None and hasattr(web_page, 'manage_FTPget'):
      for message in portal.ERP5Site_extractTranslationMessageListFromHTML(web_page.manage_FTPget()):
        translatable_message_set.add(message)

tmp = {}
for language in context.getAvailableLanguageSet():
  tmp[language] = {}
  for word in translatable_message_set:
    tmp[language][word] = unicode(Base_translateString(word, lang = language), 'utf-8')

return u"""/**
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
""" % (u"\n  ".join(
        json.dumps(
            tmp,
            sort_keys=True,
            indent=2,
            ensure_ascii=False,
            separators=(',', ': ')).splitlines())).encode('utf-8')
