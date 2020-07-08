"""Check that RenderJS translation gadget data is up to date.

This compare the current content of the translation gadget data against what
the content would be if "Update Translation Data" were used. If the scripts
are different, update the translation data to fix.
"""
from collections import defaultdict

if not context.getAvailableLanguageList():
  return []

if context.getSkinSelectionName() != 'RJS':
  return []

try:
  context.getPortalObject().changeSkin("RJS")

  # find the .js containing translation data
  gadget_translation_data_js = context.WebSite_getTranslationDataWebScriptValue()
  if gadget_translation_data_js is None:
    return []
  
  error_list = []
  if context.WebSite_getTranslationDataTextContent(
  ) != gadget_translation_data_js.getTextContent():
    error_list.append("Translation data script content is not up to date")
  
    if fixit:
      # try to detect the case of two incompatible web sites configured for the same translation gadget.
      # Use a mapping of set of web site ids keyed by translation data script reference and check
      # if we update the same translation data script more than once in the same REQUEST.
      # Using REQUEST is not really good, since upgrader uses grouped activities and we can just check
      # web sites processed in the same activity group, but that's easy and hopefully better than nothing.
      already_updated_websites = container.REQUEST.get(
          script.getId(), defaultdict(set))
      container.REQUEST.set(script.getId(), already_updated_websites)
      gadget_translation_data_js_reference = gadget_translation_data_js.getReference()
      already_updated_websites[gadget_translation_data_js_reference].add(context.getId())
      if len(already_updated_websites[gadget_translation_data_js_reference]) > 1:
        raise RuntimeError(
            "Translation script %s is used by more than one web site with different configurations (%s)"
            % (
                gadget_translation_data_js_reference,
                ", ".join(already_updated_websites[gadget_translation_data_js_reference]),
            ))
  
      context.WebSite_updateTranslationData()
      # since we might have modified some cached files, check again the modification date
      # consistency.
      error_list.extend(
          context.WebSite_checkCacheModificationDateConsistency(fixit=True))
  
  return error_list
finally:
  context.getPortalObject().changeSkin("View")
