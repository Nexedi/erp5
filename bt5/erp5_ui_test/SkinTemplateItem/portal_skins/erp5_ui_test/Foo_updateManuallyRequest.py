custom_string += '+'
custom_textarea += '!'
custom_integer += 1
custom_listfield += '$'
custom_radio += '@'

return context.Base_renderForm("Foo_viewManuallyUpdatedRequestDialog", keep_items={
  'your_custom_string': custom_string,
  'your_custom_textarea': custom_textarea,
  'your_custom_integer': custom_integer,
  'your_custom_listfield': custom_listfield,
  'your_custom_radio': custom_radio
})
