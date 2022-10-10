"""Returns the `text_content` that should be set on the translation data script for this RJS website.
"""
import json
from Products.ERP5Type.Utils import str2unicode, unicode2str

portal = context.getPortalObject()
Base_translateString = context.Base_translateString

# Collect all translatable messages from web pages referenced by this web sites.
# The convention is to use data-i18n tags in HTML, like:
#   <span data-18n="The message">The message</span>
# or in comments, like this:
#   <!-- data-i18n="The message" -->
translatable_message_set = set([])

web_page_reference_list = context.Base_getTranslationSourceFileList(only_html=1)

web_page_by_reference = {}
if web_page_reference_list:
  web_page_list = [
    b.getObject() for b in
    portal.portal_catalog.getDocumentValueList(reference=web_page_reference_list, all_languages=True)]
  web_page_by_reference = {wp.getReference(): wp.getTextContent() for wp in web_page_list}

for web_page_reference in web_page_reference_list:
  # Web pages can be in web page module ...
  web_page_text_content = web_page_by_reference.get(web_page_reference)
  if web_page_text_content is None:
    # ... or in skin folders
    web_page = context.restrictedTraverse(web_page_reference, None)
    if web_page is not None and hasattr(web_page, 'PrincipiaSearchSource'):
      web_page_text_content = web_page.PrincipiaSearchSource()

  if web_page_text_content:
    for message in portal.ERP5Site_extractTranslationMessageListFromHTML(web_page_text_content):
      translatable_message_set.add(message)

tmp = {}
for language in context.getAvailableLanguageSet():
  tmp[language] = {}
  for word in translatable_message_set:
    tmp[language][word] = str2unicode(Base_translateString(word, lang = language))

# We pass unicode to this json.dump(ensure_ascii=False), so that it produce
# UTF-8 string and not escaped characters. At the end we return an UTF-8
# encoded string and not an unicode instance, because text_content property
# is usually UTF-8 encoded str (not unicode).
return unicode2str(u"""/**
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
            separators=(',', ': ')).splitlines())))
