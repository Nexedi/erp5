custom_string += '+'
custom_textarea += '!'
custom_integer += 1
custom_listfield += '$'
custom_radio += '@'

request = container.REQUEST
request.form['your_custom_string'] = custom_string
request.form['your_custom_textarea'] = custom_textarea
request.form['your_custom_integer'] = custom_integer
request.form['your_custom_listfield'] = custom_listfield
request.form['your_custom_radio'] = custom_radio

# request.set('your_custom_variable', your_custom_variable)
# request.set('previous_custom_variable', custom_variable)

return context.Base_renderForm("Foo_viewManuallyUpdatedRequestDialog", keep_items={
  # 'your_custom_variable': your_custom_variable,
  # 'previous_custom_variable': custom_variable
})
