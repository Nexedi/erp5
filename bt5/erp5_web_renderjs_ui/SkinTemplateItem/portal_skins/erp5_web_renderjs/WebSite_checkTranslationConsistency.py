from DateTime import DateTime
if not context.getAvailableLanguageList():
  return []

translation_gadget_url = context.getLayoutProperty("configuration_translation_gadget_url")

# XXX - We only support gadget_translation.html as translation gadget, because
# we know that this gadget uses gadget_translation.js for its translation data
if translation_gadget_url != 'gadget_translation.html':
  return []

portal = context.getPortalObject()
gadget_translation_data_js = context.getDocumentValue('gadget_translation_data.js')

if gadget_translation_data_js is None:
  return ["translation data does not exist"]

signature = portal.Localizer.erp5_ui.get_translated_messages_signature(
    language_list=context.getAvailableLanguageList(),
)

error_list = []
gadget_translation_data_js_version = gadget_translation_data_js.getVersion() or ''
if signature not in gadget_translation_data_js_version:
  error_list.append(
      "Translation data gadget_translation_data.js has different version from Localizer")
  if fixit:
    context.Base_createTranslateData(
        translation_data_file='gadget_translation_data.js',
        batch_mode=True)
    gadget_translation_data_js.setVersion(signature)
return error_list
