from erp5.component.document.TextSynthClientConnector import TextSynthError

try:
  _, textsynth_response_dict, _ = context.getPortalObject().portal_web_services.textsynth.translate(
    text=source_text,
    target_lang=target_language,
    source_lang=source_language,
  )
except TextSynthError as e:
  if e.status == 498:
    return context.Base_renderForm(
      'Preference_viewTranslateDialog',
      level='error',
      message=context.Base_translateString(
        'Request captcha validation'
      )
    )
  raise

if textsynth_response_dict.get('error', False):
  return context.Base_renderForm(
    'Preference_viewTranslateDialog',
    level='error',
    message=textsynth_response_dict['error']
  )

context.REQUEST.form['your_translated_text'] = ' '.join([translation['text'] for translation in textsynth_response_dict['translations']])

textsynth_language_dict = {language_tuple[1]:language_tuple[0] for language_tuple in context.Base_getTextSynthTranslateLanguage()}
return context.Base_renderForm(
  'Preference_viewTranslateDialog',
  message=context.Base_translateString(
    "Text translated from ${source_language} to ${target_language}",
    mapping={
      'source_language': textsynth_language_dict[textsynth_response_dict['translations'][0]['detected_source_lang']],
      'target_language': textsynth_language_dict[target_language],
    }
  )
)
