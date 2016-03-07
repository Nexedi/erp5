from Products.ERP5Type.Utils import convertToUpperCase
def upperCase(text):
  return convertToUpperCase(text.replace('-', '_'))

property_name = args[0]
language = args[1]
method = getattr(context, 'get%s' % upperCase('%s_translated_%s' % (language, property_name)))
translated_message = method(no_original_value=True)

return translated_message
