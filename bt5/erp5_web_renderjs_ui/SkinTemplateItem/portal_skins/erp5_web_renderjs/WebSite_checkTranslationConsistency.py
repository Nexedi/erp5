portal = context.getPortalObject()

if not context.getAvailableLanguageList():
  return []

translation_gadget_url = context.getLayoutProperty("configuration_translation_gadget_url")
if not translation_gadget_url:
  return []
translation_gadget = context.getDocumentValue(translation_gadget_url)
if not translation_gadget:
  return []

# XXX workaround a bug with getImplicitSuccessorValueList
translation_gadget = portal.restrictedTraverse(translation_gadget.getRelativeUrl())

# find the .js containing translation data
gadget_translation_data_js = None
for successor in translation_gadget.getImplicitSuccessorValueList():
  successor = successor.getObject()
  if successor.getReference() and successor.getReference().endswith('translation_data.js'):
    gadget_translation_data_js = successor
    break


if gadget_translation_data_js is None:
  return ["translation data script does not exist"]

signature = portal.Localizer.erp5_ui.get_translated_messages_signature(
    language_list=context.getAvailableLanguageList(),
)

error_list = []
gadget_translation_data_js_version = gadget_translation_data_js.getVersion() or ''
if signature not in gadget_translation_data_js_version:
  error_list.append(
      "Translation data script has different version from Localizer")
  if fixit:
    context.Base_createTranslateData(
        translation_data_file=gadget_translation_data_js.getReference(),
        batch_mode=True)
    gadget_translation_data_js.edit(version=signature)
return error_list
