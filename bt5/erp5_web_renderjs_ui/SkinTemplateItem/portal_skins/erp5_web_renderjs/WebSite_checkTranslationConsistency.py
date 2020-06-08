portal = context.getPortalObject()

if not context.getAvailableLanguageList():
  return []

if context.getSkinSelectionName() != 'RJS':
  return []

translation_gadget_url = context.getLayoutProperty(
    "configuration_translation_gadget_url")

# find the .js containing translation data
gadget_translation_data_js = context.WebSite_getTranslationDataWebScriptValue()
if gadget_translation_data_js is None:
  return []

error_list = []
if context.WebSite_getTranslationDataTextContent() != gadget_translation_data_js.getTextContent():
  error_list.append(
      "Translation data script content is not up to date")
  if fixit:
    context.WebSite_updateTranslationData()
    # since we might have modified some cached files, check again the modification date
    # consistency.
    error_list.extend(
        context.WebSite_checkCacheModificationDateConsistency(fixit=True))

return error_list
